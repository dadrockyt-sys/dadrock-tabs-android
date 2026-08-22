from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
ANALYSIS_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-kong-pitch-benchmark.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
CHECKPOINT_PATH = "/opt/kong/CRNN_note_F1=0.9677_pedal_F1=0.9186.pth"

V143_MODULES = (
    "modal_analyzer",
    "v143_ai_tab_gpu_worker",
    "v143_candidate_timing_adapter",
    "v143_deterministic_separator",
    "v143_modal_rhythm_router",
    "v143_production_engine",
    "v143_production_separator",
    "v143_reference_free_rhythm_pipeline",
    "v143_reference_free_timing",
    "v143_rhythm_bend_consensus",
    "v143_rhythm_bend_evidence",
    "v143_rhythm_deterministic_stem_provider",
    "v143_rhythm_event_assembly",
    "v143_rhythm_guitar_note_mapper",
    "v143_rhythm_legato_evidence",
    "v143_rhythm_output_adapter",
    "v143_rhythm_runtime",
    "v143_rhythm_stem_provider",
    "v143_rhythm_sustain_technique_enricher",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
    "v143_vercel_audio_request_adapter",
)

# Calibration only. Build steps deliberately precede all add_local_* calls.
kong_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg", "wget")
    .pip_install(
        "audio-separator[gpu]==0.44.5",
        "setuptools==81.0.0",
        "numpy==1.26.4",
        "librosa==0.10.2.post1",
        "scipy",
        "soundfile",
        "requests",
        "piano-transcription-inference==0.0.6",
    )
    .run_commands(
        "mkdir -p /opt/kong",
        "wget -q -O '/opt/kong/CRNN_note_F1=0.9677_pedal_F1=0.9186.pth' "
        "'https://zenodo.org/record/4034264/files/CRNN_note_F1%3D0.9677_pedal_F1%3D0.9186.pth?download=1'",
        "test $(stat -c%s '/opt/kong/CRNN_note_F1=0.9677_pedal_F1=0.9186.pth') -gt 160000000",
    )
    .add_local_python_source(*V143_MODULES)
)

benchmark_app = modal.App("dadrock-v143-intro-kong-pitch-benchmark")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if result == result else default
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int | None = None) -> int | None:
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


