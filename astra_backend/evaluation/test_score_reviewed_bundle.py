import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from score_reviewed_bundle import score_bundle

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.docs = {
            'prediction': {'audioSha256': 'a'*64, 'events': [{'start': .5, 'midi': 60}, {'start': 1.1, 'midi': 64}]},
            'labels': {'audioSha256': 'a'*64, 'reviewStatus': 'complete', 'unresolvedItems': [],
                       'pitchPolicy': 'reviewed-sounding-midi-at-attack', 'roles': ['rhythm'],
                       'coverageReviewed': True, 'windowSeconds': [0,2], 'events': [
                           {'id': 'private-note-id', 'role': 'rhythm', 'reviewStatus': 'complete', 'kind': 'attack', 'beat': 1, 'midi': 60},
                           {'id': 'rest', 'role': 'rhythm', 'reviewStatus': 'complete', 'kind': 'rest', 'beat': 2}]},
            'alignment': {'audioSha256': 'a'*64, 'reviewStatus': 'complete', 'unresolvedItems': [], 'independentOfPredictions': True,
                          'evidenceId': 'synthetic-landmarks', 'segments': [
                              {'beatStart': 0, 'beatEnd': 4, 'timeStart': 0, 'timeEnd': 2}]} }
        self.spec = {'version': 1, 'scope': 'whole-mix-to-rhythm', 'audioSha256': 'a'*64,
                     'pitchPolicy': 'reviewed-sounding-midi-at-attack', 'windowSeconds': [0,2], 'onsetToleranceSeconds': .05}
        self.spec['sourceSha256ByRole'] = {'rhythm': 'c'*64}
        self.docs['labels']['sourceSha256ByRole'] = {'rhythm': 'c'*64}
        self.write()
    def write(self):
        for key, doc in self.docs.items():
            data = json.dumps(doc).encode()
            (self.root/key).write_bytes(data)
            self.spec[key+'Sha256'] = hashlib.sha256(data).hexdigest()
    def run_score(self):
        return score_bundle(self.spec, predictions_path=self.root/'prediction', labels_path=self.root/'labels', alignment_path=self.root/'alignment')
    def test_complete_bundle_wires_to_scorer_without_private_output(self):
        result = self.run_score()
        self.assertEqual((result['metrics']['tp'], result['metrics']['fp'], result['metrics']['fn']), (1,1,0))
        self.assertFalse(result['customerDeliveryEligible'])
        self.assertIsNone(result['roleAccuracy'])
        self.assertNotIn('private-note-id', json.dumps(result))
    def test_tampering_is_rejected(self):
        (self.root/'prediction').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'): self.run_score()
    def test_unreviewed_labels_or_alignment_are_rejected(self):
        for group, field, bad in [('labels','reviewStatus','draft'), ('labels','unresolvedItems',['bend']),
                                  ('labels','coverageReviewed',False), ('alignment','independentOfPredictions',False),
                                  ('alignment','evidenceId',''), ('labels','audioSha256','b'*64), ('labels','sourceSha256ByRole',{'rhythm':'d'*64})]:
            original = self.docs[group][field]
            self.docs[group][field] = bad; self.write()
            with self.assertRaises(ValueError): self.run_score()
            self.docs[group][field] = original
        self.write()
    def test_timing_gap_and_out_of_map_event_rejected(self):
        self.docs['alignment']['segments'].append({'beatStart': 5,'beatEnd': 6,'timeStart': 2,'timeEnd': 3})
        self.write()
        with self.assertRaisesRegex(ValueError, 'gap'): self.run_score()
        self.docs['alignment']['segments'].pop()
        self.docs['labels']['events'][0]['beat'] = 5; self.write()
        with self.assertRaises(ValueError): self.run_score()
    def test_rest_and_bend_cannot_create_notes(self):
        row = self.docs['labels']['events'][1]
        for kind in ['rest','tie-continuation','bend-continuation']:
            row['kind'] = kind; self.write()
            self.assertEqual(self.run_score()['metrics']['targets'],1)
        row['midi'] = 60; self.write()
        with self.assertRaises(ValueError): self.run_score()
    def test_coincident_roles_do_not_duplicate_acoustic_targets(self):
        self.spec['scope'] = 'whole-mix-to-combined-reference'
        self.docs['labels']['roles'] = ['bass','lead','rhythm']
        self.spec['sourceSha256ByRole'] = {role: 'c'*64 for role in ['bass','lead','rhythm']}
        self.docs['labels']['sourceSha256ByRole'] = dict(self.spec['sourceSha256ByRole'])
        row = dict(self.docs['labels']['events'][0]); row.update(id='lead-note',role='lead')
        self.docs['labels']['events'].append(row); self.write()
        result = self.run_score()
        self.assertEqual(result['metrics']['targets'],1)
        self.assertEqual(result['mergedCoincidentRoleTargets'],1)
    def test_cli_failure_never_writes_report(self):
        self.docs['labels']['reviewStatus'] = 'draft'; self.write()
        spec = self.root/'spec.json'; spec.write_text(json.dumps(self.spec)); out = self.root/'result.json'
        proc = subprocess.run([sys.executable, str(Path(__file__).with_name('score_reviewed_bundle.py')),
            '--spec',str(spec),'--predictions',str(self.root/'prediction'),'--labels',str(self.root/'labels'),
            '--alignment',str(self.root/'alignment'),'--output',str(out)],capture_output=True)
        self.assertNotEqual(proc.returncode,0)
        self.assertFalse(out.exists())
    def test_complete_alignment_with_unresolved_or_missing_review_items_is_rejected(self):
        for value in [['downbeat unverified'], None, False, '']:
            self.docs['alignment']['unresolvedItems'] = value
            self.write()
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'alignment review incomplete'):
                self.run_score()
        del self.docs['alignment']['unresolvedItems']
        self.write()
        with self.assertRaisesRegex(ValueError, 'alignment review incomplete'):
            self.run_score()

    def test_legato_note_onset_counts_but_bend_continuation_does_not(self):
        self.docs['labels']['events'] = [
            {'id': 'picked', 'role': 'rhythm', 'reviewStatus': 'complete', 'kind': 'attack', 'beat': 1, 'midi': 60},
            {'id': 'legato', 'role': 'rhythm', 'reviewStatus': 'complete', 'kind': 'attack', 'beat': 2.2, 'midi': 64,
             'articulation': 'hammer-on'},
            {'id': 'bend', 'role': 'rhythm', 'reviewStatus': 'complete', 'kind': 'bend-continuation', 'beat': 2.5}]
        self.write()
        result = self.run_score()
        self.assertEqual((result['metrics']['targets'], result['metrics']['tp']), (2, 2))

    def test_piecewise_timing_interpolates_each_segment(self):
        self.docs['alignment']['segments'] = [
            {'beatStart':0,'beatEnd':2,'timeStart':0,'timeEnd':1},
            {'beatStart':2,'beatEnd':3,'timeStart':1,'timeEnd':2}]
        self.docs['labels']['events'][0]['beat'] = 2.1
        self.docs['labels']['events'][0]['midi'] = 64
        self.write()
        self.assertEqual(self.run_score()['metrics']['tp'],1)

if __name__ == '__main__': unittest.main()
