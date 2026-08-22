from __future__ import annotations

import json
import math
from collections import defaultdict
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
    / "intro-repetition-consensus-decoder.json"
)

FIRST_MEASURE = 1
LAST_MEASURE = 16
STEPS_PER_MEASURE = 16
DEVELOPMENT_MEASURES = tuple(range(1, 13))
HOLDOUT_MEASURES = tuple(range(13, 17))


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0 else 2.0 * precision * recall / (precision + recall)


def _candidate_atoms(cache: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = cache.get("analysis", {}) or {}
    rows = analysis.get("introCandidates", []) or analysis.get("introRows", []) or []
    atoms: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        step = int(row.get("step") or 0)
        if not FIRST_MEASURE <= measure <= LAST_MEASURE or not 0 <= step < STEPS_PER_MEASURE:
            continue
        hypotheses = list(row.get("pitchHypotheses", []) or [])
        dominant = _safe_int(row.get("dominantMidi"))
        if dominant is not None and all(
            _safe_int(h.get("midi")) != dominant
            for h in hypotheses
            if isinstance(h, dict)
        ):
            hypotheses.append({"midi": dominant})
        for hypothesis in hypotheses:
            if not isinstance(hypothesis, dict):
                continue
            midi = _safe_int(hypothesis.get("midi"))
            if midi is None:
                continue
            atoms.append(
                {
                    "measure": measure,
                    "step": step,
                    "midi": midi,
                    "sourceCount": max(0, int(hypothesis.get("sourceCount") or 0)),
                    "eventCount": max(0, int(hypothesis.get("eventCount") or 0)),
                    "maxAmplitude": max(0.0, _safe_float(hypothesis.get("maxAmplitude"))),
                    "minGridError": max(0.0, _safe_float(hypothesis.get("minGridError"))),
                    "maxDuration": max(0.0, _safe_float(hypothesis.get("maxDuration"))),
                }
            )
    return atoms


def _atom_quality(atom: dict[str, Any]) -> float:
    source = min(float(atom.get("sourceCount") or 0) / 2.0, 1.0)
    event = min(float(atom.get("eventCount") or 0) / 2.0, 1.0)
    amplitude = min(max(float(atom.get("maxAmplitude") or 0.0), 0.0), 1.0)
    grid = 1.0 - min(max(float(atom.get("minGridError") or 0.0), 0.0) / 0.10, 1.0)
    duration = min(max(float(atom.get("maxDuration") or 0.0), 0.0) / 0.40, 1.0)
    return (source + event + amplitude + grid + duration) / 5.0


def _reference_sets(
    reference: dict[str, Any], measures: set[int]
) -> dict[tuple[int, int], set[int]]:
    output: dict[tuple[int, int], set[int]] = {}
    for measure in reference.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number not in measures:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            step = int(event.get("step") or 0)
            midi = _safe_int(event.get("midiPitch"))
            if midi is None:
                midi = _safe_int(event.get("soundingMidiPitch"))
            if midi is not None:
                output.setdefault((number, step), set()).add(midi)
    return output


def _grade(
    reference: dict[tuple[int, int], set[int]],
    predicted: dict[tuple[int, int], set[int]],
) -> dict[str, Any]:
    ref_locations = set(reference)
    pred_locations = set(predicted)
    location_hits = len(ref_locations & pred_locations)
    location_precision = location_hits / max(len(pred_locations), 1)
    location_recall = location_hits / max(len(ref_locations), 1)

    ref_events = sum(len(values) for values in reference.values())
    pred_events = sum(len(values) for values in predicted.values())
    pitch_hits = sum(
        len(expected & predicted.get(location, set()))
        for location, expected in reference.items()
    )
    pitch_precision = pitch_hits / max(pred_events, 1)
    pitch_recall = pitch_hits / max(ref_events, 1)

    exact_sets = sum(
        1
        for location, expected in reference.items()
        if predicted.get(location, set()) == expected
    )

    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(location_precision),
        "locationRecallPercent": _pct(location_recall),
        "locationF1Percent": _pct(_f1(location_precision, location_recall)),
        "referencePitchEventCount": ref_events,
        "predictedPitchEventCount": pred_events,
        "pitchPrecisionPercent": _pct(pitch_precision),
        "pitchRecallPercent": _pct(pitch_recall),
        "pitchF1Percent": _pct(_f1(pitch_precision, pitch_recall)),
        "exactPitchSetPercent": _pct(exact_sets / max(len(ref_locations), 1)),
    }


