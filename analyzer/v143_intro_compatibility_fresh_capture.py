#!/usr/bin/env python3
"""Research-only fresh V143 measures 1-16 compatibility capture.

This producer is intentionally isolated from production. It creates one fresh,
fully fingerprinted separator invocation and uses the exact resulting direct and
cascade stems for both stem identity capture and the historical measures 1-16
raw-attack Basic Pitch cache.

Do not reinterpret any output from this producer as recovered historical
separator provenance. It produces fresh compatibility evidence only.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_shadow_modal import shadow_image


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_AUDIO = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
DEBUG_ROOT = REPO_ROOT / "debug" / "v143-contextual-prune"
RUNS_ROOT = DEBUG_ROOT / "intro-compatibility-runs"

EXPECTED_BRANCH = "v143-contextual-prune-lobo"
EXPECTED_SOURCE_GIT_BLOB_SHA = "5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"
EXPECTED_AUDIO_SEPARATOR_VERSION = "0.44.5"
EXPECTED_BS_ROFORMER_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"
EXPECTED_DEMUCS_MODEL = "htdemucs_6s.yaml"
AUDIO_SEPARATOR_MODEL_DIR = Path("/tmp/audio-separator-models")
DECODED_PCM_HASH_METHOD = "soundfile-int16-always2d-numpy-tobytes-sha256-v1"

INTRO_FIRST_MEASURE = 1
INTRO_LAST_MEASURE = 16
WIDE_GRID_TOLERANCE_SECONDS = 0.30
PRODUCTION_GRID_TOLERANCE_SECONDS = 0.10

CAPTURE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")

app = modal.App("dadrock-v143-intro-compatibility-fresh-capture")
capture_image = shadow_image.add_local_python_source(
    "modal_analyzer",
    "v143_contextual_prune_shadow_modal",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_blob_sha1_bytes(value: bytes) -> str:
    header = f"blob {len(value)}\0".encode("utf-8")
    return hashlib.sha1(header + value).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _normalized_package_name(value: Any) -> str:
    return re.sub(r"[-_.]+", "-", str(value or "").strip().lower())


def _safe_suffix(value: str) -> str:
    suffix = str(value or ".audio").strip().lower()
    if suffix not in {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"}:
        return ".audio"
    return suffix


def _validate_capture_id(value: str) -> str:
    capture_id = str(value).strip()
    if capture_id in {".", ".."} or not CAPTURE_ID_RE.fullmatch(capture_id):
        raise ValueError(
            "capture_id must be 1-96 characters using only letters, numbers, '.', '_' or '-'"
        )
    return capture_id


def _new_capture_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex[:12]}"


def _ensure_debug_path(path: Path) -> Path:
    resolved_root = DEBUG_ROOT.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise RuntimeError(f"Refusing write outside isolated debug root: {path}") from exc
    return resolved


def _run_directory(capture_id: str) -> Path:
    capture_id = _validate_capture_id(capture_id)
    return _ensure_debug_path(RUNS_ROOT / capture_id)


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {(result.stderr or result.stdout).strip()}"
        )
    return result.stdout.strip()


def _local_checkout_identity() -> tuple[str, str]:
    branch = _git_output("rev-parse", "--abbrev-ref", "HEAD")
    commit = _git_output("rev-parse", "HEAD")
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(
            f"Refusing capture from branch {branch!r}; expected {EXPECTED_BRANCH!r}"
        )
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError(f"Unexpected git commit identity: {commit!r}")
    return branch, commit


def _write_new_text(path: Path, text: str) -> None:
    path = _ensure_debug_path(path)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing compatibility artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    if tmp.exists():
        raise FileExistsError(f"Refusing to reuse temporary artifact path: {tmp}")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _artifact_paths(capture_id: str) -> dict[str, str]:
    run_dir = _run_directory(capture_id)
    values = {
        "runDirectory": run_dir,
        "captureManifest": run_dir / "fresh-capture.json",
        "rawAttackCache": run_dir / "fresh-raw-attack-cache.json",
        "packageInventory": run_dir / "package-inventory.txt",
        "runtimeFingerprint": run_dir / "runtime-fingerprint.json",
        "modelCacheManifest": run_dir / "model-cache-manifest.json",
    }
    return {
        key: str(_ensure_debug_path(path).relative_to(REPO_ROOT.resolve()))
        for key, path in values.items()
    }


def _remote_file_sha(module: Any) -> str:
    import inspect

    source_path = inspect.getsourcefile(module)
    if not source_path:
        raise RuntimeError(f"Cannot resolve source path for module {module!r}")
    path = Path(source_path)
    if not path.exists():
        raise RuntimeError(f"Resolved module source is missing: {path}")
    return _sha256_file(path)


def _package_inventory() -> list[dict[str, str]]:
    from importlib import metadata

    rows: list[dict[str, str]] = []
    for dist in metadata.distributions():
        name = str(dist.metadata.get("Name") or "").strip()
        version = str(dist.version or "").strip()
        if not name or not version:
            continue
        rows.append({"name": name, "version": version})
    rows.sort(key=lambda row: (_normalized_package_name(row["name"]), row["version"]))
    return rows


def _nvidia_driver_version() -> str | None:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return lines[0] if lines else None


def _runtime_identity(installed_package_inventory_sha256: str) -> dict[str, Any]:
    from importlib import metadata
    import platform

    import onnxruntime as ort
    import torch

    cuda_available = bool(torch.cuda.is_available())
    capability = torch.cuda.get_device_capability(0) if cuda_available else None
    cuda_matmul = getattr(getattr(torch.backends, "cuda", None), "matmul", None)
    runtime: dict[str, Any] = {
        "runtimeFingerprintSha256": None,
        "modalImageIdOrDigest": os.environ.get("MODAL_IMAGE_ID")
        or os.environ.get("MODAL_IMAGE_DIGEST"),
        "pythonVersion": platform.python_version(),
        "platform": platform.platform(),
        "audioSeparatorVersion": metadata.version("audio-separator"),
        "torchVersion": str(torch.__version__),
        "torchCudaVersion": None if torch.version.cuda is None else str(torch.version.cuda),
        "cudnnVersion": (
            None
            if not hasattr(torch.backends, "cudnn")
            else torch.backends.cudnn.version()
        ),
        "onnxRuntimeVersion": str(ort.__version__),
        "onnxProviders": list(ort.get_available_providers()),
        "gpuName": torch.cuda.get_device_name(0) if cuda_available else None,
        "gpuComputeCapability": (
            None if capability is None else f"{int(capability[0])}.{int(capability[1])}"
        ),
        "nvidiaDriverVersion": _nvidia_driver_version(),
        "torchDeterministicAlgorithmsEnabled": bool(
            torch.are_deterministic_algorithms_enabled()
        ),
        "torchCudnnDeterministic": bool(
            getattr(torch.backends.cudnn, "deterministic", False)
        ),
        "torchCudnnBenchmark": bool(getattr(torch.backends.cudnn, "benchmark", False)),
        "torchAllowTf32Matmul": (
            None if cuda_matmul is None else bool(cuda_matmul.allow_tf32)
        ),
        "torchAllowTf32Cudnn": bool(getattr(torch.backends.cudnn, "allow_tf32", False)),
    }
    if runtime["audioSeparatorVersion"] != EXPECTED_AUDIO_SEPARATOR_VERSION:
        raise RuntimeError(
            "Fresh capture image lost audio-separator=="
            f"{EXPECTED_AUDIO_SEPARATOR_VERSION}: {runtime['audioSeparatorVersion']}"
        )
    runtime_for_digest = dict(runtime)
    runtime_for_digest.pop("runtimeFingerprintSha256", None)
    runtime["runtimeFingerprintSha256"] = _canonical_sha256(
        {
            "runtimeIdentity": runtime_for_digest,
            "installedPackageInventorySha256": installed_package_inventory_sha256,
        }
    )
    return runtime


def _model_cache_files(model_dir: Path) -> list[dict[str, Any]]:
    if not model_dir.exists() or not model_dir.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(model_dir.rglob("*")):
        if not path.is_file():
            continue
        rows.append(
            {
                "path": str(path),
                "size": int(path.stat().st_size),
                "sha256": _sha256_file(path),
            }
        )
    rows.sort(key=lambda row: str(row["path"]))
    return rows


def _basic_pitch_model_identity() -> dict[str, Any]:
    try:
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except Exception as exc:
        return {
            "basicPitchModelPath": None,
            "basicPitchModelSha256": None,
            "basicPitchModelIdentityError": str(exc),
        }
    path = Path(str(ICASSP_2022_MODEL_PATH))
    if path.is_file():
        return {
            "basicPitchModelPath": str(path),
            "basicPitchModelSha256": _sha256_file(path),
        }
    return {
        "basicPitchModelPath": str(path),
        "basicPitchModelSha256": None,
    }


def _pcm_identity(path: Path) -> dict[str, Any]:
    import soundfile as sf

    audio, sample_rate = sf.read(str(path), dtype="int16", always_2d=True)
    return {
        "wavSha256": _sha256_file(path),
        "decodedPcmSha256": hashlib.sha256(audio.tobytes()).hexdigest(),
        "sampleRate": int(sample_rate),
        "frames": int(audio.shape[0]),
        "channels": int(audio.shape[1]),
    }


def _build_historical_intro_cache(
    *,
    normalized: Path,
    direct: Path,
    cascade: Path,
    source_metadata: dict[str, Any],
) -> dict[str, Any]:
    from collections import Counter

    from v143_candidate_timing_adapter import (
        GUITAR_MIDI_MAX,
        GUITAR_MIDI_MIN,
        HISTORICAL_WIDE_RECALL_SWEEPS,
        build_subdivision_grid,
        nearest_timing_slot,
        note_events_from_predict,
        parse_note_event,
    )
    from v143_reference_free_timing import estimate_reference_free_timing

    timing = estimate_reference_free_timing(normalized)
    grid = build_subdivision_grid(**timing.candidate_adapter_kwargs())

    raw_events: list[dict[str, Any]] = []
    sweep_counts: Counter[str] = Counter()
    stem_counts: Counter[str] = Counter()
    rejected_outside_wide_grid = 0
    rejected_outside_intro = 0
    event_id = 0

    for stem_index, stem in enumerate((direct, cascade)):
        stem_name = f"stem{stem_index}:{stem.name}"
        for sweep_name, onset_threshold, frame_threshold in HISTORICAL_WIDE_RECALL_SWEEPS:
            detected = note_events_from_predict(
                stem,
                onset_threshold=float(onset_threshold),
                frame_threshold=float(frame_threshold),
            )
            for raw_index, raw in enumerate(detected):
                parsed = parse_note_event(raw)
                if parsed is None:
                    continue
                onset, offset, midi, amplitude = parsed
                if midi < GUITAR_MIDI_MIN or midi > GUITAR_MIDI_MAX:
                    continue

                wide_nearest = nearest_timing_slot(
                    onset,
                    grid,
                    max_grid_error_seconds=WIDE_GRID_TOLERANCE_SECONDS,
                )
                if wide_nearest is None:
                    rejected_outside_wide_grid += 1
                    continue
                slot, wide_error = wide_nearest
                if not INTRO_FIRST_MEASURE <= int(slot.measure) <= INTRO_LAST_MEASURE:
                    rejected_outside_intro += 1
                    continue

                production_nearest = nearest_timing_slot(
                    onset,
                    grid,
                    max_grid_error_seconds=PRODUCTION_GRID_TOLERANCE_SECONDS,
                )
                production_accepted = production_nearest is not None

                event_id += 1
                sweep_counts[str(sweep_name)] += 1
                stem_counts[stem_name] += 1
                raw_events.append(
                    {
                        "eventId": event_id,
                        "stemIndex": int(stem_index),
                        "stemName": stem_name,
                        "sweepName": str(sweep_name),
                        "onsetThreshold": float(onset_threshold),
                        "frameThreshold": float(frame_threshold),
                        "rawIndex": int(raw_index),
                        "midi": int(midi),
                        "amplitude": float(amplitude),
                        "onsetTime": float(onset),
                        "offsetTime": float(offset),
                        "duration": float(max(0.0, offset - onset)),
                        "nearestMeasure": int(slot.measure),
                        "nearestStep": int(slot.step),
                        "nearestGlobalStep": int(slot.global_step),
                        "nearestGridTime": float(slot.time_seconds),
                        "signedGridResidualSeconds": float(onset - slot.time_seconds),
                        "absoluteGridResidualSeconds": float(wide_error),
                        "withinProductionGridTolerance": bool(production_accepted),
                    }
                )

    intro_grid = [
        {
            "globalStep": int(slot.global_step),
            "measure": int(slot.measure),
            "step": int(slot.step),
            "timeSeconds": float(slot.time_seconds),
        }
        for slot in grid
        if INTRO_FIRST_MEASURE <= int(slot.measure) <= INTRO_LAST_MEASURE
    ]

    if len(intro_grid) != 244:
        raise RuntimeError(
            f"Fresh intro grid lost historical 244-row bar phase: {len(intro_grid)}"
        )

    return {
        "cacheVersion": 1,
        "scope": "professional-measures-1-16-raw-reference-free-attacks",
        "timing": {
            "tempoBpm": float(timing.tempo_bpm),
            "firstBeatInMeasure": int(timing.first_beat_in_measure),
            "downbeatIndexMod4": int(timing.downbeat_index_mod4),
            "beatConfidence": float(timing.beat_confidence),
            "barConfidence": float(timing.bar_confidence),
            "beatTimes": [float(value) for value in timing.beat_times],
        },
        "grid": intro_grid,
        "events": raw_events,
        "rawEventCount": len(raw_events),
        "productionAcceptedEventCount": sum(
            1 for event in raw_events if event["withinProductionGridTolerance"]
        ),
        "sweepEventCounts": dict(sorted(sweep_counts.items())),
        "stemEventCounts": dict(sorted(stem_counts.items())),
        "candidateStemCount": 2,
        "rejectedOutsideWideGrid": int(rejected_outside_wide_grid),
        "rejectedOutsideIntro": int(rejected_outside_intro),
        # Preserve the archived producer's exact key lookup. modal_analyzer
        # exposes durationSeconds, so the historical source wrote null here.
        "sourceDurationSeconds": source_metadata.get("duration"),
        "wideGridToleranceSeconds": WIDE_GRID_TOLERANCE_SECONDS,
        "productionGridToleranceSeconds": PRODUCTION_GRID_TOLERANCE_SECONDS,
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


@app.function(image=capture_image, gpu="L4", timeout=1800, memory=12288)
def capture_fresh_compatibility(
    source_audio: bytes,
    suffix: str,
    capture_id: str,
    git_commit: str,
    source_audio_sha256: str,
) -> dict[str, Any]:
    """Create fresh compatibility evidence from exactly one separator pass."""

    if not source_audio:
        raise ValueError("Compatibility source audio is empty")
    if len(source_audio) > 50 * 1024 * 1024:
        raise ValueError("Compatibility source audio cannot exceed 50 MB")
    capture_id = _validate_capture_id(capture_id)
    if _sha256_bytes(source_audio) != source_audio_sha256:
        raise RuntimeError("Local/remote source audio SHA-256 mismatch")
    if _git_blob_sha1_bytes(source_audio) != EXPECTED_SOURCE_GIT_BLOB_SHA:
        raise RuntimeError("Source audio Git blob identity does not match the pinned baseline")

    import tempfile

    import modal_analyzer as legacy
    import v143_deterministic_separator
    import v143_production_separator
    import v143_seeded_audio_separator_cli
    from v143_deterministic_separator import build_deterministic_v143_stems

    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    packages = _package_inventory()
    package_inventory_sha = _canonical_sha256(packages)
    runtime_identity = _runtime_identity(package_inventory_sha)

    seeded_cli_source_sha = _remote_file_sha(v143_seeded_audio_separator_cli)
    production_separator_source_sha = _remote_file_sha(v143_deterministic_separator)

    with tempfile.TemporaryDirectory(prefix="v143-intro-compatibility-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        normalized = root / "normalized.wav"
        stems_dir = root / "single-separator-pass"
        source.write_bytes(source_audio)

        source_metadata = legacy.inspect_audio_file(str(source))
        legacy.validate_audio_metadata(source_metadata)
        legacy.normalize_audio_file(str(source), str(normalized))

        recorded_commands: list[list[str]] = []
        original_run_separator = v143_production_separator.run_separator

        def recording_run_separator(command: list[str]):
            recorded_commands.append([str(value) for value in command])
            return original_run_separator(command)

        v143_production_separator.run_separator = recording_run_separator
        try:
            # Non-negotiable provenance guard: this is the only separator build
            # in this producer. The exact returned files are reused below.
            stems = build_deterministic_v143_stems(normalized, stems_dir)
        finally:
            v143_production_separator.run_separator = original_run_separator

        if len(recorded_commands) != 3:
            raise RuntimeError(
                f"Expected exactly three CLI commands in one frozen graph, got {len(recorded_commands)}"
            )

        direct = Path(str(stems.get("directGuitar") or ""))
        cascade = Path(str(stems.get("cascadeGuitar") or ""))
        for label, path in (("direct", direct), ("cascade", cascade)):
            if not path.exists() or path.stat().st_size <= 0:
                raise RuntimeError(f"Fresh {label} stem missing: {path}")
        if direct.name != "direct-demucs6s-guitar.wav":
            raise RuntimeError(f"Unexpected direct stem name: {direct.name}")
        if cascade.name != "bsroformer-demucs6s-guitar.wav":
            raise RuntimeError(f"Unexpected cascade stem name: {cascade.name}")
        if stems.get("deterministic") is not True or stems.get("referenceFree") is not True:
            raise RuntimeError("Fresh separator lost deterministic/reference-free invariants")

        direct_identity = _pcm_identity(direct)
        cascade_identity = _pcm_identity(cascade)

        model_files = _model_cache_files(AUDIO_SEPARATOR_MODEL_DIR)
        captured_model_names = {Path(str(row["path"])).name for row in model_files}
        model_capture_complete = {
            EXPECTED_BS_ROFORMER_MODEL,
            EXPECTED_DEMUCS_MODEL,
        }.issubset(captured_model_names)
        model_manifest_sha = _canonical_sha256(model_files) if model_files else None

        # Build the raw-attack cache from the same exact stem files whose
        # WAV/decoded-PCM identities were captured above. No second separation.
        raw_cache = _build_historical_intro_cache(
            normalized=normalized,
            direct=direct,
            cascade=cascade,
            source_metadata=source_metadata,
        )
        raw_cache_text = json.dumps(raw_cache, indent=2) + "\n"
        raw_cache_sha = _sha256_bytes(raw_cache_text.encode("utf-8"))

        direct_key = "stem0:direct-demucs6s-guitar.wav"
        cascade_key = "stem1:bsroformer-demucs6s-guitar.wav"
        stem_counts = dict(raw_cache.get("stemEventCounts") or {})

        model_identity = {
            "bsRoformerModelIdentifier": EXPECTED_BS_ROFORMER_MODEL,
            "demucsModelIdentifier": EXPECTED_DEMUCS_MODEL,
            "audioSeparatorModelDir": str(AUDIO_SEPARATOR_MODEL_DIR),
            "modelCacheManifestSha256": model_manifest_sha,
            "modelCacheFiles": model_files,
            "modelPayloadCaptureComplete": bool(model_capture_complete),
            **_basic_pitch_model_identity(),
        }

        manifest: dict[str, Any] = {
            "captureIdentity": {
                "captureId": capture_id,
                "createdAtUtc": created_at,
                "gitBranch": EXPECTED_BRANCH,
                "gitCommit": git_commit,
                "sourceAudioGitBlobSha": EXPECTED_SOURCE_GIT_BLOB_SHA,
                "sourceAudioSha256": source_audio_sha256,
            },
            "runtimeIdentity": runtime_identity,
            "resolvedDependencyIdentity": {
                "installedPackageInventorySha256": package_inventory_sha,
                "installedPackageInventory": packages,
            },
            "modelPayloadIdentity": model_identity,
            "separatorInvocation": {
                "seed": 143,
                "demucsShifts": 1,
                "demucsOverlap": 0.10,
                "demucsSegmentSize": 6,
                "roformerBatchSize": 1,
                "seededCliSourceSha256": seeded_cli_source_sha,
                "productionSeparatorSourceSha256": production_separator_source_sha,
                "directCommand": recorded_commands[0],
                "cascadeCommands": recorded_commands[1:],
                "singleSeparatorGraphExecution": True,
                "commandCount": len(recorded_commands),
            },
            "stemIdentity": {
                "decodedPcmHashMethod": DECODED_PCM_HASH_METHOD,
                "directWavSha256": direct_identity["wavSha256"],
                "directDecodedPcmSha256": direct_identity["decodedPcmSha256"],
                "directDecodedSampleRate": direct_identity["sampleRate"],
                "directDecodedFrames": direct_identity["frames"],
                "directDecodedChannels": direct_identity["channels"],
                "cascadeWavSha256": cascade_identity["wavSha256"],
                "cascadeDecodedPcmSha256": cascade_identity["decodedPcmSha256"],
                "cascadeDecodedSampleRate": cascade_identity["sampleRate"],
                "cascadeDecodedFrames": cascade_identity["frames"],
                "cascadeDecodedChannels": cascade_identity["channels"],
            },
            "introFingerprint": {
                "rawAttackCacheSha256": raw_cache_sha,
                "rawEventCount": int(raw_cache["rawEventCount"]),
                "directStemEventCount": int(stem_counts.get(direct_key, 0)),
                "cascadeStemEventCount": int(stem_counts.get(cascade_key, 0)),
                "sweepEventCounts": dict(raw_cache.get("sweepEventCounts") or {}),
                "gridRowCount": len(raw_cache.get("grid") or []),
            },
            "downstreamFrozenReplay": {
                "gridRowCount": None,
                "onsetCount": None,
                "onsetVectorCount": None,
                "gridFeatureCount": None,
                "sequenceFeatureCount": None,
                "contextualCarrierCount": None,
                "frozenDecisionDigest": None,
                "frozenScoreDigest": None,
            },
            "attestations": {
                "freshCompatibilityEvidenceOnly": True,
                "historicalProvenanceClaimed": False,
                "productionModified": False,
                "liveEndpointModified": False,
                "professionalReferenceUsedAtRuntime": False,
                "historicalArtifactsOverwritten": False,
            },
            "artifactPaths": _artifact_paths(capture_id),
        }

        compressed_cache = gzip.compress(raw_cache_text.encode("utf-8"), compresslevel=9)
        return {
            "manifest": manifest,
            "rawCacheGzipBase64": base64.b64encode(compressed_cache).decode("ascii"),
            "runtimeFingerprint": runtime_identity,
            "modelCacheManifest": {
                "audioSeparatorModelDir": str(AUDIO_SEPARATOR_MODEL_DIR),
                "modelCacheManifestSha256": model_manifest_sha,
                "modelPayloadCaptureComplete": bool(model_capture_complete),
                "files": model_files,
            },
            "packageInventoryText": "".join(
                f"{row['name']}=={row['version']}\n" for row in packages
            ),
        }


@app.local_entrypoint(name="capture")
def capture(
    audio_path: str = str(SOURCE_AUDIO),
    capture_id: str = "",
) -> None:
    """Run one explicitly requested fresh compatibility capture."""

    branch, git_commit = _local_checkout_identity()
    source = Path(audio_path)
    if source.resolve() != SOURCE_AUDIO.resolve():
        raise RuntimeError(
            "Compatibility capture is pinned to public/gomywayfullaitest.m4a"
        )
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Compatibility source audio missing or empty: {source}")

    source_audio = source.read_bytes()
    source_audio_sha = _sha256_bytes(source_audio)
    if _git_blob_sha1_bytes(source_audio) != EXPECTED_SOURCE_GIT_BLOB_SHA:
        raise RuntimeError("Pinned source audio Git blob identity changed")

    capture_id = _validate_capture_id(capture_id) if capture_id else _new_capture_id()
    run_dir = _run_directory(capture_id)
    if run_dir.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing compatibility run: {run_dir}"
        )

    result = capture_fresh_compatibility.remote(
        source_audio,
        source.suffix,
        capture_id,
        git_commit,
        source_audio_sha,
    )

    manifest = dict(result["manifest"])
    artifact_paths = dict(manifest["artifactPaths"])
    raw_cache_text = gzip.decompress(
        base64.b64decode(str(result["rawCacheGzipBase64"]))
    ).decode("utf-8")
    if _sha256_bytes(raw_cache_text.encode("utf-8")) != manifest["introFingerprint"][
        "rawAttackCacheSha256"
    ]:
        raise RuntimeError("Returned raw cache bytes do not match manifest SHA-256")

    files = {
        "packageInventory": str(result["packageInventoryText"]),
        "runtimeFingerprint": json.dumps(result["runtimeFingerprint"], indent=2) + "\n",
        "modelCacheManifest": json.dumps(result["modelCacheManifest"], indent=2) + "\n",
        "rawAttackCache": raw_cache_text,
        "captureManifest": json.dumps(manifest, indent=2) + "\n",
    }
    for key in (
        "packageInventory",
        "runtimeFingerprint",
        "modelCacheManifest",
        "rawAttackCache",
        "captureManifest",
    ):
        path = REPO_ROOT / artifact_paths[key]
        _write_new_text(path, files[key])

    print(json.dumps(
        {
            "status": "FRESH_COMPATIBILITY_CAPTURE_SAVED",
            "captureId": capture_id,
            "branch": branch,
            "gitCommit": git_commit,
            "runDirectory": artifact_paths["runDirectory"],
            "rawEventCount": manifest["introFingerprint"]["rawEventCount"],
            "rawAttackCacheSha256": manifest["introFingerprint"]["rawAttackCacheSha256"],
            "modelPayloadCaptureComplete": manifest["modelPayloadIdentity"][
                "modelPayloadCaptureComplete"
            ],
            "historicalProvenanceClaimed": False,
            "productionModified": False,
        },
        indent=2,
    ))


if __name__ == "__main__":
    pass
