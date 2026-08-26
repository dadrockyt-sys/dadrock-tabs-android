from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTIC_DIR = ROOT / "validation" / "v144_rhythm_calibration"
if str(DIAGNOSTIC_DIR) not in sys.path:
    sys.path.insert(0, str(DIAGNOSTIC_DIR))

from analyze_current_baseline_fit_mechanisms import (  # noqa: E402
    BASELINE_EVENT_COUNT,
    BASELINE_EVENT_SHA256,
    SOURCE_EVENT_COUNT,
    SOURCE_EVENT_SHA256,
    canonical_events,
    f1_from_matched,
    reconstruct_current_baseline,
    same_onset_pitch_mechanisms,
    sha256_json,
)


class CurrentBaselineFitMechanismTests(unittest.TestCase):
    def test_reconstructs_new_locked_baseline_from_frozen_v5(self) -> None:
        source_path = ROOT / "debug" / "v143-contextual-prune" / "v5-professional-pdf" / "v5-render-stream.json"
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        source = canonical_events(payload.get("events") or [])
        self.assertEqual(len(source), SOURCE_EVENT_COUNT)
        self.assertEqual(sha256_json(source), SOURCE_EVENT_SHA256)
        baseline = reconstruct_current_baseline(source)
        self.assertEqual(len(baseline), BASELINE_EVENT_COUNT)
        self.assertEqual(sha256_json(baseline), BASELINE_EVENT_SHA256)

    def test_f1_from_matched_uses_fixed_generated_and_reference_counts(self) -> None:
        self.assertEqual(f1_from_matched(0, 0, 0), 1.0)
        self.assertAlmostEqual(f1_from_matched(3, 4, 5), 6.0 / 9.0)

    def test_same_onset_mechanisms_separate_exact_substitution_extra_and_missing(self) -> None:
        generated = [
            {"measure": 1, "step": 0, "midi": 60},
            {"measure": 1, "step": 0, "midi": 62},
            {"measure": 1, "step": 0, "midi": 64},
            {"measure": 2, "step": 4, "midi": 67},
        ]
        reference = [
            {"measure": 1, "step": 0, "midi": 60},
            {"measure": 1, "step": 0, "midi": 63},
            {"measure": 2, "step": 4, "midi": 69},
            {"measure": 3, "step": 0, "midi": 72},
        ]
        result = same_onset_pitch_mechanisms(generated, reference)
        self.assertEqual(result["exactOnsetExactPitchNotes"], 1)
        self.assertEqual(result["sameOnsetWrongPitchSubstitutionSlots"], 2)
        self.assertEqual(result["sameOnsetExtraGeneratedSlotsAfterSubstitution"], 1)
        self.assertEqual(result["sameOnsetMissingReferenceSlotsAfterSubstitution"], 1)

    def test_duplicate_pitch_multiset_exact_matching_is_count_aware(self) -> None:
        generated = [
            {"measure": 1, "step": 0, "midi": 60},
            {"measure": 1, "step": 0, "midi": 60},
        ]
        reference = [{"measure": 1, "step": 0, "midi": 60}]
        result = same_onset_pitch_mechanisms(generated, reference)
        self.assertEqual(result["exactOnsetExactPitchNotes"], 1)
        self.assertEqual(result["sameOnsetWrongPitchSubstitutionSlots"], 0)
        self.assertEqual(result["sameOnsetExtraGeneratedSlotsAfterSubstitution"], 1)
        self.assertEqual(result["sameOnsetMissingReferenceSlotsAfterSubstitution"], 0)


if __name__ == "__main__":
    unittest.main()
