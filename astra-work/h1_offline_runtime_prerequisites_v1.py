#!/usr/bin/env python3
"""Read-only H1 frozen-runtime prerequisite inspection, NOT a training runner.

No real media, GitHub Actions, workflow dispatch, launch receipt, model forward,
optimizer, or network operations. This tool can establish local identities but
cannot attest independent source trust or authorize the blocked launch.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys

EXPECTED = {"python": "3.10.15", "torch": "1.11.0+cpu", "numpy": "1.21.6"}
UPSTREAM_BLOBS = {
    "models/common.py": "84beb4cf251b9cb9274d10cf203318314181af31",
    "models/tabcnn.py": "e09856db2fffd77642e005ab509846acc894b886",
    "tools/instrument.py": "eddc48a8b95de057035cd11ea2d1951e754ef349",
    "tools/constants.py": "79666ea0c5b0214ca664da454069b8d286cc5c18",
}
GENERATED_INIT = {
    "__init__.py": b"",
    "models/__init__.py": b"",
    "tools/__init__.py": b"from .constants import *\nfrom .instrument import *\n",
}


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def version_report(actual: dict[str, str], *, cuda_available: bool | None) -> dict:
    """Compare actual imported module version strings to the frozen versions."""
    if set(actual) != set(EXPECTED):
        raise ValueError("VERSION_KEYS_MISSING_OR_EXTRA")
    exact = {key: type(actual[key]) is str and actual[key] == value for key, value in EXPECTED.items()}
    cuda_disabled = cuda_available is False
    return {
        "expected": dict(EXPECTED),
        "observed": dict(actual),
        "exactVersionMatches": exact,
        "cudaAvailable": cuda_available,
        "versionsAndCpuMatch": all(exact.values()) and cuda_disabled,
    }


def local_imported_versions() -> dict:
    """Only import the two versioned libraries; perform no model computation."""
    observed = {"python": ".".join(str(x) for x in sys.version_info[:3])}
    errors = {}
    torch_module = None
    for name in ("torch", "numpy"):
        try:
            module = importlib.import_module(name)
            raw = getattr(module, "__version__", None)
            if not isinstance(raw, str):
                raise RuntimeError("MISSING_IMPORTED_PACKAGE_VERSION")
            observed[name] = raw
            if name == "torch":
                torch_module = module
        except Exception as exc:  # Fail closed, don't let optional local deps hide mismatch.
            observed[name] = "UNAVAILABLE"
            errors[name] = type(exc).__name__
    cuda = None
    if torch_module is not None:
        try:
            cuda = bool(torch_module.cuda.is_available())
        except Exception as exc:
            errors["torchCuda"] = type(exc).__name__
    result = version_report(observed, cuda_available=cuda)
    result["importErrors"] = errors
    return result


def read_exact_file(root: Path, relative: str) -> bytes:
    current = root
    for component in relative.split("/"):
        if component in ("", ".", ".."):
            raise ValueError("INVALID_RELATIVE_PATH")
        current = current / component
        if current.is_symlink():
            raise RuntimeError("UPSTREAM_PATH_SYMLINK:" + relative)
    if not current.is_file() or current.resolve() != current:
        raise RuntimeError("UPSTREAM_FILE_MISSING:" + relative)
    return current.read_bytes()


def inspect_upstream(
    source_root: Path,
    *,
    expected_blobs: dict[str, str] = UPSTREAM_BLOBS,
    init_contents: dict[str, bytes] = GENERATED_INIT,
) -> dict:
    """Compare on-disk upstream source IDs. Test injection is fixture-only."""
    root = source_root.resolve(strict=True)
    matches = {}
    for file, expected in sorted(expected_blobs.items()):
        raw = read_exact_file(root, "amt_tools/" + file)
        matches[file] = blob_sha(raw) == expected
    inits = {}
    for file, expected in sorted(init_contents.items()):
        inits[file] = read_exact_file(root, "amt_tools/" + file) == expected
    return {
        "expectedUpstreamCount": len(expected_blobs),
        "sourceBlobMatches": matches,
        "generatedInitMatches": inits,
        "allSourcesAndInitsMatch": all(matches.values()) and all(inits.values()),
    }


def review(
    version_evidence: dict,
    upstream_evidence: dict | None,
) -> dict:
    exact = version_evidence["versionsAndCpuMatch"]
    upstream_ok = bool(upstream_evidence and upstream_evidence.get("allSourcesAndInitsMatch") is True)
    return {
        "schema": "astra-h1-offline-runtime-prerequisites-v1",
        "versions": version_evidence,
        "upstream": upstream_evidence if upstream_evidence is not None else {"status": "NOT_STAGED_OR_NOT_CHECKED"},
        "prerequisitesLocallyMatched": exact and upstream_ok,
        "status": "LOCAL_IDENTITIES_ONLY_REVIEW_REQUIRED" if exact and upstream_ok else "BLOCKED_OR_UNVERIFIED",
        "independentApproval": "PENDING",
        "fullModelParityExecuted": False,
        "realDataAccess": False,
        "trainingExecuted": False,
        "launchPermission": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, help="Existing verified upstream folder; never downloaded")
    args = parser.parse_args()
    environment = local_imported_versions()
    upstream = None
    if args.source_root is not None:
        try:
            upstream = inspect_upstream(args.source_root)
        except (OSError, RuntimeError, ValueError) as exc:
            upstream = {"status": "REJECTED", "errorCode": str(exc).split(":", 1)[0]}
    result = review(environment, upstream)
    print(json.dumps(result, sort_keys=True, indent=2))
    # Not an authorization exit code: zero means only local identities matched.
    return 0 if result["prerequisitesLocallyMatched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
