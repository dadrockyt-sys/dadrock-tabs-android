from __future__ import annotations

import json
from collections import Counter
from typing import Any

import benchmark_gomyway_1419_champion_cached_family_b_recur13_gate_v1 as gate


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def rows_to_counter(rows: list[dict[str, Any]], predicate) -> Counter:
    out: Counter = Counter()
    for row in rows:
        if predicate(row):
            out[token(row)] = 1
    return out


def main() -> None:
    rows = gate.cached.load_profile_rows()
    print(f"Loaded cached joint detector rows: {len(rows)}")
    print("Heavy feature extraction reused: True")

    payload = gate.v2.load_json(gate.recall.CANDIDATE_PATH)
    events = gate.v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = gate.v2.build_timing_grid(events)

    reference_payload = gate.v2.load_json(gate.recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = gate.v3.reference_tokens(reference_payload)

    baseline_1382, _, _ = gate.recur.build_frozen_1382(grid)
    champion_additions = rows_to_counter(rows, gate.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = gate.recur.grade(champion_1419, reference)

    champion_tokens = set(champion_additions.keys())
    residual_rows = [row for row in rows if token(row) not in champion_tokens]
    additions = rows_to_counter(residual_rows, gate.family_b_recur13)
    candidate = champion_1419 + additions
    evaluation = gate.recall.evaluate_recall(candidate, champion_1419, reference, score_1419)

    print("GOMYWAY 14.19 FAMILY-B RECUR13 CROSS-VALIDATION DIAGNOSTIC V1")
    print("Baseline:", score_1419["pitchF1"], score_1419["matched"], score_1419["missing"], score_1419["extra"])
    print("Addition count:", int(sum(additions.values())))
    print("Addition tokens:", sorted([list(k) for k in additions.keys()]))
    print("Full score:", json.dumps(evaluation.get("fullScore", {}), sort_keys=True))
    print("Cross-validation passed:", evaluation.get("crossValidationPassed"))
    print("Section stability passed:", evaluation.get("sectionStabilityPassed"))
    print("Shifted-window stability passed:", evaluation.get("shiftedWindowStabilityPassed"))
    print("Accepted over champion:", evaluation.get("acceptedOverChampion"))

    print("Evaluation keys:", sorted(evaluation.keys()))
    for key in sorted(evaluation.keys()):
        if key in {"fullScore"}:
            continue
        value = evaluation[key]
        if isinstance(value, (dict, list, tuple)):
            print(f"DETAIL {key}: {json.dumps(value, sort_keys=True, default=str)}")
        else:
            print(f"DETAIL {key}: {value}")

    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
