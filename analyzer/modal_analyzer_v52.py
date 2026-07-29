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
_original_render_path = v25.render_path
_RENDER_HANDOFFS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def selected_rows(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_index, assignment in enumerate(path):
        for note, string_index, fret in assignment:
            rows.append(
                {
                    "groupIndex": group_index,
                    "start": round(float(note.get("start") or 0.0), 4),
                    "midi": int(note.get("midi") or note.get("pitch") or 0),
                    "stringIndex": int(string_index),
                    "fret": int(fret),
                }
            )
    return rows


def rendered_rows(groups: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group_index, group in enumerate(groups):
        for event in group:
            string_index = event.get("stringIndex")
            if string_index is None:
                string_index = event.get("string_index")
            start = event.get("start")
            if start is None:
                start = event.get("startTime")
            if start is None:
                start = event.get("start_time")
            midi = event.get("midi")
            if midi is None:
                midi = event.get("pitch")
            rows.append(
                {
                    "groupIndex": group_index,
                    "start": round(float(start or 0.0), 4),
                    "midi": int(midi or 0),
                    "stringIndex": int(string_index or 0),
                    "fret": int(event.get("fret") or 0),
                }
            )
    return rows


def compare_rows(
    selected: list[dict[str, Any]],
    rendered: list[dict[str, Any]],
) -> dict[str, Any]:
    mismatches: list[dict[str, Any]] = []
    matches = 0
    missing = 0

    unused = list(rendered)
    for chosen in selected:
        candidates = [
            event
            for event in unused
            if event["groupIndex"] == chosen["groupIndex"]
            and abs(event["start"] - chosen["start"]) <= 0.015
            and (not chosen["midi"] or not event["midi"] or event["midi"] == chosen["midi"])
        ]
        if not candidates:
            missing += 1
            continue
        final = min(candidates, key=lambda item: abs(item["start"] - chosen["start"]))
        unused.remove(final)
        if final["stringIndex"] == chosen["stringIndex"] and final["fret"] == chosen["fret"]:
            matches += 1
        else:
            mismatches.append(
                {
                    "start": chosen["start"],
                    "midi": chosen["midi"],
                    "selected": {
                        "stringIndex": chosen["stringIndex"],
                        "fret": chosen["fret"],
                    },
                    "rendered": {
                        "stringIndex": final["stringIndex"],
                        "fret": final["fret"],
                    },
                }
            )

    return {
        "matchedAssignments": matches,
        "mismatchCount": len(mismatches),
        "missingAssignments": missing,
        "mismatches": mismatches,
    }


def tracing_render_path(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[list[dict[str, Any]]]:
    rendered = _original_render_path(path)
    chosen = selected_rows(path)
    output = rendered_rows(rendered)
    profile = previous.previous.path_region_profile(path)
    comparison = compare_rows(chosen, output)
    _RENDER_HANDOFFS.append(
        {
            "windowIndex": len(_RENDER_HANDOFFS),
            "pathUpperCenter": profile.get("pathUpperCenter"),
            "dominantRegion": profile.get("dominantRegion"),
            "selectedCount": len(chosen),
            "renderedCount": len(output),
            **comparison,
        }
    )
    return rendered


# render_path is called only after the cross-anchor ranking has selected the
# actual winning path for a harmonic window. This avoids v51's false positives
# from tracing every anchor candidate before the final winner was known.
v25.render_path = tracing_render_path


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _RENDER_HANDOFFS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    total_matches = sum(item["matchedAssignments"] for item in _RENDER_HANDOFFS)
    total_mismatches = sum(item["mismatchCount"] for item in _RENDER_HANDOFFS)
    total_missing = sum(item["missingAssignments"] for item in _RENDER_HANDOFFS)

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["winningPathRenderHandoff"] = {
        "benchmarkBaseline": 63.0,
        "windowCount": len(_RENDER_HANDOFFS),
        "matchedAssignments": total_matches,
        "mismatchCount": total_mismatches,
        "missingAssignments": total_missing,
        "windows": list(_RENDER_HANDOFFS),
        "policy": (
            "trace-only-the-cross-anchor-winning-path-at-the-exact-render-path-"
            "handoff-and-compare-its-string-fret-assignments-to-rendered-events"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.2-phase-1-winning-path-render-handoff-diagnostics"
    result["guitarBrainLesson"] = (
        "separate-real-render-remapping-from-false-mismatches-caused-by-tracing-losing-anchor-candidates"
    )
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
