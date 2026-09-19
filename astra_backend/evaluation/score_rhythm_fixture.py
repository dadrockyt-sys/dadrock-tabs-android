"""Replay the declared rhythm-fixture diagnostic; reference stays scoring-only."""
import argparse
import hashlib
import json
from pathlib import Path
from score_note_onsets import score_note_onsets

parser = argparse.ArgumentParser()
parser.add_argument('--reference', required=True)
parser.add_argument('--spec', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
spec_path = Path(args.spec)
spec = json.loads(spec_path.read_text())
reference_bytes = Path(args.reference).read_bytes()
blob = hashlib.sha1(b'blob '+str(len(reference_bytes)).encode()+b'\0'+reference_bytes).hexdigest()
if blob != spec['referenceGitBlob']:
    raise ValueError('Reference bytes do not match frozen Git blob')
reference = json.loads(reference_bytes)
notes = []
tuning = [64,59,55,50,45,40]
for start in [1]+reference['repeat']['targetMeasureStarts']:
    for index, note in enumerate(reference['notes']):
        measure = start+note['measure']-1
        notes.append({'id': f'{measure}:{index}',
            'start': spec['assumedFirstMeasureSeconds']+((measure-1)*16+note['step'])*60/spec['tempoBpm']/4,
            'midi': tuning[note['stringIndex']]+note['fret']})
prediction_path = Path(spec['predictionFile'])
prediction_bytes = prediction_path.read_bytes()
result = score_note_onsets(json.loads(prediction_bytes)['events'], notes,
    start=spec['windowSeconds'][0], end=spec['windowSeconds'][1], tolerance=spec['onsetToleranceSeconds'])
result.pop('matches')
result.update({'status':spec['status'], 'independentAlignmentVerified':False,
    'overallModelAccuracy':None, 'predictionSha256':hashlib.sha256(prediction_bytes).hexdigest(),
    'specSha256':hashlib.sha256(spec_path.read_bytes()).hexdigest(),
    'interpretation':'Conditional comparison to historical rhythm fixture at assumed zero-offset 129-BPM grid. FP means unmatched to this fixture only. Not three-role or full-song accuracy.',
    'predictionChanged':False, 'modelRerun':False})
Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
