"""Bounded audio-only diagnostic, not a transcription or alignment approval."""
import argparse
import hashlib
import io
import json
import time
import wave
from pathlib import Path
import numpy as np


def inspect(path, expected_sha256):
    started = time.monotonic()
    raw = Path(path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError('Audio SHA256 mismatch')
    with wave.open(io.BytesIO(raw)) as audio:
        if (audio.getnchannels(), audio.getsampwidth(), audio.getcomptype()) != (1, 2, 'NONE'):
            raise ValueError('Expected mono PCM16 WAV')
        sr = audio.getframerate()
        samples = np.frombuffer(audio.readframes(sr), dtype='<i2').astype(float) / 32768
    if len(samples) != sr:
        raise ValueError('At least one second of audio required')
    size = max(1, round(sr * .001))
    rms = np.array([np.sqrt(np.mean(samples[i:i+size]**2)) for i in range(0, len(samples)-size+1, size)])
    energy = []
    for threshold in [.001, .005, .01, .02, .05]:
        for consecutive in [1, 10]:
            indices = np.flatnonzero(np.convolve((rms > threshold).astype(int), np.ones(consecutive, dtype=int), 'valid') == consecutive)
            energy.append({'rmsThreshold': threshold, 'consecutiveBins': consecutive,
                           'firstTimeSeconds': float(indices[0]*size/sr) if len(indices) else None})
    candidates = np.arange(180, 281, .25)
    harmonic_rows = []
    for t in [.08, .10, .12, .14, .16, .18, .20, .22, .24, .26, .28, .30, .32, .34, .36, .38, .40]:
        frame = samples[int(t*sr):int((t+.06)*sr)]
        spectrum = np.abs(np.fft.rfft(frame*np.hanning(len(frame)), n=32768))
        frequencies = np.fft.rfftfreq(32768, 1/sr)
        row = {'windowStartSeconds': t, 'windowDurationSeconds': .06}
        for name, harmonics in [('harmonics234Hz', [2,3,4]), ('harmonics3456Hz', [3,4,5,6])]:
            values = np.array([np.interp(candidates*k, frequencies, spectrum) for k in harmonics])
            support = np.exp(np.log(values+1e-8).mean(axis=0))
            row[name] = float(candidates[support.argmax()])
        harmonic_rows.append(row)
    return {'kind': 'opening-attack-audio-diagnostic', 'audioSha256': digest,
            'numpyVersion': np.__version__, 'sampleRate': sr, 'analyzedSeconds': 1,
            'energyBinSamples': size, 'energyBinSeconds': size/sr,
            'energyThresholdObservations': energy, 'harmonicSearchHz': [180,280.75],
            'harmonicSearchStepHz': .25, 'fftSize': 32768, 'harmonicObservations': harmonic_rows,
            'runtimeSeconds': time.monotonic()-started,
            'measureOneTimeSeconds': None, 'bendAttackMidi': None, 'reviewStatus': 'diagnostic-only',
            'predictionsRead': False, 'labelsRead': False, 'customerDeliveryEligible': False,
            'limitations': ['Energy thresholds locate signal activity, not a verified guitar onset.',
                           'Harmonic search is restricted to 180-280.75 Hz; it cannot identify arbitrary pitches.',
                           'The two harmonic subsets overlap and are not independent estimators.',
                           'Windows mix 60 ms of changing sound; zero padding does not improve physical resolution.',
                           'Mixed instruments and transient noise can dominate; no confidence or note truth is assigned.']}


def main():
    parser = argparse.ArgumentParser()
    for arg in ['wav','audio-sha256','output']:
        parser.add_argument('--'+arg, required=True)
    args = parser.parse_args()
    result = inspect(args.wav, args.audio_sha256)
    with Path(args.output).open('x') as out:
        out.write(json.dumps(result, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
