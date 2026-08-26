from __future__ import annotations

from pathlib import Path
import sys
import unittest

# Synthetic-only gate coverage: importing the diagnostic does not read calibration labels.
ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(DIAGNOSTIC_DIR) not in sys.path:
    sys.path.insert(0, str(DIAGNOSTIC_DIR))

from analyze_current_baseline_fit_onset_topology import analyze_onset_topology  # noqa: E402


def note(
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
    }


class CurrentBaselineFitOnsetTopologyTests(unittest.TestCase):
    def test_singletons_classify_same_and_different_string_pitch_cases(self) -> None:
        generated = [
            note(1, 0, 60, 1, 1),
            note(1, 1, 61, 1, 2),
            note(1, 2, 62, 1, 3),
            note(1, 3, 63, 1, 4),
        ]
        reference = [
            note(1, 0, 60, 1, 1),
            note(1, 1, 63, 1, 4),
            note(1, 2, 62, 2, 7),
            note(1, 3, 65, 2, 10),
        ]
        result = analyze_onset_topology(generated, reference)
        topology = result["topology"]
        self.assertEqual(topology["singletonToSingletonOnsets"], 4)
        self.assertEqual(topology["singletonExactPitchSameStringOnsets"], 1)
        self.assertEqual(topology["singletonWrongPitchSameStringOnsets"], 1)
        self.assertEqual(topology["singletonExactPitchDifferentStringOnsets"], 1)
        self.assertEqual(topology["singletonWrongPitchDifferentStringOnsets"], 1)

    def test_dyad_same_string_set_wrong_pitch_counts_slots(self) -> None:
        generated = [
            note(2, 0, 60, 1, 1),
            note(2, 0, 64, 2, 9),
        ]
        reference = [
            note(2, 0, 62, 1, 3),
            note(2, 0, 65, 2, 10),
        ]
        result = analyze_onset_topology(generated, reference)
        topology = result["topology"]
        self.assertEqual(topology["dyadToDyadOnsets"], 1)
        self.assertEqual(topology["dyadSameStringSetOnsets"], 1)
        self.assertEqual(topology["dyadSameStringSetWrongPitchOnsets"], 1)
        self.assertEqual(topology["sameOnsetWrongPitchSubstitutionSlots"], 2)
        self.assertEqual(topology["sameStringWrongPitchSubstitutionSlots"], 2)
        self.assertEqual(result["wrongPitchSlotsByCardinalityPair"]["g2-r2"], 2)
        self.assertEqual(result["sameStringWrongPitchSlotsByCardinalityPair"]["g2-r2"], 2)

    def test_three_plus_and_cardinality_mismatch_are_counted_without_ranking(self) -> None:
        generated = [
            note(3, 0, 60, 1, 1),
            note(3, 0, 64, 2, 9),
            note(3, 0, 67, 3, 17),
            note(3, 1, 60, 1, 1),
            note(3, 1, 64, 2, 9),
        ]
        reference = [
            note(3, 0, 61, 1, 2),
            note(3, 0, 65, 2, 10),
            note(3, 0, 68, 3, 18),
            note(3, 1, 60, 1, 1),
        ]
        result = analyze_onset_topology(generated, reference)
        topology = result["topology"]
        self.assertEqual(topology["threePlusEqualCardinalityOnsets"], 1)
        self.assertEqual(topology["threePlusSameStringSetOnsets"], 1)
        self.assertEqual(topology["threePlusSameStringSetWrongPitchOnsets"], 1)
        self.assertEqual(topology["sharedCardinalityMismatchOnsets"], 1)
        self.assertEqual(topology["sharedGeneratedHeavierOnsets"], 1)
        self.assertNotIn("candidate", result)
        self.assertNotIn("ranking", result)

    def test_generated_only_reference_only_and_cardinality_pairs_are_explicit(self) -> None:
        generated = [
            note(4, 0, 60, 1, 1),
            note(4, 2, 62, 1, 3),
        ]
        reference = [
            note(4, 0, 60, 1, 1),
            note(4, 1, 64, 2, 9),
        ]
        result = analyze_onset_topology(generated, reference)
        self.assertEqual(result["cardinalityPairs"], {"g0-r1": 1, "g1-r0": 1, "g1-r1": 1})
        topology = result["topology"]
        self.assertEqual(topology["generatedOnlyOnsets"], 1)
        self.assertEqual(topology["referenceOnlyOnsets"], 1)
        self.assertEqual(topology["sharedOnsets"], 1)
        self.assertEqual(topology["unionOnsetCount"], 3)

    def test_analysis_is_deterministic_under_input_reversal(self) -> None:
        generated = [
            note(5, 0, 60, 1, 1),
            note(5, 0, 64, 2, 9),
            note(5, 1, 67, 3, 17),
        ]
        reference = [
            note(5, 0, 62, 1, 3),
            note(5, 0, 65, 2, 10),
            note(5, 1, 67, 3, 17),
        ]
        forward = analyze_onset_topology(generated, reference)
        reverse = analyze_onset_topology(list(reversed(generated)), list(reversed(reference)))
        self.assertEqual(forward, reverse)


if __name__ == "__main__":
    unittest.main()
    # Manual Actions retrigger
