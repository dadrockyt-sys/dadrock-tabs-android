from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from statistics import mean
from typing import Any

import modal

from v143_ai_tab_gpu_worker import image as separator_gpu_image


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"

MODEL_FILES = (
    "intro-correlation-safe-grid-event-selector-model.json",
    "intro-correlation-safe-sequence-event-model.json",
    "fresh-17-96-correlation-safe-sequence-frozen-events.json",
    "contextual-prune-frozen-model.json",
)

SHADOW_MODULES = (
    "v143_ai_tab_gpu_worker",
    "v143_candidate_timing_adapter",
    "v143_reference_free_timing",
    "v143_contextual_prune_reference_free_carrier",
    "v143_contextual_prune_runtime",
    "v143_contextual_prune_shadow_correction",
    "v143_correlation_safe_fixed_count_reranker_freeze",
    "v143_intro_sequence_event_model",
    "v143_intro_learned_grid_event_selector",
    "v143_intro_learned_onset_spectral_set_model",
    "v143_intro_raw_attack_temporal_diagnostic",
    "v143_intro_repetition_recovery_event_selector",
    "v143_intro_supervised_temporal_assignment",
    "v143_deterministic_separator",
    "v143_seeded_separator",
    "v143_production_separator",
    "v143_seeded_audio_separator_cli",
)

app = modal.App("dadrock-v143-contextual-prune-correction-shadow")

shadow_image = (
    separator_gpu_image
    .pip_install(
        "setuptools==81.0.0",
        "basic-pitch",
        "librosa",
        "scipy",
        "soundfile",
    )
    .add_local_python_source(*SHADOW_MODULES)
)
for filename in MODEL_FILES:
    shadow_image = shadow_image.add_local_file(
        CAL / filename,
        f"/public/training/v143-musical-reconstruction-calibration/{filename}",
    )


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
            "Reference-free research normalization failed:\n"
            + (result.stderr or result.stdout or "unknown ffmpeg error")[-4000:]
        )
    if not destination.exists() or destination.stat().st_size <= 0:
        raise RuntimeError("Reference-free research normalization produced no audio")
    return destination


def _build_shadow_stems(normalized: Path, output_dir: Path) -> tuple[dict[str, Any], Path, Path]:
    from v143_deterministic_separator import build_deterministic_v143_stems

    stems = build_deterministic_v143_stems(normalized, output_dir)
    direct = Path(str(stems.get("directGuitar") or ""))
    cascade = Path(str(stems.get("cascadeGuitar") or ""))
    for label, path in (("direct", direct), ("cascade", cascade)):
        if not path.exists() or path.stat().st_size <= 0:
            raise RuntimeError(f"Correction shadow {label} guitar view is missing: {path}")
    if stems.get("deterministic") is not True or stems.get("referenceFree") is not True:
        raise RuntimeError("Correction shadow separator lost deterministic reference-free invariants")
    return stems, direct, cascade


def _pitch_count_summary(values: dict[tuple[int, int], tuple[int, ...]]) -> dict[str, Any]:
    counts = [len(midis) for midis in values.values()]
    return {
        "observedEventCount": len(counts),
        "totalPitchHypotheses": int(sum(counts)),
        "meanPitchHypotheses": float(mean(counts)) if counts else 0.0,
        "maxPitchHypotheses": max(counts, default=0),
        "eventsWithFiveOrMore": sum(1 for count in counts if count >= 5),
        "eventsWithSixOrMore": sum(1 for count in counts if count >= 6),
    }


