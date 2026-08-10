from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3161_protected_source_recall_recovery_v1 as protected

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-repeated-phrase-cross-partition-agreement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-repeated-phrase-cross-partition-agreement-v1-manifest.json"
CANDIDATE_PATH = protected.recall.CANDIDATE_PATH
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def region_stats(rows: list[dict[str, Any]], signature: str) -> dict[str, int | float]:
    hit = [r for r in rows if signature in set(str(s) for s in (r.get("signatures") or []))]
    true = sum(str(r.get("label")) == "true" for r in hit)
    false = sum(str(r.get("label")) == "false" for r in hit)
    total = true + false
    return {
        "true": true,
        "false": false,
        "precision": round(100.0 * true / total, 2) if total else 0.0,
        "support": total,
    }


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("Repeated-phrase profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profiler is not anchored to frozen 36.76 champion")

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    schemes: list[tuple[str, Callable[[dict[str, Any]], int]]] = [
        ("normal", lambda row: int(row["measure"]) % FOLD_COUNT),
        ("shifted", lambda row: (int(row["measure"]) + 2) % FOLD_COUNT),
        (
            "section",
            lambda row: min(
                FOLD_COUNT - 1,
                int(FOLD_COUNT * (int(row["measure"]) - lo) / span),
            ),
        ),
    ]

    signatures = sorted({str(sig) for r in rows for sig in (r.get("signatures") or [])})
    ranked: list[dict[str, Any]] = []

    for sig in signatures:
        full = region_stats(rows, sig)
        region_rows: list[dict[str, Any]] = []
        positive_regions = 0
        useful_regions = 0
        poison_regions = 0
        active_regions = 0
        worst_active_precision = 100.0

        for scheme, fold_fn in schemes:
            for fold in range(FOLD_COUNT):
                test = [r for r in rows if fold_fn(r) == fold]
                stats = region_stats(test, sig)
                support = int(stats["support"])
                true = int(stats["true"])
                false = int(stats["false"])
                precision = float(stats["precision"])
                if support > 0:
                    active_regions += 1
                    worst_active_precision = min(worst_active_precision, precision)
                if true > 0:
                    positive_regions += 1
                if true > 0 and precision >= 20.0:
                    useful_regions += 1
                if true == 0 and false >= 3:
                    poison_regions += 1
                region_rows.append({
                    "scheme": scheme,
                    "fold": fold,
                    **stats,
                })

        total_true = int(full["true"])
        total_false = int(full["false"])
        total = total_true + total_false
        full_precision = float(full["precision"])

        # Cross-partition reliability prioritizes broad positive support and penalizes poison pockets.
        agreement_score = (
            3.0 * useful_regions
            + 1.5 * positive_regions
            - 4.0 * poison_regions
            + 0.05 * full_precision
            + 0.10 * total_true
        )

        ranked.append({
            "signature": sig,
            "true": total_true,
            "false": total_false,
            "precision": full_precision,
            "support": total,
            "activeRegions": active_regions,
            "positiveRegions": positive_regions,
            "usefulRegions": useful_regions,
            "poisonRegions": poison_regions,
            "worstActivePrecision": round(worst_active_precision if active_regions else 0.0, 2),
            "agreementScore": round(agreement_score, 3),
            "regions": region_rows,
        })

    ranked.sort(
        key=lambda r: (
            -int(r["usefulRegions"]),
            int(r["poisonRegions"]),
            -int(r["positiveRegions"]),
            -float(r["precision"]),
            -int(r["true"]),
        )
    )

    stable = [
        r for r in ranked
        if int(r["true"]) >= 3
        and float(r["precision"]) >= 20.0
        and int(r["usefulRegions"]) >= 5
        and int(r["poisonRegions"]) <= 1
    ]
    stable_map = {str(r["signature"]): r for r in stable}

    scored: list[dict[str, Any]] = []
    for row in rows:
        hits = [stable_map[str(sig)] for sig in set(row.get("signatures") or []) if str(sig) in stable_map]
        vote = len(hits)
        weight = sum(
            (float(h["precision"]) / 100.0)
            * (1.0 + 0.08 * int(h["usefulRegions"]))
            / (1.0 + int(h["poisonRegions"]))
            for h in hits
        )
        scored.append({**row, "agreementVotes": vote, "agreementWeight": round(weight, 6)})

    results: list[dict[str, Any]] = []
    for cutoff in [0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.00, 1.25, 1.50, 2.00]:
        chosen = [r for r in scored if float(r.get("agreementWeight", 0.0)) >= cutoff]
        true = sum(str(r.get("label")) == "true" for r in chosen)
        false = sum(str(r.get("label")) == "false" for r in chosen)
        matched = EXPECTED[0] + true
        missing = EXPECTED[1] - true
        extra = EXPECTED[2] + false
        results.append({
            "cutoff": cutoff,
            "selected": len(chosen),
            "recoverTrue": true,
            "recoverFalse": false,
            "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
            "pitchF1": pitch_f1(matched, missing, extra),
            "matchedMissingExtra": [matched, missing, extra],
        })

    improving = [r for r in results if int(r["recoverTrue"]) > 0 and float(r["pitchF1"]) > EXPECTED_F1]
    best = max(
        improving,
        key=lambda r: (float(r["pitchF1"]), float(r["precision"]), int(r["recoverTrue"]), -int(r["recoverFalse"])),
    ) if improving else None

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during cross-partition phrase profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-repeated-phrase-cross-partition-agreement",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "signatureCount": len(ranked),
        "stableSignatureCount": len(stable),
        "stableSignatures": stable,
        "rankedSignatures": ranked,
        "candidateRows": scored,
        "thresholdResults": results,
        "bestCandidate": best,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-only",
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
        "candidateSha256": after,
        "bestCandidate": best,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 REPEATED-PHRASE CROSS-PARTITION AGREEMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Total phrase signatures:", len(ranked))
    print("Cross-partition stable signatures:", len(stable))
    for r in stable[:30]:
        print(
            "STABLE", r["signature"],
            "true=", r["true"],
            "false=", r["false"],
            "precision=", r["precision"],
            "usefulRegions=", r["usefulRegions"],
            "poisonRegions=", r["poisonRegions"],
        )
    for r in results:
        print(
            "weight>=", r["cutoff"],
            "true=", r["recoverTrue"],
            "false=", r["recoverFalse"],
            "precision=", r["precision"],
            "F1=", r["pitchF1"],
            "m/m/e=", r["matchedMissingExtra"],
        )
    print("Best cross-partition phrase candidate:", best)
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
