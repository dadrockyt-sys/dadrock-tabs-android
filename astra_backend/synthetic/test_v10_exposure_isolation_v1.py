import unittest
import numpy as np

from astra_backend.synthetic.v10_exposure_isolation_v1 import (
    BASELINE_EXPECTED_ATTACKED_NOTE_LABELS,
    TARGET_ATTACKED_NOTE_LABELS,
    TARGET_MULTI_POSITIVE_FRAMES,
    TARGET_POSITIVE_FRAMES,
    TARGET_SINGLE_POSITIVE_FRAMES,
    _target_multi_schedule,
    static_contract_summary,
)


class V10ExposureStaticTests(unittest.TestCase):
    def test_exact_exposure_arithmetic(self):
        self.assertEqual(TARGET_POSITIVE_FRAMES,16000)
        self.assertEqual(TARGET_MULTI_POSITIVE_FRAMES,1851)
        self.assertEqual(TARGET_SINGLE_POSITIVE_FRAMES,14149)
        self.assertEqual(
            TARGET_SINGLE_POSITIVE_FRAMES + 3*TARGET_MULTI_POSITIVE_FRAMES,
            TARGET_ATTACKED_NOTE_LABELS,
        )
        self.assertEqual(TARGET_ATTACKED_NOTE_LABELS,19702)
        self.assertEqual(BASELINE_EXPECTED_ATTACKED_NOTE_LABELS,17676)

    def test_schedule_exactly_500_batches(self):
        s=_target_multi_schedule()
        self.assertEqual(len(s),500)
        self.assertEqual(int(np.sum(s==4)),351)
        self.assertEqual(int(np.sum(s==3)),149)
        self.assertEqual(int(s.sum()),1851)

    def test_static_summary_does_not_authorize_execution(self):
        x=static_contract_summary()
        self.assertEqual(x["optimizerStepsPlanned"],0)
        self.assertFalse(x["modelInferencePlanned"])


if __name__=="__main__":
    unittest.main()
