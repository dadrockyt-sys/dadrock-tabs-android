import unittest

from score_role_aware_note_onsets import score_role_aware_note_onsets


class RoleAwareScoreTests(unittest.TestCase):
    def test_disjoint_roles_share_one_prediction_inventory(self):
        predictions = [
            {'id': 'p1', 'midi': 50, 'start': 1.0},
            {'id': 'p2', 'midi': 62, 'start': 2.0},
        ]
        result = score_role_aware_note_onsets(
            predictions,
            {
                'rhythm': [{'id': 'r1', 'midi': 50, 'start': 1.01}],
                'lead': [{'id': 'l1', 'midi': 62, 'start': 2.01}],
            },
            start=0, end=3, tolerance=.05,
        )
        self.assertEqual(result['tp'], 2)
        self.assertEqual(result['byRole']['rhythm']['tp'], 1)
        self.assertEqual(result['byRole']['lead']['tp'], 1)

    def test_prediction_cannot_count_twice_in_joint_score(self):
        predictions = [{'id': 'p1', 'midi': 50, 'start': 1.0}]
        result = score_role_aware_note_onsets(
            predictions,
            {
                'rhythm': [{'id': 'r1', 'midi': 50, 'start': 1.0}],
                'lead': [{'id': 'l1', 'midi': 62, 'start': 1.0}],
            },
            start=0, end=2, tolerance=.05,
        )
        self.assertEqual(result['tp'], 1)
        self.assertEqual(result['fp'], 0)
        self.assertEqual(result['fn'], 1)

    def test_cross_role_same_pitch_same_time_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'AMBIGUOUS_CROSS_ROLE_TARGET_COLLISION'):
            score_role_aware_note_onsets(
                [],
                {
                    'rhythm': [{'id': 'r1', 'midi': 50, 'start': 1.0}],
                    'lead': [{'id': 'l1', 'midi': 50, 'start': 1.02}],
                },
                start=0, end=2, tolerance=.05,
            )

    def test_role_transfer_can_leave_joint_score_unchanged(self):
        targets = {
            'rhythm': [{'id': 'r1', 'midi': 50, 'start': 1.0}],
            'lead': [{'id': 'l1', 'midi': 62, 'start': 1.0}],
        }
        lead_prediction = score_role_aware_note_onsets(
            [{'id': 'p1', 'midi': 62, 'start': 1.0}], targets,
            start=0, end=2, tolerance=.05,
        )
        rhythm_prediction = score_role_aware_note_onsets(
            [{'id': 'p1', 'midi': 50, 'start': 1.0}], targets,
            start=0, end=2, tolerance=.05,
        )
        self.assertEqual(lead_prediction['tp'], rhythm_prediction['tp'])
        self.assertEqual(lead_prediction['byRole']['lead']['tp'], 1)
        self.assertEqual(rhythm_prediction['byRole']['rhythm']['tp'], 1)

    def test_ids_must_be_globally_unique(self):
        with self.assertRaisesRegex(ValueError, 'globally unique'):
            score_role_aware_note_onsets(
                [],
                {
                    'rhythm': [{'id': 'same', 'midi': 50, 'start': 1.0}],
                    'lead': [{'id': 'same', 'midi': 62, 'start': 1.0}],
                },
                start=0, end=2, tolerance=.05,
            )


if __name__ == '__main__':
    unittest.main()
