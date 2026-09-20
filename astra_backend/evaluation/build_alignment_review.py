"""Build a self-contained audio-only timing review; never load predictions."""
import argparse
import base64
import hashlib
import io
import json
import math
import struct
import wave
from pathlib import Path


def build(wav_path, evidence_path):
    raw = Path(wav_path).read_bytes()
    evidence_raw = Path(evidence_path).read_bytes()
    evidence = json.loads(evidence_raw)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != evidence['audioSha256']:
        raise ValueError('Audio differs from pulse evidence')
    with wave.open(io.BytesIO(raw)) as source:
        if source.getnchannels() != 1 or source.getsampwidth() != 2 or source.getcomptype() != 'NONE':
            raise ValueError('Expected mono PCM16 WAV')
        rate, count = source.getframerate(), source.getnframes()
        pcm = source.readframes(count)
    if len(pcm) != count * 2 or count == 0 or rate != evidence['sampleRate']:
        raise ValueError('Incomplete audio or sample-rate mismatch')
    duration = count / rate
    pulses = evidence['observedFirst33BeatSeconds']
    if not isinstance(pulses, list) or any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or not 0 <= t < duration for t in pulses):
        raise ValueError('Invalid pulse times')
    if any(a >= b for a, b in zip(pulses, pulses[1:])):
        raise ValueError('Pulse times must increase')
    samples = struct.unpack('<' + 'h' * count, pcm)
    stride = max(1, math.ceil(count / 1800))
    peaks = [round(max(abs(v) for v in samples[i:i+stride]) / 32768, 5) for i in range(0, count, stride)]
    data = {'audioSha256': digest, 'evidenceSha256': hashlib.sha256(evidence_raw).hexdigest(),
            'duration': duration, 'pulses': pulses, 'peaks': peaks}
    template = Path(__file__).with_name('alignment_review.html').read_text()
    return template.replace('__DATA__', json.dumps(data, allow_nan=False)).replace('__AUDIO__', base64.b64encode(raw).decode())


def main():
    parser = argparse.ArgumentParser()
    for name in ['wav', 'evidence', 'output']:
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    html = build(args.wav, args.evidence)
    with Path(args.output).open('x') as output:
        output.write(html)


if __name__ == '__main__':
    main()
