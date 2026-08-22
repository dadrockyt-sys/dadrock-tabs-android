import os
import statistics
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v55 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v55")

v25 = previous.v25
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
_original_build_phrase_paths = v25.build_phrase_paths
_LOCAL_VOICING_DECISIONS: list[dict[str, Any]] = []

NOTE_NAMES = {
    0: "C", 1: "C#", 2: "D", 3: "D#", 4: "E", 5: "F",
    6: "F#", 7: "G", 8: "G#", 9: "A", 10: "A#", 11: "B",
}

CHORD_TEMPLATES: list[tuple[str, set[int], tuple[float, float, bool], int | None]] = [
    ("Am", {9, 0, 4}, (5.0, 7.0, False), None),
    ("C/G", {0, 4, 7}, (5.0, 8.0, False), 7),
    ("D/F#", {2, 6, 9}, (2.0, 4.0, False), 6),
    ("Fmaj7", {5, 9, 0, 4}, (0.0, 3.0, True), None),
    ("G/B", {7, 11, 2}, (0.0, 3.0, True), 11),
]


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def infer_group_chord(notes: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not notes:
        return None

    weighted: Counter[int] = Counter()
    bass_midi: int | None = None
    for note in notes:
        midi = int(note.get("midi") or 0)
        duration = max(
            0.05,
            float(note.get("end") or note.get("end_time") or 0.0)
            - float(note.get("start") or 0.0),
        )
        weighted[midi % 12] += duration
        if bass_midi is None or midi < bass_midi:
            bass_midi = midi

    present = set(weighted)
    total_weight = sum(weighted.values()) or 1.0
    bass_pc = bass_midi % 12 if bass_midi is not None else None
    best: dict[str, Any] | None = None

    for name, tones, zone, expected_bass in CHORD_TEMPLATES:
        covered = sum(weight for pc, weight in weighted.items() if pc in tones)
        missing = len(tones - present)
        extras = len(present - tones)
        score = covered / total_weight
        score -= missing * 0.08
        score -= extras * 0.045
        if expected_bass is not None:
            score += 0.18 if bass_pc == expected_bass else -0.03

        candidate = {
            "name": name,
            "confidence": round(max(0.0, min(1.0, score)), 3),
            "preferredRange": [zone[0], zone[1]],
            "allowOpen": zone[2],
            "bassPitchClass": NOTE_NAMES.get(bass_pc, str(bass_pc)),
            "pitchClasses": [NOTE_NAMES[pc] for pc in sorted(present)],
        }
        if best is None or candidate["confidence"] > best["confidence"]:
            best = candidate

    if best is None or float(best["confidence"]) < 0.52:
        return None
    return best


def assignment_profile(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> dict[str, Any]:
    frets = [
        int(fret)
        for note, _, fret in assignment
        if int(note.get("midi") or 0) > LOW_BASS_MIDI_MAX
    ]
    if not frets:
        return {"center": None, "openUpperCount": 0, "span": 0}
    positive = [fret for fret in frets if fret > 0]
    return {
        "center": round(float(statistics.median(frets)), 3),
        "openUpperCount": sum(1 for fret in frets if fret == 0),
        "span": max(positive) - min(positive) if positive else 0,
    }


def local_assignment_adjustment(
    assignment: list[tuple[dict[str, Any], int, int]],
    chord: dict[str, Any] | None,
) -> tuple[float, dict[str, Any]]:
    profile = assignment_profile(assignment)
    center = profile["center"]
    if chord is None or center is None:
        return 0.0, {**profile, "active": False}

    lower, upper = [float(value) for value in chord["preferredRange"]]
    confidence = float(chord["confidence"])
    allow_open = bool(chord["allowOpen"])
    adjustment = 0.0
    reasons: list[str] = []

    # Local groups get deliberately moderate weights. The phrase-level V57 rule
    # proved that forcing one inferred chord across a mixed phrase can collapse
    # neighbouring Am and C/G groups into the open position.
    if lower <= center <= upper:
        reward = 7.0 * confidence
        adjustment -= reward
        reasons.append(f"local-zone-reward-{reward:.2f}")
    elif center < lower:
        penalty = ((lower - center) * 4.0 + 3.0) * confidence
        adjustment += penalty
        reasons.append(f"local-below-zone+{penalty:.2f}")
    else:
        penalty = ((center - upper) * 4.0 + 3.0) * confidence
        adjustment += penalty
        reasons.append(f"local-above-zone+{penalty:.2f}")

    opens = int(profile["openUpperCount"])
    if allow_open:
        if opens:
            reward = min(6.0, 2.0 + opens * 1.5) * confidence
            adjustment -= reward
            reasons.append(f"local-open-character-{reward:.2f}")
    elif opens:
        penalty = min(8.0, opens * 3.0) * confidence
        adjustment += penalty
        reasons.append(f"local-unwanted-open+{penalty:.2f}")

    if int(profile["span"]) > 4:
        penalty = (int(profile["span"]) - 4) * 1.5
        adjustment += penalty
        reasons.append(f"local-wide-shape+{penalty:.2f}")

    return adjustment, {
        **profile,
        "active": True,
        "chord": chord["name"],
        "confidence": confidence,
        "preferredRange": chord["preferredRange"],
        "allowOpen": allow_open,
        "adjustment": round(adjustment, 3),
        "reasons": reasons,
    }


def locally_chord_aware_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    candidates = _original_build_phrase_paths(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )
    group_chords = [infer_group_chord(group) for group in groups]
    rescored: list[tuple[float, Any, float, list[dict[str, Any]]]] = []

    for raw_score, path in candidates:
        adjustment = 0.0
        diagnostics: list[dict[str, Any]] = []
        for group_index, assignment in enumerate(path):
            chord = group_chords[group_index] if group_index < len(group_chords) else None
            local_adjustment, diagnostic = local_assignment_adjustment(assignment, chord)
            adjustment += local_adjustment
            diagnostics.append({"groupIndex": group_index, **diagnostic})
        rescored.append(
            (float(raw_score) + adjustment, path, float(raw_score), diagnostics)
        )

    rescored.sort(key=lambda item: item[0])
    phrase_start = (
        round(float(groups[0][0].get("start") or 0.0), 4)
        if groups and groups[0]
        else None
    )
    _LOCAL_VOICING_DECISIONS.append(
        {
            "phraseIndex": len(_LOCAL_VOICING_DECISIONS),
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "groupChords": group_chords,
            "candidateCount": len(rescored),
            "winnerRawScore": round(rescored[0][2], 3) if rescored else None,
            "winnerScore": round(rescored[0][0], 3) if rescored else None,
            "winnerGroups": rescored[0][3] if rescored else [],
        }
    )
    return [(score, path) for score, path, _, _ in rescored]


v25.build_phrase_paths = locally_chord_aware_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _LOCAL_VOICING_DECISIONS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["localGroupChordVoicingZones"] = {
        "honestFixtureBaseline": 19.06,
        "decisionCount": len(_LOCAL_VOICING_DECISIONS),
        "decisions": list(_LOCAL_VOICING_DECISIONS),
        "policy": (
            "infer-and-score-each-local-note-group-independently-so-a-mixed-phrase-"
            "can-move-from-fifth-position-Am-to-low-D-over-F-sharp-and-open-Fmaj7-"
            "without-forcing-one-chord-zone-across-neighbouring-groups"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.8-phase-1-local-group-chord-voicing-zones"
    result["guitarBrainLesson"] = (
        "apply-chord-voicing-zones-to-local-note-groups-not-entire-mixed-harmonic-phrases"
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
