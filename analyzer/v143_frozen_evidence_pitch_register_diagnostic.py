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
GUITAR_LOW = 40
GUITAR_HIGH = 88
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}


def _quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ordered[lo]
    w = pos - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


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


def _hypotheses(attack: list[Any]) -> dict[int, list[Any]]:
    return {int(item[0]): item for item in attack[4]}


def _notes(attack: list[Any]) -> list[dict[str, Any]]:
    result = []
    for note in attack[5]:
        midi = int(note[1])
        string = int(note[2])
        fret = int(note[3])
        if string not in STANDARD_TUNING:
            raise RuntimeError(f"invalid string index {string}")
        if STANDARD_TUNING[string] + fret != midi:
            raise RuntimeError(f"string/fret mapping mismatch midi={midi} string={string} fret={fret}")
        result.append({
            "id": int(note[0]),
            "midi": midi,
            "string": string,
            "fret": fret,
            "sustain": bool(note[4]),
        })
    return result


def _counter(counter: collections.Counter[int]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items())}


def _octave_options(midi: int) -> list[int]:
    result = []
    for candidate in range(GUITAR_LOW, GUITAR_HIGH + 1):
        if candidate % 12 == midi % 12:
            result.append(candidate)
    return result


def _load_rows(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("approved frozen source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen source identity changed")
    if provenance.get("referenceFree") is not True:
        raise RuntimeError("frozen evidence is not reference-free")
    if provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("professional reference provenance is unsafe")
    if provenance.get("referenceRuntimeInputUsed") is not False or provenance.get("preScorer") is not True:
        raise RuntimeError("evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    if len(attacks) != ATTACK_COUNT:
        raise RuntimeError("frozen attack cardinality changed")

    rows = []
    for index, attack in enumerate(attacks):
        primary = int(attack[3])
        hypotheses = _hypotheses(attack)
        notes = _notes(attack)
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        primary_notes = [note for note in notes if int(note["midi"]) == primary]
        if not primary_notes:
            raise RuntimeError(f"primary missing from selected notes at attack {index}")
        ranked = sorted(hypotheses.items(), key=lambda item: (float(item[1][4]), -int(item[0])), reverse=True)
        best_midi, best_hyp = ranked[0]
        primary_score = float(hypotheses[primary][4])
        best_score = float(best_hyp[4])
        rows.append({
            "index": index,
            "measure": int(attack[0]),
            "step": int(attack[1]),
            "timeSeconds": float(attack[2]),
            "primary": primary,
            "primaryPitchClass": primary % 12,
            "primaryScore": primary_score,
            "primaryRank": 1 + [int(midi) for midi, _ in ranked].index(primary),
            "bestHypothesis": int(best_midi),
            "bestHypothesisScore": best_score,
            "bestMinusPrimaryInterval": int(best_midi) - primary,
            "bestScoreMarginVsPrimary": best_score - primary_score,
            "hypothesisCount": len(hypotheses),
            "hypothesisMidis": sorted(hypotheses),
            "notes": notes,
            "selectedMidis": sorted({int(note["midi"]) for note in notes}),
            "primaryStrings": sorted({int(note["string"]) for note in primary_notes}),
            "primaryFrets": sorted({int(note["fret"]) for note in primary_notes}),
        })
    rows.sort(key=lambda row: float(row["timeSeconds"]))
    return rows


def _context_octave_support(rows: list[dict[str, Any]], radius: int = 4) -> dict[str, Any]:
    high_with_lower_neighbor = 0
    low_with_upper_neighbor = 0
    high_count = 0
    low_count = 0
    examples = []
    for i, row in enumerate(rows):
        primary = int(row["primary"])
        neighbors = rows[max(0, i - radius):i] + rows[i + 1:min(len(rows), i + radius + 1)]
        neighbor_primaries = {int(other["primary"]) for other in neighbors}
        if primary - 12 >= GUITAR_LOW:
            high_count += 1
            if primary - 12 in neighbor_primaries:
                high_with_lower_neighbor += 1
                if len(examples) < 40:
                    examples.append({
                        "measure": int(row["measure"]),
                        "step": int(row["step"]),
                        "primary": primary,
                        "contextLowerOctave": primary - 12,
                    })
        if primary + 12 <= GUITAR_HIGH:
            low_count += 1
            if primary + 12 in neighbor_primaries:
                low_with_upper_neighbor += 1
    return {
        "neighborRadiusAttacks": radius,
        "primaryHasLegalLowerOctaveCount": high_count,
        "legalLowerOctaveAppearsAsNeighborPrimaryCount": high_with_lower_neighbor,
        "lowerOctaveNeighborRate": high_with_lower_neighbor / high_count if high_count else None,
        "primaryHasLegalUpperOctaveCount": low_count,
        "legalUpperOctaveAppearsAsNeighborPrimaryCount": low_with_upper_neighbor,
        "upperOctaveNeighborRate": low_with_upper_neighbor / low_count if low_count else None,
        "examplesLowerOctaveNeighbor": examples,
    }


def _continuity_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_diffs = []
    same_pc_octave_jumps = []
    large_jump_foldable = 0
    fold_reductions = []
    prior = None
    for row in rows:
        current = int(row["primary"])
        if prior is not None:
            diff = current - prior
            raw_diffs.append(abs(diff))
            if current % 12 == prior % 12 and abs(diff) >= 12:
                same_pc_octave_jumps.append(abs(diff))
            best_option = min(_octave_options(current), key=lambda candidate: (abs(candidate - prior), abs(candidate - current)))
            raw_abs = abs(current - prior)
            folded_abs = abs(best_option - prior)
            if raw_abs >= 12 and folded_abs <= 7 and folded_abs < raw_abs:
                large_jump_foldable += 1
                fold_reductions.append(raw_abs - folded_abs)
        prior = current
    return {
        "adjacentPairCount": len(raw_diffs),
        "absolutePrimarySemitoneJump": _summary([float(v) for v in raw_diffs]),
        "jumpAtLeast12Count": sum(v >= 12 for v in raw_diffs),
        "jumpAtLeast19Count": sum(v >= 19 for v in raw_diffs),
        "samePitchClassOctaveJumpCount": len(same_pc_octave_jumps),
        "samePitchClassOctaveJumpSize": _summary([float(v) for v in same_pc_octave_jumps]),
        "largeJumpCouldBecomeSevenSemitonesOrLessByOctaveEquivalentFoldCount": large_jump_foldable,
        "potentialFoldReductionSemitones": _summary([float(v) for v in fold_reductions]),
        "interpretationBoundary": "octave-equivalent folding is diagnostic only and is not a proposed pitch correction",
    }


def _voicing_diagnostic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = collections.Counter()
    note_counts = []
    spans = []
    fret_spans = []
    primary_above_lowest_intervals = []
    primary_not_lowest = 0
    disconnected_strings = 0
    wide_fret_span = 0
    exact_octave_pairs = 0
    harmonic_family_pairs = 0
    non_harmonic_multinote = 0
    for row in rows:
        notes = list(row["notes"])
        note_counts.append(len(notes))
        midis = sorted({int(note["midi"]) for note in notes})
        strings = sorted({int(note["string"]) for note in notes})
        frets = [int(note["fret"]) for note in notes]
        if midis:
            span = max(midis) - min(midis)
            spans.append(span)
            primary_delta = int(row["primary"]) - min(midis)
            primary_above_lowest_intervals.append(primary_delta)
            if primary_delta > 0:
                primary_not_lowest += 1
        if frets:
            fret_span = max(frets) - min(frets)
            fret_spans.append(fret_span)
            if fret_span >= 6:
                wide_fret_span += 1
        if strings and max(strings) - min(strings) + 1 != len(strings):
            disconnected_strings += 1
        if len(midis) > 1:
            intervals = {abs(b - a) for i, a in enumerate(midis) for b in midis[i + 1:]}
            if 12 in intervals:
                exact_octave_pairs += 1
            if intervals & HARMONIC_INTERVALS:
                harmonic_family_pairs += 1
            if not intervals & HARMONIC_INTERVALS:
                non_harmonic_multinote += 1
        counts[len(notes)] += 1
    return {
        "selectedNoteCountPerAttack": _counter(counts),
        "selectedNoteCountSummary": _summary([float(v) for v in note_counts]),
        "selectedPitchSpanSemitones": _summary([float(v) for v in spans]),
        "selectedFretSpan": _summary([float(v) for v in fret_spans]),
        "primaryAboveLowestSelectedInterval": _summary([float(v) for v in primary_above_lowest_intervals]),
        "primaryNotLowestSelectedPitchCount": primary_not_lowest,
        "primaryNotLowestSelectedPitchRate": primary_not_lowest / len(rows),
        "disconnectedSelectedStringSetCount": disconnected_strings,
        "wideSelectedFretSpanAtLeast6Count": wide_fret_span,
        "multiNoteAttackWithExactOctavePairCount": exact_octave_pairs,
        "multiNoteAttackWithAnyHarmonicFamilyPairCount": harmonic_family_pairs,
        "multiNoteAttackWithoutHarmonicFamilyPairCount": non_harmonic_multinote,
    }


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows = _load_rows(evidence)
    primary_midis = [int(row["primary"]) for row in rows]
    primary_strings = [int(row["primaryStrings"][0]) for row in rows]
    primary_frets = [int(row["primaryFrets"][0]) for row in rows]
    hypothesis_counts = [int(row["hypothesisCount"]) for row in rows]
    rank_counter = collections.Counter(int(row["primaryRank"]) for row in rows)
    interval_counter = collections.Counter(int(row["bestMinusPrimaryInterval"]) for row in rows)
    best_diff = [row for row in rows if int(row["bestHypothesis"]) != int(row["primary"])]
    harmonic_best_diff = [row for row in best_diff if int(row["bestMinusPrimaryInterval"]) in HARMONIC_INTERVALS]
    nonharmonic_best_diff = [row for row in best_diff if int(row["bestMinusPrimaryInterval"]) not in HARMONIC_INTERVALS]
    lower_hypothesis_attacks = [row for row in rows if any(int(midi) < int(row["primary"]) for midi in row["hypothesisMidis"])]
    exact_lower_octave_hypothesis = [row for row in rows if int(row["primary"]) - 12 in row["hypothesisMidis"]]
    exact_upper_octave_hypothesis = [row for row in rows if int(row["primary"]) + 12 in row["hypothesisMidis"]]

    ambiguous_small_margin = [
        row for row in best_diff
        if 0.0 < float(row["bestScoreMarginVsPrimary"]) <= 0.25
    ]
    ambiguous_nonharmonic = [
        row for row in nonharmonic_best_diff
        if float(row["bestScoreMarginVsPrimary"]) <= 0.5
    ]

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-pitch-register-diagnostic",
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
        "attackCount": len(rows),
        "primaryRegister": {
            "midi": _summary([float(v) for v in primary_midis]),
            "pitchClassCounts": _counter(collections.Counter(v % 12 for v in primary_midis)),
            "midiCounts": _counter(collections.Counter(primary_midis)),
            "primaryStringCounts": _counter(collections.Counter(primary_strings)),
            "primaryFret": _summary([float(v) for v in primary_frets]),
            "primaryAtOrAboveMidi64Count": sum(v >= 64 for v in primary_midis),
            "primaryAtOrAboveMidi67Count": sum(v >= 67 for v in primary_midis),
            "primaryBelowMidi52Count": sum(v < 52 for v in primary_midis),
        },
        "hypothesisSelection": {
            "hypothesisCountPerAttack": _summary([float(v) for v in hypothesis_counts]),
            "singleHypothesisAttackCount": sum(v == 1 for v in hypothesis_counts),
            "primaryRankCounts": _counter(rank_counter),
            "bestHypothesisDiffersFromPrimaryCount": len(best_diff),
            "bestHypothesisDiffersFromPrimaryRate": len(best_diff) / len(rows),
            "bestMinusPrimaryIntervalCounts": _counter(interval_counter),
            "bestDiffIsUpperHarmonicFamilyCount": len(harmonic_best_diff),
            "bestDiffIsNonHarmonicFamilyCount": len(nonharmonic_best_diff),
            "bestScoreMarginVsPrimaryWhenDifferent": _summary([float(row["bestScoreMarginVsPrimary"]) for row in best_diff]),
            "differentBestWithMarginAtMost025Count": len(ambiguous_small_margin),
            "nonHarmonicDifferentBestWithMarginAtMost05Count": len(ambiguous_nonharmonic),
            "anyLowerHypothesisThanPrimaryAttackCount": len(lower_hypothesis_attacks),
            "exactLowerOctaveHypothesisAttackCount": len(exact_lower_octave_hypothesis),
            "exactUpperOctaveHypothesisAttackCount": len(exact_upper_octave_hypothesis),
        },
        "contextOctaveSupport": _context_octave_support(rows),
        "primaryContinuity": _continuity_diagnostic(rows),
        "selectedVoicingPhysics": _voicing_diagnostic(rows),
        "rankedNonHarmonicBestAlternatives": [
            {
                "measure": int(row["measure"]),
                "step": int(row["step"]),
                "primary": int(row["primary"]),
                "bestHypothesis": int(row["bestHypothesis"]),
                "interval": int(row["bestMinusPrimaryInterval"]),
                "scoreMargin": float(row["bestScoreMarginVsPrimary"]),
                "selectedMidis": list(row["selectedMidis"]),
            }
            for row in sorted(nonharmonic_best_diff, key=lambda item: float(item["bestScoreMarginVsPrimary"]), reverse=True)[:80]
        ],
        "invariants": {
            "all725AttacksRead": len(rows) == ATTACK_COUNT,
            "standardTuningMappingsValidated": True,
            "eventsMutated": False,
            "attackGridMutated": False,
            "pitchSelectionMutated": False,
            "referenceConsulted": False,
        },
        "interpretationBoundary": "all octave folding, continuity and voicing tests are diagnostics only; no pitch is changed or selected by this report",
    }


def main(source: str, destination: str) -> None:
    evidence = json.loads(Path(source).read_text(encoding="utf-8"))
    report = diagnose(evidence)
    output = Path(destination)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    compact = {
        "primaryRegister": report["primaryRegister"],
        "hypothesisSelection": report["hypothesisSelection"],
        "contextOctaveSupport": {k: v for k, v in report["contextOctaveSupport"].items() if not k.startswith("examples")},
        "primaryContinuity": report["primaryContinuity"],
        "selectedVoicingPhysics": report["selectedVoicingPhysics"],
    }
    print(json.dumps(compact, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_pitch_register_diagnostic.py EVIDENCE OUTPUT")
    main(sys.argv[1], sys.argv[2])
