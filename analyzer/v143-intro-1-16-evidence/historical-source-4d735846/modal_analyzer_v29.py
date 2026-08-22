import os
import statistics
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v28 as previous

engine = previous.engine
base = previous.previous.previous.previous.base
v25 = previous.v25
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v28")

# Phase 1: identify musical context before choosing string/fret locations.
NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

CHORD_INTERVALS: dict[str, tuple[int, ...]] = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "min7": (0, 3, 7, 10),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "5": (0, 7),
}

# Standard-tuning open-position voicings. String indexes are high E=0 ... low E=5.
# These are preferences, not forced answers. They give the optimizer real guitar knowledge.
OPEN_VOICINGS: dict[str, dict[int, int]] = {
    "A": {0: 0, 1: 2, 2: 2, 3: 2, 4: 0},
    "Am": {0: 0, 1: 1, 2: 2, 3: 2, 4: 0},
    "Am7": {0: 0, 1: 1, 2: 0, 3: 2, 4: 0},
    "C": {0: 0, 1: 1, 2: 0, 3: 2, 4: 3},
    "C/G": {0: 0, 1: 1, 2: 0, 3: 2, 4: 3, 5: 3},
    "D": {0: 2, 1: 3, 2: 2, 3: 0},
    "D/F#": {0: 2, 1: 3, 2: 2, 3: 0, 5: 2},
    "Dm": {0: 1, 1: 3, 2: 2, 3: 0},
    "E": {0: 0, 1: 0, 2: 1, 3: 2, 4: 2, 5: 0},
    "Em": {0: 0, 1: 0, 2: 0, 3: 2, 4: 2, 5: 0},
    "Fmaj7": {0: 0, 1: 1, 2: 2, 3: 3},
    "G": {0: 3, 1: 0, 2: 0, 3: 0, 4: 2, 5: 3},
    "G/B": {0: 3, 1: 0, 2: 0, 3: 0, 4: 2},
}

ACTIVE_HARMONY: dict[str, Any] = {
    "chord": None,
    "confidence": 0.0,
    "bassPitchClass": None,
    "texture": "unknown",
}


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def pitch_class_name(pitch_class: int) -> str:
    return NOTE_NAMES[int(pitch_class) % 12]


def chord_name(root: int, quality: str, bass_pitch_class: int | None = None) -> str:
    root_name = pitch_class_name(root)
    suffix = {
        "major": "",
        "minor": "m",
        "7": "7",
        "maj7": "maj7",
        "min7": "m7",
        "sus2": "sus2",
        "sus4": "sus4",
        "5": "5",
    }[quality]
    name = f"{root_name}{suffix}"
    if bass_pitch_class is not None and bass_pitch_class != root:
        name += f"/{pitch_class_name(bass_pitch_class)}"
    return name


def weighted_pitch_classes(groups: list[list[dict[str, Any]]]) -> Counter[int]:
    weights: Counter[int] = Counter()
    for group in groups:
        for note in group:
            midi = int(note["midi"])
            duration = max(0.08, float(note.get("end") or note["start"]) - float(note["start"]))
            confidence = float(note.get("confidence") or note.get("amplitude") or 0.75)
            weights[midi % 12] += duration * max(0.25, confidence)
    return weights


