from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import Counter
from pathlib import Path
from statistics import mean, median
from typing import Any, Iterable, Mapping, Sequence


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
DEFAULT_INPUT = "debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json"
DEFAULT_OUTPUT = "debug/v143-contextual-prune/repaired-timing-precision-candidate-physical-grid-fidelity.json"


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = max(0.0, min(1.0, float(fraction))) * (len(ordered) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _key(row: Mapping[str, Any]) -> tuple[int, int] | None:
    try:
        return int(row["measure"]), int(row["step"])
    except (KeyError, TypeError, ValueError):
        return None


def _residual_row(row: Mapping[str, Any], index: int) -> dict[str, Any] | None:
    key = _key(row)
    onset = _finite(row.get("onsetTime"))
    grid = _finite(row.get("timeSeconds"))
    if key is None or onset is None or grid is None:
        return None
    signed = onset - grid
    return {
        "index": int(index),
        "measure": int(key[0]),
        "step": int(key[1]),
        "timeSeconds": float(grid),
        "onsetTime": float(onset),
        "signedResidualSeconds": float(signed),
        "absoluteResidualSeconds": float(abs(signed)),
        "dominantMidi": int(row["dominantMidi"]) if row.get("dominantMidi") is not None else None,
        "midi": int(row["midi"]) if row.get("midi") is not None else None,
    }


def _residual_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    parsed = [value for index, row in enumerate(rows) if (value := _residual_row(row, index)) is not None]
    absolute = [float(item["absoluteResidualSeconds"]) for item in parsed]
    signed = [float(item["signedResidualSeconds"]) for item in parsed]
    thresholds = (0.030, 0.060, 0.100, 0.150, 0.300, 0.500)
    threshold_counts = {
        f"within{int(round(limit * 1000))}msCount": sum(value <= limit for value in absolute)
        for limit in thresholds
    }
    threshold_fractions = {
        f"within{int(round(limit * 1000))}msFraction": (sum(value <= limit for value in absolute) / len(absolute) if absolute else 0.0)
        for limit in thresholds
    }
    worst = sorted(
        parsed,
        key=lambda item: (-float(item["absoluteResidualSeconds"]), int(item["measure"]), int(item["step"]), int(item["index"])),
    )[:30]
    return {
        "rowCount": len(rows),
        "validResidualCount": len(parsed),
        "invalidResidualCount": len(rows) - len(parsed),
        "signedMeanSeconds": float(mean(signed)) if signed else 0.0,
        "signedMedianSeconds": float(median(signed)) if signed else 0.0,
        "absoluteMeanSeconds": float(mean(absolute)) if absolute else 0.0,
        "absoluteMedianSeconds": float(median(absolute)) if absolute else 0.0,
        "absoluteP90Seconds": float(_percentile(absolute, 0.90)),
        "absoluteP95Seconds": float(_percentile(absolute, 0.95)),
        "absoluteP99Seconds": float(_percentile(absolute, 0.99)),
        "absoluteMaxSeconds": float(max(absolute)) if absolute else 0.0,
        **threshold_counts,
        **threshold_fractions,
        "over300msCount": sum(value > 0.300 for value in absolute),
        "over500msCount": sum(value > 0.500 for value in absolute),
        "worstResidualRows": worst,
    }


def _source_event_consistency(
    source_rows: Sequence[Mapping[str, Any]],
    events: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    source_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    duplicate_source_keys: Counter[tuple[int, int]] = Counter()
    for row in source_rows:
        key = _key(row)
        if key is None:
            continue
        duplicate_source_keys[key] += 1
        source_by_key.setdefault(key, row)

    event_key_counts: Counter[tuple[int, int]] = Counter()
    missing_source: list[dict[str, int]] = []
    onset_mismatch = 0
    grid_mismatch = 0
    dominant_mismatch = 0
    max_onset_delta = 0.0
    max_grid_delta = 0.0
    for event in events:
        key = _key(event)
        if key is None:
            continue
        event_key_counts[key] += 1
        source = source_by_key.get(key)
        if source is None:
            missing_source.append({"measure": int(key[0]), "step": int(key[1])})
            continue
        event_onset = _finite(event.get("onsetTime"))
        source_onset = _finite(source.get("onsetTime"))
        event_grid = _finite(event.get("timeSeconds"))
        source_grid = _finite(source.get("timeSeconds"))
        if event_onset is None or source_onset is None or abs(event_onset - source_onset) > 1.0e-9:
            onset_mismatch += 1
            if event_onset is not None and source_onset is not None:
                max_onset_delta = max(max_onset_delta, abs(event_onset - source_onset))
        if event_grid is None or source_grid is None or abs(event_grid - source_grid) > 1.0e-9:
            grid_mismatch += 1
            if event_grid is not None and source_grid is not None:
                max_grid_delta = max(max_grid_delta, abs(event_grid - source_grid))
        event_dominant = event.get("dominantMidi")
        source_dominant = source.get("dominantMidi")
        if event_dominant != source_dominant:
            dominant_mismatch += 1

    duplicate_source = [
        {"measure": int(key[0]), "step": int(key[1]), "count": int(count)}
        for key, count in sorted(duplicate_source_keys.items())
        if count > 1
    ]
    source_without_events = [
        {"measure": int(key[0]), "step": int(key[1])}
        for key in sorted(source_by_key)
        if event_key_counts[key] == 0
    ]
    return {
        "sourceUniqueKeyCount": len(source_by_key),
        "eventUniqueKeyCount": len(event_key_counts),
        "duplicateSourceKeyCount": len(duplicate_source),
        "duplicateSourceKeys": duplicate_source[:30],
        "eventKeysMissingSourceCount": len(missing_source),
        "eventKeysMissingSource": missing_source[:30],
        "sourceKeysWithoutEventsCount": len(source_without_events),
        "sourceKeysWithoutEvents": source_without_events[:30],
        "eventSourceOnsetMismatchCount": int(onset_mismatch),
        "eventSourceTimeSecondsMismatchCount": int(grid_mismatch),
        "eventSourceDominantMidiMismatchCount": int(dominant_mismatch),
        "maximumEventSourceOnsetDeltaSeconds": float(max_onset_delta),
        "maximumEventSourceGridDeltaSeconds": float(max_grid_delta),
    }


def analyze_candidate(data: Mapping[str, Any]) -> dict[str, Any]:
    source_rows = data.get("sourceRows") or []
    events = data.get("events") or []
    if not isinstance(source_rows, list) or not isinstance(events, list):
        raise ValueError("candidate product sourceRows/events must be lists")
    source_maps = [row for row in source_rows if isinstance(row, Mapping)]
    event_maps = [row for row in events if isinstance(row, Mapping)]
    return {
        "schemaVersion": 1,
        "gate": "v143-candidate-physical-grid-fidelity",
        "candidateMode": data.get("mode"),
        "selectedCountDeclared": int(data.get("selectedCount") or 0),
        "noteCountDeclared": int(data.get("noteCount") or 0),
        "sourceRows": _residual_summary(source_maps),
        "events": _residual_summary(event_maps),
        "sourceEventConsistency": _source_event_consistency(source_maps, event_maps),
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "runtimeOutputChanged": False,
        "productionModified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f"candidate product missing: {input_path}")
    data = json.loads(input_path.read_text(encoding="utf-8"))
    diagnostic = analyze_candidate(data)

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    diagnostic["protectedPipelineBlob"] = protected
    diagnostic["protectedPipelineUnchanged"] = protected == EXPECTED_PROTECTED_BLOB
    if diagnostic["protectedPipelineUnchanged"] is not True:
        raise SystemExit(f"protected pipeline changed: {protected}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(diagnostic, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "sourceRows": diagnostic["sourceRows"],
        "sourceEventConsistency": diagnostic["sourceEventConsistency"],
        "protectedPipelineUnchanged": diagnostic["protectedPipelineUnchanged"],
    }, sort_keys=True))
    print(f"WROTE={output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
