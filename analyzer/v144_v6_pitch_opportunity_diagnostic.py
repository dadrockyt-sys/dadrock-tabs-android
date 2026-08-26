#!/usr/bin/env python3
"""Report-only V6 pitch opportunity diagnostic.

Determines whether exact calibration-reference pitches at already-shared V6 onsets are:
- already selected by the V6 primary;
- present somewhere in the original V2 source candidate pool (selection problem);
- present only as the right pitch class in another octave/register (register problem); or
- absent even by pitch class (candidate-generation/separation problem).

This script never writes or modifies a candidate.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any, Mapping, Sequence

from v144_rhythm_calibration_diagnostics import build_reference


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def summary(values: Sequence[float]) -> dict[str, Any]:
    values = sorted(float(v) for v in values)
    if not values:
        return {"count": 0}
    def pct(q: float) -> float:
        if len(values) == 1:
            return values[0]
        pos = (len(values) - 1) * q
        lo = int(pos)
        hi = min(len(values) - 1, lo + 1)
        frac = pos - lo
        return values[lo] * (1.0 - frac) + values[hi] * frac
    return {
        "count": len(values),
        "min": values[0],
        "p10": pct(0.10),
        "p25": pct(0.25),
        "median": median(values),
        "mean": mean(values),
        "p75": pct(0.75),
        "p90": pct(0.90),
        "max": values[-1],
    }


def key(row: Mapping[str, Any]) -> tuple[int, int]:
    return int(row["measure"]), int(row["step"])


def classify_onset(
    v6_group: Sequence[Mapping[str, Any]],
    attack: Mapping[str, Any],
    ref_group: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    candidates = [c for c in attack.get("candidates", []) if isinstance(c, Mapping) and isinstance(c.get("midi"), int)]
    ranked = sorted(candidates, key=lambda c: (-float(c.get("score") or 0.0), int(c["midi"])))
    ref_midis = [int(n["midi"]) for n in ref_group]
    ref_set = set(ref_midis)
    ref_pcs = {m % 12 for m in ref_midis}
    candidate_midis = {int(c["midi"]) for c in candidates}
    candidate_pcs = {m % 12 for m in candidate_midis}
    v6_midis = [int(e["midi"]) for e in v6_group]
    v6_set = set(v6_midis)
    primaries = [e for e in v6_group if bool(e.get("v5Primary"))]
    if len(primaries) != 1:
        raise ValueError(f"expected one V6 primary at {key(v6_group[0])}, got {len(primaries)}")
    primary_midi = int(primaries[0]["midi"])
    top_midi = int(ranked[0]["midi"]) if ranked else None

    exact_candidates = [c for c in ranked if int(c["midi"]) in ref_set]
    pc_candidates = [c for c in ranked if int(c["midi"]) % 12 in ref_pcs]
    best_exact_rank = None
    best_exact_gap = None
    best_exact_midi = None
    if exact_candidates and ranked:
        score_by_midi = {int(c["midi"]): float(c.get("score") or 0.0) for c in ranked}
        top_score = float(ranked[0].get("score") or 0.0)
        ranks = [(i + 1, c) for i, c in enumerate(ranked) if int(c["midi"]) in ref_set]
        best_exact_rank, best_c = ranks[0]
        best_exact_midi = int(best_c["midi"])
        best_exact_gap = top_score - score_by_midi[best_exact_midi]

    selected_midis = {int(c["midi"]) for c in candidates if bool(c.get("selected"))}
    original_primary_midis = {int(c["midi"]) for c in candidates if bool(c.get("primary"))}
    return {
        "primaryExactHit": primary_midi in ref_set,
        "v6AnyExactHit": bool(v6_set & ref_set),
        "candidateExactHit": bool(candidate_midis & ref_set),
        "candidatePitchClassHit": bool(candidate_pcs & ref_pcs),
        "topScoreExactHit": top_midi in ref_set if top_midi is not None else False,
        "originalV2SelectedExactHit": bool(selected_midis & ref_set),
        "originalV2PrimaryExactHit": bool(original_primary_midis & ref_set),
        "allReferenceMidiSetCoveredByCandidates": ref_set <= candidate_midis,
        "allReferencePitchClassSetCoveredByCandidates": ref_pcs <= candidate_pcs,
        "bestExactCandidateRank": best_exact_rank,
        "bestExactCandidateScoreGapFromTop": best_exact_gap,
        "bestExactCandidateMidi": best_exact_midi,
        "primaryMidi": primary_midi,
        "topScoreMidi": top_midi,
        "candidateCount": len(candidates),
        "v6EventCountAtOnset": len(v6_group),
        "referenceEventCountAtOnset": len(ref_group),
    }


def aggregate(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    flag_names = (
        "primaryExactHit",
        "v6AnyExactHit",
        "candidateExactHit",
        "candidatePitchClassHit",
        "topScoreExactHit",
        "originalV2SelectedExactHit",
        "originalV2PrimaryExactHit",
        "allReferenceMidiSetCoveredByCandidates",
        "allReferencePitchClassSetCoveredByCandidates",
    )
    flags = {name: sum(1 for row in rows if bool(row.get(name))) for name in flag_names}
    primary_wrong = [row for row in rows if not bool(row.get("primaryExactHit"))]
    selection_fixable = [row for row in primary_wrong if bool(row.get("candidateExactHit"))]
    register_only = [
        row for row in primary_wrong
        if not bool(row.get("candidateExactHit")) and bool(row.get("candidatePitchClassHit"))
    ]
    candidate_miss = [row for row in primary_wrong if not bool(row.get("candidatePitchClassHit"))]
    exact_ranks = [float(row["bestExactCandidateRank"]) for row in rows if row.get("bestExactCandidateRank") is not None]
    exact_gaps = [float(row["bestExactCandidateScoreGapFromTop"]) for row in rows if row.get("bestExactCandidateScoreGapFromTop") is not None]
    return {
        "sharedOnsetCount": total,
        "flags": flags,
        "primaryWrongOnsetCount": len(primary_wrong),
        "primaryWrongButExactCandidateExists": len(selection_fixable),
        "primaryWrongNoExactCandidateButPitchClassCandidateExists": len(register_only),
        "primaryWrongNoCandidatePitchClassMatch": len(candidate_miss),
        "bestExactCandidateRank": summary(exact_ranks),
        "bestExactCandidateScoreGapFromTop": summary(exact_gaps),
        "candidateCount": summary([float(row["candidateCount"]) for row in rows]),
        "v6EventCountAtOnset": summary([float(row["v6EventCountAtOnset"]) for row in rows]),
        "referenceEventCountAtOnset": summary([float(row["referenceEventCountAtOnset"]) for row in rows]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v6_stream", type=Path)
    parser.add_argument("v2_candidate_product", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    v6 = load_json(args.v6_stream)
    events = v6.get("events") if isinstance(v6, Mapping) else None
    if not isinstance(events, list) or len(events) != 1149:
        raise ValueError("expected frozen V6 with 1149 events")

    product = load_json(args.v2_candidate_product)
    replay = product.get("precisionReplayEvidence") if isinstance(product, Mapping) else None
    eligible = replay.get("eligibleAttacks") if isinstance(replay, Mapping) else None
    if not isinstance(eligible, list) or len(eligible) != 984:
        raise ValueError("expected exact V2 replay evidence with 984 eligible attacks")

    reference = build_reference(load_json(args.structured_source))
    if len(reference) != 946:
        raise ValueError("expected 946 calibration reference notes")

    v6_by_key: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    ref_by_key: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for event in events:
        v6_by_key[key(event)].append(event)
    for note in reference:
        ref_by_key[key(note)].append(note)
    evidence_by_key = {(int(a["measure"]), int(a["step"])): a for a in eligible}

    shared = sorted(set(v6_by_key) & set(ref_by_key))
    if len(shared) != 351:
        raise ValueError(f"expected 351 frozen V6/reference shared onsets, got {len(shared)}")

    rows: list[dict[str, Any]] = []
    for k in shared:
        attack = evidence_by_key.get(k)
        if attack is None:
            raise ValueError(f"missing V2 evidence at shared onset {k}")
        row = classify_onset(v6_by_key[k], attack, ref_by_key[k])
        row["measureParity"] = "odd" if k[0] % 2 else "even"
        rows.append(row)

    odd = [row for row in rows if row["measureParity"] == "odd"]
    even = [row for row in rows if row["measureParity"] == "even"]

    v6_only_onsets = sorted(set(v6_by_key) - set(ref_by_key))
    ref_only_onsets = sorted(set(ref_by_key) - set(v6_by_key))

    report = {
        "schemaVersion": 1,
        "classification": "v144-v6-pitch-opportunity-calibration-diagnostic",
        "calibrationReferenceUsed": True,
        "unseenHoldout": False,
        "candidateModified": False,
        "candidateGenerated": False,
        "modalInvoked": False,
        "productionModified": False,
        "v6EventCount": len(events),
        "v6OnsetCount": len(v6_by_key),
        "referenceEventCount": len(reference),
        "referenceOnsetCount": len(ref_by_key),
        "sharedOnsetCount": len(shared),
        "v6OnlyOnsetCount": len(v6_only_onsets),
        "referenceOnlyOnsetCount": len(ref_only_onsets),
        "overall": aggregate(rows),
        "oddMeasures": aggregate(odd),
        "evenMeasures": aggregate(even),
        "interpretationBuckets": {
            "selectionFixableDefinition": "V6 primary misses, but exact reference MIDI exists in the original V2 candidate set at the same onset.",
            "registerOnlyDefinition": "V6 primary misses and exact reference MIDI is absent, but the correct reference pitch class exists in another register in the V2 candidate set.",
            "candidateGenerationMissDefinition": "V6 primary misses and no V2 candidate at that onset even matches a reference pitch class; selection logic alone cannot recover the target pitch class.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
