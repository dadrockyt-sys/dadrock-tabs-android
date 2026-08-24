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
OPEN_MIDIS = set(STANDARD_TUNING.values())


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
        "q25": _quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "mean": statistics.mean(values) if values else None,
        "q75": _quantile(values, 0.75),
        "max": max(values) if values else None,
    }


def _counter(counter: collections.Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda x: x[0])}


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
    if provenance.get("referenceRuntimeInputUsed") is not False:
        raise RuntimeError("reference entered runtime evidence")
    if provenance.get("preScorer") is not True:
        raise RuntimeError("evidence is not sealed pre-scorer evidence")

    attacks = list(evidence.get("attacks") or [])
    if len(attacks) != ATTACK_COUNT:
        raise RuntimeError(f"frozen attack cardinality changed: {len(attacks)}")

    rows: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for index, attack in enumerate(attacks):
        measure = int(attack[0])
        step = int(attack[1])
        primary = int(attack[3])
        key = (measure, step)
        if key in seen:
            raise RuntimeError(f"duplicate frozen attack coordinate {key}")
        seen.add(key)

        hypotheses = {int(item[0]): item for item in attack[4]}
        if primary not in hypotheses:
            raise RuntimeError(f"primary missing from hypotheses at attack {index}")
        primary_hyp = hypotheses[primary]
        primary_support = {
            "attack": float(primary_hyp[1]),
            "body": float(primary_hyp[2]),
            "persistence": float(primary_hyp[3]),
            "combined": float(primary_hyp[4]),
        }
        if not all(math.isfinite(value) for value in primary_support.values()):
            raise RuntimeError(f"non-finite primary evidence at attack {index}")

        notes: list[dict[str, Any]] = []
        for note in attack[5]:
            midi = int(note[1])
            string = int(note[2])
            fret = int(note[3])
            if string not in STANDARD_TUNING:
                raise RuntimeError(f"invalid string index {string}")
            if STANDARD_TUNING[string] + fret != midi:
                raise RuntimeError(
                    f"string/fret mapping mismatch midi={midi} string={string} fret={fret}"
                )
            notes.append({"midi": midi, "string": string, "fret": fret, "sustain": bool(note[4])})

        primary_notes = [note for note in notes if int(note["midi"]) == primary]
        if not primary_notes:
            raise RuntimeError(f"primary missing from selected notes at attack {index}")

        primary_mapped_open = any(int(note["fret"]) == 0 for note in primary_notes)
        any_selected_open = any(int(note["fret"]) == 0 for note in notes)
        open_high_e_64 = primary == 64 and any(
            int(note["string"]) == 0 and int(note["fret"]) == 0 for note in primary_notes
        )
        rivals = [item for midi, item in hypotheses.items() if midi != primary]
        best_combined_rival = max(rivals, key=lambda item: float(item[4])) if rivals else None
        best_attack_rival = max(rivals, key=lambda item: float(item[1])) if rivals else None

        rows.append({
            "index": index,
            "measure": measure,
            "step": step,
            "primary": primary,
            "hypothesisCount": len(hypotheses),
            "singleHypothesis": len(hypotheses) == 1,
            "primaryMappedOpen": primary_mapped_open,
            "primaryMidiIsStandardOpenPitch": primary in OPEN_MIDIS,
            "anySelectedOpen": any_selected_open,
            "primaryMidi64": primary == 64,
            "openHighE64": open_high_e_64,
            "primarySupport": primary_support,
            "rivalCount": len(rivals),
            "bestCombinedRival": best_combined_rival,
            "bestAttackRival": best_attack_rival,
        })
    return rows


def _diversity(rows: list[dict[str, Any]], total: int) -> dict[str, Any]:
    single = sum(bool(row["singleHypothesis"]) for row in rows)
    counts = [float(row["hypothesisCount"]) for row in rows]
    return {
        "count": len(rows),
        "rateAllAttacks": len(rows) / total if total else None,
        "singleHypothesisCount": single,
        "singleHypothesisRate": single / len(rows) if rows else None,
        "hypothesisCount": _summary(counts),
        "multiHypothesisCount": len(rows) - single,
    }


