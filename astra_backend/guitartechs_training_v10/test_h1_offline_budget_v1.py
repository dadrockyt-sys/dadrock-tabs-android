"""No-runtime, no-network H1 budget audit fixtures."""
import unittest
from guitartechs_training_v10.h1_offline_budget_v1 import (
    ARCHIVES, REQUIRED_STAGE_EVIDENCE, WALL_LIMIT_SECONDS,
    stage_budget_review, workflow_budget_audit,
)


def fake_workflow():
    manifest='\n'.join(f'{name} {size} md5 sha P1 chords' for name,size in ARCHIVES.items())
    return ('timeout-minutes: 300\n'
            '            ok=0\n'
            '            for url in "https://zenodo.org/api/records/14963133/files/$file/content" '
            '"https://zenodo.org/records/14963133/files/$file?download=1"; do\n'
            '              if curl --fail --location --max-time 300 --retry 0 -o file "$url"; then\n'
            '                ok=1;break\n'
            '              fi\n'
            '            done\n'
            '            test "$ok" = 1\n'+manifest+'\n')


class BudgetGuards(unittest.TestCase):
    def test_bounded_retry_upper_limit_does_not_prove_feasibility(self):
        receipt=workflow_budget_audit(fake_workflow())
        self.assertEqual(receipt['archiveCount'],8)
        self.assertEqual(receipt['compressedInputBytes'],4004045267)
        self.assertEqual(receipt['singleArchiveRequestCeilingSeconds'],600)
        self.assertEqual(receipt['allArchivesRequestCeilingSeconds'],4800)
        self.assertFalse(receipt['downloadWorstCaseExceedsRunnerLimit'])
        self.assertEqual(receipt['readiness'],'UNPROVEN_BLOCKED')

    def test_unknown_retry_or_missing_archive_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,'UNKNOWN_WORKFLOW'):
            workflow_budget_audit(fake_workflow().replace('--retry 0','--retry 2'))
        with self.assertRaisesRegex(RuntimeError,'FROZEN_EIGHT_ARCHIVE'):
            workflow_budget_audit(fake_workflow().replace('P1_chords.zip','P9_chords.zip'))

    def test_timing_evidence_mandatory(self):
        r=stage_budget_review({})
        self.assertEqual(r['readiness'],'UNPROVEN_BLOCKED')
        self.assertEqual(len(r['missingStages']),len(REQUIRED_STAGE_EVIDENCE))
        evidence={name:{'seconds':1,'evidenceRunId':37852114708} for name in REQUIRED_STAGE_EVIDENCE}
        self.assertEqual(stage_budget_review(evidence)['readiness'],'UNPROVEN_BLOCKED')
        evidence['archivesAndPreparation']['seconds']=WALL_LIMIT_SECONDS
        self.assertEqual(stage_budget_review(evidence)['readiness'],'INFEASIBLE_BOUND')
        evidence['archivesAndPreparation']['seconds']=float('nan')
        with self.assertRaisesRegex(ValueError,'invalid stage duration'):
            stage_budget_review(evidence)


if __name__=='__main__': unittest.main()
