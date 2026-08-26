from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "analyze_fit_only_pruning_ceiling.py"
SPEC = importlib.util.spec_from_file_location("v144_fit_only_pruning_ceiling", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load pruning ceiling diagnostic")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DeletionOnlyCeilingTests(unittest.TestCase):
    def test_pitch_content_ceiling_matches_locked_fit_counts(self) -> None:
        ceiling = MODULE.deletion_only_ceiling(138, 594)
        self.assertEqual(ceiling["matched"], 138)
        self.assertEqual(ceiling["generated"], 138)
        self.assertEqual(ceiling["reference"], 594)
        self.assertEqual(ceiling["precision"], 1.0)
        self.assertEqual(ceiling["recall"], 138 / 594)
        self.assertEqual(ceiling["f1"], 0.3770491803278689)
        self.assertFalse(ceiling["mayInsertMissingReferenceItems"])
        self.assertFalse(ceiling["mayRepitchGeneratedItems"])
        self.assertFalse(ceiling["mayMoveGeneratedOnsets"])
        self.assertFalse(ceiling["mayChangeStringOrFret"])

    def test_timing_and_position_ceilings_are_far_below_near100(self) -> None:
        timing = MODULE.deletion_only_ceiling(28, 594)
        position = MODULE.deletion_only_ceiling(20, 594)
        self.assertEqual(timing["f1"], 0.09003215434083602)
        self.assertEqual(position["f1"], 0.06514657980456026)
        self.assertLess(timing["f1"], MODULE.NEAR_100)
        self.assertLess(position["f1"], MODULE.NEAR_100)

    def test_invalid_counts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            MODULE.deletion_only_ceiling(-1, 10)
        with self.assertRaises(ValueError):
            MODULE.deletion_only_ceiling(11, 10)


if __name__ == "__main__":
    unittest.main()
