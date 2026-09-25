import unittest

import numpy as np
import torch

from astra_backend.guitartechs_training_v5 import objective_decoder as MOD


class GuitarTechsV5ComponentTests(unittest.TestCase):
    def test_auxiliary_targets_separate_onset_activity_and_pitch(self):
        labels = torch.full((1, 6, 5), -1, dtype=torch.long)
        labels[0, 0, 1] = 5
        labels[0, 0, 2] = 5
        labels[0, 0, 3] = 7
        info = MOD.auxiliary_targets(labels)
        self.assertEqual(float(info["onsetTarget"][0, 1, 0]), 1.0)
        self.assertEqual(float(info["onsetTarget"][0, 2, 0]), 0.0)
        self.assertEqual(float(info["onsetTarget"][0, 3, 0]), 1.0)
        self.assertEqual(float(info["activityTarget"][0, 2, 0]), 1.0)
        midi_45 = 45 - MOD.MIN_MIDI
        self.assertEqual(float(info["pitchTarget"][0, 1, midi_45]), 1.0)

    def test_decoder_requires_onset_to_start_but_not_to_continue(self):
        frames = 6
        state = np.zeros((frames, 6, MOD.NUM_CLASSES), dtype=np.float64)
        state[..., MOD.SILENCE_CLASS] = 1.0
        onset = np.zeros((frames, 6), dtype=np.float64)
        activity = np.zeros((frames, 6), dtype=np.float64)
        for t in range(1, 5):
            state[t, 0, :] = 0.0
            state[t, 0, MOD.SILENCE_CLASS] = 0.10
            state[t, 0, 4] = 0.90
            activity[t, 0] = 0.90
        decoded = MOD.decode_multitask(state, onset, activity)
        self.assertEqual(MOD.count_active_runs(decoded), 0)

        onset[1, 0] = 0.90
        decoded = MOD.decode_multitask(state, onset, activity)
        self.assertTrue(np.all(decoded[1:5, 0] == 4))
        self.assertEqual(MOD.count_active_runs(decoded), 1)

    def test_decoder_requires_new_onset_for_fret_change(self):
        state = np.zeros((6, 6, MOD.NUM_CLASSES), dtype=np.float64)
        state[..., MOD.SILENCE_CLASS] = 1.0
        onset = np.zeros((6, 6), dtype=np.float64)
        activity = np.zeros((6, 6), dtype=np.float64)
        for t in (1, 2):
            state[t, 0, :] = 0.0
            state[t, 0, MOD.SILENCE_CLASS] = 0.10
            state[t, 0, 4] = 0.90
            activity[t, 0] = 0.90
        for t in (3, 4):
            state[t, 0, :] = 0.0
            state[t, 0, MOD.SILENCE_CLASS] = 0.10
            state[t, 0, 7] = 0.90
            activity[t, 0] = 0.90
        onset[1, 0] = 0.9
        decoded = MOD.decode_multitask(state, onset, activity)
        self.assertTrue(np.all(decoded[1:3, 0] == 4))
        self.assertTrue(np.all(decoded[3:5, 0] == -1))

        onset[3, 0] = 0.9
        decoded = MOD.decode_multitask(state, onset, activity)
        self.assertTrue(np.all(decoded[3:5, 0] == 7))

    def test_reference_aware_identity_margin_does_not_penalize_legitimate_unison(self):
        labels = torch.full((1, 6, 2), -1, dtype=torch.long)
        labels[0, 0, 1] = 5
        labels[0, 1, 1] = 0
        outputs = synthetic_outputs(labels, correct_logit=7.0)
        _, parts = MOD.v5_sequence_loss(outputs, labels)
        self.assertAlmostEqual(float(parts["identityMargin"]), 0.0, places=6)

    def test_wrong_string_pitch_equivalent_is_penalized(self):
        labels = torch.full((1, 6, 2), -1, dtype=torch.long)
        labels[0, 0, 1] = 5
        outputs = synthetic_outputs(labels, correct_logit=2.0)
        x = outputs["tablature"].reshape(1, 2, 6, MOD.NUM_CLASSES)
        x[0, 1, 1, 0] = 5.0
        _, bad = MOD.v5_sequence_loss(outputs, labels)
        x[0, 1, 0, 5] = 8.0
        _, good = MOD.v5_sequence_loss(outputs, labels)
        self.assertGreater(float(bad["identityMargin"]), float(good["identityMargin"]))

    def test_multitask_loss_is_finite_and_all_heads_receive_gradients(self):
        labels = torch.full((1, 6, 5), -1, dtype=torch.long)
        labels[0, 0, 1:4] = 5
        labels[0, 1, 2:4] = 0
        outputs = synthetic_outputs(labels, correct_logit=1.5)
        loss, parts = MOD.v5_sequence_loss(outputs, labels)
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        for key in ("tablature", "onset", "activity", "pitch", "taskLogVars"):
            self.assertIsNotNone(outputs[key].grad, key)
            self.assertTrue(torch.all(torch.isfinite(outputs[key].grad)), key)
        for key in ("state", "onset", "activity", "pitch"):
            self.assertTrue(torch.isfinite(parts[key]))

    def test_content_weights_remain_bounded(self):
        weights = MOD.bounded_content_weights({
            "chords": 14,
            "scales": 12,
            "singlenotes": 10,
            "PalmMute": 5,
        })
        self.assertEqual(set(weights), set(MOD.PRIMARY_CONTENT))
        self.assertTrue(all(MOD.CONTENT_WEIGHT_MIN <= x <= MOD.CONTENT_WEIGHT_MAX for x in weights.values()))


def synthetic_outputs(labels, correct_logit=2.0):
    target = MOD.normalized_targets(labels)
    batch, frames, _ = target.shape
    state = torch.zeros(
        (batch, frames, MOD.NUM_STRINGS, MOD.NUM_CLASSES),
        dtype=torch.float32,
    )
    for b in range(batch):
        for t in range(frames):
            for s in range(MOD.NUM_STRINGS):
                cls = int(target[b, t, s].item())
                if cls != MOD.MASK:
                    state[b, t, s, cls] = correct_logit
    state = state.reshape(batch, frames, MOD.NUM_STRINGS * MOD.NUM_CLASSES).detach().requires_grad_(True)

    info = MOD.auxiliary_targets(labels)
    onset = torch.where(info["onsetTarget"] > 0, torch.tensor(2.0), torch.tensor(-2.0)).detach().requires_grad_(True)
    activity = torch.where(info["activityTarget"] > 0, torch.tensor(2.0), torch.tensor(-2.0)).detach().requires_grad_(True)
    pitch = torch.where(info["pitchTarget"] > 0, torch.tensor(2.0), torch.tensor(-2.0)).detach().requires_grad_(True)
    task_log_vars = torch.zeros(4, dtype=torch.float32, requires_grad=True)
    return {
        "tablature": state,
        "onset": onset,
        "activity": activity,
        "pitch": pitch,
        "taskLogVars": task_log_vars,
    }


if __name__ == "__main__":
    unittest.main()
