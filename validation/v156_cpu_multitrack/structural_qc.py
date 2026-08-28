#!/usr/bin/env python3
"""Independent reference-blind structural QC for the single V156 candidate."""
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
EXPECTED_PREREG_GIT_BLOB = "bbad04a6f2076cde2ec2a266ec321c151d9b5868"
EXPECTED_ENGINE_BLOB = "3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8"
CANDIDATE_SCHEMA = "dadrock.tabs.v156.cpu-hybrid-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v156.cpu-hybrid-generation-receipt.v1"
QC_SCHEMA = "dadrock.tabs.v156.reference-blind-structural-qc.v1"
RANGES = {"combinedGuitar": (40, 88), "bass": (28, 67)}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def finite_number(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v))


def fail(msg: str) -> None:
    raise RuntimeError(f"V156 structural QC failure: {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--pre-run-receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        fail("QC output is write-once")
    for p in (args.candidate, args.receipt, args.preregistration, args.pre_run_receipt):
        if not p.is_file():
            fail(f"missing input {p}")

    candidate = json.loads(args.candidate.read_text())
    receipt = json.loads(args.receipt.read_text())
    prereg = json.loads(args.preregistration.read_text())
    pre_run = json.loads(args.pre_run_receipt.read_text())

    if candidate.get("schema") != CANDIDATE_SCHEMA:
        fail("candidate schema")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        fail("generation receipt schema")
    if receipt.get("validation") != "PENDING_INDEPENDENT_STRUCTURAL_QC":
        fail("unexpected pre-QC receipt state")
    if prereg.get("status") != "PREREGISTERED_BEFORE_GENERATION" or prereg.get("version") != "V156":
        fail("preregistration identity/status")
    contract = prereg.get("canonicalContract") or {}
    if contract.get("candidateSchema") != CANDIDATE_SCHEMA or contract.get("generationReceiptSchema") != RECEIPT_SCHEMA or contract.get("structuralQcSchema") != QC_SCHEMA:
        fail("canonical schema contract drift")
    if git_blob_sha(args.preregistration) != EXPECTED_PREREG_GIT_BLOB:
        fail("preregistration Git blob drift")

    if pre_run.get("validation") != "PASS" or pre_run.get("version") != "V156":
        fail("pre-run receipt state")
    trigger = pre_run.get("triggerSafety") or {}
    if trigger.get("workflowCreationIsSingleTrigger") is not True or trigger.get("secondArmEditForbidden") is not True:
        fail("trigger-safety pre-run contract")
    pins = pre_run.get("pinnedGitBlobs") or {}
    if pins.get("preregistration") != EXPECTED_PREREG_GIT_BLOB or pins.get("inheritedReferenceBlindEngine") != EXPECTED_ENGINE_BLOB:
        fail("pre-run prereg/engine pin drift")

    if receipt.get("candidateSha256") != sha256(args.candidate):
        fail("candidate SHA receipt mismatch")
    if receipt.get("preregistrationSha256") != sha256(args.preregistration):
        fail("preregistration SHA receipt mismatch")
    if receipt.get("implementation", {}).get("inheritedReferenceBlindEngineGitBlob") != EXPECTED_ENGINE_BLOB:
        fail("engine identity in generation receipt")

    safety = candidate.get("safety") or {}
    required_false = ["referenceRead", "humanCorrection", "referenceGuidedFiltering", "thresholdSweep", "variantSelection", "modalUsed", "cudaGpuUsed", "mainOrProductionModified"]
    for key in required_false:
        if safety.get(key) is not False:
            fail(f"candidate safety {key}")
    if safety.get("professionalReferencePathsOpened") != 0 or safety.get("referenceFacingScoreCalls") != 0:
        fail("candidate reference-access counters")
    rsafety = receipt.get("safety") or {}
    for key in required_false:
        if rsafety.get(key) is not False:
            fail(f"receipt safety {key}")
    if rsafety.get("professionalReferencePathsOpened") != 0 or rsafety.get("referenceFacingScoreCalls") != 0:
        fail("receipt reference-access counters")

    env = receipt.get("environment") or {}
    if env.get("validation") != "PASS":
        fail("environment receipt embedded state")
    versions = env.get("versions") or {}
    for package, expected in EXPECTED_DEPS.items():
        if str(versions.get(package)) != expected:
            fail(f"dependency drift {package}: {versions.get(package)!r} != {expected!r}")
    if str(versions.get("torch")) != "2.8.0+cpu":
        fail(f"torch drift: {versions.get('torch')!r}")
    if env.get("device") != "cpu" or env.get("cudaAvailable") is not False or env.get("torchCudaVersion") is not None:
        fail("environment is not confirmed CPU-only")
    if env.get("demucsModel") != "htdemucs_6s" or env.get("demucsShifts") != 1 or env.get("demucsJobs") != 1:
        fail("Demucs contract drift")
    checkpoints = env.get("demucsModelCheckpointFiles")
    if not isinstance(checkpoints, list) or not checkpoints:
        fail("missing Demucs model checkpoint receipt")
    for item in checkpoints:
        if not isinstance(item, dict) or not item.get("path") or not item.get("sha256") or not isinstance(item.get("bytes"), int) or item["bytes"] <= 0:
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
            for field in contract.get("eventRequiredFields", []):
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
    for field in contract.get("timebaseRequiredFields", []):
        if field not in tb:
            fail(f"timebase missing {field}")
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
        "schema": QC_SCHEMA,
        "validation": "PASS",
        "candidatePath": str(args.candidate),
        "candidateSha256": sha256(args.candidate),
        "generationReceiptPath": str(args.receipt),
        "generationReceiptSha256": sha256(args.receipt),
        "preregistrationPath": str(args.preregistration),
        "preregistrationGitBlob": git_blob_sha(args.preregistration),
        "preRunReceiptPath": str(args.pre_run_receipt),
        "preRunReceiptSha256": sha256(args.pre_run_receipt),
        "streamStats": stream_stats,
        "timebaseQc": tb.get("qc"),
        "environmentIdentity": {
            "demucsModel": env.get("demucsModel"),
            "demucsModelCheckpointFiles": checkpoints,
            "versions": versions,
        },
        "safety": {
            "referenceRead": False,
            "professionalQualityMetricUsed": False,
            "humanCorrection": False,
            "thresholdSweep": False,
            "variantSelection": False,
            "gpuUsed": False,
            "mainOrProductionModified": False,
            "referenceFacingScoreCalls": 0,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
