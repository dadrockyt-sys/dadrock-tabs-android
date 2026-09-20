import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from build_pulse_timing_prior import build_prior


class PulseTimingPriorTests(unittest.TestCase):
    def base(self):
        return {
            'kind': 'audio-only-onset-and-pulse-diagnostic',
            'audioSha256': 'a' * 64,
            'frameResolutionSeconds': .01,
            'observedFirst33BeatSeconds': [0.1, 0.6, 1.1, 1.6, 2.1, 2.6],
            'earlyPulseFit': {'periodSeconds': .5, 'bpm': 120, 'rmsResidualSeconds': .001,
                              'maxAbsoluteResidualSeconds': .002},
            'firstRmsAbove001Seconds': .05,
            'firstDetectedOnsetSeconds': .08,
            'predictionsRead': False,
            'referenceLabelsRead': False,
        }

    def build(self, doc=None):
        return build_prior(doc or self.base(), evidence_sha256='b' * 64)

    def test_regular_train_stays_diagnostic_and_never_selects_downbeat(self):
        result = self.build()
        self.assertEqual(result['intervalAnomalies'], [])
        self.assertEqual(len(result['stablePulseRuns']), 1)
        self.assertAlmostEqual(result['stablePulseRuns'][0]['fittedBpm'], 120)
        self.assertEqual(result['candidateDownbeats'], [])
        self.assertFalse(result['measureOneStartVerified'])
        self.assertFalse(result['tempoMapVerified'])
        self.assertFalse(result['customerDeliveryEligible'])

    def test_large_interval_glitch_is_flagged_and_splits_fit(self):
        doc = self.base()
        doc['observedFirst33BeatSeconds'] = [0, .5, 1, 1.5, 2, 3.2, 3.7, 4.2, 4.7, 5.2]
        result = self.build(doc)
        self.assertEqual([(x['leftPulseIndex'], x['rightPulseIndex']) for x in result['intervalAnomalies']], [(4, 5)])
        self.assertEqual(len(result['stablePulseRuns']), 2)

    def test_rejects_prediction_or_label_contaminated_evidence(self):
        for field in ['predictionsRead', 'referenceLabelsRead']:
            doc = self.base()
            doc[field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.build(doc)

    def test_rejects_invalid_or_nonincreasing_pulses(self):
        for pulses in [[0, .5, .5, 1], [0, float('nan'), 1, 2], [0, True, 1, 2], [0, .5, 1]]:
            doc = self.base()
            doc['observedFirst33BeatSeconds'] = pulses
            with self.subTest(pulses=pulses), self.assertRaises(ValueError):
                self.build(doc)

    def test_frame_quantization_sets_minimum_outlier_tolerance(self):
        doc = self.base()
        doc['observedFirst33BeatSeconds'] = [0, .5, 1.01, 1.5, 2.0, 2.5]
        result = self.build(doc)
        self.assertGreaterEqual(result['outlierToleranceSeconds'], .03)
        self.assertEqual(result['intervalAnomalies'], [])

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / 'evidence.json'
            output = root / 'report.json'
            evidence.write_text(json.dumps(self.base()))
            output.write_text('existing')
            proc = subprocess.run([
                sys.executable,
                str(Path(__file__).with_name('build_pulse_timing_prior.py')),
                '--evidence', str(evidence),
                '--output', str(output)
            ], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(output.read_text(), 'existing')


if __name__ == '__main__':
    unittest.main()
