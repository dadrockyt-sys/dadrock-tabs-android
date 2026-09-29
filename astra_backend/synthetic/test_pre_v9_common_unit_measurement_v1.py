import unittest

from astra_backend.synthetic.pre_v9_common_unit_measurement_v1 import (
    linear_quantile,
    summarize_grouped_clips,
    v8_l0_rows,
)


class PreV9MeasurementTests(unittest.TestCase):
    def test_linear_quantile_matches_declared_convention(self):
        self.assertEqual(linear_quantile([0.0, 10.0], 0.25), 2.5)

    def test_v8_l0_note_and_attack_units_separate(self):
        rows = v8_l0_rows()
        summary = summarize_grouped_clips(rows)
        self.assertEqual(summary["clipCount"], 273)
        self.assertEqual(summary["noteLabelCount"], 903)
        self.assertEqual(summary["attackGroupCount"], 735)
        self.assertEqual(summary["eligiblePositiveIoiCount"], 462)
        self.assertAlmostEqual(summary["aggregateAttackGroupsPerSecond"], 735 / 546)
        self.assertEqual(summary["repeat250Fraction"], 0.0)

    def test_v8_chord_note_multiplicity_collapses_only_for_timing(self):
        chord = next(r for r in v8_l0_rows() if r["family"] == "chords")
        self.assertEqual(chord["noteLabelCount"], 6)
        self.assertEqual(chord["attackGroups"], [0.32, 1.08])


if __name__ == "__main__":
    unittest.main()
