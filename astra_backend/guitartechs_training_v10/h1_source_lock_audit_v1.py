"""Read-only H1 source-lock audit. Never creates or dispatches a launch receipt."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "astra-h1-pilot-reviewed-source-lock-draft-v1"
BLOB_RE = re.compile(r"[0-9a-f]{40}\Z")


def git_blob_id(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()


def required_workflow_paths(yaml: str) -> set[str]:
    """Extract the literal Python path set from the *current* dormant H1 workflow."""
    matches = re.findall(r"\brequired\s*=\s*(\{[^{}]*\})", yaml, re.S)
    if len(matches) != 1:
        raise RuntimeError("H1_WORKFLOW_SOURCE_SET_MISSING_OR_AMBIGUOUS")
    try:
        entries = ast.literal_eval(matches[0])
    except (SyntaxError, ValueError) as exc:
        raise RuntimeError("H1_WORKFLOW_SOURCE_SET_NOT_LITERAL") from exc
    if not isinstance(entries, set) or not entries or not all(isinstance(e, str) for e in entries):
        raise RuntimeError("H1_WORKFLOW_SOURCE_SET_INVALID")
    return entries


def verify_lock(root: str | Path, lock: dict, *, extra_check: bool = True) -> dict:
    """Compare on-disk paths and Git blobs with a separate draft lock.

    This is integrity checking only; it does not prove human review,
    independent authorization, durable consumption, or safety clearance.
    """
    base = Path(root).resolve(strict=True)
    if lock.get("schema") != SCHEMA or lock.get("status") != "DRAFT_REQUIRES_INDEPENDENT_REVIEW_NOT_LAUNCH_AUTHORIZATION":
        raise RuntimeError("H1_SOURCE_LOCK_SCHEMA_OR_STATUS_MISMATCH")
    required = lock.get("requiredLiveWorkflowSources")
    extras = lock.get("additionalOfflineTestAndBudgetSources")
    if not isinstance(required, dict) or not isinstance(extras, dict) or not required:
        raise RuntimeError("H1_SOURCE_LOCK_EMPTY")
    expected = dict(required)
    if extra_check:
        if set(required).intersection(extras):
            raise RuntimeError("H1_SOURCE_LOCK_DUPLICATE_PATH")
        expected.update(extras)
    workflow_path = ".github/workflows/guitar-techs-h1-20epoch-paired-pilot.yml"
    if workflow_path not in required:
        raise RuntimeError("H1_SOURCE_LOCK_WORKFLOW_MISSING")
    for name, want in sorted(expected.items()):
        if not isinstance(name, str) or not isinstance(want, str) or not BLOB_RE.fullmatch(want):
            raise RuntimeError("H1_SOURCE_LOCK_INVALID_PATH_OR_DIGEST")
        parts = Path(name)
        if parts.is_absolute() or any(piece in ("", "..") for piece in name.split("/")):
            raise RuntimeError("H1_SOURCE_LOCK_PATH_TRAVERSAL")
        path = base / name
        if path.is_symlink() or not path.is_file() or path.resolve() != path:
            raise RuntimeError("H1_SOURCE_LOCK_MISSING_OR_LINK:" + name)
        got = git_blob_id(path.read_bytes())
        if got != want:
            raise RuntimeError("H1_SOURCE_LOCK_BLOB_MISMATCH:" + name)
    workflow = (base / workflow_path).read_text(encoding="utf-8")
    if required_workflow_paths(workflow) != set(required):
        raise RuntimeError("H1_SOURCE_LOCK_EXHAUSTIVE_SET_MISMATCH")
    return {
        "schema": "astra-h1-source-lock-offline-check-v1",
        "requiredCount": len(required),
        "additionalCount": len(extras) if extra_check else 0,
        "fileBlobStatus": "match",
        "reviewStatus": "PENDING",
        "launchPermission": False,
    }


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True)
    p.add_argument("--lock", required=True)
    args = p.parse_args()
    outcome = verify_lock(args.root, json.loads(Path(args.lock).read_text()))
    print(json.dumps(outcome, sort_keys=True))


if __name__ == "__main__":
    main()
