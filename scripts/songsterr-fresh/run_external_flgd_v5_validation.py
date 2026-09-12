#!/usr/bin/env python3
"""Official deferred-reveal entrypoint for FLGD V5 external validation.

Scoring semantics are supplied by the frozen core harness
`external_flgd_v5_validation.py`.  This adapter changes execution order only:
all 79 performances must finish reference-blind Basic Pitch + V5 inference
before any reference matching/correctness calculation is entered.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
from collections import Counter
from pathlib import Path

CORE_PATH = Path(__file__).with_name("external_flgd_v5_validation.py")
spec = importlib.util.spec_from_file_location("flgd_v5_frozen_core", CORE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("FLGD_V5_CORE_IMPORT_SPEC_FAILED")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

CONTRACT = core.CONTRACT
ADAPTER_CONTRACT = "songsterr-fresh-flgd-v5-deferred-correctness-reveal-v1"
VERSION = 1


class DeferredRevealError(RuntimeError):
    pass


def process_one_file_reference_blind(
    repo_root: Path,
    dataset_root: Path,
    work_dir: Path,
    v5,
    row: dict,
    index: int,
) -> dict:
    """Run source verification, canonicalization, Basic Pitch and V5 only.

    Deliberately has no reference-note argument and performs no matcher call.
    """
    stem = row["stem"]
    audio_info = row.get("audio", {})
    audio_rel = audio_info.get("path")
    if not isinstance(audio_rel, str):
        raise core.ValidationError(f"AUDIO_PATH_INVALID:{stem}")
    source_mp3 = dataset_root / audio_rel
    if not source_mp3.is_file() or source_mp3.is_symlink():
        raise core.ValidationError(f"AUDIO_FILE_INVALID:{stem}")
    source_sha = core.sha256_file(source_mp3)
    if source_sha != audio_info.get("sha256"):
        raise core.ValidationError(f"AUDIO_SHA256_CHANGED:{stem}")

    file_root = work_dir / f"track-{index:03d}-{stem}"
    if file_root.exists():
        raise core.ValidationError(f"TRACK_WORK_DIR_ALREADY_EXISTS:{file_root}")
    file_root.mkdir(parents=True)

    canonical_wav = file_root / "canonical.wav"
    audio, canonical = core.canonicalize_audio(source_mp3, canonical_wav)

    inference_json = file_root / "basic-pitch.json"
    inference_log = file_root / "basic-pitch.log"
    core.run_transcriber(repo_root, canonical_wav, inference_json, inference_log, source_sha)
    estimates = core.validate_basic_pitch_payload(inference_json)
    classified, class_counts = core.classify_events(v5, audio, estimates)

    before = [(x["noteId"], x["startSeconds"], x["midi"]) for x in estimates]
    after = [(x["noteId"], x["startSeconds"], x["midi"]) for x in classified]
    if before != after:
        raise core.ValidationError(f"PHASE1_EVENT_IDENTITY_CHANGED:{stem}")
    if sum(class_counts.values()) != len(estimates):
        raise core.ValidationError(f"PHASE1_CLASSIFICATION_COUNT_MISMATCH:{stem}")

    return {
        "index": index,
        "stem": stem,
        "split": row["split"],
        "guitarType": row["guitarType"],
        "sourceAudio": {"path": audio_rel, "sha256": source_sha},
        "canonicalAudio": canonical,
        "decodedEventCount": len(estimates),
        "classificationCounts": class_counts,
        "classifiedEventCount": sum(class_counts.values()),
        "positiveCount": int(class_counts[core.CLASS_POSITIVE]),
        "basicPitchOutputSha256": core.sha256_file(inference_json),
        "_decodedEvents": estimates,
        "_classifiedEvents": classified,
    }


def score_processed_file(processed: dict, references: list[dict]) -> dict:
    """Apply the already-frozen matcher only after global Phase-1 completion."""
    estimates = list(processed["_decodedEvents"])
    classified = list(processed["_classifiedEvents"])
    positives = [row for row in classified if row["classification"] == core.CLASS_POSITIVE]

    positive_matches = core.maximum_cardinality_matches(positives, references)
    baseline_matches = core.maximum_cardinality_matches(estimates, references)
    correct = len(positive_matches)
    baseline_correct = len(baseline_matches)

    result = {key: value for key, value in processed.items() if not key.startswith("_")}
    result.update({
        "referenceEventCount": len(references),
        "positiveCorrectCount": correct,
        "positivePrecision": core.precision(correct, len(positives)),
        "positiveRecall": core.recall(correct, len(references)),
        "baselineCorrectCount": baseline_correct,
        "baselinePrecision": core.precision(baseline_correct, len(estimates)),
    })
    return result


def run_two_phase_items(items: list, phase1_processor, phase2_scorer) -> list:
    """Guarantee Phase 2 is unreachable until every Phase-1 item succeeds."""
    processed = []
    total = len(items)
    for index, item in enumerate(items, start=1):
        processed.append(phase1_processor(item, index, total))
    if len(processed) != total:
        raise DeferredRevealError("PHASE1_COMPLETENESS_GUARD_FAILED")
    return [phase2_scorer(item) for item in processed]


def aggregate_scored_rows(rows: list[dict]) -> dict:
    decoded = sum(row["decodedEventCount"] for row in rows)
    classified = sum(row["classifiedEventCount"] for row in rows)
    positives = sum(row["positiveCount"] for row in rows)
    correct = sum(row["positiveCorrectCount"] for row in rows)
    baseline_correct = sum(row["baselineCorrectCount"] for row in rows)
    refs = sum(row["referenceEventCount"] for row in rows)
    class_counts = Counter()
    for row in rows:
        class_counts.update(row["classificationCounts"])

    aggregate = {
        "completedFileCount": len(rows),
        "referenceEventCount": refs,
        "decodedEventCount": decoded,
        "classifiedEventCount": classified,
        "classificationCounts": {
            name: int(class_counts.get(name, 0)) for name in core.CLASSIFICATIONS
        },
        "positiveEventCount": positives,
        "positiveCorrectCount": correct,
        "positivePrecision": core.precision(correct, positives),
        "positivePrecisionWilsonLowerOneSided95": core.wilson_lower_one_sided_95(correct, positives),
        "positiveRecall": core.recall(correct, refs),
        "baselineCorrectCount": baseline_correct,
        "baselinePrecision": core.precision(baseline_correct, decoded),
        "bySplit": core.summarize_by(rows, "split"),
        "byGuitarType": core.summarize_by(rows, "guitarType"),
        "identityRuntimeGuards": True,
        "policyBoundaryGuard": True,
    }
    aggregate["gates"] = core.evaluate_gates(aggregate)
    aggregate["externalValidationPassed"] = bool(
        aggregate["gates"]["allMandatoryGatesPassed"]
    )
    return aggregate


def run_real(
    repo_root: Path,
    dataset_root: Path,
    stage_b_path: Path,
    work_dir: Path,
) -> dict:
    source = core.verify_repo_source(repo_root)
    dataset = core.verify_dataset_source(dataset_root)
    runtime = core.package_runtime()
    stage_b = core.validate_stage_b_report(stage_b_path)
    v5 = core.load_frozen_v5(repo_root)

    if work_dir.exists():
        raise core.ValidationError("WORK_DIR_MUST_NOT_ALREADY_EXIST")
    work_dir.mkdir(parents=True)

    phase1_rows = []
    total = len(stage_b["included"])
    for index, row in enumerate(stage_b["included"], start=1):
        stem = row["stem"]
        print(f"FLGD_V5_PHASE1_TRACK_START {index}/{total} {stem}", flush=True)
        processed = process_one_file_reference_blind(
            repo_root, dataset_root, work_dir, v5, row, index
        )
        phase1_rows.append(processed)
        counts = processed["classificationCounts"]
        print(
            "FLGD_V5_PHASE1_TRACK_COMPLETE "
            f"{index}/{total} {stem} decoded={processed['decodedEventCount']} "
            f"positive={counts[core.CLASS_POSITIVE]} "
            f"negative={counts[core.CLASS_NEGATIVE]} "
            f"insufficient={counts[core.CLASS_INSUFFICIENT]}",
            flush=True,
        )

    if len(phase1_rows) != core.EXPECTED_PERFORMANCE_COUNT:
        raise core.ValidationError(
            f"PHASE1_PERFORMANCE_COUNT_CHANGED:{len(phase1_rows)}"
        )
    if sum(row["classifiedEventCount"] for row in phase1_rows) != sum(
        row["decodedEventCount"] for row in phase1_rows
    ):
        raise core.ValidationError("PHASE1_GLOBAL_EVENT_PRESERVATION_FAILED")

    print(
        f"FLGD_V5_PHASE1_ALL_REFERENCE_BLIND_COMPLETE {len(phase1_rows)}/{total}",
        flush=True,
    )

    # Reference material is reconstructed only after all 79 reference-blind
    # inference/classification records exist.
    adapter = core.load_stage_b_adapter(repo_root)
    references_by_stem = core.reconstruct_references(adapter, dataset_root, stage_b)
    print("FLGD_V5_PHASE2_SCORING_START", flush=True)

    scored_rows = []
    for processed in phase1_rows:
        stem = processed["stem"]
        scored_rows.append(score_processed_file(processed, references_by_stem[stem]))

    aggregate = aggregate_scored_rows(scored_rows)
    return {
        "contract": CONTRACT,
        "version": core.VERSION,
        "executionSafety": {
            "contract": ADAPTER_CONTRACT,
            "version": VERSION,
            "referenceBlindPhase1RequiredForAllFiles": True,
            "phase1CompletedFileCountBeforeScoring": len(phase1_rows),
            "partialCorrectnessProgressEmitted": False,
            "adapterSha256": core.sha256_file(Path(__file__).resolve()),
        },
        "source": source,
        "dataset": dataset,
        "runtime": runtime,
        "inputs": {
            "stageAReportSha256": core.EXPECTED_STAGE_A_REPORT_SHA256,
            "stageBReportSha256": core.EXPECTED_STAGE_B_REPORT_SHA256,
            "includedPopulationSha256": core.EXPECTED_INCLUDED_POPULATION_SHA256,
            "referenceEventIdentitySha256": core.EXPECTED_REFERENCE_IDENTITY_SHA256,
            "ignoredDuplicateReleaseIdentitySha256": core.EXPECTED_IGNORED_RELEASE_IDENTITY_SHA256,
        },
        "scoringContract": {
            "onsetToleranceSeconds": core.ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCents": core.PITCH_TOLERANCE_CENTS,
            "inclusiveAbsTolerance": core.INCLUSIVE_ABS_TOL,
            "wilsonZOneSided95": core.WILSON_Z_ONE_SIDED_95,
            "minimumTotalPositives": core.MIN_TOTAL_POSITIVES,
            "overallWilsonLowerBoundMin": core.OVERALL_WILSON_LOWER_BOUND_MIN,
            "stratumMinimumPositives": core.STRATUM_MIN_POSITIVES,
            "stratumPointPrecisionMin": core.STRATUM_POINT_PRECISION_MIN,
            "durationUsedForMatching": False,
        },
        "files": scored_rows,
        "aggregate": aggregate,
        "policyBoundary": {
            "basicPitchInvoked": True,
            "v5ClassifierInvoked": True,
            "demucsInvoked": False,
            "audioSamplesUsedForPitchAnalysis": True,
            "estimateReferenceMatchingPerformed": True,
            "correctnessMetricComputed": True,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "protectedSongUsed": False,
            "separatePolicyReviewRequired": True,
        },
    }


def self_test() -> dict:
    signature = inspect.signature(process_one_file_reference_blind)
    assert "references" not in signature.parameters

    score_calls = []

    def phase1_ok(item, index, total):
        return {"item": item, "index": index, "total": total}

    def phase2(record):
        score_calls.append(record["item"])
        return record["item"]

    assert run_two_phase_items(["a", "b", "c"], phase1_ok, phase2) == ["a", "b", "c"]
    assert score_calls == ["a", "b", "c"]

    score_calls.clear()

    def phase1_fail(item, index, total):
        if index == 2:
            raise DeferredRevealError("SYNTHETIC_PHASE1_FAILURE")
        return {"item": item}

    try:
        run_two_phase_items(["a", "b", "c"], phase1_fail, phase2)
    except DeferredRevealError as exc:
        assert str(exc) == "SYNTHETIC_PHASE1_FAILURE"
    else:
        raise AssertionError("synthetic phase1 failure must propagate")
    assert score_calls == []

    # Scoring uses the already-frozen core matcher.
    processed = {
        "index": 1,
        "stem": "synthetic",
        "split": "train",
        "guitarType": "nylon",
        "sourceAudio": {"path": "synthetic.mp3", "sha256": "x" * 64},
        "canonicalAudio": {"sampleRate": 44100},
        "decodedEventCount": 2,
        "classificationCounts": {
            core.CLASS_POSITIVE: 1,
            core.CLASS_NEGATIVE: 1,
            core.CLASS_INSUFFICIENT: 0,
        },
        "classifiedEventCount": 2,
        "positiveCount": 1,
        "basicPitchOutputSha256": "y" * 64,
        "_decodedEvents": [
            {"noteId": "e0", "startSeconds": 1.05, "midi": 60},
            {"noteId": "e1", "startSeconds": 2.0, "midi": 61},
        ],
        "_classifiedEvents": [
            {
                "noteId": "e0",
                "startSeconds": 1.05,
                "midi": 60,
                "classification": core.CLASS_POSITIVE,
                "reason": "synthetic",
            },
            {
                "noteId": "e1",
                "startSeconds": 2.0,
                "midi": 61,
                "classification": core.CLASS_NEGATIVE,
                "reason": "synthetic",
            },
        ],
    }
    refs = [
        {"referenceId": "r0", "onsetSeconds": 1.0, "midi": 60},
        {"referenceId": "r1", "onsetSeconds": 2.0, "midi": 61},
    ]
    scored = score_processed_file(processed, refs)
    assert scored["positiveCorrectCount"] == 1
    assert scored["positivePrecision"] == 1.0
    assert scored["baselineCorrectCount"] == 2
    assert not any(key.startswith("_") for key in scored)

    source_text = Path(__file__).read_text(encoding="utf-8")
    complete_line = next(
        line for line in source_text.splitlines() if "FLGD_V5_PHASE1_TRACK_COMPLETE" in line
    )
    assert "correct=" not in complete_line
    assert "precision" not in complete_line.lower()

    return {
        "contract": ADAPTER_CONTRACT,
        "selfTest": "PASS",
        "phase1ApiContainsReferences": False,
        "syntheticPhase1FailureEnteredScoring": False,
        "partialCorrectnessProgressEmitted": False,
        "coreScoringContract": core.CONTRACT,
        "policyBoundary": {
            "realFLGDAccessed": False,
            "basicPitchInvoked": False,
            "v5ClassifierInvoked": False,
            "correctnessMetricComputedOnRealCorpus": False,
            "protectedSongUsed": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root")
    parser.add_argument("--dataset-root")
    parser.add_argument("--stage-b-result")
    parser.add_argument("--work-dir")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(core.canonical_json(self_test()))
        return 0

    required = {
        "repo_root": args.repo_root,
        "dataset_root": args.dataset_root,
        "stage_b_result": args.stage_b_result,
        "work_dir": args.work_dir,
        "output": args.output,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise core.ValidationError(f"REAL_MODE_ARGUMENTS_REQUIRED:{','.join(missing)}")

    output = Path(args.output).resolve()
    if output.exists():
        raise core.ValidationError("OUTPUT_MUST_NOT_ALREADY_EXIST")

    result = run_real(
        Path(args.repo_root).resolve(),
        Path(args.dataset_root).resolve(),
        Path(args.stage_b_result).resolve(),
        Path(args.work_dir).resolve(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(core.canonical_json({
        "contract": CONTRACT,
        "executionSafety": result["executionSafety"],
        "output": str(output),
        "outputSha256": core.sha256_file(output),
        "aggregate": result["aggregate"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeferredRevealError, core.ValidationError) as exc:
        print(f"FLGD_V5_EXTERNAL_VALIDATION_ERROR:{exc}")
        raise SystemExit(2)
