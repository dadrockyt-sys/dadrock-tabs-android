#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from typing import Any

SHA256_RE=re.compile(r"^[0-9a-f]{64}$")
CATEGORIES=("chords","scales","singlenotes","techniques","music")
ROLES=("lead","rhythm")

def is_sha(v:Any)->bool:
    return isinstance(v,str) and bool(SHA256_RE.fullmatch(v))

def nonempty(v:Any)->bool:
    return isinstance(v,str) and bool(v.strip())

def validate(package:Any)->dict[str,Any]:
    e=[]
    if not isinstance(package,dict):
        return {"contractValid":False,"captureReady":False,"errors":["TOP_LEVEL_OBJECT_REQUIRED"]}
    if package.get("schema")!="astra-guitar-fl-stage-b-precapture-package-v1":
        e.append("SCHEMA_MISMATCH")
    hw=package.get("hardware")
    if not isinstance(hw,dict):
        e.append("HARDWARE_REQUIRED"); hw={}
    if hw.get("clockTopology")!="single_shared_authoritative_hardware_clock_only": e.append("CLOCK_TOPOLOGY_INVALID")
    pa=hw.get("planeA",{})
    if pa.get("sampleRateHz")!=48000 or pa.get("bitDepth")!=24 or pa.get("channels")!=1: e.append("PLANE_A_FORMAT_INVALID")
    if pa.get("fullScaleClippedSamplesMax")!=0: e.append("PLANE_A_CLIP_RULE_INVALID")
    pb=hw.get("planeB",{})
    if pb.get("minScanRateHz",0)<1000 or pb.get("maxTimestampGapMs")!=2.0: e.append("PLANE_B_QA_INVALID")
    pc=hw.get("planeC",{})
    if pc.get("channelsRequired")!=6 or pc.get("missingClockFramesMax")!=0: e.append("PLANE_C_QA_INVALID")
    clock=hw.get("clock",{})
    if clock.get("gapsMax")!=0 or clock.get("duplicatesMax")!=0 or clock.get("strictlyMonotonic") is not True: e.append("CLOCK_QA_INVALID")

    rights=package.get("rightsManifest")
    if not isinstance(rights,dict):
        e.append("RIGHTS_MANIFEST_REQUIRED"); rights={}
    if rights.get("protectedSongsExcluded") is not True: e.append("PROTECTED_SONG_EXCLUSION_REQUIRED")
    if not is_sha(rights.get("contentManifestSha256")): e.append("CONTENT_MANIFEST_SHA_INVALID")
    performers=rights.get("performers")
    if not isinstance(performers,list): performers=[]; e.append("PERFORMERS_REQUIRED")
    if len(performers)<6: e.append("PERFORMER_COUNT_BELOW_MINIMUM")
    pids=set()
    for i,p in enumerate(performers):
        if not isinstance(p,dict): e.append(f"PERFORMER[{i}]_OBJECT_REQUIRED"); continue
        pid=p.get("performerId")
        if not nonempty(pid): e.append(f"PERFORMER[{i}]_ID_REQUIRED")
        elif pid in pids: e.append(f"PERFORMER[{i}]_ID_DUPLICATE")
        else: pids.add(pid)
        for f in ("releaseDocumentSha256",):
            if not is_sha(p.get(f)): e.append(f"PERFORMER[{i}]_{f.upper()}_INVALID")
        for f in ("recordingProductValidationUseGranted","referenceSensorDataUseGranted","internalRetentionGranted"):
            if p.get(f) is not True: e.append(f"PERFORMER[{i}]_{f.upper()}_REQUIRED")

    contents=rights.get("contents")
    if not isinstance(contents,list): contents=[]; e.append("CONTENTS_REQUIRED")
    cids=set()
    allowed={"original_project_composition","public_domain","commissioned_cleared","explicit_rightsholder_grant"}
    for i,c in enumerate(contents):
        if not isinstance(c,dict): e.append(f"CONTENT[{i}]_OBJECT_REQUIRED"); continue
        cid=c.get("contentId")
        if not nonempty(cid): e.append(f"CONTENT[{i}]_ID_REQUIRED")
        elif cid in cids: e.append(f"CONTENT[{i}]_ID_DUPLICATE")
        else: cids.add(cid)
        if c.get("provenanceClass") not in allowed: e.append(f"CONTENT[{i}]_PROVENANCE_INVALID")
        if c.get("protectedSong") is not False: e.append(f"CONTENT[{i}]_PROTECTED_SONG_FORBIDDEN")
        if c.get("productValidationUseGranted") is not True: e.append(f"CONTENT[{i}]_PRODUCT_VALIDATION_GRANT_REQUIRED")
        if not is_sha(c.get("rightsDocumentSha256")): e.append(f"CONTENT[{i}]_RIGHTS_SHA_INVALID")

    plan=package.get("capturePlan")
    if not isinstance(plan,dict):
        e.append("CAPTURE_PLAN_REQUIRED"); plan={}
    slots=plan.get("slots")
    if not isinstance(slots,list): slots=[]; e.append("SLOTS_REQUIRED")
    slotids=set(); cells={}
    for i,s in enumerate(slots):
        if not isinstance(s,dict): e.append(f"SLOT[{i}]_OBJECT_REQUIRED"); continue
        sid=s.get("slotId"); pid=s.get("performerId"); cid=s.get("contentId"); cat=s.get("category"); role=s.get("role")
        if not nonempty(sid): e.append(f"SLOT[{i}]_ID_REQUIRED")
        elif sid in slotids: e.append(f"SLOT[{i}]_ID_DUPLICATE")
        else: slotids.add(sid)
        if pid not in pids: e.append(f"SLOT[{i}]_UNKNOWN_PERFORMER")
        if cid not in cids: e.append(f"SLOT[{i}]_UNKNOWN_CONTENT")
        if cat not in CATEGORIES: e.append(f"SLOT[{i}]_CATEGORY_INVALID")
        if role not in ROLES: e.append(f"SLOT[{i}]_ROLE_INVALID")
        if pid in pids and cat in CATEGORIES: cells[(pid,cat)]=cells.get((pid,cat),0)+1
    if len(slots)<60: e.append("SLOT_COUNT_BELOW_MINIMUM")
    for pid in pids:
        for cat in CATEGORIES:
            if cells.get((pid,cat),0)<2: e.append(f"CELL_BELOW_MINIMUM:{pid}:{cat}")

    for f in ("rightsManifestSha256","hardwareConfigurationSha256","calibrationPackageSha256","referenceDecoderSha256","clockSyncConfigurationSha256"):
        if not is_sha(plan.get(f)): e.append(f"{f.upper()}_INVALID")

    forbidden=package.get("authority",{})
    if forbidden.get("spendingAuthorized") is not False: e.append("SPENDING_MUST_REMAIN_FALSE")
    if forbidden.get("procurementAuthorized") is not False: e.append("PROCUREMENT_MUST_REMAIN_FALSE")
    if forbidden.get("performerContactAuthorized") is not False: e.append("PERFORMER_CONTACT_MUST_REMAIN_FALSE")
    if forbidden.get("captureAuthorized") is not False: e.append("CAPTURE_AUTHORITY_MUST_REMAIN_FALSE")
    if forbidden.get("empiricalExecutionAuthorized") is not False: e.append("EMPIRICAL_AUTHORITY_MUST_REMAIN_FALSE")

    errors=sorted(set(e))
    return {
      "schema":"astra-guitar-fl-stage-b-precapture-validation-v1",
      "contractValid":not errors,
      "captureReady":False,
      "errors":errors,
      "performerCount":len(pids),
      "contentCount":len(cids),
      "slotCount":len(slots),
      "categoryCount":len(CATEGORIES),
      "minimumSlotsRequired":60,
      "realCaptureAuthorized":False,
      "modelInferenceAuthorized":False,
      "referenceScoringAuthorized":False
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--package",required=True); ap.add_argument("--output"); a=ap.parse_args()
    result=validate(json.loads(Path(a.package).read_text()))
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if a.output: Path(a.output).write_text(rendered)
    print(rendered,end="")
    return 0 if result["contractValid"] else 2
if __name__=="__main__": raise SystemExit(main())
