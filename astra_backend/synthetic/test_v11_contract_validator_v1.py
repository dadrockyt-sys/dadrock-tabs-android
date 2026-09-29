import unittest
from astra_backend.synthetic.v11_contract_validator_v1 import ContractError, validate

def fixture():
    return {
      "schema":"astra-v11-state-semantics-contract-v1",
      "status":"frozen-preparation-empirical-execution-not-authorized",
      "durationsSeconds":{"isolated":1.03,"scales":0.27,"chords":0.48,"repeated":0.31,"legatoAttack":0.50,"legatoContinuation":0.74,"palmmute":0.16,"mixedPositive":0.86},
      "identity":{"clips":294,"positiveClips":273,"negativeOnlyClips":21,"attackGroupsEachArm":1638,"attackedNoteLabelsEachArm":1806,
                  "exactAttackedStringFretOnsetIdentity":True,"requireAtLeastOneLegatoContinuation":True,"zeroSameStringOverlap":True,"negativeOnlyUnchanged":True},
      "training":{"models":2,"optimizerStepsPerModel":500,"maxOptimizerStepsTotal":1000,"thresholdSearch":False,"automaticScientificRetries":0},
      "baselineReproduction":{"tolerance":1e-12},
      "supportGate":{"commonPrecisionGainAtLeast":0.15,"commonF1GainAtLeast":0.10},
      "evaluation":{"v2b":False,"realAudio":False},
      "boundaries":{"empiricalExecutionAuthorized":False},
    }

class Tests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate(fixture())["valid"])
    def test_bad_duration(self):
        x=fixture(); x["durationsSeconds"]["isolated"]=1.0
        with self.assertRaises(ContractError): validate(x)
    def test_empirical_arm_rejected(self):
        x=fixture(); x["boundaries"]["empiricalExecutionAuthorized"]=True
        with self.assertRaises(ContractError): validate(x)

if __name__=="__main__": unittest.main()
