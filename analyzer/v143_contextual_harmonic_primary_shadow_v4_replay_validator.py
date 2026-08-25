#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_CHECKPOINT_SHA256 = "1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c"
EXPECTED_PROBE = "v143-electric-guitar-robust-tabcnn-exact-grid"
POLICY = "v3-physical-harmonic-plus-electric-tabcnn-pairwise-consensus-v4"


def _candidate_map(attack: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(item["midi"]): item for item in attack.get("candidates") or []}


def _legal_positions(midi: int) -> list[tuple[int, int]]:
    return [(i, int(midi) - open_midi) for i, open_midi in enumerate(OPEN_MIDI_HIGH_TO_LOW) if 0 <= int(midi) - open_midi <= MAX_FRET]


def _resolve(midis: list[int]) -> dict[int, tuple[int, int]] | None:
    ordered = tuple(sorted(set(int(x) for x in midis)))
    if not ordered or len(ordered) > 6 or ordered[-1] - ordered[0] > 28:
        return None
    sets = [_legal_positions(midi) for midi in ordered]
    if any(not values for values in sets):
        return None
    best_key = None
    best_positions = None
    for positions in product(*sets):
        strings = tuple(item[0] for item in positions)
        if len(set(strings)) != len(strings) or any(strings[i] <= strings[i + 1] for i in range(len(strings) - 1)):
            continue
        frets = tuple(item[1] for item in positions)
        key = (max(frets) - min(frets), max(frets), sum(frets), sum(fret > 12 for fret in frets), strings, frets)
        if best_key is None or key < best_key:
            best_key, best_positions = key, positions
    if best_positions is None:
        return None
    return {midi: pos for midi, pos in zip(ordered, best_positions)}


def _render_subset(attack: dict[str, Any], selected: set[int], primary: int) -> list[int]:
    cmap = _candidate_map(attack)
    others = sorted(
        (m for m in selected if m != primary),
        key=lambda midi: (-float(cmap[midi]["score"]), -float(cmap[midi]["attack"]), -float(cmap[midi]["body"]), int(midi)),
    )
    rendered = [int(primary)]
    if _resolve(rendered) is None:
        return []
    for midi in others:
        trial = rendered + [int(midi)]
        if _resolve(trial) is not None:
            rendered = trial
    return rendered


