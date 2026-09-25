#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from guitartechs_training_v2.diagnostics import diagnose_capture
from guitartechs_real_training import real_training as base
from guitartechs_training_v4.train_v4_resumable import _infer_v4

CANDIDATE_ID = "astra_guitartechs_tabcnn_v4_recall_routing"
SOURCE_RUN_ID = 35961115171
EXPECTED_CAPTURE_COUNTS = {"P1": 136, "P2": 120}
CONTENT_NAMES = ("chords", "scales", "singlenotes", "PalmMute")
EVENT_COUNT_KEYS = (
    "referenceEvents", "predictedEvents", "exactTruePositive", "falsePositive",
    "falseNegative", "onsetOnlyMatched",
)
LABEL_COUNT_KEYS = (
    "exactStringFret", "fretWrongSameString", "stringWrongSameFret",
    "bothStringAndFretWrong", "pitchCorrectWrongString", "stagedMatched",
    "unmatchedPredicted", "unmatchedReference",
)
FRAME_COUNT_KEYS = (
    "valid", "referenceActive", "predictedActive", "exactActive",
    "wrongFretWhileActive", "activityFalsePositive", "activityFalseNegative",
    "silentCorrect",
)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _content_name(category):
    return "PalmMute" if category == "techniques" else category


def _ratio(num, den, empty=0.0):
    return num / den if den else empty


def _finalize_event_counts(counts):
    out = dict(counts)
    ref = out["referenceEvents"]
    pred = out["predictedEvents"]
    tp = out["exactTruePositive"]
    onset = out["onsetOnlyMatched"]
    out["precision"] = _ratio(tp, pred, 1.0 if not ref else 0.0)
    out["recall"] = _ratio(tp, ref, 1.0 if not pred else 0.0)
    p, r = out["precision"], out["recall"]
    out["f1"] = 2 * p * r / (p + r) if p + r else 0.0
    out["onsetOnlyPrecision"] = _ratio(onset, pred, 1.0 if not ref else 0.0)
    out["onsetOnlyRecall"] = _ratio(onset, ref, 1.0 if not pred else 0.0)
    p, r = out["onsetOnlyPrecision"], out["onsetOnlyRecall"]
    out["onsetOnlyF1"] = 2 * p * r / (p + r) if p + r else 0.0
    out["falsePositiveToFalseNegativeRatio"] = (
        out["falsePositive"] / out["falseNegative"]
        if out["falseNegative"] else (0.0 if not out["falsePositive"] else None)
    )
    return out


def _finalize_frame_counts(counts):
    out = dict(counts)
    ref = out["referenceActive"]
    pred = out["predictedActive"]
    out["activeExactRecall"] = _ratio(out["exactActive"], ref, 1.0 if not pred else 0.0)
    out["activeExactPrecision"] = _ratio(out["exactActive"], pred, 1.0 if not ref else 0.0)
    out["activityFalsePositiveToFalseNegativeRatio"] = (
        out["activityFalsePositive"] / out["activityFalseNegative"]
        if out["activityFalseNegative"] else (0.0 if not out["activityFalsePositive"] else None)
    )
    out["referenceActiveFractionOfValid"] = _ratio(ref, out["valid"], 0.0)
    out["predictedActiveFractionOfValid"] = _ratio(pred, out["valid"], 0.0)
    return out


def _empty_accumulator():
    return {
        "captures": 0,
        "event": {k: 0 for k in EVENT_COUNT_KEYS},
        "labels": {k: 0 for k in LABEL_COUNT_KEYS},
        "frames": {k: 0 for k in FRAME_COUNT_KEYS},
        "perStringFrames": [{k: 0 for k in FRAME_COUNT_KEYS} for _ in range(6)],
        "stringConfusion": [[0] * 6 for _ in range(6)],
        "fretConfusion": [[0] * 20 for _ in range(20)],
        "temporal": {
            "exactMatchedPairs": 0,
            "fragmentedReferenceRuns": 0,
            "mergedPredictedRuns": 0,
            "exactPairsEndErrorOverOneFrame": 0,
            "startMeanWeighted": 0.0,
            "endMeanWeighted": 0.0,
            "durationMeanWeighted": 0.0,
            "overlapMeanWeighted": 0.0,
        },
    }


