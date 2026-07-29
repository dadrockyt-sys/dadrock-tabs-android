import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v29 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v29")

# Phase 1.1: make harmony decisions as a connected progression rather than
# unrelated chord guesses. This remains general guitar knowledge and does not
# contain song-specific tablature.
SEQUENCE_STATE: dict[str, Any] = {
    "keyRoot": None,
    "keyMode": None,
    "previousRoot": None,
    "previousQuality": None,
    "previousBassPitchClass": None,
    "history": [],
}

DIATONIC_TRIADS = {
    "major": {
        0: "major",
        2: "minor",
        4: "minor",
        5: "major",
        7: "major",
        9: "minor",
        11: "minor",
    },
    "minor": {
        0: "minor",
        2: "minor",
        3: "major",
        5: "minor",
        7: "minor",
        8: "major",
        10: "major",
    },
}

COMMON_ROOT_MOTIONS = {
    0: 0.7,
    5: 0.45,
    7: 0.55,
    2: 0.25,
    10: 0.2,
}


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def reset_sequence_state() -> None:
    SEQUENCE_STATE.update(
        {
            "keyRoot": None,
            "keyMode": None,
            "previousRoot": None,
            "previousQuality": None,
            "previousBassPitchClass": None,
            "history": [],
        }
    )


def configure_key_context(groups: list[list[dict[str, Any]]]) -> dict[str, Any]:
    key = previous.infer_key(groups)
    SEQUENCE_STATE["keyRoot"] = key.get("root")
    SEQUENCE_STATE["keyMode"] = key.get("mode")
    return key


def key_compatibility(root: int, quality: str) -> float:
    key_root = SEQUENCE_STATE.get("keyRoot")
    key_mode = SEQUENCE_STATE.get("keyMode")
    if key_root is None or key_mode not in DIATONIC_TRIADS:
        return 0.0

    degree = (int(root) - int(key_root)) % 12
    expected = DIATONIC_TRIADS[str(key_mode)].get(degree)
    if expected is None:
        return -0.12
    if quality == expected:
        return 0.22
    if quality in {"7", "maj7"} and expected == "major":
        return 0.12
    if quality == "min7" and expected == "minor":
        return 0.12
    if quality in {"sus2", "sus4", "5"}:
        return 0.04
    return -0.08


def progression_compatibility(root: int, quality: str, bass_pc: int) -> float:
    previous_root = SEQUENCE_STATE.get("previousRoot")
    previous_quality = SEQUENCE_STATE.get("previousQuality")
    previous_bass = SEQUENCE_STATE.get("previousBassPitchClass")
    score = 0.0

    if previous_root is not None:
        movement = (int(root) - int(previous_root)) % 12
        reverse = (int(previous_root) - int(root)) % 12
        score += max(
            COMMON_ROOT_MOTIONS.get(movement, 0.0),
            COMMON_ROOT_MOTIONS.get(reverse, 0.0),
        )
        if int(root) == int(previous_root):
            score += 0.25 if quality == previous_quality else 0.08

    if previous_bass is not None:
        bass_distance = min(
            (int(bass_pc) - int(previous_bass)) % 12,
            (int(previous_bass) - int(bass_pc)) % 12,
        )
        if bass_distance <= 2:
            score += 0.18
        elif bass_distance >= 6:
            score -= 0.1

    return score


def sequence_aware_infer_chord(groups: list[list[dict[str, Any]]]) -> dict[str, Any]:
    weights = previous.weighted_pitch_classes(groups)
    if not weights:
        return {
            "name": None,
            "confidence": 0.0,
            "root": None,
            "quality": None,
            "bassPitchClass": None,
            "alternatives": [],
        }

    notes = [note for group in groups for note in group]
    bass_midi = min(int(note["midi"]) for note in notes)
    bass_pc = bass_midi % 12
    total = sum(weights.values()) or 1.0
    ranked: list[tuple[float, int, str, float]] = []

    for root in range(12):
        for quality, intervals in previous.CHORD_INTERVALS.items():
            chord_pcs = {(root + interval) % 12 for interval in intervals}
            covered = sum(weight for pc, weight in weights.items() if pc in chord_pcs)
            outside = total - covered
            root_weight = weights.get(root, 0.0)
            bass_is_chord_tone = bass_pc in chord_pcs
            raw = covered - outside * 1.45 + root_weight * 0.22
            raw += total * (0.12 if bass_is_chord_tone else -0.2)
            normalized = raw / total
            normalized += key_compatibility(root, quality)
            normalized += progression_compatibility(root, quality, bass_pc)
            ranked.append((normalized, root, quality, covered / total))

    ranked.sort(key=lambda item: item[0], reverse=True)
    best_score, root, quality, coverage = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else best_score
    confidence = max(
        0.0,
        min(
            1.0,
            coverage * 0.72 + max(0.0, best_score - second_score) * 0.28,
        ),
    )

    result = {
        "name": previous.chord_name(root, quality, bass_pc),
        "baseName": previous.chord_name(root, quality),
        "confidence": round(confidence, 3),
        "root": root,
        "quality": quality,
        "bassPitchClass": bass_pc,
        "bassMidi": bass_midi,
        "pitchClasses": sorted(weights),
        "alternatives": [
            {
                "name": previous.chord_name(candidate_root, candidate_quality, bass_pc),
                "score": round(float(score), 3),
                "coverage": round(float(candidate_coverage), 3),
            }
            for score, candidate_root, candidate_quality, candidate_coverage in ranked[:4]
        ],
    }

    SEQUENCE_STATE["previousRoot"] = root
    SEQUENCE_STATE["previousQuality"] = quality
    SEQUENCE_STATE["previousBassPitchClass"] = bass_pc
    SEQUENCE_STATE["history"].append(result["name"])
    return result


