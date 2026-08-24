from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from v143_reference_free_timing import (
    BEATS_PER_MEASURE,
    STFT_HOP_SAMPLES,
    TIMING_SAMPLE_RATE,
    _dynamic_beat_frames,
    _finite_audio,
    _normalized_onset_envelope,
    _refine_beat_frames,
    _resample_audio,
    _tempo_from_onsets,
)

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_HISTORICAL_TEMPO_BPM = 129.19921875
EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4 = 1
EXPECTED_HISTORICAL_FIRST_BEAT_IN_MEASURE = 3


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _phase_scores(accents: np.ndarray) -> list[float]:
    values = np.asarray(accents, dtype=np.float64)
    indices = np.arange(len(values), dtype=int)
    scores: list[float] = []
    for phase in range(BEATS_PER_MEASURE):
        mask = (indices % BEATS_PER_MEASURE) == phase
        if int(np.sum(mask)) < 2 or int(np.sum(~mask)) < 2:
            scores.append(float("-inf"))
            continue
        scores.append(float(np.mean(values[mask]) - np.mean(values[~mask])))
    return scores


def _phase_summary(accents: np.ndarray) -> dict[str, Any]:
    scores = _phase_scores(accents)
    finite = [(index, score) for index, score in enumerate(scores) if math.isfinite(score)]
    if not finite:
        raise RuntimeError("no finite bar-phase scores")
    ordered = sorted(finite, key=lambda item: item[1], reverse=True)
    winner, top = ordered[0]
    runner_up = ordered[1][1] if len(ordered) >= 2 else top
    spread = max(float(np.std(accents)), 1e-9)
    return {
        "winnerDownbeatIndexMod4": int(winner),
        "winnerFirstBeatInMeasure": int((-winner) % BEATS_PER_MEASURE),
        "scores": [float(score) if math.isfinite(score) else None for score in scores],
        "topMinusRunnerUp": float(top - runner_up),
        "normalizedTopMinusRunnerUp": float((top - runner_up) / spread),
        "beatAccentMean": float(np.mean(accents)),
        "beatAccentStd": float(np.std(accents)),
    }


