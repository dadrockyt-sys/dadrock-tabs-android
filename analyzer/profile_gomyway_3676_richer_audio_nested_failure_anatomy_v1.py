from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_onset_slot_richer_audio_stability_v1 as richer

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-richer-audio-nested-failure-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-richer-audio-nested-failure-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fold_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key in ("normalCv", "sectionCv", "shiftedWindowCv"):
        for row in payload.get(key) or []:
            rows.append(dict(row))
    return rows


def main() -> None:
    before = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if not SOURCE_PATH.exists():
        raise RuntimeError(
            "Richer-audio nested CV output is missing; run "
            "benchmark_gomyway_3676_onset_slot_richer_audio_nested_cv_v1.py first"
        )

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Richer-audio nested CV is not anchored to frozen 36.76 champion")

    rows = fold_rows(payload)
    if len(rows) != 15:
        raise RuntimeError(f"Expected 15 outer-fold rows, found {len(rows)}")

    passed = [r for r in rows if bool(r.get("passed"))]
    failed = [r for r in rows if not bool(r.get("passed"))]
    overall_fail_rate = len(failed) / len(rows)

    stats: dict[str, dict[str, Any]] = {}
    for feature in richer.FEATURE_NAMES:
        selected_pass = selected_fail = 0
        pos_pass = neg_pass = pos_fail = neg_fail = 0
        pass_weights: list[float] = []
        fail_weights: list[float] = []
        schemes_pass: Counter[str] = Counter()
        schemes_fail: Counter[str] = Counter()

        for row in rows:
            model = row.get("model") or {}
            features = [str(x) for x in (model.get("features") or [])]
            if feature not in features:
                continue
            weight = float((model.get("weights") or {}).get(feature, 0.0))
            is_pass = bool(row.get("passed"))
            scheme = str(row.get("scheme"))
            if is_pass:
                selected_pass += 1
                pass_weights.append(weight)
                schemes_pass[scheme] += 1
                pos_pass += int(weight > 0)
                neg_pass += int(weight < 0)
            else:
                selected_fail += 1
                fail_weights.append(weight)
                schemes_fail[scheme] += 1
                pos_fail += int(weight > 0)
                neg_fail += int(weight < 0)

        selected_total = selected_pass + selected_fail
        fail_rate_when_selected = selected_fail / selected_total if selected_total else 0.0
        enrichment = fail_rate_when_selected - overall_fail_rate if selected_total else 0.0
        stats[feature] = {
            "feature": feature,
            "selectedTotal": selected_total,
            "selectedPass": selected_pass,
            "selectedFail": selected_fail,
            "failRateWhenSelectedPct": round(100.0 * fail_rate_when_selected, 2),
            "failureEnrichmentPctPoints": round(100.0 * enrichment, 2),
            "passPositiveWeights": pos_pass,
            "passNegativeWeights": neg_pass,
            "failPositiveWeights": pos_fail,
            "failNegativeWeights": neg_fail,
            "meanAbsWeightPass": round(sum(abs(x) for x in pass_weights) / len(pass_weights), 6) if pass_weights else 0.0,
            "meanAbsWeightFail": round(sum(abs(x) for x in fail_weights) / len(fail_weights), 6) if fail_weights else 0.0,
            "passSchemes": dict(schemes_pass),
            "failSchemes": dict(schemes_fail),
        }

    ranked_failure = sorted(
        stats.values(),
        key=lambda r: (
            -int(r["selectedFail"]),
            -float(r["failureEnrichmentPctPoints"]),
            -int(r["selectedTotal"]),
            str(r["feature"]),
        ),
    )
    ranked_success = sorted(
        stats.values(),
        key=lambda r: (
            -int(r["selectedPass"]),
            float(r["failureEnrichmentPctPoints"]),
            -int(r["selectedTotal"]),
            str(r["feature"]),
        ),
    )

    hyper_pass: Counter[str] = Counter()
    hyper_fail: Counter[str] = Counter()
    for row in rows:
        key = (
            f"k{row.get('chosenTopK')}|"
            f"c{row.get('chosenMinConsistency')}|"
            f"q{row.get('chosenQuantile')}"
        )
        (hyper_pass if bool(row.get("passed")) else hyper_fail)[key] += 1

    failed_rows = [
        {
            "scheme": r.get("scheme"),
            "fold": r.get("fold"),
            "features": (r.get("model") or {}).get("features") or [],
            "weights": (r.get("model") or {}).get("weights") or {},
            "chosenTopK": r.get("chosenTopK"),
            "chosenMinConsistency": r.get("chosenMinConsistency"),
            "chosenQuantile": r.get("chosenQuantile"),
            "heldoutBase": r.get("heldoutBase"),
            "heldoutCandidate": r.get("heldoutCandidate"),
            "heldoutPrecisionLift": r.get("heldoutPrecisionLift"),
        }
        for r in failed
    ]

    after = sha256(richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during richer-audio failure anatomy")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-richer-audio-nested-failure-anatomy-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "outerFoldCount": len(rows),
        "passedFoldCount": len(passed),
        "failedFoldCount": len(failed),
        "overallFailureRatePct": round(100.0 * overall_fail_rate, 2),
        "rankedFailureAssociatedFeatures": ranked_failure,
        "rankedSuccessAssociatedFeatures": ranked_success,
        "hyperparametersPassed": dict(hyper_pass),
        "hyperparametersFailed": dict(hyper_fail),
        "failedFolds": failed_rows,
        "note": (
            "Diagnostic only. This profiles already-completed outer-fold results to identify recurring "
            "feature-selection/sign/hyperparameter patterns in passing versus failing held-out folds. "
            "It must not be used as a global blacklist or promotion rule. Any follow-up rule must be "
            "relearned inside training folds only."
        ),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "validatedNewChampion": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RICHER AUDIO NESTED FAILURE ANATOMY V1 COMPLETE")
    print("Passed / failed outer folds:", len(passed), "/", len(failed))
    print("Top failure-associated features:")
    for item in ranked_failure[:10]:
        print("FAILASSOC", {
            "feature": item["feature"],
            "selectedPass": item["selectedPass"],
            "selectedFail": item["selectedFail"],
            "failRateWhenSelectedPct": item["failRateWhenSelectedPct"],
            "failureEnrichmentPctPoints": item["failureEnrichmentPctPoints"],
        })
    print("Top success-associated features:")
    for item in ranked_success[:10]:
        print("SUCCESSASSOC", {
            "feature": item["feature"],
            "selectedPass": item["selectedPass"],
            "selectedFail": item["selectedFail"],
            "failureEnrichmentPctPoints": item["failureEnrichmentPctPoints"],
        })
    print("Validated new champion: False")
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
