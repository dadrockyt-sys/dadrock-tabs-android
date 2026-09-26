import tempfile
import unittest
import zipfile
from pathlib import Path

import numpy as np
import torch

from tiny_fit_pilot_v1 import (
    FEATURE_DIM,
    FROZEN_CAPTURE_KEYS,
    MAX_EXAMPLES,
    MAX_FRAMES_PER_EXAMPLE,
    MAX_OPTIMIZER_STEPS,
    MAX_TRAIN_EVAL_SECONDS,
    TinyEventFitModel,
    decode_event_list,
    explicit_event_loss,
    extract_selected_source,
    fit_tiny_model,
    select_pilot_capture_keys,
    validate_training_arrays,
)


class TinyFitPilotTests(unittest.TestCase):
    def _logits(self, frames=10):
        state = torch.full((frames, 6, 21), -8.0)
        state[:, :, 20] = 8.0
        onset = torch.full((frames, 6), -8.0)
        return state, onset

    def test_metadata_only_selection_is_frozen(self):
        corrections = {
            "P1|chords|Set1_maj|ego": -30,
            "P1|chords|Drop3_7|micamp": -17,
            "P1|chords|Drop3_7|directinput": -19,
            "P1|scales|B|directinput": -24,
            "P1|scales|Ab|micamp": -22,
            "P1|scales|Ab|directinput": -24,
            "P1|singlenotes|allsinglenotes|micamp": -23,
            "P1|singlenotes|allsinglenotes|directinput": -24,
            "P1|techniques|PalmMute|micamp": -22,
            "P1|techniques|PalmMute|directinput": -24,
            "P2|scales|Ab|directinput": -15,
        }
        self.assertEqual(select_pilot_capture_keys(corrections), FROZEN_CAPTURE_KEYS)

    def test_explicit_loss_supervises_same_fret_reattack(self):
        model = TinyEventFitModel()
        x = torch.zeros((1, 8, FEATURE_DIM))
        state = torch.full((1, 6, 8), -1, dtype=torch.long)
        state[0, 0, 2:7] = 5
        onset_two = torch.zeros((1, 6, 8), dtype=torch.long)
        onset_two[0, 0, 2] = 1
        onset_two[0, 0, 5] = 1
        onset_one = onset_two.clone()
        onset_one[0, 0, 5] = 0
        outputs = model(x)
        loss_two, parts_two = explicit_event_loss(outputs, state, onset_two)
        loss_one, parts_one = explicit_event_loss(outputs, state, onset_one)
        self.assertTrue(torch.isfinite(loss_two))
        self.assertGreater(float(parts_two["onset"].detach()), float(parts_one["onset"].detach()))
        self.assertGreater(float(loss_two.detach()), float(loss_one.detach()))

    def test_decoder_emits_same_fret_reattack(self):
        state, onset = self._logits()
        state[2:9, 0, 20] = -8.0
        state[2:9, 0, 5] = 8.0
        onset[2, 0] = 8.0
        onset[5, 0] = 8.0
        events = decode_event_list(state.reshape(10, -1), onset, hop_seconds=0.01)
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 2)
        self.assertEqual([e.fret for e in s0], [5, 5])
        self.assertAlmostEqual(s0[0].start, 0.02)
        self.assertAlmostEqual(s0[0].end, 0.05)
        self.assertAlmostEqual(s0[1].start, 0.05)

    def test_decoder_does_not_invent_fret_change_without_onset(self):
        state, onset = self._logits()
        state[2:4, 0, 20] = -8.0
        state[2:4, 0, 5] = 8.0
        state[4:8, 0, 20] = -8.0
        state[4:8, 0, 7] = 8.0
        onset[2, 0] = 8.0
        events = decode_event_list(state.reshape(10, -1), onset, hop_seconds=0.01)
        s0 = [e for e in events if e.string == 0]
        self.assertEqual(len(s0), 1)
        self.assertEqual(s0[0].fret, 5)
        self.assertAlmostEqual(s0[0].end, 0.04)

    def test_selected_zip_extraction_opens_only_frozen_members(self):
        with tempfile.TemporaryDirectory() as td:
            archive = Path(td) / "P1_chords.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("dataset/midi/midi_Drop3_7.mid", b"MIDI")
                zf.writestr("dataset/directinput/directinput_Drop3_7.wav", b"AUDIO")
                zf.writestr("dataset/directinput/directinput_Set1_maj.wav", b"UNRELATED")
                zf.writestr("dataset/midi/midi_Set1_maj.mid", b"UNRELATED-MIDI")
            out = Path(td) / "selected"
            receipt = extract_selected_source(
                archive,
                capture_key="P1|chords|Drop3_7|directinput",
                output_dir=out,
            )
            files = sorted(p for p in out.rglob("*") if p.is_file())
            self.assertEqual(len(files), 2)
            self.assertFalse(receipt["unrelatedMediaExtracted"])
            self.assertEqual({p.read_bytes() for p in files}, {b"MIDI", b"AUDIO"})

    def test_training_array_caps_fail_closed(self):
        okay_x = np.zeros((MAX_EXAMPLES, MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM), dtype=np.float32)
        okay_y = np.full((MAX_EXAMPLES, 6, MAX_FRAMES_PER_EXAMPLE), -1, dtype=np.int16)
        okay_o = np.zeros_like(okay_y)
        validate_training_arrays(okay_x, okay_y, okay_o)
        with self.assertRaises(ValueError):
            validate_training_arrays(np.zeros((MAX_EXAMPLES + 1, 10, FEATURE_DIM)), np.zeros((MAX_EXAMPLES + 1, 6, 10)), np.zeros((MAX_EXAMPLES + 1, 6, 10)))
        with self.assertRaises(ValueError):
            validate_training_arrays(np.zeros((1, MAX_FRAMES_PER_EXAMPLE + 1, FEATURE_DIM)), np.zeros((1, 6, MAX_FRAMES_PER_EXAMPLE + 1)), np.zeros((1, 6, MAX_FRAMES_PER_EXAMPLE + 1)))

    def test_optimizer_and_wall_caps_reject_extension(self):
        x = np.zeros((1, 8, FEATURE_DIM), dtype=np.float32)
        state = np.full((1, 6, 8), -1, dtype=np.int16)
        onset = np.zeros_like(state)
        with self.assertRaises(ValueError):
            fit_tiny_model(x, state, onset, requested_steps=MAX_OPTIMIZER_STEPS + 1)
        with self.assertRaises(ValueError):
            fit_tiny_model(x, state, onset, wall_seconds_limit=MAX_TRAIN_EVAL_SECONDS + 1)

    def test_synthetic_backward_is_finite_and_loss_falls(self):
        rng = np.random.RandomState(7)
        x = rng.normal(0, 1, size=(2, 20, FEATURE_DIM)).astype(np.float32)
        state = np.full((2, 6, 20), -1, dtype=np.int16)
        onset = np.zeros_like(state)
        for b in range(2):
            state[b, 0, 3:15] = 5 + b
            onset[b, 0, 3] = 1
            onset[b, 0, 9] = 1
        _, receipt = fit_tiny_model(x, state, onset, requested_steps=20, wall_seconds_limit=60)
        self.assertEqual(receipt["optimizerSteps"], 20)
        self.assertEqual(receipt["stopReason"], "requested_steps_reached")
        self.assertLess(receipt["finalLoss"]["total"], receipt["initialLoss"]["total"])

    def test_fake_clock_stops_before_step_cap(self):
        x = np.zeros((1, 8, FEATURE_DIM), dtype=np.float32)
        state = np.full((1, 6, 8), -1, dtype=np.int16)
        onset = np.zeros_like(state)
        ticks = iter(range(1000))
        _, receipt = fit_tiny_model(
            x, state, onset,
            requested_steps=20,
            wall_seconds_limit=3,
            clock=lambda: next(ticks),
        )
        self.assertEqual(receipt["stopReason"], "training_evaluation_wall_limit")
        self.assertLess(receipt["optimizerSteps"], 20)
        self.assertLessEqual(receipt["optimizerSteps"], MAX_OPTIMIZER_STEPS)


if __name__ == "__main__":
    unittest.main()
