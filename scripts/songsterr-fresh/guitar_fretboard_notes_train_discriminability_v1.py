#!/usr/bin/env python3
"""Train-only physical-position discriminability probe for guitar-fretboard-notes.

NON_HOLDOUT feasibility research only. The pinned train split is the only remotely
retrievable corpus input. Reserved test/validation sources are rejected fail-closed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
import tempfile
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

DATASET_ID = "collegefishiesd/guitar-fretboard-notes"
DATASET_REVISION = "a33a26243e88e7ccd4893bee30eac3219ec8bef8"
TRAIN_PARQUET = "data/train-00000-of-00001.parquet"
TRAIN_URL = (
    f"https://huggingface.co/datasets/{DATASET_ID}/resolve/"
    f"{DATASET_REVISION}/{TRAIN_PARQUET}?download=true"
)
FEATURE_CONTRACT_ID = "gfn-train-position-features-v1"
ALLOWED_SOURCES = ("ele", "eqm", "eqm2")
RESERVED_SOURCES = ("deb", "ele_natural")
EXPECTED_ROW_COUNT = 234
EXPECTED_SAMPLE_RATE = 44100
EXPECTED_POSITIONS = {(s, f) for s in range(1, 7) for f in range(13)}
AUTHORIZATION_BOUNDARY = {
    "basicPitchAuthorized": False,
    "v6Authorized": False,
    "correctnessAuthorized": False,
    "modelValidationComplete": False,
    "customerEligibleEvents": 0,
    "mayAdvanceDelivery": False,
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_file(path: str | os.PathLike[str]) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _require_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{field} must be an integer")
    return int(value)


def validate_metadata_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"train row count must be {EXPECTED_ROW_COUNT}, got {len(rows)}")

    sources = {str(r.get("source")) for r in rows}
    if sources != set(ALLOWED_SOURCES):
        raise ValueError(f"train source set mismatch: {sorted(sources)}")
    if any(s in sources for s in RESERVED_SOURCES):
        raise ValueError("reserved source appeared in train study")

    identities: set[tuple[str, int, int]] = set()
    per_source_positions: dict[str, set[tuple[int, int]]] = defaultdict(set)
    per_source_count: Counter[str] = Counter()

    for row in rows:
        source = str(row.get("source"))
        string_number = _require_int(row.get("string_number"), "string_number")
        fret = _require_int(row.get("fret"), "fret")
        midi = _require_int(row.get("midi_number"), "midi_number")
        if not 1 <= string_number <= 6:
            raise ValueError("string_number outside 1..6")
        if not 0 <= fret <= 12:
            raise ValueError("fret outside 0..12")
        if not 40 <= midi <= 76:
            raise ValueError("midi_number outside 40..76")
        ident = (source, string_number, fret)
        if ident in identities:
            raise ValueError(f"duplicate identity: {ident}")
        identities.add(ident)
        per_source_positions[source].add((string_number, fret))
        per_source_count[source] += 1

    for source in ALLOWED_SOURCES:
        if per_source_count[source] != 78:
            raise ValueError(f"source {source} must have 78 rows")
        if per_source_positions[source] != EXPECTED_POSITIONS:
            raise ValueError(f"source {source} does not contain the complete fret-0..12 grid")

    return {
        "rowCount": len(rows),
        "observedSources": sorted(sources),
        "rowsPerSource": {s: per_source_count[s] for s in sorted(per_source_count)},
        "identityUnique": True,
        "completePositionGridPerSource": True,
    }


def decode_audio(audio_obj: Any) -> tuple[np.ndarray, int]:
    """Decode a Hugging Face parquet Audio struct without using datasets.Audio."""
    try:
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError("soundfile is required to decode corpus audio") from exc

    if not isinstance(audio_obj, dict):
        raise ValueError("audio field must be a struct/dict")
    audio_bytes = audio_obj.get("bytes")
    if audio_bytes is None:
        raise ValueError("audio bytes are absent from parquet row; path-only audio is not accepted")
    waveform, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float64", always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float64)
    if waveform.ndim != 1:
        raise ValueError("audio must decode as mono")
    if int(sample_rate) != EXPECTED_SAMPLE_RATE:
        raise ValueError(f"sample rate must be {EXPECTED_SAMPLE_RATE}")
    if waveform.size == 0 or not np.all(np.isfinite(waveform)):
        raise ValueError("waveform must be nonempty and finite")
    return waveform, int(sample_rate)


def _frame_rms_nonoverlap(x: np.ndarray, frame: int = 1024) -> np.ndarray:
    n = int(math.ceil(len(x) / frame))
    padded = np.pad(x, (0, n * frame - len(x)))
    frames = padded.reshape(n, frame)
    return np.sqrt(np.mean(frames * frames, axis=1))


def extract_features(waveform: np.ndarray, sample_rate: int, fundamental_hz: float) -> np.ndarray:
    if int(sample_rate) != EXPECTED_SAMPLE_RATE:
        raise ValueError("unexpected sample rate")
    x = np.asarray(waveform, dtype=np.float64)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise ValueError("waveform must be finite mono data")
    if not np.isfinite(fundamental_hz) or float(fundamental_hz) <= 0:
        raise ValueError("fundamental_hz must be positive and finite")

    x = x - np.mean(x)
    frame_rms = _frame_rms_nonoverlap(x, 1024)
    max_rms = float(np.max(frame_rms)) if frame_rms.size else 0.0
    if not np.isfinite(max_rms) or max_rms <= 0.0:
        raise ValueError("no positive finite RMS frame")
    threshold = 0.15 * max_rms
    onset_candidates = np.flatnonzero(frame_rms >= threshold)
    if onset_candidates.size == 0:
        raise ValueError("onset frame not found")
    start = int(onset_candidates[0]) * 1024

    segment = x[start : start + 65536]
    if segment.size < 65536:
        segment = np.pad(segment, (0, 65536 - segment.size))
    seg_rms = float(np.sqrt(np.mean(segment * segment)))
    if not np.isfinite(seg_rms) or seg_rms <= 0.0:
        raise ValueError("analysis segment has no positive finite RMS")
    segment = segment / seg_rms

    windowed = segment * np.hanning(segment.size)
    spectrum = np.fft.rfft(windowed)
    power = np.abs(spectrum) ** 2
    freqs = np.fft.rfftfreq(segment.size, d=1.0 / sample_rate)

    harmonic_logs: list[float | None] = []
    f0 = float(fundamental_hz)
    nyquist = sample_rate / 2.0
    cents_ratio = 2.0 ** (25.0 / 1200.0)
    for harmonic in range(1, 13):
        center = harmonic * f0
        if center >= nyquist:
            harmonic_logs.append(None)
            continue
        lower = center / cents_ratio
        upper = center * cents_ratio
        mask = (freqs >= lower) & (freqs <= upper)
        if not np.any(mask):
            harmonic_logs.append(None)
            continue
        band_power = float(np.sum(power[mask]))
        harmonic_logs.append(math.log(max(band_power, 1e-30)))

    finite_logs = [v for v in harmonic_logs if v is not None and np.isfinite(v)]
    if not finite_logs or harmonic_logs[0] is None:
        raise ValueError("fundamental harmonic feature unavailable")
    fill_value = float(min(finite_logs))
    harmonic = np.asarray([fill_value if v is None else float(v) for v in harmonic_logs], dtype=np.float64)
    harmonic = harmonic - harmonic[0]

    boundaries_ms = ((0, 100), (100, 300), (300, 700), (700, 1400))
    rms_values: list[float] = []
    for lo_ms, hi_ms in boundaries_ms:
        lo = int(round(sample_rate * lo_ms / 1000.0))
        hi = int(round(sample_rate * hi_ms / 1000.0))
        region = segment[lo:hi]
        rms_values.append(float(np.sqrt(np.mean(region * region))) if region.size else 0.0)
    denom = sum(rms_values) + 1e-12
    temporal = np.asarray([v / denom for v in rms_values], dtype=np.float64)

    features = np.concatenate([harmonic, temporal])
    if features.shape != (16,) or not np.all(np.isfinite(features)):
        raise ValueError("feature vector must be 16 finite values")
    return features


def _standardize_from_prototypes(prototypes: list[dict[str, Any]], queries: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    p = np.stack([np.asarray(r["features"], dtype=np.float64) for r in prototypes])
    q = np.stack([np.asarray(r["features"], dtype=np.float64) for r in queries])
    mean = np.mean(p, axis=0)
    std = np.std(p, axis=0, ddof=0)
    std = np.where(std < 1e-12, 1.0, std)
    return (p - mean) / std, (q - mean) / std


def evaluate_direction(feature_rows: list[dict[str, Any]], prototype_source: str, query_source: str) -> dict[str, Any]:
    prototypes = sorted(
        [r for r in feature_rows if r["source"] == prototype_source],
        key=lambda r: (r["string_number"], r["fret"]),
    )
    queries_all = sorted(
        [r for r in feature_rows if r["source"] == query_source],
        key=lambda r: (r["string_number"], r["fret"]),
    )
    if len(prototypes) != 78 or len(queries_all) != 78:
        raise ValueError("each comparison source must have 78 feature rows")

    candidate_indices_by_midi: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(prototypes):
        candidate_indices_by_midi[int(row["midi_number"])].append(idx)
    eligible_queries = [q for q in queries_all if len(candidate_indices_by_midi[int(q["midi_number"])]) >= 2]
    if not eligible_queries:
        raise ValueError("no same-pitch ambiguous-position queries")

    pz, qz = _standardize_from_prototypes(prototypes, eligible_queries)
    correct = 0
    chance_terms: list[float] = []
    confusion: Counter[tuple[int, int]] = Counter()
    per_midi: dict[int, dict[str, int]] = defaultdict(lambda: {"queries": 0, "correct": 0, "candidateCount": 0})

    for q_idx, query in enumerate(eligible_queries):
        midi = int(query["midi_number"])
        candidate_indices = candidate_indices_by_midi[midi]
        candidates = []
        for p_idx in candidate_indices:
            distance = float(np.linalg.norm(qz[q_idx] - pz[p_idx]))
            pr = prototypes[p_idx]
            candidates.append((distance, int(pr["string_number"]), int(pr["fret"]), p_idx))
        candidates.sort(key=lambda x: (x[0], x[1], x[2]))
        _, predicted_string, predicted_fret, _ = candidates[0]
        true_string = int(query["string_number"])
        true_fret = int(query["fret"])
        is_correct = predicted_string == true_string and predicted_fret == true_fret
        correct += int(is_correct)
        chance_terms.append(1.0 / len(candidate_indices))
        confusion[(true_string, predicted_string)] += 1
        per_midi[midi]["queries"] += 1
        per_midi[midi]["correct"] += int(is_correct)
        per_midi[midi]["candidateCount"] = len(candidate_indices)

    n = len(eligible_queries)
    accuracy = correct / n
    chance = float(np.mean(chance_terms))
    return {
        "prototypeSource": prototype_source,
        "querySource": query_source,
        "eligibleQueryCount": n,
        "correctCount": correct,
        "exactPositionAccuracy": accuracy,
        "chanceBaseline": chance,
        "accuracyLiftOverChance": accuracy - chance,
        "confusionTrueToPredictedString": {
            f"{a}->{b}": confusion[(a, b)] for a, b in sorted(confusion)
        },
        "perMidi": {str(m): per_midi[m] for m in sorted(per_midi)},
    }


def evaluate_primary(feature_rows: list[dict[str, Any]]) -> dict[str, Any]:
    forward = evaluate_direction(feature_rows, "eqm", "eqm2")
    reverse = evaluate_direction(feature_rows, "eqm2", "eqm")
    total_n = forward["eligibleQueryCount"] + reverse["eligibleQueryCount"]
    total_correct = forward["correctCount"] + reverse["correctCount"]
    pooled_accuracy = total_correct / total_n
    pooled_chance = (
        forward["chanceBaseline"] * forward["eligibleQueryCount"]
        + reverse["chanceBaseline"] * reverse["eligibleQueryCount"]
    ) / total_n
    return {
        "directions": [forward, reverse],
        "pooled": {
            "eligibleQueryCount": total_n,
            "correctCount": total_correct,
            "exactPositionAccuracy": pooled_accuracy,
            "chanceBaseline": pooled_chance,
            "accuracyLiftOverChance": pooled_accuracy - pooled_chance,
        },
    }


def download_train_parquet(destination: str | os.PathLike[str]) -> None:
    req = urllib.request.Request(TRAIN_URL, headers={"User-Agent": "songsterr-fresh-gfn-v1/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response, open(destination, "wb") as out:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)


def load_train_rows(parquet_path: str | os.PathLike[str]) -> list[dict[str, Any]]:
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("pyarrow is required to read the pinned train parquet") from exc
    table = pq.read_table(parquet_path)
    rows = table.to_pylist()
    if not isinstance(rows, list):
        raise ValueError("parquet decode did not produce rows")
    return rows


def run_study(parquet_path: str | os.PathLike[str]) -> dict[str, Any]:
    rows = load_train_rows(parquet_path)
    integrity = validate_metadata_rows(rows)
    feature_rows: list[dict[str, Any]] = []
    feature_failures: list[str] = []
    for row in rows:
        ident = f"{row.get('source')}:{row.get('string_number')}:{row.get('fret')}"
        try:
            waveform, sr = decode_audio(row.get("audio"))
            features = extract_features(waveform, sr, float(row["frequency"]))
        except Exception as exc:
            feature_failures.append(f"{ident}:{type(exc).__name__}:{exc}")
            continue
        feature_rows.append({
            "source": str(row["source"]),
            "string_number": int(row["string_number"]),
            "fret": int(row["fret"]),
            "midi_number": int(row["midi_number"]),
            "features": [float(v) for v in features],
        })

    if feature_failures:
        raise ValueError("feature extraction failures: " + " | ".join(feature_failures[:10]))
    if len(feature_rows) != EXPECTED_ROW_COUNT:
        raise ValueError("feature row count mismatch")

    primary = evaluate_primary(feature_rows)
    return {
        "contract": "songsterr-fresh-gfn-train-position-discriminability-v1",
        "studyStage": "NON_HOLDOUT_EXTERNAL_CORPUS_FEASIBILITY",
        "datasetId": DATASET_ID,
        "datasetRevision": DATASET_REVISION,
        "datasetSplitAccessed": "train",
        "reservedSplitsAccessed": False,
        "reservedSourcesAccessed": False,
        "featureContractId": FEATURE_CONTRACT_ID,
        "trainParquetSha256": sha256_file(parquet_path),
        "integrity": integrity,
        "featureExtractionFailureCount": 0,
        "primaryCrossSessionResult": primary,
        "interpretation": "DESCRIPTIVE_NON_HOLDOUT_FEASIBILITY_ONLY",
        **AUTHORIZATION_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-parquet", help="Use an already-downloaded pinned train parquet")
    parser.add_argument("--output", required=True, help="Canonical result JSON output path")
    args = parser.parse_args()

    temp_path: str | None = None
    try:
        if args.local_parquet:
            parquet_path = args.local_parquet
        else:
            fd, temp_path = tempfile.mkstemp(prefix="gfn-train-", suffix=".parquet")
            os.close(fd)
            download_train_parquet(temp_path)
            parquet_path = temp_path
        result = run_study(parquet_path)
        output_bytes = canonical_json_bytes(result)
        Path(args.output).write_bytes(output_bytes)
        print(output_bytes.decode("utf-8"))
        return 0
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
