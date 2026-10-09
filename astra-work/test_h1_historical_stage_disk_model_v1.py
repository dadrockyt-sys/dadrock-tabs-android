"""Scalar-only synthetic regression tests of historical stage disk arithmetic."""
from dataclasses import replace
import unittest
from h1_historical_stage_disk_model_v1 import (
    ARCHIVES, ACCEPTED_CAPTURES, ACCEPTED_WAV_HEADERS, ACCEPTED_VIDEO_MP3_NO_DURATIONS,
    COMPRESSED_SUM, EXTRACTED_VISIBLE_LOGICAL_SUM, FEATURE_AND_LABEL_BYTES_PER_FRAME,
    NOMINAL_WAV_FRAMES, hypothetical_video_frames, validate_archives, stage_scenario, receipt,
)


class HistoricalStageDiskTests(unittest.TestCase):
    def test_eight_original_jobs_counts_and_sizes_reconcile(self):
        validate_archives()
        self.assertEqual(sum(a.compressed for a in ARCHIVES), COMPRESSED_SUM)
        self.assertEqual(sum(a.extracted_visible for a in ARCHIVES), EXTRACTED_VISIBLE_LOGICAL_SUM)
        self.assertEqual(sum(a.wav_accepted for a in ARCHIVES), ACCEPTED_WAV_HEADERS)
        self.assertEqual(sum(a.video_accepted for a in ARCHIVES), ACCEPTED_VIDEO_MP3_NO_DURATIONS)
        self.assertEqual(sum(a.accepted for a in ARCHIVES), ACCEPTED_CAPTURES)
        self.assertEqual(sum(a.nominal_wav_frames for a in ARCHIVES), NOMINAL_WAV_FRAMES)

    def test_hypothetical_video_frame_rate_rounds_up_per_capture(self):
        self.assertEqual(hypothetical_video_frames(1), 2584)
        self.assertEqual(hypothetical_video_frames(2), 5168)
        self.assertEqual(hypothetical_video_frames(5), 12920)

    def test_stage_source_order_and_no_zip_after_extraction(self):
        value = stage_scenario(1)
        rows = value['perArchive']
        self.assertEqual([v['archive'] for v in rows], [a.name for a in ARCHIVES])
        for r, a in zip(rows, ARCHIVES):
            self.assertEqual(r['atZipAndExtractionLogicalBytes'], r['previouslyRetainedNominalPreparedBytes'] + a.compressed + a.extracted_visible)
            self.assertEqual(r['atEndOfPreparationLogicalBytes'], r['previouslyRetainedNominalPreparedBytes'] + a.extracted_visible + r['currentNominalPreparedPayloadBytes'])
            self.assertEqual(r['afterArchiveCleanupLogicalBytes'], r['previouslyRetainedNominalPreparedBytes'] + r['currentNominalPreparedPayloadBytes'])

    def test_no_double_count_of_past_archives(self):
        rows = stage_scenario(1)['perArchive']
        self.assertEqual(rows[0]['previouslyRetainedNominalPreparedBytes'], 0)
        self.assertEqual(rows[1]['previouslyRetainedNominalPreparedBytes'], rows[0]['afterArchiveCleanupLogicalBytes'])
        self.assertEqual(rows[-1]['afterArchiveCleanupLogicalBytes'], sum(x['currentNominalPreparedPayloadBytes'] for x in rows))

    def test_largest_known_archive_source_identity(self):
        arch = max(ARCHIVES, key=lambda a: a.compressed + a.extracted_visible)
        self.assertEqual(arch.name, 'P2_chords.zip')
        self.assertEqual(arch.compressed + arch.extracted_visible, 3_593_659_397)

    def test_stage_peak_is_not_represented_as_actual_peak(self):
        for minutes in (1, 2, 5, 10, 15):
            with self.subTest(minutes=minutes):
                s = stage_scenario(minutes)
                self.assertTrue(s['scenarioOnly'])
                self.assertFalse(s['completePeakBoundEstablished'])
                self.assertIsNone(s['actualPeakFilesystemBytes'])
                self.assertIsNone(s['availableRunnerDiskBytes'])
                self.assertGreaterEqual(s['maxIdentifiableStageLogicalBytes'], s['conditionalTotalNominalPreparedPayloadBytes'])

    def test_scenario_payload_matches_source_780_byte_formula(self):
        for minutes in (1, 10):
            with self.subTest(minutes=minutes):
                s = stage_scenario(minutes)
                frames = NOMINAL_WAV_FRAMES + ACCEPTED_VIDEO_MP3_NO_DURATIONS * hypothetical_video_frames(minutes)
                self.assertEqual(s['conditionalTotalNominalPreparedPayloadBytes'], frames * FEATURE_AND_LABEL_BYTES_PER_FRAME)

    def test_conditional_stage_footprint_nondecreasing(self):
        scenarios = [stage_scenario(x) for x in (1,2,5,10,15)]
        self.assertEqual([s['hypotheticalVideoMinutesPerAcceptedMp3Capture'] for s in scenarios], [1,2,5,10,15])
        self.assertTrue(all(scenarios[i]['maxIdentifiableStageLogicalBytes'] < scenarios[i+1]['maxIdentifiableStageLogicalBytes'] for i in range(4)))

    def test_altered_count_or_size_rejected(self):
        for altered in (replace(ARCHIVES[0], video_accepted=31), replace(ARCHIVES[0], extracted_visible=0), replace(ARCHIVES[0], nominal_wav_frames=1)):
            with self.subTest(altered=altered), self.assertRaisesRegex(ValueError, 'HISTORICAL_SCALAR_RECONCILIATION_FAILED'):
                validate_archives((altered,*ARCHIVES[1:]))

    def test_invalid_minutes_and_types_rejected(self):
        for bad in (0, -1, 1.5, True, '10', None):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                hypothetical_video_frames(bad)

    def test_duplicate_archives_rejected(self):
        with self.assertRaisesRegex(ValueError, 'HISTORICAL_ARCHIVE_SET_DRIFT'):
            validate_archives((ARCHIVES[0],) * 8)

    def test_receipt_is_consistently_non_authorizing(self):
        r = receipt()
        self.assertEqual(r['readiness'], 'NO_GO_INSUFFICIENT_EVIDENCE')
        self.assertFalse(r['launchPermission'])
        self.assertFalse(r['mediaAcquired'])
        self.assertFalse(r['trainingExecuted'])
        self.assertEqual(r['population']['mp3VideoDurationsAbsent'], 98)
        self.assertEqual(len(r['scenarios']), 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
