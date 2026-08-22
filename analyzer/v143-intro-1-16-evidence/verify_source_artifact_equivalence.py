#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SNAPSHOT = HERE / "codespace-snapshot"
SOURCE = HERE / "historical-source-4d735846"
CAL = REPO_ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

RAW_CACHE = SNAPSHOT / "intro-raw-attack-cache.json"
ONSET_CACHE = SNAPSHOT / "intro-onset-spectrum-cache.json"
BASE_MODEL = SNAPSHOT / "intro-correlation-safe-grid-event-selector-model.json"
SEQUENCE_MODEL = SNAPSHOT / "intro-correlation-safe-sequence-event-model.json"
CONTEXTUAL_MODEL = CAL / "contextual-prune-frozen-model.json"

RAW_SOURCE = SOURCE / "v143_intro_capture_raw_attack_cache.py"
CLUSTER_SOURCE = SOURCE / "v143_intro_raw_attack_temporal_diagnostic.py"
ONSET_SOURCE = SOURCE / "v143_intro_capture_onset_spectrum_cache.py"
GRID_SOURCE = SOURCE / "v143_intro_learned_grid_event_selector.py"
SEQUENCE_SOURCE = SOURCE / "v143_intro_sequence_event_model.py"
FREEZE_SOURCE = SOURCE / "v143_correlation_safe_fixed_count_reranker_freeze.py"
CONTEXTUAL_RUNTIME_SOURCE = SOURCE / "v143_contextual_prune_runtime.py"
CONSOLIDATED_CARRIER_SOURCE = SOURCE / "v143_contextual_prune_reference_free_carrier.py"

SOURCE_FILES = (
    RAW_SOURCE,
    CLUSTER_SOURCE,
    ONSET_SOURCE,
    GRID_SOURCE,
    SEQUENCE_SOURCE,
    FREEZE_SOURCE,
    CONTEXTUAL_RUNTIME_SOURCE,
    CONSOLIDATED_CARRIER_SOURCE,
)

EXPECTED_SWEEPS = {
    "o030_f020": (0.30, 0.20),
    "o025_f015": (0.25, 0.15),
    "o020_f012": (0.20, 0.12),
    "o015_f010": (0.15, 0.10),
}
EXPECTED_RAW_EVENT_FIELDS = {
    "eventId",
    "stemIndex",
    "stemName",
    "sweepName",
    "onsetThreshold",
    "frameThreshold",
    "rawIndex",
    "midi",
    "amplitude",
    "onsetTime",
    "offsetTime",
    "duration",
    "nearestMeasure",
    "nearestStep",
    "nearestGlobalStep",
    "nearestGridTime",
    "signedGridResidualSeconds",
    "absoluteGridResidualSeconds",
    "withinProductionGridTolerance",
}
EXPECTED_ONSET_METADATA_FIELDS = (
    "onsetGroupId",
    "measure",
    "onsetTime",
    "candidateMidis",
    "candidateCount",
    "sourceClusterCount",
    "stemSupportMax",
    "sweepSupportMax",
    "detectionCountSum",
)
WINDOW_NAMES = ("attackMax", "earlyMean", "sustainMean")
VIEW_NAMES = ("viewA", "viewB")

