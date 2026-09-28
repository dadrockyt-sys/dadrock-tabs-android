import unittest
from evaluation.p1_p2_transfer_evaluation_v1 import _eval_event, aggregate, repeated_ref_indices, EvalPitchEvent

class TransferEvaluationTests(unittest.TestCase):
    def test_edge_guard_is_symmetric(self):
        a=_eval_event("a",0,0,.01,.20,2.0); b=_eval_event("b",0,0,.20,1.99,2.0)
        self.assertFalse(a.onset_eligible); self.assertTrue(a.offset_eligible)
        self.assertTrue(b.onset_eligible); self.assertFalse(b.offset_eligible)
    def test_aggregate(self):
        rows=[{"x":{"truePositive":2,"falsePositive":1,"falseNegative":1}},{"x":{"truePositive":1,"falsePositive":0,"falseNegative":1}}]
        r=aggregate(rows,"x"); self.assertEqual((r["truePositive"],r["falsePositive"],r["falseNegative"]),(3,1,2))
    def test_repeated_refs(self):
        r=[EvalPitchEvent("a",60,.1,.2,.1,.2,False,False,True,True),EvalPitchEvent("b",60,.3,.4,.3,.4,False,False,True,True)]
        self.assertEqual(repeated_ref_indices(r),{1})
if __name__=="__main__": unittest.main()
