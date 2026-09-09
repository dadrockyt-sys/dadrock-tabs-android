#!/usr/bin/env python3

import librosa
import numpy as np

CONTRACT = "songsterr-fresh-activation-spectral-valley-rule-v1"
MIN_DURATION_SECONDS = 0.07
MAX_SEARCH_SECONDS = 4.0
ACTIVATION_LOW_THRESHOLD = 0.20
ACTIVATION_SUSTAINED_LOW_FRAMES = 3
ACTIVATION_MIN_DROP = 0.15
ACTIVATION_ONSET_WINDOW_SECONDS = 0.08
SPECTRAL_MIN_DROP_DB = 6.0
SPECTRAL_FRAMES = 3


def fixed_rule_manifest():
    return {
        "contract": CONTRACT,
        "activationLowThreshold": ACTIVATION_LOW_THRESHOLD,
        "activationSustainedLowFrames": ACTIVATION_SUSTAINED_LOW_FRAMES,
        "activationMinimumDrop": ACTIVATION_MIN_DROP,
        "minimumObservedSpanSeconds": MIN_DURATION_SECONDS,
        "maximumSearchSeconds": MAX_SEARCH_SECONDS,
        "spectralCorroborationMinimumDropDb": SPECTRAL_MIN_DROP_DB,
        "spectralCorroborationFrames": SPECTRAL_FRAMES,
        "thresholdSweepUsed": False,
    }


def first_activation_valley(trace, frame_times, source_start, reattack):
    trace = np.asarray(trace)
    frame_times = np.asarray(frame_times)
    start_time = float(source_start) + MIN_DURATION_SECONDS
    stop_time = min(float(source_start) + MAX_SEARCH_SECONDS, float(reattack))
    start = int(np.searchsorted(frame_times, start_time, side="left"))
    stop = int(np.searchsorted(frame_times, stop_time, side="left"))
    if start >= stop:
        return None, "NO_ACTIVATION_SEARCH_WINDOW"

    onset_start = int(np.searchsorted(frame_times, float(source_start), side="left"))
    onset_stop = int(np.searchsorted(
        frame_times,
        float(source_start) + ACTIVATION_ONSET_WINDOW_SECONDS,
        side="right",
    ))
    onset_start = max(0, min(len(trace) - 1, onset_start))
    onset_stop = max(onset_start + 1, min(len(trace), onset_stop))
    onset_peak = float(np.max(trace[onset_start:onset_stop]))

    run = 0
    run_start = None
    saw_sustained_low = False
    saw_drop = False
    for frame in range(start, stop):
        if float(trace[frame]) <= ACTIVATION_LOW_THRESHOLD:
            if run == 0:
                run_start = frame
            run += 1
            if run < ACTIVATION_SUSTAINED_LOW_FRAMES:
                continue
            saw_sustained_low = True
            valley = float(np.mean(trace[run_start:frame + 1]))
            drop = onset_peak - valley
            if drop < ACTIVATION_MIN_DROP:
                continue
            saw_drop = True
            return {
                "frameIndex": int(run_start),
                "timeSeconds": float(frame_times[run_start]),
                "onsetActivationPeak": onset_peak,
                "valleyActivationMean": valley,
                "activationDrop": float(drop),
            }, None
        else:
            run = 0
            run_start = None

    if not saw_sustained_low:
        return None, "NO_SUSTAINED_SUBTHRESHOLD_ACTIVATION"
    if not saw_drop:
        return None, "INSUFFICIENT_ACTIVATION_DROP"
    return None, "NO_QUALIFYING_ACTIVATION_VALLEY"


def spectral_corroboration(
    cqt_db,
    *,
    bin_index,
    source_start,
    valley_time,
    sr,
    hop_length,
):
    release_frame = int(librosa.time_to_frames(
        float(valley_time),
        sr=sr,
        hop_length=hop_length,
    ))
    release_frame = max(0, min(cqt_db.shape[1] - 1, release_frame))
    release_stop = min(cqt_db.shape[1], release_frame + SPECTRAL_FRAMES)
    release_level = float(np.mean(cqt_db[bin_index, release_frame:release_stop]))

    onset_frame = int(librosa.time_to_frames(
        float(source_start),
        sr=sr,
        hop_length=hop_length,
    ))
    onset_frame = max(0, min(cqt_db.shape[1] - 1, onset_frame))
    onset_stop = min(cqt_db.shape[1], onset_frame + 5)
    onset_level = float(np.max(cqt_db[bin_index, onset_frame:onset_stop]))
    spectral_drop = float(onset_level - release_level)

    return {
        "passed": spectral_drop >= SPECTRAL_MIN_DROP_DB,
        "onsetSpectralDb": onset_level,
        "valleySpectralDb": release_level,
        "spectralDropDb": spectral_drop,
        "minimumSpectralDropDb": SPECTRAL_MIN_DROP_DB,
        "spectralFrames": SPECTRAL_FRAMES,
    }


def evaluate_activation_spectral_valley(
    *,
    trace,
    frame_times,
    source_start,
    reattack,
    cqt_db,
    bin_index,
    sr,
    hop_length,
):
    valley, reason = first_activation_valley(
        trace,
        frame_times,
        float(source_start),
        float(reattack),
    )
    if valley is None:
        return None, reason

    corroboration = spectral_corroboration(
        cqt_db,
        bin_index=bin_index,
        source_start=source_start,
        valley_time=valley["timeSeconds"],
        sr=sr,
        hop_length=hop_length,
    )
    if corroboration["passed"] is not True:
        return None, "INSUFFICIENT_SPECTRAL_CORROBORATION"

    observed_span = float(valley["timeSeconds"] - float(source_start))
    if observed_span < MIN_DURATION_SECONDS or float(valley["timeSeconds"]) >= float(reattack):
        return None, "VALLEY_OUTSIDE_VALID_RELEASE_WINDOW"

    return {
        "observedValleySeconds": float(valley["timeSeconds"]),
        "observedSpanFromOnsetSeconds": observed_span,
        "onsetActivationPeak": float(valley["onsetActivationPeak"]),
        "valleyActivationMean": float(valley["valleyActivationMean"]),
        "activationDrop": float(valley["activationDrop"]),
        "onsetSpectralDb": corroboration["onsetSpectralDb"],
        "valleySpectralDb": corroboration["valleySpectralDb"],
        "spectralDropDb": corroboration["spectralDropDb"],
    }, None
