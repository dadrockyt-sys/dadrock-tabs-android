import copy, unittest
from astra_backend.synthetic.v9_empirical_v1 import (
    GAP_CLASSES, POSITIVE_COUNTS, SUPPORTS, FIRST, FINAL_MARGIN,
    attack_times, make_timing, timing_distance, verify,
)

class V9EmpiricalStaticTests(unittest.TestCase):
    def test_supports_fit_all_families(self):
        for family,classes in GAP_CLASSES.items():
            worst=FIRST[1]+FINAL_MARGIN+sum(SUPPORTS[k][1] for k in classes)
            self.assertLess(worst,4.0)

    def test_attack_times_are_deterministic_and_in_bounds(self):
        a,g=attack_times("palmmute",0,0); b,h=attack_times("palmmute",0,0)
        self.assertEqual(a,b); self.assertEqual(g,h)
        self.assertEqual(len(a),10)
        self.assertTrue(all(0<=x<4 for x in a))
        self.assertLess(a[-1]+FINAL_MARGIN,4.0)

    def test_mixed_negative_has_no_attacks(self):
        a,g=attack_times("mixed",0,0)
        self.assertEqual(a,[]); self.assertEqual(g,[])

    def test_attack_total(self):
        total=sum((42 if f!="mixed" else 21)*POSITIVE_COUNTS[f] for f in POSITIVE_COUNTS)
        self.assertEqual(total,1638)

    def test_gap_total(self):
        total=sum((42 if f!="mixed" else 21)*len(GAP_CLASSES[f]) for f in GAP_CLASSES)
        self.assertEqual(total,1365)

if __name__=="__main__":
    unittest.main()