def _rival_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    multi = [row for row in rows if row["bestCombinedRival"] is not None]
    combined_margins: list[float] = []
    attack_margins_same_rival: list[float] = []
    body_margins: list[float] = []
    persistence_margins: list[float] = []
    attack_margins_best_attack: list[float] = []
    combined_wins_attack_loses_same = 0
    combined_loses_any = 0
    attack_loses_any = 0
    rival_midi_counts: collections.Counter[int] = collections.Counter()

    for row in multi:
        primary = row["primarySupport"]
        rival = row["bestCombinedRival"]
        attack_rival = row["bestAttackRival"]
        assert rival is not None and attack_rival is not None
        rival_midi_counts[int(rival[0])] += 1
        combined_margin = float(primary["combined"]) - float(rival[4])
        attack_margin_same = float(primary["attack"]) - float(rival[1])
        combined_margins.append(combined_margin)
        attack_margins_same_rival.append(attack_margin_same)
        body_margins.append(float(primary["body"]) - float(rival[2]))
        persistence_margins.append(float(primary["persistence"]) - float(rival[3]))
        attack_best_margin = float(primary["attack"]) - float(attack_rival[1])
        attack_margins_best_attack.append(attack_best_margin)
        if combined_margin >= 0.0 and attack_margin_same < 0.0:
            combined_wins_attack_loses_same += 1
        if combined_margin < 0.0:
            combined_loses_any += 1
        if attack_best_margin < 0.0:
            attack_loses_any += 1

    return {
        "multiHypothesisCount": len(multi),
        "bestCombinedRivalMidiCounts": _counter(rival_midi_counts),
        "primaryMinusBestCombinedRival": {
            "combined": _summary(combined_margins),
            "attack": _summary(attack_margins_same_rival),
            "body": _summary(body_margins),
            "persistence": _summary(persistence_margins),
        },
        "primaryMinusBestAttackRivalAttackSupport": _summary(attack_margins_best_attack),
        "primaryCombinedWinsButAttackLosesToSameRivalCount": combined_wins_attack_loses_same,
        "primaryCombinedWinsButAttackLosesToSameRivalRate": (
            combined_wins_attack_loses_same / len(multi) if multi else None
        ),
        "primaryCombinedLosesToBestCombinedRivalCount": combined_loses_any,
        "primaryAttackLosesToBestAttackRivalCount": attack_loses_any,
    }


def _primary_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in rows:
        grouped[int(row["primary"])].append(row)
    result: list[dict[str, Any]] = []
    for midi, group in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        if len(group) < 10:
            continue
        diversity = _diversity(group, len(rows))
        result.append({
            "primaryMidi": midi,
            "count": len(group),
            "singleHypothesisCount": diversity["singleHypothesisCount"],
            "singleHypothesisRate": diversity["singleHypothesisRate"],
            "hypothesisCountMean": diversity["hypothesisCount"]["mean"],
            "hypothesisCountMedian": diversity["hypothesisCount"]["median"],
            "primaryMappedOpenCount": sum(bool(row["primaryMappedOpen"]) for row in group),
            "anySelectedOpenCount": sum(bool(row["anySelectedOpen"]) for row in group),
        })
    return result


def _windows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for start in range(1, 113, 8):
        end = start + 7
        scoped = [row for row in rows if start <= int(row["measure"]) <= end]
        midi64 = [row for row in scoped if bool(row["primaryMidi64"])]
        result.append({
            "startMeasure": start,
            "endMeasure": end,
            "attackCount": len(scoped),
            "midi64Count": len(midi64),
            "midi64Rate": len(midi64) / len(scoped) if scoped else None,
            "midi64SingleHypothesisCount": sum(bool(row["singleHypothesis"]) for row in midi64),
            "midi64SingleHypothesisRate": (
                sum(bool(row["singleHypothesis"]) for row in midi64) / len(midi64) if midi64 else None
            ),
        })
    return result


