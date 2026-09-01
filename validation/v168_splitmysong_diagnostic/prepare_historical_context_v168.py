#!/usr/bin/env python3
"""Prepare and freeze the historical AYGGMW context for SplitMySong diagnostic.

Reference-blind / no-pitch-inference stage. Reproduces the exact historical source,
normalized mix, and deterministic Demucs htdemucs_6s stems used by V166, verifies
all frozen byte identities, and writes a private receipt. It never reads a scorer
or professional reference and never invokes Basic Pitch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import torch

BRANCH = "v143-contextual-prune-lobo"
HISTORICAL_SOURCE_COMMIT = "74b0f815ff3f66f325220975c410621503de440f"
HISTORICAL_SOURCE_PATH = "public/gomywayfullaitest.m4a"
HISTORICAL_SOURCE_BYTES = 3478611
HISTORICAL_SOURCE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
HISTORICAL_MIX_SHA256 = "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e"
HISTORICAL_GUITAR_SHA256 = "4c71e9e15dd07e60a5442923b86523bafe4313056ca3c892054a607aa7e4e9d2"
HISTORICAL_BASS_SHA256 = "4b34b2bc3367d9f8ed4dce39b95ad3d60c49d6541186df6b0d24a4211b03c7ef"
HISTORICAL_DRUMS_SHA256 = "05890ac9cad62eacf0099c962b137a458228811a85b8ea828bb15f238d2c1e50"
TIMEBASE_SHA256 = "899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0"
TIMEBASE_BLOB = "abebae25801b7ddeb5b933977c4f4a918f7bf9ef"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def require_sha(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"{label} SHA256 mismatch: {observed} != {expected}")


def run_text(args: list[str], cwd: Path) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def verify_repo(repo: Path) -> dict[str, Any]:
    top = Path(run_text(["git", "rev-parse", "--show-toplevel"], repo)).resolve()
    if top != repo.resolve():
        raise RuntimeError("repo-root mismatch")
    branch = run_text(["git", "branch", "--show-current"], repo)
    if branch != BRANCH:
        raise RuntimeError(f"wrong branch: {branch!r}")
    tracked = run_text(
        ["git", "status", "--porcelain", "--untracked-files=no"], repo
    )
    if tracked:
        raise RuntimeError("tracked repository changes present")
    timebase = repo / "debug/v166-cpu-autonomous/timebase.json"
    if git_blob_sha(timebase) != TIMEBASE_BLOB:
        raise RuntimeError("V166 timebase Git blob mismatch")
    require_sha(timebase, TIMEBASE_SHA256, "V166 timebase")
    return {
        "branch": branch,
        "head": run_text(["git", "rev-parse", "HEAD"], repo),
        "timebaseGitBlob": TIMEBASE_BLOB,
        "timebaseSha256": TIMEBASE_SHA256,
    }


def verify_cpu_runtime() -> dict[str, Any]:
    if platform.python_version() != "3.10.21":
        raise RuntimeError(f"Python mismatch: {platform.python_version()}")
    if torch.__version__ != "2.8.0+cpu":
        raise RuntimeError(f"Torch mismatch: {torch.__version__}")
    if torch.version.cuda is not None or torch.cuda.is_available():
        raise RuntimeError("CUDA must be unavailable")
    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    return {
        "pythonVersion": platform.python_version(),
        "torchVersion": torch.__version__,
        "torchCudaVersion": torch.version.cuda,
        "cudaAvailable": torch.cuda.is_available(),
    }


def ensure_historical_commit(repo: Path) -> None:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{HISTORICAL_SOURCE_COMMIT}^{{commit}}"],
        cwd=repo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if probe.returncode == 0:
        return
    subprocess.check_call(
        ["git", "fetch", "--no-tags", "origin", HISTORICAL_SOURCE_COMMIT], cwd=repo
    )


def materialize_source(repo: Path, target: Path) -> None:
    ensure_historical_commit(repo)
    with target.open("wb") as handle:
        proc = subprocess.run(
            ["git", "show", f"{HISTORICAL_SOURCE_COMMIT}:{HISTORICAL_SOURCE_PATH}"],
            cwd=repo,
            stdout=handle,
            stderr=subprocess.PIPE,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))
    if target.stat().st_size != HISTORICAL_SOURCE_BYTES:
        raise RuntimeError("historical source byte count mismatch")
    require_sha(target, HISTORICAL_SOURCE_SHA256, "historical source")


def normalize_mix(source: Path, target: Path) -> str:
    import imageio_ffmpeg

    exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.check_call(
        [
            exe,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-ar",
            "44100",
            "-ac",
            "2",
            "-c:a",
            "pcm_s16le",
            str(target),
        ]
    )
    require_sha(target, HISTORICAL_MIX_SHA256, "historical normalized mix")
    return exe


def separate(mix: Path, demucs_root: Path) -> dict[str, Path]:
    from demucs.separate import main as demucs_main

    random.seed(0)
    np.random.seed(0)
    torch.manual_seed(0)
    demucs_main(
        [
            "-n",
            "htdemucs_6s",
            "-d",
            "cpu",
            "--shifts",
            "1",
            "-j",
            "1",
            "-o",
            str(demucs_root),
            str(mix),
        ]
    )
    base = demucs_root / "htdemucs_6s" / mix.stem
    stems = {
        "guitar": base / "guitar.wav",
        "bass": base / "bass.wav",
        "drums": base / "drums.wav",
    }
    require_sha(stems["guitar"], HISTORICAL_GUITAR_SHA256, "historical Guitar stem")
    require_sha(stems["bass"], HISTORICAL_BASS_SHA256, "historical Bass stem")
    require_sha(stems["drums"], HISTORICAL_DRUMS_SHA256, "historical Drums stem")
    return stems


def copy_private(src: Path, dst: Path) -> None:
    shutil.copy2(src, dst)
    os.chmod(dst, 0o600)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    out = args.output_dir.resolve()
    if out.exists():
        raise RuntimeError(f"context output already exists; write-once: {out}")
    build = out.with_name(out.name + ".building")
    if build.exists():
        raise RuntimeError(f"incomplete prior context build exists: {build}")

    repo_info = verify_repo(repo)
    runtime = verify_cpu_runtime()
    build.mkdir(parents=True, mode=0o700)
    source = build / "historical-source.m4a"
    mix = build / "historical-mix.wav"
    demucs_root = build / "demucs-work"

    try:
        materialize_source(repo, source)
        ffmpeg_exe = normalize_mix(source, mix)
        stems = separate(mix, demucs_root)

        final_mix = build / "mix.wav"
        final_guitar = build / "guitar-original-demucs.wav"
        final_bass = build / "bass-original-demucs.wav"
        final_drums = build / "drums-original-demucs.wav"
        mix.rename(final_mix)
        copy_private(stems["guitar"], final_guitar)
        copy_private(stems["bass"], final_bass)
        copy_private(stems["drums"], final_drums)

        source.unlink()
        shutil.rmtree(demucs_root)

        receipt = {
            "schema": "dadrock.tabs.v168.splitmysong-historical-context-preflight.v1",
            "status": "HISTORICAL_CONTEXT_FROZEN",
            "validation": "PASS",
            "purpose": "reference-blind SplitMySong AYGGMW A/B context reproduction",
            "repository": repo_info,
            "runtime": runtime,
            "historicalSource": {
                "commit": HISTORICAL_SOURCE_COMMIT,
                "path": HISTORICAL_SOURCE_PATH,
                "bytes": HISTORICAL_SOURCE_BYTES,
                "sha256": HISTORICAL_SOURCE_SHA256,
                "retainedAfterVerification": False,
            },
            "normalization": {
                "imageioFfmpegExecutable": ffmpeg_exe,
                "mixSha256": HISTORICAL_MIX_SHA256,
            },
            "demucs": {
                "model": "htdemucs_6s",
                "device": "cpu",
                "shifts": 1,
                "jobs": 1,
                "guitarSha256": HISTORICAL_GUITAR_SHA256,
                "bassSha256": HISTORICAL_BASS_SHA256,
                "drumsSha256": HISTORICAL_DRUMS_SHA256,
            },
            "privateFiles": {
                "mix": "mix.wav",
                "guitarOriginalDemucs": "guitar-original-demucs.wav",
                "bassOriginalDemucs": "bass-original-demucs.wav",
                "drumsOriginalDemucs": "drums-original-demucs.wav",
            },
            "safety": {
                "basicPitchImported": False,
                "pitchInferenceInvoked": False,
                "candidateGenerated": False,
                "referenceRead": False,
                "scorerRead": False,
                "referenceFacingScoreCalls": 0,
                "gpuCudaUsed": False,
                "modalUsed": False,
                "mainOrProductionModified": False,
            },
        }
        receipt_path = build / "context-receipt.json"
        receipt_path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        os.chmod(receipt_path, 0o600)

        for path, expected, label in (
            (final_mix, HISTORICAL_MIX_SHA256, "final mix"),
            (final_guitar, HISTORICAL_GUITAR_SHA256, "final Guitar"),
            (final_bass, HISTORICAL_BASS_SHA256, "final Bass"),
            (final_drums, HISTORICAL_DRUMS_SHA256, "final Drums"),
        ):
            require_sha(path, expected, label)

        receipt_sha = sha256_file(receipt_path)
        build.rename(out)
    except Exception:
        print(
            "CONTEXT PREFLIGHT FAILED BEFORE BASIC PITCH INFERENCE; "
            f"inspect private build directory if present: {build}",
            file=sys.stderr if 'sys' in globals() else None,
        )
        raise

    print(json.dumps({
        "status": "HISTORICAL_CONTEXT_FROZEN",
        "validation": "PASS",
        "contextReceiptSha256": receipt_sha,
        "mixSha256": HISTORICAL_MIX_SHA256,
        "guitarOriginalDemucsSha256": HISTORICAL_GUITAR_SHA256,
        "bassOriginalDemucsSha256": HISTORICAL_BASS_SHA256,
        "drumsOriginalDemucsSha256": HISTORICAL_DRUMS_SHA256,
        "pitchInferenceInvoked": False,
        "candidateGenerated": False,
        "referenceRead": False,
        "scorerRead": False,
    }, indent=2, sort_keys=True))
    print("\nHISTORICAL CONTEXT PREFLIGHT PASS")
    print("No Basic Pitch inference was invoked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
