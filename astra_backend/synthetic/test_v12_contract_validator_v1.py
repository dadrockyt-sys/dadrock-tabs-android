import unittest
from astra_backend.synthetic.v12_contract_validator_v1 import ContractError, validate

def fixture():
    return {
      "schema":"astra-v12-family-mixture-contract-v1",
      "status":"frozen-preparation-empirical-execution-not-authorized",
      "targetPositiveSlots":{"isolated":914,"scales":3657,"chords":1829,"repeated":3657,"legato":914,"palmmute":4572,"mixed":457,"total":16000},
      "expectedV9PositivePools":{"total":1170},
      "fixed":{"models":2,"optimizerStepsPerModel":500,"maxOptimizerStepsTotal":1000,"thresholdSearch":False,"automaticScientificRetries":0},
      "boundaries":{"empiricalExecutionAuthorized":False}
    }

class Tests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate(fixture())["valid"])
    def test_bad_total(self):
        x=fixture(); x["targetPositiveSlots"]["isolated"]=913
        with self.assertRaises(ContractError): validate(x)
    def test_armed_rejected(self):
        x=fixture(); x["boundaries"]["empiricalExecutionAuthorized"]=True
        with self.assertRaises(ContractError): validate(x)
if __name__=="__main__": unittest.main()
