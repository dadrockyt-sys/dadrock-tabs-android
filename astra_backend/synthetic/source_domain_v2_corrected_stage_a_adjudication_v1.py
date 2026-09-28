#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

SCHEMA="astra-source-domain-v2-corrected-stage-a-adjudication-result-v1"
CONTROL_SHA="16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894"
MANIFEST_SHA="2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"

RETAIN=(
 "deterministicRerenderIdentity","stateIdentity","onsetIdentity","referenceIdentity",
 "finiteAudioAndFeatures","peakUnder0_999","noUnlabeledTransientInjection",
 "cqtChangedEveryPositiveSelectedRow","manifestBindingExact","selectedRowsExact",
 "renderCeiling","audioSecondsCeiling","wallTimeCeiling"
)

def adjudicate(stage_a_path, isolated_path, out_path):
    a=json.loads(Path(stage_a_path).read_text())
    i=json.loads(Path(isolated_path).read_text())
    if a["schema"]!="astra-source-domain-v2-stage-a-result-v1":
        raise RuntimeError("wrong Stage-A frozen summary")
    if i["schema"]!="astra-source-domain-v2-source-isolating-pitch-result-v1":
        raise RuntimeError("wrong isolated-pitch frozen summary")
    if a["frozenInputs"]["controlSha256"]!=CONTROL_SHA or i["frozenInputs"]["controlSha256"]!=CONTROL_SHA:
        raise RuntimeError("control identity mismatch")
    if a["frozenInputs"]["manifestContentSha256"]!=MANIFEST_SHA or i["frozenInputs"]["manifestContentSha256"]!=MANIFEST_SHA:
        raise RuntimeError("manifest identity mismatch")

    ac=a["scientificGate"]["criteria"]
    retained={k:bool(ac[k]) for k in RETAIN}
    iso=i["summary"]
    replacement={
      "isolatedAdmissionPassed":bool(iso["admissionPassed"]),
      "allIsolatedMeasurableWithin15Cents":bool(iso["criteria"]["allIsolatedMeasurableWithin15Cents"]),
      "allOriginalMeasurableEventsRetained":bool(iso["criteria"]["allOriginalMeasurableEventsRetained"]),
      "originalMeasurableEventsExactly86":int(iso["originalMeasurableEvents"])==86,
      "isolatedMeasurableEventsExactly86":int(iso["isolatedMeasurableEvents"])==86,
      "missingOriginalMeasurableEventsZero":int(iso["missingOriginalMeasurableEvents"])==0,
      "outside15CentsZero":int(iso["outside15Cents"])==0,
      "maxAbsoluteIsolatedCentsAtMost15":float(iso["maxAbsoluteIsolatedCents"])<=15.0,
    }
    passed=all(retained.values()) and all(replacement.values())
    result={
      "schema":SCHEMA,
      "status":"passed" if passed else "failed",
      "originalStageAFailurePreserved":True,
      "frozenIdentities":{"controlSha256":CONTROL_SHA,"manifestContentSha256":MANIFEST_SHA},
      "retainedOriginalCriteria":retained,
      "replacementPitchCriteria":replacement,
      "correctedStageAPassed":passed,
      "execution":{
        "waveformRenders":0,"audioSeconds":0,"modelLoads":0,"modelInference":False,
        "optimizerSteps":0,"thresholdWork":False,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "automaticRetry":False,"productionMutation":False
      },
      "nextAction":"model-free-stage-b-preparation-and-coverage-only" if passed else "freeze-and-stop"
    }
    Path(out_path).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("CORRECTED_STAGE_A="+json.dumps(result,sort_keys=True))
    if not passed: raise SystemExit("corrected Stage-A adjudication failed")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage-a",required=True)
    ap.add_argument("--isolated",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    adjudicate(a.stage_a,a.isolated,a.out)

if __name__=="__main__":
    main()
