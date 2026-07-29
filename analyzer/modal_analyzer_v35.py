import os
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v34 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v34")

# Module chain for the Phase 1 harmony and fingering callbacks.
v33 = previous.previous
v31 = v33.previous
v30 = v31.previous
v29 = v30.previous
v25 = v29.v25

HARMONIC_EVIDENCE: dict[str, Any] = {
    "pitchClasses": [],
    "root": None,
    "quality": None,
    "bassPitchClass": None,
    "confidence": 0.0,
    "coverage": 0.0,
    "completeness": 0.0,
    "openVoicingApproved": False,
}


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def evidence_aware_infer_chord(
    groups: list[list[dict[str, Any]]],
) -> dict[str, Any]:
    """Capture how strongly the heard notes support the inferred chord.

    Comfort alone must never be enough to force an open-position shape.
    """
    result = v35_original_infer_chord(groups)
    pitch_classes = {
        int(note["midi"]) % 12
        for group in groups
        for note in group
    }
    root = result.get("root")
    quality = result.get("quality")
    confidence = float(result.get("confidence") or 0.0)

    chord_pcs: set[int] = set()
    if root is not None and quality in v29.CHORD_INTERVALS:
        chord_pcs = {
            (int(root) + int(interval)) % 12
            for interval in v29.CHORD_INTERVALS[str(quality)]
        }

    coverage = (
        len(pitch_classes & chord_pcs) / max(1, len(pitch_classes))
        if chord_pcs
        else 0.0
    )
    required_tones = min(3, len(chord_pcs))
    completeness = (
        len(pitch_classes & chord_pcs) / max(1, required_tones)
        if chord_pcs
        else 0.0
    )
    completeness = min(1.0, completeness)

    bass_pc = result.get("bassPitchClass")
    bass_supported = bass_pc is not None and int(bass_pc) in chord_pcs
    open_approved = bool(
        confidence >= 0.58
        and coverage >= 0.78
        and completeness >= 0.67
        and bass_supported
    )

    HARMONIC_EVIDENCE.update(
        {
            "pitchClasses": sorted(pitch_classes),
            "root": root,
            "quality": quality,
            "bassPitchClass": bass_pc,
            "confidence": round(confidence, 3),
            "coverage": round(coverage, 3),
            "completeness": round(completeness, 3),
            "openVoicingApproved": open_approved,
        }
    )
    result["voicingEvidence"] = dict(HARMONIC_EVIDENCE)
    return result


def evidence_gated_assignment_cost(
    assignment: list[tuple[dict[str, Any], int, int]],
    transcription_type: str,
    anchor: int,
) -> float:
    """Use open strings only when harmony and inversion genuinely support them."""
    cost = v31.safe_harmony_voicing_cost(
        assignment,
        transcription_type,
        anchor,
    )
    if not assignment or transcription_type == "bass":
        return cost

    confidence = float(HARMONIC_EVIDENCE.get("confidence") or 0.0)
    coverage = float(HARMONIC_EVIDENCE.get("coverage") or 0.0)
    completeness = float(HARMONIC_EVIDENCE.get("completeness") or 0.0)
    open_approved = bool(HARMONIC_EVIDENCE.get("openVoicingApproved"))

    open_notes = [
        (note, int(string_index), int(fret))
        for note, string_index, fret in assignment
        if int(fret) == 0
    ]
    fretted = [int(fret) for _, _, fret in assignment if int(fret) > 0]

    if open_notes:
        if open_approved:
            # A small reward, deliberately weaker than V29's original blanket
            # open-position preference.
            cost -= len(open_notes) * (0.45 + confidence * 0.35)
        else:
            weakness = (
                max(0.0, 0.62 - confidence)
                + max(0.0, 0.82 - coverage)
                + max(0.0, 0.72 - completeness)
            )
            cost += len(open_notes) * (2.2 + weakness * 4.0)

    # Do not collapse a previously mid-neck phrase into first position merely
    # because one isolated note has an open-string equivalent.
    if anchor <= 2 and open_notes and not open_approved:
        cost += 3.5

    # Reward a coherent low-position chord only when several notes form one
    # compact shape, rather than rewarding a lone open string.
    if open_approved and len(assignment) >= 2 and fretted:
        span = max(fretted) - min(fretted)
        if span <= 3:
            cost -= 1.1

    # Preserve V30's bass-voice placement without calling its recursive wrapper.
    bass_pc = HARMONIC_EVIDENCE.get("bassPitchClass")
    if bass_pc is not None and confidence >= 0.42:
        lowest = min(assignment, key=lambda item: int(item[0]["midi"]))
        note, string_index, fret = lowest
        if int(note["midi"]) % 12 == int(bass_pc):
            if int(string_index) >= 3:
                cost -= 2.2 + confidence * 1.8
            else:
                cost += 1.8 + confidence
            if int(fret) == 0 and int(string_index) >= 3 and open_approved:
                cost -= 0.35

    return cost


# Install the evidence capture around V30's sequence-aware chord inference.
v35_original_infer_chord = v29.infer_chord
v29.infer_chord = evidence_aware_infer_chord

# Install one non-recursive scorer at the actual V25 beam-search callback.
v25.guitarist_assignment_cost = evidence_gated_assignment_cost


def summarize_voicing_evidence(result: dict[str, Any]) -> dict[str, Any]:
    windows = (
        result.get("musicalUnderstanding", {})
        .get("harmonicWindows", [])
    )
    summaries: list[dict[str, Any]] = []
    approved = 0
    rejected = 0
    for window in windows:
        chord = window.get("chord") or {}
        evidence = chord.get("voicingEvidence") or {}
        if evidence.get("openVoicingApproved"):
            approved += 1
        else:
            rejected += 1
        summaries.append(
            {
                "phraseIndex": window.get("phraseIndex"),
                "windowIndex": window.get("windowIndex"),
                "chord": chord.get("name"),
                "coverage": evidence.get("coverage"),
                "completeness": evidence.get("completeness"),
                "openVoicingApproved": evidence.get("openVoicingApproved"),
                "chosenAnchor": window.get("chosenAnchor"),
            }
        )
    return {
        "approvedOpenWindows": approved,
        "rejectedOpenWindows": rejected,
        "windows": summaries,
        "policy": "open-position-requires-chord-pitch-and-bass-evidence",
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["voicingEvidence"] = summarize_voicing_evidence(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "3.5-phase-1-evidence-gated-voicings"
    result["guitarBrainLesson"] = (
        "approve-open-position-only-when-chord-pitches-and-bass-support-it"
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
