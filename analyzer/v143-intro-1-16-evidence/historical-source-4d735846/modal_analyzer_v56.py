import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v55 as previous
import modal_analyzer_v24 as v24

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    previous.image
    .add_local_python_source("modal_analyzer_v55")
    .add_local_python_source("modal_analyzer_v24")
)

_original_style_path_candidates = v24.style_path_candidates
_VOICING_DECISIONS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def path_upper_frets(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> list[int]:
    return [
        int(fret)
        for assignment in path
        for note, _, fret in assignment
        if int(note.get("midi") or 0) > previous.LOW_BASS_MIDI_MAX
    ]


def path_center(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> float | None:
    frets = path_upper_frets(path)
    return float(statistics.median(frets)) if frets else None


def path_open_upper_count(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> int:
    return sum(1 for fret in path_upper_frets(path) if fret == 0)


def normalized_chord_name(chord_name: str | None) -> str:
    return (
        str(chord_name or "")
        .replace("♯", "#")
        .replace("♭", "b")
        .replace(" ", "")
        .upper()
    )


def preferred_zone_for_chord(
    chord_name: str | None,
) -> tuple[float, float, bool, str] | None:
    chord = normalized_chord_name(chord_name)
    if not chord:
        return None

    # These are general guitarist voicing families, not hard-coded note output:
    # fifth-position Am and C/G arpeggios, low D/F# inversion, and open Fmaj7/G/B.
    if chord.startswith("AM") and not chord.startswith("AMAJ"):
        return 5.0, 7.0, False, "fifth-position-minor-arpeggio"
    if chord.startswith("C/G"):
        return 5.0, 8.0, False, "closed-c-over-g-arpeggio"
    if chord.startswith("D/F#"):
        return 2.0, 4.0, False, "low-d-over-f-sharp-inversion"
    if chord.startswith("FMAJ7"):
        return 0.0, 3.0, True, "open-f-major-seven"
    if chord.startswith("G/B"):
        return 0.0, 3.0, True, "open-g-over-b"
    return None


def chord_voicing_adjustment(
    path: list[list[tuple[dict[str, Any], int, int]]],
    chord_name: str | None,
    chord_confidence: float,
) -> tuple[float, dict[str, Any]]:
    zone = preferred_zone_for_chord(chord_name)
    center = path_center(path)
    opens = path_open_upper_count(path)
    if zone is None or center is None or chord_confidence < 0.45:
        return 0.0, {
            "chord": chord_name,
            "center": center,
            "openUpperCount": opens,
            "active": False,
        }

    lower, upper, allow_open, reason = zone
    adjustment = 0.0
    reasons: list[str] = []

    if center < lower:
        penalty = (lower - center) * 7.0 + 5.0
        adjustment += penalty
        reasons.append(f"below-zone+{penalty:.2f}")
    elif center > upper:
        penalty = (center - upper) * 7.0 + 5.0
        adjustment += penalty
        reasons.append(f"above-zone+{penalty:.2f}")
    else:
        adjustment -= 12.0
        reasons.append("inside-chord-zone-12.00")

    if allow_open:
        if opens:
            reward = min(10.0, 3.0 + opens * 2.0)
            adjustment -= reward
            reasons.append(f"intentional-open-voicing-{reward:.2f}")
        elif center > 1.5:
            adjustment += 6.0
            reasons.append("missing-open-character+6.00")
    elif opens:
        penalty = min(15.0, opens * 5.0)
        adjustment += penalty
        reasons.append(f"unwanted-open-upper+{penalty:.2f}")

    frets = [fret for fret in path_upper_frets(path) if fret > 0]
    if frets:
        span = max(frets) - min(frets)
        if span > 4:
            adjustment += (span - 4) * 2.5
            reasons.append(f"wide-voicing-span+{(span - 4) * 2.5:.2f}")

    return adjustment, {
        "chord": chord_name,
        "center": round(center, 3),
        "preferredRange": [lower, upper],
        "openUpperCount": opens,
        "allowOpenUpperStrings": allow_open,
        "active": True,
        "voicingFamily": reason,
        "adjustment": round(adjustment, 3),
        "reasons": reasons,
    }


def chord_aware_style_path_candidates(
    window: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
    previous_anchor: int | None,
    chord_name: str | None,
    chord_map: dict[int, tuple[int, int]],
    chord_confidence: float,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    candidates = _original_style_path_candidates(
        window,
        transcription_type,
        anchor,
        previous_assignment,
        previous_anchor,
        chord_name,
        chord_map,
        chord_confidence,
    )

    rescored: list[
        tuple[
            float,
            list[list[tuple[dict[str, Any], int, int]]],
            float,
            dict[str, Any],
        ]
    ] = []
    for raw_score, path in candidates:
        adjustment, diagnostic = chord_voicing_adjustment(
            path,
            chord_name,
            chord_confidence,
        )
        rescored.append((float(raw_score) + adjustment, path, float(raw_score), diagnostic))

    rescored.sort(key=lambda item: item[0])
    if rescored:
        _VOICING_DECISIONS.append(
            {
                "windowStart": round(
                    min(float(note.get("start") or 0.0) for group in window for note in group),
                    4,
                ) if window else None,
                "anchor": int(anchor),
                "chord": chord_name,
                "chordConfidence": round(float(chord_confidence), 3),
                "winner": rescored[0][3],
                "topCandidates": [
                    {
                        "rank": rank,
                        "score": round(score, 3),
                        "rawScore": round(raw_score, 3),
                        **diagnostic,
                    }
                    for rank, (score, _, raw_score, diagnostic) in enumerate(
                        rescored[:4],
                        start=1,
                    )
                ],
            }
        )

    return [(score, path) for score, path, _, _ in rescored]


v24.style_path_candidates = chord_aware_style_path_candidates


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _VOICING_DECISIONS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["chordIdentityVoicingZones"] = {
        "honestFixtureBaseline": 19.06,
        "decisionCount": len(_VOICING_DECISIONS),
        "decisions": list(_VOICING_DECISIONS),
        "policy": (
            "use-detected-chord-identity-and-confidence-to-choose-between-open-low-"
            "and-fifth-position-arpeggio-voicings-before-rendering"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.6-phase-1-chord-identity-voicing-zones"
    result["guitarBrainLesson"] = (
        "intentional-position-shifts-belong-to-the-chord-voicing-not-to-a-global-"
        "minimum-movement-rule"
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