def infer_texture(groups: list[list[dict[str, Any]]]) -> str:
    if not groups:
        return "unknown"
    polyphonic = sum(1 for group in groups if len(group) >= 2)
    average_group_size = statistics.mean(len(group) for group in groups)
    starts = [min(float(note["start"]) for note in group) for group in groups]
    intervals = [b - a for a, b in zip(starts, starts[1:]) if b > a]
    median_interval = statistics.median(intervals) if intervals else 0.5

    if polyphonic >= max(2, len(groups) // 3):
        return "chordal"
    if average_group_size <= 1.35 and median_interval <= 0.5:
        return "arpeggio"
    if average_group_size <= 1.2:
        return "melodic"
    return "mixed"


def infer_chord(groups: list[list[dict[str, Any]]]) -> dict[str, Any]:
    weights = weighted_pitch_classes(groups)
    if not weights:
        return {"name": None, "confidence": 0.0, "root": None, "quality": None, "bassPitchClass": None}

    all_notes = [note for group in groups for note in group]
    bass_note = min(all_notes, key=lambda note: int(note["midi"]))
    bass_pc = int(bass_note["midi"]) % 12
    total_weight = sum(weights.values()) or 1.0
    ranked: list[tuple[float, int, str]] = []

    for root in range(12):
        for quality, intervals in CHORD_INTERVALS.items():
            chord_pcs = {(root + interval) % 12 for interval in intervals}
            covered = sum(weight for pc, weight in weights.items() if pc in chord_pcs)
            outside = sum(weight for pc, weight in weights.items() if pc not in chord_pcs)
            root_weight = weights.get(root, 0.0)
            bass_bonus = 0.16 * total_weight if bass_pc in chord_pcs else -0.18 * total_weight
            complexity_penalty = max(0, len(chord_pcs) - len(weights)) * 0.05 * total_weight
            score = covered - outside * 1.35 + root_weight * 0.25 + bass_bonus - complexity_penalty
            ranked.append((score, root, quality))

    ranked.sort(reverse=True, key=lambda item: item[0])
    best_score, root, quality = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else best_score
    coverage = sum(weight for pc, weight in weights.items() if pc in {(root + i) % 12 for i in CHORD_INTERVALS[quality]})
    confidence = max(0.0, min(1.0, (coverage / total_weight) * 0.75 + max(0.0, best_score - second_score) / total_weight * 0.25))

    return {
        "name": chord_name(root, quality, bass_pc),
        "baseName": chord_name(root, quality),
        "confidence": round(confidence, 3),
        "root": root,
        "quality": quality,
        "bassPitchClass": bass_pc,
        "pitchClasses": sorted(weights),
    }


def infer_key(groups: list[list[dict[str, Any]]]) -> dict[str, Any]:
    weights = weighted_pitch_classes(groups)
    if not weights:
        return {"name": None, "confidence": 0.0}

    major = (0, 2, 4, 5, 7, 9, 11)
    minor = (0, 2, 3, 5, 7, 8, 10)
    total = sum(weights.values()) or 1.0
    candidates: list[tuple[float, int, str]] = []
    for root in range(12):
        for mode, intervals in (("major", major), ("minor", minor)):
            scale = {(root + interval) % 12 for interval in intervals}
            inside = sum(weight for pc, weight in weights.items() if pc in scale)
            outside = total - inside
            tonic = weights.get(root, 0.0)
            fifth = weights.get((root + 7) % 12, 0.0)
            score = inside - outside * 1.5 + tonic * 0.18 + fifth * 0.08
            candidates.append((score, root, mode))

    candidates.sort(reverse=True, key=lambda item: item[0])
    best, root, mode = candidates[0]
    second = candidates[1][0] if len(candidates) > 1 else best
    confidence = max(0.0, min(1.0, 0.55 + (best - second) / total * 0.45))
    return {
        "name": f"{pitch_class_name(root)} {mode}",
        "root": root,
        "mode": mode,
        "confidence": round(confidence, 3),
    }


def split_harmonic_windows(phrase: list[list[dict[str, Any]]]) -> list[list[list[dict[str, Any]]]]:
    """Split a phrase into short musical decisions before fret assignment."""
    if not phrase:
        return []

    windows: list[list[list[dict[str, Any]]]] = []
    current: list[list[dict[str, Any]]] = []
    window_start = min(float(note["start"]) for note in phrase[0])

    for group in phrase:
        group_start = min(float(note["start"]) for note in group)
        gap = 0.0
        if current:
            prior_start = min(float(note["start"]) for note in current[-1])
            gap = group_start - prior_start

        should_break = bool(current) and (
            len(current) >= 6
            or group_start - window_start >= 1.65
            or gap >= 0.72
        )
        if should_break:
            windows.append(current)
            current = []
            window_start = group_start
        current.append(group)

    if current:
        windows.append(current)
    return windows


def harmony_voicing_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = previous.held_shape_assignment_cost(assignment, transcription_type, anchor)
    chord = ACTIVE_HARMONY.get("chord")
    confidence = float(ACTIVE_HARMONY.get("confidence") or 0.0)
    texture = str(ACTIVE_HARMONY.get("texture") or "unknown")
    if not chord or confidence < 0.45 or transcription_type == "bass":
        return cost

    voicing = OPEN_VOICINGS.get(str(chord))
    if voicing is None and "/" in str(chord):
        voicing = OPEN_VOICINGS.get(str(chord).split("/", 1)[0])

    if voicing:
        matched = 0
        mismatched = 0
        for _, string_index, fret in assignment:
            string_index = int(string_index)
            fret = int(fret)
            if string_index in voicing:
                if voicing[string_index] == fret:
                    matched += 1
                else:
                    mismatched += 1
        cost -= matched * (2.8 + confidence * 2.0)
        cost += mismatched * (0.8 + confidence * 1.2)

        if texture in {"arpeggio", "chordal"} and anchor <= 2:
            cost -= matched * 0.8

    return cost


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)
    extracted = [
        parsed
        for event in note_events
        if (parsed := engine.extract_note_event(event)) is not None
    ]
    cleaned = base.clean_detected_notes(extracted, transcription_type)
    onset_groups = base.guitarist_group_notes(cleaned, transcription_type)
    phrases = engine.split_phrases(onset_groups)

    global_key = infer_key(onset_groups)
    mapped_groups: list[list[dict[str, Any]]] = []
    harmony_diagnostics: list[dict[str, Any]] = []
    candidate_diagnostics: list[dict[str, Any]] = []
    previous_assignment = None
    previous_anchor = None

    # Install the phase-1-aware score into the phrase optimizer.
    v25.guitarist_assignment_cost = harmony_voicing_cost
    v25.phrase_movement_cost = previous.held_shape_transition_cost

    for phrase_index, phrase in enumerate(phrases):
        for window_index, window in enumerate(split_harmonic_windows(phrase)):
            harmony = infer_chord(window)
            texture = infer_texture(window)
            ACTIVE_HARMONY.update(
                {
                    "chord": harmony.get("name"),
                    "confidence": harmony.get("confidence", 0.0),
                    "bassPitchClass": harmony.get("bassPitchClass"),
                    "texture": texture,
                }
            )

            anchors = list(v25.ANCHORS)
            if previous_anchor is not None:
                anchors.insert(0, int(previous_anchor))
            if harmony.get("baseName") in OPEN_VOICINGS and 0 not in anchors:
                anchors.insert(0, 0)

            ranked: list[tuple[float, int, list[list[tuple[dict[str, Any], int, int]]]]] = []
            for anchor in dict.fromkeys(anchors):
                for score, path in v25.build_phrase_paths(
                    window,
                    transcription_type,
                    int(anchor),
                    previous_assignment,
                ):
                    anchor_shift = 0.0
                    if previous_anchor is not None:
                        anchor_shift = abs(int(anchor) - int(previous_anchor)) * 1.2
                    ranked.append((score + anchor_shift, int(anchor), path))

            if not ranked:
                continue

            ranked.sort(key=lambda item: item[0])
            winning_score, winning_anchor, winning_path = ranked[0]
            mapped_groups.extend(v25.render_path(winning_path))
            previous_assignment = winning_path[-1] if winning_path else previous_assignment
            previous_anchor = winning_anchor

            start = min(float(note["start"]) for group in window for note in group)
            end = max(float(note.get("end") or note["start"]) for group in window for note in group)
            harmony_diagnostics.append(
                {
                    "phraseIndex": phrase_index,
                    "windowIndex": window_index,
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "texture": texture,
                    "chord": harmony,
                    "chosenAnchor": winning_anchor,
                }
            )
            candidate_diagnostics.append(
                {
                    "phraseIndex": phrase_index,
                    "windowIndex": window_index,
                    "chosenAnchor": winning_anchor,
                    "winningScore": round(float(winning_score), 3),
                    "topCandidates": [
                        {
                            "anchor": anchor,
                            "score": round(float(score), 3),
                            "metrics": previous.previous.previous.path_metrics(path),
                        }
                        for score, anchor, path in ranked[:4]
                    ],
                }
            )

    generated_tab = engine.create_tab(mapped_groups, transcription_type)
    flattened = [event for group in mapped_groups for event in group]
    detected_chords = [
        item["chord"]["name"]
        for item in harmony_diagnostics
        if item.get("chord", {}).get("name")
    ]

    return {
        "generatedTab": generated_tab,
        "tuning": "Standard Bass" if transcription_type == "bass" else "E Standard",
        "tempo": None,
        "timeSignature": None,
        "keySignature": global_key.get("name"),
        "difficulty": None,
        "techniques": sorted({event["technique"] for event in flattened if event.get("technique")}),
        "confidence": None,
        "events": flattened,
        "noteCount": len(flattened),
        "rawNoteCount": len(extracted),
        "cleanedNoteCount": len(cleaned),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
        "musicalUnderstanding": {
            "key": global_key,
            "detectedChords": detected_chords,
            "harmonicWindows": harmony_diagnostics,
        },
        "candidateDiagnostics": candidate_diagnostics,
        "styleProfile": "jimmy-paige-phase-1-harmony-first",
        "engineVersion": "2.9-phase-1-musical-understanding",
        "guitarBrainLesson": "infer-key-chord-bass-and-texture-before-fret-assignment",
    }


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
