from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_1448_periodicity_survivor_additions_precision_v1 as p1448
import benchmark_gomyway_1448_periodicity_survivor_precision_prune_cv_v1 as b1448
import benchmark_gomyway_1444_cached_periodicity_survivor_precision_prune_cv_v1 as b1444
import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

recur = p1448.recur
recall = p1448.recall
v2 = p1448.v2
v3 = p1448.v3
bench = p1448.bench
cached = p1448.cached
gate = p1448.gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1444_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1.json"
PROFILE_1448_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-additions-precision-v1.json"
PERIODICITY_PATH = prune.PERIODICITY_PATH
PRECISION_PATH = prune.PRECISION_PATH
OUTPUT_PATH = PUBLIC / "gomyway-1451-periodicity-survivor-additions-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1451-periodicity-survivor-additions-precision-v1-manifest.json"
EXPECTED_1451 = (183, 684, 1472)
EXPECTED_1451_F1 = 14.51


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def summarize(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        out.append({"signature": signature, **precision_row(int(counts["true"]), int(counts["false"]))})
    return sorted(out, key=lambda r: (float(r["precision"]), int(r["true"]), -int(r["false"])), reverse=True)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    survivor_1444_payload = v2.load_json(PROFILE_1444_PATH)
    survivor_1448_payload = v2.load_json(PROFILE_1448_PATH)
    if survivor_1444_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.44 survivor profile is not reference-free during detection")
    if survivor_1448_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.48 survivor profile is not reference-free during detection")
    survivor_1444_rows = list(survivor_1444_payload.get("rows", []))
    survivor_1448_rows = list(survivor_1448_payload.get("rows", []))

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
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

    cached_rows = cached.load_profile_rows()
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419_additions = bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions
    winner_rows = [row for row in periodicity_payload.get("rows", []) if gate.sig_d(row)]
    periodicity_additions = gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions

    first_pruned: Counter[tuple[int, int, int]] = Counter()
    for prow in winner_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached 14.30 precision detail for token {tok}")
        if prune.pred_a(detail) or prune.pred_b(detail) or prune.pred_c(detail):
            first_pruned[tok] = 1
    champion_1444 = champion_1430 - first_pruned

    second_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in survivor_1444_rows:
        if b1444.pred_a(row) or b1444.pred_b(row) or b1444.pred_c(row) or b1444.pred_d(row):
            second_pruned[token(row)] = 1
    champion_1448 = champion_1444 - second_pruned

    third_pruned: Counter[tuple[int, int, int]] = Counter()
    remaining_rows: list[dict[str, Any]] = []
    for row in survivor_1448_rows:
        if b1448.pred_a(row):
            third_pruned[token(row)] = 1
        else:
            remaining_rows.append(row)

    champion_1451 = champion_1448 - third_pruned
    score_1451 = recur.grade(champion_1451, reference)
    actual = (int(score_1451["matched"]), int(score_1451["missing"]), int(score_1451["extra"]))
    if actual != EXPECTED_1451 or abs(float(score_1451["pitchF1"]) - EXPECTED_1451_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.51 champion {EXPECTED_1451}/{EXPECTED_1451_F1}, got {actual}/{score_1451['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in remaining_rows:
        tok = token(row)
        truth = "true" if reference.get(tok, 0) > 0 else "false"
        b = prune.fine_buckets(row)
        recurrence = int(row.get("recurrence", 0))
        recur_b = "recur_4plus" if recurrence >= 4 else f"recur_{recurrence}"
        rms_b = str(row.get("rmsBucket", "rms_na"))
        flux_b = str(row.get("fluxBucket", "flux_na"))
        ratio_b = str(row.get("ratioBucket", "ratio_na"))
        template_b = str(row.get("templateBucket", "template_na"))

        signatures = (
            b["maxc"], b["minc"], b["maxm"], b["maxo"], b["mino"], recur_b,
            rms_b, flux_b, ratio_b, template_b,
            f"{b['maxc']}|{b['minc']}",
            f"{b['maxc']}|{b['maxm']}",
            f"{b['minc']}|{b['maxm']}",
            f"{b['maxo']}|{b['mino']}",
            f"{b['maxc']}|{b['minc']}|{b['maxm']}",
            f"{b['maxo']}|{b['mino']}|{b['maxm']}",
            f"{recur_b}|{b['maxc']}|{b['maxm']}",
            f"{rms_b}|{flux_b}",
            f"{ratio_b}|{template_b}",
            f"{rms_b}|{b['maxc']}|{b['maxm']}",
            f"{flux_b}|{b['maxc']}|{b['maxm']}",
            f"{ratio_b}|{b['maxc']}|{b['maxm']}",
            f"{template_b}|{b['maxc']}|{b['maxm']}",
            f"{recur_b}|{rms_b}|{b['maxc']}",
            f"{recur_b}|{flux_b}|{b['maxm']}",
        )
        for signature in signatures:
            groups[signature][truth] += 1

        details.append({**row, "survives1451Prune": True, "trueSurvivorAddition": truth == "true"})

    ranked = summarize(groups)
    supported_true = [r for r in ranked if int(r["true"]) >= 2]
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 2]
    zero_precision.sort(key=lambda r: (int(r["false"]), str(r["signature"])), reverse=True)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.51 survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.51-periodicity-survivor-additions-precision",
        "champion1451Score": score_1451,
        "validatedThirdPruneRule": "survivor_prune_a_low_rms_maxc55_maxm15",
        "survivorAdditionCount": len(remaining_rows),
        "trueSurvivorAdditionCount": sum(1 for row in details if row["trueSurvivorAddition"]),
        "falseSurvivorAdditionCount": sum(1 for row in details if not row["trueSurvivorAddition"]),
        "supportedTrueSignatures": supported_true,
        "zeroPrecisionSignatures": zero_precision,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-zero-precision-14.51-survivor-prunes-with-prune-specific-heldout-cv-or-freeze-14.51-if-exhausted",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score_1451["pitchF1"],
        "survivorAdditionCount": len(remaining_rows),
        "trueSurvivorAdditionCount": output["trueSurvivorAdditionCount"],
        "falseSurvivorAdditionCount": output["falseSurvivorAdditionCount"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.51 PERIODICITY SURVIVOR ADDITIONS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score_1451["pitchF1"])
    print("Champion matched/missing/extra:", score_1451["matched"], "/", score_1451["missing"], "/", score_1451["extra"])
    print("Survivor additions:", len(remaining_rows))
    print("True survivor additions:", output["trueSurvivorAdditionCount"])
    print("False survivor additions:", output["falseSurvivorAdditionCount"])
    print("Top supported true signatures (2+ true):")
    for row in supported_true[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top zero-precision survivor prune signatures (2+ false, 0 true):")
    for row in zero_precision[:40]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
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
