import unittest
from repeated_phrase_confidence import partition_recurring_events


def alignment(n=4):
    return {
        'reviewStatus':'complete','independentOfPredictions':True,
        'windowSeconds':[0.0,float(n*2)],
        'segments':[{'beatStart':4*i,'beatEnd':4*(i+1),'timeStart':2*i,'timeEnd':2*(i+1)} for i in range(n)]
    }


def e(i, measure, relative, midi=60):
    beat=4*(measure-1)+relative
    return {'id':i,'start':(measure-1)*2+relative*.5,'midi':midi,
            'structureGrid':{'nearestBeat':beat,'nearestTime':(measure-1)*2+relative*.5,'absoluteDisplacementSeconds':0}}


class RepeatConfidenceTests(unittest.TestCase):
    def test_three_measure_recurrence_is_supported(self):
        rows=[e('a',1,1),e('b',2,1),e('c',3,1)]
        out=partition_recurring_events(rows,alignment(3),min_stream_coverage=1.0)
        self.assertEqual(out['status'],'complete')
        self.assertEqual(len(out['recurringCoreEvents']),3)

    def test_two_measure_repeat_is_not_enough(self):
        rows=[e('a',1,1),e('b',2,1),e('c',3,2)]
        out=partition_recurring_events(rows,alignment(3),min_stream_coverage=.5)
        self.assertEqual(len(out['recurringCoreEvents']),0)
        self.assertEqual(out['status'],'abstained')

    def test_stream_abstains_when_repeat_coverage_is_below_sixty_percent(self):
        rows=[e('a',1,1),e('b',2,1),e('c',3,1),e('d',1,2,61),e('e',2,3,62),e('f',3,0,63)]
        out=partition_recurring_events(rows,alignment(3))
        self.assertEqual(out['diagnostics']['recurringSupportCoverage'],.5)
        self.assertEqual(out['status'],'abstained')
        self.assertEqual(len(out['recurringCoreEvents']),0)

    def test_repeated_stream_keeps_one_off_events_as_uncertain_not_deleted(self):
        rows=[e('a',1,1),e('b',2,1),e('c',3,1),e('d',1,2,61)]
        out=partition_recurring_events(rows,alignment(3),min_stream_coverage=.7)
        self.assertEqual(out['status'],'complete')
        self.assertEqual(len(out['recurringCoreEvents']),3)
        self.assertEqual(len(out['uncertainEvents']),1)
        self.assertFalse(out['diagnostics']['eventsDeleted'])

    def test_pitch_and_relative_slot_both_define_recurrence(self):
        rows=[e('a',1,1,60),e('b',2,1,61),e('c',3,1,60),e('d',4,2,60)]
        out=partition_recurring_events(rows,alignment(4),min_stream_coverage=.5)
        self.assertEqual(out['status'],'abstained')

    def test_out_of_window_event_does_not_require_grid_metadata(self):
        rows=[e('a',1,1),e('b',2,1),e('c',3,1),{'id':'outside','start':9.0,'midi':70}]
        out=partition_recurring_events(rows,alignment(3),min_stream_coverage=1.0)
        self.assertEqual(out['status'],'complete')
        self.assertEqual(len(out['recurringCoreEvents']),3)
        self.assertEqual(len(out['uncertainEvents']),1)

    def test_requires_prediction_independent_complete_alignment(self):
        a=alignment(3)
        a['independentOfPredictions']=False
        with self.assertRaises(ValueError):
            partition_recurring_events([e('a',1,1)],a)


if __name__=='__main__':
    unittest.main()
