from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import modal

from v143_contextual_prune_historical_band_diagnostic_modal import (
    _research_normalize_audio,
    _safe_suffix,
    diagnostic_image,
)
from v143_contextual_prune_section3_repeatability_modal import _pcm_sha256


app = modal.App("dadrock-v143-section3-hashseed-ab-probe")
probe_image = diagnostic_image.add_local_python_source(
    "v143_contextual_prune_historical_band_diagnostic_modal",
    "v143_contextual_prune_section3_repeatability_modal",
)

LEGACY_WORKERS = 4
FIXED_WORKERS = 2
SEPARATOR_SEED = "143"

KNOWN_DIRECT = {
    "A": "30cffcc2e472abe6d613b3853295c47b71ae8c4318f8709c8c9d45d69d9351f8",
    "B": "1542856aca8275c727e6c77edd941588aa359b65b8b897c1b3ada2926f2d579e",
}
KNOWN_CASCADE = {
    "A": "68a1c75e59bf45fbae340938e580575c043e7a94a70e7be2361e4c2d4621cb56",
    "B": "e26f7a430b835adcd7a284db8a18c3aa93632b81e1c1a653eeffa16c02a62bc3",
}


def _family(value: str, known: dict[str, str]) -> str:
    for label, expected in known.items():
        if value == expected:
            return label
    return "other"


def _build_three_stage_stems(input_audio: Path, root: Path, mode: str) -> dict[str, Any]:
    """Re-run the frozen separator graph with one controlled startup-hash difference.

    Both modes use the exact same seeded child CLI, model files, Demucs parameters,
    BS-RoFormer parameters, and V143_SEPARATOR_SEED=143. The only manipulated
    variable is whether PYTHONHASHSEED is absent at child interpreter startup
    (legacy behavior) or fixed to 143 (current deterministic wrapper behavior).
    """
    from v143_production_separator import (
        normalize_input_audio,
        separate_demucs_guitar,
        separate_roformer_instrumental,
    )
    from v143_seeded_separator import seeded_audio_separator_cli

    if mode not in {"legacy-unset", "fixed-143"}:
        raise ValueError(f"Unsupported probe mode: {mode}")

    cli = seeded_audio_separator_cli()
    work = root / "work"
    normalized = normalize_input_audio(input_audio, work / "normalized")

    previous_hash = os.environ.get("PYTHONHASHSEED")
    previous_separator = os.environ.get("V143_SEPARATOR_SEED")
    try:
        if mode == "legacy-unset":
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = SEPARATOR_SEED
        os.environ["V143_SEPARATOR_SEED"] = SEPARATOR_SEED

        direct = separate_demucs_guitar(cli, normalized, work / "direct")
        roformer = separate_roformer_instrumental(cli, normalized, work / "roformer")
        cascade = separate_demucs_guitar(cli, Path(roformer["path"]), work / "cascade")
    finally:
        if previous_hash is None:
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = previous_hash
        if previous_separator is None:
            os.environ.pop("V143_SEPARATOR_SEED", None)
        else:
            os.environ["V143_SEPARATOR_SEED"] = previous_separator

    return {
        "direct": Path(direct["path"]),
        "roformer": Path(roformer["path"]),
        "cascade": Path(cascade["path"]),
    }


