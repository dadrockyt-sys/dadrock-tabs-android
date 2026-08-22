import itertools
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v36 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v36")

v25 = previous.v25
original_all_group_assignments = v25.all_group_assignments

CANDIDATE_BUCKET_LIMIT = 14
TOTAL_CANDIDATE_LIMIT = 56
MAX_COMBINATIONS = 5000


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


def candidate_center(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> float:
    frets = [int(fret) for _, _, fret in assignment if int(fret) > 0]
    return float(statistics.median(frets)) if frets else 0.0


def candidate_bucket(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> str:
    center = candidate_center(assignment)
    open_count = sum(1 for _, _, fret in assignment if int(fret) == 0)
    if open_count and center <= 3.0:
        return "open"
    if center <= 4.0:
        return "low"
    if center <= 9.0:
        return "mid"
    return "high"


def diversity_rank(
    assignment: list[tuple[dict[str, Any], int, int]],
    anchor: int,
) -> float:
    frets = [int(fret) for _, _, fret in assignment]
    fretted = [fret for fret in frets if fret > 0]
    strings = [int(string_index) for _, string_index, _ in assignment]
    center = float(statistics.median(fretted)) if fretted else 0.0
    span = max(fretted) - min(fretted) if fretted else 0
    skipped = max(strings) - min(strings) + 1 - len(set(strings)) if strings else 0
    return (
        abs(center - float(anchor)) * 0.75
        + span * 1.15
        + skipped * 1.8
        + max(0, max(fretted, default=0) - 17) * 1.2
    )


def protected_group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
    anchor: int,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    """Keep musically distinct positions alive until the phrase beam can score them.

    V25 previously retained only one globally cheapest list. This version reserves
    space for open, low, mid-neck and high-neck alternatives so a comfortable
    open-string answer cannot eliminate the correct mid-neck voicing too early.
    """
    if not group:
        return []

    candidates = list(original_all_group_assignments(group, transcription_type, anchor))
    seen = {assignment_key(candidate) for candidate in candidates}

    note_options: list[list[tuple[dict[str, Any], int, int]]] = []
    for note in sorted(group, key=lambda item: int(item["midi"]), reverse=True):
        positions = engine.playable_positions(int(note["midi"]), transcription_type)
        ranked_positions = sorted(
            positions,
            key=lambda item: (
                abs(int(item[1]) - int(anchor)),
                int(item[1]),
                int(item[0]),
            ),
        )

        # Preserve choices from several fretboard regions, not just nearest anchor.
        selected: list[tuple[int, int]] = []
        for low, high, quota in ((0, 3, 3), (4, 9, 4), (10, 16, 3), (17, 24, 2)):
            region = [
                (int(string_index), int(fret))
                for string_index, fret in ranked_positions
                if low <= int(fret) <= high
            ]
            selected.extend(region[:quota])

        if not selected:
            selected = [(int(s), int(f)) for s, f in ranked_positions[:8]]

        unique_positions = list(dict.fromkeys(selected))
        note_options.append(
            [(note, string_index, fret) for string_index, fret in unique_positions]
        )

    tested = 0
    for combination in itertools.product(*note_options):
        tested += 1
        if tested > MAX_COMBINATIONS:
            break

        strings = [int(item[1]) for item in combination]
        if len(set(strings)) != len(strings):
            continue
        if max(strings) - min(strings) > 5:
            continue

        fretted = [int(item[2]) for item in combination if int(item[2]) > 0]
        if fretted and max(fretted) - min(fretted) > 5:
            continue

        candidate = list(combination)
        key = assignment_key(candidate)
        if key not in seen:
            candidates.append(candidate)
            seen.add(key)

    buckets: dict[str, list[list[tuple[dict[str, Any], int, int]]]] = {
        "open": [],
        "low": [],
        "mid": [],
        "high": [],
    }
    for candidate in candidates:
        buckets[candidate_bucket(candidate)].append(candidate)

    protected: list[list[tuple[dict[str, Any], int, int]]] = []
    for bucket_name in ("open", "low", "mid", "high"):
        bucket = buckets[bucket_name]
        bucket.sort(key=lambda candidate: diversity_rank(candidate, anchor))
        protected.extend(bucket[:CANDIDATE_BUCKET_LIMIT])

    protected.sort(key=lambda candidate: diversity_rank(candidate, anchor))
    return protected[:TOTAL_CANDIDATE_LIMIT]


# Install candidate diversity before V36's harmony and path scorers run.
v25.all_group_assignments = protected_group_assignments
# Give the beam enough width to preserve the protected candidate families.
v25.PATH_BEAM_WIDTH = max(int(getattr(v25, "PATH_BEAM_WIDTH", 48)), 72)


def summarize_candidate_training(result: dict[str, Any]) -> dict[str, Any]:
    diagnostics = list(result.get("candidateDiagnostics") or [])
    candidate_counts = [
        len(item.get("topCandidates") or [])
        for item in diagnostics
    ]
    return {
        "protectedRegions": ["open", "low", "mid", "high"],
        "perRegionLimit": CANDIDATE_BUCKET_LIMIT,
        "totalGroupLimit": TOTAL_CANDIDATE_LIMIT,
        "beamWidth": int(v25.PATH_BEAM_WIDTH),
        "diagnosticWindowCount": len(diagnostics),
        "reportedTopCandidateCounts": candidate_counts,
        "policy": "preserve-musically-distinct-fretboard-regions-before-beam-pruning",
    }


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["candidateDiversity"] = summarize_candidate_training(result)
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "3.7-phase-1-candidate-diversity"
    result["guitarBrainLesson"] = (
        "preserve-open-low-mid-and-high-fretboard-options-before-path-scoring"
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
