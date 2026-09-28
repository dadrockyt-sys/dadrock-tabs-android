import unittest
import numpy as np

from evaluation.real_domain_failure_localization_v1 import (
    spectral_novelty, summarize_p1, summarize_onset, _synthetic_refs
)

class RealDomainFailureLocalizationTests(unittest.TestCase):
    def test_spectral_novelty(self):
        x=np.array([[0.,0.],[1.,-1.],[3.,0.]],dtype=np.float32)
        r=spectral_novelty(x,2,1)
        self.assertAlmostEqual(r["positiveFlux"],3.0)
        self.assertAlmostEqual(r["l2Difference"],(5.0)**0.5)

    def test_synthetic_reference_timestamp_uses_frozen_512_hop(self):
        d={
          "split":np.asarray(["test"]),
          "onset":np.zeros((1,6,4),dtype=np.int16),
          "state":np.full((1,6,4),20,dtype=np.int16),
        }
        d["onset"][0,0,2]=1
        d["state"][0,0,2]=3
        rows=_synthetic_refs(d)
        self.assertEqual(len(rows),1)
        self.assertAlmostEqual(rows[0]["start"],2*(512/22050))

    def test_p1_summary(self):
        rows=[
          {"exactStringFretTop1":True,"pitchOnlyTop1":True,"wrongStringCorrectPitchTop1":False,
           "absoluteSemitoneError":0,"sameStringFretError":0,"sameStringTrueFretRank":1,"globalTrueStateRank":1,
           "trueClassTop1":True,"trueClassTop3":True,"trueClassTop5":True,
           "trueStateProbability":.7,"silenceProbability":.2},
          {"exactStringFretTop1":False,"pitchOnlyTop1":False,"wrongStringCorrectPitchTop1":False,
           "absoluteSemitoneError":2,"sameStringFretError":-2,"sameStringTrueFretRank":3,"globalTrueStateRank":7,
           "trueClassTop1":False,"trueClassTop3":False,"trueClassTop5":False,
           "trueStateProbability":.1,"silenceProbability":.8},
        ]
        r=summarize_p1(rows)
        self.assertEqual(r["count"],2)
        self.assertAlmostEqual(r["exactStringFretTop1Rate"],.5)
        self.assertAlmostEqual(r["medianAbsoluteSemitoneError"],1.0)
        self.assertAlmostEqual(r["trueClassTop5Rate"],.5)

    def test_onset_summary_windows(self):
        row={
          "onsetProbabilityAtReference":.1,"stateCorrectAtReference":False,
          "window1MaxOnsetProbability":.6,"window1CrossesThreshold":True,"window1MaxFrameOffset":1,"window1StateCorrectAtLocalMax":True,
          "window2MaxOnsetProbability":.6,"window2CrossesThreshold":True,"window2MaxFrameOffset":1,"window2StateCorrectAtLocalMax":True,
          "window4MaxOnsetProbability":.7,"window4CrossesThreshold":True,"window4MaxFrameOffset":3,"window4StateCorrectAtLocalMax":False,
          "frameDiffL2_k1":1.0,"positiveSpectralFlux_k1":2.0,
          "frameDiffL2_k2":2.0,"positiveSpectralFlux_k2":3.0,
          "frameDiffL2_k4":4.0,"positiveSpectralFlux_k4":5.0,
        }
        r=summarize_onset([row])
        self.assertEqual(r["count"],1)
        self.assertAlmostEqual(r["window1ThresholdCrossRate"],1.0)
        self.assertAlmostEqual(r["window4AbsMaxFrameOffsetMedian"],3.0)

if __name__=="__main__":
    unittest.main()
