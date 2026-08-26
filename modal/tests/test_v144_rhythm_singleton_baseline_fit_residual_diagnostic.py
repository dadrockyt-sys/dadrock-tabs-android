from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(SEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(SEARCH_DIR))

from analyze_singleton_baseline_fit_residuals import (  # noqa: E402
    BASELINE_CHANGED_EVENT_COUNT,
    BASELINE_EVENT_COUNT,
    BASELINE_EVENT_SHA256,
    BASELINE_MEASURE_COUNT,
    BASELINE_NAME,
    CONTEXT_SIGNATURE,
    SEMITONE_SHIFT,
    SOURCE_PITCH_CLASS,
    SOURCE_STRING_INDEX,
    TARGET_STRING_INDEX,
    _validate_manifest,
    analyze_fit_residuals,
    diagnostic_contract,
)


def note(
    *,
    measure: int,
    step: int,
    midi: int,
    string_index: int,
    fret: int,
) -> dict:
    return {
        "measure": measure,
        "step": step,
        "midi": midi,
        "stringIndex": string_index,
        "fret": fret,
        "durationSteps": 1,
        "techniques": [],
    }


def valid_manifest() -> dict:
    return {
        "classification": "v144-rhythm-selected-calibration-baseline",
        "status": "accepted-calibration-baseline-not-production",
        "name": BASELINE_NAME,
        "transform": {
            "contextSignature": CONTEXT_SIGNATURE,
            "sourceStringIndex": SOURCE_STRING_INDEX,
            "sourcePitchClass": SOURCE_PITCH_CLASS,
            "targetStringIndex": TARGET_STRING_INDEX,
            "semitoneShift": SEMITONE_SHIFT,
            "changedEventCount": BASELINE_CHANGED_EVENT_COUNT,
            "professionalReferenceRuntimeInput": False,
        },
        "selectedCandidate": {
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "pdfEventSha256": BASELINE_EVENT_SHA256,
            "pdfEventFidelity": 1.0,
            "generatedMeasureCount": BASELINE_MEASURE_COUNT,
        },
        "promotionScope": {
            "calibrationBaseline": True,
            "productionPromotionAllowed": False,
            "mayClaimUnseenGeneralization": False,
        },
    }


