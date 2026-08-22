from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

from v143_modal_live_endpoint import app, rhythm_image


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-stage-diagnostic.json"
)

INTRO_FIRST_MEASURE = 1
INTRO_LAST_MEASURE = 16

# Same production image. The professional reference is intentionally excluded
# from the remote image and is loaded only after the audio pipeline has finished.
stage_image = rhythm_image.add_local_python_source("v143_modal_live_endpoint")


@app.function(
    image=stage_image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def run_v143_stages(source_audio: bytes, suffix: str = ".m4a") -> dict[str, Any]:
    """Return pre-selection and post-selection V143 rows for intro diagnosis."""
    import modal_analyzer as legacy
    from v143_reference_free_rhythm_pipeline import analyze_reference_free_rhythm
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-intro-stage-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Stage diagnostic source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        result = analyze_reference_free_rhythm(
            normalized,
            bundle.candidate_stem_paths,
            bundle.carrier_stem_a_path,
            bundle.carrier_stem_b_path,
        )

        intro_candidates = [
            dict(row)
            for row in result.candidates
            if INTRO_FIRST_MEASURE <= int(row.get("measure") or 0) <= INTRO_LAST_MEASURE
        ]
        intro_rows = [
            dict(row)
            for row in result.rows
            if INTRO_FIRST_MEASURE <= int(row.get("measure") or 0) <= INTRO_LAST_MEASURE
        ]

        return {
            "tempo": float(result.timing.tempo_bpm),
            "firstBeatInMeasure": int(result.timing.first_beat_in_measure),
            "beatConfidence": float(result.timing.beat_confidence),
            "barConfidence": float(result.timing.bar_confidence),
            "totalCandidateCount": int(result.candidate_count),
            "totalSelectedCount": int(result.selected_count),
            "introCandidates": intro_candidates,
            "introRows": intro_rows,
            "sourceDurationSeconds": source_metadata.get("duration"),
            "referenceFree": True,
            "professionalReferenceUsedByAnalyzer": False,
            "runtimeLabelsRequired": False,
        }


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _reference_events(reference: dict[str, Any]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        measure_number = int(measure.get("measureNumber") or 0)
        if not INTRO_FIRST_MEASURE <= measure_number <= INTRO_LAST_MEASURE:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            event = dict(raw)
            event["measureNumber"] = measure_number
            events.append(event)
    return events


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (int(row.get("measure", row.get("measureNumber", 0)) or 0), int(row.get("step", 0) or 0))


def _hypothesis_midis(row: dict[str, Any]) -> set[int]:
    values: set[int] = set()
    for hypothesis in row.get("pitchHypotheses", []) or []:
        if not isinstance(hypothesis, dict):
            continue
        midi = _int(hypothesis.get("midi"))
        if midi is not None:
            values.add(midi)
    dominant = _int(row.get("dominantMidi"))
    if dominant is not None:
        values.add(dominant)
    return values


def _percent(numerator: int, denominator: int) -> float:
    return round(100.0 * numerator / denominator, 3) if denominator else 100.0


def grade_stages(reference: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    refs = _reference_events(reference)
    candidates = [dict(row) for row in analysis.get("introCandidates", []) or []]
    rows = [dict(row) for row in analysis.get("introRows", []) or []]
    selected = [row for row in rows if row.get("v143Selected") is True]

    candidate_by_loc = {_location(row): row for row in candidates}
    row_by_loc = {_location(row): row for row in rows}
    selected_by_loc = {_location(row): row for row in selected}

    reference_locations = {(int(event["measureNumber"]), int(event.get("step") or 0)) for event in refs}

    raw_location_hits = sum(1 for loc in reference_locations if loc in candidate_by_loc)
    selected_location_hits = sum(1 for loc in reference_locations if loc in selected_by_loc)

    raw_pitch_hits = 0
    selected_hypothesis_pitch_hits = 0
    selected_dominant_pitch_hits = 0
    raw_near_step_hits = 0
    correct_pitch_locations_selected = 0
    correct_pitch_locations_total = 0

    offset_histogram: Counter[int] = Counter()
    missing_examples: list[dict[str, Any]] = []

    for ref in refs:
        measure = int(ref["measureNumber"])
        step = int(ref.get("step") or 0)
        midi = _int(ref.get("midiPitch"))
        loc = (measure, step)

        raw = candidate_by_loc.get(loc)
        if raw is not None and midi is not None and midi in _hypothesis_midis(raw):
            raw_pitch_hits += 1
            correct_pitch_locations_total += 1
            selected_raw = selected_by_loc.get(loc)
            if selected_raw is not None:
                correct_pitch_locations_selected += 1
        elif midi is not None:
            best_delta: int | None = None
            for delta in (-2, -1, 1, 2):
                neighbor = candidate_by_loc.get((measure, step + delta))
                if neighbor is not None and midi in _hypothesis_midis(neighbor):
                    if best_delta is None or abs(delta) < abs(best_delta):
                        best_delta = delta
            if best_delta is not None:
                raw_near_step_hits += 1
                offset_histogram[best_delta] += 1

        sel = selected_by_loc.get(loc)
        if sel is not None and midi is not None:
            if midi in _hypothesis_midis(sel):
                selected_hypothesis_pitch_hits += 1
            if _int(sel.get("dominantMidi")) == midi:
                selected_dominant_pitch_hits += 1

        if len(missing_examples) < 24 and (
            raw is None or midi is None or midi not in _hypothesis_midis(raw)
        ):
            missing_examples.append({
                "measure": measure,
                "step": step,
                "referenceMidi": midi,
                "candidatePresent": raw is not None,
                "candidateHypotheses": sorted(_hypothesis_midis(raw)) if raw else [],
                "selected": bool(row_by_loc.get(loc, {}).get("v143Selected")),
            })

    total_refs = len(refs)
    total_ref_locations = len(reference_locations)
    selected_rate = _percent(len(selected), len(rows))

    metrics = {
        "referenceEventCount": total_refs,
        "referenceUniqueLocationCount": total_ref_locations,
        "rawCandidateSlotCount": len(candidates),
        "v143RowCount": len(rows),
        "v143SelectedSlotCount": len(selected),
        "v143SelectionRatePercent": selected_rate,
        "rawExactLocationRecallPercent": _percent(raw_location_hits, total_ref_locations),
        "selectedExactLocationRecallPercent": _percent(selected_location_hits, total_ref_locations),
        "rawExactPitchHypothesisRecallPercent": _percent(raw_pitch_hits, total_refs),
        "selectedPitchHypothesisRecallPercent": _percent(selected_hypothesis_pitch_hits, total_refs),
        "selectedDominantPitchRecallPercent": _percent(selected_dominant_pitch_hits, total_refs),
        "rawCorrectPitchNearStepPlusMinus2AdditionalPercent": _percent(raw_near_step_hits, total_refs),
        "correctPitchSlotSurvivalThroughV143Percent": _percent(
            correct_pitch_locations_selected,
            correct_pitch_locations_total,
        ),
    }

    # Diagnosis deliberately uses broad thresholds. It tells us which stage to
    # rebuild first; it does not choose production parameters.
    if metrics["rawExactLocationRecallPercent"] < 75.0:
        diagnosis = "candidate-generation-or-timing-is-primary-bottleneck"
    elif metrics["rawExactPitchHypothesisRecallPercent"] < 70.0:
        diagnosis = "pitch-hypothesis-recovery-is-primary-bottleneck"
    elif metrics["correctPitchSlotSurvivalThroughV143Percent"] < 75.0:
        diagnosis = "v143-selection-is-primary-bottleneck"
    else:
        diagnosis = "post-selection-musical-reconstruction-is-primary-bottleneck"

    return {
        "diagnosticVersion": 1,
        "scope": "professional-measures-1-16",
        "metrics": metrics,
        "nearStepOffsetHistogram": {str(key): value for key, value in sorted(offset_histogram.items())},
        "diagnosis": diagnosis,
        "missingExamples": missing_examples,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineDiagnostic": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


@app.local_entrypoint()
def main(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Running V143 pre/post-selection stage diagnostic on real audio...")
    analysis = run_v143_stages.remote(payload, source.suffix)

    # Reference enters only here, after remote audio analysis is complete.
    reference = json.loads(REFERENCE_PATH.read_text())
    report = {
        "analysis": {
            "tempo": analysis.get("tempo"),
            "firstBeatInMeasure": analysis.get("firstBeatInMeasure"),
            "beatConfidence": analysis.get("beatConfidence"),
            "barConfidence": analysis.get("barConfidence"),
            "totalCandidateCount": analysis.get("totalCandidateCount"),
            "totalSelectedCount": analysis.get("totalSelectedCount"),
            "referenceFree": analysis.get("referenceFree") is True,
        },
        "diagnostic": grade_stages(reference, analysis),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    metrics = report["diagnostic"]["metrics"]
    print()
    print("=== V143 INTRO STAGE DIAGNOSTIC ===")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print("nearStepOffsetHistogram:", report["diagnostic"]["nearStepOffsetHistogram"])
    print("DIAGNOSIS:", report["diagnostic"]["diagnosis"])
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
