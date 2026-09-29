import copy, unittest
from astra_backend.synthetic.v10_contract_validator_v1 import ContractError, validate

def fixture():
    return {
      "schema":"astra-v10-exposure-isolation-contract-v1",
      "status":"frozen-preparation-empirical-execution-not-authorized",
      "fixed":{"models":2,"optimizerStepsPerModel":500,"maxOptimizerStepsTotal":1000,
               "positiveOnsetSlotsPerBatch":32,"positiveOnsetSlotsTotal":16000,
               "thresholdSearch":False,"automaticScientificRetries":0},
      "interventionExposure":{"targetSampledAttackedNoteLabels":19702,
                              "targetMultiLabelPositiveFrames":1851,
                              "targetSingleLabelPositiveFrames":14149,
                              "batchesWith4MultiFrames":351,"batchesWith3MultiFrames":149},
      "reproductionGate":{"controlSampledAttackedNoteLabelsExactly":17676},
      "supportGate":{"balancedSampledAttackedNoteLabelsExactly":19702,
                     "controlSampledAttackedNoteLabelsExactly":17676},
      "boundaries":{"empiricalExecutionAuthorized":False}
    }

class Tests(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate(fixture())["valid"])
    def test_bad_target(self):
        x=fixture(); x["interventionExposure"]["targetSampledAttackedNoteLabels"]=19701
        with self.assertRaises(ContractError): validate(x)
    def test_armed_rejected(self):
        x=fixture(); x["boundaries"]["empiricalExecutionAuthorized"]=True
        with self.assertRaises(ContractError): validate(x)

if __name__=="__main__":
    unittest.main()
