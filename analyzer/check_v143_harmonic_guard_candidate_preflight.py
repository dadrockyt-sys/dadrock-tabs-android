#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import py_compile
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "debug" / "v143-contextual-prune" / "harmonic-guard-candidate-preflight-diagnostic.json"
EXPECTED_PROTECTED = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
EXPECTED_AUDIO = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EXPECTED_OLD_CANDIDATE_BLOB = "20e7a583fcb96249636cc63b01cf9ae0044f2c62"
FORBIDDEN = (
    "professionalexample",
    "professional-rhythm-complete",
    "rhythm-professional-holdout-score",
    "songsterr",
    "are you gonna go my way",
    "lenny kravitz",
    "craig ross",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def main() -> int:
    checks: dict[str, bool] = {}
    details: dict[str, object] = {}
    errors: list[str] = []

    trigger = ROOT / "debug" / "v143-contextual-prune" / "RUN_HARMONIC_GUARD_CANDIDATE_ONCE"
    old_candidate = ROOT / "debug" / "v143-contextual-prune" / "repaired-timing-precision-candidate-product.json"
    guard_proof = ROOT / "debug" / "v143-contextual-prune" / "precision-promoted-harmonic-guard-proof.json"
    audio = ROOT / "public" / "gomywayfullaitest.m4a"
    protected = ROOT / "analyzer" / "v143_reference_free_rhythm_pipeline.py"
    new_candidate = ROOT / "debug" / "v143-contextual-prune" / "repaired-timing-precision-harmonic-guard-candidate-product.json"

    checks["originalOneShotMarkerStillPresent"] = trigger.is_file()
    checks["oldCandidatePresent"] = old_candidate.is_file() and old_candidate.stat().st_size > 0
    checks["guardProofPresent"] = guard_proof.is_file() and guard_proof.stat().st_size > 0
    checks["approvedAudioPresent"] = audio.is_file() and audio.stat().st_size > 0
    checks["protectedPipelinePresent"] = protected.is_file() and protected.stat().st_size > 0
    details["newCandidateAlreadyPresent"] = new_candidate.is_file() and new_candidate.stat().st_size > 0

    try:
        details["oldCandidateBlob"] = git_blob("debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json")
        checks["oldCandidateBlobExact"] = details["oldCandidateBlob"] == EXPECTED_OLD_CANDIDATE_BLOB
    except Exception as exc:
        checks["oldCandidateBlobExact"] = False
        errors.append(f"old-candidate-blob: {exc}")

    try:
        details["protectedPipelineBlob"] = git_blob("analyzer/v143_reference_free_rhythm_pipeline.py")
        checks["protectedPipelineExact"] = details["protectedPipelineBlob"] == EXPECTED_PROTECTED
    except Exception as exc:
        checks["protectedPipelineExact"] = False
        errors.append(f"protected-pipeline-blob: {exc}")

    try:
        details["approvedAudioSha256"] = sha256(audio)
        checks["approvedAudioShaExact"] = details["approvedAudioSha256"] == EXPECTED_AUDIO
    except Exception as exc:
        checks["approvedAudioShaExact"] = False
        errors.append(f"approved-audio-sha: {exc}")

    try:
        proof = json.loads(guard_proof.read_text(encoding="utf-8"))
        required = {
            "passed": True,
            "correctionChangesPitchIdentity": True,
            "correctionChangesAttackIdentity": False,
            "protectedPipelineUnchanged": True,
            "antiLeakagePassed": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
            "modalGpuUsed": False,
        }
        proof_checks = {key: proof.get(key) is expected for key, expected in required.items()}
        proof_checks["oldCandidateOpportunityCount96"] = int(proof.get("oldCandidateScoringRelevantSuppressionOpportunityCount") or -1) == 96
        details["guardProofChecks"] = proof_checks
        checks["guardProofExact"] = all(proof_checks.values())
    except Exception as exc:
        checks["guardProofExact"] = False
        errors.append(f"guard-proof: {exc}")

    compile_paths = (
        "analyzer/v143_repaired_timing_precision_candidate_product_modal.py",
        "analyzer/v143_precision_promoted_harmonic_guard.py",
        "analyzer/check_v143_precision_promoted_harmonic_guard.py",
        "analyzer/v143_precision_sustain_promotion.py",
    )
    compile_results: dict[str, bool] = {}
    for rel in compile_paths:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
            compile_results[rel] = True
        except Exception as exc:
            compile_results[rel] = False
            errors.append(f"py_compile {rel}: {exc}")
    details["compileResults"] = compile_results
    checks["allCandidatePythonCompiles"] = all(compile_results.values())

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "analyzer")
    checker = subprocess.run(
        ["python", "analyzer/check_v143_precision_promoted_harmonic_guard.py"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    details["guardCheckerReturnCode"] = checker.returncode
    details["guardCheckerStdoutTail"] = checker.stdout[-3000:]
    details["guardCheckerStderrTail"] = checker.stderr[-3000:]
    checks["guardCheckerPassed"] = checker.returncode == 0

    scan_paths = (
        "analyzer/v143_repaired_timing_precision_candidate_product_modal.py",
        "analyzer/v143_precision_promoted_harmonic_guard.py",
        "analyzer/v143_precision_sustain_promotion.py",
        "analyzer/v143_contextual_prune_precision_candidate_events.py",
    )
    hits: list[dict[str, str]] = []
    for rel in scan_paths:
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        for token in FORBIDDEN:
            if token in text:
                hits.append({"path": rel, "token": token})
    details["antiLeakageHits"] = hits
    checks["antiLeakagePassed"] = not hits

    failed = [name for name, passed in checks.items() if not passed]
    report = {
        "schemaVersion": 1,
        "gate": "v143-harmonic-guard-candidate-pre-modal-preflight-replay",
        "checks": checks,
        "failedChecks": failed,
        "details": details,
        "errors": errors,
        "modalImported": False,
        "modalInvoked": False,
        "modalGpuUsed": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "passed": not failed,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
