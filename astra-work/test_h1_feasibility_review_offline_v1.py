"""Only synthetic scalar cases; never runs H1, model or Actions."""
import copy
import math
import tempfile
from pathlib import Path
import unittest
from h1_feasibility_review_offline_v1 import (
    STAGES, LIMIT_SECONDS, evidence_template, examine_evidence,
    source_consistency, read_pinned_json_regular,
)

SOURCES = {
    'historicPreparedFrames':1_924_805,'largestHistoricCaptureFrames':23_773,
    'historicPreparedPayloadBytes':1_501_347_900,
    'historicLogicalOverlapScenarioBytes':4_391_923_097,
    'priorReceiptsReconciled':True,
}


def filled():
    w = evidence_template()
    for stage in STAGES:
        w['stageUpperBounds'][stage] = {
            'upperBoundSeconds': 100, 'evidenceRunId':123,
            'evidenceSha256':'a'*64,
        }
    w['runnerResources'] = {
        'availableDiskBytesAtJobStart':10_000_000_000,
        'peakAdditionalDiskBytes':6_000_000_000,'diskReserveBytes':1_000_000_000,
        'availableRamBytes':12_000_000_000,'peakResidentRamBytes':6_000_000_000,
        'ramReserveBytes':1_000_000_000,
    }
    w['runnerEvidence']={'runId':123,'evidenceSha256':'b'*64,'runnerImage':'ubuntu-22.04'}
    return w


