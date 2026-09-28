import unittest
import numpy as np

from synthetic.s12_pilot_v1 import onset_frames, soften_features

class S12Tests(unittest.TestCase):
    def test_onset_frames_unique_and_skips_zero(self):
        o=np.zeros((6,6),dtype=np.int16)
        o[0,0]=1; o[1,2]=1; o[2,2]=1; o[3,5]=1
        self.assertEqual(onset_frames(o),[2,5])

    def test_softening_changes_only_onset_and_following(self):
        x=np.tile(np.arange(6,dtype=np.float32)[:,None],(1,3))/5.0
        o=np.zeros((6,6),dtype=np.int16); o[0,2]=1
        y=soften_features(x,o,0.5)
        self.assertTrue(np.array_equal(y[0],x[0]))
        self.assertTrue(np.array_equal(y[1],x[1]))
        self.assertFalse(np.array_equal(y[2],x[2]))
        self.assertFalse(np.array_equal(y[3],x[3]))
        self.assertTrue(np.array_equal(y[4],x[4]))
        self.assertTrue(np.array_equal(y[5],x[5]))

    def test_blend_zero_is_identity(self):
        x=np.random.RandomState(1).rand(8,4).astype(np.float32)
        o=np.zeros((6,8),dtype=np.int16); o[0,3]=1
        self.assertTrue(np.array_equal(soften_features(x,o,0.0),x))

    def test_blend_one_copies_preceding_transition(self):
        x=np.zeros((5,2),dtype=np.float32); x[1]=0.2; x[2]=0.9; x[3]=0.8
        o=np.zeros((6,5),dtype=np.int16); o[0,2]=1
        y=soften_features(x,o,1.0)
        self.assertTrue(np.allclose(y[2],x[1]))
        self.assertTrue(np.allclose(y[3],y[2]))

    def test_frame_zero_onset_not_transformed(self):
        x=np.random.RandomState(2).rand(4,3).astype(np.float32)
        o=np.zeros((6,4),dtype=np.int16); o[0,0]=1
        self.assertTrue(np.array_equal(soften_features(x,o,0.7),x))

    def test_out_of_range_blend_rejected(self):
        x=np.zeros((4,3),dtype=np.float32); o=np.zeros((6,4),dtype=np.int16)
        with self.assertRaises(ValueError): soften_features(x,o,-0.1)
        with self.assertRaises(ValueError): soften_features(x,o,1.1)

    def test_values_remain_finite_and_bounded(self):
        x=np.array([[0,1],[1,0],[1,1]],dtype=np.float32)
        o=np.zeros((6,3),dtype=np.int16); o[0,1]=1
        y=soften_features(x,o,0.7)
        self.assertTrue(np.isfinite(y).all())
        self.assertGreaterEqual(float(y.min()),0.0)
        self.assertLessEqual(float(y.max()),1.0)

if __name__=="__main__":
    unittest.main()
