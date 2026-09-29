import unittest
import torch
from synthetic.v6_onset_objectives_v1 import spread_onset_targets,bce_onset_loss,focal_onset_loss,onset_loss

class V6Tests(unittest.TestCase):
    def test_spread_center_and_adjacent(self):
        x=torch.zeros((1,1,5)); x[0,0,2]=1
        y=spread_onset_targets(x)
        self.assertTrue(torch.equal(y,torch.tensor([[[0.,.5,1.,.5,0.]]])))

    def test_spread_edge(self):
        x=torch.zeros((1,1,3)); x[0,0,0]=1
        y=spread_onset_targets(x)
        self.assertTrue(torch.equal(y,torch.tensor([[[1.,.5,0.]]])))

    def test_bce_finite(self):
        self.assertTrue(torch.isfinite(bce_onset_loss(torch.zeros((4,6)),torch.zeros((4,6)))))

    def test_focal_finite_hard(self):
        z=torch.zeros((4,6)); y=torch.randint(0,2,(4,6)).float()
        self.assertTrue(torch.isfinite(focal_onset_loss(z,y)))

    def test_focal_finite_soft(self):
        z=torch.zeros((2,2)); y=torch.tensor([[1.,.5],[0.,.5]])
        self.assertTrue(torch.isfinite(focal_onset_loss(z,y)))

    def test_dispatch(self):
        z=torch.zeros((2,2)); y=torch.zeros((2,2))
        for arm in ('O0','O1','O2','O3'):
            self.assertTrue(torch.isfinite(onset_loss(z,y,arm)))

    def test_unknown_arm_rejected(self):
        with self.assertRaises(ValueError):
            onset_loss(torch.zeros((1,1)),torch.zeros((1,1)),'OX')

if __name__=='__main__':
    unittest.main(verbosity=2)
