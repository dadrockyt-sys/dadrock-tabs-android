#!/usr/bin/env python3
"""Grade the frozen preregistered contextual V167 Guitar recovery family.

The manifest, every candidate hash, and Bass coordinate identity are verified
before scorer code is imported or the professional reference is opened. Scoring
selects only a complete whole-rule variant; it never changes or selects an
individual event.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

EXPECTED_BASE_SHA256 = "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c575bf709673"
EXPECTED_VARIANTS = 37
EPS = 1e-12
EXPECTED_GUITAR_BASELINE = {
    "primaryF1": 0.419156774457634,
    "primaryPrecision": 512 / 1050,
    "primaryRecall": 512 / 1393,
    "matched": 512,
    "generated": 1050,
    "reference": 1393,
}
EXPECTED_BASS_BASELINE = {
    "primaryF1": 0.8045325779036827,
    "primaryPrecision": 0.83203125,
    "primaryRecall": 0.7787934186471663,
    "matched": 426,
    "generated": 512,
    "reference": 547,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_frozen_frontend_scorer_contextual", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metric_view(score: dict[str, Any]) -> dict[str, Any]:
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


def scoring_coordinates(events: list[dict[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        (int(event["measure"]), float(event["step"]), int(event["midi"]))
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    )


def assert_expected(name: str, metric: dict[str, Any], expected: dict[str, Any]) -> None:
    for key in ("primaryF1", "primaryPrecision", "primaryRecall"):
        if abs(float(metric[key]) - float(expected[key])) > EPS:
            raise RuntimeError(f"{name} {key} drift: {metric[key]} != {expected[key]}")
    for key in ("matched", "generated", "reference"):
        if int(metric[key]) != int(expected[key]):
            raise RuntimeError(f"{name} {key} drift: {metric[key]} != {expected[key]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer-code", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"score report already exists: {args.output}")
    if sha256_file(args.base) != EXPECTED_BASE_SHA256:
        raise RuntimeError("frozen Iteration 003 SHA256 mismatch")

    # Pre-reference freeze boundary.
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "dadrock.tabs.v167.predeclared-contextual-guitar-recovery-manifest.v1":
        raise RuntimeError("unexpected contextual manifest schema")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("contextual manifest is not frozen before scoring")
    policy = manifest.get("policy") or {}
    required_policy = {
        "referenceRead": False,
        "scorerRead": False,
        "allVariantRulesPredeclaredBeforeScoring": True,
        "individualEventSelectionByReference": False,
        "iteration003Immutable": True,
        "bassNormalizedStreamFixedToIteration003": True,
    }
    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            raise RuntimeError(f"contextual manifest policy boundary invalid: {key}")

    variants = list(manifest.get("variants") or [])
    if len(variants) != EXPECTED_VARIANTS:
        raise RuntimeError(f"contextual variant count drift: {len(variants)}")
    baseline_rows = [row for row in variants if bool((row.get("config") or {}).get("baseline", False))]
    if len(baseline_rows) != 1 or str(baseline_rows[0].get("id")) != "gctx-baseline":
        raise RuntimeError("contextual baseline identity drift")

    base_payload = json.loads(args.base.read_text(encoding="utf-8"))
    base_bass = scoring_coordinates(list((base_payload.get("streams") or {}).get("bass") or []))
    if len(base_bass) != 512:
        raise RuntimeError("Iteration 003 Bass coordinate count drift")

    seen_ids: set[str] = set()
    for row in variants:
        variant_id = str(row["id"])
        if variant_id in seen_ids:
            raise RuntimeError(f"duplicate contextual variant id: {variant_id}")
        seen_ids.add(variant_id)
        path = args.variant_root / str(row["relativePath"])
        if not path.is_file() or sha256_file(path) != str(row["sha256"]):
            raise RuntimeError(f"frozen contextual variant hash mismatch: {variant_id}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        candidate_bass = scoring_coordinates(list((payload.get("streams") or {}).get("bass") or []))
        if candidate_bass != base_bass:
            raise RuntimeError(f"Bass stream changed in contextual variant: {variant_id}")
        if int((row.get("counts") or {}).get("bass", -1)) != 512:
            raise RuntimeError(f"Bass count changed in contextual manifest row: {variant_id}")

    manifest_sha256 = sha256_file(args.manifest)

    # Only after every complete candidate and Bass identity is sealed do we read
    # scorer/reference material.
    scorer = load_module(args.scorer_code)
    reference_payload = scorer.load_json(args.reference)
    reference_guitar, reference_bass, reference_counts = scorer.load_reference(reference_payload)

    results: list[dict[str, Any]] = []
    baseline_metric: dict[str, Any] | None = None
    baseline_bass_metric: dict[str, Any] | None = None

    for row in variants:
        path = args.variant_root / str(row["relativePath"])
        payload = scorer.load_json(path)
        generated_guitar, generated_bass = scorer.load_generated(payload)
        guitar_metric = metric_view(scorer.score_stream(generated_guitar, reference_guitar))
        if bool((row.get("config") or {}).get("baseline", False)):
            baseline_metric = guitar_metric
            baseline_bass_metric = metric_view(scorer.score_stream(generated_bass, reference_bass))
        results.append({
            "id": str(row["id"]),
            "stream": "combinedGuitar",
            "candidateSha256": str(row["sha256"]),
            "config": row["config"],
            "generationSummary": row["summary"],
            "metrics": guitar_metric,
        })

    if baseline_metric is None or baseline_bass_metric is None:
        raise RuntimeError("contextual baseline was not scored")
    assert_expected("Guitar baseline", baseline_metric, EXPECTED_GUITAR_BASELINE)
    assert_expected("Bass baseline", baseline_bass_metric, EXPECTED_BASS_BASELINE)

    for row in results:
        metric = row["metrics"]
        row["deltaVsIteration003"] = {
            "f1PercentagePoints": 100.0 * (metric["primaryF1"] - baseline_metric["primaryF1"]),
            "precisionPercentagePoints": 100.0 * (metric["primaryPrecision"] - baseline_metric["primaryPrecision"]),
            "recallPercentagePoints": 100.0 * (metric["primaryRecall"] - baseline_metric["primaryRecall"]),
            "matched": metric["matched"] - baseline_metric["matched"],
            "generated": metric["generated"] - baseline_metric["generated"],
            "falsePositive": metric["falsePositive"] - baseline_metric["falsePositive"],
            "falseNegative": metric["falseNegative"] - baseline_metric["falseNegative"],
        }

    winner = min(results, key=lambda row: (
        -float(row["metrics"]["primaryF1"]),
        -float(row["metrics"]["primaryPrecision"]),
        int((row.get("generationSummary") or {}).get("added", 0)),
        str(row["id"]),
    ))
    nonbaseline_beating = [
        row for row in results
        if not bool((row.get("config") or {}).get("baseline", False))
        and float(row["metrics"]["primaryF1"]) > float(baseline_metric["primaryF1"]) + EPS
    ]

    report = {
        "schema": "dadrock.tabs.v167.contextual-guitar-recovery-sweep.v1",
        "version": "V167",
        "status": "REFERENCE_GRADED_COMPLETE_PREDECLARED_CONTEXTUAL_VARIANTS",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "manifestSha256": manifest_sha256,
        "iteration003Sha256": sha256_file(args.base),
        "referenceSha256": sha256_file(args.reference),
        "scorerSha256": sha256_file(args.scorer_code),
        "referenceCounts": reference_counts,
        "iteration003Baseline": {
            "combinedGuitar": baseline_metric,
            "bass": baseline_bass_metric,
        },
        "selectionPolicy": {
            "wholeVariantOnly": True,
            "individualEventSelectionByReference": False,
            "allVariantsFrozenBeforeReferenceRead": True,
            "tieBreak": ["max_primary_f1", "max_primary_precision", "fewer_added_events", "lexicographic_rule_id"],
            "iteration004CreatedByThisSweep": False,
            "postScoreVariantMutation": False,
        },
        "winner": {
            "id": winner["id"],
            "candidateSha256": winner["candidateSha256"],
            "config": winner["config"],
            "generationSummary": winner["generationSummary"],
            "metrics": winner["metrics"],
            "deltaVsIteration003": winner["deltaVsIteration003"],
            "beatsIteration003GuitarF1": float(winner["metrics"]["primaryF1"]) > float(baseline_metric["primaryF1"]) + EPS,
        },
        "nonBaselineVariantsBeatingIteration003": len(nonbaseline_beating),
        "variants": results,
        "policy": {
            "calibrationOnly": True,
            "generalizationClaim": False,
            "bassCoordinateIdentityVerifiedBeforeReferenceRead": True,
            "scoringWritesNoCandidateCorrections": True,
            "postScoreRetuningOfSameVariantSet": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifestSha256": manifest_sha256,
        "variantCount": len(results),
        "nonBaselineVariantsBeatingIteration003": len(nonbaseline_beating),
        "winner": report["winner"],
        "bassBaseline": baseline_bass_metric,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
