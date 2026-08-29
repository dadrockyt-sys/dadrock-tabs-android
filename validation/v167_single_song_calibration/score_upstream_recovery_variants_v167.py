#!/usr/bin/env python3
"""Score a fully predeclared/frozen V167 upstream-recovery variant manifest.

The manifest and every candidate SHA256 are verified before the professional
reference is opened. This script may read the frozen scorer/reference because it
only grades complete predeclared variants and selects whole deterministic rules.
It never changes a candidate or chooses an individual event.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

EXPECTED_BASELINE = {
    "combinedGuitar": {
        "f1": 0.419156774457634,
        "precision": 512 / 1050,
        "recall": 512 / 1393,
        "generated": 1050,
        "matched": 512,
        "reference": 1393,
    },
    "bass": {
        "f1": 0.7186512118018967,
        "precision": 341 / 402,
        "recall": 341 / 547,
        "generated": 402,
        "matched": 341,
        "reference": 547,
    },
}
EPS = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_frozen_frontend_scorer", path)
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


def assert_baseline(stream: str, metric: dict[str, Any]) -> None:
    expected = EXPECTED_BASELINE[stream]
    for key, metric_key in (("f1", "primaryF1"), ("precision", "primaryPrecision"), ("recall", "primaryRecall")):
        if abs(float(metric[metric_key]) - float(expected[key])) > EPS:
            raise RuntimeError(f"{stream} baseline {key} drift: {metric[metric_key]} != {expected[key]}")
    for key in ("generated", "matched", "reference"):
        if int(metric[key]) != int(expected[key]):
            raise RuntimeError(f"{stream} baseline {key} drift: {metric[key]} != {expected[key]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer-code", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"score report already exists: {args.output}")

    # Freeze boundary: verify the complete predeclared manifest and every variant
    # before importing scorer code or opening the reference payload.
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != "dadrock.tabs.v167.predeclared-upstream-recovery-variant-manifest.v1" or manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("unexpected recovery manifest boundary")
    policy = manifest.get("policy") or {}
    if policy.get("referenceRead") is not False or policy.get("scorerRead") is not False or policy.get("allVariantRulesPredeclaredBeforeScoring") is not True or policy.get("individualEventSelectionByReference") is not False:
        raise RuntimeError("recovery manifest policy boundary invalid")
    variants = list(manifest.get("variants") or [])
    if not variants:
        raise RuntimeError("recovery manifest has no variants")
    seen_ids: set[str] = set()
    for row in variants:
        variant_id = str(row["id"])
        if variant_id in seen_ids:
            raise RuntimeError(f"duplicate recovery variant id: {variant_id}")
        seen_ids.add(variant_id)
        path = args.variant_root / str(row["relativePath"])
        if not path.is_file() or sha256_file(path) != str(row["sha256"]):
            raise RuntimeError(f"frozen recovery variant hash mismatch: {variant_id}")

    manifest_sha256 = sha256_file(args.manifest)

    # Only now cross the reference-facing boundary.
    scorer = load_module(args.scorer_code)
    reference_payload = scorer.load_json(args.reference)
    reference_guitar, reference_bass, reference_counts = scorer.load_reference(reference_payload)

    results: list[dict[str, Any]] = []
    baseline_metrics: dict[str, dict[str, Any]] = {}
    for row in variants:
        path = args.variant_root / str(row["relativePath"])
        payload = scorer.load_json(path)
        generated_guitar, generated_bass = scorer.load_generated(payload)
        stream = str(row["stream"])
        if stream == "combinedGuitar":
            metric = metric_view(scorer.score_stream(generated_guitar, reference_guitar))
        elif stream == "bass":
            metric = metric_view(scorer.score_stream(generated_bass, reference_bass))
        else:
            raise RuntimeError(f"unknown recovery stream: {stream}")
        result = {
            "id": str(row["id"]),
            "stream": stream,
            "candidateSha256": str(row["sha256"]),
            "config": row["config"],
            "generationSummary": row["summary"],
            "metrics": metric,
        }
        results.append(result)
        if bool((row.get("config") or {}).get("baseline", False)):
            if stream in baseline_metrics:
                raise RuntimeError(f"duplicate baseline for {stream}")
            baseline_metrics[stream] = metric

    for stream in ("combinedGuitar", "bass"):
        if stream not in baseline_metrics:
            raise RuntimeError(f"missing baseline for {stream}")
        assert_baseline(stream, baseline_metrics[stream])

    for row in results:
        baseline = baseline_metrics[row["stream"]]
        metric = row["metrics"]
        row["deltaVsIteration002"] = {
            "f1PercentagePoints": 100.0 * (metric["primaryF1"] - baseline["primaryF1"]),
            "precisionPercentagePoints": 100.0 * (metric["primaryPrecision"] - baseline["primaryPrecision"]),
            "recallPercentagePoints": 100.0 * (metric["primaryRecall"] - baseline["primaryRecall"]),
            "matched": metric["matched"] - baseline["matched"],
            "generated": metric["generated"] - baseline["generated"],
            "falsePositive": metric["falsePositive"] - baseline["falsePositive"],
            "falseNegative": metric["falseNegative"] - baseline["falseNegative"],
        }

    winners: dict[str, Any] = {}
    for stream in ("combinedGuitar", "bass"):
        rows = [r for r in results if r["stream"] == stream]
        # Frozen tie break: max F1, then max precision, then fewer additions,
        # then lexicographically smaller predeclared rule id.
        best = min(rows, key=lambda r: (
            -float(r["metrics"]["primaryF1"]),
            -float(r["metrics"]["primaryPrecision"]),
            int((r.get("generationSummary") or {}).get("added", 0)),
            str(r["id"]),
        ))
        baseline = baseline_metrics[stream]
        winners[stream] = {
            "id": best["id"],
            "candidateSha256": best["candidateSha256"],
            "config": best["config"],
            "generationSummary": best["generationSummary"],
            "metrics": best["metrics"],
            "deltaVsIteration002": best["deltaVsIteration002"],
            "materialGainAtLeast1pp": float(best["metrics"]["primaryF1"] - baseline["primaryF1"]) >= 0.01 - EPS,
        }

    report = {
        "schema": "dadrock.tabs.v167.fixed-upstream-recovery-rule-sweep.v1",
        "version": "V167",
        "status": "REFERENCE_GRADED_COMPLETE_PREDECLARED_VARIANTS",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "manifestSha256": manifest_sha256,
        "referenceSha256": sha256_file(args.reference),
        "scorerSha256": sha256_file(args.scorer_code),
        "referenceCounts": reference_counts,
        "iteration002Baseline": baseline_metrics,
        "selectionPolicy": {
            "wholeVariantOnly": True,
            "individualEventSelectionByReference": False,
            "allVariantsFrozenBeforeReferenceRead": True,
            "tieBreak": ["max_primary_f1", "max_primary_precision", "fewer_added_events", "lexicographic_rule_id"],
            "materialGainReportingThresholdPercentagePoints": 1.0,
            "automaticIteration003Promotion": False,
        },
        "winners": winners,
        "variants": results,
        "policy": {
            "calibrationOnly": True,
            "generalizationClaim": False,
            "scoringWritesNoCandidateCorrections": True,
            "postScoreRetuningOfSameVariantSet": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifestSha256": manifest_sha256,
        "guitarWinner": winners["combinedGuitar"],
        "bassWinner": winners["bass"],
        "variantCount": len(results),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
