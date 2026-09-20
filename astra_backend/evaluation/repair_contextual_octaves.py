"""Reference-blind contextual octave repair for guitar note-event predictions.

The transform only considers isolated onset groups. It may move one event down
exactly one octave when the lower candidate is strongly supported by both
immediate neighboring onset groups and reduces local voice-leading movement.
It never reads score/reference labels and never changes event timing/count.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

ONSET_GROUP_SECONDS = 0.035
CONTEXT_HORIZON_SECONDS = 0.75
OCTAVE_SEMITONES = 12
MIN_GUITAR_MIDI = 40
MAX_LOWER_NEIGHBOR_DISTANCE = 4
MAX_LOWER_CONTEXT_COST = 8
MIN_CONTEXT_IMPROVEMENT = 8


def require(ok, message):
    if not ok:
        raise ValueError(message)


def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def validate_events(events):
    require(isinstance(events, list), "events must be a list")
    ids = set()
    for row in events:
        require(isinstance(row, dict), "event must be an object")
        ident = row.get("id")
        require(isinstance(ident, str) and ident and ident not in ids, "event ids must be unique")
        ids.add(ident)
        start, end, midi = row.get("start"), row.get("end"), row.get("midi")
        require(finite(start) and finite(end) and 0 <= start < end, "invalid event time")
        require(isinstance(midi, int) and not isinstance(midi, bool) and 0 <= midi <= 127, "invalid midi")


def group_onsets(events):
    ordered = sorted(range(len(events)), key=lambda i: (events[i]["start"], events[i]["id"]))
    groups = []
    for index in ordered:
        if not groups or events[index]["start"] - events[groups[-1][0]]["start"] > ONSET_GROUP_SECONDS:
            groups.append([index])
        else:
            groups[-1].append(index)
    return groups


def nearest_pitch_distance(pitch, group, events):
    return min(abs(pitch - events[i]["midi"]) for i in group)


def repair_events(events):
    validate_events(events)
    repaired = [dict(row) for row in events]
    groups = group_onsets(events)
    changes = []
    for group_index in range(1, len(groups) - 1):
        group = groups[group_index]
        if len(group) != 1:
            continue
        event_index = group[0]
        event = events[event_index]
        original = event["midi"]
        lower = original - OCTAVE_SEMITONES
        if lower < MIN_GUITAR_MIDI:
            continue

        previous_group = groups[group_index - 1]
        next_group = groups[group_index + 1]
        event_time = event["start"]
        previous_time = max(events[i]["start"] for i in previous_group)
        next_time = min(events[i]["start"] for i in next_group)
        if event_time - previous_time > CONTEXT_HORIZON_SECONDS or next_time - event_time > CONTEXT_HORIZON_SECONDS:
            continue

        original_prev = nearest_pitch_distance(original, previous_group, events)
        original_next = nearest_pitch_distance(original, next_group, events)
        lower_prev = nearest_pitch_distance(lower, previous_group, events)
        lower_next = nearest_pitch_distance(lower, next_group, events)
        original_cost = original_prev + original_next
        lower_cost = lower_prev + lower_next

        if lower_prev > MAX_LOWER_NEIGHBOR_DISTANCE or lower_next > MAX_LOWER_NEIGHBOR_DISTANCE:
            continue
        if lower_cost > MAX_LOWER_CONTEXT_COST:
            continue
        if original_cost - lower_cost < MIN_CONTEXT_IMPROVEMENT:
            continue

        repaired[event_index]["midi"] = lower
        changes.append({
            "eventId": event["id"],
            "start": event["start"],
            "fromMidi": original,
            "toMidi": lower,
            "originalContextCost": original_cost,
            "lowerContextCost": lower_cost,
            "previousLowerDistance": lower_prev,
            "nextLowerDistance": lower_next,
        })

    return repaired, changes


def transform(document, *, input_sha256):
    require(isinstance(document, dict), "prediction document must be an object")
    require(document.get("customerDeliveryEligible") is False, "development input must not authorize delivery")
    events = document.get("events")
    repaired, changes = repair_events(events)
    output = dict(document)
    output["kind"] = "contextual-octave-repaired-development-prediction"
    output["version"] = 1
    output["sourcePredictionSha256"] = input_sha256
    output["events"] = repaired
    output["octaveRepair"] = {
        "policy": "singleton-one-octave-down-only-when-both-neighbor-groups-support-local-continuity",
        "referenceLabelsRead": False,
        "eventCountChanged": False,
        "timingChanged": False,
        "changeCount": len(changes),
        "changes": changes,
        "constants": {
            "onsetGroupSeconds": ONSET_GROUP_SECONDS,
            "contextHorizonSeconds": CONTEXT_HORIZON_SECONDS,
            "octaveSemitones": OCTAVE_SEMITONES,
            "minGuitarMidi": MIN_GUITAR_MIDI,
            "maxLowerNeighborDistance": MAX_LOWER_NEIGHBOR_DISTANCE,
            "maxLowerContextCost": MAX_LOWER_CONTEXT_COST,
            "minContextImprovement": MIN_CONTEXT_IMPROVEMENT,
        },
    }
    output["customerDeliveryEligible"] = False
    return output


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prediction", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    out = Path(a.output)
    require(not out.exists(), "refusing to overwrite output")
    raw = Path(a.prediction).read_bytes()
    doc = json.loads(raw)
    result = transform(doc, input_sha256=sha256_bytes(raw))
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"changeCount": result["octaveRepair"]["changeCount"], "eventCount": len(result["events"])}, sort_keys=True))


if __name__ == "__main__":
    main()
