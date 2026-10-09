"""Read-only integration of exact historical scalar receipts; never runs H1.

In an actual checkout this exercises the whole paper-review CLI input contract.
In an incomplete sandbox, tests requiring the missing original timing receipt SKIP.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest

from h1_feasibility_review_offline_v1 import (
    SOURCE_ANCHORS, evidence_template, examine_evidence,
    read_pinned_json_regular, source_consistency,
)

ROOT = Path(os.environ.get('ASTRA_H1_SCALAR_ROOT', Path(__file__).resolve().parent))
FILES = {
    'frames': ROOT / 'H1_PHASE11D_EXACT_PREPARED_FRAME_RECOVERY_2026-10-09.json',
    'capacity': ROOT / 'H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json',
    'timings': ROOT / 'H1_PHASE11D_V9_HISTORICAL_PREP_TIMINGS_2026-10-09.json',
}


class OriginalScalarReceiptIntegration(unittest.TestCase):
    def exact(self, key, anchor):
        path = FILES[key]
        if not path.is_file():
            self.skipTest(f'original committed {key} receipt absent: {path.name}')
        return read_pinned_json_regular(path, SOURCE_ANCHORS[anchor])

    def test_actual_frames_receipt_has_frozen_blob(self):
        frames = self.exact('frames', 'framesGitBlob')
        self.assertEqual(frames['population']['totalFrames'], 1_924_805)
        self.assertEqual(frames['population']['maxFrames'], 23_773)

    def test_actual_capacity_receipt_has_frozen_blob(self):
        capacity = self.exact('capacity', 'stageCapacityGitBlob')
        self.assertEqual(capacity['completePreparedArrayPayloadBytes'], 1_501_347_900)
        self.assertEqual(capacity['largestIdentifiableStage']['historicalLogicalPlusExactPreparedPayloadBytes'], 4_391_923_097)

    def test_single_byte_tampering_is_rejected(self):
        source = FILES['frames']
        if not source.is_file():
            self.skipTest('original committed frame receipt absent')
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / 'tampered.json'
            tampered.write_bytes(source.read_bytes() + b' ')
            with self.assertRaisesRegex(ValueError, 'PRIOR_SOURCE_BLOB_MISMATCH'):
                read_pinned_json_regular(tampered, SOURCE_ANCHORS['framesGitBlob'])

    def test_original_three_receipts_return_blocked_review(self):
        f = self.exact('frames', 'framesGitBlob')
        c = self.exact('capacity', 'stageCapacityGitBlob')
        t = self.exact('timings', 'priorV9TimingsGitBlob')
        crosscheck = source_consistency(f, c, t)
        verdict = examine_evidence(evidence_template(), crosscheck)
        self.assertTrue(crosscheck['priorReceiptsReconciled'])
        self.assertEqual(verdict['technicalPaperReviewStatus'], 'BLOCKED_MISSING_EVIDENCE')
        self.assertEqual(len(verdict['missingEvidence']), 19)
        self.assertFalse(verdict['launchPermission'])
        self.assertFalse(verdict['actualRunnerTelemetryProvenByThisTool'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
