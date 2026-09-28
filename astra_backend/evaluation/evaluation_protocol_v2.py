#!/usr/bin/env python3
"""Prospective pitch-event evaluation protocol.

This module is deliberately separate from the frozen v1 scorer. It provides
boundary-aware crop events, strict validation, and deterministic
maximum-cardinality/minimum-error matching for future evaluation only.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Sequence

ONSET_TOLERANCE = 0.05
OFFSET_TOLERANCE = 0.05


@dataclass(frozen=True)
class EvalPitchEvent:
    id: str
    pitch: int
    start: float
    end: float
    source_start: float
    source_end: float
    carry_in: bool
    carry_out: bool
    onset_eligible: bool
    offset_eligible: bool


def _finite(value, name):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{name} must be finite")
    return x


def _pitch(value):
    x = _finite(value, "pitch")
    if int(x) != x:
        raise ValueError("pitch must be an integer MIDI note")
    p = int(x)
    if not 0 <= p <= 127:
        raise ValueError("pitch must be in MIDI range")
    return p


def crop_source_events(rows: Iterable[Sequence], crop_start_seconds, crop_end_seconds, *, id_prefix="event"):
    """Clip source-timed pitch events while retaining boundary provenance.

    Input rows are (start, end, pitch) or (id, start, end, pitch). Events that
    intersect the crop are returned. Carry-in events are onset-ineligible;
    carry-out events are offset-ineligible. A carry-out whose attack begins in
    the crop remains onset-eligible. Malformed/non-finite events are rejected.
    """
    crop_start = _finite(crop_start_seconds, "crop start")
    crop_end = _finite(crop_end_seconds, "crop end")
    if crop_end <= crop_start:
        raise ValueError("invalid crop interval")
    out = []
    for i, row in enumerate(rows):
        if len(row) == 3:
            event_id = f"{id_prefix}:{i}"
            start, end, pitch = row
        elif len(row) >= 4:
            event_id = str(row[0])
            start, end, pitch = row[1], row[2], row[3]
        else:
            raise ValueError("event row must contain start/end/pitch")
        start = _finite(start, "event start")
        end = _finite(end, "event end")
        pitch = _pitch(pitch)
        if end <= start:
            raise ValueError("event end must be greater than start")
        if start >= crop_end or end <= crop_start:
            continue
        carry_in = start < crop_start
        carry_out = end > crop_end
        local_start = max(start, crop_start) - crop_start
        local_end = min(end, crop_end) - crop_start
        if local_end <= local_start:
            continue
        out.append(EvalPitchEvent(
            event_id, pitch, local_start, local_end,
            start, end, carry_in, carry_out,
            not carry_in, not carry_out,
        ))
    return sorted(out, key=lambda e: (e.pitch, e.start, e.end, e.id))


def basic_pitch_to_crop_events_v2(note_events, crop_start_seconds, crop_end_seconds):
    rows = []
    for i, row in enumerate(note_events):
        if len(row) < 3:
            raise ValueError("invalid Basic Pitch note tuple")
        rows.append((f"bp:{i}", row[0], row[1], row[2]))
    return crop_source_events(rows, crop_start_seconds, crop_end_seconds, id_prefix="bp")


def _collapse_onset_ambiguity(events):
    """Collapse one observable same-pitch onset regardless of later duration."""
    seen = {}
    for e in sorted(events, key=lambda x: (x.pitch, x.start, x.end, x.id)):
        key = (e.pitch, round(e.start, 9))
        seen.setdefault(key, e)
    return list(seen.values())


def _collapse_offset_ambiguity(events):
    """Collapse only exact same-pitch/onset/offset duplicates."""
    seen = {}
    for e in sorted(events, key=lambda x: (x.pitch, x.start, x.end, x.id)):
        key = (e.pitch, round(e.start, 9), round(e.end, 9))
        seen.setdefault(key, e)
    return list(seen.values())


def _candidate_error(p, r, require_offset):
    if p.pitch != r.pitch:
        return None
    onset = abs(p.start - r.start)
    if onset > ONSET_TOLERANCE:
        return None
    offset = abs(p.end - r.end)
    if require_offset and offset > OFFSET_TOLERANCE:
        return None
    return onset + (offset if require_offset else 0.0)


class _Edge:
    __slots__ = ("to", "rev", "cap", "cost", "payload")

    def __init__(self, to, rev, cap, cost, payload=None):
        self.to = to
        self.rev = rev
        self.cap = cap
        self.cost = cost
        self.payload = payload


def _add_edge(graph, u, v, cap, cost, payload=None):
    graph[u].append(_Edge(v, len(graph[v]), cap, cost, payload))
    graph[v].append(_Edge(u, len(graph[u]) - 1, 0, -cost, None))


def _maximum_cardinality_min_error(preds, refs, require_offset):
    """Min-cost max-flow: maximize matches, then minimize total timing error.

    Costs use integer nanoseconds plus a deterministic low-order tie rank.
    Bellman-Ford is used because residual reverse edges can have negative cost.
    """
    n, m = len(preds), len(refs)
    src = 0
    p0 = 1
    r0 = p0 + n
    sink = r0 + m
    graph = [[] for _ in range(sink + 1)]
    for i in range(n):
        _add_edge(graph, src, p0 + i, 1, 0)
    for j in range(m):
        _add_edge(graph, r0 + j, sink, 1, 0)

    max_matches = min(n, m)
    tie_base = (n * m + 1) * (max_matches + 1) if n and m else 1
    rank = 0
    for i, p in enumerate(preds):
        for j, r in enumerate(refs):
            err = _candidate_error(p, r, require_offset)
            if err is None:
                continue
            primary = int(round(err * 1_000_000_000))
            cost = primary * tie_base + rank
            _add_edge(graph, p0 + i, r0 + j, 1, cost, (i, j))
            rank += 1

    while True:
        inf = 10**40
        dist = [inf] * len(graph)
        prev = [None] * len(graph)
        dist[src] = 0
        for _ in range(len(graph) - 1):
            changed = False
            for u in range(len(graph)):
                if dist[u] == inf:
                    continue
                for ei, e in enumerate(graph[u]):
                    if e.cap <= 0:
                        continue
                    nd = dist[u] + e.cost
                    if nd < dist[e.to]:
                        dist[e.to] = nd
                        prev[e.to] = (u, ei)
                        changed = True
            if not changed:
                break
        if prev[sink] is None:
            break
        v = sink
        while v != src:
            u, ei = prev[v]
            e = graph[u][ei]
            e.cap -= 1
            graph[v][e.rev].cap += 1
            v = u

    pairs = []
    for i in range(n):
        for e in graph[p0 + i]:
            if r0 <= e.to < r0 + m and e.payload is not None and e.cap == 0:
                pairs.append(e.payload)
    return sorted(pairs)


def _score(preds, refs, require_offset):
    pairs = _maximum_cardinality_min_error(preds, refs, require_offset)
    tp = len(pairs)
    fp = len(preds) - tp
    fn = len(refs) - tp
    precision = tp / len(preds) if preds else (1.0 if not refs else 0.0)
    recall = tp / len(refs) if refs else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "referenceCount": len(refs),
        "predictionCount": len(preds),
        "truePositive": tp,
        "falsePositive": fp,
        "falseNegative": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matchedPairs": pairs,
    }


def score_pitch_events_v2(preds, refs):
    pred_on = _collapse_onset_ambiguity([e for e in preds if e.onset_eligible])
    ref_on = _collapse_onset_ambiguity([e for e in refs if e.onset_eligible])
    pred_off = _collapse_offset_ambiguity(
        [e for e in preds if e.onset_eligible and e.offset_eligible]
    )
    ref_off = _collapse_offset_ambiguity(
        [e for e in refs if e.onset_eligible and e.offset_eligible]
    )
    return {
        "pitchOnset": _score(pred_on, ref_on, False),
        "pitchOnsetOffset": _score(pred_off, ref_off, True),
        "eligibility": {
            "predictionOnsetExcludedCarryIn": sum(1 for e in preds if not e.onset_eligible),
            "predictionOffsetExcludedCarryOut": sum(
                1 for e in preds if e.onset_eligible and not e.offset_eligible
            ),
            "referenceOnsetExcludedCarryIn": sum(1 for e in refs if not e.onset_eligible),
            "referenceOffsetExcludedCarryOut": sum(
                1 for e in refs if e.onset_eligible and not e.offset_eligible
            ),
        },
        "ambiguityPolicy": {
            "onset": "collapse same pitch + simultaneous onset regardless of duration",
            "onsetOffset": "collapse only exact same pitch + onset + offset duplicates",
        },
    }


def validate_manifest_binding(meta, manifest_entry):
    """Require the next runner to bind all frozen crop/source/target identities."""
    prepared = meta.get("prepared", {})
    crop = prepared.get("crop", {})
    checks = {
        "captureKey": meta.get("captureKey"),
        "captureView": meta.get("captureView"),
        "performer": meta.get("performer"),
        "audioSourceSha256": meta.get("audioSourceSha256"),
        "midiSourceSha256": meta.get("midiSourceSha256"),
        "featureSha256": meta.get("featureSha256"),
        "sourceEventSha256": prepared.get("sourceEventSha256"),
        "targetSha256": prepared.get("targetSha256"),
        "cropStartFrame": crop.get("startFrame"),
        "cropFrames": crop.get("frames"),
        "cropHopSeconds": crop.get("hopSeconds"),
        "unresolvedLabelCount": prepared.get("unresolvedLabelCount"),
    }
    for key, expected in manifest_entry.items():
        if key not in checks:
            raise ValueError(f"unsupported manifest identity field: {key}")
        actual = checks[key]
        if actual != expected:
            raise RuntimeError(
                f"manifest identity mismatch for {key}: {actual!r} != {expected!r}"
            )
    if checks["unresolvedLabelCount"] != 0:
        raise RuntimeError("unresolved selected labels")
    return True
