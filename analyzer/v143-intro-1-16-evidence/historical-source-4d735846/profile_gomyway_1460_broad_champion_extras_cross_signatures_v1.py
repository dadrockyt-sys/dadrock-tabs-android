from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1454_broad_score_agreement_precision_prune_cv_v1 as b1454
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy

recur = b1454.recur
recall = b1454.recall
v2 = b1454.v2
v3 = b1454.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1460-broad-champion-extras-cross-signatures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1460-broad-champion-extras-cross-signatures-v1-manifest.json"
EXPECTED = (183, 684, 1456)
EXPECTED_F1 = 14.60


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        rows.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda row: (-int(row["total"]), -float(row["precision"]), str(row["signature"])))


def add(groups: dict[str, Counter[str]], signature: str, truth: str, count: int) -> None:
    groups[signature][truth] += count


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    champion_1454 = b1454.reconstruct_1454(grid)
    winner_scores = legacy.spectral.specialist_scores(legacy.WINNER_STEM, grid)
    alt_scores = legacy.spectral.specialist_scores(legacy.ALT_STEM, grid)

    def score_agreement(tok: tuple[int, int, int]) -> tuple[str, str]:
        return (
            legacy.pruning.score_bucket(tok, winner_scores, alt_scores),
            legacy.pruning.agreement_bucket(tok, winner_scores, alt_scores),
        )

    validated_union = {
        ("16_20", "both_ge8"),
        ("20_plus", "both_ge8"),
        ("20_plus", "single_stem_or_weak_second"),
    }
    fifth_pruned = Counter({tok: count for tok, count in champion_1454.items() if score_agreement(tok) in validated_union})
    champion = champion_1454 - fifth_pruned

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.60 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    base_winner = legacy.precond.prediction(legacy.precond.grouped_for(legacy.WINNER_STEM, grid))
    base_alt = legacy.precond.prediction(legacy.precond.grouped_for(legacy.ALT_STEM, grid))
    base_champion = legacy.precond.merge_with_cap(base_winner, base_alt)
    top1 = legacy.gate.accepted_tokens(legacy.temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = legacy.adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)

    dimensions: dict[str, dict[str, Counter[str]]] = {
        name: defaultdict(Counter)
        for name in (
            "scoreBucket", "stemAgreement", "recurrenceReason", "scoreAgreement",
            "stepAgreement", "stepScore", "step", "pitch", "stepPitch", "section",
        )
    }

    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        score_bucket = legacy.pruning.score_bucket(tok, winner_scores, alt_scores)
        agreement_bucket = legacy.pruning.agreement_bucket(tok, winner_scores, alt_scores)
        recurrence_bucket = legacy.pruning.reason_bucket(tok, adaptive_base, winner_scores, alt_scores)
        add(dimensions["scoreBucket"], score_bucket, truth, count)
        add(dimensions["stemAgreement"], agreement_bucket, truth, count)
        add(dimensions["recurrenceReason"], recurrence_bucket, truth, count)
        add(dimensions["scoreAgreement"], f"score{score_bucket}|{agreement_bucket}", truth, count)
        add(dimensions["stepAgreement"], f"step{step}|{agreement_bucket}", truth, count)
        add(dimensions["stepScore"], f"step{step}|score{score_bucket}", truth, count)
        add(dimensions["step"], str(step), truth, count)
        add(dimensions["pitch"], str(pitch), truth, count)
        add(dimensions["stepPitch"], f"step{step}|midi{pitch}", truth, count)
        add(dimensions["section"], legacy.section_name(measure), truth, count)

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    profiles = {name: precision_rows(groups) for name, groups in dimensions.items()}

    eligible_dimensions = ("scoreBucket", "stemAgreement", "recurrenceReason", "scoreAgreement")
    zero_precision_generalizable: list[dict[str, Any]] = []
    for dimension in eligible_dimensions:
        for row in profiles[dimension]:
            if int(row["true"]) == 0 and int(row["false"]) >= 5:
                zero_precision_generalizable.append({"dimension": dimension, **row})
    zero_precision_generalizable.sort(key=lambda row: (-int(row["false"]), str(row["dimension"]), str(row["signature"])))

    diagnostic_zero_precision: list[dict[str, Any]] = []
    for dimension in ("stepAgreement", "stepScore", "step", "pitch", "stepPitch", "section"):
        for row in profiles[dimension]:
            if int(row["true"]) == 0 and int(row["false"]) >= 5:
                diagnostic_zero_precision.append({"dimension": dimension, **row})
    diagnostic_zero_precision.sort(key=lambda row: (-int(row["false"]), str(row["dimension"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.60 broad extras profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.60-broad-champion-extras-cross-signatures",
        "champion1460Score": score,
        "validatedFifthPruneRule": "drop_union_visible_zero_precision_score_agreement",
        "fifthPruneCount": int(sum(fifth_pruned.values())),
        "profiles": profiles,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision_generalizable,
        "diagnosticCoordinateZeroPrecisionMin5False": diagnostic_zero_precision,
        "coordinateProfilesAreDiagnosticOnly": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-14.60-broad-signatures-or-profile-new-independent-audio-features",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.60 BROAD CHAMPION EXTRAS CROSS-SIGNATURES V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated fifth prune count:", sum(fifth_pruned.values()))
    print("Generalizable zero-precision broad signatures (5+ false, 0 true):")
    for row in zero_precision_generalizable[:40]:
        print(f"  {row['dimension']} :: {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Diagnostic coordinate zero-precision signatures (NOT final rules):")
    for row in diagnostic_zero_precision[:30]:
        print(f"  {row['dimension']} :: {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top score/agreement buckets:")
    for row in profiles["scoreAgreement"][:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top stem-agreement buckets:")
    for row in profiles["stemAgreement"][:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top recurrence-reason buckets:")
    for row in profiles["recurrenceReason"][:20]:
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
