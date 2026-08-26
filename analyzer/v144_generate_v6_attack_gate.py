#!/usr/bin/env python3
"""Generate V144 V6 by applying one locked source-only attack gate to frozen V5.

This generator MUST NOT consume the professional calibration reference. It uses only:
1. the frozen terminal V5 render stream; and
2. the exact, authorized V2 precision replay evidence.

Musical event content for surviving attacks is copied from V5 unchanged. The only
musical operation is dropping whole attacks that fail the locked source-evidence gate:
    detectionCountSum >= 12 && precisionGridErrorSeconds <= 0.06
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

LOCKED_MIN_DETECTIONS = 12.0
LOCKED_MAX_GRID_ERROR_SECONDS = 0.06
EXPECTED_V5_EVENTS = 1209
EXPECTED_V5_ONSETS = 891
EXPECTED_V2_ELIGIBLE_ATTACKS = 984
EXPECTED_V6_EVENTS = 1149
EXPECTED_V6_ONSETS = 839


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def attack_key(event: Mapping[str, Any]) -> tuple[int, int]:
    return int(event["measure"]), int(event["step"])


def onset_count(events: Sequence[Mapping[str, Any]]) -> int:
    return len({attack_key(event) for event in events})


def gate_passes(attack: Mapping[str, Any]) -> bool:
    return (
        float(attack.get("detectionCountSum") or 0.0) >= LOCKED_MIN_DETECTIONS
        and float(attack.get("precisionGridErrorSeconds") or 1.0) <= LOCKED_MAX_GRID_ERROR_SECONDS
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v5_stream", type=Path)
    parser.add_argument("v2_candidate_product", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    v5 = load_json(args.v5_stream)
    events = v5.get("events") if isinstance(v5, Mapping) else None
    if not isinstance(events, list) or len(events) != EXPECTED_V5_EVENTS:
        raise ValueError(f"expected frozen V5 with {EXPECTED_V5_EVENTS} events")
    if onset_count(events) != EXPECTED_V5_ONSETS:
        raise ValueError(f"expected frozen V5 with {EXPECTED_V5_ONSETS} onsets")

    product = load_json(args.v2_candidate_product)
    replay = product.get("precisionReplayEvidence") if isinstance(product, Mapping) else None
    eligible = replay.get("eligibleAttacks") if isinstance(replay, Mapping) else None
    if not isinstance(eligible, list) or len(eligible) != EXPECTED_V2_ELIGIBLE_ATTACKS:
        raise ValueError(f"expected {EXPECTED_V2_ELIGIBLE_ATTACKS} V2 eligible attacks")

    evidence_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    for attack in eligible:
        if not isinstance(attack, Mapping):
            raise ValueError("non-object V2 attack evidence")
        key = (int(attack["measure"]), int(attack["step"]))
        if key in evidence_by_key:
            raise ValueError(f"duplicate V2 attack evidence for {key}")
        evidence_by_key[key] = attack

    v5_keys = {attack_key(event) for event in events}
    missing = sorted(v5_keys - set(evidence_by_key))
    if missing:
        raise ValueError(f"missing V2 source evidence for {len(missing)} V5 attacks; first={missing[0]}")

    kept_keys = {key for key in v5_keys if gate_passes(evidence_by_key[key])}
    dropped_keys = v5_keys - kept_keys
    kept_events = [dict(event) for event in events if attack_key(event) in kept_keys]

    if onset_count(kept_events) != EXPECTED_V6_ONSETS:
        raise ValueError(
            f"locked gate produced {onset_count(kept_events)} onsets; expected {EXPECTED_V6_ONSETS}"
        )
    if len(kept_events) != EXPECTED_V6_EVENTS:
        raise ValueError(f"locked gate produced {len(kept_events)} events; expected {EXPECTED_V6_EVENTS}")

    # Preserve every surviving V5 event object exactly; only whole attacks are removed.
    output = dict(v5)
    output["classification"] = "v144-source-only-v6-conservative-attack-gate-render-stream"
    output["sourceClassification"] = v5.get("classification")
    output["v6Policy"] = {
        "name": "conservative-source-evidence-attack-gate",
        "detectionCountSumMinInclusive": LOCKED_MIN_DETECTIONS,
        "precisionGridErrorSecondsMaxInclusive": LOCKED_MAX_GRID_ERROR_SECONDS,
        "timingRelocated": False,
        "pitchRewritten": False,
        "secondaryVoicingPruned": False,
        "professionalReferenceReadDuringGeneration": False,
    }
    output["events"] = kept_events

    attack_class_before = Counter(str(event.get("v5AttackClass") or "unknown") for event in events)
    attack_class_after = Counter(str(event.get("v5AttackClass") or "unknown") for event in kept_events)
    primary_before = sum(1 for event in events if bool(event.get("v5Primary")))
    primary_after = sum(1 for event in kept_events if bool(event.get("v5Primary")))

    manifest = {
        "schemaVersion": 1,
        "classification": "v144-v6-source-only-generation-manifest",
        "candidateGenerated": True,
        "calibrationReferenceUsedDuringGeneration": False,
        "unseenHoldout": False,
        "modalInvoked": False,
        "productionModified": False,
        "sourceV5Sha256": sha256_file(args.v5_stream),
        "sourceV2CandidateProductSha256": sha256_file(args.v2_candidate_product),
        "policy": output["v6Policy"],
        "v5EventCount": len(events),
        "v5OnsetCount": len(v5_keys),
        "v6EventCount": len(kept_events),
        "v6OnsetCount": len(kept_keys),
        "droppedEventCount": len(events) - len(kept_events),
        "droppedOnsetCount": len(dropped_keys),
        "v5PrimaryEventCount": primary_before,
        "v6PrimaryEventCount": primary_after,
        "v5AttackClassEventCounts": dict(sorted(attack_class_before.items())),
        "v6AttackClassEventCounts": dict(sorted(attack_class_after.items())),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
