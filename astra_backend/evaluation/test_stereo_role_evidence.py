import unittest
from stereo_role_evidence import classify_channels, deduplicate_cross_channel, label_mono_events


def e(i, t, m, a=.5):
    return {'id': i, 'start': t, 'midi': m, 'amplitude': a}


class StereoRoleEvidenceTests(unittest.TestCase):
    def test_maps_more_chordal_lower_channel_to_rhythm(self):
        left=[e('l1',0,40),e('l2',0.01,47),e('l3',1,52),e('l4',1.01,59),e('l5',2,50)]
        right=[e('r1',0,64),e('r2',1,67),e('r3',2,69)]
        out=classify_channels(left,right,channel_correlation=.05)
        self.assertEqual(out['status'],'complete')
        self.assertEqual(out['mapping'],{'rhythm':'left','lead':'right'})

    def test_swapped_channels_map_by_evidence_not_side(self):
        rhythm=[e('a',0,40),e('b',0.01,47),e('c',1,52),e('d',1.01,59),e('e',2,50)]
        lead=[e('x',0,64),e('y',1,67),e('z',2,69)]
        out=classify_channels(lead,rhythm,channel_correlation=.05)
        self.assertEqual(out['mapping'],{'rhythm':'right','lead':'left'})

    def test_correlated_channels_abstain(self):
        rows=[e('a',0,52),e('b',1,64)]
        out=classify_channels(rows,rows,channel_correlation=.9)
        self.assertEqual(out['status'],'abstained')
        self.assertIn('CHANNELS_TOO_CORRELATED',out['reasons'])

    def test_weak_role_contrast_abstains(self):
        left=[e('a',0,52),e('b',1,55),e('c',2,57)]
        right=[e('x',0,59),e('y',1,62),e('z',2,64)]
        out=classify_channels(left,right,channel_correlation=.05)
        self.assertEqual(out['status'],'abstained')

    def test_duplicate_keeps_stronger_channel_event(self):
        out=deduplicate_cross_channel([e('l',1,60,.8)],[e('r',1.01,60,.4)])
        self.assertEqual(len(out['left']),1)
        self.assertEqual(len(out['right']),0)

    def test_equal_amplitude_duplicate_is_not_role_biased(self):
        out=deduplicate_cross_channel([e('l',1,60,.5)],[e('r',1.01,60,.5)])
        self.assertEqual(len(out['left']),1)
        self.assertEqual(len(out['right']),1)

    def test_mono_labeling_can_abstain_on_channel_tie(self):
        mono=[e('m',1,60,.5)]
        left=[e('l',1,60,.5)]
        right=[e('r',1.01,60,.48)]
        out=label_mono_events(mono,left,right,{'rhythm':'left','lead':'right'})
        self.assertEqual(len(out['ambiguous']),1)

    def test_mono_unique_channel_match_inherits_role(self):
        mono=[e('m',1,60,.5)]
        out=label_mono_events(mono,[e('l',1,60,.4)],[],{'rhythm':'left','lead':'right'})
        self.assertEqual(len(out['rhythm']),1)


if __name__=='__main__':
    unittest.main()
