"""Score immutable, reviewed development labels; never import an audio model."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from score_note_onsets import score_note_onsets


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_verified(path, digest):
    raw = Path(path).read_bytes()
    require(isinstance(digest, str) and hashlib.sha256(raw).hexdigest() == digest, 'Artifact hash mismatch')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def score_bundle(spec, *, predictions_path, labels_path, alignment_path):
    require(spec.get('version') == 1, 'Unsupported bundle version')
    require(spec.get('pitchPolicy') == 'reviewed-sounding-midi-at-attack', 'Pitch policy must be explicit')
    require(spec.get('scope') in ['whole-mix-to-rhythm', 'whole-mix-to-combined-reference'], 'Unsupported comparison scope')
    roles = ['rhythm'] if spec['scope'] == 'whole-mix-to-rhythm' else ['bass', 'lead', 'rhythm']
    prediction = load_verified(predictions_path, spec['predictionSha256'])
    labels = load_verified(labels_path, spec['labelsSha256'])
    alignment = load_verified(alignment_path, spec['alignmentSha256'])
    audio = spec['audioSha256']
    require(isinstance(audio, str) and len(audio) == 64 and all(c in '0123456789abcdef' for c in audio), 'Invalid audio identity')
    require(all(doc.get('audioSha256') == audio for doc in [prediction, labels, alignment]), 'Audio identity mismatch')
    require(labels.get('reviewStatus') == 'complete' and labels.get('unresolvedItems') == [], 'Label review incomplete')
    require(alignment.get('reviewStatus') == 'complete' and alignment.get('independentOfPredictions') is True,
            'Independent alignment review incomplete')
    require(isinstance(alignment.get('evidenceId'), str) and alignment['evidenceId'].strip(), 'Alignment evidence identity missing')
    require(labels.get('pitchPolicy') == spec['pitchPolicy'], 'Label pitch policy mismatch')
    require(sorted(labels.get('roles', [])) == sorted(roles), 'Reference role coverage mismatch')
    sources = spec.get('sourceSha256ByRole', {})
    require(set(sources) == set(roles), 'Source identities missing')
    require(all(isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v) for v in sources.values()), 'Invalid source digest')
    require(labels.get('sourceSha256ByRole') == sources, 'Professional source identity mismatch')
    start, end = spec['windowSeconds']
    require(finite(start) and finite(end) and 0 <= start < end, 'Invalid scoring window')
    require(labels.get('windowSeconds') == [start, end], 'Label window mismatch')
    segments = alignment.get('segments')
    require(isinstance(segments, list) and segments, 'Missing timing segments')
    previous = None
    for seg in segments:
        require(all(finite(seg.get(k)) for k in ['beatStart', 'beatEnd', 'timeStart', 'timeEnd']), 'Invalid timing segment')
        require(seg['beatStart'] >= 0 and seg['beatEnd'] > seg['beatStart'] and 0 <= seg['timeStart'] < seg['timeEnd'], 'Non-monotonic timing segment')
        if previous:
            require(seg['beatStart'] == previous['beatEnd'] and seg['timeStart'] == previous['timeEnd'], 'Timing gap or overlap')
        previous = seg
    require(segments[0]['timeStart'] <= start and segments[-1]['timeEnd'] >= end, 'Timing map does not cover scoring window')
    def timestamp(beat):
        require(finite(beat), 'Invalid score beat')
        for seg in segments:
            if seg['beatStart'] <= beat <= seg['beatEnd']:
                fraction = (beat-seg['beatStart'])/(seg['beatEnd']-seg['beatStart'])
                return seg['timeStart'] + fraction*(seg['timeEnd']-seg['timeStart'])
        raise ValueError('Event outside timing map')
    rows = labels.get('events')
    require(isinstance(rows, list), 'Missing reviewed event list')
    targets, ids = [], set()
    for row in rows:
        identity = row.get('id')
        require(isinstance(identity, str) and identity.strip() and identity not in ids, 'Duplicate or missing reference identity')
        ids.add(identity)
        require(row.get('role') in roles, 'Unexpected reference role')
        require(row.get('reviewStatus') == 'complete', 'Unreviewed event')
        kind = row.get('kind')
        require(kind in ['attack', 'rest', 'tie-continuation', 'bend-continuation'], 'Unknown event kind')
        onset = timestamp(row.get('beat'))
        require(start <= onset < end, 'Reference event outside scored window')
        if kind == 'attack':
            midi = row.get('midi')
            require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'Unresolved attack pitch')
            targets.append({'id': identity, 'midi': midi, 'start': onset})
        else:
            require('midi' not in row, 'Non-attack event cannot add pitched target')
    require(labels.get('coverageReviewed') is True, 'Rests/measure coverage review missing')
    # Multiple roles playing the same MIDI at the same instant are one acoustic target.
    if len(roles) > 1:
        unique = {}
        for target in targets:
            unique.setdefault((target['start'], target['midi']), target)
        merged = len(targets)-len(unique)
        targets = list(unique.values())
    else:
        merged = 0
    metrics = score_note_onsets(prediction['events'], targets, start=start, end=end,
                                tolerance=spec['onsetToleranceSeconds'])
    metrics.pop('matches')  # No private labels or matched reference IDs in the report.
    return {'status': 'scored-reviewed-development-bundle', 'scope': spec['scope'],
            'metrics': metrics, 'mergedCoincidentRoleTargets': merged,
            'customerDeliveryEligible': False, 'roleAccuracy': None,
            'inputHashes': {k: spec[k] for k in ['predictionSha256', 'labelsSha256', 'alignmentSha256', 'audioSha256']},
            'limitations': ['Reviews are asserted by the supplied bundle; hashes bind bytes, not musical truth.',
                            'No duration, technique, fingering or three-role separation score.',
                            'Unmatched whole-mix events may be outside the reference scope.']}


def main():
    parser = argparse.ArgumentParser()
    for flag in ['spec', 'predictions', 'labels', 'alignment', 'output']:
        parser.add_argument('--'+flag, required=True)
    args = parser.parse_args()
    output = Path(args.output)
    require(not output.exists(), 'Refusing to overwrite an existing scoring report')
    spec = json.loads(Path(args.spec).read_text())
    result = score_bundle(spec, predictions_path=args.predictions, labels_path=args.labels, alignment_path=args.alignment)
    result['specSha256'] = hashlib.sha256(Path(args.spec).read_bytes()).hexdigest()
    # Exclusive creation also prevents a concurrent overwrite after validation.
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')

if __name__ == '__main__':
    main()
