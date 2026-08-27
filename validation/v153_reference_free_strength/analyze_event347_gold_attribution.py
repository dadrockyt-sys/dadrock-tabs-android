#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = ROOT / "validation/rhythm_holdout"
for entry in (ROOT, HOLDOUT):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_rhythm_holdout as scorer  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import materialize_accepted_family  # noqa: E402

PREREG = ROOT / "debug/v153-reference-free-strength/phase-d-event347-attribution-preregistration.json"
CANDIDATE = ROOT / "debug/v153-reference-free-strength/candidate/candidate.json"
SCORE_RESULT = ROOT / "debug/v153-reference-free-strength/phase-c-score/score-result.json"
GOLD = ROOT / "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json"
V5 = ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"

EXPECTED = {
    "preregBlob": "5060106c4bf8646562c35dd9b9586e94550de454",
    "candidateBlob": "975ab36c234b423d1b56e59588e960f7d9d7103f",
    "candidateEventSha": "df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b",
    "scoreBlob": "02ee60863f2d55a410083e512a972818c3d7102b",
    "scoreSha": "1a6a18a338498f3d5015f9f56869319156cd31c6f77caf328bf70111caa0b501",
    "acceptedEventSha": "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
    "goldSha": "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac",
    "coreBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True
    ).strip()


def require_blob(path: Path, expected: str) -> None:
    actual = blob(path)
    if actual != expected:
        raise RuntimeError(f"blob mismatch {path}: {actual} != {expected}")


