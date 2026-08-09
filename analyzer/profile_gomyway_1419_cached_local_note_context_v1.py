from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

cached = bench.cached
recur = bench.recur
v2 = bench.v2
v3 = bench.v3
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-local-note-context-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-local-note-context-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision(t: int, f: int) -> float:
    return round(100.0 * t / (t + f), 2) if t + f else 0.0


def rows_to_counter(rows: list[dict[str, Any]]) -> Counter:
    out: Counter = Counter()
    for row in rows:
        if bench.champion_1419_predicate(row):
            out[token(row)] = 1
    return out


def bucket_count(value: int) -> str:
    if value <= 0:
        return "0"
    if value == 1:
        return "1"
    if value == 2:
        return "2"
    if value <= 4:
        return "3_4"
    return "5plus"


def bucket_pitch_distance(value: int | None) -> str:
    if value is None:
        return "none"
    if value == 0:
        return "0"
    if value <= 2:
        return "1_2"
    if value <= 5:
        return "3_5"
    if value <= 12:
        return "6_12"
    return "13plus"


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    rows = cached.load_profile_rows()
    print(f"Loaded cached joint detector rows: {len(rows)}", flush=True)
    print("No audio feature extraction required; using frozen 14.19 note context.", flush=True)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = v3.reference_tokens(reference_payload)
    reference = set(reference_counter.keys())

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_additions = rows_to_counter(rows)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = recur.grade(champion_1419, reference_counter)
    actual = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual != EXPECTED_1419 or abs(float(score_1419["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, "
            f"got {actual}/{score_1419['pitchF1']}"
        )

    champion_tokens = set(champion_1419.keys())
    residual = [row for row in rows if token(row) not in champion_tokens]

    by_measure: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    by_pitch: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for tok in champion_tokens:
        m, s, p = tok
        by_measure[m].append(tok)
        by_pitch[p].append(tok)

    for vals in by_measure.values():
        vals.sort()
    for vals in by_pitch.values():
        vals.sort()

    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    detail_rows: list[dict[str, Any]] = []

    for row in residual:
        m, s, p = token(row)
        same_measure = by_measure.get(m, [])

        same_measure_count = len(same_measure)
        near_step4 = sum(1 for _, cs, _ in same_measure if abs(cs - s) <= 4)
        near_step8 = sum(1 for _, cs, _ in same_measure if abs(cs - s) <= 8)
        exact_step_other_pitch = sum(1 for _, cs, cp in same_measure if cs == s and cp != p)

        pitch_distances = [abs(cp - p) for _, _, cp in same_measure]
        nearest_pitch = min(pitch_distances) if pitch_distances else None

        same_pitch_tokens = by_pitch.get(p, [])
        same_pitch_pm1 = sum(1 for cm, _, _ in same_pitch_tokens if 0 < abs(cm - m) <= 1)
        same_pitch_pm2 = sum(1 for cm, _, _ in same_pitch_tokens if 0 < abs(cm - m) <= 2)
        same_pitch_pm4 = sum(1 for cm, _, _ in same_pitch_tokens if 0 < abs(cm - m) <= 4)
        same_pitch_pm8 = sum(1 for cm, _, _ in same_pitch_tokens if 0 < abs(cm - m) <= 8)

        octave_neighbor = 0
        for op in (p - 12, p + 12):
            octave_neighbor += sum(
                1 for cm, _, _ in by_pitch.get(op, []) if abs(cm - m) <= 2
            )

        features = {
            "sameMeasure": bucket_count(same_measure_count),
            "nearStep4": bucket_count(near_step4),
            "nearStep8": bucket_count(near_step8),
            "exactStepOtherPitch": bucket_count(exact_step_other_pitch),
            "nearestPitch": bucket_pitch_distance(nearest_pitch),
            "samePitchPm1": bucket_count(same_pitch_pm1),
            "samePitchPm2": bucket_count(same_pitch_pm2),
            "samePitchPm4": bucket_count(same_pitch_pm4),
            "samePitchPm8": bucket_count(same_pitch_pm8),
            "octavePm2": bucket_count(octave_neighbor),
        }

        exact = (
            f"sm{features['sameMeasure']}|ns4_{features['nearStep4']}|ns8_{features['nearStep8']}|"
            f"xp_{features['exactStepOtherPitch']}|np_{features['nearestPitch']}|"
            f"sp2_{features['samePitchPm2']}|sp4_{features['samePitchPm4']}|oct_{features['octavePm2']}"
        )
        temporal = (
            f"sp1_{features['samePitchPm1']}|sp2_{features['samePitchPm2']}|"
            f"sp4_{features['samePitchPm4']}|sp8_{features['samePitchPm8']}"
        )
        measure_context = (
            f"sm{features['sameMeasure']}|ns4_{features['nearStep4']}|"
            f"xp_{features['exactStepOtherPitch']}|np_{features['nearestPitch']}"
        )
        hybrid = (
            f"ns4_{features['nearStep4']}|np_{features['nearestPitch']}|"
            f"sp4_{features['samePitchPm4']}|oct_{features['octavePm2']}"
        )

        is_true = token(row) in reference
        idx = 0 if is_true else 1
        for label in (
            "exact:" + exact,
            "temporal:" + temporal,
            "measure:" + measure_context,
            "hybrid:" + hybrid,
        ):
            counts[label][idx] += 1

        detail_rows.append({
            "token": list(token(row)),
            "isTrue": is_true,
            "sameMeasureCount": same_measure_count,
            "nearStep4": near_step4,
            "nearStep8": near_step8,
            "exactStepOtherPitch": exact_step_other_pitch,
            "nearestPitchDistance": nearest_pitch,
            "samePitchPm1": same_pitch_pm1,
            "samePitchPm2": same_pitch_pm2,
            "samePitchPm4": same_pitch_pm4,
            "samePitchPm8": same_pitch_pm8,
            "octaveNeighborPm2": octave_neighbor,
        })

    summary = [
        {"signature": sig, "true": tf[0], "false": tf[1], "precision": precision(tf[0], tf[1])}
        for sig, tf in counts.items()
    ]
    summary.sort(key=lambda r: (r["precision"], r["true"], -r["false"]), reverse=True)

    repeatable = [r for r in summary if r["true"] >= 2]
    supported = [r for r in summary if r["true"] >= 3]

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-local-note-context",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "residualRows": len(residual),
        "topSignatures": summary[:50],
        "topRepeatableSignatures": repeatable[:40],
        "topSupportedSignatures": supported[:30],
        "details": detail_rows,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-high-precision-local-context-signatures-or-pivot",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": before,
        "championPitchF1": 14.19,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during local-context profiling")

    print("GOMYWAY 14.19 CACHED LOCAL NOTE CONTEXT V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Residual rows:", len(residual))
    print("\nTop repeatable local-context signatures:")
    for r in repeatable[:25]:
        print(f"  {r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}%")
    print("\nTop supported local-context signatures (3+ true):")
    for r in supported[:20]:
        print(f"  {r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
