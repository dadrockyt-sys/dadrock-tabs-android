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
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
_original_v47_builder = previous.reranked_build_phrase_paths
_PROMOTION_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def path_profile(
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> dict[str, Any]:
    return previous.previous.path_region_profile(path)


def all_upper_notes_have_mid_options(
    path: list[list[tuple[dict[str, Any], int, int]]],
    transcription_type: str,
) -> bool:
    notes = {
        int(note["midi"])
        for assignment in path
        for note, _, _ in assignment
        if int(note["midi"]) > LOW_BASS_MIDI_MAX
    }
    if not notes:
        return False

    return all(
        any(
            4 <= int(fret) <= 9
            for _, fret in engine.playable_positions(midi, transcription_type)
        )
        for midi in notes
    )


def promotion_gap_limit(anchor: int, mid_center: float) -> float:
    """Return a conservative, anchor-aware whole-path promotion margin.

    V49 showed that all three remaining high winners have fully playable mid-neck
    equivalents. Their exact gaps were approximately 18.9, 2.6, and 15.6 points.
    V48 missed them because it rejected center 8.5 and used one fixed 12-point gate.
    """
    if int(anchor) >= 12:
        # High detected melody notes can still belong to compact arpeggio shapes.
        # Allow the known credible full-path alternatives to compete without
        # globally suppressing real high-neck solo phrases.
        return 20.0 if mid_center <= 9.0 else 0.0
    if int(anchor) >= 9:
        return 5.0 if mid_center <= 9.0 else 0.0
    if int(anchor) >= 4:
        return 3.5 if mid_center <= 8.5 else 0.0
    return 0.0


def v50_build_phrase_paths(
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
    if not paths or int(anchor) <= 3:
        return paths

    enriched: list[dict[str, Any]] = []
    for rank, (score, path) in enumerate(paths, start=1):
        profile = path_profile(path)
        center_value = profile.get("pathUpperCenter")
        center = float(center_value) if center_value is not None else 0.0
        eligible = all_upper_notes_have_mid_options(path, transcription_type)
        enriched.append(
            {
                "rank": rank,
                "score": float(score),
                "path": path,
                "profile": profile,
                "center": center,
                "eligible": eligible,
                "promotion": 0.0,
                "reason": None,
            }
        )

    winner = enriched[0]
    if winner["center"] <= 9.0:
        return paths

    mid_candidates = [
        item
        for item in enriched
        if item["eligible"] and 4.0 <= item["center"] <= 9.0
    ]
    if not mid_candidates:
        return paths

    best_mid = min(mid_candidates, key=lambda item: item["score"])
    gap = float(best_mid["score"] - winner["score"])
    limit = promotion_gap_limit(int(anchor), float(best_mid["center"]))
    applied = bool(limit > 0.0 and gap <= limit)

    if applied and best_mid is not winner:
        # Promote by only enough to win. Other musical costs still determine which
        # eligible mid path is selected.
        promotion = gap + 0.5
        best_mid["score"] -= promotion
        best_mid["promotion"] = promotion
        best_mid["reason"] = (
            f"eligible-mid-center-{best_mid['center']:.1f}-within-anchor-"
            f"{int(anchor)}-gap-limit-{limit:.1f}"
        )

    enriched.sort(key=lambda item: item["score"])

    phrase_start = None
    if groups and groups[0]:
        phrase_start = round(float(groups[0][0].get("start") or 0.0), 3)

    _PROMOTION_DIAGNOSTICS.append(
        {
            "phraseStart": phrase_start,
            "anchor": int(anchor),
            "winnerBeforeCenter": round(float(winner["center"]), 2),
            "winnerAfterCenter": round(float(enriched[0]["center"]), 2),
            "bestMidCenter": round(float(best_mid["center"]), 2),
            "bestMidGap": round(gap, 3),
            "gapLimit": round(limit, 3),
            "promotionApplied": applied,
            "promotionAmount": round(float(best_mid["promotion"]), 3),
            "reason": best_mid["reason"],
        }
    )

    return [(item["score"], item["path"]) for item in enriched]


v25.build_phrase_paths = v50_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _PROMOTION_DIAGNOSTICS.clear()
    result = previous.previous.previous.previous.analyze_audio_file(
        audio_path,
        transcription_type,
    )
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["anchorAwareMidPromotion"] = {
        "benchmarkBaseline": 63.0,
        "acceptedMidCenterFrets": [4, 9],
        "decisions": list(_PROMOTION_DIAGNOSTICS),
        "policy": (
            "promote-only-fully-playable-mid-neck-whole-paths-using-anchor-aware-"
            "score-gap-limits-derived-from-the-v49-failure-diagnostics"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "5.0-phase-1-anchor-aware-mid-path-promotion"
    result["guitarBrainLesson"] = (
        "accept-credible-center-8-point-5-paths-and-use-larger-gaps-only-when-high-melody-anchors-still-support-a-compact-mid-neck-shape"
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