def _accumulate(acc, diagnosis):
    acc["captures"] += 1
    for k in EVENT_COUNT_KEYS:
        acc["event"][k] += int(diagnosis["eventMicro"][k])
    for k in LABEL_COUNT_KEYS:
        acc["labels"][k] += int(diagnosis["onsetLabelDecomposition"][k])
    ft = diagnosis["frameActivity"]["totals"]
    for k in FRAME_COUNT_KEYS:
        acc["frames"][k] += int(ft[k])
    for s in range(6):
        for k in FRAME_COUNT_KEYS:
            acc["perStringFrames"][s][k] += int(diagnosis["frameActivity"]["perString"][s][k])
    for r in range(6):
        for c in range(6):
            acc["stringConfusion"][r][c] += int(diagnosis["stringConfusionRefRowsPredColumns"][r][c])
    for r in range(20):
        for c in range(20):
            acc["fretConfusion"][r][c] += int(diagnosis["fretConfusionRefRowsPredColumns"][r][c])
    t = diagnosis["temporalRun"]
    n = int(t["exactMatchedPairs"])
    acc["temporal"]["exactMatchedPairs"] += n
    acc["temporal"]["fragmentedReferenceRuns"] += int(t["fragmentedReferenceRuns"])
    acc["temporal"]["mergedPredictedRuns"] += int(t["mergedPredictedRuns"])
    acc["temporal"]["exactPairsEndErrorOverOneFrame"] += int(t["exactPairsEndErrorOverOneFrame"])
    acc["temporal"]["startMeanWeighted"] += float(t["startAbsoluteErrorMs"]["mean"]) * n
    acc["temporal"]["endMeanWeighted"] += float(t["endAbsoluteErrorMs"]["mean"]) * n
    acc["temporal"]["durationMeanWeighted"] += float(t["durationAbsoluteErrorMs"]["mean"]) * n
    acc["temporal"]["overlapMeanWeighted"] += float(t["referenceOverlapFraction"]["mean"]) * n


def _finalize_accumulator(acc):
    exact = acc["temporal"]["exactMatchedPairs"]
    staged = acc["labels"]["stagedMatched"]
    onset = acc["event"]["onsetOnlyMatched"]
    temporal = {
        "exactMatchedPairs": exact,
        "fragmentedReferenceRuns": acc["temporal"]["fragmentedReferenceRuns"],
        "mergedPredictedRuns": acc["temporal"]["mergedPredictedRuns"],
        "exactPairsEndErrorOverOneFrame": acc["temporal"]["exactPairsEndErrorOverOneFrame"],
        "meanStartAbsoluteErrorMs": _ratio(acc["temporal"]["startMeanWeighted"], exact),
        "meanEndAbsoluteErrorMs": _ratio(acc["temporal"]["endMeanWeighted"], exact),
        "meanDurationAbsoluteErrorMs": _ratio(acc["temporal"]["durationMeanWeighted"], exact),
        "meanReferenceOverlapFraction": _ratio(acc["temporal"]["overlapMeanWeighted"], exact),
        "predictedToReferenceRunRatio": _ratio(acc["event"]["predictedEvents"], acc["event"]["referenceEvents"]),
    }
    labels = dict(acc["labels"])
    labels["stagedMatchCoverageVsOnsetMaximum"] = _ratio(staged, onset, 1.0)
    per_string = [_finalize_frame_counts(x) for x in acc["perStringFrames"]]
    return {
        "captureCount": acc["captures"],
        "eventMicro": _finalize_event_counts(acc["event"]),
        "onsetLabelDecomposition": labels,
        "frameActivity": _finalize_frame_counts(acc["frames"]),
        "perStringFrameActivity": per_string,
        "stringConfusionRefRowsPredColumns": acc["stringConfusion"],
        "fretConfusionRefRowsPredColumns": acc["fretConfusion"],
        "temporalRun": temporal,
    }


def _reproduce_frozen_metrics(captures):
    perfs = defaultdict(list)
    for item in captures:
        perfs[item["performance"]].append(item)
    perf_metrics = []
    fields = ("precision", "recall", "f1", "completeness", "frameAccuracy", "abstentionRate")
    for key, views in sorted(perfs.items()):
        rec = {"performance": key, "category": views[0]["category"]}
        for f in fields:
            rec[f] = float(np.mean([v[f] for v in views]))
        perf_metrics.append(rec)
    fold = {f: float(np.mean([p[f] for p in perf_metrics])) for f in fields}
    fold["contentF1"] = {}
    for category in ("chords", "scales", "singlenotes", "techniques"):
        vals = [p["f1"] for p in perf_metrics if p["category"] == category]
        name = _content_name(category)
        fold["contentF1"][name] = float(np.mean(vals)) if vals else 0.0
    fold["performanceCount"] = len(perf_metrics)
    fold["captureCount"] = len(captures)
    return fold


def _assert_metrics_match(actual, expected, tolerance=1e-12):
    fields = ("precision", "recall", "f1", "completeness", "frameAccuracy", "abstentionRate")
    for f in fields:
        if abs(float(actual[f]) - float(expected[f])) > tolerance:
            raise RuntimeError(f"frozen metric reproduction mismatch at {f}: {actual[f]} vs {expected[f]}")
    for content in CONTENT_NAMES:
        if abs(float(actual["contentF1"][content]) - float(expected["contentF1"][content])) > tolerance:
            raise RuntimeError(f"frozen content metric reproduction mismatch at {content}")


