#!/usr/bin/env python3
"""Promote the frozen V167 upstream-recovery Bass winner to rich Iteration 003.

This transform is reference-blind. It reads only frozen generated/evidence/timebase
artifacts plus the already-frozen recovery sweep manifest/report. It reconstructs
the exact already-scored score-minimal winner and requires its SHA256 to match the
frozen sweep candidate before writing a rich Iteration 003 payload. Guitar and all
pre-existing Iteration 002 Bass event dictionaries are preserved unchanged; only
the frozen winner's 110 Bass recovery events are added.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

EXPECTED = {
    "baseSha256": "96fbc329d9ba46b06d430c7c3c7b7f5b0e9077f6e133da5c3165c1fde609b5cc",
    "poolSha256": "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673",
    "manifestSha256": "c91ee15d702746e082c059b5f99c44fcfa7a89f18e5e9f2fc81eb6513d1baa80",
    "reportSha256": "1bcc5eca05df31270ff7ff638cca6def3166a0e5084c4874d70d710d4696836f",
    "baseBuilderGitBlob": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    "rearmBuilderGitBlob": "fbbee07493084792912c774d375ca5011672891f",
    "winnerId": "b-r975-o50-a10-low_register_no_stable_state",
    "winnerCandidateSha256": "2e04edd9cb61795ea9679ce899c7ded9549bb0f5d9f8e04a5d53fdf07ec9fa13",
    "winnerAdded": 110,
    "baseGuitarCount": 1050,
    "baseBassCount": 402,
    "winnerBassCount": 512,
}
EXPECTED_WINNER_CONFIG = {
    "id": "b-r975-o50-a10-low_register_no_stable_state",
    "stream": "bass",
    "baseline": False,
    "templateRankMin": 0.975,
    "onsetSupportMin": 0.5,
    "activitySupportMin": 0.1,
    "fundamentalPresentRequired": True,
    "scope": "low_register_no_stable_state",
    "lowRegisterMaxMidi": 40,
    "existingEventsPreferred": True,
    "newRecoveryCapPerPreviouslyEmptyStep": 1,
    "preExistingIteration002StepCollisionsPreserved": True,
}
EXPECTED_WINNER_METRICS = {
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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def load_module(path: Path, expected_blob: str, name: str):
    if not path.is_file() or git_blob_sha(path) != expected_blob:
        raise RuntimeError(f"{name} identity mismatch")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name}: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalized_stream(events: list[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    rows = [
        (int(event["measure"]), float(event["step"]), int(event["midi"]))
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    ]
    return sorted(rows)


def canonical_dict_counter(events: list[Mapping[str, Any]]) -> Counter[str]:
    return Counter(json.dumps(event, sort_keys=True, separators=(",", ":"), allow_nan=False) for event in events)


def exact_metrics(metric: Mapping[str, Any]) -> bool:
    for key, expected in EXPECTED_WINNER_METRICS.items():
        actual = metric.get(key)
        if isinstance(expected, float):
            if abs(float(actual) - expected) > 1e-12:
                return False
        elif int(actual) != expected:
            return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--base-builder", type=Path, required=True)
    ap.add_argument("--rearm-builder", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--proof", type=Path, required=True)
    ap.add_argument("--base-blob", required=True)
    ap.add_argument("--pool-blob", required=True)
    ap.add_argument("--timebase-blob", required=True)
    ap.add_argument("--manifest-blob", required=True)
    ap.add_argument("--report-blob", required=True)
    args = ap.parse_args()

    if args.output.exists() or args.proof.exists():
        raise RuntimeError("Iteration 003 promotion outputs must not pre-exist")
    for path, expected in (
        (args.base, EXPECTED["baseSha256"]),
        (args.pool, EXPECTED["poolSha256"]),
        (args.manifest, EXPECTED["manifestSha256"]),
        (args.report, EXPECTED["reportSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen promotion input SHA256 mismatch: {path}: {actual}")

    base_builder = load_module(args.base_builder, EXPECTED["baseBuilderGitBlob"], "v167_frozen_recovery_base_builder")
    rearm_builder = load_module(args.rearm_builder, EXPECTED["rearmBuilderGitBlob"], "v167_frozen_recovery_rearm_builder")

    base = json.loads(args.base.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    report = json.loads(args.report.read_text(encoding="utf-8"))

    if base.get("version") != "V167" or int((base.get("calibration") or {}).get("iteration", -1)) != 2:
        raise RuntimeError("promotion base must be frozen V167 Iteration 002")
    safety = base.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise RuntimeError("Iteration 002 safety boundary invalid")
    if manifest.get("status") != "FROZEN_BEFORE_REFERENCE_SCORING":
        raise RuntimeError("recovery manifest is not the frozen pre-score manifest")
    if report.get("status") != "REFERENCE_GRADED_COMPLETE_PREDECLARED_VARIANTS":
        raise RuntimeError("recovery report status mismatch")
    selection = report.get("selectionPolicy") or {}
    if selection.get("wholeVariantOnly") is not True or selection.get("individualEventSelectionByReference") is not False:
        raise RuntimeError("frozen whole-rule selection policy mismatch")

    winner = (report.get("winners") or {}).get("bass") or {}
    if winner.get("id") != EXPECTED["winnerId"]:
        raise RuntimeError("frozen Bass winner id mismatch")
    if winner.get("candidateSha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("frozen Bass winner candidate SHA256 mismatch")
    if winner.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError(f"frozen Bass winner config mismatch: {winner.get('config')}")
    if not exact_metrics(winner.get("metrics") or {}):
        raise RuntimeError("frozen Bass winner metrics mismatch")
    if int((winner.get("generationSummary") or {}).get("added", -1)) != EXPECTED["winnerAdded"]:
        raise RuntimeError("frozen Bass winner addition count mismatch")

    manifest_row = next((row for row in manifest.get("variants") or [] if row.get("id") == EXPECTED["winnerId"]), None)
    if not manifest_row:
        raise RuntimeError("winner absent from frozen pre-score manifest")
    if manifest_row.get("sha256") != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError("manifest winner SHA256 mismatch")
    if manifest_row.get("config") != EXPECTED_WINNER_CONFIG:
        raise RuntimeError("manifest winner config mismatch")
    if manifest_row.get("summary") != winner.get("generationSummary"):
        raise RuntimeError("manifest/report winner generation summary mismatch")

    streams = base.get("streams") or {}
    full_guitar = streams.get("combinedGuitar") or []
    full_bass = streams.get("bass") or []
    if len(full_guitar) != EXPECTED["baseGuitarCount"] or len(full_bass) != EXPECTED["baseBassCount"]:
        raise RuntimeError("Iteration 002 stream count drift")
    compact_guitar = [base_builder.compact_base_note(dict(row), "combinedGuitar") for row in full_guitar]
    compact_bass = [base_builder.compact_base_note(dict(row), "bass") for row in full_bass]

    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds") or []]
    if len(lattice) < 5 or any(b <= a for a, b in zip(lattice, lattice[1:])):
        raise RuntimeError("invalid frozen subdivision lattice")
    upstream = pool.get("upstreamPitchPools") or {}
    bass_rows = list((upstream.get("bassPreAdmission") or {}).get("candidates") or [])
    if len(bass_rows) != 36520:
        raise RuntimeError("frozen Bass upstream pool count drift")

    recovered_bass, summary = rearm_builder.build_bass(
        compact_bass,
        bass_rows,
        copy.deepcopy(EXPECTED_WINNER_CONFIG),
        lattice,
    )
    if summary != winner.get("generationSummary"):
        raise RuntimeError(f"reconstructed winner summary mismatch: {summary}")
    if len(recovered_bass) != EXPECTED["winnerBassCount"]:
        raise RuntimeError("reconstructed winner Bass count mismatch")

    variant = {**copy.deepcopy(EXPECTED_WINNER_CONFIG), "summary": copy.deepcopy(summary)}
    minimal_payload = base_builder.score_minimal_payload(base, compact_guitar, recovered_bass, variant)
    with tempfile.TemporaryDirectory(prefix="v167-i003-promotion-") as tmp:
        minimal_path = Path(tmp) / "winner.json"
        write_json(minimal_path, minimal_payload)
        reconstructed_winner_sha256 = sha256_file(minimal_path)
    if reconstructed_winner_sha256 != EXPECTED["winnerCandidateSha256"]:
        raise RuntimeError(
            "reconstructed score-minimal winner does not equal frozen scored winner: "
            f"{reconstructed_winner_sha256}"
        )

    additions = [copy.deepcopy(row) for row in recovered_bass if "v167RecoverySweepEvidence" in row]
    if len(additions) != EXPECTED["winnerAdded"]:
        raise RuntimeError(f"reconstructed recovery additions drift: {len(additions)}")
    base_compact_counter = Counter((int(x["measure"]), float(x["step"]), int(x["midi"])) for x in compact_bass)
    recovered_counter = Counter((int(x["measure"]), float(x["step"]), int(x["midi"])) for x in recovered_bass)
    addition_counter = Counter((int(x["measure"]), float(x["step"]), int(x["midi"])) for x in additions)
    if recovered_counter != base_compact_counter + addition_counter:
        raise RuntimeError("reconstructed winner is not exactly Iteration 002 Bass plus frozen additions")

    output = copy.deepcopy(base)
    output_streams = output.get("streams")
    if not isinstance(output_streams, dict):
        raise RuntimeError("Iteration 002 output missing streams")
    rich_bass = [copy.deepcopy(row) for row in full_bass] + additions
    rich_bass.sort(key=lambda row: (int(row["measure"]), float(row["step"]), int(row["midi"]), 1 if "v167RecoverySweepEvidence" in row else 0))
    output_streams["combinedGuitar"] = copy.deepcopy(full_guitar)
    output_streams["bass"] = rich_bass

    # Prove every pre-existing rich event dictionary is preserved exactly, even
    # though the combined Bass list is canonically re-sorted after additions.
    original_bass_dicts = canonical_dict_counter(full_bass)
    promoted_base_bass_dicts = canonical_dict_counter([row for row in rich_bass if "v167RecoverySweepEvidence" not in row])
    if promoted_base_bass_dicts != original_bass_dicts:
        raise RuntimeError("pre-existing Iteration 002 Bass event content changed during promotion")
    if output_streams["combinedGuitar"] != full_guitar:
        raise RuntimeError("Iteration 003 Guitar changed during Bass-only promotion")

    if normalized_stream(output_streams["combinedGuitar"]) != normalized_stream(minimal_payload["streams"]["combinedGuitar"]):
        raise RuntimeError("Iteration 003 Guitar normalized stream differs from frozen scored winner")
    if normalized_stream(output_streams["bass"]) != normalized_stream(minimal_payload["streams"]["bass"]):
        raise RuntimeError("Iteration 003 Bass normalized stream differs from frozen scored winner")

    prior_calibration = copy.deepcopy(base.get("calibration"))
    output["schema"] = "dadrock.tabs.v167.single-song-calibrated-generated.v3"
    output["version"] = "V167"
    output["status"] = "CALIBRATION_ITERATION_003_FROZEN_UPSTREAM_BASS_WINNER_PROMOTED"
    output["calibration"] = {
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "iteration": 3,
        "parentVersion": "V167",
        "parentIteration": 2,
        "parentCandidateGitBlob": args.base_blob,
        "parentCandidateSha256": sha256_file(args.base),
        "evidencePoolGitBlob": args.pool_blob,
        "timebaseGitBlob": args.timebase_blob,
        "recoverySweepManifestGitBlob": args.manifest_blob,
        "recoverySweepReportGitBlob": args.report_blob,
        "selectedRuleId": EXPECTED["winnerId"],
        "selectedWholeRule": copy.deepcopy(EXPECTED_WINNER_CONFIG),
        "frozenScoredWinnerCandidateSha256": EXPECTED["winnerCandidateSha256"],
        "reconstructedScoredWinnerCandidateSha256": reconstructed_winner_sha256,
        "streamChanges": {
            "combinedGuitar": {
                "changed": False,
                "eventCount": len(full_guitar),
                "normalizedStreamEqualFrozenWinner": True,
            },
            "bass": {
                "preExistingEventsChanged": False,
                "parentEventCount": len(full_bass),
                "recoveryEventsAdded": len(additions),
                "eventCount": len(rich_bass),
                "normalizedStreamEqualFrozenWinner": True,
            },
        },
        "inheritedFrozenSweepMetrics": {
            "combinedGuitar": copy.deepcopy((report.get("iteration002Baseline") or {}).get("combinedGuitar")),
            "bass": copy.deepcopy(winner.get("metrics")),
            "basis": "exact_normalized_measure_step_midi_stream_equality_to_already_scored_frozen_winner",
            "newReferenceFacingScorePerformedByPromotion": False,
        },
        "priorCalibration": prior_calibration,
        "professionalReferenceReadByTransform": False,
        "directReferenceEventCopy": False,
        "individualEventSelectionByReference": False,
        "wholeRuleSelectedByFrozenReferenceGradedSweep": True,
        "humanCorrection": False,
        "generalizationClaim": False,
    }

    write_json(args.output, output)
    proof = {
        "schema": "dadrock.tabs.v167.iteration-003-promotion-proof.v1",
        "version": "V167",
        "status": "ITERATION_003_NORMALIZED_STREAM_EQUALITY_PROVEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration002GitBlob": args.base_blob,
            "iteration002Sha256": sha256_file(args.base),
            "evidencePoolGitBlob": args.pool_blob,
            "evidencePoolSha256": sha256_file(args.pool),
            "timebaseGitBlob": args.timebase_blob,
            "timebaseSha256": sha256_file(args.timebase),
            "sweepManifestGitBlob": args.manifest_blob,
            "sweepManifestSha256": sha256_file(args.manifest),
            "sweepReportGitBlob": args.report_blob,
            "sweepReportSha256": sha256_file(args.report),
            "baseBuilderGitBlob": EXPECTED["baseBuilderGitBlob"],
            "rearmBuilderGitBlob": EXPECTED["rearmBuilderGitBlob"],
        },
        "selectedWinner": {
            "id": EXPECTED["winnerId"],
            "config": copy.deepcopy(EXPECTED_WINNER_CONFIG),
            "generationSummary": copy.deepcopy(summary),
            "frozenCandidateSha256": EXPECTED["winnerCandidateSha256"],
            "reconstructedCandidateSha256": reconstructed_winner_sha256,
            "frozenMetrics": copy.deepcopy(winner.get("metrics")),
        },
        "streamProof": {
            "combinedGuitar": {
                "parentCount": len(full_guitar),
                "iteration003Count": len(output_streams["combinedGuitar"]),
                "parentRichListExactlyPreserved": output_streams["combinedGuitar"] == full_guitar,
                "normalizedEqualFrozenScoredWinner": True,
            },
            "bass": {
                "parentCount": len(full_bass),
                "recoveryAdditions": len(additions),
                "iteration003Count": len(output_streams["bass"]),
                "preExistingRichEventDictionaryMultisetExactlyPreserved": promoted_base_bass_dicts == original_bass_dicts,
                "normalizedEqualFrozenScoredWinner": True,
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
        "iteration003CandidateSha256": sha256_file(args.output),
    }
    write_json(args.proof, proof)
    print(json.dumps({
        "winnerId": EXPECTED["winnerId"],
        "reconstructedWinnerSha256": reconstructed_winner_sha256,
        "recoveryAdditions": len(additions),
        "iteration003Counts": {
            "combinedGuitar": len(output_streams["combinedGuitar"]),
            "bass": len(output_streams["bass"]),
        },
        "iteration003CandidateSha256": sha256_file(args.output),
        "newReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