GRID_FEATURE_NAMES = (
    "hasNearbyOnset",
    "signedResidualOverWindow",
    "absoluteResidualOverWindow",
    "secondNearestAbsoluteResidualOverWindow",
    "nearbyCountScaled",
    "candidateCountScaled",
    "sourceClusterCountScaled",
    "nearestStemSupportScaled",
    "nearestSweepSupportScaled",
    "nearestDetectionCountScaled",
    "nearbyMaxStemSupportScaled",
    "nearbyMaxSweepSupportScaled",
    "nearbyDetectionCountSumScaled",
    "attackMax:meanViewMean",
    "attackMax:meanViewStd",
    "attackMax:top1",
    "attackMax:top1MinusTop2",
    "attackMax:normA",
    "attackMax:normB",
    "attackMax:viewCorrelation",
    "earlyMean:meanViewMean",
    "earlyMean:meanViewStd",
    "earlyMean:top1",
    "earlyMean:top1MinusTop2",
    "earlyMean:normA",
    "earlyMean:normB",
    "earlyMean:viewCorrelation",
    "sustainMean:meanViewMean",
    "sustainMean:meanViewStd",
    "sustainMean:top1",
    "sustainMean:top1MinusTop2",
    "sustainMean:normA",
    "sustainMean:normB",
    "sustainMean:viewCorrelation",
    "stepSin",
    "stepCos",
)
CORRELATION_COLUMNS = (19, 26, 33)
CONTEXTUAL_FEATURE_NAMES = (
    "baseScore",
    "sequenceScore",
    "sequenceEvidence",
    "stepSin",
    "stepCos",
    "strongBeat",
    "eighthGrid",
    "measureBaseCount",
    "neighborStepCount1",
    "neighborStepCount2",
    "sameStepAdjacentMeasures",
    "sameStepTwoMeasures",
    "sameStepFourMeasures",
    "sameStepWindow4Count",
    "baseSequenceInteraction",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_json(path: Path) -> Any:
    require(path.exists() and path.stat().st_size > 0, f"missing/empty JSON artifact: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sha_manifest(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        digest, rel = raw.split(maxsplit=1)
        rel = rel.strip()
        if rel.startswith("*"):
            rel = rel[1:]
        if rel.startswith("./"):
            rel = rel[2:]
        out[rel] = digest
    return out


def verify_manifest_files(base: Path, manifest_name: str, paths: list[Path]) -> dict[str, str]:
    manifest = read_sha_manifest(base / manifest_name)
    verified: dict[str, str] = {}
    for path in paths:
        rel = path.relative_to(base).as_posix()
        require(rel in manifest, f"checksum manifest missing {rel}")
        actual = sha256(path)
        require(actual == manifest[rel], f"checksum mismatch for {rel}: {actual} != {manifest[rel]}")
        verified[rel] = actual
    return verified


def module_literals(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: dict[str, Any] = {}
    for node in tree.body:
        target: ast.Name | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target = node.targets[0]
            value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target = node.target
            value_node = node.value
        if target is None or value_node is None:
            continue
        try:
            values[target.id] = ast.literal_eval(value_node)
        except (ValueError, TypeError):
            pass
    return values


def all_named_literal_assignments(path: Path, name: str) -> list[Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: list[Any] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    try:
                        values.append(ast.literal_eval(node.value))
                    except (ValueError, TypeError):
                        pass
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            try:
                values.append(ast.literal_eval(node.value))
            except (ValueError, TypeError):
                pass
    return values


def as_finite_float(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise AssertionError(f"{label} is not numeric: {value!r}") from exc
    require(math.isfinite(out), f"{label} is not finite: {value!r}")
    return out


def verify_source_constants() -> dict[str, Any]:
    raw = module_literals(RAW_SOURCE)
    onset = module_literals(ONSET_SOURCE)
    grid = module_literals(GRID_SOURCE)
    sequence = module_literals(SEQUENCE_SOURCE)
    runtime = module_literals(CONTEXTUAL_RUNTIME_SOURCE)

    require(raw.get("INTRO_FIRST_MEASURE") == 1, "historical raw producer first measure changed")
    require(raw.get("INTRO_LAST_MEASURE") == 16, "historical raw producer last measure changed")
    require(float(raw.get("WIDE_GRID_TOLERANCE_SECONDS")) == 0.30, "historical wide grid tolerance changed")
    require(float(raw.get("PRODUCTION_GRID_TOLERANCE_SECONDS")) == 0.10, "historical production grid tolerance changed")

    expected_onset = {
        "TARGET_SR": 22050,
        "HOP_LENGTH": 128,
        "BINS_PER_OCTAVE": 36,
        "CQT_MIDI_MIN": 28,
        "CQT_MIDI_MAX": 112,
        "GUITAR_MIDI_MIN": 40,
        "GUITAR_MIDI_MAX": 88,
        "ONSET_GROUP_TOLERANCE_SECONDS": 0.030,
    }
    for name, expected in expected_onset.items():
        require(onset.get(name) == expected, f"historical onset producer constant {name} changed: {onset.get(name)!r}")

    require(grid.get("STEPS_PER_MEASURE") == 16, "grid selector steps-per-measure changed")
    require(tuple(sequence.get("WINDOWS_MS", ())) == (50, 75, 100, 125, 150, 200), "sequence windows changed")
    feature_count_values = all_named_literal_assignments(GRID_SOURCE, "feature_count")
    require(36 in feature_count_values, f"historical grid feature_count=36 not found: {feature_count_values}")
    require(tuple(runtime.get("FEATURE_NAMES", ())) == CONTEXTUAL_FEATURE_NAMES, "contextual runtime feature ordering changed")

    cluster_text = CLUSTER_SOURCE.read_text(encoding="utf-8")
    consolidated_text = CONSOLIDATED_CARRIER_SOURCE.read_text(encoding="utf-8")
    require('"onsetTime": float(median(onsets))' in cluster_text, "historical median cluster-onset policy not found")
    consolidated_is_historical_median = '"onsetTime": float(median(onsets))' in consolidated_text
    consolidated_uses_weighted_onset = "weight_sum" in consolidated_text and 'float(row["onsetTime"]) * weight' in consolidated_text

    return {
        "rawWideGridToleranceSeconds": raw["WIDE_GRID_TOLERANCE_SECONDS"],
        "rawProductionGridToleranceSeconds": raw["PRODUCTION_GRID_TOLERANCE_SECONDS"],
        "onsetConstants": expected_onset,
        "gridFeatureCount": 36,
        "sequenceWindowsMs": list(sequence["WINDOWS_MS"]),
        "contextualFeatureCount": len(CONTEXTUAL_FEATURE_NAMES),
        "historicalClusterOnsetPolicy": "median",
        "consolidatedCarrierUsesHistoricalMedianClusterOnset": consolidated_is_historical_median,
        "consolidatedCarrierUsesWeightedClusterOnset": consolidated_uses_weighted_onset,
    }


def verify_raw_cache(raw: dict[str, Any]) -> dict[str, Any]:
    require(raw.get("cacheVersion") == 1, "raw cacheVersion changed")
    require(raw.get("scope") == "professional-measures-1-16-raw-reference-free-attacks", "raw scope changed")
    require(raw.get("referenceFree") is True, "raw cache not marked reference-free")
    require(raw.get("professionalReferenceUsedByAnalyzer") is False, "raw cache claims professional runtime/analyzer reference")
    require(raw.get("runtimeLabelsRequired") is False, "raw cache claims runtime labels required")
    require(raw.get("productionModified") is False, "raw cache claims production modified")
    require(float(raw.get("wideGridToleranceSeconds")) == 0.30, "raw artifact wide tolerance != source")
    require(float(raw.get("productionGridToleranceSeconds")) == 0.10, "raw artifact production tolerance != source")
    require(int(raw.get("candidateStemCount")) == 2, "raw artifact does not contain exactly two guitar views")

    events = raw.get("events") or []
    grid = raw.get("grid") or []
    require(isinstance(events, list) and events, "raw cache events missing/empty")
    require(isinstance(grid, list) and grid, "raw cache grid missing/empty")
    require(int(raw.get("rawEventCount")) == len(events), "rawEventCount != len(events)")

    expected_grid_keys = {(measure, step) for measure in range(1, 17) for step in range(16)}
    grid_keys: set[tuple[int, int]] = set()
    global_steps: set[int] = set()
    for index, row in enumerate(grid):
        require(isinstance(row, dict), f"grid row {index} is not an object")
        key = (int(row.get("measure") or 0), int(row.get("step") or -1))
        require(key not in grid_keys, f"duplicate grid key {key}")
        grid_keys.add(key)
        global_steps.add(int(row.get("globalStep")))
        as_finite_float(row.get("timeSeconds"), f"grid[{index}].timeSeconds")
    require(grid_keys == expected_grid_keys, f"raw grid keys differ from exact 16x16 contract; missing={sorted(expected_grid_keys-grid_keys)[:8]} extra={sorted(grid_keys-expected_grid_keys)[:8]}")
    require(len(global_steps) == 256, "raw grid globalStep values are not unique")

    event_ids: list[int] = []
    sweep_counts: Counter[str] = Counter()
    stem_counts: Counter[str] = Counter()
    stem_indices: set[int] = set()
    production_accepted = 0
    for index, event in enumerate(events):
        require(isinstance(event, dict), f"event {index} is not an object")
        missing = EXPECTED_RAW_EVENT_FIELDS - set(event)
        require(not missing, f"event {index} missing fields: {sorted(missing)}")
        event_id = int(event["eventId"])
        event_ids.append(event_id)
        measure = int(event["nearestMeasure"])
        step = int(event["nearestStep"])
        midi = int(event["midi"])
        stem_index = int(event["stemIndex"])
        sweep_name = str(event["sweepName"])
        require(1 <= measure <= 16, f"event {event_id} outside measures 1-16")
        require(0 <= step < 16, f"event {event_id} step outside 0-15")
        require(40 <= midi <= 88, f"event {event_id} outside guitar MIDI 40-88")
        require(stem_index in (0, 1), f"event {event_id} invalid stemIndex {stem_index}")
        require(sweep_name in EXPECTED_SWEEPS, f"event {event_id} unknown sweep {sweep_name}")
        expected_onset, expected_frame = EXPECTED_SWEEPS[sweep_name]
        require(math.isclose(float(event["onsetThreshold"]), expected_onset, abs_tol=1e-12), f"event {event_id} onset threshold mismatch")
        require(math.isclose(float(event["frameThreshold"]), expected_frame, abs_tol=1e-12), f"event {event_id} frame threshold mismatch")
        onset = as_finite_float(event["onsetTime"], f"event {event_id} onsetTime")
        offset = as_finite_float(event["offsetTime"], f"event {event_id} offsetTime")
        residual = as_finite_float(event["signedGridResidualSeconds"], f"event {event_id} signed residual")
        absolute = as_finite_float(event["absoluteGridResidualSeconds"], f"event {event_id} absolute residual")
        grid_time = as_finite_float(event["nearestGridTime"], f"event {event_id} nearestGridTime")
        require(offset >= onset - 1e-12, f"event {event_id} offset precedes onset")
        require(math.isclose(residual, onset - grid_time, abs_tol=1e-9), f"event {event_id} signed residual inconsistent")
        require(math.isclose(absolute, abs(residual), abs_tol=1e-9), f"event {event_id} absolute residual inconsistent")
        require(absolute <= 0.30 + 1e-9, f"event {event_id} exceeds historical wide-grid tolerance")
        accepted = bool(event["withinProductionGridTolerance"])
        require(accepted == (absolute <= 0.10 + 1e-12), f"event {event_id} production acceptance inconsistent with nearest residual")
        if accepted:
            production_accepted += 1
        sweep_counts[sweep_name] += 1
        stem_name = str(event["stemName"])
        stem_counts[stem_name] += 1
        stem_indices.add(stem_index)

    require(event_ids == list(range(1, len(events) + 1)), "raw eventId sequence is not exact 1..N writer order")
    require(stem_indices == {0, 1}, f"raw events do not cover exactly two stem indices: {sorted(stem_indices)}")
    require(dict(sweep_counts) == {str(k): int(v) for k, v in (raw.get("sweepEventCounts") or {}).items()}, "raw sweepEventCounts do not match events")
    require(dict(stem_counts) == {str(k): int(v) for k, v in (raw.get("stemEventCounts") or {}).items()}, "raw stemEventCounts do not match events")
    require(production_accepted == int(raw.get("productionAcceptedEventCount")), "productionAcceptedEventCount does not match events")

    timing = raw.get("timing") or {}
    for key in ("tempoBpm", "beatConfidence", "barConfidence"):
        as_finite_float(timing.get(key), f"timing.{key}")
    require(isinstance(timing.get("beatTimes"), list) and timing["beatTimes"], "raw timing beatTimes missing")

    return {
        "rawEventCount": len(events),
        "productionAcceptedEventCount": production_accepted,
        "gridCount": len(grid),
        "sweepEventCounts": dict(sorted(sweep_counts.items())),
        "stemEventCounts": dict(sorted(stem_counts.items())),
    }


def historical_clusters(raw: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in raw.get("events") or []:
        grouped[(int(event.get("nearestMeasure") or 0), int(event.get("midi") or 0))].append(dict(event))

    clusters: list[dict[str, Any]] = []
    cluster_id = 0
    for (measure, midi), events in sorted(grouped.items()):
        events.sort(key=lambda row: (float(row["onsetTime"]), int(row.get("eventId") or 0)))
        current: list[dict[str, Any]] = []
        center = 0.0

        def flush(rows: list[dict[str, Any]]) -> None:
            nonlocal cluster_id
            if not rows:
                return
            cluster_id += 1
            onsets = [float(row["onsetTime"]) for row in rows]
            amplitudes = [float(row.get("amplitude") or 0.0) for row in rows]
            stems = sorted({int(row.get("stemIndex") or 0) for row in rows})
            sweeps = sorted({str(row.get("sweepName") or "") for row in rows})
            clusters.append(
                {
                    "clusterId": cluster_id,
                    "measure": int(measure),
                    "midi": int(midi),
                    "onsetTime": float(median(onsets)),
                    "minOnsetTime": min(onsets),
                    "maxOnsetTime": max(onsets),
                    "detectionCount": len(rows),
                    "stemSupport": len(stems),
                    "sweepSupport": len(sweeps),
                    "stems": stems,
                    "sweeps": sweeps,
                    "maxAmplitude": max(amplitudes) if amplitudes else 0.0,
                    "meanAmplitude": sum(amplitudes) / len(amplitudes) if amplitudes else 0.0,
                    "productionAccepted": any(bool(row.get("withinProductionGridTolerance")) for row in rows),
                }
            )

        for event in events:
            onset = float(event["onsetTime"])
            if not current:
                current = [event]
                center = onset
            elif abs(onset - center) <= 0.030:
                current.append(event)
                center = float(median([float(row["onsetTime"]) for row in current]))
            else:
                flush(current)
                current = [event]
                center = onset
        flush(current)
    return clusters


def historical_onset_groups(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for cluster in clusters:
        measure = int(cluster.get("measure") or 0)
        onset = float(cluster.get("onsetTime") if cluster.get("onsetTime") is not None else -1.0)
        midi = int(cluster.get("midi") or 0)
        if 1 <= measure <= 16 and onset >= 0.0 and 40 <= midi <= 88:
            by_measure[measure].append(cluster)

    groups: list[dict[str, Any]] = []
    group_id = 0
    for measure in sorted(by_measure):
        rows = sorted(
            by_measure[measure],
            key=lambda row: (float(row.get("onsetTime") or 0.0), int(row.get("midi") or 0), int(row.get("clusterId") or 0)),
        )
        current: list[dict[str, Any]] = []
        anchor: float | None = None

        def flush() -> None:
            nonlocal current, anchor, group_id
            if not current:
                return
            weights = [max(1, int(row.get("detectionCount") or 1)) for row in current]
            weight_sum = float(sum(weights))
            onset_time = sum(float(row.get("onsetTime") or 0.0) * weight for row, weight in zip(current, weights)) / max(weight_sum, 1.0)
            midis = sorted({int(row.get("midi") or 0) for row in current})
            group_id += 1
            groups.append(
                {
                    "onsetGroupId": group_id,
                    "measure": measure,
                    "onsetTime": round(float(onset_time), 9),
                    "candidateMidis": midis,
                    "candidateCount": len(midis),
                    "sourceClusterCount": len(current),
                    "stemSupportMax": max(int(row.get("stemSupport") or 0) for row in current),
                    "sweepSupportMax": max(int(row.get("sweepSupport") or 0) for row in current),
                    "detectionCountSum": sum(int(row.get("detectionCount") or 0) for row in current),
                }
            )
            current = []
            anchor = None

        for row in rows:
            onset = float(row.get("onsetTime") or 0.0)
            if not current:
                current = [row]
                anchor = onset
            elif abs(onset - float(anchor)) <= 0.030:
                current.append(row)
            else:
                flush()
                current = [row]
                anchor = onset
        flush()
    return groups


def compare_group_metadata(expected: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    require(len(expected) == len(rows), f"historical onset-group count {len(expected)} != preserved rows {len(rows)}")
    for index, (group, row) in enumerate(zip(expected, rows)):
        for field in EXPECTED_ONSET_METADATA_FIELDS:
            require(field in row, f"onset row {index} missing metadata field {field}")
            if field == "onsetTime":
                require(math.isclose(float(row[field]), float(group[field]), abs_tol=5e-10), f"onset row {index} onsetTime differs from historical grouping: {row[field]} != {group[field]}")
            else:
                require(row[field] == group[field], f"onset row {index} field {field} differs from historical grouping: {row[field]!r} != {group[field]!r}")


def verify_onset_cache(onset: dict[str, Any], raw: dict[str, Any]) -> dict[str, Any]:
    require(onset.get("cacheVersion") == 1, "onset cacheVersion changed")
    require(onset.get("scope") == "reference-free-physical-onset-whole-spectrum-cache", "onset scope changed")
    expected_scalars = {
        "targetSampleRate": 22050,
        "hopLength": 128,
        "binsPerOctave": 36,
        "spectrumMidiMin": 28,
        "spectrumMidiMax": 112,
        "guitarMidiMin": 40,
        "guitarMidiMax": 88,
        "candidateStemCount": 2,
    }
    for key, expected in expected_scalars.items():
        require(onset.get(key) == expected, f"onset artifact {key}={onset.get(key)!r} != historical source {expected!r}")
    require(math.isclose(float(onset.get("onsetGroupingToleranceMs")), 30.0, abs_tol=1e-12), "onset grouping tolerance != 30 ms")
    require(onset.get("referenceFree") is True, "onset cache not marked reference-free")
    require(onset.get("professionalReferenceUsedByAnalyzer") is False, "onset cache claims professional analyzer reference")
    require(onset.get("runtimeLabelsRequired") is False, "onset cache claims runtime labels required")
    require(onset.get("productionModified") is False, "onset cache claims production modified")

    rows = onset.get("rows") or []
    require(isinstance(rows, list) and rows, "onset rows missing/empty")
    require(int(onset.get("onsetGroupCount")) == len(rows), "onsetGroupCount != len(rows)")

    clusters = historical_clusters(raw)
    expected_groups = historical_onset_groups(clusters)
    compare_group_metadata(expected_groups, rows)

    vector_len = int(onset["spectrumMidiMax"]) - int(onset["spectrumMidiMin"]) + 1
    require(vector_len == 85, f"unexpected spectral semitone vector length {vector_len}")
    vector_count = 0
    for row_index, row in enumerate(rows):
        require(1 <= int(row["measure"]) <= 16, f"onset row {row_index} outside measures 1-16")
        candidate_midis = [int(value) for value in row.get("candidateMidis") or []]
        require(candidate_midis == sorted(set(candidate_midis)), f"onset row {row_index} candidateMidis not sorted unique")
        require(all(40 <= midi <= 88 for midi in candidate_midis), f"onset row {row_index} candidate MIDI outside guitar range")
        for view in VIEW_NAMES:
            payload = row.get(view)
            require(isinstance(payload, dict), f"onset row {row_index} missing {view}")
            for window in WINDOW_NAMES:
                values = payload.get(window)
                require(isinstance(values, list) and len(values) == vector_len, f"onset row {row_index} {view}.{window} length != {vector_len}")
                numeric = [as_finite_float(value, f"row {row_index} {view}.{window}") for value in values]
                require(abs(float(median(numeric))) <= 1.1e-6, f"onset row {row_index} {view}.{window} median floor is not approximately zero")
                vector_count += 1

    return {
        "physicalAttackClusterCount": len(clusters),
        "onsetGroupCount": len(rows),
        "spectralVectorLength": vector_len,
        "spectralVectorsVerified": vector_count,
        "historicalGroupMetadataExact": True,
    }


def verify_feature_carrier(base: dict[str, Any], sequence: dict[str, Any], contextual: dict[str, Any]) -> dict[str, Any]:
    require(len(GRID_FEATURE_NAMES) == 36, "internal reconstructed grid feature map is not width 36")
    require(tuple(index for index, name in enumerate(GRID_FEATURE_NAMES) if name.endswith(":viewCorrelation")) == CORRELATION_COLUMNS, "reconstructed correlation columns changed")

    require(base.get("model") == "v143-correlation-safe-grid-event-selector", "unexpected preserved base selector model")
    require(int(base.get("windowMs")) == 100, "base selector windowMs != 100")
    require(float(base.get("threshold")) == 0.27, "base selector threshold != 0.27")
    require(tuple(base.get("neutralizedFeatureColumns") or ()) == CORRELATION_COLUMNS, "base selector neutralized columns do not match 36-feature ordering")
    require(tuple(base.get("neutralizedFeatureNames") or ()) == tuple(GRID_FEATURE_NAMES[index] for index in CORRELATION_COLUMNS), "base selector neutralized feature names do not match source ordering")
    require(len(base.get("featureMean") or []) == 36, "base selector featureMean width != 36")
    require(len(base.get("featureStd") or []) == 36, "base selector featureStd width != 36")
    require(len(base.get("weights") or []) == 37, "base selector weight width != 36 + intercept")
    require(base.get("professionalReferenceRequiredAtRuntime") is False, "base model claims runtime professional reference")
    require(base.get("productionModified") is False, "base model claims production modified")

    sequence_width = 6 * 36 + 3 + 14 + 6 + 5 + 8 + 8
    require(sequence_width == 260, "derived sequence feature width != 260")
    require(sequence.get("model") == "v143-correlation-safe-sequence-event-model", "unexpected preserved sequence model")
    require(sequence.get("baseSelectorModel") == "intro-correlation-safe-grid-event-selector-model.json", "sequence model points at unexpected base model")
    require(tuple(sequence.get("neutralizedGridFeatureColumns") or ()) == CORRELATION_COLUMNS, "sequence neutralized grid columns changed")
    require(float(sequence.get("neutralizedRawValue")) == 1.0, "sequence neutralizedRawValue changed")
    require(len(sequence.get("featureMean") or []) == sequence_width, f"sequence featureMean width != {sequence_width}")
    require(len(sequence.get("featureStd") or []) == sequence_width, f"sequence featureStd width != {sequence_width}")
    basis = sequence.get("pcaBasis") or []
    require(len(basis) == sequence_width, f"sequence PCA basis row count != {sequence_width}")
    components = int(sequence.get("pcaComponents"))
    require(components == 24, "sequence pcaComponents != 24")
    require(all(isinstance(row, list) and len(row) == components for row in basis), "sequence PCA basis column count mismatch")
    require(len(sequence.get("ridgeWeights") or []) == components + 1, "sequence ridgeWeights width != PCA components + intercept")
    require(sequence.get("professionalReferenceRequiredAtRuntime") is False, "sequence model claims runtime professional reference")

    absolute_neutralized = [window * 36 + column for window in range(6) for column in CORRELATION_COLUMNS]

    require(contextual.get("model") == "v143-contextual-prune", "unexpected contextual model")
    require(tuple(contextual.get("featureNames") or ()) == CONTEXTUAL_FEATURE_NAMES, "contextual model feature names/order differ from runtime")
    require(len(contextual.get("featureMean") or []) == 15, "contextual featureMean width != 15")
    require(len(contextual.get("featureStd") or []) == 15, "contextual featureStd width != 15")
    require(len(contextual.get("weights") or []) == 16, "contextual weights width != 15 + intercept")
    require(float(contextual.get("baseThreshold")) == 0.27, "contextual baseThreshold != 0.27")
    require(float(contextual.get("pruneFraction")) == 0.15, "contextual pruneFraction != 0.15")
    require(contextual.get("candidateAddsEvents") is False, "contextual model can add events")
    require(contextual.get("candidateRelocatesEvents") is False, "contextual model can relocate events")
    require(contextual.get("professionalReferenceRequiredAtRuntime") is False, "contextual model claims runtime professional reference")
    require(contextual.get("measures97To113UsedForTraining") is False, "contextual model claims reserve measures used for training")
    require(contextual.get("productionModified") is False, "contextual model claims production modified")

    return {
        "gridFeatureWidth": 36,
        "gridFeatureNames": list(GRID_FEATURE_NAMES),
        "viewCorrelationColumns": list(CORRELATION_COLUMNS),
        "sequenceWindowCount": 6,
        "sequenceRawFeatureWidth": sequence_width,
        "sequencePcaComponents": components,
        "sequenceAbsoluteNeutralizedColumns": absolute_neutralized,
        "contextualFeatureWidth": 15,
        "contextualFeatureNames": list(CONTEXTUAL_FEATURE_NAMES),
        "baseThreshold": 0.27,
        "contextualPruneFraction": 0.15,
    }


def main() -> None:
    for path in (*SOURCE_FILES, RAW_CACHE, ONSET_CACHE, BASE_MODEL, SEQUENCE_MODEL, CONTEXTUAL_MODEL):
        require(path.exists() and path.stat().st_size > 0, f"required path missing/empty: {path}")

    source_checksums = verify_manifest_files(
        SOURCE,
        "SHA256SUMS.txt",
        list(SOURCE_FILES),
    )
    snapshot_checksums = verify_manifest_files(
        SNAPSHOT,
        "SHA256SUMS.txt",
        [RAW_CACHE, ONSET_CACHE, BASE_MODEL, SEQUENCE_MODEL],
    )

    source_contract = verify_source_constants()
    raw = load_json(RAW_CACHE)
    raw_report = verify_raw_cache(raw)
    onset = load_json(ONSET_CACHE)
    onset_report = verify_onset_cache(onset, raw)
    base = load_json(BASE_MODEL)
    sequence = load_json(SEQUENCE_MODEL)
    contextual = load_json(CONTEXTUAL_MODEL)
    carrier_report = verify_feature_carrier(base, sequence, contextual)

    report = {
        "verification": "v143-static-source-artifact-equivalence",
        "status": "PASS",
        "scope": "measures-1-16 preserved raw/onset carrier plus frozen 36-feature/sequence/contextual model contracts",
        "sourceArchive": "historical-source-4d735846",
        "sourceChecksumsVerified": source_checksums,
        "snapshotChecksumsVerified": snapshot_checksums,
        "sourceContract": source_contract,
        "rawCache": raw_report,
        "onsetSpectrumCache": onset_report,
        "carrier": carrier_report,
        "referenceFreeRuntimeContract": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "retrained": False,
        "runtimeReplayPerformed": False,
        "replayGuard": {
            "useHistoricalMedianClusterChainForPreservedCacheReplay": True,
            "consolidatedReferenceFreeCarrierIsBitExactForHistoricalClusterOnset": bool(source_contract["consolidatedCarrierUsesHistoricalMedianClusterOnset"]),
            "note": "The later consolidated carrier uses an amplitude-weighted candidate-cluster onset while the preserved measures 1-16 onset cache was produced from the historical median-onset clustering function. Do not use the consolidated carrier as a bit-exact historical cache replay path without reconciling that policy difference.",
        },
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    print("V143 STATIC SOURCE/ARTIFACT EQUIVALENCE: PASS")
    print("RUNTIME REPLAY PERFORMED: False")
    print("PRODUCTION MODIFIED: False")


if __name__ == "__main__":
    main()
