import copy
import unittest

from .independent_real_development_intake_validator_v1 import (
    IntakeValidationError,
    validate_intake,
)

REQ=[
    "single-note","repeated-attacks","legato","palm-mute",
    "dyad-or-chord","clean-capture","distorted-or-overdriven-capture",
]


def fixture():
    clips=[]
    for i in range(18):
        clips.append({
            "id":f"p{i:02d}",
            "sha256":f"{i+1:064x}",
            "durationSeconds":5.0,
            "kind":"positive",
            "coverage":REQ if i==0 else [],
            "annotations":[{"eventStart":1.0,"pitch":60,"confidence":"high"}],
        })
    for i in range(6):
        clips.append({
            "id":f"n{i:02d}",
            "sha256":f"{100+i:064x}",
            "durationSeconds":5.0,
            "kind":"negative-only",
            "coverage":[],
            "annotations":[],
        })
    return {
        "schema":"astra-independent-real-development-intake-v1",
        "independence":{
            "createdOrSourcedAfterDesignFreeze":True,
            "noP1Overlap":True,"noP2Overlap":True,"noP3Overlap":True,
            "noPreviouslyInspectedOrTunedAudio":True,
            "declaration":"New independent development clips."
        },
        "candidate":{
            "name":"frozen-candidate","weightsSha256":"a"*64,
            "sourceCommit":"deadbeef","modelSourcePath":"m.py",
            "frontendSourcePath":"f.py","evaluatorSourcePath":"e.py",
            "stateThreshold":0.5,"onsetThreshold":0.5
        },
        "clips":clips,
        "summary":{
            "clipCount":24,"positiveClipCount":18,"negativeOnlyClipCount":6,
            "positiveAudioSeconds":90.0,"negativeAudioSeconds":30.0,
            "coverage":REQ
        },
        "annotationsFrozenBeforeInference":True,
        "modelInferenceCount":0,"optimizerSteps":0,
        "p1Accessed":False,"p2Accessed":False,"p3Accessed":False
    }


class TestIntakeValidator(unittest.TestCase):
    def test_valid(self): self.assertTrue(validate_intake(fixture()))
    def test_rejects_old_data(self):
        x=fixture(); x["independence"]["createdOrSourcedAfterDesignFreeze"]=False
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_too_few_clips(self):
        x=fixture(); x["clips"]=x["clips"][:-1]
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_short_negative_duration(self):
        x=fixture(); x["clips"][-1]["durationSeconds"]=4.0; x["summary"]["negativeAudioSeconds"]=29.0
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_missing_coverage(self):
        x=fixture(); x["clips"][0]["coverage"]=REQ[:-1]; x["summary"]["coverage"]=REQ[:-1]
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_post_output_annotation_state(self):
        x=fixture(); x["annotationsFrozenBeforeInference"]=False
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_inference_before_verification(self):
        x=fixture(); x["modelInferenceCount"]=1
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_p3_access(self):
        x=fixture(); x["p3Accessed"]=True
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_threshold_change(self):
        x=fixture(); x["candidate"]["onsetThreshold"]=0.4
        with self.assertRaises(IntakeValidationError): validate_intake(x)
    def test_rejects_summary_mismatch(self):
        x=fixture(); x["summary"]["clipCount"]=25
        with self.assertRaises(IntakeValidationError): validate_intake(x)


if __name__=="__main__":
    unittest.main()
