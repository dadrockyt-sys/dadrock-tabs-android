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
_RERANK_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def close_mid_path_promotion(
    paths: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]],
    transcription_type: str,
    anchor: int,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    """Prefer a compact equivalent mid-neck path when it is competitively scored.

    V47 proved that complete-path reranking changes the real winner. Its remaining
    errors are high-position paths whose compact mid-neck equivalents survive only
    a few points behind. This second pass promotes the lower equivalent only when:

    * the harmonic anchor is not a genuine low-position cadence,
    * every upper note can be played in the 4-9 region,
    * and the mid candidate is within a musically small score margin.

    This preserves high positions when the pitches truly require them.
    """
    if not paths or int(anchor) <= 3:
        return paths

    enriched: list[dict[str, Any]] = []
    for rank, (score, path) in enumerate(paths, start=1):
        profile = previous.previous.path_region_profile(path)
        center_value = profile.get("pathUpperCenter")
        center = float(center_value) if center_value is not None else 0.0
        mid_available = previous.upper_notes_have_mid_options(path, transcription_type)
        enriched.append(
            {
                "rank": rank,
                "score": float(score),
                "path": path,
                "profile": profile,
                "center": center,
                "midAvailable": mid_available,
                "promotion": 0.0,
                "reason": None,
            }
        )

    winner = enriched[0]
    mid_candidates = [
        item
        for item in enriched
        if item["midAvailable"] and 4.0 <= item["center"] <= 8.0
    ]

    if not mid_candidates:
        return paths

    best_mid = min(mid_candidates, key=lambda item: item["score"])
    score_gap = best_mid["score"] - winner["score"]

    winner_too_high = winner["center"] > 8.0 and winner["midAvailable"]
    close_enough = score_gap <= 12.0

    if winner_too_high and close_enough and best_mid is not winner:
        # Win by a small deterministic margin, rather than overwhelming all other
        # musical costs. This is a tie-break between already-credible full paths.
        promotion = score_gap + 0.75
        best_mid["promotion"] = promotion
        best_mid["score"] -= promotion
        best_mid["reason"] = "compact-mid-equivalent-within-12-points"

    # Apply a gentle universal tax above fret 8 when the entire pitch set has a
    # lower equivalent. This resolves near-ties without banning legitimate solos.
    for item in enriched:
        if item["midAvailable"] and item["center"] > 8.0:
            item["score"] += (item["center"] - 8.0) * 2.5

    enriched.sort(key=lambda item: item["score"])

    _RERANK_DIAGNOSTICS.append(
        {
            "anchor": int(anchor),
            "winnerBefore": {
                "rawRank": winner["rank"],
                "center": winner["center"],
                "score": round(float(paths[0][0]), 3),
            },
            "winnerAfter": {
                "rawRank": enriched[0]["rank"],
                "center": enriched[0]["center"],
                "score": round(enriched[0]["score"], 3),
                "reason": enriched[0]["reason"],
            },
            "bestMidGapBeforePromotion": round(score_gap, 3),
            "promotionApplied": round(best_mid["promotion"], 3),
        }
    )

    return [(item["score"], item["path"]) for item in enriched]


_v47_build_phrase_paths = previous.reranked_build_phrase_paths


def v48_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    paths = _v47_build_phrase_paths(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )
    return close_mid_path_promotion(paths, transcription_type, anchor)


v25.build_phrase_paths = v48_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _RERANK_DIAGNOSTICS.clear()
    result = previous.previous.previous.previous.analyze_audio_file(
        audio_path,
        transcription_type,
    )
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["closeMidPathPromotion"] = {
        "benchmarkBaseline": 63.0,
        "maximumPromotionGap": 12.0,
        "preferredCompactCenterFrets": [4, 8],
        "decisions": list(_RERANK_DIAGNOSTICS),
        "policy": (
            "when-a-high-winning-path-and-a-compact-mid-equivalent-are-both-"
            "credible-promote-the-lower-full-path-as-a-musical-tie-break"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "4.8-phase-1-close-mid-path-promotion"
    result["guitarBrainLesson"] = (
        "prefer-the-compact-mid-neck-equivalent-when-it-survives-within-twelve-points-of-an-avoidable-high-path"
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
