from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

HARMONIC_INTERVAL_WEIGHTS = {12: 0.35, 19: 0.25, 24: 0.20, 28: 0.12, 31: 0.10, 36: 0.08}
LOCAL_RADIUS_STEPS = 2
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
FUNDAMENTAL_MIN_RAW_RATIO = 0.55
OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24


def _candidate_map(attack: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(item["midi"]): item for item in attack.get("candidates") or []}


def _positive(attack: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {midi: item for midi, item in _candidate_map(attack).items() if float(item["attack"]) > POSITIVE_ATTACK_FLOOR and float(item["body"]) > POSITIVE_BODY_FLOOR}


def _strongest_raw(attack: dict[str, Any]) -> int | None:
    positive = _positive(attack)
    if not positive:
        return None
    return int(max(positive, key=lambda midi: (float(positive[midi]["score"]), float(positive[midi]["attack"]), -int(midi))))


def _family_score(midi: int, positive: dict[int, dict[str, Any]]) -> float:
    base = positive[midi]
    score = float(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = positive.get(int(midi) + int(interval))
        if upper is not None:
            score += float(weight) * max(0.0, min(float(base["score"]), float(upper["score"])))
    return float(score)


def _view_evidence(item: dict[str, Any], view_name: str) -> dict[str, float]:
    view = item.get(view_name) or {}
    attack = float(view.get("attack", -99.0))
    early = float(view.get("early", -99.0))
    sustain = float(view.get("sustain", -99.0))
    body = max(early, sustain)
    continuity = min(early, sustain)
    return {"attack": attack, "early": early, "sustain": sustain, "body": body, "continuity": continuity, "score": attack + 0.65 * body + 0.15 * continuity}


def _positive_view(attack: dict[str, Any], view_name: str) -> dict[int, dict[str, float]]:
    output = {}
    for item in attack.get("candidates") or []:
        midi = int(item["midi"])
        evidence = _view_evidence(item, view_name)
        if evidence["attack"] > POSITIVE_ATTACK_FLOOR and evidence["body"] > POSITIVE_BODY_FLOOR:
            output[midi] = evidence
    return output


def _harmonic_support_count(midi: int, positive: dict[int, Any]) -> int:
    return sum(1 for interval in HARMONIC_INTERVAL_WEIGHTS if int(midi) + int(interval) in positive)


def _local_lower(key: tuple[int, int], current: int, primary: dict[tuple[int, int], int], positive: dict[int, dict[str, Any]]) -> tuple[int | None, int]:
    measure, step = key
    support = Counter()
    for other_key, other_primary in primary.items():
        if other_key == key or other_key[0] != measure or abs(other_key[1] - step) > LOCAL_RADIUS_STEPS:
            continue
        lower = int(other_primary)
        if lower not in positive or current - lower not in HARMONIC_INTERVAL_WEIGHTS:
            continue
        if float(positive[lower]["score"]) < FUNDAMENTAL_MIN_RAW_RATIO * max(1e-6, float(positive[current]["score"])):
            continue
        support[lower] += 1
    if not support:
        return None, 0
    lower = max(support, key=lambda midi: (int(support[midi]), _family_score(int(midi), positive), float(positive[int(midi)]["score"]), float(positive[int(midi)]["attack"]), -int(midi)))
    return int(lower), int(support[lower])


def _two_view_lower(attack: dict[str, Any], current: int, positive: dict[int, dict[str, Any]]) -> tuple[int | None, dict[str, Any] | None]:
    view_a = _positive_view(attack, "viewA")
    view_b = _positive_view(attack, "viewB")
    if current not in view_a or current not in view_b:
        return None, None
    strongest_a = max(view_a, key=lambda midi: (view_a[midi]["score"], view_a[midi]["attack"], -int(midi)))
    strongest_b = max(view_b, key=lambda midi: (view_b[midi]["score"], view_b[midi]["attack"], -int(midi)))
    strongest_a_score = max(1e-6, float(view_a[strongest_a]["score"]))
    strongest_b_score = max(1e-6, float(view_b[strongest_b]["score"]))
    current_a_count = _harmonic_support_count(current, view_a)
    current_b_count = _harmonic_support_count(current, view_b)
    candidates = []
    for lower in sorted(set(view_a).intersection(view_b)):
        if lower >= current or current - lower not in HARMONIC_INTERVAL_WEIGHTS or lower not in positive:
            continue
        ratio_a = float(view_a[lower]["score"]) / strongest_a_score
        ratio_b = float(view_b[lower]["score"]) / strongest_b_score
        if ratio_a < FUNDAMENTAL_MIN_RAW_RATIO or ratio_b < FUNDAMENTAL_MIN_RAW_RATIO:
            continue
        lower_a_count = _harmonic_support_count(lower, view_a)
        lower_b_count = _harmonic_support_count(lower, view_b)
        additional_a = any(lower + interval in view_a and lower + interval != current for interval in HARMONIC_INTERVAL_WEIGHTS)
        additional_b = any(lower + interval in view_b and lower + interval != current for interval in HARMONIC_INTERVAL_WEIGHTS)
        if not additional_a or not additional_b:
            continue
        if lower_a_count <= current_a_count or lower_b_count <= current_b_count:
            continue
        candidates.append((int(lower), int(lower_a_count), int(lower_b_count), float(ratio_a), float(ratio_b)))
    if not candidates:
        return None, None
    winner = max(candidates, key=lambda row: (min(row[1], row[2]), max(row[1], row[2]), _family_score(row[0], positive), float(positive[row[0]]["score"]), float(positive[row[0]]["attack"]), -row[0]))
    return winner[0], {
        "lowerViewAHarmonicSupportCount": winner[1],
        "lowerViewBHarmonicSupportCount": winner[2],
        "currentViewAHarmonicSupportCount": current_a_count,
        "currentViewBHarmonicSupportCount": current_b_count,
        "lowerViewAStrongestScoreRatio": winner[3],
        "lowerViewBStrongestScoreRatio": winner[4],
    }


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
    others = sorted((m for m in selected if m != primary), key=lambda midi: (-float(cmap[midi]["score"]), -float(cmap[midi]["attack"]), -float(cmap[midi]["body"]), int(midi)))
    rendered = [int(primary)]
    if _resolve(rendered) is None:
        return []
    for midi in others:
        trial = rendered + [int(midi)]
        if _resolve(trial) is not None:
            rendered = trial
    return rendered


def validate(product: dict[str, Any]) -> dict[str, Any]:
    evidence = product.get("precisionReplayEvidence") or {}
    attacks = [item for item in evidence.get("eligibleAttacks") or [] if bool(item.get("retained"))]
    by_key = {(int(item["measure"]), int(item["step"])): item for item in attacks}
    primary = {}
    selected = {}
    for key, attack in by_key.items():
        primaries = [int(item["midi"]) for item in attack.get("candidates") or [] if bool(item.get("primary"))]
        if len(primaries) != 1:
            raise RuntimeError(f"Expected one replay primary at {key}, got {primaries}")
        primary[key] = primaries[0]
        selected[key] = {int(item["midi"]) for item in attack.get("candidates") or [] if bool(item.get("selected"))}

    output_primary = dict(primary)
    output_selected = {key: set(values) for key, values in selected.items()}
    corrections = []
    reason_counts = Counter()

    for key in sorted(by_key):
        attack = by_key[key]
        current = int(primary[key])
        if _strongest_raw(attack) != current:
            continue
        positive = _positive(attack)
        if current not in positive:
            continue
        local, local_count = _local_lower(key, current, primary, positive)
        two_view, two_view_diag = _two_view_lower(attack, current, positive)
        if local is not None:
            lower = int(local)
            reason = "local+two-view-extra-harmonic-support" if two_view == local else "same-measure-local-primary-support"
        elif two_view is not None:
            lower = int(two_view)
            reason = "two-view-extra-harmonic-support"
        else:
            continue

        before = set(output_selected[key])
        after = set(before)
        after.add(lower)
        after.discard(current)
        after.add(lower)
        output_primary[key] = lower
        output_selected[key] = after
        reason_counts[reason] += 1
        row = {
            "measure": key[0], "step": key[1], "oldPrimary": current, "newPrimary": lower,
            "harmonicInterval": current - lower, "reason": reason,
            "neighborSupportCount": int(local_count if local == lower else 0),
            "oldSelected": sorted(before), "newSelected": sorted(after),
            "lowerAttack": float(positive[lower]["attack"]), "lowerBody": float(positive[lower]["body"]),
            "lowerScore": float(positive[lower]["score"]), "oldPrimaryScore": float(positive[current]["score"]),
        }
        if two_view == lower and two_view_diag:
            row.update(two_view_diag)
        corrections.append(row)

    invented, invalid_primary, unplayable_primary = [], [], []
    baseline_rendered = shadow_rendered = 0
    shadow_voicing_drops = []
    for key, attack in by_key.items():
        observed = set(int(value) for value in attack.get("candidateMidis") or [])
        if not output_selected[key].issubset(observed):
            invented.append([key[0], key[1]])
        if output_primary[key] not in output_selected[key]:
            invalid_primary.append([key[0], key[1]])
        if _resolve([output_primary[key]]) is None:
            unplayable_primary.append([key[0], key[1]])
        base_render = _render_subset(attack, selected[key], primary[key])
        shadow_render = _render_subset(attack, output_selected[key], output_primary[key])
        baseline_rendered += len(base_render)
        shadow_rendered += len(shadow_render)
        if len(shadow_render) < len(output_selected[key]):
            shadow_voicing_drops.append({
                "measure": key[0], "step": key[1], "selected": sorted(output_selected[key]),
                "rendered": sorted(shadow_render), "primary": output_primary[key],
            })

    return {
        "schemaVersion": 1,
        "policy": "local-or-two-view-extra-harmonic-primary-v3",
        "inputRetainedAttackCount": len(by_key), "outputRetainedAttackCount": len(by_key),
        "correctedPrimaryCount": len(corrections), "correctionReasons": dict(sorted(reason_counts.items())),
        "oldPrimaryMidi64Count": sum(value == 64 for value in primary.values()),
        "newPrimaryMidi64Count": sum(value == 64 for value in output_primary.values()),
        "baselineSelectedPitchCount": sum(len(x) for x in selected.values()),
        "shadowSelectedPitchCount": sum(len(x) for x in output_selected.values()),
        "baselineRenderedPitchCount": baseline_rendered, "shadowRenderedPitchCount": shadow_rendered,
        "shadowVoicingDropCount": sum(len(output_selected[k]) - len(_render_subset(by_key[k], output_selected[k], output_primary[k])) for k in by_key),
        "shadowVoicingDropAttacks": shadow_voicing_drops,
        "changedAttackIdentity": False, "inventedPitchCount": len(invented),
        "invalidPrimaryCount": len(invalid_primary), "unplayablePrimaryCount": len(unplayable_primary),
        "harmonicIntervals": dict(sorted(Counter(item["harmonicInterval"] for item in corrections).items())),
        "primaryTransitions": {f"{old}->{new}": count for (old, new), count in sorted(Counter((item["oldPrimary"], item["newPrimary"]) for item in corrections).items())},
        "corrections": corrections,
        "referenceFree": True, "professionalReferenceUsed": False, "productionModified": False,
        "validationPassed": bool(by_key) and not invented and not invalid_primary and not unplayable_primary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_json", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = validate(json.loads(args.product_json.read_text()))
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
