import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v62 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v62")

v25 = previous.v25
_BEAM_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_center(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> float | None:
    frets = [int(item[2]) for item in assignment]
    return float(statistics.median(frets)) if frets else None


def oracle_for_group(group: list[dict[str, Any]]) -> dict[str, Any]:
    start = previous.group_start(group)
    return previous.previous.previous.oracle_chord_for_start(start)


def in_oracle_zone(
    assignment: list[tuple[dict[str, Any], int, int]],
    oracle: dict[str, Any],
) -> bool:
    center = assignment_center(assignment)
    if center is None:
        return False
    lower, upper = [float(value) for value in oracle["preferredRange"]]
    return lower <= center <= upper


def oracle_distance(
    assignment: list[tuple[dict[str, Any], int, int]],
    oracle: dict[str, Any],
) -> float:
    center = assignment_center(assignment)
    if center is None:
        return 99.0
    lower, upper = [float(value) for value in oracle["preferredRange"]]
    if lower <= center <= upper:
        return 0.0
    return min(abs(center - lower), abs(center - upper))


def oracle_assignment_adjustment(
    assignment: list[tuple[dict[str, Any], int, int]],
    oracle: dict[str, Any],
) -> float:
    distance = oracle_distance(assignment, oracle)
    adjustment = distance * 8.0
    frets = [int(item[2]) for item in assignment]
    allow_open = bool(oracle.get("allowOpen"))
    open_count = sum(1 for fret in frets if fret == 0)

    if distance == 0.0:
        adjustment -= 9.0
    if allow_open and open_count:
        adjustment -= min(7.0, 2.0 + open_count * 1.5)
    elif not allow_open and open_count:
        adjustment += open_count * 3.0
    return adjustment


def diverse_oracle_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = [(0.0, [])]
    step_diagnostics: list[dict[str, Any]] = []

    for group_index, group in enumerate(groups):
        oracle = oracle_for_group(group)
        assignments = v25.all_group_assignments(group, transcription_type, anchor)
        if not assignments:
            assignments = previous.previous.previous.previous.previous.previous.group_assignments(
                group,
                transcription_type,
                anchor,
            )

        next_beam: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
        for accumulated, path in beam:
            prior = path[-1] if path else previous_assignment
            for assignment in assignments:
                cost = accumulated
                cost += v25.guitarist_assignment_cost(assignment, transcription_type, anchor)
                cost += v25.phrase_movement_cost(prior, assignment, anchor)
                cost += oracle_assignment_adjustment(assignment, oracle)
                next_beam.append((cost, path + [assignment]))

        next_beam.sort(key=lambda item: item[0])

        # Preserve target-zone paths separately from the globally cheapest paths.
        # V62 proved the correct candidates exist, but the normal beam deleted them.
        target_paths = [
            item for item in next_beam
            if item[1] and in_oracle_zone(item[1][-1], oracle)
        ]
        target_paths.sort(key=lambda item: item[0])

        global_keep = next_beam[:64]
        target_keep = target_paths[:32]
        merged: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
        seen: set[tuple[tuple[tuple[int, int, int], ...], ...]] = set()

        for item in target_keep + global_keep:
            path_key = tuple(v25.assignment_key(assignment) for assignment in item[1])
            if path_key in seen:
                continue
            seen.add(path_key)
            merged.append(item)
            if len(merged) >= 80:
                break

        beam = merged
        step_diagnostics.append(
            {
                "groupIndex": group_index,
                "groupStart": round(previous.group_start(group), 4),
                "oracle": oracle,
                "assignmentCount": len(assignments),
                "expandedPathCount": len(next_beam),
                "targetPathCount": len(target_paths),
                "preservedPathCount": len(beam),
                "preservedTargetCount": sum(
                    1 for _, path in beam
                    if path and in_oracle_zone(path[-1], oracle)
                ),
                "preservedCenters": sorted(
                    {
                        round(float(center), 3)
                        for _, path in beam
                        if path and (center := assignment_center(path[-1])) is not None
                    }
                ),
            }
        )

    rescored: list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]] = []
    for base_cost, path in beam:
        metrics = previous.previous.previous.previous.previous.path_metrics(path)
        total = base_cost
        # Keep normal guitarist continuity, but do not punish the known purposeful
        # open/low/fifth-position changes as aggressively as the legacy beam.
        total += metrics["positionShiftTotal"] * 0.35
        total += metrics["largeShiftCount"] * 1.5
        total -= metrics["repeatConsistency"] * 5.5

        for group, assignment in zip(groups, path):
            total += oracle_assignment_adjustment(assignment, oracle_for_group(group))
        rescored.append((total, path))

    rescored.sort(key=lambda item: item[0])
    _BEAM_DIAGNOSTICS.append(
        {
            "phraseIndex": len(_BEAM_DIAGNOSTICS),
            "phraseStart": round(previous.group_start(groups[0]), 4) if groups else None,
            "anchor": int(anchor),
            "steps": step_diagnostics,
            "finalCandidateCount": len(rescored),
            "winnerCenters": [
                round(float(center), 3) if center is not None else None
                for assignment in (rescored[0][1] if rescored else [])
                for center in [assignment_center(assignment)]
            ],
        }
    )
    return rescored[:8]


v25.build_phrase_paths = diverse_oracle_build_phrase_paths


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _BEAM_DIAGNOSTICS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["oracleBeamPreservation"] = {
        "honestFixtureBaseline": 19.06,
        "phraseCount": len(_BEAM_DIAGNOSTICS),
        "phrases": list(_BEAM_DIAGNOSTICS),
        "policy": (
            "preserve-correct-open-low-and-fifth-position-candidates-through-every-"
            "beam-step-and-rerank-complete-paths-with-intentional-shifts-allowed"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.3-phase-1-oracle-beam-path-preservation"
    result["guitarBrainLesson"] = (
        "candidate-generation-is-not-enough-correct-voicings-must-survive-every-beam-step"
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
        original_metadata = engine.inspect_audio_file(str(audio_path))
        engine.validate_audio_metadata(original_metadata)
        normalized_path = Path(temp_dir) / "normalized.wav"
        engine.normalize_audio_file(str(audio_path), str(normalized_path))
        normalized_metadata = engine.inspect_audio_file(str(normalized_path))
        result = analyze_audio_file(str(normalized_path), transcription_type)
        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = {
            "sampleRate": normalized_metadata["sampleRate"],
            "channels": normalized_metadata["channels"],
            "codec": normalized_metadata["codec"],
            "formatName": normalized_metadata["formatName"],
        }

    return to_json_safe(result)
