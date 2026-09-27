import unittest

import torch

from evaluation.event_decoder_v2 import decode_event_list_v2


class EventDecoderV2Tests(unittest.TestCase):
    def _logits(self, frames=12):
        state = torch.full((frames, 6, 21), -8.0)
        state[:, :, 20] = 8.0
        onset = torch.full((frames, 6), -8.0)
        return state, onset

    def test_same_fret_consecutive_onset_plateau_is_one_attack(self):
        state, onset = self._logits()
        state[2:8, 0, 20] = -8.0
        state[2:8, 0, 5] = 8.0
        onset[2, 0] = 8.0
        onset[3, 0] = 8.0

        events = decode_event_list_v2(
            state.reshape(12, -1), onset, hop_seconds=0.01
        )
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 1)
        self.assertEqual(s0[0].fret, 5)
        self.assertAlmostEqual(s0[0].start, 0.02)
        self.assertAlmostEqual(s0[0].end, 0.08)

    def test_same_fret_fresh_threshold_crossing_is_reattack(self):
        state, onset = self._logits()
        state[2:10, 0, 20] = -8.0
        state[2:10, 0, 5] = 8.0
        onset[2, 0] = 8.0
        onset[5, 0] = 8.0

        events = decode_event_list_v2(
            state.reshape(12, -1), onset, hop_seconds=0.01
        )
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 2)
        self.assertEqual([e.fret for e in s0], [5, 5])
        self.assertAlmostEqual(s0[0].start, 0.02)
        self.assertAlmostEqual(s0[0].end, 0.05)
        self.assertAlmostEqual(s0[1].start, 0.05)

    def test_different_fret_onset_is_not_suppressed_by_plateau(self):
        state, onset = self._logits()
        state[2:4, 0, 20] = -8.0
        state[2:4, 0, 5] = 8.0
        state[4:8, 0, 20] = -8.0
        state[4:8, 0, 7] = 8.0
        onset[2, 0] = 8.0
        onset[3, 0] = 8.0
        onset[4, 0] = 8.0

        events = decode_event_list_v2(
            state.reshape(12, -1), onset, hop_seconds=0.01
        )
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 2)
        self.assertEqual([e.fret for e in s0], [5, 7])
        self.assertAlmostEqual(s0[0].start, 0.02)
        self.assertAlmostEqual(s0[0].end, 0.04)
        self.assertAlmostEqual(s0[1].start, 0.04)

    def test_state_change_without_onset_still_does_not_invent_attack(self):
        state, onset = self._logits()
        state[2:4, 0, 20] = -8.0
        state[2:4, 0, 5] = 8.0
        state[4:8, 0, 20] = -8.0
        state[4:8, 0, 7] = 8.0
        onset[2, 0] = 8.0

        events = decode_event_list_v2(
            state.reshape(12, -1), onset, hop_seconds=0.01
        )
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 1)
        self.assertEqual(s0[0].fret, 5)
        self.assertAlmostEqual(s0[0].end, 0.04)


if __name__ == "__main__":
    unittest.main()
