from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from v143_attack_shadow_v1_replay_validator import (
    _expected_voicing,
    _finite,
    _select_v2,
)
from v143_contextual_prune_attack_shadow_v2 import build_report as build_attack_shadow_report
from v143_precision_replay_artifact_validator import validate_product


class AttackShadowV2ReplayValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AttackShadowV2ReplayValidationError(message)


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    base_validation = validate_product(product)
    _require(base_validation.get("passed") is True, "base replay validator did not pass")

    shadow = build_attack_shadow_report(product)
    _require(shadow.get("referenceFree") is True, "attack shadow is not reference-free")
    _require(int(shadow.get("removedBaselineAttackCount") or 0) == 0, "attack shadow removed baseline attacks")
    _require(int(shadow.get("thresholdsAdded") or 0) == 0, "attack shadow introduced a numeric threshold")

    replay = product.get("precisionReplayEvidence") or {}
    eligible_rows = replay.get("eligibleAttacks") or []
    eligible = {
        (int(attack["measure"]), int(attack["step"])): attack
        for attack in eligible_rows
    }
    _require(len(eligible) == int(replay.get("eligibleAttackCount") or -1), "eligible attack count mismatch")

    baseline_keys = {
        key
        for key, attack in eligible.items()
        if attack.get("retained") is True
    }
    baseline_grid_times = {
        round(_finite(eligible[key]["gridTime"]), 12)
        for key in baseline_keys
    }
    rescued_keys = {
        (int(item["measure"]), int(item["step"]))
        for item in shadow.get("rescuedAttackKeys") or []
    }
    _require(not (rescued_keys & baseline_keys), "rescued attack overlaps baseline retained attack")

    selected_total = 0
    rendered_total = 0
    voicing_dropped_total = 0
    grid_collision_count = 0
    unobserved_pitch_count = 0
    unplayable_primary_count = 0
    pitch_count_distribution: Counter[int] = Counter()
    per_attack: list[dict[str, Any]] = []

    for key in sorted(rescued_keys):
        attack = eligible[key]
        selected, primary = _select_v2(attack)
        observed = set(int(value) for value in (attack.get("candidateMidis") or []))
        unobserved = selected - observed
        unobserved_pitch_count += len(unobserved)
        _require(not unobserved, f"rescued attack {key} selected unobserved pitches")

        try:
            kept, voicing = _expected_voicing(attack, selected, primary)
        except Exception:
            unplayable_primary_count += 1
            raise
        kept_set = set(kept)
        _require(kept_set.issubset(selected), f"voicing escaped selected pitch set at {key}")
        for midi in kept:
            position = voicing[int(midi)]
            _require(0 <= int(position["stringIndex"]) < 6, f"invalid string at {key} MIDI {midi}")
            _require(0 <= int(position["fret"]) <= 24, f"invalid fret at {key} MIDI {midi}")

        if round(_finite(attack["gridTime"]), 12) in baseline_grid_times:
            grid_collision_count += 1

        selected_total += len(selected)
        rendered_total += len(kept_set)
        voicing_dropped_total += len(selected - kept_set)
        pitch_count_distribution[len(selected)] += 1
        per_attack.append(
            {
                "measure": key[0],
                "step": key[1],
                "primaryMidi": int(primary),
                "selectedPitchSet": sorted(selected),
                "renderedPitchSet": sorted(kept_set),
                "voicingDroppedPitchSet": sorted(selected - kept_set),
                "gridTime": _finite(attack["gridTime"]),
                "onsetTime": _finite(attack["onsetTime"]),
            }
        )

    return {
        "schemaVersion": 2,
        "classification": "v143-reference-free-attack-shadow-v2-pitch-voicing-replay",
        "attackPolicy": {
            "eligibleAttackCount": int(shadow["eligibleAttackCount"]),
            "baselineRetainedAttackCount": int(shadow["baselineRetainedAttackCount"]),
            "baselinePrunedAttackCount": int(shadow["baselinePrunedAttackCount"]),
            "rescuedAttackCount": len(rescued_keys),
            "shadowRetainedAttackCount": int(shadow["shadowRetainedAttackCount"]),
            "remainingPrunedAttackCount": int(shadow["remainingPrunedAttackCount"]),
            "removedBaselineAttackCount": int(shadow["removedBaselineAttackCount"]),
            "reasonCounts": shadow["reasonCounts"],
        },
        "pitchReplay": {
            "rescuedSelectedPitchCount": selected_total,
            "pitchCountDistribution": {
                str(count): attack_count
                for count, attack_count in sorted(pitch_count_distribution.items())
            },
            "unobservedPitchCount": unobserved_pitch_count,
        },
        "voicingReplay": {
            "renderedPitchCount": rendered_total,
            "voicingDroppedPitchCount": voicing_dropped_total,
            "unplayablePrimaryCount": unplayable_primary_count,
            "gridTimeCollisionWithBaselineCount": grid_collision_count,
            "standardTuning": True,
            "maxFret": 24,
        },
        "rescuedAttacks": per_attack,
        "downstreamBoundary": {
            "techniqueSustainReplayAvailableForNewlyRescuedAttacks": False,
            "freezeReady": False,
            "reason": "schema-2 intentionally does not persist the full downstream CQT/stem universe for hypothetical newly retained attacks",
        },
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    product = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_report(product)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
