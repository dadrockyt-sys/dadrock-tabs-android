#!/usr/bin/env python3
"""Non-scoring structural audit of FLGD canonical MIDI note edges."""

from __future__ import annotations

import argparse
import importlib.util
import json
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path

STAGE_B_PATH = Path(__file__).with_name("prepare_flgd_v5_stage_b_manifest.py")
spec = importlib.util.spec_from_file_location("flgd_stage_b_for_edge_audit", STAGE_B_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("STAGE_B_IMPORT_SPEC_FAILED")
stage_b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stage_b)

CONTRACT = "songsterr-fresh-flgd-v5-midi-edge-audit-v1"
VERSION = 1

POLICY_BOUNDARY = {
    "basicPitchInvoked": False,
    "v5ClassifierInvoked": False,
    "demucsInvoked": False,
    "audioSamplesUsedForPitchAnalysis": False,
    "estimateReferenceMatchingPerformed": False,
    "correctnessMetricComputed": False,
    "protectedSongUsed": False,
    "modelValidationComplete": False,
    "customerEligibleEvents": 0,
    "mayAdvanceDelivery": False,
    "durationAuthorityChanged": False,
}


class AuditError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _extract_note_messages(data: bytes, label: str) -> tuple[dict, list[dict]]:
    if len(data) < 14 or data[:4] != b"MThd":
        raise AuditError(f"MIDI_HEADER_INVALID:{label}")
    header_length = struct.unpack(">I", data[4:8])[0]
    if header_length != 6:
        raise AuditError(f"MIDI_HEADER_LENGTH_CHANGED:{label}:{header_length}")
    midi_format, track_count, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise AuditError(f"MIDI_SMPTE_DIVISION_NOT_AUTHORIZED:{label}")

    pos = 14
    messages = []
    for track_index in range(int(track_count)):
        if pos + 8 > len(data) or data[pos : pos + 4] != b"MTrk":
            raise AuditError(f"MIDI_TRACK_HEADER_INVALID:{label}:{track_index}")
        length = struct.unpack(">I", data[pos + 4 : pos + 8])[0]
        pos += 8
        end = pos + length
        if end > len(data):
            raise AuditError(f"MIDI_TRACK_TRUNCATED:{label}:{track_index}")
        try:
            notes, _tempos = stage_b._parse_track(data[pos:end], track_index)
        except stage_b.StageBError as exc:
            raise AuditError(f"MIDI_TRACK_PARSE_FAILED:{label}:{exc}") from exc
        messages.extend(notes)
        pos = end
    if pos != len(data):
        raise AuditError(f"MIDI_TRAILING_BYTES:{label}:{len(data)-pos}")

    messages.sort(key=lambda row: (row["tick"], row["trackIndex"], row["eventOrder"]))
    for ordinal, row in enumerate(messages, start=1):
        row["globalMessageOrdinal"] = ordinal
    return {
        "format": int(midi_format),
        "trackCount": int(track_count),
        "ticksPerQuarter": int(division),
    }, messages


def _edge_context(messages: list[dict], index: int) -> dict:
    edge = messages[index]
    key = (edge["channel"], edge["midi"])
    same = [
        (i, row)
        for i, row in enumerate(messages)
        if (row["channel"], row["midi"]) == key
    ]
    earlier = [row for i, row in same if i < index]
    later = [row for i, row in same if i > index]
    same_tick = [row for _i, row in same if row["tick"] == edge["tick"]]
    return {
        "hasEarlierOn": any(row["isOn"] for row in earlier),
        "hasEarlierOff": any(not row["isOn"] for row in earlier),
        "hasLaterOn": any(row["isOn"] for row in later),
        "hasLaterOff": any(not row["isOn"] for row in later),
        "isEarliestSameKeyMessage": not earlier,
        "isLatestSameKeyMessage": not later,
        "sameTickSameKeySequence": [
            {
                "globalMessageOrdinal": row["globalMessageOrdinal"],
                "trackIndex": row["trackIndex"],
                "eventOrder": row["eventOrder"],
                "isOn": row["isOn"],
                "velocity": row["velocity"],
            }
            for row in same_tick
        ],
    }


def audit_midi_bytes(data: bytes, label: str) -> dict:
    header, messages = _extract_note_messages(data, label)
    active: dict[tuple[int, int], deque[dict]] = defaultdict(deque)
    matched_pairs = 0
    overlap_count = 0
    unmatched_offs = []

    for index, message in enumerate(messages):
        key = (int(message["channel"]), int(message["midi"]))
        if message["isOn"]:
            if active[key]:
                overlap_count += 1
            active[key].append(message)
        else:
            if active[key]:
                active[key].popleft()
                matched_pairs += 1
            else:
                context = _edge_context(messages, index)
                unmatched_offs.append({
                    "tick": int(message["tick"]),
                    "trackIndex": int(message["trackIndex"]),
                    "eventOrder": int(message["eventOrder"]),
                    "globalMessageOrdinal": int(message["globalMessageOrdinal"]),
                    "channel": key[0],
                    "midi": key[1],
                    "velocity": int(message["velocity"]),
                    "statusForm": "note-off-or-note-on-zero",
                    **context,
                    "duplicateReleaseCandidate": bool(context["hasEarlierOn"] and context["hasEarlierOff"]),
                    "leadingBoundaryReleaseCandidate": bool(context["isEarliestSameKeyMessage"] and context["hasLaterOn"]),
                })

    unmatched_ons = []
    for key, queue in sorted(active.items()):
        for message in queue:
            index = int(message["globalMessageOrdinal"]) - 1
            context = _edge_context(messages, index)
            unmatched_ons.append({
                "tick": int(message["tick"]),
                "trackIndex": int(message["trackIndex"]),
                "eventOrder": int(message["eventOrder"]),
                "globalMessageOrdinal": int(message["globalMessageOrdinal"]),
                "channel": int(key[0]),
                "midi": int(key[1]),
                "velocity": int(message["velocity"]),
                **context,
                "trailingBoundaryOnCandidate": bool(context["isLatestSameKeyMessage"]),
            })

    return {
        **header,
        "noteMessageCount": len(messages),
        "noteOnCount": sum(1 for row in messages if row["isOn"]),
        "noteOffCount": sum(1 for row in messages if not row["isOn"]),
        "matchedPairCount": matched_pairs,
        "sameKeyOverlapCount": overlap_count,
        "unmatchedNoteOffCount": len(unmatched_offs),
        "unmatchedNoteOnCount": len(unmatched_ons),
        "unmatchedNoteOffs": unmatched_offs,
        "unmatchedNoteOns": unmatched_ons,
    }


