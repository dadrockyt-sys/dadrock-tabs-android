#!/usr/bin/env python3
"""Inventory-only FLGD V5 external-validation candidate.

No model inference, no V5 classification, no audio-sample pitch analysis, and no
correctness scoring are authorized here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import struct
import subprocess
import wave
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-flgd-v5-inventory-v1"
VERSION = 1
EXPECTED_REPOSITORY = "xavriley/FrancoisLeducGuitarDataset"
EXPECTED_ORIGIN_CANONICAL = "https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset"
EXPECTED_REVISION = "a38306c244b3ea81496ad58b4514622185e58211"
AUDIO_EXTENSIONS = {".wav", ".flac", ".mp3", ".ogg", ".m4a", ".aiff", ".aif"}
MIDI_EXTENSIONS = {".mid", ".midi"}


class InventoryError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


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
        raise InventoryError(f"GIT_COMMAND_FAILED:{' '.join(args)}:{proc.stderr.strip()}")
    return proc.stdout.strip()


def normalize_origin_url(value: str) -> str:
    normalized = str(value).strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    return normalized


def verify_git_revision(root: Path) -> dict:
    if not (root / ".git").exists():
        raise InventoryError("DATASET_GIT_CHECKOUT_REQUIRED")
    head = git_output(root, "rev-parse", "HEAD")
    if head != EXPECTED_REVISION:
        raise InventoryError(f"DATASET_REVISION_CHANGED:{head}!={EXPECTED_REVISION}")
    status = git_output(root, "status", "--porcelain")
    if status:
        raise InventoryError("DATASET_WORKTREE_MUST_BE_CLEAN")
    remote = git_output(root, "remote", "get-url", "origin")
    normalized_remote = normalize_origin_url(remote)
    if normalized_remote != EXPECTED_ORIGIN_CANONICAL:
        raise InventoryError(
            f"DATASET_ORIGIN_CHANGED:{normalized_remote}!={EXPECTED_ORIGIN_CANONICAL}"
        )
    return {
        "headSha": head,
        "originUrl": remote,
        "originCanonical": normalized_remote,
        "worktreeClean": True,
    }


def relative_regular_files(root: Path) -> list[Path]:
    rows: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d != ".git")
        current_path = Path(current)
        for name in sorted(files):
            path = current_path / name
            if path.is_symlink():
                raise InventoryError(f"SYMLINK_NOT_AUTHORIZED:{path.relative_to(root).as_posix()}")
            if path.is_file():
                rows.append(path)
    rows.sort(key=lambda p: p.relative_to(root).as_posix())
    return rows


def inspect_wav(path: Path) -> dict:
    try:
        with wave.open(str(path), "rb") as handle:
            return {
                "channels": int(handle.getnchannels()),
                "sampleWidthBytes": int(handle.getsampwidth()),
                "sampleRate": int(handle.getframerate()),
                "frameCount": int(handle.getnframes()),
                "compressionType": str(handle.getcomptype()),
            }
    except (wave.Error, EOFError) as exc:
        raise InventoryError(f"WAV_HEADER_INVALID:{path}:{exc}") from exc


def inspect_midi_header(path: Path) -> dict:
    with path.open("rb") as handle:
        header = handle.read(14)
    if len(header) < 14 or header[:4] != b"MThd":
        raise InventoryError(f"MIDI_HEADER_INVALID:{path}")
    header_length = struct.unpack(">I", header[4:8])[0]
    if header_length != 6:
        raise InventoryError(f"MIDI_HEADER_LENGTH_CHANGED:{path}:{header_length}")
    midi_format, track_count, division = struct.unpack(">HHH", header[8:14])
    return {
        "format": int(midi_format),
        "trackCount": int(track_count),
        "divisionRaw": int(division),
        "usesSmpteDivision": bool(division & 0x8000),
        "ticksPerQuarterIfMetric": None if (division & 0x8000) else int(division),
    }


def inspect_metadata(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InventoryError("METADATA_HEADER_REQUIRED")
        fields = [str(x) for x in reader.fieldnames]
        row_count = 0
        domains: dict[str, set[str]] = {field: set() for field in fields}
        for row in reader:
            row_count += 1
            for field in fields:
                value = row.get(field)
                if value is not None and len(domains[field]) < 256:
                    domains[field].add(str(value))
    return {
        "sha256": sha256_file(path),
        "columns": fields,
        "rowCount": row_count,
        "valueDomainsCapped256": {
            field: sorted(values) for field, values in domains.items()
        },
    }


def build_pairing(file_rows: list[dict]) -> dict:
    audio_by_stem: dict[str, list[dict]] = defaultdict(list)
    midi_by_stem: dict[str, list[dict]] = defaultdict(list)
    for row in file_rows:
        parts = row["path"].split("/")
        if len(parts) < 2:
            continue
        top = parts[0]
        stem = Path(parts[-1]).stem
        ext = row["extension"]
        if top == "audio" and ext in AUDIO_EXTENSIONS:
            audio_by_stem[stem].append(row)
        elif top == "midi" and ext in MIDI_EXTENSIONS:
            midi_by_stem[stem].append(row)

    stems = sorted(set(audio_by_stem) | set(midi_by_stem))
    pairs = []
    unpaired_audio = []
    unpaired_midi = []
    ambiguous = []
    for stem in stems:
        audio = audio_by_stem.get(stem, [])
        midi = midi_by_stem.get(stem, [])
        if len(audio) == 1 and len(midi) == 1:
            pairs.append({
                "stem": stem,
                "audio": audio[0]["path"],
                "audioSha256": audio[0]["sha256"],
                "midi": midi[0]["path"],
                "midiSha256": midi[0]["sha256"],
            })
        elif len(audio) > 1 or len(midi) > 1:
            ambiguous.append({
                "stem": stem,
                "audio": [x["path"] for x in audio],
                "midi": [x["path"] for x in midi],
            })
        else:
            if audio:
                unpaired_audio.extend(x["path"] for x in audio)
            if midi:
                unpaired_midi.extend(x["path"] for x in midi)

    return {
        "exactOneToOnePairs": pairs,
        "unpairedAudio": sorted(unpaired_audio),
        "unpairedMidi": sorted(unpaired_midi),
        "ambiguousStemGroups": ambiguous,
    }


def inventory(root: Path) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise InventoryError("DATASET_ROOT_DIRECTORY_REQUIRED")
    git_identity = verify_git_revision(root)

    paths = relative_regular_files(root)
    file_rows = []
    extension_counts = Counter()
    total_bytes = 0
    wav_headers = Counter()
    midi_headers = Counter()

    for path in paths:
        rel = path.relative_to(root).as_posix()
        ext = path.suffix.lower()
        size = int(path.stat().st_size)
        row = {
            "path": rel,
            "sizeBytes": size,
            "extension": ext,
            "sha256": sha256_file(path),
        }
        total_bytes += size
        extension_counts[ext or "<none>"] += 1

        if ext == ".wav":
            header = inspect_wav(path)
            row["wavHeader"] = header
            wav_headers[canonical_json(header)] += 1
        if ext in MIDI_EXTENSIONS:
            header = inspect_midi_header(path)
            row["midiHeader"] = header
            midi_headers[canonical_json(header)] += 1
        file_rows.append(row)

    pairing = build_pairing(file_rows)
    metadata_path = root / "metadata.csv"
    metadata = inspect_metadata(metadata_path) if metadata_path.is_file() else None

    audio_rows = [
        row for row in file_rows
        if row["path"].split("/", 1)[0] == "audio" and row["extension"] in AUDIO_EXTENSIONS
    ]
    midi_rows = [
        row for row in file_rows
        if row["path"].split("/", 1)[0] == "midi" and row["extension"] in MIDI_EXTENSIONS
    ]

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "dataset": {
            "name": "Francois Leduc Guitar Dataset",
            "repository": EXPECTED_REPOSITORY,
            "expectedOriginCanonical": EXPECTED_ORIGIN_CANONICAL,
            "expectedRevision": EXPECTED_REVISION,
            "git": git_identity,
            "selectedReleaseLicenseDeclaration": "MIT",
        },
        "summary": {
            "regularFileCount": len(file_rows),
            "totalBytes": total_bytes,
            "extensionCounts": dict(sorted(extension_counts.items())),
            "audioFileCount": len(audio_rows),
            "midiFileCount": len(midi_rows),
            "exactOneToOnePairCount": len(pairing["exactOneToOnePairs"]),
            "unpairedAudioCount": len(pairing["unpairedAudio"]),
            "unpairedMidiCount": len(pairing["unpairedMidi"]),
            "ambiguousStemGroupCount": len(pairing["ambiguousStemGroups"]),
        },
        "wavHeaderSignatures": [
            {"header": json.loads(key), "count": count}
            for key, count in sorted(wav_headers.items())
        ],
        "midiHeaderSignatures": [
            {"header": json.loads(key), "count": count}
            for key, count in sorted(midi_headers.items())
        ],
        "metadata": metadata,
        "pairing": pairing,
        "files": file_rows,
        "policyBoundary": {
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
        },
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
        raise InventoryError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = inventory(Path(args.dataset_root))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "summary": result["summary"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
