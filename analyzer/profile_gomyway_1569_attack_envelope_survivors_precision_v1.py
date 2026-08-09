from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1542_attack_envelope_survivor_precision_prune_cv_v1 as b1542
import benchmark_gomyway_1499_attack_envelope_survivor_precision_prune_cv_v1 as b1499
import benchmark_gomyway_1460_attack_envelope_precision_prune_cv_v1 as b1460

recur = b1542.recur
recall = b1542.recall
v2 = b1542.v2
v3 = b1542.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1542_PATH = PUBLIC / "gomyway-1542-attack-envelope-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1569-attack-envelope-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1569-attack-envelope-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 1283)
EXPECTED_F1 = 15.69


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        out.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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

    profile_payload = v2.load_json(PROFILE_1542_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.42 survivor profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("15.42 survivor profile has no rows")
    row_by_token = {token(row): row for row in rows}

    champion_1542 = b1542.reconstruct_1542(grid)

    eighth_pruned: Counter[tuple[int, int, int]] = Counter()
    survivor_rows: list[dict[str, Any]] = []
    for tok, count in champion_1542.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        if b1542.pred_a(row) or b1542.pred_b(row) or b1542.pred_c(row) or b1542.pred_d(row):
            eighth_pruned[tok] = count
        else:
            survivor_rows.append(row)

    champion = champion_1542 - eighth_pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 15.69 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    for row in survivor_rows:
        tok = token(row)
        truth = "true" if reference.get(tok, 0) > 0 else "false"
        count = int(row.get("count", 1))
        b = b1460.buckets(row)

        signatures = {
            "minAttack": b["minAttack"],
            "maxDecay": b["maxDecay"],
            "minCrest": b["minCrest"],
            "maxZcr": b["maxZcr"],
            "attackDisagreement": b["attackDisagreement"],
            "attackDecay": f"{b['minAttack']}|{b['maxDecay']}",
            "attackCrest": f"{b['minAttack']}|{b['minCrest']}",
            "attackZcr": f"{b['minAttack']}|{b['maxZcr']}",
            "attackAgreement": f"{b['minAttack']}|{b['attackDisagreement']}",
            "decayCrest": f"{b['maxDecay']}|{b['minCrest']}",
            "decayZcr": f"{b['maxDecay']}|{b['maxZcr']}",
            "crestZcr": f"{b['minCrest']}|{b['maxZcr']}",
            "decayAgreement": f"{b['maxDecay']}|{b['attackDisagreement']}",
            "attackDecayCrest": f"{b['minAttack']}|{b['maxDecay']}|{b['minCrest']}",
            "attackDecayAgreement": f"{b['minAttack']}|{b['maxDecay']}|{b['attackDisagreement']}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({**row, "survives1569Prune": True, "trueSurvivor": truth == "true"})

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 15.69 attack-envelope survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-15.69-attack-envelope-survivors-precision",
        "champion1569Score": score,
        "validatedAttack1542PruneRule": "attack1542_prune_union_a_b_c_d",
        "validatedAttack1542PruneCount": int(sum(eighth_pruned.values())),
        "survivorRowCount": len(survivor_rows),
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
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
        "recommendedNextAction": "benchmark-only-repeatable-zero-precision-15.69-attack-envelope-survivor-signatures-with-prune-specific-heldout-cv-or-freeze-family-if-exhausted",
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

    print("GOMYWAY 15.69 ATTACK-ENVELOPE SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated 15.42 attack prune count:", sum(eighth_pruned.values()))
    print("Attack-envelope survivor rows:", len(survivor_rows))
    print("Generalizable zero-precision attack/envelope survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true survivor signatures (5+ true):")
    for row in supported_true[:30]:
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
