#!/usr/bin/env python3
"""Inspect a failed V168 SplitMySong historical-context build without rerunning models.

This is a read-only diagnostic. It does not import or invoke Basic Pitch, does not
invoke Demucs, and accepts no scorer/reference input. It hashes already-produced
historical stems and likely Demucs model-cache files so an exact reproducibility
failure can be attributed before the one-shot pitch-inference attempt is consumed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

EXPECTED = {
    "mix": "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e",
    "guitar": "4c71e9e15dd07e60a5442923b86523bafe4313056ca3c892054a607aa7e4e9d2",
    "bass": "4b34b2bc3367d9f8ed4dce39b95ad3d60c49d6541186df6b0d24a4211b03c7ef",
    "drums": "05890ac9cad62eacf0099c962b137a458228811a85b8ea828bb15f238d2c1e50",
}
MODEL_BASENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_MODEL_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_info(path: Path, expected: str | None = None) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False}
    observed = sha256_file(path)
    out: dict[str, Any] = {
        "path": str(path),
        "exists": True,
        "bytes": path.stat().st_size,
        "sha256": observed,
    }
    if expected is not None:
        out["expectedSha256"] = expected
        out["exactMatch"] = observed == expected
    return out


def safe_version(name: str) -> str | None:
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return None


def candidate_cache_roots(home: Path) -> list[Path]:
    roots = [
        home / ".cache" / "torch" / "hub" / "checkpoints",
        home / ".cache" / "demucs",
        home / ".cache" / "huggingface" / "hub",
        Path("/root/.cache/torch/hub/checkpoints"),
        Path("/root/.cache/demucs"),
        Path("/root/.cache/huggingface/hub"),
    ]
    seen: set[str] = set()
    unique: list[Path] = []
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def find_model_files(home: Path) -> list[dict[str, Any]]:
    found: list[Path] = []
    seen: set[str] = set()
    for root in candidate_cache_roots(home):
        if not root.exists():
            continue
        # The official Demucs cache normally carries the exact .th basename.
        for pattern in (MODEL_BASENAME, "*5c90dfd2*", "*34c22ccb*"):
            try:
                matches = root.rglob(pattern)
                for path in matches:
                    try:
                        resolved = str(path.resolve())
                    except OSError:
                        resolved = str(path)
                    if path.is_file() and resolved not in seen:
                        seen.add(resolved)
                        found.append(path)
            except (OSError, PermissionError):
                continue
    rows: list[dict[str, Any]] = []
    for path in sorted(found, key=lambda p: str(p)):
        row = file_info(path)
        row["expectedOfficialModelSha256"] = EXPECTED_MODEL_SHA256
        row["matchesExpectedOfficialModel"] = row.get("sha256") == EXPECTED_MODEL_SHA256
        try:
            if path.is_symlink():
                row["symlinkTarget"] = os.readlink(path)
        except OSError:
            pass
        rows.append(row)
    return rows


def locate_outputs(build_dir: Path) -> dict[str, Path]:
    mix = build_dir / "historical-mix.wav"
    if not mix.is_file():
        mix = build_dir / "mix.wav"

    roots = [
        build_dir / "demucs-work" / "htdemucs_6s" / "historical-mix",
        build_dir / "demucs" / "htdemucs_6s" / "historical-mix",
    ]
    stem_root = next((p for p in roots if p.is_dir()), roots[0])
    return {
        "mix": mix,
        "guitar": stem_root / "guitar.wav",
        "bass": stem_root / "bass.wav",
        "drums": stem_root / "drums.wav",
        "other": stem_root / "other.wav",
        "vocals": stem_root / "vocals.wav",
        "piano": stem_root / "piano.wav",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--build-dir",
        type=Path,
        default=Path.home() / "v168-splitmysong-private" / "historical-context.building",
    )
    args = ap.parse_args()

    build_dir = args.build_dir.expanduser().resolve()
    if not build_dir.is_dir():
        raise RuntimeError(f"failed historical-context build directory not found: {build_dir}")

    outputs = locate_outputs(build_dir)
    stem_rows: dict[str, Any] = {}
    for name, path in outputs.items():
        stem_rows[name] = file_info(path, EXPECTED.get(name))

    packages = {
        name: safe_version(name)
        for name in (
            "demucs",
            "torch",
            "torchaudio",
            "numpy",
            "soundfile",
            "julius",
            "huggingface-hub",
            "safetensors",
            "pyyaml",
            "tqdm",
        )
    }

    report = {
        "schema": "dadrock.tabs.v168.splitmysong-historical-context-failure-diagnostic.v1",
        "status": "READ_ONLY_DIAGNOSTIC",
        "buildDir": str(build_dir),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": packages,
        },
        "outputs": stem_rows,
        "modelFiles": find_model_files(Path.home()),
        "officialModelIdentity": {
            "signature": "5c90dfd2",
            "filename": MODEL_BASENAME,
            "sha256": EXPECTED_MODEL_SHA256,
        },
        "safety": {
            "demucsInvoked": False,
            "basicPitchImported": False,
            "pitchInferenceInvoked": False,
            "candidateGenerated": False,
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
        },
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    print("\nHISTORICAL CONTEXT FAILURE DIAGNOSTIC COMPLETE")
    print("No Demucs or Basic Pitch inference was invoked by this diagnostic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
