"""Synthetic-only shape arithmetic regression tests; never run models or media."""
import unittest
from h1_offline_memory_shape_review_v1 import receipt, sizes_for_frames

class MemoryShapes(unittest.TestCase):
    def setUp(self):
        self.known = sizes_for_frames(23_773)

    def test_historic_fmax_feature_and_label_bytes(self):
        self.assertEqual(self.known['preparedFloat32FeaturePayloadBytes'], 18_257_664)
        self.assertEqual(self.known['preparedInt16LabelPayloadBytes'], 285_276)

    def test_known_max_evaluation_allocations(self):
        self.assertEqual(self.known['paddedEvaluationCqtFloat32Bytes'], 18_263_808)
        self.assertEqual(self.known['fullStateFloat32Bytes'], 11_981_592)
        self.assertEqual(self.known['fullEventFloat32Bytes'], 570_552)
        self.assertEqual(self.known['singleFullStateFloat64CopyBytes'], 23_963_184)

    def test_evaluation_chunks_are_bounded_to_512(self):
        self.assertEqual(self.known['oneChunkContiguousInputFloat32Bytes'], 3_538_944)
        self.assertEqual(sizes_for_frames(200)['oneChunkContiguousInputFloat32Bytes'], 200*192*9*4)

    def test_training_sequence_and_paired_view_shapes(self):
        self.assertEqual(self.known['oneTrainingSequenceInputFloat32Bytes'], 1_382_400)
        self.assertEqual(self.known['twoPairedTrainingSequenceInputPayloadBytes'], 2_764_800)

    def test_nominal_pcm_is_explicitly_not_audio_measurement(self):
        self.assertEqual(self.known['nominalHopEquivalentMonoPcmFloat32Bytes'], 23_773*512*4)
        self.assertEqual(self.known['nominalPcmPipePlusCopyBytes'], 2*23_773*512*4)
        self.assertFalse(receipt()['nominalPcmDerivedFromActualAudioDuration'])

    def test_total_historical_prepared_payload_reconciles(self):
        self.assertEqual(receipt()['preparedArrayPayloadAllCapturesBytes'], 1_501_347_900)
        self.assertEqual(receipt()['historicPreparedTotalFrames'], 1_924_805)

    def test_frozen_source_anchor_filenames_and_sha_shape(self):
        anchors=receipt()['sourceAnchorsFromExistingGitHubReadOnlyInspection']
        self.assertEqual(len(anchors),6)
        self.assertTrue(all(a['path'].endswith('.py') and len(a['gitBlob'])==40 for a in anchors.values()))
        self.assertFalse(receipt()['localPinnedSourceFilesVerifiedByThisModel'])

    def test_status_is_never_launch_or_peak_approval(self):
        r=receipt()
        self.assertEqual(r['readiness'],'NO_GO_INSUFFICIENT_EVIDENCE')
        self.assertFalse(r['completePeakRamBoundEstablished'])
        self.assertFalse(r['runnerEffectiveAvailableRamMeasured'])
        self.assertFalse(r['twelveStageH1TimeBoundEstablished'])
        self.assertFalse(r['launchPermission'])
        self.assertFalse(r['modelImported'])
        self.assertFalse(r['mediaRead'])

    def test_reject_wrong_scalar_lengths_and_types(self):
        for bad in (-1,0,199,200.0,True,'23773',None):
            with self.subTest(bad=bad),self.assertRaises(ValueError): sizes_for_frames(bad)

    def test_scales_linearly_with_max_capture_frames(self):
        lo=sizes_for_frames(200)
        hi=sizes_for_frames(201)
        self.assertEqual(hi['fullStateFloat32Bytes']-lo['fullStateFloat32Bytes'],6*21*4)
        self.assertEqual(hi['singleFullStateFloat64CopyBytes']-lo['singleFullStateFloat64CopyBytes'],6*21*8)

if __name__=='__main__': unittest.main(verbosity=2)