def validate(product: dict[str, Any], v3: dict[str, Any], electric: dict[str, Any]) -> dict[str, Any]:
    if electric.get("probe") != EXPECTED_PROBE:
        raise ValueError("unexpected electric probe")
    source = electric.get("sourceAudio") or {}
    checkpoint = electric.get("checkpoint") or {}
    if source.get("approvedFixture") is not True or source.get("sha256") != EXPECTED_AUDIO_SHA256:
        raise ValueError("electric probe is not bound to exact approved fixture")
    if checkpoint.get("sha256") != EXPECTED_CHECKPOINT_SHA256:
        raise ValueError("unexpected electric checkpoint")
    if electric.get("referenceFree") is not True or electric.get("professionalReferenceUsed") is not False:
        raise ValueError("invalid electric probe provenance")
    if v3.get("validationPassed") is not True or int(v3.get("correctedPrimaryCount") or 0) != 43:
        raise ValueError("unexpected v3 validation")

    comparisons = {
        (int(item["measure"]), int(item["step"])): item
        for item in electric.get("v3CorrectionComparisons") or []
    }
    v3_corrections = {
        (int(item["measure"]), int(item["step"])): item
        for item in v3.get("correctionKeys") or []
    }
    if set(comparisons) != set(v3_corrections):
        raise ValueError("electric/v3 correction key mismatch")
    for key, correction in v3_corrections.items():
        comparison = comparisons[key]
        if int(comparison["oldPrimary"]) != int(correction["oldPrimary"]) or int(comparison["newPrimary"]) != int(correction["newPrimary"]):
            raise ValueError(f"electric/v3 identity mismatch at {key}")
        expected_preference = float(comparison["newMaxLegalProbability"]) > float(comparison["oldMaxLegalProbability"])
        if bool(comparison.get("newPreferred")) != expected_preference:
            raise ValueError(f"electric pairwise preference mismatch at {key}")

    evidence = product.get("precisionReplayEvidence") or {}
    retained = [item for item in evidence.get("eligibleAttacks") or [] if bool(item.get("retained"))]
    by_key = {(int(item["measure"]), int(item["step"])): item for item in retained}
    primary = {}
    selected = {}
    for key, attack in by_key.items():
        primaries = [int(item["midi"]) for item in attack.get("candidates") or [] if bool(item.get("primary"))]
        if len(primaries) != 1:
            raise RuntimeError(f"expected one replay primary at {key}")
        primary[key] = primaries[0]
        selected[key] = {int(item["midi"]) for item in attack.get("candidates") or [] if bool(item.get("selected"))}

    output_primary = dict(primary)
    output_selected = {key: set(values) for key, values in selected.items()}
    accepted = []
    rejected = []
    for key in sorted(v3_corrections):
        correction = v3_corrections[key]
        comparison = comparisons[key]
        row = {
            "measure": key[0],
            "step": key[1],
            "oldPrimary": int(correction["oldPrimary"]),
            "newPrimary": int(correction["newPrimary"]),
            "reason": str(correction.get("reason") or ""),
            "oldMaxLegalProbability": float(comparison["oldMaxLegalProbability"]),
            "newMaxLegalProbability": float(comparison["newMaxLegalProbability"]),
            "probabilityDelta": float(comparison["newMaxLegalProbability"]) - float(comparison["oldMaxLegalProbability"]),
            "modelChoosesOld": bool(comparison.get("modelChoosesOld")),
            "modelChoosesNew": bool(comparison.get("modelChoosesNew")),
        }
        if bool(comparison["newPreferred"]):
            old = row["oldPrimary"]
            new = row["newPrimary"]
            if primary[key] != old:
                raise ValueError(f"baseline primary mismatch at {key}")
            before = set(output_selected[key])
            after = set(before)
            after.add(new)
            after.discard(old)
            after.add(new)
            output_primary[key] = new
            output_selected[key] = after
            row["oldSelected"] = sorted(before)
            row["newSelected"] = sorted(after)
            accepted.append(row)
        else:
            rejected.append(row)

    invented = []
    invalid_primary = []
    unplayable_primary = []
    baseline_rendered = 0
    shadow_rendered = 0
    voicing_drops = []
    for key, attack in by_key.items():
        observed = set(int(value) for value in attack.get("candidateMidis") or [])
        if not output_selected[key].issubset(observed):
            invented.append(key)
        if output_primary[key] not in output_selected[key]:
            invalid_primary.append(key)
        if _resolve([output_primary[key]]) is None:
            unplayable_primary.append(key)
        base_render = _render_subset(attack, selected[key], primary[key])
        shadow_render = _render_subset(attack, output_selected[key], output_primary[key])
        baseline_rendered += len(base_render)
        shadow_rendered += len(shadow_render)
        if len(shadow_render) < len(output_selected[key]):
            voicing_drops.append({
                "measure": key[0], "step": key[1], "primary": output_primary[key],
                "selected": sorted(output_selected[key]), "rendered": sorted(shadow_render),
            })

    transitions = Counter((item["oldPrimary"], item["newPrimary"]) for item in accepted)
    reasons = Counter(item["reason"] for item in accepted)
    intervals = Counter(item["oldPrimary"] - item["newPrimary"] for item in accepted)
    return {
        "schemaVersion": 1,
        "policy": POLICY,
        "sourcePrimaryPolicy": str(v3.get("policy") or "local-or-two-view-extra-harmonic-primary-v3"),
        "externalConsensusModel": "robust electric-guitar TabCNN trained with GuitarProFX",
        "externalConsensusDecision": "strict pairwise new-lower max-legal probability > old-upper max-legal probability",
        "newNumericThresholdIntroduced": False,
        "inputRetainedAttackCount": len(by_key),
        "outputRetainedAttackCount": len(by_key),
        "v3ProposedCorrectionCount": len(v3_corrections),
        "correctedPrimaryCount": len(accepted),
        "rejectedV3CorrectionCount": len(rejected),
        "correctionReasons": dict(sorted(reasons.items())),
        "harmonicIntervals": dict(sorted(intervals.items())),
        "primaryTransitions": {f"{old}->{new}": count for (old, new), count in sorted(transitions.items())},
        "oldPrimaryMidi64Count": sum(value == 64 for value in primary.values()),
        "newPrimaryMidi64Count": sum(value == 64 for value in output_primary.values()),
        "baselineSelectedPitchCount": sum(len(values) for values in selected.values()),
        "shadowSelectedPitchCount": sum(len(values) for values in output_selected.values()),
        "baselineRenderedPitchCount": baseline_rendered,
        "shadowRenderedPitchCount": shadow_rendered,
        "shadowVoicingDropCount": sum(len(output_selected[key]) - len(_render_subset(by_key[key], output_selected[key], output_primary[key])) for key in by_key),
        "shadowVoicingDropAttacks": voicing_drops,
        "acceptedCorrections": accepted,
        "rejectedCorrections": rejected,
        "changedAttackIdentity": False,
        "inventedPitchCount": len(invented),
        "invalidPrimaryCount": len(invalid_primary),
        "unplayablePrimaryCount": len(unplayable_primary),
        "sourceAudioSha256": EXPECTED_AUDIO_SHA256,
        "electricCheckpointSha256": EXPECTED_CHECKPOINT_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "validationPassed": bool(by_key) and not invented and not invalid_primary and not unplayable_primary and len(accepted) == 34,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("v3_validation", type=Path)
    parser.add_argument("electric_probe", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(json.loads(args.product.read_text()), json.loads(args.v3_validation.read_text()), json.loads(args.electric_probe.read_text()))
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
    return 0 if report["validationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
