"""No-media capacity formula tests. Only scalar constants; no audio, model or network."""
import unittest
from h1_offline_capacity_model_v1 import (
    CAPTURES, MIN_FRAMES_PER_CAPTURE, COMPRESSED_ARCHIVE_BYTES,
    HISTORIC_INVENTORY_EXTRACTED_SUM_BYTES,
    prepared_bytes, hypothetical_frame_count, evaluation_array_bytes, build_receipt,
)

class CapacityFixtureTests(unittest.TestCase):
    def test_exact_per_frame_payload_for_accepted_shapes(self):
        self.assertEqual(prepared_bytes(CAPTURES * MIN_FRAMES_PER_CAPTURE), 39_936_000)
        self.assertEqual(prepared_bytes(100_000), 78_000_000)

    def test_one_minute_nominal_frame_ceil_does_not_understate(self):
        n = hypothetical_frame_count(1)
        self.assertEqual(n, CAPTURES * 2584)
        self.assertEqual(prepared_bytes(n), 515973120 )

    def test_all_scenarios_are_conditional(self):
        x = build_receipt()
        self.assertEqual([s['hypotheticalMinutesPerCapture'] for s in x['nominalDurationSensitivity']], [1,2,5,10,15])
        self.assertTrue(all(s['notAnObservedH1FrameCount'] for s in x['nominalDurationSensitivity']))
        self.assertIsNone(x['optionalUnverifiedFrameAggregate'])
        self.assertFalse(x['verifiedDiskOrMemoryHeadroom'])
        self.assertFalse(x['launchPermission'])

    def test_incomplete_aggregate_never_authorizes(self):
        x = build_receipt(500_000)
        self.assertEqual(x['optionalUnverifiedFrameAggregate']['preparedPayloadBytesExcludingNpyHeaders'], 390_000_000)
        self.assertFalse(x['optionalUnverifiedFrameAggregate']['independentFrameProvenanceVerified'])
        self.assertEqual(x['readiness'], 'NO_GO_INSUFFICIENT_EVIDENCE')

    def test_negative_or_missing_actual_frames_rejected(self):
        for value in (0, -1, 51_199, 51_200.0, True, '51200'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                prepared_bytes(value)

    def test_invalid_synthetic_durations_rejected(self):
        for value in (0, -1, 2.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                hypothetical_frame_count(value)

    def test_evaluation_tallies_are_not_peak_ram(self):
        x = evaluation_array_bytes(100_000)
        self.assertEqual(x['storedStateFloat32Bytes'], 50_400_000)
        self.assertEqual(x['storedEventFloat32Bytes'], 2_400_000)
        self.assertEqual(x['stateToFloat64CopyBytes'], 100_800_000)
        self.assertTrue(x['notAPeakMemoryBound'])

    def test_metadata_is_not_simultaneous_peak(self):
        x = build_receipt()['historicMetadata']
        self.assertEqual(x['compressedArchiveSumBytes'], COMPRESSED_ARCHIVE_BYTES)
        self.assertEqual(x['priorInventoryExtractedAggregateBytesAcrossSeparateRuns'], HISTORIC_INVENTORY_EXTRACTED_SUM_BYTES)
        self.assertIsNone(x['observedSameRunnerPeakExtractionBytes'])

    def test_missing_maximum_frames_still_blocks(self):
        r = build_receipt()
        self.assertIn('largestAcceptedCaptureFrames', r['unknownForHardRamBound'])
        self.assertIn('effectiveRunnerFreeDiskBytes', r['unknownForHardDiskBound'])
        self.assertFalse(r['trainingExecuted'])
        self.assertFalse(r['realMediaRead'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
