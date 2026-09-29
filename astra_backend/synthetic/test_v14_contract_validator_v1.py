import copy, json, unittest
from pathlib import Path
from astra_backend.synthetic.v14_contract_validator_v1 import summarize, validate
from astra_backend.synthetic import v14_empirical_v1

CONTRACT=Path("docs/astra/V14_MATCHED_CONTEXT_BRIDGE_CONTRACT_V1.json")

class V14ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract=json.loads(CONTRACT.read_text())
    def test_frozen_contract_passes(self):
        self.assertTrue(validate(self.contract)["passed"])
    def test_schedule_identity(self):
        s=summarize()
        self.assertEqual(s["attackGroupCount"],819)
        self.assertEqual(s["gapClassCounts"],{"S":252,"M":225,"L":69})
        self.assertGreaterEqual(s["minimumPostLastAttackMarginSeconds"],.12)
    def test_reject_empirical_authorization(self):
        c=copy.deepcopy(self.contract); c["authorization"]["empiricalRenderingTrainingAuthorized"]=True
        with self.assertRaises(ValueError): validate(c)
    def test_reject_attack_count_drift(self):
        c=copy.deepcopy(self.contract); c["bridge"]["attackGroupsPerPositiveClip"]["repeated"]=6
        with self.assertRaises(ValueError): validate(c)
    def test_reject_gap_total_drift(self):
        c=copy.deepcopy(self.contract); c["bridge"]["gapClassTotals"]["L"]=70
        with self.assertRaises(ValueError): validate(c)
    def test_reject_gate_weakening(self):
        c=copy.deepcopy(self.contract); c["empiricalGate"]["commonF1AtLeast"]=.55
        with self.assertRaises(ValueError): validate(c)
    def test_historical_batch_root_is_frozen(self):
        self.assertEqual(v14_empirical_v1.BATCH_ROOT, 20260927)

    def test_no_execution(self):
        r=validate(self.contract)
        self.assertEqual(r["execution"]["waveformRenders"],0)
        self.assertEqual(r["execution"]["optimizerSteps"],0)
        self.assertEqual(r["execution"]["modelInference"],0)

if __name__=="__main__": unittest.main()
