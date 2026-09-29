import unittest
from astra_backend.synthetic.v13_contract_validator_v1 import ContractError, validate

def fixture():
    return {
      "schema":"astra-v13-active-nononset-mixture-contract-v1",
      "status":"frozen-preparation-empirical-execution-not-authorized",
      "targetActiveNonOnsetSlots":{"isolated":2511,"scales":2569,"chords":2219,"repeated":2861,"legato":3037,"palmmute":1752,"mixed":1051,"total":16000},
      "expectedV9ActiveNonOnsetPools":{"total":10444},
      "fixed":{"models":2,"optimizerStepsPerModel":500,"maxOptimizerStepsTotal":1000,"thresholdSearch":False,"automaticScientificRetries":0},
      "identity":{"positiveOnsetSelectionsIdentical":True,"negativeStructureInactiveSelectionsIdentical":True,"otherInactiveSelectionsIdentical":True,"samePerStepPermutation":True,"attackedNoteLabelExposureIdentical":True},
      "evaluation":{"v2b":False,"realAudio":False},
      "boundaries":{"empiricalExecutionAuthorized":False}
    }

class Tests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate(fixture())["valid"])
    def test_bad_target(self):
        x=fixture(); x["targetActiveNonOnsetSlots"]["isolated"]=2510
        with self.assertRaises(ContractError): validate(x)
    def test_empirical_rejected(self):
        x=fixture(); x["boundaries"]["empiricalExecutionAuthorized"]=True
        with self.assertRaises(ContractError): validate(x)
if __name__=="__main__": unittest.main()
