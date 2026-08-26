from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(DIAGNOSTIC_DIR) not in sys.path:
    sys.path.insert(0, str(DIAGNOSTIC_DIR))

from analyze_fit_error_mechanisms import (  # noqa: E402
    f1_from_matched,
    same_onset_pitch_mechanisms,
)


class FitErrorMechanismDiagnosticTests(unittest.TestCase):
    def test_same_onset_pitch_mechanisms_are_multiset_safe(self) -> None:
        generated = [
            {"measure": 1, "step": 0, "midi": 60},
            {"measure": 1, "step": 0, "midi": 61},
            {"measure": 1, "step": 0, "midi": 62},
            {"measure": 2, "step": 4, "midi": 66},
        ]
        reference = [
            {"measure": 1, "step": 0, "midi": 60},
            {"measure": 1, "step": 0, "midi": 63},
            {"measure": 3, "step": 8, "midi": 65},
        ]
        self.assertEqual(
            same_onset_pitch_mechanisms(generated, reference),
            {
                "exactOnsetExactPitchNotes": 1,
                "sameOnsetWrongPitchSubstitutionSlots": 1,
                "sameOnsetExtraGeneratedSlotsAfterSubstitution": 2,
                "sameOnsetMissingReferenceSlotsAfterSubstitution": 1,
            },
        )

    def test_same_onset_mechanisms_handle_duplicate_pitches(self) -> None:
        generated = [
            {"measure": 4, "step": 12, "midi": 64},
            {"measure": 4, "step": 12, "midi": 64},
            {"measure": 4, "step": 12, "midi": 67},
        ]
        reference = [
            {"measure": 4, "step": 12, "midi": 64},
            {"measure": 4, "step": 12, "midi": 69},
            {"measure": 4, "step": 12, "midi": 69},
        ]
        result = same_onset_pitch_mechanisms(generated, reference)
        self.assertEqual(result["exactOnsetExactPitchNotes"], 1)
        self.assertEqual(result["sameOnsetWrongPitchSubstitutionSlots"], 2)
        self.assertEqual(result["sameOnsetExtraGeneratedSlotsAfterSubstitution"], 0)
        self.assertEqual(result["sameOnsetMissingReferenceSlotsAfterSubstitution"], 0)

    def test_f1_ceiling_helper(self) -> None:
        self.assertEqual(f1_from_matched(0, 0, 0), 1.0)
        self.assertAlmostEqual(f1_from_matched(2, 3, 4), 4.0 / 7.0)
        self.assertAlmostEqual(f1_from_matched(4, 4, 4), 1.0)


if __name__ == "__main__":
    unittest.main()
