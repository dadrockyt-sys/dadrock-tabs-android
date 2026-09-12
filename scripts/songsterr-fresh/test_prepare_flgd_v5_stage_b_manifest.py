#!/usr/bin/env python3
"""Controlled synthetic contract test for FLGD V5 Stage B manifest parsing."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import subprocess
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("prepare_flgd_v5_stage_b_manifest.py")
spec = importlib.util.spec_from_file_location("flgd_stage_b", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def run(*args: str, cwd: Path) -> str:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def varlen(value: int) -> bytes:
    assert value >= 0
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buffer))


def track(payload: bytes) -> bytes:
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def midi_format1_running_status() -> bytes:
    # Track 0: 120 BPM at tick 0, 150 BPM at tick 480.
    t0 = bytearray()
    t0 += varlen(0) + b"\xff\x51\x03" + (500000).to_bytes(3, "big")
    t0 += varlen(480) + b"\xff\x51\x03" + (400000).to_bytes(3, "big")
    t0 += varlen(0) + b"\xff\x2f\x00"

    # Track 1: two notes; after the first status byte, running status is used.
    t1 = bytearray()
    t1 += varlen(0) + bytes([0x90, 60, 100])
    t1 += varlen(120) + bytes([64, 90])
    t1 += varlen(120) + bytes([60, 0])
    t1 += varlen(120) + bytes([64, 0])
    t1 += varlen(0) + b"\xff\x2f\x00"

    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, 480)
    return header + track(bytes(t0)) + track(bytes(t1))


def midi_format0_default_tempo_overlap() -> bytes:
    # No tempo meta event: standard default tempo must apply.
    t = bytearray()
    t += varlen(0) + bytes([0x91, 67, 100])
    t += varlen(60) + bytes([0x91, 67, 90])
    t += varlen(60) + bytes([0x81, 67, 0])
    t += varlen(60) + bytes([0x81, 67, 0])
    t += varlen(0) + b"\xff\x2f\x00"
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, 240)
    return header + track(bytes(t))


def midi_unmatched_off() -> bytes:
    t = varlen(0) + bytes([0x80, 60, 0]) + varlen(0) + b"\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, 480) + track(t)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expect_stage_b_error(fn, contains: str) -> None:
    try:
        fn()
    except m.StageBError as exc:
        assert contains in str(exc), (contains, str(exc))
    else:
        raise AssertionError(f"expected StageBError containing {contains}")


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "dataset"
        root.mkdir()
        for name in ("audio", "midi", "syncpoints", "test_set/model_output_ymt3"):
            (root / name).mkdir(parents=True, exist_ok=True)

        (root / "audio/a.mp3").write_bytes(b"synthetic-audio-a")
        (root / "audio/b.mp3").write_bytes(b"synthetic-audio-b")
        (root / "midi/a.mid").write_bytes(midi_format1_running_status())
        (root / "midi/b.mid").write_bytes(midi_format0_default_tempo_overlap())
        (root / "syncpoints/a-syncpoints.json").write_text(
            json.dumps([[0, 0.1, 0], [0, 0.6, 240], [1, 1.1, 0]]), encoding="utf-8"
        )
        (root / "syncpoints/b-syncpoints.json").write_text(
            json.dumps([[0, 0.2], [0, 0.7, 120], [1, 1.2, 0]]), encoding="utf-8"
        )
        # This deliberately exists but must never enter the canonical population.
        (root / "test_set/model_output_ymt3/forbidden.mid").write_bytes(midi_unmatched_off())

        metadata = root / "metadata.csv"
        with metadata.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=m.EXPECTED_METADATA_COLUMNS)
            writer.writeheader()
            writer.writerow({
                "split": "train",
                "midi_filename": "a.mid",
                "audio_filename": "a.mp3",
                "guitar_type": "acoustic",
                "slice_id": "a",
                "artist": "artist-a",
                "name": "piece-a",
            })
            writer.writerow({
                "split": "test",
                "midi_filename": "midi/b.mid",
                "audio_filename": "audio/b.mp3",
                "guitar_type": "electric",
                "slice_id": "b",
                "artist": "artist-b",
                "name": "piece-b",
            })

        run("git", "init", cwd=root)
        run("git", "config", "user.email", "ci@example.invalid", cwd=root)
        run("git", "config", "user.name", "CI", cwd=root)
        run("git", "remote", "add", "origin", m.EXPECTED_ORIGIN_CANONICAL, cwd=root)
        run("git", "add", ".", cwd=root)
        run("git", "commit", "-m", "synthetic", cwd=root)
        head = run("git", "rev-parse", "HEAD", cwd=root)

        # Test-only bindings; production source constants remain exact FLGD values.
        original_revision = m.EXPECTED_REVISION
        original_metadata_sha = m.EXPECTED_METADATA_SHA256
        original_row_count = m.EXPECTED_ROW_COUNT
        m.EXPECTED_REVISION = head
        m.EXPECTED_METADATA_SHA256 = sha(metadata)
        m.EXPECTED_ROW_COUNT = 2

        result = m.build_stage_b(root)
        assert result["summary"]["includedPerformanceCount"] == 2
        assert result["summary"]["splitCounts"] == {"test": 1, "train": 1}
        assert result["summary"]["guitarTypeCounts"] == {"acoustic": 1, "electric": 1}
        assert result["summary"]["referenceEventCount"] == 4
        assert result["summary"]["sameKeyOverlapCount"] == 1
        assert result["summary"]["midiFormatCounts"] == {"0": 1, "1": 1}
        assert result["summary"]["ticksPerQuarterCounts"] == {"240": 1, "480": 1}
        assert result["summary"]["syncpointArityCounts"] == {"2": 1, "3": 5}
        assert result["summary"]["midiMin"] == 60
        assert result["summary"]["midiMax"] == 67
        assert result["policyBoundary"] == m.POLICY_BOUNDARY
        assert len(result["includedPopulationSha256"]) == 64
        assert len(result["referenceEventIdentitySha256"]) == 64
        assert all(not row["audio"]["path"].startswith("test_set/") for row in result["included"])
        assert all(not row["midi"]["path"].startswith("test_set/") for row in result["included"])

        # Verify the 480-PPQ file's exact standard timing under 500,000 us/qn.
        a = next(row for row in result["included"] if row["stem"] == "a")
        assert a["midi"]["referenceEventCount"] == 2
        assert abs(a["midi"]["onsetMinSeconds"] - 0.0) < 1e-12
        assert abs(a["midi"]["onsetMaxSeconds"] - 0.125) < 1e-12
        assert abs(a["midi"]["offsetMaxSeconds"] - 0.375) < 1e-12

        # Clean-worktree and origin guards.
        (root / "untracked.tmp").write_text("x", encoding="utf-8")
        expect_stage_b_error(lambda: m.verify_dataset_git(root), "DATASET_WORKTREE_MUST_BE_CLEAN")
        (root / "untracked.tmp").unlink()
        run("git", "remote", "set-url", "origin", "https://example.invalid/wrong", cwd=root)
        expect_stage_b_error(lambda: m.verify_dataset_git(root), "DATASET_ORIGIN_CHANGED")
        run("git", "remote", "set-url", "origin", m.EXPECTED_ORIGIN_CANONICAL, cwd=root)

        # Malformed canonical MIDI must fail closed; commit the corruption so Git is clean.
        (root / "midi/b.mid").write_bytes(midi_unmatched_off())
        run("git", "add", "midi/b.mid", cwd=root)
        run("git", "commit", "-m", "malformed midi", cwd=root)
        m.EXPECTED_REVISION = run("git", "rev-parse", "HEAD", cwd=root)
        expect_stage_b_error(lambda: m.build_stage_b(root), "MIDI_UNMATCHED_NOTE_OFF")

        # Restore module constants before final source-constant assertions.
        m.EXPECTED_REVISION = original_revision
        m.EXPECTED_METADATA_SHA256 = original_metadata_sha
        m.EXPECTED_ROW_COUNT = original_row_count
        assert m.EXPECTED_REVISION == "a38306c244b3ea81496ad58b4514622185e58211"
        assert m.EXPECTED_METADATA_SHA256 == "05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b"
        assert m.EXPECTED_ROW_COUNT == 79

    print("FLGD_V5_STAGE_B_SYNTHETIC_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
