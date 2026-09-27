import unittest, numpy as np
from evaluation.event_contract_v2 import Event, score_events
from evaluation.p1_p2_combined_diagnostic_v1 import correspond, projection_identity

class CombinedDiagnosticTests(unittest.TestCase):
    def test_correspondence_keeps_unmatched_and_never_zips(self):
        p1=[{"id":"P1|x:A:1","string":0,"fret":3},{"id":"P1|x:A:2","string":1,"fret":5}]
        p2=[{"id":"P2|x:A:2","string":1,"fret":5}]
        r=correspond(p1,p2)
        self.assertEqual(len(r["matches"]),1)
        self.assertEqual(r["unmatchedP1"],["P1|x:A:1"])
        self.assertEqual(r["unmatchedP2"],[])

    def test_wrong_string_or_fret_is_not_correspondence(self):
        p1=[{"id":"P1|x:A:9","string":0,"fret":3}]
        p2=[{"id":"P2|x:A:9","string":0,"fret":4}]
        self.assertEqual(correspond(p1,p2)["matches"],[])

    def test_bias_cancels_in_projection_delta(self):
        w=np.array([2.,-1.]); h1=np.array([.5,3.]); h2=np.array([2.,-4.])
        r=projection_identity(w,7.5,h1,h2)
        self.assertAlmostEqual(r["delta"],r["projectedDelta"],places=10)
        self.assertAlmostEqual(r["biasCancelsError"],0.0,places=10)

    def test_boundary_accounting_changes_only_excluded_predictions(self):
        refs=[Event("r",0,3,.10,.20)]
        preds=[Event("p1",0,3,.10,.20),Event("p2",1,5,.28,.32)]
        raw=score_events(preds,refs,onset_tolerance=.05,offset_tolerance=.05)
        scored=score_events(preds,refs,onset_tolerance=.05,offset_tolerance=.05,
                            excluded_intervals=[(1,.25,.35)])
        self.assertEqual(raw["predictionCount"],2)
        self.assertEqual(scored["predictionCount"],1)
        self.assertEqual(scored["truePositive"],1)

if __name__=="__main__": unittest.main()
