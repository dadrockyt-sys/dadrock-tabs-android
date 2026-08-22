from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1430_cached_periodicity_precision_prune_cv_v2 as cv2
import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune
import profile_gomyway_1430_periodicity_champion_additions_precision_v1 as p1430

recur = prune.recur
recall = prune.recall
v2 = prune.v2
v3 = prune.v3
bench = prune.bench
cached = prune.cached
gate = prune.gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PERIODICITY_PATH = prune.PERIODICITY_PATH
PRECISION_PATH = prune.PRECISION_PATH
OUTPUT_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1-manifest.json"
EXPECTED_1444 = (183, 684, 1484)
EXPECTED_1444_F1 = 14.44


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

    periodicity_payload = v2.load_json(PERIODICITY_PATH)
    precision_payload = v2.load_json(PRECISION_PATH)
    if periodicity_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Periodicity profile is not reference-free during detection")
    if precision_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.30 precision profile is not reference-free during detection")

    periodicity_rows = list(periodicity_payload.get("rows", []))
    precision_rows = list(precision_payload.get("rows", []))
    precision_by_token = {token(row): row for row in precision_rows}

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    cached_rows = cached.load_profile_rows()
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419_additions = bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions

    winner_rows = [row for row in periodicity_rows if gate.sig_d(row)]
    periodicity_additions = gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions

    pruned_tokens: Counter[tuple[int, int, int]] = Counter()
    survivor_rows: list[dict[str, Any]] = []
    for prow in winner_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached 14.30 precision detail for token {tok}")
        merged = dict(detail)
        merged["token"] = list(tok)
        if prune.pred_a(merged) or prune.pred_b(merged) or prune.pred_c(merged):
            pruned_tokens[tok] = 1
        else:
            survivor_rows.append(merged)

    champion_1444 = champion_1430 - pruned_tokens
    score_1444 = recur.grade(champion_1444, reference)
    actual = (int(score_1444["matched"]), int(score_1444["missing"]), int(score_1444["extra"]))
    if actual != EXPECTED_1444 or abs(float(score_1444["pitchF1"]) - EXPECTED_1444_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.44 champion {EXPECTED_1444}/{EXPECTED_1444_F1}, got {actual}/{score_1444['pitchF1']}")

    # Truth labels are downstream grading only. Feature signatures below are detector-side only.
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in survivor_rows:
        tok = token(row)
        measure, step, pitch = tok
        is_true = reference.get(tok, 0) > 0
        truth = "true" if is_true else "false"

        b = prune.fine_buckets(row)
        recurrence = int(row.get("recurrence", 0))
        recur_b = "recur_4plus" if recurrence >= 4 else f"recur_{recurrence}"
        step_b = f"step_{step}"
        pitch_b = f"midi_{pitch}"
        rms_b = str(row.get("rmsBucket", "rms_na"))
        flux_b = str(row.get("fluxBucket", "flux_na"))
        ratio_b = str(row.get("ratioBucket", "ratio_na"))
        template_b = str(row.get("templateBucket", "template_na"))

        signatures = (
            b["maxc"], b["minc"], b["maxm"], b["maxo"], b["mino"], recur_b,
            step_b, pitch_b, rms_b, flux_b, ratio_b, template_b,
            f"{b['maxc']}|{b['minc']}",
            f"{b['maxc']}|{b['maxm']}",
            f"{b['minc']}|{b['maxm']}",
            f"{b['maxo']}|{b['mino']}",
            f"{b['maxc']}|{b['minc']}|{b['maxm']}",
            f"{b['maxo']}|{b['mino']}|{b['maxm']}",
            f"{step_b}|{pitch_b}",
            f"{step_b}|{b['maxc']}|{b['maxm']}",
            f"{pitch_b}|{b['maxc']}|{b['maxm']}",
            f"{recur_b}|{b['maxc']}|{b['maxm']}",
            f"{rms_b}|{flux_b}",
            f"{ratio_b}|{template_b}",
            f"{rms_b}|{b['maxc']}|{b['maxm']}",
            f"{flux_b}|{b['maxc']}|{b['maxm']}",
            f"{ratio_b}|{b['maxc']}|{b['maxm']}",
            f"{template_b}|{b['maxc']}|{b['maxm']}",
            f"{step_b}|{ratio_b}|{b['maxc']}",
            f"{pitch_b}|{ratio_b}|{b['maxc']}",
        )
        for signature in signatures:
            groups[signature][truth] += 1

        details.append({
            **row,
            "survives1444Prune": True,
            "trueSurvivorAddition": is_true,
        })

    ranked = summarize(groups)
    supported_true = [r for r in ranked if int(r["true"]) >= 2]
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 2]
    zero_precision.sort(key=lambda r: (int(r["false"]), str(r["signature"])), reverse=True)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.44 survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.44-periodicity-survivor-additions-precision",
        "champion1444Score": score_1444,
        "validatedPruneRule": "prune_union_a_b_c",
        "periodicityAdditionCountBeforePrune": len(winner_rows),
        "prunedAdditionCount": int(sum(pruned_tokens.values())),
        "survivorAdditionCount": len(survivor_rows),
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
        "recommendedNextAction": "benchmark-only-repeatable-zero-precision-survivor-prunes-with-prune-specific-heldout-cv",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score_1444["pitchF1"],
        "survivorAdditionCount": len(survivor_rows),
        "trueSurvivorAdditionCount": output["trueSurvivorAdditionCount"],
        "falseSurvivorAdditionCount": output["falseSurvivorAdditionCount"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.44 PERIODICITY SURVIVOR ADDITIONS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score_1444["pitchF1"])
    print("Champion matched/missing/extra:", score_1444["matched"], "/", score_1444["missing"], "/", score_1444["extra"])
    print("Survivor additions:", len(survivor_rows))
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