def bass_voice_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = previous.harmony_voicing_cost(assignment, transcription_type, anchor)
    if not assignment or transcription_type == "bass":
        return cost

    bass_pc = previous.ACTIVE_HARMONY.get("bassPitchClass")
    confidence = float(previous.ACTIVE_HARMONY.get("confidence") or 0.0)
    if bass_pc is None or confidence < 0.42:
        return cost

    lowest = min(assignment, key=lambda item: int(item[0]["midi"]))
    note, string_index, fret = lowest
    matches_bass = int(note["midi"]) % 12 == int(bass_pc)

    # In an arpeggio, the lowest voice should normally live on D/A/low-E and
    # should retain the inferred inversion instead of being moved to a treble string.
    if matches_bass:
        if int(string_index) >= 3:
            cost -= 2.2 + confidence * 1.8
        else:
            cost += 1.8 + confidence
    if int(fret) == 0 and int(string_index) >= 3:
        cost -= 0.45 if int(anchor) <= 2 else 0.0
    return cost


# Install the phase-1.1 decisions into v29's existing harmony-first pipeline.
previous.infer_chord = sequence_aware_infer_chord
previous.harmony_voicing_cost = bass_voice_cost
previous.v25.guitarist_assignment_cost = bass_voice_cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    from basic_pitch.inference import predict

    # Run one lightweight detection pass solely to establish global key context.
    # V29 performs the production pass and all existing cleaning/mapping steps.
    _, _, note_events = predict(audio_path)
    extracted = [
        parsed
        for event in note_events
        if (parsed := engine.extract_note_event(event)) is not None
    ]
    cleaned = previous.base.clean_detected_notes(extracted, transcription_type)
    groups = previous.base.guitarist_group_notes(cleaned, transcription_type)

    reset_sequence_state()
    key_context = configure_key_context(groups)
    result = previous.analyze_audio_file(audio_path, transcription_type)
    result["engineVersion"] = "3.0-phase-1-chord-sequence-bass-voice"
    result["guitarBrainLesson"] = "connect-chords-and-preserve-bass-inversions"
    result["phase1Sequence"] = {
        "keyContext": key_context,
        "smoothedChordHistory": list(SEQUENCE_STATE.get("history") or []),
    }
    return result


@app.function(
    image=image,
    timeout=600,
    memory=4096,
    secrets=[modal.Secret.from_name("dadrock-analyzer-secret")],
)
@modal.fastapi_endpoint(method="POST")
def analyze(payload: dict) -> dict:
    import requests
    from fastapi import HTTPException

    expected_token = os.environ.get("ANALYZER_API_TOKEN")
    supplied_token = str(payload.get("token") or "")
    if not expected_token or supplied_token != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized analyzer request.")

    audio_url = str(payload.get("audioUrl") or "").strip()
    transcription_type = str(payload.get("transcriptionType") or "").strip().lower()
    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise HTTPException(status_code=400, detail="transcriptionType must be lead, rhythm, or bass.")
    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=400, detail="A valid audioUrl is required.")

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    headers: dict[str, str] = {}
    blob_token = str(payload.get("blobToken") or "").strip()
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"
        try:
            response = requests.get(audio_url, headers=headers, timeout=120)
        except requests.RequestException as error:
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.") from error
        if not response.ok:
            raise HTTPException(status_code=502, detail="The analyzer could not download the audio file.")
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(status_code=413, detail="The uploaded audio cannot be larger than 50 MB.")

        audio_path.write_bytes(response.content)
        try:
            original_metadata = engine.inspect_audio_file(str(audio_path))
            engine.validate_audio_metadata(original_metadata)
            normalized_path = Path(temp_dir) / "normalized.wav"
            engine.normalize_audio_file(str(audio_path), str(normalized_path))
            normalized_metadata = engine.inspect_audio_file(str(normalized_path))
            result = analyze_audio_file(str(normalized_path), transcription_type)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
