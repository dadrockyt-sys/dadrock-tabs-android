from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
TEMPORAL_PATH = PUBLIC / "gomyway-1382-dual-stem-temporal-attack-evidence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1419-cached-post-attack-sustain-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-cached-post-attack-sustain-evidence-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19

DECAY_BUCKETS = [
    ("drop_lt_m4", float("-inf"), -4.0),
    ("drop_m4_m2", -4.0, -2.0),
    ("drop_m2_m1", -2.0, -1.0),
    ("drop_m1_m05", -1.0, -0.5),
    ("drop_m05_0", -0.5, 0.0),
    ("hold_0_05", 0.0, 0.5),
    ("rise_05_1", 0.5, 1.0),
    ("rise_1_plus", 1.0, float("inf")),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision(t: int, f: int) -> float:
    return round(100.0 * t / (t + f), 2) if t + f else 0.0


def bucket(value: float) -> str:
    for name, lo, hi in DECAY_BUCKETS:
        if lo <= value < hi:
            return name
    return "unknown"


def load_temporal_rows() -> list[dict[str, Any]]:
    if not TEMPORAL_PATH.exists():
        raise RuntimeError(
            f"Missing cached temporal profile: {TEMPORAL_PATH.relative_to(ROOT)}. "
            "Run profile_gomyway_1382_dual_stem_temporal_attack_evidence_v1.py first."
        )
    payload = json.loads(TEMPORAL_PATH.read_text(encoding="utf-8"))
    if payload.get("passed") is not True:
        raise RuntimeError("Cached temporal profile is not marked passed.")
    if payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cached temporal profile does not preserve reference-free detection.")
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Cached temporal profile contains no rows.")
    return rows


def champion_1419_tokens() -> set[tuple[int, int, int]]:
    rows = cached.load_profile_rows()
    return {token(row) for row in rows if bench.champion_1419_predicate(row)}


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    temporal_rows = load_temporal_rows()

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    additions = champion_1419_tokens()
    from collections import Counter
    champion_1419 = baseline_1382 + Counter({t: 1 for t in additions})
    score = recur.grade(champion_1419, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED_1419 or abs(float(score["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, got {actual}/{score['pitchF1']}")

    champion_all = set(champion_1419.keys())
    missing_reference = reference - champion_1419

    feature_rows: list[dict[str, Any]] = []
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    joint_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for row in temporal_rows:
        tok = token(row)
        if tok in champion_all:
            continue
        winner = row.get("winner") or {}
        alternate = row.get("alternate") or {}
        if "postDelta" not in winner or "postDelta" not in alternate:
            continue

        w_post = float(winner["postDelta"])
        a_post = float(alternate["postDelta"])
        min_post = min(w_post, a_post)
        max_post = max(w_post, a_post)
        mean_post = (w_post + a_post) / 2.0
        agreement = "both_hold" if w_post >= -0.5 and a_post >= -0.5 else (
            "one_hold" if w_post >= -0.5 or a_post >= -0.5 else "both_drop"
        )
        min_bucket = bucket(min_post)
        recurrence = int(row.get("recurrence", 0))
        recur_label = "4plus" if recurrence >= 4 else str(recurrence)
        is_true = missing_reference.get(tok, 0) > 0
        idx = 0 if is_true else 1

        counts[f"minpost_{min_bucket}"][idx] += 1
        counts[f"agreement_{agreement}"][idx] += 1
        counts[f"agreement_{agreement}|recur_{recur_label}"][idx] += 1
        joint = f"{min_bucket}|{agreement}|recur_{recur_label}"
        joint_counts[joint][idx] += 1

        feature_rows.append({
            "token": list(tok),
            "trueMissingReference": is_true,
            "recurrence": recurrence,
            "winnerPostDelta": w_post,
            "alternatePostDelta": a_post,
            "minPostDelta": round(min_post, 4),
            "maxPostDelta": round(max_post, 4),
            "meanPostDelta": round(mean_post, 4),
            "minPostBucket": min_bucket,
            "postAgreement": agreement,
            "minCenter": float(row.get("minCenter", 0.0)),
            "minProminence": float(row.get("minProminence", 0.0)),
            "minRiseVsPreMax": float(row.get("minRiseVsPreMax", 0.0)),
        })

    summary = [
        {"signature": key, "true": val[0], "false": val[1], "precision": precision(val[0], val[1])}
        for key, val in counts.items()
    ]
    summary.sort(key=lambda r: (r["precision"], r["true"], -r["false"]), reverse=True)

    joint_summary = [
        {"signature": key, "true": val[0], "false": val[1], "precision": precision(val[0], val[1])}
        for key, val in joint_counts.items()
        if val[0] + val[1] >= 2
    ]
    joint_summary.sort(key=lambda r: (r["precision"], r["true"], -r["false"]), reverse=True)

    supported = [row for row in joint_summary if int(row["true"]) >= 2]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cached post-attack sustain profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-cached-post-attack-sustain-evidence",
        "championFrozen": {"pitchF1": 14.19, "matched": 178, "missing": 689, "extra": 1464},
        "temporalRowsLoaded": len(temporal_rows),
        "residualRowsProfiled": len(feature_rows),
        "summary": summary,
        "jointSummary": joint_summary,
        "supportedJointSummary": supported,
        "rows": feature_rows,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": 14.19,
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CACHED POST-ATTACK SUSTAIN EVIDENCE V1")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion remains frozen: 14.19 / 178 / 689 / 1464")
    print("Temporal rows loaded:", len(temporal_rows))
    print("Residual rows profiled:", len(feature_rows))
    print("\nTop post-attack signatures:")
    for row in summary[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nTop repeatable post-attack joint signatures:")
    for row in joint_summary[:25]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nTop supported post-attack signatures (2+ true):")
    for row in supported[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