@benchmark_app.function(
    image=kong_image,
    gpu="L4",
    timeout=1200,
    memory=12288,
)
def run_kong_on_deterministic_views(
    source_audio: bytes,
    targets: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run the public high-resolution CRNN checkpoint on both guitar views.

    The professional reference is intentionally not mounted or passed here.
    """
    import tempfile

    import librosa
    import numpy as np
    import torch

    # Compatibility aliases for older research-package dependencies.
    if not hasattr(np, "complex"):
        np.complex = complex  # type: ignore[attr-defined]
    if not hasattr(np, "float"):
        np.float = float  # type: ignore[attr-defined]
    if not hasattr(np, "int"):
        np.int = int  # type: ignore[attr-defined]

    import modal_analyzer as legacy
    from piano_transcription_inference import PianoTranscription, sample_rate
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    clean_targets: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for raw in targets:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step") or 0)
        time_seconds = _safe_float(raw.get("timeSeconds"), -1.0)
        location = (measure, step)
        if 1 <= measure <= 16 and 0 <= step < 16 and time_seconds >= 0 and location not in seen:
            seen.add(location)
            clean_targets.append(
                {"measure": measure, "step": step, "timeSeconds": time_seconds}
            )
    if not clean_targets:
        raise RuntimeError("No valid cached intro timing targets")

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    with tempfile.TemporaryDirectory(prefix="v143-kong-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("Kong benchmark source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        views = {
            "direct": Path(bundle.carrier_stem_a_path),
            "cascade": Path(bundle.carrier_stem_b_path),
        }

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if device.type != "cuda":
            raise RuntimeError("Kong benchmark requires the requested Modal GPU")

        transcriptor = PianoTranscription(
            model_type="Note_pedal",
            checkpoint_path=CHECKPOINT_PATH,
            device=device,
        )
        crop_seconds = max(item["timeSeconds"] for item in clean_targets) + 1.5

        view_outputs: dict[str, list[dict[str, Any]]] = {}
        for view_name, view_path in views.items():
            audio, _ = librosa.load(
                str(view_path), sr=sample_rate, mono=True, duration=crop_seconds
            )
            audio = np.asarray(audio, dtype=np.float32)
            if audio.size == 0:
                raise RuntimeError(f"Empty deterministic guitar view: {view_name}")

            result = transcriptor.transcribe(audio, None)
            events: list[dict[str, Any]] = []
            for raw in result.get("est_note_events", []) or []:
                midi = _safe_int(raw.get("midi_note"))
                onset = _safe_float(raw.get("onset_time"), -1.0)
                offset = _safe_float(raw.get("offset_time"), onset)
                if midi is None or onset < 0 or midi < 40 or midi > 88:
                    continue
                events.append(
                    {
                        "midi": midi,
                        "onsetTime": onset,
                        "offsetTime": max(offset, onset),
                        "velocity": _safe_int(raw.get("velocity"), 0),
                    }
                )
            view_outputs[view_name] = events

    return {
        "modelFamily": "Kong high-resolution onset-offset CRNN",
        "checkpoint": Path(CHECKPOINT_PATH).name,
        "sampleRate": int(sample_rate),
        "targetCount": len(clean_targets),
        "views": view_outputs,
        "sourceDurationSeconds": source_metadata.get("duration"),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _targets_from_cache(cache: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = cache.get("analysis", {}) or {}
    rows = analysis.get("introRows", []) or analysis.get("introCandidates", []) or []
    targets: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        step = int(row.get("step") or 0)
        time_seconds = _safe_float(row.get("timeSeconds"), -1.0)
        key = (measure, step)
        if 1 <= measure <= 16 and 0 <= step < 16 and time_seconds >= 0 and key not in seen:
            seen.add(key)
            targets.append(
                {"measure": measure, "step": step, "timeSeconds": time_seconds}
            )
    return sorted(targets, key=lambda x: (x["timeSeconds"], x["measure"], x["step"]))


def _reference_pitch_sets(
    reference: dict[str, Any], measures: set[int]
) -> dict[tuple[int, int], set[int]]:
    output: dict[tuple[int, int], set[int]] = {}
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number not in measures:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            step = int(event.get("step") or 0)
            midi = _safe_int(event.get("midiPitch"))
            if midi is None:
                midi = _safe_int(event.get("soundingMidiPitch"))
            if midi is not None:
                output.setdefault((number, step), set()).add(midi)
    return output


def _target_index(
    targets: list[dict[str, Any]], measures: set[int]
) -> list[tuple[float, tuple[int, int]]]:
    return [
        (
            float(item["timeSeconds"]),
            (int(item["measure"]), int(item["step"])),
        )
        for item in targets
        if int(item["measure"]) in measures
    ]


def _snap_events(
    events: list[dict[str, Any]],
    targets: list[dict[str, Any]],
    measures: set[int],
    *,
    tolerance: float,
    mode: str,
) -> dict[tuple[int, int], set[int]]:
    indexed = _target_index(targets, measures)
    predicted: dict[tuple[int, int], set[int]] = {}
    if not indexed:
        return predicted

    if mode == "onset":
        for event in events:
            onset = _safe_float(event.get("onsetTime"), -1.0)
            midi = _safe_int(event.get("midi"))
            if onset < 0 or midi is None:
                continue
            target_time, location = min(indexed, key=lambda item: abs(item[0] - onset))
            if abs(target_time - onset) <= tolerance:
                predicted.setdefault(location, set()).add(midi)
        return predicted

    if mode == "active":
        for target_time, location in indexed:
            for event in events:
                onset = _safe_float(event.get("onsetTime"), -1.0)
                offset = _safe_float(event.get("offsetTime"), onset)
                midi = _safe_int(event.get("midi"))
                if midi is None:
                    continue
                if onset - tolerance <= target_time <= offset + tolerance:
                    predicted.setdefault(location, set()).add(midi)
        return predicted

    raise ValueError(mode)


def _combine(
    a: dict[tuple[int, int], set[int]],
    b: dict[tuple[int, int], set[int]],
    mode: str,
) -> dict[tuple[int, int], set[int]]:
    result: dict[tuple[int, int], set[int]] = {}
    for location in set(a) | set(b):
        left = a.get(location, set())
        right = b.get(location, set())
        if mode == "direct":
            chosen = left
        elif mode == "cascade":
            chosen = right
        elif mode == "intersection":
            chosen = left & right
        elif mode == "union":
            chosen = left | right
        else:
            raise ValueError(mode)
        if chosen:
            result[location] = chosen
    return result


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0 else 2 * precision * recall / (precision + recall)


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _grade(
    reference: dict[tuple[int, int], set[int]],
    predicted: dict[tuple[int, int], set[int]],
) -> dict[str, Any]:
    ref_locations = set(reference)
    pred_locations = set(predicted)
    location_hits = len(ref_locations & pred_locations)
    lp = location_hits / max(len(pred_locations), 1)
    lr = location_hits / max(len(ref_locations), 1)

    ref_events = sum(len(values) for values in reference.values())
    pred_events = sum(len(values) for values in predicted.values())
    pitch_hits = sum(
        len(expected & predicted.get(location, set()))
        for location, expected in reference.items()
    )
    pp = pitch_hits / max(pred_events, 1)
    pr = pitch_hits / max(ref_events, 1)

    exact_sets = sum(
        1 for location, expected in reference.items()
        if predicted.get(location, set()) == expected
    )

    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(lp),
        "locationRecallPercent": _pct(lr),
        "locationF1Percent": _pct(_f1(lp, lr)),
        "referencePitchEventCount": ref_events,
        "predictedPitchEventCount": pred_events,
        "pitchPrecisionPercent": _pct(pp),
        "pitchRecallPercent": _pct(pr),
        "pitchF1Percent": _pct(_f1(pp, pr)),
        "exactPitchSetPercent": _pct(exact_sets / max(len(ref_locations), 1)),
    }


def _prediction_for_config(
    remote: dict[str, Any],
    targets: list[dict[str, Any]],
    measures: set[int],
    config: dict[str, Any],
) -> dict[tuple[int, int], set[int]]:
    direct = _snap_events(
        remote.get("views", {}).get("direct", []) or [],
        targets,
        measures,
        tolerance=float(config["toleranceSeconds"]),
        mode=str(config["eventMode"]),
    )
    cascade = _snap_events(
        remote.get("views", {}).get("cascade", []) or [],
        targets,
        measures,
        tolerance=float(config["toleranceSeconds"]),
        mode=str(config["eventMode"]),
    )
    return _combine(direct, cascade, str(config["sourceMode"]))


@benchmark_app.local_entrypoint()
def main(audio_path: str = str(DEFAULT_AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Audio file missing or empty: {source}")
    if not ANALYSIS_CACHE_PATH.exists():
        raise RuntimeError(f"Analysis cache missing: {ANALYSIS_CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    cache = json.loads(ANALYSIS_CACHE_PATH.read_text())
    targets = _targets_from_cache(cache)
    if not targets:
        raise RuntimeError("No intro timing targets recovered from analysis cache")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Running high-resolution CRNN pitch benchmark on deterministic guitar views...")
    remote = run_kong_on_deterministic_views.remote(payload, targets, source.suffix)

    # The professional reference enters only after reference-free inference ends.
    reference = json.loads(REFERENCE_PATH.read_text())
    dev_ref = _reference_pitch_sets(reference, DEVELOPMENT_MEASURES)
    holdout_ref = _reference_pitch_sets(reference, HOLDOUT_MEASURES)

    configs: list[dict[str, Any]] = []
    for source_mode in ("direct", "cascade", "intersection", "union"):
        for event_mode in ("onset", "active"):
            for tolerance in (0.04, 0.06, 0.08, 0.10, 0.12, 0.16):
                config = {
                    "sourceMode": source_mode,
                    "eventMode": event_mode,
                    "toleranceSeconds": tolerance,
                }
                dev_pred = _prediction_for_config(
                    remote, targets, DEVELOPMENT_MEASURES, config
                )
                dev_grade = _grade(dev_ref, dev_pred)
                objective = (
                    0.80 * dev_grade["pitchF1Percent"]
                    + 0.20 * dev_grade["locationF1Percent"]
                )
                configs.append(
                    {
                        **config,
                        "developmentObjectivePercent": round(objective, 3),
                        "development": dev_grade,
                    }
                )

    configs.sort(
        key=lambda row: (
            row["developmentObjectivePercent"],
            row["development"]["pitchF1Percent"],
            row["development"]["pitchRecallPercent"],
        ),
        reverse=True,
    )
    best = configs[0]
    best_config = {
        "sourceMode": best["sourceMode"],
        "eventMode": best["eventMode"],
        "toleranceSeconds": best["toleranceSeconds"],
        "developmentObjectivePercent": best["developmentObjectivePercent"],
    }
    holdout_pred = _prediction_for_config(
        remote, targets, HOLDOUT_MEASURES, best_config
    )
    holdout_grade = _grade(holdout_ref, holdout_pred)

    report = {
        "modelFamily": remote.get("modelFamily"),
        "checkpoint": remote.get("checkpoint"),
        "targetCount": remote.get("targetCount"),
        "bestDevelopmentConfiguration": best_config,
        "development": best["development"],
        "holdout": holdout_grade,
        "topDevelopmentConfigurations": configs[:10],
        "referenceFreeInference": remote.get("referenceFree") is True,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print("=== HIGH-RESOLUTION CRNN PITCH BENCHMARK COMPLETE ===")
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(best_config, indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(best["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to choose configuration):")
    print(json.dumps(holdout_grade, indent=2))
    print()
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
