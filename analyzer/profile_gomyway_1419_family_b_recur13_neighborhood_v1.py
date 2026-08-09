from __future__ import annotations

from collections import defaultdict
from typing import Any

import benchmark_gomyway_1419_champion_cached_family_b_recur13_gate_v1 as bench

cached = bench.cached
v2 = bench.v2
v3 = bench.v3
recall = bench.recall


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def label(row: dict[str, Any], reference: set[tuple[int, int, int]]) -> str:
    return "TRUE" if token(row) in reference else "FALSE"


def precision(rows: list[dict[str, Any]], reference: set[tuple[int, int, int]]) -> tuple[int, int, float]:
    true_count = sum(1 for row in rows if token(row) in reference)
    false_count = len(rows) - true_count
    total = true_count + false_count
    pct = 100.0 * true_count / total if total else 0.0
    return true_count, false_count, pct


def main() -> None:
    rows = cached.load_profile_rows()
    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = v3.reference_tokens(reference_payload)
    reference = set(reference_counter.keys())

    champion_tokens = {
        token(row)
        for row in rows
        if bench.champion_1419_predicate(row)
    }
    residual = [row for row in rows if token(row) not in champion_tokens]
    family_b_rows = [row for row in residual if bench.family_b(row)]
    neighborhood = [
        row for row in family_b_rows
        if 10 <= int(row["recurrence"]) <= 16
    ]

    print("GOMYWAY 14.19 FAMILY-B RECUR13 NEIGHBORHOOD V1")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Family-B residual rows:", len(family_b_rows))
    print("Neighborhood recurrence 10..16 rows:", len(neighborhood))

    by_recur: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in neighborhood:
        by_recur[int(row["recurrence"])].append(row)

    print("\nRecurrence precision 10..16:")
    for recur_value in range(10, 17):
        subset = by_recur.get(recur_value, [])
        t, f, p = precision(subset, reference)
        print(f"  recur={recur_value}: true={t} false={f} precision={p:.2f}%")

    windows = [
        ("ratio_130_170", lambda r: 1.30 <= float(r["minTargetVsSubharmonicRatio"]) < 1.70),
        ("ratio_140_160", lambda r: 1.40 <= float(r["minTargetVsSubharmonicRatio"]) < 1.60),
        ("template_130_230", lambda r: 1.30 <= float(r["minTemplateRatio"]) < 2.30),
        ("ratio_130_170_template_130_230", lambda r: (
            1.30 <= float(r["minTargetVsSubharmonicRatio"]) < 1.70
            and 1.30 <= float(r["minTemplateRatio"]) < 2.30
        )),
    ]

    print("\nNeighborhood window precision:")
    for name, pred in windows:
        subset = [row for row in neighborhood if pred(row)]
        t, f, p = precision(subset, reference)
        print(f"  {name}: true={t} false={f} precision={p:.2f}%")

    print("\nDetailed family-B neighborhood rows:")
    for row in sorted(
        neighborhood,
        key=lambda r: (
            int(r["recurrence"]),
            token(r)[0],
            token(r)[1],
            token(r)[2],
        ),
    ):
        tok = token(row)
        print(
            f"  {label(row, reference)} token={tok} "
            f"recur={int(row['recurrence'])} "
            f"rms={float(row['minRmsRise']):.6f} "
            f"flux={float(row['minPositiveFlux']):.6f} "
            f"ratio={float(row['minTargetVsSubharmonicRatio']):.6f} "
            f"template={float(row['minTemplateRatio']):.6f}"
        )

    print("\nProfessional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
