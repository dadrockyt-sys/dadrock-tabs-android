#!/usr/bin/env python3
"""Reference-blind V168 diagnostic for V166 shared-onset/grid equivalence.

This diagnostic does NOT run Demucs or Basic Pitch. It consumes an already-built
current/drifted drums stem plus the byte-frozen historical normalized mix,
timebase, and V166 candidate. It asks a deliberately narrower question than WAV
identity: does the changed drums waveform alter any V166 event-step decision at
the exact lattice neighborhoods whose historical evidence was frozen in the V166
candidate?

A PASS is intentionally very strict: every V166 lattice step must be represented
by at least one historical stepSelection candidate, historical repeated support
values must be internally consistent, every stored historical score must
recompute, and the current shared envelope must leave every selected V166 step
unchanged. If lattice coverage is incomplete the result is FAIL_CLOSED even when
all observed event decisions agree.

No professional reference, scorer, prior score, or SplitMySong Guitar audio is
accepted by this CLI or opened by this program.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

EXPECTED = {
    "candidateSha256": "fa2411598b401f745eff49a9cbda294ed767de093c905909531c7dd4dc6eb378",
    "timebaseSha256": "899746d3048d239bc0032375d412a109ea04b055df19df1b7b08dc3e73aa5ca0",
    "mixSha256": "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e",
    "v166EventLogicBlob": "6561194742093d76bab452ef0bbb0b889724dc4e",
    "v165EventLogicBlob": "b296b3c322c13f8963f253f9b0666db66766a178",
    "v164EventLogicBlob": "62303877a1971f75cacda002c5ad921680161674",
    "guitarCount": 1050,
    "bassCount": 402,
    "subdivisionCount": 1805,
}

SR = 22050
HOP = 256
EPS = 1e-12


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def load_mono(path: Path) -> np.ndarray:
    import librosa

    y, sr = librosa.load(str(path), sr=SR, mono=True)
    y = np.asarray(y, dtype=np.float32)
    if sr != SR or y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid audio load: {path}")
    return y


def onset_env(y: np.ndarray) -> np.ndarray:
    import librosa

    x = np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("invalid onset envelope")
    return x


def positive_unit_scale(x: np.ndarray) -> np.ndarray:
    x = np.maximum(np.asarray(x, dtype=float), 0.0)
    peak = float(np.max(x)) if x.size else 0.0
    if not math.isfinite(peak) or peak <= EPS:
        raise RuntimeError("unit-scale envelope lacks positive evidence")
    return x / peak


def shared_onset_env(mix: np.ndarray, drums: np.ndarray) -> np.ndarray:
    mix_env = onset_env(mix)
    drums_env = onset_env(drums)
    n = min(len(mix_env), len(drums_env))
    if n == 0:
        raise RuntimeError("empty shared onset envelope")
    # Exact frozen V162->V166 behavior.
    return 0.65 * positive_unit_scale(drums_env[:n]) + 0.35 * positive_unit_scale(mix_env[:n])


def import_event_logic(repo_root: Path):
    v166 = repo_root / "validation/v166_cpu_autonomous/event_logic_v166.py"
    v165 = repo_root / "validation/v165_cpu_autonomous/event_logic_v165.py"
    v164 = repo_root / "validation/v164_cpu_autonomous/event_logic_v164.py"
    pins = {
        v166: EXPECTED["v166EventLogicBlob"],
        v165: EXPECTED["v165EventLogicBlob"],
        v164: EXPECTED["v164EventLogicBlob"],
    }
    for path, expected in pins.items():
        if not path.is_file() or git_blob_sha(path) != expected:
            raise RuntimeError(f"frozen event-logic identity mismatch: {path}")
    spec = importlib.util.spec_from_file_location("_v168_frozen_v166_event_logic", v166)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load frozen V166 event logic")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def candidate_nominal_substep(lattice: list[float], k: int) -> float:
    if k == 0:
        return float(lattice[1] - lattice[0])
    if k == len(lattice) - 1:
        return float(lattice[-1] - lattice[-2])
    return 0.5 * float(lattice[k + 1] - lattice[k - 1])


def current_shared_support(event_logic, shared_env: np.ndarray, lattice: list[float], k: int) -> float:
    _beat_index, beat_start, beat_end = event_logic._candidate_beat_bounds(lattice, int(k))
    frame = event_logic.seconds_to_nearest_frame(float(lattice[k]), len(shared_env))
    support, _prov = event_logic.beat_support_unit(
        float(shared_env[frame]), shared_env, beat_start, beat_end
    )
    return float(support)


def select_from_rows(event_logic, event_time: float, nearest: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
    nearest_row = next(row for row in rows if int(row["step"]) == int(nearest))
    winner = sorted(
        rows,
        key=lambda r: (-float(r["score"]), abs(int(r["step"]) - int(nearest)), int(r["step"])),
    )[0]
    if (
        int(winner["step"]) != int(nearest)
        and float(winner["score"]) + event_logic.EPS
        < float(nearest_row["score"]) + event_logic.EVENT_NON_NEAREST_MARGIN
    ):
        winner = nearest_row
    return winner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    candidate_path = args.candidate.resolve()
    timebase_path = args.timebase.resolve()
    mix_path = args.mix.resolve()
    drums_path = args.drums.resolve()
    report_path = args.report.resolve()

    for path in (candidate_path, timebase_path, mix_path, drums_path):
        if not path.is_file():
            raise RuntimeError(f"missing functional-equivalence input: {path}")
    if report_path.exists():
        raise RuntimeError("functional-equivalence report is write-once")

    observed_hashes = {
        "candidateSha256": sha256_file(candidate_path),
        "timebaseSha256": sha256_file(timebase_path),
        "mixSha256": sha256_file(mix_path),
        "drumsSha256": sha256_file(drums_path),
    }
    for key in ("candidateSha256", "timebaseSha256", "mixSha256"):
        if observed_hashes[key] != EXPECTED[key]:
            raise RuntimeError(f"frozen input mismatch: {key}: {observed_hashes[key]} != {EXPECTED[key]}")

    candidate = load_json(candidate_path)
    timebase = load_json(timebase_path)
    streams = candidate.get("streams") or {}
    guitar = streams.get("combinedGuitar") or []
    bass = streams.get("bass") or []
    if len(guitar) != EXPECTED["guitarCount"] or len(bass) != EXPECTED["bassCount"]:
        raise RuntimeError("frozen V166 event counts mismatch")

    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds", [])]
    if len(lattice) != EXPECTED["subdivisionCount"]:
        raise RuntimeError(f"frozen lattice count mismatch: {len(lattice)}")
    if not all(math.isfinite(x) for x in lattice) or not all(lattice[i + 1] > lattice[i] for i in range(len(lattice) - 1)):
        raise RuntimeError("invalid frozen lattice")

    event_logic = import_event_logic(repo)
    mix_y = load_mono(mix_path)
    drums_y = load_mono(drums_path)
    current_shared = shared_onset_env(mix_y, drums_y)

    historical_support_by_step: dict[int, list[float]] = {}
    current_support_cache: dict[int, float] = {}
    option_count = 0
    score_recompute_mismatches = 0
    frozen_selection_mismatches = 0
    current_selection_changes = 0
    max_abs_shared_delta = 0.0
    max_abs_score_delta = 0.0
    changed_examples: list[dict[str, Any]] = []

    for stream_name, events in (("combinedGuitar", guitar), ("bass", bass)):
        for event_index, event in enumerate(events):
            selection = event.get("stepSelection") or {}
            nearest = int(selection.get("nearestStep"))
            frozen_winner = selection.get("winner") or {}
            frozen_winner_step = int(frozen_winner.get("step"))
            frozen_candidates = selection.get("candidates") or []
            if not frozen_candidates:
                raise RuntimeError(f"missing stepSelection candidates: {stream_name}[{event_index}]")
            event_time = float(event["startSeconds"])
            stored_rows: list[dict[str, Any]] = []
            current_rows: list[dict[str, Any]] = []

            for row in frozen_candidates:
                k = int(row["step"])
                if not 0 <= k < len(lattice):
                    raise RuntimeError("stored candidate step outside frozen lattice")
                option_count += 1
                old_shared = float(row["sharedSupport"])
                old_inst = float(row["instrumentSupport"])
                old_score = float(row["score"])
                historical_support_by_step.setdefault(k, []).append(old_shared)

                old_recomputed = float(
                    event_logic.event_step_score(
                        event_time,
                        float(lattice[k]),
                        candidate_nominal_substep(lattice, k),
                        old_inst,
                        old_shared,
                    )
                )
                if abs(old_recomputed - old_score) > 1e-12:
                    score_recompute_mismatches += 1

                if k not in current_support_cache:
                    current_support_cache[k] = current_shared_support(event_logic, current_shared, lattice, k)
                new_shared = current_support_cache[k]
                new_score = float(
                    event_logic.event_step_score(
                        event_time,
                        float(lattice[k]),
                        candidate_nominal_substep(lattice, k),
                        old_inst,
                        new_shared,
                    )
                )
                max_abs_shared_delta = max(max_abs_shared_delta, abs(new_shared - old_shared))
                max_abs_score_delta = max(max_abs_score_delta, abs(new_score - old_score))
                stored_rows.append({"step": k, "score": old_score})
                current_rows.append({"step": k, "score": new_score})

            frozen_reselected = select_from_rows(event_logic, event_time, nearest, stored_rows)
            if int(frozen_reselected["step"]) != frozen_winner_step:
                frozen_selection_mismatches += 1

            current_winner = select_from_rows(event_logic, event_time, nearest, current_rows)
            current_step = int(current_winner["step"])
            if current_step != frozen_winner_step:
                current_selection_changes += 1
                if len(changed_examples) < 20:
                    changed_examples.append({
                        "stream": stream_name,
                        "eventIndex": event_index,
                        "midi": int(event.get("midi", -1)),
                        "startSeconds": event_time,
                        "nearestStep": nearest,
                        "frozenWinnerStep": frozen_winner_step,
                        "currentWinnerStep": current_step,
                    })

    inconsistent_historical_steps = 0
    max_historical_repeat_spread = 0.0
    for values in historical_support_by_step.values():
        spread = max(values) - min(values)
        max_historical_repeat_spread = max(max_historical_repeat_spread, spread)
        if spread > 1e-12:
            inconsistent_historical_steps += 1

    covered_steps = sorted(historical_support_by_step)
    uncovered_steps = [k for k in range(len(lattice)) if k not in historical_support_by_step]
    coverage = len(covered_steps) / len(lattice)

    # Strict preregistered acceptance: no hidden extrapolation from observed event
    # neighborhoods. Incomplete lattice coverage is fail-closed even if all observed
    # historical event decisions remain unchanged.
    exact_full_lattice_decision_equivalence = bool(
        not uncovered_steps
        and score_recompute_mismatches == 0
        and frozen_selection_mismatches == 0
        and inconsistent_historical_steps == 0
        and current_selection_changes == 0
    )

    if exact_full_lattice_decision_equivalence:
        status = "FULL_LATTICE_GRID_DECISION_EQUIVALENT"
        validation = "PASS"
    elif current_selection_changes == 0 and frozen_selection_mismatches == 0 and score_recompute_mismatches == 0 and inconsistent_historical_steps == 0:
        status = "OBSERVED_EVENT_NEIGHBORHOODS_EQUIVALENT_BUT_LATTICE_COVERAGE_INCOMPLETE"
        validation = "FAIL_CLOSED"
    else:
        status = "GRID_DECISION_DIVERGENCE"
        validation = "FAIL"

    report = {
        "schema": "dadrock.tabs.v168.splitmysong-shared-context-equivalence.v1",
        "status": status,
        "validation": validation,
        "question": "Does the drifted Demucs drums stem preserve the frozen V166 shared-onset grid decisions?",
        "inputIdentities": observed_hashes,
        "frozenIdentities": {
            "candidateSha256": EXPECTED["candidateSha256"],
            "timebaseSha256": EXPECTED["timebaseSha256"],
            "mixSha256": EXPECTED["mixSha256"],
            "eventLogicGitBlob": EXPECTED["v166EventLogicBlob"],
        },
        "counts": {
            "guitarEvents": len(guitar),
            "bassEvents": len(bass),
            "eventTotal": len(guitar) + len(bass),
            "optionRows": option_count,
            "latticeSteps": len(lattice),
            "coveredLatticeSteps": len(covered_steps),
            "uncoveredLatticeSteps": len(uncovered_steps),
            "currentSelectionChanges": current_selection_changes,
            "frozenSelectionRecomputeMismatches": frozen_selection_mismatches,
            "storedScoreRecomputeMismatches": score_recompute_mismatches,
            "inconsistentRepeatedHistoricalSupportSteps": inconsistent_historical_steps,
        },
        "coverage": {
            "ratio": coverage,
            "percent": 100.0 * coverage,
            "firstUncoveredSteps": uncovered_steps[:50],
        },
        "continuousDrift": {
            "maxAbsSharedSupportDelta": max_abs_shared_delta,
            "maxAbsEventStepScoreDelta": max_abs_score_delta,
            "maxHistoricalRepeatedSupportSpread": max_historical_repeat_spread,
        },
        "changedDecisionExamples": changed_examples,
        "acceptance": {
            "requiresAllLatticeStepsCovered": True,
            "requiresZeroCurrentSelectionChanges": True,
            "requiresZeroFrozenSelectionRecomputeMismatches": True,
            "requiresZeroStoredScoreRecomputeMismatches": True,
            "requiresConsistentRepeatedHistoricalSupport": True,
            "byteEquivalenceClaimed": False,
        },
        "safety": {
            "basicPitchImported": False,
            "pitchInferenceInvoked": False,
            "candidateGenerated": False,
            "professionalReferenceRead": False,
            "scorerRead": False,
            "referenceFacingScoreCalls": 0,
            "splitMySongGuitarRead": False,
            "gpuCudaUsed": False,
        },
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"status={status}")
    print(f"validation={validation}")
    print(f"coveredLatticeSteps={len(covered_steps)}/{len(lattice)} ({100.0 * coverage:.6f}%)")
    print(f"currentSelectionChanges={current_selection_changes}")
    print(f"maxAbsSharedSupportDelta={max_abs_shared_delta:.17g}")
    print(f"maxAbsEventStepScoreDelta={max_abs_score_delta:.17g}")
    print(f"reportSha256={sha256_file(report_path)}")
    print("No Basic Pitch inference, scorer, professional reference, or SplitMySong Guitar access occurred.")
    return 0 if validation == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
