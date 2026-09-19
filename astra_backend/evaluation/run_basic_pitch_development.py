"""Fixed whole-mix development baseline. No reference input or role assignment."""
import argparse
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import resource
import time

parser = argparse.ArgumentParser()
parser.add_argument('--audio', required=True)
parser.add_argument('--output', required=True)
args = parser.parse_args()
if not Path(args.audio).is_file():
    parser.error("Audio file must exist before model loading.")
# Bound address space; timeout is applied by the caller. This is not a RAM-fit claim.
resource.setrlimit(resource.RLIMIT_AS, (4096 * 1024 * 1024, 4096 * 1024 * 1024))
model = Path(metadata.distribution('basic-pitch').locate_file('basic_pitch/saved_models/icassp_2022/nmp.tflite'))
assert hashlib.sha256(model.read_bytes()).hexdigest() == '3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676'
started = time.monotonic()
from basic_pitch.inference import predict
_, _, notes = predict(args.audio, model_or_model_path=str(model), onset_threshold=0.5,
    frame_threshold=0.3, minimum_note_length=127.7,
    minimum_frequency=82.4068892282175, maximum_frequency=1318.5102276514797,
    multiple_pitch_bends=False, melodia_trick=True, midi_tempo=120)
result = {'kind': 'whole-mix-basic-pitch-development-only', 'roleAssignment': None,
          'customerDeliveryEligible': False, 'accuracyScore': None,
          'audioSha256': hashlib.sha256(Path(args.audio).read_bytes()).hexdigest(),
          'wallSeconds': time.monotonic()-started,
          'peakRssKiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
          'events': [{'start': float(n[0]), 'end': float(n[1]), 'midi': int(n[2]), 'amplitude': float(n[3])} for n in notes]}
Path(args.output).write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k != 'events'}))
print('eventCount',len(notes))
