import unittest

from astra_backend.synthetic.v9_final_contract_validator_v1 import (
    ContractError,
    timing_distance,
    validate,
)


def fixture():
    return {
        "schema":"astra-v9-final-empirical-contract-v1",
        "status":"frozen-execution-not-authorized",
        "reference":{
            "v2b":{"density":1.4905949321256224,"ioiP50":0.256,"ioiP90":0.882358,"repeat250":0.47019867549668876,"longGap700":0.12582781456953643},
            "v8L0CommonUnit":{"density":1.3461538461538463,"ioiP50":0.36,"ioiP90":0.4,"repeat250":0.0,"longGap700":0.09090909090909091,"timingDistanceV1":1.6103247395960165}
        },
        "intervention":{
            "clipSeconds":4.0,"positiveSeconds":1092,"attackGroupCount":1638,"attackGroupDensity":1.5,
            "attackedNoteLabelCount":1806,"firstAttackSupportSeconds":[0.05,0.12],"finalMarginSeconds":0.12,
            "sustainSupportSeconds":[0.12,0.48],
            "attackGroupsPerPositiveClip":{"isolated":5,"scales":8,"chords":2,"repeated":8,"legato":4,"palmmute":10,"mixed":4},
            "gapClasses":{"S":{"supportSeconds":[0.08,0.25]},"M":{"supportSeconds":[0.251,0.316]},"L":{"supportSeconds":[0.7,1.36]}},
            "gapClassMultisets":{
                "isolated":["S","S","S","M"],
                "scales":["S","S","S","M","M","M","L"],
                "chords":["M"],
                "repeated":["S","S","S","M","M","M","L"],
                "legato":["S","M","L"],
                "palmmute":["S","S","S","S","M","M","M","M","L"],
                "mixed":["S","S","L"]
            },
            "aggregateGapClassCounts":{"S":630,"M":546,"L":189,"total":1365},
            "aggregateGapClassFractions":{"S":630/1365,"M":546/1365,"L":189/1365}
        },
        "v9aGate":{
            "maxAdvancingArms":1,"attackGroupCountExactly":1638,"attackedNoteLabelCountExactly":1806,
            "infeasibleClipCountExactly":0,"invalidLabelCountExactly":0,"invalidOffsetCountExactly":0,"fallbackOperationCountExactly":0
        },
        "training":{"models":2,"optimizerStepsPerModel":500,"maxOptimizerStepsTotal":1000,"stateThreshold":0.5,"onsetThreshold":0.5},
        "launch":{"armed":False},
        "boundaries":{"executionAuthorized":False}
    }


class FinalContractValidatorTests(unittest.TestCase):
    def test_frozen_fixture_validates(self):
        out = validate(fixture())
        self.assertTrue(out["valid"])
        self.assertEqual(out["attackGroupCount"], 1638)
        self.assertEqual(out["attackedNoteLabelCount"], 1806)
        self.assertLess(out["worstCaseFamilySeconds"]["palmmute"], 4.0)

    def test_baseline_distance_is_frozen_value(self):
        f=fixture()
        self.assertAlmostEqual(timing_distance(f["reference"]["v8L0CommonUnit"], f["reference"]["v2b"]), 1.6103247395960165)

    def test_wrong_group_count_rejected(self):
        f=fixture(); f["intervention"]["attackGroupCount"]=1637
        with self.assertRaises(ContractError): validate(f)

    def test_overlapping_gap_support_rejected(self):
        f=fixture(); f["intervention"]["gapClasses"]["M"]["supportSeconds"][0]=0.25
        with self.assertRaises(ContractError): validate(f)

    def test_unfit_support_rejected(self):
        f=fixture(); f["intervention"]["gapClasses"]["L"]["supportSeconds"][1]=2.0
        with self.assertRaises(ContractError): validate(f)

    def test_armed_launch_rejected(self):
        f=fixture(); f["launch"]["armed"]=True
        with self.assertRaises(ContractError): validate(f)


if __name__ == "__main__":
    unittest.main()
