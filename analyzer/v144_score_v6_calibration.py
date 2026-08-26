#!/usr/bin/env python3
"""Score frozen V6 against the already-consumed professional calibration reference.

This is NOT an unseen-holdout scorer. V6 must already be frozen before this script runs.
It independently re-scores frozen V5 and frozen V6 with the same metric implementation
and verifies V6 matches the previously predicted policy-sweep result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from v144_rhythm_calibration_diagnostics import build_reference
from v144_v6_policy_sweep import metric_bundle, split_bundle

EXPECTED_V5 = {
    "eventCount": 1209,
    "onsetCount": 891,
    "onsets": 0.4819277108433735,
    "exactEvent": 0.044547563805104405,
    "pitchContent": 0.5976798143851508,
    "pitchClassContent": 0.8046403712296984,
    "measurePitch": 0.2830626450116009,
    "measurePitchClass": 0.468677494199536,
    "positionContent": 0.4677494199535963,
}

EXPECTED_V6 = {
    "eventCount": 1149,
    "onsetCount": 839,
    "onsets": 0.48682385575589454,
    "exactEvent": 0.04486873508353222,
    "pitchContent": 0.6042959427207636,
    "pitchClassContent": 0.8085918854415275,
    "measurePitch": 0.28544152744630075,
    "measurePitchClass": 0.4715990453460621,
    "positionContent": 0.469689737470167,
}

METRICS = (
    "onsets",
    "exactEvent",
    "pitchContent",
    "pitchClassContent",
    "measurePitch",
    "measurePitchClass",
    "positionContent",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def f1(bundle: Mapping[str, Any], metric: str) -> float:
    return float((bundle.get(metric) or {}).get("f1") or 0.0)


def verify_expected(name: str, bundle: Mapping[str, Any], expected: Mapping[str, Any]) -> None:
    if int(bundle.get("eventCount") or -1) != int(expected["eventCount"]):
        raise ValueError(f"{name} eventCount mismatch: {bundle.get('eventCount')} != {expected['eventCount']}")
    if int(bundle.get("onsetCount") or -1) != int(expected["onsetCount"]):
        raise ValueError(f"{name} onsetCount mismatch: {bundle.get('onsetCount')} != {expected['onsetCount']}")
    for metric in METRICS:
        actual = f1(bundle, metric)
        target = float(expected[metric])
        if abs(actual - target) > 1e-12:
            raise ValueError(f"{name} {metric} mismatch: {actual} != {target}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v5_stream", type=Path)
    parser.add_argument("v6_stream", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    v5 = load_json(args.v5_stream)
    v6 = load_json(args.v6_stream)
    v5_events = v5.get("events") if isinstance(v5, Mapping) else None
    v6_events = v6.get("events") if isinstance(v6, Mapping) else None
    if not isinstance(v5_events, list) or not isinstance(v6_events, list):
        raise ValueError("V5/V6 stream missing events")

    reference = build_reference(load_json(args.structured_source))
    if len(reference) != 946:
        raise ValueError(f"expected 946 calibration reference notes, got {len(reference)}")

    v5_overall = metric_bundle(v5_events, reference)
    v6_overall = metric_bundle(v6_events, reference)
    v5_splits = split_bundle(v5_events, reference)
    v6_splits = split_bundle(v6_events, reference)

    verify_expected("V5", v5_overall, EXPECTED_V5)
    verify_expected("V6", v6_overall, EXPECTED_V6)

    improvements = {metric: f1(v6_overall, metric) - f1(v5_overall, metric) for metric in METRICS}
    split_improvements = {
        split: {
            metric: f1(v6_splits[split], metric) - f1(v5_splits[split], metric)
            for metric in METRICS
        }
        for split in ("oddMeasures", "evenMeasures")
    }

    if any(delta <= 0.0 for delta in improvements.values()):
        raise ValueError(f"expected every overall calibration metric to improve, got {improvements}")

    robust_both_splits = [
        metric
        for metric in METRICS
        if split_improvements["oddMeasures"][metric] >= -1e-12
        and split_improvements["evenMeasures"][metric] >= -1e-12
        and improvements[metric] > 0.0
    ]

    report = {
        "schemaVersion": 1,
        "classification": "v144-v6-frozen-post-generation-calibration-score",
        "calibrationReferenceUsed": True,
        "unseenHoldout": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "predictionVerified": True,
        "referenceNoteCount": len(reference),
        "v5": v5_overall,
        "v6": v6_overall,
        "v5Splits": v5_splits,
        "v6Splits": v6_splits,
        "improvementsVsV5F1": improvements,
        "splitImprovementsVsV5F1": split_improvements,
        "robustImprovedMetricsBothSplits": robust_both_splits,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
