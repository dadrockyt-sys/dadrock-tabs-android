"""Reference-blind structure-grid consistency filter for note-event predictions."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

FLOAT_EPSILON_SECONDS = 1e-9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_alignment(alignment):
    require(isinstance(alignment, dict), "alignment must be an object")
    require(alignment.get("reviewStatus") == "complete", "alignment must be complete")
    require(alignment.get("independentOfPredictions") is True, "alignment must be prediction-independent")
    segments = alignment.get("segments")
    require(isinstance(segments, list) and segments, "alignment segments missing")
    previous_beat = None
    previous_time = None
    normalized = []
    for index, segment in enumerate(segments):
        require(isinstance(segment, dict), "alignment segment must be an object")
        bs, be = segment.get("beatStart"), segment.get("beatEnd")
        ts, te = segment.get("timeStart"), segment.get("timeEnd")
        require(all(finite(v) for v in (bs, be, ts, te)), "alignment segment values must be finite")
        require(0 <= bs < be and 0 <= ts < te, "invalid alignment segment bounds")
        if index:
            require(abs(bs - previous_beat) <= FLOAT_EPSILON_SECONDS, "alignment beats must be contiguous")
            require(abs(ts - previous_time) <= FLOAT_EPSILON_SECONDS, "alignment times must be contiguous")
        previous_beat, previous_time = be, te
        normalized.append((float(bs), float(be), float(ts), float(te)))
    return normalized


def build_grid(alignment, *, subdivision_beats):
    require(finite(subdivision_beats) and subdivision_beats > 0, "subdivision_beats must be positive")
    segments = validate_alignment(alignment)
    slots = []
    for bs, be, ts, te in segments:
        count_float = (be - bs) / subdivision_beats
        count = round(count_float)
        require(abs(count_float - count) <= FLOAT_EPSILON_SECONDS and count >= 1,
                "segment beat span must divide evenly by subdivision_beats")
        for index in range(count):
            beat = bs + index * subdivision_beats
            alpha = (beat - bs) / (be - bs)
            slots.append({"beat": beat, "time": ts + alpha * (te - ts)})
    return slots


def validate_events(events):
    require(isinstance(events, list), "events must be a list")
    ids = set()
    out = []
    for index, row in enumerate(events):
        require(isinstance(row, dict), "event must be an object")
        identity = row.get("id", str(index))
        require(isinstance(identity, str) and identity and identity not in ids, "event IDs must be unique")
        ids.add(identity)
        start, midi = row.get("start"), row.get("midi")
        require(finite(start) and start >= 0, "invalid event start")
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, "invalid event MIDI")
        out.append(dict(row, id=identity, start=float(start), midi=midi))
    return out


def nearest_slot(start, grid):
    require(grid, "structure grid is empty")
    slot = min(grid, key=lambda item: (abs(start - item["time"]), item["time"]))
    return slot, abs(start - slot["time"])


def filter_events(events, alignment, *, subdivision_beats=0.25, tolerance_seconds=0.05,
                  window_seconds=None):
    require(finite(tolerance_seconds) and tolerance_seconds >= 0, "invalid tolerance_seconds")
    rows = validate_events(events)
    grid = build_grid(alignment, subdivision_beats=subdivision_beats)
    if window_seconds is None:
        start_window, end_window = grid[0]["time"], alignment["segments"][-1]["timeEnd"]
    else:
        require(isinstance(window_seconds, list) and len(window_seconds) == 2
                and all(finite(v) for v in window_seconds)
                and 0 <= window_seconds[0] < window_seconds[1], "invalid window_seconds")
        start_window, end_window = map(float, window_seconds)

    kept, removed = [], []
    for row in rows:
        if not (start_window <= row["start"] < end_window):
            kept.append(row)
            continue
        slot, distance = nearest_slot(row["start"], grid)
        annotated = dict(row)
        annotated["structureGrid"] = {
            "nearestBeat": slot["beat"],
            "nearestTime": slot["time"],
            "absoluteDisplacementSeconds": distance,
        }
        # Scorer tolerance is inclusive. Epsilon prevents binary floating-point
        # representation from rejecting an event mathematically exactly on the boundary.
        if distance <= tolerance_seconds + FLOAT_EPSILON_SECONDS:
            kept.append(annotated)
        else:
            removed.append(annotated)
    return kept, removed, grid


def transform(document, alignment, *, subdivision_beats=0.25, tolerance_seconds=0.05,
              window_seconds=None, source_sha256=None, alignment_sha256=None):
    require(isinstance(document, dict), "prediction document must be an object")
    require(document.get("customerDeliveryEligible") is False, "development prediction cannot authorize delivery")
    kept, removed, grid = filter_events(
        document.get("events"), alignment,
        subdivision_beats=subdivision_beats,
        tolerance_seconds=tolerance_seconds,
        window_seconds=window_seconds,
    )
    out = dict(document)
    out["kind"] = "structure-grid-filtered-development-prediction"
    out["version"] = 1
    out["events"] = kept
    out["structureGridFilter"] = {
        "referenceLabelsRead": False,
        "sourcePredictionSha256": source_sha256,
        "alignmentSha256": alignment_sha256,
        "subdivisionBeats": subdivision_beats,
        "toleranceSeconds": tolerance_seconds,
        "floatingPointEpsilonSeconds": FLOAT_EPSILON_SECONDS,
        "gridSlotCount": len(grid),
        "inputEventCount": len(document.get("events", [])),
        "keptEventCount": len(kept),
        "removedEventCount": len(removed),
        "removedEvents": removed,
        "eventCountCanOnlyDecrease": True,
        "eventTimingChanged": False,
        "eventMidiChanged": False,
    }
    out["customerDeliveryEligible"] = False
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prediction", required=True)
    parser.add_argument("--alignment", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--subdivision-beats", type=float, default=0.25)
    parser.add_argument("--tolerance-seconds", type=float, default=0.05)
    args = parser.parse_args()
    output = Path(args.output)
    require(not output.exists(), "refusing to overwrite output")
    pred_raw = Path(args.prediction).read_bytes()
    align_raw = Path(args.alignment).read_bytes()
    prediction = json.loads(pred_raw)
    alignment = json.loads(align_raw)
    result = transform(
        prediction, alignment,
        subdivision_beats=args.subdivision_beats,
        tolerance_seconds=args.tolerance_seconds,
        window_seconds=alignment.get("windowSeconds"),
        source_sha256=sha256_bytes(pred_raw),
        alignment_sha256=sha256_bytes(align_raw),
    )
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "inputEventCount": result["structureGridFilter"]["inputEventCount"],
        "keptEventCount": result["structureGridFilter"]["keptEventCount"],
        "removedEventCount": result["structureGridFilter"]["removedEventCount"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
