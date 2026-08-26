from __future__ import annotations

import sys
import unittest
from pathlib import Path

MODAL_ROOT = Path(__file__).resolve().parents[1]
if str(MODAL_ROOT) not in sys.path:
    sys.path.insert(0, str(MODAL_ROOT))

from v144_rhythm_context_split_policy import (  # noqa: E402
    ContextSplitConfig,
    context_signature,
    evaluate_candidate_pair,
    split_for_location,
)


class ContextSplitPolicyTests(unittest.TestCase):
    def test_split_is_deterministic_and_covers_all_three_buckets(self) -> None:
        first = [split_for_location(m, s) for m in range(1, 114) for s in range(16)]
        second = [split_for_location(m, s) for m in range(1, 114) for s in range(16)]
        self.assertEqual(first, second)
        self.assertEqual(set(first), {"fit", "validation", "canary"})

    def test_context_signature_ignores_label_like_fields(self) -> None:
        clean = {"measure": 17, "step": 6, "midi": 52}
        leaked = {
            **clean,
            "truth": "professional-reference-match",
            "professionalReferenceLabel": 1,
            "holdoutAnswer": "do-not-use",
        }
        self.assertEqual(context_signature(clean), context_signature(leaked))

    def test_candidate_requires_pitch_gain_without_metric_regression(self) -> None:
        config = ContextSplitConfig()
        baseline = {
            "gatedMetrics": {
                "pitchContentF1": 0.28,
                "pitchTimingTolerantF1": 0.04,
                "stringFretTimingTolerantF1": 0.03,
                "chordPitchSetTolerantF1": 0.02,
                "exactVoicingTolerantF1": 0.02,
                "pdfEventFidelity": 1.0,
            },
            "criticalMismatchCount": 100,
        }
        improved = {
            "gatedMetrics": {
                "pitchContentF1": 0.29,
                "pitchTimingTolerantF1": 0.041,
                "stringFretTimingTolerantF1": 0.031,
                "chordPitchSetTolerantF1": 0.021,
                "exactVoicingTolerantF1": 0.021,
                "pdfEventFidelity": 1.0,
            },
            "criticalMismatchCount": 95,
        }
        result = evaluate_candidate_pair(baseline, improved, config=config)
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["pitchContentGain"], 0.005)

    def test_pdf_fidelity_regression_is_rejected(self) -> None:
        config = ContextSplitConfig()
        baseline = {
            "gatedMetrics": {
                "pitchContentF1": 0.28,
                "pitchTimingTolerantF1": 0.04,
                "stringFretTimingTolerantF1": 0.03,
                "chordPitchSetTolerantF1": 0.02,
                "exactVoicingTolerantF1": 0.02,
                "pdfEventFidelity": 1.0,
            },
            "criticalMismatchCount": 100,
        }
        candidate = {
            "gatedMetrics": {
                "pitchContentF1": 0.30,
                "pitchTimingTolerantF1": 0.05,
                "stringFretTimingTolerantF1": 0.04,
                "chordPitchSetTolerantF1": 0.03,
                "exactVoicingTolerantF1": 0.03,
                "pdfEventFidelity": 0.999,
            },
            "criticalMismatchCount": 90,
        }
        result = evaluate_candidate_pair(baseline, candidate, config=config)
        self.assertFalse(result["passed"])
        self.assertIn("pdf-event-fidelity-not-exact", result["reasons"])


if __name__ == "__main__":
    unittest.main()
