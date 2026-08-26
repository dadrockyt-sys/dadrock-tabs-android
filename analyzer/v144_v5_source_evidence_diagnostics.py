#!/usr/bin/env python3
"""Grade frozen V5 decisions by their original source-only V2 evidence.

The professional source is already-consumed calibration material. It is used only to
label outcomes for aggregate diagnostics; this script never edits V5 or emits the
reference payload. Runtime/V6 rules must depend on source-only fields, not reference
values.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from v144_rhythm_calibration_diagnostics import build_reference  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = 1.0 if generated == 0 else matched / generated
    recall = 1.0 if reference == 0 else matched / reference
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "matched": matched,
        "generated": generated,
        "reference": reference,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def percentile(values: Sequence[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    low = int(index)
    high = min(low + 1, len(ordered) - 1)
    fraction = index - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def numeric_summary(values: Iterable[Any]) -> dict[str, Any]:
    cleaned = [float(value) for value in values if isinstance(value, (int, float))]
    if not cleaned:
        return {"count": 0}
    return {
        "count": len(cleaned),
        "min": min(cleaned),
        "p10": percentile(cleaned, 0.10),
        "p25": percentile(cleaned, 0.25),
        "median": statistics.median(cleaned),
        "p75": percentile(cleaned, 0.75),
        "p90": percentile(cleaned, 0.90),
        "max": max(cleaned),
        "mean": statistics.fmean(cleaned),
    }


def outcome_summary(rows: Sequence[Mapping[str, Any]], label: str) -> dict[str, Any]:
    matched = [row for row in rows if bool(row[label])]
    missed = [row for row in rows if not bool(row[label])]
    fields = (
        "precisionStrength",
        "precisionGridErrorSeconds",
        "stemSupportMax",
        "sweepSupportMax",
        "detectionCountSum",
    )
    return {
        "rowCount": len(rows),
        "matchedCount": len(matched),
        "unmatchedCount": len(missed),
        "matched": {field: numeric_summary(row.get(field) for row in matched) for field in fields},
        "unmatched": {field: numeric_summary(row.get(field) for row in missed) for field in fields},
    }


def attack_metric(rows: Sequence[Mapping[str, Any]], reference_onsets: set[tuple[int, int]]) -> dict[str, Any]:
    retained = {(int(row["measure"]), int(row["step"])) for row in rows}
    matched = len(retained & reference_onsets)
    return prf(matched, len(retained), len(reference_onsets))


def event_metric(rows: Sequence[Mapping[str, Any]], reference_events: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    generated = Counter((int(row["measure"]), int(row["step"]), int(row["midi"])) for row in rows)
    matched = sum((generated & reference_events).values())
    return prf(matched, sum(generated.values()), sum(reference_events.values()))


def evaluate_attack_rules(
    rows: Sequence[Mapping[str, Any]], reference_onsets: set[tuple[int, int]]
) -> list[dict[str, Any]]:
    rules: list[tuple[str, Any]] = [("all-v5", lambda row: True)]
    for value in (1, 2):
        rules.append((f"stemSupportMax>={value}", lambda row, value=value: float(row["stemSupportMax"]) >= value))
    for value in (1, 2, 3, 4):
        rules.append((f"sweepSupportMax>={value}", lambda row, value=value: float(row["sweepSupportMax"]) >= value))
    for value in (4, 6, 8, 10, 12, 16, 20, 24, 32):
        rules.append((f"detectionCountSum>={value}", lambda row, value=value: float(row["detectionCountSum"]) >= value))
    for value in (2.0, 3.0, 4.0, 5.0, 6.0):
        rules.append((f"precisionStrength>={value}", lambda row, value=value: float(row["precisionStrength"]) >= value))
    for value in (0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.16):
        rules.append((f"gridError<={value:.2f}", lambda row, value=value: float(row["precisionGridErrorSeconds"]) <= value))
    # Conservative combinations chosen only from source-side evidence dimensions.
    for detections in (8, 12, 16):
        for grid_error in (0.06, 0.10, 0.16):
            rules.append((
                f"detection>={detections}&grid<={grid_error:.2f}",
                lambda row, detections=detections, grid_error=grid_error:
                    float(row["detectionCountSum"]) >= detections
                    and float(row["precisionGridErrorSeconds"]) <= grid_error,
            ))

    results: list[dict[str, Any]] = []
    for name, predicate in rules:
        kept = [row for row in rows if predicate(row)]
        odd = [row for row in kept if int(row["measure"]) % 2 == 1]
        even = [row for row in kept if int(row["measure"]) % 2 == 0]
        odd_ref = {key for key in reference_onsets if key[0] % 2 == 1}
        even_ref = {key for key in reference_onsets if key[0] % 2 == 0}
        overall = attack_metric(kept, reference_onsets)
        odd_metric = attack_metric(odd, odd_ref)
        even_metric = attack_metric(even, even_ref)
        results.append({
            "rule": name,
            "keptAttackCount": len(kept),
            "overall": overall,
            "oddMeasures": odd_metric,
            "evenMeasures": even_metric,
            "crossSplitMinF1": min(float(odd_metric["f1"]), float(even_metric["f1"])),
        })
    return sorted(
        results,
        key=lambda row: (
            -float(row["crossSplitMinF1"]),
            -float(row["overall"]["f1"]),
            -float(row["overall"]["precision"]),
            -int(row["keptAttackCount"]),
        ),
    )


def candidate_features(candidate: Mapping[str, Any], candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    score = float(candidate.get("score") or 0.0)
    scores = sorted((float(item.get("score") or 0.0) for item in candidates), reverse=True)
    score_rank = 1 + sum(1 for value in scores if value > score + 1e-12)
    best_score = scores[0] if scores else score
    view_a = candidate.get("viewA") if isinstance(candidate.get("viewA"), Mapping) else {}
    view_b = candidate.get("viewB") if isinstance(candidate.get("viewB"), Mapping) else {}
    return {
        "candidateScore": score,
        "scoreDeltaFromBest": best_score - score,
        "candidateScoreRank": score_rank,
        "candidateAttack": float(candidate.get("attack") or 0.0),
        "candidateEarly": float(candidate.get("early") or 0.0),
        "candidateSustain": float(candidate.get("sustain") or 0.0),
        "candidateBody": float(candidate.get("body") or 0.0),
        "candidateContinuity": float(candidate.get("continuity") or 0.0),
        "originalV2Selected": bool(candidate.get("selected")),
        "originalV2Primary": bool(candidate.get("primary")),
        "viewAttackDelta": abs(float(view_a.get("attack") or 0.0) - float(view_b.get("attack") or 0.0)),
        "viewEarlyDelta": abs(float(view_a.get("early") or 0.0) - float(view_b.get("early") or 0.0)),
        "viewSustainDelta": abs(float(view_a.get("sustain") or 0.0) - float(view_b.get("sustain") or 0.0)),
    }


def pitch_outcome_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    fields = (
        "candidateScore",
        "scoreDeltaFromBest",
        "candidateScoreRank",
        "candidateAttack",
        "candidateEarly",
        "candidateSustain",
        "candidateBody",
        "candidateContinuity",
        "viewAttackDelta",
        "viewEarlyDelta",
        "viewSustainDelta",
    )
    matched = [row for row in rows if row["exactPitchAtExactOnset"]]
    unmatched = [row for row in rows if not row["exactPitchAtExactOnset"]]
    return {
        "rowCount": len(rows),
        "matchedCount": len(matched),
        "unmatchedCount": len(unmatched),
        "matched": {field: numeric_summary(row.get(field) for row in matched) for field in fields},
        "unmatched": {field: numeric_summary(row.get(field) for row in unmatched) for field in fields},
        "matchedFlags": {
            "v5Primary": sum(bool(row.get("v5Primary")) for row in matched),
            "v5PrimaryCorrected": sum(bool(row.get("v5PrimaryCorrected")) for row in matched),
            "originalV2Selected": sum(bool(row.get("originalV2Selected")) for row in matched),
            "originalV2Primary": sum(bool(row.get("originalV2Primary")) for row in matched),
        },
        "unmatchedFlags": {
            "v5Primary": sum(bool(row.get("v5Primary")) for row in unmatched),
            "v5PrimaryCorrected": sum(bool(row.get("v5PrimaryCorrected")) for row in unmatched),
            "originalV2Selected": sum(bool(row.get("originalV2Selected")) for row in unmatched),
            "originalV2Primary": sum(bool(row.get("originalV2Primary")) for row in unmatched),
        },
    }


def octave_confusion_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    false_rows = [row for row in rows if not row["exactPitchAtExactOnset"]]
    lower_available = [row for row in false_rows if row.get("lowerOctaveCandidateAvailable")]
    upper_available = [row for row in false_rows if row.get("upperOctaveCandidateAvailable")]
    lower_reference = [row for row in lower_available if row.get("lowerOctaveIsReferenceAtOnset")]
    upper_reference = [row for row in upper_available if row.get("upperOctaveIsReferenceAtOnset")]
    return {
        "falseEventCount": len(false_rows),
        "falseWithLowerOctaveCandidate": len(lower_available),
        "falseWithUpperOctaveCandidate": len(upper_available),
        "falseWhereLowerOctaveCandidateIsReferencePitch": len(lower_reference),
        "falseWhereUpperOctaveCandidateIsReferencePitch": len(upper_reference),
        "lowerReferenceScoreDelta": numeric_summary(row.get("lowerOctaveScoreMinusEventScore") for row in lower_reference),
        "upperReferenceScoreDelta": numeric_summary(row.get("upperOctaveScoreMinusEventScore") for row in upper_reference),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v5_stream", type=Path)
    parser.add_argument("v2_candidate_product", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    stream = load_json(args.v5_stream)
    v5_events = stream.get("events")
    if not isinstance(v5_events, list) or len(v5_events) != 1209:
        raise ValueError("expected exact frozen V5 1209-event stream")

    product = load_json(args.v2_candidate_product)
    replay = product.get("precisionReplayEvidence") if isinstance(product, Mapping) else None
    if not isinstance(replay, Mapping):
        raise ValueError("V2 product missing precisionReplayEvidence")
    eligible = replay.get("eligibleAttacks")
    if not isinstance(eligible, list) or len(eligible) != 984:
        raise ValueError("expected exact V2 984 eligible attacks")
    if int(replay.get("retainedAttackCount") or -1) != 725:
        raise ValueError("unexpected V2 retained attack count")

    reference_notes = build_reference(load_json(args.structured_source))
    reference_onsets = {(int(note["measure"]), int(note["step"])) for note in reference_notes}
    reference_events = Counter(
        (int(note["measure"]), int(note["step"]), int(note["midi"])) for note in reference_notes
    )
    reference_pitches_by_onset: dict[tuple[int, int], set[int]] = defaultdict(set)
    for note in reference_notes:
        reference_pitches_by_onset[(int(note["measure"]), int(note["step"]))].add(int(note["midi"]))

    evidence_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    for attack in eligible:
        key = (int(attack["measure"]), int(attack["step"]))
        if key in evidence_by_key:
            raise ValueError(f"duplicate V2 eligible attack key {key}")
        evidence_by_key[key] = attack

    grouped_v5: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for event in v5_events:
        grouped_v5[(int(event["measure"]), int(event["step"]))].append(event)
    if len(grouped_v5) != 891:
        raise ValueError(f"expected V5 891 attack groups, got {len(grouped_v5)}")

    attack_rows: list[dict[str, Any]] = []
    event_rows: list[dict[str, Any]] = []
    missing_attack_evidence: list[str] = []
    missing_pitch_evidence = 0

    for key, events in sorted(grouped_v5.items()):
        attack = evidence_by_key.get(key)
        if attack is None:
            missing_attack_evidence.append(f"{key[0]}:{key[1]}")
            continue
        attack_class_values = {str(event.get("v5AttackClass")) for event in events}
        attack_class = next(iter(attack_class_values)) if len(attack_class_values) == 1 else "mixed"
        ref_pitches = reference_pitches_by_onset.get(key, set())
        v5_midis = [int(event["midi"]) for event in events]
        attack_row = {
            "measure": key[0],
            "step": key[1],
            "v5AttackClass": attack_class,
            "referenceOnsetExact": key in reference_onsets,
            "anyV5PitchExactAtOnset": any(midi in ref_pitches for midi in v5_midis),
            "v5PitchCount": len(v5_midis),
            "referencePitchCountAtOnset": len(ref_pitches),
            "precisionStrength": float(attack.get("precisionStrength") or 0.0),
            "precisionGridErrorSeconds": float(attack.get("precisionGridErrorSeconds") or 0.0),
            "stemSupportMax": float(attack.get("stemSupportMax") or 0.0),
            "sweepSupportMax": float(attack.get("sweepSupportMax") or 0.0),
            "detectionCountSum": float(attack.get("detectionCountSum") or 0.0),
            "originalV2Retained": bool(attack.get("retained")),
        }
        attack_rows.append(attack_row)

        candidates = attack.get("candidates") if isinstance(attack.get("candidates"), list) else []
        candidate_by_midi = {int(candidate["midi"]): candidate for candidate in candidates if isinstance(candidate, Mapping) and isinstance(candidate.get("midi"), int)}
        for event in events:
            midi = int(event["midi"])
            candidate = candidate_by_midi.get(midi)
            if candidate is None:
                missing_pitch_evidence += 1
                features = {}
            else:
                features = candidate_features(candidate, candidates)
            lower = candidate_by_midi.get(midi - 12)
            upper = candidate_by_midi.get(midi + 12)
            row = {
                "measure": key[0],
                "step": key[1],
                "midi": midi,
                "v5AttackClass": attack_class,
                "v5Primary": bool(event.get("v5Primary")),
                "v5PrimaryCorrected": bool(event.get("v5PrimaryCorrected")),
                "metadataSource": event.get("metadataSource"),
                "exactPitchAtExactOnset": midi in ref_pitches,
                "referenceOnsetExact": key in reference_onsets,
                "lowerOctaveCandidateAvailable": lower is not None,
                "upperOctaveCandidateAvailable": upper is not None,
                "lowerOctaveIsReferenceAtOnset": (midi - 12) in ref_pitches,
                "upperOctaveIsReferenceAtOnset": (midi + 12) in ref_pitches,
                "lowerOctaveScoreMinusEventScore": None if lower is None or candidate is None else float(lower.get("score") or 0.0) - float(candidate.get("score") or 0.0),
                "upperOctaveScoreMinusEventScore": None if upper is None or candidate is None else float(upper.get("score") or 0.0) - float(candidate.get("score") or 0.0),
                **features,
            }
            event_rows.append(row)

    if missing_attack_evidence:
        raise ValueError(f"V5 attacks missing exact V2 evidence: {missing_attack_evidence[:20]}")

    baseline_attacks = [row for row in attack_rows if row["v5AttackClass"] == "baseline"]
    rescued_attacks = [row for row in attack_rows if row["v5AttackClass"] == "rescued"]
    baseline_events = [row for row in event_rows if row["v5AttackClass"] == "baseline"]
    rescued_events = [row for row in event_rows if row["v5AttackClass"] == "rescued"]

    report = {
        "schemaVersion": 1,
        "classification": "v144-v5-source-evidence-calibration-diagnostic",
        "calibrationReferenceUsed": True,
        "unseenHoldout": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "v2EligibleAttackCount": len(eligible),
        "v2OriginallyRetainedAttackCount": sum(bool(row.get("retained")) for row in eligible),
        "v5AttackCount": len(attack_rows),
        "v5EventCount": len(event_rows),
        "v5BaselineAttackCount": len(baseline_attacks),
        "v5RescuedAttackCount": len(rescued_attacks),
        "missingPitchEvidenceEventCount": missing_pitch_evidence,
        "referenceOnsetCount": len(reference_onsets),
        "referenceNoteCount": len(reference_notes),
        "attackMetrics": {
            "allV5": attack_metric(attack_rows, reference_onsets),
            "baselineOnly": attack_metric(baseline_attacks, reference_onsets),
            "rescuedOnly": attack_metric(rescued_attacks, reference_onsets),
        },
        "attackEvidenceByOutcome": {
            "allV5": outcome_summary(attack_rows, "referenceOnsetExact"),
            "baseline": outcome_summary(baseline_attacks, "referenceOnsetExact"),
            "rescued": outcome_summary(rescued_attacks, "referenceOnsetExact"),
        },
        "attackRuleSweep": evaluate_attack_rules(attack_rows, reference_onsets)[:30],
        "eventMetrics": {
            "allV5Exact": event_metric(event_rows, reference_events),
            "baselineExact": event_metric(baseline_events, reference_events),
            "rescuedExact": event_metric(rescued_events, reference_events),
        },
        "pitchEvidenceByOutcome": {
            "allV5": pitch_outcome_summary(event_rows),
            "baseline": pitch_outcome_summary(baseline_events),
            "rescued": pitch_outcome_summary(rescued_events),
        },
        "octaveConfusion": {
            "allV5": octave_confusion_summary(event_rows),
            "baseline": octave_confusion_summary(baseline_events),
            "rescued": octave_confusion_summary(rescued_events),
        },
        "provenanceCounts": {
            "attackClass": dict(sorted(Counter(row["v5AttackClass"] for row in attack_rows).items())),
            "metadataSource": dict(sorted(Counter(str(event.get("metadataSource")) for event in v5_events).items())),
            "v5Primary": dict(sorted((str(key), value) for key, value in Counter(bool(event.get("v5Primary")) for event in v5_events).items())),
            "v5PrimaryCorrected": dict(sorted((str(key), value) for key, value in Counter(bool(event.get("v5PrimaryCorrected")) for event in v5_events).items())),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
