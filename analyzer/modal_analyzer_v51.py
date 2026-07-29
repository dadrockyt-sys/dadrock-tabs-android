import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v47 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v47")

v25 = previous.v25
_original_v47_builder = previous.reranked_build_phrase_paths
_SELECTED_PATHS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_rows(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_index, assignment in enumerate(path):
        for note, string_index, fret in assignment:
            rows.append(
                {
                    "groupIndex": group_index,
                    "start": round(float(note.get("start") or 0.0), 4),
                    "end": round(float(note.get("end") or note.get("end_time") or 0.0), 4),
                    "midi": int(note.get("midi") or note.get("pitch") or 0),
                    "stringIndex": int(string_index),
                    "fret": int(fret),
                }
            )
    return rows


def tracing_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    paths = _original_v47_builder(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )
    if paths:
        phrase_start = None
        if groups and groups[0]:
            phrase_start = round(float(groups[0][0].get("start") or 0.0), 4)
        winner_score, winner_path = paths[0]
        profile = previous.previous.path_region_profile(winner_path)
        _SELECTED_PATHS.append(
            {
                "phraseIndex": len(_SELECTED_PATHS),
                "phraseStart": phrase_start,
                "anchor": int(anchor),
                "winnerScore": round(float(winner_score), 3),
                "winnerUpperCenter": profile.get("pathUpperCenter"),
                "winnerDominantRegion": profile.get("dominantRegion"),
                "selectedAssignments": assignment_rows(winner_path),
            }
        )
    return paths


v25.build_phrase_paths = tracing_build_phrase_paths


def is_final_event(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and "fret" in value
        and ("stringIndex" in value or "string_index" in value)
        and any(key in value for key in ("start", "startTime", "start_time"))
    )


def collect_event_lists(value: Any, path: str = "result") -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            found.extend(collect_event_lists(child, f"{path}.{key}"))
    elif isinstance(value, list):
        matching = [item for item in value if is_final_event(item)]
        if matching:
            found.append(
                {
                    "jsonPath": path,
                    "eventCount": len(matching),
                    "events": matching,
                }
            )
        for index, child in enumerate(value):
            if isinstance(child, (dict, list)):
                found.extend(collect_event_lists(child, f"{path}[{index}]"))
    return found


def normalized_event(event: dict[str, Any]) -> dict[str, Any]:
    start = event.get("start")
    if start is None:
        start = event.get("startTime")
    if start is None:
        start = event.get("start_time")
    string_index = event.get("stringIndex")
    if string_index is None:
        string_index = event.get("string_index")
    midi = event.get("midi")
    if midi is None:
        midi = event.get("pitch")
    return {
        "start": round(float(start or 0.0), 4),
        "midi": int(midi or 0),
        "stringIndex": int(string_index or 0),
        "fret": int(event.get("fret") or 0),
    }


def compare_selected_to_final(
    selected: list[dict[str, Any]],
    final_events: list[dict[str, Any]],
) -> dict[str, Any]:
    final_rows = [normalized_event(event) for event in final_events]
    mismatches: list[dict[str, Any]] = []
    matches = 0

    for phrase in selected:
        for chosen in phrase["selectedAssignments"]:
            candidates = [
                event
                for event in final_rows
                if abs(event["start"] - chosen["start"]) <= 0.015
                and (not chosen["midi"] or not event["midi"] or event["midi"] == chosen["midi"])
            ]
            if not candidates:
                continue
            final = min(candidates, key=lambda item: abs(item["start"] - chosen["start"]))
            if final["stringIndex"] == chosen["stringIndex"] and final["fret"] == chosen["fret"]:
                matches += 1
            else:
                mismatches.append(
                    {
                        "phraseIndex": phrase["phraseIndex"],
                        "start": chosen["start"],
                        "midi": chosen["midi"],
                        "selected": {
                            "stringIndex": chosen["stringIndex"],
                            "fret": chosen["fret"],
                        },
                        "final": {
                            "stringIndex": final["stringIndex"],
                            "fret": final["fret"],
                        },
                    }
                )

    return {
        "matchedAssignments": matches,
        "mismatchCount": len(mismatches),
        "mismatches": mismatches[:100],
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _SELECTED_PATHS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    discovered = collect_event_lists(result)
    best_list = max(discovered, key=lambda item: item["eventCount"], default=None)
    comparison = (
        compare_selected_to_final(_SELECTED_PATHS, best_list["events"])
        if best_list is not None
        else {"matchedAssignments": 0, "mismatchCount": 0, "mismatches": []}
    )

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["pathToFinalEventHandoff"] = {
        "benchmarkBaseline": 63.0,
        "selectedPhraseCount": len(_SELECTED_PATHS),
        "selectedPaths": list(_SELECTED_PATHS),
        "discoveredEventLists": [
            {"jsonPath": item["jsonPath"], "eventCount": item["eventCount"]}
            for item in discovered
        ],
        "comparedEventList": best_list["jsonPath"] if best_list else None,
        **comparison,
        "policy": "compare-the-v47-winning-string-and-fret-assignments-with-the-final-events-returned-to-the-tab-renderer",
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.1-phase-1-path-to-final-event-handoff-diagnostics"
    result["guitarBrainLesson"] = "verify-whether-winning-phrase-fingerings-survive-normalization-and-render-preparation"
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
