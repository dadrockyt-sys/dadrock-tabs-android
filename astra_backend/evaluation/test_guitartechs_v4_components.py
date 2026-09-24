import copy
import importlib.util
from pathlib import Path
import random
import tempfile
import unittest

import numpy as np
import torch

PATH = Path(__file__).resolve().parents[1] / "guitartechs_training_v4" / "objective_decoder.py"
SPEC = importlib.util.spec_from_file_location("guitartechs_v4_objective_decoder", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def logits_for(labels, correct_logit=4.0, other_logit=0.0):
    batch, strings, frames = labels.shape
    logits = torch.full(
        (batch, frames, MOD.NUM_STRINGS, MOD.NUM_CLASSES),
        other_logit,
        dtype=torch.float32,
    )
    for b in range(batch):
        for s in range(strings):
            for t in range(frames):
                value = int(labels[b, s, t])
                if value == MOD.MASK:
                    continue
                cls = MOD.SILENCE_CLASS if value == -1 else value
                logits[b, t, s, cls] = correct_logit
    return logits.reshape(batch, frames, MOD.NUM_STRINGS * MOD.NUM_CLASSES)


class GuitarTechsV4ComponentTests(unittest.TestCase):
    def test_content_balancing_is_bounded_and_rare_content_gets_more_weight(self):
        weights = MOD.bounded_content_weights({
            "chords": 20,
            "scales": 20,
            "singlenotes": 4,
            "PalmMute": 1,
        })
        self.assertGreater(weights["PalmMute"], weights["chords"])
        self.assertGreater(weights["singlenotes"], weights["chords"])
        for value in weights.values():
            self.assertGreaterEqual(value, MOD.CONTENT_WEIGHT_MIN)
            self.assertLessEqual(value, MOD.CONTENT_WEIGHT_MAX)

    def test_active_weighting_increases_penalty_for_missed_active_frame(self):
        labels = torch.full((1, 6, 3), -1, dtype=torch.long)
        labels[0, 0, 1] = 5
        logits = logits_for(labels)
        # Force the active frame toward silence.
        x = logits.reshape(1, 3, 6, MOD.NUM_CLASSES).clone()
        x[0, 1, 0, :] = 0.0
        x[0, 1, 0, MOD.SILENCE_CLASS] = 4.0
        logits = x.reshape(1, 3, 6 * MOD.NUM_CLASSES)
        loss1, _ = MOD.v4_sequence_loss(logits, labels, active_weight=1.0, continuity_lambda=0.0, identity_lambda=0.0)
        loss2, _ = MOD.v4_sequence_loss(logits, labels, active_weight=1.5, continuity_lambda=0.0, identity_lambda=0.0)
        self.assertGreater(float(loss2), float(loss1))

    def test_pitch_equivalent_wrong_string_margin_is_penalized(self):
        labels = torch.full((1, 6, 2), -1, dtype=torch.long)
        labels[0, 0, 0] = 5  # MIDI 45; same pitch is open A on string 1.
        logits = logits_for(labels, correct_logit=2.0)
        x = logits.reshape(1, 2, 6, MOD.NUM_CLASSES).clone()
        x[0, 0, 1, 0] = 4.0
        _, bad = MOD.v4_sequence_loss(logits=x.reshape(1, 2, 6 * MOD.NUM_CLASSES), labels=labels)
        x[0, 0, 0, 5] = 7.0
        _, good = MOD.v4_sequence_loss(logits=x.reshape(1, 2, 6 * MOD.NUM_CLASSES), labels=labels)
        self.assertGreater(float(bad["identityMargin"]), float(good["identityMargin"]))

    def test_reference_aware_margin_does_not_penalize_legitimate_same_pitch_unison(self):
        labels = torch.full((1, 6, 1), -1, dtype=torch.long)
        labels[0, 0, 0] = 5
        labels[0, 1, 0] = 0
        logits = logits_for(labels, correct_logit=7.0)
        _, parts = MOD.v4_sequence_loss(logits, labels, continuity_lambda=0.0)
        self.assertAlmostEqual(float(parts["identityMargin"]), 0.0, places=6)

    def test_continuity_penalty_detects_fragmenting_probability_swings(self):
        labels = torch.full((1, 6, 4), -1, dtype=torch.long)
        labels[0, 2, :] = 7
        stable = logits_for(labels)
        fragmented = stable.reshape(1, 4, 6, MOD.NUM_CLASSES).clone()
        fragmented[0, 2, 2, :] = 0.0
        fragmented[0, 2, 2, MOD.SILENCE_CLASS] = 5.0
        _, a = MOD.v4_sequence_loss(stable, labels, identity_lambda=0.0)
        _, b = MOD.v4_sequence_loss(fragmented.reshape(1, 4, 6 * MOD.NUM_CLASSES), labels, identity_lambda=0.0)
        self.assertGreater(float(b["continuity"]), float(a["continuity"]))

    def test_decoder_merges_short_gap_and_prunes_singleton_false_event(self):
        probs = np.zeros((14, 6, MOD.NUM_CLASSES), dtype=np.float64)
        probs[..., MOD.SILENCE_CLASS] = 1.0

        for t in range(2, 10):
            probs[t, 0, :] = 0.0
            probs[t, 0, MOD.SILENCE_CLASS] = 0.15
            probs[t, 0, 4] = 0.85

        # Two-frame confidence dip inside the true run.
        for t in (5, 6):
            probs[t, 0, :] = 0.0
            probs[t, 0, MOD.SILENCE_CLASS] = 0.55
            probs[t, 0, 4] = 0.45

        # One-frame false active event.
        probs[12, 0, :] = 0.0
        probs[12, 0, MOD.SILENCE_CLASS] = 0.20
        probs[12, 0, 9] = 0.80

        decoded = MOD.decode_with_hysteresis(probs)
        self.assertTrue(np.all(decoded[2:10, 0] == 4))
        self.assertEqual(int(decoded[12, 0]), -1)
        self.assertEqual(MOD.count_active_runs(decoded), 1)

    def test_decoder_recovers_two_frame_confirmed_low_confidence_onset(self):
        probs = np.zeros((8, 6, MOD.NUM_CLASSES), dtype=np.float64)
        probs[..., MOD.SILENCE_CLASS] = 1.0
        probs[2, 0, :] = 0.0
        probs[2, 0, MOD.SILENCE_CLASS] = 0.50
        probs[2, 0, 4] = 0.45
        probs[2, 0, 9] = 0.05
        probs[3, 0, :] = 0.0
        probs[3, 0, MOD.SILENCE_CLASS] = 0.45
        probs[3, 0, 4] = 0.40
        probs[3, 0, 9] = 0.15
        for t in range(4, 7):
            probs[t, 0, :] = 0.0
            probs[t, 0, MOD.SILENCE_CLASS] = 0.10
            probs[t, 0, 4] = 0.90
        decoded = MOD.decode_with_hysteresis(probs)
        self.assertEqual(int(decoded[2, 0]), 4)
        self.assertTrue(np.all(decoded[2:7, 0] == 4))

    def test_decoder_rejects_unconfirmed_low_confidence_spike(self):
        probs = np.zeros((7, 6, MOD.NUM_CLASSES), dtype=np.float64)
        probs[..., MOD.SILENCE_CLASS] = 1.0
        probs[3, 0, :] = 0.0
        probs[3, 0, MOD.SILENCE_CLASS] = 0.50
        probs[3, 0, 4] = 0.45
        probs[3, 0, 9] = 0.05
        decoded = MOD.decode_with_hysteresis(probs)
        self.assertEqual(int(decoded[3, 0]), -1)
        self.assertEqual(MOD.count_active_runs(decoded), 0)

    def test_decoder_preserves_true_onset_boundary(self):
        probs = np.zeros((8, 6, MOD.NUM_CLASSES), dtype=np.float64)
        probs[..., MOD.SILENCE_CLASS] = 1.0
        for t in range(3, 7):
            probs[t, 1, :] = 0.0
            probs[t, 1, MOD.SILENCE_CLASS] = 0.05
            probs[t, 1, 8] = 0.95
        decoded = MOD.decode_with_hysteresis(probs)
        self.assertTrue(np.all(decoded[:3, 1] == -1))
        self.assertTrue(np.all(decoded[3:7, 1] == 8))

    def test_invalid_probability_tensor_fails_closed(self):
        probs = np.zeros((2, 6, MOD.NUM_CLASSES), dtype=np.float64)
        with self.assertRaises(ValueError):
            MOD.decode_with_hysteresis(probs)

    def test_v4_objective_state_resume_is_exact(self):
        labels = torch.full((1, 6, 5), -1, dtype=torch.long)
        labels[0, 0, 1:4] = 5
        inputs = torch.arange(20, dtype=torch.float32).reshape(1, 5, 4) / 20.0

        def new_pair():
            torch.manual_seed(1234)
            model = torch.nn.Linear(4, 6 * MOD.NUM_CLASSES)
            opt = torch.optim.Adadelta(model.parameters(), lr=1.0)
            return model, opt

        def step(model, opt):
            opt.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss, _ = MOD.v4_sequence_loss(logits, labels, content_weight=1.0)
            loss.backward()
            opt.step()

        continuous, continuous_opt = new_pair()
        for _ in range(4):
            step(continuous, continuous_opt)

        split, split_opt = new_pair()
        for _ in range(2):
            step(split, split_opt)
        model_state = copy.deepcopy(split.state_dict())
        optimizer_state = copy.deepcopy(split_opt.state_dict())

        resumed, resumed_opt = new_pair()
        resumed.load_state_dict(model_state)
        resumed_opt.load_state_dict(optimizer_state)
        for _ in range(2):
            step(resumed, resumed_opt)

        for key, value in continuous.state_dict().items():
            self.assertTrue(torch.equal(value, resumed.state_dict()[key]))
        self.assertEqual(continuous_opt.state_dict().keys(), resumed_opt.state_dict().keys())


if __name__ == "__main__":
    unittest.main()
