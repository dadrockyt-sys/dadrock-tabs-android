import unittest
import torch
from synthetic.s10_pilot_v1 import init_pair,identity_contract,CONTROL_WIDTH

class S10Tests(unittest.TestCase):
    def test_identity_preserving_widening(self):
        c,w=init_pair(960)
        x=torch.randn((16,960),generator=torch.Generator().manual_seed(10))
        checks=identity_contract(c,w,x)
        self.assertTrue(all(checks.values()))

    def test_extra64_hidden_nonzero_output_zero(self):
        _,w=init_pair(960)
        self.assertGreater(torch.count_nonzero(w.state_hidden.weight[CONTROL_WIDTH:]).item(),0)
        self.assertEqual(torch.count_nonzero(w.state_out.weight[:,CONTROL_WIDTH:]).item(),0)

    def test_wide_has_more_parameters(self):
        c,w=init_pair(960)
        self.assertGreater(sum(p.numel() for p in w.parameters()),sum(p.numel() for p in c.parameters()))

if __name__=="__main__": unittest.main()
