#!/usr/bin/env python3
"""Inspect a failed V168 SplitMySong historical-context build without rerunning models.

This is a read-only diagnostic. It does not import or invoke Basic Pitch, does not
invoke Demucs, and accepts no scorer/reference input. It hashes already-produced
historical stems and the local Demucs model-cache files so an exact reproducibility
failure can be attributed before the one-shot pitch-inference attempt is consumed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
import platform
from pathlib import Path
from typing import Any

EXPECTED = {
    "mix": "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e",
    "guitar": "4c71e9e15dd07e60a5442923b86523bafe4313056ca3c892054a607aa7e4e9d2",
    "bass": "4b34b2bc3367d9f8ed4dce39b95ad3d60c49d6541186df6b0d24a4211b03c7ef",
    "drums": "05890ac9cad62eacf0099c962b137a458228811a85b8ea828bb15f238d2c1e50",
}

# Demucs 4.1.0 named-model loading tries Hugging Face first. The frozen model name
# htdemucs_6s maps to adefossez/HTDemucs-6s -> 5c90dfd2.safetensors.
HF_REPO_CACHE_NAME = "models--adefossez--HTDemucs-6s"
HF_MODEL_BASENAME = "5c90dfd2.safetensors"
HF_MODEL_SHA256 = "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411"
HF_YAML_BASENAME = "htdemucs_6s.yaml"

# If Hugging Face loading fails, Demucs retains the legacy official remote fallback.
LEGACY_MODEL_BASENAME = "5c90dfd2-34c22ccb.th"
LEGACY_MODEL_SHA256 = "34c22ccb381c6f9fdbf324f04e1e2fe21aaaf293f5ded163a162697ff9a02ddd"


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
    if path.is_symlink():
        try:
            out["symlinkTarget"] = os.readlink(path)
            out["resolvedPath"] = str(path.resolve())
        except OSError:
            pass
    return out


def safe_version(name: str) -> str | None:
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return None


def candidate_cache_roots(home: Path) -> list[Path]:
    roots = [
        home / ".cache" / "huggingface" / "hub",
        home / ".cache" / "torch" / "hub" / "checkpoints",
        home / ".cache" / "demucs",
        Path("/root/.cache/huggingface/hub"),
        Path("/root/.cache/torch/hub/checkpoints"),
        Path("/root/.cache/demucs"),
    ]
    seen: set[str] = set()
    unique: list[Path] = []
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def expected_for_model_path(path: Path) -> tuple[str | None, str | None]:
    if path.name == HF_MODEL_BASENAME:
        return "huggingFaceSafetensors", HF_MODEL_SHA256
    if path.name == LEGACY_MODEL_BASENAME:
        return "legacyTorchCheckpoint", LEGACY_MODEL_SHA256
    return None, None


def find_model_files(home: Path) -> list[dict[str, Any]]:
    found: list[Path] = []
    seen: set[str] = set()
    patterns = (
        HF_MODEL_BASENAME,
        LEGACY_MODEL_BASENAME,
        "*5c90dfd2*",
        "*34c22ccb*",
    )
    for root in candidate_cache_roots(home):
        if not root.exists():
            continue
        for pattern in patterns:
            try:
                for path in root.rglob(pattern):
                    if not path.is_file():
                        continue
                    key = str(path.absolute())
                    if key not in seen:
                        seen.add(key)
                        found.append(path)
            except (OSError, PermissionError):
                continue

    rows: list[dict[str, Any]] = []
    for path in sorted(found, key=lambda p: str(p)):
        kind, expected_sha = expected_for_model_path(path)
        row = file_info(path, expected_sha)
        row["modelKind"] = kind or "relatedCacheFile"
        rows.append(row)
    return rows


def hf_cache_metadata(home: Path) -> list[dict[str, Any]]:
    hubs = [home / ".cache" / "huggingface" / "hub", Path("/root/.cache/huggingface/hub")]
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for hub in hubs:
        repo = hub / HF_REPO_CACHE_NAME
        key = str(repo.absolute())
        if key in seen or not repo.is_dir():
            continue
        seen.add(key)
        row: dict[str, Any] = {"repoCache": str(repo), "exists": True}
        ref = repo / "refs" / "main"
        if ref.is_file():
            row["mainRef"] = ref.read_text(encoding="utf-8", errors="replace").strip()
        snapshots = repo / "snapshots"
        if snapshots.is_dir():
            row["snapshotIds"] = sorted(p.name for p in snapshots.iterdir() if p.is_dir())
            snapshot_files: list[dict[str, Any]] = []
            for snap in sorted((p for p in snapshots.iterdir() if p.is_dir()), key=lambda p: p.name):
                for filename in (HF_YAML_BASENAME, HF_MODEL_BASENAME):
                    path = snap / filename
                    if path.is_file():
                        _kind, expected_sha = expected_for_model_path(path)
                        item = file_info(path, expected_sha)
                        item["snapshotId"] = snap.name
                        snapshot_files.append(item)
            row["snapshotFiles"] = snapshot_files
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
    output_rows = {
        name: file_info(path, EXPECTED.get(name)) for name, path in outputs.items()
    }

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
        "schema": "dadrock.tabs.v168.splitmysong-historical-context-failure-diagnostic.v2",
        "status": "READ_ONLY_DIAGNOSTIC",
        "buildDir": str(build_dir),
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "packages": packages,
        },
        "outputs": output_rows,
        "modelFiles": find_model_files(Path.home()),
        "huggingFaceCache": hf_cache_metadata(Path.home()),
        "officialModelIdentities": {
            "signature": "5c90dfd2",
            "namedModel": "htdemucs_6s",
            "huggingFace": {
                "repoId": "adefossez/HTDemucs-6s",
                "filename": HF_MODEL_BASENAME,
                "sha256": HF_MODEL_SHA256,
            },
            "legacyFallback": {
                "filename": LEGACY_MODEL_BASENAME,
                "sha256": LEGACY_MODEL_SHA256,
            },
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
