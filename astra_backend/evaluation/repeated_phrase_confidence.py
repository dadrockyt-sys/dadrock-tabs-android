"""Reference-blind recurring-measure support for structure-aligned note events."""
from __future__ import annotations

import math
from collections import defaultdict

MIN_DISTINCT_MEASURE_SUPPORT = 3
MIN_STREAM_REPEAT_COVERAGE = 0.60
FLOAT_EPSILON = 1e-9


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_alignment(alignment):
    require(isinstance(alignment, dict), 'alignment must be an object')
    require(alignment.get('reviewStatus') == 'complete', 'alignment must be complete')
    require(alignment.get('independentOfPredictions') is True, 'alignment must be prediction-independent')
    segments = alignment.get('segments')
    require(isinstance(segments, list) and len(segments) >= MIN_DISTINCT_MEASURE_SUPPORT,
            'need at least three aligned measures')
    return segments


def measure_position(beat, segments):
    require(finite(beat), 'nearest beat must be finite')
    for index, segment in enumerate(segments):
        bs, be = segment['beatStart'], segment['beatEnd']
        if bs - FLOAT_EPSILON <= beat < be - FLOAT_EPSILON:
            return index + 1, round(float(beat - bs), 9)
    raise ValueError('nearest beat falls outside alignment segments')


def partition_recurring_events(events, alignment,
                               *, min_measure_support=MIN_DISTINCT_MEASURE_SUPPORT,
                               min_stream_coverage=MIN_STREAM_REPEAT_COVERAGE,
                               window_seconds=None):
    require(isinstance(events, list), 'events must be a list')
    require(isinstance(min_measure_support, int) and min_measure_support >= 3,
            'min_measure_support must be an integer >= 3')
    require(finite(min_stream_coverage) and 0 < min_stream_coverage <= 1,
            'min_stream_coverage must be in (0,1]')
    segments = validate_alignment(alignment)
    if window_seconds is None:
        start_window, end_window = segments[0]['timeStart'], segments[-1]['timeEnd']
    else:
        require(isinstance(window_seconds, list) and len(window_seconds) == 2
                and all(finite(v) for v in window_seconds)
                and 0 <= window_seconds[0] < window_seconds[1], 'invalid window_seconds')
        start_window, end_window = map(float, window_seconds)

    normalized = []
    ids = set()
    for index, row in enumerate(events):
        require(isinstance(row, dict), 'event must be an object')
        identity = row.get('id', str(index))
        require(isinstance(identity, str) and identity and identity not in ids, 'event IDs must be unique')
        ids.add(identity)
        midi, start = row.get('midi'), row.get('start')
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, 'invalid MIDI')
        require(finite(start) and start >= 0, 'invalid start')
        annotated = dict(row)
        if start_window <= start < end_window:
            grid = row.get('structureGrid')
            require(isinstance(grid, dict) and finite(grid.get('nearestBeat')),
                    'structureGrid.nearestBeat required for in-window event')
            measure, relative_beat = measure_position(grid['nearestBeat'], segments)
            annotated['repeatEvidence'] = {
                'measureIndex': measure,
                'relativeBeat': relative_beat,
            }
        normalized.append(annotated)

    in_window = [row for row in normalized if 'repeatEvidence' in row]
    support = defaultdict(set)
    for row in in_window:
        key = (row['midi'], row['repeatEvidence']['relativeBeat'])
        support[key].add(row['repeatEvidence']['measureIndex'])

    supported_count = 0
    for row in in_window:
        key = (row['midi'], row['repeatEvidence']['relativeBeat'])
        count = len(support[key])
        row['repeatEvidence']['distinctMeasureSupport'] = count
        row['repeatEvidence']['recurringCore'] = count >= min_measure_support
        supported_count += int(count >= min_measure_support)

    coverage = supported_count / len(in_window) if in_window else 0.0
    active = coverage + FLOAT_EPSILON >= min_stream_coverage
    recurring, uncertain = [], []
    for row in normalized:
        if 'repeatEvidence' not in row:
            uncertain.append(row)
        elif active and row['repeatEvidence']['recurringCore']:
            recurring.append(row)
        else:
            uncertain.append(row)

    return {
        'status': 'complete' if active else 'abstained',
        'recurringCoreEvents': recurring,
        'uncertainEvents': uncertain,
        'diagnostics': {
            'referenceLabelsRead': False,
            'minDistinctMeasureSupport': min_measure_support,
            'minStreamRepeatCoverage': min_stream_coverage,
            'inWindowEventCount': len(in_window),
            'recurringSupportedEventCount': supported_count,
            'recurringSupportCoverage': coverage,
            'distinctRecurringKeys': sum(1 for measures in support.values() if len(measures) >= min_measure_support),
            'eventTimingChanged': False,
            'eventMidiChanged': False,
            'eventsDeleted': False,
        },
    }
