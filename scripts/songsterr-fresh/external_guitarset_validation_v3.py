#!/usr/bin/env python3
"""Preregistered GuitarSet external validation harness for Songsterr Fresh V3.

This harness evaluates the frozen V2 independent pitch corroborator on the
locked GuitarSet v1.1.0 evaluation corpus defined before results in:
docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md

It never promotes model validation or customer delivery. It does not use
duration, model note ends, confidence, reference tabs, or protected-song data.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-guitarset-external-validation-v3"
VERSION = 3
DATASET_NAME = "GuitarSet"
DATASET_VERSION = "1.1.0"
DATASET_DOI = "10.5281/zenodo.3371780"

ANNOTATION_ARCHIVE_MD5 = "b39b78e63d3446f2e54ddb7a54df9b10"
AUDIO_ARCHIVE_MD5 = "275966d6610ac34999b58426beb119c3"

EXPECTED_DATASET_TRACK_COUNT = 360
EXCLUDED_TRACK_IDS = (
    "02_Funk2-119-G_comp",
    "04_BN3-154-E_comp",
    "04_Jazz1-200-B_comp",
)
LOCKED_EVALUATION_TRACK_COUNT = 357

SAMPLE_RATE = 44100
MIN_MIDI = 40
MAX_MIDI = 88
BASIC_PITCH_VERSION = "0.4.0"
ONSET_THRESHOLD = 0.5
FRAME_THRESHOLD = 0.3
MINIMUM_NOTE_LENGTH_MS = 127.7
ONSET_TOLERANCE_SECONDS = 0.050
PITCH_TOLERANCE_CENTS = 50.0

WILSON_Z_ONE_SIDED_95 = 1.6448536269514722
MIN_TOTAL_POSITIVES = 1000
OVERALL_WILSON_LOWER_BOUND_MIN = 0.9900
STRATUM_MIN_POSITIVES = 50
STRATUM_POINT_PRECISION_MIN = 0.9500

FROZEN_V2_CONTRACT = "songsterr-fresh-independent-pitch-corroboration-research-v2"
CLASS_POSITIVE = "independently-corroborated-candidate"
CLASS_NEGATIVE = "not-independently-corroborated"
CLASS_INSUFFICIENT = "insufficient-evidence"

PLAYER_IDS = tuple(f"{value:02d}" for value in range(6))
MODES = ("comp", "solo")


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


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract_zip(archive_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    with zipfile.ZipFile(archive_path, "r") as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if root != target and root not in target.parents:
                raise ValidationError(f"ZIP_PATH_TRAVERSAL:{member.filename}")
        archive.extractall(destination)


def track_metadata(track_id: str) -> tuple[str, str]:
    if len(track_id) < 4 or "_" not in track_id:
        raise ValidationError(f"TRACK_ID_INVALID:{track_id}")
    player = track_id.split("_", 1)[0]
    mode = track_id.rsplit("_", 1)[-1]
    if player not in PLAYER_IDS:
        raise ValidationError(f"TRACK_PLAYER_INVALID:{track_id}:{player}")
    if mode not in MODES:
        raise ValidationError(f"TRACK_MODE_INVALID:{track_id}:{mode}")
    return player, mode


def wav_track_id(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_mic"):
        stem = stem[:-4]
    return stem


def discover_locked_tracks(annotation_root: Path, audio_root: Path) -> list[dict]:
    jams_by_track: dict[str, Path] = {}
    for path in annotation_root.rglob("*.jams"):
        track_id = path.stem
        if track_id in jams_by_track:
            raise ValidationError(f"DUPLICATE_JAMS_TRACK:{track_id}")
        jams_by_track[track_id] = path

    audio_by_track: dict[str, Path] = {}
    for path in audio_root.rglob("*.wav"):
        track_id = wav_track_id(path)
        if track_id in audio_by_track:
            raise ValidationError(f"DUPLICATE_AUDIO_TRACK:{track_id}")
        audio_by_track[track_id] = path

    if set(jams_by_track) != set(audio_by_track):
        missing_audio = sorted(set(jams_by_track) - set(audio_by_track))
        missing_jams = sorted(set(audio_by_track) - set(jams_by_track))
        raise ValidationError(
            f"DATASET_TRACK_SET_MISMATCH:missingAudio={missing_audio}:missingJams={missing_jams}"
        )
    if len(jams_by_track) != EXPECTED_DATASET_TRACK_COUNT:
        raise ValidationError(
            f"DATASET_TRACK_COUNT_CHANGED:{len(jams_by_track)}!={EXPECTED_DATASET_TRACK_COUNT}"
        )
    for track_id in EXCLUDED_TRACK_IDS:
        if track_id not in jams_by_track:
            raise ValidationError(f"PREREGISTERED_EXCLUSION_MISSING:{track_id}")

    locked = []
    for track_id in sorted(jams_by_track):
        if track_id in EXCLUDED_TRACK_IDS:
            continue
        player, mode = track_metadata(track_id)
        locked.append(
            {
                "trackId": track_id,
                "playerId": player,
                "mode": mode,
                "jamsPath": jams_by_track[track_id],
                "audioPath": audio_by_track[track_id],
            }
        )
    if len(locked) != LOCKED_EVALUATION_TRACK_COUNT:
        raise ValidationError(
            f"LOCKED_TRACK_COUNT_CHANGED:{len(locked)}!={LOCKED_EVALUATION_TRACK_COUNT}"
        )
    return locked


def load_reference_notes(jams_path: Path) -> list[dict]:
    try:
        payload = json.loads(jams_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValidationError(f"JAMS_LOAD_FAILED:{jams_path}") from exc
    annotations = [
        entry
        for entry in payload.get("annotations", [])
        if entry.get("namespace") == "note_midi"
    ]
    by_string = {}
    for entry in annotations:
        source = str(entry.get("annotation_metadata", {}).get("data_source"))
        if source in by_string:
            raise ValidationError(f"DUPLICATE_NOTE_STRING_ANNOTATION:{jams_path}:{source}")
        by_string[source] = entry
    if set(by_string) != {str(i) for i in range(6)}:
        raise ValidationError(
            f"SIX_STRING_NOTE_ANNOTATIONS_REQUIRED:{jams_path}:{sorted(by_string)}"
        )

    rows = []
    for string_num in range(6):
        entry = by_string[str(string_num)]
        data = entry.get("data")
        if not isinstance(data, list):
            raise ValidationError(f"NOTE_ANNOTATION_DATA_REQUIRED:{jams_path}:{string_num}")
        for local_index, note in enumerate(data):
            onset = finite_number(note.get("time"), "reference.time")
            midi = finite_number(note.get("value"), "reference.value")
            if onset < 0.0:
                raise ValidationError("REFERENCE_ONSET_NEGATIVE")
            rows.append(
                {
                    "referenceId": f"string-{string_num}-note-{local_index:06d}",
                    "onsetSeconds": onset,
                    "midi": midi,
                    "string": string_num,
                }
            )
    rows.sort(
        key=lambda row: (
            row["onsetSeconds"],
            row["midi"],
            row["string"],
            row["referenceId"],
        )
    )
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
    if payload.get("diagnostics", {}).get("modelNoteEndsUsedAsDuration") is not False:
        raise ValidationError("BASIC_PITCH_MODEL_END_DURATION_GUARD_CHANGED")
    notes = payload.get("notes")
    if not isinstance(notes, list):
        raise ValidationError("BASIC_PITCH_NOTES_REQUIRED")

    result = []
    seen_ids = set()
    for index, note in enumerate(notes):
        note_id = note.get("noteId")
        if not isinstance(note_id, str) or not note_id or note_id in seen_ids:
            raise ValidationError(f"BASIC_PITCH_NOTE_ID_INVALID:{index}")
        seen_ids.add(note_id)
        start = finite_number(note.get("startSeconds"), f"notes[{index}].startSeconds")
        midi = note.get("midi")
        if isinstance(midi, bool) or not isinstance(midi, int):
            raise ValidationError(f"notes[{index}].midi:INTEGER_REQUIRED")
        if start < 0.0 or not MIN_MIDI <= midi <= MAX_MIDI:
            raise ValidationError(f"BASIC_PITCH_NOTE_OUT_OF_RANGE:{index}")
        result.append({"noteId": note_id, "startSeconds": start, "midi": midi})
    result.sort(key=lambda row: (row["startSeconds"], row["midi"], row["noteId"]))
    return result


def load_frozen_v2(repo_root: Path):
    path = repo_root / "scripts/songsterr-fresh/independent_pitch_corroboration_v2.py"
    spec = importlib.util.spec_from_file_location("songsterr_frozen_v2", path)
    if spec is None or spec.loader is None:
        raise ValidationError("FROZEN_V2_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if module.CONTRACT != FROZEN_V2_CONTRACT:
        raise ValidationError("FROZEN_V2_CONTRACT_CHANGED")
    expected = {
        "SAMPLE_RATE": SAMPLE_RATE,
        "WINDOW_SAMPLES": 16384,
        "PLAYABLE_MIDI_MIN": MIN_MIDI,
        "PLAYABLE_MIDI_MAX": MAX_MIDI,
        "MIN_WINDOW_RMS": 1e-4,
    }
    for field, value in expected.items():
        if getattr(module, field) != value:
            raise ValidationError(f"FROZEN_V2_CONSTANT_CHANGED:{field}")
    if tuple(module.COMPETITOR_OFFSETS) != (-12, -7, -2, -1, 1, 2, 7, 12):
        raise ValidationError("FROZEN_V2_COMPETITOR_OFFSETS_CHANGED")
    return module


def read_mono_audio(path: Path):
    try:
        import numpy as np
        import soundfile as sf
    except Exception as exc:
        raise ValidationError("NUMPY_SOUNDFILE_REQUIRED") from exc
    try:
        audio, sample_rate = sf.read(str(path), dtype="float64", always_2d=True)
    except Exception as exc:
        raise ValidationError(f"AUDIO_READ_FAILED:{path}") from exc
    if int(sample_rate) != SAMPLE_RATE:
        raise ValidationError(f"TRACK_SAMPLE_RATE_CHANGED:{path}:{sample_rate}")
    if audio.ndim != 2 or audio.shape[1] != 1:
        raise ValidationError(f"TRACK_MONO_AUDIO_REQUIRED:{path}:{audio.shape}")
    mono = np.asarray(audio[:, 0], dtype=np.float64)
    if not np.all(np.isfinite(mono)):
        raise ValidationError(f"TRACK_AUDIO_NONFINITE:{path}")
    return mono


def classify_events(v2, audio, events: list[dict]) -> tuple[list[dict], dict]:
    results = []
    counts = {
        CLASS_POSITIVE: 0,
        CLASS_NEGATIVE: 0,
        CLASS_INSUFFICIENT: 0,
    }
    for event in events:
        start_sample = int(math.floor(event["startSeconds"] * SAMPLE_RATE + 0.5))
        stop_sample = start_sample + int(v2.WINDOW_SAMPLES)
        if start_sample < 0 or stop_sample > len(audio):
            classification = CLASS_INSUFFICIENT
            reason = "FIXED_WINDOW_OUTSIDE_AUDIO"
        else:
            scored = v2.classify_window(audio[start_sample:stop_sample], int(event["midi"]))
            classification = scored["classification"]
            reason = scored["reason"]
        if classification not in counts:
            raise ValidationError(f"FROZEN_V2_UNEXPECTED_CLASSIFICATION:{classification}")
        counts[classification] += 1
        results.append(
            {
                "noteId": event["noteId"],
                "startSeconds": event["startSeconds"],
                "midi": event["midi"],
                "classification": classification,
                "reason": reason,
            }
        )
    if [
        (row["noteId"], row["startSeconds"], row["midi"]) for row in results
    ] != [
        (row["noteId"], row["startSeconds"], row["midi"]) for row in events
    ]:
        raise ValidationError("EVENT_IDENTITY_CHANGED_DURING_CORROBORATION")
    return results, counts


def valid_match(estimate: dict, reference: dict) -> bool:
    onset_delta = abs(float(estimate["startSeconds"]) - float(reference["onsetSeconds"]))
    pitch_delta_cents = abs(float(estimate["midi"]) - float(reference["midi"])) * 100.0
    return onset_delta <= ONSET_TOLERANCE_SECONDS and pitch_delta_cents <= PITCH_TOLERANCE_CENTS


def maximum_cardinality_matches(estimates: list[dict], references: list[dict]) -> dict[int, int]:
    adjacency = []
    for estimate in estimates:
        candidates = [
            index for index, reference in enumerate(references) if valid_match(estimate, reference)
        ]
        candidates.sort(
            key=lambda index: (
                abs(estimate["startSeconds"] - references[index]["onsetSeconds"]),
                abs(estimate["midi"] - references[index]["midi"]),
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
            current = ref_to_est.get(ref_index)
            if current is None or augment(current, seen_refs):
                ref_to_est[ref_index] = est_index
                return True
        return False

    for est_index in range(len(estimates)):
        augment(est_index, set())

    return {est_index: ref_index for ref_index, est_index in ref_to_est.items()}


def wilson_lower_bound(successes: int, trials: int) -> float:
    if isinstance(successes, bool) or isinstance(trials, bool):
        raise ValidationError("WILSON_INTEGER_COUNTS_REQUIRED")
    if not isinstance(successes, int) or not isinstance(trials, int):
        raise ValidationError("WILSON_INTEGER_COUNTS_REQUIRED")
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValidationError("WILSON_COUNT_RANGE_INVALID")
    z = WILSON_Z_ONE_SIDED_95
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    center = p + z2 / (2.0 * trials)
    adjustment = z * math.sqrt(p * (1.0 - p) / trials + z2 / (4.0 * trials * trials))
    return (center - adjustment) / denominator


def precision(correct: int, total: int) -> float | None:
    return None if total == 0 else correct / total


def run_basic_pitch(
    *,
    repo_root: Path,
    python_executable: Path,
    audio_path: Path,
    track_id: str,
    output_path: Path,
    log_path: Path,
) -> None:
    script = repo_root / "scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py"
    command = [
        str(python_executable),
        str(script),
        "--input",
        str(audio_path),
        "--output",
        str(output_path),
        "--audio-source",
        f"guitarset-v1.1.0:audio_mono-mic:{track_id}",
        "--separation-source",
        "external-validation-isolated-guitar:no-demucs",
        "--minimum-midi",
        str(MIN_MIDI),
        "--maximum-midi",
        str(MAX_MIDI),
        "--onset-threshold",
        str(ONSET_THRESHOLD),
        "--frame-threshold",
        str(FRAME_THRESHOLD),
        "--minimum-note-length-ms",
        str(MINIMUM_NOTE_LENGTH_MS),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    log_path.write_text(completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise ValidationError(f"BASIC_PITCH_EXECUTION_FAILED:{track_id}:{completed.returncode}")


def evaluate_track(
    *,
    repo_root: Path,
    python_executable: Path,
    v2,
    track: dict,
    inference_dir: Path,
) -> dict:
    track_id = track["trackId"]
    inference_path = inference_dir / f"{track_id}.json"
    log_path = inference_dir / f"{track_id}.log"
    run_basic_pitch(
        repo_root=repo_root,
        python_executable=python_executable,
        audio_path=track["audioPath"],
        track_id=track_id,
        output_path=inference_path,
        log_path=log_path,
    )
    events = validate_basic_pitch_payload(inference_path)
    audio = read_mono_audio(track["audioPath"])
    classified, class_counts = classify_events(v2, audio, events)
    references = load_reference_notes(track["jamsPath"])

    positives = [row for row in classified if row["classification"] == CLASS_POSITIVE]
    positive_matches = maximum_cardinality_matches(positives, references)
    all_matches = maximum_cardinality_matches(classified, references)

    positive_rows = []
    for index, event in enumerate(positives):
        ref_index = positive_matches.get(index)
        if ref_index is None:
            positive_rows.append(
                {
                    **event,
                    "correct": False,
                    "referenceId": None,
                    "referenceOnsetSeconds": None,
                    "referenceMidi": None,
                }
            )
        else:
            ref = references[ref_index]
            positive_rows.append(
                {
                    **event,
                    "correct": True,
                    "referenceId": ref["referenceId"],
                    "referenceOnsetSeconds": ref["onsetSeconds"],
                    "referenceMidi": ref["midi"],
                }
            )

    return {
        "trackId": track_id,
        "playerId": track["playerId"],
        "mode": track["mode"],
        "audioSha256": sha256_file(track["audioPath"]),
        "jamsSha256": sha256_file(track["jamsPath"]),
        "basicPitchOutputSha256": sha256_file(inference_path),
        "decodedEventCount": len(events),
        "referenceNoteCount": len(references),
        "classificationCounts": class_counts,
        "positiveEventCount": len(positives),
        "positiveCorrectCount": len(positive_matches),
        "allDecodedCorrectCount": len(all_matches),
        "positiveEvents": positive_rows,
    }


def build_aggregate(track_results: list[dict]) -> dict:
    total_decoded = sum(row["decodedEventCount"] for row in track_results)
    total_reference = sum(row["referenceNoteCount"] for row in track_results)
    total_positive = sum(row["positiveEventCount"] for row in track_results)
    total_positive_correct = sum(row["positiveCorrectCount"] for row in track_results)
    total_all_correct = sum(row["allDecodedCorrectCount"] for row in track_results)
    class_counts = defaultdict(int)
    by_player = {player: {"positive": 0, "correct": 0} for player in PLAYER_IDS}
    by_mode = {mode: {"positive": 0, "correct": 0} for mode in MODES}

    for row in track_results:
        for label, count in row["classificationCounts"].items():
            class_counts[label] += int(count)
        player = by_player[row["playerId"]]
        player["positive"] += row["positiveEventCount"]
        player["correct"] += row["positiveCorrectCount"]
        mode = by_mode[row["mode"]]
        mode["positive"] += row["positiveEventCount"]
        mode["correct"] += row["positiveCorrectCount"]

    overall_precision = precision(total_positive_correct, total_positive)
    overall_lb = None if total_positive == 0 else wilson_lower_bound(total_positive_correct, total_positive)
    player_rows = {
        player_id: {
            **values,
            "precision": precision(values["correct"], values["positive"]),
        }
        for player_id, values in by_player.items()
    }
    mode_rows = {
        mode_name: {
            **values,
            "precision": precision(values["correct"], values["positive"]),
        }
        for mode_name, values in by_mode.items()
    }

    gates = {
        "allLockedTracksCompleted": len(track_results) == LOCKED_EVALUATION_TRACK_COUNT,
        "minimumTotalPositiveEvents": total_positive >= MIN_TOTAL_POSITIVES,
        "overallWilsonLowerBound": overall_lb is not None and overall_lb >= OVERALL_WILSON_LOWER_BOUND_MIN,
        "perPlayer": {
            player_id: (
                values["positive"] >= STRATUM_MIN_POSITIVES
                and values["precision"] is not None
                and values["precision"] >= STRATUM_POINT_PRECISION_MIN
            )
            for player_id, values in player_rows.items()
        },
        "perMode": {
            mode_name: (
                values["positive"] >= STRATUM_MIN_POSITIVES
                and values["precision"] is not None
                and values["precision"] >= STRATUM_POINT_PRECISION_MIN
            )
            for mode_name, values in mode_rows.items()
        },
    }
    passed = (
        gates["allLockedTracksCompleted"]
        and gates["minimumTotalPositiveEvents"]
        and gates["overallWilsonLowerBound"]
        and all(gates["perPlayer"].values())
        and all(gates["perMode"].values())
    )

    return {
        "decodedEventCount": total_decoded,
        "referenceNoteCount": total_reference,
        "classificationCounts": dict(sorted(class_counts.items())),
        "positiveEventCount": total_positive,
        "positiveCorrectCount": total_positive_correct,
        "positivePrecision": overall_precision,
        "positivePrecisionWilsonLowerOneSided95": overall_lb,
        "baselineAllDecodedCorrectCount": total_all_correct,
        "baselineAllDecodedPrecision": precision(total_all_correct, total_decoded),
        "positiveRecallAgainstReference": precision(total_positive_correct, total_reference),
        "byPlayer": player_rows,
        "byMode": mode_rows,
        "gates": gates,
        "validationPassed": passed,
    }


def run_validation(args: argparse.Namespace) -> dict:
    repo_root = Path(args.repo_root).resolve()
    annotation_zip = Path(args.annotation_zip).resolve()
    audio_zip = Path(args.audio_mic_zip).resolve()
    output = Path(args.output).resolve()
    work_dir = Path(args.work_dir).resolve()
    python_executable = Path(args.python_executable).resolve()

    if output.exists():
        raise ValidationError(f"OUTPUT_ALREADY_EXISTS:{output}")
    if work_dir.exists() and any(work_dir.iterdir()):
        raise ValidationError(f"WORK_DIR_MUST_BE_EMPTY:{work_dir}")
    work_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    if md5_file(annotation_zip) != ANNOTATION_ARCHIVE_MD5:
        raise ValidationError("ANNOTATION_ARCHIVE_MD5_CHANGED")
    if md5_file(audio_zip) != AUDIO_ARCHIVE_MD5:
        raise ValidationError("AUDIO_ARCHIVE_MD5_CHANGED")

    annotation_root = work_dir / "annotations"
    audio_root = work_dir / "audio"
    inference_dir = work_dir / "inference"
    inference_dir.mkdir(parents=True, exist_ok=True)
    safe_extract_zip(annotation_zip, annotation_root)
    safe_extract_zip(audio_zip, audio_root)

    tracks = discover_locked_tracks(annotation_root, audio_root)
    v2 = load_frozen_v2(repo_root)

    track_results = []
    for index, track in enumerate(tracks, start=1):
        print(f"V3_GUITARSET_TRACK:{index}/{len(tracks)}:{track['trackId']}", flush=True)
        track_results.append(
            evaluate_track(
                repo_root=repo_root,
                python_executable=python_executable,
                v2=v2,
                track=track,
                inference_dir=inference_dir,
            )
        )

    aggregate = build_aggregate(track_results)
    result = {
        "contract": CONTRACT,
        "version": VERSION,
        "status": "V3_EXTERNAL_VALIDATION_COMPLETE",
        "dataset": {
            "name": DATASET_NAME,
            "version": DATASET_VERSION,
            "doi": DATASET_DOI,
            "annotationArchiveMd5": ANNOTATION_ARCHIVE_MD5,
            "audioMonoMicArchiveMd5": AUDIO_ARCHIVE_MD5,
            "sourceTrackCount": EXPECTED_DATASET_TRACK_COUNT,
            "excludedTrackIds": list(EXCLUDED_TRACK_IDS),
            "lockedEvaluationTrackCount": LOCKED_EVALUATION_TRACK_COUNT,
            "evaluatedTrackIds": [row["trackId"] for row in track_results],
        },
        "method": {
            "demucsInvoked": False,
            "inputRole": "already-isolated-acoustic-guitar-microphone-audio",
            "sampleRate": SAMPLE_RATE,
            "basicPitchVersion": BASIC_PITCH_VERSION,
            "basicPitch": {
                "minimumMidi": MIN_MIDI,
                "maximumMidi": MAX_MIDI,
                "onsetThreshold": ONSET_THRESHOLD,
                "frameThreshold": FRAME_THRESHOLD,
                "minimumNoteLengthMs": MINIMUM_NOTE_LENGTH_MS,
                "multiplePitchBends": False,
                "melodiaTrick": True,
            },
            "corroboratorContract": FROZEN_V2_CONTRACT,
            "reference": "union-of-six-note_midi-annotations",
            "matching": {
                "algorithm": "one-to-one-maximum-cardinality-bipartite",
                "onsetToleranceSeconds": ONSET_TOLERANCE_SECONDS,
                "pitchToleranceCents": PITCH_TOLERANCE_CENTS,
                "offsetsUsed": False,
            },
            "policy": {
                "minimumTotalPositiveEvents": MIN_TOTAL_POSITIVES,
                "overallWilsonLowerBoundMinimum": OVERALL_WILSON_LOWER_BOUND_MIN,
                "wilsonZOneSided95": WILSON_Z_ONE_SIDED_95,
                "stratumMinimumPositiveEvents": STRATUM_MIN_POSITIVES,
                "stratumPointPrecisionMinimum": STRATUM_POINT_PRECISION_MIN,
            },
        },
        "aggregate": aggregate,
        "tracks": track_results,
        "hardGuards": {
            "usesProtectedSong": False,
            "usesReferenceTab": False,
            "usesProfessionalScorer": False,
            "importsArchivedV143Logic": False,
            "usesGoatResearch": False,
            "usesBasicPitchConfidenceForClassification": False,
            "usesBasicPitchNoteEndForClassification": False,
            "usesDurationForClassification": False,
            "changesPitchIdentity": False,
            "changesOnsetIdentity": False,
            "dropsDecodedEvents": False,
            "tunesFrozenV2": False,
            "setsModelValidationComplete": False,
            "setsCustomerEligibility": False,
            "changesDurationAuthority": False,
        },
        "policyBoundary": {
            "externalValidationPassed": bool(aggregate["validationPassed"]),
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "separatePolicyReviewRequired": True,
        },
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "output": str(output),
                "validationPassed": aggregate["validationPassed"],
                "positiveEventCount": aggregate["positiveEventCount"],
                "positiveCorrectCount": aggregate["positiveCorrectCount"],
                "positivePrecision": aggregate["positivePrecision"],
                "positivePrecisionWilsonLowerOneSided95": aggregate[
                    "positivePrecisionWilsonLowerOneSided95"
                ],
                "policyBoundary": result["policyBoundary"],
            }
        )
    )
    return result


def run_self_test(repo_root: Path) -> None:
    assert track_metadata("00_BN1-129-Eb_comp") == ("00", "comp")
    assert track_metadata("05_Rock3-120-A_solo") == ("05", "solo")
    assert wav_track_id(Path("00_BN1-129-Eb_comp_mic.wav")) == "00_BN1-129-Eb_comp"

    assert abs(wilson_lower_bound(1000, 1000) - 0.9973017567602394) < 1e-15
    assert wilson_lower_bound(995, 1000) < OVERALL_WILSON_LOWER_BOUND_MIN
    assert wilson_lower_bound(1990, 2000) > OVERALL_WILSON_LOWER_BOUND_MIN

    estimates = [
        {"noteId": "e0", "startSeconds": 1.000, "midi": 60},
        {"noteId": "e1", "startSeconds": 1.020, "midi": 60},
        {"noteId": "e2", "startSeconds": 2.000, "midi": 64},
        {"noteId": "e3", "startSeconds": 3.000, "midi": 67},
    ]
    references = [
        {"referenceId": "r0", "onsetSeconds": 1.010, "midi": 60.0},
        {"referenceId": "r1", "onsetSeconds": 1.030, "midi": 60.0},
        {"referenceId": "r2", "onsetSeconds": 2.050, "midi": 64.5},
        {"referenceId": "r3", "onsetSeconds": 3.051, "midi": 67.0},
    ]
    matches = maximum_cardinality_matches(estimates, references)
    assert len(matches) == 3
    assert 0 in matches and 1 in matches and 2 in matches and 3 not in matches

    poly_estimates = [
        {"noteId": "p0", "startSeconds": 4.000, "midi": 60},
        {"noteId": "p1", "startSeconds": 4.000, "midi": 64},
        {"noteId": "p2", "startSeconds": 4.000, "midi": 67},
    ]
    poly_refs = [
        {"referenceId": "q0", "onsetSeconds": 4.001, "midi": 60.0},
        {"referenceId": "q1", "onsetSeconds": 4.002, "midi": 64.0},
        {"referenceId": "q2", "onsetSeconds": 4.003, "midi": 67.0},
    ]
    assert len(maximum_cardinality_matches(poly_estimates, poly_refs)) == 3

    boundary_est = [{"noteId": "b", "startSeconds": 5.000, "midi": 69}]
    boundary_ref = [{"referenceId": "br", "onsetSeconds": 5.050, "midi": 69.5}]
    assert len(maximum_cardinality_matches(boundary_est, boundary_ref)) == 1
    outside_ref = [{"referenceId": "bo", "onsetSeconds": 5.050001, "midi": 69.5}]
    assert len(maximum_cardinality_matches(boundary_est, outside_ref)) == 0

    module = load_frozen_v2(repo_root)
    assert module.CLASS_CORROBORATED == CLASS_POSITIVE
    assert module.CLASS_NOT_CORROBORATED == CLASS_NEGATIVE
    assert module.CLASS_INSUFFICIENT == CLASS_INSUFFICIENT

    fake_tracks = []
    for player in PLAYER_IDS:
        for mode in MODES:
            fake_tracks.append(
                {
                    "trackId": f"{player}_synthetic_{mode}",
                    "playerId": player,
                    "mode": mode,
                    "decodedEventCount": 100,
                    "referenceNoteCount": 100,
                    "classificationCounts": {
                        CLASS_POSITIVE: 100,
                        CLASS_NEGATIVE: 0,
                        CLASS_INSUFFICIENT: 0,
                    },
                    "positiveEventCount": 100,
                    "positiveCorrectCount": 100,
                    "allDecodedCorrectCount": 100,
                }
            )
    while len(fake_tracks) < LOCKED_EVALUATION_TRACK_COUNT:
        template = fake_tracks[len(fake_tracks) % 12].copy()
        template["trackId"] = f"synthetic-{len(fake_tracks):03d}"
        fake_tracks.append(template)
    aggregate = build_aggregate(fake_tracks)
    assert aggregate["validationPassed"] is True
    assert aggregate["positiveEventCount"] == LOCKED_EVALUATION_TRACK_COUNT * 100
    assert aggregate["positivePrecision"] == 1.0

    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "selfTest": "PASS",
                "guitarsetEvaluated": False,
                "protectedSongEvaluated": False,
                "frozenV2Imported": True,
                "modelValidationComplete": False,
                "customerEligibleEvents": 0,
            }
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--annotation-zip")
    parser.add_argument("--audio-mic-zip")
    parser.add_argument("--work-dir")
    parser.add_argument("--output")
    parser.add_argument("--python-executable", default=sys.executable)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if args.self_test:
        run_self_test(repo_root)
        return 0
    required = (
        args.annotation_zip,
        args.audio_mic_zip,
        args.work_dir,
        args.output,
        args.python_executable,
    )
    if not all(required):
        raise ValidationError(
            "USAGE_REQUIRES_ANNOTATION_ZIP_AUDIO_MIC_ZIP_WORK_DIR_OUTPUT_PYTHON"
        )
    run_validation(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(f"V3_EXTERNAL_VALIDATION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
