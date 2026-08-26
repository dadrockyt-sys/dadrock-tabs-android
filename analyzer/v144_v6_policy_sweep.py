#!/usr/bin/env python3
"""Calibration-only sweep of source-only V6 pruning policies.

Consumes frozen V5 plus exact V2 source evidence and an already-consumed professional
calibration source. Emits aggregate comparisons only; it never writes a candidate.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from v144_rhythm_calibration_diagnostics import build_reference  # noqa: E402
from v144_v5_source_evidence_diagnostics import candidate_features, prf  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def counter_f1(generated: Sequence[Any], reference: Sequence[Any]) -> dict[str, Any]:
    g = Counter(generated)
    r = Counter(reference)
    matched = sum((g & r).values())
    return prf(matched, sum(g.values()), sum(r.values()))


def metric_bundle(events: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, int]]) -> dict[str, Any]:
    generated_onsets = sorted({(int(event["measure"]), int(event["step"])) for event in events})
    reference_onsets = sorted({(int(note["measure"]), int(note["step"])) for note in reference})
    return {
        "eventCount": len(events),
        "onsetCount": len(generated_onsets),
        "onsets": counter_f1(generated_onsets, reference_onsets),
        "exactEvent": counter_f1(
            [(int(event["measure"]), int(event["step"]), int(event["midi"])) for event in events],
            [(int(note["measure"]), int(note["step"]), int(note["midi"])) for note in reference],
        ),
        "pitchContent": counter_f1(
            [int(event["midi"]) for event in events],
            [int(note["midi"]) for note in reference],
        ),
        "pitchClassContent": counter_f1(
            [int(event["midi"]) % 12 for event in events],
            [int(note["midi"]) % 12 for note in reference],
        ),
        "measurePitch": counter_f1(
            [(int(event["measure"]), int(event["midi"])) for event in events],
            [(int(note["measure"]), int(note["midi"])) for note in reference],
        ),
        "measurePitchClass": counter_f1(
            [(int(event["measure"]), int(event["midi"]) % 12) for event in events],
            [(int(note["measure"]), int(note["midi"]) % 12) for note in reference],
        ),
        "positionContent": counter_f1(
            [(int(event["stringIndex"]), int(event["fret"]), int(event["midi"])) for event in events],
            [(int(note["stringIndex"]), int(note["fret"]), int(note["midi"])) for note in reference],
        ),
    }


def split_bundle(events: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, int]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, parity in (("oddMeasures", 1), ("evenMeasures", 0)):
        e = [event for event in events if int(event["measure"]) % 2 == parity]
        r = [note for note in reference if int(note["measure"]) % 2 == parity]
        result[name] = metric_bundle(e, r)
    return result


def f1(bundle: Mapping[str, Any], metric: str) -> float:
    return float((bundle.get(metric) or {}).get("f1") or 0.0)


def build_rows(v5_events: Sequence[Mapping[str, Any]], eligible: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    evidence_by_key = {(int(attack["measure"]), int(attack["step"])): attack for attack in eligible}
    rows: list[dict[str, Any]] = []
    for event in v5_events:
        key = (int(event["measure"]), int(event["step"]))
        attack = evidence_by_key.get(key)
        if attack is None:
            raise ValueError(f"missing V2 attack evidence for {key}")
        candidates = attack.get("candidates") if isinstance(attack.get("candidates"), list) else []
        candidate_by_midi = {
            int(candidate["midi"]): candidate
            for candidate in candidates
            if isinstance(candidate, Mapping) and isinstance(candidate.get("midi"), int)
        }
        candidate = candidate_by_midi.get(int(event["midi"]))
        if candidate is None:
            raise ValueError(f"missing V2 pitch evidence for {key} midi={event['midi']}")
        rows.append({
            **event,
            "precisionStrength": float(attack.get("precisionStrength") or 0.0),
            "precisionGridErrorSeconds": float(attack.get("precisionGridErrorSeconds") or 0.0),
            "stemSupportMax": float(attack.get("stemSupportMax") or 0.0),
            "sweepSupportMax": float(attack.get("sweepSupportMax") or 0.0),
            "detectionCountSum": float(attack.get("detectionCountSum") or 0.0),
            **candidate_features(candidate, candidates),
        })
    return rows


def policy_variants() -> list[tuple[str, Callable[[Mapping[str, Any], Sequence[Mapping[str, Any]]], bool]]]:
    policies: list[tuple[str, Callable[[Mapping[str, Any], Sequence[Mapping[str, Any]]], bool]]] = []
    policies.append(("all-events", lambda row, group: True))
    policies.append(("primary-only", lambda row, group: bool(row.get("v5Primary"))))
    policies.append(("primary-or-original-v2-selected", lambda row, group: bool(row.get("v5Primary")) or bool(row.get("originalV2Selected"))))
    for rank in (1, 2):
        policies.append((
            f"primary-or-score-rank<={rank}",
            lambda row, group, rank=rank: bool(row.get("v5Primary")) or int(row.get("candidateScoreRank") or 999) <= rank,
        ))
    for delta in (0.10, 0.25, 0.50, 0.75):
        policies.append((
            f"primary-or-score-delta<={delta:.2f}",
            lambda row, group, delta=delta: bool(row.get("v5Primary")) or float(row.get("scoreDeltaFromBest") or 0.0) <= delta,
        ))
    for score in (2.5, 3.0, 3.5, 4.0, 4.5):
        policies.append((
            f"primary-or-score>={score:.1f}",
            lambda row, group, score=score: bool(row.get("v5Primary")) or float(row.get("candidateScore") or 0.0) >= score,
        ))
    for attack in (1.25, 1.5, 1.75, 2.0):
        policies.append((
            f"primary-or-candidate-attack>={attack:.2f}",
            lambda row, group, attack=attack: bool(row.get("v5Primary")) or float(row.get("candidateAttack") or 0.0) >= attack,
        ))
    for sustain in (1.0, 1.5, 2.0, 2.5):
        policies.append((
            f"primary-or-sustain>={sustain:.1f}",
            lambda row, group, sustain=sustain: bool(row.get("v5Primary")) or float(row.get("candidateSustain") or 0.0) >= sustain,
        ))
    # Max-two preserves every primary and only the strongest-scoring secondary.
    policies.append((
        "primary-plus-best-one-secondary",
        lambda row, group: bool(row.get("v5Primary")) or row is max(
            [item for item in group if not bool(item.get("v5Primary"))],
            key=lambda item: (float(item.get("candidateScore") or 0.0), -int(item.get("midi") or 0)),
            default=row,
        ),
    ))
    return policies


def apply_policy(
    rows: Sequence[Mapping[str, Any]],
    attack_gate: bool,
    event_policy: Callable[[Mapping[str, Any], Sequence[Mapping[str, Any]]], bool],
) -> list[Mapping[str, Any]]:
    grouped: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(row)
    kept: list[Mapping[str, Any]] = []
    for _key, group in sorted(grouped.items()):
        anchor = group[0]
        if attack_gate and not (
            float(anchor.get("detectionCountSum") or 0.0) >= 12.0
            and float(anchor.get("precisionGridErrorSeconds") or 1.0) <= 0.06
        ):
            continue
        selected = [row for row in group if event_policy(row, group)]
        # Source-only safety: every surviving attack must keep its V5 primary.
        if not any(bool(row.get("v5Primary")) for row in selected):
            primary = next((row for row in group if bool(row.get("v5Primary"))), None)
            if primary is not None:
                selected.append(primary)
        kept.extend(selected)
    return kept


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v5_stream", type=Path)
    parser.add_argument("v2_candidate_product", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    stream = load_json(args.v5_stream)
    events = stream.get("events")
    if not isinstance(events, list) or len(events) != 1209:
        raise ValueError("expected frozen V5 1209 events")
    product = load_json(args.v2_candidate_product)
    replay = product.get("precisionReplayEvidence") if isinstance(product, Mapping) else None
    eligible = replay.get("eligibleAttacks") if isinstance(replay, Mapping) else None
    if not isinstance(eligible, list) or len(eligible) != 984:
        raise ValueError("expected 984 V2 eligible attacks")
    reference = build_reference(load_json(args.structured_source))
    rows = build_rows(events, eligible)

    baseline = metric_bundle(rows, reference)
    baseline_split = split_bundle(rows, reference)
    metric_names = ("onsets", "exactEvent", "pitchContent", "pitchClassContent", "measurePitch", "measurePitchClass", "positionContent")

    results: list[dict[str, Any]] = []
    for attack_gate in (False, True):
        for policy_name, event_policy in policy_variants():
            kept = apply_policy(rows, attack_gate, event_policy)
            overall = metric_bundle(kept, reference)
            splits = split_bundle(kept, reference)
            improvements = {
                metric: f1(overall, metric) - f1(baseline, metric)
                for metric in metric_names
            }
            split_improvements = {
                split: {
                    metric: f1(splits[split], metric) - f1(baseline_split[split], metric)
                    for metric in metric_names
                }
                for split in ("oddMeasures", "evenMeasures")
            }
            robust_metrics = [
                metric for metric in metric_names
                if improvements[metric] > 1e-12
                and split_improvements["oddMeasures"][metric] >= -1e-12
                and split_improvements["evenMeasures"][metric] >= -1e-12
            ]
            regressions = [metric for metric in metric_names if improvements[metric] < -1e-12]
            results.append({
                "attackGate": "detection>=12&grid<=0.06" if attack_gate else "none",
                "eventPolicy": policy_name,
                "overall": overall,
                "splits": splits,
                "improvementsVsV5F1": improvements,
                "splitImprovementsVsV5F1": split_improvements,
                "robustImprovedMetrics": robust_metrics,
                "regressedMetrics": regressions,
                "eventCountDeltaVsReference": len(kept) - len(reference),
            })

    results.sort(
        key=lambda row: (
            -len(row["robustImprovedMetrics"]),
            len(row["regressedMetrics"]),
            -float(row["overall"]["pitchContent"]["f1"]),
            -float(row["overall"]["pitchClassContent"]["f1"]),
            -float(row["overall"]["onsets"]["f1"]),
            abs(int(row["eventCountDeltaVsReference"])),
        )
    )

    report = {
        "schemaVersion": 1,
        "classification": "v144-v6-source-only-policy-calibration-sweep",
        "calibrationReferenceUsed": True,
        "unseenHoldout": False,
        "candidateGenerated": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "baselineV5": baseline,
        "baselineSplits": baseline_split,
        "policyCount": len(results),
        "policies": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
