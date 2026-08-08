import base64
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import modal

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

STEM_PATH = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-guitar-specific-neural-detector-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-guitar-specific-neural-detector-v1-manifest.json"

TUNED_BASIC_PITCH_F1 = 6.39
SNAP_TOLERANCE_SECONDS = 0.085
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]

app = modal.App("jimmy-paige-guitar-specific-neural-detector-v1")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "hf-midi-transcription",
        "pretty_midi",
        "librosa",
        "soundfile",
    )
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def floating(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@app.function(
    image=image,
    gpu="L4",
    timeout=3600,
    memory=16384,
)
def transcribe_guitar_model(audio_b64: str):
    import tempfile

    import pretty_midi
    from hf_midi_transcription import MidiTranscriptionModel

    audio_bytes = base64.b64decode(audio_b64.encode("ascii"))

    with tempfile.TemporaryDirectory(prefix="jimmy-guitar-neural-v1-") as temp_dir:
        temp_root = Path(temp_dir)
        audio_path = temp_root / "guitar.wav"
        midi_path = temp_root / "guitar.mid"
        audio_path.write_bytes(audio_bytes)

        model = MidiTranscriptionModel.from_pretrained(
            "xavriley/midi-transcription-models",
            instrument="guitar",
        )
        model.transcribe(str(audio_path), str(midi_path))

        midi = pretty_midi.PrettyMIDI(str(midi_path))
        normalized = []
        for instrument in midi.instruments:
            if instrument.is_drum:
                continue
            for note in instrument.notes:
                normalized.append(
                    {
                        "onset": float(note.start),
                        "offset": float(note.end),
                        "midi": int(note.pitch),
                        "velocity": int(note.velocity),
                    }
                )

        return normalized


@app.local_entrypoint()
def main() -> None:
    import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
    import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing proven separator stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diagnostics = v2.build_timing_grid(events)
    grid_items = list(grid.items())

    reference = v2.load_json(REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = v3.reference_tokens(reference)

    print("JIMMY PAIGE GUITAR-SPECIFIC NEURAL DETECTOR BENCHMARK V1")
    print("Model: xavriley/midi-transcription-models")
    print("Instrument checkpoint: guitar")
    print("License: MIT")
    print("Input stem:", STEM_PATH.relative_to(ROOT))
    print("Tuned Basic Pitch F1 to beat:", TUNED_BASIC_PITCH_F1)

    stem_b64 = base64.b64encode(STEM_PATH.read_bytes()).decode("ascii")
    raw_notes = transcribe_guitar_model.remote(stem_b64)

    predicted: Counter[tuple[int, int, int]] = Counter()
    discarded = 0
    for row in raw_notes:
        onset = floating(row.get("onset"))
        midi_note = integer(row.get("midi"))
        if onset is None or midi_note is None:
            continue

        slot, distance = v2.nearest_grid_slot(onset, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            discarded += 1
            continue
        measure, step = slot
        predicted[(measure, step, midi_note)] += 1

    matched = sum((predicted & reference_counter).values())
    predicted_count = sum(predicted.values())
    reference_count = sum(reference_counter.values())
    missing = sum((reference_counter - predicted).values())
    extra = sum((predicted - reference_counter).values())
    score = round(100.0 * v2.f1(matched, predicted_count, reference_count), 2)

    priority_reference = Counter(
        {token: count for token, count in reference_counter.items() if token[0] in PRIORITY_MEASURES}
    )
    priority_predicted = Counter(
        {token: count for token, count in predicted.items() if token[0] in PRIORITY_MEASURES}
    )
    priority_matched = sum((priority_reference & priority_predicted).values())
    priority_missing = sum((priority_reference - priority_predicted).values())
    priority_extra = sum((priority_predicted - priority_reference).values())

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during guitar neural benchmark.")

    beats_basic_pitch = score > TUNED_BASIC_PITCH_F1
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "guitar-specific-neural-pitch-detector",
        "model": "xavriley/midi-transcription-models",
        "instrumentCheckpoint": "guitar",
        "modelLicense": "MIT",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "timingGrid": grid_diagnostics,
        "snapToleranceSeconds": SNAP_TOLERANCE_SECONDS,
        "tunedBasicPitchF1": TUNED_BASIC_PITCH_F1,
        "rawNeuralNoteCount": len(raw_notes),
        "snappedPredictionCount": predicted_count,
        "discardedOutsideGrid": discarded,
        "pitchF1": score,
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "priorityBatch": {
            "matched": priority_matched,
            "missing": priority_missing,
            "extra": priority_extra,
        },
        "beatsTunedBasicPitch": beats_basic_pitch,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "validate-guitar-specific-detector-on-more-sections"
            if beats_basic_pitch
            else "evaluate-multi-instrument-transformer-detector"
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY GUITAR-SPECIFIC NEURAL DETECTOR V1 COMPLETE")
    print("Passed: True")
    print("Tuned Basic Pitch F1:", TUNED_BASIC_PITCH_F1)
    print("Guitar neural pitch F1:", score)
    print("Matched/missing/extra:", matched, "/", missing, "/", extra)
    print("Priority matched/missing/extra:", priority_matched, "/", priority_missing, "/", priority_extra)
    print("Guitar neural beats tuned Basic Pitch:", beats_basic_pitch)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))
