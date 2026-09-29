import unittest
from astra_backend.synthetic.v13_active_nononset_mixture_v1 import TARGET_SLOTS,TOTAL_ACTIVE_SLOTS,static_summary

class V13StaticTests(unittest.TestCase):
    def test_exact_target_slots(self):
        self.assertEqual(sum(TARGET_SLOTS.values()),16000)
        self.assertEqual(TOTAL_ACTIVE_SLOTS,16000)
        self.assertEqual(TARGET_SLOTS,{"isolated":2511,"scales":2569,"chords":2219,"repeated":2861,"legato":3037,"palmmute":1752,"mixed":1051})
    def test_static_is_model_free(self):
        x=static_summary()
        self.assertEqual(x["optimizerSteps"],0)
        self.assertEqual(x["modelsTrained"],0)
        self.assertEqual(x["modelInference"],0)
        self.assertEqual(x["waveformsRendered"],0)
        self.assertEqual(x["v2bInference"],0)

if __name__=="__main__": unittest.main()
