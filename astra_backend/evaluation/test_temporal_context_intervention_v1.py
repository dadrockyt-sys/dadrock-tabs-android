import unittest, torch
from evaluation.temporal_context_intervention_v1 import (
    temporal_triplet,repeated_current,clone_identical_pair,ControlledContextModel
)

class TemporalContextSyntheticTests(unittest.TestCase):
    def test_edge_replication(self):
        x=torch.arange(1*3*192,dtype=torch.float32).reshape(1,3,192)
        y=temporal_triplet(x)
        self.assertTrue(torch.equal(y[:,0,:192],x[:,0,:]))
        self.assertTrue(torch.equal(y[:,0,192:384],x[:,0,:]))
        self.assertTrue(torch.equal(y[:,-1,384:],x[:,-1,:]))
    def test_repeated_current_exact(self):
        x=torch.randn(2,4,192)
        y=repeated_current(x)
        self.assertTrue(torch.equal(y[:,:,:192],x))
        self.assertTrue(torch.equal(y[:,:,192:384],x))
        self.assertTrue(torch.equal(y[:,:,384:],x))
    def test_equal_parameter_count(self):
        a=ControlledContextModel(); b=ControlledContextModel()
        self.assertEqual(sum(p.numel() for p in a.parameters()),sum(p.numel() for p in b.parameters()))
    def test_identical_initialization(self):
        a,b=clone_identical_pair()
        for pa,pb in zip(a.parameters(),b.parameters()):
            self.assertTrue(torch.equal(pa,pb))
    def test_context_information_differs_when_neighbors_differ(self):
        x=torch.zeros(1,3,192); x[:,0,:]=1; x[:,2,:]=2
        self.assertFalse(torch.equal(temporal_triplet(x),repeated_current(x)))

if __name__=="__main__": unittest.main()
