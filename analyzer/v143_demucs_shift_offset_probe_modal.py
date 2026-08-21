from __future__ import annotations

import concurrent.futures
import hashlib
import json
import os
import sys
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
from v143_production_separator import (
    normalize_input_audio,
    separate_demucs_guitar,
    separate_roformer_instrumental,
)
from v143_section3_hashseed_ab_probe_modal import KNOWN_CASCADE, KNOWN_DIRECT, _family
from v143_seeded_separator import seeded_audio_separator_cli


app = modal.App("dadrock-v143-demucs-shift-offset-probe")
probe_image = diagnostic_image.add_local_python_source(
    "v143_demucs_shift_offset_probe_modal",
    "v143_shift_trace_audio_separator_cli",
    "v143_seeded_audio_separator_cli",
    "v143_seeded_separator",
    "v143_contextual_prune_historical_band_diagnostic_modal",
    "v143_contextual_prune_section3_repeatability_modal",
    "v143_section3_hashseed_ab_probe_modal",
    "v143_production_separator",
)

BATCH_SIZE = 4
MAX_BATCHES = 3
SEED = "143"
EXPECTED_SHIFT_MAX = 22050  # 0.5 s at the frozen 44.1 kHz Demucs sample rate.


def _read_trace(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _shift_values(rows: list[dict[str, Any]]) -> list[int]:
    return [
        int(row["value"])
        for row in rows
        if int(row.get("a", -1)) == 0 and int(row.get("b", -1)) == EXPECTED_SHIFT_MAX
    ]


def _counts(values: list[str]) -> dict[str, int]:
    return {value: values.count(value) for value in sorted(set(values))}


def _sequences_by_family(workers: list[dict[str, Any]], key: str) -> dict[str, list[list[int]]]:
    result: dict[str, list[list[int]]] = {}
    for family in sorted({str(row["directFamily"]) for row in workers}):
        unique = {
            tuple(int(v) for v in row[key])
            for row in workers
            if str(row["directFamily"]) == family
        }
        result[family] = [list(values) for values in sorted(unique)]
    return result


@app.function(image=probe_image, gpu="L4", timeout=1800, memory=12288)
def trace_worker(source_audio: bytes, suffix: str, worker_index: int) -> dict[str, Any]:
    if not source_audio:
        raise ValueError("Probe audio is empty")

    with tempfile.TemporaryDirectory(prefix=f"v143-shift-trace-{worker_index}-") as temp_dir:
        root = Path(temp_dir)
        source = root / f"uploaded{_safe_suffix(suffix)}"
        research_normalized = root / "research-normalized.wav"
        source.write_bytes(source_audio)
        _research_normalize_audio(source, research_normalized)

        work = root / "separator"
        normalized = normalize_input_audio(research_normalized, work / "normalized")
        regular_cli = seeded_audio_separator_cli()
        trace_cli = [sys.executable, "-m", "v143_shift_trace_audio_separator_cli"]
        direct_trace_path = root / "direct-shift-trace.jsonl"
        cascade_trace_path = root / "cascade-shift-trace.jsonl"

        saved = {name: os.environ.get(name) for name in (
            "PYTHONHASHSEED",
            "V143_SEPARATOR_SEED",
            "V143_SHIFT_TRACE_PATH",
            "V143_SHIFT_TRACE_STAGE",
        )}
        try:
            os.environ["PYTHONHASHSEED"] = SEED
            os.environ["V143_SEPARATOR_SEED"] = SEED

            os.environ["V143_SHIFT_TRACE_PATH"] = str(direct_trace_path)
            os.environ["V143_SHIFT_TRACE_STAGE"] = "direct"
            direct = separate_demucs_guitar(trace_cli, normalized, work / "direct")

            os.environ.pop("V143_SHIFT_TRACE_PATH", None)
            os.environ.pop("V143_SHIFT_TRACE_STAGE", None)
            roformer = separate_roformer_instrumental(regular_cli, normalized, work / "roformer")

            os.environ["V143_SHIFT_TRACE_PATH"] = str(cascade_trace_path)
            os.environ["V143_SHIFT_TRACE_STAGE"] = "cascade"
            cascade = separate_demucs_guitar(trace_cli, Path(roformer["path"]), work / "cascade")
        finally:
            for name, value in saved.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

        direct_pcm = _pcm_sha256(Path(direct["path"]))
        roformer_pcm = _pcm_sha256(Path(roformer["path"]))
        cascade_pcm = _pcm_sha256(Path(cascade["path"]))
        direct_trace = _read_trace(direct_trace_path)
        cascade_trace = _read_trace(cascade_trace_path)
        direct_family = _family(direct_pcm["sha256"], KNOWN_DIRECT)
        cascade_family = _family(cascade_pcm["sha256"], KNOWN_CASCADE)

        return {
            "worker": int(worker_index),
            "modalTaskId": os.environ.get("MODAL_TASK_ID"),
            "directFamily": direct_family,
            "cascadeFamily": cascade_family,
            "familyLockstep": direct_family == cascade_family,
            "directPcm": direct_pcm,
            "roformerPcm": roformer_pcm,
            "cascadePcm": cascade_pcm,
            "directTrace": direct_trace,
            "cascadeTrace": cascade_trace,
            "directShiftValues": _shift_values(direct_trace),
            "cascadeShiftValues": _shift_values(cascade_trace),
        }


@app.local_entrypoint(name="diagnose")
def diagnose(audio_path: str = "public/gomywayfullaitest.m4a") -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    payload = source.read_bytes()

    workers: list[dict[str, Any]] = []
    batches_run = 0
    for batch in range(MAX_BATCHES):
        start = batch * BATCH_SIZE + 1

        def invoke(offset: int) -> dict[str, Any]:
            return trace_worker.remote(payload, source.suffix, start + offset)

        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as pool:
            workers.extend(pool.map(invoke, range(BATCH_SIZE)))
        batches_run += 1
        families = {str(row["directFamily"]) for row in workers}
        if "A" in families and "B" in families:
            break

    workers.sort(key=lambda row: int(row["worker"]))
    direct_families = [str(row["directFamily"]) for row in workers]
    cascade_families = [str(row["cascadeFamily"]) for row in workers]
    roformer_hashes = {str(row["roformerPcm"]["sha256"]) for row in workers}
    direct_sequences = _sequences_by_family(workers, "directShiftValues")
    cascade_sequences = _sequences_by_family(workers, "cascadeShiftValues")

    both = "A" in direct_families and "B" in direct_families
    same_direct = None
    same_cascade = None
    if both:
        same_direct = direct_sequences.get("A") == direct_sequences.get("B")
        same_cascade = cascade_sequences.get("A") == cascade_sequences.get("B")

    result = {
        "schemaVersion": 1,
        "gate": "v143-demucs-shift-offset-probe",
        "executionStrategy": "adaptive-fixed-143-exact-demucs-randint-trace-with-unchanged-return-values",
        "batchSize": BATCH_SIZE,
        "maxBatches": MAX_BATCHES,
        "batchesRun": batches_run,
        "workerCount": len(workers),
        "sourceSha256": hashlib.sha256(payload).hexdigest(),
        "knownFamilies": {"direct": KNOWN_DIRECT, "cascade": KNOWN_CASCADE},
        "workers": workers,
        "summary": {
            "directFamilyCounts": _counts(direct_families),
            "cascadeFamilyCounts": _counts(cascade_families),
            "allDirectCascadeFamiliesLockstep": all(row["familyLockstep"] is True for row in workers),
            "bothKnownFamiliesObserved": both,
            "roformerPcmExactAcrossWorkers": len(roformer_hashes) == 1,
            "directShiftSequencesByFamily": direct_sequences,
            "cascadeShiftSequencesByFamily": cascade_sequences,
            "sameDirectShiftSequencesAcrossFamilies": same_direct,
            "sameCascadeShiftSequencesAcrossFamilies": same_cascade,
        },
        "inferenceGuide": {
            "differentShiftSequencesAcrossFamilies": "Python-random state consumed before Demucs shift selection is sufficient to explain the family split.",
            "sameShiftSequencesAcrossFamilies": "The family split occurs after shift selection; investigate GPU/kernel-level nondeterminism next.",
            "onlyOneFamilyObserved": "Inconclusive for family causality; rerun later without changing production.",
        },
        "invariants": {
            "traceWrapperReturnsOriginalRandintValueUnchanged": True,
            "pythonHashSeedAtChildStartup": 143,
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
