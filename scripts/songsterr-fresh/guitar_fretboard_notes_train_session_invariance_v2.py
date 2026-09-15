#!/usr/bin/env python3
"""Train-only session-invariance probe for guitar-fretboard-notes.

NON_HOLDOUT feasibility research only. Only the pinned train parquet and sources
`ele`, `eqm`, and `eqm2` are permitted. Reserved sources fail closed.
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
from typing import Any

import numpy as np

DATASET_ID = "collegefishiesd/guitar-fretboard-notes"
DATASET_REVISION = "a33a26243e88e7ccd4893bee30eac3219ec8bef8"
TRAIN_PARQUET = "data/train-00000-of-00001.parquet"
TRAIN_URL = (
    f"https://huggingface.co/datasets/{DATASET_ID}/resolve/"
    f"{DATASET_REVISION}/{TRAIN_PARQUET}?download=true"
)
EXPECTED_TRAIN_PARQUET_SHA256 = "86ac522303251f2a5d77376261c23bf1af09b3c69183ad365b105cd230354add"
FEATURE_CONTRACT_ID = "gfn-train-position-features-v2"
NORMALIZATION_CONTRACT_ID = "gfn-train-session-robust-mad-v2"
ALLOWED_SOURCES = ("ele", "eqm", "eqm2")
RESERVED_SOURCES = ("deb", "ele_natural")
PRIMARY_DIRECTIONS = (("eqm", "eqm2"), ("eqm2", "eqm"))
DIAGNOSTIC_DIRECTIONS = (("eqm", "ele"), ("ele", "eqm"), ("eqm2", "ele"), ("ele", "eqm2"))
EXPECTED_ROW_COUNT = 234
EXPECTED_SAMPLE_RATE = 44100
EXPECTED_POSITIONS = {(s, f) for s in range(1, 7) for f in range(13)}
V1_POOLED_ACCURACY = 0.5367647058823529
V1_DIRECTIONAL_GAP = 0.13235294117647056
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


def validate_train_parquet_sha(path: str | os.PathLike[str]) -> str:
    actual = sha256_file(path)
    if actual != EXPECTED_TRAIN_PARQUET_SHA256:
        raise ValueError(
            "train parquet SHA-256 mismatch: "
            f"expected {EXPECTED_TRAIN_PARQUET_SHA256}, got {actual}"
        )
    return actual


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


def _source_normalization_stats(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[str]]:
    if matrix.ndim != 2 or matrix.shape[1] != 16 or matrix.shape[0] != 78:
        raise ValueError("source feature matrix must be 78x16")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("source feature matrix must be finite")

    median = np.median(matrix, axis=0)
    mad = np.median(np.abs(matrix - median), axis=0)
    scale = 1.4826 * mad
    fallback_std = np.std(matrix, axis=0, ddof=0)
    methods: list[str] = []
    resolved = scale.copy()
    for idx in range(16):
        if not np.isfinite(resolved[idx]) or resolved[idx] < 1e-9:
            if np.isfinite(fallback_std[idx]) and fallback_std[idx] >= 1e-9:
                resolved[idx] = fallback_std[idx]
                methods.append("std")
            else:
                resolved[idx] = 1.0
                methods.append("unit")
        else:
            methods.append("mad")
    if not np.all(np.isfinite(median)) or not np.all(np.isfinite(resolved)):
        raise ValueError("normalization statistics must be finite")
    return median, resolved, methods


def normalize_feature_rows(feature_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}

    for source in ALLOWED_SOURCES:
        source_rows = sorted(
            [r for r in feature_rows if str(r.get("source")) == source],
            key=lambda r: (int(r["string_number"]), int(r["fret"])),
        )
        if len(source_rows) != 78:
            raise ValueError(f"source {source} must have 78 feature rows")
        matrix = np.stack([np.asarray(r["features"], dtype=np.float64) for r in source_rows])
        median, scale, methods = _source_normalization_stats(matrix)
        transformed = (matrix - median) / scale
        if not np.all(np.isfinite(transformed)):
            raise ValueError(f"normalized features for {source} must be finite")
        for row, vector in zip(source_rows, transformed, strict=True):
            normalized.append({
                "source": source,
                "string_number": int(row["string_number"]),
                "fret": int(row["fret"]),
                "midi_number": int(row["midi_number"]),
                "features": [float(v) for v in vector],
            })
        summary[source] = {
            "rowCount": 78,
            "median": [float(v) for v in median],
            "scale": [float(v) for v in scale],
            "scaleMethod": methods,
            "allFinite": True,
        }

    if len(normalized) != EXPECTED_ROW_COUNT:
        raise ValueError("normalized feature row count mismatch")
    normalized.sort(key=lambda r: (r["source"], r["string_number"], r["fret"]))
    return normalized, summary


def evaluate_direction(feature_rows: list[dict[str, Any]], prototype_source: str, query_source: str) -> dict[str, Any]:
    if prototype_source not in ALLOWED_SOURCES or query_source not in ALLOWED_SOURCES:
        raise ValueError("comparison source outside allowed train sources")
    if prototype_source == query_source:
        raise ValueError("self-comparison is forbidden")

    prototypes = sorted(
        [r for r in feature_rows if r["source"] == prototype_source],
        key=lambda r: (r["string_number"], r["fret"]),
    )
    queries_all = sorted(
        [r for r in feature_rows if r["source"] == query_source],
        key=lambda r: (r["string_number"], r["fret"]),
    )
    if len(prototypes) != 78 or len(queries_all) != 78:
        raise ValueError("each comparison source must have 78 normalized feature rows")

    candidate_indices_by_midi: dict[int, list[int]] = defaultdict(list)
    for idx, row in enumerate(prototypes):
        candidate_indices_by_midi[int(row["midi_number"])].append(idx)
    eligible_queries = [q for q in queries_all if len(candidate_indices_by_midi[int(q["midi_number"])]) >= 2]
    if not eligible_queries:
        raise ValueError("no same-pitch ambiguous-position queries")

    p = np.stack([np.asarray(r["features"], dtype=np.float64) for r in prototypes])
    q = np.stack([np.asarray(r["features"], dtype=np.float64) for r in eligible_queries])
    correct = 0
    chance_terms: list[float] = []
    confusion: Counter[tuple[int, int]] = Counter()
    per_midi: dict[int, dict[str, int]] = defaultdict(lambda: {"queries": 0, "correct": 0, "candidateCount": 0})

    for q_idx, query in enumerate(eligible_queries):
        midi = int(query["midi_number"])
        candidate_indices = candidate_indices_by_midi[midi]
        candidates: list[tuple[float, int, int, int]] = []
        for p_idx in candidate_indices:
            distance = float(np.linalg.norm(q[q_idx] - p[p_idx]))
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
        "confusionTrueToPredictedString": {f"{a}->{b}": confusion[(a, b)] for a, b in sorted(confusion)},
        "perMidi": {str(m): per_midi[m] for m in sorted(per_midi)},
    }


def _pool_two(direction_a: dict[str, Any], direction_b: dict[str, Any]) -> dict[str, Any]:
    total_n = int(direction_a["eligibleQueryCount"]) + int(direction_b["eligibleQueryCount"])
    total_correct = int(direction_a["correctCount"]) + int(direction_b["correctCount"])
    pooled_accuracy = total_correct / total_n
    pooled_chance = (
        float(direction_a["chanceBaseline"]) * int(direction_a["eligibleQueryCount"])
        + float(direction_b["chanceBaseline"]) * int(direction_b["eligibleQueryCount"])
    ) / total_n
    return {
        "eligibleQueryCount": total_n,
        "correctCount": total_correct,
        "exactPositionAccuracy": pooled_accuracy,
        "chanceBaseline": pooled_chance,
        "accuracyLiftOverChance": pooled_accuracy - pooled_chance,
    }


def classify_session_invariance(pooled_accuracy: float, directional_gap: float) -> str:
    accuracy_improved = float(pooled_accuracy) > V1_POOLED_ACCURACY
    gap_improved = float(directional_gap) < V1_DIRECTIONAL_GAP
    if accuracy_improved and gap_improved:
        return "SESSION_INVARIANCE_IMPROVED"
    if accuracy_improved != gap_improved:
        return "MIXED"
    return "NO_IMPROVEMENT"


def evaluate_all(normalized_rows: list[dict[str, Any]]) -> dict[str, Any]:
    primary_results = [evaluate_direction(normalized_rows, a, b) for a, b in PRIMARY_DIRECTIONS]
    pooled = _pool_two(primary_results[0], primary_results[1])
    directional_gap = abs(
        float(primary_results[0]["exactPositionAccuracy"]) - float(primary_results[1]["exactPositionAccuracy"])
    )
    diagnostics = [evaluate_direction(normalized_rows, a, b) for a, b in DIAGNOSTIC_DIRECTIONS]
    return {
        "primary": {
            "directions": primary_results,
            "pooled": pooled,
            "absoluteDirectionalAccuracyGap": directional_gap,
            "v1Comparison": {
                "v1PooledAccuracy": V1_POOLED_ACCURACY,
                "v1AbsoluteDirectionalAccuracyGap": V1_DIRECTIONAL_GAP,
                "classification": classify_session_invariance(
                    pooled["exactPositionAccuracy"], directional_gap
                ),
            },
        },
        "diagnosticEleDirections": diagnostics,
    }


def download_train_parquet(destination: str | os.PathLike[str]) -> None:
    req = urllib.request.Request(TRAIN_URL, headers={"User-Agent": "songsterr-fresh-gfn-v2/1.0"})
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
    parquet_sha = validate_train_parquet_sha(parquet_path)
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

    normalized_rows, normalization = normalize_feature_rows(feature_rows)
    evaluation = evaluate_all(normalized_rows)

    return {
        "contract": "songsterr-fresh-gfn-train-session-invariance-v2",
        "studyStage": "NON_HOLDOUT_EXTERNAL_CORPUS_FEASIBILITY",
        "datasetId": DATASET_ID,
        "datasetRevision": DATASET_REVISION,
        "datasetSplitAccessed": "train",
        "reservedSplitsAccessed": False,
        "reservedSourcesAccessed": False,
        "featureContractId": FEATURE_CONTRACT_ID,
        "normalizationContractId": NORMALIZATION_CONTRACT_ID,
        "trainParquetSha256": parquet_sha,
        "integrity": integrity,
        "featureExtractionFailureCount": 0,
        "normalization": normalization,
        "evaluation": evaluation,
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
            fd, temp_path = tempfile.mkstemp(prefix="gfn-train-v2-", suffix=".parquet")
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
