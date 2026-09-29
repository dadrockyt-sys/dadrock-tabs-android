import unittest

from astra_backend.synthetic.v9_measurement_contract_v1 import (
    ContractError,
    check_count_rate_consistency,
    group_acoustic_attacks,
    pooled_density,
    repeat_fraction,
    validate_group_times,
    validate_manifest,
)


class MeasurementContractTests(unittest.TestCase):
    def test_three_note_chord_is_one_acoustic_group_but_three_note_labels(self):
        note_times = [1.0, 1.0, 1.0]
        groups = group_acoustic_attacks(note_times, 0.010)
        self.assertEqual(groups, [1.0])
        self.assertEqual(len(note_times), 3)
        self.assertIsNone(repeat_fraction(groups))

    def test_two_distinct_short_gap_attacks_remain_two_groups(self):
        groups = group_acoustic_attacks([0.100, 0.280], 0.010)
        self.assertEqual(groups, [0.100, 0.280])
        self.assertEqual(repeat_fraction(groups), 1.0)

    def test_singleton_and_empty_repeat_fraction_are_undefined(self):
        self.assertIsNone(repeat_fraction([]))
        self.assertIsNone(repeat_fraction([0.1]))

    def test_crop_boundary_default_is_half_open(self):
        validate_group_times([0.0, 0.999], 1.0)
        with self.assertRaises(ContractError):
            validate_group_times([1.0], 1.0)
        validate_group_times([1.0], 1.0, include_endpoint=True)

    def test_duplicate_ids_rejected(self):
        clips = [
            {"id":"C01","kind":"positive","evaluationStartSeconds":0,"evaluationEndSeconds":1},
            {"id":"C01","kind":"negative-only","evaluationStartSeconds":0,"evaluationEndSeconds":1},
        ]
        with self.assertRaises(ContractError):
            validate_manifest(clips)

    def test_missing_nonfinite_and_boolean_numeric_fields_rejected(self):
        for bad in (None, float("inf"), float("nan"), True):
            clips = [{"id":"C01","kind":"positive","evaluationStartSeconds":0,"evaluationEndSeconds":bad}]
            with self.assertRaises(ContractError):
                validate_manifest(clips)

    def test_impossible_duration_rejected(self):
        clips = [{"id":"C01","kind":"positive","evaluationStartSeconds":2,"evaluationEndSeconds":1}]
        with self.assertRaises(ContractError):
            validate_manifest(clips)

    def test_corrected_duration_propagates_into_totals(self):
        clips = [
            {"id":"C04","kind":"positive","evaluationStartSeconds":0,"evaluationEndSeconds":5.806},
            {"id":"D01","kind":"negative-only","evaluationStartSeconds":0,"evaluationEndSeconds":8.098},
        ]
        result = validate_manifest(clips, {"C04": 5.799183673469388, "D01": 8.097959183673469})
        self.assertAlmostEqual(result["positiveSeconds"], 5.799183673469388)
        self.assertAlmostEqual(result["negativeSeconds"], 8.097959183673469)

    def test_pooled_density_uses_positive_seconds_only(self):
        self.assertAlmostEqual(pooled_density([2, 1], [1.0, 2.0]), 1.0)

    def test_count_rate_consistency(self):
        check_count_rate_consistency(3, 2.0, 1.5)
        with self.assertRaises(ContractError):
            check_count_rate_consistency(3, 2.0, 1.4)


if __name__ == "__main__":
    unittest.main()
