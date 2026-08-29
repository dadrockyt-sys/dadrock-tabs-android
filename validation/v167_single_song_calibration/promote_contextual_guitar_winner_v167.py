#!/usr/bin/env python3
"""Promote the frozen V167 contextual Guitar winner to rich Iteration 004.

This transform performs no new scoring and never opens the professional reference
or scorer. It reconstructs the already-scored complete contextual winner from the
immutable Iteration 003 parent plus the frozen reference-blind evidence/timebase,
requires exact SHA256 equality to the frozen scored candidate, then promotes only
those already-frozen Guitar additions into the rich I003 payload. Bass is preserved
exactly as the rich I003 list.
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

import build_contextual_guitar_recovery_variants_v167 as contextual_builder
import build_upstream_recovery_variants_v167 as base_builder

EXPECTED = {
    "baseSha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "poolSha256": "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673",
    "manifestSha256": "2f51fa0cba372acc8f797a2e700b3b0a6bb42b807ad4bad818b3c40c262df876",
    "reportSha256": "6b661f6dfa27d31204f4e8a9035d286d5324440b947eb3e49db99205dad9320e",
    "baseBuilderGitBlob": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    "contextualBuilderGitBlob": "fd257fe88c5dcd9b3ab135263a6457140c3f63b6",
    "winnerId": "gctx-o50-q100-allow-noharm",
    "winnerCandidateSha256": "2527870bc4655c238d5f4fbd0e243ab518554e17c4e2c29db2794225bbbeed43",
    "winnerAdded": 63,
    "baseGuitarCount": 1050,
    "winnerGuitarCount": 1113,
    "baseBassCount": 512,
}

EXPECTED_WINNER_CONFIG = {
    "activeStateMode": "allow_active",
    "activitySupportMin": 0.05,
    "baseline": False,
    "candidateToMaxActiveTemplateScoreMin": 1.0,
    "chordIntervalsAllowed": [3, 4, 5, 7, 8, 9, 10],
    "existingIteration003EventsPreferred": True,
    "fundamentalPresentRequired": True,
    "harmonicOctaveIntervalsRejected": [12, 19, 24],
    "id": "gctx-o50-q100-allow-noharm",
    "intervalContextPolicy": "exclude_harmonic_octave",
    "maxAddsPerSite": 1,
    "onsetSupportMin": 0.5,
    "polyphonyCap": 6,
    "requireBasicPitchActiveContext": True,
    "stepMidiDedupe": True,
    "stream": "combinedGuitar",
    "templateRankMin": 0.975,
}

EXPECTED_WINNER_SUMMARY = {
    "added": 63,
    "eligible": 69,
    "sitesWithActiveContext": 204,
    "sitesWithAdds": 63,
    "sitesWithEligible": 63,
}

EXPECTED_WINNER_METRICS = {
    "primaryF1": 0.42617717478052675,
    "primaryPrecision": 0.4797843665768194,
    "primaryRecall": 0.38334529791816224,
    "matched": 534,
    "generated": 1113,
    "reference": 1393,
    "falsePositive": 579,
    "falseNegative": 859,
    "grossF1": 0.5450917797286512,
    "sameMeasurePitchContentF1": 0.5897845171588189,
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
    "grossF1": 0.8309726156751652,
    "sameMeasurePitchContentF1": 0.8404154863078376,
}

EPS = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def normalized_stream(events: list[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        (int(event["measure"]), float(event["step"]), int(event["midi"]))
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    )


def canonical_dict_counter(events: list[Mapping[str, Any]]) -> Counter[str]:
    return Counter(json.dumps(event, sort_keys=True, separators=(",", ":"), allow_nan=False) for event in events)


def exact_metrics(metric: Mapping[str, Any], expected: Mapping[str, Any], name: str) -> None:
    for key, target in expected.items():
        actual = metric.get(key)
        if isinstance(target, float):
            if abs(float(actual) - target) > EPS:
                raise RuntimeError(f"{name} metric drift {key}: {actual} != {target}")
        elif int(actual) != int(target):
            raise RuntimeError(f"{name} metric drift {key}: {actual} != {target}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--base-builder", type=Path, required=True)
    ap.add_argument("--contextual-builder", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--proof", type=Path, required=True)
    ap.add_argument("--base-blob", required=True)
    ap.add_argument("--pool-blob", required=True)
    ap.add_argument("--timebase-blob", required=True)
    ap.add_argument("--manifest-blob", required=True)
    ap.add_argument("--report-blob", required=True)
    args = ap.parse_args()

    if args.output.exists() or args.proof.exists():
        raise RuntimeError("Iteration 004 promotion outputs must not pre-exist")

    for path, expected in (
        (args.base, EXPECTED["baseSha256"]),
        (args.pool, EXPECTED["poolSha256"]),
        (args.manifest, EXPECTED["manifestSha256"]),
        (args.report, EXPECTED["reportSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen promotion input SHA256 mismatch: {path}: {actual}")

    if git_blob_sha(args.base_builder) != EXPECTED["baseBuilderGitBlob"]:
        raise RuntimeError("frozen base builder identity mismatch")
    if git_blob_sha(args.contextual_builder) != EXPECTED["contextualBuilderGitBlob"]:
        raise RuntimeError("frozen contextual builder identity mismatch")

    base = json.loads(args.base.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))

    if base.get("version") != "V167" or int((base.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("promotion base must be frozen V167 Iteration 003")
    safety = base.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise RuntimeError("Iteration 003 safety boundary invalid")

    if manifest.get("schema") != "dadrock.tabs.v167.predeclared-contextual-guitar-recovery-manifest.v1":
        raise RuntimeError("unexpected frozen contextual manifest schema")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("contextual manifest is not the frozen pre-score manifest")
    mpolicy = manifest.get("policy") or {}
    for key, expected in {
        "referenceRead": False,
        "scorerRead": False,
        "allVariantRulesPredeclaredBeforeScoring": True,
        "individualEventSelectionByReference": False,
        "iteration003Immutable": True,
        "bassNormalizedStreamFixedToIteration003": True,
        "newRecoveryStepMidiDedupeAgainstImmutableParent": True,
        "preExistingParentCoordinateDuplicatesPreserved": True,
    }.items():
        if mpolicy.get(key) is not expected:
            raise RuntimeError(f"frozen contextual manifest policy mismatch: {key}")

    if report.get("schema") != "dadrock.tabs.v167.contextual-guitar-recovery-sweep.v1":
        raise RuntimeError("unexpected frozen contextual report schema")
    if report.get("status") != "REFERENCE_GRADED_COMPLETE_PREDECLARED_CONTEXTUAL_VARIANTS":
        raise RuntimeError("contextual report status mismatch")
    selection = report.get("selectionPolicy") or {}
    for key, expected in {
        "wholeVariantOnly": True,
        "individualEventSelectionByReference": False,
        "allVariantsFrozenBeforeReferenceRead": True,
        "iteration004CreatedByThisSweep": False,
        "postScoreVariantMutation": False,
    }.items():
        if selection.get(key) is not expected:
            raise RuntimeError(f"frozen contextual selection policy mismatch: {key}")

    winner = report.get("winner") or {}
    if winner.get("id") != EXPECTED["winnerId"]:
        raise RuntimeError("frozen contextual winner id mismatch")
    if winner.get("candidateSha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("frozen contextual winner candidate SHA256 mismatch")
    if winner.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError(f"frozen contextual winner config mismatch: {winner.get('config')}")
    if winner.get("generationSummary") != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError("frozen contextual winner generation summary mismatch")
    exact_metrics(winner.get("metrics") or {}, EXPECTED_WINNER_METRICS, "Guitar winner")
    exact_metrics((report.get("iteration003Baseline") or {}).get("bass") or {}, EXPECTED_BASS_METRICS, "Bass baseline")
    if int(report.get("nonBaselineVariantsBeatingIteration003", -1)) != 10:
        raise RuntimeError("frozen contextual positive-rule count drift")

    manifest_row = next((row for row in manifest.get("variants") or [] if row.get("id") == EXPECTED["winnerId"]), None)
    if not manifest_row:
        raise RuntimeError("contextual winner absent from frozen pre-score manifest")
    if manifest_row.get("sha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("manifest contextual winner SHA256 mismatch")
    if manifest_row.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError("manifest contextual winner config mismatch")
    if manifest_row.get("summary") != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError("manifest contextual winner summary mismatch")

    streams = base.get("streams") or {}
    full_guitar = list(streams.get("combinedGuitar") or [])
    full_bass = list(streams.get("bass") or [])
    if len(full_guitar) != EXPECTED["baseGuitarCount"]:
        raise RuntimeError("Iteration 003 Guitar count drift")
    if len(full_bass) != EXPECTED["baseBassCount"]:
        raise RuntimeError("Iteration 003 Bass count drift")

    compact_guitar = [base_builder.compact_base_note(dict(row), "combinedGuitar") for row in full_guitar]
    compact_bass = [base_builder.compact_base_note(dict(row), "bass") for row in full_bass]
    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds") or []]
    if len(lattice) < 5 or any(b <= a for a, b in zip(lattice, lattice[1:])):
        raise RuntimeError("invalid frozen subdivision lattice")
    guitar_rows = list((((pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}).get("candidates") or []))
    if len(guitar_rows) != 13328:
        raise RuntimeError("frozen Guitar upstream pool count drift")

    recovered_guitar, summary = contextual_builder.build_guitar(
        compact_guitar,
        guitar_rows,
        copy.deepcopy(EXPECTED_WINNER_CONFIG),
        lattice,
    )
    if summary != EXPECTED_WINNER_SUMMARY:
        raise RuntimeError(f"reconstructed contextual winner summary mismatch: {summary}")
    if len(recovered_guitar) != EXPECTED["winnerGuitarCount"]:
        raise RuntimeError("reconstructed contextual winner Guitar count mismatch")

    variant = {**copy.deepcopy(EXPECTED_WINNER_CONFIG), "summary": copy.deepcopy(summary)}
    minimal_payload = base_builder.score_minimal_payload(base, recovered_guitar, compact_bass, variant)
    with tempfile.TemporaryDirectory(prefix="v167-i004-promotion-") as tmp:
        minimal_path = Path(tmp) / "winner.json"
        write_json(minimal_path, minimal_payload)
        reconstructed_winner_sha256 = sha256_file(minimal_path)
    if reconstructed_winner_sha256 != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError(
            "reconstructed score-minimal contextual winner does not equal frozen scored winner: "
            f"{reconstructed_winner_sha256}"
        )

    parent_coordinate_set = {
        (int(row["measure"]), float(row["step"]), int(row["midi"]))
        for row in compact_guitar
        if not bool(row.get("excludeFromScoring", False))
    }
    additions = [
        copy.deepcopy(row)
        for row in recovered_guitar
        if (int(row["measure"]), float(row["step"]), int(row["midi"])) not in parent_coordinate_set
    ]
    if len(additions) != EXPECTED["winnerAdded"]:
        raise RuntimeError(f"reconstructed contextual additions drift: {len(additions)}")
    if any("v167RecoverySweepEvidence" not in row for row in additions):
        raise RuntimeError("reconstructed contextual addition missing frozen recovery evidence")
    addition_coordinates = [(int(row["measure"]), float(row["step"]), int(row["midi"])) for row in additions]
    if len(set(addition_coordinates)) != len(addition_coordinates):
        raise RuntimeError("reconstructed contextual additions contain duplicate coordinates")

    output = copy.deepcopy(base)
    output_streams = output.get("streams")
    if not isinstance(output_streams, dict):
        raise RuntimeError("Iteration 003 output missing streams")

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
        raise RuntimeError("pre-existing Iteration 003 Guitar event dictionaries changed during promotion")
    if output_streams["bass"] != full_bass:
        raise RuntimeError("Iteration 004 Bass rich list changed during Guitar-only promotion")

    if normalized_stream(output_streams["combinedGuitar"]) != normalized_stream(minimal_payload["streams"]["combinedGuitar"]):
        raise RuntimeError("Iteration 004 Guitar normalized stream differs from frozen scored contextual winner")
    if normalized_stream(output_streams["bass"]) != normalized_stream(minimal_payload["streams"]["bass"]):
        raise RuntimeError("Iteration 004 Bass normalized stream differs from frozen I003 Bass")

    prior_calibration = copy.deepcopy(base.get("calibration"))
    output["schema"] = "dadrock.tabs.v167.single-song-calibrated-generated.v4"
    output["version"] = "V167"
    output["status"] = "CALIBRATION_ITERATION_004_FROZEN_CONTEXTUAL_GUITAR_WINNER_PROMOTED"
    output["calibration"] = {
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "iteration": 4,
        "parentVersion": "V167",
        "parentIteration": 3,
        "parentCandidateGitBlob": args.base_blob,
        "parentCandidateSha256": sha256_file(args.base),
        "evidencePoolGitBlob": args.pool_blob,
        "timebaseGitBlob": args.timebase_blob,
        "contextualSweepManifestGitBlob": args.manifest_blob,
        "contextualSweepReportGitBlob": args.report_blob,
        "selectedRuleId": EXPECTED["winnerId"],
        "selectedWholeRule": copy.deepcopy(EXPECTED_WINNER_CONFIG),
        "frozenScoredWinnerCandidateSha256": EXPECTED["winnerCandidateSha256"],
        "reconstructedScoredWinnerCandidateSha256": reconstructed_winner_sha256,
        "streamChanges": {
            "combinedGuitar": {
                "preExistingEventsChanged": False,
                "parentEventCount": len(full_guitar),
                "contextualRecoveryEventsAdded": len(additions),
                "eventCount": len(rich_guitar),
                "normalizedStreamEqualFrozenWinner": True,
            },
            "bass": {
                "changed": False,
                "parentEventCount": len(full_bass),
                "eventCount": len(rich_bass),
                "richListExactlyPreserved": True,
                "normalizedStreamEqualIteration003": True,
            },
        },
        "inheritedFrozenSweepMetrics": {
            "combinedGuitar": copy.deepcopy(winner.get("metrics")),
            "bass": copy.deepcopy((report.get("iteration003Baseline") or {}).get("bass")),
            "basis": "exact_normalized_measure_step_midi_stream_equality_to_already_scored_frozen_contextual_winner",
            "newReferenceFacingScorePerformedByPromotion": False,
        },
        "priorCalibration": prior_calibration,
        "professionalReferenceReadByTransform": False,
        "scorerReadByTransform": False,
        "directReferenceEventCopy": False,
        "individualEventSelectionByReference": False,
        "wholeRuleSelectedByFrozenReferenceGradedSweep": True,
        "postSweepRetuning": False,
        "humanCorrection": False,
        "generalizationClaim": False,
    }

    output_safety = copy.deepcopy(base.get("safety") or {})
    output_safety.update({
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
    })
    output["safety"] = output_safety

    write_json(args.output, output)
    proof = {
        "schema": "dadrock.tabs.v167.iteration-004-contextual-guitar-promotion-proof.v1",
        "version": "V167",
        "status": "ITERATION_004_NORMALIZED_STREAM_EQUALITY_PROVEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003GitBlob": args.base_blob,
            "iteration003Sha256": sha256_file(args.base),
            "evidencePoolGitBlob": args.pool_blob,
            "evidencePoolSha256": sha256_file(args.pool),
            "timebaseGitBlob": args.timebase_blob,
            "timebaseSha256": sha256_file(args.timebase),
            "contextualSweepManifestGitBlob": args.manifest_blob,
            "contextualSweepManifestSha256": sha256_file(args.manifest),
            "contextualSweepReportGitBlob": args.report_blob,
            "contextualSweepReportSha256": sha256_file(args.report),
            "baseBuilderGitBlob": EXPECTED["baseBuilderGitBlob"],
            "contextualBuilderGitBlob": EXPECTED["contextualBuilderGitBlob"],
        },
        "selectedWinner": {
            "id": EXPECTED["winnerId"],
            "config": copy.deepcopy(EXPECTED_WINNER_CONFIG),
            "generationSummary": copy.deepcopy(summary),
            "frozenCandidateSha256": EXPECTED["winnerCandidateSha256"],
            "reconstructedCandidateSha256": reconstructed_winner_sha256,
            "frozenGuitarMetrics": copy.deepcopy(winner.get("metrics")),
            "inheritedBassMetrics": copy.deepcopy((report.get("iteration003Baseline") or {}).get("bass")),
        },
        "streamProof": {
            "combinedGuitar": {
                "parentCount": len(full_guitar),
                "contextualRecoveryAdditions": len(additions),
                "iteration004Count": len(output_streams["combinedGuitar"]),
                "parentRichEventDictionaryMultisetExactlyPreserved": (
                    promoted_guitar_dicts == original_guitar_dicts + addition_dicts
                ),
                "newCoordinatesDisjointFromParent": all(coord not in parent_coordinate_set for coord in addition_coordinates),
                "newCoordinatesUnique": len(set(addition_coordinates)) == len(addition_coordinates),
                "normalizedEqualFrozenScoredWinner": True,
            },
            "bass": {
                "parentCount": len(full_bass),
                "iteration004Count": len(output_streams["bass"]),
                "richListExactlyPreserved": output_streams["bass"] == full_bass,
                "normalizedEqualIteration003": True,
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
        "iteration004CandidateSha256": sha256_file(args.output),
    }
    write_json(args.proof, proof)

    print(json.dumps({
        "winnerId": EXPECTED["winnerId"],
        "reconstructedWinnerSha256": reconstructed_winner_sha256,
        "contextualRecoveryAdditions": len(additions),
        "iteration004Counts": {
            "combinedGuitar": len(output_streams["combinedGuitar"]),
            "bass": len(output_streams["bass"]),
        },
        "iteration004CandidateSha256": sha256_file(args.output),
        "newReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