class PaperOnlyTest(unittest.TestCase):
    def test_unfilled_template_blocks_all_twelve_stages_and_resources(self):
        r = examine_evidence(evidence_template(), SOURCES)
        self.assertEqual(r['technicalPaperReviewStatus'],'BLOCKED_MISSING_EVIDENCE')
        self.assertEqual(len([x for x in r['missingEvidence'] if x.startswith('stage:')]),12)
        self.assertEqual(len([x for x in r['missingEvidence'] if x.startswith('resource:')]),6)
        self.assertFalse(r['launchPermission'])

    def test_fake_complete_evidence_is_still_not_an_approval(self):
        r=examine_evidence(filled(),SOURCES)
        self.assertEqual(r['completeTwelveStageBoundSeconds'],1200)
        self.assertEqual(r['technicalPaperReviewStatus'],'PAPER_PACKAGE_AWAITS_EXTERNAL_VERIFICATION')
        self.assertFalse(r['actualRunnerTelemetryProvenByThisTool'])
        self.assertFalse(r['launchPermission'])

    def test_over_300_minutes_fails(self):
        w=filled(); w['stageUpperBounds'][STAGES[1]]['upperBoundSeconds']=LIMIT_SECONDS
        self.assertEqual(examine_evidence(w,SOURCES)['technicalPaperReviewStatus'],'BLOCKED_BOUND_EXCEEDS_LIMIT')

    def test_disk_reserve_and_ram_reserve_enforced(self):
        for field in ('disk','ram'):
            w=filled()
            if field=='disk':w['runnerResources']['diskReserveBytes']=6_000_000_000
            else:w['runnerResources']['ramReserveBytes']=7_000_000_000
            self.assertEqual(examine_evidence(w,SOURCES)['technicalPaperReviewStatus'],'BLOCKED_BOUND_EXCEEDS_LIMIT')

    def test_unknown_extra_stage_rejected(self):
        w=filled();w['stageUpperBounds']['stageThirteen']=None
        with self.assertRaisesRegex(ValueError,'INCORRECT_TWELVE_STAGE_SET'):examine_evidence(w,SOURCES)

    def test_wrong_git_blob_anchors_rejected(self):
        w=filled();w['sourceAnchors']['framesGitBlob']='0'*40
        with self.assertRaisesRegex(ValueError,'WORKSHEET_SOURCE_IDENTITY_MISMATCH'):examine_evidence(w,SOURCES)

    def test_bool_nan_and_negative_numbers_rejected(self):
        for invalid in (-1,math.nan,True,float('inf')):
            w=filled();w['stageUpperBounds'][STAGES[0]]['upperBoundSeconds']=invalid
            with self.subTest(invalid=invalid),self.assertRaisesRegex(ValueError,'INVALID_STAGE_BOUND'):examine_evidence(w,SOURCES)
        w=filled();w['runnerResources']['peakResidentRamBytes']=True
        with self.assertRaisesRegex(ValueError,'INVALID_RESOURCE_BYTE_COUNT'):examine_evidence(w,SOURCES)

    def test_no_self_approved_support_or_source_controls(self):
        for field in ('writtenSupportCase16795041','independentSourceAndPackageReview',
                      'sharedAtomicOneUseControlReview'):
            w=filled();w['documentation'][field]='CLEARED'
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'CANNOT_BE_SELF_APPROVED'):examine_evidence(w,SOURCES)

    def test_missing_stage_provenance_rejected(self):
        w=filled();del w['stageUpperBounds'][STAGES[0]]['evidenceSha256']
        with self.assertRaisesRegex(ValueError,'STAGE_PROVENANCE_REQUIRED'):examine_evidence(w,SOURCES)

    def test_historic_overlap_is_only_review_discrepancy(self):
        w=filled();w['runnerResources']['peakAdditionalDiskBytes']=2_000_000_000
        r=examine_evidence(w,SOURCES)
        self.assertTrue(r['reviewHistoricalOverlapDiscrepancy'])
        self.assertFalse(r['launchPermission'])

    def test_source_receipt_drift_rejected(self):
        f={'schema':'astra-h1-prior-scalar-exact-prepared-frame-recovery-v1',
           'population':{'captures':256,'totalFrames':1_924_805,'maxFrames':23_773,
                         'featureAndLabelPayloadBytes':1_501_347_900}}
        a=[{'exactPreparedFrames':1_924_805,'thisArchivePreparedArrayPayloadBytes':1_501_347_900,
            'modeledZipPlusExtractionBytes':4_391_923_097,
            'modeledEndOfPreparationBytes':2,'modeledAfterArchiveCleanupBytes':1}]*8
        c={'schema':'astra-h1-exact-prior-scalar-stage-capacity-review-v1',
           'perArchiveSequentialStages':a,'completePreparedArrayPayloadBytes':1_501_347_900,
           'largestIdentifiableStage':{'historicalLogicalPlusExactPreparedPayloadBytes':4_391_923_097}}
        t={'schema':'astra-h1-prior-v9-preparation-log-reconciliation-v1',
           'jobs':[{'preparedCaptureTotal':256,'prepElapsedSeconds':1551.28}]*10}
        with self.assertRaisesRegex(ValueError,'PER_ARCHIVE_CAPACITY_RECONCILIATION_FAILURE'):
            source_consistency(f,c,t)
        f['population']['totalFrames']=4
        with self.assertRaisesRegex(ValueError,'FROZEN_PREPARED_FRAME_AGGREGATE_DRIFT'):
            source_consistency(f,c,t)

    def test_pinned_source_blob_and_symlink_rejection(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'source.json'
            path.write_text('{"only":"fixture"}\n')
            raw=path.read_bytes()
            sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
            self.assertEqual(read_pinned_json_regular(path,sha),{'only':'fixture'})
            with self.assertRaisesRegex(ValueError,'PRIOR_SOURCE_BLOB_MISMATCH'):
                read_pinned_json_regular(path,'f'*40)
            link=Path(tmp)/'link.json'
            link.symlink_to(path)
            with self.assertRaisesRegex(ValueError,'PINNED_INPUT_FILE_MISSING_OR_SYMLINK'):
                read_pinned_json_regular(link,sha)

    def test_missing_runner_reference_blocks(self):
        w=filled();w['runnerEvidence']=None
        r=examine_evidence(w,SOURCES)
        self.assertIn('runnerEvidence',r['missingEvidence'])
        self.assertEqual(r['technicalPaperReviewStatus'],'BLOCKED_MISSING_EVIDENCE')


if __name__=='__main__': unittest.main(verbosity=2)
