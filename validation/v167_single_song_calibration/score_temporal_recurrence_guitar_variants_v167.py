#!/usr/bin/env python3
"""Score the frozen V167 same-MIDI temporal-recurrence Guitar family.

The complete manifest and every candidate hash are verified before scorer/reference
access. The exact I005 reproduction control is verified reference-blind and never
scored. Bass is verified normalized-identical to I005 and never scored. Exactly the
three preregistered new Guitar whole rules receive score calls. No candidate is
mutated or retuned after scoring and this grader never creates Iteration 006.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

EPS = 1e-12
EXPECTED = {
    "manifestSchema": "dadrock.tabs.v167.predeclared-temporal-recurrence-guitar-manifest.v1",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "referenceSha256": "b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7",
    "reproductionId": "recur-repro-i005",
    "newIds": ["recur-gap1-earliest", "recur-gap1-strongest", "recur-gap2-strongest"],
    "plannedGuitarScoreCalls": 3,
}

I005_GUITAR = {
    "primaryF1": 0.42794058610999597,
    "primaryPrecision": 0.4854280510018215,
    "primaryRecall": 0.3826274228284279,
    "matched": 533,
    "generated": 1098,
    "reference": 1393,
    "falsePositive": 565,
    "falseNegative": 860,
    "grossF1": 0.5475712565234846,
    "sameMeasurePitchContentF1": 0.5917302288237656,
}

I005_BASS = {
    "primaryF1": 0.8045325779036827,
    "primaryPrecision": 0.83203125,
    "primaryRecall": 0.7787934186471663,
    "matched": 426,
    "generated": 512,
    "reference": 547,
    "falsePositive": 86,
    "falseNegative": 121,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_frozen_frontend_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized(events: list[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        (int(row["measure"]), float(row["step"]), int(row["midi"]))
        for row in events
        if not bool(row.get("excludeFromScoring", False))
    )


def metric_view(score: Mapping[str, Any]) -> dict[str, Any]:
    primary = score["primaryTimingAwarePitch"]
    gross = score["grossTimingAwarePitch"]
    pitch = score["diagnosticPitchContentByMeasure"]
    return {
        "primaryF1": float(primary["f1"]),
        "primaryPrecision": float(primary["precision"]),
        "primaryRecall": float(primary["recall"]),
        "matched": int(primary["matched"]),
        "generated": int(primary["generated"]),
        "reference": int(primary["reference"]),
        "falsePositive": int(primary["falsePositive"]),
        "falseNegative": int(primary["falseNegative"]),
        "grossF1": float(gross["f1"]),
        "sameMeasurePitchContentF1": float(pitch["f1"]),
    }


def delta(metric: Mapping[str, Any], baseline: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "f1PercentagePoints": 100.0 * (float(metric["primaryF1"]) - float(baseline["primaryF1"])),
        "precisionPercentagePoints": 100.0 * (
            float(metric["primaryPrecision"]) - float(baseline["primaryPrecision"])
        ),
        "recallPercentagePoints": 100.0 * (
            float(metric["primaryRecall"]) - float(baseline["primaryRecall"])
        ),
        "matched": int(metric["matched"]) - int(baseline["matched"]),
        "generated": int(metric["generated"]) - int(baseline["generated"]),
        "falsePositive": int(metric["falsePositive"]) - int(baseline["falsePositive"]),
        "falseNegative": int(metric["falseNegative"]) - int(baseline["falseNegative"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--i005", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer-code", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"recurrence score report already exists: {args.output}")
    if sha256_file(args.i005) != EXPECTED["i005Sha256"]:
        raise RuntimeError("frozen I005 SHA mismatch")

    # PRE-REFERENCE FREEZE BOUNDARY.
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != EXPECTED["manifestSchema"]:
        raise RuntimeError("unexpected temporal-recurrence manifest schema")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("temporal-recurrence manifest is not frozen pre-score")
    policy = manifest.get("policy") or {}
    expected_policy = {
        "professionalReferenceReadByGenerator": False,
        "scorerReadByGenerator": False,
        "newReferenceFacingScoreCallsByGenerator": 0,
        "allVariantRulesPredeclaredBeforeScoring": True,
        "individualEventSelectionByReference": False,
        "onlyFrozenI005AdditionsFiltered": True,
        "allI003GuitarEventsAlwaysKept": True,
        "bassFixedExactlyToI005": True,
        "reproductionControlScored": False,
        "newGuitarVariantScoreCallsPlanned": 3,
        "bassScoreCallsPlanned": 0,
        "automaticIteration006Promotion": False,
        "noThresholdSweep": True,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            raise RuntimeError(f"temporal-recurrence manifest policy mismatch: {key}")
    promotion = policy.get("promotionEligibility") or {}
    if abs(float(promotion.get("minimumF1GainPercentagePointsVsI005")) - 0.10) > EPS:
        raise RuntimeError("recurrence promotion F1 threshold drift")
    if promotion.get("precisionMustBeAtLeastI005") is not True:
        raise RuntimeError("recurrence promotion precision guard drift")

    variants = list(manifest.get("variants") or [])
    if len(variants) != 4:
        raise RuntimeError(f"unexpected recurrence variant count: {len(variants)}")
    ids = [str(row["id"]) for row in variants]
    if set(ids) != {EXPECTED["reproductionId"], *EXPECTED["newIds"]}:
        raise RuntimeError(f"unexpected recurrence variant ids: {ids}")
    if len(set(ids)) != len(ids):
        raise RuntimeError("duplicate recurrence variant id")

    payloads: dict[str, dict[str, Any]] = {}
    for row in variants:
        path = args.variant_root / str(row["relativePath"])
        if not path.is_file():
            raise RuntimeError(f"missing frozen recurrence candidate: {row['id']}")
        if sha256_file(path) != str(row["sha256"]):
            raise RuntimeError(f"frozen recurrence candidate hash mismatch: {row['id']}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema") != "dadrock.tabs.v167.temporal-recurrence-score-candidate.v1":
            raise RuntimeError(f"candidate schema drift: {row['id']}")
        payloads[str(row["id"])] = payload

    i005 = json.loads(args.i005.read_text(encoding="utf-8"))
    i005_streams = i005.get("streams") or {}
    i005_guitar = list(i005_streams.get("combinedGuitar") or [])
    i005_bass = list(i005_streams.get("bass") or [])
    repro = payloads[EXPECTED["reproductionId"]]
    if normalized(repro["streams"]["combinedGuitar"]) != normalized(i005_guitar):
        raise RuntimeError("recurrence reproduction Guitar differs from I005")
    if normalized(repro["streams"]["bass"]) != normalized(i005_bass):
        raise RuntimeError("recurrence reproduction Bass differs from I005")
    for variant_id, payload in payloads.items():
        if normalized(payload["streams"]["bass"]) != normalized(i005_bass):
            raise RuntimeError(f"recurrence Bass differs from I005: {variant_id}")

    manifest_sha256 = sha256_file(args.manifest)
    if sha256_file(args.reference) != EXPECTED["referenceSha256"]:
        raise RuntimeError("frozen professional reference SHA mismatch")

    # ONLY NOW cross the reference-facing boundary.
    scorer = load_module(args.scorer_code)
    reference_payload = scorer.load_json(args.reference)
    reference_guitar, _reference_bass, reference_counts = scorer.load_reference(reference_payload)

    results: list[dict[str, Any]] = []
    guitar_score_calls = 0
    for variant_id in EXPECTED["newIds"]:
        row = next(item for item in variants if str(item["id"]) == variant_id)
        payload = payloads[variant_id]
        generated_guitar, _generated_bass = scorer.load_generated(payload)
        metric = metric_view(scorer.score_stream(generated_guitar, reference_guitar))
        guitar_score_calls += 1
        results.append({
            "id": variant_id,
            "candidateSha256": str(row["sha256"]),
            "config": row["config"],
            "generationSummary": row["summary"],
            "metrics": metric,
            "deltaVsI005": delta(metric, I005_GUITAR),
        })

    if guitar_score_calls != EXPECTED["plannedGuitarScoreCalls"]:
        raise RuntimeError("unexpected Guitar score-call count")

    baseline_row = {
        "id": "i005-baseline",
        "candidateSha256": EXPECTED["i005Sha256"],
        "config": {"baseline": True, "source": "frozen_iteration_005_inherited_without_score_call"},
        "generationSummary": {
            "keptI005Additions": 48,
            "guitarEventCount": 1098,
            "bassEventCount": 512,
        },
        "metrics": I005_GUITAR,
        "deltaVsI005": delta(I005_GUITAR, I005_GUITAR),
    }
    ranked = [baseline_row, *results]
    best = min(
        ranked,
        key=lambda row: (
            -float(row["metrics"]["primaryF1"]),
            -float(row["metrics"]["primaryPrecision"]),
            int((row.get("generationSummary") or {}).get("keptI005Additions", 48)),
            str(row["id"]),
        ),
    )
    best_delta = delta(best["metrics"], I005_GUITAR)
    promotion_eligible = (
        best["id"] != "i005-baseline"
        and float(best_delta["f1PercentagePoints"]) + EPS >= 0.10
        and float(best["metrics"]["primaryPrecision"]) + EPS >= float(I005_GUITAR["primaryPrecision"])
    )

    report = {
        "schema": "dadrock.tabs.v167.temporal-recurrence-guitar-sweep.v1",
        "version": "V167",
        "status": "REFERENCE_GRADED_COMPLETE_PREDECLARED_TEMPORAL_RECURRENCE_VARIANTS",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "manifestSha256": manifest_sha256,
        "referenceSha256": sha256_file(args.reference),
        "scorerSha256": sha256_file(args.scorer_code),
        "referenceCounts": reference_counts,
        "iteration005BaselineInheritedWithoutScoreCall": {
            "combinedGuitar": I005_GUITAR,
            "bass": I005_BASS,
        },
        "reproductionControl": {
            "id": EXPECTED["reproductionId"],
            "candidateSha256": next(
                str(row["sha256"])
                for row in variants
                if str(row["id"]) == EXPECTED["reproductionId"]
            ),
            "normalizedGuitarExactlyI005": True,
            "normalizedBassExactlyI005": True,
            "scoreCalls": 0,
        },
        "selectionPolicy": {
            "wholeVariantOnly": True,
            "individualEventSelectionByReference": False,
            "allVariantsFrozenBeforeReferenceRead": True,
            "reproductionControlScoreCalls": 0,
            "guitarScoreCalls": guitar_score_calls,
            "bassScoreCalls": 0,
            "tieBreak": [
                "max_primary_f1",
                "max_primary_precision",
                "fewer_kept_i005_additions",
                "lexicographic_rule_id",
            ],
            "promotionMinimumF1GainPercentagePointsVsI005": 0.10,
            "promotionRequiresPrecisionAtLeastI005": True,
            "automaticIteration006Promotion": False,
            "postScoreCandidateMutation": False,
            "postScoreRetuning": False,
        },
        "winnerIncludingI005Baseline": {
            **best,
            "deltaVsI005": best_delta,
            "eligibleForSeparateNoRescoreIteration006Promotion": promotion_eligible,
        },
        "newVariantsBeatingI005": sum(
            float(row["metrics"]["primaryF1"]) > float(I005_GUITAR["primaryF1"]) + EPS
            for row in results
        ),
        "newVariantsMeetingPromotionEligibility": sum(
            float(row["deltaVsI005"]["f1PercentagePoints"]) + EPS >= 0.10
            and float(row["metrics"]["primaryPrecision"]) + EPS >= float(I005_GUITAR["primaryPrecision"])
            for row in results
        ),
        "variants": results,
        "policy": {
            "calibrationOnly": True,
            "generalizationClaim": False,
            "scoringWritesNoCandidateCorrections": True,
            "postScoreRetuning": False,
            "iteration006CreatedByThisSweep": False,
            "bassStreamScored": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "manifestSha256": manifest_sha256,
        "guitarScoreCalls": guitar_score_calls,
        "bassScoreCalls": 0,
        "winner": report["winnerIncludingI005Baseline"],
        "newVariantsBeatingI005": report["newVariantsBeatingI005"],
        "newVariantsMeetingPromotionEligibility": report["newVariantsMeetingPromotionEligibility"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
