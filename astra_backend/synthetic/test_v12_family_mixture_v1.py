import unittest
from astra_backend.synthetic.v12_family_mixture_v1 import (
    HISTORICAL_TRAIN_POSITIVE_COUNTS,TARGET_SLOTS,TOTAL_POSITIVE_SLOTS,static_summary
)

class V12StaticTests(unittest.TestCase):
    def test_historical_total(self):
        self.assertEqual(sum(HISTORICAL_TRAIN_POSITIVE_COUNTS.values()),525)
    def test_exact_target_slots(self):
        self.assertEqual(sum(TARGET_SLOTS.values()),16000)
        self.assertEqual(TOTAL_POSITIVE_SLOTS,16000)
        self.assertEqual(TARGET_SLOTS,{"isolated":914,"scales":3657,"chords":1829,"repeated":3657,"legato":914,"palmmute":4572,"mixed":457})
    def test_static_is_model_free(self):
        x=static_summary()
        self.assertEqual(x["optimizerSteps"],0)
        self.assertEqual(x["modelsTrained"],0)
        self.assertEqual(x["modelInference"],0)
        self.assertEqual(x["waveformsRendered"],0)
        self.assertEqual(x["v2bInference"],0)

if __name__=="__main__": unittest.main()
