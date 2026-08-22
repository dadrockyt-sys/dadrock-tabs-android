import itertools
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v24 as previous

base = previous.base
engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v24")

ANCHORS = (0, 2, 5, 7, 9, 12)
GROUP_CANDIDATE_LIMIT = 28
PATH_BEAM_WIDTH = 48
MAX_FRET_SPAN = 5
MAX_STRING_SPAN = 5


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_key(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        sorted(
            (int(note["midi"]), int(string_index), int(fret))
            for note, string_index, fret in assignment
        )
    )


def all_group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
    anchor: int,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    """Generate real fretboard alternatives instead of inheriting one narrow candidate set."""
    if not group:
        return []

    note_options: list[list[tuple[dict[str, Any], int, int]]] = []
    for note in sorted(group, key=lambda item: int(item["midi"]), reverse=True):
        positions = engine.playable_positions(int(note["midi"]), transcription_type)
        ranked: list[tuple[float, dict[str, Any], int, int]] = []
        for string_index, fret in positions:
            distance = abs(float(fret) - float(anchor))
            open_bonus = -1.0 if fret == 0 and anchor <= 2 else 0.0
            high_fret_penalty = max(0, fret - 15) * 0.5
            ranked.append(
                (
                    distance + open_bonus + high_fret_penalty,
                    note,
                    int(string_index),
                    int(fret),
                )
            )
        ranked.sort(key=lambda item: item[0])
        note_options.append(
            [(note_value, string_index, fret) for _, note_value, string_index, fret in ranked[:6]]
        )

    candidates: list[list[tuple[dict[str, Any], int, int]]] = []
    for combination in itertools.product(*note_options):
        strings = [item[1] for item in combination]
        if len(set(strings)) != len(strings):
            continue
        if max(strings) - min(strings) > MAX_STRING_SPAN:
            continue

        frets = [item[2] for item in combination if item[2] > 0]
        if frets and max(frets) - min(frets) > MAX_FRET_SPAN:
            continue

        candidates.append(list(combination))

    def initial_cost(candidate: list[tuple[dict[str, Any], int, int]]) -> float:
        frets = [item[2] for item in candidate]
        non_open = [fret for fret in frets if fret > 0]
        strings = [item[1] for item in candidate]
        cost = 0.0
        if non_open:
            cost += abs(statistics.median(non_open) - anchor) * 1.2
            cost += (max(non_open) - min(non_open)) * 1.4
        cost += (max(strings) - min(strings)) * 0.45
        cost -= sum(1 for fret in frets if fret == 0 and anchor <= 2) * 0.7
        return cost

    candidates.sort(key=initial_cost)
    return candidates[:GROUP_CANDIDATE_LIMIT]


def ringing_conflict_cost(
    prior: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
) -> float:
    if not prior:
        return 0.0

    current_start = min(float(note["start"]) for note, _, _ in current)
    ringing_strings = {
        string_index
        for note, string_index, _ in prior
        if float(note.get("end") or note["start"]) > current_start + 0.04
    }
    reused = sum(1 for _, string_index, _ in current if string_index in ringing_strings)
    return reused * 3.8


