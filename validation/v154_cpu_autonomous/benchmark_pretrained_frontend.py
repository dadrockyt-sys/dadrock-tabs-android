#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
TEMPO_BPM = 129.19921875
STEPS_PER_BEAT = 4
STEPS_PER_MEASURE = 16
STEP_SECONDS = (60.0 / TEMPO_BPM) / STEPS_PER_BEAT
LOCAL_TOLERANCE_SECONDS = 0.5 * STEP_SECONDS
GROSS_TOLERANCE_SECONDS = 2.0 * STEP_SECONDS
MIN_MIDI = 40
MAX_MIDI = 88
REFERENCE_NOTE_COUNT = 946
EXPECTED_GOLD_SHA256 = "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac"
ACCEPTED_BASELINE = {
    "localPitchTimingF1": 0.06698564593301436,
    "localPitchMatches": 70,
    "grossPitchMatches": 189,
    "criticalMismatchCount": 1712,
    "pitchContentF1": 0.35406698564593303,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_path(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise ValueError(f"model path does not exist: {path}")
    h = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = child.relative_to(path).as_posix().encode("utf-8")
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        payload = child.read_bytes()
        h.update(len(payload).to_bytes(8, "big"))
        h.update(payload)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def hz_for_midi(midi: int) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def grid_location(seconds: float) -> dict[str, Any]:
    absolute_step_float = seconds / STEP_SECONDS
    nearest_absolute_step = int(round(absolute_step_float))
    nearest_measure = nearest_absolute_step // STEPS_PER_MEASURE + 1
    nearest_step = nearest_absolute_step % STEPS_PER_MEASURE
    continuous_measure = int(math.floor(max(0.0, absolute_step_float) / STEPS_PER_MEASURE)) + 1
    continuous_step = absolute_step_float - (continuous_measure - 1) * STEPS_PER_MEASURE
    return {
        "absoluteStepFloat": absolute_step_float,
        "nearestAbsoluteStep": nearest_absolute_step,
        "nearestMeasure": nearest_measure,
        "nearestStep": nearest_step,
        "continuousMeasure": continuous_measure,
        "continuousStep": continuous_step,
        "quantizationErrorSteps": absolute_step_float - nearest_absolute_step,
    }


def json_pitch_bend(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return list(value)
    return value


def transcribe(audio: Path, branch_id: str, audio_role: str, output: Path) -> int:
    if output.exists():
        raise RuntimeError(f"one-use transcription output already exists: {output}")
    if not audio.is_file():
        raise FileNotFoundError(audio)

    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    model_path = Path(ICASSP_2022_MODEL_PATH)
    model_sha = sha256_path(model_path)
    package_version = importlib.metadata.version("basic-pitch")
    if package_version != "0.4.0":
        raise RuntimeError(f"Basic Pitch version mismatch: {package_version}")

    _model_output, _midi_data, note_events = predict(
        audio,
        model_or_model_path=model_path,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length=127.7,
        minimum_frequency=hz_for_midi(MIN_MIDI),
        maximum_frequency=hz_for_midi(MAX_MIDI),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )

    rows: list[dict[str, Any]] = []
    for source_index, note in enumerate(note_events):
        if len(note) < 4:
            raise RuntimeError(f"unexpected Basic Pitch note tuple: {note!r}")
        start = float(note[0])
        end = float(note[1])
        midi = int(round(float(note[2])))
        amplitude = float(note[3])
        pitch_bend = note[4] if len(note) > 4 else None
        if not (math.isfinite(start) and math.isfinite(end) and math.isfinite(amplitude)):
            raise RuntimeError("non-finite Basic Pitch note")
        if end < start:
            raise RuntimeError("Basic Pitch note ends before it starts")
        if midi < MIN_MIDI or midi > MAX_MIDI:
            raise RuntimeError(f"Basic Pitch emitted MIDI outside fixed guitar range: {midi}")
        grid = grid_location(start)
        duration_steps = max(1, int(round((end - start) / STEP_SECONDS)))
        rows.append(
            {
                "sourceIndex": source_index,
                "startSeconds": start,
                "endSeconds": end,
                "durationSeconds": end - start,
                "durationStepsNearest": duration_steps,
                "midi": midi,
                "amplitude": amplitude,
                "pitchBend": json_pitch_bend(pitch_bend),
                **grid,
            }
        )

    payload = {
        "schema": "dadrock.tabs.v154.basic-pitch-transcription.v1",
        "classification": "reference-free-pretrained-cpu-note-transcription",
        "branchId": branch_id,
        "audioRole": audio_role,
        "audio": {
            "path": str(audio),
            "bytes": audio.stat().st_size,
            "sha256": sha256_file(audio),
        },
        "grid": {
            "tempoBpm": TEMPO_BPM,
            "stepsPerBeat": STEPS_PER_BEAT,
            "stepsPerMeasure": STEPS_PER_MEASURE,
            "stepDurationSeconds": STEP_SECONDS,
        },
        "basicPitch": {
            "packageVersion": package_version,
            "modelPath": str(model_path),
            "modelSha256": model_sha,
            "onsetThreshold": 0.5,
            "frameThreshold": 0.3,
            "minimumNoteLengthMs": 127.7,
            "minimumMidi": MIN_MIDI,
            "maximumMidi": MAX_MIDI,
            "multiplePitchBends": False,
            "melodiaTrick": True,
        },
        "noteEventCount": len(rows),
        "noteEvents": rows,
        "safety": {
            "goldOrReferenceRead": False,
            "humanCorrection": False,
            "thresholdSweep": False,
            "goldGuidedFiltering": False,
            "modalUsed": False,
            "cudaGpuUsed": False,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }
    write_json(output, payload)
    print(json.dumps({
        "branchId": branch_id,
        "noteEventCount": len(rows),
        "modelSha256": model_sha,
        "audioSha256": payload["audio"]["sha256"],
        "goldOrReferenceRead": False,
        "cudaGpuUsed": False,
    }, sort_keys=True))
    return 0


def flatten_gold(reference: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for measure_obj in reference.get("measures") or []:
        measure = int(measure_obj["measure"])
        for onset in measure_obj.get("events") or []:
            step = int(onset["step"])
            absolute_step = (measure - 1) * STEPS_PER_MEASURE + step
            onset_seconds = absolute_step * STEP_SECONDS
            for note in onset.get("notes") or []:
                rows.append({
                    "measure": measure,
                    "step": step,
                    "absoluteStep": absolute_step,
                    "onsetSeconds": onset_seconds,
                    "midi": int(note["midi"]),
                })
    return rows


def transcription_notes(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for note in payload.get("noteEvents") or []:
        start = float(note["startSeconds"])
        nearest_absolute_step = int(round(start / STEP_SECONDS))
        measure = nearest_absolute_step // STEPS_PER_MEASURE + 1
        step = nearest_absolute_step % STEPS_PER_MEASURE
        rows.append({
            "onsetSeconds": start,
            "measure": measure,
            "step": step,
            "midi": int(note["midi"]),
        })
    return rows


def greedy_same_pitch_time_match(
    generated: Sequence[Mapping[str, Any]],
    reference: Sequence[Mapping[str, Any]],
    tolerance_seconds: float,
) -> list[tuple[int, int, float]]:
    by_pitch_g: dict[int, list[int]] = {}
    by_pitch_r: dict[int, list[int]] = {}
    for i, note in enumerate(generated):
        by_pitch_g.setdefault(int(note["midi"]), []).append(i)
    for i, note in enumerate(reference):
        by_pitch_r.setdefault(int(note["midi"]), []).append(i)

    candidates: list[tuple[float, int, int]] = []
    for midi, g_indices in by_pitch_g.items():
        r_indices = by_pitch_r.get(midi, [])
        for gi in g_indices:
            gt = float(generated[gi]["onsetSeconds"])
            for ri in r_indices:
                delta = abs(gt - float(reference[ri]["onsetSeconds"]))
                if delta <= tolerance_seconds + 1e-12:
                    candidates.append((delta, gi, ri))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    used_g: set[int] = set()
    used_r: set[int] = set()
    pairs: list[tuple[int, int, float]] = []
    for delta, gi, ri in candidates:
        if gi in used_g or ri in used_r:
            continue
        used_g.add(gi)
        used_r.add(ri)
        pairs.append((gi, ri, delta))
    return pairs


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = matched / generated if generated else 1.0
    recall = matched / reference if reference else 1.0
    f1 = 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)
    return {
        "matched": matched,
        "generated": generated,
        "reference": reference,
        "falsePositive": generated - matched,
        "falseNegative": reference - matched,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def pitch_content_by_measure(
    generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    g = Counter((int(n["measure"]), int(n["midi"])) for n in generated)
    r = Counter((int(n["measure"]), int(n["midi"])) for n in reference)
    matched = sum((g & r).values())
    return prf(matched, sum(g.values()), sum(r.values()))


def exact_quantized_pitchset_f1(
    generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    def groups(rows: Sequence[Mapping[str, Any]]) -> Counter[tuple[int, tuple[int, ...]]]:
        by_step: dict[int, list[int]] = {}
        for n in rows:
            absolute_step = (int(n["measure"]) - 1) * STEPS_PER_MEASURE + int(n["step"])
            by_step.setdefault(absolute_step, []).append(int(n["midi"]))
        return Counter((step, tuple(sorted(midis))) for step, midis in by_step.items())
    g = groups(generated)
    r = groups(reference)
    matched = sum((g & r).values())
    return prf(matched, sum(g.values()), sum(r.values()))


def score_branch(payload: Mapping[str, Any], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    generated = transcription_notes(payload)
    local_pairs = greedy_same_pitch_time_match(generated, reference, LOCAL_TOLERANCE_SECONDS)
    gross_pairs = greedy_same_pitch_time_match(generated, reference, GROSS_TOLERANCE_SECONDS)
    local = prf(len(local_pairs), len(generated), len(reference))
    gross = prf(len(gross_pairs), len(generated), len(reference))
    measures_generated = {int(n["measure"]) for n in generated}
    measures_reference = {int(n["measure"]) for n in reference}
    missing_measures = sorted(measures_reference - measures_generated)
    critical = len(missing_measures) + (len(reference) - len(gross_pairs)) + (len(generated) - len(gross_pairs))
    local_deltas = sorted(float(d) for _, _, d in local_pairs)
    return {
        "branchId": payload["branchId"],
        "generatedNoteCount": len(generated),
        "localPitchTiming": local,
        "grossPitchTiming": gross,
        "pitchContentByMeasureDiagnostic": pitch_content_by_measure(generated, reference),
        "exactQuantizedChordPitchSetDiagnostic": exact_quantized_pitchset_f1(generated, reference),
        "criticalMismatchCount": critical,
        "criticalMismatchBreakdown": {
            "missingReferenceMeasures": len(missing_measures),
            "grossUnmatchedReferenceNotes": len(reference) - len(gross_pairs),
            "grossUnmatchedGeneratedNotes": len(generated) - len(gross_pairs),
        },
        "localTimingDeltaSeconds": {
            "minimum": min(local_deltas) if local_deltas else None,
            "median": local_deltas[len(local_deltas) // 2] if local_deltas else None,
            "maximum": max(local_deltas) if local_deltas else None,
        },
    }


def interpretation(best_f1: float) -> str:
    if best_f1 >= 0.20:
        return "BREAKTHROUGH_SIGNAL"
    if best_f1 >= 0.10 and best_f1 > ACCEPTED_BASELINE["localPitchTimingF1"]:
        return "PROMISING_RESET"
    if best_f1 > ACCEPTED_BASELINE["localPitchTimingF1"]:
        return "WEAK_GAIN"
    return "NO_GAIN"


def score(raw_path: Path, guitar_path: Path, gold_path: Path, output: Path) -> int:
    if output.exists():
        raise RuntimeError(f"one-use score output already exists: {output}")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    guitar = json.loads(guitar_path.read_text(encoding="utf-8"))
    for payload, expected in ((raw, "raw-basic-pitch"), (guitar, "demucs6-guitar-basic-pitch")):
        if payload.get("branchId") != expected:
            raise RuntimeError(f"branch identity mismatch: expected {expected}")
        safety = payload.get("safety") or {}
        if safety.get("goldOrReferenceRead") is not False or safety.get("humanCorrection") is not False:
            raise RuntimeError("transcription anti-leakage flag failed")
    if sha256_file(gold_path) != EXPECTED_GOLD_SHA256:
        raise RuntimeError("Gold SHA mismatch")
    reference_obj = json.loads(gold_path.read_text(encoding="utf-8"))
    reference = flatten_gold(reference_obj)
    if len(reference) != REFERENCE_NOTE_COUNT:
        raise RuntimeError(f"Gold note count mismatch: {len(reference)}")

    branches = [score_branch(raw, reference), score_branch(guitar, reference)]
    branches.sort(
        key=lambda r: (
            -float(r["localPitchTiming"]["f1"]),
            -float(r["grossPitchTiming"]["f1"]),
            str(r["branchId"]),
        )
    )
    best = branches[0]
    best_f1 = float(best["localPitchTiming"]["f1"])
    report = {
        "schema": "dadrock.tabs.v154.cpu-autonomous.phase-a-result.v1",
        "classification": "post-freeze-cpu-pretrained-frontend-calibration-comparison",
        "evaluationRole": "calibration architecture comparison, not unseen holdout",
        "primaryMetric": "continuous-time same-pitch onset F1 within plus/minus 0.5 frozen grid step",
        "secondaryMetric": "continuous-time same-pitch onset F1 within plus/minus 2.0 frozen grid steps",
        "localToleranceSeconds": LOCAL_TOLERANCE_SECONDS,
        "grossToleranceSeconds": GROSS_TOLERANCE_SECONDS,
        "stepDurationSeconds": STEP_SECONDS,
        "reference": {"sha256": EXPECTED_GOLD_SHA256, "noteCount": len(reference)},
        "acceptedBaseline": ACCEPTED_BASELINE,
        "branchesRanked": branches,
        "preferredFrontend": best["branchId"],
        "preferredLocalPitchTimingF1": best_f1,
        "absoluteLocalF1GainVsAccepted": best_f1 - ACCEPTED_BASELINE["localPitchTimingF1"],
        "relativeLocalF1MultiplierVsAccepted": best_f1 / ACCEPTED_BASELINE["localPitchTimingF1"] if ACCEPTED_BASELINE["localPitchTimingF1"] else None,
        "interpretation": interpretation(best_f1),
        "nextStagePolicy": "If the pretrained frontend beats accepted local pitch timing, use its frozen reference-free note proposals as inputs to a new CQT/onset/fretboard sequence decoder. Do not tune Basic Pitch thresholds from this Gold result.",
        "safety": {
            "predefinedBranches": 2,
            "humanCorrection": False,
            "thresholdSweep": False,
            "goldGuidedConstruction": False,
            "candidateModificationAfterScore": False,
            "modalUsed": False,
            "cudaGpuUsed": False,
            "mainOrProductionModified": False,
        },
    }
    write_json(output, report)
    print(json.dumps({
        "preferredFrontend": report["preferredFrontend"],
        "preferredLocalPitchTimingF1": report["preferredLocalPitchTimingF1"],
        "acceptedBaselineLocalPitchTimingF1": ACCEPTED_BASELINE["localPitchTimingF1"],
        "interpretation": report["interpretation"],
        "branches": [
            {
                "branchId": r["branchId"],
                "notes": r["generatedNoteCount"],
                "localF1": r["localPitchTiming"]["f1"],
                "grossF1": r["grossPitchTiming"]["f1"],
                "critical": r["criticalMismatchCount"],
            }
            for r in branches
        ],
        "modalUsed": False,
        "cudaGpuUsed": False,
    }, indent=2, sort_keys=True))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    t = sub.add_parser("transcribe")
    t.add_argument("--audio", required=True, type=Path)
    t.add_argument("--branch-id", required=True)
    t.add_argument("--audio-role", required=True)
    t.add_argument("--output", required=True, type=Path)
    s = sub.add_parser("score")
    s.add_argument("--raw", required=True, type=Path)
    s.add_argument("--guitar", required=True, type=Path)
    s.add_argument("--gold", required=True, type=Path)
    s.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    if args.mode == "transcribe":
        return transcribe(args.audio, args.branch_id, args.audio_role, args.output)
    return score(args.raw, args.guitar, args.gold, args.output)


if __name__ == "__main__":
    raise SystemExit(main())
