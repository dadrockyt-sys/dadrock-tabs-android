import unittest

import torch

from evaluation.event_contract_v2 import Event, score_events
from evaluation.event_decoder_v2 import decode_event_list_v2
from tiny_fit_pilot_v1 import decode_event_list


class DecoderV2CheckSemanticsTests(unittest.TestCase):
    def _logits(self, frames=12):
        state = torch.full((frames, 6, 21), -8.0)
        state[:, :, 20] = 8.0
        onset = torch.full((frames, 6), -8.0)
        return state, onset

    def test_plateau_false_positive_removed_without_threshold_change(self):
        state, onset = self._logits()
        state[2:8, 0, 20] = -8.0
        state[2:8, 0, 5] = 8.0
        onset[2, 0] = 8.0
        onset[3, 0] = 8.0
        ref = [Event("r", 0, 5, 0.02, 0.08)]

        v1 = decode_event_list(state.reshape(12, -1), onset, hop_seconds=0.01)
        v2 = decode_event_list_v2(state.reshape(12, -1), onset, hop_seconds=0.01)
        self.assertEqual(score_events(v1, ref)["falsePositive"], 1)
        self.assertEqual(score_events(v2, ref)["falsePositive"], 0)
        self.assertEqual(score_events(v2, ref)["f1"], 1.0)

    def test_real_same_fret_reattack_with_fresh_edge_is_preserved(self):
        state, onset = self._logits()
        state[2:10, 0, 20] = -8.0
        state[2:10, 0, 5] = 8.0
        onset[2, 0] = 8.0
        onset[6, 0] = 8.0
        ref = [
            Event("r1", 0, 5, 0.02, 0.06),
            Event("r2", 0, 5, 0.06, 0.10),
        ]
        v2 = decode_event_list_v2(state.reshape(12, -1), onset, hop_seconds=0.01)
        out = score_events(v2, ref)
        self.assertEqual(out["truePositive"], 2)
        self.assertEqual(out["falsePositive"], 0)
        self.assertEqual(out["falseNegative"], 0)
        self.assertEqual(out["f1"], 1.0)


if __name__ == "__main__":
    unittest.main()
