#!/usr/bin/env python3
"""One-use V158 professional-reference scoring guard.

This guard preserves the V158 reference-blind boundary until the sole official
score call.  It deliberately verifies the professional reference by its Git
blob identity only; it never opens or hashes the reference content itself.
The frozen scorer is therefore the single process permitted to read the
professional reference payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    result = subprocess.run(
        ["git", "ls-files", "-s", "--", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    line = result.stdout.strip()
    if not line:
        raise RuntimeError(f"path is not tracked by git: {path}")
    fields = line.split()
    if len(fields) < 4:
        raise RuntimeError(f"unexpected git ls-files output for {path}: {line!r}")
    return fields[1]


def git_commit(commit: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{commit}^{{commit}}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_equal(label: str, actual: str, expected: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{label} mismatch: expected {expected}, got {actual}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer", type=Path, required=True)
    ap.add_argument("--generation-receipt", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--structural-qc", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--score-receipt", type=Path, required=True)
    ap.add_argument("--pre-score-receipt", type=Path, required=True)
    ap.add_argument("--freeze-commit", required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"score output already exists: {args.output}")
    if args.score_receipt.exists():
        raise RuntimeError(f"score receipt already exists: {args.score_receipt}")

    pre = load_json(args.pre_score_receipt)
    if not isinstance(pre, dict):
        raise ValueError("pre-score receipt must be a JSON object")
    if pre.get("schema") != "dadrock.tabs.v158.pre-score-reference-identity-receipt.v1":
        raise ValueError("unexpected pre-score receipt schema")
    if pre.get("status") != "SEALED_BEFORE_REFERENCE_SCORE":
        raise ValueError("pre-score receipt is not sealed")

    expected_keys = (
        "candidate_sha256",
        "candidate_git_blob",
        "generation_receipt_sha256",
        "generation_receipt_git_blob",
        "environment_receipt_sha256",
        "environment_receipt_git_blob",
        "structural_qc_git_blob",
        "scorer_git_blob",
        "guard_git_blob",
        "freeze_commit",
        "reference_sha256",
        "reference_git_blob",
    )
    missing = [key for key in expected_keys if not isinstance(pre.get(key), str) or not pre[key]]
    if missing:
        raise ValueError(f"pre-score receipt missing required identity fields: {missing}")

    require_equal("freeze commit argument", args.freeze_commit, pre["freeze_commit"])
    require_equal("freeze commit", git_commit(args.freeze_commit), pre["freeze_commit"])

    candidate_sha_before = sha256(args.candidate)
    candidate_blob_before = git_blob(args.candidate)
    generation_sha = sha256(args.generation_receipt)
    generation_blob = git_blob(args.generation_receipt)
    environment_sha = sha256(args.environment_receipt)
    environment_blob = git_blob(args.environment_receipt)
    qc_blob = git_blob(args.structural_qc)
    scorer_blob = git_blob(args.scorer)
    guard_blob = git_blob(Path(__file__))

    # Critical boundary: git metadata only. Do NOT open/hash reference content here.
    reference_blob = git_blob(args.reference)

    require_equal("candidate sha256", candidate_sha_before, pre["candidate_sha256"])
    require_equal("candidate git blob", candidate_blob_before, pre["candidate_git_blob"])
    require_equal("generation receipt sha256", generation_sha, pre["generation_receipt_sha256"])
    require_equal("generation receipt git blob", generation_blob, pre["generation_receipt_git_blob"])
    require_equal("environment receipt sha256", environment_sha, pre["environment_receipt_sha256"])
    require_equal("environment receipt git blob", environment_blob, pre["environment_receipt_git_blob"])
    require_equal("structural QC git blob", qc_blob, pre["structural_qc_git_blob"])
    require_equal("scorer git blob", scorer_blob, pre["scorer_git_blob"])
    require_equal("guard git blob", guard_blob, pre["guard_git_blob"])
    require_equal("reference git blob", reference_blob, pre["reference_git_blob"])

    attempt: dict[str, Any] = {
        "schema": "dadrock.tabs.v158.one-shot-reference-score-receipt.v1",
        "status": "REFERENCE_CALL_STARTED",
        "candidate_sha256_before": candidate_sha_before,
        "candidate_git_blob_before": candidate_blob_before,
        "generation_receipt_sha256": generation_sha,
        "generation_receipt_git_blob": generation_blob,
        "environment_receipt_sha256": environment_sha,
        "environment_receipt_git_blob": environment_blob,
        "structural_qc_git_blob": qc_blob,
        "scorer_git_blob": scorer_blob,
        "guard_git_blob": guard_blob,
        "freeze_commit": args.freeze_commit,
        "reference_sha256_expected": pre["reference_sha256"],
        "reference_git_blob_verified_without_content_read": reference_blob,
        "guard_reference_content_reads": 0,
        "frozen_scorer_invocations": 0,
        "retry_allowed": False,
    }

    # Persist consumption before the reference-facing subprocess begins.  Even a
    # scorer failure consumes V158 and must never be retried.
    write_json(args.score_receipt, attempt)

    attempt["frozen_scorer_invocations"] = 1
    write_json(args.score_receipt, attempt)
    result = subprocess.run(
        ["python", str(args.scorer), str(args.candidate), str(args.reference), "--output", str(args.output)],
        check=False,
    )

    candidate_sha_after = sha256(args.candidate)
    candidate_blob_after = git_blob(args.candidate)
    attempt["candidate_sha256_after"] = candidate_sha_after
    attempt["candidate_git_blob_after"] = candidate_blob_after
    attempt["scorer_returncode"] = result.returncode
    require_equal("candidate sha256 after score", candidate_sha_after, candidate_sha_before)
    require_equal("candidate git blob after score", candidate_blob_after, candidate_blob_before)

    if result.returncode != 0:
        attempt["status"] = "CONSUMED_SCORER_FAILED"
        attempt["score_output_exists"] = args.output.exists()
        if args.output.exists():
            attempt["score_sha256"] = sha256(args.output)
        write_json(args.score_receipt, attempt)
        raise RuntimeError(f"frozen scorer failed with return code {result.returncode}; V158 is consumed and retry is forbidden")

    if not args.output.exists():
        attempt["status"] = "CONSUMED_SCORER_NO_OUTPUT"
        write_json(args.score_receipt, attempt)
        raise RuntimeError("frozen scorer returned success without score output; V158 is consumed and retry is forbidden")

    attempt["status"] = "COMPLETE_CONSUMED"
    attempt["score_output_exists"] = True
    attempt["score_sha256"] = sha256(args.output)
    write_json(args.score_receipt, attempt)
    print(json.dumps(attempt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
