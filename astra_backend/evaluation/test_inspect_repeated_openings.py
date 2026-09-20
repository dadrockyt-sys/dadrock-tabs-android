import hashlib
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from inspect_repeated_openings import inspect


class RepeatedOpeningDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name) / 'synthetic.wav'
        sr = 22050
        period = 1.8946567921092904
        count = 16
        duration = .6 + (count - 1) * period + .5
        n = int(duration * sr)
        rng = np.random.default_rng(7)
        x = rng.normal(0, 0.0005, n)
        for measure in range(count):
            attack = .1 + measure * period
            start = int(attack * sr)
            length = int(.36 * sr)
            rel = np.arange(length) / sr
            if measure == 0:
                f0 = np.where(rel < .22, 247.0, 247.0 - np.clip((rel - .22) / .08, 0, 1) * 27.0)
            else:
                rise = 220 + np.clip((rel - .07) / .09, 0, 1) * 27
                f0 = np.where(rel < .16, rise, 247.0)
                f0 = np.where(rel > .22, 247.0 - np.clip((rel - .22) / .08, 0, 1) * 27.0, f0)
            phase = 2 * np.pi * np.cumsum(f0) / sr
            env = np.exp(-rel * 2.0)
            tone = sum((0.12 / harmonic) * np.sin(harmonic * phase) for harmonic in [1, 2, 3, 4])
            x[start:start + length] += env * tone
            x[start:start + 32] += np.hanning(64)[32:] * .35
        x = np.clip(x, -.95, .95)
        with wave.open(str(cls.path), 'wb') as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(sr)
            out.writeframes((x * 32767).astype('<i2').tobytes())
        cls.sha = hashlib.sha256(cls.path.read_bytes()).hexdigest()
        cls.period = period

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_repeated_later_cluster_is_low_high_low_and_distinct_from_opening(self):
        result = inspect(self.path, expected_sha256=self.sha, measure_period_seconds=self.period, measure_count=16)
        self.assertTrue(result['laterMeasureAggregate']['lowHighLowContour'])
        self.assertGreaterEqual(result['directLowHighLowContourCountLaterMeasures'], 13)
        self.assertEqual(result['laterClusterCloserToItselfThanOpeningCount'], 15)
        self.assertFalse(result['bendLabelsAssigned'])
        self.assertFalse(result['predictionsRead'])
        self.assertFalse(result['referenceLabelsRead'])

    def test_hash_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
            inspect(self.path, expected_sha256='0' * 64, measure_period_seconds=self.period, measure_count=16)

    def test_invalid_measure_period_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'measure-period'):
            inspect(self.path, expected_sha256=self.sha, measure_period_seconds=.1, measure_count=16)


if __name__ == '__main__':
    unittest.main()
