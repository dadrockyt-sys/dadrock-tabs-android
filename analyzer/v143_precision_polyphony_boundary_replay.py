from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Mapping

from v143_contextual_prune_precision_shadow import (
    HARMONIC_INTERVAL_WEIGHTS,
    POSITIVE_ATTACK_FLOOR,
    POSITIVE_BODY_FLOOR,
)
from v143_precision_polyphony_boundary import resolve_precision_polyphony


EXPECTED_RETAINED_ATTACK_COUNT = 725
EXPECTED_ORIGINAL_PITCH_HYPOTHESIS_COUNT = 7535
EXPECTED_STORED_SELECTED_PITCH_COUNT = 970
EXPECTED_BASELINE_RENDERED_PITCH_COUNT = 967


class PrecisionPolyphonyReplayError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PrecisionPolyphonyReplayError(message)


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise PrecisionPolyphonyReplayError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise PrecisionPolyphonyReplayError(f"{label} is not finite")
    return number


def _candidate_map(attack: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    output: dict[int, Mapping[str, Any]] = {}
    for item in attack.get("candidates") or []:
        midi = int(item["midi"])
        _require(midi not in output, f"duplicate replay MIDI {midi}")
        for field in ("score", "attack", "body"):
            _finite(item.get(field), f"candidate {midi} {field}")
        output[midi] = item
    expected = [int(value) for value in (attack.get("candidateMidis") or [])]
    _require(expected == list(output), "candidateMidis do not match candidate records")
    return output


def _resolve(
    *,
    primary: int,
    precision_midis: list[int],
    observed_midis: list[int],
    candidates: Mapping[int, Mapping[str, Any]],
):
    evidence = {
        int(midi): {
            "score": _finite(item.get("score"), f"candidate {midi} score"),
            "attack": _finite(item.get("attack"), f"candidate {midi} attack"),
            "body": _finite(item.get("body"), f"candidate {midi} body"),
        }
        for midi, item in candidates.items()
        if int(midi) in set(observed_midis)
    }
    return resolve_precision_polyphony(
        primary_midi=int(primary),
        precision_midis=precision_midis,
        observed_midis=observed_midis,
        evidence=evidence,
        positive_attack_floor=POSITIVE_ATTACK_FLOOR,
        positive_body_floor=POSITIVE_BODY_FLOOR,
        harmonic_intervals=tuple(HARMONIC_INTERVAL_WEIGHTS),
    )


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    replay = product.get("precisionReplayEvidence") or {}
    _require(replay.get("schemaVersion") == 2, "precision replay schema must be 2")
    _require(replay.get("referenceFree") is True, "precision replay must be reference-free")
    _require(replay.get("professionalReferenceUsed") is False, "precision replay provenance is invalid")
    _require(replay.get("runtimeLabelsRequired") is False, "runtime labels must not be required")
    _require(replay.get("productionModified") is False, "persisted replay says production was modified")
    for field in (
        "fixedRetainedAttackPitchReplayReady",
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
    ):
        _require(replay.get(field) is True, f"precision replay is not ready: {field}")

    attacks = replay.get("attacks") or []
    _require(
        len(attacks) == EXPECTED_RETAINED_ATTACK_COUNT,
        f"retained attack identity mismatch: {len(attacks)}",
    )
    _require(
        int(replay.get("retainedAttackCount") or -1) == EXPECTED_RETAINED_ATTACK_COUNT,
        "retainedAttackCount does not match the persisted precision capture",
    )

    seen_keys: set[tuple[int, int]] = set()
    original_total = 0
    stored_selected_total = 0
    baseline_rendered_total = 0
    boundary_candidate_total = 0
    boundary_rendered_total = 0
    recovered_pitch_total = 0
    recovered_attack_count = 0
    recovery_eligible_pitch_total = 0
    boundary_dropped_pitch_total = 0
    retained_voicing_drop_total = 0
    retained_render_loss_total = 0
    primary_violation_count = 0
    unobserved_pitch_count = 0
    promoted_harmonic_guard_violation_count = 0
    protected_harmonic_attack_count = 0
    max_baseline_chord_size = 0
    max_boundary_chord_size = 0
    changed_attacks: list[dict[str, Any]] = []

    for attack in attacks:
        key = (int(attack["measure"]), int(attack["step"]))
        _require(key not in seen_keys, f"duplicate retained replay attack {key}")
        seen_keys.add(key)
        _require(attack.get("retained") is True, f"attack {key} is not retained")

        candidates = _candidate_map(attack)
        observed = list(candidates)
        precision = [
            int(midi)
            for midi, item in candidates.items()
            if item.get("selected") is True
        ]
        primaries = [
            int(midi)
            for midi, item in candidates.items()
            if item.get("primary") is True
        ]
        _require(len(primaries) == 1, f"attack {key} must have exactly one primary")
        primary = primaries[0]
        _require(primary in set(precision), f"primary {primary} is not precision-selected at {key}")

        original_total += len(observed)
        stored_selected_total += len(precision)

        baseline = _resolve(
            primary=primary,
            precision_midis=precision,
            observed_midis=precision,
            candidates=candidates,
        )
        _require(not baseline.recovered_midis, f"baseline replay recovered a pitch at {key}")

        boundary = _resolve(
            primary=primary,
            precision_midis=precision,
            observed_midis=observed,
            candidates=candidates,
        )

        baseline_set = set(baseline.selected_midis)
        boundary_set = set(boundary.selected_midis)
        precision_set = set(precision)
        observed_set = set(observed)
        recovered_set = set(boundary.recovered_midis)
        boundary_candidate_set = set(boundary.candidate_midis)

        baseline_rendered_total += len(baseline_set)
        boundary_candidate_total += len(boundary_candidate_set)
        boundary_rendered_total += len(boundary_set)
        recovered_pitch_total += len(recovered_set)
        recovered_attack_count += int(bool(recovered_set))
        recovery_eligible_pitch_total += len(boundary_candidate_set - precision_set)
        boundary_dropped_pitch_total += len(boundary.dropped_midis)
        retained_voicing_drop_total += len(precision_set - baseline_set)
        retained_render_loss = baseline_set - boundary_set
        retained_render_loss_total += len(retained_render_loss)
        max_baseline_chord_size = max(max_baseline_chord_size, len(baseline_set))
        max_boundary_chord_size = max(max_boundary_chord_size, len(boundary_set))

        if primary not in boundary_set:
            primary_violation_count += 1
        unobserved_pitch_count += len(boundary_set - observed_set)
        if boundary.protected_harmonic_midi is not None:
            protected_harmonic_attack_count += 1
            if int(boundary.protected_harmonic_midi) in recovered_set:
                promoted_harmonic_guard_violation_count += 1

        _require(
            not retained_render_loss,
            f"boundary displaced a previously rendered precision pitch at {key}: {sorted(retained_render_loss)}",
        )
        _require(primary in boundary_set, f"boundary dropped primary at {key}")
        _require(boundary_set.issubset(observed_set), f"boundary invented pitch at {key}")
        _require(
            boundary.protected_harmonic_midi is None
            or int(boundary.protected_harmonic_midi) not in recovered_set,
            f"boundary reintroduced protected harmonic at {key}",
        )

        if recovered_set:
            changed_attacks.append(
                {
                    "measure": key[0],
                    "step": key[1],
                    "primaryMidi": int(primary),
                    "observedPitchCount": len(observed_set),
                    "precisionSelectedMidis": sorted(precision_set),
                    "baselineRenderedMidis": sorted(baseline_set),
                    "boundaryCandidateMidis": sorted(boundary_candidate_set),
                    "boundaryRenderedMidis": sorted(boundary_set),
                    "recoveredMidis": sorted(recovered_set),
                    "droppedCandidateMidis": sorted(boundary.dropped_midis),
                    "protectedPromotedHarmonicMidi": (
                        int(boundary.protected_harmonic_midi)
                        if boundary.protected_harmonic_midi is not None
                        else None
                    ),
                }
            )

    _require(
        original_total == EXPECTED_ORIGINAL_PITCH_HYPOTHESIS_COUNT,
        f"original hypothesis count mismatch: {original_total}",
    )
    _require(
        stored_selected_total == EXPECTED_STORED_SELECTED_PITCH_COUNT,
        f"stored selected pitch count mismatch: {stored_selected_total}",
    )
    _require(
        baseline_rendered_total == EXPECTED_BASELINE_RENDERED_PITCH_COUNT,
        f"baseline deterministic rendered pitch count mismatch: {baseline_rendered_total}",
    )
    _require(primary_violation_count == 0, "boundary changed one or more primaries")
    _require(unobserved_pitch_count == 0, "boundary created one or more unobserved pitches")
    _require(
        promoted_harmonic_guard_violation_count == 0,
        "boundary violated promoted-harmonic protection",
    )
    _require(retained_render_loss_total == 0, "boundary displaced retained rendered pitches")

    measures = sorted({measure for measure, _step in seen_keys})
    return {
        "schemaVersion": 1,
        "classification": "v143-precision-polyphony-boundary-cpu-replay",
        "source": {
            "persistedPrecisionReplaySchema": int(replay["schemaVersion"]),
            "retainedAttackCount": len(attacks),
            "originalPitchHypothesisCount": original_total,
            "storedSelectedPitchCount": stored_selected_total,
            "baselineDeterministicRenderedPitchCount": baseline_rendered_total,
            "measureStart": min(measures) if measures else None,
            "measureEnd": max(measures) if measures else None,
            "measureCount": len(measures),
            "referenceFree": True,
            "newInferenceUsed": False,
            "paidModelRequired": False,
            "professionalReferenceUsed": False,
            "productionModified": False,
        },
        "boundary": {
            "candidatePitchCount": boundary_candidate_total,
            "renderedPitchCount": boundary_rendered_total,
            "renderedPitchDeltaVsBaseline": boundary_rendered_total - baseline_rendered_total,
            "renderedPitchRatioVsBaseline": (
                float(boundary_rendered_total / baseline_rendered_total)
                if baseline_rendered_total
                else None
            ),
            "recoveryEligiblePitchCount": recovery_eligible_pitch_total,
            "recoveredPitchCount": recovered_pitch_total,
            "recoveredAttackCount": recovered_attack_count,
            "voicingOrCapacityDroppedCandidatePitchCount": boundary_dropped_pitch_total,
            "retainedVoicingDroppedPitchCount": retained_voicing_drop_total,
            "retainedRenderedPitchLossCount": retained_render_loss_total,
            "maxBaselineChordSize": max_baseline_chord_size,
            "maxBoundaryChordSize": max_boundary_chord_size,
            "protectedPromotedHarmonicAttackCount": protected_harmonic_attack_count,
            "promotedHarmonicGuardViolationCount": promoted_harmonic_guard_violation_count,
            "primaryViolationCount": primary_violation_count,
            "unobservedPitchCount": unobserved_pitch_count,
            "unobservedAttackCount": 0,
            "attackIdentityChanged": False,
        },
        "changedAttacks": changed_attacks,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "newInferenceUsed": False,
        "paidModelRequired": False,
        "professionalReferenceUsed": False,
        "productionModified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json",
    )
    parser.add_argument(
        "--output",
        default="debug/v143-contextual-prune/precision-polyphony-boundary-replay.json",
    )
    args = parser.parse_args()
    product = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = build_report(product)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
