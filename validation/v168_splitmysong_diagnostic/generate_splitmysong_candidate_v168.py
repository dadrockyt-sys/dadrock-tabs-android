#!/usr/bin/env python3
"""One-shot reference-blind SplitMySong AYGGMW diagnostic candidate generator.

This diagnostic changes exactly one front-end input relative to the frozen V166/V167
lineage: the Guitar audio. Historical mix/drums/bass/timebase context is reproduced
and hash-verified before pitch inference. No scorer/reference path is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import math
import os
import platform
import random
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

BRANCH = "v143-contextual-prune-lobo"
PRIVATE_SOURCE_SHA256 = "6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9"
NORMALIZED_GUITAR_SHA256 = "fdb0578d71f77c150e7fe66766a03953be55e7028fef4c24dc777416f2e7ff4f"
ARM_RECEIPT_SHA256 = "f34aef34a729d4ca32ba42975717a1b8e79b568aa1a8dc44d13c2eb1bcd6ef6f"
ENV_RECEIPT_SHA256 = "c7bf81f59220808cef01a7e399830dbf8a23df4b052fac10bac75c498ad78847"
FFMPEG_RECEIPT_SHA256 = "e7713b47a4f3bf468b706bb0eef8c683ea3e2ec3571e3170f203e28bf9ee1f1f"

HISTORICAL_SOURCE_COMMIT = "74b0f815ff3f66f325220975c410621503de440f"
HISTORICAL_SOURCE_PATH = "public/gomywayfullaitest.m4a"
HISTORICAL_SOURCE_BYTES = 3478611
HISTORICAL_SOURCE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
HISTORICAL_MIX_SHA256 = "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e"
HISTORICAL_GUITAR_SHA256 = "4c71e9e15dd07e60a5442923b86523bafe4313056ca3c892054a607aa7e4e9d2"
HISTORICAL_BASS_SHA256 = "4b34b2bc3367d9f8ed4dce39b95ad3d60c49d6541186df6b0d24a4211b03c7ef"
HISTORICAL_DRUMS_SHA256 = "05890ac9cad62eacf0099c962b137a458228811a85b8ea828bb15f238d2c1e50"
TIMEBASE_SHA256 = "899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0"
BASIC_PITCH_MODEL_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"

PINNED_BLOBS = {
    "debug/v166-cpu-autonomous/timebase.json": "abebae25801b7ddeb5b933977c4f4a918f7bf9ef",
    "validation/v166_cpu_autonomous/transcribe_v166.py": "f04ca86525b2ce71680a90b84ed476943e9e6426",
    "validation/v166_cpu_autonomous/event_logic_v166.py": "6561194742093d76bab452ef0bbb0b889724dc4e",
    "validation/v167_single_song_calibration/instrument_v166_nearmiss_v167.py": "1224932a841e27bfdfe8d61fd631e5c1f728d485",
    "validation/v167_single_song_calibration/run_instrument_v166_nearmiss_v167.py": "af216b9727ca851a32c43c318ee18849c4043752",
    "validation/v167_single_song_calibration/augment_upstream_pitch_pool_v167.py": "daf4ace1b6eff1da81bb537b38caa4dcb0976b29",
    "validation/v167_single_song_calibration/apply_global_phase_v167.py": "9b13b65a2b4c9fd6a801afe50a0ecc153de56b3c",
    "validation/v167_single_song_calibration/apply_step_rules_v167.py": "00dc94081117664890d1dc5539bf5e69fedf76fa",
    "validation/v167_single_song_calibration/step_rule_sweep_v167.py": "14cac9e217f65f72933c72ee349523ca9681fc21",
    "debug/v167-single-song-calibration/step-rule-sweep.json": "2096d3caa58b6ce7d6ab57aeaa7512989e2e4acd",
    "validation/v167_single_song_calibration/build_upstream_recovery_variants_v167.py": "24413d321f64bbfcce48812ceb85b4593dcfa80c",
    "validation/v167_single_song_calibration/build_state_split_guitar_variants_v167.py": "6b480d43744a5c67c02510d55162581d896afee4",
}

EXPECTED_PACKAGES = {
    "basic-pitch": "0.4.0",
    "tflite-runtime": "2.14.0",
    "torch": "2.8.0+cpu",
    "numpy": "1.26.4",
    "scipy": "1.13.1",
    "soundfile": "0.12.1",
    "librosa": "0.11.0",
    "imageio-ffmpeg": "0.6.0",
    "demucs": "4.1.0",
}
STEPS_PER_MEASURE = 16


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


def run_text(args: list[str], *, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def require_file_sha(path: Path, expected: str, label: str) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing {label}: {path}")
    observed = sha256_file(path)
    if observed != expected:
        raise RuntimeError(f"{label} SHA256 mismatch: {observed} != {expected}")


def verify_repo(repo: Path) -> dict[str, str]:
    git_dir = run_text(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if Path(git_dir).resolve() != repo.resolve():
        raise RuntimeError("repo-root mismatch")
    branch = run_text(["git", "branch", "--show-current"], cwd=repo)
    if branch != BRANCH:
        raise RuntimeError(f"wrong branch: {branch!r} != {BRANCH!r}")
    tracked = run_text(["git", "status", "--porcelain", "--untracked-files=no"], cwd=repo)
    if tracked:
        raise RuntimeError("tracked repository changes present; generation refuses to run")
    observed: dict[str, str] = {}
    for rel, expected in PINNED_BLOBS.items():
        path = repo / rel
        if not path.is_file():
            raise RuntimeError(f"missing pinned repository input: {rel}")
        blob = git_blob_sha(path)
        observed[rel] = blob
        if blob != expected:
            raise RuntimeError(f"pinned Git blob mismatch for {rel}: {blob} != {expected}")
    require_file_sha(repo / "debug/v166-cpu-autonomous/timebase.json", TIMEBASE_SHA256, "V166 timebase")
    return observed


def verify_runtime() -> dict[str, Any]:
    if platform.python_version() != "3.10.21":
        raise RuntimeError(f"Python mismatch: {platform.python_version()}")
    packages = {name: md.version(name) for name in EXPECTED_PACKAGES}
    for name, expected in EXPECTED_PACKAGES.items():
        if packages[name] != expected:
            raise RuntimeError(f"package mismatch {name}: {packages[name]} != {expected}")
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
        "packages": packages,
        "torchCudaVersion": torch.version.cuda,
        "cudaAvailable": torch.cuda.is_available(),
    }


def ensure_historical_object(repo: Path) -> None:
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
        ["git", "fetch", "--no-tags", "origin", HISTORICAL_SOURCE_COMMIT],
        cwd=repo,
    )
    subprocess.check_call(
        ["git", "cat-file", "-e", f"{HISTORICAL_SOURCE_COMMIT}^{{commit}}"],
        cwd=repo,
    )


def materialize_historical_source(repo: Path, target: Path) -> None:
    ensure_historical_object(repo)
    with target.open("wb") as handle:
        proc = subprocess.run(
            ["git", "show", f"{HISTORICAL_SOURCE_COMMIT}:{HISTORICAL_SOURCE_PATH}"],
            cwd=repo,
            stdout=handle,
            stderr=subprocess.PIPE,
            check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(
            "historical source materialization failed: "
            + proc.stderr.decode("utf-8", errors="replace")
        )
    if target.stat().st_size != HISTORICAL_SOURCE_BYTES:
        raise RuntimeError("historical source byte count mismatch")
    require_file_sha(target, HISTORICAL_SOURCE_SHA256, "historical source")


def normalize_historical_mix(source: Path, target: Path) -> str:
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.check_call(
        [
            ffmpeg_exe,
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
    require_file_sha(target, HISTORICAL_MIX_SHA256, "historical normalized mix")
    return ffmpeg_exe


def reproduce_historical_stems(mix: Path, demucs_dir: Path) -> dict[str, Path]:
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
            str(demucs_dir),
            str(mix),
        ]
    )
    stem_dir = demucs_dir / "htdemucs_6s" / mix.stem
    paths = {
        "guitar": stem_dir / "guitar.wav",
        "bass": stem_dir / "bass.wav",
        "drums": stem_dir / "drums.wav",
    }
    require_file_sha(paths["guitar"], HISTORICAL_GUITAR_SHA256, "historical Demucs guitar stem")
    require_file_sha(paths["bass"], HISTORICAL_BASS_SHA256, "historical Demucs bass stem")
    require_file_sha(paths["drums"], HISTORICAL_DRUMS_SHA256, "historical Demucs drums stem")
    return paths


def import_pipeline_modules(repo: Path):
    v167_dir = repo / "validation/v167_single_song_calibration"
    sys.path.insert(0, str(v167_dir))
    try:
        import run_instrument_v166_nearmiss_v167 as runner
        import augment_upstream_pitch_pool_v167 as augment
        import apply_global_phase_v167 as phase
        import apply_step_rules_v167 as step_apply
        import build_state_split_guitar_variants_v167 as state_builder
    finally:
        if sys.path and sys.path[0] == str(v167_dir):
            sys.path.pop(0)
    return runner, augment, phase, step_apply, state_builder


def raw_basic_pitch_from_notes(notes: Any, midi_min: int, midi_max: int) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for note in notes:
        if len(note) < 4:
            continue
        start, end = float(note[0]), float(note[1])
        midi = int(round(float(note[2])))
        confidence = float(note[3])
        if (
            midi_min <= midi <= midi_max
            and math.isfinite(start)
            and math.isfinite(end)
            and math.isfinite(confidence)
        ):
            raw.append(
                {
                    "midi": midi,
                    "startSeconds": start,
                    "endSeconds": end,
                    "durationSeconds": max(0.0, end - start),
                    "confidence": confidence,
                }
            )
    return raw


def build_candidate(
    repo: Path,
    normalized_guitar: Path,
    historical_mix: Path,
    historical_drums: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    from basic_pitch import ICASSP_2022_MODEL_PATH
    import basic_pitch.inference as bp_inference

    model_path = Path(ICASSP_2022_MODEL_PATH)
    require_file_sha(model_path, BASIC_PITCH_MODEL_SHA256, "Basic Pitch model")

    runner, augment, phase, step_apply, state_builder = import_pipeline_modules(repo)
    v166_path = repo / "validation/v166_cpu_autonomous/transcribe_v166.py"
    module = runner.load_v166_module_with_event_logic(v166_path)

    timebase = json.loads((repo / "debug/v166-cpu-autonomous/timebase.json").read_text(encoding="utf-8"))
    lattice = [float(x) for x in timebase["subdivisionTimesSeconds"]]

    mix_y = module.load_mono(historical_mix)
    drums_y = module.load_mono(historical_drums)
    shared_env = module.shared_onset_env(mix_y, drums_y)

    original_predict = bp_inference.predict
    cache: dict[str, Any] = {}
    counters = {"wrapperCalls": 0, "actualInferenceCalls": 0}

    def cached_predict(*args, **kwargs):
        counters["wrapperCalls"] += 1
        if "result" not in cache:
            cache["result"] = original_predict(*args, **kwargs)
            counters["actualInferenceCalls"] += 1
        return cache["result"]

    bp_inference.predict = cached_predict
    try:
        v166_guitar_raw, v166_meta, guitar_env = module.guitar_events(normalized_guitar)
    finally:
        bp_inference.predict = original_predict

    if counters["actualInferenceCalls"] != 1:
        raise AssertionError(f"expected exactly one Basic Pitch inference, got {counters}")
    notes = cache["result"][2]
    raw_basic_pitch = raw_basic_pitch_from_notes(
        notes, module.GUITAR_RANGE[0], module.GUITAR_RANGE[1]
    )
    if len(raw_basic_pitch) != int(v166_meta["basicPitchRawEventCount"]):
        raise AssertionError("cached Basic Pitch raw note count disagrees with V166 front-end")

    v166_guitar, pre_grid, evidence_corrections = module.map_events(
        v166_guitar_raw, lattice, guitar_env, shared_env, "combinedGuitar"
    )

    i001_guitar = [phase.shift_event(row, -12) for row in v166_guitar]

    rule_code = repo / "validation/v167_single_song_calibration/step_rule_sweep_v167.py"
    rule_module = step_apply.load_rule_module(rule_code)
    i002_guitar, i002_summary = step_apply.transform_stream(
        i001_guitar, "combinedGuitar", "max_score_x_shared", rule_module
    )

    pool_seed = {"guitar": {"rawBasicPitch": raw_basic_pitch}}
    standalone_pool = augment.guitar_pool(module, normalized_guitar, pool_seed)
    rows = list(standalone_pool["candidates"])

    config = state_builder.full_config(
        "gss-active-only",
        inactive_enabled=False,
        inactive_ratio_min=None,
        inactive_interval_policy=None,
    )
    expected_config = {
        "id": "gss-active-only",
        "stream": "combinedGuitar",
        "baseline": False,
        "reproductionControl": False,
        "templateRankMin": 0.975,
        "activitySupportMin": 0.05,
        "onsetSupportMin": 0.50,
        "requireBasicPitchActiveContext": True,
        "fundamentalPresentRequired": True,
        "maxAddsPerSite": 1,
        "existingIteration003EventsPreferred": True,
        "stepMidiDedupe": True,
        "polyphonyCap": 6,
        "activeBranch": {
            "candidateState": "basic_pitch_active",
            "candidateToMaxActiveTemplateScoreMin": 1.0,
            "intervalContextPolicy": "exclude_harmonic_octave",
            "harmonicOctaveIntervalsRejected": [12, 19, 24],
        },
        "inactiveBranch": {
            "enabled": False,
            "candidateState": "basic_pitch_inactive",
            "candidateToMaxActiveTemplateScoreMin": None,
            "intervalContextPolicy": None,
            "harmonicOctaveIntervalsRejected": [12, 19, 24],
            "chordIntervalsAllowed": [3, 4, 5, 7, 8, 9, 10],
        },
    }
    if config != expected_config:
        raise AssertionError("gss-active-only frozen config drifted")

    final_guitar, i005_summary = state_builder.build_guitar(
        i002_guitar, rows, config, lattice
    )

    coords = [
        (int(row["absoluteGridStep"]), int(row["midi"])) for row in final_guitar
    ]
    if len(coords) != len(set(coords)):
        raise AssertionError("final Guitar candidate contains duplicate step/MIDI coordinates")
    per_step: dict[int, int] = {}
    for absolute, _midi in coords:
        if absolute < 0:
            raise AssertionError("negative final Guitar grid step")
        per_step[absolute] = per_step.get(absolute, 0) + 1
    if max(per_step.values(), default=0) > 6:
        raise AssertionError("final Guitar candidate exceeds frozen polyphony cap")

    candidate = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-candidate.v1",
        "version": "V168_SPLITMYSONG_DIAGNOSTIC",
        "status": "REFERENCE_BLIND_CANDIDATE_FROZEN_PENDING_LEGACY_SCORE",
        "diagnosticOnly": True,
        "song": {
            "artist": "Lenny Kravitz",
            "title": "Are You Gonna Go My Way",
            "alignmentStartOffsetSeconds": 0.0,
            "timeStretchApplied": False,
        },
        "streams": {"combinedGuitar": final_guitar},
        "pipeline": {
            "changedInput": "guitar_audio_only",
            "historicalMixDrumsBassTimebasePreserved": True,
            "v166RawBasicPitchCount": int(v166_meta["basicPitchRawEventCount"]),
            "v166MappedGuitarCount": len(v166_guitar),
            "v167I001EquivalentGuitarCount": len(i001_guitar),
            "v167I002EquivalentGuitarCount": len(i002_guitar),
            "v167I002RuleSummary": i002_summary,
            "upstreamPitchPoolSiteCount": int(standalone_pool["siteCount"]),
            "upstreamPitchPoolCandidateCount": int(standalone_pool["candidateCount"]),
            "i005Config": config,
            "i005Summary": i005_summary,
            "finalGuitarCount": len(final_guitar),
            "preGridExcludedAtV166": int(pre_grid),
            "evidenceStepCorrectionsAtV166": int(evidence_corrections),
            "basicPitchInference": counters,
        },
        "safety": {
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "professionalReferencePathsOpened": 0,
            "referenceGuidedFiltering": False,
            "thresholdTuningPerformed": False,
            "humanCorrection": False,
            "pitchInferenceInvoked": True,
            "candidateGenerated": True,
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    details = {
        "basicPitchModelSha256": sha256_file(model_path),
        "v166Metadata": v166_meta,
        "basicPitchRawCount": len(raw_basic_pitch),
        "standalonePitchPool": {
            "siteCount": int(standalone_pool["siteCount"]),
            "candidateCount": int(standalone_pool["candidateCount"]),
        },
        "i005Summary": i005_summary,
        "counts": {
            "v166Mapped": len(v166_guitar),
            "i001": len(i001_guitar),
            "i002": len(i002_guitar),
            "final": len(final_guitar),
        },
        "basicPitchInference": counters,
    }
    return candidate, details


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--normalized-guitar", type=Path, required=True)
    ap.add_argument("--arm-receipt", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--ffmpeg-receipt", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o700)

    candidate_path = out_dir / "splitmysong-i005-candidate.json"
    receipt_path = out_dir / "splitmysong-generation-receipt.json"
    freeze_path = out_dir / "splitmysong-candidate-freeze.json"
    attempt_marker = out_dir / "splitmysong-generation-attempt.marker"
    for path in (candidate_path, receipt_path, freeze_path, attempt_marker):
        if path.exists():
            raise RuntimeError(
                f"one-shot generation output/marker already exists; rerun forbidden: {path}"
            )

    require_file_sha(args.source, PRIVATE_SOURCE_SHA256, "private SplitMySong source")
    require_file_sha(args.normalized_guitar, NORMALIZED_GUITAR_SHA256, "normalized SplitMySong Guitar")
    require_file_sha(args.arm_receipt, ARM_RECEIPT_SHA256, "ARM preflight receipt")
    require_file_sha(args.environment_receipt, ENV_RECEIPT_SHA256, "CPU environment receipt")
    require_file_sha(args.ffmpeg_receipt, FFMPEG_RECEIPT_SHA256, "FFmpeg normalizer receipt")
    repo_blobs = verify_repo(repo)
    runtime = verify_runtime()

    context_dir = out_dir / "historical-context-work"
    if context_dir.exists():
        raise RuntimeError(
            "historical context work directory already exists; inspect/remove only if no "
            "generation-attempt marker exists"
        )
    context_dir.mkdir(mode=0o700)
    historical_source = context_dir / "historical-source.m4a"
    historical_mix = context_dir / "historical-mix.wav"
    demucs_dir = context_dir / "demucs"

    materialize_historical_source(repo, historical_source)
    imageio_ffmpeg_exe = normalize_historical_mix(historical_source, historical_mix)
    stems = reproduce_historical_stems(historical_mix, demucs_dir)

    attempt_marker.write_text(
        "ONE_SHOT_PITCH_INFERENCE_ARMED_AND_STARTED\n", encoding="utf-8"
    )
    os.chmod(attempt_marker, 0o600)

    candidate, details = build_candidate(
        repo, args.normalized_guitar, historical_mix, stems["drums"]
    )
    write_json(candidate_path, candidate)
    candidate_sha = sha256_file(candidate_path)

    receipt = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-generation-receipt.v1",
        "status": "REFERENCE_BLIND_CANDIDATE_GENERATED_AND_HASH_FROZEN",
        "candidatePath": str(candidate_path),
        "candidateSha256": candidate_sha,
        "inputIdentities": {
            "privateSplitMySongSourceSha256": PRIVATE_SOURCE_SHA256,
            "normalizedSplitMySongGuitarSha256": NORMALIZED_GUITAR_SHA256,
            "armReceiptSha256": ARM_RECEIPT_SHA256,
            "environmentReceiptSha256": ENV_RECEIPT_SHA256,
            "ffmpegReceiptSha256": FFMPEG_RECEIPT_SHA256,
            "historicalSourceSha256": HISTORICAL_SOURCE_SHA256,
            "historicalNormalizedMixSha256": HISTORICAL_MIX_SHA256,
            "historicalDemucsGuitarSha256": HISTORICAL_GUITAR_SHA256,
            "historicalDemucsBassSha256": HISTORICAL_BASS_SHA256,
            "historicalDemucsDrumsSha256": HISTORICAL_DRUMS_SHA256,
            "timebaseSha256": TIMEBASE_SHA256,
        },
        "historicalContext": {
            "sourceCommit": HISTORICAL_SOURCE_COMMIT,
            "sourcePath": HISTORICAL_SOURCE_PATH,
            "imageioFfmpegExecutable": imageio_ffmpeg_exe,
            "demucsModel": "htdemucs_6s",
            "demucsDevice": "cpu",
            "demucsShifts": 1,
            "demucsJobs": 1,
            "changedInput": "guitar_audio_only",
        },
        "repositoryGitBlobs": repo_blobs,
        "runtime": runtime,
        "generation": details,
        "safety": {
            "referenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "professionalReferencePathsOpened": 0,
            "referenceGuidedFiltering": False,
            "thresholdTuningPerformed": False,
            "humanCorrection": False,
            "candidateGenerated": True,
            "pitchInferenceInvoked": True,
            "basicPitchActualInferenceCalls": int(
                details["basicPitchInference"]["actualInferenceCalls"]
            ),
            "gpuCudaUsed": False,
            "modalUsed": False,
            "mainOrProductionModified": False,
        },
    }
    write_json(receipt_path, receipt)
    receipt_sha = sha256_file(receipt_path)

    freeze = {
        "schema": "dadrock.tabs.v168.splitmysong-ayggmw-diagnostic-candidate-freeze.v1",
        "status": "FROZEN_BEFORE_ANY_LEGACY_REFERENCE_OR_SCORER_ACCESS",
        "candidateSha256": candidate_sha,
        "generationReceiptSha256": receipt_sha,
        "referenceRead": False,
        "scorerRead": False,
        "referenceFacingScoreCalls": 0,
    }
    write_json(freeze_path, freeze)
    freeze_sha = sha256_file(freeze_path)

    shutil.rmtree(context_dir)

    print(
        json.dumps(
            {
                "status": freeze["status"],
                "candidateSha256": candidate_sha,
                "generationReceiptSha256": receipt_sha,
                "candidateFreezeSha256": freeze_sha,
                "finalGuitarCount": len(candidate["streams"]["combinedGuitar"]),
                "i005Summary": candidate["pipeline"]["i005Summary"],
                "basicPitchActualInferenceCalls": details["basicPitchInference"][
                    "actualInferenceCalls"
                ],
                "referenceRead": False,
                "scorerRead": False,
                "referenceFacingScoreCalls": 0,
            },
            indent=2,
            sort_keys=True,
        )
    )
    print("\nREFERENCE-BLIND CANDIDATE FROZEN")
    print("Do not run any scorer until these hashes are checkpointed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
