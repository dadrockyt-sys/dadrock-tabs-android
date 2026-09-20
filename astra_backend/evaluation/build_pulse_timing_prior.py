"""Build an audio-only pulse timing prior without selecting a bar/downbeat."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _fit_line(times: list[float], start_index: int) -> dict:
    """Least-squares pulse-period fit over one contiguous pulse run."""
    n = len(times)
    require(n >= 2, 'Need at least two pulses for a fit')
    xs = list(range(n))
    mean_x = (n - 1) / 2
    mean_y = sum(times) / n
    denom = sum((x - mean_x) ** 2 for x in xs)
    period = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, times)) / denom
    intercept = mean_y - period * mean_x
    residuals = [y - (intercept + period * x) for x, y in zip(xs, times)]
    return {
        'pulseStartIndex': start_index,
        'pulseEndIndex': start_index + n - 1,
        'pulseCount': n,
        'beatIntervals': n - 1,
        'timeStart': times[0],
        'timeEnd': times[-1],
        'fittedPeriodSeconds': period,
        'fittedBpm': 60 / period,
        'fittedFirstPulseSeconds': intercept,
        'rmsResidualSeconds': math.sqrt(sum(r * r for r in residuals) / n),
        'maxAbsoluteResidualSeconds': max(abs(r) for r in residuals),
    }


def build_prior(evidence: dict, *, evidence_sha256: str) -> dict:
    require(isinstance(evidence, dict), 'Evidence must be an object')
    require(evidence.get('kind') == 'audio-only-onset-and-pulse-diagnostic', 'Unexpected evidence kind')
    require(evidence.get('predictionsRead') is False, 'Pulse evidence must be independent of predictions')
    require(evidence.get('referenceLabelsRead') is False, 'Pulse evidence must be independent of labels')

    audio_sha = evidence.get('audioSha256')
    require(isinstance(audio_sha, str) and len(audio_sha) == 64 and all(c in '0123456789abcdef' for c in audio_sha),
            'Invalid audio identity')
    frame = evidence.get('frameResolutionSeconds')
    require(finite(frame) and frame > 0, 'Invalid frame resolution')
    pulses = evidence.get('observedFirst33BeatSeconds')
    require(isinstance(pulses, list) and len(pulses) >= 4, 'Need at least four observed pulses')
    require(all(finite(t) and t >= 0 for t in pulses), 'Invalid pulse time')
    require(all(a < b for a, b in zip(pulses, pulses[1:])), 'Pulse times must strictly increase')

    intervals = [b - a for a, b in zip(pulses, pulses[1:])]
    median_interval = statistics.median(intervals)
    deviations = [abs(value - median_interval) for value in intervals]
    mad = statistics.median(deviations)
    robust_sigma = 1.4826 * mad
    # The tracker is quantized to hop frames. Requiring at least three frames of
    # deviation avoids pretending frame jitter is a tempo discontinuity.
    outlier_tolerance = max(3 * robust_sigma, 3 * frame)
    outlier_indices = [i for i, deviation in enumerate(deviations) if deviation > outlier_tolerance]

    anomalies = [{
        'leftPulseIndex': i,
        'rightPulseIndex': i + 1,
        'timeStart': pulses[i],
        'timeEnd': pulses[i + 1],
        'intervalSeconds': intervals[i],
        'deviationFromMedianSeconds': deviations[i],
    } for i in outlier_indices]

    # Split only on clearly irregular observed intervals. These fits are a
    # timing prior, never a bar/downbeat selection or reviewed alignment.
    runs = []
    run_start = 0
    for interval_index in outlier_indices:
        run_end = interval_index
        if run_end - run_start + 1 >= 4:
            runs.append(_fit_line(pulses[run_start:run_end + 1], run_start))
        run_start = interval_index + 1
    if len(pulses) - run_start >= 4:
        runs.append(_fit_line(pulses[run_start:], run_start))

    early = evidence.get('earlyPulseFit')
    early_summary = None
    if isinstance(early, dict):
        keys = ['periodSeconds', 'bpm', 'rmsResidualSeconds', 'maxAbsoluteResidualSeconds']
        if all(finite(early.get(key)) for key in keys):
            early_summary = {key: early[key] for key in keys}

    return {
        'kind': 'audio-only-pulse-timing-prior',
        'version': 1,
        'sourceEvidenceSha256': evidence_sha256,
        'audioSha256': audio_sha,
        'pulseCount': len(pulses),
        'frameResolutionSeconds': frame,
        'medianIntervalSeconds': median_interval,
        'medianPulseRateBpm': 60 / median_interval,
        'medianAbsoluteDeviationSeconds': mad,
        'robustSigmaSeconds': robust_sigma,
        'outlierToleranceSeconds': outlier_tolerance,
        'intervalAnomalies': anomalies,
        'stablePulseRuns': runs,
        'preservedEarlyPulseFit': early_summary,
        'openingSignalContext': {
            'firstRmsAbove001Seconds': evidence.get('firstRmsAbove001Seconds'),
            'firstDetectedOnsetSeconds': evidence.get('firstDetectedOnsetSeconds'),
            'firstObservedPulseSeconds': pulses[0],
        },
        'candidateDownbeats': [],
        'measureOneStartVerified': False,
        'tempoMapVerified': False,
        'reviewStatus': 'diagnostic-only',
        'predictionsRead': False,
        'referenceLabelsRead': False,
        'customerDeliveryEligible': False,
        'limitations': [
            'Observed pulses are audio-only diagnostics and do not identify measure 1, beat number or note ground truth.',
            'Stable-run fits describe tracker phase/rate only; they are not approved timing-map segments for scoring.',
            'Interval anomalies may be tracker errors, expressive timing or real tempo change; this utility does not decide which.',
            'Opening RMS/onset/pulse times are preserved as separate observations and are not collapsed into an invented anchor.',
            'No prediction, professional reference label or score is consulted or produced.'
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Path(args.evidence)
    raw = source.read_bytes()
    evidence = json.loads(raw)
    report = build_prior(evidence, evidence_sha256=hashlib.sha256(raw).hexdigest())
    output = Path(args.output)
    if output.exists():
        raise ValueError('Refusing to overwrite existing report')
    with output.open('x') as stream:
        stream.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
