#!/usr/bin/env python3
"""Zero-optimizer diagnostic for the frozen Astra V3 tiny-fit checkpoint.

This diagnostic does not train, retune thresholds, open P2/P3, or alter the
frozen V3 result. It re-prepares the same four P1 crops, verifies that they are
bit-identical to V3, loads the frozen V3 model, applies preregistered crop-boundary
exclusions through event_contract_v2.score_events, and records exact unmatched
prediction events after those exclusions.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

import numpy as np
import torch

from evaluation.event_contract_v2 import Event, _match, score_events, validate_events
from tiny_fit_pilot_v1 import (
    FROZEN_CAPTURE_KEYS,
    NUM_CLASSES,
    NUM_FRETS,
    NUM_STRINGS,
    ONSET_THRESHOLD,
    SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD,
    TinyEventFitModel,
    _load_prepared_examples,
    _sha256_file,
    _sha256_json,
    decode_event_list,
)

SCHEMA = "astra-tiny-fit-v3-zero-optimizer-diagnostic-v1"


def _event_dict(e):
    return {
        "id": e.id,
        "string": e.string,
        "fret": e.fret,
        "start": e.start,
        "end": e.end,
    }


def _event_from_dict(row):
    return Event(
        row["id"], int(row["string"]), int(row["fret"]),
        float(row["start"]), float(row["end"]),
    )


def _intersects(e, interval):
    string, lo, hi = interval
    return e.string == string and e.start < hi and e.end > lo


def boundary_exclusions(prepared):
    """Derive whole-event in-crop exclusion spans from prepared event IDs."""
    hop = float(prepared["crop"]["hopSeconds"])
    frames = int(prepared["crop"]["frames"])
    boundary = set(prepared["carryInEventIds"]) | set(prepared["carryOutEventIds"])
    grid = prepared["eventId"]
    if len(grid) != NUM_STRINGS or any(len(row) != frames for row in grid):
        raise ValueError("unexpected prepared eventId grid shape")

    intervals = []
    records = []
    for event_id in sorted(boundary):
        hits = []
        for string, row in enumerate(grid):
            indices = [i for i, value in enumerate(row) if value == event_id]
            if indices:
                hits.append((string, indices))
        if len(hits) != 1:
            raise RuntimeError("boundary event must occupy exactly one string: " + event_id)
        string, indices = hits[0]
        if indices != list(range(indices[0], indices[-1] + 1)):
            raise RuntimeError("boundary event occupancy must be contiguous: " + event_id)
        lo = indices[0] * hop
        hi = (indices[-1] + 1) * hop
        kind = []
        if event_id in prepared["carryInEventIds"]:
            kind.append("carry_in")
        if event_id in prepared["carryOutEventIds"]:
            kind.append("carry_out")
        intervals.append((string, lo, hi))
        records.append({
            "eventId": event_id,
            "string": string,
            "start": lo,
            "end": hi,
            "kind": kind,
            "frameStart": indices[0],
            "frameEndExclusive": indices[-1] + 1,
        })
    return intervals, records


def detailed_score(predictions, references, *, excluded_intervals):
    """Use the frozen matcher while exposing exact matched/unmatched event IDs."""
    pred = validate_events(predictions)
    ref = validate_events(references)
    exclusions = list(excluded_intervals)

    def admitted(e):
        return not any(_intersects(e, interval) for interval in exclusions)

    admitted_pred = [e for e in pred if admitted(e)]
    admitted_ref = [e for e in ref if admitted(e)]
    excluded_pred = [e for e in pred if not admitted(e)]
    excluded_ref = [e for e in ref if not admitted(e)]

    groups = defaultdict(lambda: [[], []])
    for side, events in enumerate((admitted_pred, admitted_ref)):
        for event in events:
            groups[(event.string, event.fret)][side].append(event)

    matches = []
    for ps, rs in groups.values():
        matches.extend(_match(ps, rs, 0.05))

    matched_pred_ids = {p.id for p, _ in matches}
    matched_ref_ids = {r.id for _, r in matches}
    return {
        "matches": [{"prediction": _event_dict(p), "reference": _event_dict(r)} for p, r in matches],
        "falsePositives": [_event_dict(e) for e in admitted_pred if e.id not in matched_pred_ids],
        "falseNegatives": [_event_dict(e) for e in admitted_ref if e.id not in matched_ref_ids],
        "excludedPredictions": [_event_dict(e) for e in excluded_pred],
        "excludedReferences": [_event_dict(e) for e in excluded_ref],
    }


def _probability_detail(event, state_logits, onset_logits, state_target, onset_target, refs, hop):
    frame = int(round(event.start / hop))
    frame = max(0, min(state_logits.shape[0] - 1, frame))
    state_prob = torch.softmax(
        state_logits[frame].reshape(NUM_STRINGS, NUM_CLASSES), dim=-1
    ).detach().cpu().numpy()
    onset_prob = torch.sigmoid(onset_logits[frame]).detach().cpu().numpy()
    string = event.string
    fret = event.fret

    same_identity = [r for r in refs if r.string == string and r.fret == fret]
    same_string = [r for r in refs if r.string == string]
    nearest_identity = min(same_identity, key=lambda r: abs(r.start - event.start)) if same_identity else None
    nearest_string = min(same_string, key=lambda r: abs(r.start - event.start)) if same_string else None

    return {
        **_event_dict(event),
        "startFrame": frame,
        "onsetProbability": float(onset_prob[string]),
        "onsetMarginAboveThreshold": float(onset_prob[string] - ONSET_THRESHOLD),
        "activeProbability": float(state_prob[string, fret]),
        "activeMarginAboveThreshold": float(state_prob[string, fret] - STATE_ACTIVE_THRESHOLD),
        "silenceProbability": float(state_prob[string, SILENCE_CLASS]),
        "activeMinusSilence": float(state_prob[string, fret] - state_prob[string, SILENCE_CLASS]),
        "targetStateAtStart": int(state_target[string, frame]),
        "targetOnsetAtStart": int(onset_target[string, frame]),
        "nearestSameStringFretReference": (
            {
                **_event_dict(nearest_identity),
                "onsetDeltaSeconds": float(event.start - nearest_identity.start),
            } if nearest_identity is not None else None
        ),
        "nearestSameStringReference": (
            {
                **_event_dict(nearest_string),
                "onsetDeltaSeconds": float(event.start - nearest_string.start),
            } if nearest_string is not None else None
        ),
    }


def _prepared_summary(metas):
    return [
        {
            "captureKey": m["captureKey"],
            "featureSha256": m["featureSha256"],
            "sourceEventSha256": m["prepared"]["sourceEventSha256"],
            "targetSha256": m["prepared"]["targetSha256"],
            "midiSourceSha256": m["midiSourceSha256"],
            "audioSourceSha256": m["audioSourceSha256"],
            "cropSelection": m["cropSelection"],
            "unresolvedLabelCount": m["prepared"]["unresolvedLabelCount"],
        }
        for m in metas
    ]


def run(args):
    frozen = json.loads(Path(args.frozen_result).read_text())
    metas, features, state, onset = _load_prepared_examples(args.examples_dir)
    if tuple(sorted(m["captureKey"] for m in metas)) != tuple(sorted(FROZEN_CAPTURE_KEYS)):
        raise RuntimeError("diagnostic capture identity mismatch")

    prepared = _prepared_summary(metas)
    if prepared != frozen["prepared"]:
        raise RuntimeError("re-prepared examples do not exactly match frozen V3 result")

    checkpoint = torch.load(args.model, map_location="cpu")
    if checkpoint.get("schema") != "astra-tiny-fit-pilot-v1":
        raise RuntimeError("unexpected V3 checkpoint schema")
    if checkpoint.get("candidateId") != "astra_tiny_event_fit_v1":
        raise RuntimeError("unexpected V3 checkpoint candidate")
    if checkpoint.get("optimizerSteps") != 200:
        raise RuntimeError("diagnostic requires the exact 200-step V3 checkpoint")
    target_set_sha = _sha256_json(prepared)
    if checkpoint.get("preparedTargetSetSha256") != target_set_sha:
        raise RuntimeError("V3 checkpoint target-set identity mismatch")

    model = TinyEventFitModel()
    model.load_state_dict(checkpoint["stateDict"], strict=True)
    model.eval()
    with torch.no_grad():
        outputs = model(torch.as_tensor(features, dtype=torch.float32))

    examples = []
    raw_totals = {"reference": 0, "prediction": 0, "tp": 0, "fp": 0, "fn": 0}
    corrected_totals = {"reference": 0, "prediction": 0, "tp": 0, "fp": 0, "fn": 0}
    corrected_offset_ok = corrected_tp = 0

    frozen_by_key = {
        row["captureKey"]: row for row in frozen["evaluation"]["examples"]
    }

    for index, meta in enumerate(metas):
        hop = float(meta["hopSeconds"])
        pred = decode_event_list(
            outputs["state"][index], outputs["onset"][index],
            hop_seconds=hop, id_prefix=f"diag:{index}",
        )
        ref = [_event_from_dict(row) for row in meta["prepared"]["scorableEvents"]]

        raw = score_events(pred, ref, onset_tolerance=0.05, offset_tolerance=0.05)
        frozen_row = frozen_by_key[meta["captureKey"]]
        for key in ("referenceCount", "predictionCount", "truePositive", "falsePositive", "falseNegative"):
            if raw[key] != frozen_row["event"][key]:
                raise RuntimeError("raw V3 score reproduction mismatch " + meta["captureKey"] + " " + key)
        if not math.isclose(raw["f1"], frozen_row["event"]["f1"], rel_tol=0, abs_tol=1e-12):
            raise RuntimeError("raw V3 F1 reproduction mismatch " + meta["captureKey"])

        intervals, boundary_records = boundary_exclusions(meta["prepared"])
        corrected = score_events(
            pred, ref,
            onset_tolerance=0.05,
            offset_tolerance=0.05,
            excluded_intervals=intervals,
        )
        details = detailed_score(pred, ref, excluded_intervals=intervals)

        excluded_predictions = []
        for row in details["excludedPredictions"]:
            e = _event_from_dict(row)
            excluded_predictions.append({
                **row,
                "boundaryEvents": [
                    rec for rec, interval in zip(boundary_records, intervals)
                    if _intersects(e, interval)
                ],
            })

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
            for row in details["falsePositives"]
        ]

        examples.append({
            "captureKey": meta["captureKey"],
            "featureSha256": meta["featureSha256"],
            "targetSha256": meta["prepared"]["targetSha256"],
            "cropSelection": meta["cropSelection"],
            "boundaryExclusions": boundary_records,
            "rawV3Score": raw,
            "boundaryCorrectedScore": corrected,
            "excludedBoundaryPredictions": excluded_predictions,
            "remainingFalsePositives": remaining_fp,
            "remainingFalseNegatives": details["falseNegatives"],
        })

        for totals, score in ((raw_totals, raw), (corrected_totals, corrected)):
            totals["reference"] += score["referenceCount"]
            totals["prediction"] += score["predictionCount"]
            totals["tp"] += score["truePositive"]
            totals["fp"] += score["falsePositive"]
            totals["fn"] += score["falseNegative"]
        corrected_tp += corrected["truePositive"]
        corrected_offset_ok += corrected["matchedOffsetWithinTolerance"]

    corrected_min_f1 = min(row["boundaryCorrectedScore"]["f1"] for row in examples)
    corrected_offset_fraction = (
        corrected_offset_ok / corrected_tp if corrected_tp else None
    )
    receipt = {
        "schema": SCHEMA,
        "date": "2026-09-26",
        "sourceV3": {
            "runId": 36280547470,
            "artifactId": 10918434248,
            "modelSha256": _sha256_file(args.model),
            "resultSha256": _sha256_file(args.frozen_result),
            "preparedTargetSetSha256": target_set_sha,
        },
        "execution": {
            "optimizerStepsExecuted": 0,
            "thresholdsChanged": False,
            "modelWeightsChanged": False,
            "captureSelectionChanged": False,
            "cropSelectionChanged": False,
        },
        "thresholds": {
            "stateActive": STATE_ACTIVE_THRESHOLD,
            "onset": ONSET_THRESHOLD,
            "eventF1Min": 0.95,
            "offsetWithin50msFractionMin": 0.90,
        },
        "rawTotals": raw_totals,
        "boundaryCorrectedTotals": corrected_totals,
        "boundaryCorrectedTrainingExampleF1Min": corrected_min_f1,
        "boundaryCorrectedMatchedOffsetWithin50msFraction": corrected_offset_fraction,
        "boundaryCorrectedWouldMeetFrozenF1Gate": corrected_min_f1 >= 0.95,
        "examples": examples,
        "guards": {
            "p2Opened": False,
            "p3Opened": False,
            "paidComputeUsed": False,
            "optimizerExecuted": False,
            "automaticRetry": False,
            "automaticFullTraining": False,
            "customerDeliveryEligible": False,
        },
        "meaning": "diagnostic-only rescore of the frozen V3 P1 checkpoint; not a new training or generalization result",
    }
    Path(args.out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("TINY_FIT_V3_DIAGNOSTIC=" + json.dumps({
        "optimizerStepsExecuted": 0,
        "rawFalsePositiveTotal": raw_totals["fp"],
        "boundaryCorrectedFalsePositiveTotal": corrected_totals["fp"],
        "boundaryCorrectedTrainingExampleF1Min": corrected_min_f1,
        "boundaryCorrectedMatchedOffsetWithin50msFraction": corrected_offset_fraction,
        "remainingFalsePositiveTotal": sum(len(x["remainingFalsePositives"]) for x in examples),
    }, sort_keys=True))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--examples-dir", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--frozen-result", required=True)
    p.add_argument("--out", required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