def phrase_movement_cost(
    prior: list[tuple[dict[str, Any], int, int]] | None,
    current: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    cost = previous.previous.previous.previous.guitarist_movement_cost(
        prior,
        current,
        anchor,
        anchor,
    )
    cost += ringing_conflict_cost(prior, current)

    if prior:
        prior_strings = [item[1] for item in prior]
        current_strings = [item[1] for item in current]
        crossing = abs(statistics.mean(current_strings) - statistics.mean(prior_strings))
        cost += max(0.0, crossing - 1.5) * 1.6

        if len(prior) == 1 and len(current) == 1:
            _, old_string, old_fret = prior[0]
            _, new_string, new_fret = current[0]
            if old_string == new_string and abs(new_fret - old_fret) <= 4:
                cost -= 2.2
            elif abs(new_string - old_string) >= 3:
                cost += 2.4

    return cost


def guitarist_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    cost = previous.previous.previous.previous.chord_shape_cost(
        assignment,
        transcription_type,
        anchor,
    )
    frets = [item[2] for item in assignment]
    strings = [item[1] for item in assignment]
    non_open = [fret for fret in frets if fret > 0]

    if non_open:
        span = max(non_open) - min(non_open)
        if span > 4:
            cost += (span - 4) * 7.0
        if statistics.median(non_open) > 12 and anchor < 10:
            cost += 5.0

    if len(strings) >= 2:
        gaps = max(strings) - min(strings) + 1 - len(set(strings))
        cost += gaps * 2.3

    # Keep the melodic top voice on the high E/B/G strings where practical.
    highest = max(assignment, key=lambda item: int(item[0]["midi"]))
    if transcription_type == "lead":
        if highest[1] <= 2:
            cost -= 1.5
        else:
            cost += 1.4

    return cost


def build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = [(0.0, [])]

    for group in groups:
        assignments = all_group_assignments(group, transcription_type, anchor)
        if not assignments:
            assignments = previous.previous.previous.previous.previous.group_assignments(
                group,
                transcription_type,
                anchor,
            )

        next_beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            for assignment in assignments:
                cost = accumulated
                cost += guitarist_assignment_cost(assignment, transcription_type, anchor)
                cost += phrase_movement_cost(prior, assignment, anchor)
                next_beam.append((cost, path + [assignment]))

        next_beam.sort(key=lambda item: item[0])
        beam = next_beam[:PATH_BEAM_WIDTH]

    rescored: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
    for base_cost, path in beam:
        metrics = previous.previous.path_metrics(path)
        total = base_cost
        total += metrics["positionShiftTotal"] * 1.4
        total += metrics["largeShiftCount"] * 9.0
        total -= metrics["repeatConsistency"] * 5.5
        rescored.append((total, path))

    rescored.sort(key=lambda item: item[0])
    return rescored[:4]


def render_path(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[list[dict[str, Any]]]:
    mapped: list[list[dict[str, Any]]] = []
    for assignment in path:
        mapped_group: list[dict[str, Any]] = []
        for note, string_index, fret in assignment:
            bend = engine.estimate_bend_semitones(note.get("pitchBends"))
            mapped_group.append(
                {
                    **note,
                    "stringIndex": int(string_index),
                    "fret": int(fret),
                    "technique": "bend" if bend >= 0.35 else None,
                    "bendSemitones": round(float(bend), 2),
                }
            )
        mapped.append(mapped_group)
    return mapped


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

    mapped_groups: list[list[dict[str, Any]]] = []
    diagnostics: list[dict[str, Any]] = []
    previous_assignment = None
    previous_anchor = None

    for phrase_index, phrase in enumerate(phrases):
        anchors = list(ANCHORS)
        if previous_anchor is not None:
            anchors.insert(0, previous_anchor)

        ranked: list[tuple[float, int, list[list[tuple[dict[str, Any], int, int]]]]] = []
        for anchor in dict.fromkeys(anchors):
            for score, path in build_phrase_paths(
                phrase,
                transcription_type,
                int(anchor),
                previous_assignment,
            ):
                anchor_shift = 0.0
                if previous_anchor is not None:
                    anchor_shift = abs(int(anchor) - int(previous_anchor)) * 1.4
                ranked.append((score + anchor_shift, int(anchor), path))

        if not ranked:
            continue
        ranked.sort(key=lambda item: item[0])
        winning_score, winning_anchor, winning_path = ranked[0]
        mapped_groups.extend(render_path(winning_path))
        previous_assignment = winning_path[-1] if winning_path else previous_assignment
        previous_anchor = winning_anchor

        diagnostics.append(
            {
                "phraseIndex": phrase_index,
                "chosenAnchor": winning_anchor,
                "winningScore": round(float(winning_score), 3),
                "topCandidates": [
                    {
                        "anchor": anchor,
                        "score": round(float(score), 3),
                        "metrics": previous.previous.path_metrics(path),
                    }
                    for score, anchor, path in ranked[:4]
                ],
            }
        )

    generated_tab = engine.create_tab(mapped_groups, transcription_type)
    flattened = [event for group in mapped_groups for event in group]

    return {
        "generatedTab": generated_tab,
        "tuning": "Standard Bass" if transcription_type == "bass" else "E Standard",
        "tempo": None,
        "timeSignature": None,
        "keySignature": None,
        "difficulty": None,
        "techniques": sorted(
            {
                event["technique"]
                for event in flattened
                if event.get("technique")
            }
        ),
        "confidence": None,
        "events": flattened,
        "noteCount": len(flattened),
        "rawNoteCount": len(extracted),
        "cleanedNoteCount": len(cleaned),
        "onsetGroupCount": len(mapped_groups),
        "phraseCount": len(phrases),
        "candidateDiagnostics": diagnostics,
        "styleProfile": "phrase-first-classic-rock-guitarist",
        "engineVersion": "2.5-phrase-first-fretboard-intelligence",
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