def _index_atoms(atoms: list[dict[str, Any]]) -> dict[int, dict[int, list[dict[str, Any]]]]:
    indexed: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for atom in atoms:
        indexed[int(atom["measure"])][int(atom["step"])].append(atom)
    return indexed


def _measure_has_pitch_near(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measure: int,
    target_step: int,
    midi: int,
    tolerance_steps: int,
) -> bool:
    for delta in range(-tolerance_steps, tolerance_steps + 1):
        step = target_step + delta
        if not 0 <= step < STEPS_PER_MEASURE:
            continue
        if any(int(atom["midi"]) == midi for atom in indexed.get(measure, {}).get(step, [])):
            return True
    return False


def _recurrence_support(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    *,
    target_measure: int,
    target_step: int,
    midi: int,
    tolerance_steps: int,
    phase_modulus: int,
) -> tuple[float, float]:
    development = [m for m in DEVELOPMENT_MEASURES if m != target_measure]
    if not development:
        return 0.0, 0.0
    overall_hits = sum(
        1
        for measure in development
        if _measure_has_pitch_near(indexed, measure, target_step, midi, tolerance_steps)
    )
    overall = overall_hits / len(development)

    phase_group = [
        measure
        for measure in development
        if (measure - FIRST_MEASURE) % phase_modulus
        == (target_measure - FIRST_MEASURE) % phase_modulus
    ]
    if not phase_group:
        phase = overall
    else:
        phase_hits = sum(
            1
            for measure in phase_group
            if _measure_has_pitch_near(indexed, measure, target_step, midi, tolerance_steps)
        )
        phase = phase_hits / len(phase_group)
    return overall, phase


def _decode_measure(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measure: int,
    config: dict[str, Any],
) -> dict[tuple[int, int], set[int]]:
    tolerance_steps = int(config["toleranceSteps"])
    recurrence_weight = float(config["recurrenceWeight"])
    phase_weight = float(config["phaseWeight"])
    local_weight = float(config["localWeight"])
    distance_penalty = float(config["distancePenalty"])
    minimum_score = float(config["minimumScore"])
    second_ratio = float(config["secondRatio"])
    max_polyphony = int(config["maxPolyphony"])
    phase_modulus = int(config["phaseModulus"])

    predicted: dict[tuple[int, int], set[int]] = {}
    measure_atoms = indexed.get(measure, {})

    for target_step in range(STEPS_PER_MEASURE):
        by_midi: dict[int, dict[str, float]] = {}
        for delta in range(-tolerance_steps, tolerance_steps + 1):
            source_step = target_step + delta
            if not 0 <= source_step < STEPS_PER_MEASURE:
                continue
            for atom in measure_atoms.get(source_step, []):
                midi = int(atom["midi"])
                quality = _atom_quality(atom)
                local_value = quality - distance_penalty * abs(delta)
                current = by_midi.setdefault(
                    midi,
                    {"local": -999.0, "distance": float(abs(delta))},
                )
                if local_value > current["local"]:
                    current["local"] = local_value
                    current["distance"] = float(abs(delta))

        scored: list[tuple[float, int]] = []
        for midi, local in by_midi.items():
            recurrence, phase = _recurrence_support(
                indexed,
                target_measure=measure,
                target_step=target_step,
                midi=midi,
                tolerance_steps=tolerance_steps,
                phase_modulus=phase_modulus,
            )
            score = (
                local_weight * max(local["local"], 0.0)
                + recurrence_weight * recurrence
                + phase_weight * phase
            )
            scored.append((score, midi))

        scored.sort(reverse=True)
        if not scored or scored[0][0] < minimum_score:
            continue

        chosen = {int(scored[0][1])}
        if max_polyphony >= 2 and len(scored) >= 2:
            first_score = max(scored[0][0], 1e-9)
            if scored[1][0] >= minimum_score and scored[1][0] / first_score >= second_ratio:
                chosen.add(int(scored[1][1]))
        if max_polyphony >= 3 and len(scored) >= 3:
            first_score = max(scored[0][0], 1e-9)
            if scored[2][0] >= minimum_score and scored[2][0] / first_score >= second_ratio:
                chosen.add(int(scored[2][1]))

        predicted[(measure, target_step)] = chosen

    return predicted


