from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1382_champion_cached_onset_fundamental_joint_gate_v1 as cached

joint = cached.joint
onset = cached.onset
attack = cached.attack
recur = cached.recur
v2 = cached.v2
v3 = cached.v3
recall = cached.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = cached.PROFILE_PATH
OUTPUT_PATH = PUBLIC / "gomyway-1417-champion-joint-recall-additions-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1417-champion-joint-recall-additions-profile-v1-manifest.json"
EXPECTED_BASELINE = (173, 694, 1464)
EXPECTED_BASELINE_F1 = 13.82
EXPECTED_CHAMPION = (178, 689, 1467)
EXPECTED_CHAMPION_F1 = 14.17


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_cached_rows() -> list[dict[str, Any]]:
    rows = cached.load_profile_rows()
    return rows


def winner_predicate(row: dict[str, Any]) -> bool:
    return (
        cached.sig_a(row)
        or cached.sig_b(row)
        or cached.sig_c(row)
        or cached.sig_d(row)
        or cached.sig_e(row)
    )


def sig_names(row: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for name, fn in [
        ("sig_a", cached.sig_a),
        ("sig_b", cached.sig_b),
        ("sig_c", cached.sig_c),
        ("sig_d", cached.sig_d),
        ("sig_e", cached.sig_e),
    ]:
        if fn(row):
            names.append(name)
    return names


def bucket(v: float, cuts: list[tuple[str, float | None, float | None]]) -> str:
    for name, lo, hi in cuts:
        if (lo is None or v >= lo) and (hi is None or v < hi):
            return name
    return "other"


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    rows = load_cached_rows()
    print(f"Loaded cached joint detector rows: {len(rows)}", flush=True)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline, _, _ = recur.build_frozen_1382(grid)
    baseline_score = recur.grade(baseline, reference)
    baseline_actual = (
        int(baseline_score["matched"]),
        int(baseline_score["missing"]),
        int(baseline_score["extra"]),
    )
    if baseline_actual != EXPECTED_BASELINE or abs(float(baseline_score["pitchF1"]) - EXPECTED_BASELINE_F1) > 0.01:
        raise RuntimeError(
            f"Expected 13.82 baseline {EXPECTED_BASELINE}/{EXPECTED_BASELINE_F1}, "
            f"got {baseline_actual}/{baseline_score['pitchF1']}"
        )

    winner_rows = [row for row in rows if winner_predicate(row)]
    additions = Counter()
    row_by_token: dict[tuple[int, int, int], dict[str, Any]] = {}
    for row in winner_rows:
        token = tuple(int(v) for v in row["token"])
        additions[token] = 1
        row_by_token[token] = row

    champion = baseline + additions
    champion_score = recur.grade(champion, reference)
    champion_actual = (
        int(champion_score["matched"]),
        int(champion_score["missing"]),
        int(champion_score["extra"]),
    )
    if champion_actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_CHAMPION_F1) > 0.01:
        raise RuntimeError(
            f"Expected 14.17 champion {EXPECTED_CHAMPION}/{EXPECTED_CHAMPION_F1}, "
            f"got {champion_actual}/{champion_score['pitchF1']}"
        )

    missing_before = reference - baseline
    profiled_rows: list[dict[str, Any]] = []

    signature_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    ratio_template_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    onset_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    recurrence_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    rms_cuts = [
        ("rms_lt0", None, 0.0),
        ("rms_0_010", 0.0, 0.10),
        ("rms_010_050", 0.10, 0.50),
        ("rms_050_100", 0.50, 1.0),
        ("rms_100plus", 1.0, None),
    ]
    flux_cuts = [
        ("flux_0_010", 0.0, 0.10),
        ("flux_010_025", 0.10, 0.25),
        ("flux_025_050", 0.25, 0.50),
        ("flux_050_100", 0.50, 1.0),
        ("flux_100plus", 1.0, None),
    ]

    for token in sorted(additions):
        row = row_by_token[token]
        is_true = missing_before.get(token, 0) > 0
        idx = 0 if is_true else 1
        names = sig_names(row)
        primary = "+".join(names) if names else "none"
        signature_counts[primary][idx] += 1

        ratio_key = f"{row['ratioBucket']}|{row['templateBucket']}"
        ratio_template_counts[ratio_key][idx] += 1
        onset_key = f"{row['rmsBucket']}|{row['fluxBucket']}"
        onset_counts[onset_key][idx] += 1
        recurrence = int(row["recurrence"])
        recurrence_counts[f"recur_{'4plus' if recurrence >= 4 else recurrence}"][idx] += 1

        profiled_rows.append(
            {
                "token": list(token),
                "trueMissingReference": is_true,
                "winnerSignatures": names,
                "recurrence": recurrence,
                "rmsBucket": row["rmsBucket"],
                "fluxBucket": row["fluxBucket"],
                "ratioBucket": row["ratioBucket"],
                "templateBucket": row["templateBucket"],
                "minRmsLog2Rise": row["minRmsLog2Rise"],
                "minPositiveFlux": row["minPositiveFlux"],
                "minTargetVsSubharmonicRatio": row["minTargetVsSubharmonicRatio"],
                "minTemplateRatio": row["minTemplateRatio"],
            }
        )

    def summarize(counts: dict[str, list[int]]) -> list[dict[str, Any]]:
        items = []
        for key, value in counts.items():
            items.append({"signature": key, **precision_row(value[0], value[1])})
        items.sort(
            key=lambda r: (float(r["precision"]), int(r["true"]), -int(r["false"])),
            reverse=True,
        )
        return items

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.17 additions profiler")

    true_additions = sum(1 for row in profiled_rows if row["trueMissingReference"])
    false_additions = len(profiled_rows) - true_additions

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.17-joint-recall-additions-residual-profile",
        "baselineScore": baseline_score,
        "championScore": champion_score,
        "winner": "union_top3_plus_two_50",
        "additionCount": len(profiled_rows),
        "trueAdditions": true_additions,
        "falseAdditions": false_additions,
        "rows": profiled_rows,
        "winnerSignatureSummary": summarize(signature_counts),
        "onsetSummary": summarize(onset_counts),
        "fundamentalSummary": summarize(ratio_template_counts),
        "recurrenceSummary": summarize(recurrence_counts),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-reference-free-prune-of-14.17-winner-false-additions-if-repeatable-signature-exists-else-retain-14.17-and-resume-recall",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "championMatched": champion_score["matched"],
        "championMissing": champion_score["missing"],
        "championExtra": champion_score["extra"],
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.17 CHAMPION JOINT RECALL ADDITIONS PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print(
        "Champion matched/missing/extra:",
        champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"],
    )
    print("Winner additions:", len(profiled_rows))
    print("True additions:", true_additions)
    print("False additions:", false_additions)
    print("Winner signature precision:")
    for row in summarize(signature_counts):
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
    print("Onset precision:")
    for row in summarize(onset_counts):
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
    print("Fundamental/overtone precision:")
    for row in summarize(ratio_template_counts):
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
    print("Recurrence precision:")
    for row in summarize(recurrence_counts):
        print(
            f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%"
        )
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
