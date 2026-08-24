from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence

SECONDARY_RAW_RATIO = 0.80
HARMONIC_SECONDARY_RAW_RATIO = 0.92
HARMONIC_INTERVALS = frozenset({12, 19, 24, 28, 31, 36})
EXPECTED_EVENT_SHA256 = "641a3928d7389e3c3e1593fc3b8432206434655bd798df79aeaa4b09666cf012"
EXPECTED_SOURCE_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"


def _finite(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite physical evidence: {value!r}")
    return number


def _canonical_event_sha(events: Sequence[Mapping[str, Any]]) -> str:
    raw = json.dumps(
        list(events),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _margin_counts(margins: Sequence[float]) -> dict[str, int]:
    return {
        "lt0p01": sum(value < 0.01 for value in margins),
        "lt0p02": sum(value < 0.02 for value in margins),
        "lt0p05": sum(value < 0.05 for value in margins),
        "lt0p10": sum(value < 0.10 for value in margins),
    }


def _rate(numerator: int, denominator: int) -> float:
    return float(numerator / denominator) if denominator else 0.0


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    events = product.get("events") or []
    if not isinstance(events, list) or not events:
        raise ValueError("candidate product has no events")

    trace = product.get("preFreezeTrace") or {}
    candidate = product.get("candidate") or {}
    diagnostics = product.get("precisionDiagnostics") or {}

    event_sha = _canonical_event_sha(events)
    if event_sha != EXPECTED_EVENT_SHA256:
        raise ValueError(f"unexpected candidate event SHA: {event_sha}")
    if str(trace.get("eventsSha256") or "") != EXPECTED_EVENT_SHA256:
        raise ValueError("preFreezeTrace event SHA mismatch")
    if str(candidate.get("sourceSha256") or "") != EXPECTED_SOURCE_SHA256:
        raise ValueError("approved source SHA mismatch")
    if candidate.get("professionalReferenceUsed") is not False:
        raise ValueError("professional reference must remain closed")

    attacks: dict[tuple[int, int], list[Mapping[str, Any]]] = defaultdict(list)
    for event in events:
        attacks[(int(event["measure"]), int(event["step"]))].append(event)

    support_distribution: Counter[int] = Counter()
    limiting_dimensions: Counter[str] = Counter()
    promoted_attack_count = 0
    retained_secondary_count = 0
    strongest_raw_secondary_count = 0
    nontrivial_secondary_count = 0
    harmonic_nontrivial_count = 0
    nonharmonic_nontrivial_count = 0
    margins: list[float] = []
    midi64_margins: list[float] = []
    non64_margins: list[float] = []
    midi64_attack_count = 0
    midi64_single_count = 0
    midi64_promoted_count = 0
    midi64_nontrivial_attack_keys: set[tuple[int, int]] = set()
    non64_attack_count = 0
    non64_single_count = 0
    non64_promoted_count = 0
    non64_nontrivial_attack_keys: set[tuple[int, int]] = set()
    gate_validation_failures: list[dict[str, Any]] = []
    retained_pitch_count = 0

    for key in sorted(attacks):
        hypotheses: dict[int, Mapping[str, Any]] = {}
        for event in attacks[key]:
            for hypothesis in event.get("pitchHypotheses") or []:
                midi = int(hypothesis["midi"])
                existing = hypotheses.get(midi)
                if existing is not None:
                    for field in ("physicalAttack", "physicalBody", "physicalScore", "precisionPrimary"):
                        if existing.get(field) != hypothesis.get(field):
                            raise ValueError(f"inconsistent duplicate hypothesis at {key}, MIDI {midi}")
                hypotheses[midi] = hypothesis

        primaries = [item for item in hypotheses.values() if item.get("precisionPrimary") is True]
        if len(primaries) != 1:
            raise ValueError(f"expected exactly one precision primary at {key}, found {len(primaries)}")

        primary = primaries[0]
        primary_midi = int(primary["midi"])
        strongest = max(
            hypotheses.values(),
            key=lambda item: (
                _finite(item["physicalScore"]),
                _finite(item["physicalAttack"]),
                -int(item["midi"]),
            ),
        )
        strongest_midi = int(strongest["midi"])
        promoted = primary_midi != strongest_midi
        promoted_attack_count += int(promoted)

        support_count = len(hypotheses)
        support_distribution[support_count] += 1
        retained_pitch_count += support_count

        if primary_midi == 64:
            midi64_attack_count += 1
            midi64_single_count += int(support_count == 1)
            midi64_promoted_count += int(promoted)
        else:
            non64_attack_count += 1
            non64_single_count += int(support_count == 1)
            non64_promoted_count += int(promoted)

        strongest_score = max(1e-6, _finite(strongest["physicalScore"]))
        strongest_attack = max(1e-6, _finite(strongest["physicalAttack"]))
        strongest_body = max(1e-6, _finite(strongest["physicalBody"]))

        for hypothesis in hypotheses.values():
            midi = int(hypothesis["midi"])
            if midi == primary_midi:
                continue
            retained_secondary_count += 1
            is_strongest_raw = midi == strongest_midi
            strongest_raw_secondary_count += int(is_strongest_raw)

            delta = midi - primary_midi
            harmonic_upper = delta in HARMONIC_INTERVALS
            floor = HARMONIC_SECONDARY_RAW_RATIO if harmonic_upper else SECONDARY_RAW_RATIO
            ratios = {
                "score": _finite(hypothesis["physicalScore"]) / strongest_score,
                "attack": _finite(hypothesis["physicalAttack"]) / strongest_attack,
                "body": _finite(hypothesis["physicalBody"]) / strongest_body,
            }

            failed = [name for name, ratio in ratios.items() if ratio + 1e-12 < floor]
            if failed:
                gate_validation_failures.append(
                    {
                        "measure": key[0],
                        "step": key[1],
                        "primaryMidi": primary_midi,
                        "midi": midi,
                        "floor": floor,
                        "failedDimensions": failed,
                    }
                )

            if is_strongest_raw:
                continue

            nontrivial_secondary_count += 1
            harmonic_nontrivial_count += int(harmonic_upper)
            nonharmonic_nontrivial_count += int(not harmonic_upper)
            minimum = min(ratios.values())
            margin = minimum - floor
            margins.append(margin)

            limiting = [name for name in ("score", "attack", "body") if abs(ratios[name] - minimum) <= 1e-12]
            limiting_dimensions["+".join(limiting)] += 1

            if primary_midi == 64:
                midi64_margins.append(margin)
                midi64_nontrivial_attack_keys.add(key)
            else:
                non64_margins.append(margin)
                non64_nontrivial_attack_keys.add(key)

    attack_count = len(attacks)
    if attack_count != int(diagnostics.get("retainedAttackCount") or -1):
        raise ValueError("retained attack count does not match precision diagnostics")
    if retained_pitch_count != int(diagnostics.get("retainedPitchHypothesisCount") or -1):
        raise ValueError("retained pitch count does not match precision diagnostics")
    if promoted_attack_count != int(diagnostics.get("fundamentalPromotionCount") or -1):
        raise ValueError("promotion count does not match precision diagnostics")
    if gate_validation_failures:
        raise ValueError(f"retained hypothesis failed historical gate: {gate_validation_failures[:3]}")

    margin_summary = {
        "count": len(margins),
        "minimum": min(margins) if margins else None,
        "median": statistics.median(margins) if margins else None,
        "maximum": max(margins) if margins else None,
        **_margin_counts(margins),
    }
    midi64_margin_summary = {
        "count": len(midi64_margins),
        "median": statistics.median(midi64_margins) if midi64_margins else None,
        **_margin_counts(midi64_margins),
    }
    non64_margin_summary = {
        "count": len(non64_margins),
        "median": statistics.median(non64_margins) if non64_margins else None,
        **_margin_counts(non64_margins),
    }

    return {
        "schemaVersion": 1,
        "classification": "hard-intersection-survivorship-brittleness-clue",
        "source": {
            "candidateProduct": "debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json",
            "candidateRunId": int(trace.get("runId") or 0),
            "triggerSha": str(trace.get("triggerSha") or ""),
            "eventsSha256": event_sha,
            "approvedAudioSha256": EXPECTED_SOURCE_SHA256,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "newInferenceUsed": False,
        },
        "historicalGate": {
            "secondaryRawRatio": SECONDARY_RAW_RATIO,
            "harmonicSecondaryRawRatio": HARMONIC_SECONDARY_RAW_RATIO,
            "harmonicIntervals": sorted(HARMONIC_INTERVALS),
            "denominator": "strongest-raw-candidate independently for score, attack, and body",
            "intersection": "score AND attack AND body",
        },
        "reconstruction": {
            "attackCount": attack_count,
            "retainedPitchHypothesisCount": retained_pitch_count,
            "retainedSecondaryHypothesisCount": retained_secondary_count,
            "fundamentalPromotionCount": promoted_attack_count,
            "strongestRawSecondaryCount": strongest_raw_secondary_count,
            "nontrivialSecondaryCount": nontrivial_secondary_count,
            "supportCountDistribution": {str(key): support_distribution[key] for key in sorted(support_distribution)},
            "gateValidationFailureCount": len(gate_validation_failures),
        },
        "nontrivialSecondarySurvivorship": {
            "definition": "retained secondary excluding the strongest-raw candidate that is necessarily retained when a lower fundamental is promoted",
            "count": nontrivial_secondary_count,
            "harmonicUpperCount": harmonic_nontrivial_count,
            "nonHarmonicCount": nonharmonic_nontrivial_count,
            "limitingDimensionCounts": dict(sorted(limiting_dimensions.items())),
            "minimumGateMarginSummary": margin_summary,
            "within0p05Rate": _rate(margin_summary["lt0p05"], len(margins)),
            "within0p10Rate": _rate(margin_summary["lt0p10"], len(margins)),
        },
        "midi64Survivorship": {
            "primaryMidi64AttackCount": midi64_attack_count,
            "primaryMidi64SingleHypothesisCount": midi64_single_count,
            "primaryMidi64SingleHypothesisRate": _rate(midi64_single_count, midi64_attack_count),
            "primaryMidi64PromotionCount": midi64_promoted_count,
            "primaryMidi64PromotionRate": _rate(midi64_promoted_count, midi64_attack_count),
            "primaryMidi64AttacksWithNontrivialSecondary": len(midi64_nontrivial_attack_keys),
            "primaryMidi64NontrivialSecondaryAttackRate": _rate(len(midi64_nontrivial_attack_keys), midi64_attack_count),
            "primaryMidi64NontrivialSecondaryMargins": midi64_margin_summary,
            "non64AttackCount": non64_attack_count,
            "non64SingleHypothesisCount": non64_single_count,
            "non64SingleHypothesisRate": _rate(non64_single_count, non64_attack_count),
            "non64PromotionCount": non64_promoted_count,
            "non64PromotionRate": _rate(non64_promoted_count, non64_attack_count),
            "non64AttacksWithNontrivialSecondary": len(non64_nontrivial_attack_keys),
            "non64NontrivialSecondaryAttackRate": _rate(len(non64_nontrivial_attack_keys), non64_attack_count),
            "non64NontrivialSecondaryMargins": non64_margin_summary,
        },
        "interpretation": {
            "strongestRawSecondaryAccounting": (
                "All 144 promoted-fundamental attacks necessarily retain the strongest raw candidate; "
                "those 144 rows account for 144 of the 262 retained secondaries. Only 118 retained "
                "secondaries are nontrivial gate survivors."
            ),
            "brittleness": (
                "Among the 118 nontrivial retained secondaries, attack is the limiting dimension 57 times, "
                "body 47 times, and total score only 14 times. 61/118 survive within 0.05 of the hard floor "
                "and 94/118 within 0.10. The surviving boundary is therefore controlled primarily by the "
                "independent attack/body conjunction rather than total physical score."
            ),
            "midi64": (
                "Only 15/202 primary-MIDI64 attacks retain any nontrivial secondary, versus 93/523 non64 attacks. "
                "This is a retained-survivorship disparity only; the unavailable suppressed rows prevent an exact "
                "claim about how many MIDI64 alternatives a relaxed rule would recover."
            ),
            "suppressedRowsUnavailable": True,
            "exactRecoveryCountsClaimed": False,
            "eventMutationJustified": False,
            "nextSafeTest": (
                "Evaluate a source-only alternative such as strong total score plus either strong attack or strong body "
                "when full pre-precision rows become available; do not tune thresholds against professional mismatches."
            ),
        },
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json",
    )
    parser.add_argument(
        "--output",
        default="debug/v143-contextual-prune/precision-survivorship-gate-brittleness-diagnostic.json",
    )
    args = parser.parse_args()
    product = json.loads(Path(args.input).read_text())
    report = build_report(product)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