def _decode_measures(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measures: tuple[int, ...],
    config: dict[str, Any],
) -> dict[tuple[int, int], set[int]]:
    output: dict[tuple[int, int], set[int]] = {}
    for measure in measures:
        output.update(_decode_measure(indexed, measure, config))
    return output


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Analysis cache missing: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Professional reference missing: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    atoms = _candidate_atoms(cache)
    indexed = _index_atoms(atoms)
    development_reference = _reference_sets(reference, set(DEVELOPMENT_MEASURES))
    holdout_reference = _reference_sets(reference, set(HOLDOUT_MEASURES))

    configs: list[dict[str, Any]] = []
    for tolerance_steps in (1, 2):
        for recurrence_weight in (1.0, 2.0, 3.0):
            for phase_weight in (0.0, 1.0, 2.0):
                for local_weight in (0.25, 0.5, 1.0):
                    for distance_penalty in (0.0, 0.15, 0.30):
                        for minimum_score in (0.75, 1.0, 1.25, 1.5, 1.75, 2.0):
                            for second_ratio in (0.55, 0.70, 0.85):
                                for max_polyphony in (1, 2):
                                    for phase_modulus in (2, 4):
                                        config = {
                                            "toleranceSteps": tolerance_steps,
                                            "recurrenceWeight": recurrence_weight,
                                            "phaseWeight": phase_weight,
                                            "localWeight": local_weight,
                                            "distancePenalty": distance_penalty,
                                            "minimumScore": minimum_score,
                                            "secondRatio": second_ratio,
                                            "maxPolyphony": max_polyphony,
                                            "phaseModulus": phase_modulus,
                                        }
                                        predicted = _decode_measures(
                                            indexed, DEVELOPMENT_MEASURES, config
                                        )
                                        grade = _grade(development_reference, predicted)
                                        objective = (
                                            0.80 * grade["pitchF1Percent"]
                                            + 0.15 * grade["pitchRecallPercent"]
                                            + 0.05 * grade["locationF1Percent"]
                                        )
                                        configs.append(
                                            {
                                                **config,
                                                "developmentObjectivePercent": round(objective, 3),
                                                "development": grade,
                                            }
                                        )

    configs.sort(
        key=lambda row: (
            row["developmentObjectivePercent"],
            row["development"]["pitchF1Percent"],
            row["development"]["pitchRecallPercent"],
        ),
        reverse=True,
    )
    best = configs[0]
    best_config = {
        key: value
        for key, value in best.items()
        if key not in {"development", "developmentObjectivePercent"}
    }
    best_config["developmentObjectivePercent"] = best["developmentObjectivePercent"]

    holdout_prediction = _decode_measures(indexed, HOLDOUT_MEASURES, best_config)
    holdout_grade = _grade(holdout_reference, holdout_prediction)

    report = {
        "decoderFamily": "reference-free-repetition-consensus-temporal-decoder",
        "candidatePitchAtomCount": len(atoms),
        "developmentMeasures": list(DEVELOPMENT_MEASURES),
        "holdoutMeasures": list(HOLDOUT_MEASURES),
        "bestDevelopmentConfiguration": best_config,
        "development": best["development"],
        "holdout": holdout_grade,
        "topDevelopmentConfigurations": configs[:20],
        "professionalReferenceUsedByDecoder": False,
        "professionalReferenceUsedOnlyForOfflineConfigurationSelectionAndGrading": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 REPETITION-CONSENSUS TEMPORAL DECODER ===")
    print("candidatePitchAtomCount:", len(atoms))
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(best_config, indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(best["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to choose configuration):")
    print(json.dumps(holdout_grade, indent=2))
    print()
    print("Professional reference used by decoder: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
