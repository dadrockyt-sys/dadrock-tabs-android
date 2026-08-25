#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

ATTACK_RATIO_FLOOR = 0.70
ATTACK_EXCEPTION_FLOOR = 0.60
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
FUNDAMENTAL_MIN_RAW_RATIO = 0.55
SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
HARMONIC_INTERVAL_WEIGHTS = {12: 0.35, 19: 0.25, 24: 0.20, 28: 0.12, 31: 0.10, 36: 0.08}
OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24
EXPECTED_POLICY = "envelope-balanced-secondary-v2"
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_ELECTRIC_CHECKPOINT_SHA256 = "1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c"
POLICY = "existing-exception-band-plus-electric-tabcnn-subfloor-consensus-v3"


def _key(a: dict[str, Any]) -> tuple[int, int]:
    return int(a["measure"]), int(a["step"])


def _candidates(a: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(c["midi"]): c for c in a.get("candidates") or []}


def _best(a: dict[str, Any]) -> dict[str, Any] | None:
    cs = _candidates(a)
    if not cs:
        return None
    return max(cs.values(), key=lambda c: (float(c["score"]), float(c["attack"]), -int(c["midi"])))


def _positive_best(a: dict[str, Any]) -> bool:
    c = _best(a)
    return bool(c and float(c["attack"]) > POSITIVE_ATTACK_FLOOR and float(c["body"]) > POSITIVE_BODY_FLOOR)


def _ratio(a: dict[str, Any]) -> float:
    c = _best(a)
    if c is None:
        return 0.0
    return max(0.0, float(c["attack"])) / max(1e-6, float(c["body"]))


def _positive_candidates(a: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        midi: c for midi, c in _candidates(a).items()
        if float(c["attack"]) > POSITIVE_ATTACK_FLOOR and float(c["body"]) > POSITIVE_BODY_FLOOR
    }


