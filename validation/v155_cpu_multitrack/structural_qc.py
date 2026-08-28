#!/usr/bin/env python3
"""Reference-blind structural QC for the single V155 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

EXPECTED_DEPS = {
    "numpy": "1.26.4",
    "scipy": "1.13.1",
    "librosa": "0.11.0",
    "soundfile": "0.12.1",
    "imageio-ffmpeg": "0.6.0",
    "demucs": "4.1.0",
    "basic-pitch": "0.4.0",
}
RANGES = {"combinedGuitar": (40, 88), "bass": (28, 67)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def fail(msg: str) -> None:
    raise RuntimeError(f"V155 structural QC failure: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        fail("QC output is write-once")

    candidate = json.loads(args.candidate.read_text())
    receipt = json.loads(args.receipt.read_text())
    prereg = json.loads(args.preregistration.read_text())
    if candidate.get("schema") != "dadrock.tabs.v155.cpu-hybrid-generated.v1":
        fail("candidate schema")
    if prereg.get("status") != "PREREGISTERED_BEFORE_GENERATION" or prereg.get("version") != "V155":
        fail("preregistration identity/status")
    if receipt.get("candidateSha256") != sha256(args.candidate):
        fail("candidate SHA receipt mismatch")
    if receipt.get("preregistrationSha256") != sha256(args.preregistration):
        fail("preregistration SHA receipt mismatch")

    safety = candidate.get("safety") or {}
    required_false = ["referenceRead", "humanCorrection", "referenceGuidedFiltering", "thresholdSweep", "modalUsed", "cudaGpuUsed"]
    for key in required_false:
        if safety.get(key) is not False:
            fail(f"candidate safety {key}")
    rsafety = receipt.get("safety") or {}
    for key in required_false + ["variantSelection", "mainOrProductionModified"]:
        if rsafety.get(key) is not False:
            fail(f"receipt safety {key}")

    env = receipt.get("environment") or {}
    versions = env.get("versions") or {}
    for package, expected in EXPECTED_DEPS.items():
        if str(versions.get(package)) != expected:
            fail(f"dependency drift {package}: {versions.get(package)!r} != {expected!r}")
    if env.get("device") != "cpu" or env.get("cudaAvailable") is not False or env.get("torchCudaVersion") is not None:
        fail("environment is not confirmed CPU-only")
    if env.get("demucsModel") != "htdemucs_6s":
        fail("Demucs model drift")
    checkpoints = env.get("demucsModelCheckpointFiles")
    if not isinstance(checkpoints, list) or not checkpoints:
        fail("missing Demucs model checkpoint receipt")
    for item in checkpoints:
        if not isinstance(item, dict) or not item.get("name") or not item.get("sha256") or not item.get("bytes"):
            fail("invalid Demucs checkpoint identity")

    streams = candidate.get("streams") or {}
    if set(streams) != {"combinedGuitar", "bass"}:
        fail("unexpected stream set")
    stream_stats = {}
    for stream, (lo, hi) in RANGES.items():
        rows = streams.get(stream)
        if not isinstance(rows, list) or not rows:
            fail(f"empty {stream} stream")
        seen = set()
        previous_sort = None
        sources = {}
        for idx, row in enumerate(rows):
            for field in ("measure", "step", "midi", "startSeconds", "rawGridStep", "absoluteGridStep", "source"):
                if field not in row:
                    fail(f"{stream}[{idx}] missing {field}")
            if not isinstance(row["measure"], int) or row["measure"] < 1:
                fail(f"{stream}[{idx}] invalid measure")
            if not isinstance(row["step"], int) or not 0 <= row["step"] <= 15:
                fail(f"{stream}[{idx}] invalid snapped step")
            if not isinstance(row["absoluteGridStep"], int) or row["absoluteGridStep"] < 0:
                fail(f"{stream}[{idx}] invalid absoluteGridStep")
            if row["measure"] != row["absoluteGridStep"] // 16 + 1 or row["step"] != row["absoluteGridStep"] % 16:
                fail(f"{stream}[{idx}] measure/step mismatch")
            if not finite_number(row["rawGridStep"]) or not finite_number(row["startSeconds"]) or float(row["startSeconds"]) < 0:
                fail(f"{stream}[{idx}] nonfinite timing")
            if not isinstance(row["midi"], int) or not lo <= row["midi"] <= hi:
                fail(f"{stream}[{idx}] MIDI range")
            if not isinstance(row["source"], str) or not row["source"]:
                fail(f"{stream}[{idx}] source")
            key = (row["measure"], row["step"], row["midi"])
            if key in seen:
                fail(f"{stream} duplicate scorer row {key}")
            seen.add(key)
            sort_key = (row["absoluteGridStep"], row["midi"], row["source"])
            if previous_sort is not None and sort_key < previous_sort:
                fail(f"{stream} output not in preregistered sort order")
            previous_sort = sort_key
            sources[row["source"]] = sources.get(row["source"], 0) + 1
        stream_stats[stream] = {
            "count": len(rows),
            "sources": sources,
            "midiMin": min(r["midi"] for r in rows),
            "midiMax": max(r["midi"] for r in rows),
        }

    tb = candidate.get("timebase") or {}
    beat_times = tb.get("beatTimesSeconds")
    beat_steps = tb.get("beatGridSteps")
    if not isinstance(beat_times, list) or len(beat_times) < 8 or not isinstance(beat_steps, list) or len(beat_steps) != len(beat_times):
        fail("invalid beat-grid arrays")
    if any(not finite_number(x) for x in beat_times + beat_steps):
        fail("nonfinite beat grid")
    if any(float(b) <= float(a) for a, b in zip(beat_times, beat_times[1:])):
        fail("beat times not strictly increasing")
    if tb.get("qc", {}).get("strictlyIncreasingBeatTimes") is not True:
        fail("timebase QC flag")

    report = {
        "schema": "dadrock.tabs.v155.reference-blind-structural-qc.v1",
        "validation": "PASS",
        "candidatePath": str(args.candidate),
        "candidateSha256": sha256(args.candidate),
        "generationReceiptPath": str(args.receipt),
        "generationReceiptSha256": sha256(args.receipt),
        "preregistrationPath": str(args.preregistration),
        "preregistrationSha256": sha256(args.preregistration),
        "streamStats": stream_stats,
        "timebaseQc": tb.get("qc"),
        "safety": {
            "referenceRead": False,
            "professionalQualityMetricUsed": False,
            "humanCorrection": False,
            "thresholdSweep": False,
            "variantSelection": False,
            "gpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
