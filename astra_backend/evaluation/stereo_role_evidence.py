"""Reference-blind stereo guitar role evidence from same-clock note events."""
from __future__ import annotations

import math
import statistics

ONSET_GROUP_SECONDS = 0.05
DEDUP_TOLERANCE_SECONDS = 0.05
MAX_ABS_CHANNEL_CORRELATION = 0.25
MIN_CHORD_RATE_GAP = 0.05
MIN_CHORD_RATE_RATIO = 2.0
MIN_MEDIAN_PITCH_GAP = 5.0
MONO_CHANNEL_DOMINANCE_RATIO = 1.20
OCTAVE_INTERVALS = {12, 24, 36}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_events(events, label):
    require(isinstance(events, list), f'{label} events must be a list')
    ids = set()
    out = []
    for index, row in enumerate(events):
        require(isinstance(row, dict), f'{label} event must be an object')
        identity = row.get('id', f'{label}-{index}')
        require(isinstance(identity, str) and identity and identity not in ids, f'{label} event IDs must be unique')
        ids.add(identity)
        midi, start = row.get('midi'), row.get('start')
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'Invalid MIDI')
        require(finite(start) and start >= 0, 'Invalid start')
        amp = row.get('amplitude', row.get('amp', 0.0))
        require(finite(amp) and amp >= 0, 'Invalid amplitude')
        out.append({**row, 'id': identity, 'midi': midi, 'start': float(start), 'amplitude': float(amp)})
    return sorted(out, key=lambda row: (row['start'], row['midi'], row['id']))


def onset_groups(events):
    groups = []
    for row in events:
        if not groups or row['start'] - groups[-1][0]['start'] > ONSET_GROUP_SECONDS:
            groups.append([row])
        else:
            groups[-1].append(row)
    return groups


def chord_like(group):
    midis = sorted(set(row['midi'] for row in group))
    if len(midis) < 2:
        return False
    return any((b - a) not in OCTAVE_INTERVALS for i, a in enumerate(midis) for b in midis[i + 1:])


def channel_features(events):
    rows = validate_events(events, 'channel')
    require(rows, 'channel must contain events')
    groups = onset_groups(rows)
    chord_count = sum(1 for group in groups if chord_like(group))
    return {
        'eventCount': len(rows),
        'onsetGroupCount': len(groups),
        'multiEventGroupCount': sum(1 for group in groups if len(group) >= 2),
        'chordLikeGroupCount': chord_count,
        'chordLikeRate': chord_count / len(groups),
        'medianMidi': float(statistics.median(row['midi'] for row in rows)),
    }


def classify_channels(left_events, right_events, *, channel_correlation):
    require(finite(channel_correlation) and -1 <= channel_correlation <= 1, 'Invalid channel correlation')
    left = channel_features(left_events)
    right = channel_features(right_events)
    result = {
        'status': 'abstained',
        'mapping': None,
        'channelCorrelation': float(channel_correlation),
        'features': {'left': left, 'right': right},
        'reasons': [],
    }
    if abs(channel_correlation) > MAX_ABS_CHANNEL_CORRELATION:
        result['reasons'].append('CHANNELS_TOO_CORRELATED')
        return result

    if left['chordLikeRate'] >= right['chordLikeRate']:
        rhythm_name, rhythm, lead_name, lead = 'left', left, 'right', right
    else:
        rhythm_name, rhythm, lead_name, lead = 'right', right, 'left', left

    gap = rhythm['chordLikeRate'] - lead['chordLikeRate']
    ratio = rhythm['chordLikeRate'] / max(lead['chordLikeRate'], 1e-9)
    pitch_gap = lead['medianMidi'] - rhythm['medianMidi']
    if gap < MIN_CHORD_RATE_GAP:
        result['reasons'].append('CHORDALITY_GAP_TOO_SMALL')
    if ratio < MIN_CHORD_RATE_RATIO:
        result['reasons'].append('CHORDALITY_RATIO_TOO_SMALL')
    if pitch_gap < MIN_MEDIAN_PITCH_GAP:
        result['reasons'].append('RELATIVE_REGISTER_GAP_TOO_SMALL')
    if result['reasons']:
        return result

    result['status'] = 'complete'
    result['mapping'] = {'rhythm': rhythm_name, 'lead': lead_name}
    result['diagnostics'] = {
        'chordLikeRateGap': gap,
        'chordLikeRateRatio': ratio,
        'relativeMedianPitchGapSemitones': pitch_gap,
    }
    return result


