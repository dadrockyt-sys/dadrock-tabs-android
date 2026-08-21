from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_shadow_modal import shadow_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
SECTION2_CACHE = CAL / "fresh-section2-reference-free-cache.json"
SECTION3_CACHE = CAL / "fresh-section3-reference-free-cache.json"

app = modal.App("dadrock-v143-contextual-prune-band-diagnostic")

# The remote function module imports v143_contextual_prune_shadow_modal at
# container startup, so the module itself must be mounted into the image.
diagnostic_image = shadow_image.add_local_python_source(
    "v143_contextual_prune_shadow_modal"
)
for filename in (
    "fresh-section2-reference-free-cache.json",
    "fresh-section3-reference-free-cache.json",
):
    diagnostic_image = diagnostic_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _research_normalize_audio(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        str(source),
        "-map",
        "0:a:0",
        "-vn",
        "-ar",
        "44100",
        "-ac",
        "2",
        "-c:a",
        "pcm_s16le",
        str(destination),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            "Historical V143 research normalization failed:\n"
            + (result.stderr or result.stdout or "unknown ffmpeg error")[-4000:]
        )
    if not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError("Historical V143 research normalization produced no audio")
    return destination


def _build_shadow_stems(normalized: Path, output_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    from v143_deterministic_separator import build_deterministic_v143_stems

    stems = build_deterministic_v143_stems(normalized, output_dir)
    direct = Path(str(stems.get("directGuitar") or ""))
    cascade = Path(str(stems.get("cascadeGuitar") or ""))
    for label, path in (("direct", direct), ("cascade", cascade)):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Diagnostic {label} guitar view is missing: {path}")
    if stems.get("deterministic") is not True:
        raise RuntimeError("Diagnostic separator is not deterministic")
    if stems.get("referenceFree") is not True:
        raise RuntimeError("Diagnostic separator is not reference-free")
    return stems, direct, cascade


def _first_mismatch(expected: Any, actual: Any, path: str = "$") -> dict[str, Any] | None:
    if isinstance(expected, bool) or isinstance(actual, bool):
        return None if expected == actual else {"path": path, "expected": expected, "actual": actual}
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        left = float(expected)
        right = float(actual)
        if math.isfinite(left) and math.isfinite(right) and math.isclose(
            left, right, rel_tol=1e-12, abs_tol=1e-12
        ):
            return None
        return None if left == right else {"path": path, "expected": expected, "actual": actual}
    if type(expected) is not type(actual):
        return {
            "path": path,
            "expectedType": type(expected).__name__,
            "actualType": type(actual).__name__,
            "expected": expected,
            "actual": actual,
        }
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return {
                "path": path,
                "missingKeys": sorted(set(expected) - set(actual)),
                "extraKeys": sorted(set(actual) - set(expected)),
            }
        for key in expected:
            mismatch = _first_mismatch(expected[key], actual[key], f"{path}.{key}")
            if mismatch is not None:
                return mismatch
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return {"path": path, "expectedLength": len(expected), "actualLength": len(actual)}
        for index, (left, right) in enumerate(zip(expected, actual)):
            mismatch = _first_mismatch(left, right, f"{path}[{index}]")
            if mismatch is not None:
                return mismatch
        return None
    return None if expected == actual else {"path": path, "expected": expected, "actual": actual}


def _normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Historical captures restart onsetGroupId inside each 16-measure cache.
    # The ID is an ordering artifact only; none of the frozen scorers consume it.
    out: list[dict[str, Any]] = []
    for raw in rows:
        row = dict(raw)
        row.pop("onsetGroupId", None)
        out.append(row)
    return out


def _timing_payload(timing: Any) -> dict[str, Any]:
    return {
        "tempoBpm": float(timing.tempo_bpm),
        "firstBeatInMeasure": int(timing.first_beat_in_measure),
        "downbeatIndexMod4": int(timing.downbeat_index_mod4),
        "beatConfidence": float(timing.beat_confidence),
        "barConfidence": float(timing.bar_confidence),
    }


def _expected_semantics(cache: dict[str, Any], start: int, end: int) -> dict[str, Any]:
    if cache.get("referenceFree") is not True:
        raise RuntimeError("Historical cache lost referenceFree=true")
    if cache.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Historical cache unexpectedly used professional reference")
    section = dict(cache.get("section") or {})
    if int(section.get("startMeasure", -1)) != start or int(section.get("endMeasure", -1)) != end:
        raise RuntimeError(f"Unexpected historical cache section: {section}")

    return {
        "timing": dict(cache.get("timing") or {}),
        "grid": [dict(row) for row in cache.get("grid", []) or []],
        "rows": _normalize_rows([dict(row) for row in cache.get("rows", []) or []]),
        "targetSampleRate": int(cache.get("targetSampleRate", -1)),
        "hopLength": int(cache.get("hopLength", -1)),
        "binsPerOctave": int(cache.get("binsPerOctave", -1)),
        "spectrumMidiMin": int(cache.get("spectrumMidiMin", -1)),
        "spectrumMidiMax": int(cache.get("spectrumMidiMax", -1)),
        "guitarMidiMin": int(cache.get("guitarMidiMin", -1)),
        "guitarMidiMax": int(cache.get("guitarMidiMax", -1)),
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }


def _generated_semantics(carrier: Any) -> dict[str, Any]:
    return {
        "timing": _timing_payload(carrier.timing),
        "grid": [dict(row) for row in carrier.grid_rows],
        "rows": _normalize_rows([dict(row) for row in carrier.rows]),
        "targetSampleRate": 22050,
        "hopLength": 128,
        "binsPerOctave": 36,
        "spectrumMidiMin": 28,
        "spectrumMidiMax": 112,
        "guitarMidiMin": 40,
        "guitarMidiMax": 88,
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
    }


def _band_result(label: str, cache: dict[str, Any], carrier: Any, start: int, end: int) -> dict[str, Any]:
    expected = _expected_semantics(cache, start, end)
    generated = _generated_semantics(carrier)
    mismatch = _first_mismatch(expected, generated)
    return {
        "label": label,
        "measures": f"{start}-{end}",
        "comparisonScope": "scoring-relevant-carrier-semantics",
        "expectedSemanticSha256": _canonical_sha256(expected),
        "generatedSemanticSha256": _canonical_sha256(generated),
        "exactSemanticReplayPassed": expected == generated,
        "toleranceSemanticReplayPassed": mismatch is None,
        "firstMismatch": mismatch,
        "expected": {
            "gridCount": len(expected["grid"]),
            "rowCount": len(expected["rows"]),
            "rawEventCount": int(cache.get("rawEventCount", -1)),
            "candidateClusterCount": int(cache.get("candidateClusterCount", -1)),
            "onsetGroupCount": int(cache.get("onsetGroupCount", -1)),
            "sweepEventCounts": dict(cache.get("sweepEventCounts") or {}),
            "stemEventCounts": dict(cache.get("stemEventCounts") or {}),
        },
        "generated": {
            "gridCount": len(generated["grid"]),
            "rowCount": len(generated["rows"]),
            "rawEventCount": int(carrier.raw_event_count),
            "candidateClusterCount": int(carrier.candidate_cluster_count),
            "onsetGroupCount": len(carrier.rows),
            "sweepEventCounts": dict(carrier.sweep_event_counts),
            "stemEventCounts": dict(carrier.stem_event_counts),
        },
    }


def _freeze_cache_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (tuple, list)):
        return tuple(_freeze_cache_value(item) for item in value)
    if isinstance(value, dict):
        return tuple(
            sorted((str(key), _freeze_cache_value(item)) for key, item in value.items())
        )
    return repr(value)


