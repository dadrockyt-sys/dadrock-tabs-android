import unittest
import numpy as np

from evaluation.p1_p2_activation_diagnostic_v1 import (
    _classify, summarize_array
)


class ActivationDiagnosticTests(unittest.TestCase):
    def test_summary_is_finite_and_exact_for_simple_array(self):
        x=np.array([[0.0,2.0],[-2.0,0.0]],dtype=np.float32)
        s=summarize_array(x)
        self.assertEqual(s["count"],4)
        self.assertEqual(s["mean"],0.0)
        self.assertEqual(s["absMean"],1.0)
        self.assertAlmostEqual(s["l2Rms"],np.sqrt(2.0))

    def test_classifies_both_head_collapse(self):
        probes=[
            {"windowAnyOnsetPass":False,"windowAnyTrueStatePass":False,"windowAnyJointTrueAdmission":False},
            {"windowAnyOnsetPass":False,"windowAnyTrueStatePass":False,"windowAnyJointTrueAdmission":False},
        ]
        self.assertEqual(_classify(probes),"both_heads_or_representation_domain_collapse")

    def test_classifies_onset_only_failure(self):
        probes=[{"windowAnyOnsetPass":False,"windowAnyTrueStatePass":True,"windowAnyJointTrueAdmission":False}]
        self.assertEqual(_classify(probes),"onset_head_generalization_failure")

    def test_classifies_state_only_failure(self):
        probes=[{"windowAnyOnsetPass":True,"windowAnyTrueStatePass":False,"windowAnyJointTrueAdmission":False}]
        self.assertEqual(_classify(probes),"state_head_or_representation_failure")

    def test_classifies_joint_misalignment(self):
        probes=[
            {"windowAnyOnsetPass":True,"windowAnyTrueStatePass":True,"windowAnyJointTrueAdmission":False}
        ]
        self.assertEqual(_classify(probes),"onset_state_admission_misalignment")


if __name__=="__main__":
    unittest.main()
