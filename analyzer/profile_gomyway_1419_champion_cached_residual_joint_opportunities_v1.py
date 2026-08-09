from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1382_champion_cached_onset_fundamental_joint_gate_v1 as cached

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1382-onset-fundamental-joint-evidence-v1.json"
PRUNE_RESULT_PATH = PUBLIC / "gomyway-1417-champion-cached-joint-false-addition-prune-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1419-champion-cached-residual-joint-opportunities-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-champion-cached-residual-joint-opportunities-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_F1 = 14.19


def recur_label(row: dict[str, Any]) -> str:
    r = int(row["recurrence"])
    return "4plus" if r >= 4 else str(r)


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def champion_1419_addition(row: dict[str, Any]) -> bool:
    # Frozen validated 14.19 successor:
    # clean a/b/c signatures + sig_d ratio<10 + sig_e flux<0.20.
    if cached.sig_a(row) or cached.sig_b(row) or cached.sig_c(row):
        return True
    if cached.sig_d(row) and float(row["minTargetVsSubharmonicRatio"]) < 10.0:
        return True
    if cached.sig_e(row) and float(row["minPositiveFlux"]) < 0.20:
        return True
    return False


def summarize(rows: list[dict[str, Any]], key_fn) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = defaultdict(lambda: {"true": 0, "false": 0, "tokens": []})
    for row in rows:
        key = str(key_fn(row))
        b = buckets[key]
        if bool(row.get("trueMissingReference")):
            b["true"] += 1
        else:
            b["false"] += 1
        if len(b["tokens"]) < 12:
            b["tokens"].append(list(token(row)))

    out: list[dict[str, Any]] = []
    for key, b in buckets.items():
        total = int(b["true"]) + int(b["false"])
        precision = (100.0 * int(b["true"]) / total) if total else 0.0
        out.append(
            {
                "key": key,
                "true": int(b["true"]),
                "false": int(b["false"]),
                "total": total,
                "precision": round(precision, 2),
                "tokens": b["tokens"],
            }
        )
    out.sort(key=lambda x: (-x["precision"], -x["true"], x["false"], x["key"]))
    return out


def main() -> None:
    if not PROFILE_PATH.exists():
        raise RuntimeError(
            f"Missing cached joint profile: {PROFILE_PATH.relative_to(ROOT)}. "
            "Run profile_gomyway_1382_onset_fundamental_joint_evidence_v1.py first."
        )
    if not PRUNE_RESULT_PATH.exists():
        raise RuntimeError(
            f"Missing 14.19 prune result: {PRUNE_RESULT_PATH.relative_to(ROOT)}. "
            "Run benchmark_gomyway_1417_champion_cached_joint_false_addition_prune_v1.py first."
        )

    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    prune = json.loads(PRUNE_RESULT_PATH.read_text(encoding="utf-8"))
    if profile.get("passed") is not True or profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cached joint profile is not a passed reference-free feature cache.")
    if prune.get("passed") is not True or prune.get("validatedNewChampion") is not True:
        raise RuntimeError("14.19 prune result is not a validated new champion.")

    winner = prune.get("winnerEvaluation", {}).get("fullScore", {})
    actual = (int(winner.get("matched", -1)), int(winner.get("missing", -1)), int(winner.get("extra", -1)))
    if actual != EXPECTED_1419 or abs(float(winner.get("pitchF1", -1.0)) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_F1}, got {actual}/{winner.get('pitchF1')}")

    rows = profile.get("rows")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("Cached joint profile contains no rows.")

    champion_tokens = {token(row) for row in rows if champion_1419_addition(row)}
    residual = [row for row in rows if token(row) not in champion_tokens]

    exact = summarize(
        residual,
        lambda r: "|".join(
            [
                str(r["rmsBucket"]),
                str(r["fluxBucket"]),
                str(r["ratioBucket"]),
                str(r["templateBucket"]),
                "recur_" + recur_label(r),
            ]
        ),
    )
    onset_fundamental = summarize(
        residual,
        lambda r: "|".join(
            [
                str(r["rmsBucket"]),
                str(r["fluxBucket"]),
                str(r["ratioBucket"]),
                str(r["templateBucket"]),
            ]
        ),
    )
    fundamental_recur = summarize(
        residual,
        lambda r: "|".join(
            [
                str(r["ratioBucket"]),
                str(r["templateBucket"]),
                "recur_" + recur_label(r),
            ]
        ),
    )

    interesting_exact = [b for b in exact if b["true"] >= 1 and b["precision"] >= 20.0][:40]
    repeatable_exact = [b for b in exact if b["true"] >= 2][:40]
    repeatable_joint = [b for b in onset_fundamental if b["true"] >= 2][:40]
    repeatable_fundamental = [b for b in fundamental_recur if b["true"] >= 2][:40]

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "cached-14.19-residual-reference-free-onset-fundamental-opportunities",
        "championScore": winner,
        "cachedFeatureRows": len(rows),
        "championRecallAdditionTokens": len(champion_tokens),
        "residualRows": len(residual),
        "interestingExactBuckets": interesting_exact,
        "repeatableExactBuckets": repeatable_exact,
        "repeatableOnsetFundamentalBuckets": repeatable_joint,
        "repeatableFundamentalRecurrenceBuckets": repeatable_fundamental,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-or-high-confidence-residual-joint-buckets-against-frozen-14.19",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "input": str(PROFILE_PATH.relative_to(ROOT)),
        "championResult": str(PRUNE_RESULT_PATH.relative_to(ROOT)),
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": winner["pitchF1"],
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 CHAMPION CACHED RESIDUAL JOINT OPPORTUNITIES V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion pitch F1:", winner["pitchF1"])
    print("Champion matched/missing/extra:", winner["matched"], "/", winner["missing"], "/", winner["extra"])
    print("Cached feature rows:", len(rows))
    print("Champion recall addition tokens excluded:", len(champion_tokens))
    print("Residual feature rows:", len(residual))

    print("Top high-confidence exact residual buckets:")
    for b in interesting_exact[:25]:
        print(f"  {b['key']}: true={b['true']} false={b['false']} precision={b['precision']}%")

    print("Top repeatable exact residual buckets:")
    for b in repeatable_exact[:20]:
        print(f"  {b['key']}: true={b['true']} false={b['false']} precision={b['precision']}%")

    print("Top repeatable onset/fundamental residual buckets:")
    for b in repeatable_joint[:20]:
        print(f"  {b['key']}: true={b['true']} false={b['false']} precision={b['precision']}%")

    print("Professional reference used during detection: False")
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
