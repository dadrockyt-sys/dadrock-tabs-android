"""Reference-blind physical-continuity refinement for attacked-bend candidates."""
from __future__ import annotations

import math
import numpy as np

from extract_raw_bend_starts import (
    MIDI_OFFSET,
    CONTOUR_BINS_PER_SEMITONE,
    model_frame_times,
    require,
    validate_raw,
)

GLIDE_WINDOW_SECONDS = (0.035, 0.240)
MIN_ACTIVE_CONTOUR_SALIENCE = 0.15
MIN_ACTIVE_FRAMES = 8
MIN_UNIQUE_CONTOUR_BINS = 4
MAX_FRAME_JUMP_SEMITONES = 1.0
MIN_NONDECREASING_FRACTION = 0.90
PITCH_FLOOR_OFFSET = -1.0
PITCH_CEILING_OFFSET = 3.5
FLOAT_EPSILON = 1e-9


def glide_features(raw, candidate):
    validate_raw(raw)
    contour = raw['contour']
    times = model_frame_times(contour.shape[0])
    time = candidate.get('time')
    midi = candidate.get('midi')
    require(isinstance(time, (int, float)) and not isinstance(time, bool) and math.isfinite(time), 'invalid candidate time')
    require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'invalid candidate midi')
    left = int(np.searchsorted(times, time + GLIDE_WINDOW_SECONDS[0], side='left'))
    right = int(np.searchsorted(times, time + GLIDE_WINDOW_SECONDS[1], side='right'))
    low_bin = max(0, int(math.floor((midi + PITCH_FLOOR_OFFSET - MIDI_OFFSET) * CONTOUR_BINS_PER_SEMITONE)))
    high_bin = min(contour.shape[1], int(math.ceil((midi + PITCH_CEILING_OFFSET - MIDI_OFFSET) * CONTOUR_BINS_PER_SEMITONE)) + 1)
    require(right > left and high_bin > low_bin, 'candidate contour window unavailable')
    block = contour[left:right, low_bin:high_bin]
    maxima = np.argmax(block, axis=1)
    salience = block[np.arange(len(maxima)), maxima]
    pitches = MIDI_OFFSET + (low_bin + maxima) / CONTOUR_BINS_PER_SEMITONE
    active = salience >= MIN_ACTIVE_CONTOUR_SALIENCE
    active_pitches = pitches[active]
    if len(active_pitches) < 2:
        return {
            'activeFrameCount': int(len(active_pitches)),
            'uniqueContourBinCount': int(len(set(active_pitches.tolist()))),
            'maxFrameJumpSemitones': None,
            'nondecreasingFraction': None,
            'netRiseSemitones': None,
        }
    diffs = np.diff(active_pitches)
    return {
        'activeFrameCount': int(len(active_pitches)),
        'uniqueContourBinCount': int(len(set(active_pitches.tolist()))),
        'maxFrameJumpSemitones': float(np.max(np.abs(diffs))),
        'nondecreasingFraction': float(np.mean(diffs >= -1 / CONTOUR_BINS_PER_SEMITONE)),
        'netRiseSemitones': float(active_pitches[-1] - active_pitches[0]),
    }


def refine(raw, candidates):
    validate_raw(raw)
    require(isinstance(candidates, list), 'candidates must be a list')
    kept, rejected = [], []
    for candidate in candidates:
        require(isinstance(candidate, dict), 'candidate must be an object')
        features = glide_features(raw, candidate)
        accepted = (
            features['activeFrameCount'] >= MIN_ACTIVE_FRAMES
            and features['uniqueContourBinCount'] >= MIN_UNIQUE_CONTOUR_BINS
            and features['maxFrameJumpSemitones'] is not None
            and features['maxFrameJumpSemitones'] <= MAX_FRAME_JUMP_SEMITONES + FLOAT_EPSILON
            and features['nondecreasingFraction'] is not None
            and features['nondecreasingFraction'] + FLOAT_EPSILON >= MIN_NONDECREASING_FRACTION
        )
        annotated = dict(candidate)
        annotated['glideContinuity'] = features
        if accepted:
            kept.append(annotated)
        else:
            rejected.append(annotated)
    return kept, rejected


def build_report(raw, source):
    require(isinstance(source, dict), 'source candidate document must be an object')
    require(source.get('customerDeliveryEligible') is False, 'source cannot authorize delivery')
    require(source.get('policy', {}).get('referenceLabelsRead') is False, 'source must be reference-blind')
    kept, rejected = refine(raw, source.get('candidates'))
    return {
        'kind': 'basic-pitch-glide-continuity-bend-candidates',
        'version': 1,
        'candidateCount': len(kept),
        'candidates': kept,
        'rejectedCandidateCount': len(rejected),
        'rejectedCandidates': rejected,
        'policy': {
            'referenceLabelsRead': False,
            'glideWindowSeconds': list(GLIDE_WINDOW_SECONDS),
            'minActiveContourSalience': MIN_ACTIVE_CONTOUR_SALIENCE,
            'minActiveFrames': MIN_ACTIVE_FRAMES,
            'minUniqueContourBins': MIN_UNIQUE_CONTOUR_BINS,
            'maxFrameJumpSemitones': MAX_FRAME_JUMP_SEMITONES,
            'minNondecreasingFraction': MIN_NONDECREASING_FRACTION,
        },
        'customerDeliveryEligible': False,
    }
