import unittest
import numpy as np

from evaluation.p2_attack_preparation_integrity_audit_v1 import (
    attack_metrics, cqt_novelty, crop_coordinate, group_simultaneous_events,
    local_peaks, mean_mix, nearest_cqt_peak, qualified_nearest_peak,
    seconds_to_index, stft_positive_flux,
)

SPEC={
 "rmsPreSeconds":0.040,"rmsPreGapSeconds":0.005,"rmsPostSeconds":0.060,
 "stftNfft":256,"stftHopSamples":64,
 "rawPeakSearchSeconds":0.080,"rawPeakContextSeconds":0.250,
 "cqtPeakSearchFrames":4,"cqtPeakContextFrames":12,
 "peakMadMultiplier":3.0,"simultaneousToleranceSeconds":1e-6,
}

class AuditTests(unittest.TestCase):
    def test_known_lag_and_crop_sign(self):
        r=crop_coordinate(1.000,-20,20,0.01)
        self.assertAlmostEqual(r["alignedSeconds"],0.980)
        self.assertAlmostEqual(r["cropStartSeconds"],0.200)
        self.assertAlmostEqual(r["cropLocalSeconds"],0.780)
        self.assertEqual(r["preparedFrame"],78)

    def test_sample_rounding(self):
        self.assertEqual(seconds_to_index(0.5,22050),11025)

    def test_stereo_mean_mix_and_cancellation_visible(self):
        x=np.column_stack([np.ones(100),-np.ones(100)])
        self.assertAlmostEqual(float(np.max(np.abs(mean_mix(x)))),0.0)

    def test_gain_scales_raw_but_ratio_is_stable(self):
        sr=1000
        x=np.zeros(1000); x[500:560]=2.0; x[460:495]=0.5
        a=attack_metrics(x,sr,0.5,SPEC); b=attack_metrics(x*3,sr,0.5,SPEC)
        self.assertAlmostEqual(b["postRms"]/a["postRms"],3.0,places=6)
        self.assertAlmostEqual(a["postToPreRmsRatio"],b["postToPreRmsRatio"],places=6)

    def test_silence_has_no_qualified_peak(self):
        v=np.zeros(100); t=np.arange(100)/1000.0
        self.assertIsNone(qualified_nearest_peak(v,t,0.05,0.02,0.05,3.0))

    def test_impulse_peak_near_target(self):
        sr=4000
        x=np.zeros(sr); x[2000]=1.0
        flux,t=stft_positive_flux(x,sr,SPEC)
        p=qualified_nearest_peak(flux,t,0.5,0.08,0.25,3.0)
        self.assertIsNotNone(p)
        self.assertLess(abs(p["offsetSeconds"]),0.08)

    def test_cqt_novelty_and_nearest_peak(self):
        x=np.zeros((20,4),dtype=float); x[10:,0]=5
        flux,l2=cqt_novelty(x)
        self.assertEqual(int(np.argmax(flux)),10)
        p=nearest_cqt_peak(x,10,0.01,SPEC)
        self.assertIsNotNone(p)
        self.assertAlmostEqual(p["offsetSeconds"],0.0)

    def test_repeated_chord_attack_groups_once(self):
        rows=[
          {"id":"a","sourceStart":1.0},{"id":"b","sourceStart":1.0},
          {"id":"c","sourceStart":1.5},{"id":"d","sourceStart":1.5},
        ]
        g=group_simultaneous_events(rows,1e-6)
        self.assertEqual([len(x["events"]) for x in g],[2,2])

    def test_out_of_range_peak_is_unresolved(self):
        v=np.array([0.,0.,10.,0.,0.]); t=np.arange(5)*0.1
        self.assertIsNone(qualified_nearest_peak(v,t,1.0,0.05,0.2,3.0))

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError): mean_mix(np.array([0.,np.nan]))

    def test_clipping_is_finite_and_measurable(self):
        x=np.ones(1000)
        r=attack_metrics(x,1000,0.5,SPEC)
        self.assertTrue(np.isfinite(r["postRms"]))

    def test_local_peak_tie_rule_candidate_set(self):
        self.assertEqual(local_peaks(np.array([0.,2.,2.,0.])).tolist(),[1])

if __name__=="__main__":
    unittest.main()
