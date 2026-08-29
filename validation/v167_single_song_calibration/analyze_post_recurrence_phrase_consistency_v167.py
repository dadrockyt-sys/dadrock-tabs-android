#!/usr/bin/env python3
"""Reference-blind phrase/metrical consistency diagnosis after terminal recurrence sweep.

This is a distinct post-recurrence structural analysis. It does NOT extend or retune
the closed same-MIDI burst-collapse family. Inputs are limited to immutable generated
candidates and frozen aggregate whole-rule reports. The professional reference and
scorer are not accepted. No per-event reference match assignments are read.

The analysis asks whether the exact 48 frozen I005 additions recur at consistent
metrical positions or within repeated immutable-I003 local riff contexts. It reports
structure only and selects no new rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

EXPECTED = {
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "recurrenceReportSha256": "800e9dbcd8565b32d2015ba6cc97a142c91dbf1c3b76f39f96818b3f4c735382",
    "temporalDiagnosisSha256": "fd5c12339e594ae1207e2c4edb2eb034a9249de15ab99d3623cf5f6922061b36",
    "i003GuitarCount": 1050,
    "i005GuitarCount": 1098,
    "additionCount": 48,
}

STEPS_PER_MEASURE = 16
LOCAL_RADIUS = 4


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def coord(row: Mapping[str, Any]) -> tuple[int, int]:
    return int(row["absoluteGridStep"]), int(row["midi"])


def step_in_measure(row: Mapping[str, Any]) -> int:
    absolute = int(row["absoluteGridStep"])
    measure = int(row["measure"])
    step = int(round(float(row["step"])))
    if (measure - 1) * STEPS_PER_MEASURE + step != absolute:
        raise RuntimeError("measure/step/absolute invariant drift")
    return step


def counter_dict(counter: Counter[Any]) -> dict[str, int]:
    return {str(k): int(v) for k, v in sorted(counter.items(), key=lambda item: str(item[0]))}


def multiplicity_histogram(values: Iterable[int]) -> dict[str, int]:
    return counter_dict(Counter(int(x) for x in values))


def local_signature(
    base_by_step: Mapping[int, list[int]],
    center_step: int,
    center_midi: int,
    *,
    relative_pitch: bool,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    signature: list[tuple[int, tuple[int, ...]]] = []
    for offset in range(-LOCAL_RADIUS, LOCAL_RADIUS + 1):
        pitches = sorted(int(p) for p in base_by_step.get(center_step + offset, []))
        if relative_pitch:
            values = tuple(int(p - center_midi) for p in pitches)
        else:
            values = tuple(pitches)
        signature.append((offset, values))
    return tuple(signature)


def sig_key(signature: tuple[tuple[int, tuple[int, ...]], ...]) -> str:
    return json.dumps(signature, separators=(",", ":"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--i003", type=Path, required=True)
    ap.add_argument("--i005", type=Path, required=True)
    ap.add_argument("--recurrence-report", type=Path, required=True)
    ap.add_argument("--temporal-diagnosis", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"post-recurrence analysis output already exists: {args.output}")
    for path, expected in (
        (args.i003, EXPECTED["i003Sha256"]),
        (args.i005, EXPECTED["i005Sha256"]),
        (args.recurrence_report, EXPECTED["recurrenceReportSha256"]),
        (args.temporal_diagnosis, EXPECTED["temporalDiagnosisSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen post-recurrence input SHA mismatch: {path}: {actual}")

    i003 = json.loads(args.i003.read_text(encoding="utf-8"))
    i005 = json.loads(args.i005.read_text(encoding="utf-8"))
    recurrence = json.loads(args.recurrence_report.read_text(encoding="utf-8"))
    temporal = json.loads(args.temporal_diagnosis.read_text(encoding="utf-8"))

    if int((i003.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("phrase consistency base must be I003")
    if int((i005.get("calibration") or {}).get("iteration", -1)) != 5:
        raise RuntimeError("phrase consistency source must be I005")
    if recurrence.get("status") != "REFERENCE_GRADED_COMPLETE_PREDECLARED_TEMPORAL_RECURRENCE_VARIANTS":
        raise RuntimeError("recurrence report is not terminal expected schema/status")
    if recurrence.get("newVariantsBeatingI005") != 1:
        raise RuntimeError("unexpected recurrence aggregate result")
    if recurrence.get("newVariantsMeetingPromotionEligibility") != 0:
        raise RuntimeError("unexpected recurrence promotion eligibility")
    winner = recurrence.get("winnerIncludingI005Baseline") or {}
    if winner.get("id") != "recur-gap1-earliest":
        raise RuntimeError("unexpected terminal recurrence winner")
    if winner.get("eligibleForSeparateNoRescoreIteration006Promotion") is not False:
        raise RuntimeError("unexpected recurrence promotion eligibility flag")
    if temporal.get("schema") != "dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1":
        raise RuntimeError("unexpected frozen temporal diagnosis schema")
    tpolicy = temporal.get("policy") or {}
    if tpolicy.get("professionalReferenceReadByAnalysis") is not False or tpolicy.get("scorerReadByAnalysis") is not False:
        raise RuntimeError("temporal diagnosis reference/scorer boundary invalid")

    i003_guitar = list((i003.get("streams") or {}).get("combinedGuitar") or [])
    i005_guitar = list((i005.get("streams") or {}).get("combinedGuitar") or [])
    if len(i003_guitar) != EXPECTED["i003GuitarCount"]:
        raise RuntimeError("I003 Guitar count drift")
    if len(i005_guitar) != EXPECTED["i005GuitarCount"]:
        raise RuntimeError("I005 Guitar count drift")

    base_coords = {coord(row) for row in i003_guitar}
    additions = [dict(row) for row in i005_guitar if coord(row) not in base_coords]
    if len(additions) != EXPECTED["additionCount"]:
        raise RuntimeError(f"I005 addition count drift: {len(additions)}")
    additions.sort(key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"])))

    base_by_step: dict[int, list[int]] = defaultdict(list)
    base_same_midi_phase: Counter[tuple[int, int]] = Counter()
    base_phase: Counter[int] = Counter()
    for row in i003_guitar:
        absolute = int(row["absoluteGridStep"])
        midi = int(row["midi"])
        phase = step_in_measure(row)
        base_by_step[absolute].append(midi)
        base_same_midi_phase[(midi, phase)] += 1
        base_phase[phase] += 1

    addition_phase: Counter[int] = Counter()
    addition_midi_phase: Counter[tuple[int, int]] = Counter()
    for row in additions:
        phase = step_in_measure(row)
        addition_phase[phase] += 1
        addition_midi_phase[(int(row["midi"]), phase)] += 1

    absolute_sig_counts: Counter[str] = Counter()
    relative_sig_counts: Counter[str] = Counter()
    absolute_sigs: dict[tuple[int, int], str] = {}
    relative_sigs: dict[tuple[int, int], str] = {}
    for row in additions:
        step = int(row["absoluteGridStep"])
        midi = int(row["midi"])
        akey = sig_key(local_signature(base_by_step, step, midi, relative_pitch=False))
        rkey = sig_key(local_signature(base_by_step, step, midi, relative_pitch=True))
        absolute_sigs[(step, midi)] = akey
        relative_sigs[(step, midi)] = rkey
        absolute_sig_counts[akey] += 1
        relative_sig_counts[rkey] += 1

    selected_rows: list[dict[str, Any]] = []
    for row in additions:
        step = int(row["absoluteGridStep"])
        midi = int(row["midi"])
        phase = step_in_measure(row)
        wrapper = row.get("v167RecoverySweepEvidence") or {}
        evidence = wrapper.get("evidence") or {}
        if (wrapper.get("rule") or {}).get("id") != "gss-active-only":
            raise RuntimeError("unexpected I005 addition provenance")
        selected_rows.append({
            "absoluteGridStep": step,
            "measure": int(row["measure"]),
            "stepWithinMeasure": phase,
            "midi": midi,
            "onsetSupport": float(evidence.get("onsetSupport", 0.0)),
            "activitySupport": float(evidence.get("activitySupport", 0.0)),
            "baseSameMidiSamePhaseOccurrences": int(base_same_midi_phase[(midi, phase)]),
            "baseAnyMidiSamePhaseEvents": int(base_phase[phase]),
            "additionSameMidiSamePhaseMultiplicity": int(addition_midi_phase[(midi, phase)]),
            "additionSamePhaseMultiplicity": int(addition_phase[phase]),
            "exactLocalBaseContextMultiplicityAmongAdditions": int(absolute_sig_counts[absolute_sigs[(step, midi)]]),
            "relativeLocalBaseContextMultiplicityAmongAdditions": int(relative_sig_counts[relative_sigs[(step, midi)]]),
        })

    repeated_exact_groups = [
        {"multiplicity": count, "signature": key}
        for key, count in absolute_sig_counts.items()
        if count >= 2
    ]
    repeated_relative_groups = [
        {"multiplicity": count, "signature": key}
        for key, count in relative_sig_counts.items()
        if count >= 2
    ]
    repeated_exact_groups.sort(key=lambda x: (-int(x["multiplicity"]), str(x["signature"])))
    repeated_relative_groups.sort(key=lambda x: (-int(x["multiplicity"]), str(x["signature"])))

    report = {
        "schema": "dadrock.tabs.v167.post-recurrence-phrase-consistency-analysis.v1",
        "version": "V167",
        "status": "POST_RECURRENCE_PHRASE_CONSISTENCY_REFERENCE_BLIND_ANALYSIS_FROZEN",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.i003),
            "iteration005Sha256": sha256_file(args.i005),
            "terminalRecurrenceReportSha256": sha256_file(args.recurrence_report),
            "temporalDiagnosisSha256": sha256_file(args.temporal_diagnosis),
        },
        "aggregateOutcomeRead": {
            "winnerId": str(winner["id"]),
            "winnerF1PercentagePointsVsI005": float((winner.get("deltaVsI005") or {})["f1PercentagePoints"]),
            "winnerPrecisionPercentagePointsVsI005": float((winner.get("deltaVsI005") or {})["precisionPercentagePoints"]),
            "winnerRecallPercentagePointsVsI005": float((winner.get("deltaVsI005") or {})["recallPercentagePoints"]),
            "winnerMatchedDeltaVsI005": int((winner.get("deltaVsI005") or {})["matched"]),
            "winnerFalsePositiveDeltaVsI005": int((winner.get("deltaVsI005") or {})["falsePositive"]),
            "promotionEligible": False,
            "interpretationBoundary": "aggregate whole-rule outcome only; no individual pruned/kept event is labeled correct or incorrect",
        },
        "metricalStructure": {
            "additionStepWithinMeasureHistogram": counter_dict(addition_phase),
            "additionMidiStepWithinMeasureMultiplicityHistogram": multiplicity_histogram(addition_midi_phase.values()),
            "baseSameMidiSamePhaseOccurrenceHistogramAcrossAdditions": multiplicity_histogram(
                base_same_midi_phase[(int(row["midi"]), step_in_measure(row))] for row in additions
            ),
            "additionsWithAtLeastOneImmutableBaseSameMidiSamePhaseOccurrence": sum(
                base_same_midi_phase[(int(row["midi"]), step_in_measure(row))] >= 1 for row in additions
            ),
            "additionsWithAtLeastTwoImmutableBaseSameMidiSamePhaseOccurrences": sum(
                base_same_midi_phase[(int(row["midi"]), step_in_measure(row))] >= 2 for row in additions
            ),
        },
        "phraseContextStructure": {
            "localRadiusGridSteps": LOCAL_RADIUS,
            "exactImmutableBaseContextMultiplicityHistogram": multiplicity_histogram(absolute_sig_counts.values()),
            "relativePitchImmutableBaseContextMultiplicityHistogram": multiplicity_histogram(relative_sig_counts.values()),
            "additionsInRepeatedExactContextGroups": sum(count for count in absolute_sig_counts.values() if count >= 2),
            "additionsInRepeatedRelativeContextGroups": sum(count for count in relative_sig_counts.values() if count >= 2),
            "repeatedExactContextGroupCount": sum(count >= 2 for count in absolute_sig_counts.values()),
            "repeatedRelativeContextGroupCount": sum(count >= 2 for count in relative_sig_counts.values()),
            "largestExactContextGroup": max(absolute_sig_counts.values(), default=0),
            "largestRelativeContextGroup": max(relative_sig_counts.values(), default=0),
            "repeatedExactContextGroups": repeated_exact_groups,
            "repeatedRelativeContextGroups": repeated_relative_groups,
        },
        "selectedRowsReferenceBlind": selected_rows,
        "diagnosticInterpretation": {
            "closedFamily": "same-MIDI gap1/gap2 burst collapse is terminal; no recurrence retuning is permitted",
            "question": "Does a genuinely distinct metrical/phrase-repetition structure exist among the 48 I005 additions that could justify later preregistration without using per-event reference outcomes?",
            "ruleSelection": "none; report structure only",
        },
        "policy": {
            "professionalReferenceReadByAnalysis": False,
            "scorerReadByAnalysis": False,
            "newReferenceFacingScoreCalls": 0,
            "perEventReferenceMatchAssignmentsRead": False,
            "individualEventCorrectnessInferred": False,
            "closedRecurrenceFamilyRetuned": False,
            "newRuleSelectedByThisAnalysis": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
            "generalizationClaim": False,
            "terminalAggregateRecurrenceScoresRead": True,
        },
    }
    write_json(args.output, report)
    print(json.dumps({
        "additionCount": len(additions),
        "sameMidiSamePhaseBaseSupport": report["metricalStructure"]["additionsWithAtLeastOneImmutableBaseSameMidiSamePhaseOccurrence"],
        "repeatedExactContextAdditions": report["phraseContextStructure"]["additionsInRepeatedExactContextGroups"],
        "repeatedRelativeContextAdditions": report["phraseContextStructure"]["additionsInRepeatedRelativeContextGroups"],
        "largestRelativeContextGroup": report["phraseContextStructure"]["largestRelativeContextGroup"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
