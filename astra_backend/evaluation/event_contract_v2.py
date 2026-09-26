"""Offline event-preserving primitives. No corpus, model or legacy-score imports.

Times are seconds; strings 0..5 run low E to high E. Each event is ONE attack.
A tie is represented by extending that event's end, never a second event.
This is a new diagnostic protocol, not a replacement for frozen V1-V5 scoring.
"""
from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass
import math

SCHEMA = "astra-explicit-note-events-v2"
MASK = -100
STRING_ORDER = ("E", "A", "D", "G", "B", "e")
OPEN_MIDI = (40, 45, 50, 55, 59, 64)


@dataclass(frozen=True)
class Event:
    id: str
    string: int
    fret: int
    start: float
    end: float


def validate_events(events):
    events = list(events)
    ids = set()
    for e in events:
        if not isinstance(e, Event) or not isinstance(e.id, str) or not e.id or e.id in ids:
            raise ValueError("events require unique nonempty IDs")
        ids.add(e.id)
        if type(e.string) is not int or not 0 <= e.string < 6:
            raise ValueError("string must be an integer in 0..5")
        if type(e.fret) is not int or not 0 <= e.fret <= 19:
            raise ValueError("fret must be an integer in 0..19")
        if any(isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t)
               for t in (e.start, e.end)) or not 0 <= e.start < e.end:
            raise ValueError("event times must be finite, nonnegative, ordered")
    ordered = sorted(events, key=lambda e: (e.string, e.start, e.end, e.id))
    for a, b in zip(ordered, ordered[1:]):
        if a.string == b.string and b.start < a.end:
            raise ValueError("overlapping same-string events need explicit source resolution")
    return ordered


def _number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be finite")
    if value < 0 or (positive and value == 0):
        raise ValueError(name + " out of range")


def from_string_notes(notes, *, capture_id, lag_ms):
    """Adapt existing midi_string_events output without reading files/importing ML.

    Positive lag follows legacy semantics: add lag to MIDI times. No alignment
    search, clipping, inferred ties, overlap repair, or out-of-range masking.
    Inputs requiring any such decision are rejected for explicit adapter review.
    """
    if not isinstance(capture_id, str) or not capture_id:
        raise ValueError("capture_id required")
    if not isinstance(notes, dict) or set(notes) - set(STRING_ORDER):
        raise ValueError("unknown string track")
    if isinstance(lag_ms, bool) or not isinstance(lag_ms, (int, float)) or not math.isfinite(lag_ms):
        raise ValueError("finite lag required")
    result = []
    for string, name in enumerate(STRING_ORDER):
        for index, (start, end, pitch) in enumerate(notes.get(name, [])):
            if type(pitch) is not int:
                raise ValueError("integer MIDI pitch required")
            _number(start, "source start")
            _number(end, "source end")
            result.append(Event(f"{capture_id}:{name}:{index}", string, pitch - OPEN_MIDI[string],
                                start + lag_ms / 1000, end + lag_ms / 1000))
    return validate_events(result)


def frame_targets(events, *, frames, hop_seconds):
    """Produce occupancy AND onset/event ID arrays; never infer starts from frets.

    Reject sub-frame attacks/collisions rather than silently dropping them. Any
    source MASK/unresolved interval must be resolved in a versioned adapter first.
    """
    if type(frames) is not int or frames <= 0:
        raise ValueError("frames must be positive")
    _number(hop_seconds, "hop_seconds", positive=True)
    events = validate_events(events)
    times = [i * hop_seconds for i in range(frames)]
    state = [[-1] * frames for _ in range(6)]
    onset = [[False] * frames for _ in range(6)]
    identity = [[None] * frames for _ in range(6)]
    for e in events:
        if e.end > frames * hop_seconds:
            raise ValueError("event extends beyond frame coverage")
        lo, hi = bisect_left(times, e.start), bisect_left(times, e.end)
        if lo >= hi:
            raise ValueError("attack cannot be represented at this frame resolution")
        for i in range(lo, hi):
            if identity[e.string][i] is not None:
                raise ValueError("events collide on the frame grid")
            state[e.string][i] = e.fret
            identity[e.string][i] = e.id
        onset[e.string][lo] = True
    return {"schema": SCHEMA, "state": state, "onset": onset, "eventId": identity}


