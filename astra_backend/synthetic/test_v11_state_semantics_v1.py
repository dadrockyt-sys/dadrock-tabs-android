import unittest

from astra_backend.synthetic.v11_state_semantics_v1 import (
    HISTORICAL_ATTACK_DURATION,
    LEGATO_CONTINUATION_DURATION,
    attacked_signature,
    build_state_semantic_template,
)
from astra_backend.synthetic.v9_empirical_v1 import _v9_template

class V11StateSemanticsStaticTests(unittest.TestCase):
    def test_attack_identity_unchanged_across_families(self):
        for family in ("isolated","scales","chords","repeated","legato","palmmute","mixed"):
            for base in (0,1,10,12):
                for variant in (0,2):
                    c=_v9_template(family,base,variant)
                    i=build_state_semantic_template(family,base,variant)
                    self.assertEqual(attacked_signature(c),attacked_signature(i))

    def test_historical_durations_frozen(self):
        self.assertEqual(HISTORICAL_ATTACK_DURATION["isolated"],1.03)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["scales"],0.27)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["chords"],0.48)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["repeated"],0.31)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["legato"],0.50)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["palmmute"],0.16)
        self.assertEqual(HISTORICAL_ATTACK_DURATION["mixed"],0.86)
        self.assertEqual(LEGATO_CONTINUATION_DURATION,0.74)

    def test_legato_restores_nonattacked_continuation_when_room_exists(self):
        found=0
        for base in range(14):
            for variant in range(3):
                t=build_state_semantic_template("legato",base,variant)
                found += sum(not x.get("attack",True) for x in t["segments"])
        self.assertGreater(found,0)

    def test_no_same_string_overlap(self):
        for family in ("isolated","scales","chords","repeated","legato","palmmute","mixed"):
            for base in range(14):
                for variant in range(3):
                    t=build_state_semantic_template(family,base,variant)
                    for s in range(6):
                        rows=sorted([x for x in t["segments"] if x["string"]==s],key=lambda x:x["start"])
                        for a,b in zip(rows,rows[1:]):
                            self.assertLessEqual(a["end"],b["start"]+1e-12)

if __name__=="__main__":
    unittest.main()
