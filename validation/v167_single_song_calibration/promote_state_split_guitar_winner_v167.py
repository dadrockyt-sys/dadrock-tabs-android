#!/usr/bin/env python3
"""Promote the frozen V167 state-split Guitar winner to rich Iteration 005.

This transform performs zero new scoring and never opens the professional reference
or scorer. It reconstructs the already-scored `gss-active-only` winner from the
immutable Iteration 003 construction base plus the frozen reference-blind evidence
and timebase, requires exact SHA256 equality to the frozen scored candidate, then
promotes only those already-frozen Guitar additions into the rich I003 payload.
Iteration 004 remains the logical prior/current-best parent. Bass is required to be
rich-list identical across I003 and I004 and is preserved unchanged.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

import build_state_split_guitar_variants_v167 as state_builder
import build_upstream_recovery_variants_v167 as base_builder

EXPECTED = {
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i004Sha256": "728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc",
    "poolSha256": "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673",
    "manifestSha256": "113add46d50e423708972ed18eb88df48ec1d60968e75d5e251f609f84a365e4",
    "reportSha256": "f4dfd04849eab3f15290cadb2b9ff0a2903bc6174beb428b35c71aa7c7347562",
    "receiptGitBlob": "c40cd73d857c4d42d87c41c95d17d47be5f15e3c",
    "baseBuilderGitBlob": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    "stateBuilderGitBlob": "6b480d43744a5c67c02510d55162581d896afee4",
    "winnerId": "gss-active-only",
    "winnerCandidateSha256": "aa042135c542f2025522bb0d8ab9491c8457bf95025db5953b714d452afc0d5e",
    "winnerAdded": 48,
    "i003GuitarCount": 1050,
    "i004GuitarCount": 1113,
    "winnerGuitarCount": 1098,
    "bassCount": 512,
}

EXPECTED_WINNER_CONFIG = {
    "activeBranch": {
        "candidateState": "basic_pitch_active",
        "candidateToMaxActiveTemplateScoreMin": 1.0,
        "harmonicOctaveIntervalsRejected": [12, 19, 24],
        "intervalContextPolicy": "exclude_harmonic_octave",
    },
    "activitySupportMin": 0.05,
    "baseline": False,
    "existingIteration003EventsPreferred": True,
    "fundamentalPresentRequired": True,
    "id": "gss-active-only",
    "inactiveBranch": {
        "candidateState": "basic_pitch_inactive",
        "candidateToMaxActiveTemplateScoreMin": None,
        "chordIntervalsAllowed": [3, 4, 5, 7, 8, 9, 10],
        "enabled": False,
        "harmonicOctaveIntervalsRejected": [12, 19, 24],
        "intervalContextPolicy": None,
    },
    "maxAddsPerSite": 1,
    "onsetSupportMin": 0.5,
    "polyphonyCap": 6,
    "reproductionControl": False,
    "requireBasicPitchActiveContext": True,
    "stepMidiDedupe": True,
    "stream": "combinedGuitar",
    "templateRankMin": 0.975,
}

EXPECTED_WINNER_SUMMARY = {
    "activeAdded": 48,
    "activeEligible": 48,
    "added": 48,
    "eligible": 48,
    "inactiveAdded": 0,
    "inactiveEligible": 0,
    "sitesWithActiveContext": 204,
    "sitesWithAdds": 48,
    "sitesWithEligible": 48,
}

EXPECTED_WINNER_METRICS = {
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

EXPECTED_BASS_METRICS = {
    "primaryF1": 0.8045325779036827,
    "primaryPrecision": 0.83203125,
    "primaryRecall": 0.7787934186471663,
    "matched": 426,
    "generated": 512,
    "reference": 547,
    "falsePositive": 86,
    "falseNegative": 121,
}

EPS = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def normalized_stream(
    events: list[Mapping[str, Any]],
) -> list[tuple[int, float, int]]:
    return sorted(
        (int(event["measure"]), float(event["step"]), int(event["midi"]))
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    )


def canonical_dict_counter(
    events: list[Mapping[str, Any]],
) -> Counter[str]:
    return Counter(
        json.dumps(
            event,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        for event in events
    )


def exact_metrics(
    metric: Mapping[str, Any],
    expected: Mapping[str, Any],
    name: str,
) -> None:
    for key, target in expected.items():
        actual = metric.get(key)
        if isinstance(target, float):
            if abs(float(actual) - target) > EPS:
                raise RuntimeError(
                    f"{name} metric drift {key}: {actual} != {target}"
                )
        elif int(actual) != int(target):
            raise RuntimeError(
                f"{name} metric drift {key}: {actual} != {target}"
            )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-i003", type=Path, required=True)
    ap.add_argument("--parent-i004", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--base-builder", type=Path, required=True)
    ap.add_argument("--state-builder", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--proof", type=Path, required=True)
    ap.add_argument("--i003-blob", required=True)
    ap.add_argument("--i004-blob", required=True)
    ap.add_argument("--pool-blob", required=True)
    ap.add_argument("--timebase-blob", required=True)
    ap.add_argument("--manifest-blob", required=True)
    ap.add_argument("--report-blob", required=True)
    ap.add_argument("--receipt-blob", required=True)
    args = ap.parse_args()

    if args.output.exists() or args.proof.exists():
        raise RuntimeError("Iteration 005 promotion outputs must not pre-exist")

    for path, expected in (
        (args.base_i003, EXPECTED["i003Sha256"]),
        (args.parent_i004, EXPECTED["i004Sha256"]),
        (args.pool, EXPECTED["poolSha256"]),
        (args.manifest, EXPECTED["manifestSha256"]),
        (args.report, EXPECTED["reportSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(
                f"frozen promotion input SHA256 mismatch: {path}: {actual}"
            )

    if git_blob_sha(args.receipt) != EXPECTED["receiptGitBlob"]:
        raise RuntimeError("frozen state-split receipt identity mismatch")
    if git_blob_sha(args.base_builder) != EXPECTED["baseBuilderGitBlob"]:
        raise RuntimeError("frozen base builder identity mismatch")
    if git_blob_sha(args.state_builder) != EXPECTED["stateBuilderGitBlob"]:
        raise RuntimeError("frozen state-split builder identity mismatch")

    i003 = json.loads(args.base_i003.read_text(encoding="utf-8"))
    i004 = json.loads(args.parent_i004.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))
    receipt = json.loads(args.receipt.read_text(encoding="utf-8"))

    if i003.get("version") != "V167" or int(
        (i003.get("calibration") or {}).get("iteration", -1)
    ) != 3:
        raise RuntimeError("construction base must be frozen V167 Iteration 003")
    if i004.get("version") != "V167" or int(
        (i004.get("calibration") or {}).get("iteration", -1)
    ) != 4:
        raise RuntimeError("logical parent must be frozen V167 Iteration 004")
    for payload, name in ((i003, "I003"), (i004, "I004")):
        safety = payload.get("safety") or {}
        if safety.get("referenceRead") is not False:
            raise RuntimeError(f"{name} safety boundary invalid")
        if safety.get("humanCorrection") is not False:
            raise RuntimeError(f"{name} human-correction boundary invalid")

    if manifest.get("schema") != (
        "dadrock.tabs.v167.predeclared-state-split-guitar-manifest.v1"
    ):
        raise RuntimeError("unexpected frozen state-split manifest schema")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("state-split manifest is not frozen pre-score")
    mpolicy = manifest.get("policy") or {}
    for key, expected in {
        "professionalReferenceReadByGenerator": False,
        "scorerReadByGenerator": False,
        "allNewRulesPredeclaredBeforeScoring": True,
        "individualEventSelectionByReference": False,
        "iteration003Immutable": True,
        "iteration004Immutable": True,
        "bassStreamFixedExactlyToIteration004": True,
        "reproductionControlScored": False,
        "automaticIteration005Promotion": False,
    }.items():
        if mpolicy.get(key) != expected:
            raise RuntimeError(
                f"frozen state-split manifest policy mismatch: {key}"
            )

    if report.get("schema") != "dadrock.tabs.v167.state-split-guitar-sweep.v1":
        raise RuntimeError("unexpected frozen state-split report schema")
    if report.get("status") != (
        "REFERENCE_GRADED_COMPLETE_PREDECLARED_STATE_SPLIT_VARIANTS"
    ):
        raise RuntimeError("state-split report status mismatch")
    selection = report.get("selectionPolicy") or {}
    for key, expected in {
        "wholeVariantOnly": True,
        "individualEventSelectionByReference": False,
        "allNewVariantsFrozenBeforeReferenceRead": True,
        "reproductionControlScored": False,
        "bassScoreCalls": 0,
        "guitarScoreCalls": 5,
        "iteration005CreatedByThisSweep": False,
        "postScoreVariantMutation": False,
        "postScoreRetuning": False,
    }.items():
        if selection.get(key) != expected:
            raise RuntimeError(
                f"frozen state-split selection policy mismatch: {key}"
            )

    if receipt.get("status") != "STATE_SPLIT_GUITAR_SWEEP_FROZEN":
        raise RuntimeError("state-split receipt not terminal/frozen")
    rpolicy = receipt.get("policy") or {}
    for key, expected in {
        "bassScoreCalls": 0,
        "reproductionControlScoreCalls": 0,
        "iteration005Created": False,
        "postScoreCandidateMutation": False,
        "postScoreRetuning": False,
        "gpuCudaModalUsed": False,
        "mainOrProductionModified": False,
    }.items():
        if rpolicy.get(key) != expected:
            raise RuntimeError(
                f"frozen state-split receipt policy mismatch: {key}"
            )

    winner = report.get("winner") or {}
    receipt_winner = receipt.get("winner") or {}
    if winner.get("id") != EXPECTED["winnerId"]:
        raise RuntimeError("frozen state-split winner id mismatch")
    if receipt_winner.get("id") != EXPECTED["winnerId"]:
        raise RuntimeError("state-split receipt winner id mismatch")
    if winner.get("candidateSha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("frozen state-split winner candidate SHA mismatch")
    if receipt_winner.get("candidateSha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("receipt state-split winner candidate SHA mismatch")
    if winner.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError("frozen state-split winner config mismatch")
    if winner.get("generationSummary") != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError("frozen state-split winner summary mismatch")
    exact_metrics(
        winner.get("metrics") or {},
        EXPECTED_WINNER_METRICS,
        "Guitar winner",
    )
    exact_metrics(
        ((report.get("iteration004Baseline") or {}).get(
            "bassInheritedWithoutScoreCall"
        ) or {}),
        EXPECTED_BASS_METRICS,
        "inherited Bass",
    )
    if report.get("newVariantsBeatingIteration004") != 4:
        raise RuntimeError("state-split positive-rule count drift")

    manifest_winner = next(
        (
            row
            for row in manifest.get("newVariants") or []
            if row.get("id") == EXPECTED["winnerId"]
        ),
        None,
    )
    if not manifest_winner:
        raise RuntimeError("state-split winner absent from frozen manifest")
    if manifest_winner.get("sha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("manifest state-split winner SHA mismatch")
    if manifest_winner.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError("manifest state-split winner config mismatch")
    if manifest_winner.get("summary") != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError("manifest state-split winner summary mismatch")

    i003_streams = i003.get("streams") or {}
    i004_streams = i004.get("streams") or {}
    full_guitar = list(i003_streams.get("combinedGuitar") or [])
    full_bass = list(i003_streams.get("bass") or [])
    i004_guitar = list(i004_streams.get("combinedGuitar") or [])
    i004_bass = list(i004_streams.get("bass") or [])
    if len(full_guitar) != EXPECTED["i003GuitarCount"]:
        raise RuntimeError("I003 Guitar count drift")
    if len(i004_guitar) != EXPECTED["i004GuitarCount"]:
        raise RuntimeError("I004 Guitar count drift")
    if len(full_bass) != EXPECTED["bassCount"]:
        raise RuntimeError("I003 Bass count drift")
    if len(i004_bass) != EXPECTED["bassCount"]:
        raise RuntimeError("I004 Bass count drift")
    if i004_bass != full_bass:
        raise RuntimeError("I004 Bass rich list is not exactly I003 Bass")

    compact_guitar = [
        base_builder.compact_base_note(dict(row), "combinedGuitar")
        for row in full_guitar
    ]
    compact_bass = [
        base_builder.compact_base_note(dict(row), "bass")
        for row in full_bass
    ]
    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds") or []]
    if len(lattice) < 5 or any(
        b <= a for a, b in zip(lattice, lattice[1:])
    ):
        raise RuntimeError("invalid frozen subdivision lattice")
    guitar_rows = list(
        (((pool.get("upstreamPitchPools") or {}).get(
            "guitarStandaloneHarmonic"
        ) or {}).get("candidates") or [])
    )
    if len(guitar_rows) != 13328:
        raise RuntimeError("frozen Guitar upstream pool count drift")

    recovered_guitar, summary = state_builder.build_guitar(
        compact_guitar,
        guitar_rows,
        copy.deepcopy(EXPECTED_WINNER_CONFIG),
        lattice,
    )
    if summary != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError(
            f"reconstructed state-split winner summary mismatch: {summary}"
        )
    if len(recovered_guitar) != EXPECTED["winnerGuitarCount"]:
        raise RuntimeError("reconstructed winner Guitar count mismatch")

    variant = {
        **copy.deepcopy(EXPECTED_WINNER_CONFIG),
        "summary": copy.deepcopy(summary),
    }
    minimal_payload = base_builder.score_minimal_payload(
        i003,
        recovered_guitar,
        compact_bass,
        variant,
    )
    with tempfile.TemporaryDirectory(prefix="v167-i005-promotion-") as tmp:
        minimal_path = Path(tmp) / "winner.json"
        write_json(minimal_path, minimal_payload)
        reconstructed_winner_sha256 = sha256_file(minimal_path)
    if reconstructed_winner_sha256 != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError(
            "reconstructed score-minimal state-split winner does not equal "
            f"frozen scored winner: {reconstructed_winner_sha256}"
        )

    parent_coordinate_set = {
        (int(row["measure"]), float(row["step"]), int(row["midi"]))
        for row in compact_guitar
        if not bool(row.get("excludeFromScoring", False))
    }
    additions = [
        copy.deepcopy(row)
        for row in recovered_guitar
        if (
            int(row["measure"]),
            float(row["step"]),
            int(row["midi"]),
        ) not in parent_coordinate_set
    ]
    if len(additions) != EXPECTED["winnerAdded"]:
        raise RuntimeError(
            f"reconstructed state-split additions drift: {len(additions)}"
        )
    if any("v167RecoverySweepEvidence" not in row for row in additions):
        raise RuntimeError(
            "reconstructed state-split addition missing frozen recovery evidence"
        )
    addition_coordinates = [
        (int(row["measure"]), float(row["step"]), int(row["midi"]))
        for row in additions
    ]
    if len(set(addition_coordinates)) != len(addition_coordinates):
        raise RuntimeError(
            "reconstructed state-split additions contain duplicate coordinates"
        )

    output = copy.deepcopy(i003)
    output_streams = output.get("streams")
    if not isinstance(output_streams, dict):
        raise RuntimeError("I003 output missing streams")

    rich_guitar = [copy.deepcopy(row) for row in full_guitar] + additions
    rich_guitar.sort(
        key=lambda row: (
            int(row["measure"]),
            float(row["step"]),
            int(row["midi"]),
            1 if "v167RecoverySweepEvidence" in row else 0,
        )
    )
    rich_bass = copy.deepcopy(full_bass)
    output_streams["combinedGuitar"] = rich_guitar
    output_streams["bass"] = rich_bass

    original_guitar_dicts = canonical_dict_counter(full_guitar)
    promoted_guitar_dicts = canonical_dict_counter(rich_guitar)
    addition_dicts = canonical_dict_counter(additions)
    if promoted_guitar_dicts != original_guitar_dicts + addition_dicts:
        raise RuntimeError(
            "pre-existing I003 Guitar dictionaries changed during I005 promotion"
        )
    if output_streams["bass"] != full_bass:
        raise RuntimeError("I005 Bass rich list changed during Guitar promotion")

    if normalized_stream(output_streams["combinedGuitar"]) != normalized_stream(
        minimal_payload["streams"]["combinedGuitar"]
    ):
        raise RuntimeError(
            "I005 Guitar normalized stream differs from frozen scored winner"
        )
    if normalized_stream(output_streams["bass"]) != normalized_stream(
        minimal_payload["streams"]["bass"]
    ):
        raise RuntimeError("I005 Bass normalized stream differs from frozen Bass")
    if normalized_stream(output_streams["bass"]) != normalized_stream(i004_bass):
        raise RuntimeError("I005 Bass normalized stream differs from I004 Bass")

    prior_i003_calibration = copy.deepcopy(i003.get("calibration"))
    prior_i004_calibration = copy.deepcopy(i004.get("calibration"))
    output["schema"] = "dadrock.tabs.v167.single-song-calibrated-generated.v5"
    output["version"] = "V167"
    output["status"] = (
        "CALIBRATION_ITERATION_005_FROZEN_STATE_SPLIT_GUITAR_WINNER_PROMOTED"
    )
    output["calibration"] = {
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "iteration": 5,
        "parentVersion": "V167",
        "parentIteration": 4,
        "logicalParentCandidateGitBlob": args.i004_blob,
        "logicalParentCandidateSha256": sha256_file(args.parent_i004),
        "constructionBaseIteration": 3,
        "constructionBaseCandidateGitBlob": args.i003_blob,
        "constructionBaseCandidateSha256": sha256_file(args.base_i003),
        "evidencePoolGitBlob": args.pool_blob,
        "timebaseGitBlob": args.timebase_blob,
        "stateSplitSweepManifestGitBlob": args.manifest_blob,
        "stateSplitSweepReportGitBlob": args.report_blob,
        "stateSplitSweepReceiptGitBlob": args.receipt_blob,
        "selectedRuleId": EXPECTED["winnerId"],
        "selectedWholeRule": copy.deepcopy(EXPECTED_WINNER_CONFIG),
        "frozenScoredWinnerCandidateSha256": EXPECTED[
            "winnerCandidateSha256"
        ],
        "reconstructedScoredWinnerCandidateSha256": (
            reconstructed_winner_sha256
        ),
        "streamChanges": {
            "combinedGuitar": {
                "constructionBasePreExistingEventsChanged": False,
                "constructionBaseEventCount": len(full_guitar),
                "stateSplitRecoveryEventsAdded": len(additions),
                "eventCount": len(rich_guitar),
                "normalizedStreamEqualFrozenWinner": True,
                "logicalParentI004EventCount": len(i004_guitar),
                "netEventDeltaVsI004": len(rich_guitar) - len(i004_guitar),
            },
            "bass": {
                "changed": False,
                "i003EventCount": len(full_bass),
                "i004EventCount": len(i004_bass),
                "eventCount": len(rich_bass),
                "richListExactlyPreservedAcrossI003I004I005": True,
                "normalizedStreamEqualI004": True,
            },
        },
        "inheritedFrozenSweepMetrics": {
            "combinedGuitar": copy.deepcopy(winner.get("metrics")),
            "bass": copy.deepcopy(
                (report.get("iteration004Baseline") or {}).get(
                    "bassInheritedWithoutScoreCall"
                )
            ),
            "basis": (
                "exact_normalized_measure_step_midi_stream_equality_to_"
                "already_scored_frozen_state_split_winner"
            ),
            "newReferenceFacingScorePerformedByPromotion": False,
        },
        "priorIteration004Calibration": prior_i004_calibration,
        "constructionBaseIteration003Calibration": prior_i003_calibration,
        "professionalReferenceReadByTransform": False,
        "scorerReadByTransform": False,
        "directReferenceEventCopy": False,
        "individualEventSelectionByReference": False,
        "wholeRuleSelectedByFrozenReferenceGradedSweep": True,
        "postSweepRetuning": False,
        "humanCorrection": False,
        "generalizationClaim": False,
    }

    output_safety = copy.deepcopy(i003.get("safety") or {})
    output_safety.update(
        {
            "referenceRead": False,
            "scorerRead": False,
            "humanCorrection": False,
            "aggregateFrozenScoreReportRead": True,
            "selectedWholeFrozenRuleOnly": True,
            "individualEventSelectionByReference": False,
            "directReferenceEventCopy": False,
            "tuningPerformedByPromotion": False,
            "newReferenceFacingScoreCalls": 0,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        }
    )
    output["safety"] = output_safety

    write_json(args.output, output)
    proof = {
        "schema": (
            "dadrock.tabs.v167.iteration-005-state-split-guitar-promotion-proof.v1"
        ),
        "version": "V167",
        "status": "ITERATION_005_NORMALIZED_STREAM_EQUALITY_PROVEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003GitBlob": args.i003_blob,
            "iteration003Sha256": sha256_file(args.base_i003),
            "iteration004GitBlob": args.i004_blob,
            "iteration004Sha256": sha256_file(args.parent_i004),
            "evidencePoolGitBlob": args.pool_blob,
            "evidencePoolSha256": sha256_file(args.pool),
            "timebaseGitBlob": args.timebase_blob,
            "timebaseSha256": sha256_file(args.timebase),
            "stateSplitSweepManifestGitBlob": args.manifest_blob,
            "stateSplitSweepManifestSha256": sha256_file(args.manifest),
            "stateSplitSweepReportGitBlob": args.report_blob,
            "stateSplitSweepReportSha256": sha256_file(args.report),
            "stateSplitSweepReceiptGitBlob": args.receipt_blob,
            "baseBuilderGitBlob": EXPECTED["baseBuilderGitBlob"],
            "stateSplitBuilderGitBlob": EXPECTED["stateBuilderGitBlob"],
        },
        "selectedWinner": {
            "id": EXPECTED["winnerId"],
            "config": copy.deepcopy(EXPECTED_WINNER_CONFIG),
            "generationSummary": copy.deepcopy(summary),
            "frozenCandidateSha256": EXPECTED["winnerCandidateSha256"],
            "reconstructedCandidateSha256": reconstructed_winner_sha256,
            "frozenGuitarMetrics": copy.deepcopy(winner.get("metrics")),
            "inheritedBassMetrics": copy.deepcopy(
                (report.get("iteration004Baseline") or {}).get(
                    "bassInheritedWithoutScoreCall"
                )
            ),
        },
        "streamProof": {
            "combinedGuitar": {
                "constructionBaseCount": len(full_guitar),
                "stateSplitRecoveryAdditions": len(additions),
                "iteration005Count": len(output_streams["combinedGuitar"]),
                "logicalParentI004Count": len(i004_guitar),
                "netCountDeltaVsI004": len(rich_guitar) - len(i004_guitar),
                "constructionBaseRichEventDictionaryMultisetExactlyPreserved": (
                    promoted_guitar_dicts
                    == original_guitar_dicts + addition_dicts
                ),
                "newCoordinatesDisjointFromConstructionBase": all(
                    coord not in parent_coordinate_set
                    for coord in addition_coordinates
                ),
                "newCoordinatesUnique": (
                    len(set(addition_coordinates)) == len(addition_coordinates)
                ),
                "normalizedEqualFrozenScoredWinner": True,
            },
            "bass": {
                "iteration003Count": len(full_bass),
                "iteration004Count": len(i004_bass),
                "iteration005Count": len(output_streams["bass"]),
                "richListExactlyPreservedAcrossI003I004I005": (
                    output_streams["bass"] == i004_bass == full_bass
                ),
                "normalizedEqualI004": True,
            },
        },
        "policy": {
            "professionalReferenceReadByPromotion": False,
            "scorerReadByPromotion": False,
            "newReferenceFacingScoreCalls": 0,
            "individualEventSelectionByReference": False,
            "directReferenceEventCopy": False,
            "postSweepRetuning": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
        },
        "iteration005CandidateSha256": sha256_file(args.output),
    }
    write_json(args.proof, proof)

    print(
        json.dumps(
            {
                "winnerId": EXPECTED["winnerId"],
                "reconstructedWinnerSha256": reconstructed_winner_sha256,
                "stateSplitRecoveryAdditions": len(additions),
                "iteration005Counts": {
                    "combinedGuitar": len(output_streams["combinedGuitar"]),
                    "bass": len(output_streams["bass"]),
                },
                "iteration005CandidateSha256": sha256_file(args.output),
                "newReferenceFacingScoreCalls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