def _match(pred, ref, tolerance):
    # Ordered maximum-cardinality matching, then minimum total onset error.
    # Stored pairs make this intentionally a small-clip diagnostic implementation.
    prev = [(0, 0.0, ()) for _ in range(len(ref) + 1)]
    for i, p in enumerate(pred):
        row = [(0, 0.0, ())]
        for j, r in enumerate(ref):
            choices = [prev[j + 1], row[j]]
            error = abs(p.start - r.start)
            if error <= tolerance + 1e-12:
                n, cost, pairs = prev[j]
                choices.append((n + 1, cost + error, pairs + ((p, r),)))
            row.append(min(choices, key=lambda x: (-x[0], x[1], tuple((a.id, b.id) for a, b in x[2]))))
        prev = row
    return prev[-1][2]


def score_events(predictions, references, *, onset_tolerance=0.05, offset_tolerance=0.05,
                 excluded_intervals=()):
    """Score explicit events. Exclusions are (string, start, end) half-open spans.

    Events intersecting an uncertain span are excluded WHOLE on both sides;
    counts remain visible. Never clip a note and invent an onset at a mask edge.
    Caller must preregister exclusion provenance; this function cannot prove it.
    """
    _number(onset_tolerance, "onset_tolerance")
    _number(offset_tolerance, "offset_tolerance")
    pred, ref = validate_events(predictions), validate_events(references)
    exclusions = list(excluded_intervals)
    for string, lo, hi in exclusions:
        if type(string) is not int or not 0 <= string < 6:
            raise ValueError("invalid exclusion string")
        _number(lo, "exclusion start")
        _number(hi, "exclusion end")
        if hi <= lo:
            raise ValueError("invalid exclusion interval")
    def admitted(e):
        return not any(e.string == s and e.start < hi and e.end > lo for s, lo, hi in exclusions)
    pp, rr = [e for e in pred if admitted(e)], [e for e in ref if admitted(e)]
    groups = defaultdict(lambda: [[], []])
    for side, events in enumerate((pp, rr)):
        for e in events:
            groups[(e.string, e.fret)][side].append(e)
    matches = []
    for ps, rs in groups.values():
        matches.extend(_match(ps, rs, onset_tolerance))
    tp, fp, fn = len(matches), len(pp) - len(matches), len(rr) - len(matches)
    precision = tp / len(pp) if pp else (1.0 if not rr else 0.0)
    recall = tp / len(rr) if rr else (1.0 if not pp else 0.0)
    offset_errors = [abs(p.end - r.end) for p, r in matches]
    return {
        "schema": SCHEMA, "referenceCount": len(rr), "predictionCount": len(pp),
        "excludedReferenceCount": len(ref) - len(rr), "excludedPredictionCount": len(pred) - len(pp),
        "truePositive": tp, "falsePositive": fp, "falseNegative": fn,
        "precision": precision, "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "matchedOffsetWithinTolerance": sum(e <= offset_tolerance + 1e-12 for e in offset_errors),
        "matchedOffsetMAESeconds": sum(offset_errors) / tp if tp else None,
        "matchedOnsetMAESeconds": sum(abs(p.start - r.start) for p, r in matches) / tp if tp else None,
        "emptyReference": not rr, "abstentionRate": None,
        "customerDeliveryEligible": False,
    }


def delivery_counts(statuses):
    """Explicit statuses, independent of whether predicted events are empty."""
    statuses = list(statuses)
    if any(s not in {"complete", "partial", "abstained", "failed"} for s in statuses):
        raise ValueError("unknown delivery status")
    counts = {s: statuses.count(s) for s in ("complete", "partial", "abstained", "failed")}
    return {"requests": len(statuses), **counts,
            "abstentionRate": counts["abstained"] / len(statuses) if statuses else None}
