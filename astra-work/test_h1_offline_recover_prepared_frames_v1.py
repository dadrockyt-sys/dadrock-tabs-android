"""Pure-scalar synthetic fixtures for the non-launch historical frame reconciler."""
import copy
import hashlib
import unittest
from h1_offline_recover_prepared_frames_v1 import reconcile, digest


class ScalarFrameTests(unittest.TestCase):
    def fixture(self):
        keys={'P1|chords|fakeA|ego':0,'P2|scales|fakeB|directinput':0}
        j={'schema':'astra-guitar-techs-post-v9-fixed-output-admission-audit-v1',
           'guards':{'optimizerStepsExecuted':0},'manifestSha256':'synthetic-manifest',
           'folds':{}}
        summary={'aggregate':{'captures':2,'v9EvaluatedStringPositions':6*(220+310)},
                 'execution':{'manifestSha256':'synthetic-manifest'},'folds':{}}
        sizes={'p1-train-p2-validate':('P2',1),'p2-train-p1-validate':('P1',1)}
        for fold,performer,frames in [('p1-train-p2-validate','P2',310),('p2-train-p1-validate','P1',220)]:
            key=next(k for k in keys if k.startswith(performer+'|'))
            rec={'captureKeySha256':digest(key.encode()),
                 'audit':{'frames':frames,'validPositions':6*frames-3,'maskedPositions':3}}
            j['folds'][fold]={'v8':{'captures':[copy.deepcopy(rec)]},'v9':{'captures':[copy.deepcopy(rec)]}}
            summary['folds'][fold]={'frames':frames,'stringPositions':6*frames,'captures':1}
        return j,{'correctionsMs':keys},summary,sizes

    def test_positive_two_capture_fixture_stays_non_authorizing(self):
        a,c,s,f=self.fixture();out=reconcile(a,c,s,f)
        self.assertEqual(out['population']['totalFrames'],530)
        self.assertEqual(out['population']['maxFrames'],310)
        self.assertEqual(out['population']['featureAndLabelPayloadBytes'],530*780)
        self.assertFalse(out['launchPermission'])
        self.assertEqual(out['readiness'],'NO_GO_INSUFFICIENT_EVIDENCE')

    def test_detect_changed_manifest(self):
        a,c,s,f=self.fixture();a['manifestSha256']='tampered'
        with self.assertRaisesRegex(ValueError,'MANIFEST_IDENTITY_MISMATCH'):reconcile(a,c,s,f)

    def test_detect_v8_v9_length_divergence(self):
        a,c,s,f=self.fixture();a['folds']['p2-train-p1-validate']['v8']['captures'][0]['audit']['frames']=219
        with self.assertRaisesRegex(ValueError,'FRAME_AND_STRING_POSITIONS_MISMATCH|V8_V9_FRAME_COUNT_DISAGREEMENT'):reconcile(a,c,s,f)

    def test_detect_strange_positions(self):
        a,c,s,f=self.fixture();a['folds']['p1-train-p2-validate']['v9']['captures'][0]['audit']['validPositions']+=1
        with self.assertRaisesRegex(ValueError,'FRAME_AND_STRING_POSITIONS_MISMATCH'):reconcile(a,c,s,f)

    def test_detect_unknown_accepted_key_hash(self):
        a,c,s,f=self.fixture();a['folds']['p1-train-p2-validate']['v9']['captures'][0]['captureKeySha256']=hashlib.sha256(b'impostor').hexdigest()
        with self.assertRaisesRegex(ValueError,'CAPTURE_IDENTITY_MISMATCH'):reconcile(a,c,s,f)

    def test_reject_missing_accepted_key(self):
        a,c,s,f=self.fixture();c['correctionsMs'].pop('P1|chords|fakeA|ego')
        with self.assertRaisesRegex(ValueError,'ACCEPTED_CAPTURE_SET_MISMATCH'):reconcile(a,c,s,f)

    def test_detect_summary_total_drift(self):
        a,c,s,f=self.fixture();s['aggregate']['v9EvaluatedStringPositions']+=6
        with self.assertRaisesRegex(ValueError,'PUBLISHED_AGGREGATE_FRAME_SUM_MISMATCH'):reconcile(a,c,s,f)

    def test_optimizer_zero_guard(self):
        a,c,s,f=self.fixture();a['guards']['optimizerStepsExecuted']=1
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_NONZERO_OPTIMIZATION'):reconcile(a,c,s,f)

    def test_invalid_frame_count(self):
        a,c,s,f=self.fixture()
        for v in ('v8','v9'):a['folds']['p1-train-p2-validate'][v]['captures'][0]['audit']['frames']=100
        with self.assertRaisesRegex(ValueError,'CAPTURE_FRAME_COUNT_INVALID'):reconcile(a,c,s,f)


if __name__=='__main__':unittest.main(verbosity=2)
