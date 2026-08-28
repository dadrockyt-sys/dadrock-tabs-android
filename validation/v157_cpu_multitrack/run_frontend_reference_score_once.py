#!/usr/bin/env python3
"""Guarded one-time V157 CPU reference-facing score.

Pins the exact frozen V157 candidate, independent QC, immutable professional
reference payload, and frozen scorer identity. The professional reference is read
only by the single scorer subprocess. This wrapper never modifies or retunes the
candidate and refuses any second score attempt after score/receipt creation.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "debug/v157-cpu-autonomous/generated.json"
QC = ROOT / "debug/v157-cpu-autonomous/structural-qc.json"
REF = ROOT / "research/v154-professional-references/scorer-ready/frontend-reference-payload.json"
SCORER = ROOT / "validation/v154_cpu_multitrack/score_frontend_reference.py"
OUT_DIR = ROOT / "debug/v157-cpu-autonomous/frontend-reference-score"
SCORE = OUT_DIR / "score.json"
RECEIPT = OUT_DIR / "score-receipt.json"

EXPECTED_GEN_SHA256 = "f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71"
EXPECTED_GEN_GIT_BLOB = "3491814f4cc075aaf3eefaecf2d179f57d2d5dae"
EXPECTED_QC_GIT_BLOB = "3528adbceb640743cc8f0e472d2cd62c49c1ebc3"
EXPECTED_REF_SHA256 = "b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7"
EXPECTED_SCORER_GIT_BLOB = "9644e65719fbd361a9b39778ae9950c5e983e855"
EXPECTED_FREEZE_COMMIT = "c26e41d239d44d656bf57cf195ed39416658b680"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def require_candidate_and_qc() -> dict[str, str]:
    identities = {
        "generatedSha256": sha256(GEN),
        "generatedGitBlob": git_blob_sha(GEN),
        "qcGitBlob": git_blob_sha(QC),
        "scorerGitBlobSha": git_blob_sha(SCORER),
    }
    expected = {
        "generatedSha256": EXPECTED_GEN_SHA256,
        "generatedGitBlob": EXPECTED_GEN_GIT_BLOB,
        "qcGitBlob": EXPECTED_QC_GIT_BLOB,
        "scorerGitBlobSha": EXPECTED_SCORER_GIT_BLOB,
    }
    if identities != expected:
        raise RuntimeError(f"V157 frozen local identity drift: {identities}")
    qc: dict[str, Any] = json.loads(QC.read_text(encoding="utf-8"))
    if qc.get("validation") != "PASS":
        raise RuntimeError("V157 independent structural QC is not PASS")
    safety = qc.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("referenceFacingScoreCalls") != 0:
        raise RuntimeError("V157 QC does not prove pre-score reference isolation")
    return identities


def require_all_score_inputs() -> dict[str, str]:
    identities = require_candidate_and_qc()
    identities["referenceSha256"] = sha256(REF)
    if identities["referenceSha256"] != EXPECTED_REF_SHA256:
        raise RuntimeError(f"frozen reference identity drift: {identities['referenceSha256']}")
    return identities


def main() -> int:
    if SCORE.exists() or RECEIPT.exists():
        raise RuntimeError("V157 reference-facing score already exists; refusing any second score call")

    # Local frozen candidate/QC/scorer checks happen before the reference is opened.
    require_candidate_and_qc()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # This is the one and only V157 reference-facing score call. Identity hashing
    # and scoring both occur inside this guarded invocation; there is no retry.
    before = require_all_score_inputs()
    cmd = [sys.executable, str(SCORER), str(GEN), str(REF), "--output", str(SCORE)]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError(f"frozen scorer exited {proc.returncode}; do not auto-rerun")
    if not SCORE.exists():
        raise RuntimeError("scorer returned success without score output")

    after = require_all_score_inputs()
    if before != after:
        raise RuntimeError("frozen score inputs changed during V157 scoring")

    report: dict[str, Any] = json.loads(SCORE.read_text(encoding="utf-8"))
    guitar = report["combinedGuitar"]["primaryTimingAwarePitch"]
    bass = report["bass"]["primaryTimingAwarePitch"]
    gross_guitar = report["combinedGuitar"]["grossTimingAwarePitch"]
    gross_bass = report["bass"]["grossTimingAwarePitch"]

    receipt = {
        "schema": "dadrock.tabs.v157.cpu-front-end-score-receipt.v1",
        "validation": "PASS",
        "candidateFreezeCommit": EXPECTED_FREEZE_COMMIT,
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
            "bothFrontEndGatesPass": bool(guitar["f1"] >= 0.80 and bass["f1"] >= 0.80),
        },
        "policy": {
            "cpuOnly": True,
            "generatedCandidateModified": False,
            "generatedCandidateRetuned": False,
            "humanCandidateCorrection": False,
            "thresholdSweep": False,
            "variantSelection": False,
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
