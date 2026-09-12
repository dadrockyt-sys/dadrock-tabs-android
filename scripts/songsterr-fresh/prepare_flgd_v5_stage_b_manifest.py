#!/usr/bin/env python3
"""Prepare the non-scoring FLGD V5 Stage B population/timing manifest.

This tool is deliberately stdlib-only. It binds the exact FLGD Git release,
metadata-named canonical audio/MIDI/syncpoint identities, and parses canonical
reference MIDI timing/notes. It does not decode audio samples, run Basic Pitch,
run V5, match estimates to references, or compute correctness.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import struct
import subprocess
from collections import Counter, defaultdict, deque
from pathlib import Path, PurePosixPath

CONTRACT = "songsterr-fresh-flgd-v5-stage-b-manifest-v1"
VERSION = 1
EXPECTED_ORIGIN_CANONICAL = "https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset"
EXPECTED_REVISION = "a38306c244b3ea81496ad58b4514622185e58211"
EXPECTED_STAGE_A_REPORT_SHA256 = "f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3"
EXPECTED_METADATA_SHA256 = "05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b"
EXPECTED_METADATA_COLUMNS = [
    "split",
    "midi_filename",
    "audio_filename",
    "guitar_type",
    "slice_id",
    "artist",
    "name",
]
EXPECTED_ROW_COUNT = 79
DEFAULT_TEMPO_US_PER_QUARTER = 500_000

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


class StageBError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def git_output(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise StageBError(f"GIT_COMMAND_FAILED:{' '.join(args)}:{proc.stderr.strip()}")
    return proc.stdout.strip()


def normalize_origin_url(value: str) -> str:
    normalized = str(value).strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


def verify_dataset_git(root: Path) -> dict:
    if not (root / ".git").exists():
        raise StageBError("DATASET_GIT_CHECKOUT_REQUIRED")
    head = git_output(root, "rev-parse", "HEAD")
    if head != EXPECTED_REVISION:
        raise StageBError(f"DATASET_REVISION_CHANGED:{head}!={EXPECTED_REVISION}")
    if git_output(root, "status", "--porcelain"):
        raise StageBError("DATASET_WORKTREE_MUST_BE_CLEAN")
    origin = git_output(root, "remote", "get-url", "origin")
    canonical = normalize_origin_url(origin)
    if canonical != EXPECTED_ORIGIN_CANONICAL:
        raise StageBError(f"DATASET_ORIGIN_CHANGED:{canonical}!={EXPECTED_ORIGIN_CANONICAL}")
    return {
        "headSha": head,
        "originUrl": origin,
        "originCanonical": canonical,
        "worktreeClean": True,
    }


def _safe_metadata_path(root_name: str, raw_value: str) -> str:
    text = str(raw_value).strip().replace("\\", "/")
    if not text:
        raise StageBError(f"EMPTY_{root_name.upper()}_FILENAME")
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts:
        raise StageBError(f"UNSAFE_{root_name.upper()}_FILENAME:{text}")
    parts = list(pure.parts)
    if parts and parts[0] == root_name:
        rel = PurePosixPath(*parts)
    else:
        rel = PurePosixPath(root_name) / pure
    if not rel.parts or rel.parts[0] != root_name:
        raise StageBError(f"NONCANONICAL_{root_name.upper()}_PATH:{text}")
    return rel.as_posix()


def _read_metadata(root: Path) -> tuple[list[dict], dict]:
    path = root / "metadata.csv"
    if not path.is_file():
        raise StageBError("METADATA_CSV_REQUIRED")
    actual_sha = sha256_file(path)
    if actual_sha != EXPECTED_METADATA_SHA256:
        raise StageBError(f"METADATA_SHA256_CHANGED:{actual_sha}!={EXPECTED_METADATA_SHA256}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != EXPECTED_METADATA_COLUMNS:
            raise StageBError(f"METADATA_COLUMNS_CHANGED:{reader.fieldnames}")
        rows = []
        for index, source in enumerate(reader, start=1):
            row = {field: str(source.get(field, "")).strip() for field in EXPECTED_METADATA_COLUMNS}
            row["rowIndex"] = index
            row["audioPath"] = _safe_metadata_path("audio", row["audio_filename"])
            row["midiPath"] = _safe_metadata_path("midi", row["midi_filename"])
            audio_stem = Path(row["audioPath"]).stem
            midi_stem = Path(row["midiPath"]).stem
            if audio_stem != midi_stem:
                raise StageBError(f"ROW_STEM_MISMATCH:{index}:{audio_stem}!={midi_stem}")
            row["stem"] = audio_stem
            row["syncpointPath"] = f"syncpoints/{audio_stem}-syncpoints.json"
            rows.append(row)

    if len(rows) != EXPECTED_ROW_COUNT:
        raise StageBError(f"METADATA_ROW_COUNT_CHANGED:{len(rows)}!={EXPECTED_ROW_COUNT}")

    audio_paths = [row["audioPath"] for row in rows]
    midi_paths = [row["midiPath"] for row in rows]
    stems = [row["stem"] for row in rows]
    if len(set(audio_paths)) != len(rows):
        raise StageBError("METADATA_AUDIO_PATHS_NOT_UNIQUE")
    if len(set(midi_paths)) != len(rows):
        raise StageBError("METADATA_MIDI_PATHS_NOT_UNIQUE")
    if len(set(stems)) != len(rows):
        raise StageBError("METADATA_STEMS_NOT_UNIQUE")

    return rows, {
        "path": "metadata.csv",
        "sha256": actual_sha,
        "rowCount": len(rows),
        "columns": EXPECTED_METADATA_COLUMNS,
        "splitCounts": dict(sorted(Counter(row["split"] for row in rows).items())),
        "guitarTypeCounts": dict(sorted(Counter(row["guitar_type"] for row in rows).items())),
    }


def _verify_exact_canonical_membership(root: Path, rows: list[dict]) -> None:
    actual_audio = sorted(
        p.relative_to(root).as_posix()
        for p in (root / "audio").rglob("*")
        if p.is_file()
    )
    actual_midi = sorted(
        p.relative_to(root).as_posix()
        for p in (root / "midi").rglob("*")
        if p.is_file()
    )
    expected_audio = sorted(row["audioPath"] for row in rows)
    expected_midi = sorted(row["midiPath"] for row in rows)
    if actual_audio != expected_audio:
        raise StageBError("CANONICAL_AUDIO_MEMBERSHIP_DIFFERS_FROM_METADATA")
    if actual_midi != expected_midi:
        raise StageBError("CANONICAL_MIDI_MEMBERSHIP_DIFFERS_FROM_METADATA")


def _finite_number(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise StageBError(f"{label}:FINITE_NUMBER_REQUIRED")
    result = float(value)
    if not math.isfinite(result):
        raise StageBError(f"{label}:FINITE_NUMBER_REQUIRED")
    return result


def inspect_syncpoints(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StageBError(f"SYNCPOINT_JSON_INVALID:{path}:{exc}") from exc
    if not isinstance(value, list):
        raise StageBError(f"SYNCPOINT_TOP_LEVEL_LIST_REQUIRED:{path}")
    if not value:
        raise StageBError(f"SYNCPOINT_LIST_EMPTY:{path}")

    arities = Counter()
    coords: dict[int, list[float]] = defaultdict(list)
    for index, point in enumerate(value):
        if not isinstance(point, list) or len(point) not in (2, 3):
            raise StageBError(f"SYNCPOINT_ARITY_INVALID:{path}:{index}")
        arities[len(point)] += 1
        for coord_index, raw in enumerate(point):
            coords[coord_index].append(
                _finite_number(raw, f"SYNCPOINT_{index}_COORD_{coord_index}")
            )

    second = coords[1]
    nondecreasing = all(a <= b for a, b in zip(second, second[1:]))
    return {
        "sha256": sha256_file(path),
        "pointCount": len(value),
        "arityCounts": {str(key): count for key, count in sorted(arities.items())},
        "coordinateRanges": {
            str(key): {"min": min(values), "max": max(values)}
            for key, values in sorted(coords.items())
        },
        "secondCoordinateNondecreasing": nondecreasing,
    }


def _read_varlen(data: bytes, pos: int, limit: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= limit:
            raise StageBError("MIDI_TRUNCATED_VARLEN")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, pos
    raise StageBError("MIDI_VARLEN_TOO_LONG")


def _parse_track(track: bytes, track_index: int) -> tuple[list[dict], list[dict]]:
    pos = 0
    tick = 0
    running_status: int | None = None
    event_order = 0
    note_messages: list[dict] = []
    tempos: list[dict] = []

    while pos < len(track):
        delta, pos = _read_varlen(track, pos, len(track))
        tick += delta
        if pos >= len(track):
            raise StageBError(f"MIDI_TRACK_TRUNCATED_AFTER_DELTA:{track_index}")

        first = track[pos]
        if first & 0x80:
            status = first
            pos += 1
            first_data: int | None = None
        else:
            if running_status is None:
                raise StageBError(f"MIDI_RUNNING_STATUS_WITHOUT_STATUS:{track_index}")
            status = running_status
            first_data = first
            pos += 1

        event_order += 1

        if status == 0xFF:
            if pos >= len(track):
                raise StageBError("MIDI_META_TYPE_TRUNCATED")
            meta_type = track[pos]
            pos += 1
            length, pos = _read_varlen(track, pos, len(track))
            end = pos + length
            if end > len(track):
                raise StageBError("MIDI_META_PAYLOAD_TRUNCATED")
            payload = track[pos:end]
            pos = end
            if meta_type == 0x51:
                if len(payload) != 3:
                    raise StageBError("MIDI_TEMPO_LENGTH_INVALID")
                tempo = int.from_bytes(payload, "big")
                if tempo <= 0:
                    raise StageBError("MIDI_TEMPO_NONPOSITIVE")
                tempos.append({
                    "tick": tick,
                    "tempoUsPerQuarter": tempo,
                    "trackIndex": track_index,
                    "eventOrder": event_order,
                })
            continue

        if status in (0xF0, 0xF7):
            length, pos = _read_varlen(track, pos, len(track))
            end = pos + length
            if end > len(track):
                raise StageBError("MIDI_SYSEX_PAYLOAD_TRUNCATED")
            pos = end
            continue

        if status >= 0xF0:
            raise StageBError(f"MIDI_UNSUPPORTED_SYSTEM_STATUS:{status:02x}")

        running_status = status
        kind = status & 0xF0
        channel = status & 0x0F
        data_len = 1 if kind in (0xC0, 0xD0) else 2
        values: list[int] = []
        if first_data is not None:
            values.append(first_data)
        while len(values) < data_len:
            if pos >= len(track):
                raise StageBError("MIDI_CHANNEL_PAYLOAD_TRUNCATED")
            byte = track[pos]
            pos += 1
            if byte & 0x80:
                raise StageBError("MIDI_CHANNEL_DATA_STATUS_BIT_SET")
            values.append(byte)

        if kind in (0x80, 0x90):
            note = int(values[0])
            velocity = int(values[1])
            is_on = kind == 0x90 and velocity > 0
            note_messages.append({
                "tick": tick,
                "trackIndex": track_index,
                "eventOrder": event_order,
                "channel": channel,
                "midi": note,
                "isOn": is_on,
                "velocity": velocity,
            })

    return note_messages, tempos


def _tempo_map(tempos: list[dict], ppq: int) -> tuple[list[dict], callable]:
    by_tick: dict[int, set[int]] = defaultdict(set)
    for row in tempos:
        by_tick[int(row["tick"])].add(int(row["tempoUsPerQuarter"]))
    for tick, values in by_tick.items():
        if len(values) != 1:
            raise StageBError(f"MIDI_CONFLICTING_TEMPO_AT_TICK:{tick}:{sorted(values)}")

    changes = [(tick, next(iter(values))) for tick, values in sorted(by_tick.items())]
    if not changes or changes[0][0] != 0:
        changes.insert(0, (0, DEFAULT_TEMPO_US_PER_QUARTER))

    segments = []
    current_tick = 0
    current_seconds = 0.0
    current_tempo = changes[0][1]
    if changes[0][0] != 0:
        raise StageBError("INTERNAL_TEMPO_MAP_START_ERROR")
    segments.append({"tick": 0, "seconds": 0.0, "tempoUsPerQuarter": current_tempo})

    for tick, tempo in changes[1:]:
        if tick < current_tick:
            raise StageBError("TEMPO_TICKS_NOT_SORTED")
        current_seconds += (
            float(tick - current_tick) * float(current_tempo) / 1_000_000.0 / float(ppq)
        )
        current_tick = tick
        current_tempo = tempo
        segments.append({
            "tick": tick,
            "seconds": current_seconds,
            "tempoUsPerQuarter": tempo,
        })

    def tick_to_seconds(target_tick: int) -> float:
        selected = segments[0]
        for segment in segments[1:]:
            if segment["tick"] > target_tick:
                break
            selected = segment
        return float(selected["seconds"]) + (
            float(target_tick - int(selected["tick"]))
            * float(selected["tempoUsPerQuarter"])
            / 1_000_000.0
            / float(ppq)
        )

    return segments, tick_to_seconds


def inspect_reference_midi(path: Path, stem: str) -> dict:
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        raise StageBError(f"MIDI_HEADER_INVALID:{path}")
    header_length = struct.unpack(">I", data[4:8])[0]
    if header_length != 6:
        raise StageBError(f"MIDI_HEADER_LENGTH_CHANGED:{path}:{header_length}")
    midi_format, track_count, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise StageBError(f"MIDI_SMPTE_DIVISION_NOT_AUTHORIZED:{path}")
    ppq = int(division)
    if ppq <= 0:
        raise StageBError(f"MIDI_PPQ_NONPOSITIVE:{path}")
    if midi_format not in (0, 1):
        raise StageBError(f"MIDI_FORMAT_NOT_AUTHORIZED:{path}:{midi_format}")

    pos = 14
    note_messages: list[dict] = []
    tempos: list[dict] = []
    for track_index in range(int(track_count)):
        if pos + 8 > len(data) or data[pos : pos + 4] != b"MTrk":
            raise StageBError(f"MIDI_TRACK_HEADER_INVALID:{path}:{track_index}")
        length = struct.unpack(">I", data[pos + 4 : pos + 8])[0]
        pos += 8
        end = pos + length
        if end > len(data):
            raise StageBError(f"MIDI_TRACK_LENGTH_TRUNCATED:{path}:{track_index}")
        notes_part, tempos_part = _parse_track(data[pos:end], track_index)
        note_messages.extend(notes_part)
        tempos.extend(tempos_part)
        pos = end
    if pos != len(data):
        raise StageBError(f"MIDI_TRAILING_BYTES:{path}:{len(data)-pos}")

    tempo_segments, tick_to_seconds = _tempo_map(tempos, ppq)
    messages = sorted(
        note_messages,
        key=lambda row: (row["tick"], row["trackIndex"], row["eventOrder"]),
    )
    active: dict[tuple[int, int], deque[dict]] = defaultdict(deque)
    paired = []
    overlap_count = 0
    channels = set()
    for message in messages:
        key = (int(message["channel"]), int(message["midi"]))
        channels.add(key[0])
        if message["isOn"]:
            if active[key]:
                overlap_count += 1
            active[key].append(message)
        else:
            if not active[key]:
                raise StageBError(f"MIDI_UNMATCHED_NOTE_OFF:{path}:{key}:{message['tick']}")
            onset = active[key].popleft()
            if int(message["tick"]) < int(onset["tick"]):
                raise StageBError("MIDI_NOTE_OFFSET_BEFORE_ONSET")
            paired.append({
                "channel": key[0],
                "midi": key[1],
                "onsetTick": int(onset["tick"]),
                "offsetTick": int(message["tick"]),
                "onsetTrackIndex": int(onset["trackIndex"]),
                "onsetEventOrder": int(onset["eventOrder"]),
            })

    leftovers = [key for key, queue in active.items() if queue]
    if leftovers:
        raise StageBError(f"MIDI_UNMATCHED_NOTE_ON:{path}:{leftovers[:8]}")

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
            raise StageBError("MIDI_CONVERTED_TIME_NONFINITE")
        if onset_seconds < 0.0 or offset_seconds < onset_seconds:
            raise StageBError("MIDI_CONVERTED_TIME_INVALID")
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

    notes = [row["midi"] for row in identities]
    onsets = [row["onsetSeconds"] for row in identities]
    offsets = [row["offsetSeconds"] for row in identities]
    durations = [b - a for a, b in zip(onsets, offsets)]
    tempo_values = sorted({int(row["tempoUsPerQuarter"]) for row in tempo_segments})

    return {
        "sha256": sha256_bytes(data),
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
        "referenceEventIdentitySha256": sha256_bytes(canonical_json(identities).encode("utf-8")),
        "_identities": identities,
    }


def build_stage_b(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise StageBError("DATASET_ROOT_DIRECTORY_REQUIRED")
    git_identity = verify_dataset_git(root)
    rows, metadata = _read_metadata(root)
    _verify_exact_canonical_membership(root, rows)

    population_rows = []
    global_reference_identities = []
    ppq_counts = Counter()
    track_count_counts = Counter()
    format_counts = Counter()
    sync_arity_counts = Counter()
    total_events = 0
    total_overlap = 0
    all_midis = []
    all_onsets = []
    all_offsets = []
    all_durations = []
    tempo_domain = set()
    channel_domain = set()

    for row in rows:
        audio_path = root / row["audioPath"]
        midi_path = root / row["midiPath"]
        sync_path = root / row["syncpointPath"]
        for label, path in (("AUDIO", audio_path), ("MIDI", midi_path), ("SYNCPOINT", sync_path)):
            if not path.is_file():
                raise StageBError(f"{label}_FILE_MISSING:{path.relative_to(root).as_posix()}")
            if path.is_symlink():
                raise StageBError(f"{label}_SYMLINK_NOT_AUTHORIZED:{path.relative_to(root).as_posix()}")

        sync = inspect_syncpoints(sync_path)
        midi = inspect_reference_midi(midi_path, row["stem"])
        identities = midi.pop("_identities")
        global_reference_identities.extend(identities)

        for arity, count in sync["arityCounts"].items():
            sync_arity_counts[arity] += int(count)
        ppq_counts[str(midi["ticksPerQuarter"])] += 1
        track_count_counts[str(midi["trackCount"])] += 1
        format_counts[str(midi["format"])] += 1
        total_events += int(midi["referenceEventCount"])
        total_overlap += int(midi["sameKeyOverlapCount"])
        tempo_domain.update(midi["tempoUsPerQuarterDomain"])
        channel_domain.update(midi["channelDomain"])
        if midi["midiMin"] is not None:
            all_midis.extend((int(midi["midiMin"]), int(midi["midiMax"])))
            all_onsets.extend((float(midi["onsetMinSeconds"]), float(midi["onsetMaxSeconds"])))
            all_offsets.extend((float(midi["offsetMinSeconds"]), float(midi["offsetMaxSeconds"])))
            all_durations.extend((float(midi["durationMinSeconds"]), float(midi["durationMaxSeconds"])))

        population_rows.append({
            "rowIndex": row["rowIndex"],
            "stem": row["stem"],
            "split": row["split"],
            "guitarType": row["guitar_type"],
            "sliceId": row["slice_id"],
            "artist": row["artist"],
            "name": row["name"],
            "audio": {
                "path": row["audioPath"],
                "sha256": sha256_file(audio_path),
                "sizeBytes": int(audio_path.stat().st_size),
            },
            "midi": {"path": row["midiPath"], **midi},
            "syncpoints": {"path": row["syncpointPath"], **sync},
        })

    population_identity = [
        {
            "rowIndex": row["rowIndex"],
            "stem": row["stem"],
            "split": row["split"],
            "guitarType": row["guitarType"],
            "audioPath": row["audio"]["path"],
            "audioSha256": row["audio"]["sha256"],
            "midiPath": row["midi"]["path"],
            "midiSha256": row["midi"]["sha256"],
            "syncpointPath": row["syncpoints"]["path"],
            "syncpointSha256": row["syncpoints"]["sha256"],
        }
        for row in population_rows
    ]

    if len(global_reference_identities) != total_events:
        raise StageBError("REFERENCE_IDENTITY_COUNT_MISMATCH")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "dataset": {
            "name": "Francois Leduc Guitar Dataset",
            "expectedOriginCanonical": EXPECTED_ORIGIN_CANONICAL,
            "expectedRevision": EXPECTED_REVISION,
            "git": git_identity,
            "selectedReleaseLicenseDeclaration": "MIT",
            "stageAReportSha256": EXPECTED_STAGE_A_REPORT_SHA256,
            "metadataSha256": EXPECTED_METADATA_SHA256,
        },
        "metadata": metadata,
        "summary": {
            "includedPerformanceCount": len(population_rows),
            "splitCounts": metadata["splitCounts"],
            "guitarTypeCounts": metadata["guitarTypeCounts"],
            "referenceEventCount": total_events,
            "midiMin": min(all_midis) if all_midis else None,
            "midiMax": max(all_midis) if all_midis else None,
            "onsetMinSeconds": min(all_onsets) if all_onsets else None,
            "onsetMaxSeconds": max(all_onsets) if all_onsets else None,
            "offsetMinSeconds": min(all_offsets) if all_offsets else None,
            "offsetMaxSeconds": max(all_offsets) if all_offsets else None,
            "durationMinSeconds": min(all_durations) if all_durations else None,
            "durationMaxSeconds": max(all_durations) if all_durations else None,
            "sameKeyOverlapCount": total_overlap,
            "midiFormatCounts": dict(sorted(format_counts.items())),
            "trackCountCounts": dict(sorted(track_count_counts.items())),
            "ticksPerQuarterCounts": dict(sorted(ppq_counts.items())),
            "tempoUsPerQuarterDomain": sorted(tempo_domain),
            "channelDomain": sorted(channel_domain),
            "syncpointArityCounts": dict(sorted(sync_arity_counts.items())),
        },
        "includedPopulationSha256": sha256_bytes(
            canonical_json(population_identity).encode("utf-8")
        ),
        "referenceEventIdentitySha256": sha256_bytes(
            canonical_json(global_reference_identities).encode("utf-8")
        ),
        "included": population_rows,
        "policyBoundary": dict(POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output).resolve()
    if output.exists():
        raise StageBError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = build_stage_b(Path(args.dataset_root))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "summary": result["summary"],
        "includedPopulationSha256": result["includedPopulationSha256"],
        "referenceEventIdentitySha256": result["referenceEventIdentitySha256"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StageBError as exc:
        print(f"FLGD_V5_STAGE_B_ERROR:{exc}")
        raise SystemExit(2)
