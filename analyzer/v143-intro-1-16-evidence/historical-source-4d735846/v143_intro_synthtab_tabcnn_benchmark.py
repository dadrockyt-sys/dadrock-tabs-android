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

SYNTHTAB_ROOT = "/opt/synthtab"
SYNTHTAB_MODEL = f"{SYNTHTAB_ROOT}/SynthTab-Pretrained.pt"

# Calibration-only image. The official SynthTab code/checkpoint are downloaded
# at image-build time and are never wired into the customer/production path.
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


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if result == result else default
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int | None = None) -> int | None:
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
def run_synthtab_on_views(
    source_audio: bytes,
    targets: list[dict[str, Any]],
    suffix: str = ".m4a",
) -> dict[str, Any]:
    """Run official pretrained SynthTab TabCNN on both deterministic guitar views."""
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

    if SYNTHTAB_ROOT not in sys.path:
        sys.path.insert(0, SYNTHTAB_ROOT)
    # Required so torch can resolve tabcnn.TabCNN from the serialized checkpoint.
    import tabcnn  # noqa: F401

    clean_targets: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for raw in targets:
        if not isinstance(raw, dict):
            continue
        measure = int(raw.get("measure") or 0)
        step = int(raw.get("step") or 0)
        time_seconds = _float(raw.get("timeSeconds"), -1.0)
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

    with tempfile.TemporaryDirectory(prefix="v143-synthtab-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{safe_suffix}"
        normalized = root / "normalized.wav"
        source.write_bytes(source_audio)
        if source.stat().st_size <= 0:
            raise RuntimeError("SynthTab benchmark audio is empty")

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        bundle = build_deterministic_rhythm_stem_bundle(normalized).validate()
        views = {
            "direct": Path(bundle.carrier_stem_a_path),
            "cascade": Path(bundle.carrier_stem_b_path),
        }

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            model = torch.load(SYNTHTAB_MODEL, map_location=device, weights_only=False)
        except TypeError:
            model = torch.load(SYNTHTAB_MODEL, map_location=device)
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
        tuning = [int(value) for value in model.profile.get_midi_tuning()]
        num_strings = int(model.profile.get_num_dofs())
        num_frets = int(model.profile.get_num_frets())
        crop_seconds = max(item["timeSeconds"] for item in clean_targets) + 1.5

        view_outputs: dict[str, list[dict[str, Any]]] = {}
        for view_name, view_path in views.items():
            audio, _ = librosa.load(
                str(view_path), sr=sample_rate, mono=True, duration=crop_seconds
            )
            audio = np.asarray(audio, dtype=np.float32)
            if audio.size == 0:
                raise RuntimeError(f"Empty deterministic guitar view: {view_name}")

            # Follow SynthTab's official evaluation feature settings.
            feats = data_proc.process_audio(audio)  # C x F x T
            feat_tensor = tools.array_to_tensor(feats[None, ...], device)
            with torch.inference_mode():
                output = model.run_on_batch({tools.KEY_FEATS: feat_tensor})
            tablature = np.asarray(tools.tensor_to_array(output[tools.KEY_TABLATURE]))
            if tablature.ndim == 3:
                tablature = tablature[0]
            if tablature.ndim != 2 or tablature.shape[0] != num_strings:
                raise RuntimeError(f"Unexpected SynthTab output shape: {tablature.shape}")

            frame_count = int(tablature.shape[1])
            rows: list[dict[str, Any]] = []
            for target in clean_targets:
                frame = int(round(target["timeSeconds"] * sample_rate / hop_length))
                frame = max(0, min(frame_count - 1, frame))
                notes: list[dict[str, int]] = []
                for model_string in range(num_strings):
                    fret = int(tablature[model_string, frame])
                    if 0 <= fret <= num_frets:
                        notes.append(
                            {
                                "modelStringIndex": model_string,
                                "fret": fret,
                                "midi": int(tuning[model_string] + fret),
                            }
                        )
                rows.append({**target, "frame": frame, "notes": notes})
            view_outputs[view_name] = rows

    return {
        "model": "SynthTab-Pretrained.pt",
        "officialRepository": "yongyizang/SynthTab",
        "sampleRate": sample_rate,
        "hopLength": hop_length,
        "cqtBins": 192,
        "binsPerOctave": 24,
        "modelTuningMidiLowToHigh": tuning,
        "numStrings": num_strings,
        "numFrets": num_frets,
        "targetCount": len(clean_targets),
        "views": view_outputs,
        "sourceDurationSeconds": source_metadata.get("duration"),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _reference(payload: dict[str, Any], measures: set[int]) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    result: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number not in measures:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            step = int(event.get("step") or 0)
            string_index = _int(event.get("stringIndex"))
            fret = _int(event.get("fret"))
            midi = _int(event.get("midiPitch"))
            if midi is None:
                midi = _int(event.get("soundingMidiPitch"))
            if string_index is None or fret is None or midi is None:
                continue
            result.setdefault((number, step), set()).add((string_index, fret, midi))
    return result


def _predictions(
    remote: dict[str, Any],
    measures: set[int],
    source_mode: str,
    reverse_strings: bool,
) -> dict[tuple[int, int], set[tuple[int, int, int]]]:
    num_strings = int(remote.get("numStrings") or 6)
    by_view: dict[str, dict[tuple[int, int], set[tuple[int, int, int]]]] = {}
    for view_name in ("direct", "cascade"):
        mapped: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
        for row in remote.get("views", {}).get(view_name, []) or []:
            measure = int(row.get("measure") or 0)
            step = int(row.get("step") or 0)
            if measure not in measures:
                continue
            notes: set[tuple[int, int, int]] = set()
            for note in row.get("notes", []) or []:
                model_string = int(note.get("modelStringIndex") or 0)
                ref_string = num_strings - 1 - model_string if reverse_strings else model_string
                notes.add((ref_string, int(note["fret"]), int(note["midi"])))
            if notes:
                mapped[(measure, step)] = notes
        by_view[view_name] = mapped

    locations = set(by_view["direct"]) | set(by_view["cascade"])
    result: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
    for location in locations:
        a = by_view["direct"].get(location, set())
        b = by_view["cascade"].get(location, set())
        if source_mode == "direct":
            chosen = a
        elif source_mode == "cascade":
            chosen = b
        elif source_mode == "intersection":
            chosen = a & b
        elif source_mode == "union":
            chosen = a | b
        else:
            raise ValueError(source_mode)
        if chosen:
            result[location] = chosen
    return result


def _f1(p: float, r: float) -> float:
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def _pct(value: float) -> float:
    return round(value * 100.0, 3)


def _grade(
    expected: dict[tuple[int, int], set[tuple[int, int, int]]],
    actual: dict[tuple[int, int], set[tuple[int, int, int]]],
) -> dict[str, Any]:
    ref_locations = set(expected)
    pred_locations = set(actual)
    location_hits = len(ref_locations & pred_locations)
    lp = location_hits / max(len(pred_locations), 1)
    lr = location_hits / max(len(ref_locations), 1)

    ref_events = sum(len(v) for v in expected.values())
    pred_events = sum(len(v) for v in actual.values())
    exact_hits = 0
    pitch_hits = 0
    string_hits = 0
    fret_hits = 0
    exact_voicings = 0

    for location, wanted in expected.items():
        got = actual.get(location, set())
        exact_hits += len(wanted & got)
        pitch_hits += len({m for _s, _f, m in wanted} & {m for _s, _f, m in got})
        string_hits += len({s for s, _f, _m in wanted} & {s for s, _f, _m in got})
        fret_hits += len({f for _s, f, _m in wanted} & {f for _s, f, _m in got})
        if got == wanted:
            exact_voicings += 1

    ref_pitch = sum(len({m for _s, _f, m in v}) for v in expected.values())
    pred_pitch = sum(len({m for _s, _f, m in v}) for v in actual.values())
    ref_string = sum(len({s for s, _f, _m in v}) for v in expected.values())
    pred_string = sum(len({s for s, _f, _m in v}) for v in actual.values())
    ref_fret = sum(len({f for _s, f, _m in v}) for v in expected.values())
    pred_fret = sum(len({f for _s, f, _m in v}) for v in actual.values())

    ep = exact_hits / max(pred_events, 1)
    er = exact_hits / max(ref_events, 1)
    pp = pitch_hits / max(pred_pitch, 1)
    pr = pitch_hits / max(ref_pitch, 1)
    sp = string_hits / max(pred_string, 1)
    sr = string_hits / max(ref_string, 1)
    fp = fret_hits / max(pred_fret, 1)
    fr = fret_hits / max(ref_fret, 1)

    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(lp),
        "locationRecallPercent": _pct(lr),
        "locationF1Percent": _pct(_f1(lp, lr)),
        "referenceEventCount": ref_events,
        "predictedEventCount": pred_events,
        "exactStringFretPitchPrecisionPercent": _pct(ep),
        "exactStringFretPitchRecallPercent": _pct(er),
        "exactStringFretPitchF1Percent": _pct(_f1(ep, er)),
        "pitchPrecisionPercent": _pct(pp),
        "pitchRecallPercent": _pct(pr),
        "pitchF1Percent": _pct(_f1(pp, pr)),
        "stringPrecisionPercent": _pct(sp),
        "stringRecallPercent": _pct(sr),
        "stringF1Percent": _pct(_f1(sp, sr)),
        "fretPrecisionPercent": _pct(fp),
        "fretRecallPercent": _pct(fr),
        "fretF1Percent": _pct(_f1(fp, fr)),
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
    targets = [
        {
            "measure": int(row.get("measure") or 0),
            "step": int(row.get("step") or 0),
            "timeSeconds": _float(row.get("timeSeconds"), -1.0),
        }
        for row in (cache.get("analysis", {}).get("introRows", []) or [])
        if isinstance(row, dict)
    ]
    if not targets:
        raise RuntimeError("Analysis cache contains no intro targets")

    payload = source.read_bytes()
    print("Running official pretrained SynthTab TabCNN on both deterministic guitar views...")
    remote = run_synthtab_on_views.remote(payload, targets, source.suffix)

    reference_payload = json.loads(REFERENCE_PATH.read_text())
    ref_dev = _reference(reference_payload, DEVELOPMENT_MEASURES)
    ref_hold = _reference(reference_payload, HOLDOUT_MEASURES)

    best: dict[str, Any] | None = None
    trials: list[dict[str, Any]] = []
    for source_mode in ("direct", "cascade", "intersection", "union"):
        for reverse_strings in (False, True):
            pred_dev = _predictions(
                remote, DEVELOPMENT_MEASURES, source_mode, reverse_strings
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
        raise RuntimeError("No SynthTab development trial completed")

    pred_hold = _predictions(
        remote,
        HOLDOUT_MEASURES,
        str(best["sourceMode"]),
        bool(best["reverseModelStringOrder"]),
    )
    holdout = _grade(ref_hold, pred_hold)

    report = {
        "reportVersion": 1,
        "scope": "professional-intro-direct-guitar-tablature-benchmark",
        "challenger": {
            "name": "SynthTab pretrained TabCNN",
            "officialRepository": remote.get("officialRepository"),
            "checkpoint": remote.get("model"),
            "sampleRate": remote.get("sampleRate"),
            "hopLength": remote.get("hopLength"),
            "cqtBins": remote.get("cqtBins"),
            "binsPerOctave": remote.get("binsPerOctave"),
            "modelTuningMidiLowToHigh": remote.get("modelTuningMidiLowToHigh"),
            "numFrets": remote.get("numFrets"),
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
        "referenceFreeRemoteInference": remote.get("referenceFree") is True,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print()
    print("=== SYNTHTAB DIRECT TABLATURE INTRO BENCHMARK ===")
    print("targetLocations:", remote.get("targetCount"))
    print("modelTuningMidiLowToHigh:", remote.get("modelTuningMidiLowToHigh"))
    print("numFrets:", remote.get("numFrets"))
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
