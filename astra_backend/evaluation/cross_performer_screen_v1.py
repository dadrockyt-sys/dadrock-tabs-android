#!/usr/bin/env python3
"""Minimal P2 cross-performer screen for the frozen Astra V3 model + decoder V2.

This module is intentionally separate from the proven P1 tiny-fit preparation
path. It supports exactly four homologous P2 direct-input captures and performs
inference only. No fitting, threshold search, P3 access, or production mutation.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import shutil
import zipfile

import numpy as np
import torch

from evaluation.event_contract_v2 import Event, score_events
from evaluation.event_decoder_v2 import decode_event_list_v2
from evaluation.prepared_event_adapter_v1 import (
    select_launch_ready_training_crop,
    source_events_from_notes,
)
from evaluation.tiny_fit_v3_diagnostic import boundary_exclusions
from tiny_fit_pilot_v1 import (
    FEATURE_DIM,
    MAX_FRAMES_PER_EXAMPLE,
    TinyEventFitModel,
    _sha256_file,
    repeated_reference_events,
)

P2_CAPTURE_KEYS = (
    "P2|chords|Drop3_7|directinput",
    "P2|scales|Ab|directinput",
    "P2|singlenotes|allsinglenotes|directinput",
    "P2|techniques|PalmMute|directinput",
)
NUM_EXAMPLES = 4

AGG_PRECISION_MIN = 0.75
AGG_RECALL_MIN = 0.60
AGG_F1_MIN = 0.67
EACH_EXAMPLE_F1_MIN = 0.55
REPEATED_RECALL_MIN = 0.60

SCHEMA = "astra-v3-decoder-v2-p2-cross-performer-screen-v1"


def _performance_key_from_path(path):
    path = Path(path)
    stem = path.stem
    parent = path.parent.name
    for prefix in (parent + "_", "midi_", "directinput_", "micamp_", "ego_", "exo_"):
        if stem.lower().startswith(prefix.lower()) and len(stem) > len(prefix):
            return stem[len(prefix):]
    return stem


def extract_selected_source(archive_path, *, capture_key, output_dir):
    if capture_key not in P2_CAPTURE_KEYS:
        raise ValueError("capture key is outside frozen P2 screen selection")
    performer, category, performance, view = capture_key.split("|")
    if performer != "P2" or view != "directinput":
        raise ValueError("cross-performer screen permits only selected P2 directinput")
    archive = Path(archive_path)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    midi = []
    audio = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = Path(info.filename)
            if "__MACOSX" in member.parts or member.name == ".DS_Store" or member.name.startswith("._"):
                continue
            if any(part in {"", ".", ".."} for part in member.parts):
                raise RuntimeError("unsafe archive member path")
            suffix = member.suffix.lower()
            if _performance_key_from_path(member) != performance:
                continue
            if suffix in (".mid", ".midi"):
                midi.append(info)
            elif suffix in (".wav", ".mp3") and member.parent.name == view:
                audio.append(info)
        if len(midi) != 1 or len(audio) != 1:
            raise RuntimeError(
                f"selected P2 archive source ambiguity: midi={len(midi)} audio={len(audio)}"
            )
        outputs = []
        for info, parent in ((midi[0], "midi"), (audio[0], view)):
            dest_dir = root / parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / Path(info.filename).name
            if dest.exists():
                raise RuntimeError("selected extraction destination already exists")
            with zf.open(info, "r") as src, dest.open("wb") as dst:
                shutil.copyfileobj(src, dst, length=1024 * 1024)
            outputs.append({
                "member": info.filename,
                "path": str(dest),
                "sha256": _sha256_file(dest),
                "bytes": dest.stat().st_size,
            })
    receipt = {
        "schema": "astra-p2-cross-screen-selected-source-v1",
        "captureKey": capture_key,
        "archive": archive.name,
        "selectedMembers": outputs,
        "unrelatedMediaExtracted": False,
        "optimizerStepsExecuted": 0,
        "p3Opened": False,
    }
    print("P2_SCREEN_SELECTED_SOURCE=" + json.dumps(receipt, sort_keys=True))
    return receipt


def prepare_capture(args):
    from guitartechs_real_training.real_training import (
        decode_audio,
        midi_string_events,
        performance_key,
        visible_files,
    )
    from tabcnn_runtime.preprocessing import (
        HOP_LENGTH_SAMPLES,
        SAMPLE_RATE_HZ,
        extract_cqt_features,
        rms_normalize,
    )

    if args.capture_key not in P2_CAPTURE_KEYS:
        raise RuntimeError("capture key outside frozen P2 screen selection")
    corrections_doc = json.loads(Path(args.corrections).read_text())
    corrections = corrections_doc["correctionsMs"]
    if args.capture_key not in corrections:
        raise RuntimeError("selected P2 capture has no frozen alignment correction")

    performer, category, pkey, view = args.capture_key.split("|")
    if performer != "P2" or view != "directinput":
        raise RuntimeError("P2 screen preparation is directinput-only")

    root = Path(args.root)
    files = visible_files(root)
    midis = {}
    audio = defaultdict(dict)
    for path in files:
        key = performance_key(path)
        suffix = path.suffix.lower()
        if suffix in (".mid", ".midi"):
            midis[key] = path
        elif suffix in (".wav", ".mp3"):
            audio[key][path.parent.name] = path
    if pkey not in midis or view not in audio.get(pkey, {}):
        raise RuntimeError("missing exact homologous P2 screen source " + args.capture_key)

    midi_path = midis[pkey]
    audio_path = audio[pkey][view]
    lag_ms = corrections[args.capture_key]
    notes = midi_string_events(midi_path)
    _, source_issues, _ = source_events_from_notes(
        notes, capture_id=args.capture_key, lag_ms=lag_ms
    )

    audio_samples = decode_audio(audio_path)
    features = extract_cqt_features(
        rms_normalize(audio_samples)
    ).squeeze(0).astype(np.float32, copy=False)
    if features.ndim != 2 or features.shape[0] != FEATURE_DIM:
        raise RuntimeError("unexpected CQT feature shape")
    if features.shape[1] < MAX_FRAMES_PER_EXAMPLE:
        raise RuntimeError("selected P2 source shorter than 200 frames")

    hop_seconds = HOP_LENGTH_SAMPLES / SAMPLE_RATE_HZ
    crop_selection, prepared = select_launch_ready_training_crop(
        notes,
        capture_id=args.capture_key,
        lag_ms=lag_ms,
        allowlist_lag_ms=corrections[args.capture_key],
        total_frames=int(features.shape[1]),
        frames=MAX_FRAMES_PER_EXAMPLE,
        hop_seconds=hop_seconds,
    )
    if prepared is None:
        print("P2_SCREEN_PREPARE_REJECT=" + json.dumps({
            "captureKey": args.capture_key,
            "cropSelection": crop_selection,
            "sourceIssueCountBeforeCrop": len(source_issues),
        }, sort_keys=True), flush=True)
        raise RuntimeError("no launch-ready P2 screen crop")
    if not prepared["launchReady"] or prepared["unresolvedLabelCount"] != 0:
        raise RuntimeError("P2 screen crop is not launch-ready")

    start = prepared["crop"]["startFrame"]
    cropped_features = np.ascontiguousarray(
        features[:, start:start + MAX_FRAMES_PER_EXAMPLE].T,
        dtype=np.float32,
    )
    if cropped_features.shape != (MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM):
        raise RuntimeError("prepared P2 feature crop shape mismatch")

    out_dir = Path(args.output_dir) / hashlib.sha256(args.capture_key.encode()).hexdigest()[:16]
    out_dir.mkdir(parents=True, exist_ok=True)
    feature_path = out_dir / "features.npy"
    meta_path = out_dir / "meta.json"
    np.save(feature_path, cropped_features, allow_pickle=False)

    meta = {
        "schema": "astra-p2-cross-screen-prepared-example-v1",
        "captureKey": args.capture_key,
        "performer": performer,
        "category": category,
        "performanceKey": pkey,
        "captureView": view,
        "lagMs": lag_ms,
        "hopSeconds": hop_seconds,
        "cropSelection": crop_selection,
        "featureSha256": _sha256_file(feature_path),
        "midiSourceSha256": _sha256_file(midi_path),
        "audioSourceSha256": _sha256_file(audio_path),
        "alignmentCorrectionsSha256": _sha256_file(args.corrections),
        "prepared": prepared,
        "sourceIssueCountBeforeCrop": len(source_issues),
        "guards": {
            "optimizerStepsExecuted": 0,
            "p3Opened": False,
            "customerDeliveryEligible": False,
        },
    }
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    print("P2_SCREEN_PREPARED=" + json.dumps({
        "captureKey": args.capture_key,
        "cropSelection": crop_selection,
        "referenceEvents": len(prepared["scorableEvents"]),
        "carryIn": len(prepared["carryInEventIds"]),
        "carryOut": len(prepared["carryOutEventIds"]),
        "featureSha256": meta["featureSha256"],
        "targetSha256": prepared["targetSha256"],
        "unresolvedLabelCount": prepared["unresolvedLabelCount"],
    }, sort_keys=True))


def _load_examples(root):
    root = Path(root)
    metas = []
    features = []
    for meta_path in sorted(root.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text())
        feature_path = meta_path.parent / "features.npy"
        if _sha256_file(feature_path) != meta["featureSha256"]:
            raise RuntimeError("prepared P2 feature hash mismatch")
        metas.append(meta)
        features.append(np.load(feature_path, allow_pickle=False))
    if len(metas) != NUM_EXAMPLES:
        raise RuntimeError("P2 screen requires exactly four examples")
    keys = {m["captureKey"] for m in metas}
    if keys != set(P2_CAPTURE_KEYS):
        raise RuntimeError("P2 screen capture identity mismatch")
    if any(m["performer"] != "P2" or m["captureView"] != "directinput" for m in metas):
        raise RuntimeError("P2 screen performer/view mismatch")
    return metas, np.stack(features, axis=0)


def _event(row):
    return Event(
        row["id"], int(row["string"]), int(row["fret"]),
        float(row["start"]), float(row["end"]),
    )


def _ratio(num, den):
    return num / den if den else None


def evaluate(args):
    metas, features = _load_examples(args.examples_dir)
    checkpoint = torch.load(args.model, map_location="cpu")
    if checkpoint.get("schema") != "astra-tiny-fit-pilot-v1":
        raise RuntimeError("unexpected frozen V3 checkpoint schema")
    if checkpoint.get("candidateId") != "astra_tiny_event_fit_v1":
        raise RuntimeError("unexpected frozen V3 candidate")
    if checkpoint.get("optimizerSteps") != 200:
        raise RuntimeError("frozen V3 optimizer-step identity mismatch")

    model = TinyEventFitModel()
    model.load_state_dict(checkpoint["stateDict"], strict=True)
    model.eval()
    with torch.no_grad():
        outputs = model(torch.as_tensor(features, dtype=torch.float32))

    totals = {"reference": 0, "prediction": 0, "tp": 0, "fp": 0, "fn": 0}
    examples = []
    repeated_ref_total = 0
    repeated_tp_total = 0
    offset_ok = 0
    unresolved_total = 0

    for i, meta in enumerate(metas):
        hop = float(meta["hopSeconds"])
        refs = [_event(row) for row in meta["prepared"]["scorableEvents"]]
        exclusions, exclusion_records = boundary_exclusions(meta["prepared"])
        preds = decode_event_list_v2(
            outputs["state"][i], outputs["onset"][i],
            hop_seconds=hop, id_prefix=f"p2:{i}",
        )
        score = score_events(
            preds, refs,
            onset_tolerance=0.05,
            offset_tolerance=0.05,
            excluded_intervals=exclusions,
        )
        totals["reference"] += score["referenceCount"]
        totals["prediction"] += score["predictionCount"]
        totals["tp"] += score["truePositive"]
        totals["fp"] += score["falsePositive"]
        totals["fn"] += score["falseNegative"]
        offset_ok += score["matchedOffsetWithinTolerance"]
        unresolved_total += int(meta["prepared"]["unresolvedLabelCount"])

        repeated = repeated_reference_events(refs)
        repeated_ref_total += len(repeated)
        rep_recall = None
        if repeated:
            rep_score = score_events(
                preds, repeated,
                onset_tolerance=0.05,
                offset_tolerance=0.05,
                excluded_intervals=exclusions,
            )
            repeated_tp_total += rep_score["truePositive"]
            rep_recall = _ratio(rep_score["truePositive"], rep_score["referenceCount"])

        examples.append({
            "captureKey": meta["captureKey"],
            "category": meta["category"],
            "cropSelection": meta["cropSelection"],
            "featureSha256": meta["featureSha256"],
            "targetSha256": meta["prepared"]["targetSha256"],
            "referenceCount": score["referenceCount"],
            "predictionCount": score["predictionCount"],
            "precision": score["precision"],
            "recall": score["recall"],
            "f1": score["f1"],
            "matchedOffsetWithinTolerance": score["matchedOffsetWithinTolerance"],
            "repeatedReferenceAttackCount": len(repeated),
            "repeatedAttackRecall": rep_recall,
            "boundaryExclusions": exclusion_records,
        })

    precision = _ratio(totals["tp"], totals["prediction"])
    recall = _ratio(totals["tp"], totals["reference"])
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else 0.0
    )
    min_example_f1 = min(row["f1"] for row in examples)
    offset_fraction = _ratio(offset_ok, totals["tp"])
    repeated_recall = _ratio(repeated_tp_total, repeated_ref_total)

    with torch.no_grad():
        silence = torch.zeros((1, MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM), dtype=torch.float32)
        out = model(silence)
        silence_pred = decode_event_list_v2(
            out["state"][0], out["onset"][0],
            hop_seconds=float(metas[0]["hopSeconds"]),
            id_prefix="p2-silence",
        )

    finite_values = [
        precision, recall, f1, min_example_f1,
        offset_fraction,
        *[x["precision"] for x in examples],
        *[x["recall"] for x in examples],
        *[x["f1"] for x in examples],
    ]
    all_finite = all(v is not None and math.isfinite(v) for v in finite_values)

    screen_green = (
        precision is not None and precision >= AGG_PRECISION_MIN
        and recall is not None and recall >= AGG_RECALL_MIN
        and f1 >= AGG_F1_MIN
        and min_example_f1 >= EACH_EXAMPLE_F1_MIN
        and repeated_ref_total > 0
        and repeated_recall is not None and repeated_recall >= REPEATED_RECALL_MIN
        and len(silence_pred) == 0
        and unresolved_total == 0
        and all_finite
    )

    receipt = {
        "schema": SCHEMA,
        "sourceModel": {
            "runId": 36280547470,
            "artifactId": 10918434248,
            "modelSha256": _sha256_file(args.model),
        },
        "execution": {
            "optimizerStepsExecuted": 0,
            "thresholdsChanged": False,
            "modelWeightsChanged": False,
            "p1MediaAccessed": False,
            "p2MediaAccessed": True,
            "p3Opened": False,
        },
        "population": {
            "performer": "P2",
            "captureKeys": list(P2_CAPTURE_KEYS),
            "captureView": "directinput",
            "examples": 4,
            "framesPerExample": MAX_FRAMES_PER_EXAMPLE,
            "selection": "exact homologous content names; deterministic source-only launch-ready crop per capture",
        },
        "thresholds": {
            "aggregatePrecisionMin": AGG_PRECISION_MIN,
            "aggregateRecallMin": AGG_RECALL_MIN,
            "aggregateF1Min": AGG_F1_MIN,
            "eachExampleF1Min": EACH_EXAMPLE_F1_MIN,
            "repeatedAttackRecallMinWhenPresent": REPEATED_RECALL_MIN,
            "source": "docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json",
            "postResultRetuningAllowed": False,
        },
        "evaluation": {
            "totals": totals,
            "aggregatePrecision": precision,
            "aggregateRecall": recall,
            "aggregateF1": f1,
            "minimumExampleF1": min_example_f1,
            "matchedOffsetWithin50msFraction": offset_fraction,
            "repeatedReferenceAttackCount": repeated_ref_total,
            "repeatedAttackRecall": repeated_recall,
            "syntheticSilenceFalsePositiveCount": len(silence_pred),
            "unresolvedLabelCount": unresolved_total,
            "allMetricsFinite": all_finite,
            "examples": examples,
            "crossPerformerScreenGreen": screen_green,
        },
        "meaning": (
            "Small source-disjoint P2 diagnostic screen only. Green supports designing a broader "
            "P1/P2 development evaluation; it does not establish final generalization, authorize "
            "P3, full training, threshold tuning, production mutation, or customer delivery."
        ),
        "guards": {
            "automaticRetry": False,
            "p3Opened": False,
            "fullTrainingAuthorized": False,
            "customerDeliveryEligible": False,
        },
    }
    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("P2_CROSS_PERFORMER_SCREEN=" + json.dumps({
        "optimizerStepsExecuted": 0,
        "aggregatePrecision": precision,
        "aggregateRecall": recall,
        "aggregateF1": f1,
        "minimumExampleF1": min_example_f1,
        "repeatedAttackRecall": repeated_recall,
        "matchedOffsetWithin50msFraction": offset_fraction,
        "crossPerformerScreenGreen": screen_green,
    }, sort_keys=True))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)

    x = sub.add_parser("extract-selected-source")
    x.add_argument("--archive", required=True)
    x.add_argument("--capture-key", required=True)
    x.add_argument("--output-dir", required=True)

    q = sub.add_parser("prepare-capture")
    q.add_argument("--root", required=True)
    q.add_argument("--capture-key", required=True)
    q.add_argument("--corrections", required=True)
    q.add_argument("--output-dir", required=True)

    e = sub.add_parser("evaluate")
    e.add_argument("--examples-dir", required=True)
    e.add_argument("--model", required=True)
    e.add_argument("--out", required=True)

    args = p.parse_args()
    if args.command == "extract-selected-source":
        extract_selected_source(args.archive, capture_key=args.capture_key, output_dir=args.output_dir)
    elif args.command == "prepare-capture":
        prepare_capture(args)
    elif args.command == "evaluate":
        evaluate(args)


if __name__ == "__main__":
    main()
