import unittest
import numpy as np

from align_development import SAMPLE_RATE, evaluate_alignment, onset_envelope


def click_audio(onsets, lag_seconds=0.0, duration=12.0):
    samples = np.zeros(int(duration * SAMPLE_RATE), dtype=np.float64)
    for onset in onsets:
        start = int(round((onset + lag_seconds) * SAMPLE_RATE))
        if 0 <= start < len(samples) - 40:
            samples[start:start+8] += 0.95
            samples[start+8:start+24] += 0.45
            samples[start+24:start+40] += 0.15
    n = np.arange(len(samples), dtype=np.float64)
    samples += 0.001 * np.sin(2 * np.pi * 73 * n / SAMPLE_RATE)
    return samples


class AlignmentTests(unittest.TestCase):
    def test_recovers_known_positive_lag_and_passes_gate(self):
        onsets = [0.4 + i * 0.22 for i in range(45)]
        out = evaluate_alignment(onsets, click_audio(onsets, 0.032))
        self.assertEqual(out["status"], "complete")
        self.assertLessEqual(abs(out["appliedCorrectionMs"] - 32), 4)
        self.assertGreaterEqual(out["matchedFraction"], 0.8)
        self.assertLessEqual(out["medianAbsoluteResidualMs"], 10)
        self.assertLessEqual(out["bootstrapLagMadMs"], 5)

    def test_recovers_known_negative_lag(self):
        onsets = [0.5 + i * 0.21 for i in range(45)]
        out = evaluate_alignment(onsets, click_audio(onsets, -0.026))
        self.assertEqual(out["status"], "complete")
        self.assertLessEqual(abs(out["appliedCorrectionMs"] + 26), 4)

    def test_less_than_thirty_midi_groups_abstains(self):
        onsets = [0.5 + i * 0.2 for i in range(29)]
        out = evaluate_alignment(onsets, click_audio(onsets, 0.01))
        self.assertEqual(out["status"], "abstained")
        self.assertIn("MINIMUM_MIDI_ONSET_GROUPS_NOT_MET", out["blockers"])

    def test_silence_abstains(self):
        onsets = [0.5 + i * 0.2 for i in range(40)]
        samples = np.zeros(int(10 * SAMPLE_RATE), dtype=np.float64)
        out = evaluate_alignment(onsets, samples)
        self.assertEqual(out["status"], "abstained")
        self.assertIn("AUDIO_ONSET_ENVELOPE_EMPTY", out["blockers"])

    def test_envelope_is_deterministic(self):
        samples = click_audio([1.0, 2.0, 3.0], duration=4)
        first = onset_envelope(samples)
        second = onset_envelope(samples.copy())
        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_array_equal(first[1], second[1])


if __name__ == "__main__":
    unittest.main()
