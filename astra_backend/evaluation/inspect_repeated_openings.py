"""Audio-only repeated-opening diagnostic; never reads predictions or reference labels."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import wave
from pathlib import Path

import numpy as np


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _normalized_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=float) - float(np.mean(a))
    b = np.asarray(b, dtype=float) - float(np.mean(b))
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else -1.0


def _frames(samples: np.ndarray, size: int, hop: int) -> np.ndarray:
    require(size > 0 and hop > 0 and len(samples) >= size, 'Audio too short for analysis frame')
    view = np.lib.stride_tricks.sliding_window_view(samples, size)[::hop]
    return np.asarray(view)


def _onset_envelope(samples: np.ndarray, sr: int, *, frame: int = 1024, hop: int = 128):
    window = np.hanning(frame)
    frames = _frames(samples, frame, hop) * window
    spectrum = np.abs(np.fft.rfft(frames, axis=1)) / float(np.sum(window))
    freqs = np.fft.rfftfreq(frame, 1 / sr)
    keep = (freqs >= 80) & (freqs <= 5000)
    logged = np.log1p(200 * spectrum[:, keep])
    flux = np.maximum(0, np.diff(logged, axis=0)).sum(axis=1)
    times = (np.arange(1, len(frames)) * hop + frame / 2) / sr
    median = float(np.median(flux))
    mad = float(np.median(np.abs(flux - median)))
    if mad:
        flux = (flux - median) / mad
    return times, flux


def _segment_spectrum(segment: np.ndarray, sr: int, *, frame: int = 1024, hop: int = 64, nfft: int = 8192):
    window = np.hanning(frame)
    frames = _frames(segment, frame, hop) * window
    magnitude = (np.abs(np.fft.rfft(frames, n=nfft, axis=1)) / float(np.sum(window))).T
    freqs = np.fft.rfftfreq(nfft, 1 / sr)
    times = (np.arange(len(frames)) * hop + frame / 2) / sr
    return freqs, times, magnitude


def _ridge_f0(freqs: np.ndarray, times: np.ndarray, magnitude: np.ndarray) -> np.ndarray:
    bands = [(2, 420, 520), (3, 630, 780), (4, 840, 1040)]
    rows = []
    for harmonic, low, high in bands:
        ids = np.flatnonzero((freqs >= low) & (freqs <= high))
        require(len(ids) > 0, 'Harmonic band missing from spectrum')
        peaks = ids[np.argmax(magnitude[ids, :], axis=0)]
        rows.append(freqs[peaks] / harmonic)
    return np.median(np.vstack(rows), axis=0)


def _window_median(times: np.ndarray, values: np.ndarray, start: float, end: float) -> float:
    mask = (times >= start) & (times <= end)
    require(np.any(mask), 'Requested diagnostic window is empty')
    return float(np.median(values[mask]))


def inspect(path: str | Path, *, expected_sha256: str, measure_period_seconds: float,
            measure_count: int = 16) -> dict:
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == expected_sha256, 'Audio SHA256 mismatch')
    require(isinstance(measure_count, int) and not isinstance(measure_count, bool) and 2 <= measure_count <= 64,
            'Invalid measure count')
    require(isinstance(measure_period_seconds, (int, float)) and math.isfinite(measure_period_seconds)
            and 1.0 < measure_period_seconds < 4.0, 'Invalid measure-period prior')
    with wave.open(io.BytesIO(raw)) as audio:
        require((audio.getnchannels(), audio.getsampwidth(), audio.getcomptype()) == (1, 2, 'NONE'),
                'Expected mono PCM16 WAV')
        sr = audio.getframerate()
        samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(float) / 32768
    require(len(samples) / sr >= 0.4 + (measure_count - 1) * (measure_period_seconds - 0.12),
            'Audio too short for requested repeated-opening review')

    onset_times, onset = _onset_envelope(samples, sr)
    opening = np.flatnonzero((onset_times >= .05) & (onset_times <= .16))
    require(len(opening) > 0, 'Opening attack search window is empty')
    opening_index = int(opening[np.argmax(onset[opening])])
    opening_attack = float(onset_times[opening_index])
    pre_roll_frames = 4
    template_start_index = opening_index - pre_roll_frames
    require(template_start_index >= 0, 'Opening template pre-roll is unavailable')
    template_end_time = opening_attack + .36
    template_end_index = int(np.searchsorted(onset_times, template_end_time))
    template = onset[template_start_index:template_end_index]
    require(len(template) >= 8, 'Opening template too short')

    template_starts = [float(onset_times[template_start_index])]
    correlations = [1.0]
    search_half_width = .10
    for _ in range(1, measure_count):
        expected = template_starts[-1] + measure_period_seconds
        left = int(np.searchsorted(onset_times, expected - search_half_width))
        right = int(np.searchsorted(onset_times, expected + search_half_width))
        best = None
        for index in range(left, right + 1):
            if index < 0 or index + len(template) > len(onset):
                continue
            score = _normalized_corr(template, onset[index:index + len(template)])
            candidate = (score, -abs(float(onset_times[index]) - expected), -index)
            if best is None or candidate > best[0]:
                best = (candidate, index, score)
        require(best is not None, 'Unable to match repeated opening within timing prior')
        index, score = best[1], best[2]
        template_starts.append(float(onset_times[index]))
        correlations.append(float(score))

    attack_offset = opening_attack - template_starts[0]
    attacks = [start + attack_offset for start in template_starts]
    segment_length = int(round(.40 * sr))
    spectra = []
    ridge_tracks = []
    spectrum_times = None
    spectrum_freqs = None
    for attack in attacks:
        begin = int(round(attack * sr))
        segment = samples[begin:begin + segment_length]
        require(len(segment) == segment_length, 'Opening segment exceeds audio')
        spectrum_freqs, spectrum_times, magnitude = _segment_spectrum(segment, sr)
        spectra.append(magnitude)
        ridge_tracks.append(_ridge_f0(spectrum_freqs, spectrum_times, magnitude))
    spectra = np.stack(spectra)
    ridge_tracks = np.stack(ridge_tracks)

    summaries = []
    for index, track in enumerate(ridge_tracks):
        early = _window_median(spectrum_times, track, .025, .09)
        crest = _window_median(spectrum_times, track, .145, .22)
        release = _window_median(spectrum_times, track, .29, .34)
        direct_low_high_low = (205 <= early <= 235 and 235 <= crest <= 258 and 207 <= release <= 235
                               and crest - early >= 10 and crest - release >= 10)
        summaries.append({
            'measureOrdinal': index + 1,
            'templateCorrelation': correlations[index],
            'attackTimeSeconds': attacks[index],
            'earlyRidgeHz': early,
            'crestRidgeHz': crest,
            'releaseRidgeHz': release,
            'directLowHighLowContour': bool(direct_low_high_low),
        })

    later_median_spectrum = np.median(spectra[1:], axis=0)
    later_median_track = _ridge_f0(spectrum_freqs, spectrum_times, later_median_spectrum)
    aggregate = {
        'earlyRidgeHz': _window_median(spectrum_times, later_median_track, .025, .09),
        'crestRidgeHz': _window_median(spectrum_times, later_median_track, .145, .22),
        'releaseRidgeHz': _window_median(spectrum_times, later_median_track, .29, .34),
    }
    aggregate['riseHz'] = aggregate['crestRidgeHz'] - aggregate['earlyRidgeHz']
    aggregate['fallHz'] = aggregate['crestRidgeHz'] - aggregate['releaseRidgeHz']
    aggregate['lowHighLowContour'] = bool(
        205 <= aggregate['earlyRidgeHz'] <= 235 and 235 <= aggregate['crestRidgeHz'] <= 258
        and 207 <= aggregate['releaseRidgeHz'] <= 235
        and aggregate['riseHz'] >= 10 and aggregate['fallHz'] >= 10
    )

    spectral_mask = (spectrum_freqs >= 400) & (spectrum_freqs <= 1100)
    time_mask = spectrum_times <= .34
    feature = np.log1p(100 * spectra[:, spectral_mask, :][:, :, time_mask])
    feature = feature - np.mean(feature, axis=1, keepdims=True)
    later_median_feature = np.median(feature[1:], axis=0)
    opening_feature = feature[0]
    later_cluster_closer_count = 0
    cluster_rows = []
    for index in range(1, measure_count):
        to_later = _normalized_corr(feature[index].ravel(), later_median_feature.ravel())
        to_opening = _normalized_corr(feature[index].ravel(), opening_feature.ravel())
        closer = to_later > to_opening
        later_cluster_closer_count += int(closer)
        cluster_rows.append({
            'measureOrdinal': index + 1,
            'correlationToLaterMedian': to_later,
            'correlationToOpeningMeasure': to_opening,
            'closerToLaterMedian': bool(closer),
        })

    return {
        'kind': 'audio-only-repeated-opening-diagnostic',
        'version': 1,
        'audioSha256': digest,
        'numpyVersion': np.__version__,
        'sampleRate': sr,
        'measureCount': measure_count,
        'measurePeriodPriorSeconds': measure_period_seconds,
        'searchHalfWidthSeconds': search_half_width,
        'openingAttackSeconds': opening_attack,
        'openingTemplatePreRollSeconds': attack_offset,
        'measureOpenings': summaries,
        'laterMeasureAggregate': aggregate,
        'directLowHighLowContourCountLaterMeasures': int(sum(r['directLowHighLowContour'] for r in summaries[1:])),
        'laterClusterCloserToItselfThanOpeningCount': later_cluster_closer_count,
        'laterClusterComparisons': cluster_rows,
        'reviewStatus': 'diagnostic-only',
        'measureOneStartVerified': False,
        'bendLabelsAssigned': False,
        'predictionsRead': False,
        'referenceLabelsRead': False,
        'customerDeliveryEligible': False,
        'limitations': [
            'The measure-period prior comes from audio-only pulse evidence, but repeated-opening matching is still a diagnostic rather than approved alignment.',
            'Harmonic ridges are measured in the mixed recording and can be contaminated by other instruments or transients.',
            'The aggregate later-measure contour and cluster separation support a repeated articulation distinction but do not assign private scorer labels by themselves.',
            'No prediction events, normalized reference labels or historical score-maximizing alignment are read.',
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--wav', required=True)
    parser.add_argument('--audio-sha256', required=True)
    parser.add_argument('--measure-period-seconds', required=True, type=float)
    parser.add_argument('--measure-count', type=int, default=16)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    require(not output.exists(), 'Refusing to overwrite existing diagnostic')
    result = inspect(args.wav, expected_sha256=args.audio_sha256,
                     measure_period_seconds=args.measure_period_seconds, measure_count=args.measure_count)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in [
        'kind', 'audioSha256', 'openingAttackSeconds', 'laterMeasureAggregate',
        'directLowHighLowContourCountLaterMeasures', 'laterClusterCloserToItselfThanOpeningCount',
        'reviewStatus']}, sort_keys=True))


if __name__ == '__main__':
    main()
