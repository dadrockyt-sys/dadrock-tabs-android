"""Prepared-event crop/mask adapter for Astra's training-only tiny-fit pilot.

Pure standard library. Inputs are the tuple dictionary emitted by the frozen
``midi_string_events`` parser. This module does not open corpus media, import ML,
repair source events, or alter the frozen V1-V5 label/scoring protocols.
"""
from bisect import bisect_left
from dataclasses import dataclass
import hashlib
import json
import math

MASK = -100
SCHEMA = "astra-prepared-event-crop-v1"
STRING_ORDER = ("E", "A", "D", "G", "B", "e")
OPEN_MIDI = (40, 45, 50, 55, 59, 64)
NUM_STRINGS = 6
MAX_FRET = 19


@dataclass(frozen=True)
class SourceEvent:
    id: str
    string: int
    fret: int
    source_start: float
    source_end: float
    aligned_start: float
    aligned_end: float


def _finite_number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(name + " must be a finite number")
    return float(value)


def _sha256_json(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _normalize_notes(notes):
    if not isinstance(notes, dict) or set(notes) - set(STRING_ORDER):
        raise ValueError("notes contain an unknown string track")
    canonical = {}
    for name in STRING_ORDER:
        rows = []
        for row in notes.get(name, []):
            if not isinstance(row, (list, tuple)) or len(row) != 3:
                raise ValueError("each source note must be (start, end, midi_pitch)")
            start = _finite_number(row[0], "source start")
            end = _finite_number(row[1], "source end")
            pitch = row[2]
            if type(pitch) is not int:
                raise ValueError("source MIDI pitch must be an integer")
            rows.append((start, end, pitch))
        canonical[name] = rows
    return canonical


def source_events_from_notes(notes, *, capture_id, lag_ms):
    """Return every source attack plus explicit unresolved-source diagnostics.

    Unlike ``event_contract_v2.from_string_notes``, this preparation layer does
    not discard unsupported/overlapping/sub-frame candidates. It records them so
    the caller can stop the real pilot before optimizer work.
    """
    if not isinstance(capture_id, str) or not capture_id:
        raise ValueError("capture_id is required")
    lag = _finite_number(lag_ms, "lag_ms") / 1000.0
    canonical = _normalize_notes(notes)
    events = []
    issues = []
    for string, name in enumerate(STRING_ORDER):
        for index, (start, end, pitch) in enumerate(canonical[name]):
            event_id = f"{capture_id}:{name}:{index}"
            fret = pitch - OPEN_MIDI[string]
            aligned_start = start + lag
            aligned_end = end + lag
            event = SourceEvent(
                event_id, string, fret, start, end, aligned_start, aligned_end
            )
            events.append(event)
            if end <= start:
                issues.append({"code": "nonpositive_source_duration", "eventId": event_id})
            if aligned_start < 0 or aligned_end <= 0:
                issues.append({"code": "negative_aligned_time", "eventId": event_id})
            if not 0 <= fret <= MAX_FRET:
                issues.append({
                    "code": "unsupported_fret",
                    "eventId": event_id,
                    "fret": fret,
                })

    ordered = sorted(events, key=lambda e: (e.string, e.aligned_start, e.aligned_end, e.id))
    for string in range(NUM_STRINGS):
        seq = [e for e in ordered if e.string == string and e.aligned_end > e.aligned_start]
        active = []
        for event in seq:
            active = [a for a in active if a.aligned_end > event.aligned_start]
            for other in active:
                issues.append({
                    "code": "same_string_overlap",
                    "eventId": other.id,
                    "otherEventId": event.id,
                })
            active.append(event)
    return ordered, issues, canonical


def _mask_intersects(event, interval):
    string, start, end = interval
    return event.string == string and event.aligned_start < end and event.aligned_end > start


def _event_intersects_crop(event, crop_start, crop_end):
    return event.aligned_start < crop_end and event.aligned_end > crop_start


def _event_frame_span(event, crop_start, frames, hop_seconds):
    times = [i * hop_seconds for i in range(frames)]
    rel_start = max(0.0, event.aligned_start - crop_start)
    rel_end = min(frames * hop_seconds, event.aligned_end - crop_start)
    return bisect_left(times, rel_start), bisect_left(times, rel_end)


def _canonical_issue(issue):
    return {k: issue[k] for k in sorted(issue)}


def prepare_event_crop(
    notes,
    *,
    capture_id,
    lag_ms,
    allowlist_lag_ms,
    crop_start_frame,
    frames,
    hop_seconds,
    excluded_intervals=(),
):
    """Prepare one event-preserving crop with explicit boundary/mask semantics.

    - Event IDs are source scoped and never regenerated at crop/mask edges.
    - Carry-in occupancy is retained, but no false onset is created at frame 0.
    - Carry-out onset supervision is retained, but boundary events are excluded
      from offset/event scoring.
    - Any event intersecting a registered exclusion is masked for its whole
      in-crop occupancy and excluded whole from event scoring.
    - Unsupported frets, overlaps, negative aligned time and sub-frame attacks
      are reported as unresolved. ``launchReady`` is false when any occur.
    """
    if type(crop_start_frame) is not int or crop_start_frame < 0:
        raise ValueError("crop_start_frame must be a nonnegative integer")
    if type(frames) is not int or frames <= 0:
        raise ValueError("frames must be a positive integer")
    hop = _finite_number(hop_seconds, "hop_seconds")
    if hop <= 0:
        raise ValueError("hop_seconds must be positive")
    requested_lag = _finite_number(lag_ms, "lag_ms")
    allowed_lag = _finite_number(allowlist_lag_ms, "allowlist_lag_ms")
    if requested_lag != allowed_lag:
        raise ValueError("lag_ms does not match the frozen allowlist entry")

    exclusions = []
    for item in excluded_intervals:
        if not isinstance(item, (list, tuple)) or len(item) != 3:
            raise ValueError("excluded intervals must be (string, start, end)")
        string, start, end = item
        if type(string) is not int or not 0 <= string < NUM_STRINGS:
            raise ValueError("invalid exclusion string")
        start = _finite_number(start, "exclusion start")
        end = _finite_number(end, "exclusion end")
        if end <= start:
            raise ValueError("invalid exclusion interval")
        exclusions.append((string, start, end))

    events, issues, canonical_notes = source_events_from_notes(
        notes, capture_id=capture_id, lag_ms=requested_lag
    )
    crop_start = crop_start_frame * hop
    crop_end = crop_start + frames * hop

    state = [[-1] * frames for _ in range(NUM_STRINGS)]
    onset = [[0] * frames for _ in range(NUM_STRINGS)]
    event_id = [[None] * frames for _ in range(NUM_STRINGS)]
    loss_mask = [[True] * frames for _ in range(NUM_STRINGS)]

    # Raw registered masks are invalid for all heads.
    for string, start, end in exclusions:
        lo = max(0, bisect_left([crop_start + i * hop for i in range(frames)], start))
        hi = min(frames, bisect_left([crop_start + i * hop for i in range(frames)], end))
        for frame in range(lo, hi):
            loss_mask[string][frame] = False
            state[string][frame] = MASK
            onset[string][frame] = MASK
            event_id[string][frame] = None

    source_issue_ids = {
        issue["eventId"]
        for issue in issues
        if issue["code"] in {
            "nonpositive_source_duration",
            "negative_aligned_time",
            "unsupported_fret",
            "same_string_overlap",
        }
    }
    for issue in issues:
        if issue["code"] == "same_string_overlap":
            source_issue_ids.add(issue["otherEventId"])

    # Keep every source issue visible, but only an issue that intersects this
    # selected training crop blocks this crop's optimizer use. This avoids
    # silently deleting bad source events elsewhere in a performance while also
    # avoiding an unrelated out-of-crop event vetoing an otherwise explicit crop.
    in_crop_ids = {
        event.id for event in events
        if _event_intersects_crop(event, crop_start, crop_end)
    }
    unresolved_ids = source_issue_ids & in_crop_ids

    carry_in = []
    carry_out = []
    excluded = []
    scorable = []
    in_crop_source_ids = []

    for event in events:
        if not _event_intersects_crop(event, crop_start, crop_end):
            continue
        in_crop_source_ids.append(event.id)
        if event.aligned_start < crop_start:
            carry_in.append(event.id)
        if event.aligned_end > crop_end:
            carry_out.append(event.id)

        lo, hi = _event_frame_span(event, crop_start, frames, hop)
        if lo >= hi and event.id not in unresolved_ids:
            issues.append({"code": "subframe_attack", "eventId": event.id})
            unresolved_ids.add(event.id)

        masked = any(_mask_intersects(event, interval) for interval in exclusions)
        if masked:
            excluded.append({"eventId": event.id, "reason": "registered_mask_intersection"})
        if event.aligned_start < crop_start or event.aligned_end > crop_end:
            excluded.append({"eventId": event.id, "reason": "crop_boundary"})
        if event.id in unresolved_ids:
            excluded.append({"eventId": event.id, "reason": "unresolved_source"})

        # Unresolved or explicitly masked events are made loss-ineligible for
        # their entire in-crop occupancy. They are never silently deleted.
        if event.id in unresolved_ids or masked:
            for frame in range(max(0, lo), min(frames, hi)):
                loss_mask[event.string][frame] = False
                state[event.string][frame] = MASK
                onset[event.string][frame] = MASK
                event_id[event.string][frame] = None
            continue

        for frame in range(max(0, lo), min(frames, hi)):
            if not loss_mask[event.string][frame]:
                continue
            if event_id[event.string][frame] is not None:
                issues.append({
                    "code": "frame_grid_collision",
                    "eventId": event.id,
                    "otherEventId": event_id[event.string][frame],
                    "frame": frame,
                })
                unresolved_ids.update((event.id, event_id[event.string][frame]))
                loss_mask[event.string][frame] = False
                state[event.string][frame] = MASK
                onset[event.string][frame] = MASK
                event_id[event.string][frame] = None
                continue
            state[event.string][frame] = event.fret
            event_id[event.string][frame] = event.id

        # A source attack inside the crop is the only way to create an onset.
        if crop_start <= event.aligned_start < crop_end and lo < frames:
            if loss_mask[event.string][lo]:
                onset[event.string][lo] = 1

        if (
            event.id not in unresolved_ids
            and not masked
            and event.aligned_start >= crop_start
            and event.aligned_end <= crop_end
            and lo < hi
        ):
            scorable.append({
                "id": event.id,
                "string": event.string,
                "fret": event.fret,
                "start": event.aligned_start - crop_start,
                "end": event.aligned_end - crop_start,
            })

    # If a late frame-grid collision was discovered, mask every occupied frame
    # for every implicated event and remove it from scoring.
    if any(i["code"] == "frame_grid_collision" for i in issues):
        for string in range(NUM_STRINGS):
            for frame in range(frames):
                if event_id[string][frame] in unresolved_ids:
                    loss_mask[string][frame] = False
                    state[string][frame] = MASK
                    onset[string][frame] = MASK
                    event_id[string][frame] = None
        scorable = [e for e in scorable if e["id"] not in unresolved_ids]

    unresolved = [
        _canonical_issue(i) for i in issues
        if i.get("eventId") in unresolved_ids or i.get("otherEventId") in unresolved_ids
    ]
    source_issues = [_canonical_issue(i) for i in issues]
    excluded_unique = {}
    for row in excluded:
        excluded_unique[(row["eventId"], row["reason"])] = row
    excluded = [excluded_unique[k] for k in sorted(excluded_unique)]

    source_payload = {
        "captureId": capture_id,
        "lagMs": requested_lag,
        "notes": {name: [list(row) for row in canonical_notes[name]] for name in STRING_ORDER},
    }
    allowlist_payload = {"captureId": capture_id, "lagMs": allowed_lag}
    target_payload = {
        "state": state,
        "onset": onset,
        "eventId": event_id,
        "lossMask": loss_mask,
    }

    return {
        "schema": SCHEMA,
        "captureId": capture_id,
        "lagMs": requested_lag,
        "allowlistEntrySha256": _sha256_json(allowlist_payload),
        "sourceEventSha256": _sha256_json(source_payload),
        "targetSha256": _sha256_json(target_payload),
        "crop": {
            "startFrame": crop_start_frame,
            "frames": frames,
            "hopSeconds": hop,
            "startSeconds": crop_start,
            "endSeconds": crop_end,
        },
        "state": state,
        "onset": onset,
        "eventId": event_id,
        "lossMask": loss_mask,
        "scorableEvents": sorted(scorable, key=lambda e: (e["string"], e["start"], e["id"])),
        "carryInEventIds": sorted(set(carry_in)),
        "carryOutEventIds": sorted(set(carry_out)),
        "excludedEvents": excluded,
        "inCropSourceEventIds": sorted(in_crop_source_ids),
        "unresolved": unresolved,
        "unresolvedLabelCount": len(unresolved_ids),
        "sourceIssues": source_issues,
        "outOfCropSourceIssueCount": max(0, len(source_issues) - len(unresolved)),
        "launchReady": len(unresolved_ids) == 0,
        "customerDeliveryEligible": False,
    }


def select_training_crop(events, *, total_frames, frames, hop_seconds):
    """Freeze a deterministic training-only crop rule with no model outputs.

    Prefer the earliest 200-frame-capable window containing a repeated attack
    (same string/fret, distinct source IDs). Otherwise use the earliest event.
    This deliberately establishes source-event coverage for a fitting test; it is
    not a validation or generalization selection rule.
    """
    if type(total_frames) is not int or total_frames <= 0:
        raise ValueError("total_frames must be positive")
    if type(frames) is not int or frames <= 0 or frames > total_frames:
        raise ValueError("frames must fit inside total_frames")
    hop = _finite_number(hop_seconds, "hop_seconds")
    if hop <= 0:
        raise ValueError("hop_seconds must be positive")
    usable = [
        e for e in events
        if 0 <= e.fret <= MAX_FRET and 0 <= e.aligned_start < e.aligned_end
    ]
    by_key = {}
    repeated = []
    for e in sorted(usable, key=lambda x: (x.aligned_start, x.string, x.fret, x.id)):
        key = (e.string, e.fret)
        prev = by_key.get(key)
        if prev is not None:
            first_frame = int(math.floor(prev.aligned_start / hop))
            second_frame = int(math.floor(e.aligned_start / hop))
            if second_frame - first_frame < frames:
                repeated.append((prev, e, first_frame, second_frame))
        by_key[key] = e

    max_start = total_frames - frames

    def start_for(seconds):
        frame = max(0, int(math.floor(seconds / hop)) - 8)
        return min(max_start, frame)

    if repeated:
        first, second, first_frame, second_frame = min(
            repeated,
            key=lambda pair: (pair[1].aligned_start, pair[0].aligned_start, pair[0].id),
        )
        start = start_for(first.aligned_start)
        if second_frame >= start + frames:
            start = max(0, second_frame - frames + 1)
        start = min(max_start, start)
        if not (start <= first_frame < start + frames and start <= second_frame < start + frames):
            raise RuntimeError("repeat crop selection invariant failed")
        return {
            "startFrame": start,
            "reason": "earliest_repeated_same_fret_attack",
            "coverageEventIds": [first.id, second.id],
        }

    if usable:
        first = min(usable, key=lambda e: (e.aligned_start, e.string, e.fret, e.id))
        return {"startFrame": start_for(first.aligned_start), "reason": "earliest_source_attack", "coverageEventIds": [first.id]}

    return {"startFrame": 0, "reason": "no_resolved_source_attack", "coverageEventIds": []}
