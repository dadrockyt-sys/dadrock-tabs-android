#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from v143_contextual_prune_precision_shadow import _precision_pitch_set


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRODUCT = ROOT / "debug" / "v143-contextual-prune" / "repaired-timing-precision-candidate-product.json"
DEFAULT_OUTPUT = ROOT / "debug" / "v143-contextual-prune" / "precision-polyphonic-expansion-audit.json"
EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}
SPECTRUM_MIDI_MIN = 28
SPECTRUM_MIDI_MAX = 112


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if math.isfinite(number) else fallback


def _event_key(event: Mapping[str, Any]) -> tuple[int, int]:
    return int(event["measure"]), int(event["step"])


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ratio(value: float, denominator: float) -> float:
    return float(value / max(1e-9, denominator))


def _quantiles(values: Iterable[float]) -> dict[str, float | None]:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return {"min": None, "p10": None, "p25": None, "median": None, "p75": None, "p90": None, "max": None}

    def q(fraction: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        index = fraction * (len(ordered) - 1)
        lo = int(math.floor(index))
        hi = int(math.ceil(index))
        if lo == hi:
            return ordered[lo]
        weight = index - lo
        return ordered[lo] * (1.0 - weight) + ordered[hi] * weight

    return {
        "min": ordered[0],
        "p10": q(0.10),
        "p25": q(0.25),
        "median": q(0.50),
        "p75": q(0.75),
        "p90": q(0.90),
        "max": ordered[-1],
    }


def _synthetic_harmonic_promotion_double_count() -> dict[str, Any]:
    size = SPECTRUM_MIDI_MAX - SPECTRUM_MIDI_MIN + 1

    def vector(lower: float, upper: float) -> list[float]:
        values = [-2.0] * size
        values[40 - SPECTRUM_MIDI_MIN] = float(lower)
        values[52 - SPECTRUM_MIDI_MIN] = float(upper)
        return values

    lower = 0.78
    upper = 0.90
    row = {
        "candidateMidis": [40, 52],
        "viewA": {
            "attackMax": vector(lower, upper),
            "earlyMean": vector(lower, upper),
            "sustainMean": vector(lower, upper),
        },
        "viewB": {
            "attackMax": vector(lower, upper),
            "earlyMean": vector(lower, upper),
            "sustainMean": vector(lower, upper),
        },
    }
    selected, promoted, primary = _precision_pitch_set(row)
    strongest_raw = 52
    interval = strongest_raw - int(primary)
    return {
        "syntheticObservedMidis": [40, 52],
        "syntheticPrimaryMidi": int(primary),
        "syntheticStrongestRawMidi": strongest_raw,
        "syntheticSelectedMidis": list(selected),
        "syntheticPrimaryPromoted": bool(promoted),
        "syntheticStrongestRawIntervalAbovePrimary": interval,
        "syntheticStrongestHarmonicRetainedAsSecondary": bool(
            promoted
            and interval in HARMONIC_INTERVALS
            and strongest_raw in set(selected)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    product_path = Path(args.product)
    output_path = Path(args.output)
    product = json.loads(product_path.read_text(encoding="utf-8"))
    events = product.get("events")
    if not isinstance(events, list) or not events:
        raise SystemExit("candidate product contains no events")

    by_key: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for raw in events:
        if not isinstance(raw, Mapping):
            raise SystemExit("candidate product contains a non-object event")
        by_key[_event_key(raw)].append(dict(raw))

    multi_note_attacks = 0
    rendered_secondary_count = 0
    harmonic_secondary_count = 0
    nonharmonic_secondary_count = 0
    promoted_primary_attack_count = 0
    promoted_primary_with_strongest_rendered_count = 0
    promoted_primary_with_harmonic_strongest_rendered_count = 0
    promoted_primary_strongest_interval_histogram: Counter[int] = Counter()
    max_chord_size = 0
    chord_size_histogram: Counter[int] = Counter()
    secondary_score_ratios: list[float] = []
    secondary_attack_ratios: list[float] = []
    secondary_body_ratios: list[float] = []
    harmonic_secondary_score_ratios: list[float] = []
    harmonic_secondary_attack_ratios: list[float] = []
    harmonic_secondary_body_ratios: list[float] = []
    nonharmonic_secondary_score_ratios: list[float] = []
    pitch_support_indistinguishable_attacks = 0
    multi_hypothesis_attack_count = 0
    rendered_harmonic_interval_histogram: Counter[int] = Counter()
    rendered_secondary_interval_histogram: Counter[int] = Counter()
    bad_groups: list[str] = []

    for key, group in sorted(by_key.items()):
        chord_size = len(group)
        max_chord_size = max(max_chord_size, chord_size)
        chord_size_histogram[chord_size] += 1
        if chord_size > 1:
            multi_note_attacks += 1

        primaries = {int(event.get("dominantMidi")) for event in group}
        if len(primaries) != 1:
            bad_groups.append(f"{key}: inconsistent dominantMidi")
            continue
        primary = next(iter(primaries))

        hypotheses_raw = group[0].get("pitchHypotheses")
        hypotheses = hypotheses_raw if isinstance(hypotheses_raw, list) else []
        hypothesis_map: dict[int, Mapping[str, Any]] = {}
        for item in hypotheses:
            if isinstance(item, Mapping) and item.get("midi") is not None:
                hypothesis_map[int(item["midi"])] = item

        for other in group[1:]:
            if other.get("pitchHypotheses") != hypotheses_raw:
                bad_groups.append(f"{key}: pitchHypotheses differ across rendered notes")
                break

        if len(hypothesis_map) > 1:
            multi_hypothesis_attack_count += 1
            support_tuples = {
                (
                    int(item.get("stemSupport") or 0),
                    int(item.get("sweepSupport") or 0),
                    int(item.get("detectionCount") or 0),
                )
                for item in hypothesis_map.values()
            }
            if len(support_tuples) == 1:
                pitch_support_indistinguishable_attacks += 1

        evidence_values = list(hypothesis_map.values())
        strongest_score = max((_finite(item.get("physicalScore"), -99.0) for item in evidence_values), default=-99.0)
        strongest_attack = max((_finite(item.get("physicalAttack"), -99.0) for item in evidence_values), default=-99.0)
        strongest_body = max((_finite(item.get("physicalBody"), -99.0) for item in evidence_values), default=-99.0)
        strongest_midi = None
        if hypothesis_map:
            strongest_midi = max(
                hypothesis_map,
                key=lambda midi: (
                    _finite(hypothesis_map[midi].get("physicalScore"), -99.0),
                    _finite(hypothesis_map[midi].get("physicalAttack"), -99.0),
                    -int(midi),
                ),
            )

        rendered_midis = {int(event["midi"]) for event in group}
        if primary not in rendered_midis:
            bad_groups.append(f"{key}: primary not rendered")

        if strongest_midi is not None and int(primary) != int(strongest_midi):
            promoted_primary_attack_count += 1
            interval = int(strongest_midi) - int(primary)
            promoted_primary_strongest_interval_histogram[interval] += 1
            if int(strongest_midi) in rendered_midis:
                promoted_primary_with_strongest_rendered_count += 1
                if interval in HARMONIC_INTERVALS:
                    promoted_primary_with_harmonic_strongest_rendered_count += 1

        for midi in sorted(rendered_midis - {primary}):
            rendered_secondary_count += 1
            interval = int(midi) - int(primary)
            rendered_secondary_interval_histogram[interval] += 1
            is_harmonic = interval in HARMONIC_INTERVALS
            if is_harmonic:
                harmonic_secondary_count += 1
                rendered_harmonic_interval_histogram[interval] += 1
            else:
                nonharmonic_secondary_count += 1

            item = hypothesis_map.get(midi)
            if item is None:
                bad_groups.append(f"{key}: rendered secondary {midi} missing pitch hypothesis")
                continue
            score_ratio = _ratio(_finite(item.get("physicalScore")), strongest_score)
            attack_ratio = _ratio(_finite(item.get("physicalAttack")), strongest_attack)
            body_ratio = _ratio(_finite(item.get("physicalBody")), strongest_body)
            secondary_score_ratios.append(score_ratio)
            secondary_attack_ratios.append(attack_ratio)
            secondary_body_ratios.append(body_ratio)
            if is_harmonic:
                harmonic_secondary_score_ratios.append(score_ratio)
                harmonic_secondary_attack_ratios.append(attack_ratio)
                harmonic_secondary_body_ratios.append(body_ratio)
            else:
                nonharmonic_secondary_score_ratios.append(score_ratio)

    selected_count = int(product.get("selectedCount") or 0)
    note_count = int(product.get("noteCount") or len(events))
    attack_count = len(by_key)
    precision_diagnostics = product.get("precisionDiagnostics") if isinstance(product.get("precisionDiagnostics"), Mapping) else {}
    fundamental_promotions_metadata = int(precision_diagnostics.get("fundamentalPromotionCount") or 0)
    synthetic = _synthetic_harmonic_promotion_double_count()
    protected_blob = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        cwd=ROOT,
        text=True,
    ).strip()

    report = {
        "schemaVersion": 2,
        "gate": "v143-precision-polyphonic-expansion-audio-only-audit",
        "candidateProductSha256": _sha256(product_path),
        "selectedCountMetadata": selected_count,
        "uniqueRenderedAttackCount": attack_count,
        "renderedNoteCount": note_count,
        "renderedExpansionNoteCount": note_count - attack_count,
        "multiNoteAttackCount": multi_note_attacks,
        "maxChordSize": max_chord_size,
        "chordSizeHistogram": {str(key): value for key, value in sorted(chord_size_histogram.items())},
        "renderedSecondaryCount": rendered_secondary_count,
        "harmonicSecondaryCount": harmonic_secondary_count,
        "nonharmonicSecondaryCount": nonharmonic_secondary_count,
        "harmonicSecondaryFraction": _ratio(harmonic_secondary_count, rendered_secondary_count) if rendered_secondary_count else 0.0,
        "renderedSecondaryIntervalHistogram": {str(key): value for key, value in sorted(rendered_secondary_interval_histogram.items())},
        "renderedHarmonicIntervalHistogram": {str(key): value for key, value in sorted(rendered_harmonic_interval_histogram.items())},
        "fundamentalPromotionCountMetadata": fundamental_promotions_metadata,
        "promotedPrimaryAttackCountFromSerializedEvidence": promoted_primary_attack_count,
        "promotedPrimaryWithStrongestRenderedCount": promoted_primary_with_strongest_rendered_count,
        "promotedPrimaryWithHarmonicStrongestRenderedCount": promoted_primary_with_harmonic_strongest_rendered_count,
        "promotedPrimaryStrongestIntervalHistogram": {str(key): value for key, value in sorted(promoted_primary_strongest_interval_histogram.items())},
        "promotionStrongestRetentionFraction": _ratio(promoted_primary_with_strongest_rendered_count, promoted_primary_attack_count) if promoted_primary_attack_count else 0.0,
        "promotionHarmonicStrongestRetentionFraction": _ratio(promoted_primary_with_harmonic_strongest_rendered_count, promoted_primary_attack_count) if promoted_primary_attack_count else 0.0,
        "secondaryScoreRatioQuantiles": _quantiles(secondary_score_ratios),
        "secondaryAttackRatioQuantiles": _quantiles(secondary_attack_ratios),
        "secondaryBodyRatioQuantiles": _quantiles(secondary_body_ratios),
        "harmonicSecondaryScoreRatioQuantiles": _quantiles(harmonic_secondary_score_ratios),
        "harmonicSecondaryAttackRatioQuantiles": _quantiles(harmonic_secondary_attack_ratios),
        "harmonicSecondaryBodyRatioQuantiles": _quantiles(harmonic_secondary_body_ratios),
        "nonharmonicSecondaryScoreRatioQuantiles": _quantiles(nonharmonic_secondary_score_ratios),
        "multiHypothesisAttackCount": multi_hypothesis_attack_count,
        "pitchSupportIndistinguishableAttackCount": pitch_support_indistinguishable_attacks,
        "pitchSupportIndistinguishableFraction": _ratio(pitch_support_indistinguishable_attacks, multi_hypothesis_attack_count) if multi_hypothesis_attack_count else 0.0,
        "perPitchBasicPitchSupportRecoverableFromSerializedHypotheses": pitch_support_indistinguishable_attacks < multi_hypothesis_attack_count,
        **synthetic,
        "harmonicPromotionDoubleCountPathProven": synthetic["syntheticStrongestHarmonicRetainedAsSecondary"],
        "badGroupCount": len(bad_groups),
        "badGroupExamples": bad_groups[:20],
        "selectedCountMatchesUniqueRenderedAttacks": selected_count == attack_count,
        "noteCountMatchesEvents": note_count == len(events),
        "protectedPipelineBlob": protected_blob,
        "expectedProtectedPipelineBlob": EXPECTED_PROTECTED_BLOB,
        "protectedPipelineUnchanged": protected_blob == EXPECTED_PROTECTED_BLOB,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "modalGpuUsed": False,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if bad_groups:
        raise SystemExit(f"polyphonic expansion audit found malformed groups: {bad_groups[:5]}")
    if not report["selectedCountMatchesUniqueRenderedAttacks"]:
        raise SystemExit("selected attack count does not match unique rendered attack count")
    if not report["noteCountMatchesEvents"]:
        raise SystemExit("note count metadata does not match events")
    if not report["harmonicPromotionDoubleCountPathProven"]:
        raise SystemExit("synthetic harmonic promotion double-count path was not reproduced")
    if not report["protectedPipelineUnchanged"]:
        raise SystemExit("protected rhythm pipeline changed")

    print("V143 precision polyphonic expansion audio-only audit complete")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