@app.function(image=probe_image, gpu="L4", timeout=1800, memory=12288)
def probe_worker(source_audio: bytes, suffix: str, worker_index: int, mode: str) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("Probe audio is empty")

    with tempfile.TemporaryDirectory(prefix=f"v143-hashseed-{mode}-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        research_normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, research_normalized)

        stems = _build_three_stage_stems(research_normalized, root / "separator", mode)
        direct_pcm = _pcm_sha256(stems["direct"])
        roformer_pcm = _pcm_sha256(stems["roformer"])
        cascade_pcm = _pcm_sha256(stems["cascade"])

        runtime: dict[str, Any] = {
            "modalTaskId": os.environ.get("MODAL_TASK_ID"),
            "mode": mode,
        }
        try:
            import torch

            runtime.update(
                {
                    "torch": str(torch.__version__),
                    "torchCuda": None if torch.version.cuda is None else str(torch.version.cuda),
                    "cudnn": int(torch.backends.cudnn.version()) if torch.backends.cudnn.version() is not None else None,
                    "deviceName": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                    "deviceCapability": list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None,
                }
            )
        except Exception as exc:
            runtime["torchIdentityError"] = f"{type(exc).__name__}: {exc}"

        return {
            "worker": int(worker_index),
            "mode": mode,
            "runtimeIdentity": runtime,
            "directPcm": direct_pcm,
            "roformerPcm": roformer_pcm,
            "cascadePcm": cascade_pcm,
            "directFamily": _family(direct_pcm["sha256"], KNOWN_DIRECT),
            "cascadeFamily": _family(cascade_pcm["sha256"], KNOWN_CASCADE),
            "historicalPcmPair": (
                direct_pcm["sha256"] == KNOWN_DIRECT["B"]
                and cascade_pcm["sha256"] == KNOWN_CASCADE["B"]
            ),
            "alternatePcmPair": (
                direct_pcm["sha256"] == KNOWN_DIRECT["A"]
                and cascade_pcm["sha256"] == KNOWN_CASCADE["A"]
            ),
        }


def _counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    values = [str(row[key]) for row in rows]
    return {value: values.count(value) for value in sorted(set(values))}


def _mode_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "workerCount": len(rows),
        "directFamilies": _counts(rows, "directFamily"),
        "cascadeFamilies": _counts(rows, "cascadeFamily"),
        "historicalPcmPairCount": sum(row["historicalPcmPair"] is True for row in rows),
        "alternatePcmPairCount": sum(row["alternatePcmPair"] is True for row in rows),
        "uniqueDirectPcm": sorted({row["directPcm"]["sha256"] for row in rows}),
        "uniqueRoformerPcm": sorted({row["roformerPcm"]["sha256"] for row in rows}),
        "uniqueCascadePcm": sorted({row["cascadePcm"]["sha256"] for row in rows}),
    }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    jobs = [
        *(('legacy-unset', index) for index in range(1, LEGACY_WORKERS + 1)),
        *(('fixed-143', index) for index in range(1, FIXED_WORKERS + 1)),
    ]

    def invoke(job: tuple[str, int]) -> dict[str, Any]:
        mode, index = job
        return probe_worker.remote(payload, source.suffix, index, mode)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        workers = list(pool.map(invoke, jobs))

    workers.sort(key=lambda row: (str(row["mode"]), int(row["worker"])))
    legacy = [row for row in workers if row["mode"] == "legacy-unset"]
    fixed = [row for row in workers if row["mode"] == "fixed-143"]

    result = {
        "schemaVersion": 1,
        "gate": "v143-section3-hashseed-ab-probe",
        "executionStrategy": "controlled-legacy-unset-vs-fixed-143-child-startup-hash-with-three-stage-pcm-fingerprints",
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "knownFamilies": {"direct": KNOWN_DIRECT, "cascade": KNOWN_CASCADE},
        "workers": workers,
        "legacyUnset": _mode_summary(legacy),
        "fixed143": _mode_summary(fixed),
        "inference": {
            "historicalFamilyObservedUnderLegacyUnset": any(row["historicalPcmPair"] for row in legacy),
            "historicalFamilyObservedUnderFixed143": any(row["historicalPcmPair"] for row in fixed),
            "alternateFamilyObservedUnderLegacyUnset": any(row["alternatePcmPair"] for row in legacy),
            "alternateFamilyObservedUnderFixed143": any(row["alternatePcmPair"] for row in fixed),
            "onlyManipulatedSeparatorVariable": "PYTHONHASHSEED presence/value at child interpreter startup",
        },
        "invariants": {
            "separatorSeed": 143,
            "demucsShifts": 1,
            "demucsOverlap": 0.10,
            "demucsSegmentSize": 6,
            "roformerBatchSize": 1,
            "professionalReferenceOpened": False,
            "runtimeLabelsRequired": False,
            "frozenModelModified": False,
            "frozenPredictionsModified": False,
            "thresholdsModified": False,
            "liveEndpointDeployedOrModified": False,
            "productionModified": False,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    pass
