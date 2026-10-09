"""Read-only relative path and exact original 3-receipt CLI regression checks.

No model, media, Actions, network, paid compute or training. Uses original
pinned scalar JSON files copied from the previously authorized repo evidence.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from h1_feasibility_review_offline_v1 import (
    SOURCE_ANCHORS, read_json_regular, read_pinned_json_regular,
)

ROOT = Path(__file__).resolve().parent
FRAMES = 'H1_PHASE11D_EXACT_PREPARED_FRAME_RECOVERY_2026-10-09.json'
CAPACITY = 'H1_PHASE11D_EXACT_STAGE_CAPACITY_2026-10-09.json'
TIMINGS = 'H1_PHASE11D_V9_HISTORICAL_PREP_TIMINGS_2026-10-09.json'
WORKSHEET = 'H1_FEASIBILITY_MEASUREMENT_WORKSHEET_BLANK_2026-10-09.json'


@contextmanager
def chdir(destination):
    """Python 3.10-compatible directory switch for local scalar-only fixture tests."""
    before = Path.cwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(before)


class RelativeOriginalReceiptTests(unittest.TestCase):
    def test_relative_paths_accept_three_exact_original_files(self):
        with chdir(ROOT):
            for name, key in ((FRAMES, 'framesGitBlob'), (CAPACITY, 'stageCapacityGitBlob'),
                              (TIMINGS, 'priorV9TimingsGitBlob')):
                self.assertTrue(read_pinned_json_regular(Path(name), SOURCE_ANCHORS[key]))

    def test_relative_worksheet_is_readable_without_approving_anything(self):
        with chdir(ROOT):
            value = read_json_regular(Path(WORKSHEET))
        self.assertEqual(value['documentation']['writtenSupportCase16795041'], 'PENDING')
        self.assertTrue(all(x is None for x in value['stageUpperBounds'].values()))

    def test_original_three_receipt_cli_with_relative_paths_is_blocked(self):
        args = [sys.executable, str(ROOT/'h1_feasibility_review_offline_v1.py'),
                '--frames', FRAMES, '--capacity', CAPACITY, '--timings', TIMINGS,
                '--worksheet', WORKSHEET]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=8,
                                check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        obj = json.loads(result.stdout)
        self.assertEqual(obj['technicalPaperReviewStatus'], 'BLOCKED_MISSING_EVIDENCE')
        self.assertEqual(len(obj['missingEvidence']), 19)
        self.assertTrue(obj['sourceVerification']['priorReceiptsReconciled'])
        self.assertIsNone(obj['completeTwelveStageBoundSeconds'])
        self.assertFalse(obj['actualRunnerTelemetryProvenByThisTool'])
        self.assertFalse(obj['launchPermission'])

    def test_relative_parent_symlink_is_rejected_even_with_matching_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            real = base/'actual'
            real.mkdir()
            data = real/'source.json'
            data.write_bytes((ROOT/FRAMES).read_bytes())
            (base/'linked').symlink_to(real, target_is_directory=True)
            with chdir(base):
                with self.assertRaisesRegex(ValueError,
                                            'PINNED_INPUT_FILE_MISSING_OR_SYMLINK'):
                    read_pinned_json_regular(Path('linked/source.json'),
                                             SOURCE_ANCHORS['framesGitBlob'])

    def test_tampered_exact_relative_receipt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'timings.json'
            p.write_bytes((ROOT/TIMINGS).read_bytes() + b' ')
            with chdir(tmp):
                with self.assertRaisesRegex(ValueError, 'PRIOR_SOURCE_BLOB_MISMATCH'):
                    read_pinned_json_regular(Path('timings.json'),
                                             SOURCE_ANCHORS['priorV9TimingsGitBlob'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