class SingletonBaselineFitResidualDiagnosticTests(unittest.TestCase):
    def test_analysis_is_deterministic_under_input_reversal(self) -> None:
        generated = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=4, midi=60, string_index=1, fret=1),
            note(measure=2, step=4, midi=64, string_index=0, fret=0),
        ]
        reference = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=4, midi=62, string_index=1, fret=3),
        ]
        forward = analyze_fit_residuals(generated, reference)
        reverse = analyze_fit_residuals(list(reversed(generated)), list(reversed(reference)))
        self.assertEqual(forward, reverse)

    def test_shared_singletons_and_cardinality_mismatch_are_aggregate(self) -> None:
        generated = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=0, midi=64, string_index=0, fret=0),
            note(measure=3, step=0, midi=60, string_index=1, fret=1),
            note(measure=3, step=0, midi=64, string_index=0, fret=0),
            note(measure=4, step=0, midi=67, string_index=1, fret=8),
        ]
        reference = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=0, midi=52, string_index=3, fret=2),
            note(measure=3, step=0, midi=60, string_index=1, fret=1),
            note(measure=5, step=0, midi=69, string_index=0, fret=5),
        ]
        report = analyze_fit_residuals(generated, reference)
        topology = report["topology"]
        self.assertEqual(topology["singletonToSingletonOnsets"], 2)
        self.assertEqual(topology["singletonExactPitchSameStringOnsets"], 1)
        self.assertEqual(topology["singletonWrongPitchDifferentStringOnsets"], 1)
        self.assertEqual(topology["sharedCardinalityMismatchOnsets"], 1)
        self.assertEqual(topology["sharedGeneratedHeavierOnsets"], 1)
        self.assertEqual(topology["generatedOnlyOnsets"], 1)
        self.assertEqual(topology["referenceOnlyOnsets"], 1)
        self.assertEqual(report["cardinalityPairs"]["g1-r1"], 2)
        self.assertEqual(report["cardinalityPairs"]["g2-r1"], 1)
        self.assertEqual(report["cardinalityPairs"]["g1-r0"], 1)
        self.assertEqual(report["cardinalityPairs"]["g0-r1"], 1)

    def test_mechanism_counts_remain_descriptive_and_position_aware(self) -> None:
        generated = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=0, midi=60, string_index=1, fret=1),
            note(measure=3, step=0, midi=67, string_index=1, fret=8),
        ]
        reference = [
            note(measure=1, step=0, midi=64, string_index=0, fret=0),
            note(measure=2, step=0, midi=62, string_index=1, fret=3),
            note(measure=3, step=0, midi=67, string_index=2, fret=12),
        ]
        report = analyze_fit_residuals(generated, reference)
        mechanisms = report["mechanisms"]
        self.assertEqual(report["generatedNoteCount"], 3)
        self.assertEqual(report["referenceNoteCount"], 3)
        self.assertEqual(mechanisms["sameOnsetWrongPitchSubstitutionSlots"], 1)
        self.assertGreaterEqual(mechanisms["correctPitchTimingButWrongStringFret"], 1)
        self.assertGreaterEqual(report["pitchContentMatchedNotes"], 2)
        self.assertGreaterEqual(report["tightPitchTimingMatchedNotes"], 2)
        self.assertEqual(report["exactStringFretTimingMatchedNotes"], 1)

    def test_contract_forbids_candidate_and_later_stage_surfaces(self) -> None:
        contract = diagnostic_contract()
        self.assertFalse(contract["candidateConstructionPerformed"])
        self.assertFalse(contract["candidateRankingPerformed"])
        self.assertFalse(contract["candidateSelectionPerformed"])
        self.assertFalse(contract["candidateRuleOrShiftHistogramEmitted"])
        self.assertFalse(contract["validationLabelsUsedForDiagnostic"])
        self.assertFalse(contract["canaryLabelsUsedForDiagnostic"])
        boundary = contract["interpretationBoundary"]
        self.assertTrue(boundary["aggregateFitResidualsOnly"])
        self.assertTrue(boundary["mayInformMateriallyDistinctFamilyUnit"])
        self.assertFalse(boundary["mayRankSpecificRuleOrShift"])
        self.assertFalse(boundary["validationMayInformFamilyShape"])
        self.assertFalse(boundary["canaryMayInformFamilyShape"])
        self.assertFalse(boundary["consumedFamilyResultsMayInformFamilyShape"])
        self.assertFalse(boundary["fixedSelectorThresholdsMayChange"])
        self.assertFalse(boundary["runtimeReferenceInputAllowed"])

    def test_aggregate_result_contains_no_specific_rule_or_shift_fields(self) -> None:
        generated = [note(measure=1, step=0, midi=64, string_index=0, fret=0)]
        reference = [note(measure=1, step=0, midi=52, string_index=3, fret=2)]
        report = analyze_fit_residuals(generated, reference)
        serialized_keys = repr(report)
        for forbidden in (
            "contextSignature",
            "sourceStringIndex",
            "sourcePitchClass",
            "targetStringIndex",
            "semitoneShift",
            "candidateName",
        ):
            self.assertNotIn(forbidden, serialized_keys)

    def test_manifest_validator_locks_identity_and_calibration_only_scope(self) -> None:
        manifest = valid_manifest()
        _validate_manifest(manifest)

        mutations = [
            ("name", "wrong"),
            ("status", "production"),
        ]
        for key, value in mutations:
            changed = valid_manifest()
            changed[key] = value
            with self.assertRaises(ValueError):
                _validate_manifest(changed)

        changed = valid_manifest()
        changed["selectedCandidate"]["eventSha256"] = "0" * 64
        with self.assertRaises(ValueError):
            _validate_manifest(changed)

        changed = valid_manifest()
        changed["promotionScope"]["productionPromotionAllowed"] = True
        with self.assertRaises(ValueError):
            _validate_manifest(changed)

        changed = valid_manifest()
        changed["promotionScope"]["mayClaimUnseenGeneralization"] = True
        with self.assertRaises(ValueError):
            _validate_manifest(changed)


if __name__ == "__main__":
    unittest.main()