def deduplicate_cross_channel(left_events, right_events, *, tolerance=DEDUP_TOLERANCE_SECONDS):
    left = validate_events(left_events, 'left')
    right = validate_events(right_events, 'right')
    require(finite(tolerance) and tolerance >= 0, 'Invalid deduplication tolerance')
    candidates = []
    for li, lrow in enumerate(left):
        for ri, rrow in enumerate(right):
            if lrow['midi'] == rrow['midi'] and abs(lrow['start'] - rrow['start']) <= tolerance:
                candidates.append((abs(lrow['start'] - rrow['start']), li, ri))
    used_left, used_right, drop_left, drop_right = set(), set(), set(), set()
    for _, li, ri in sorted(candidates):
        if li in used_left or ri in used_right:
            continue
        used_left.add(li)
        used_right.add(ri)
        la, ra = left[li]['amplitude'], right[ri]['amplitude']
        if la > ra:
            drop_right.add(ri)
        elif ra > la:
            drop_left.add(li)
    return {
        'left': [row for i, row in enumerate(left) if i not in drop_left],
        'right': [row for i, row in enumerate(right) if i not in drop_right],
        'pairedDuplicateCount': len(used_left),
        'leftDroppedCount': len(drop_left),
        'rightDroppedCount': len(drop_right),
    }


def _nearest_same_midi(events, row, tolerance):
    matches = [candidate for candidate in events
               if candidate['midi'] == row['midi'] and abs(candidate['start'] - row['start']) <= tolerance]
    if not matches:
        return None
    return min(matches, key=lambda candidate: (abs(candidate['start'] - row['start']), -candidate['amplitude'], candidate['id']))


def label_mono_events(mono_events, left_events, right_events, mapping, *, tolerance=DEDUP_TOLERANCE_SECONDS):
    mono = validate_events(mono_events, 'mono')
    left = validate_events(left_events, 'left')
    right = validate_events(right_events, 'right')
    require(mapping in ({'rhythm': 'left', 'lead': 'right'}, {'rhythm': 'right', 'lead': 'left'}), 'Invalid role mapping')
    channel_to_role = {channel: role for role, channel in mapping.items()}
    output = {'rhythm': [], 'lead': [], 'ambiguous': [], 'unassigned': []}
    for row in mono:
        lmatch = _nearest_same_midi(left, row, tolerance)
        rmatch = _nearest_same_midi(right, row, tolerance)
        annotated = {**row}
        if lmatch is None and rmatch is None:
            output['unassigned'].append(annotated)
            continue
        if lmatch is None or rmatch is None:
            channel = 'left' if lmatch is not None else 'right'
            annotated['roleEvidenceChannel'] = channel
            output[channel_to_role[channel]].append(annotated)
            continue
        stronger = max(lmatch['amplitude'], rmatch['amplitude'])
        weaker = min(lmatch['amplitude'], rmatch['amplitude'])
        if weaker > 0 and stronger < weaker * MONO_CHANNEL_DOMINANCE_RATIO:
            output['ambiguous'].append(annotated)
            continue
        if weaker == 0 and stronger == 0:
            output['ambiguous'].append(annotated)
            continue
        channel = 'left' if lmatch['amplitude'] > rmatch['amplitude'] else 'right'
        annotated['roleEvidenceChannel'] = channel
        annotated['channelAmplitudeRatio'] = stronger / max(weaker, 1e-12)
        output[channel_to_role[channel]].append(annotated)
    return output
