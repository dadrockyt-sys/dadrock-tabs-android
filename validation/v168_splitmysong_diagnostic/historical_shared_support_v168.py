#!/usr/bin/env python3
"""Exact persisted V166 shared-support lookup for the SplitMySong diagnostic.

This module is deliberately reference-blind and audio-free. It never regenerates
Demucs stems and never invents values for uncovered lattice steps. Historical
sharedSupport is accepted only from the frozen V166 candidate's persisted
stepSelection option rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

V166_CANDIDATE_SHA256 = "fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378"
V166_TIMEBASE_SHA256 = "899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0"
EXPECTED_GUITAR = 1050
EXPECTED_BASS = 402
EXPECTED_EVENTS = 1452
EXPECTED_OPTION_ROWS = 4356
EXPECTED_COVERED_STEPS = 1617
EXPECTED_LATTICE_STEPS = 1805
EVENT_NON_NEAREST_MARGIN = 0.05
EPS = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def candidate_nominal_substep(lattice: list[float], k: int) -> float:
    if k == 0:
        return float(lattice[1] - lattice[0])
    if k == len(lattice) - 1:
        return float(lattice[-1] - lattice[-2])
    return 0.5 * float(lattice[k + 1] - lattice[k - 1])


def event_step_score(
    event_time: float,
    step_time: float,
    nominal_substep: float,
    instrument_support: float,
    shared_support: float,
) -> float:
    temporal = max(
        0.0,
        min(
            1.0,
            1.0
            - abs(float(event_time) - float(step_time))
            / (0.75 * float(nominal_substep)),
        ),
    )
    return max(
        0.0,
        min(
            1.0,
            0.70 * temporal
            + 0.20 * float(instrument_support)
            + 0.10 * float(shared_support),
        ),
    )


def select_from_rows(nearest: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    nearest_rows = [row for row in rows if int(row["step"]) == int(nearest)]
    if len(nearest_rows) != 1:
        raise RuntimeError("timing neighborhood must contain exactly one nearest row")
    nearest_row = nearest_rows[0]
    winner = sorted(
        rows,
        key=lambda r: (
            -float(r["score"]),
            abs(int(r["step"]) - int(nearest)),
            int(r["step"]),
        ),
    )[0]
    if (
        int(winner["step"]) != int(nearest)
        and float(winner["score"]) + EPS
        < float(nearest_row["score"]) + EVENT_NON_NEAREST_MARGIN
    ):
        winner = nearest_row
    return winner


def nearest_step(event_time: float, lattice: list[float]) -> int:
    if not lattice:
        raise RuntimeError("empty lattice")
    return min(
        range(len(lattice)),
        key=lambda k: (abs(float(lattice[k]) - float(event_time)), int(k)),
    )


def option_steps_for_event(event_time: float, lattice: list[float]) -> tuple[int, list[int]]:
    nearest = nearest_step(event_time, lattice)
    return nearest, [k for k in (nearest - 1, nearest, nearest + 1) if 0 <= k < len(lattice)]


def _support_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": int(row["step"]),
        "sharedSupport": float(row["sharedSupport"]),
        "normalizationBeatIndex": int(row["normalizationBeatIndex"]),
        "sharedNormalizationLoFrame": int(row["sharedNormalizationLoFrame"]),
        "sharedNormalizationHiFrame": int(row["sharedNormalizationHiFrame"]),
        "time": float(row["time"]),
    }


def build_historical_support_table(candidate: dict[str, Any]) -> tuple[dict[int, dict[str, Any]], dict[str, int]]:
    streams = candidate.get("streams") or {}
    guitar = streams.get("combinedGuitar") or []
    bass = streams.get("bass") or []
    if len(guitar) != EXPECTED_GUITAR or len(bass) != EXPECTED_BASS:
        raise RuntimeError(
            f"frozen V166 stream counts mismatch: guitar={len(guitar)} bass={len(bass)}"
        )

    table: dict[int, dict[str, Any]] = {}
    option_rows = 0
    events = 0
    for stream_name, rows in (("combinedGuitar", guitar), ("bass", bass)):
        for event_index, event in enumerate(rows):
            events += 1
            selection = event.get("stepSelection") or {}
            candidates = selection.get("candidates") or []
            if not candidates:
                raise RuntimeError(
                    f"missing stepSelection candidates: {stream_name}[{event_index}]"
                )
            for row in candidates:
                option_rows += 1
                record = _support_record(row)
                step = int(record["step"])
                old = table.get(step)
                if old is None:
                    table[step] = record
                elif old != record:
                    raise RuntimeError(
                        f"inconsistent historical shared-support/provenance at step {step}"
                    )

    if events != EXPECTED_EVENTS:
        raise RuntimeError(f"frozen V166 event count mismatch: {events}")
    if option_rows != EXPECTED_OPTION_ROWS:
        raise RuntimeError(f"frozen V166 option-row count mismatch: {option_rows}")
    if len(table) != EXPECTED_COVERED_STEPS:
        raise RuntimeError(f"frozen V166 covered-step count mismatch: {len(table)}")
    return table, {
        "eventCount": events,
        "optionRowCount": option_rows,
        "coveredStepCount": len(table),
    }


def validate_historical_rows(
    candidate: dict[str, Any],
    lattice: list[float],
    table: dict[int, dict[str, Any]],
) -> dict[str, int]:
    streams = candidate.get("streams") or {}
    score_mismatches = 0
    winner_mismatches = 0
    option_step_mismatches = 0
    events_checked = 0

    for stream_name, rows in (
        ("combinedGuitar", streams.get("combinedGuitar") or []),
        ("bass", streams.get("bass") or []),
    ):
        for event_index, event in enumerate(rows):
            events_checked += 1
            event_time = float(event["startSeconds"])
            selection = event.get("stepSelection") or {}
            stored_nearest = int(selection["nearestStep"])
            computed_nearest, computed_options = option_steps_for_event(event_time, lattice)
            stored_rows = selection.get("candidates") or []
            stored_steps = [int(row["step"]) for row in stored_rows]
            if stored_nearest != computed_nearest or stored_steps != computed_options:
                option_step_mismatches += 1

            recomputed_rows: list[dict[str, Any]] = []
            for row in stored_rows:
                step = int(row["step"])
                historical = table.get(step)
                if historical is None:
                    raise RuntimeError("historical row references an uncovered support step")
                support = float(historical["sharedSupport"])
                if support != float(row["sharedSupport"]):
                    raise RuntimeError("historical support table disagrees with source row")
                score = event_step_score(
                    event_time,
                    float(lattice[step]),
                    candidate_nominal_substep(lattice, step),
                    float(row["instrumentSupport"]),
                    support,
                )
                if abs(score - float(row["score"])) > 1e-12:
                    score_mismatches += 1
                recomputed_rows.append({"step": step, "score": score})

            winner = select_from_rows(stored_nearest, recomputed_rows)
            stored_winner = int((selection.get("winner") or {})["step"])
            if int(winner["step"]) != stored_winner:
                winner_mismatches += 1

    if events_checked != EXPECTED_EVENTS:
        raise RuntimeError("historical validation did not inspect every frozen event")
    return {
        "eventsChecked": events_checked,
        "optionStepMismatches": option_step_mismatches,
        "scoreRecomputeMismatches": score_mismatches,
        "winnerRecomputeMismatches": winner_mismatches,
    }


def load_and_validate(repo_root: Path) -> tuple[dict[str, Any], list[float], dict[int, dict[str, Any]], dict[str, Any]]:
    candidate_path = repo_root / "debug/v166-cpu-autonomous/generated.json"
    timebase_path = repo_root / "debug/v166-cpu-autonomous/timebase.json"
    if sha256_file(candidate_path) != V166_CANDIDATE_SHA256:
        raise RuntimeError("frozen V166 candidate SHA256 mismatch")
    if sha256_file(timebase_path) != V166_TIMEBASE_SHA256:
        raise RuntimeError("frozen V166 timebase SHA256 mismatch")

    candidate = load_json(candidate_path)
    timebase = load_json(timebase_path)
    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds", [])]
    if len(lattice) != EXPECTED_LATTICE_STEPS:
        raise RuntimeError(f"frozen V166 lattice count mismatch: {len(lattice)}")
    if not all(math.isfinite(x) for x in lattice) or not all(
        lattice[i + 1] > lattice[i] for i in range(len(lattice) - 1)
    ):
        raise RuntimeError("frozen V166 lattice invalid")

    table, table_stats = build_historical_support_table(candidate)
    validation = validate_historical_rows(candidate, lattice, table)
    if any(validation[key] != 0 for key in (
        "optionStepMismatches",
        "scoreRecomputeMismatches",
        "winnerRecomputeMismatches",
    )):
        raise RuntimeError(f"historical support self-validation failed: {validation}")
    report = {
        "status": "HISTORICAL_SHARED_SUPPORT_TABLE_READY",
        "candidateSha256": V166_CANDIDATE_SHA256,
        "timebaseSha256": V166_TIMEBASE_SHA256,
        "latticeStepCount": len(lattice),
        "coveredStepCount": len(table),
        "uncoveredStepCount": len(lattice) - len(table),
        "coveragePercent": 100.0 * len(table) / len(lattice),
        "table": table_stats,
        "historicalSelfValidation": validation,
        "safety": {
            "audioRead": False,
            "pitchInferenceInvoked": False,
            "referenceRead": False,
            "scorerRead": False,
            "gpuCudaUsed": False,
            "modalUsed": False,
        },
    }
    return candidate, lattice, table, report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report_path = args.report.resolve()
    if report_path.exists():
        raise RuntimeError("historical support report is write-once")
    _candidate, _lattice, _table, report = load_and_validate(args.repo_root.resolve())
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
