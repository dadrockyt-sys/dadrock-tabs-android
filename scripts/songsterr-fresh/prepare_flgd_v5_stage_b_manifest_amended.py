#!/usr/bin/env python3
"""Official audited pairing adapter for FLGD V5 Stage B.

Changes only the canonical-MIDI note-edge pairing rule frozen in
SONGSTERR_FRESH_FLGD_V5_STAGE_B_MIDI_PAIRING_AMENDMENT.md.  All other Stage B
population, metadata, syncpoint, tempo, identity and policy behavior is supplied
by the already-green core prepare_flgd_v5_stage_b_manifest.py.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path

CORE_PATH = Path(__file__).with_name("prepare_flgd_v5_stage_b_manifest.py")
spec = importlib.util.spec_from_file_location("flgd_stage_b_core", CORE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("STAGE_B_CORE_IMPORT_SPEC_FAILED")
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

CONTRACT = "songsterr-fresh-flgd-v5-stage-b-manifest-pairing-amended-v1"
VERSION = 1
MIDI_EDGE_AUDIT_REPORT_SHA256 = (
    "111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24"
)
EXPECTED_REAL_IGNORED_DUPLICATE_RELEASE_COUNT = 24


class AdapterError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def inspect_reference_midi_amended(path: Path, stem: str) -> dict:
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        raise core.StageBError(f"MIDI_HEADER_INVALID:{path}")
    header_length = struct.unpack(">I", data[4:8])[0]
    if header_length != 6:
        raise core.StageBError(f"MIDI_HEADER_LENGTH_CHANGED:{path}:{header_length}")
    midi_format, track_count, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise core.StageBError(f"MIDI_SMPTE_DIVISION_NOT_AUTHORIZED:{path}")
    ppq = int(division)
    if ppq <= 0:
        raise core.StageBError(f"MIDI_PPQ_NONPOSITIVE:{path}")
    if midi_format not in (0, 1):
        raise core.StageBError(f"MIDI_FORMAT_NOT_AUTHORIZED:{path}:{midi_format}")

    pos = 14
    note_messages: list[dict] = []
    tempos: list[dict] = []
    for track_index in range(int(track_count)):
        if pos + 8 > len(data) or data[pos : pos + 4] != b"MTrk":
            raise core.StageBError(f"MIDI_TRACK_HEADER_INVALID:{path}:{track_index}")
        length = struct.unpack(">I", data[pos + 4 : pos + 8])[0]
        pos += 8
        end = pos + length
        if end > len(data):
            raise core.StageBError(f"MIDI_TRACK_LENGTH_TRUNCATED:{path}:{track_index}")
        notes_part, tempos_part = core._parse_track(data[pos:end], track_index)
        note_messages.extend(notes_part)
        tempos.extend(tempos_part)
        pos = end
    if pos != len(data):
        raise core.StageBError(f"MIDI_TRAILING_BYTES:{path}:{len(data)-pos}")

    tempo_segments, tick_to_seconds = core._tempo_map(tempos, ppq)
    messages = sorted(
        note_messages,
        key=lambda row: (row["tick"], row["trackIndex"], row["eventOrder"]),
    )

    active: dict[tuple[int, int], deque[dict]] = defaultdict(deque)
    completed_pairs = Counter()
    paired: list[dict] = []
    ignored_duplicate_releases: list[dict] = []
    overlap_count = 0
    channels = set()

    for message in messages:
        key = (int(message["channel"]), int(message["midi"]))
        channels.add(key[0])
        if message["isOn"]:
            if active[key]:
                overlap_count += 1
            active[key].append(message)
            continue

        if active[key]:
            onset = active[key].popleft()
            if int(message["tick"]) < int(onset["tick"]):
                raise core.StageBError("MIDI_NOTE_OFFSET_BEFORE_ONSET")
            paired.append({
                "channel": key[0],
                "midi": key[1],
                "onsetTick": int(onset["tick"]),
                "offsetTick": int(message["tick"]),
                "onsetTrackIndex": int(onset["trackIndex"]),
                "onsetEventOrder": int(onset["eventOrder"]),
            })
            completed_pairs[key] += 1
            continue

        if completed_pairs[key] > 0:
            ignored_duplicate_releases.append({
                "channel": key[0],
                "midi": key[1],
                "tick": int(message["tick"]),
                "trackIndex": int(message["trackIndex"]),
                "eventOrder": int(message["eventOrder"]),
                "velocity": int(message["velocity"]),
            })
            continue

        raise core.StageBError(
            f"MIDI_UNMATCHED_NOTE_OFF:{path}:{key}:{message['tick']}"
        )

    leftovers = [key for key, queue in active.items() if queue]
    if leftovers:
        raise core.StageBError(f"MIDI_UNMATCHED_NOTE_ON:{path}:{leftovers[:8]}")

    paired.sort(
        key=lambda row: (
            row["onsetTick"],
            row["onsetTrackIndex"],
            row["onsetEventOrder"],
            row["channel"],
            row["midi"],
            row["offsetTick"],
        )
    )
    identities = []
    for ordinal, row in enumerate(paired, start=1):
        onset_seconds = tick_to_seconds(row["onsetTick"])
        offset_seconds = tick_to_seconds(row["offsetTick"])
        if not math.isfinite(onset_seconds) or not math.isfinite(offset_seconds):
            raise core.StageBError("MIDI_CONVERTED_TIME_NONFINITE")
        if onset_seconds < 0.0 or offset_seconds < onset_seconds:
            raise core.StageBError("MIDI_CONVERTED_TIME_INVALID")
        identities.append({
            "stem": stem,
            "eventOrdinal": ordinal,
            "channel": row["channel"],
            "midi": row["midi"],
            "onsetTick": row["onsetTick"],
            "offsetTick": row["offsetTick"],
            "onsetSeconds": onset_seconds,
            "offsetSeconds": offset_seconds,
        })

    ignored_identities = [
        {"stem": stem, **row} for row in ignored_duplicate_releases
    ]
    notes = [row["midi"] for row in identities]
    onsets = [row["onsetSeconds"] for row in identities]
    offsets = [row["offsetSeconds"] for row in identities]
    durations = [b - a for a, b in zip(onsets, offsets)]
    tempo_values = sorted({int(row["tempoUsPerQuarter"]) for row in tempo_segments})

    return {
        "sha256": core.sha256_bytes(data),
        "format": int(midi_format),
        "trackCount": int(track_count),
        "ticksPerQuarter": ppq,
        "tempoSegmentCount": len(tempo_segments),
        "tempoUsPerQuarterDomain": tempo_values,
        "channelDomain": sorted(channels),
        "sameKeyOverlapCount": overlap_count,
        "referenceEventCount": len(identities),
        "midiMin": min(notes) if notes else None,
        "midiMax": max(notes) if notes else None,
        "onsetMinSeconds": min(onsets) if onsets else None,
        "onsetMaxSeconds": max(onsets) if onsets else None,
        "offsetMinSeconds": min(offsets) if offsets else None,
        "offsetMaxSeconds": max(offsets) if offsets else None,
        "durationMinSeconds": min(durations) if durations else None,
        "durationMaxSeconds": max(durations) if durations else None,
        "referenceEventIdentitySha256": core.sha256_bytes(
            core.canonical_json(identities).encode("utf-8")
        ),
        "ignoredDuplicateReleaseCount": len(ignored_identities),
        "ignoredDuplicateReleaseIdentitySha256": core.sha256_bytes(
            core.canonical_json(ignored_identities).encode("utf-8")
        ),
        "_identities": identities,
        "_ignoredDuplicateReleases": ignored_duplicate_releases,
    }


def build_stage_b_amended(root: Path, *, expected_ignored_count: int | None = None) -> dict:
    original = core.inspect_reference_midi
    core.inspect_reference_midi = inspect_reference_midi_amended
    try:
        result = core.build_stage_b(root)
    finally:
        core.inspect_reference_midi = original

    ignored_global = []
    for row in result["included"]:
        ignored = row["midi"].pop("_ignoredDuplicateReleases", [])
        for edge in ignored:
            ignored_global.append({
                "stem": row["stem"],
                "midiPath": row["midi"]["path"],
                **edge,
            })

    actual_count = len(ignored_global)
    if expected_ignored_count is not None and actual_count != expected_ignored_count:
        raise core.StageBError(
            f"IGNORED_DUPLICATE_RELEASE_COUNT_CHANGED:{actual_count}!={expected_ignored_count}"
        )

    result["contract"] = CONTRACT
    result["version"] = VERSION
    result["dataset"]["midiEdgeAuditReportSha256"] = MIDI_EDGE_AUDIT_REPORT_SHA256
    result["summary"]["ignoredDuplicateReleaseCount"] = actual_count
    result["ignoredDuplicateReleaseIdentitySha256"] = core.sha256_bytes(
        core.canonical_json(ignored_global).encode("utf-8")
    )
    result["pairingAmendment"] = {
        "rule": "ignore-unmatched-note-off-only-after-prior-completed-same-key-pair",
        "leadingOrphanNoteOffFails": True,
        "unmatchedNoteOnFails": True,
        "expectedRealIgnoredDuplicateReleaseCount": EXPECTED_REAL_IGNORED_DUPLICATE_RELEASE_COUNT,
    }
    return result


def _varlen(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def _track(payload: bytes) -> bytes:
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def _midi_duplicate_release() -> bytes:
    payload = bytearray()
    payload += _varlen(0) + bytes([0x90, 60, 100])
    payload += _varlen(120) + bytes([0x80, 60, 0])
    payload += _varlen(10) + bytes([0x80, 60, 0])
    payload += _varlen(0) + b"\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + _track(bytes(payload))


def _midi_leading_orphan() -> bytes:
    payload = _varlen(0) + bytes([0x80, 60, 0]) + _varlen(0) + b"\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + _track(payload)


def _midi_trailing_on() -> bytes:
    payload = _varlen(0) + bytes([0x90, 60, 100]) + _varlen(0) + b"\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + _track(payload)


def self_test() -> dict:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        good = root / "good.mid"
        good.write_bytes(_midi_duplicate_release())
        parsed = inspect_reference_midi_amended(good, "good")
        assert parsed["referenceEventCount"] == 1
        assert parsed["ignoredDuplicateReleaseCount"] == 1
        assert len(parsed["_ignoredDuplicateReleases"]) == 1

        bad_off = root / "bad-off.mid"
        bad_off.write_bytes(_midi_leading_orphan())
        try:
            inspect_reference_midi_amended(bad_off, "bad-off")
        except core.StageBError as exc:
            assert "MIDI_UNMATCHED_NOTE_OFF" in str(exc)
        else:
            raise AssertionError("leading orphan note-off must fail")

        bad_on = root / "bad-on.mid"
        bad_on.write_bytes(_midi_trailing_on())
        try:
            inspect_reference_midi_amended(bad_on, "bad-on")
        except core.StageBError as exc:
            assert "MIDI_UNMATCHED_NOTE_ON" in str(exc)
        else:
            raise AssertionError("trailing unmatched note-on must fail")

    return {
        "contract": CONTRACT,
        "selfTest": "PASS",
        "midiEdgeAuditReportSha256": MIDI_EDGE_AUDIT_REPORT_SHA256,
        "expectedRealIgnoredDuplicateReleaseCount": EXPECTED_REAL_IGNORED_DUPLICATE_RELEASE_COUNT,
        "policyBoundary": dict(core.POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--dataset-root")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(canonical_json(self_test()))
        return 0
    if not args.dataset_root or not args.output:
        raise AdapterError("DATASET_ROOT_AND_OUTPUT_REQUIRED")
    output = Path(args.output).resolve()
    if output.exists():
        raise AdapterError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = build_stage_b_amended(
        Path(args.dataset_root),
        expected_ignored_count=EXPECTED_REAL_IGNORED_DUPLICATE_RELEASE_COUNT,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "summary": result["summary"],
        "includedPopulationSha256": result["includedPopulationSha256"],
        "referenceEventIdentitySha256": result["referenceEventIdentitySha256"],
        "ignoredDuplicateReleaseIdentitySha256": result["ignoredDuplicateReleaseIdentitySha256"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AdapterError, core.StageBError) as exc:
        print(f"FLGD_V5_STAGE_B_AMENDED_ERROR:{exc}")
        raise SystemExit(2)
