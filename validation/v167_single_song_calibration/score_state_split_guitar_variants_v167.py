#!/usr/bin/env python3
"""Grade the frozen V167 state-split Guitar family.

All generated candidates and the no-score I004 reproduction control are verified
before scorer code is imported or the professional reference is opened. Only
frozen I004 plus four genuinely new complete Guitar variants are scored. Bass is
never scored in this sweep because it is byte-for-stream fixed to frozen I004.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

EXPECTED_I004_SHA256 = "728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc"
EXPECTED_MANIFEST_SCHEMA = "dadrock.tabs.v167.predeclared-state-split-guitar-manifest.v1"
EXPECTED_REPRODUCTION_ID = "gss-repro-q100-noharm"
EXPECTED_NEW_IDS = (
    "gss-active-only",
    "gss-inactive-q125-noharm",
    "gss-inactive-q100-chord",
    "gss-inactive-q125-chord",
)
EXPECTED_BASELINE = {
    "primaryF1": 0.42617717478052675,
    "primaryPrecision": 0.4797843665768194,
    "primaryRecall": 0.38334529791816224,
    "matched": 534,
    "generated": 1113,
    "reference": 1393,
    "falsePositive": 579,
    "falseNegative": 859,
}
INHERITED_BASS = {
    "primaryF1": 0.8045325779036827,
    "primaryPrecision": 0.83203125,
    "primaryRecall": 0.7787934186471663,
    "matched": 426,
    "generated": 512,
    "reference": 547,
    "falsePositive": 86,
    "falseNegative": 121,
}
BASELINE_TOTAL_ADDITIONS_VS_I003 = 63
EPS = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        "v167_frozen_frontend_scorer_state_split", path
    )
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
        (
            int(event["measure"]),
            float(event["step"]),
            int(event["midi"]),
        )
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    )


def assert_expected(
    name: str,
    metric: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    for key in ("primaryF1", "primaryPrecision", "primaryRecall"):
        if abs(float(metric[key]) - float(expected[key])) > EPS:
            raise RuntimeError(
                f"{name} {key} drift: {metric[key]} != {expected[key]}"
            )
    for key in (
        "matched",
        "generated",
        "reference",
        "falsePositive",
        "falseNegative",
    ):
        if int(metric[key]) != int(expected[key]):
            raise RuntimeError(
                f"{name} {key} drift: {metric[key]} != {expected[key]}"
            )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant-root", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--baseline-i004", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer-code", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"state-split score report already exists: {args.output}")
    if sha256_file(args.baseline_i004) != EXPECTED_I004_SHA256:
        raise RuntimeError("frozen I004 SHA256 mismatch")

    # Pre-reference boundary begins here. The manifest and every generated file,
    # including the intentionally unscored reproduction control, are verified
    # before the scorer module or professional reference is opened.
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("schema") != EXPECTED_MANIFEST_SCHEMA:
        raise RuntimeError("unexpected state-split manifest schema")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("state-split manifest is not frozen before scoring")

    policy = manifest.get("policy") or {}
    expected_policy = {
        "professionalReferenceReadByGenerator": False,
        "scorerReadByGenerator": False,
        "allNewRulesPredeclaredBeforeScoring": True,
        "individualEventSelectionByReference": False,
        "iteration003Immutable": True,
        "iteration004Immutable": True,
        "baselineIsFrozenIteration004": True,
        "bassStreamFixedExactlyToIteration004": True,
        "reproductionControlScored": False,
        "reproductionMustEqualIteration004BeforeScoring": True,
        "newRuleCount": 4,
        "postScoreRetuning": False,
        "automaticIteration005Promotion": False,
    }
    for key, expected in expected_policy.items():
        if policy.get(key) != expected:
            raise RuntimeError(
                f"state-split manifest policy boundary invalid: {key}"
            )

    baseline_row = manifest.get("baseline") or {}
    if str(baseline_row.get("id")) != "i004-baseline":
        raise RuntimeError("state-split baseline identity drift")
    if str(baseline_row.get("candidateSha256")) != EXPECTED_I004_SHA256:
        raise RuntimeError("state-split manifest I004 SHA drift")
    if int(baseline_row.get("totalAdditionsVsI003", -1)) != BASELINE_TOTAL_ADDITIONS_VS_I003:
        raise RuntimeError("state-split baseline addition count drift")
    if baseline_row.get("scored") is not True:
        raise RuntimeError("state-split I004 baseline must be scored")

    i004_payload = json.loads(args.baseline_i004.read_text(encoding="utf-8"))
    i004_streams = i004_payload.get("streams") or {}
    i004_guitar_coordinates = scoring_coordinates(
        list(i004_streams.get("combinedGuitar") or [])
    )
    i004_bass_coordinates = scoring_coordinates(
        list(i004_streams.get("bass") or [])
    )
    if len(i004_guitar_coordinates) != 1113:
        raise RuntimeError("I004 Guitar coordinate count drift")
    if len(i004_bass_coordinates) != 512:
        raise RuntimeError("I004 Bass coordinate count drift")

    reproduction = manifest.get("reproductionControl") or {}
    if str(reproduction.get("id")) != EXPECTED_REPRODUCTION_ID:
        raise RuntimeError("state-split reproduction-control identity drift")
    if reproduction.get("scored") is not False:
        raise RuntimeError("state-split reproduction control must not be scored")
    if reproduction.get("normalizedGuitarExactlyIteration004") is not True:
        raise RuntimeError("reproduction manifest lacks I004 Guitar equality proof")
    if reproduction.get("normalizedBassExactlyIteration004") is not True:
        raise RuntimeError("reproduction manifest lacks I004 Bass equality proof")
    reproduction_path = args.variant_root / str(reproduction["relativePath"])
    if (
        not reproduction_path.is_file()
        or sha256_file(reproduction_path) != str(reproduction["sha256"])
    ):
        raise RuntimeError("state-split reproduction-control hash mismatch")
    reproduction_payload = json.loads(
        reproduction_path.read_text(encoding="utf-8")
    )
    reproduction_streams = reproduction_payload.get("streams") or {}
    if scoring_coordinates(
        list(reproduction_streams.get("combinedGuitar") or [])
    ) != i004_guitar_coordinates:
        raise RuntimeError(
            "state-split reproduction control no longer equals I004 Guitar"
        )
    if scoring_coordinates(
        list(reproduction_streams.get("bass") or [])
    ) != i004_bass_coordinates:
        raise RuntimeError(
            "state-split reproduction control no longer equals I004 Bass"
        )

    new_variants = list(manifest.get("newVariants") or [])
    if len(new_variants) != 4:
        raise RuntimeError(f"state-split new variant count drift: {len(new_variants)}")
    if [str(row.get("id")) for row in new_variants] != list(EXPECTED_NEW_IDS):
        raise RuntimeError("state-split new variant identity/order drift")

    seen_ids: set[str] = set()
    frozen_candidates: list[tuple[dict[str, Any], Path]] = []
    for row in new_variants:
        variant_id = str(row["id"])
        if variant_id in seen_ids:
            raise RuntimeError(f"duplicate state-split variant id: {variant_id}")
        seen_ids.add(variant_id)
        if row.get("scored") is not True:
            raise RuntimeError(f"new state-split rule not marked scored: {variant_id}")
        path = args.variant_root / str(row["relativePath"])
        if not path.is_file() or sha256_file(path) != str(row["sha256"]):
            raise RuntimeError(f"frozen state-split candidate hash mismatch: {variant_id}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        streams = payload.get("streams") or {}
        candidate_bass = scoring_coordinates(list(streams.get("bass") or []))
        if candidate_bass != i004_bass_coordinates:
            raise RuntimeError(f"Bass stream changed in state-split variant: {variant_id}")
        if int((row.get("counts") or {}).get("bass", -1)) != 512:
            raise RuntimeError(f"Bass count changed in state-split manifest: {variant_id}")
        total_additions = int(row.get("totalAdditionsVsI003", -1))
        if total_additions != int((row.get("summary") or {}).get("added", -2)):
            raise RuntimeError(f"state-split addition count drift: {variant_id}")
        frozen_candidates.append((row, path))

    manifest_sha256 = sha256_file(args.manifest)

    # Only now cross the reference-facing boundary.
    scorer = load_module(args.scorer_code)
    reference_payload = scorer.load_json(args.reference)
    reference_guitar, _reference_bass, reference_counts = scorer.load_reference(
        reference_payload
    )

    # Exactly one baseline Guitar call + four new Guitar calls.
    baseline_generated_guitar, _baseline_generated_bass = scorer.load_generated(
        scorer.load_json(args.baseline_i004)
    )
    baseline_metric = metric_view(
        scorer.score_stream(baseline_generated_guitar, reference_guitar)
    )
    assert_expected("I004 Guitar baseline", baseline_metric, EXPECTED_BASELINE)

    results: list[dict[str, Any]] = [
        {
            "id": "i004-baseline",
            "kind": "baseline",
            "candidateSha256": EXPECTED_I004_SHA256,
            "config": {
                "baseline": True,
                "source": "frozen_iteration_004",
            },
            "generationSummary": {
                "added": BASELINE_TOTAL_ADDITIONS_VS_I003,
                "activeAdded": 46,
                "inactiveAdded": 17,
            },
            "totalAdditionsVsI003": BASELINE_TOTAL_ADDITIONS_VS_I003,
            "metrics": baseline_metric,
            "deltaVsIteration004": {
                "f1PercentagePoints": 0.0,
                "precisionPercentagePoints": 0.0,
                "recallPercentagePoints": 0.0,
                "matched": 0,
                "generated": 0,
                "falsePositive": 0,
                "falseNegative": 0,
            },
        }
    ]

    for row, path in frozen_candidates:
        payload = scorer.load_json(path)
        generated_guitar, _generated_bass = scorer.load_generated(payload)
        metric = metric_view(
            scorer.score_stream(generated_guitar, reference_guitar)
        )
        results.append(
            {
                "id": str(row["id"]),
                "kind": "new_state_split_rule",
                "candidateSha256": str(row["sha256"]),
                "config": row["config"],
                "generationSummary": row["summary"],
                "totalAdditionsVsI003": int(row["totalAdditionsVsI003"]),
                "metrics": metric,
                "deltaVsIteration004": {
                    "f1PercentagePoints": 100.0
                    * (metric["primaryF1"] - baseline_metric["primaryF1"]),
                    "precisionPercentagePoints": 100.0
                    * (
                        metric["primaryPrecision"]
                        - baseline_metric["primaryPrecision"]
                    ),
                    "recallPercentagePoints": 100.0
                    * (
                        metric["primaryRecall"]
                        - baseline_metric["primaryRecall"]
                    ),
                    "matched": metric["matched"] - baseline_metric["matched"],
                    "generated": metric["generated"] - baseline_metric["generated"],
                    "falsePositive": metric["falsePositive"]
                    - baseline_metric["falsePositive"],
                    "falseNegative": metric["falseNegative"]
                    - baseline_metric["falseNegative"],
                },
            }
        )

    if len(results) != 5:
        raise AssertionError("state-split scorer call/result count drift")

    winner = min(
        results,
        key=lambda row: (
            -float(row["metrics"]["primaryF1"]),
            -float(row["metrics"]["primaryPrecision"]),
            int(row["totalAdditionsVsI003"]),
            str(row["id"]),
        ),
    )
    new_beating = [
        row
        for row in results
        if row["kind"] == "new_state_split_rule"
        and float(row["metrics"]["primaryF1"])
        > float(baseline_metric["primaryF1"]) + EPS
    ]

    report = {
        "schema": "dadrock.tabs.v167.state-split-guitar-sweep.v1",
        "version": "V167",
        "status": "REFERENCE_GRADED_COMPLETE_PREDECLARED_STATE_SPLIT_VARIANTS",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "manifestSha256": manifest_sha256,
        "iteration004Sha256": sha256_file(args.baseline_i004),
        "referenceSha256": sha256_file(args.reference),
        "scorerSha256": sha256_file(args.scorer_code),
        "referenceCounts": reference_counts,
        "iteration004Baseline": {
            "combinedGuitar": baseline_metric,
            "bassInheritedWithoutScoreCall": INHERITED_BASS,
        },
        "reproductionControl": {
            "id": str(reproduction["id"]),
            "candidateSha256": str(reproduction["sha256"]),
            "normalizedGuitarExactlyIteration004": True,
            "normalizedBassExactlyIteration004": True,
            "scoreCalls": 0,
        },
        "selectionPolicy": {
            "wholeVariantOnly": True,
            "individualEventSelectionByReference": False,
            "allNewVariantsFrozenBeforeReferenceRead": True,
            "reproductionControlScored": False,
            "bassScoreCalls": 0,
            "guitarScoreCalls": 5,
            "tieBreak": [
                "max_primary_f1",
                "max_primary_precision",
                "fewer_total_additions_vs_i003",
                "lexicographic_rule_id",
            ],
            "iteration005CreatedByThisSweep": False,
            "postScoreVariantMutation": False,
            "postScoreRetuning": False,
        },
        "winner": {
            "id": winner["id"],
            "candidateSha256": winner["candidateSha256"],
            "config": winner["config"],
            "generationSummary": winner["generationSummary"],
            "totalAdditionsVsI003": winner["totalAdditionsVsI003"],
            "metrics": winner["metrics"],
            "deltaVsIteration004": winner["deltaVsIteration004"],
            "beatsIteration004GuitarF1": (
                float(winner["metrics"]["primaryF1"])
                > float(baseline_metric["primaryF1"]) + EPS
            ),
        },
        "newVariantsBeatingIteration004": len(new_beating),
        "newVariantIdsBeatingIteration004": [
            row["id"]
            for row in sorted(
                new_beating,
                key=lambda row: (
                    -float(row["metrics"]["primaryF1"]),
                    -float(row["metrics"]["primaryPrecision"]),
                    int(row["totalAdditionsVsI003"]),
                    str(row["id"]),
                ),
            )
        ],
        "variants": results,
        "policy": {
            "calibrationOnly": True,
            "generalizationClaim": False,
            "scoringWritesNoCandidateCorrections": True,
            "postScoreRetuningOfSameVariantSet": False,
            "bassCoordinateIdentityVerifiedBeforeReferenceRead": True,
            "bassScoreCalls": 0,
            "reproductionControlScoreCalls": 0,
            "guitarScoreCalls": 5,
            "automaticIteration005Promotion": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "manifestSha256": manifest_sha256,
                "guitarScoreCalls": 5,
                "bassScoreCalls": 0,
                "reproductionControlScoreCalls": 0,
                "newVariantsBeatingIteration004": len(new_beating),
                "winner": report["winner"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