@app.function(
    image=shadow_image,
    gpu="L4",
    timeout=1800,
    memory=12288,
)
def analyze_reference_free_correction_shadow(
    source_audio: bytes,
    suffix: str = ".audio",
    measure_start: int = 1,
    measure_end: int = 113,
) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("source_audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Correction shadow audio cannot exceed 50 MB")

    from v143_contextual_prune_reference_free_carrier import (
        build_contextual_prune_reference_free_carrier,
    )
    from v143_contextual_prune_runtime import run_contextual_prune
    from v143_contextual_prune_shadow_correction import (
        apply_reference_free_shadow_correction,
    )

    with tempfile.TemporaryDirectory(prefix="v143-correction-shadow-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, normalized)

        stems, direct, cascade = _build_shadow_stems(normalized, root / "stems")
        carrier = build_contextual_prune_reference_free_carrier(
            normalized,
            (direct, cascade),
            measure_start=int(measure_start),
            measure_end=int(measure_end),
        )
        targets = set(range(carrier.measure_start, carrier.measure_end + 1))
        base = run_contextual_prune(
            carrier.rows_by_measure,
            carrier.grid,
            targets,
            context_measures=targets,
        )
        correction = apply_reference_free_shadow_correction(
            carrier.rows,
            carrier.grid,
            base.candidate_events,
            targets,
        )

        base_measures = {measure for measure, _step in base.candidate_events}
        corrected_measures = {measure for measure, _step in correction.corrected_events}
        missing_before = sorted(targets - base_measures)
        missing_after = sorted(targets - corrected_measures)
        before_pitch = _pitch_count_summary(correction.original_pitch_sets)
        after_pitch = _pitch_count_summary(correction.pitch_sets)

        pitch_changes = []
        for key in sorted(correction.pitch_sets):
            before = correction.original_pitch_sets.get(key, ())
            after = correction.pitch_sets.get(key, ())
            if before == after:
                continue
            pitch_changes.append(
                {
                    "measure": int(key[0]),
                    "step": int(key[1]),
                    "beforeMidis": list(before),
                    "afterMidis": list(after),
                    "suppressedCount": max(0, len(before) - len(after)),
                }
            )

        return {
            "schemaVersion": 1,
            "mode": "v143-contextual-prune-reference-free-correction-shadow",
            "sourceSha256": _sha256_bytes(source_audio),
            "measureStart": carrier.measure_start,
            "measureEnd": carrier.measure_end,
            "carrier": carrier.summary(),
            "baseSelector": base.diagnostics(),
            "correction": correction.diagnostics(),
            "coverage": {
                "targetMeasureCount": len(targets),
                "populatedMeasureCountBefore": len(base_measures),
                "populatedMeasureCountAfter": len(corrected_measures),
                "missingMeasuresBefore": missing_before,
                "missingMeasuresAfter": missing_after,
            },
            "pitchSupport": {
                "before": before_pitch,
                "after": after_pitch,
                "changedEventCount": len(pitch_changes),
                "suppressedPitchCount": correction.suppressed_pitch_count,
            },
            "rescuedEvents": [
                {"measure": int(measure), "step": int(step)}
                for measure, step in sorted(correction.rescued_events)
            ],
            "pitchChanges": pitch_changes,
            "separator": {
                "deterministic": stems.get("deterministic") is True,
                "referenceFree": stems.get("referenceFree") is True,
                "settings": dict(stems.get("settings") or {}),
                "models": dict(stems.get("models") or {}),
            },
            "invariants": {
                "sourceIsApprovedFixture": _sha256_bytes(source_audio) == APPROVED_AUDIO_SHA256,
                "referenceFree": True,
                "runtimeLabelsRequired": False,
                "baseEventsPreserved": base.candidate_events.issubset(correction.corrected_events),
                "rescuedEventsPhysicallyObserved": correction.diagnostics()["rescuesAreObservedSlots"],
                "candidateRelocatesEvents": False,
                "liveRhythmOutputChanged": False,
                "leadChanged": False,
                "bassChanged": False,
                "productionModified": False,
            },
        }


@app.local_entrypoint(name="approved_audio")
def approved_audio(
    audio_path: str = "public/gomywayfullaitest.m4a",
    output_path: str = "debug/v143-contextual-prune/shadow-correction-approved-audio.json",
) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Approved audio fixture missing or empty: {source}")
    source_bytes = source.read_bytes()
    source_sha = _sha256_bytes(source_bytes)
    if source_sha != APPROVED_AUDIO_SHA256:
        raise RuntimeError(
            f"Approved audio SHA changed: {source_sha} != {APPROVED_AUDIO_SHA256}"
        )
    result = analyze_reference_free_correction_shadow.remote(
        source_bytes,
        source.suffix,
        1,
        113,
    )
    if result.get("invariants", {}).get("sourceIsApprovedFixture") is not True:
        raise RuntimeError("Correction shadow did not receive the approved fixture")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["correction"], sort_keys=True))
    print(json.dumps(result["coverage"], sort_keys=True))
    print(json.dumps(result["pitchSupport"], sort_keys=True))
    print(f"WROTE={output}")


if __name__ == "__main__":
    pass
