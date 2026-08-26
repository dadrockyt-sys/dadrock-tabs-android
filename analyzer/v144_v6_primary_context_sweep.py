#!/usr/bin/env python3
"""Calibration-only sweep of source-only primary-pitch context policies for frozen V6.

Selectors never read the professional reference. They choose one primary MIDI per frozen
V6 attack from the original V2 candidate pool using only source evidence and source-side
context. The consumed professional reference is used afterwards only to grade policies.

No V7 candidate is written by this script.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Callable, Mapping, Sequence

from v144_rhythm_calibration_diagnostics import build_reference
from v144_v6_policy_sweep import counter_f1

METRICS = ("exactEvent", "pitchContent", "pitchClassContent", "measurePitch", "measurePitchClass")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def attack_key(row: Mapping[str, Any]) -> tuple[int, int]:
    return int(row["measure"]), int(row["step"])


def metric_bundle(events: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, int]]) -> dict[str, Any]:
    return {
        "eventCount": len(events),
        "exactEvent": counter_f1(
            [(int(e["measure"]), int(e["step"]), int(e["midi"])) for e in events],
            [(int(r["measure"]), int(r["step"]), int(r["midi"])) for r in reference],
        ),
        "pitchContent": counter_f1([int(e["midi"]) for e in events], [int(r["midi"]) for r in reference]),
        "pitchClassContent": counter_f1([int(e["midi"]) % 12 for e in events], [int(r["midi"]) % 12 for r in reference]),
        "measurePitch": counter_f1(
            [(int(e["measure"]), int(e["midi"])) for e in events],
            [(int(r["measure"]), int(r["midi"])) for r in reference],
        ),
        "measurePitchClass": counter_f1(
            [(int(e["measure"]), int(e["midi"]) % 12) for e in events],
            [(int(r["measure"]), int(r["midi"]) % 12) for r in reference],
        ),
    }


def split_bundle(events: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, int]]) -> dict[str, Any]:
    result = {}
    for name, parity in (("oddMeasures", 1), ("evenMeasures", 0)):
        e = [row for row in events if int(row["measure"]) % 2 == parity]
        r = [row for row in reference if int(row["measure"]) % 2 == parity]
        result[name] = metric_bundle(e, r)
    return result


def f1(bundle: Mapping[str, Any], metric: str) -> float:
    return float((bundle.get(metric) or {}).get("f1") or 0.0)


def build_attacks(v6_events: Sequence[Mapping[str, Any]], eligible: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for event in v6_events:
        grouped[attack_key(event)].append(event)
    evidence_by_key = {(int(a["measure"]), int(a["step"])): a for a in eligible}
    attacks: list[dict[str, Any]] = []
    for key in sorted(grouped):
        group = grouped[key]
        primaries = [e for e in group if bool(e.get("v5Primary"))]
        if len(primaries) != 1:
            raise ValueError(f"expected exactly one V6 primary at {key}, got {len(primaries)}")
        evidence = evidence_by_key.get(key)
        if evidence is None:
            raise ValueError(f"missing V2 evidence for V6 attack {key}")
        raw_candidates = [c for c in evidence.get("candidates", []) if isinstance(c, Mapping) and isinstance(c.get("midi"), int)]
        if not raw_candidates:
            raise ValueError(f"no V2 candidates at {key}")
        ranked = sorted(raw_candidates, key=lambda c: (-float(c.get("score") or 0.0), int(c["midi"])))
        top_score = float(ranked[0].get("score") or 0.0)
        candidates = []
        for rank, c in enumerate(ranked, start=1):
            candidates.append({
                "midi": int(c["midi"]),
                "score": float(c.get("score") or 0.0),
                "gap": top_score - float(c.get("score") or 0.0),
                "rank": rank,
                "selected": bool(c.get("selected")),
                "originalPrimary": bool(c.get("primary")),
            })
        current_primary = int(primaries[0]["midi"])
        if current_primary not in {int(c["midi"]) for c in candidates}:
            raise ValueError(f"V6 primary {current_primary} missing from V2 candidate pool at {key}")
        attacks.append({
            "key": key,
            "measure": key[0],
            "step": key[1],
            "gridTime": float(evidence.get("gridTime") or 0.0),
            "events": [dict(e) for e in group],
            "currentPrimary": current_primary,
            "candidates": candidates,
        })
    attacks.sort(key=lambda a: (float(a["gridTime"]), int(a["measure"]), int(a["step"])))
    if len(attacks) != 839:
        raise ValueError(f"expected 839 frozen V6 attacks, got {len(attacks)}")
    return attacks


def candidate_pool(attack: Mapping[str, Any], max_gap: float) -> list[Mapping[str, Any]]:
    current = int(attack["currentPrimary"])
    pool = [c for c in attack["candidates"] if float(c["gap"]) <= max_gap + 1e-12 or int(c["midi"]) == current]
    return pool or [min(attack["candidates"], key=lambda c: float(c["gap"]))]


def choose_current(attacks: Sequence[Mapping[str, Any]]) -> list[int]:
    return [int(a["currentPrimary"]) for a in attacks]


def choose_top_score(attacks: Sequence[Mapping[str, Any]]) -> list[int]:
    return [int(min(a["candidates"], key=lambda c: (float(c["gap"]), int(c["midi"])))["midi"]) for a in attacks]


def choose_local_neighbor(attacks: Sequence[Mapping[str, Any]], max_gap: float, continuity_lambda: float) -> list[int]:
    current = [int(a["currentPrimary"]) for a in attacks]
    chosen = []
    for i, attack in enumerate(attacks):
        neighbors = []
        if i > 0:
            neighbors.append(current[i - 1])
        if i + 1 < len(attacks):
            neighbors.append(current[i + 1])
        target = float(median(neighbors)) if neighbors else float(current[i])
        pool = candidate_pool(attack, max_gap)
        best = max(
            pool,
            key=lambda c: (
                -float(c["gap"]) - continuity_lambda * min(abs(int(c["midi"]) - target), 18.0),
                -float(c["gap"]),
                -abs(int(c["midi"]) - current[i]),
                -int(c["midi"]),
            ),
        )
        chosen.append(int(best["midi"]))
    return chosen


def choose_dp(attacks: Sequence[Mapping[str, Any]], max_gap: float, continuity_lambda: float, tau_seconds: float) -> list[int]:
    pools = [candidate_pool(a, max_gap) for a in attacks]
    scores: list[list[float]] = [[-math.inf] * len(pool) for pool in pools]
    backs: list[list[int]] = [[-1] * len(pool) for pool in pools]
    for j, c in enumerate(pools[0]):
        scores[0][j] = -float(c["gap"])
    for i in range(1, len(attacks)):
        dt = max(0.0, float(attacks[i]["gridTime"]) - float(attacks[i - 1]["gridTime"]))
        weight = math.exp(-dt / max(tau_seconds, 1e-6))
        for j, c in enumerate(pools[i]):
            base = -float(c["gap"])
            best_score = -math.inf
            best_k = -1
            midi = int(c["midi"])
            for k, prev in enumerate(pools[i - 1]):
                transition = continuity_lambda * weight * min(abs(midi - int(prev["midi"])), 18.0)
                value = scores[i - 1][k] + base - transition
                if value > best_score:
                    best_score = value
                    best_k = k
            scores[i][j] = best_score
            backs[i][j] = best_k
    j = max(range(len(pools[-1])), key=lambda idx: scores[-1][idx])
    path = [0] * len(attacks)
    for i in range(len(attacks) - 1, -1, -1):
        path[i] = int(pools[i][j]["midi"])
        if i > 0:
            j = backs[i][j]
    return path


def measure_signatures(attacks: Sequence[Mapping[str, Any]]) -> dict[int, set[int]]:
    sig: dict[int, set[int]] = defaultdict(set)
    for attack in attacks:
        sig[int(attack["measure"])].add(int(attack["step"]))
    return dict(sig)


def jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def choose_repeat_support(
    attacks: Sequence[Mapping[str, Any]],
    max_gap: float,
    measure_window: int,
    beta: float,
    pitch_class_weight: float,
) -> list[int]:
    signatures = measure_signatures(attacks)
    by_measure_step: dict[tuple[int, int], Mapping[str, Any]] = {
        (int(a["measure"]), int(a["step"])): a for a in attacks
    }
    chosen = []
    temp = 2.0
    for attack in attacks:
        measure = int(attack["measure"])
        step = int(attack["step"])
        pool = candidate_pool(attack, max_gap)
        peer_weights: list[tuple[Mapping[str, Any], float]] = []
        for peer_measure in range(max(1, measure - measure_window), measure + measure_window + 1):
            if peer_measure == measure:
                continue
            peer = by_measure_step.get((peer_measure, step))
            if peer is None:
                continue
            sim = jaccard(signatures.get(measure, set()), signatures.get(peer_measure, set()))
            if sim < 0.5:
                continue
            distance_weight = 1.0 / (1.0 + abs(peer_measure - measure))
            peer_weights.append((peer, sim * distance_weight))
        denom = sum(w for _, w in peer_weights) or 1.0
        def utility(c: Mapping[str, Any]) -> tuple[float, float, int]:
            midi = int(c["midi"])
            pc = midi % 12
            exact_support = 0.0
            pc_support = 0.0
            for peer, w in peer_weights:
                for peer_c in peer["candidates"]:
                    peer_strength = math.exp(-float(peer_c["gap"]) / temp)
                    peer_midi = int(peer_c["midi"])
                    if peer_midi == midi:
                        exact_support += w * peer_strength
                    elif peer_midi % 12 == pc:
                        pc_support += w * peer_strength
            support = (exact_support + pitch_class_weight * pc_support) / denom
            score = -float(c["gap"]) + beta * support
            return score, -float(c["gap"]), -midi
        best = max(pool, key=utility)
        chosen.append(int(best["midi"]))
    return chosen


def simulate_events(attacks: Sequence[Mapping[str, Any]], chosen_midis: Sequence[int]) -> tuple[list[dict[str, Any]], int, int]:
    if len(attacks) != len(chosen_midis):
        raise ValueError("chosen path length mismatch")
    result: list[dict[str, Any]] = []
    changed = 0
    duplicate_promotions = 0
    for attack, chosen_midi in zip(attacks, chosen_midis):
        events = [dict(e) for e in attack["events"]]
        current = int(attack["currentPrimary"])
        if int(chosen_midi) == current:
            result.extend(events)
            continue
        changed += 1
        primary_index = next(i for i, e in enumerate(events) if bool(e.get("v5Primary")))
        existing_indices = [i for i, e in enumerate(events) if i != primary_index and int(e["midi"]) == int(chosen_midi)]
        if existing_indices:
            # Promote an already-present secondary musically by removing the old primary pitch.
            duplicate_promotions += 1
            events.pop(primary_index)
        else:
            # Pitch-only simulation: fingering is intentionally not graded in this sweep.
            events[primary_index]["midi"] = int(chosen_midi)
        result.extend(events)
    return result, changed, duplicate_promotions


def primary_hit_count(attacks: Sequence[Mapping[str, Any]], chosen: Sequence[int], reference: Sequence[Mapping[str, int]]) -> int:
    ref_by_key: dict[tuple[int, int], set[int]] = defaultdict(set)
    for note in reference:
        ref_by_key[attack_key(note)].add(int(note["midi"]))
    return sum(1 for attack, midi in zip(attacks, chosen) if int(midi) in ref_by_key.get(tuple(attack["key"]), set()))


def selector_specs() -> list[tuple[str, Callable[[Sequence[Mapping[str, Any]]], list[int]]]]:
    specs: list[tuple[str, Callable[[Sequence[Mapping[str, Any]]], list[int]]]] = [
        ("v6-current-primary", choose_current),
        ("source-top-score", choose_top_score),
    ]
    for gap in (2.5, 4.0, 6.0):
        for lam in (0.10, 0.20, 0.35):
            specs.append((
                f"local-neighbor-gap{gap:.1f}-lambda{lam:.2f}",
                lambda attacks, gap=gap, lam=lam: choose_local_neighbor(attacks, gap, lam),
            ))
    for gap in (3.0, 5.0):
        for lam in (0.10, 0.20, 0.35):
            for tau in (0.5, 1.0):
                specs.append((
                    f"dp-gap{gap:.1f}-lambda{lam:.2f}-tau{tau:.1f}",
                    lambda attacks, gap=gap, lam=lam, tau=tau: choose_dp(attacks, gap, lam, tau),
                ))
    for gap in (4.0, 6.0):
        for window in (4, 8, 16):
            for beta in (0.75, 1.5):
                for pc_weight in (0.0, 0.35):
                    specs.append((
                        f"repeat-gap{gap:.1f}-w{window}-beta{beta:.2f}-pc{pc_weight:.2f}",
                        lambda attacks, gap=gap, window=window, beta=beta, pc_weight=pc_weight: choose_repeat_support(
                            attacks, gap, window, beta, pc_weight
                        ),
                    ))
    return specs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v6_stream", type=Path)
    parser.add_argument("v2_candidate_product", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    v6 = load_json(args.v6_stream)
    events = v6.get("events") if isinstance(v6, Mapping) else None
    if not isinstance(events, list) or len(events) != 1149:
        raise ValueError("expected frozen V6 with 1149 events")
    product = load_json(args.v2_candidate_product)
    replay = product.get("precisionReplayEvidence") if isinstance(product, Mapping) else None
    eligible = replay.get("eligibleAttacks") if isinstance(replay, Mapping) else None
    if not isinstance(eligible, list) or len(eligible) != 984:
        raise ValueError("expected exact V2 replay evidence with 984 eligible attacks")
    reference = build_reference(load_json(args.structured_source))
    if len(reference) != 946:
        raise ValueError("expected 946 calibration reference notes")

    attacks = build_attacks(events, eligible)
    baseline = metric_bundle(events, reference)
    baseline_splits = split_bundle(events, reference)
    baseline_primary_hits = primary_hit_count(attacks, choose_current(attacks), reference)

    results = []
    for name, selector in selector_specs():
        chosen = selector(attacks)
        simulated, changed, duplicate_promotions = simulate_events(attacks, chosen)
        overall = metric_bundle(simulated, reference)
        splits = split_bundle(simulated, reference)
        improvements = {metric: f1(overall, metric) - f1(baseline, metric) for metric in METRICS}
        split_improvements = {
            split: {metric: f1(splits[split], metric) - f1(baseline_splits[split], metric) for metric in METRICS}
            for split in ("oddMeasures", "evenMeasures")
        }
        robust = [
            metric for metric in METRICS
            if improvements[metric] > 1e-12
            and split_improvements["oddMeasures"][metric] >= -1e-12
            and split_improvements["evenMeasures"][metric] >= -1e-12
        ]
        regressions = [metric for metric in METRICS if improvements[metric] < -1e-12]
        primary_hits = primary_hit_count(attacks, chosen, reference)
        results.append({
            "policy": name,
            "sourceOnlySelector": True,
            "candidateGenerated": False,
            "changedPrimaryCount": changed,
            "duplicateSecondaryPromotions": duplicate_promotions,
            "simulatedEventCount": len(simulated),
            "primaryExactHitCount": primary_hits,
            "primaryExactHitDeltaVsV6": primary_hits - baseline_primary_hits,
            "overall": overall,
            "splits": splits,
            "improvementsVsV6F1": improvements,
            "splitImprovementsVsV6F1": split_improvements,
            "robustImprovedMetrics": robust,
            "regressedMetrics": regressions,
        })

    results.sort(key=lambda row: (
        -len(row["robustImprovedMetrics"]),
        len(row["regressedMetrics"]),
        -int(row["primaryExactHitDeltaVsV6"]),
        -float(row["overall"]["exactEvent"]["f1"]),
        -float(row["overall"]["measurePitch"]["f1"]),
        int(row["changedPrimaryCount"]),
    ))

    report = {
        "schemaVersion": 1,
        "classification": "v144-v6-primary-context-source-only-calibration-sweep",
        "calibrationReferenceUsedForGrading": True,
        "selectorsReadCalibrationReference": False,
        "unseenHoldout": False,
        "candidateGenerated": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "v6Baseline": baseline,
        "v6BaselineSplits": baseline_splits,
        "v6PrimaryExactHitCount": baseline_primary_hits,
        "policyCount": len(results),
        "policies": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