@app.function(image=diagnostic_image, gpu="L4", timeout=1800, memory=12288)
def diagnose_sections_2_and_3(source_audio: bytes, suffix: str = ".audio") -> dict[str, Any]:
    """Replay each historical band exactly while sharing expensive inference.

    Each carrier keeps its original band-specific measure range. That matters
    because the carrier's whole-onset CQT crop ends shortly after the last onset
    in that range; building one 33-64 carrier and slicing it can change edge CQT
    evidence near measure 48. Basic Pitch prediction is the expensive repeated
    operation, so this diagnostic loads the model once, memoizes compact note
    events across both band builds, and reuses the same reference-free timing.
    The comparison remains fully reference-free and label-blind.
    """
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Diagnostic audio cannot exceed 50 MB")

    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict as basic_pitch_predict
    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_reference_free_timing import estimate_reference_free_timing

    section2 = json.loads(SECTION2_CACHE.read_text(encoding="utf-8"))
    section3 = json.loads(SECTION3_CACHE.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory(prefix="v143-band-diagnostic-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)
        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")

        timing = estimate_reference_free_timing(normalized)
        basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)
        prediction_cache: dict[Any, tuple[Any, ...]] = {}
        cache_hits = 0
        cache_misses = 0

        def memoized_predict(audio_path: str, *args: Any, **kwargs: Any) -> Any:
            nonlocal cache_hits, cache_misses
            key = (
                str(Path(audio_path).resolve()),
                _freeze_cache_value(args),
                _freeze_cache_value(kwargs),
            )
            if key in prediction_cache:
                cache_hits += 1
                return (None, None, prediction_cache[key])

            result = basic_pitch_predict(
                audio_path,
                basic_pitch_model,
                *args,
                **kwargs,
            )
            if not isinstance(result, tuple) or len(result) < 3:
                raise RuntimeError(
                    f"Unexpected Basic Pitch return shape for {audio_path}"
                )
            note_events = tuple(result[2] or ())
            prediction_cache[key] = note_events
            cache_misses += 1
            return (None, None, note_events)

        def fixed_timing(_path: str | Path) -> Any:
            return timing

        carrier2 = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=33,
            measure_end=48,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )
        carrier3 = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=49,
            measure_end=64,
            predictor=memoized_predict,
            timing_estimator=fixed_timing,
        )

        result2 = _band_result("section2", section2, carrier2, 33, 48)
        result3 = _band_result("section3", section3, carrier3, 49, 64)

        return {
            "schemaVersion": 4,
            "gate": "v143-contextual-prune-historical-band-carrier-diagnostic",
            "executionStrategy": "dual-band-carriers-single-loaded-model-compact-note-cache",
            "sourceSha256": hashlib.sha256(source_audio).hexdigest(),
            "researchNormalizedSha256": _sha256(normalized),
            "section2CacheSha256": _sha256(SECTION2_CACHE),
            "section3CacheSha256": _sha256(SECTION3_CACHE),
            "section2": result2,
            "section3": result3,
            "predictionCache": {
                "entryCount": len(prediction_cache),
                "misses": int(cache_misses),
                "hits": int(cache_hits),
                "expectedUniquePredictions": 8,
                "reusedForSecondBand": cache_hits >= 8,
                "storesNoteEventsOnly": True,
                "singleLoadedBasicPitchModel": True,
            },
            "allHistoricalBandsReplayedWithinTolerance": (
                result2["toleranceSemanticReplayPassed"] is True
                and result3["toleranceSemanticReplayPassed"] is True
            ),
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "professionalReferenceOpened": False,
                "runtimeLabelsRequired": False,
                "frozenModelModified": False,
                "frozenPredictionsModified": False,
                "liveEndpointDeployedOrModified": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    result = diagnose_sections_2_and_3.remote(source.read_bytes(), source.suffix)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
