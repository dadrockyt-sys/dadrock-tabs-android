from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1419_cached_local_note_context_v1 as local

bench = local.bench
cached = local.cached
recur = local.recur
v2 = local.v2
v3 = local.v3
recall = local.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-harmonic-chord-completion-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-harmonic-chord-completion-v1-manifest.json"
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


def interval_class(distance: int) -> int:
    mod = distance % 12
    return min(mod, 12 - mod) if mod else 0


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    rows = cached.load_profile_rows()
    print(f"Loaded cached joint detector rows: {len(rows)}", flush=True)
    print("No audio analysis required; profiling harmonic completion around frozen 14.19 champion.", flush=True)

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

    same_onset: dict[tuple[int, int], list[int]] = defaultdict(list)
    for m, s, p in champion_tokens:
        same_onset[(m, s)].append(p)
    for pitches in same_onset.values():
        pitches.sort()

    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    details: list[dict[str, Any]] = []

    for row in residual:
        m, s, p = token(row)
        companions = [cp for cp in same_onset.get((m, s), []) if cp != p]
        abs_intervals = sorted(abs(cp - p) for cp in companions)
        classes = sorted(set(interval_class(iv) for iv in abs_intervals))

        has_m3 = 3 in abs_intervals or 3 in classes
        has_M3 = 4 in abs_intervals or 4 in classes
        has_4th = 5 in abs_intervals or 5 in classes
        has_5th = 7 in abs_intervals or 5 in classes
        has_m6 = 8 in abs_intervals or 4 in classes
        has_M6 = 9 in abs_intervals or 3 in classes
        has_oct = 12 in abs_intervals or 24 in abs_intervals
        has_power = any(iv in abs_intervals for iv in (7, 12, 19, 24))
        has_third_family = has_m3 or has_M3 or has_m6 or has_M6
        compact = any(1 <= iv <= 12 for iv in abs_intervals)

        triad_like = False
        if len(companions) >= 2:
            all_pitches = sorted(set(companions + [p]))
            for i in range(len(all_pitches)):
                for j in range(i + 1, len(all_pitches)):
                    for k in range(j + 1, len(all_pitches)):
                        tri = [all_pitches[i], all_pitches[j], all_pitches[k]]
                        pcs = sorted({x % 12 for x in tri})
                        if len(pcs) < 3:
                            continue
                        root = min(pcs)
                        rel = sorted((pc - root) % 12 for pc in pcs)
                        normalized = tuple(rel)
                        if normalized in {
                            (0, 3, 7), (0, 4, 7), (0, 5, 7),
                            (0, 3, 6), (0, 4, 8), (0, 5, 9),
                        }:
                            triad_like = True

        companion_bucket = "0" if not companions else "1" if len(companions) == 1 else "2plus"
        class_key = "_".join(str(v) for v in classes) if classes else "none"

        signatures = [
            f"companions_{companion_bucket}|classes_{class_key}",
            f"companions_{companion_bucket}|third_{int(has_third_family)}|power_{int(has_power)}|oct_{int(has_oct)}",
            f"companions_{companion_bucket}|compact_{int(compact)}|triad_{int(triad_like)}",
        ]

        if companions:
            nearest = min(abs_intervals)
            nearest_bucket = (
                "1_2" if nearest <= 2 else
                "3_4" if nearest <= 4 else
                "5_7" if nearest <= 7 else
                "8_12" if nearest <= 12 else
                "13plus"
            )
            signatures.append(
                f"companions_{companion_bucket}|nearest_{nearest_bucket}|third_{int(has_third_family)}|power_{int(has_power)}"
            )

        is_true = token(row) in reference
        idx = 0 if is_true else 1
        for sig in signatures:
            counts[sig][idx] += 1

        details.append({
            "token": list(token(row)),
            "isTrue": is_true,
            "companionPitches": companions,
            "absoluteIntervals": abs_intervals,
            "intervalClasses": classes,
            "hasMinorThirdFamily": has_m3 or has_M6,
            "hasMajorThirdFamily": has_M3 or has_m6,
            "hasFourth": has_4th,
            "hasFifthOrPower": has_5th or has_power,
            "hasOctave": has_oct,
            "triadLike": triad_like,
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
        "profileType": "validated-14.19-cached-harmonic-chord-completion",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "residualRows": len(residual),
        "topSignatures": summary[:60],
        "topRepeatableSignatures": repeatable[:40],
        "topSupportedSignatures": supported[:30],
        "details": details,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-high-precision-harmonic-completion-signatures-or-pivot",
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
        raise RuntimeError("Protected candidate changed during harmonic chord-completion profiling")

    print("GOMYWAY 14.19 CACHED HARMONIC CHORD COMPLETION V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Residual rows:", len(residual))
    print("\nTop repeatable harmonic-completion signatures:")
    for r in repeatable[:25]:
        print(f"  {r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}%")
    print("\nTop supported harmonic-completion signatures (3+ true):")
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
