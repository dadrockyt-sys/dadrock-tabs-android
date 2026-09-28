import unittest
import numpy as np
from evaluation.synthetic_real_domain_diagnostic_v1 import _quantiles, centroid_distance

class DomainDiagnosticTests(unittest.TestCase):
    def test_quantiles_finite(self):
        r=_quantiles(np.array([0.,1.,2.,3.]))
        self.assertEqual(r["count"],4)
        self.assertAlmostEqual(r["mean"],1.5)

    def test_centroid_identity(self):
        r=centroid_distance([1,2,3],[1,2,3])
        self.assertAlmostEqual(r["l2"],0.0)
        self.assertAlmostEqual(r["cosineDistance"],0.0)

    def test_centroid_shift(self):
        r=centroid_distance([1,0],[0,1])
        self.assertGreater(r["l2"],0)
        self.assertAlmostEqual(r["cosineSimilarity"],0.0)

if __name__=="__main__": unittest.main()
