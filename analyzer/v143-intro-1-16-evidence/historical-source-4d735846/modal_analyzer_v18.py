import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v17 as guitarist

app = modal.App("dadrock-tab-analyzer")
image = guitarist.image.add_local_python_source(
    "modal_analyzer_v17"
)

OCTAVE_GHOST_RATIO = 0.46
REPEATED_PHRASE_ROUNDING = 0.05
SUSTAIN_CONFLICT_TOLERANCE = 0.025


def to_json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {
            str(key): to_json_safe(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]

    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return to_json_safe(item_method())
        except (TypeError, ValueError):
            pass

    tolist_method = getattr(value, "tolist", None)
    if callable(tolist_method):
        try:
            return to_json_safe(tolist_method())
        except (TypeError, ValueError):
            pass

    return str(value)


def remove_octave_ghosts(
    groups: list[list[dict[str, Any]]],
) -> list[list[dict[str, Any]]]:
    """Remove weak octave echoes commonly produced by guitar harmonics."""
    cleaned: list[list[dict[str, Any]]] = []

    for group in groups:
        keep: list[dict[str, Any]] = []
        strongest = sorted(
            group,
            key=lambda note: float(note.get("amplitude") or 0),
            reverse=True,
        )

        for note in strongest:
            amplitude = float(note.get("amplitude") or 0)
            pitch = int(note["midi"])
            is_ghost = any(
                abs(pitch - int(existing["midi"])) == 12
                and amplitude
                < float(existing.get("amplitude") or 0)
                * OCTAVE_GHOST_RATIO
                for existing in keep
            )
            if not is_ghost:
                keep.append(note)

        keep.sort(key=lambda note: int(note["midi"]))
        if keep:
            cleaned.append(keep)

    return cleaned


def phrase_signature(
    phrase: list[list[dict[str, Any]]],
) -> tuple[tuple[int, ...], ...]:
    """Pitch-only phrase identity, independent of exact timing noise."""
    return tuple(
        tuple(sorted(int(note["midi"]) for note in group))
        for group in phrase
    )


def apply_cached_fingering(
    mapped: list[list[dict[str, Any]]],
    cached: list[dict[int, tuple[int, int]]],
    transcription_type: str,
) -> list[list[dict[str, Any]]]:
    """Reuse fingering for repeated riffs whenever it remains playable."""
    if len(mapped) != len(cached):
        return mapped

    result: list[list[dict[str, Any]]] = []

    for group, cached_group in zip(mapped, cached):
        used_strings: set[int] = set()
        rebuilt: list[dict[str, Any]] = []

        for event in sorted(group, key=lambda item: int(item["midi"]), reverse=True):
            midi = int(event["midi"])
            preferred = cached_group.get(midi)

            if preferred is not None:
                string_index, fret = preferred
                playable = (
                    string_index,
                    fret,
                ) in guitarist.engine.playable_positions(
                    midi,
                    transcription_type,
                )

                if playable and string_index not in used_strings:
                    event = {
                        **event,
                        "stringIndex": int(string_index),
                        "fret": int(fret),
                    }

            used_strings.add(int(event["stringIndex"]))
            rebuilt.append(event)

        result.append(rebuilt)

    return result


def repair_sustain_conflicts(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
) -> list[list[dict[str, Any]]]:
    """Avoid placing a new note on a string that should still be ringing."""
    active_until: dict[int, float] = {}
    repaired: list[list[dict[str, Any]]] = []

    for group in groups:
        group_start = min(float(event["start"]) for event in group)
        used_in_group: set[int] = set()
        next_group: list[dict[str, Any]] = []

        for event in sorted(
            group,
            key=lambda item: float(item.get("amplitude") or 0),
            reverse=True,
        ):
            current_string = int(event["stringIndex"])
            string_busy = (
                active_until.get(current_string, -1.0)
                > group_start + SUSTAIN_CONFLICT_TOLERANCE
            )

            if string_busy or current_string in used_in_group:
                alternatives = []
                for string_index, fret in guitarist.engine.playable_positions(
                    int(event["midi"]),
                    transcription_type,
                ):
                    if string_index in used_in_group:
                        continue
                    if (
                        active_until.get(string_index, -1.0)
                        > group_start + SUSTAIN_CONFLICT_TOLERANCE
                    ):
                        continue
                    movement = abs(fret - int(event["fret"]))
                    alternatives.append((movement, string_index, fret))

                if alternatives:
                    _, string_index, fret = min(alternatives)
                    event = {
                        **event,
                        "stringIndex": int(string_index),
                        "fret": int(fret),
                    }
                    current_string = string_index

            used_in_group.add(current_string)
            active_until[current_string] = max(
                active_until.get(current_string, -1.0),
                float(event.get("end") or group_start),
            )
            next_group.append(event)

        next_group.sort(key=lambda item: int(item["stringIndex"]))
        repaired.append(next_group)

    return repaired


def calculate_confidence(
    raw_count: int,
    cleaned_count: int,
    mapped_groups: list[list[dict[str, Any]]],
) -> float:
    if raw_count <= 0 or not mapped_groups:
        return 0.0

    retention = min(1.0, cleaned_count / raw_count)
    group_sizes = [len(group) for group in mapped_groups]
    playable_density = min(
        1.0,
        statistics.mean(group_sizes) / 2.5,
    )
    score = 0.45 + retention * 0.35 + playable_density * 0.20
    return round(min(0.98, max(0.05, score)), 3)


def analyze_audio_file(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    from basic_pitch.inference import predict

    _, _, note_events = predict(audio_path)

    extracted = [
        parsed
        for event in note_events
        if (
            parsed := guitarist.engine.extract_note_event(event)
        ) is not None
    ]

    cleaned = guitarist.clean_detected_notes(
        extracted,
        transcription_type,
    )
    onset_groups = guitarist.guitarist_group_notes(
        cleaned,
        transcription_type,
    )
    onset_groups = remove_octave_ghosts(onset_groups)
    phrases = guitarist.engine.split_phrases(onset_groups)

    original_local_cost = guitarist.engine.local_assignment_cost
    original_transition_cost = guitarist.engine.transition_cost
    guitarist.engine.local_assignment_cost = (
        guitarist.guitarist_local_assignment_cost
    )
    guitarist.engine.transition_cost = (
        guitarist.guitarist_transition_cost
    )

    phrase_cache: dict[
        tuple[tuple[int, ...], ...],
        list[dict[int, tuple[int, int]]],
    ] = {}
    mapped_groups: list[list[dict[str, Any]]] = []
    repeated_phrase_count = 0

    try:
        for phrase in phrases:
            mapped_phrase = guitarist.engine.map_phrase_to_fretboard(
                phrase,
                transcription_type,
            )
            signature = phrase_signature(phrase)
            cached = phrase_cache.get(signature)

            if cached is not None:
                mapped_phrase = apply_cached_fingering(
                    mapped_phrase,
                    cached,
                    transcription_type,
                )
                repeated_phrase_count += 1
            else:
                phrase_cache[signature] = [
                    {
                        int(event["midi"]): (
                            int(event["stringIndex"]),
                            int(event["fret"]),
                        )
                        for event in group
                    }
                    for group in mapped_phrase
                ]

            mapped_groups.extend(mapped_phrase)
    finally:
        guitarist.engine.local_assignment_cost = original_local_cost
        guitarist.engine.transition_cost = original_transition_cost

    mapped_groups = repair_sustain_conflicts(
        mapped_groups,
        transcription_type,
    )

    generated_tab = guitarist.engine.create_tab(
        mapped_groups,
        transcription_type,
    )
    flattened = [
        event
        for group in mapped_groups
        for event in group
    ]
    techniques = sorted(
        {
            event["technique"]
            for event in flattened
            if event.get("technique")
        }
    )

    return {
        "generatedTab": generated_tab,
        "tuning": (
            "Standard Bass"
            if transcription_type == "bass"
            else "E Standard"
        ),
        "tempo": None,
        "timeSignature": None,
        "keySignature": None,
        "difficulty": None,
        "techniques": techniques,
        "confidence": calculate_confidence(
            len(extracted),
            len(cleaned),
            mapped_groups,
        ),
        "events": flattened,
        "noteCount": len(flattened),
        "rawNoteCount": len(extracted),
        "cleanedNoteCount": len(cleaned),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
        "repeatedPhraseCount": repeated_phrase_count,
        "engineVersion": "1.8-guitarist-memory",
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
        raise HTTPException(
            status_code=401,
            detail="Unauthorized analyzer request.",
        )

    audio_url = str(payload.get("audioUrl") or "").strip()
    transcription_type = str(
        payload.get("transcriptionType") or ""
    ).strip().lower()

    if transcription_type not in {"lead", "rhythm", "bass"}:
        raise HTTPException(
            status_code=400,
            detail="transcriptionType must be lead, rhythm, or bass.",
        )

    if not audio_url.startswith(("https://", "http://")):
        raise HTTPException(
            status_code=400,
            detail="A valid audioUrl is required.",
        )

    suffix = Path(audio_url).suffix.lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        suffix = ".audio"

    blob_token = str(payload.get("blobToken") or "").strip()
    headers: dict[str, str] = {}
    if blob_token:
        headers["Authorization"] = f"Bearer {blob_token}"

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = Path(temp_dir) / f"uploaded{suffix}"

        try:
            response = requests.get(
                audio_url,
                headers=headers,
                timeout=120,
            )
        except requests.RequestException as error:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            )

        if len(response.content) > guitarist.engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

        audio_path.write_bytes(response.content)

        try:
            original_metadata = guitarist.engine.inspect_audio_file(
                str(audio_path)
            )
            guitarist.engine.validate_audio_metadata(original_metadata)

            normalized_path = Path(temp_dir) / "normalized.wav"
            guitarist.engine.normalize_audio_file(
                str(audio_path),
                str(normalized_path),
            )
            normalized_metadata = guitarist.engine.inspect_audio_file(
                str(normalized_path)
            )
            result = analyze_audio_file(
                str(normalized_path),
                transcription_type,
            )
        except ValueError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
