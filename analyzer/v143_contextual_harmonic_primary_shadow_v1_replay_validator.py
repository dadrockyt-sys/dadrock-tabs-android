from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


HARMONIC_INTERVAL_WEIGHTS = {
    12: 0.35,
    19: 0.25,
    24: 0.20,
    28: 0.12,
    31: 0.10,
    36: 0.08,
}
LOCAL_RADIUS_STEPS = 2
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
FUNDAMENTAL_MIN_RAW_RATIO = 0.55


def _candidate_map(attack: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(item["midi"]): item for item in attack.get("candidates") or []}


def _positive(attack: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        midi: item
        for midi, item in _candidate_map(attack).items()
        if float(item["attack"]) > POSITIVE_ATTACK_FLOOR
        and float(item["body"]) > POSITIVE_BODY_FLOOR
    }


def _strongest_raw(attack: dict[str, Any]) -> int | None:
    positive = _positive(attack)
    if not positive:
        return None
    return int(max(positive, key=lambda midi: (
        float(positive[midi]["score"]),
        float(positive[midi]["attack"]),
        -int(midi),
    )))


def _family_score(midi: int, positive: dict[int, dict[str, Any]]) -> float:
    base = positive[midi]
    score = float(base["score"])
    for interval, weight in HARMONIC_INTERVAL_WEIGHTS.items():
        upper = positive.get(int(midi) + int(interval))
        if upper is None:
            continue
        score += float(weight) * max(
            0.0,
            min(float(base["score"]), float(upper["score"])),
        )
    return float(score)


def validate(product: dict[str, Any]) -> dict[str, Any]:
    evidence = product.get("precisionReplayEvidence") or {}
    attacks = [
        item for item in evidence.get("eligibleAttacks") or []
        if bool(item.get("retained"))
    ]
    by_key = {
        (int(item["measure"]), int(item["step"])): item
        for item in attacks
    }
    primary: dict[tuple[int, int], int] = {}
    selected: dict[tuple[int, int], set[int]] = {}
    for key, attack in by_key.items():
        primaries = [
            int(item["midi"])
            for item in attack.get("candidates") or []
            if bool(item.get("primary"))
        ]
        if len(primaries) != 1:
            raise RuntimeError(f"Expected one replay primary at {key}, got {primaries}")
        primary[key] = primaries[0]
        selected[key] = {
            int(item["midi"])
            for item in attack.get("candidates") or []
            if bool(item.get("selected"))
        }

    corrections: list[dict[str, Any]] = []
    output_primary = dict(primary)
    output_selected = {key: set(values) for key, values in selected.items()}

    for key in sorted(by_key):
        attack = by_key[key]
        current = int(primary[key])
        if _strongest_raw(attack) != current:
            continue
        positive = _positive(attack)
        measure, step = key
        support: Counter[int] = Counter()
        for other_key, other_primary in primary.items():
            if other_key == key or other_key[0] != measure:
                continue
            if abs(other_key[1] - step) > LOCAL_RADIUS_STEPS:
                continue
            lower = int(other_primary)
            if lower not in positive:
                continue
            if current - lower not in HARMONIC_INTERVAL_WEIGHTS:
                continue
            if float(positive[lower]["score"]) < (
                FUNDAMENTAL_MIN_RAW_RATIO * max(1e-6, float(positive[current]["score"]))
            ):
                continue
            support[lower] += 1

        if not support:
            continue

        lower = max(
            support,
            key=lambda midi: (
                int(support[midi]),
                _family_score(int(midi), positive),
                float(positive[int(midi)]["score"]),
                float(positive[int(midi)]["attack"]),
                -int(midi),
            ),
        )

        before = set(output_selected[key])
        after = set(before)
        after.add(int(lower))
        after.discard(current)
        after.add(int(lower))
        output_primary[key] = int(lower)
        output_selected[key] = after
        corrections.append({
            "measure": int(measure),
            "step": int(step),
            "oldPrimary": int(current),
            "newPrimary": int(lower),
            "harmonicInterval": int(current - lower),
            "neighborSupportCount": int(support[lower]),
            "oldSelected": sorted(before),
            "newSelected": sorted(after),
            "lowerAttack": float(positive[lower]["attack"]),
            "lowerBody": float(positive[lower]["body"]),
            "lowerScore": float(positive[lower]["score"]),
            "oldPrimaryScore": float(positive[current]["score"]),
        })

    invented = []
    invalid_primary = []
    for key, attack in by_key.items():
        observed = set(int(value) for value in attack.get("candidateMidis") or [])
        if not output_selected[key].issubset(observed):
            invented.append([key[0], key[1]])
        if output_primary[key] not in output_selected[key]:
            invalid_primary.append([key[0], key[1]])

    return {
        "schemaVersion": 1,
        "policy": "same-measure-neighbor-supported-harmonic-primary-v1",
        "inputRetainedAttackCount": len(by_key),
        "outputRetainedAttackCount": len(by_key),
        "correctedPrimaryCount": len(corrections),
        "oldPrimaryMidi64Count": sum(value == 64 for value in primary.values()),
        "newPrimaryMidi64Count": sum(value == 64 for value in output_primary.values()),
        "changedAttackIdentity": False,
        "inventedPitchCount": len(invented),
        "invalidPrimaryCount": len(invalid_primary),
        "harmonicIntervals": dict(sorted(Counter(
            item["harmonicInterval"] for item in corrections
        ).items())),
        "primaryTransitions": {
            f"{old}->{new}": count
            for (old, new), count in sorted(Counter(
                (item["oldPrimary"], item["newPrimary"])
                for item in corrections
            ).items())
        },
        "corrections": corrections,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "productionModified": False,
        "validationPassed": (
            len(by_key) > 0
            and len(invented) == 0
            and len(invalid_primary) == 0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product_json", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    product = json.loads(args.product_json.read_text())
    report = validate(product)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