def pair_detail(
    pairs: Sequence[tuple[int, int]],
    generated_index: int,
    reference: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    for gi, ri in pairs:
        if gi == generated_index:
            return {"matched": True, "referenceIndex": ri, "referenceNote": dict(reference[ri])}
    return {"matched": False, "referenceIndex": None, "referenceNote": None}


def onset_pair_detail(
    pairs: Sequence[tuple[int, int]],
    generated_index: int,
    reference_onsets: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    for gi, ri in pairs:
        if gi == generated_index:
            return {"matched": True, "referenceIndex": ri, "referenceOnset": dict(reference_onsets[ri])}
    return {"matched": False, "referenceIndex": None, "referenceOnset": None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    out = args.output if args.output.is_absolute() else ROOT / args.output
    if out.exists():
        raise RuntimeError("one-use attribution output already exists")

    require_blob(PREREG, EXPECTED["preregBlob"])
    require_blob(CANDIDATE, EXPECTED["candidateBlob"])
    require_blob(SCORE_RESULT, EXPECTED["scoreBlob"])
    require_blob(ROOT / "validation/rhythm_holdout/score_rhythm_holdout.py", EXPECTED["coreBlob"])
    require_blob(ROOT / "validation/rhythm_holdout/canonical.py", EXPECTED["canonicalBlob"])
    require_blob(ROOT / "modal/v147_phase_c_artifact_support.py", EXPECTED["supportBlob"])
    if sha(SCORE_RESULT) != EXPECTED["scoreSha"]:
        raise RuntimeError("V153 score result SHA mismatch")
    if sha(GOLD) != EXPECTED["goldSha"]:
        raise RuntimeError("Gold SHA mismatch")

    accepted = canonical_events(materialize_accepted_family(load(V5)))
    candidate = canonical_events((load(CANDIDATE).get("renderEvents") or []))
    if sha256_json(accepted) != EXPECTED["acceptedEventSha"]:
        raise RuntimeError("accepted event SHA mismatch")
    if sha256_json(candidate) != EXPECTED["candidateEventSha"]:
        raise RuntimeError("candidate event SHA mismatch")
    if len(accepted) != 1144 or len(candidate) != 1144:
        raise RuntimeError("event count mismatch")

    changed = [int(a["eventIndex"]) for a, b in zip(accepted, candidate) if dict(a) != dict(b)]
    if changed != [347]:
        raise RuntimeError(f"unexpected changed set: {changed}")
    accepted_pos = next(i for i, row in enumerate(accepted) if int(row["eventIndex"]) == 347)
    candidate_pos = next(i for i, row in enumerate(candidate) if int(row["eventIndex"]) == 347)
    if accepted_pos != candidate_pos:
        raise RuntimeError("event 347 position changed")
    a347 = dict(accepted[accepted_pos])
    c347 = dict(candidate[candidate_pos])
    if (int(a347["measure"]), int(a347["step"]), int(a347["midi"]), int(c347["midi"])) != (35, 9, 62, 61):
        raise RuntimeError("event 347 expected identity mismatch")

    reference = scorer.validate_reference(load(GOLD))
    accepted_notes, _ = scorer.flatten_generated(accepted)
    candidate_notes, _ = scorer.flatten_generated(candidate)
    reference_notes, _, reference_measures = scorer.flatten_reference(reference)
    if len(reference_notes) != 946:
        raise RuntimeError("reference note count mismatch")

    accepted_pc = scorer.multiset_match(
        ((n["measure"], n["midi"]) for n in accepted_notes),
        ((n["measure"], n["midi"]) for n in reference_notes),
    )
    candidate_pc = scorer.multiset_match(
        ((n["measure"], n["midi"]) for n in candidate_notes),
        ((n["measure"], n["midi"]) for n in reference_notes),
    )

    def measure_midi_counts(notes: Sequence[Mapping[str, Any]]) -> Counter[tuple[int, int]]:
        return Counter((int(n["measure"]), int(n["midi"])) for n in notes)

    ac = measure_midi_counts(accepted_notes)
    cc = measure_midi_counts(candidate_notes)
    rc = measure_midi_counts(reference_notes)
    affected: dict[str, Any] = {}
    for midi in (62, 61):
        key = (35, midi)
        am = min(ac[key], rc[key])
        cm = min(cc[key], rc[key])
        affected[str(midi)] = {
            "measure": 35,
            "midi": midi,
            "acceptedGeneratedCount": ac[key],
            "candidateGeneratedCount": cc[key],
            "referenceCount": rc[key],
            "acceptedMatchedContribution": am,
            "candidateMatchedContribution": cm,
            "matchedContributionDelta": cm - am,
        }

    pitch_pairs_a = scorer.greedy_match(
        accepted_notes, reference_notes, lambda g, r: g["midi"] == r["midi"], scorer.STEP_TOLERANCE
    )
    pitch_pairs_c = scorer.greedy_match(
        candidate_notes, reference_notes, lambda g, r: g["midi"] == r["midi"], scorer.STEP_TOLERANCE
    )
    position_pairs_a = scorer.greedy_match(
        accepted_notes,
        reference_notes,
        lambda g, r: g["midi"] == r["midi"] and g["stringIndex"] == r["stringIndex"] and g["fret"] == r["fret"],
        scorer.STEP_TOLERANCE,
    )
    position_pairs_c = scorer.greedy_match(
        candidate_notes,
        reference_notes,
        lambda g, r: g["midi"] == r["midi"] and g["stringIndex"] == r["stringIndex"] and g["fret"] == r["fret"],
        scorer.STEP_TOLERANCE,
    )
    gross_pairs_a = scorer.greedy_match(
        accepted_notes, reference_notes, lambda g, r: g["midi"] == r["midi"], scorer.GROSS_STEP_TOLERANCE
    )
    gross_pairs_c = scorer.greedy_match(
        candidate_notes, reference_notes, lambda g, r: g["midi"] == r["midi"], scorer.GROSS_STEP_TOLERANCE
    )

    accepted_onsets = scorer.onset_groups(accepted_notes)
    candidate_onsets = scorer.onset_groups(candidate_notes)
    reference_onsets = scorer.onset_groups(reference_notes)
    onset_a_idx = next(i for i, x in enumerate(accepted_onsets) if int(x["measure"]) == 35 and int(x["step"]) == 9)
    onset_c_idx = next(i for i, x in enumerate(candidate_onsets) if int(x["measure"]) == 35 and int(x["step"]) == 9)
    pitchset_pairs_a = scorer.greedy_match(
        accepted_onsets, reference_onsets, lambda g, r: g["pitchSet"] == r["pitchSet"], scorer.STEP_TOLERANCE
    )
    pitchset_pairs_c = scorer.greedy_match(
        candidate_onsets, reference_onsets, lambda g, r: g["pitchSet"] == r["pitchSet"], scorer.STEP_TOLERANCE
    )
    voicing_pairs_a = scorer.greedy_match(
        accepted_onsets, reference_onsets, lambda g, r: g["voicing"] == r["voicing"], scorer.STEP_TOLERANCE
    )
    voicing_pairs_c = scorer.greedy_match(
        candidate_onsets, reference_onsets, lambda g, r: g["voicing"] == r["voicing"], scorer.STEP_TOLERANCE
    )

    accepted_measures = {int(n["measure"]) for n in accepted_notes}
    candidate_measures = {int(n["measure"]) for n in candidate_notes}
    missing_a = reference_measures - accepted_measures
    missing_c = reference_measures - candidate_measures
    critical_a = len(missing_a) + (len(reference_notes) - len(gross_pairs_a)) + (len(accepted_notes) - len(gross_pairs_a))
    critical_c = len(missing_c) + (len(reference_notes) - len(gross_pairs_c)) + (len(candidate_notes) - len(gross_pairs_c))

    nearby_reference = [
        dict(n) for n in reference_notes
        if int(n["measure"]) == 35 and 7 <= int(n["step"]) <= 11
    ]
    nearby_reference.sort(key=lambda n: (int(n["step"]), int(n["midi"]), int(n["stringIndex"])))

    score_result = load(SCORE_RESULT)
    result = {
        "schema": "dadrock.tabs.v153.event347.phase-d-attribution.v1",
        "classification": "cpu-reference-facing-post-score-attribution",
        "gate": "GO_EXPLAINED",
        "eventIndex": 347,
        "acceptedEvent": a347,
        "candidateEvent": c347,
        "changedFields": {k: {"accepted": a347.get(k), "candidate": c347.get(k)} for k in sorted(set(a347) | set(c347)) if a347.get(k) != c347.get(k)},
        "pitchContentMechanism": {
            "definition": "multiset match over (measure, midi), independent of step within the measure",
            "affectedMeasureMidiCounts": affected,
            "acceptedGlobalMatched": int(accepted_pc["matched"]),
            "candidateGlobalMatched": int(candidate_pc["matched"]),
            "globalMatchedDelta": int(candidate_pc["matched"] - accepted_pc["matched"]),
            "acceptedF1": float(accepted_pc["f1"]),
            "candidateF1": float(candidate_pc["f1"]),
            "f1Delta": float(candidate_pc["f1"] - accepted_pc["f1"]),
        },
        "timingAttribution": {
            "tolerantPitch": {
                "acceptedTotalMatches": len(pitch_pairs_a),
                "candidateTotalMatches": len(pitch_pairs_c),
                "totalDelta": len(pitch_pairs_c) - len(pitch_pairs_a),
                "acceptedEvent347": pair_detail(pitch_pairs_a, accepted_pos, reference_notes),
                "candidateEvent347": pair_detail(pitch_pairs_c, candidate_pos, reference_notes),
            },
            "tolerantPosition": {
                "acceptedTotalMatches": len(position_pairs_a),
                "candidateTotalMatches": len(position_pairs_c),
                "totalDelta": len(position_pairs_c) - len(position_pairs_a),
                "acceptedEvent347": pair_detail(position_pairs_a, accepted_pos, reference_notes),
                "candidateEvent347": pair_detail(position_pairs_c, candidate_pos, reference_notes),
            },
            "grossPitch": {
                "acceptedTotalMatches": len(gross_pairs_a),
                "candidateTotalMatches": len(gross_pairs_c),
                "totalDelta": len(gross_pairs_c) - len(gross_pairs_a),
                "acceptedEvent347": pair_detail(gross_pairs_a, accepted_pos, reference_notes),
                "candidateEvent347": pair_detail(gross_pairs_c, candidate_pos, reference_notes),
            },
        },
        "onsetAttribution": {
            "acceptedOnset": dict(accepted_onsets[onset_a_idx]),
            "candidateOnset": dict(candidate_onsets[onset_c_idx]),
            "pitchSet": {
                "acceptedTotalMatches": len(pitchset_pairs_a),
                "candidateTotalMatches": len(pitchset_pairs_c),
                "totalDelta": len(pitchset_pairs_c) - len(pitchset_pairs_a),
                "acceptedEvent347Onset": onset_pair_detail(pitchset_pairs_a, onset_a_idx, reference_onsets),
                "candidateEvent347Onset": onset_pair_detail(pitchset_pairs_c, onset_c_idx, reference_onsets),
            },
            "voicing": {
                "acceptedTotalMatches": len(voicing_pairs_a),
                "candidateTotalMatches": len(voicing_pairs_c),
                "totalDelta": len(voicing_pairs_c) - len(voicing_pairs_a),
                "acceptedEvent347Onset": onset_pair_detail(voicing_pairs_a, onset_a_idx, reference_onsets),
                "candidateEvent347Onset": onset_pair_detail(voicing_pairs_c, onset_c_idx, reference_onsets),
            },
        },
        "criticalMismatchAttribution": {
            "acceptedGrossPairs": len(gross_pairs_a),
            "candidateGrossPairs": len(gross_pairs_c),
            "acceptedCriticalMismatchCount": critical_a,
            "candidateCriticalMismatchCount": critical_c,
            "delta": critical_c - critical_a,
        },
        "nearbyGoldMeasure35Steps7to11": nearby_reference,
        "scoreResultCrossCheck": {
            "acceptedPitchContentF1": float(score_result["acceptedBaseline"]["gatedMetrics"]["pitchContentF1"]),
            "candidatePitchContentF1": float(score_result["score"]["gatedMetrics"]["pitchContentF1"]),
            "candidatePitchTimingMatches": int(score_result["score"]["diagnostics"]["pitchTiming"]["matched"]),
            "candidatePositionTimingMatches": int(score_result["score"]["diagnostics"]["stringFretTiming"]["matched"]),
            "candidateChordPitchSetMatches": int(score_result["score"]["diagnostics"]["chordPitchSet"]["matched"]),
            "candidateCriticalMismatchCount": int(score_result["score"]["criticalMismatchCount"]),
        },
        "interpretation": {
            "event347CausesExactlyOnePitchContentMatchLoss": int(candidate_pc["matched"] - accepted_pc["matched"]) == -1,
            "event347ChangesTolerantPitchMatchCount": len(pitch_pairs_c) != len(pitch_pairs_a),
            "event347ChangesTolerantPositionMatchCount": len(position_pairs_c) != len(position_pairs_a),
            "event347ChangesGrossPitchMatchCount": len(gross_pairs_c) != len(gross_pairs_a),
            "event347ChangesChordPitchSetMatchCount": len(pitchset_pairs_c) != len(pitchset_pairs_a),
            "event347ChangesVoicingMatchCount": len(voicing_pairs_c) != len(voicing_pairs_a),
            "event347ChangesCriticalMismatchCount": critical_c != critical_a,
        },
        "safety": {
            "scoreWrapperInvoked": False,
            "scoreCallCount": 0,
            "candidateModified": False,
            "candidateConstructed": False,
            "candidateVariantsConstructed": 0,
            "candidateSearchRun": False,
            "thresholdWeightFilterRuleTuning": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalL4CudaGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }

    if result["pitchContentMechanism"]["acceptedGlobalMatched"] != 370:
        raise RuntimeError("accepted pitch-content matched count unexpected")
    if result["pitchContentMechanism"]["candidateGlobalMatched"] != 369:
        raise RuntimeError("candidate pitch-content matched count unexpected")
    if result["timingAttribution"]["tolerantPitch"]["candidateTotalMatches"] != 70:
        raise RuntimeError("candidate tolerant pitch match cross-check failed")
    if result["timingAttribution"]["tolerantPosition"]["candidateTotalMatches"] != 57:
        raise RuntimeError("candidate tolerant position cross-check failed")
    if result["onsetAttribution"]["pitchSet"]["candidateTotalMatches"] != 42:
        raise RuntimeError("candidate pitch-set cross-check failed")
    if critical_c != 1712:
        raise RuntimeError("candidate critical mismatch cross-check failed")
    if result["pitchContentMechanism"]["globalMatchedDelta"] != -1:
        raise RuntimeError("pitch-content attribution did not isolate one lost match")
    if any((
        result["timingAttribution"]["tolerantPitch"]["totalDelta"],
        result["timingAttribution"]["tolerantPosition"]["totalDelta"],
        result["timingAttribution"]["grossPitch"]["totalDelta"],
        result["onsetAttribution"]["pitchSet"]["totalDelta"],
        result["onsetAttribution"]["voicing"]["totalDelta"],
        result["criticalMismatchAttribution"]["delta"],
    )):
        raise RuntimeError("non-pitch-content metric unexpectedly changed")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "eventIndex": 347,
        "pitchContentMatchedDelta": result["pitchContentMechanism"]["globalMatchedDelta"],
        "pitchContentF1Delta": result["pitchContentMechanism"]["f1Delta"],
        "tolerantPitchMatchDelta": result["timingAttribution"]["tolerantPitch"]["totalDelta"],
        "grossPitchMatchDelta": result["timingAttribution"]["grossPitch"]["totalDelta"],
        "chordPitchSetMatchDelta": result["onsetAttribution"]["pitchSet"]["totalDelta"],
        "criticalMismatchDelta": result["criticalMismatchAttribution"]["delta"],
        "scoreCallCount": 0,
        "modalL4CudaGpuUsed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
