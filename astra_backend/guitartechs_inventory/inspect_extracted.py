#!/usr/bin/env python3
"""Inventory-only Guitar-TECHS extracted archive inspector.

Reads file layout, WAV headers and Standard MIDI File event structure.
It performs no audio feature extraction, alignment, model import or training.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import struct
import wave


IGNORED_DIRS = {"__MACOSX"}
IGNORED_NAMES = {".DS_Store"}
MIDI_SUFFIXES = {".mid", ".midi"}


def visible_files(root: Path):
    out = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        if path.name in IGNORED_NAMES or path.name.startswith("._"):
            continue
        out.append(path)
    return sorted(out)


def performance_key(path: Path, root: Path):
    rel = path.relative_to(root)
    stem = path.stem
    parent = path.parent.name
    prefixes = ["midi_", "directinput_", "micamp_", "ego_", "exo_"]
    candidates = [f"{parent}_"] + prefixes
    for prefix in candidates:
        if stem.lower().startswith(prefix.lower()) and len(stem) > len(prefix):
            return stem[len(prefix):]
    return stem


def read_vlq(data: bytes, index: int):
    value = 0
    for _ in range(4):
        if index >= len(data):
            raise ValueError("truncated vlq")
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, index
    return value, index


def parse_midi(path: Path, root: Path):
    data = path.read_bytes()
    rel = path.relative_to(root).as_posix()
    if len(data) < 14 or data[:4] != b"MThd":
        return {"path": rel, "valid": False, "reason": "missing-MThd"}
    header_len = struct.unpack(">I", data[4:8])[0]
    if header_len < 6 or len(data) < 8 + header_len:
        return {"path": rel, "valid": False, "reason": "invalid-header-length"}
    fmt, declared_tracks, division = struct.unpack(">HHH", data[8:14])
    pos = 8 + header_len
    tracks = []

    for track_index in range(declared_tracks):
        if pos + 8 > len(data) or data[pos:pos+4] != b"MTrk":
            break
        size = struct.unpack(">I", data[pos+4:pos+8])[0]
        chunk = data[pos+8:pos+8+size]
        pos += 8 + size
        i = 0
        running = None
        abs_tick = 0
        names, instruments, text_events = [], [], []
        programs = []
        note_channels = collections.Counter()
        unique_pitches = set()
        controls = collections.Counter()
        control_values = collections.Counter()
        meta_types = collections.Counter()
        note_ons = 0
        note_offs = 0
        pitch_values = []
        active = collections.Counter()
        max_active = 0
        overlap_note_ons = 0

        while i < len(chunk):
            try:
                delta, i = read_vlq(chunk, i)
                abs_tick += delta
                if i >= len(chunk):
                    break
                status = chunk[i]
                if status < 0x80:
                    if running is None:
                        break
                    status = running
                else:
                    i += 1
                    if status < 0xF0:
                        running = status

                if status == 0xFF:
                    if i >= len(chunk):
                        break
                    meta_type = chunk[i]
                    i += 1
                    length, i = read_vlq(chunk, i)
                    payload = chunk[i:i+length]
                    i += length
                    meta_types[meta_type] += 1
                    if meta_type == 0x03:
                        names.append(payload.decode("utf-8", "replace"))
                    elif meta_type == 0x04:
                        instruments.append(payload.decode("utf-8", "replace"))
                    elif meta_type in {0x01, 0x02, 0x05, 0x06, 0x07}:
                        text_events.append({
                            "type": meta_type,
                            "text": payload.decode("utf-8", "replace")[:300],
                        })
                    continue

                if status in (0xF0, 0xF7):
                    length, i = read_vlq(chunk, i)
                    i += length
                    continue

                kind = status & 0xF0
                channel = status & 0x0F
                if kind in (0xC0, 0xD0):
                    if i >= len(chunk):
                        break
                    a = chunk[i]
                    i += 1
                    if kind == 0xC0:
                        programs.append({"channel": channel, "program": a, "tick": abs_tick})
                    continue

                if i + 1 >= len(chunk):
                    break
                a, b = chunk[i], chunk[i+1]
                i += 2

                if kind == 0x90 and b > 0:
                    note_ons += 1
                    note_channels[channel] += 1
                    unique_pitches.add(a)
                    if active[a] > 0:
                        overlap_note_ons += 1
                    active[a] += 1
                    max_active = max(max_active, sum(active.values()))
                elif kind == 0x80 or (kind == 0x90 and b == 0):
                    note_offs += 1
                    if active[a] > 0:
                        active[a] -= 1
                elif kind == 0xE0:
                    pitch_values.append(((b << 7) | a) - 8192)
                elif kind == 0xB0:
                    controls[a] += 1
                    control_values[(a, b)] += 1
            except Exception:
                break

        tracks.append({
            "index": track_index,
            "names": names,
            "instruments": instruments,
            "textEvents": text_events,
            "programs": programs[:30],
            "noteOns": note_ons,
            "noteOffs": note_offs,
            "noteChannels": {str(k): v for k, v in sorted(note_channels.items())},
            "uniqueMidi": sorted(unique_pitches),
            "minMidi": min(unique_pitches) if unique_pitches else None,
            "maxMidi": max(unique_pitches) if unique_pitches else None,
            "pitchBendEvents": len(pitch_values),
            "pitchBendMin": min(pitch_values) if pitch_values else None,
            "pitchBendMax": max(pitch_values) if pitch_values else None,
            "pitchBendUnique": sorted(set(pitch_values))[:100],
            "controlChangeCounts": {str(k): v for k, v in sorted(controls.items())},
            "controlChangeValueCounts": {
                f"{cc}:{value}": count
                for (cc, value), count in sorted(control_values.items())
            },
            "maxSimultaneousActiveNotes": max_active,
            "samePitchOverlapNoteOns": overlap_note_ons,
            "metaTypes": {str(k): v for k, v in sorted(meta_types.items())},
        })

    return {
        "path": rel,
        "performanceKey": performance_key(path, root),
        "valid": True,
        "format": fmt,
        "tracksDeclared": declared_tracks,
        "tracksParsed": len(tracks),
        "division": division,
        "tracks": tracks,
    }


def wav_header(path: Path, root: Path):
    rel = path.relative_to(root).as_posix()
    try:
        with wave.open(str(path), "rb") as handle:
            rate = handle.getframerate()
            frames = handle.getnframes()
            return {
                "path": rel,
                "performanceKey": performance_key(path, root),
                "captureView": path.parent.name,
                "channels": handle.getnchannels(),
                "sampleRate": rate,
                "sampleWidth": handle.getsampwidth(),
                "frames": frames,
                "durationSeconds": frames / rate if rate else None,
            }
    except Exception as exc:
        return {"path": rel, "error": str(exc)}


def build_groups(files, root: Path):
    groups = {}
    for path in files:
        suffix = path.suffix.lower()
        key = performance_key(path, root)
        group = groups.setdefault(key, {
            "performanceKey": key,
            "midiFiles": [],
            "audioCaptureViews": {},
            "videoCaptureViews": {},
            "otherFiles": [],
        })
        rel = path.relative_to(root).as_posix()
        parts = path.relative_to(root).parts
        if suffix in MIDI_SUFFIXES:
            group["midiFiles"].append(rel)
        elif suffix == ".wav" and "audio" in parts:
            view = path.parent.name
            group["audioCaptureViews"].setdefault(view, []).append(rel)
        elif suffix == ".mp3" and "video" in parts:
            view = path.parent.name
            group["videoCaptureViews"].setdefault(view, []).append(rel)
        else:
            group["otherFiles"].append(rel)
    for group in groups.values():
        group["midiFiles"].sort()
        group["audioCaptureViews"] = {k: sorted(v) for k, v in sorted(group["audioCaptureViews"].items())}
        group["videoCaptureViews"] = {k: sorted(v) for k, v in sorted(group["videoCaptureViews"].items())}
        group["otherFiles"].sort()
    return [groups[k] for k in sorted(groups)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--performer", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--bytes", required=True, type=int)
    parser.add_argument("--md5", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    files = visible_files(root)
    extension_counts = collections.Counter((p.suffix.lower() or "<none>") for p in files)
    extension_bytes = collections.Counter()
    for path in files:
        extension_bytes[path.suffix.lower() or "<none>"] += path.stat().st_size

    midi_files = [p for p in files if p.suffix.lower() in MIDI_SUFFIXES]
    wav_files = [p for p in files if p.suffix.lower() == ".wav"]

    receipt = {
        "schema": "astra-guitar-techs-development-inventory-archive-v1",
        "archiveIdentity": {
            "file": args.archive,
            "bytes": args.bytes,
            "md5": args.md5,
            "astraSha256": args.sha256,
            "verifiedBeforeExtraction": True,
        },
        "performer": args.performer,
        "category": args.category,
        "fileCount": len(files),
        "totalExtractedBytes": sum(p.stat().st_size for p in files),
        "extensionCounts": dict(sorted(extension_counts.items())),
        "extensionBytes": dict(sorted(extension_bytes.items())),
        "performanceGroups": build_groups(files, root),
        "midi": [parse_midi(p, root) for p in midi_files],
        "wav": [wav_header(p, root) for p in wav_files],
        "allVisiblePaths": [p.relative_to(root).as_posix() for p in files],
        "policy": {
            "inventoryOnly": True,
            "alignmentRun": False,
            "audioFeaturesComputed": False,
            "modelImported": False,
            "trainingRun": False,
            "p3Opened": False,
        },
    }
    print("ASTRA_GUITARTECHS_INVENTORY_RECEIPT=" + json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
