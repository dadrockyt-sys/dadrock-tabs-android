#!/usr/bin/env python3
import unittest
import torch
from synthetic.v5_target_structure_v1 import (
    NUM_STRINGS,NUM_CLASSES,SILENCE_CLASS,
    exact_state_loss,pitch_equivalent_state_loss,mixed_state_loss,
    compatible_state_probability,compatible_onset_probability,
)

class V5TargetStructureTests(unittest.TestCase):
    def test_losses_finite(self):
        z=torch.zeros((4,NUM_STRINGS*NUM_CLASSES))
        t=torch.full((4,NUM_STRINGS),-1,dtype=torch.long)
        t[0,0]=0; t[1,1]=0; t[2,2]=5
        for fn in (exact_state_loss,pitch_equivalent_state_loss,mixed_state_loss):
            self.assertTrue(torch.isfinite(fn(z,t)))

    def test_mixed_is_exact_half_average(self):
        torch.manual_seed(7)
        z=torch.randn((3,NUM_STRINGS*NUM_CLASSES))
        t=torch.full((3,NUM_STRINGS),-1,dtype=torch.long)
        t[0,0]=0; t[1,1]=2; t[2,3]=7
        e=exact_state_loss(z,t)
        p=pitch_equivalent_state_loss(z,t)
        self.assertTrue(torch.allclose(mixed_state_loss(z,t),.5*e+.5*p))

    def test_pitch_equivalent_rewards_alternate_position(self):
        # MIDI 45 can be string 0 fret 5 or string 1 fret 0.
        logits=torch.full((1,NUM_STRINGS,NUM_CLASSES),-8.0)
        logits[:,:,SILENCE_CLASS]=0.0
        logits[0,1,0]=8.0
        target=torch.full((1,NUM_STRINGS),-1,dtype=torch.long)
        target[0,0]=5
        good=pitch_equivalent_state_loss(logits.reshape(1,-1),target)
        bad_logits=logits.clone(); bad_logits[0,1,0]=-8.0
        bad=pitch_equivalent_state_loss(bad_logits.reshape(1,-1),target)
        self.assertLess(float(good),float(bad))

    def test_compatible_probability_is_bounded(self):
        p=torch.zeros((NUM_STRINGS,NUM_CLASSES))
        p[:,SILENCE_CLASS]=1
        p[0,5]=.30; p[1,0]=.40
        q=compatible_state_probability(p,45)
        self.assertGreaterEqual(float(q),0)
        self.assertLessEqual(float(q),1)
        self.assertAlmostEqual(float(q),1-(1-.30)*(1-.40),places=6)

    def test_compatible_onset_uses_max_string(self):
        p=torch.tensor([.1,.7,.2,.3,.4,.5])
        self.assertAlmostEqual(float(compatible_onset_probability(p,45)),.7,places=6)

    def test_unrepresentable_rejected(self):
        p=torch.zeros((NUM_STRINGS,NUM_CLASSES))
        with self.assertRaises(ValueError):
            compatible_state_probability(p,37)

if __name__=="__main__":
    unittest.main(verbosity=2)
