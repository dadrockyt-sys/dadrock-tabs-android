from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1454_periodicity_survivor_additions_precision_v1 as p1454
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy
import benchmark_gomyway_1451_periodicity_survivor_precision_prune_cv_v1 as b1451
import benchmark_gomyway_1448_periodicity_survivor_precision_prune_cv_v1 as b1448
import benchmark_gomyway_1444_cached_periodicity_survivor_precision_prune_cv_v1 as b1444
import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

recur = p1454.recur
recall = p1454.recall
v2 = p1454.v2
v3 = p1454.v3
bench = p1454.bench
cached = p1454.cached
gate = p1454.gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1444_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1.json"
PROFILE_1448_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-additions-precision-v1.json"
PROFILE_1451_PATH = PUBLIC / "gomyway-1451-periodicity-survivor-additions-precision-v1.json"
PERIODICITY_PATH = prune.PERIODICITY_PATH
PRECISION_PATH = prune.PRECISION_PATH
OUTPUT_PATH = PUBLIC / "gomyway-1454-broad-champion-extras-cross-signatures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1454-broad-champion-extras-cross-signatures-v1-manifest.json"
EXPECTED = (183, 684, 1467)
EXPECTED_F1 = 14.54


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


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

    payload_1444 = v2.load_json(PROFILE_1444_PATH)
    payload_1448 = v2.load_json(PROFILE_1448_PATH)
    payload_1451 = v2.load_json(PROFILE_1451_PATH)
    for name, payload in (("14.44", payload_1444), ("14.48", payload_1448), ("14.51", payload_1451)):
        if payload.get("professionalReferenceUsedDuringDetection") is not False:
            raise RuntimeError(f"{name} survivor profile is not reference-free during detection")

    rows_1444 = list(payload_1444.get("rows", []))
    rows_1448 = list(payload_1448.get("rows", []))
    rows_1451 = list(payload_1451.get("rows", []))

    candidate_payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(candidate_payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    periodicity_payload = v2.load_json(PERIODICITY_PATH)
    precision_payload = v2.load_json(PRECISION_PATH)
    precision_by_token = {token(row): row for row in precision_payload.get("rows", [])}

    # Reconstruct the exact frozen 14.54 champion.
    cached_rows = cached.load_profile_rows()
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419 = baseline_1382 + bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    periodicity_rows = [row for row in periodicity_payload.get("rows", []) if gate.sig_d(row)]
    champion_1430 = champion_1419 + gate.rows_to_counter(periodicity_rows, lambda row: True)

    first_pruned: Counter[tuple[int, int, int]] = Counter()
    for prow in periodicity_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached 14.30 precision detail for token {tok}")
        if prune.pred_a(detail) or prune.pred_b(detail) or prune.pred_c(detail):
            first_pruned[tok] = 1
    champion_1444 = champion_1430 - first_pruned

    second_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1444:
        if b1444.pred_a(row) or b1444.pred_b(row) or b1444.pred_c(row) or b1444.pred_d(row):
            second_pruned[token(row)] = 1
    champion_1448 = champion_1444 - second_pruned

    third_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1448:
        if b1448.pred_a(row):
            third_pruned[token(row)] = 1
    champion_1451 = champion_1448 - third_pruned

    fourth_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1451:
        if b1451.pred_a(row) or b1451.pred_b(row) or b1451.pred_c(row):
            fourth_pruned[token(row)] = 1
    champion = champion_1451 - fourth_pruned

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.54 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    # Independent detector evidence. The professional reference is not used to
    # compute these features; it is consulted only below to label precision.
    winner_scores = legacy.spectral.specialist_scores(legacy.WINNER_STEM, grid)
    alt_scores = legacy.spectral.specialist_scores(legacy.ALT_STEM, grid)
    base_winner = legacy.precond.prediction(legacy.precond.grouped_for(legacy.WINNER_STEM, grid))
    base_alt = legacy.precond.prediction(legacy.precond.grouped_for(legacy.ALT_STEM, grid))
    base_champion = legacy.precond.merge_with_cap(base_winner, base_alt)
    top1 = legacy.gate.accepted_tokens(legacy.temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = legacy.adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)

    dimensions: dict[str, dict[str, Counter[str]]] = {
        name: defaultdict(Counter)
        for name in (
            "scoreBucket", "stemAgreement", "recurrenceReason",
            "scoreAgreement", "stepAgreement", "stepScore",
            "step", "pitch", "stepPitch", "section",
            "periodicity", "periodicityScoreAgreement",
        )
    }

    periodicity_by_token = {token(row): row for row in periodicity_payload.get("rows", [])}
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

        # Diagnostic-only coordinate views. Never promote these directly into
        # production rules without independent detector/audio evidence.
        add(dimensions["step"], str(step), truth, count)
        add(dimensions["pitch"], str(pitch), truth, count)
        add(dimensions["stepPitch"], f"step{step}|midi{pitch}", truth, count)
        add(dimensions["section"], legacy.section_name(measure), truth, count)

        prow = periodicity_by_token.get(tok)
        if prow is not None:
            b = prune.fine_buckets(prow)
            periodicity_sig = f"{b['maxc']}|{b['minc']}|{b['maxm']}"
            add(dimensions["periodicity"], periodicity_sig, truth, count)
            add(
                dimensions["periodicityScoreAgreement"],
                f"{periodicity_sig}|score{score_bucket}|{agreement_bucket}",
                truth,
                count,
            )

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    profiles = {name: precision_rows(groups) for name, groups in dimensions.items()}

    # Broad pruning hypotheses need stronger support than the tiny periodicity
    # survivor pocket. Require at least 5 observed false events and zero true.
    eligible_dimensions = (
        "scoreBucket", "stemAgreement", "recurrenceReason",
        "scoreAgreement", "periodicity", "periodicityScoreAgreement",
    )
    zero_precision_generalizable: list[dict[str, Any]] = []
    for dimension in eligible_dimensions:
        for row in profiles[dimension]:
            if int(row["true"]) == 0 and int(row["false"]) >= 5:
                zero_precision_generalizable.append({"dimension": dimension, **row})
    zero_precision_generalizable.sort(
        key=lambda row: (-int(row["false"]), str(row["dimension"]), str(row["signature"]))
    )

    diagnostic_zero_precision: list[dict[str, Any]] = []
    for dimension in ("stepAgreement", "stepScore", "step", "pitch", "stepPitch", "section"):
        for row in profiles[dimension]:
            if int(row["true"]) == 0 and int(row["false"]) >= 5:
                diagnostic_zero_precision.append({"dimension": dimension, **row})
    diagnostic_zero_precision.sort(
        key=lambda row: (-int(row["false"]), str(row["dimension"]), str(row["signature"]))
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.54 broad extras profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.54-broad-champion-extras-cross-signatures",
        "champion1454Score": score,
        "championPredictionCount": int(sum(champion.values())),
        "championMatchedCount": int(sum(matched.values())),
        "championExtraCount": int(sum(extras.values())),
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
        "recommendedNextAction": "benchmark-only-generalizable-zero-precision-broad-extra-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 14.54 BROAD CHAMPION EXTRAS CROSS-SIGNATURES V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Champion predictions:", sum(champion.values()))
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
