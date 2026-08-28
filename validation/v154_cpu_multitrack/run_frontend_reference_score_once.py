#!/usr/bin/env python3
"""Guarded one-time V154 CPU reference-facing score.

This wrapper pins the exact frozen generated candidate, immutable professional
reference payload, and scorer identity. It invokes the frozen scorer exactly once,
then writes an immutable receipt. It never modifies or retunes the candidate.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json"
REF = ROOT / "research/v154-professional-references/scorer-ready/frontend-reference-payload.json"
SCORER = ROOT / "validation/v154_cpu_multitrack/score_frontend_reference.py"
OUT_DIR = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score"
SCORE = OUT_DIR / "score.json"
RECEIPT = OUT_DIR / "score-receipt.json"

EXPECTED_GEN_SHA256 = "1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37"
EXPECTED_REF_SHA256 = "b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7"
EXPECTED_SCORER_GIT_BLOB = "9644e65719fbd361a9b39778ae9950c5e983e855"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def require_identity() -> dict[str, str]:
    identities = {
        "generatedSha256": sha256(GEN),
        "referenceSha256": sha256(REF),
        "scorerGitBlobSha": git_blob_sha(SCORER),
    }
    expected = {
        "generatedSha256": EXPECTED_GEN_SHA256,
        "referenceSha256": EXPECTED_REF_SHA256,
        "scorerGitBlobSha": EXPECTED_SCORER_GIT_BLOB,
    }
    if identities != expected:
        raise RuntimeError(f"frozen score input identity drift: {identities}")
    return identities


def main() -> int:
    if SCORE.exists() or RECEIPT.exists():
        raise RuntimeError("V154 reference-facing score already exists; refusing any second score call")

    before = require_identity()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # This subprocess invocation is the one and only reference-facing score call.
    cmd = [sys.executable, str(SCORER), str(GEN), str(REF), "--output", str(SCORE)]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        # The scorer writes only at the end. Preserve stdout/stderr in the job log,
        # but do not silently retry: any failure must be inspected before deciding
        # whether a score call actually completed.
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError(f"frozen scorer exited {proc.returncode}; do not auto-rerun")

    if not SCORE.exists():
        raise RuntimeError("scorer returned success without score output")

    after = require_identity()
    if before != after:
        raise RuntimeError("frozen score inputs changed during scoring")

    report: dict[str, Any] = json.loads(SCORE.read_text(encoding="utf-8"))
    guitar = report["combinedGuitar"]["primaryTimingAwarePitch"]
    bass = report["bass"]["primaryTimingAwarePitch"]
    gross_guitar = report["combinedGuitar"]["grossTimingAwarePitch"]
    gross_bass = report["bass"]["grossTimingAwarePitch"]

    receipt = {
        "schema": "dadrock.tabs.v154.cpu-front-end-score-receipt.v1",
        "validation": "PASS",
        "scorePath": str(SCORE.relative_to(ROOT)),
        "scoreSha256": sha256(SCORE),
        "frozenInputs": before,
        "referenceFacingScoreCalls": 1,
        "scorerInvocationCountInWrapper": 1,
        "metrics": {
            "combinedGuitarPrimaryTimingAwarePitch": guitar,
            "bassPrimaryTimingAwarePitch": bass,
            "combinedGuitarGrossTimingAwarePitch": gross_guitar,
            "bassGrossTimingAwarePitch": gross_bass,
        },
        "gates": {
            "combinedGuitarTimingAwarePitchF1Target": 0.80,
            "combinedGuitarTimingAwarePitchF1": guitar["f1"],
            "combinedGuitarPass": bool(guitar["f1"] >= 0.80),
            "bassTimingAwarePitchF1Target": 0.80,
            "bassTimingAwarePitchF1": bass["f1"],
            "bassPass": bool(bass["f1"] >= 0.80),
        },
        "policy": {
            "cpuOnly": True,
            "generatedCandidateModified": False,
            "generatedCandidateRetuned": False,
            "humanCandidateCorrection": False,
            "thresholdSweep": False,
            "postScoreRetuningOfSameGeneratedOutputForbidden": True,
            "modalL4CudaGpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
