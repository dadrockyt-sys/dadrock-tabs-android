import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v46 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v46")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
_original_build_phrase_paths = previous._original_build_phrase_paths
_RERANK_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def upper_notes_have_mid_options(
    path: list[list[tuple[dict[str, Any], int, int]]],
    transcription_type: str,
) -> bool:
    notes: list[dict[str, Any]] = []
    for assignment in path:
        for note, _, _ in assignment:
            if int(note["midi"]) > LOW_BASS_MIDI_MAX:
                notes.append(note)

    if not notes:
        return False

    return all(
        any(
            4 <= int(fret) <= 9
            for _, fret in engine.playable_positions(
                int(note["midi"]),
                transcription_type,
            )
        )
        for note in notes
    )


def path_open_upper_count(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> int:
    return sum(
        1
        for assignment in path
        for note, _, fret in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX and int(fret) == 0
    )


def whole_path_region_adjustment(
    path: list[list[tuple[dict[str, Any], int, int]]],
    transcription_type: str,
    anchor: int,
) -> tuple[float, dict[str, Any]]:
    """Apply musical region judgment after complete paths exist.

    Earlier lessons modified callbacks inside the beam but repeatedly left the
    winner unchanged. V46 proved that genuinely different whole-path candidates
    survive with modest score gaps. This lesson reranks those complete paths.
    """
    profile = previous.path_region_profile(path)
    center_value = profile.get("pathUpperCenter")
    center = float(center_value) if center_value is not None else 0.0
    dominant = str(profile.get("dominantRegion") or "open")
    opens = path_open_upper_count(path)
    mid_available = upper_notes_have_mid_options(path, transcription_type)

    adjustment = 0.0
    reasons: list[str] = []

    if int(anchor) <= 3:
        # A genuinely low harmonic anchor should release toward the nut instead
        # of allowing persistent upper memory to hold the entire phrase at 7-9.
        if center > 5.0:
            penalty = (center - 5.0) * 4.5 + 5.0
            adjustment += penalty
            reasons.append(f"low-anchor-high-path+{penalty:.2f}")
        elif dominant in {"open", "low"}:
            adjustment -= 5.0
            reasons.append("low-anchor-release-5.00")

    elif 4 <= int(anchor) <= 9:
        # Established middle-neck phrase: park in the 5-8 box and reject both
        # open collapse and unnecessary climbing.
        if 5.0 <= center <= 8.0:
            adjustment -= 8.0
            reasons.append("mid-anchor-box-8.00")
        elif center < 4.0 and mid_available:
            penalty = (4.0 - center) * 6.0 + 8.0
            adjustment += penalty
            reasons.append(f"mid-anchor-low-path+{penalty:.2f}")
        elif center > 9.0 and mid_available:
            penalty = (center - 9.0) * 6.0 + 8.0
            adjustment += penalty
            reasons.append(f"mid-anchor-high-path+{penalty:.2f}")

    else:
        # A high melodic anchor does not automatically require moving the whole
        # shape high. Prefer a compact mid-neck equivalent when every pitch has one.
        if mid_available and 5.0 <= center <= 9.0:
            adjustment -= 7.0
            reasons.append("high-anchor-mid-equivalent-7.00")
        elif mid_available and center > 9.0:
            penalty = (center - 9.0) * 5.0 + 4.0
            adjustment += penalty
            reasons.append(f"avoidable-high-whole-path+{penalty:.2f}")

    if opens and int(anchor) >= 4 and mid_available:
        penalty = min(18.0, opens * 6.0)
        adjustment += penalty
        reasons.append(f"upper-open-collapse+{penalty:.2f}")

    return adjustment, {
        **profile,
        "upperOpenCount": opens,
        "midEquivalentAvailable": mid_available,
        "adjustment": round(adjustment, 3),
        "reasons": reasons,
    }


def reranked_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    raw_paths = _original_build_phrase_paths(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )

    reranked: list[
        tuple[
            float,
            list[list[tuple[dict[str, Any], int, int]]],
            float,
            dict[str, Any],
        ]
    ] = []

    for raw_score, path in raw_paths:
        adjustment, profile = whole_path_region_adjustment(
            path,
            transcription_type,
            anchor,
        )
        reranked.append(
            (float(raw_score) + adjustment, path, float(raw_score), profile)
        )

    reranked.sort(key=lambda item: item[0])

    phrase_start = None
    if groups and groups[0]:
        phrase_start = round(float(groups[0][0].get("start") or 0.0), 3)

    winner_raw_rank = None
    if reranked:
        winner_path = reranked[0][1]
        winner_raw_rank = next(
            (
                index
                for index, (_, path) in enumerate(raw_paths, start=1)
                if path == winner_path
            ),
            None,
        )

    _RERANK_DIAGNOSTICS.append(
        {
            "phraseIndex": len(_RERANK_DIAGNOSTICS),
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "winnerRawRank": winner_raw_rank,
            "topCandidates": [
                {
                    "rerankedRank": rank,
                    "rerankedScore": round(score, 3),
                    "rawScore": round(raw_score, 3),
                    **profile,
                }
                for rank, (score, _, raw_score, profile) in enumerate(
                    reranked[:6],
                    start=1,
                )
            ],
        }
    )

    return [(score, path) for score, path, _, _ in reranked]


v25.build_phrase_paths = reranked_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _RERANK_DIAGNOSTICS.clear()
    result = previous.previous.previous.analyze_audio_file(
        audio_path,
        transcription_type,
    )
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["wholePathReranking"] = {
        "benchmarkBaseline": 53.0,
        "phraseCount": len(_RERANK_DIAGNOSTICS),
        "phrases": list(_RERANK_DIAGNOSTICS),
        "policy": (
            "rerank-complete-surviving-paths-by-harmonic-anchor-and-whole-path-"
            "hand-region-instead-of-hoping-local-callback-weights-change-the-winner"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.7-phase-1-whole-path-reranking"
    result["guitarBrainLesson"] = (
        "choose-between-complete-low-mid-and-high-fingering-paths-after-the-beam-has-built-them"
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
        raise HTTPException(
            status_code=400,
            detail="transcriptionType must be lead, rhythm, or bass.",
        )
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
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            ) from error

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail="The analyzer could not download the audio file.",
            )
        if len(response.content) > engine.MAX_AUDIO_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail="The uploaded audio cannot be larger than 50 MB.",
            )

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
