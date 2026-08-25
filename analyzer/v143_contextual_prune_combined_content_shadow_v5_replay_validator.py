#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import v143_contextual_prune_attack_shadow_v3_replay_validator as attack_v3

EXPECTED_ATTACK_VALIDATION_SHA256 = "039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892"
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_ELECTRIC_CHECKPOINT_SHA256 = "1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c"
EXPECTED_ATTACK_POLICY = "existing-exception-band-plus-electric-tabcnn-subfloor-consensus-v3"
EXPECTED_PRIMARY_POLICY = "v3-physical-harmonic-plus-electric-tabcnn-pairwise-consensus-v4"
POLICY = "attack-v3-plus-harmonic-primary-v4-combined-content-shadow-v5"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["measure"]), int(row["step"])


def validate(
    product: dict[str, Any],
    electric: dict[str, Any],
    attack_report: dict[str, Any],
    primary_report: dict[str, Any],
    attack_report_sha256: str,
) -> dict[str, Any]:
    if attack_report_sha256 != EXPECTED_ATTACK_VALIDATION_SHA256:
        raise ValueError("unexpected durable attack-v3 validation bytes")
    if attack_report.get("validationPassed") is not True or attack_report.get("policy") != EXPECTED_ATTACK_POLICY:
        raise ValueError("unexpected durable attack-v3 validation")
    if int(attack_report.get("shadowRetainedAttackCount") or 0) != 891:
        raise ValueError("unexpected attack-v3 retained count")
    if int(attack_report.get("rescuedAttackCount") or 0) != 166:
        raise ValueError("unexpected attack-v3 rescue count")
    if attack_report.get("freezeReady") is not False:
        raise ValueError("attack-v3 report unexpectedly freeze-ready")
    if primary_report.get("validationPassed") is not True or primary_report.get("policy") != EXPECTED_PRIMARY_POLICY:
        raise ValueError("unexpected durable primary-v4 validation")
    if int(primary_report.get("correctedPrimaryCount") or 0) != 34:
        raise ValueError("unexpected primary-v4 correction count")
    if primary_report.get("sourceAudioSha256") != EXPECTED_AUDIO_SHA256:
        raise ValueError("primary-v4 source audio mismatch")
    if primary_report.get("electricCheckpointSha256") != EXPECTED_ELECTRIC_CHECKPOINT_SHA256:
        raise ValueError("primary-v4 electric checkpoint mismatch")
    if primary_report.get("referenceFree") is not True or primary_report.get("professionalReferenceUsed") is not False:
        raise ValueError("invalid primary-v4 provenance")

    fresh_attack_report = attack_v3.validate(product, electric)
    if fresh_attack_report.get("validationPassed") is not True:
        raise ValueError("fresh attack-v3 replay failed")
    summary_fields = (
        "eligibleAttackCount",
        "baselineRetainedAttackCount",
        "exceptionBandRescueCount",
        "electricSubfloorRescueCount",
        "rescuedAttackCount",
        "shadowRetainedAttackCount",
        "remainingPrunedAttackCount",
        "shadowSelectedPitchCount",
        "shadowRenderedPitchCount",
        "shadowVoicingDropCount",
    )
    for field in summary_fields:
        if fresh_attack_report.get(field) != attack_report.get(field):
            raise ValueError(f"fresh/durable attack-v3 mismatch: {field}")

    replay = product.get("precisionReplayEvidence") or {}
    attacks = replay.get("eligibleAttacks") or []
    eligible = {_key(row): row for row in attacks}
    if len(eligible) != 984:
        raise ValueError("expected 984 eligible attacks")
    baseline = {key for key, row in eligible.items() if row.get("retained") is True}
    if len(baseline) != 725:
        raise ValueError("expected 725 baseline retained attacks")

    pitch_sets: dict[tuple[int, int], set[int]] = {}
    primaries: dict[tuple[int, int], int] = {}
    for key in sorted(baseline):
        row = eligible[key]
        selected = {int(c["midi"]) for c in row.get("candidates") or [] if c.get("selected") is True}
        primary = [int(c["midi"]) for c in row.get("candidates") or [] if c.get("primary") is True]
        if len(primary) != 1 or primary[0] not in selected:
            raise ValueError(f"invalid baseline pitch identity at {key}")
        pitch_sets[key] = selected
        primaries[key] = primary[0]

    rescue_rows = attack_report.get("rescuedAttackKeys") or []
    rescue_keys: set[tuple[int, int]] = set()
    for row in rescue_rows:
        key = _key(row)
        if key in rescue_keys or key in baseline or key not in eligible:
            raise ValueError(f"invalid rescued attack identity at {key}")
        selected = {int(x) for x in row.get("selectedMidis") or []}
        primary = int(row["primaryMidi"])
        observed = set(int(x) for x in eligible[key].get("candidateMidis") or [])
        if not selected or primary not in selected or not selected.issubset(observed):
            raise ValueError(f"invalid rescued pitch identity at {key}")
        rescue_keys.add(key)
        pitch_sets[key] = selected
        primaries[key] = primary
    if len(rescue_keys) != 166:
        raise ValueError(f"expected 166 rescued attack identities, got {len(rescue_keys)}")

    shadow = baseline | rescue_keys
    if len(shadow) != 891 or set(pitch_sets) != shadow or set(primaries) != shadow:
        raise ValueError("combined attack-v3 identity mismatch")

    corrections = primary_report.get("acceptedCorrectionKeys") or []
    correction_keys: set[tuple[int, int]] = set()
    transitions = Counter()
    reasons = Counter()
    for correction in corrections:
        key = _key(correction)
        if key in correction_keys:
            raise ValueError(f"duplicate primary-v4 correction at {key}")
        if key not in baseline:
            raise ValueError(f"primary-v4 correction is not a pre-existing retained attack: {key}")
        old = int(correction["oldPrimary"])
        new = int(correction["newPrimary"])
        if primaries[key] != old:
            raise ValueError(f"baseline primary mismatch at {key}: {primaries[key]} != {old}")
        observed = set(int(x) for x in eligible[key].get("candidateMidis") or [])
        if new not in observed:
            raise ValueError(f"primary-v4 correction invents pitch at {key}")
        before = set(pitch_sets[key])
        after = set(before)
        after.add(new)
        after.discard(old)
        after.add(new)
        pitch_sets[key] = after
        primaries[key] = new
        correction_keys.add(key)
        transitions[(old, new)] += 1
        reasons[str(correction.get("reason") or "")] += 1
    if len(correction_keys) != 34:
        raise ValueError(f"expected 34 primary-v4 corrections, got {len(correction_keys)}")
    if correction_keys & rescue_keys:
        raise ValueError("primary-v4 correction unexpectedly touches a rescued attack")

    invented: list[tuple[int, int]] = []
    invalid_primary: list[tuple[int, int]] = []
    unplayable_primary: list[tuple[int, int]] = []
    voicing_drops: list[dict[str, Any]] = []
    rendered_count = 0
    for key in sorted(shadow):
        row = eligible[key]
        observed = set(int(x) for x in row.get("candidateMidis") or [])
        selected = pitch_sets[key]
        primary = primaries[key]
        if not selected.issubset(observed):
            invented.append(key)
        if primary not in selected:
            invalid_primary.append(key)
        if attack_v3._resolve([primary]) is None:
            unplayable_primary.append(key)
        rendered = attack_v3._render_subset(row, selected, primary)
        rendered_count += len(rendered)
        if len(rendered) < len(selected):
            voicing_drops.append({
                "measure": key[0],
                "step": key[1],
                "primary": primary,
                "selected": sorted(selected),
                "rendered": sorted(rendered),
            })

    baseline_selected = sum(len(pitch_sets[key]) for key in baseline)
    rescued_selected = sum(len(pitch_sets[key]) for key in rescue_keys)
    total_selected = baseline_selected + rescued_selected
    baseline_rendered = sum(len(attack_v3._render_subset(eligible[key], pitch_sets[key], primaries[key])) for key in baseline)
    rescued_rendered = rendered_count - baseline_rendered
    total_drop_count = total_selected - rendered_count
    baseline_drop_count = baseline_selected - baseline_rendered
    rescued_drop_count = rescued_selected - rescued_rendered
    measures = {key[0] for key in shadow}

    expected_baseline_selected = int(primary_report.get("shadowSelectedPitchCount") or -1)
    expected_baseline_rendered = int(primary_report.get("shadowRenderedPitchCount") or -1)
    expected_baseline_drops = int(primary_report.get("shadowVoicingDropCount") or -1)
    expected_total_selected = int(attack_report.get("shadowSelectedPitchCount") or -1)
    expected_rescued_selected = int(attack_report.get("rescuedSelectedPitchCount") or -1)
    expected_rescued_rendered = int(attack_report.get("rescuedRenderedPitchCount") or -1)
    expected_rescued_drops = int(attack_report.get("rescuedVoicingDropCount") or -1)

    invariant_checks = {
        "retained891": len(shadow) == 891,
        "baselineV4SelectedMatches": baseline_selected == expected_baseline_selected == 970,
        "baselineV4RenderedMatches": baseline_rendered == expected_baseline_rendered == 967,
        "baselineV4VoicingDropsMatch": baseline_drop_count == expected_baseline_drops == 3,
        "rescuedSelectedUnchanged": rescued_selected == expected_rescued_selected == 244,
        "rescuedRenderedUnchanged": rescued_rendered == expected_rescued_rendered == 242,
        "rescuedVoicingDropsUnchanged": rescued_drop_count == expected_rescued_drops == 2,
        "combinedSelectedMatchesAttackV3": total_selected == expected_total_selected == 1214,
        "combinedRenderedExpected": rendered_count == 1209,
        "combinedVoicingDropsExpected": total_drop_count == 5,
        "fullMeasureCoverage": measures == set(range(1, 114)),
        "noInventedPitch": not invented,
        "validPrimaries": not invalid_primary,
        "playablePrimaries": not unplayable_primary,
        "v4TouchesOnlyBaseline": not (correction_keys & rescue_keys),
        "v4CorrectionCount34": len(correction_keys) == 34,
    }

    return {
        "schemaVersion": 1,
        "classification": "v143-reference-free-combined-content-shadow-v5",
        "policy": POLICY,
        "sourceAttackPolicy": EXPECTED_ATTACK_POLICY,
        "sourcePrimaryPolicy": EXPECTED_PRIMARY_POLICY,
        "attackV3ValidationSha256": attack_report_sha256,
        "sourceAudioSha256": EXPECTED_AUDIO_SHA256,
        "electricCheckpointSha256": EXPECTED_ELECTRIC_CHECKPOINT_SHA256,
        "eligibleAttackCount": len(eligible),
        "baselineRetainedAttackCount": len(baseline),
        "rescuedAttackCount": len(rescue_keys),
        "combinedRetainedAttackCount": len(shadow),
        "remainingPrunedAttackCount": len(eligible) - len(shadow),
        "primaryV4CorrectionCount": len(correction_keys),
        "primaryV4CorrectionsOnBaselineCount": len(correction_keys),
        "primaryV4CorrectionsOnRescuedCount": len(correction_keys & rescue_keys),
        "primaryCorrectionReasons": dict(sorted(reasons.items())),
        "primaryTransitions": {f"{old}->{new}": count for (old, new), count in sorted(transitions.items())},
        "baselineV4SelectedPitchCount": baseline_selected,
        "rescuedSelectedPitchCount": rescued_selected,
        "combinedSelectedPitchCount": total_selected,
        "baselineV4RenderedPitchCount": baseline_rendered,
        "rescuedRenderedPitchCount": rescued_rendered,
        "combinedRenderedPitchCount": rendered_count,
        "baselineV4VoicingDropCount": baseline_drop_count,
        "rescuedVoicingDropCount": rescued_drop_count,
        "combinedVoicingDropCount": total_drop_count,
        "combinedVoicingDropAttacks": voicing_drops,
        "baselinePrimaryMidi64CountAfterV4": sum(primaries[key] == 64 for key in baseline),
        "rescuedPrimaryMidi64Count": sum(primaries[key] == 64 for key in rescue_keys),
        "combinedPrimaryMidi64Count": sum(value == 64 for value in primaries.values()),
        "measureCoverageCount": len(measures),
        "missingMeasures": sorted(set(range(1, 114)) - measures),
        "inventedPitchCount": len(invented),
        "invalidPrimaryCount": len(invalid_primary),
        "unplayablePrimaryCount": len(unplayable_primary),
        "newNumericThresholdIntroduced": False,
        "newInferenceUsed": False,
        "addsUnobservedAttack": False,
        "addsUnobservedPitch": False,
        "relocatesAttack": False,
        "downstreamTechniqueSustainRecomputed": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "freezeReady": False,
        "invariantChecks": invariant_checks,
        "validationPassed": all(invariant_checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("electric_evidence", type=Path)
    parser.add_argument("attack_v3_validation", type=Path)
    parser.add_argument("primary_v4_validation", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    attack_sha = _sha256(args.attack_v3_validation)
    report = validate(
        json.loads(args.product.read_text()),
        json.loads(args.electric_evidence.read_text()),
        json.loads(args.attack_v3_validation.read_text()),
        json.loads(args.primary_v4_validation.read_text()),
        attack_sha,
    )
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if report["validationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
