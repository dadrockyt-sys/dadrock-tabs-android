#!/usr/bin/env python3
"""Build the sealed V159 reference-blind timebase artifact.

This stage runs before any Guitar/Bass pitch inference.  It has no professional
reference, scorer, prior-candidate, prior-score, or prior-diagnostic input.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
V158_DIR = HERE.parent / "v158_cpu_multitrack"
if str(V158_DIR) not in sys.path:
    sys.path.insert(0, str(V158_DIR))
import transcribe_v158_base as base  # noqa: E402

SCHEMA = "dadrock.tabs.v159.reference-blind-timebase.v1"
PREREG_BLOB = "2eca55dc344908a791ba7946f42d77fbd7b8926d"
CONTRACT_BLOB = "83dfee2d537d00dbced367bdbc467d167a96db2f"
V158_BASE_BLOB = "5617ff1a6ea301ecaeb898b123b05d2a8c915388"
NORMALIZED_WAV_SHA256 = "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e"
EPS = 1e-12


def positive_unit_scale(x: np.ndarray, label: str) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    if arr.size == 0 or not np.all(np.isfinite(arr)):
        raise RuntimeError(f"V159 {label} onset envelope is empty/nonfinite")
    arr = np.maximum(arr, 0.0)
    maximum = float(np.max(arr))
    if not math.isfinite(maximum) or maximum <= EPS:
        raise RuntimeError(f"V159 {label} onset envelope has no positive energy")
    return arr / maximum


def warning_records(captured: list[warnings.WarningMessage]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in captured:
        rows.append(
            {
                "category": item.category.__name__,
                "message": str(item.message),
                "filename": Path(str(item.filename)).name,
                "lineno": int(item.lineno),
            }
        )
    return rows


def phase_score(evidence: np.ndarray, phase: int) -> float:
    index = np.arange(len(evidence), dtype=int)
    down = evidence[index % 4 == phase]
    other = evidence[index % 4 != phase]
    if down.size == 0 or other.size == 0:
        raise RuntimeError("V159 insufficient beats for four-phase score")
    return float(np.mean(down) - np.mean(other))


def choose_phase(evidence: np.ndarray) -> tuple[int, dict[str, float]]:
    scores = {str(phase): phase_score(evidence, phase) for phase in range(4)}
    selected = 0
    best = scores["0"]
    for phase in range(1, 4):
        score = scores[str(phase)]
        if score > best + EPS:
            selected = phase
            best = score
    return selected, scores


def finite_positive(value: float, label: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise RuntimeError(f"V159 invalid {label}: {result!r}")
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--implementation-contract", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError("V159 timebase artifact is write-once")
    for path in (args.mix, args.guitar, args.bass, args.drums, args.preregistration, args.implementation_contract):
        if not path.is_file():
            raise RuntimeError(f"V159 missing required timebase input: {path}")

    if base.git_blob_sha(V158_DIR / "transcribe_v158_base.py") != V158_BASE_BLOB:
        raise RuntimeError("V159 inherited V158 base-helper identity drift")
    if base.git_blob_sha(args.preregistration) != PREREG_BLOB:
        raise RuntimeError("V159 preregistration Git blob drift")
    if base.git_blob_sha(args.implementation_contract) != CONTRACT_BLOB:
        raise RuntimeError("V159 implementation-contract Git blob drift")
    prereg = json.loads(args.preregistration.read_text(encoding="utf-8"))
    contract = json.loads(args.implementation_contract.read_text(encoding="utf-8"))
    if prereg.get("schema") != "dadrock.tabs.v159.reference-blind-cpu-preregistration.v1" or prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V159 preregistration schema/state invalid")
    if contract.get("schema") != "dadrock.tabs.v159.numeric-implementation-contract.v1" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V159 numeric contract schema/state invalid")

    mix_sha = base.sha256_file(args.mix)
    if mix_sha != NORMALIZED_WAV_SHA256:
        raise RuntimeError(f"V159 normalized mix identity mismatch: {mix_sha}")

    import librosa

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        mix, _ = base.load_mono(args.mix)
        drums, _ = base.load_mono(args.drums)
        bass, _ = base.load_mono(args.bass)
        guitar, _ = base.load_mono(args.guitar)
        env_mix = base.onset_env(mix)
        env_drums = base.onset_env(drums)
        env_bass = base.onset_env(bass)
        env_guitar = base.onset_env(guitar)
        n = min(len(env_mix), len(env_drums))
        if n < 8:
            raise RuntimeError("V159 onset-envelope overlap is too short")
        unit_mix = positive_unit_scale(env_mix[:n], "mix")
        unit_drums = positive_unit_scale(env_drums[:n], "drums")
        fused = 0.5 * unit_mix + 0.5 * unit_drums
        if not np.all(np.isfinite(fused)) or float(np.min(fused)) < 0.0 or float(np.max(fused)) <= 0.0:
            raise RuntimeError("V159 fused beat envelope violates finite/nonnegative/nonzero contract")

        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=fused,
            sr=base.SR,
            hop_length=base.HOP,
            start_bpm=120.0,
            tightness=100.0,
            sparse=True,
        )
        beat_frames = np.asarray(beat_frames, dtype=int)
        if len(beat_frames) < 8:
            raise RuntimeError(f"V159 insufficient detected beat count: {len(beat_frames)}")
        detected = np.asarray(librosa.frames_to_time(beat_frames, sr=base.SR, hop_length=base.HOP), dtype=float)
        if not np.all(np.isfinite(detected)) or not np.all(np.diff(detected) > 0.0):
            raise RuntimeError("V159 detected beat times are nonfinite or not strictly increasing")

        low_flux = base.low_frequency_flux(mix)
        harm_change = base.chroma_change(mix)
        features = {
            "drums": base.sample_feature(base.robust_z(env_drums), beat_frames),
            "mix": base.sample_feature(base.robust_z(env_mix), beat_frames),
            "bass": base.sample_feature(base.robust_z(env_bass), beat_frames),
            "lowFlux": base.sample_feature(base.robust_z(low_flux), beat_frames),
            "harmonicChange": base.sample_feature(base.robust_z(harm_change), beat_frames),
        }
        evidence = (
            1.0 * features["drums"]
            + 0.5 * features["mix"]
            + 0.5 * features["bass"]
            + 0.75 * features["lowFlux"]
            + 0.75 * features["harmonicChange"]
        )
        selected_phase, phase_scores = choose_phase(evidence)

    warnings_out = warning_records(caught)
    runtime_warnings = [row for row in warnings_out if row["category"] == "RuntimeWarning"]
    if runtime_warnings:
        raise RuntimeError(f"V159 fatal rhythm RuntimeWarning(s): {runtime_warnings}")

    tracker_tempo = finite_positive(float(np.asarray(tempo).reshape(-1)[0]), "tracker tempo")
    ibis = np.diff(detected)
    if ibis.size == 0 or not np.all(np.isfinite(ibis)) or not np.all(ibis > 0.0):
        raise RuntimeError("V159 invalid detected inter-beat intervals")
    mean_ibi = finite_positive(float(np.mean(ibis)), "mean IBI")
    median_ibi = finite_positive(float(np.median(ibis)), "median IBI")
    early_period = finite_positive(float(np.median(ibis[: min(8, len(ibis))])), "early IBI")
    leading = int((-selected_phase) % 4)
    prefix = np.asarray(
        [float(detected[0] - k * early_period) for k in range(leading, 0, -1)],
        dtype=float,
    )
    grid_times = np.concatenate([prefix, detected]) if leading else detected.copy()
    if not np.all(np.isfinite(grid_times)) or not np.all(np.diff(grid_times) > 0.0):
        raise RuntimeError("V159 constructed grid times are nonfinite or not strictly increasing")
    grid_steps = 4.0 * np.arange(len(grid_times), dtype=float)

    duration = finite_positive(float(len(mix)) / float(base.SR), "audio duration")
    mean_bpm = 60.0 / mean_ibi
    median_bpm = 60.0 / median_ibi
    count_duration_bpm = 60.0 * float(len(detected)) / duration
    tempo_ratio = median_bpm / tracker_tempo

    payload = {
        "schema": SCHEMA,
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "audioIdentity": {
            "normalizedMixPath": str(args.mix),
            "normalizedMixSha256": mix_sha,
        },
        "stemIdentities": {
            "guitarSha256": base.sha256_file(args.guitar),
            "bassSha256": base.sha256_file(args.bass),
            "drumsSha256": base.sha256_file(args.drums),
        },
        "analysisSampleRate": base.SR,
        "hopLength": base.HOP,
        "audioDurationSeconds": duration,
        "trackerTempoBpm": tracker_tempo,
        "detectedBeatFrames": [int(value) for value in beat_frames],
        "detectedBeatTimesSeconds": [float(value) for value in detected],
        "gridBeatTimesSeconds": [float(value) for value in grid_times],
        "gridBeatSteps": [float(value) for value in grid_steps],
        "selectedPhase": selected_phase,
        "phaseScores": phase_scores,
        "leadingBeatCount": leading,
        "earlyPeriodSeconds": early_period,
        "diagnostics": {
            "detectedBeatCount": int(len(detected)),
            "gridBeatCount": int(len(grid_times)),
            "meanInterBeatIntervalSeconds": mean_ibi,
            "medianInterBeatIntervalSeconds": median_ibi,
            "meanIbiImpliedBpm": mean_bpm,
            "medianIbiImpliedBpm": median_bpm,
            "beatCountDurationBpm": count_duration_bpm,
            "tempoConsistencyRatio": tempo_ratio,
            "fusedEnvelopeMinimum": float(np.min(fused)),
            "fusedEnvelopeMaximum": float(np.max(fused)),
            "fusedEnvelopeMean": float(np.mean(fused)),
            "phaseEvidenceMean": float(np.mean(evidence)),
            "phaseEvidenceStd": float(np.std(evidence)),
            "firstDetectedBeatSeconds": float(detected[0]),
            "lastDetectedBeatSeconds": float(detected[-1]),
            "firstGridBeatSeconds": float(grid_times[0]),
            "lastGridBeatSeconds": float(grid_times[-1]),
            "maximumGridStep": float(grid_steps[-1]),
            "warningCount": len(warnings_out),
        },
        "warnings": warnings_out,
        "sealedInputs": {
            "preregistrationGitBlob": PREREG_BLOB,
            "implementationContractGitBlob": CONTRACT_BLOB,
            "inheritedV158BaseHelperGitBlob": V158_BASE_BLOB,
        },
        "safety": {
            "referenceRead": False,
            "professionalReferencePathsOpened": 0,
            "referenceFacingScoreCalls": 0,
            "priorGeneratedCandidateRead": False,
            "priorScoreRead": False,
            "priorDiagnosticReadByRuntime": False,
            "referenceDerivedTimingConstantsUsed": False,
            "gpu": False,
            "modal": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "timebaseSha256": base.sha256_file(args.output),
                "detectedBeatCount": len(detected),
                "trackerTempoBpm": tracker_tempo,
                "medianIbiImpliedBpm": median_bpm,
                "beatCountDurationBpm": count_duration_bpm,
                "selectedPhase": selected_phase,
                "warningCount": len(warnings_out),
                "referenceRead": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
