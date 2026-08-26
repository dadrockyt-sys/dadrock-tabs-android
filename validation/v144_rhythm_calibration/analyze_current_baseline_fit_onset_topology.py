from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_pitch_position_shift_policy import apply_pitch_position_rule  # noqa: E402
from v144_rhythm_pitch_shift_policy import apply_pitch_shift_rule  # noqa: E402
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from analyze_split_baseline import split_name  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
TRIPLE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
TRIPLE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
PITCH_SIGNATURES = ["pitchClass::4", "stepQuarter::0"]
PITCH_SHIFT = -2
PITCH_EVENT_SHA256 = "b6e1f8a8be150943d7224c74f9193b1b4050454620063846f6f5f5c773d4cbf6"
BASELINE_NAME = "pitch-position-shift-54a6e8d3aa91c422"
POSITION_SIGNATURES = ["pitchClass::11", "stepParity::0"]
POSITION_PITCH_SHIFT = -2
POSITION_STRING_SHIFT = 1
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "5b36270aaeafa73b2e25722e2576a40424ce5951dcfd2b5d769746bd9eb07e0d"
BASELINE_MEASURE_COUNT = 113


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _group_onsets(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(dict(row))
    return grouped


def _wrong_pitch_slots(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> int:
    generated_pitch = Counter(int(row["midi"]) for row in generated)
    reference_pitch = Counter(int(row["midi"]) for row in reference)
    exact = generated_pitch & reference_pitch
    generated_remaining = sum(generated_pitch.values()) - sum(exact.values())
    reference_remaining = sum(reference_pitch.values()) - sum(exact.values())
    return min(generated_remaining, reference_remaining)


def _same_string_wrong_pitch_slots(
    generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]
) -> int:
    generated_by_string: dict[int, Counter[int]] = defaultdict(Counter)
    reference_by_string: dict[int, Counter[int]] = defaultdict(Counter)
    for row in generated:
        generated_by_string[int(row["stringIndex"])][int(row["midi"])] += 1
    for row in reference:
        reference_by_string[int(row["stringIndex"])][int(row["midi"])] += 1
    slots = 0
    for string_index in sorted(set(generated_by_string) | set(reference_by_string)):
        g = generated_by_string[string_index]
        r = reference_by_string[string_index]
        exact = g & r
        g_remaining = sum(g.values()) - sum(exact.values())
        r_remaining = sum(r.values()) - sum(exact.values())
        slots += min(g_remaining, r_remaining)
    return slots


def analyze_onset_topology(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    generated_by_onset = _group_onsets(generated_notes)
    reference_by_onset = _group_onsets(reference_notes)
    all_onsets = sorted(set(generated_by_onset) | set(reference_by_onset))

    cardinality_pairs: Counter[str] = Counter()
    topology = Counter()
    wrong_pitch_slots_by_pair: Counter[str] = Counter()
    same_string_wrong_slots_by_pair: Counter[str] = Counter()

    for onset in all_onsets:
        generated = generated_by_onset.get(onset, [])
        reference = reference_by_onset.get(onset, [])
        g_count = len(generated)
        r_count = len(reference)
        pair_key = f"g{g_count}-r{r_count}"
        cardinality_pairs[pair_key] += 1

        if g_count == 0:
            topology["referenceOnlyOnsets"] += 1
            continue
        if r_count == 0:
            topology["generatedOnlyOnsets"] += 1
            continue
        topology["sharedOnsets"] += 1

        generated_pitches = Counter(int(row["midi"]) for row in generated)
        reference_pitches = Counter(int(row["midi"]) for row in reference)
        generated_strings = Counter(int(row["stringIndex"]) for row in generated)
        reference_strings = Counter(int(row["stringIndex"]) for row in reference)
        generated_positions = Counter((int(row["stringIndex"]), int(row["fret"])) for row in generated)
        reference_positions = Counter((int(row["stringIndex"]), int(row["fret"])) for row in reference)

        exact_pitch = generated_pitches == reference_pitches
        exact_strings = generated_strings == reference_strings
        exact_positions = generated_positions == reference_positions
        if exact_pitch:
            topology["exactPitchMultisetOnsets"] += 1
        if exact_strings:
            topology["exactStringMultisetOnsets"] += 1
        if exact_positions:
            topology["exactStringFretMultisetOnsets"] += 1
        if exact_pitch and exact_strings:
            topology["exactPitchAndStringMultisetOnsets"] += 1

        wrong_slots = _wrong_pitch_slots(generated, reference)
        same_string_wrong_slots = _same_string_wrong_pitch_slots(generated, reference)
        wrong_pitch_slots_by_pair[pair_key] += wrong_slots
        same_string_wrong_slots_by_pair[pair_key] += same_string_wrong_slots
        topology["sameOnsetWrongPitchSubstitutionSlots"] += wrong_slots
        topology["sameStringWrongPitchSubstitutionSlots"] += same_string_wrong_slots

        if g_count == 1 and r_count == 1:
            topology["singletonToSingletonOnsets"] += 1
            same_string = int(generated[0]["stringIndex"]) == int(reference[0]["stringIndex"])
            same_pitch = int(generated[0]["midi"]) == int(reference[0]["midi"])
            if same_string and same_pitch:
                topology["singletonExactPitchSameStringOnsets"] += 1
            elif same_string:
                topology["singletonWrongPitchSameStringOnsets"] += 1
            elif same_pitch:
                topology["singletonExactPitchDifferentStringOnsets"] += 1
            else:
                topology["singletonWrongPitchDifferentStringOnsets"] += 1

        if g_count == r_count and g_count >= 2:
            topology["equalCardinalityMultiNoteOnsets"] += 1
            if exact_strings:
                topology["equalCardinalityMultiNoteSameStringSetOnsets"] += 1
                if not exact_pitch:
                    topology["equalCardinalityMultiNoteSameStringSetWrongPitchOnsets"] += 1
            else:
                topology["equalCardinalityMultiNoteDifferentStringSetOnsets"] += 1
            if g_count == 2:
                topology["dyadToDyadOnsets"] += 1
                if exact_strings:
                    topology["dyadSameStringSetOnsets"] += 1
                    if not exact_pitch:
                        topology["dyadSameStringSetWrongPitchOnsets"] += 1
            if g_count >= 3:
                topology["threePlusEqualCardinalityOnsets"] += 1
                if exact_strings:
                    topology["threePlusSameStringSetOnsets"] += 1
                    if not exact_pitch:
                        topology["threePlusSameStringSetWrongPitchOnsets"] += 1

        if g_count != r_count:
            topology["sharedCardinalityMismatchOnsets"] += 1
            if g_count > r_count:
                topology["sharedGeneratedHeavierOnsets"] += 1
            else:
                topology["sharedReferenceHeavierOnsets"] += 1

    topology["generatedOnsetCount"] = len(generated_by_onset)
    topology["referenceOnsetCount"] = len(reference_by_onset)
    topology["unionOnsetCount"] = len(all_onsets)

    return {
        "cardinalityPairs": dict(sorted(cardinality_pairs.items())),
        "wrongPitchSlotsByCardinalityPair": dict(sorted(wrong_pitch_slots_by_pair.items())),
        "sameStringWrongPitchSlotsByCardinalityPair": dict(sorted(same_string_wrong_slots_by_pair.items())),
        "topology": dict(sorted(topology.items())),
    }


def reconstruct_current_baseline(source_events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    triple = canonical_events(apply_triple_prune(source_events, TRIPLE_SIGNATURES))
    if len(triple) != BASELINE_EVENT_COUNT or sha256_json(triple) != TRIPLE_EVENT_SHA256:
        raise ValueError("historical triple reconstruction changed")
    pitch = canonical_events(apply_pitch_shift_rule(triple, PITCH_SIGNATURES, PITCH_SHIFT))
    if len(pitch) != BASELINE_EVENT_COUNT or sha256_json(pitch) != PITCH_EVENT_SHA256:
        raise ValueError("historical pitch reconstruction changed")
    baseline = canonical_events(
        apply_pitch_position_rule(
            pitch,
            POSITION_SIGNATURES,
            POSITION_PITCH_SHIFT,
            POSITION_STRING_SHIFT,
            maximum_abs_string_shift=1,
        )
    )
    if len(baseline) != BASELINE_EVENT_COUNT or sha256_json(baseline) != BASELINE_EVENT_SHA256:
        raise ValueError("current accepted baseline reconstruction changed")
    return baseline


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnostic-only fit onset topology analysis for the current accepted V144 Rhythm baseline."
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("accepted_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.accepted_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("accepted manifest classification changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("accepted baseline name changed")
    selected = manifest.get("selectedCandidate") or {}
    if int(selected.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("accepted baseline event count changed")
    if selected.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("accepted baseline event SHA changed")
    if int(selected.get("generatedMeasureCount") or 0) != BASELINE_MEASURE_COUNT:
        raise ValueError("accepted baseline measure count changed")
    promotion = manifest.get("promotionScope") or {}
    if promotion.get("calibrationBaseline") is not True or promotion.get("productionPromotionAllowed") is not False:
        raise ValueError("accepted baseline promotion scope changed")

    v5_stream = load_json(args.v5_render_stream)
    source_events = canonical_events(v5_stream.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT or sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event identity changed")
    baseline_events = reconstruct_current_baseline(source_events)

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(baseline_events)
    fit_generated = [row for row in generated_notes if split_name(row, config) == "fit"]
    fit_reference = [row for row in reference_notes if split_name(row, config) == "fit"]

    topology = analyze_onset_topology(fit_generated, fit_reference)
    report = {
        "schemaVersion": 14419,
        "classification": "v144-rhythm-current-baseline-fit-onset-topology",
        "evaluationRole": "gold-calibration-fit-only-current-baseline-topology-diagnostic",
        "mayClaimUnseenGeneralization": False,
        "candidateConstructionPerformed": False,
        "candidateRankingPerformed": False,
        "candidateSelectionPerformed": False,
        "candidateRuleOrShiftHistogramEmitted": False,
        "validationLabelsUsedForDiagnostic": False,
        "canaryLabelsUsedForDiagnostic": False,
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "generatedMeasureCount": BASELINE_MEASURE_COUNT,
        },
        "fit": {
            "generatedNoteCount": len(fit_generated),
            "referenceNoteCount": len(fit_reference),
            **topology,
        },
        "interpretationBoundary": {
            "topologyOnly": True,
            "mayInformMateriallyDistinctFamilyUnit": True,
            "mayRankSpecificRuleOrShift": False,
            "validationMayInformFamilyShape": False,
            "canaryMayInformFamilyShape": False,
            "consumedFamilyResultsMayInformFamilyShape": False,
            "fixedSelectorThresholdsMayChange": False,
            "runtimeReferenceInputAllowed": False,
        },
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
