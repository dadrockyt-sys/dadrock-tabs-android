from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-cache.json"
)

INTRO_FIRST_MEASURE = 1
INTRO_LAST_MEASURE = 16
WIDE_GRID_TOLERANCE_SECONDS = 0.30
PRODUCTION_GRID_TOLERANCE_SECONDS = 0.10

# rhythm_image already contains the frozen separator stack, Basic Pitch, timing,
# and the V143 modules. Package the live-endpoint module itself as well so the
# remote benchmark module can hydrate cleanly inside Modal.
stage_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


@app.function(
    image=stage_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def capture_raw_attack_evidence(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    """Capture unaggregated Basic Pitch attack evidence from both deterministic views.

    This is calibration-only evidence capture. No professional reference is present
    in the remote image or passed to this function.
    """
    import modal_analyzer as legacy
    from v143_candidate_timing_adapter import (
        GUITAR_MIDI_MAX,
        GUITAR_MIDI_MIN,
        HISTORICAL_WIDE_RECALL_SWEEPS,
        build_subdivision_grid,
        nearest_timing_slot,
        note_events_from_predict,
        parse_note_event,
    )
    from v143_reference_free_timing import estimate_reference_free_timing
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-raw-attack-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Raw-attack source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        timing = estimate_reference_free_timing(normalized)
        grid = build_subdivision_grid(**timing.candidate_adapter_kwargs())
        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()

        raw_events: list[dict[str, Any]] = []
        sweep_counts: Counter[str] = Counter()
        stem_counts: Counter[str] = Counter()
        rejected_outside_wide_grid = 0
        rejected_outside_intro = 0
        event_id = 0

        for stem_index, stem_path in enumerate(bundle.candidate_stem_paths):
            stem = Path(stem_path)
            stem_name = f"stem{stem_index}:{stem.name}"
            for sweep_name, onset_threshold, frame_threshold in HISTORICAL_WIDE_RECALL_SWEEPS:
                detected = note_events_from_predict(
                    stem,
                    onset_threshold=float(onset_threshold),
                    frame_threshold=float(frame_threshold),
                )
                for raw_index, raw in enumerate(detected):
                    parsed = parse_note_event(raw)
                    if parsed is None:
                        continue
                    onset, offset, midi, amplitude = parsed
                    if midi < GUITAR_MIDI_MIN or midi > GUITAR_MIDI_MAX:
                        continue

                    wide_nearest = nearest_timing_slot(
                        onset,
                        grid,
                        max_grid_error_seconds=WIDE_GRID_TOLERANCE_SECONDS,
                    )
                    if wide_nearest is None:
                        rejected_outside_wide_grid += 1
                        continue
                    slot, wide_error = wide_nearest
                    if not INTRO_FIRST_MEASURE <= int(slot.measure) <= INTRO_LAST_MEASURE:
                        rejected_outside_intro += 1
                        continue

                    production_nearest = nearest_timing_slot(
                        onset,
                        grid,
                        max_grid_error_seconds=PRODUCTION_GRID_TOLERANCE_SECONDS,
                    )
                    production_accepted = production_nearest is not None

                    event_id += 1
                    sweep_counts[str(sweep_name)] += 1
                    stem_counts[stem_name] += 1
                    raw_events.append(
                        {
                            "eventId": event_id,
                            "stemIndex": int(stem_index),
                            "stemName": stem_name,
                            "sweepName": str(sweep_name),
                            "onsetThreshold": float(onset_threshold),
                            "frameThreshold": float(frame_threshold),
                            "rawIndex": int(raw_index),
                            "midi": int(midi),
                            "amplitude": float(amplitude),
                            "onsetTime": float(onset),
                            "offsetTime": float(offset),
                            "duration": float(max(0.0, offset - onset)),
                            "nearestMeasure": int(slot.measure),
                            "nearestStep": int(slot.step),
                            "nearestGlobalStep": int(slot.global_step),
                            "nearestGridTime": float(slot.time_seconds),
                            "signedGridResidualSeconds": float(onset - slot.time_seconds),
                            "absoluteGridResidualSeconds": float(wide_error),
                            "withinProductionGridTolerance": bool(production_accepted),
                        }
                    )

        intro_grid = [
            {
                "globalStep": int(slot.global_step),
                "measure": int(slot.measure),
                "step": int(slot.step),
                "timeSeconds": float(slot.time_seconds),
            }
            for slot in grid
            if INTRO_FIRST_MEASURE <= int(slot.measure) <= INTRO_LAST_MEASURE
        ]

        return {
            "cacheVersion": 1,
            "scope": "professional-measures-1-16-raw-reference-free-attacks",
            "timing": {
                "tempoBpm": float(timing.tempo_bpm),
                "firstBeatInMeasure": int(timing.first_beat_in_measure),
                "downbeatIndexMod4": int(timing.downbeat_index_mod4),
                "beatConfidence": float(timing.beat_confidence),
                "barConfidence": float(timing.bar_confidence),
                "beatTimes": [float(value) for value in timing.beat_times],
            },
            "grid": intro_grid,
            "events": raw_events,
            "rawEventCount": len(raw_events),
            "productionAcceptedEventCount": sum(
                1 for event in raw_events if event["withinProductionGridTolerance"]
            ),
            "sweepEventCounts": dict(sorted(sweep_counts.items())),
            "stemEventCounts": dict(sorted(stem_counts.items())),
            "candidateStemCount": len(bundle.candidate_stem_paths),
            "rejectedOutsideWideGrid": int(rejected_outside_wide_grid),
            "rejectedOutsideIntro": int(rejected_outside_intro),
            "sourceDurationSeconds": source_metadata.get("duration"),
            "wideGridToleranceSeconds": WIDE_GRID_TOLERANCE_SECONDS,
            "productionGridToleranceSeconds": PRODUCTION_GRID_TOLERANCE_SECONDS,
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


@app.local_entrypoint(name="capture_intro_raw_attack_cache")
def capture_intro_raw_attack_cache(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Capturing raw per-attack evidence from both deterministic guitar views...")
    result = capture_raw_attack_evidence.remote(payload, source.suffix)

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(result, indent=2) + "\n")

    print()
    print("=== V143 INTRO RAW ATTACK CACHE CAPTURED ===")
    print("rawEventCount:", result.get("rawEventCount"))
    print("productionAcceptedEventCount:", result.get("productionAcceptedEventCount"))
    print("candidateStemCount:", result.get("candidateStemCount"))
    print("sweepEventCounts:", result.get("sweepEventCounts"))
    print("stemEventCounts:", result.get("stemEventCounts"))
    print("tempoBpm:", result.get("timing", {}).get("tempoBpm"))
    print("referenceFree:", result.get("referenceFree") is True)
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Cache:", CACHE_PATH.relative_to(REPO_ROOT))
    print("READY FOR RAW ATTACK TEMPORAL DIAGNOSTICS: True")


if __name__ == "__main__":
    capture_intro_raw_attack_cache()
