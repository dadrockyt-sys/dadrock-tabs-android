import importlib.util
from pathlib import Path
import unittest

import numpy as np

PATH = Path(__file__).resolve().parents[1] / "guitartechs_training_v2" / "diagnostics.py"
SPEC = importlib.util.spec_from_file_location("guitartechs_v2_diagnostics", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def blank(frames=12):
    return np.full((6, frames), -1, dtype=np.int16)


class GuitarTechsV2DiagnosticsTests(unittest.TestCase):
    def test_perfect_exact_event_is_true_positive(self):
        ref = blank()
        ref[0, 2:5] = 3
        pred = ref.T.copy()
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["eventMicro"]["exactTruePositive"], 1)
        self.assertEqual(d["eventMicro"]["falsePositive"], 0)
        self.assertEqual(d["eventMicro"]["falseNegative"], 0)
        self.assertEqual(d["onsetLabelDecomposition"]["exactStringFret"], 1)

    def test_wrong_fret_same_string_is_separated_from_onset_miss(self):
        ref = blank()
        ref[1, 2:5] = 5
        pred = ref.T.copy()
        pred[2:5, 1] = 6
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["eventMicro"]["exactTruePositive"], 0)
        self.assertEqual(d["eventMicro"]["onsetOnlyMatched"], 1)
        self.assertEqual(d["onsetLabelDecomposition"]["fretWrongSameString"], 1)
        self.assertEqual(d["frameActivity"]["totals"]["wrongFretWhileActive"], 3)

    def test_wrong_string_same_fret_is_classified(self):
        ref = blank()
        ref[2, 3:6] = 7
        pred = np.full((12, 6), -1, dtype=np.int16)
        pred[3:6, 4] = 7
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["onsetLabelDecomposition"]["stringWrongSameFret"], 1)
        self.assertEqual(d["stringConfusionRefRowsPredColumns"][2][4], 1)

    def test_both_wrong_and_event_fp_fn_are_accounted(self):
        ref = blank()
        ref[0, 1:3] = 2
        pred = np.full((12, 6), -1, dtype=np.int16)
        pred[1:3, 3] = 9
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["onsetLabelDecomposition"]["bothStringAndFretWrong"], 1)
        self.assertEqual(d["eventMicro"]["falsePositive"], 1)
        self.assertEqual(d["eventMicro"]["falseNegative"], 1)

    def test_unmatched_activity_counts_fp_and_fn_frames(self):
        ref = blank(10)
        ref[0, 1:4] = 1
        pred = np.full((10, 6), -1, dtype=np.int16)
        pred[6:8, 0] = 1
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["frameActivity"]["totals"]["activityFalseNegative"], 3)
        self.assertEqual(d["frameActivity"]["totals"]["activityFalsePositive"], 2)

    def test_masked_frames_do_not_create_errors(self):
        ref = blank(8)
        ref[0, 2:5] = MOD.MASK
        pred = np.full((8, 6), -1, dtype=np.int16)
        pred[2:5, 0] = 4
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["eventMicro"]["predictedEvents"], 0)
        self.assertEqual(d["frameActivity"]["totals"]["activityFalsePositive"], 0)

    def test_fragmentation_and_end_boundary_error_are_reported(self):
        ref = blank(14)
        ref[0, 2:10] = 4
        pred = np.full((14, 6), -1, dtype=np.int16)
        pred[2:5, 0] = 4
        pred[6:10, 0] = 4
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["temporalRun"]["fragmentedReferenceRuns"], 1)
        self.assertGreaterEqual(d["temporalRun"]["exactPairsEndErrorOverOneFrame"], 1)

    def test_pitch_correct_wrong_string_is_identified(self):
        ref = blank()
        ref[0, 2:5] = 5
        pred = np.full((12, 6), -1, dtype=np.int16)
        pred[2:5, 1] = 0
        d = MOD.diagnose_capture(pred, ref)
        self.assertEqual(d["onsetLabelDecomposition"]["pitchCorrectWrongString"], 1)


if __name__ == "__main__":
    unittest.main()