def audit_dataset(root: Path) -> dict:
    root = root.resolve()
    try:
        git_identity = stage_b.verify_dataset_git(root)
        rows, metadata = stage_b._read_metadata(root)
        stage_b._verify_exact_canonical_membership(root, rows)
    except stage_b.StageBError as exc:
        raise AuditError(str(exc)) from exc

    per_file = []
    total = Counter()
    files_with_unmatched_offs = []
    files_with_unmatched_ons = []
    edge_identity_rows = []

    for row in rows:
        path = root / row["midiPath"]
        result = audit_midi_bytes(path.read_bytes(), row["midiPath"])
        per_file.append({
            "stem": row["stem"],
            "midiPath": row["midiPath"],
            "midiSha256": stage_b.sha256_file(path),
            **result,
        })
        for key in (
            "noteMessageCount",
            "noteOnCount",
            "noteOffCount",
            "matchedPairCount",
            "sameKeyOverlapCount",
            "unmatchedNoteOffCount",
            "unmatchedNoteOnCount",
        ):
            total[key] += int(result[key])
        if result["unmatchedNoteOffCount"]:
            files_with_unmatched_offs.append(row["midiPath"])
        if result["unmatchedNoteOnCount"]:
            files_with_unmatched_ons.append(row["midiPath"])
        for kind in ("unmatchedNoteOffs", "unmatchedNoteOns"):
            for edge in result[kind]:
                edge_identity_rows.append({
                    "midiPath": row["midiPath"],
                    "kind": kind,
                    **edge,
                })

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "dataset": {
            "git": git_identity,
            "metadataSha256": metadata["sha256"],
            "includedPerformanceCount": len(rows),
        },
        "summary": {
            **dict(total),
            "filesWithUnmatchedNoteOffCount": len(files_with_unmatched_offs),
            "filesWithUnmatchedNoteOnCount": len(files_with_unmatched_ons),
            "filesWithUnmatchedNoteOffs": files_with_unmatched_offs,
            "filesWithUnmatchedNoteOns": files_with_unmatched_ons,
        },
        "edgeIdentitySha256": stage_b.sha256_bytes(canonical_json(edge_identity_rows).encode("utf-8")),
        "files": per_file,
        "policyBoundary": dict(POLICY_BOUNDARY),
    }


def _synthetic_varlen(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def _synthetic_midi() -> bytes:
    # One leading unmatched release, one valid pair, one duplicate release,
    # and one trailing unmatched onset on distinct keys.
    payload = bytearray()
    payload += _synthetic_varlen(0) + bytes([0x80, 48, 0])
    payload += _synthetic_varlen(10) + bytes([0x90, 60, 100])
    payload += _synthetic_varlen(10) + bytes([0x80, 60, 0])
    payload += _synthetic_varlen(5) + bytes([0x80, 60, 0])
    payload += _synthetic_varlen(5) + bytes([0x90, 67, 100])
    payload += _synthetic_varlen(0) + b"\xff\x2f\x00"
    track = b"MTrk" + struct.pack(">I", len(payload)) + bytes(payload)
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + track


def self_test() -> dict:
    result = audit_midi_bytes(_synthetic_midi(), "synthetic.mid")
    assert result["matchedPairCount"] == 1
    assert result["unmatchedNoteOffCount"] == 2
    assert result["unmatchedNoteOnCount"] == 1
    leading = result["unmatchedNoteOffs"][0]
    duplicate = result["unmatchedNoteOffs"][1]
    assert leading["leadingBoundaryReleaseCandidate"] is False  # key 48 never starts later
    assert duplicate["duplicateReleaseCandidate"] is True
    assert result["unmatchedNoteOns"][0]["trailingBoundaryOnCandidate"] is True
    return {
        "contract": CONTRACT,
        "selfTest": "PASS",
        "policyBoundary": dict(POLICY_BOUNDARY),
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
        raise AuditError("DATASET_ROOT_AND_OUTPUT_REQUIRED")
    output = Path(args.output).resolve()
    if output.exists():
        raise AuditError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = audit_dataset(Path(args.dataset_root))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "summary": result["summary"],
        "edgeIdentitySha256": result["edgeIdentitySha256"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        print(f"FLGD_V5_MIDI_EDGE_AUDIT_ERROR:{exc}")
        raise SystemExit(2)
