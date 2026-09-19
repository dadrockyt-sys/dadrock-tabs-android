import unittest
from score_note_onsets import score_note_onsets

def score(ps, rs, **kwargs):
    return score_note_onsets(ps, rs, start=0, end=2, tolerance=kwargs.get('tolerance', .1))
def note(t, midi=60): return {'start': t, 'midi': midi}

class OnsetScoringTests(unittest.TestCase):
    def test_duplicates_cannot_reuse_target(self):
        r=score([note(.5), note(.5)], [note(.5)])
        self.assertEqual((r['tp'],r['fp'],r['fn']),(1,1,0))
    def test_maximum_matching_avoids_greedy_loss(self):
        r=score([note(.1),note(.2)],[note(.19),note(.29)])
        self.assertEqual(r['tp'],2)
    def test_minimum_error_among_maximum_matches(self):
        r=score([note(.49),note(.55)],[note(.5)])
        self.assertAlmostEqual(r['meanAbsoluteOnsetErrorSeconds'],.01)
    def test_pitch_is_exact_and_window_half_open(self):
        r=score([note(0),note(.5,61),note(2)],[note(0),note(.5)])
        self.assertEqual((r['tp'],r['fp'],r['fn']),(1,1,1))
    def test_empty_is_not_perfect_accuracy(self):
        self.assertIsNone(score([],[])['f1'])
    def test_invalid_input_rejected(self):
        for n in [note(float('nan')),note(-1),note(.5,True),note(.5,128)]:
            with self.assertRaises(ValueError):score([n],[])
        with self.assertRaises(ValueError):score([dict(note(0),id='x'),dict(note(1),id='x')],[])
    def test_order_does_not_change_counts(self):
        ps=[note(.5),note(1),note(.7,64)];rs=[note(.55),note(1.05)]
        a,b=score(ps,rs),score(ps[::-1],rs[::-1])
        self.assertEqual((a['tp'],a['fp'],a['fn']),(b['tp'],b['fp'],b['fn']))
if __name__ == '__main__': unittest.main()
