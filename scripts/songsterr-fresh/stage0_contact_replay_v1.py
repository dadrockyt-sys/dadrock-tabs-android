#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any, Mapping

SOURCES=("configuration","fixture","scanLog")
CONFIG_CONTRACT="songsterr-fresh-purpose-built-stage0-contact-configuration-v1"
FIXTURE_CONTRACT="songsterr-fresh-purpose-built-stage0-contact-fixture-v1"
SCAN_CONTRACT="songsterr-fresh-purpose-built-stage0-contact-scan-log-v1"
RESULT_CONTRACT="songsterr-fresh-purpose-built-stage0-contact-replay-v1"
STAGE="NON_HOLDOUT_STAGE0"
ENCODING="BINARY_CONTACT_VECTOR_V1"
BLOCKERS=("invalidConfigurationDeclarationCount","sourceSha256MismatchCount","invalidFixtureDeclarationCount","invalidScanLogDeclarationCount","sequenceViolationCount","nonmonotonicTickCount","driveStringMismatchCount","missingExpectedContactCount","unexpectedContactCount","healthStatusViolationCount","forbiddenAudioOrModelProvenanceCount")

def canonical_json(v:Any)->str:return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha256_bytes(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def _str(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def _int(v:Any)->bool:return isinstance(v,int) and not isinstance(v,bool)
def _blockers()->dict[str,int]:return {k:0 for k in BLOCKERS}
def _auth()->dict[str,Any]:return {"basicPitchAuthorized":False,"v6Authorized":False,"correctnessAuthorized":False,"modelValidationComplete":False,"customerEligibleEvents":0,"mayAdvanceDelivery":False}
def _prov(o:Mapping[str,Any],fields:tuple[str,...])->int:return sum(o.get(f) is not False for f in fields)

def _result(*,ok:bool,b:Mapping[str,int],hashes:Mapping[str,Any],errors:list[str],cycles:int=0,decoded:list[dict[str,Any]]|None=None)->dict[str,Any]:
    decoded=decoded or []
    return {"contract":RESULT_CONTRACT,"stage0ReplayContractValid":ok,"stage0ContactTopologyReplayPass":ok,"sourceSha256":dict(hashes),"decodedCycleCount":cycles,"decodedStringStateCount":len(decoded),"decodedStateSha256":sha256_bytes(canonical_json(decoded).encode()) if decoded else None,"blockerCounts":dict(b),"errors":sorted(set(errors)),**_auth()}

def audit_raw_sources(*,raw_sources:Mapping[str,bytes],expected_sha256:Mapping[str,str])->dict[str,Any]:
    b=_blockers(); errors=[]; required=set(SOURCES); raw=set(raw_sources); exp=set(expected_sha256)
    errors += [f"MISSING_SOURCE:{n}" for n in sorted(required-raw)]
    errors += [f"EXTRA_SOURCE:{n}" for n in sorted(raw-required)]
    errors += [f"MISSING_EXPECTED_SHA256:{n}" for n in sorted(required-exp)]
    errors += [f"EXTRA_EXPECTED_SHA256:{n}" for n in sorted(exp-required)]
    errors += [f"SOURCE_NOT_BYTES:{n}" for n in sorted(required&raw) if not isinstance(raw_sources[n],bytes)]
    if errors:b["sourceSha256MismatchCount"]=len(errors);return _result(ok=False,b=b,hashes={},errors=errors)
    report={}; mismatches=0
    for n in SOURCES:
        actual=sha256_bytes(raw_sources[n]); expected=expected_sha256[n]
        valid=isinstance(expected,str) and len(expected)==64 and all(c in "0123456789abcdefABCDEF" for c in expected)
        match=bool(valid and actual==expected.lower()); report[n]={"expected":expected,"actual":actual,"matches":match}
        if not match:mismatches+=1;errors.append(f"SOURCE_SHA256_MISMATCH:{n}")
    if mismatches:b["sourceSha256MismatchCount"]=mismatches;return _result(ok=False,b=b,hashes=report,errors=errors)
    parsed={}
    for n in SOURCES:
        try:parsed[n]=json.loads(raw_sources[n].decode("utf-8"))
        except (UnicodeDecodeError,json.JSONDecodeError) as e:errors.append(f"INVALID_JSON:{n}:{type(e).__name__}")
    if errors:b["invalidConfigurationDeclarationCount"]=len(errors);return _result(ok=False,b=b,hashes=report,errors=errors)
    return _audit(parsed["configuration"],parsed["fixture"],parsed["scanLog"],report)

def _audit(cfg:Any,fixture:Any,scan:Any,hashes:Mapping[str,Any])->dict[str,Any]:
    b=_blockers(); errors=[]; phase=[1,2,3,4,5,6]; frets=[]
    cfg_ok=isinstance(cfg,dict)
    if cfg_ok:
        frets=cfg.get("fretNumbers") if isinstance(cfg.get("fretNumbers"),list) else []
        checks=(cfg.get("contract")==CONFIG_CONTRACT,_str(cfg.get("configurationId")),_str(cfg.get("loggerFirmwareId")),_str(cfg.get("topologyId")),cfg.get("stage")==STAGE,cfg.get("stringCount")==6 and not isinstance(cfg.get("stringCount"),bool),bool(frets) and all(_int(x) and 1<=x<=36 for x in frets) and frets==sorted(set(frets)),cfg.get("phaseOrder")==phase,cfg.get("sampleEncoding")==ENCODING)
        p=_prov(cfg,("usedEvaluatedAudio","usedModelOutputs","derivedFromEvaluatedAudio"));b["forbiddenAudioOrModelProvenanceCount"]+=p
        if p:errors.append("FORBIDDEN_PROVENANCE:configuration")
        cfg_ok=all(checks)
    if not cfg_ok:b["invalidConfigurationDeclarationCount"]+=1;errors.append("INVALID_CONFIGURATION_DECLARATION")

    cycles=[]; fixture_ok=isinstance(fixture,dict)
    if fixture_ok:
        cycles=fixture.get("cycles") if isinstance(fixture.get("cycles"),list) else []
        checks=(fixture.get("contract")==FIXTURE_CONTRACT,_str(fixture.get("fixtureId")),cfg_ok and fixture.get("configurationId")==cfg.get("configurationId"),cfg_ok and fixture.get("topologyId")==cfg.get("topologyId"),fixture.get("stage")==STAGE,bool(cycles))
        p=_prov(fixture,("usedEvaluatedAudio","usedModelOutputs"));b["forbiddenAudioOrModelProvenanceCount"]+=p
        if p:errors.append("FORBIDDEN_PROVENANCE:fixture")
        fixture_ok=all(checks)
    if not fixture_ok:b["invalidFixtureDeclarationCount"]+=1;errors.append("INVALID_FIXTURE_DECLARATION")

    expected={}
    if fixture_ok:
        for ci,c in enumerate(cycles):
            if not isinstance(c,dict) or c.get("cycleSequence")!=ci or not isinstance(c.get("strings"),list):b["sequenceViolationCount"]+=1;errors.append(f"INVALID_FIXTURE_CYCLE:{ci}");continue
            rows=c["strings"]
            if len(rows)!=6:b["invalidFixtureDeclarationCount"]+=1;errors.append(f"INVALID_FIXTURE_STRING_COUNT:{ci}");continue
            for sn,row in enumerate(rows,1):
                if not isinstance(row,dict) or row.get("stringNumber")!=sn:b["sequenceViolationCount"]+=1;errors.append(f"INVALID_FIXTURE_STRING_ORDER:{ci}:{sn}");continue
                active=row.get("expectedActiveFrets")
                if not(isinstance(active,list) and all(_int(x) and x in frets for x in active) and active==sorted(set(active))):b["invalidFixtureDeclarationCount"]+=1;errors.append(f"INVALID_EXPECTED_FRETS:{ci}:{sn}");continue
                expected[(ci,sn)]=active

    records=[]; scan_ok=isinstance(scan,dict)
    if scan_ok:
        records=scan.get("records") if isinstance(scan.get("records"),list) else []
        checks=(scan.get("contract")==SCAN_CONTRACT,_str(scan.get("loggerId")),cfg_ok and scan.get("configurationId")==cfg.get("configurationId"),cfg_ok and scan.get("topologyId")==cfg.get("topologyId"),fixture_ok and scan.get("fixtureId")==fixture.get("fixtureId"),scan.get("stage")==STAGE,_str(scan.get("clockDomainId")),bool(records))
        p=_prov(scan,("usedEvaluatedAudio","usedModelOutputs","derivedFromEvaluatedAudio"));b["forbiddenAudioOrModelProvenanceCount"]+=p
        if p:errors.append("FORBIDDEN_PROVENANCE:scanLog")
        scan_ok=all(checks)
    if not scan_ok:b["invalidScanLogDeclarationCount"]+=1;errors.append("INVALID_SCAN_LOG_DECLARATION")

    decoded=[]; keys=[]; last_tick=None
    if scan_ok:
        for i,r in enumerate(records):
            if not isinstance(r,dict):b["invalidScanLogDeclarationCount"]+=1;errors.append(f"INVALID_SCAN_RECORD:{i}");continue
            ci,ps,tick,sn,raw,status=(r.get("cycleSequence"),r.get("phaseSequence"),r.get("tick"),r.get("driveStringNumber"),r.get("rawSenseValues"),r.get("healthStatus"))
            valid=_int(ci) and ci>=0 and _int(ps) and 0<=ps<=5 and _int(tick) and tick>=0 and isinstance(raw,list) and len(raw)==len(frets) and all(_int(x) and x in (0,1) for x in raw)
            if not valid:b["invalidScanLogDeclarationCount"]+=1;errors.append(f"INVALID_SCAN_RECORD_FIELDS:{i}");continue
            if sn!=phase[ps]:b["driveStringMismatchCount"]+=1;errors.append(f"DRIVE_STRING_MISMATCH:{i}")
            if last_tick is not None and tick<=last_tick:b["nonmonotonicTickCount"]+=1;errors.append(f"NONMONOTONIC_TICK:{i}")
            last_tick=tick
            if status!="OK":b["healthStatusViolationCount"]+=1;errors.append(f"HEALTH_STATUS_VIOLATION:{i}")
            keys.append((ci,ps)); obs=[frets[j] for j,x in enumerate(raw) if x==1]
            state="OPEN" if not obs else "UNAMBIGUOUS_FRET" if len(obs)==1 else "AMBIGUOUS_MULTI_CONTACT"
            decoded.append({"cycleSequence":ci,"phaseSequence":ps,"stringNumber":sn,"tick":tick,"observedActiveFrets":obs,"stateClass":state})
        wanted=[(ci,ps) for ci in range(len(cycles) if fixture_ok else 0) for ps in range(6)]
        if keys!=wanted:
            b["sequenceViolationCount"]+=sum(1 for i in range(max(len(keys),len(wanted))) if (keys[i] if i<len(keys) else None)!=(wanted[i] if i<len(wanted) else None));errors.append("SCAN_SEQUENCE_VIOLATION")

    for row in decoded:
        key=(row["cycleSequence"],row["stringNumber"])
        if key not in expected:continue
        exp,obs=set(expected[key]),set(row["observedActiveFrets"])
        b["missingExpectedContactCount"]+=len(exp-obs);b["unexpectedContactCount"]+=len(obs-exp)
    if b["missingExpectedContactCount"]:errors.append("MISSING_EXPECTED_CONTACT")
    if b["unexpectedContactCount"]:errors.append("UNEXPECTED_CONTACT")
    ok=not errors and all(v==0 for v in b.values())
    return _result(ok=ok,b=b,hashes=hashes,errors=errors,cycles=len(cycles) if fixture_ok else 0,decoded=decoded)

def parse_args()->argparse.Namespace:
    p=argparse.ArgumentParser(description="Validate frozen Stage-0 NON_HOLDOUT contact replay evidence.")
    for n in ("configuration","fixture","scan-log"):p.add_argument(f"--{n}",required=True);p.add_argument(f"--{n}-sha256",required=True)
    p.add_argument("--output");return p.parse_args()

def main()->int:
    a=parse_args(); raw={"configuration":Path(a.configuration).read_bytes(),"fixture":Path(a.fixture).read_bytes(),"scanLog":Path(a.scan_log).read_bytes()}; exp={"configuration":a.configuration_sha256,"fixture":a.fixture_sha256,"scanLog":a.scan_log_sha256}
    r=audit_raw_sources(raw_sources=raw,expected_sha256=exp); text=canonical_json(r)+"\n"
    if a.output:Path(a.output).write_text(text,encoding="utf-8")
    print(text,end="");return 0 if r["stage0ContactTopologyReplayPass"] else 2
if __name__=="__main__":raise SystemExit(main())
