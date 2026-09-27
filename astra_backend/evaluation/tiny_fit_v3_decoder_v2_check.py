#!/usr/bin/env python3
"""Zero-optimizer real-P1 check of decoder V2 on the frozen V3 tiny-fit model.

No fitting or threshold search occurs here. The script re-prepares the exact
frozen V3 crops, verifies target/model identities, reproduces boundary-corrected
decoder-V1 metrics, then evaluates the rising-edge same-fret decoder V2.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import torch

from evaluation.event_contract_v2 import score_events
from evaluation.event_decoder_v2 import (
    ONSET_THRESHOLD,
    STATE_ACTIVE_THRESHOLD,
    decode_event_list_v2,
)
from evaluation.tiny_fit_v3_diagnostic import (
    _event_from_dict,
    _prepared_summary,
    _probability_detail,
    boundary_exclusions,
    detailed_score,
)
from tiny_fit_pilot_v1 import (
    FEATURE_DIM,
    MAX_FRAMES_PER_EXAMPLE,
    TinyEventFitModel,
    _load_prepared_examples,
    _sha256_file,
    _sha256_json,
    decode_event_list,
    repeated_reference_events,
)

SCHEMA = "astra-tiny-fit-v3-decoder-v2-check-v1"


def _totals():
    return {"reference": 0, "prediction": 0, "tp": 0, "fp": 0, "fn": 0}


def _add(total, score):
    total["reference"] += score["referenceCount"]
    total["prediction"] += score["predictionCount"]
    total["tp"] += score["truePositive"]
    total["fp"] += score["falsePositive"]
    total["fn"] += score["falseNegative"]


def _finite(value):
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def run(args):
    frozen_v3 = json.loads(Path(args.frozen_v3_result).read_text())
    frozen_diag = json.loads(Path(args.frozen_diagnostic_result).read_text())

    metas, features, state, onset = _load_prepared_examples(args.examples_dir)
    prepared = _prepared_summary(metas)
    if prepared != frozen_v3["prepared"]:
        raise RuntimeError("prepared examples differ from frozen V3 target set")

    checkpoint = torch.load(args.model, map_location="cpu")
    if checkpoint.get("schema") != "astra-tiny-fit-pilot-v1":
        raise RuntimeError("unexpected frozen V3 checkpoint schema")
    if checkpoint.get("candidateId") != "astra_tiny_event_fit_v1":
        raise RuntimeError("unexpected frozen V3 candidate")
    if checkpoint.get("optimizerSteps") != 200:
        raise RuntimeError("frozen V3 checkpoint optimizer-step identity mismatch")
    target_set_sha = _sha256_json(prepared)
    if checkpoint.get("preparedTargetSetSha256") != target_set_sha:
        raise RuntimeError("frozen V3 prepared target-set identity mismatch")

    model = TinyEventFitModel()
    model.load_state_dict(checkpoint["stateDict"], strict=True)
    model.eval()
    with torch.no_grad():
        outputs = model(torch.as_tensor(features, dtype=torch.float32))

    v1_total = _totals()
    v2_total = _totals()
    v1_examples = []
    v2_examples = []
    v2_offset_ok = 0
    v2_tp = 0
    repeated_ref_total = 0
    repeated_tp_total = 0
    remaining_fp_total = 0

    for index, meta in enumerate(metas):
        hop = float(meta["hopSeconds"])
        ref = [_event_from_dict(row) for row in meta["prepared"]["scorableEvents"]]
        intervals, boundary_records = boundary_exclusions(meta["prepared"])

        pred_v1 = decode_event_list(
            outputs["state"][index], outputs["onset"][index],
            hop_seconds=hop, id_prefix=f"v1:{index}",
        )
        pred_v2 = decode_event_list_v2(
            outputs["state"][index], outputs["onset"][index],
            hop_seconds=hop, id_prefix=f"v2:{index}",
        )

        score_v1 = score_events(
            pred_v1, ref, onset_tolerance=0.05, offset_tolerance=0.05,
            excluded_intervals=intervals,
        )
        score_v2 = score_events(
            pred_v2, ref, onset_tolerance=0.05, offset_tolerance=0.05,
            excluded_intervals=intervals,
        )
        _add(v1_total, score_v1)
        _add(v2_total, score_v2)
        v2_offset_ok += score_v2["matchedOffsetWithinTolerance"]
        v2_tp += score_v2["truePositive"]

        repeated = repeated_reference_events(ref)
        repeated_ref_total += len(repeated)
        if repeated:
            rep_score = score_events(
                pred_v2, repeated, onset_tolerance=0.05, offset_tolerance=0.05,
                excluded_intervals=intervals,
            )
            repeated_tp_total += rep_score["truePositive"]

        details_v2 = detailed_score(pred_v2, ref, excluded_intervals=intervals)
        remaining_fp = [
            _probability_detail(
                _event_from_dict(row),
                outputs["state"][index],
                outputs["onset"][index],
                state[index],
                onset[index],
                ref,
                hop,
            )
            for row in details_v2["falsePositives"]
        ]
        remaining_fp_total += len(remaining_fp)

        v1_examples.append({"captureKey": meta["captureKey"], "score": score_v1})
        v2_examples.append({
            "captureKey": meta["captureKey"],
            "score": score_v2,
            "boundaryExclusions": boundary_records,
            "remainingFalsePositives": remaining_fp,
            "remainingFalseNegatives": details_v2["falseNegatives"],
        })

    v1_min_f1 = min(row["score"]["f1"] for row in v1_examples)
    v2_min_f1 = min(row["score"]["f1"] for row in v2_examples)
    v2_offset_fraction = v2_offset_ok / v2_tp if v2_tp else None
    repeated_recall = (
        repeated_tp_total / repeated_ref_total if repeated_ref_total else None
    )

    expected_v1 = frozen_diag["boundaryCorrectedTotals"]
    if v1_total != expected_v1:
        raise RuntimeError(
            f"decoder-V1 corrected total reproduction mismatch: {v1_total} != {expected_v1}"
        )
    if not math.isclose(
        v1_min_f1,
        frozen_diag["boundaryCorrectedTrainingExampleF1Min"],
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise RuntimeError("decoder-V1 corrected minimum F1 reproduction mismatch")

    with torch.no_grad():
        silence = torch.zeros(
            (1, MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM), dtype=torch.float32
        )
        silence_out = model(silence)
        silence_pred_v2 = decode_event_list_v2(
            silence_out["state"][0], silence_out["onset"][0],
            hop_seconds=float(metas[0]["hopSeconds"]),
            id_prefix="silence-v2",
        )

    unresolved = sum(m["prepared"]["unresolvedLabelCount"] for m in metas)
    metrics = {
        "decoderV2TrainingExampleF1Min": v2_min_f1,
        "matchedOffsetWithin50msFraction": v2_offset_fraction,
        "repeatedReferenceAttackCount": repeated_ref_total,
        "repeatedAttackRecall": repeated_recall,
        "repeatedAttackCoverageSatisfied": repeated_ref_total > 0,
        "noEventSyntheticFalsePositiveCount": len(silence_pred_v2),
        "remainingFalsePositiveCount": remaining_fp_total,
        "unresolvedLabelCount": unresolved,
    }
    finite = _finite(metrics) and _finite(v2_examples)
    engineering_gate = (
        v2_min_f1 >= 0.95
        and v2_offset_fraction is not None and v2_offset_fraction >= 0.90
        and repeated_ref_total > 0
        and repeated_recall is not None and repeated_recall >= 0.90
        and len(silence_pred_v2) == 0
        and unresolved == 0
        and finite
    )

    receipt = {
        "schema": SCHEMA,
        "sourceV3": {
            "runId": 36280547470,
            "artifactId": 10918434248,
            "modelSha256": _sha256_file(args.model),
            "resultSha256": _sha256_file(args.frozen_v3_result),
            "preparedTargetSetSha256": target_set_sha,
        },
        "execution": {
            "optimizerStepsExecuted": 0,
            "thresholdsChanged": False,
            "modelWeightsChanged": False,
            "captureSelectionChanged": False,
            "cropSelectionChanged": False,
        },
        "decoderV2": {
            "sameFretReattackRule": "fresh below-to-above onset-threshold crossing while same fret remains active",
            "stateActiveThreshold": STATE_ACTIVE_THRESHOLD,
            "onsetThreshold": ONSET_THRESHOLD,
        },
        "decoderV1BoundaryCorrectedReproduction": {
            "totals": v1_total,
            "trainingExampleF1Min": v1_min_f1,
            "examples": v1_examples,
        },
        "decoderV2Evaluation": {
            "totals": v2_total,
            "metrics": metrics,
            "examples": v2_examples,
            "allMetricsFinite": finite,
            "engineeringTrainingOnlyGateMet": engineering_gate,
        },
        "guards": {
            "p2Opened": False,
            "p3Opened": False,
            "paidComputeUsed": False,
            "optimizerExecuted": False,
            "thresholdRetuning": False,
            "automaticRetry": False,
            "automaticFullTraining": False,
            "customerDeliveryEligible": False,
        },
        "meaning": "training-example decoder check only; no generalization or customer claim",
    }
    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("TINY_FIT_DECODER_V2_CHECK=" + json.dumps({
        "optimizerStepsExecuted": 0,
        "v1CorrectedFalsePositiveCount": v1_total["fp"],
        "v2FalsePositiveCount": v2_total["fp"],
        "v2FalseNegativeCount": v2_total["fn"],
        "v2TrainingExampleF1Min": v2_min_f1,
        "matchedOffsetWithin50msFraction": v2_offset_fraction,
        "repeatedAttackRecall": repeated_recall,
        "engineeringTrainingOnlyGateMet": engineering_gate,
    }, sort_keys=True))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--examples-dir", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--frozen-v3-result", required=True)
    p.add_argument("--frozen-diagnostic-result", required=True)
    p.add_argument("--out", required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