def _new_model(source_root):
    sys.path.insert(0, source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile
    return TabCNN(
        dim_in=192,
        profile=GuitarProfile(tuning=["E2", "A2", "D3", "G3", "B3", "E4"], num_frets=19),
        device="cpu",
    )


def _load_frozen_model(path, expected_sha, expected_fold, source_root):
    actual_sha = sha256_file(path)
    if actual_sha != expected_sha:
        raise RuntimeError(f"model SHA-256 mismatch for {expected_fold}")
    payload = torch.load(path, map_location="cpu")
    if payload.get("candidateId") != CANDIDATE_ID or payload.get("fold") != expected_fold:
        raise RuntimeError("frozen model identity mismatch")
    model = _new_model(source_root)
    model.load_state_dict(payload["stateDict"])
    if base.state_sha256(model) != payload.get("stateSha256"):
        raise RuntimeError("model state hash does not match embedded receipt")
    return model, payload


def diagnose_fold(rows, model, validation_performer, expected_metrics, data_dir):
    selected_rows = [r for r in rows if r["performer"] == validation_performer]
    fold_acc = _empty_accumulator()
    content_acc = {name: _empty_accumulator() for name in CONTENT_NAMES}
    capture_metrics = []

    for row in selected_rows:
        feat = np.load(row["_features"], mmap_mode="r")
        ref = np.load(row["_labels"], mmap_mode="r")
        pred = _infer_v4(model, feat)
        diag = diagnose_capture(pred, ref, hop_seconds=base.HOP_LENGTH_SAMPLES / base.SAMPLE_RATE_HZ, onset_tolerance=base.ONSET_TOLERANCE)
        _accumulate(fold_acc, diag)
        _accumulate(content_acc[_content_name(row["category"])], diag)
        frozen = base.capture_metrics(pred, ref)
        frozen.update({
            "key": row["key"],
            "performance": row["performer"] + "|" + row["category"] + "|" + row["performanceKey"],
            "category": row["category"],
        })
        capture_metrics.append(frozen)

    reproduced = _reproduce_frozen_metrics(capture_metrics)
    _assert_metrics_match(reproduced, expected_metrics)
    return {
        "validationPerformer": validation_performer,
        "frozenMetricReproduction": {"passed": True, "metrics": reproduced},
        "diagnostics": _finalize_accumulator(fold_acc),
        "perContent": {name: _finalize_accumulator(content_acc[name]) for name in CONTENT_NAMES},
    }


def _merge_fold_aggregates(folds):
    total = _empty_accumulator()
    for fold in folds:
        d = fold["diagnostics"]
        total["captures"] += d["captureCount"]
        for k in EVENT_COUNT_KEYS:
            total["event"][k] += int(d["eventMicro"][k])
        for k in LABEL_COUNT_KEYS:
            total["labels"][k] += int(d["onsetLabelDecomposition"][k])
        for k in FRAME_COUNT_KEYS:
            total["frames"][k] += int(d["frameActivity"][k])
        for s in range(6):
            for k in FRAME_COUNT_KEYS:
                total["perStringFrames"][s][k] += int(d["perStringFrameActivity"][s][k])
        for r in range(6):
            for c in range(6):
                total["stringConfusion"][r][c] += int(d["stringConfusionRefRowsPredColumns"][r][c])
        for r in range(20):
            for c in range(20):
                total["fretConfusion"][r][c] += int(d["fretConfusionRefRowsPredColumns"][r][c])
        t = d["temporalRun"]
        n = int(t["exactMatchedPairs"])
        total["temporal"]["exactMatchedPairs"] += n
        total["temporal"]["fragmentedReferenceRuns"] += int(t["fragmentedReferenceRuns"])
        total["temporal"]["mergedPredictedRuns"] += int(t["mergedPredictedRuns"])
        total["temporal"]["exactPairsEndErrorOverOneFrame"] += int(t["exactPairsEndErrorOverOneFrame"])
        total["temporal"]["startMeanWeighted"] += float(t["meanStartAbsoluteErrorMs"]) * n
        total["temporal"]["endMeanWeighted"] += float(t["meanEndAbsoluteErrorMs"]) * n
        total["temporal"]["durationMeanWeighted"] += float(t["meanDurationAbsoluteErrorMs"]) * n
        total["temporal"]["overlapMeanWeighted"] += float(t["meanReferenceOverlapFraction"]) * n
    return _finalize_accumulator(total)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--development-result", required=True)
    parser.add_argument("--p1-model", required=True)
    parser.add_argument("--p1-result", required=True)
    parser.add_argument("--p2-model", required=True)
    parser.add_argument("--p2-result", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(4)
    development = json.loads(Path(args.development_result).read_text())
    if development["sourceRun"]["runId"] != SOURCE_RUN_ID or development["decision"]["status"] != "FAIL":
        raise RuntimeError("unexpected frozen V4 development result identity")

    rows = base.load_manifest(args.manifest, args.data_dir)
    if len(rows) != 256:
        raise RuntimeError("diagnostic manifest must contain exact frozen 256 paths")
    counts = {p: sum(r["performer"] == p for r in rows) for p in ("P1", "P2")}
    if counts != EXPECTED_CAPTURE_COUNTS:
        raise RuntimeError(f"diagnostic performer counts changed: {counts}")

    fold_specs = [
        (
            "p1-train-p2-validate", "P2", args.p1_model, args.p1_result,
            development["folds"]["p1-train-p2-validate"],
        ),
        (
            "p2-train-p1-validate", "P1", args.p2_model, args.p2_result,
            development["folds"]["p2-train-p1-validate"],
        ),
    ]
    fold_out = {}
    for fold, validation_performer, model_path, result_path, frozen in fold_specs:
        result_sha = sha256_file(result_path)
        if result_sha != frozen["resultJsonSha256"]:
            raise RuntimeError(f"training result SHA-256 mismatch for {fold}")
        training_result = json.loads(Path(result_path).read_text())
        if training_result.get("fold") != fold or training_result.get("guards", {}).get("p3Opened") is not False:
            raise RuntimeError("training result identity/guard mismatch")
        model, payload = _load_frozen_model(model_path, frozen["modelSha256"], fold, args.source_root)
        if int(payload.get("epoch", -1)) != int(frozen["selectedCheckpointEpoch"]):
            raise RuntimeError("selected checkpoint epoch mismatch")
        fold_diag = diagnose_fold(rows, model, validation_performer, frozen["fullValidationMetrics"], args.data_dir)
        fold_diag["selectedCheckpointEpoch"] = int(payload["epoch"])
        fold_diag["modelFileSha256"] = frozen["modelSha256"]
        fold_diag["trainingResultSha256"] = frozen["resultJsonSha256"]
        fold_out[fold] = fold_diag

    aggregate = _merge_fold_aggregates(list(fold_out.values()))
    result = {
        "schema": "astra-guitar-techs-v4-error-decomposition-v1",
        "date": "2026-09-25",
        "sourceRunId": SOURCE_RUN_ID,
        "candidateId": CANDIDATE_ID,
        "evidenceBoundary": "P1/P2 development evidence only; P3 remained sealed.",
        "metricSemantics": {
            "frozenVerdictUnchanged": True, "decoder": "frozen V4 recall-routing decoder",
            "eventMicroCounts": "Exact onset+string+fret event counts pooled across captures; diagnostic only, distinct from frozen performance-macro acceptance metrics.",
            "onsetOnly": "Maximum-cardinality onset matching within the frozen 50 ms tolerance, ignoring string/fret identity.",
            "labelDecomposition": "Staged onset-matched diagnosis prioritizing exact identity, then same string, then same fret, then both wrong.",
            "frameActivity": "Valid non-masked string-frame activity/exact-fret accounting.",
        },
        "sourceIdentities": {
            "developmentResultSha256": sha256_file(args.development_result),
            "manifestCaptureCounts": counts,
            "decoderSourceGitBlob": "b9a96f6b256de52bfbb5076482a03263415213cb",
            "v4TrainerGitBlob": "33892a222825a2713d3955cc34139b730f4adc3d",
        },
        "folds": fold_out,
        "aggregate": aggregate,
        "guards": {
            "optimizerStepsExecuted": 0,
            "modelWeightsModified": False,
            "thresholdsRetuned": False,
            "alignmentAllowlistChanged": False,
            "p3Opened": False,
            "paidComputeUsed": False,
            "customerDeliveryEligible": False,
            "mainOrProductionModified": False,
        },
    }
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("V4_ERROR_DECOMPOSITION_PASS")
    print(json.dumps({
        "sourceRunId": SOURCE_RUN_ID,
        "folds": {k: {
            "eventMicro": v["diagnostics"]["eventMicro"],
            "onsetLabelDecomposition": v["diagnostics"]["onsetLabelDecomposition"],
            "frameActivity": v["diagnostics"]["frameActivity"],
        } for k, v in fold_out.items()},
        "aggregate": {
            "eventMicro": aggregate["eventMicro"],
            "onsetLabelDecomposition": aggregate["onsetLabelDecomposition"],
            "frameActivity": aggregate["frameActivity"],
        },
        "guards": result["guards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
