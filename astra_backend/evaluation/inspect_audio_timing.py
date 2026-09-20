"""Audio-only timing evidence. No predictions, reference notes or offset search."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--audio', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
import librosa
import numpy as np
x, sr = librosa.load(args.audio, sr=None, mono=True)
hop = 128
strength = librosa.onset.onset_strength(y=x, sr=sr, hop_length=hop)
onsets = librosa.onset.onset_detect(onset_envelope=strength, sr=sr, hop_length=hop, units='time')
tempo, beats = librosa.beat.beat_track(onset_envelope=strength, sr=sr, hop_length=hop, units='time')
rms = librosa.feature.rms(y=x, frame_length=512, hop_length=hop, center=False)[0]
active = np.flatnonzero(rms > .01)
# Predefined early audio window, chosen without consulting note matches.
early = beats[(beats >= .5) & (beats < 12)]
fit = None
if len(early) >= 4:
    indices = np.arange(len(early))
    period, intercept = np.polyfit(indices, early, 1)
    residuals = early - (intercept + period*indices)
    fit = {'windowSeconds':[.5,12], 'beatCount':len(early), 'periodSeconds':float(period),
           'bpm':float(60/period), 'firstFittedPulseSeconds':float(intercept),
           'rmsResidualSeconds':float(np.sqrt(np.mean(residuals**2))),
           'maxAbsoluteResidualSeconds':float(np.max(np.abs(residuals))),
           'differenceFrom129BpmOver60BeatIntervalsSeconds':float(60*(period-60/129))}
result = {'kind':'audio-only-onset-and-pulse-diagnostic',
          'audioSha256':hashlib.sha256(Path(args.audio).read_bytes()).hexdigest(),
          'librosaVersion':importlib.metadata.version('librosa'), 'sampleRate':sr,
          'sampleCount':len(x), 'hopSamples':hop, 'frameResolutionSeconds':hop/sr,
          'tempoEstimateBpm':float(np.asarray(tempo).reshape(-1)[0]),
          'firstRmsAbove001Seconds':float(active[0]*hop/sr) if len(active) else None,
          'onsetSeconds':onsets.tolist(), 'beatSeconds':beats.tolist(), 'earlyPulseFit':fit,
          'measureOneStartVerified':False, 'tempoMapVerified':False,
          'referenceLabelsRead':False, 'predictionsRead':False,
          'limitations':['Beat tracker output is estimated pulse timing, not bar/downbeat or note-onset ground truth.',
                         'RMS threshold crossing is not a musical downbeat.',
                         'Early pulse fit is descriptive, not a full-recording tempo map.',
                         'No accuracy score or alignment selected by prediction matching.']}
Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['onsetSeconds','beatSeconds','limitations']}))