def _harmonic_family_score(midi: int, positive: dict[int, dict[str, Any]]) -> float:
    base = positive[midi]
    score = float(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = positive.get(midi + interval)
        if upper is None:
            continue
        score += weight * max(0.0, min(float(base["score"]), float(upper["score"])))
    return score


def _precision_pitch_set_v2(a: dict[str, Any]) -> tuple[set[int], int, bool]:
    original = sorted(_candidates(a))
    if not original:
        raise ValueError("attack has no candidate MIDIs")
    positive = _positive_candidates(a)
    if not positive:
        strongest = max(original, key=lambda midi: (float(_candidates(a)[midi]["score"]), float(_candidates(a)[midi]["attack"]), -midi))
        return set(original), int(strongest), False

    strongest_raw = max(positive, key=lambda midi: (float(positive[midi]["score"]), float(positive[midi]["attack"]), -midi))
    strongest = positive[strongest_raw]
    strongest_score = max(1e-6, float(strongest["score"]))
    strongest_attack = max(1e-6, float(strongest["attack"]))
    strongest_body = max(1e-6, float(strongest["body"]))

    family_scores = {midi: _harmonic_family_score(midi, positive) for midi in positive}
    primary = max(family_scores, key=lambda midi: (family_scores[midi], float(positive[midi]["attack"]), -midi))
    if float(positive[primary]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * strongest_score:
        primary = strongest_raw

    kept = {int(primary)}
    for midi, item in sorted(positive.items(), key=lambda pair: (float(pair[1]["score"]), float(pair[1]["attack"]), -pair[0]), reverse=True):
        if midi == primary:
            continue
        harmonic = midi - primary in HARMONIC_INTERVAL_WEIGHTS
        floor = HARMONIC_SECONDARY_RAW_RATIO if harmonic else SECONDARY_RAW_RATIO
        passes = (
            float(item["score"]) / strongest_score >= floor,
            float(item["attack"]) / strongest_attack >= floor,
            float(item["body"]) / strongest_body >= floor,
        )
        if sum(bool(v) for v in passes) >= (3 if harmonic else 2):
            kept.add(int(midi))

    promoted = int(primary) != int(strongest_raw)
    if promoted and strongest_raw - int(primary) in HARMONIC_INTERVAL_WEIGHTS and strongest_raw in kept:
        kept.remove(int(strongest_raw))
    kept.add(int(primary))
    return kept, int(primary), promoted


def _legal_positions(midi: int) -> list[tuple[int, int]]:
    return [(i, int(midi) - open_midi) for i, open_midi in enumerate(OPEN_MIDI_HIGH_TO_LOW) if 0 <= int(midi) - open_midi <= MAX_FRET]


def _resolve(midis: list[int] | set[int]) -> dict[int, tuple[int, int]] | None:
    ordered = tuple(sorted(set(int(x) for x in midis)))
    if not ordered or len(ordered) > 6 or ordered[-1] - ordered[0] > 28:
        return None
    sets = [_legal_positions(midi) for midi in ordered]
    if any(not values for values in sets):
        return None
    best_key = None
    best_positions = None
    for positions in product(*sets):
        strings = tuple(p[0] for p in positions)
        if len(set(strings)) != len(strings):
            continue
        if any(strings[i] <= strings[i+1] for i in range(len(strings)-1)):
            continue
        frets = tuple(p[1] for p in positions)
        key = (max(frets)-min(frets), max(frets), sum(frets), sum(f>12 for f in frets), strings, frets)
        if best_key is None or key < best_key:
            best_key, best_positions = key, positions
    if best_positions is None:
        return None
    return {midi: pos for midi, pos in zip(ordered, best_positions)}


def _render_subset(a: dict[str, Any], selected: set[int], primary: int) -> list[int]:
    cs = _candidates(a)
    if primary not in selected:
        return []
    others = sorted((m for m in selected if m != primary), key=lambda midi: (-float(cs[midi]["score"]), -float(cs[midi]["attack"]), -float(cs[midi]["body"]), midi))
    rendered = [int(primary)]
    if _resolve(rendered) is None:
        return []
    for midi in others:
        trial = rendered + [int(midi)]
        if _resolve(trial) is not None:
            rendered = trial
    return rendered


def validate(product: dict[str, Any], electric: dict[str, Any]) -> dict[str, Any]:
    replay = product.get("precisionReplayEvidence") or {}
    if replay.get("schemaVersion") != 2 or replay.get("policy") != EXPECTED_POLICY:
        raise ValueError("unexpected replay schema/policy")
    for field in ("attackPolicyReplayReady", "sourceViewEvidenceReady", "precisionStrengthRecomputeReady", "zeroValuePreservationReady"):
        if replay.get(field) is not True:
            raise ValueError(f"replay not ready: {field}")
    if replay.get("referenceFree") is not True or replay.get("professionalReferenceUsed") is not False:
        raise ValueError("invalid replay provenance")
    if electric.get("probe") != "v143-electric-guitar-robust-tabcnn-exact-grid":
        raise ValueError("unexpected electric evidence")
    if (electric.get("sourceAudio") or {}).get("sha256") != EXPECTED_AUDIO_SHA256 or (electric.get("sourceAudio") or {}).get("approvedFixture") is not True:
        raise ValueError("electric evidence is not bound to approved audio")
    if (electric.get("checkpoint") or {}).get("sha256") != EXPECTED_ELECTRIC_CHECKPOINT_SHA256:
        raise ValueError("unexpected electric checkpoint")
    if electric.get("newNumericThresholdIntroduced") is not False or electric.get("professionalReferenceUsed") is not False:
        raise ValueError("invalid electric evidence provenance")

    attacks = replay.get("eligibleAttacks") or []
    eligible = {_key(a): a for a in attacks}
    if len(eligible) != 984:
        raise ValueError(f"expected 984 eligible attacks, got {len(eligible)}")
    baseline = {k for k,a in eligible.items() if a.get("retained") is True}
    if len(baseline) != 725:
        raise ValueError(f"expected 725 baseline attacks, got {len(baseline)}")

    evidence_keys: dict[tuple[int,int], dict[str,Any]] = {}
    for row in electric.get("keys") or []:
        key = (int(row["measure"]), int(row["step"]))
        if key in evidence_keys:
            raise ValueError(f"duplicate electric evidence {key}")
        evidence_keys[key] = row
    if len(evidence_keys) != 43 or int(electric.get("subfloorCandidateOverlapCount") or 0) != 43:
        raise ValueError("expected 43 electric subfloor consensus attacks")

    exception_rescues = set()
    subfloor_rescues = set()
    for key, a in eligible.items():
        if key in baseline or not _positive_best(a):
            continue
        ratio = _ratio(a)
        if ATTACK_EXCEPTION_FLOOR <= ratio < ATTACK_RATIO_FLOOR:
            exception_rescues.add(key)
        elif ratio < ATTACK_EXCEPTION_FLOOR and key in evidence_keys:
            row = evidence_keys[key]
            overlap = set(int(x) for x in row.get("overlapMidis") or [])
            observed = set(int(x) for x in a.get("candidateMidis") or [])
            if not overlap or not overlap.issubset(observed):
                raise ValueError(f"invalid overlap evidence at {key}")
            subfloor_rescues.add(key)

    if len(exception_rescues) != 123:
        raise ValueError(f"expected 123 exception rescues, got {len(exception_rescues)}")
    if subfloor_rescues != set(evidence_keys):
        missing = sorted(set(evidence_keys)-subfloor_rescues)
        extra = sorted(subfloor_rescues-set(evidence_keys))
        raise ValueError(f"subfloor evidence mismatch missing={missing[:5]} extra={extra[:5]}")

    shadow = baseline | exception_rescues | subfloor_rescues
    if len(shadow) != 891:
        raise ValueError(f"expected 891 shadow attacks, got {len(shadow)}")

    pitch_sets: dict[tuple[int,int], set[int]] = {}
    primaries: dict[tuple[int,int], int] = {}
    promotions = 0
    for key in sorted(shadow):
        a = eligible[key]
        if key in baseline:
            selected = {int(c["midi"]) for c in a.get("candidates") or [] if c.get("selected") is True}
            p = [int(c["midi"]) for c in a.get("candidates") or [] if c.get("primary") is True]
            if len(p) != 1 or p[0] not in selected:
                raise ValueError(f"invalid baseline pitch identity at {key}")
            pitch_sets[key] = selected
            primaries[key] = p[0]
        else:
            selected, primary, promoted = _precision_pitch_set_v2(a)
            pitch_sets[key] = selected
            primaries[key] = primary
            promotions += int(promoted)

    invented = []
    invalid_primary = []
    unplayable_primary = []
    render_drops = []
    rendered_count = 0
    grid_collisions = len(shadow) - len(set(shadow))
    for key in sorted(shadow):
        a = eligible[key]
        observed = set(int(x) for x in a.get("candidateMidis") or [])
        if not pitch_sets[key].issubset(observed):
            invented.append(key)
        if primaries[key] not in pitch_sets[key]:
            invalid_primary.append(key)
        if _resolve([primaries[key]]) is None:
            unplayable_primary.append(key)
        rendered = _render_subset(a, pitch_sets[key], primaries[key])
        rendered_count += len(rendered)
        if len(rendered) < len(pitch_sets[key]):
            render_drops.append({
                "measure": key[0], "step": key[1], "primary": primaries[key],
                "selected": sorted(pitch_sets[key]), "rendered": sorted(rendered),
            })

    selected_count = sum(len(v) for v in pitch_sets.values())
    baseline_selected = sum(len(pitch_sets[k]) for k in baseline)
    rescued_selected = selected_count - baseline_selected
    baseline_rendered = sum(len(_render_subset(eligible[k], pitch_sets[k], primaries[k])) for k in baseline)
    rescued_rendered = rendered_count - baseline_rendered

    measures = {k[0] for k in shadow}
    expected_measures = set(range(1,114))
    remaining = set(eligible) - shadow
    remaining_positive = sum(1 for k in remaining if _positive_best(eligible[k]))
    remaining_nonpositive = len(remaining) - remaining_positive

    reason_counts = Counter()
    for key in exception_rescues:
        reason_counts["existing-exception-band"] += 1
    for key in subfloor_rescues:
        reason_counts["electric-tabcnn-candidate-overlap-below-0.60"] += 1

    rescue_pitch_distribution = Counter(len(pitch_sets[k]) for k in (exception_rescues|subfloor_rescues))
    subfloor_group_counts = Counter(str(evidence_keys[k].get("group") or "") for k in subfloor_rescues)
    result = {
        "schemaVersion": 1,
        "classification": "v143-reference-free-electric-consensus-attack-shadow-v3",
        "policy": POLICY,
        "sourcePitchPolicy": EXPECTED_POLICY,
        "eligibleAttackCount": len(eligible),
        "baselineRetainedAttackCount": len(baseline),
        "baselinePrunedAttackCount": len(eligible)-len(baseline),
        "exceptionBandRescueCount": len(exception_rescues),
        "electricSubfloorRescueCount": len(subfloor_rescues),
        "rescuedAttackCount": len(shadow-baseline),
        "shadowRetainedAttackCount": len(shadow),
        "remainingPrunedAttackCount": len(remaining),
        "remainingPositiveAttackCount": remaining_positive,
        "remainingNonpositiveAttackCount": remaining_nonpositive,
        "reasonCounts": dict(sorted(reason_counts.items())),
        "electricSubfloorSourceGroups": dict(sorted(subfloor_group_counts.items())),
        "baselineSelectedPitchCount": baseline_selected,
        "rescuedSelectedPitchCount": rescued_selected,
        "shadowSelectedPitchCount": selected_count,
        "baselineRenderedPitchCount": baseline_rendered,
        "rescuedRenderedPitchCount": rescued_rendered,
        "shadowRenderedPitchCount": rendered_count,
        "shadowVoicingDropCount": sum(len(pitch_sets[(x["measure"],x["step"])]) - len(x["rendered"]) for x in render_drops),
        "rescuedVoicingDropCount": rescued_selected - rescued_rendered,
        "baselineVoicingDropCount": baseline_selected - baseline_rendered,
        "shadowVoicingDropAttacks": render_drops,
        "rescuedPitchCountDistribution": {str(k):v for k,v in sorted(rescue_pitch_distribution.items())},
        "newRescueFundamentalPromotionCount": promotions,
        "inventedPitchCount": len(invented),
        "invalidPrimaryCount": len(invalid_primary),
        "unplayablePrimaryCount": len(unplayable_primary),
        "gridIdentityCollisionCount": grid_collisions,
        "measureCoverageCount": len(measures),
        "missingMeasures": sorted(expected_measures-measures),
        "electricEvidenceAttackCount": len(evidence_keys),
        "electricEvidenceShaBinding": {
            "approvedAudioSha256": EXPECTED_AUDIO_SHA256,
            "checkpointSha256": EXPECTED_ELECTRIC_CHECKPOINT_SHA256,
        },
        "constantsReusedWithoutChange": {
            "positiveAttackFloor": POSITIVE_ATTACK_FLOOR,
            "positiveBodyFloor": POSITIVE_BODY_FLOOR,
            "legacyRatioFloor": ATTACK_RATIO_FLOOR,
            "legacyRatioExceptionFloor": ATTACK_EXCEPTION_FLOOR,
            "fundamentalMinRawRatio": FUNDAMENTAL_MIN_RAW_RATIO,
            "secondaryRawRatio": SECONDARY_RAW_RATIO,
            "harmonicSecondaryRawRatio": HARMONIC_SECONDARY_RAW_RATIO,
            "harmonicIntervals": sorted(HARMONIC_INTERVAL_WEIGHTS),
        },
        "newNumericThresholdIntroduced": False,
        "addsUnobservedAttack": False,
        "addsUnobservedPitch": False,
        "relocatesAttack": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "newInferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "downstreamTechniqueSustainRecomputed": False,
        "freezeReady": False,
        "validationPassed": (
            len(shadow)==891 and len(exception_rescues)==123 and len(subfloor_rescues)==43
            and not invented and not invalid_primary and not unplayable_primary
            and grid_collisions==0 and measures==expected_measures
        ),
        "rescuedAttackKeys": [
            {"measure":k[0],"step":k[1],"reason":"existing-exception-band" if k in exception_rescues else "electric-tabcnn-candidate-overlap-below-0.60",
             "transientRatio":_ratio(eligible[k]),"selectedMidis":sorted(pitch_sets[k]),"primaryMidi":primaries[k],
             "electricOverlapMidis":sorted(int(x) for x in evidence_keys[k].get("overlapMidis") or []) if k in evidence_keys else []}
            for k in sorted(shadow-baseline)
        ],
    }
    return result


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("product",type=Path)
    p.add_argument("electric_evidence",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=validate(json.loads(args.product.read_text()),json.loads(args.electric_evidence.read_text()))
    text=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output: args.output.write_text(text)
    print(text,end="")
    return 0 if result["validationPassed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
