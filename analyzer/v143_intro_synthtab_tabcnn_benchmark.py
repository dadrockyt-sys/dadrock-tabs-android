from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import modal

from v143_modal_live_endpoint import rhythm_image


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
    / "intro-synthtab-tabcnn-benchmark.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))

SYN THTAB_ROOT = "/opt/synthtab"
SYN THTAB_MODEL = f"{SYN THTAB_ROOT}/SynthTab-Pretrained.pt"
SYN THTAB_TABCNN = f"{SYN THTAB_ROOT}/tabcnn.py"

# This image is calibration-only. It extends the already-frozen deterministic
# Rhythm image with the official SynthTab TabCNN runtime dependencies and the
# official pretrained checkpoint. Nothing here is wired into production.
synthtab_image = (
    rhythm_image
    .add_local_python_source("v143_modal_live_endpoint")
    .pip_install("amt-tools>=0.3.1")
    .run_commands(
        "mkdir -p /opt/synthtab",
        "python - <<'PY'\n"
        "from urllib.request import urlretrieve\n"
        "urlretrieve('https://raw.githubusercontent.com/yongyizang/SynthTab/main/demo_embedding/tabcnn.py', '/opt/synthtab/tabcnn.py')\n"
        "urlretrieve('https://raw.githubusercontent.com/yongyizang/SynthTab/main/demo_embedding/pretrained_models/SynthTab-Pretrained.pt', '/opt/synthtab/SynthTab-Pretrained.pt')\n"
        "PY",
        "test -s /opt/synthtab/tabcnn.py",
        "test -s /opt/synthtab/SynthTab-Pretrained.pt",
    )
)