def _window_summaries(accents: np.ndarray, *, window_beats: int, stride_beats: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    count = len(accents)
    if count < window_beats:
        return rows
    for start in range(0, count - window_beats + 1, stride_beats):
        end = start + window_beats
        summary = _phase_summary(accents[start:end])
        rows.append(
            {
                "startBeatIndex": int(start),
                "endBeatIndexExclusive": int(end),
                "winnerDownbeatIndexMod4RelativeToGlobalSequence": int(
                    (start + int(summary["winnerDownbeatIndexMod4"])) % BEATS_PER_MEASURE
                ),
                "winnerDownbeatIndexMod4WithinWindow": int(summary["winnerDownbeatIndexMod4"]),
                "topMinusRunnerUp": float(summary["topMinusRunnerUp"]),
                "normalizedTopMinusRunnerUp": float(summary["normalizedTopMinusRunnerUp"]),
            }
        )
    return rows


def _window_vote(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(int(row["winnerDownbeatIndexMod4RelativeToGlobalSequence"]) for row in rows)
    total = len(rows)
    return {
        "windowCount": total,
        "winnerCounts": {str(key): counts[key] for key in sorted(counts)},
        "historicalPhaseWinnerCount": int(counts.get(EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4, 0)),
        "historicalPhaseWinnerRate": _rate(int(counts.get(EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4, 0)), total),
        "dominantPhase": int(max(counts, key=counts.get)) if counts else None,
        "dominantPhaseCount": int(max(counts.values())) if counts else 0,
        "dominantPhaseRate": _rate(int(max(counts.values())) if counts else 0, total),
    }


def diagnose(audio_path: Path) -> dict[str, Any]:
    samples, sample_rate = sf.read(str(audio_path), dtype="float32", always_2d=False)
    mono = _finite_audio(samples)
    analysis_audio = _resample_audio(mono, int(sample_rate), TIMING_SAMPLE_RATE)
    onset, low_energy, frame_times = _normalized_onset_envelope(analysis_audio, TIMING_SAMPLE_RATE)
    hop_seconds = STFT_HOP_SAMPLES / float(TIMING_SAMPLE_RATE)
    tempo_bpm, period_frames, tempo_confidence = _tempo_from_onsets(
        onset,
        hop_seconds,
        min_tempo_bpm=55.0,
        max_tempo_bpm=210.0,
    )
    beat_frames = _dynamic_beat_frames(onset, period_frames)
    beat_frames = _refine_beat_frames(beat_frames, onset, period_frames)
    beat_times = frame_times[beat_frames]
    if len(beat_times) < 8 or np.any(np.diff(beat_times) <= 0.0):
        raise RuntimeError("invalid full-mix beat sequence")

    views = {
        "combinedExistingEstimator": onset[beat_frames] + 0.25 * low_energy[beat_frames],
        "onsetOnly": onset[beat_frames],
        "lowBandOnly": low_energy[beat_frames],
    }

    global_views: dict[str, Any] = {}
    windows16: dict[str, Any] = {}
    windows32_stride16: dict[str, Any] = {}
    for name, accents in views.items():
        global_views[name] = _phase_summary(accents)
        rows16 = _window_summaries(accents, window_beats=16, stride_beats=16)
        rows32 = _window_summaries(accents, window_beats=32, stride_beats=16)
        windows16[name] = {"vote": _window_vote(rows16), "windows": rows16}
        windows32_stride16[name] = {"vote": _window_vote(rows32), "windows": rows32}

    global_winners = {
        name: int(summary["winnerDownbeatIndexMod4"])
        for name, summary in global_views.items()
    }
    all_global_agree = len(set(global_winners.values())) == 1
    historical_global_agreement = sum(
        winner == EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4
        for winner in global_winners.values()
    )

    combined16_vote = windows16["combinedExistingEstimator"]["vote"]
    combined32_vote = windows32_stride16["combinedExistingEstimator"]["vote"]

    return {
        "schemaVersion": 1,
        "mode": "v143-reference-free-fullmix-bar-phase-stability-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "newInferenceUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "analysis": {
            "sourceSampleRate": int(sample_rate),
            "analysisSampleRate": TIMING_SAMPLE_RATE,
            "trackedBeatCount": int(len(beat_frames)),
            "firstTrackedBeatSeconds": float(beat_times[0]),
            "lastTrackedBeatSeconds": float(beat_times[-1]),
            "tempoBpm": float(tempo_bpm),
            "tempoConfidence": float(tempo_confidence),
            "historicalTempoBpm": EXPECTED_HISTORICAL_TEMPO_BPM,
            "tempoDeltaBpm": float(tempo_bpm - EXPECTED_HISTORICAL_TEMPO_BPM),
        },
        "historicalBarPhase": {
            "downbeatIndexMod4": EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4,
            "firstBeatInMeasure": EXPECTED_HISTORICAL_FIRST_BEAT_IN_MEASURE,
        },
        "globalViews": global_views,
        "globalWinnerAgreement": {
            "winners": global_winners,
            "allThreeViewsAgree": bool(all_global_agree),
            "viewsMatchingHistoricalPhase": int(historical_global_agreement),
            "allThreeViewsMatchHistoricalPhase": historical_global_agreement == len(global_winners),
        },
        "nonOverlapping16BeatWindows": windows16,
        "overlapping32BeatWindowsStride16": windows32_stride16,
        "diagnosticFlags": {
            "combinedGlobalMatchesHistoricalPhase": int(global_views["combinedExistingEstimator"]["winnerDownbeatIndexMod4"]) == EXPECTED_HISTORICAL_DOWNBEAT_INDEX_MOD4,
            "combined16WindowHistoricalWinRateAtLeast75Percent": float(combined16_vote["historicalPhaseWinnerRate"]) >= 0.75,
            "combined32WindowHistoricalWinRateAtLeast75Percent": float(combined32_vote["historicalPhaseWinnerRate"]) >= 0.75,
            "allGlobalAccentViewsAgree": bool(all_global_agree),
            "allGlobalAccentViewsMatchHistoricalPhase": historical_global_agreement == len(global_winners),
        },
        "interpretationBoundary": (
            "This reruns only the existing reference-free full-mix timing front end and tests whether its chosen 4/4 bar phase is stable across accent views and local beat windows. "
            "It does not consult labels or the professional reference and does not select or mutate a replacement phase."
        ),
        "invariants": {
            "referenceConsulted": False,
            "modalInvoked": False,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
        },
    }


def main(source: str, destination: str) -> None:
    report = diagnose(Path(source))
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "analysis": report["analysis"],
        "globalWinnerAgreement": report["globalWinnerAgreement"],
        "combined16Vote": report["nonOverlapping16BeatWindows"]["combinedExistingEstimator"]["vote"],
        "combined32Vote": report["overlapping32BeatWindowsStride16"]["combinedExistingEstimator"]["vote"],
        "flags": report["diagnosticFlags"],
    }, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_reference_free_fullmix_bar_phase_stability_diagnostic.py WAV OUTPUT")
    main(sys.argv[1], sys.argv[2])