def diagnose(evidence: dict[str, Any]) -> dict[str, Any]:
    rows = _load_rows(evidence)
    total = len(rows)
    primary64 = [row for row in rows if bool(row["primaryMidi64"])]
    non64 = [row for row in rows if not bool(row["primaryMidi64"])]
    open_high_e = [row for row in rows if bool(row["openHighE64"])]
    mapped_open = [row for row in rows if bool(row["primaryMappedOpen"])]
    mapped_fretted = [row for row in rows if not bool(row["primaryMappedOpen"])]
    midi_open = [row for row in rows if bool(row["primaryMidiIsStandardOpenPitch"])]
    midi_not_open = [row for row in rows if not bool(row["primaryMidiIsStandardOpenPitch"])]
    any_selected_open = [row for row in rows if bool(row["anySelectedOpen"])]
    no_selected_open = [row for row in rows if not bool(row["anySelectedOpen"])]
    other_mapped_open = [row for row in mapped_open if not bool(row["openHighE64"])]

    d64 = _diversity(primary64, total)
    d_non64 = _diversity(non64, total)
    single_gap = float(d64["singleHypothesisRate"] or 0.0) - float(d_non64["singleHypothesisRate"] or 0.0)
    flags = {
        "midi64AtLeast20PercentOfAttacks": len(primary64) / total >= 0.20,
        "midi64SingleHypothesisRateAtLeast85Percent": float(d64["singleHypothesisRate"] or 0.0) >= 0.85,
        "midi64SingleHypothesisRateAtLeast20PointsAboveNon64": single_gap >= 0.20,
    }
    if all(flags.values()):
        classification = "midi64-candidate-diversity-collapse-clue"
    elif flags["midi64SingleHypothesisRateAtLeast85Percent"]:
        classification = "midi64-low-candidate-diversity-without-unique-collapse-proof"
    else:
        classification = "no-large-midi64-candidate-diversity-collapse"

    definition_counts = {
        "primaryMidi64": len(primary64),
        "primaryMidiNot64": len(non64),
        "openHighE64MappedString0Fret0": len(open_high_e),
        "primaryMappedOpen": len(mapped_open),
        "primaryMappedFretted": len(mapped_fretted),
        "primaryMidiIsStandardOpenPitch": len(midi_open),
        "primaryMidiIsNotStandardOpenPitch": len(midi_not_open),
        "anySelectedVoicingNoteOpen": len(any_selected_open),
        "noSelectedVoicingNoteOpen": len(no_selected_open),
    }

    return {
        "schemaVersion": 1,
        "mode": "v143-frozen-evidence-open-string-candidate-audit",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "sourceRetiredEventSha256": RETIRED_EVENT_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "modalUsed": False,
        "productionModified": False,
        "protectedRuntimeModified": False,
        "candidateRenderProduced": False,
        "eventMutationProposed": False,
        "attackCount": total,
        "definitionAudit": {
            "counts": definition_counts,
            "partitionChecks": {
                "primaryMidi64PlusNot64": len(primary64) + len(non64) == total,
                "primaryMappedOpenPlusFretted": len(mapped_open) + len(mapped_fretted) == total,
                "primaryMidiStandardOpenPlusNot": len(midi_open) + len(midi_not_open) == total,
                "anySelectedOpenPlusNone": len(any_selected_open) + len(no_selected_open) == total,
                "openHighE64SubsetPrimaryMidi64": all(bool(row["primaryMidi64"]) for row in open_high_e),
                "openHighE64SubsetPrimaryMappedOpen": all(bool(row["primaryMappedOpen"]) for row in open_high_e),
            },
        },
        "candidateDiversity": {
            "primaryMidi64": d64,
            "non64": d_non64,
            "openHighE64": _diversity(open_high_e, total),
            "otherPrimaryMappedOpen": _diversity(other_mapped_open, total),
            "primaryMappedFretted": _diversity(mapped_fretted, total),
            "primaryMidiStandardOpenPitch": _diversity(midi_open, total),
            "primaryMidiNotStandardOpenPitch": _diversity(midi_not_open, total),
            "anySelectedVoicingNoteOpen": _diversity(any_selected_open, total),
            "noSelectedVoicingNoteOpen": _diversity(no_selected_open, total),
            "midi64MinusNon64SingleHypothesisRate": single_gap,
        },
        "midi64RivalPhysics": _rival_metrics(primary64),
        "non64RivalPhysics": _rival_metrics(non64),
        "commonPrimaryMidiTableMin10": _primary_table(rows),
        "eightMeasureMidi64Distribution": _windows(rows),
        "diagnosticFlags": flags,
        "diagnosticClassification": classification,
        "interpretationBoundary": (
            "This is a reference-free candidate-diversity audit. Concentration or low diversity is not proof that MIDI64 is wrong. "
            "No attack, pitch, timing, voicing, or render event is changed."
        ),
        "invariants": {
            "all725AttacksRead": total == ATTACK_COUNT,
            "allPrimaryMappingPartitionsReconcile": all([
                len(primary64) + len(non64) == total,
                len(mapped_open) + len(mapped_fretted) == total,
                len(midi_open) + len(midi_not_open) == total,
                len(any_selected_open) + len(no_selected_open) == total,
            ]),
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
    print(json.dumps({
        "classification": report["diagnosticClassification"],
        "definitionAudit": report["definitionAudit"],
        "candidateDiversity": report["candidateDiversity"],
        "midi64RivalPhysics": report["midi64RivalPhysics"],
    }, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: v143_frozen_evidence_open_string_candidate_audit.py SOURCE.json DEST.json")
    main(sys.argv[1], sys.argv[2])
