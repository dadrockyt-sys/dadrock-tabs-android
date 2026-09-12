#!/usr/bin/env python3
"""Frozen FLGD external-validation harness for Songsterr Fresh V5.

The correctness protocol is preregistered in
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`
and its inclusive numerical boundary is frozen in
`docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`.

`--self-test` is synthetic/contract-only and performs no model inference.
Real mode requires an exact FLGD checkout plus the immutable Stage B JSON.
The harness never promotes customer delivery; a separate policy review is
mandatory even if every external-validation gate passes.
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
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-flgd-v5-external-validation-v1"
VERSION = 1
BRANCH = "songsterr-fresh-pipeline-v1"

EXPECTED_DATASET_ORIGIN = "https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset"
EXPECTED_DATASET_REVISION = "a38306c244b3ea81496ad58b4514622185e58211"
EXPECTED_STAGE_A_REPORT_SHA256 = "f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3"
EXPECTED_STAGE_B_REPORT_SHA256 = "065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e"
EXPECTED_INCLUDED_POPULATION_SHA256 = "def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02"
EXPECTED_REFERENCE_IDENTITY_SHA256 = "e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a"
EXPECTED_IGNORED_RELEASE_IDENTITY_SHA256 = "8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3"
EXPECTED_EDGE_AUDIT_REPORT_SHA256 = "111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24"
EXPECTED_PERFORMANCE_COUNT = 79
EXPECTED_REFERENCE_EVENT_COUNT = 76392
EXPECTED_IGNORED_RELEASE_COUNT = 24
EXPECTED_SPLIT_COUNTS = {"test": 9, "train": 62, "validate": 8}
EXPECTED_GUITAR_TYPE_COUNTS = {
    "acoustic": 3,
    "electric": 35,
    "electric-band": 1,
    "nylon": 40,
}

SAMPLE_RATE = 44100
MIN_MIDI = 40
MAX_MIDI = 88
BASIC_PITCH_VERSION = "0.4.0"
NUMPY_VERSION = "1.26.4"
SCIPY_VERSION = "1.15.3"
LIBROSA_VERSION = "0.11.0"
SOUNDFILE_VERSION = "0.13.1"
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MINIMUM_NOTE_LENGTH_MS = 127.7
SEPARATION_SOURCE = "flgd-direct-solo-guitar-no-demucs"

FROZEN_V5_CONTRACT = "songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5"
CLASS_POSITIVE = "independently-corroborated-candidate"
CLASS_NEGATIVE = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"
CLASSIFICATIONS = (CLASS_POSITIVE, CLASS_NEGATIVE, CLASS_INSUFFICIENT)

ONSET_TOLERANCE_SECONDS = 0.050
PITCH_TOLERANCE_CENTS = 50.0
INCLUSIVE_ABS_TOL = 1e-12
WILSON_Z_ONE_SIDED_95 = 1.6448536269514722
MIN_TOTAL_POSITIVES = 1000
OVERALL_WILSON_LOWER_BOUND_MIN = 0.9900
STRATUM_MIN_POSITIVES = 100
STRATUM_POINT_PRECISION_MIN = 0.9500

SCORING_PREREG_PATH = "docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md"
NUMERICAL_AMENDMENT_PATH = "docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md"
TRANSCRIBER_PATH = "scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py"
V5_PATH = "scripts/songsterr-fresh/independent_pitch_corroboration_v5.py"
STAGE_B_ADAPTER_PATH = "scripts/songsterr-fresh/prepare_flgd_v5_stage_b_manifest_amended.py"

# Exact Git blob identities of pre-existing frozen implementations.  Source
# commit cleanliness additionally binds this harness and its preregistration.
TRANSCRIBER_GIT_BLOB = "e9137496363f14cbe6194e32304c8b17b0b6569c"
V5_GIT_BLOB = "4532d60ed43bf0cdf5878785c09df4006df37b29"
STAGE_B_ADAPTER_GIT_BLOB = "ecc6eaed2397b42b8e68a40f4bff1ce3c137fc8e"


class ValidationError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


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


def git_output(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise ValidationError(f"GIT_COMMAND_FAILED:{' '.join(args)}:{proc.stderr.strip()}")
    return proc.stdout.strip()


def normalize_origin(value: str) -> str:
    text = str(value).strip().rstrip("/")
    return text[:-4] if text.endswith(".git") else text


def verify_repo_source(repo_root: Path) -> dict:
    branch = git_output(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    commit = git_output(repo_root, "rev-parse", "HEAD")
    if branch != BRANCH:
        raise ValidationError(f"SOURCE_BRANCH_CHANGED:{branch}")
    if git_output(repo_root, "status", "--porcelain"):
        raise ValidationError("SOURCE_WORKTREE_MUST_BE_CLEAN")

    expected_blobs = {
        TRANSCRIBER_PATH: TRANSCRIBER_GIT_BLOB,
        V5_PATH: V5_GIT_BLOB,
        STAGE_B_ADAPTER_PATH: STAGE_B_ADAPTER_GIT_BLOB,
    }
    actual_blobs = {}
    for rel, expected in expected_blobs.items():
        actual = git_output(repo_root, "hash-object", rel)
        if actual != expected:
            raise ValidationError(f"FROZEN_IMPLEMENTATION_BLOB_CHANGED:{rel}:{actual}!={expected}")
        actual_blobs[rel] = actual

    for rel in (SCORING_PREREG_PATH, NUMERICAL_AMENDMENT_PATH):
        if not (repo_root / rel).is_file():
            raise ValidationError(f"FROZEN_POLICY_FILE_MISSING:{rel}")

    return {
        "branch": branch,
        "commitSha": commit,
        "worktreeClean": True,
        "frozenImplementationGitBlobs": actual_blobs,
        "scoringPreregistrationSha256": sha256_file(repo_root / SCORING_PREREG_PATH),
        "numericalAmendmentSha256": sha256_file(repo_root / NUMERICAL_AMENDMENT_PATH),
    }


def verify_dataset_source(dataset_root: Path) -> dict:
    if not (dataset_root / ".git").exists():
        raise ValidationError("FLGD_GIT_CHECKOUT_REQUIRED")
    head = git_output(dataset_root, "rev-parse", "HEAD")
    if head != EXPECTED_DATASET_REVISION:
        raise ValidationError(f"FLGD_REVISION_CHANGED:{head}!={EXPECTED_DATASET_REVISION}")
    if git_output(dataset_root, "status", "--porcelain"):
        raise ValidationError("FLGD_WORKTREE_MUST_BE_CLEAN")
    origin = git_output(dataset_root, "remote", "get-url", "origin")
    canonical = normalize_origin(origin)
    if canonical != EXPECTED_DATASET_ORIGIN:
        raise ValidationError(f"FLGD_ORIGIN_CHANGED:{canonical}")
    return {
        "headSha": head,
        "originCanonical": canonical,
        "worktreeClean": True,
    }


def package_runtime() -> dict:
    required = {
        "basic-pitch": BASIC_PITCH_VERSION,
        "numpy": NUMPY_VERSION,
        "scipy": SCIPY_VERSION,
        "librosa": LIBROSA_VERSION,
        "soundfile": SOUNDFILE_VERSION,
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
    if platform.system() != "Linux":
        raise ValidationError(f"PLATFORM_CHANGED:{platform.system()}")
    machine = platform.machine().lower()
    if machine not in {"x86_64", "amd64"}:
        raise ValidationError(f"MACHINE_CHANGED:{platform.machine()}")
    return {
        "python": platform.python_version(),
        "pythonImplementation": platform.python_implementation(),
        "pythonExecutable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": actual,
    }


def _required_false_boundary(boundary: dict, *, label: str) -> None:
    required_false = (
        "basicPitchInvoked",
        "v5ClassifierInvoked",
        "demucsInvoked",
        "audioSamplesUsedForPitchAnalysis",
        "estimateReferenceMatchingPerformed",
        "correctnessMetricComputed",
        "protectedSongUsed",
        "modelValidationComplete",
        "mayAdvanceDelivery",
        "durationAuthorityChanged",
    )
    for key in required_false:
        if boundary.get(key) is not False:
            raise ValidationError(f"{label}_POLICY_BOUNDARY_CHANGED:{key}")
    if boundary.get("customerEligibleEvents") != 0:
        raise ValidationError(f"{label}_CUSTOMER_ELIGIBILITY_CHANGED")


def validate_stage_b_report(path: Path) -> dict:
    actual_sha = sha256_file(path)
    if actual_sha != EXPECTED_STAGE_B_REPORT_SHA256:
        raise ValidationError(f"STAGE_B_REPORT_SHA256_CHANGED:{actual_sha}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError("STAGE_B_REPORT_LOAD_FAILED") from exc

    if payload.get("contract") != "songsterr-fresh-flgd-v5-stage-b-manifest-pairing-amended-v1":
        raise ValidationError("STAGE_B_CONTRACT_CHANGED")
    dataset = payload.get("dataset", {})
    if dataset.get("expectedOriginCanonical") != EXPECTED_DATASET_ORIGIN:
        raise ValidationError("STAGE_B_DATASET_ORIGIN_CHANGED")
    if dataset.get("expectedRevision") != EXPECTED_DATASET_REVISION:
        raise ValidationError("STAGE_B_DATASET_REVISION_CHANGED")
    if dataset.get("stageAReportSha256") != EXPECTED_STAGE_A_REPORT_SHA256:
        raise ValidationError("STAGE_B_STAGE_A_IDENTITY_CHANGED")
    if dataset.get("midiEdgeAuditReportSha256") != EXPECTED_EDGE_AUDIT_REPORT_SHA256:
        raise ValidationError("STAGE_B_EDGE_AUDIT_IDENTITY_CHANGED")

    if payload.get("includedPopulationSha256") != EXPECTED_INCLUDED_POPULATION_SHA256:
        raise ValidationError("STAGE_B_POPULATION_IDENTITY_CHANGED")
    if payload.get("referenceEventIdentitySha256") != EXPECTED_REFERENCE_IDENTITY_SHA256:
        raise ValidationError("STAGE_B_REFERENCE_IDENTITY_CHANGED")
    if payload.get("ignoredDuplicateReleaseIdentitySha256") != EXPECTED_IGNORED_RELEASE_IDENTITY_SHA256:
        raise ValidationError("STAGE_B_IGNORED_RELEASE_IDENTITY_CHANGED")

    summary = payload.get("summary", {})
    expected_summary = {
        "includedPerformanceCount": EXPECTED_PERFORMANCE_COUNT,
        "referenceEventCount": EXPECTED_REFERENCE_EVENT_COUNT,
        "ignoredDuplicateReleaseCount": EXPECTED_IGNORED_RELEASE_COUNT,
        "splitCounts": EXPECTED_SPLIT_COUNTS,
        "guitarTypeCounts": EXPECTED_GUITAR_TYPE_COUNTS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise ValidationError(f"STAGE_B_SUMMARY_CHANGED:{key}:{summary.get(key)}!={expected}")

    rows = payload.get("included")
    if not isinstance(rows, list) or len(rows) != EXPECTED_PERFORMANCE_COUNT:
        raise ValidationError("STAGE_B_INCLUDED_ROWS_CHANGED")
    if len({row.get("stem") for row in rows}) != EXPECTED_PERFORMANCE_COUNT:
        raise ValidationError("STAGE_B_STEMS_NOT_UNIQUE")
    _required_false_boundary(payload.get("policyBoundary", {}), label="STAGE_B")
    return payload


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValidationError(f"MODULE_IMPORT_SPEC_FAILED:{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_frozen_v5(repo_root: Path):
    module = load_module(repo_root / V5_PATH, "songsterr_frozen_v5")
    if module.CONTRACT != FROZEN_V5_CONTRACT:
        raise ValidationError("FROZEN_V5_CONTRACT_CHANGED")
    expected = {
        "SAMPLE_RATE": SAMPLE_RATE,
        "WINDOW_SAMPLES": 8192,
        "FFT_SIZE": 32768,
        "PLAYABLE_MIDI_MIN": MIN_MIDI,
        "PLAYABLE_MIDI_MAX": MAX_MIDI,
        "HARMONIC_COUNT_MAX": 8,
        "MIN_DEMEANED_RMS": 1e-4,
        "NECESSITY_FRACTION_MIN": 0.01,
        "FUNDAMENTAL_TO_MAX_HARMONIC_MIN": 0.05,
        "NUMPY_VERSION": NUMPY_VERSION,
        "SCIPY_VERSION": SCIPY_VERSION,
    }
    for field, value in expected.items():
        if getattr(module, field) != value:
            raise ValidationError(f"FROZEN_V5_CONSTANT_CHANGED:{field}")
    if tuple(module.WINDOW_OFFSETS) != (2048, 8192, 14336):
        raise ValidationError("FROZEN_V5_WINDOW_OFFSETS_CHANGED")
    return module


def load_stage_b_adapter(repo_root: Path):
    module = load_module(repo_root / STAGE_B_ADAPTER_PATH, "songsterr_stage_b_adapter")
    if module.CONTRACT != "songsterr-fresh-flgd-v5-stage-b-manifest-pairing-amended-v1":
        raise ValidationError("STAGE_B_ADAPTER_CONTRACT_CHANGED")
    return module


def reconstruct_references(adapter, dataset_root: Path, stage_b: dict) -> dict[str, list[dict]]:
    by_stem: dict[str, list[dict]] = {}
    global_identities = []
    global_ignored = []
    total = 0

    for row in stage_b["included"]:
        stem = row.get("stem")
        midi = row.get("midi", {})
        midi_rel = midi.get("path")
        if not isinstance(stem, str) or not stem or not isinstance(midi_rel, str):
            raise ValidationError("STAGE_B_ROW_REFERENCE_IDENTITY_INVALID")
        midi_path = dataset_root / midi_rel
        if not midi_path.is_file() or midi_path.is_symlink():
            raise ValidationError(f"REFERENCE_MIDI_FILE_INVALID:{midi_rel}")
        if sha256_file(midi_path) != midi.get("sha256"):
            raise ValidationError(f"REFERENCE_MIDI_SHA256_CHANGED:{stem}")

        parsed = adapter.inspect_reference_midi_amended(midi_path, stem)
        identities = list(parsed.pop("_identities"))
        ignored = list(parsed.pop("_ignoredDuplicateReleases"))
        if len(identities) != midi.get("referenceEventCount"):
            raise ValidationError(f"REFERENCE_EVENT_COUNT_CHANGED:{stem}")
        if parsed.get("referenceEventIdentitySha256") != midi.get("referenceEventIdentitySha256"):
            raise ValidationError(f"REFERENCE_EVENT_IDENTITY_CHANGED:{stem}")
        if parsed.get("ignoredDuplicateReleaseCount") != midi.get("ignoredDuplicateReleaseCount", 0):
            raise ValidationError(f"IGNORED_RELEASE_COUNT_CHANGED:{stem}")
        if parsed.get("ignoredDuplicateReleaseIdentitySha256") != midi.get("ignoredDuplicateReleaseIdentitySha256"):
            raise ValidationError(f"IGNORED_RELEASE_IDENTITY_CHANGED:{stem}")

        refs = []
        for identity in identities:
            refs.append({
                "referenceId": f"{stem}:reference-{int(identity['eventOrdinal']):06d}",
                "onsetSeconds": finite_number(identity["onsetSeconds"], "reference.onsetSeconds"),
                "midi": int(identity["midi"]),
            })
        by_stem[stem] = refs
        global_identities.extend(identities)
        global_ignored.extend([{"stem": stem, "midiPath": midi_rel, **edge} for edge in ignored])
        total += len(refs)

    if total != EXPECTED_REFERENCE_EVENT_COUNT:
        raise ValidationError(f"RECONSTRUCTED_REFERENCE_COUNT_CHANGED:{total}")
    if sha256_bytes(canonical_json(global_identities).encode("utf-8")) != EXPECTED_REFERENCE_IDENTITY_SHA256:
        raise ValidationError("RECONSTRUCTED_GLOBAL_REFERENCE_IDENTITY_CHANGED")
    if sha256_bytes(canonical_json(global_ignored).encode("utf-8")) != EXPECTED_IGNORED_RELEASE_IDENTITY_SHA256:
        raise ValidationError("RECONSTRUCTED_GLOBAL_IGNORED_RELEASE_IDENTITY_CHANGED")
    return by_stem


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
    for key, expected in required.items():
        if model.get(key) != expected:
            raise ValidationError(f"BASIC_PITCH_SETTING_CHANGED:{key}")

    diagnostics = payload.get("diagnostics", {})
    if diagnostics.get("modelNoteEndsUsedAsDuration") is not False:
        raise ValidationError("BASIC_PITCH_DURATION_GUARD_CHANGED")
    if diagnostics.get("predictInvocationCount") != 1:
        raise ValidationError("BASIC_PITCH_PREDICT_COUNT_CHANGED")
    provenance = payload.get("provenance", {})
    if provenance.get("gpuInvoked") is not False:
        raise ValidationError("BASIC_PITCH_GPU_INVOKED")
    if provenance.get("separationSource") != SEPARATION_SOURCE:
        raise ValidationError("BASIC_PITCH_SEPARATION_SOURCE_CHANGED")

    notes = payload.get("notes")
    if not isinstance(notes, list):
        raise ValidationError("BASIC_PITCH_NOTES_REQUIRED")
    seen = set()
    result = []
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


def canonicalize_audio(source_mp3: Path, output_wav: Path) -> tuple[object, dict]:
    try:
        import librosa
        import numpy as np
        import soundfile as sf
    except Exception as exc:
        raise ValidationError("AUDIO_RUNTIME_IMPORT_FAILED") from exc

    try:
        decoded, sample_rate = librosa.load(
            str(source_mp3), sr=SAMPLE_RATE, mono=True, dtype=np.float32
        )
    except Exception as exc:
        raise ValidationError(f"AUDIO_DECODE_FAILED:{source_mp3}") from exc
    decoded = np.asarray(decoded, dtype=np.float32)
    if int(sample_rate) != SAMPLE_RATE or decoded.ndim != 1 or decoded.size == 0:
        raise ValidationError("CANONICAL_AUDIO_SHAPE_CHANGED")
    if not np.all(np.isfinite(decoded)):
        raise ValidationError("CANONICAL_AUDIO_NONFINITE")
    if output_wav.exists():
        raise ValidationError(f"CANONICAL_WAV_ALREADY_EXISTS:{output_wav}")
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_wav), decoded, SAMPLE_RATE, subtype="FLOAT", format="WAV")
    reread, reread_rate = sf.read(str(output_wav), dtype="float64", always_2d=False)
    reread = np.asarray(reread, dtype=np.float64)
    if int(reread_rate) != SAMPLE_RATE or reread.ndim != 1 or reread.size != decoded.size:
        raise ValidationError("CANONICAL_WAV_REREAD_SHAPE_CHANGED")
    if not np.all(np.isfinite(reread)):
        raise ValidationError("CANONICAL_WAV_REREAD_NONFINITE")
    return reread, {
        "sampleRate": SAMPLE_RATE,
        "sampleCount": int(reread.size),
        "durationSeconds": float(reread.size) / float(SAMPLE_RATE),
        "wavSha256": sha256_file(output_wav),
        "wavSubtype": "FLOAT",
    }


def run_transcriber(
    repo_root: Path,
    canonical_wav: Path,
    output_json: Path,
    output_log: Path,
    source_audio_sha256: str,
) -> None:
    command = [
        sys.executable,
        str(repo_root / TRANSCRIBER_PATH),
        "--input", str(canonical_wav),
        "--output", str(output_json),
        "--audio-source", f"flgd-v5:{source_audio_sha256}",
        "--separation-source", SEPARATION_SOURCE,
        "--minimum-midi", str(MIN_MIDI),
        "--maximum-midi", str(MAX_MIDI),
        "--onset-threshold", str(ONSET_THRESHOLD),
        "--frame-threshold", str(FRAME_THRESHOLD),
        "--minimum-note-length-ms", str(MINIMUM_NOTE_LENGTH_MS),
    ]
    output_log.parent.mkdir(parents=True, exist_ok=True)
    with output_log.open("w", encoding="utf-8") as log:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
            env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
        )
    if proc.returncode != 0:
        raise ValidationError(f"BASIC_PITCH_SUBPROCESS_FAILED:exit={proc.returncode}:log={output_log}")
    if not output_json.is_file():
        raise ValidationError("BASIC_PITCH_OUTPUT_MISSING")


def classify_events(v5, audio, events: list[dict]) -> tuple[list[dict], dict[str, int]]:
    counts = {name: 0 for name in CLASSIFICATIONS}
    rows = []
    before = [(row["noteId"], row["startSeconds"], row["midi"]) for row in events]
    for event in events:
        onset_sample = int(math.floor(float(event["startSeconds"]) * SAMPLE_RATE + 0.5))
        scored = v5.classify_audio_event(audio, onset_sample, int(event["midi"]))
        classification = scored.get("classification")
        if classification not in counts:
            raise ValidationError(f"V5_UNEXPECTED_CLASSIFICATION:{classification}")
        counts[classification] += 1
        rows.append({
            "noteId": event["noteId"],
            "startSeconds": event["startSeconds"],
            "midi": event["midi"],
            "classification": classification,
            "reason": scored.get("reason"),
        })
    after = [(row["noteId"], row["startSeconds"], row["midi"]) for row in rows]
    if before != after:
        raise ValidationError("EVENT_IDENTITY_CHANGED_DURING_V5")
    if sum(counts.values()) != len(events):
        raise ValidationError("V5_CLASSIFICATION_COUNT_MISMATCH")
    return rows, counts


def inclusive_at_limit(delta: float, limit: float) -> bool:
    value = abs(float(delta))
    return value < float(limit) or math.isclose(
        value, float(limit), rel_tol=0.0, abs_tol=INCLUSIVE_ABS_TOL
    )


def pitch_delta_cents(midi_a: float, midi_b: float) -> float:
    return abs(float(midi_a) - float(midi_b)) * 100.0


def valid_match(estimate: dict, reference: dict) -> bool:
    onset_delta = abs(float(estimate["startSeconds"]) - float(reference["onsetSeconds"]))
    cents = pitch_delta_cents(float(estimate["midi"]), float(reference["midi"]))
    return inclusive_at_limit(onset_delta, ONSET_TOLERANCE_SECONDS) and inclusive_at_limit(
        cents, PITCH_TOLERANCE_CENTS
    )


def maximum_cardinality_matches(estimates: list[dict], references: list[dict]) -> dict[int, int]:
    adjacency: list[list[int]] = []
    for estimate in estimates:
        candidates = [index for index, ref in enumerate(references) if valid_match(estimate, ref)]
        candidates.sort(
            key=lambda index: (
                abs(float(estimate["startSeconds"]) - float(references[index]["onsetSeconds"])),
                pitch_delta_cents(float(estimate["midi"]), float(references[index]["midi"])),
                str(references[index]["referenceId"]),
                index,
            )
        )
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

    order = sorted(
        range(len(estimates)),
        key=lambda index: (
            float(estimates[index]["startSeconds"]),
            int(estimates[index]["midi"]),
            str(estimates[index].get("noteId", index)),
            index,
        ),
    )
    for est_index in order:
        augment(est_index, set())
    return {est_index: ref_index for ref_index, est_index in ref_to_est.items()}


def precision(correct: int, total: int) -> float | None:
    return None if total <= 0 else float(correct) / float(total)


def recall(correct: int, total_reference: int) -> float | None:
    return None if total_reference <= 0 else float(correct) / float(total_reference)


def wilson_lower_one_sided_95(correct: int, total: int) -> float | None:
    if total <= 0:
        return None
    p = float(correct) / float(total)
    n = float(total)
    z = WILSON_Z_ONE_SIDED_95
    denominator = 1.0 + z * z / n
    center = p + z * z / (2.0 * n)
    spread = z * math.sqrt((p * (1.0 - p) / n) + z * z / (4.0 * n * n))
    return (center - spread) / denominator


def summarize_stratum(rows: list[dict]) -> dict:
    positives = sum(int(row["positiveCount"]) for row in rows)
    correct = sum(int(row["positiveCorrectCount"]) for row in rows)
    decoded = sum(int(row["decodedEventCount"]) for row in rows)
    references = sum(int(row["referenceEventCount"]) for row in rows)
    return {
        "fileCount": len(rows),
        "decodedEventCount": decoded,
        "referenceEventCount": references,
        "positiveCount": positives,
        "positiveCorrectCount": correct,
        "positivePrecision": precision(correct, positives),
        "positiveRecall": recall(correct, references),
    }


def summarize_by(rows: list[dict], key: str) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    return {name: summarize_stratum(group) for name, group in sorted(groups.items())}


def evaluate_gates(aggregate: dict) -> dict:
    gates = {
        "populationCompleteness": aggregate["completedFileCount"] == EXPECTED_PERFORMANCE_COUNT,
        "eventPreservation": aggregate["classifiedEventCount"] == aggregate["decodedEventCount"],
        "minimumTotalPositiveEvents": aggregate["positiveEventCount"] >= MIN_TOTAL_POSITIVES,
        "overallWilsonLowerBound": (
            aggregate["positivePrecisionWilsonLowerOneSided95"] is not None
            and aggregate["positivePrecisionWilsonLowerOneSided95"] >= OVERALL_WILSON_LOWER_BOUND_MIN
        ),
        "identityRuntimeGuards": bool(aggregate.get("identityRuntimeGuards", False)),
        "policyBoundary": bool(aggregate.get("policyBoundaryGuard", False)),
    }

    split_gates = {}
    for name, row in aggregate["bySplit"].items():
        if row["positiveCount"] >= STRATUM_MIN_POSITIVES:
            split_gates[name] = (
                row["positivePrecision"] is not None
                and row["positivePrecision"] >= STRATUM_POINT_PRECISION_MIN
            )
        else:
            split_gates[name] = True
    guitar_gates = {}
    for name, row in aggregate["byGuitarType"].items():
        if row["positiveCount"] >= STRATUM_MIN_POSITIVES:
            guitar_gates[name] = (
                row["positivePrecision"] is not None
                and row["positivePrecision"] >= STRATUM_POINT_PRECISION_MIN
            )
        else:
            guitar_gates[name] = True
    gates["splitRobustness"] = split_gates
    gates["guitarTypeRobustness"] = guitar_gates
    flat = [value for key, value in gates.items() if key not in {"splitRobustness", "guitarTypeRobustness"}]
    flat.extend(split_gates.values())
    flat.extend(guitar_gates.values())
    gates["allMandatoryGatesPassed"] = all(bool(value) for value in flat)
    return gates


def validate_one_file(
    repo_root: Path,
    dataset_root: Path,
    work_dir: Path,
    v5,
    row: dict,
    references: list[dict],
    index: int,
) -> dict:
    stem = row["stem"]
    audio_info = row.get("audio", {})
    audio_rel = audio_info.get("path")
    if not isinstance(audio_rel, str):
        raise ValidationError(f"AUDIO_PATH_INVALID:{stem}")
    source_mp3 = dataset_root / audio_rel
    if not source_mp3.is_file() or source_mp3.is_symlink():
        raise ValidationError(f"AUDIO_FILE_INVALID:{stem}")
    source_sha = sha256_file(source_mp3)
    if source_sha != audio_info.get("sha256"):
        raise ValidationError(f"AUDIO_SHA256_CHANGED:{stem}")

    file_root = work_dir / f"track-{index:03d}-{stem}"
    if file_root.exists():
        raise ValidationError(f"TRACK_WORK_DIR_ALREADY_EXISTS:{file_root}")
    file_root.mkdir(parents=True)
    canonical_wav = file_root / "canonical.wav"
    audio, canonical = canonicalize_audio(source_mp3, canonical_wav)

    inference_json = file_root / "basic-pitch.json"
    inference_log = file_root / "basic-pitch.log"
    run_transcriber(repo_root, canonical_wav, inference_json, inference_log, source_sha)
    estimates = validate_basic_pitch_payload(inference_json)
    classified, class_counts = classify_events(v5, audio, estimates)
    positives = [row for row in classified if row["classification"] == CLASS_POSITIVE]

    positive_matches = maximum_cardinality_matches(positives, references)
    baseline_matches = maximum_cardinality_matches(estimates, references)
    correct = len(positive_matches)
    baseline_correct = len(baseline_matches)

    return {
        "index": index,
        "stem": stem,
        "split": row["split"],
        "guitarType": row["guitarType"],
        "sourceAudio": {
            "path": audio_rel,
            "sha256": source_sha,
        },
        "canonicalAudio": canonical,
        "referenceEventCount": len(references),
        "decodedEventCount": len(estimates),
        "classificationCounts": class_counts,
        "classifiedEventCount": sum(class_counts.values()),
        "positiveCount": len(positives),
        "positiveCorrectCount": correct,
        "positivePrecision": precision(correct, len(positives)),
        "positiveRecall": recall(correct, len(references)),
        "baselineCorrectCount": baseline_correct,
        "baselinePrecision": precision(baseline_correct, len(estimates)),
        "basicPitchOutputSha256": sha256_file(inference_json),
    }


def run_real(repo_root: Path, dataset_root: Path, stage_b_path: Path, work_dir: Path) -> dict:
    source = verify_repo_source(repo_root)
    dataset = verify_dataset_source(dataset_root)
    runtime = package_runtime()
    stage_b = validate_stage_b_report(stage_b_path)
    adapter = load_stage_b_adapter(repo_root)
    references_by_stem = reconstruct_references(adapter, dataset_root, stage_b)
    v5 = load_frozen_v5(repo_root)

    if work_dir.exists():
        raise ValidationError("WORK_DIR_MUST_NOT_ALREADY_EXIST")
    work_dir.mkdir(parents=True)

    rows = []
    total = len(stage_b["included"])
    for index, row in enumerate(stage_b["included"], start=1):
        stem = row["stem"]
        print(f"FLGD_V5_TRACK_START {index}/{total} {stem}", flush=True)
        result = validate_one_file(
            repo_root,
            dataset_root,
            work_dir,
            v5,
            row,
            references_by_stem[stem],
            index,
        )
        rows.append(result)
        print(
            "FLGD_V5_TRACK_COMPLETE "
            f"{index}/{total} {stem} decoded={result['decodedEventCount']} "
            f"positive={result['positiveCount']} correct={result['positiveCorrectCount']}",
            flush=True,
        )

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
        "classificationCounts": {name: int(class_counts.get(name, 0)) for name in CLASSIFICATIONS},
        "positiveEventCount": positives,
        "positiveCorrectCount": correct,
        "positivePrecision": precision(correct, positives),
        "positivePrecisionWilsonLowerOneSided95": wilson_lower_one_sided_95(correct, positives),
        "positiveRecall": recall(correct, refs),
        "baselineCorrectCount": baseline_correct,
        "baselinePrecision": precision(baseline_correct, decoded),
        "bySplit": summarize_by(rows, "split"),
        "byGuitarType": summarize_by(rows, "guitarType"),
        "identityRuntimeGuards": True,
        "policyBoundaryGuard": True,
    }
    aggregate["gates"] = evaluate_gates(aggregate)
    aggregate["externalValidationPassed"] = bool(aggregate["gates"]["allMandatoryGatesPassed"])

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "source": source,
        "dataset": dataset,
        "runtime": runtime,
        "inputs": {
            "stageAReportSha256": EXPECTED_STAGE_A_REPORT_SHA256,
            "stageBReportSha256": EXPECTED_STAGE_B_REPORT_SHA256,
            "includedPopulationSha256": EXPECTED_INCLUDED_POPULATION_SHA256,
            "referenceEventIdentitySha256": EXPECTED_REFERENCE_IDENTITY_SHA256,
            "ignoredDuplicateReleaseIdentitySha256": EXPECTED_IGNORED_RELEASE_IDENTITY_SHA256,
        },
        "scoringContract": {
            "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCents": PITCH_TOLERANCE_CENTS,
            "inclusiveAbsTolerance": INCLUSIVE_ABS_TOL,
            "wilsonZOneSided95": WILSON_Z_ONE_SIDED_95,
            "minimumTotalPositives": MIN_TOTAL_POSITIVES,
            "overallWilsonLowerBoundMin": OVERALL_WILSON_LOWER_BOUND_MIN,
            "stratumMinimumPositives": STRATUM_MIN_POSITIVES,
            "stratumPointPrecisionMin": STRATUM_POINT_PRECISION_MIN,
            "durationUsedForMatching": False,
        },
        "files": rows,
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
    # Inclusive 50-ms boundary survives binary64 representation; just outside fails.
    assert inclusive_at_limit(1.05 - 1.0, ONSET_TOLERANCE_SECONDS)
    assert not inclusive_at_limit(0.05000000001, ONSET_TOLERANCE_SECONDS)
    assert inclusive_at_limit(50.0, PITCH_TOLERANCE_CENTS)
    assert not inclusive_at_limit(50.00000001, PITCH_TOLERANCE_CENTS)

    refs = [
        {"referenceId": "r0", "onsetSeconds": 1.0, "midi": 60},
        {"referenceId": "r1", "onsetSeconds": 1.04, "midi": 60},
        {"referenceId": "r2", "onsetSeconds": 2.0, "midi": 64},
    ]
    estimates = [
        {"noteId": "e0", "startSeconds": 1.05, "midi": 60},
        {"noteId": "e1", "startSeconds": 1.0, "midi": 60},
        {"noteId": "e2", "startSeconds": 2.0, "midi": 65},
    ]
    matches = maximum_cardinality_matches(estimates, refs)
    assert len(matches) == 2
    assert 2 not in matches  # adjacent semitone must not match.

    assert precision(99, 100) == 0.99
    assert recall(50, 100) == 0.5
    assert wilson_lower_one_sided_95(1000, 1000) > 0.99
    assert wilson_lower_one_sided_95(990, 1000) < 0.99

    synthetic_rows = [
        {
            "split": "train",
            "guitarType": "nylon",
            "decodedEventCount": 800,
            "referenceEventCount": 800,
            "positiveCount": 600,
            "positiveCorrectCount": 600,
        },
        {
            "split": "test",
            "guitarType": "electric",
            "decodedEventCount": 600,
            "referenceEventCount": 600,
            "positiveCount": 500,
            "positiveCorrectCount": 500,
        },
    ]
    aggregate = {
        "completedFileCount": EXPECTED_PERFORMANCE_COUNT,
        "decodedEventCount": 1400,
        "classifiedEventCount": 1400,
        "positiveEventCount": 1100,
        "positivePrecisionWilsonLowerOneSided95": wilson_lower_one_sided_95(1100, 1100),
        "bySplit": summarize_by(synthetic_rows, "split"),
        "byGuitarType": summarize_by(synthetic_rows, "guitarType"),
        "identityRuntimeGuards": True,
        "policyBoundaryGuard": True,
    }
    gates = evaluate_gates(aggregate)
    assert gates["allMandatoryGatesPassed"] is True
    aggregate["positivePrecisionWilsonLowerOneSided95"] = 0.98
    gates = evaluate_gates(aggregate)
    assert gates["overallWilsonLowerBound"] is False
    assert gates["allMandatoryGatesPassed"] is False

    return {
        "contract": CONTRACT,
        "selfTest": "PASS",
        "matching": {
            "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCents": PITCH_TOLERANCE_CENTS,
            "inclusiveAbsTolerance": INCLUSIVE_ABS_TOL,
            "maximumCardinalitySyntheticMatchCount": len(matches),
        },
        "gates": {
            "minimumTotalPositives": MIN_TOTAL_POSITIVES,
            "overallWilsonLowerBoundMin": OVERALL_WILSON_LOWER_BOUND_MIN,
            "stratumMinimumPositives": STRATUM_MIN_POSITIVES,
            "stratumPointPrecisionMin": STRATUM_POINT_PRECISION_MIN,
        },
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
        print(canonical_json(self_test()))
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
        raise ValidationError(f"REAL_MODE_ARGUMENTS_REQUIRED:{','.join(missing)}")

    repo_root = Path(args.repo_root).resolve()
    dataset_root = Path(args.dataset_root).resolve()
    stage_b_result = Path(args.stage_b_result).resolve()
    work_dir = Path(args.work_dir).resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise ValidationError("OUTPUT_MUST_NOT_ALREADY_EXIST")

    result = run_real(repo_root, dataset_root, stage_b_result, work_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "outputSha256": sha256_file(output),
        "aggregate": result["aggregate"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"FLGD_V5_EXTERNAL_VALIDATION_ERROR:{exc}")
        raise SystemExit(2)
