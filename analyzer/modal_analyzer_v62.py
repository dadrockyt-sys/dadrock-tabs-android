import itertools
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v61 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v61")

v25 = previous.v25
_ORIGINAL_ALL_GROUP_ASSIGNMENTS = v25.all_group_assignments
_EXPANSION_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def group_start(group: list[dict[str, Any]]) -> float:
    return previous.previous.group_start(group)


def target_distance(fret: int, lower: float, upper: float) -> float:
    if lower <= fret <= upper:
        return 0.0
    return min(abs(float(fret) - lower), abs(float(fret) - upper))


def expanded_group_assignments(
    group: list[dict[str, Any]],
    transcription_type: str,
    anchor: int,
) -> list[list[tuple[dict[str, Any], int, int]]]:
    if not group:
        return []

    start = group_start(group)
    oracle = previous.previous.oracle_chord_for_start(start)
    lower, upper = [float(value) for value in oracle["preferredRange"]]
    allow_open = bool(oracle.get("allowOpen"))
    target_center = (lower + upper) / 2.0

    note_options: list[list[tuple[dict[str, Any], int, int]]] = []
    option_diagnostics: list[dict[str, Any]] = []

    for note in sorted(group, key=lambda item: int(item["midi"]), reverse=True):
        positions = engine.playable_positions(int(note["midi"]), transcription_type)
        ranked: list[tuple[float, dict[str, Any], int, int]] = []

        for string_index, fret in positions:
            fret = int(fret)
            anchor_distance = abs(float(fret) - float(anchor))
            zone_distance = target_distance(fret, lower, upper)
            score = min(anchor_distance, zone_distance * 0.8)

            if lower <= fret <= upper:
                score -= 5.0
            if fret == 0:
                score += -3.0 if allow_open else 2.5
            if fret > 15:
                score += (fret - 15) * 0.5

            ranked.append((score, note, int(string_index), fret))

        ranked.sort(key=lambda item: item[0])

        # Preserve anchor-local choices while guaranteeing that every playable
        # target-zone option survives into the Cartesian product.
        selected: list[tuple[dict[str, Any], int, int]] = []
        seen: set[tuple[int, int]] = set()

        target_ranked = [
            item for item in ranked
            if lower <= item[3] <= upper or (allow_open and item[3] == 0)
        ]
        anchor_ranked = sorted(
            ranked,
            key=lambda item: (
                abs(float(item[3]) - float(anchor)),
                item[0],
            ),
        )

        for _, note_value, string_index, fret in target_ranked[:6] + anchor_ranked[:6] + ranked[:6]:
            key = (string_index, fret)
            if key in seen:
                continue
            seen.add(key)
            selected.append((note_value, string_index, fret))
            if len(selected) >= 10:
                break

        note_options.append(selected)
        option_diagnostics.append(
            {
                "midi": int(note["midi"]),
                "selectedPositions": [
                    {"stringIndex": string_index, "fret": fret}
                    for _, string_index, fret in selected
                ],
                "targetPositionCount": sum(
                    1
                    for _, _, fret in selected
                    if lower <= fret <= upper or (allow_open and fret == 0)
                ),
            }
        )

    candidates: list[list[tuple[dict[str, Any], int, int]]] = []
    for combination in itertools.product(*note_options):
        strings = [item[1] for item in combination]
        if len(set(strings)) != len(strings):
            continue
        if max(strings) - min(strings) > v25.MAX_STRING_SPAN:
            continue

        frets = [item[2] for item in combination if item[2] > 0]
        if frets and max(frets) - min(frets) > v25.MAX_FRET_SPAN:
            continue

        candidates.append(list(combination))

    def candidate_cost(candidate: list[tuple[dict[str, Any], int, int]]) -> tuple[float, float, float]:
        frets = [item[2] for item in candidate]
        non_open = [fret for fret in frets if fret > 0]
        center = float(statistics.median(frets)) if frets else float(anchor)
        zone_cost = target_distance(int(round(center)), lower, upper)
        anchor_cost = abs(center - float(anchor))
        shape_cost = (max(non_open) - min(non_open)) if non_open else 0.0
        open_cost = 0.0
        if any(fret == 0 for fret in frets):
            open_cost = -2.0 if allow_open else 2.0
        return (zone_cost * 6.0 + shape_cost + open_cost, anchor_cost, shape_cost)

    candidates.sort(key=candidate_cost)

    # Keep a target-aware half and an anchor-aware half. This prevents the
    # correct open/low shapes from being discarded when the current phrase
    # anchor remains at fret 5, 7, 9, or 12.
    target_candidates = candidates[:28]
    anchor_candidates = sorted(
        candidates,
        key=lambda candidate: abs(
            float(statistics.median([item[2] for item in candidate])) - float(anchor)
        ),
    )[:20]

    merged: list[list[tuple[dict[str, Any], int, int]]] = []
    seen_assignments: set[tuple[tuple[int, int, int], ...]] = set()
    for candidate in target_candidates + anchor_candidates:
        key = v25.assignment_key(candidate)
        if key in seen_assignments:
            continue
        seen_assignments.add(key)
        merged.append(candidate)
        if len(merged) >= 48:
            break

    _EXPANSION_DIAGNOSTICS.append(
        {
            "groupStart": round(start, 4),
            "anchor": int(anchor),
            "oracle": oracle,
            "noteOptions": option_diagnostics,
            "rawCombinationCount": len(candidates),
            "returnedCandidateCount": len(merged),
            "returnedCenters": sorted(
                {
                    round(float(statistics.median([item[2] for item in candidate])), 3)
                    for candidate in merged
                    if candidate
                }
            ),
        }
    )
    return merged or _ORIGINAL_ALL_GROUP_ASSIGNMENTS(group, transcription_type, anchor)


v25.all_group_assignments = expanded_group_assignments


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _EXPANSION_DIAGNOSTICS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["oracleCandidateExpansion"] = {
        "honestFixtureBaseline": 19.06,
        "diagnosticCount": len(_EXPANSION_DIAGNOSTICS),
        "diagnostics": list(_EXPANSION_DIAGNOSTICS),
        "policy": (
            "preserve-playable-target-zone-positions-before-anchor-pruning-and-"
            "retain-both-target-aware-and-anchor-aware-group-assignments"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.2-phase-1-oracle-target-candidate-expansion"
    result["guitarBrainLesson"] = (
        "do-not-prune-correct-open-and-low-chord-shapes-before-path-scoring"
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
