#!/usr/bin/env python3
"""One-shot player-05 confirmation scorer for frozen GuitarSet V4 H72-D035.

This scorer reads only player-05 references. It never reads audio, imports Basic
Pitch, tunes thresholds, or touches prospective players 00/01/03.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from evaluate_guitarset_v4_discovery_family import build_variant
from score_guitarset_v3_development_candidates import (
    KNOWN_ANOMALIES,
    load_reference_events,
    metric,
    score,
    sha256_file,
    verify_candidates,
    verify_reference_root,
)

CONFIRMATION_PLAYER = "05"
DISCOVERY_PLAYERS = ("02", "04")
EVAL_PLAYERS = ("00", "01", "03")
EXPECTED_TRACK_COUNT = 60
TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}
SELECTED_CONFIG: dict[str, Any] = {
    "id": "H72-D035",
    "minBaselinePitch": 72,
    "maxDurationSeconds": 0.35,
}


def _micro(rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    return metric(
        sum(int(row[section][stream]["tp"]) for row in rows),
        sum(int(row[section][stream]["pred"]) for row in rows),
        sum(int(row[section][stream]["ref"]) for row in rows),
    )


def _aggregate(rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    if not rows:
        raise RuntimeError("cannot aggregate empty player-05 confirmation rows")
    return {
        "macroF1Pct": mean(float(row[section][stream]["f1Pct"]) for row in rows),
        "micro": _micro(rows, section, stream),
    }


def evaluate(candidate_dir: Path, reference_dir: Path) -> dict[str, Any]:
    manifest, payloads_all = verify_candidates(candidate_dir)
    payloads = [row for row in payloads_all if str(row["player"]) == CONFIRMATION_PLAYER]
    if len(payloads) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} player-05 candidates, found {len(payloads)}")
    if any(str(row["player"]) in DISCOVERY_PLAYERS for row in payloads):
        raise RuntimeError("discovery candidate entered player-05 confirmation set")
    if any(str(row["player"]) in EVAL_PLAYERS for row in payloads):
        raise RuntimeError("prospective candidate entered player-05 confirmation set")

    expected_stems = {str(row["trackStem"]) for row in payloads}
    refs = verify_reference_root(reference_dir, expected_stems)
    if len(refs) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} player-05 references, found {len(refs)}")
    if any(path.stem[:2] != CONFIRMATION_PLAYER for path in refs.values()):
        raise RuntimeError("non-player-05 reference entered confirmation")

    track_rows: list[dict[str, Any]] = []
    total_changed = 0
    total_reference_events = 0
    for payload in payloads:
        stem = str(payload["trackStem"])
        ref = load_reference_events(refs[stem])
        total_reference_events += len(ref)
        variant, changed = build_variant(payload, SELECTED_CONFIG)
        total_changed += changed

        row: dict[str, Any] = {
            "trackStem": stem,
            "baselineEventCount": len(payload["baselineEvents"]),
            "variantEventCount": len(variant),
            "changedPitchCount": changed,
            "referenceEventCount": len(ref),
        }
        for section, tol in TOLS.items():
            row[section] = {
                "baseline": score(payload["baselineEvents"], ref, tol),
                "H72-D035": score(variant, ref, tol),
            }
        track_rows.append(row)

    event_identity = all(row["baselineEventCount"] == row["variantEventCount"] for row in track_rows)
    baseline = {section: _aggregate(track_rows, section, "baseline") for section in TOLS}
    selected = {section: _aggregate(track_rows, section, "H72-D035") for section in TOLS}

    primary_macro_gain = selected["primary100ms"]["macroF1Pct"] - baseline["primary100ms"]["macroF1Pct"]
    primary_micro_gain = selected["primary100ms"]["micro"]["f1Pct"] - baseline["primary100ms"]["micro"]["f1Pct"]
    strict_micro_gain = selected["strict50ms"]["micro"]["f1Pct"] - baseline["strict50ms"]["micro"]["f1Pct"]
    track_tp_deltas = {
        row["trackStem"]: int(row["primary100ms"]["H72-D035"]["tp"] - row["primary100ms"]["baseline"]["tp"])
        for row in track_rows
    }

    conditions = {
        "eventCountIdentity": bool(event_identity),
        "atLeastOnePitchChanged": total_changed > 0,
        "primaryMacroGainStrictlyPositive": primary_macro_gain > 0.0,
        "primaryCombinedMicroGainStrictlyPositive": primary_micro_gain > 0.0,
        "strict50CombinedMicroNotLower": strict_micro_gain >= 0.0,
        "noPlayer05TrackPrimaryTPLoss": all(delta >= 0 for delta in track_tp_deltas.values()),
    }
    passed = all(conditions.values())

    return {
        "schema": "dadrock.tabs.open-corpus.guitarset-v4-player05-confirmation.v1",
        "status": "V4_PLAYER05_CONFIRMATION_PASS" if passed else "V4_PLAYER05_CONFIRMATION_FAIL",
        "selectedConfig": SELECTED_CONFIG,
        "candidateFreezeManifestSha256": sha256_file(candidate_dir / "candidate-freeze-manifest.json"),
        "confirmationPlayer": CONFIRMATION_PLAYER,
        "discoveryPlayers": list(DISCOVERY_PLAYERS),
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "confirmationTrackCount": len(track_rows),
        "totalReferenceEventCount": total_reference_events,
        "changedPitchCount": total_changed,
        "eventCountIdentity": event_identity,
        "baseline": baseline,
        "selected": selected,
        "primaryMacroGainPP": primary_macro_gain,
        "primaryCombinedMicroGainPP": primary_micro_gain,
        "strict50CombinedMicroGainPP": strict_micro_gain,
        "primaryTPDeltaByTrack": track_tp_deltas,
        "positivePrimaryTPTrackCount": sum(delta > 0 for delta in track_tp_deltas.values()),
        "neutralPrimaryTPTrackCount": sum(delta == 0 for delta in track_tp_deltas.values()),
        "negativePrimaryTPTrackCount": sum(delta < 0 for delta in track_tp_deltas.values()),
        "qualification": {
            "passed": passed,
            "conditions": conditions,
        },
        "player05ReferenceRead": True,
        "player05ConfirmationScoreCalls": 1,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "audioRead": False,
        "basicPitchInferenceCalls": 0,
        "candidateRegenerated": False,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }


def self_test() -> dict[str, Any]:
    if SELECTED_CONFIG != {"id": "H72-D035", "minBaselinePitch": 72, "maxDurationSeconds": 0.35}:
        raise RuntimeError("selected config identity self-test failed")
    fake = [
        {"primary100ms": {"baseline": {"tp": 10}, "H72-D035": {"tp": 11}}},
        {"primary100ms": {"baseline": {"tp": 8}, "H72-D035": {"tp": 8}}},
    ]
    deltas = [row["primary100ms"]["H72-D035"]["tp"] - row["primary100ms"]["baseline"]["tp"] for row in fake]
    if deltas != [1, 0] or any(delta < 0 for delta in deltas):
        raise RuntimeError("track delta self-test failed")
    return {
        "status": "V4_PLAYER05_CONFIRMATION_SELF_TEST_PASS",
        "selectedConfig": SELECTED_CONFIG,
        "expectedConfirmationTrackCount": EXPECTED_TRACK_COUNT,
        "player05ReferenceRead": False,
        "player05ConfirmationScoreCalls": 0,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "audioRead": False,
        "basicPitchInferenceCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path)
    parser.add_argument("--reference-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.candidate_dir is None or args.reference_dir is None or args.output is None:
        raise SystemExit("--candidate-dir --reference-dir --output are required")

    result = evaluate(args.candidate_dir, args.reference_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "changedPitchCount": result["changedPitchCount"],
        "primaryMacroGainPP": result["primaryMacroGainPP"],
        "primaryCombinedMicroGainPP": result["primaryCombinedMicroGainPP"],
        "strict50CombinedMicroGainPP": result["strict50CombinedMicroGainPP"],
        "positivePrimaryTPTrackCount": result["positivePrimaryTPTrackCount"],
        "negativePrimaryTPTrackCount": result["negativePrimaryTPTrackCount"],
        "qualification": result["qualification"],
        "player05ReferenceRead": result["player05ReferenceRead"],
        "player05ConfirmationScoreCalls": result["player05ConfirmationScoreCalls"],
        "guitarSetProspectiveEvaluationScoreCalls": result["guitarSetProspectiveEvaluationScoreCalls"],
        "v168ReferenceFacingScoreCalls": result["v168ReferenceFacingScoreCalls"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
