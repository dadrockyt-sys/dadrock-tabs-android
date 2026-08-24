from __future__ import annotations

import collections
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
ATTACK_COUNT = 725
STANDARD_TUNING = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}
STEPS_PER_MEASURE = 16


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def _summary(values: list[float]) -> dict[str, Any]:
    return {
        "count": len(values),
        "min": min(values) if values else None,
        "q10": _quantile(values, 0.10),
        "q25": _quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "mean": statistics.mean(values) if values else None,
        "q75": _quantile(values, 0.75),
        "q90": _quantile(values, 0.90),
        "max": max(values) if values else None,
    }


def _counter(counter: collections.Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def _hypotheses(attack: list[Any]) -> dict[int, list[Any]]:
    return {int(item[0]): item for item in attack[4]}


def _selected_notes(attack: list[Any]) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for note in attack[5]:
        midi = int(note[1])
        string = int(note[2])
        fret = int(note[3])
        if string not in STANDARD_TUNING:
            raise RuntimeError(f"invalid string index {string}")
        if STANDARD_TUNING[string] + fret != midi:
            raise RuntimeError(f"string/fret mapping mismatch midi={midi} string={string} fret={fret}")
        notes.append({
            "id": int(note[0]),
            "midi": midi,
            "string": string,
            "fret": fret,
            "sustain": bool(note[4]),
        })
    return notes


def _load_rows(evidence: dict[str, Any]) -> tuple[list[dict[str, Any]], float]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("approved frozen source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen source identity changed")
    if provenance.get("referenceFree") is not True:
        raise RuntimeError("frozen evidence is not reference-free")
    if provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("professional reference provenance is unsafe")
    if provenance.get("referenceRuntimeInputUsed") is not False:
        raise RuntimeError("reference entered runtime evidence")
    if provenance.get("preScorer") is not True:
        raise RuntimeError("evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    tempo = float(evidence.get("tempoBpm") or 0.0)
    if len(attacks) != ATTACK_COUNT or tempo <= 0.0:
        raise RuntimeError("frozen attack cardinality/tempo changed")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        time_seconds = float(attack[2])
        primary = int(attack[3])
        key = (measure, step)
        if key in seen:
            raise RuntimeError(f"duplicate frozen attack coordinate {key}")
        seen.add(key)
        hypotheses = _hypotheses(attack)
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        hyp = hypotheses[primary]
        primary_attack = float(hyp[1])
        primary_body = float(hyp[2])
        primary_persistence = float(hyp[3])
        primary_score = float(hyp[4])
        if not all(math.isfinite(v) for v in (time_seconds, primary_attack, primary_body, primary_persistence, primary_score)):
            raise RuntimeError(f"non-finite physical evidence at attack {index}")

        notes = _selected_notes(attack)
        primary_notes = [note for note in notes if int(note["midi"]) == primary]
        if not primary_notes:
            raise RuntimeError(f"primary missing from selected notes at attack {index}")
        primary_open_mappings = [note for note in primary_notes if int(note["fret"]) == 0]
        canonical_primary_note = min(primary_notes, key=lambda note: (int(note["fret"]), int(note["string"])))
        selected_midis = sorted({int(note["midi"]) for note in notes})
        rows.append({
            "index": index,
            "measure": measure,
            "step": step,
            "timeSeconds": time_seconds,
            "primary": primary,
            "primaryAttackSupport": primary_attack,
            "primaryBodySupport": primary_body,
            "attackMinusBody": primary_attack - primary_body,
            "primaryPersistenceSupport": primary_persistence,
            "primaryCombinedScore": primary_score,
            "hypothesisCount": len(hypotheses),
            "singleHypothesis": len(hypotheses) == 1,
            "primarySustainEvidence": any(bool(note["sustain"]) for note in primary_notes),
            "primaryHasOpenStringMapping": bool(primary_open_mappings),
            "canonicalPrimaryString": int(canonical_primary_note["string"]),
            "canonicalPrimaryFret": int(canonical_primary_note["fret"]),
            "openHighE64": primary == 64 and any(
                int(note["string"]) == 0 and int(note["fret"]) == 0 for note in primary_notes
            ),
            "selectedMidis": selected_midis,
            "selectedLowerPitchThanPrimary": any(midi < primary for midi in selected_midis),
        })
    rows.sort(key=lambda row: float(row["timeSeconds"]))
    return rows, tempo


def _group_summary(rows: list[dict[str, Any]], total: int) -> dict[str, Any]:
    return {
        "count": len(rows),
        "rateAllAttacks": len(rows) / total if total else None,
        "primaryAttackSupport": _summary([float(row["primaryAttackSupport"]) for row in rows]),
        "primaryBodySupport": _summary([float(row["primaryBodySupport"]) for row in rows]),
        "attackMinusBody": _summary([float(row["attackMinusBody"]) for row in rows]),
        "primaryPersistenceSupport": _summary([float(row["primaryPersistenceSupport"]) for row in rows]),
        "primaryCombinedScore": _summary([float(row["primaryCombinedScore"]) for row in rows]),
        "singleHypothesisCount": sum(bool(row["singleHypothesis"]) for row in rows),
        "singleHypothesisRate": (
            sum(bool(row["singleHypothesis"]) for row in rows) / len(rows) if rows else None
        ),
        "primarySustainEvidenceCount": sum(bool(row["primarySustainEvidence"]) for row in rows),
        "primarySustainEvidenceRate": (
            sum(bool(row["primarySustainEvidence"]) for row in rows) / len(rows) if rows else None
        ),
        "selectedLowerPitchThanPrimaryCount": sum(bool(row["selectedLowerPitchThanPrimary"]) for row in rows),
        "selectedLowerPitchThanPrimaryRate": (
            sum(bool(row["selectedLowerPitchThanPrimary"]) for row in rows) / len(rows) if rows else None
        ),
    }


def _run_summary(rows: list[dict[str, Any]], flag: str) -> dict[str, Any]:
    run_lengths: list[int] = []
    current = 0
    for row in rows:
        if bool(row[flag]):
            current += 1
        elif current:
            run_lengths.append(current)
            current = 0
    if current:
        run_lengths.append(current)
    return {
        "runCount": len(run_lengths),
        "runLength": _summary([float(value) for value in run_lengths]),
        "runsLengthAtLeast2": sum(value >= 2 for value in run_lengths),
        "runsLengthAtLeast4": sum(value >= 4 for value in run_lengths),
        "maxRunLength": max(run_lengths) if run_lengths else 0,
    }


def _sequential_repeat_summary(rows: list[dict[str, Any]], tempo: float) -> dict[str, Any]:
    step_seconds = 60.0 / tempo / 4.0
    e64_pairs = 0
    e64_short_pairs = 0
    e64_previous_sustain_short = 0
    e64_previous_sustain_weak_front_short = 0
    e64_gaps_steps: list[float] = []
    for previous, current in zip(rows, rows[1:]):
        if not (bool(previous["openHighE64"]) and bool(current["openHighE64"])):
            continue
        e64_pairs += 1
        gap_steps = (float(current["timeSeconds"]) - float(previous["timeSeconds"])) / step_seconds
        e64_gaps_steps.append(gap_steps)
        if 0.0 < gap_steps <= 2.35:
            e64_short_pairs += 1
            if bool(previous["primarySustainEvidence"]):
                e64_previous_sustain_short += 1
                if float(current["attackMinusBody"]) < 0.0:
                    e64_previous_sustain_weak_front_short += 1
    return {
        "sixteenthStepSecondsFromMetadata": step_seconds,
        "consecutiveSelectedAttackPairsBothOpenHighE64": e64_pairs,
        "timeGapSixteenthSteps": _summary(e64_gaps_steps),
        "shortGapAtMost235StepsCount": e64_short_pairs,
        "shortGapPreviousHasSustainEvidenceCount": e64_previous_sustain_short,
        "shortGapPreviousSustainAndCurrentAttackBelowBodyCount": e64_previous_sustain_weak_front_short,
    }


def _window_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for start in range(1, 113, 8):
        end = start + 7
        scoped = [row for row in rows if start <= int(row["measure"]) <= end]
        e64 = sum(bool(row["openHighE64"]) for row in scoped)
        any_open = sum(bool(row["primaryHasOpenStringMapping"]) for row in scoped)
        result.append({
            "startMeasure": start,
            "endMeasure": end,
            "attackCount": len(scoped),
            "openHighE64Count": e64,
            "openHighE64Rate": e64 / len(scoped) if scoped else None,
            "anyOpenStringPrimaryCount": any_open,
            "anyOpenStringPrimaryRate": any_open / len(scoped) if scoped else None,
        })
    return result


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows, tempo = _load_rows(evidence)
    total = len(rows)
    open_high_e = [row for row in rows if bool(row["openHighE64"])]
    other_open = [
        row for row in rows
        if bool(row["primaryHasOpenStringMapping"]) and not bool(row["openHighE64"])
    ]
    fretted = [row for row in rows if not bool(row["primaryHasOpenStringMapping"])]
    any_open = [row for row in rows if bool(row["primaryHasOpenStringMapping"])]
    single_hypothesis = [row for row in rows if bool(row["singleHypothesis"])]

    string_fret_counts = collections.Counter(
        f"{int(row['canonicalPrimaryString'])}:{int(row['canonicalPrimaryFret'])}" for row in rows
    )
    open_string_midi_counts = collections.Counter(
        int(row["primary"]) for row in any_open
    )
    open_string_string_counts = collections.Counter(
        int(row["canonicalPrimaryString"]) for row in any_open
    )

    e64_summary = _group_summary(open_high_e, total)
    fretted_summary = _group_summary(fretted, total)
    other_open_summary = _group_summary(other_open, total)

    def _median(group: dict[str, Any], metric: str) -> float:
        value = group[metric]["median"]
        return float(value) if value is not None else 0.0

    e64_single = float(e64_summary["singleHypothesisRate"] or 0.0)
    fretted_single = float(fretted_summary["singleHypothesisRate"] or 0.0)
    e64_sustain = float(e64_summary["primarySustainEvidenceRate"] or 0.0)
    fretted_sustain = float(fretted_summary["primarySustainEvidenceRate"] or 0.0)
    physical_flags = {
        "openHighEIsAtLeast20PercentOfAllAttacks": len(open_high_e) / total >= 0.20,
        "openHighESingleHypothesisRateAtLeast10PointsAboveFretted": e64_single - fretted_single >= 0.10,
        "openHighEMedianAttackMinusBodyBelowFretted": (
            _median(e64_summary, "attackMinusBody") < _median(fretted_summary, "attackMinusBody")
        ),
        "openHighEMedianPersistenceAboveFretted": (
            _median(e64_summary, "primaryPersistenceSupport") > _median(fretted_summary, "primaryPersistenceSupport")
        ),
        "openHighESustainRateAtLeast10PointsAboveFretted": e64_sustain - fretted_sustain >= 0.10,
    }
    physical_bias_count = sum(
        bool(physical_flags[key])
        for key in (
            "openHighEMedianAttackMinusBodyBelowFretted",
            "openHighEMedianPersistenceAboveFretted",
            "openHighESustainRateAtLeast10PointsAboveFretted",
        )
    )
    if (
        physical_flags["openHighEIsAtLeast20PercentOfAllAttacks"]
        and physical_flags["openHighESingleHypothesisRateAtLeast10PointsAboveFretted"]
        and physical_bias_count >= 2
    ):
        classification = "open-high-e-persistence-bias-clue"
    elif physical_flags["openHighEIsAtLeast20PercentOfAllAttacks"]:
        classification = "open-high-e-register-concentration-without-sufficient-persistence-proof"
    else:
        classification = "no-large-open-high-e-concentration"

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-open-string-bias-diagnostic",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "sourceRetiredEventSha256": RETIRED_EVENT_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "modalUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "attackCount": total,
        "tempoBpm": tempo,
        "groups": {
            "openHighE64": e64_summary,
            "otherOpenStringPrimary": other_open_summary,
            "frettedPrimary": fretted_summary,
            "anyOpenStringPrimary": _group_summary(any_open, total),
            "singleHypothesisAllPitches": _group_summary(single_hypothesis, total),
        },
        "primaryMappingConcentration": {
            "canonicalPrimaryStringFretCounts": _counter(string_fret_counts),
            "openStringPrimaryMidiCounts": _counter(open_string_midi_counts),
            "openStringPrimaryStringCounts": _counter(open_string_string_counts),
            "anyOpenStringPrimaryCount": len(any_open),
            "anyOpenStringPrimaryRate": len(any_open) / total,
            "openHighE64Count": len(open_high_e),
            "openHighE64Rate": len(open_high_e) / total,
            "openHighE64AmongSingleHypothesisCount": sum(
                bool(row["openHighE64"]) for row in single_hypothesis
            ),
            "openHighE64AmongSingleHypothesisRate": (
                sum(bool(row["openHighE64"]) for row in single_hypothesis) / len(single_hypothesis)
                if single_hypothesis else None
            ),
        },
        "openHighESequentialBehavior": {
            "runs": _run_summary(rows, "openHighE64"),
            "consecutivePairPhysics": _sequential_repeat_summary(rows, tempo),
        },
        "eightMeasureDistribution": _window_summary(rows),
        "physicalBiasFlags": physical_flags,
        "diagnosticClassification": classification,
        "interpretationBoundary": (
            "concentration and persistence statistics are diagnostic only; an open-string primary may be musically correct. "
            "No primary, hypothesis, attack, or voicing is changed by this report."
        ),
        "invariants": {
            "all725AttacksRead": total == ATTACK_COUNT,
            "standardTuningMappingsValidated": True,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
        },
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    compact = {
        "classification": report["diagnosticClassification"],
        "mappingConcentration": report["primaryMappingConcentration"],
        "openHighE64": report["groups"]["openHighE64"],
        "frettedPrimary": report["groups"]["frettedPrimary"],
        "physicalBiasFlags": report["physicalBiasFlags"],
        "sequentialBehavior": report["openHighESequentialBehavior"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_open_string_bias_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