benchmark_app = modal.App("dadrock-v143-intro-synthtab-tabcnn-benchmark")


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
    image=synthtab_image,
    gpu="L4",
    timeout=1200,
    memory=12288,
)
def run_synthtab_on_deterministic_views(
    source_audio: bytes,
    targets: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run official SynthTab TabCNN on the two deterministic guitar views.

    The professional reference is deliberately not mounted or passed here.
    This function only sees audio and reference-free timing targets.
    """
    import tempfile

    import librosa
    import numpy as np
    import torch

    import modal_analyzer as legacy
    from amt_tools import tools
    from amt_tools.features import CQT
    from v143_rhythm_deterministic_stem_provider import (
        build_deterministic_rhythm_stem_bundle,
    )

    if SYN THTAB_ROOT not in sys.path:
        sys.path.insert(0, SYN THTAB_ROOT)
    # The checkpoint was serialized with the official module/class available as
    # `tabcnn.TabCNN`, so import it before torch.load unpickles the model.
    import tabcnn  # noqa: F401

    safe_suffix = str(suffix or ".audio").lower()
    if safe_suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        safe_suffix = ".audio"

    clean_targets: list[dict[str, Any]] = []
    seen_locations: set[tuple[int, int]] = set()
    for raw in targets:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step") or 0)
        time_seconds = _safe_float(raw.get("timeSeconds"), -1.0)
        location = (measure, step)
        if (
            1 <= measure <= 16
            and 0 <= step < 16
            and time_seconds >= 0.0
            and location not in seen_locations
        ):
            seen_locations.add(location)
            clean_targets.append(
                {
                    "measure": measure,
                    "step": step,
                    "timeSeconds": time_seconds,
                }
            )
    if not clean_targets:
        raise RuntimeError("No valid intro timing targets supplied")

    with tempfile.TemporaryDirectory(prefix="v143-synthtab-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("SynthTab benchmark source audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        view_paths = {
            "direct": Path(bundle.carrier_stem_a_path),
            "cascade": Path(bundle.carrier_stem_b_path),
        }

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            model = torch.load(SYN THTAB_MODEL, map_location=device, weights_only=False)
        except TypeError:
            # Older torch releases do not expose the weights_only argument.
            model = torch.load(SYN THTAB_MODEL, map_location=device)
        model.change_device(device)
        model.eval()

        sample_rate = 22050
        hop_length = 512
        data_proc = CQT(
            sample_rate=sample_rate,
            hop_length=hop_length,
            n_bins=192,
            bins_per_octave=24,
        )

        midi_tuning = [int(value) for value in model.profile.get_midi_tuning()]
        num_dofs = int(model.profile.get_num_dofs())
        num_frets = int(model.profile.get_num_frets())
        max_time = max(item["timeSeconds"] for item in clean_targets)
        crop_seconds = max_time + 1.5

        predictions: dict[str, list[dict[str, Any]]] = {}
        for view_name, view_path in view_paths.items():
            audio, _sr = librosa.load(
                str(view_path),
                sr=sample_rate,
                mono=True,
                duration=crop_seconds,
            )
            audio = np.asarray(audio, dtype=np.float32)
            if audio.size <= 0:
                raise RuntimeError(f"SynthTab view is empty: {view_path}")

            feats = data_proc.process_audio(audio)
            # CQT returns C x F x T. Add batch dimension for amt-tools/TabCNN.
            feat_tensor = tools.array_to_tensor(feats[None, ...], device)
            batch = {tools.KEY_FEATS: feat_tensor}
            with torch.inference_mode():
                output = model.run_on_batch(batch)
            tablature = tools.tensor_to_array(output[tools.KEY_TABLATURE])
            tablature = np.asarray(tablature)
            if tablature.ndim == 3:
                tablature = tablature[0]
            if tablature.ndim != 2 or tablature.shape[0] != num_dofs:
                raise RuntimeError(
                    f"Unexpected SynthTab tablature shape: {tablature.shape}"
                )

            frame_count = int(tablature.shape[1])
            rows: list[dict[str, Any]] = []
            for target in clean_targets:
                frame = int(round(target["timeSeconds"] * sample_rate / hop_length))
                frame = max(0, min(frame_count - 1, frame))
                notes: list[dict[str, int]] = []
                for model_string in range(num_dofs):
                    fret = int(tablature[model_string, frame])
                    if fret < 0 or fret > num_frets:
                        continue
                    notes.append(
                        {
                            "modelStringIndex": model_string,
                            "fret": fret,
                            "midi": int(midi_tuning[model_string] + fret),
                        }
                    )
                rows.append(
                    {
                        **target,
                        "frame": frame,
                        "notes": notes,
                    }
                )
            predictions[view_name] = rows

    return {
        "schemaVersion": 1,
        "model": "SynthTab-Pretrained.pt",
        "modelFamily": "SynthTab TabCNN",
        "officialRepository": "yongyizang/SynthTab",
        "sampleRate": sample_rate,
        "hopLength": hop_length,
        "cqtBins": 192,
        "binsPerOctave": 24,
        "modelTuningMidiLowToHigh": midi_tuning,
        "numStrings": num_dofs,
        "numFrets": num_frets,
        "targetCount": len(clean_targets),
        "views": predictions,
        "sourceDurationSeconds": source_metadata.get("duration"),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _reference_by_location(payload: dict[str, Any], measures: set[int]) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    result: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        measure_number = int(measure.get("measureNumber") or 0)
        if measure_number not in measures:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            step = int(event.get("step") or 0)
            string_index = _safe_int(event.get("stringIndex"))
            fret = _safe_int(event.get("fret"))
            midi = _safe_int(event.get("midiPitch"), _safe_int(event.get("soundingMidiPitch")))
            if string_index is None or fret is None or midi is None:
                continue
            result.setdefault((measure_number, step), set()).add((string_index, fret, midi))
    return result


def _predicted_by_location(
    result: dict[str, Any],
    *,
    source_mode: str,
    reverse_strings: bool,
    measures: set[int],
) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    views = result.get("views", {}) or {}
    direct = {
        (int(row["measure"]), int(row["step"])): row
        for row in views.get("direct", []) or []
        if int(row.get("measure") or 0) in measures
    }
    cascade = {
        (int(row["measure"]), int(row["step"])): row
        for row in views.get("cascade", []) or []
        if int(row.get("measure") or 0) in measures
    }
    locations = set(direct) | set(cascade)
    num_strings = int(result.get("numStrings") or 6)

    def notes(row: dict[str, Any] | None) -> set[tuple[int, int, int]]:
        output: set[tuple[int, int, int]] = set()
        for note in (row or {}).get("notes", []) or []:
            model_string = int(note.get("modelStringIndex") or 0)
            string_index = num_strings - 1 - model_string if reverse_strings else model_string
            output.add((string_index, int(note["fret"]), int(note["midi"])))
        return output

    predicted: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
    for location in locations:
        a = notes(direct.get(location))
        b = notes(cascade.get(location))
        if source_mode == "direct":
            selected = a
        elif source_mode == "cascade":
            selected = b
        elif source_mode == "intersection":
            selected = a & b
        elif source_mode == "union":
            selected = a | b
        else:
            raise ValueError(source_mode)
        if selected:
            predicted[location] = selected
    return predicted


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _grade(
    reference: dict[tuple[int, int], set[tuple[int, int, int]]],
    predicted: dict[tuple[int, int], set[tuple[int, int, int]]],
) -> dict[str, Any]:
    ref_locations = set(reference)
    pred_locations = set(predicted)
    location_hits = len(ref_locations & pred_locations)
    location_precision = location_hits / max(len(pred_locations), 1)
    location_recall = location_hits / max(len(ref_locations), 1)

    ref_events = sum(len(values) for values in reference.values())
    pred_events = sum(len(values) for values in predicted.values())

    exact_hits = 0
    pitch_hits = 0
    string_hits = 0
    fret_hits = 0
    exact_voicings = 0
    for location, expected in reference.items():
        actual = predicted.get(location, set())
        exact_hits += len(expected & actual)
        expected_pitch = {midi for _string, _fret, midi in expected}
        actual_pitch = {midi for _string, _fret, midi in actual}
        pitch_hits += len(expected_pitch & actual_pitch)
        expected_strings = {string for string, _fret, _midi in expected}
        actual_strings = {string for string, _fret, _midi in actual}
        string_hits += len(expected_strings & actual_strings)
        expected_frets = {fret for _string, fret, _midi in expected}
        actual_frets = {fret for _string, fret, _midi in actual}
        fret_hits += len(expected_frets & actual_frets)
        if actual == expected:
            exact_voicings += 1

    ref_pitch_events = sum(len({midi for _s, _f, midi in values}) for values in reference.values())
    pred_pitch_events = sum(len({midi for _s, _f, midi in values}) for values in predicted.values())
    ref_string_events = sum(len({s for s, _f, _m in values}) for values in reference.values())
    pred_string_events = sum(len({s for s, _f, _m in values}) for values in predicted.values())
    ref_fret_events = sum(len({f for _s, f, _m in values}) for values in reference.values())
    pred_fret_events = sum(len({f for _s, f, _m in values}) for values in predicted.values())

    exact_precision = exact_hits / max(pred_events, 1)
    exact_recall = exact_hits / max(ref_events, 1)
    pitch_precision = pitch_hits / max(pred_pitch_events, 1)
    pitch_recall = pitch_hits / max(ref_pitch_events, 1)
    string_precision = string_hits / max(pred_string_events, 1)
    string_recall = string_hits / max(ref_string_events, 1)
    fret_precision = fret_hits / max(pred_fret_events, 1)
    fret_recall = fret_hits / max(ref_fret_events, 1)

    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(location_precision),
        "locationRecallPercent": _pct(location_recall),
        "locationF1Percent": _pct(_f1(location_precision, location_recall)),
        "referenceEventCount": ref_events,
        "predictedEventCount": pred_events,
        "exactStringFretPitchPrecisionPercent": _pct(exact_precision),
        "exactStringFretPitchRecallPercent": _pct(exact_recall),
        "exactStringFretPitchF1Percent": _pct(_f1(exact_precision, exact_recall)),
        "pitchPrecisionPercent": _pct(pitch_precision),
        "pitchRecallPercent": _pct(pitch_recall),
        "pitchF1Percent": _pct(_f1(pitch_precision, pitch_recall)),
        "stringPrecisionPercent": _pct(string_precision),
        "stringRecallPercent": _pct(string_recall),
        "stringF1Percent": _pct(_f1(string_precision, string_recall)),
        "fretPrecisionPercent": _pct(fret_precision),
        "fretRecallPercent": _pct(fret_recall),
        "fretF1Percent": _pct(_f1(fret_precision, fret_recall)),
        "exactVoicingLocationPercent": _pct(exact_voicings / max(len(ref_locations), 1)),
    }


def _objective(grade: dict[str, Any]) -> float:
    return round(
        0.45 * float(grade["exactStringFretPitchF1Percent"])
        + 0.30 * float(grade["pitchF1Percent"])
        + 0.15 * float(grade["locationF1Percent"])
        + 0.10 * float(grade["exactVoicingLocationPercent"]),
        3,
    )


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
    intro_rows = cache.get("analysis", {}).get("introRows", []) or []
    targets = [
        {
            "measure": int(row.get("measure") or 0),
            "step": int(row.get("step") or 0),
            "timeSeconds": _safe_float(row.get("timeSeconds"), -1.0),
        }
        for row in intro_rows
        if isinstance(row, dict)
    ]
    if not targets:
        raise RuntimeError("Analysis cache contains no intro timing targets")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("Running official pretrained SynthTab TabCNN on both deterministic guitar views...")
    result = run_synthtab_on_deterministic_views.remote(payload, targets, source.suffix)

    reference_payload = json.loads(REFERENCE_PATH.read_text())
    ref_dev = _reference_by_location(reference_payload, DEVELOPMENT_MEASURES)
    ref_hold = _reference_by_location(reference_payload, HOLDOUT_MEASURES)

    trials: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for source_mode in ("direct", "cascade", "intersection", "union"):
        for reverse_strings in (False, True):
            pred_dev = _predicted_by_location(
                result,
                source_mode=source_mode,
                reverse_strings=reverse_strings,
                measures=DEVELOPMENT_MEASURES,
            )
            development = _grade(ref_dev, pred_dev)
            trial = {
                "sourceMode": source_mode,
                "reverseModelStringOrder": reverse_strings,
                "developmentObjectivePercent": _objective(development),
                "development": development,
            }
            trials.append(trial)
            if best is None or (
                trial["developmentObjectivePercent"],
                development["exactStringFretPitchF1Percent"],
                development["pitchF1Percent"],
            ) > (
                best["developmentObjectivePercent"],
                best["development"]["exactStringFretPitchF1Percent"],
                best["development"]["pitchF1Percent"],
            ):
                best = trial

    if best is None:
        raise RuntimeError("No SynthTab development configuration evaluated")

    pred_hold = _predicted_by_location(
        result,
        source_mode=str(best["sourceMode"]),
        reverse_strings=bool(best["reverseModelStringOrder"]),
        measures=HOLDOUT_MEASURES,
    )
    holdout = _grade(ref_hold, pred_hold)

    report = {
        "reportVersion": 1,
        "scope": "professional-intro-direct-guitar-tablature-benchmark",
        "challenger": {
            "name": "SynthTab pretrained TabCNN",
            "officialRepository": result.get("officialRepository"),
            "checkpoint": result.get("model"),
            "sampleRate": result.get("sampleRate"),
            "hopLength": result.get("hopLength"),
            "cqtBins": result.get("cqtBins"),
            "binsPerOctave": result.get("binsPerOctave"),
            "modelTuningMidiLowToHigh": result.get("modelTuningMidiLowToHigh"),
            "numFrets": result.get("numFrets"),
        },
        "bestDevelopmentConfiguration": {
            "sourceMode": best["sourceMode"],
            "reverseModelStringOrder": best["reverseModelStringOrder"],
            "developmentObjectivePercent": best["developmentObjectivePercent"],
        },
        "development": best["development"],
        "holdout": holdout,
        "allDevelopmentTrials": trials,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineGrading": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "referenceFreeRemoteInference": result.get("referenceFree") is True,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print("=== SYN THTAB DIRECT TABLATURE INTRO BENCHMARK ===")
    print("targetLocations:", result.get("targetCount"))
    print("modelTuningMidiLowToHigh:", result.get("modelTuningMidiLowToHigh"))
    print("numFrets:", result.get("numFrets"))
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(report["bestDevelopmentConfiguration"], indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(report["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to choose view/orientation):")
    print(json.dumps(report["holdout"], indent=2))
    print()
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
