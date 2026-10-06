#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("v",HERE/"guitar_fl_stage_b_precapture_validator_v1.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
SHA="a"*64

def valid_package():
    performers=[{
      "performerId":f"p{i}","releaseDocumentSha256":SHA,
      "recordingProductValidationUseGranted":True,
      "referenceSensorDataUseGranted":True,"internalRetentionGranted":True
    } for i in range(6)]
    contents=[]
    slots=[]
    n=0
    for pi,p in enumerate(performers):
      for cat in mod.CATEGORIES:
        cid=f"c-{pi}-{cat}"
        contents.append({
          "contentId":cid,"provenanceClass":"original_project_composition",
          "protectedSong":False,"productValidationUseGranted":True,
          "rightsDocumentSha256":SHA
        })
        for k in range(2):
          slots.append({
            "slotId":f"s{n}","performerId":p["performerId"],"contentId":cid,
            "category":cat,"role":"lead" if k==0 else "rhythm"
          }); n+=1
    return {
      "schema":"astra-guitar-fl-stage-b-precapture-package-v1",
      "hardware":{
        "clockTopology":"single_shared_authoritative_hardware_clock_only",
        "planeA":{"sampleRateHz":48000,"bitDepth":24,"channels":1,"fullScaleClippedSamplesMax":0},
        "planeB":{"minScanRateHz":1000,"maxTimestampGapMs":2.0},
        "planeC":{"channelsRequired":6,"missingClockFramesMax":0},
        "clock":{"gapsMax":0,"duplicatesMax":0,"strictlyMonotonic":True}
      },
      "rightsManifest":{"protectedSongsExcluded":True,"contentManifestSha256":SHA,"performers":performers,"contents":contents},
      "capturePlan":{
        "slots":slots,"rightsManifestSha256":SHA,"hardwareConfigurationSha256":SHA,
        "calibrationPackageSha256":SHA,"referenceDecoderSha256":SHA,"clockSyncConfigurationSha256":SHA
      },
      "authority":{"spendingAuthorized":False,"procurementAuthorized":False,"performerContactAuthorized":False,"captureAuthorized":False,"empiricalExecutionAuthorized":False}
    }

class Tests(unittest.TestCase):
    def test_valid_precapture_package_passes_but_never_authorizes_capture(self):
        r=mod.validate(valid_package())
        self.assertTrue(r["contractValid"],r)
        self.assertFalse(r["captureReady"])
        self.assertEqual(r["slotCount"],60)
        self.assertFalse(r["realCaptureAuthorized"])

    def test_missing_rights_grant_fails(self):
        x=valid_package(); x["rightsManifest"]["performers"][0]["recordingProductValidationUseGranted"]=False
        r=mod.validate(x)
        self.assertFalse(r["contractValid"])
        self.assertTrue(any("PRODUCTVALIDATION" in e.replace("_","") for e in r["errors"]))

    def test_protected_content_fails(self):
        x=valid_package(); x["rightsManifest"]["contents"][0]["protectedSong"]=True
        r=mod.validate(x)
        self.assertIn("CONTENT[0]_PROTECTED_SONG_FORBIDDEN",r["errors"])

    def test_cell_balance_is_hard_gate(self):
        x=valid_package(); x["capturePlan"]["slots"]=x["capturePlan"]["slots"][1:]
        r=mod.validate(x)
        self.assertFalse(r["contractValid"])
        self.assertTrue(any(e.startswith("CELL_BELOW_MINIMUM:") for e in r["errors"]))

    def test_separate_clock_topology_is_rejected(self):
        x=valid_package(); x["hardware"]["clockTopology"]="separate_clocks_with_fit"
        self.assertIn("CLOCK_TOPOLOGY_INVALID",mod.validate(x)["errors"])

    def test_any_attempt_to_enable_capture_authority_fails(self):
        for field in ("spendingAuthorized","procurementAuthorized","performerContactAuthorized","captureAuthorized","empiricalExecutionAuthorized"):
            with self.subTest(field=field):
                x=valid_package(); x["authority"][field]=True
                self.assertFalse(mod.validate(x)["contractValid"])

if __name__=="__main__": unittest.main()
