#!/usr/bin/env python3
"""Frozen IDMT-SMT-Guitar external validation harness for Songsterr Fresh V4.

The scoring contract is preregistered in:
docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md

This harness never promotes customer delivery. It validates a hash-bound IDMT
population, invokes the frozen isolated-guitar Basic Pitch path, applies the
frozen V4 temporal-consensus classifier, and evaluates only the preregistered
one-to-one onset/pitch correctness protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

CONTRACT = "songsterr-fresh-idmt-v4-external-validation-v1"
VERSION = 1
BRANCH = "songsterr-fresh-pipeline-v1"

ARCHIVE_FILENAME = "IDMT-SMT-GUITAR_V2.zip"
ARCHIVE_MD5 = "06796e08731bccffaed6ae59361486e4"
ARCHIVE_SHA256 = "02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a"
STAGE_A_REPORT_SHA256 = "fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f"
STAGE_B_RESULT_SHA256 = "dfea0060296ea2289e82041545e8da0f80dd81c5dee6668e8bc7ab08293bbdeb"
INCLUDED_MANIFEST_SHA256 = "0c7946f6ac5af341bcca155a24189c4cd85b9366c0cab3282469ad43236ca344"
INCLUDED_PAIR_COUNT = 568
TOTAL_REFERENCE_EVENT_COUNT = 4661
EXPECTED_DATASET_COUNTS = {"dataset1": 312, "dataset2": 252, "dataset3": 4}

SAMPLE_RATE = 44100
MIN_MIDI = 40
MAX_MIDI = 88
BASIC_PITCH_VERSION = "0.4.0"
NUMPY_VERSION = "1.26.4"
SOUNDFILE_VERSION = "0.13.1"
LIBROSA_VERSION = "0.11.0"
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MINIMUM_NOTE_LENGTH_MS = 127.7

FROZEN_V4_CONTRACT = "songsterr-fresh-temporal-consensus-pitch-corroboration-research-v4"
CLASS_POSITIVE = "independently-corroborated-candidate"
CLASS_NEGATIVE = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"

ONSET_TOLERANCE_SECONDS = 0.050
PITCH_TOLERANCE_CENTS = 50.0
WILSON_Z_ONE_SIDED_95 = 1.6448536269514722
MIN_TOTAL_POSITIVES = 1000
OVERALL_WILSON_LOWER_BOUND_MIN = 0.9900
MANDATORY_DATASET_MIN_POSITIVES = 100
STRATUM_POINT_PRECISION_MIN = 0.9500
SAMPLE_WIDTH_GATE_MIN_POSITIVES = 100

SCORING_PREREG_PATH = "docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_PREREGISTRATION.md"
TRANSCRIBER_PATH = "scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py"
V4_PATH = "scripts/songsterr-fresh/independent_pitch_corroboration_v4.py"


class ValidationError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    if algorithm == "md5":
        digest = hashlib.md5(usedforsecurity=False)
    else:
        digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def hash_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def finite_number(value, label: str) -> float:
    if isinstance(value, bool):
        raise ValidationError(f"{label}:FINITE_NUMBER_REQUIRED")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{label}:FINITE_NUMBER_REQUIRED") from exc
    if not math.isfinite(number):
        raise ValidationError(f"{label}:FINITE_NUMBER_REQUIRED")
    return number


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def child_text_by_local_name(node: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    for child in list(node):
        tag = local_tag(str(child.tag))
        if tag not in out:
            out[tag] = (child.text or "").strip()
    return out


def verify_git_source(repo_root: Path) -> dict:
    def git(*args: str) -> str:
        proc = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            raise ValidationError(f"GIT_COMMAND_FAILED:{' '.join(args)}:{proc.stderr.strip()}")
        return proc.stdout.strip()

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    if branch != BRANCH:
        raise ValidationError(f"BRANCH_CHANGED:{branch}")
    if status:
        raise ValidationError("WORKTREE_MUST_BE_CLEAN")
    return {"branch": branch, "commitSha": commit, "worktreeClean": True}


def package_runtime() -> dict:
    required = {
        "basic-pitch": BASIC_PITCH_VERSION,
        "numpy": NUMPY_VERSION,
        "soundfile": SOUNDFILE_VERSION,
        "librosa": LIBROSA_VERSION,
    }
    actual = {}
    for name, expected in required.items():
        try:
            value = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ValidationError(f"RUNTIME_PACKAGE_MISSING:{name}") from exc
        if value != expected:
            raise ValidationError(f"RUNTIME_PACKAGE_VERSION_CHANGED:{name}:{value}!={expected}")
        actual[name] = value
    if sys.version_info[:2] != (3, 10):
        raise ValidationError(f"PYTHON_VERSION_CHANGED:{platform.python_version()}")
    machine = platform.machine().lower()
    if machine not in {"x86_64", "amd64"}:
        raise ValidationError(f"MACHINE_CHANGED:{platform.machine()}")
    if platform.system() != "Linux":
        raise ValidationError(f"PLATFORM_CHANGED:{platform.system()}")
    return {
        "python": platform.python_version(),
        "pythonImplementation": platform.python_implementation(),
        "pythonExecutable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": actual,
    }


def validate_stage_b_manifest(path: Path) -> dict:
    if hash_file(path) != STAGE_B_RESULT_SHA256:
        raise ValidationError("STAGE_B_RESULT_SHA256_MISMATCH")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError("STAGE_B_RESULT_LOAD_FAILED") from exc
    if payload.get("contract") != "songsterr-fresh-idmt-v4-stage-b-manifest-v1":
        raise ValidationError("STAGE_B_CONTRACT_CHANGED")
    inputs = payload.get("inputs", {})
    expected_inputs = {
        "archiveFilename": ARCHIVE_FILENAME,
        "archiveMd5": ARCHIVE_MD5,
        "archiveSha256": ARCHIVE_SHA256,
        "stageAReportSha256": STAGE_A_REPORT_SHA256,
    }
    for key, expected in expected_inputs.items():
        if inputs.get(key) != expected:
            raise ValidationError(f"STAGE_B_INPUT_IDENTITY_CHANGED:{key}")
    if payload.get("includedManifestSha256") != INCLUDED_MANIFEST_SHA256:
        raise ValidationError("INCLUDED_MANIFEST_SHA256_MISMATCH")
    summary = payload.get("summary", {})
    if summary.get("includedPairCount") != INCLUDED_PAIR_COUNT:
        raise ValidationError("INCLUDED_PAIR_COUNT_CHANGED")
    if summary.get("totalReferenceEventCount") != TOTAL_REFERENCE_EVENT_COUNT:
        raise ValidationError("REFERENCE_EVENT_COUNT_CHANGED")
    if summary.get("includedPairCountByDataset") != EXPECTED_DATASET_COUNTS:
        raise ValidationError("DATASET_PAIR_COUNTS_CHANGED")
    if summary.get("nonIntegerPitchCount") != 0:
        raise ValidationError("NONINTEGER_REFERENCE_PITCH_PRESENT")
    included = payload.get("included")
    if not isinstance(included, list) or len(included) != INCLUDED_PAIR_COUNT:
        raise ValidationError("INCLUDED_ROWS_CHANGED")
    if hash_bytes(canonical_json(included).encode("utf-8")) != INCLUDED_MANIFEST_SHA256:
        raise ValidationError("INCLUDED_ROWS_CANONICAL_HASH_CHANGED")
    boundary = payload.get("policyBoundary", {})
    required_false = (
        "basicPitchInvoked", "v4ClassifierInvoked", "demucsInvoked",
        "estimateReferenceMatchingPerformed", "correctnessMetricComputed",
        "protectedSongUsed", "durationAuthorityChanged", "admissionDecisionMade",
        "modelValidationComplete", "mayAdvanceDelivery",
    )
    if any(boundary.get(key) is not False for key in required_false):
        raise ValidationError("STAGE_B_POLICY_BOUNDARY_CHANGED")
    if boundary.get("customerEligibleEvents") != 0:
        raise ValidationError("STAGE_B_CUSTOMER_ELIGIBILITY_CHANGED")
    return payload


def verify_archive(path: Path) -> None:
    if path.name != ARCHIVE_FILENAME:
        raise ValidationError("ARCHIVE_FILENAME_CHANGED")
    if hash_file(path, "md5") != ARCHIVE_MD5:
        raise ValidationError("ARCHIVE_MD5_MISMATCH")
    if hash_file(path) != ARCHIVE_SHA256:
        raise ValidationError("ARCHIVE_SHA256_MISMATCH")


def load_frozen_v4(repo_root: Path):
    path = repo_root / V4_PATH
    spec = importlib.util.spec_from_file_location("songsterr_frozen_v4", path)
    if spec is None or spec.loader is None:
        raise ValidationError("FROZEN_V4_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.CONTRACT != FROZEN_V4_CONTRACT:
        raise ValidationError("FROZEN_V4_CONTRACT_CHANGED")
    expected = {
        "SAMPLE_RATE": SAMPLE_RATE,
        "WINDOW_SAMPLES": 8192,
        "FFT_SIZE": 32768,
        "PLAYABLE_MIDI_MIN": MIN_MIDI,
        "PLAYABLE_MIDI_MAX": MAX_MIDI,
        "HARMONIC_COUNT_MAX": 6,
        "YIN_TROUGH_THRESHOLD": 0.1,
        "LIBROSA_VERSION": LIBROSA_VERSION,
    }
    for field, value in expected.items():
        if getattr(module, field) != value:
            raise ValidationError(f"FROZEN_V4_CONSTANT_CHANGED:{field}")
    if tuple(module.WINDOW_OFFSETS) != (1024, 7168, 13312):
        raise ValidationError("FROZEN_V4_WINDOW_OFFSETS_CHANGED")
    return module


def load_reference_notes(xml_bytes: bytes, expected_count: int) -> list[dict]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValidationError("REFERENCE_XML_PARSE_FAILED") from exc
    if local_tag(str(root.tag)) != "instrumentRecording":
        raise ValidationError("REFERENCE_XML_ROOT_CHANGED")
    rows = []
    for node in root.iter():
        if local_tag(str(node.tag)) != "event":
            continue
        fields = child_text_by_local_name(node)
        if not {"onsetSec", "pitch"}.issubset(fields):
            raise ValidationError("REFERENCE_REQUIRED_FIELD_MISSING")
        onset = finite_number(fields["onsetSec"], "reference.onsetSec")
        pitch = finite_number(fields["pitch"], "reference.pitch")
        if onset < 0.0:
            raise ValidationError("REFERENCE_ONSET_NEGATIVE")
        if abs(pitch - round(pitch)) > 1e-9:
            raise ValidationError("REFERENCE_PITCH_NONINTEGER")
        rows.append({
            "referenceId": f"reference-note-{len(rows):06d}",
            "onsetSeconds": onset,
            "midi": int(round(pitch)),
        })
    rows.sort(key=lambda row: (row["onsetSeconds"], row["midi"], row["referenceId"]))
    for index, row in enumerate(rows):
        row["referenceId"] = f"reference-note-{index:06d}"
    if len(rows) != expected_count:
        raise ValidationError(f"REFERENCE_EVENT_COUNT_PER_FILE_CHANGED:{len(rows)}!={expected_count}")
    return rows


def validate_basic_pitch_payload(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"BASIC_PITCH_OUTPUT_LOAD_FAILED:{path}") from exc
    if payload.get("contract") != "songsterr-fresh-basic-pitch-isolated-guitar-v1":
        raise ValidationError("BASIC_PITCH_CONTRACT_CHANGED")
    if payload.get("referenceBlind") is not True or payload.get("role") != "guitar":
        raise ValidationError("BASIC_PITCH_REFERENCE_BLIND_ROLE_CHANGED")
    model = payload.get("model", {})
    required = {
        "packageVersion": BASIC_PITCH_VERSION,
        "minimumMidi": MIN_MIDI,
        "maximumMidi": MAX_MIDI,
        "onsetThreshold": ONSET_THRESHOLD,
        "frameThreshold": FRAME_THRESHOLD,
        "minimumNoteLengthMs": MINIMUM_NOTE_LENGTH_MS,
    }
    for field, expected in required.items():
        if model.get(field) != expected:
            raise ValidationError(f"BASIC_PITCH_MODEL_SETTING_CHANGED:{field}")
    diagnostics = payload.get("diagnostics", {})
    if diagnostics.get("modelNoteEndsUsedAsDuration") is not False:
        raise ValidationError("BASIC_PITCH_DURATION_GUARD_CHANGED")
    if diagnostics.get("predictInvocationCount") != 1:
        raise ValidationError("BASIC_PITCH_PREDICT_COUNT_CHANGED")
    notes = payload.get("notes")
    if not isinstance(notes, list):
        raise ValidationError("BASIC_PITCH_NOTES_REQUIRED")
    result = []
    seen = set()
    for index, note in enumerate(notes):
        note_id = note.get("noteId")
        if not isinstance(note_id, str) or not note_id or note_id in seen:
            raise ValidationError(f"BASIC_PITCH_NOTE_ID_INVALID:{index}")
        seen.add(note_id)
        start = finite_number(note.get("startSeconds"), f"notes[{index}].startSeconds")
        midi = note.get("midi")
        if isinstance(midi, bool) or not isinstance(midi, int):
            raise ValidationError(f"BASIC_PITCH_MIDI_INTEGER_REQUIRED:{index}")
        if start < 0.0 or not MIN_MIDI <= midi <= MAX_MIDI:
            raise ValidationError(f"BASIC_PITCH_NOTE_OUT_OF_RANGE:{index}")
        result.append({"noteId": note_id, "startSeconds": start, "midi": midi})
    result.sort(key=lambda row: (row["startSeconds"], row["midi"], row["noteId"]))
    return result


def read_audio(path: Path, expected_header: dict):
    try:
        import numpy as np
        import soundfile as sf
    except Exception as exc:
        raise ValidationError("NUMPY_SOUNDFILE_REQUIRED") from exc
    try:
        audio, sample_rate = sf.read(str(path), dtype="float64", always_2d=True)
    except Exception as exc:
        raise ValidationError(f"AUDIO_READ_FAILED:{path}") from exc
    if int(sample_rate) != SAMPLE_RATE or int(sample_rate) != int(expected_header["sampleRate"]):
        raise ValidationError("AUDIO_SAMPLE_RATE_CHANGED")
    if audio.ndim != 2 or audio.shape[1] != 1 or int(expected_header["channels"]) != 1:
        raise ValidationError("AUDIO_MONO_REQUIRED")
    if int(audio.shape[0]) != int(expected_header["frameCount"]):
        raise ValidationError("AUDIO_FRAME_COUNT_CHANGED")
    mono = np.asarray(audio[:, 0], dtype=np.float64)
    if not np.all(np.isfinite(mono)):
        raise ValidationError("AUDIO_NONFINITE")
    return mono


def classify_events(v4, audio, events: list[dict]) -> tuple[list[dict], dict]:
    counts = {CLASS_POSITIVE: 0, CLASS_NEGATIVE: 0, CLASS_INSUFFICIENT: 0}
    rows = []
    for event in events:
        onset_sample = int(math.floor(event["startSeconds"] * SAMPLE_RATE + 0.5))
        scored = v4.classify_audio_event(audio, onset_sample, int(event["midi"]))
        classification = scored.get("classification")
        if classification not in counts:
            raise ValidationError(f"V4_UNEXPECTED_CLASSIFICATION:{classification}")
        counts[classification] += 1
        rows.append({
            "noteId": event["noteId"],
            "startSeconds": event["startSeconds"],
            "midi": event["midi"],
            "classification": classification,
            "reason": scored.get("reason"),
        })
    before = [(x["noteId"], x["startSeconds"], x["midi"]) for x in events]
    after = [(x["noteId"], x["startSeconds"], x["midi"]) for x in rows]
    if before != after:
        raise ValidationError("EVENT_IDENTITY_CHANGED_DURING_V4")
    return rows, counts


def pitch_delta_cents(midi_a: float, midi_b: float) -> float:
    # Equal-tempered MIDI coordinates differ by exactly 100 cents per semitone.
    return abs(float(midi_a) - float(midi_b)) * 100.0


def valid_match(estimate: dict, reference: dict) -> bool:
    return (
        abs(float(estimate["startSeconds"]) - float(reference["onsetSeconds"])) <= ONSET_TOLERANCE_SECONDS
        and pitch_delta_cents(float(estimate["midi"]), float(reference["midi"])) <= PITCH_TOLERANCE_CENTS
    )


def maximum_cardinality_matches(estimates: list[dict], references: list[dict]) -> dict[int, int]:
    adjacency: list[list[int]] = []
    for estimate in estimates:
        candidates = [i for i, ref in enumerate(references) if valid_match(estimate, ref)]
        candidates.sort(key=lambda i: (
            abs(float(estimate["startSeconds"]) - float(references[i]["onsetSeconds"])),
            pitch_delta_cents(float(estimate["midi"]), float(references[i]["midi"])),
            i,
        ))
        adjacency.append(candidates)

    ref_to_est: dict[int, int] = {}

    def augment(est_index: int, seen_refs: set[int]) -> bool:
        for ref_index in adjacency[est_index]:
            if ref_index in seen_refs:
                continue
            seen_refs.add(ref_index)
            previous = ref_to_est.get(ref_index)
            if previous is None or augment(previous, seen_refs):
                ref_to_est[ref_index] = est_index
                return True
        return False

    for est_index in range(len(estimates)):
        augment(est_index, set())
    return {est_index: ref_index for ref_index, est_index in ref_to_est.items()}


def precision(correct: int, total: int) -> float | None:
    return None if total == 0 else float(correct) / float(total)


def wilson_lower_one_sided_95(correct: int, total: int) -> float | None:
    if total <= 0:
        return None
    p = float(correct) / float(total)
    z = WILSON_Z_ONE_SIDED_95
    n = float(total)
    denominator = 1.0 + z * z / n
    center = p + z * z / (2.0 * n)
    spread = z * math.sqrt((p * (1.0 - p) / n) + (z * z / (4.0 * n * n)))
    return (center - spread) / denominator


def numeric_summary(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "min": None, "median": None, "max": None}
    ordered = sorted(float(x) for x in values)
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": float(statistics.median(ordered)),
        "max": ordered[-1],
    }


def unmatched_diagnostics(estimates: list[dict], references: list[dict], matches: dict[int, int]) -> dict:
    same_pitch_onset = []
    onset_near_pitch = []
    for i, est in enumerate(estimates):
        if i in matches:
            continue
        same_pitch = [
            abs(float(est["startSeconds"]) - float(ref["onsetSeconds"]))
            for ref in references
            if int(est["midi"]) == int(ref["midi"])
        ]
        if same_pitch:
            same_pitch_onset.append(min(same_pitch))
        onset_near = [
            pitch_delta_cents(float(est["midi"]), float(ref["midi"]))
            for ref in references
            if abs(float(est["startSeconds"]) - float(ref["onsetSeconds"])) <= ONSET_TOLERANCE_SECONDS
        ]
        if onset_near:
            onset_near_pitch.append(min(onset_near))
    return {
        "unmatchedEstimateCount": len(estimates) - len(matches),
        "nearestSamePitchOnsetDeltaSeconds": numeric_summary(same_pitch_onset),
        "nearestWithinOnsetPitchDeltaCents": numeric_summary(onset_near_pitch),
    }


def summarize_stratum(rows: list[dict]) -> dict:
    positives = sum(row["positiveCount"] for row in rows)
    correct = sum(row["positiveCorrectCount"] for row in rows)
    return {
        "fileCount": len(rows),
        "positiveCount": positives,
        "positiveCorrectCount": correct,
        "precision": precision(correct, positives),
    }


def evaluate_gates(aggregate: dict) -> dict:
    by_dataset = aggregate["byDataset"]
    by_width = aggregate["bySampleWidthBytes"]
    gates = {
        "allIncludedFilesCompleted": aggregate["completedFileCount"] == INCLUDED_PAIR_COUNT,
        "minimumTotalPositiveEvents": aggregate["positiveEventCount"] >= MIN_TOTAL_POSITIVES,
        "overallWilsonLowerBound": (
            aggregate["positivePrecisionWilsonLowerOneSided95"] is not None
            and aggregate["positivePrecisionWilsonLowerOneSided95"] >= OVERALL_WILSON_LOWER_BOUND_MIN
        ),
        "dataset1": (
            by_dataset.get("dataset1", {}).get("positiveCount", 0) >= MANDATORY_DATASET_MIN_POSITIVES
            and (by_dataset.get("dataset1", {}).get("precision") or 0.0) >= STRATUM_POINT_PRECISION_MIN
        ),
        "dataset2": (
            by_dataset.get("dataset2", {}).get("positiveCount", 0) >= MANDATORY_DATASET_MIN_POSITIVES
            and (by_dataset.get("dataset2", {}).get("precision") or 0.0) >= STRATUM_POINT_PRECISION_MIN
        ),
    }
    for width, row in sorted(by_width.items()):
        key = f"sampleWidthBytes{width}"
        if row["positiveCount"] >= SAMPLE_WIDTH_GATE_MIN_POSITIVES:
            gates[key] = row["precision"] is not None and row["precision"] >= STRATUM_POINT_PRECISION_MIN
        else:
            gates[key] = True
    return gates


def safe_member_path(root: Path, member_name: str) -> Path:
    pure = PurePosixPath(member_name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValidationError(f"ZIP_PATH_UNSAFE:{member_name}")
    target = root.joinpath(*pure.parts)
    root_abs = root.absolute()
    target_abs = target.absolute()
    if root_abs != target_abs and root_abs not in target_abs.parents:
        raise ValidationError(f"ZIP_PATH_UNSAFE:{member_name}")
    return target


def extract_member(zf: zipfile.ZipFile, name: str, root: Path, expected_sha: str) -> Path:
    target = safe_member_path(root, name)
    if target.exists():
        raise ValidationError(f"EXTRACT_TARGET_ALREADY_EXISTS:{target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(name, "r") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    if hash_file(target) != expected_sha:
        raise ValidationError(f"EXTRACTED_MEMBER_SHA256_MISMATCH:{name}")
    return target


def run_transcriber(repo_root: Path, audio_path: Path, output_path: Path, log_path: Path, row: dict) -> None:
    # Preserve the invoking interpreter path exactly; do not realpath/resolve it.
    python_executable = sys.executable
    command = [
        python_executable,
        str(repo_root / TRANSCRIBER_PATH),
        "--input", str(audio_path),
        "--output", str(output_path),
        "--audio-source", f"idmt-v4:{row['wavSha256']}",
        "--separation-source", "idmt-direct-isolated-guitar-no-demucs",
        "--minimum-midi", str(MIN_MIDI),
        "--maximum-midi", str(MAX_MIDI),
        "--onset-threshold", str(ONSET_THRESHOLD),
        "--frame-threshold", str(FRAME_THRESHOLD),
        "--minimum-note-length-ms", str(MINIMUM_NOTE_LENGTH_MS),
    ]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(command, cwd=repo_root, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    if proc.returncode != 0:
        raise ValidationError(f"BASIC_PITCH_SUBPROCESS_FAILED:{row['stem']}:exit={proc.returncode}:log={log_path}")
    if not output_path.is_file():
        raise ValidationError(f"BASIC_PITCH_OUTPUT_MISSING:{row['stem']}")


def validate_one_file(repo_root: Path, v4, zf: zipfile.ZipFile, row: dict, index: int, work_dir: Path) -> dict:
    extracted_root = work_dir / "extracted"
    inference_root = work_dir / "inference"
    audio_path = extract_member(zf, row["wav"], extracted_root, row["wavSha256"])
    xml_path = extract_member(zf, row["xml"], extracted_root, row["xmlSha256"])

    references = load_reference_notes(xml_path.read_bytes(), int(row["referenceEventCount"]))
    audio = read_audio(audio_path, row["wavHeader"])

    inference_json = inference_root / f"track-{index:04d}.json"
    inference_log = inference_root / f"track-{index:04d}.log"
    if inference_json.exists() or inference_log.exists():
        raise ValidationError(f"INFERENCE_OUTPUT_ALREADY_EXISTS:{index}")
    run_transcriber(repo_root, audio_path, inference_json, inference_log, row)
    events = validate_basic_pitch_payload(inference_json)
    classified, class_counts = classify_events(v4, audio, events)
    positives = [x for x in classified if x["classification"] == CLASS_POSITIVE]

    positive_matches = maximum_cardinality_matches(positives, references)
    baseline_matches = maximum_cardinality_matches(events, references)

    return {
        "index": index,
        "stem": row["stem"],
        "dataset": row["dataset"],
        "wav": row["wav"],
        "xml": row["xml"],
        "wavSha256": row["wavSha256"],
        "xmlSha256": row["xmlSha256"],
        "sampleWidthBytes": int(row["wavHeader"]["sampleWidthBytes"]),
        "referenceEventCount": len(references),
        "decodedEventCount": len(events),
        "classificationCounts": class_counts,
        "positiveCount": len(positives),
        "positiveCorrectCount": len(positive_matches),
        "positivePrecision": precision(len(positive_matches), len(positives)),
        "baselineCorrectCount": len(baseline_matches),
        "baselinePrecision": precision(len(baseline_matches), len(events)),
        "positiveRecall": float(len(positive_matches)) / float(len(references)) if references else None,
        "unmatchedPositiveDiagnostics": unmatched_diagnostics(positives, references, positive_matches),
        "inferenceOutputSha256": hash_file(inference_json),
        "eventIdentitySha256": hash_bytes(canonical_json([
            {"noteId": x["noteId"], "startSeconds": x["startSeconds"], "midi": x["midi"]}
            for x in events
        ]).encode("utf-8")),
    }


def aggregate_results(tracks: list[dict]) -> dict:
    by_dataset_rows: dict[str, list[dict]] = defaultdict(list)
    by_width_rows: dict[str, list[dict]] = defaultdict(list)
    class_counts = Counter()
    decoded = 0
    references = 0
    positives = 0
    positive_correct = 0
    baseline_correct = 0

    for row in tracks:
        by_dataset_rows[row["dataset"]].append(row)
        by_width_rows[str(row["sampleWidthBytes"])].append(row)
        class_counts.update(row["classificationCounts"])
        decoded += row["decodedEventCount"]
        references += row["referenceEventCount"]
        positives += row["positiveCount"]
        positive_correct += row["positiveCorrectCount"]
        baseline_correct += row["baselineCorrectCount"]

    if references != TOTAL_REFERENCE_EVENT_COUNT:
        raise ValidationError(f"AGGREGATE_REFERENCE_COUNT_CHANGED:{references}")
    if sum(class_counts.values()) != decoded:
        raise ValidationError("AGGREGATE_CLASS_COUNTS_DO_NOT_PRESERVE_EVENTS")

    by_dataset = {key: summarize_stratum(value) for key, value in sorted(by_dataset_rows.items())}
    by_width = {key: summarize_stratum(value) for key, value in sorted(by_width_rows.items())}
    result = {
        "completedFileCount": len(tracks),
        "referenceEventCount": references,
        "decodedEventCount": decoded,
        "classificationCounts": dict(sorted(class_counts.items())),
        "positiveEventCount": positives,
        "positiveCorrectCount": positive_correct,
        "positivePrecision": precision(positive_correct, positives),
        "positivePrecisionWilsonLowerOneSided95": wilson_lower_one_sided_95(positive_correct, positives),
        "baselineCorrectCount": baseline_correct,
        "baselinePrecision": precision(baseline_correct, decoded),
        "positiveRecall": float(positive_correct) / float(references) if references else None,
        "byDataset": by_dataset,
        "bySampleWidthBytes": by_width,
    }
    result["gates"] = evaluate_gates(result)
    result["externalValidationPassed"] = all(result["gates"].values())
    return result


def implementation_hashes(repo_root: Path) -> dict:
    paths = [
        TRANSCRIBER_PATH,
        V4_PATH,
        "scripts/songsterr-fresh/external_idmt_v4_validation.py",
        SCORING_PREREG_PATH,
    ]
    return {path: hash_file(repo_root / path) for path in paths}


def run_official(args: argparse.Namespace) -> dict:
    repo_root = Path(args.repo_root).absolute()
    archive = Path(args.archive).absolute()
    manifest_path = Path(args.stage_b_manifest).absolute()
    work_dir = Path(args.work_dir).absolute()
    output = Path(args.output).absolute()

    if output.exists():
        raise ValidationError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    if work_dir.exists():
        raise ValidationError("WORK_DIR_MUST_NOT_ALREADY_EXIST")
    if not repo_root.is_dir() or not archive.is_file() or not manifest_path.is_file():
        raise ValidationError("REQUIRED_INPUT_MISSING")

    source = verify_git_source(repo_root)
    runtime = package_runtime()
    verify_archive(archive)
    manifest = validate_stage_b_manifest(manifest_path)
    v4 = load_frozen_v4(repo_root)

    work_dir.mkdir(parents=True, exist_ok=False)
    tracks = []
    with zipfile.ZipFile(archive, "r") as zf:
        names = set(zf.namelist())
        for index, row in enumerate(manifest["included"], start=1):
            if row["wav"] not in names or row["xml"] not in names:
                raise ValidationError(f"INCLUDED_MEMBER_MISSING:{row['stem']}")
            print(f"IDMT_V4_TRACK_START {index}/{INCLUDED_PAIR_COUNT} {row['stem']}", flush=True)
            result = validate_one_file(repo_root, v4, zf, row, index, work_dir)
            tracks.append(result)
            print(
                f"IDMT_V4_TRACK_COMPLETE {index}/{INCLUDED_PAIR_COUNT} "
                f"decoded={result['decodedEventCount']} positive={result['positiveCount']} "
                f"correct={result['positiveCorrectCount']}",
                flush=True,
            )

    aggregate = aggregate_results(tracks)
    source_after = verify_git_source(repo_root)
    if source_after != source:
        raise ValidationError("SOURCE_CHANGED_DURING_EXECUTION")

    payload = {
        "contract": CONTRACT,
        "version": VERSION,
        "dataset": {
            "name": "IDMT-SMT-Guitar Dataset",
            "version": "1.0.0",
            "doi": "10.5281/zenodo.7544110",
            "archiveFilename": ARCHIVE_FILENAME,
            "archiveMd5": ARCHIVE_MD5,
            "archiveSha256": ARCHIVE_SHA256,
            "stageAReportSha256": STAGE_A_REPORT_SHA256,
            "stageBManifestResultSha256": STAGE_B_RESULT_SHA256,
            "includedManifestSha256": INCLUDED_MANIFEST_SHA256,
            "includedFileCount": INCLUDED_PAIR_COUNT,
        },
        "source": source,
        "runtime": runtime,
        "implementationSha256": implementation_hashes(repo_root),
        "matching": {
            "method": "per-file-one-to-one-maximum-cardinality-bipartite",
            "onsetToleranceSecondsInclusive": ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCentsInclusive": PITCH_TOLERANCE_CENTS,
            "offsetsIgnored": True,
        },
        "gates": {
            "minimumTotalPositiveEvents": MIN_TOTAL_POSITIVES,
            "overallWilsonLowerBoundMinimum": OVERALL_WILSON_LOWER_BOUND_MIN,
            "mandatoryDatasetMinimumPositives": MANDATORY_DATASET_MIN_POSITIVES,
            "stratumPointPrecisionMinimum": STRATUM_POINT_PRECISION_MIN,
            "sampleWidthGateMinimumPositives": SAMPLE_WIDTH_GATE_MIN_POSITIVES,
            "dataset3StandaloneGate": False,
        },
        "tracks": tracks,
        "aggregate": aggregate,
        "policyBoundary": {
            "externalValidationPassed": aggregate["externalValidationPassed"],
            "separatePolicyReviewRequired": True,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "protectedSongUsed": False,
            "demucsInvoked": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "aggregate": aggregate,
        "policyBoundary": payload["policyBoundary"],
    }), flush=True)
    return payload


def run_self_test() -> dict:
    assert valid_match({"startSeconds": 1.0, "midi": 60}, {"onsetSeconds": 1.05, "midi": 60})
    assert not valid_match({"startSeconds": 1.0, "midi": 60}, {"onsetSeconds": 1.051, "midi": 60})
    assert not valid_match({"startSeconds": 1.0, "midi": 60}, {"onsetSeconds": 1.0, "midi": 61})
    estimates = [
        {"startSeconds": 1.000, "midi": 60},
        {"startSeconds": 1.010, "midi": 60},
        {"startSeconds": 2.000, "midi": 64},
    ]
    references = [
        {"onsetSeconds": 1.005, "midi": 60},
        {"onsetSeconds": 2.020, "midi": 64},
    ]
    matches = maximum_cardinality_matches(estimates, references)
    assert len(matches) == 2
    assert 0.0 < wilson_lower_one_sided_95(100, 100) < 1.0
    assert wilson_lower_one_sided_95(0, 100) == 0.0
    synthetic = {
        "completedFileCount": INCLUDED_PAIR_COUNT,
        "positiveEventCount": 1200,
        "positivePrecisionWilsonLowerOneSided95": 0.995,
        "byDataset": {
            "dataset1": {"positiveCount": 500, "precision": 0.99},
            "dataset2": {"positiveCount": 600, "precision": 0.98},
            "dataset3": {"positiveCount": 100, "precision": 0.10},
        },
        "bySampleWidthBytes": {
            "2": {"positiveCount": 1100, "precision": 0.99},
            "3": {"positiveCount": 100, "precision": 0.96},
        },
    }
    gates = evaluate_gates(synthetic)
    assert all(gates.values())
    synthetic["byDataset"]["dataset2"]["precision"] = 0.94
    assert evaluate_gates(synthetic)["dataset2"] is False
    return {
        "contract": CONTRACT,
        "selfTest": "PASS",
        "matching": {
            "onsetToleranceSecondsInclusive": ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCentsInclusive": PITCH_TOLERANCE_CENTS,
        },
        "gates": {
            "minimumTotalPositiveEvents": MIN_TOTAL_POSITIVES,
            "overallWilsonLowerBoundMinimum": OVERALL_WILSON_LOWER_BOUND_MIN,
            "mandatoryDatasetMinimumPositives": MANDATORY_DATASET_MIN_POSITIVES,
            "stratumPointPrecisionMinimum": STRATUM_POINT_PRECISION_MIN,
        },
        "policyBoundary": {
            "realIdmtEvaluated": False,
            "basicPitchInvoked": False,
            "v4ClassifierInvoked": False,
            "correctnessMetricOnRealCorpusComputed": False,
            "protectedSongUsed": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--archive")
    parser.add_argument("--stage-b-manifest")
    parser.add_argument("--work-dir")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(canonical_json(run_self_test()))
        return 0
    if not all((args.archive, args.stage_b_manifest, args.work_dir, args.output)):
        raise ValidationError("OFFICIAL_MODE_REQUIRES_ARCHIVE_MANIFEST_WORKDIR_OUTPUT")
    run_official(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"IDMT_V4_EXTERNAL_VALIDATION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
