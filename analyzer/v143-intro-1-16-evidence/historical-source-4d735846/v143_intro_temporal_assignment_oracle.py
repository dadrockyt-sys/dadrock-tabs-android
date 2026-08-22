from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-temporal-assignment-oracle.json"
)

FIRST_MEASURE = 1
LAST_MEASURE = 16
STEPS_PER_MEASURE = 16


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _global_step(measure: int, step: int) -> int:
    return (int(measure) - FIRST_MEASURE) * STEPS_PER_MEASURE + int(step)


def _reference_events(reference: dict[str, Any]) -> list[dict[str, int]]:
    events: list[dict[str, int]] = []
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if not FIRST_MEASURE <= number <= LAST_MEASURE:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            midi = _safe_int(raw.get("midiPitch"))
            if midi is None:
                midi = _safe_int(raw.get("soundingMidiPitch"))
            if midi is None:
                continue
            step = int(raw.get("step") or 0)
            events.append(
                {
                    "measure": number,
                    "step": step,
                    "globalStep": _global_step(number, step),
                    "midi": midi,
                }
            )
    return events


def _candidate_atoms(cache: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = cache.get("analysis", {}) or {}
    rows = analysis.get("introCandidates", []) or analysis.get("introRows", []) or []
    atoms: list[dict[str, Any]] = []
    seen: set[tuple[int, int, int]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        step = int(row.get("step") or 0)
        if not FIRST_MEASURE <= measure <= LAST_MEASURE or not 0 <= step < STEPS_PER_MEASURE:
            continue
        hypotheses = list(row.get("pitchHypotheses", []) or [])
        dominant = _safe_int(row.get("dominantMidi"))
        if dominant is not None and all(_safe_int(h.get("midi")) != dominant for h in hypotheses if isinstance(h, dict)):
            hypotheses.append({"midi": dominant})
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                continue
            midi = _safe_int(hypothesis.get("midi"))
            if midi is None:
                continue
            key = (measure, step, midi)
            if key in seen:
                continue
            seen.add(key)
            atoms.append(
                {
                    "measure": measure,
                    "step": step,
                    "globalStep": _global_step(measure, step),
                    "midi": midi,
                    "sourceCount": int(hypothesis.get("sourceCount") or 0),
                    "eventCount": int(hypothesis.get("eventCount") or 0),
                    "maxAmplitude": float(hypothesis.get("maxAmplitude") or 0.0),
                    "minGridError": float(hypothesis.get("minGridError") or 0.0),
                    "maxDuration": float(hypothesis.get("maxDuration") or 0.0),
                }
            )
    return atoms


def _maximum_matching(
    refs: list[dict[str, int]],
    atoms: list[dict[str, Any]],
    tolerance_steps: int,
) -> tuple[int, list[int], list[dict[str, Any]]]:
    atoms_by_midi: dict[int, list[int]] = defaultdict(list)
    for index, atom in enumerate(atoms):
        atoms_by_midi[int(atom["midi"])].append(index)

    adjacency: list[list[int]] = []
    for ref in refs:
        candidates = [
            atom_index
            for atom_index in atoms_by_midi.get(int(ref["midi"]), [])
            if abs(int(atoms[atom_index]["globalStep"]) - int(ref["globalStep"])) <= tolerance_steps
        ]
        candidates.sort(
            key=lambda atom_index: (
                abs(int(atoms[atom_index]["globalStep"]) - int(ref["globalStep"])),
                -int(atoms[atom_index].get("sourceCount") or 0),
                -float(atoms[atom_index].get("maxAmplitude") or 0.0),
                float(atoms[atom_index].get("minGridError") or 0.0),
                atom_index,
            )
        )
        adjacency.append(candidates)

    matched_atom_to_ref: dict[int, int] = {}

    def augment(ref_index: int, visited: set[int]) -> bool:
        for atom_index in adjacency[ref_index]:
            if atom_index in visited:
                continue
            visited.add(atom_index)
            previous_ref = matched_atom_to_ref.get(atom_index)
            if previous_ref is None or augment(previous_ref, visited):
                matched_atom_to_ref[atom_index] = ref_index
                return True
        return False

    order = sorted(range(len(refs)), key=lambda idx: (len(adjacency[idx]), refs[idx]["globalStep"], refs[idx]["midi"]))
    matches = 0
    for ref_index in order:
        if augment(ref_index, set()):
            matches += 1

    offsets: list[int] = []
    examples: list[dict[str, Any]] = []
    for atom_index, ref_index in matched_atom_to_ref.items():
        ref = refs[ref_index]
        atom = atoms[atom_index]
        offset = int(atom["globalStep"]) - int(ref["globalStep"])
        offsets.append(offset)
        if len(examples) < 24 and offset != 0:
            examples.append(
                {
                    "referenceMeasure": ref["measure"],
                    "referenceStep": ref["step"],
                    "midi": ref["midi"],
                    "candidateMeasure": atom["measure"],
                    "candidateStep": atom["step"],
                    "offsetSteps": offset,
                    "sourceCount": atom.get("sourceCount"),
                    "maxAmplitude": atom.get("maxAmplitude"),
                    "minGridError": atom.get("minGridError"),
                }
            )
    return matches, offsets, examples


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _phase_shift_score(refs: list[dict[str, int]], atoms: list[dict[str, Any]], shift: int) -> int:
    atom_keys = {(int(atom["globalStep"]), int(atom["midi"])) for atom in atoms}
    return sum(
        1
        for ref in refs
        if (int(ref["globalStep"]) + shift, int(ref["midi"])) in atom_keys
    )


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Analysis cache missing: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    refs = _reference_events(reference)
    atoms = _candidate_atoms(cache)
    if not refs or not atoms:
        raise RuntimeError("Reference events or candidate atoms are empty")

    tolerance_rows: list[dict[str, Any]] = []
    all_examples: list[dict[str, Any]] = []
    for tolerance in range(0, 5):
        matches, offsets, examples = _maximum_matching(refs, atoms, tolerance)
        histogram = Counter(offsets)
        row = {
            "toleranceSteps": tolerance,
            "matchedReferenceEvents": matches,
            "referenceEventCount": len(refs),
            "collisionAwareRecallPercent": _pct(matches / len(refs)),
            "offsetHistogram": {str(k): int(v) for k, v in sorted(histogram.items())},
        }
        tolerance_rows.append(row)
        if tolerance == 2:
            all_examples = examples

    phase_rows = [
        {
            "globalShiftSteps": shift,
            "exactPitchHits": _phase_shift_score(refs, atoms, shift),
            "recallPercent": _pct(_phase_shift_score(refs, atoms, shift) / len(refs)),
        }
        for shift in range(-4, 5)
    ]
    phase_rows.sort(key=lambda row: (row["exactPitchHits"], -abs(row["globalShiftSteps"])), reverse=True)

    tol2 = next(row for row in tolerance_rows if row["toleranceSteps"] == 2)
    exact = next(row for row in tolerance_rows if row["toleranceSteps"] == 0)
    recoverable_gain = float(tol2["collisionAwareRecallPercent"]) - float(exact["collisionAwareRecallPercent"])

    if float(tol2["collisionAwareRecallPercent"]) >= 85.0 and recoverable_gain >= 15.0:
        diagnosis = "temporal-reassignment-is-primary-next-step"
    elif float(tol2["collisionAwareRecallPercent"]) >= 80.0:
        diagnosis = "existing-basic-pitch-universe-is-viable-with-global-decoding"
    else:
        diagnosis = "candidate-pitch-universe-needs-a-stronger-transcription-engine"

    report = {
        "referenceEventCount": len(refs),
        "candidatePitchAtomCount": len(atoms),
        "toleranceSweep": tolerance_rows,
        "bestGlobalPhaseShifts": phase_rows[:5],
        "tolerance2MovedMatchExamples": all_examples,
        "diagnosis": diagnosis,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineOracle": True,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 COLLISION-AWARE TEMPORAL PITCH ORACLE ===")
    print("referenceEventCount:", len(refs))
    print("candidatePitchAtomCount:", len(atoms))
    print()
    print("tol  matches  recall")
    for row in tolerance_rows:
        print(
            f"{row['toleranceSteps']:>3}  "
            f"{row['matchedReferenceEvents']:>7}  "
            f"{row['collisionAwareRecallPercent']:>6.3f}%"
        )
    print()
    print("BEST GLOBAL PHASE SHIFTS:")
    for row in phase_rows[:5]:
        print(
            f"shift {row['globalShiftSteps']:+d}: "
            f"{row['exactPitchHits']}/{len(refs)} = {row['recallPercent']:.3f}%"
        )
    print()
    print("DIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
