#!/usr/bin/env python3
"""Deterministic parameter-manifest generator for source-domain joint coverage V2.

No waveform rendering, model loading, inference, optimizer, or real-data access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

SCHEMA="astra-source-domain-joint-coverage-manifest-v2"
ROOT="astra-source-domain-joint-v2"
EXPECTED_CONTROL_SHA256="16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894"
FAMILIES=("isolated","scales","chords","repeated","legato","palmmute","mixed")
AXES={
 "attackBaseRiseSeconds":("log_uniform",.0015,.050),
 "transientNoiseGain":("uniform",0.0,.20),
 "transientDecaySeconds":("log_uniform",.003,.020),
 "dampingMultiplier":("log_uniform",.60,1.80),
 "brightness":("uniform",.55,.92),
 "pickPosition":("uniform",.08,.48),
 "lowpassCutoffHz":("log_uniform",2800.0,12000.0),
 "spectralTiltDb":("uniform",-6.0,6.0),
 "highpassCornerHz":("uniform",20.0,80.0),
 "nonlinearDrive":("uniform",1.0,2.5),
 "nonlinearWet":("uniform",0.0,.30),
 "broadbandNoiseRmsRelative":("log_uniform",1e-5,3e-3),
}

def _sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def _seed(*parts):
    raw="|".join(map(str,parts)).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") & 0x7fffffff

def _perm(n,kind,family,axis):
    return np.random.RandomState(_seed(ROOT,kind,family,axis)).permutation(n)

def _map(axis,u):
    dist,lo,hi=AXES[axis]
    u=float(u)
    if not 0<u<1: raise ValueError("quantile must lie strictly inside (0,1)")
    if dist=="uniform": return float(lo+(hi-lo)*u)
    if dist=="log_uniform": return float(math.exp(math.log(lo)+(math.log(hi)-math.log(lo))*u))
    raise ValueError("unknown distribution")

def _categoricals(n,kind,family,nonlinear_count,hum_count):
    nl_order=_perm(n,kind,family,"nonlinearActive")
    hum_order=_perm(n,kind,family,"humActive")
    nl=np.zeros(n,dtype=bool); nl[nl_order[:nonlinear_count]]=True
    hum=np.zeros(n,dtype=bool); hum[hum_order[:hum_count]]=True
    freq=np.full(n,0,dtype=int)
    active=np.flatnonzero(hum)
    order=_perm(len(active),kind,family,"humFundamentalHz")
    active_order=active[order]
    split=(len(active_order)+1)//2
    freq[active_order[:split]]=50; freq[active_order[split:]]=60
    return nl,hum,freq

def _rows_for_family(indices,kind,family):
    indices=np.asarray(indices,dtype=int)
    n=len(indices)
    if kind=="train":
        if n!=30: raise RuntimeError("training family must have exactly 30 rows")
        nonlinear_count=15; hum_count=11
    elif kind=="challenge":
        if n!=6: raise RuntimeError("challenge family must have exactly 6 rows")
        nonlinear_count=3; hum_count=2
    else: raise ValueError("unknown manifest kind")
    values={}; strata={}
    for axis in AXES:
        p=_perm(n,kind,family,axis)
        strata[axis]=p.astype(int)
        values[axis]=np.array([_map(axis,(int(k)+.5)/n) for k in p],dtype=float)
    nl,hum,freq=_categoricals(n,kind,family,nonlinear_count,hum_count)
    rows=[]
    for pos,row_index in enumerate(indices):
        row={"rowIndex":int(row_index),"family":family,"kind":kind,
             "nonlinearActive":bool(nl[pos]),"humActive":bool(hum[pos]),
             "humFundamentalHz":int(freq[pos]) if hum[pos] else None,
             "strata":{axis:int(strata[axis][pos]) for axis in AXES}}
        for axis in AXES: row[axis]=float(values[axis][pos])
        rows.append(row)
    return rows

def _vector_key(row):
    fields=[row[a] for a in AXES]+[row["nonlinearActive"],row["humActive"],row["humFundamentalHz"]]
    return json.dumps(fields,separators=(",",":"),sort_keys=False)

def _validate_group(rows,n,nonlinear_count,hum_count):
    for axis,(dist,lo,hi) in AXES.items():
        st=sorted(r["strata"][axis] for r in rows)
        if st!=list(range(n)): raise RuntimeError("marginal stratum coverage failed: "+axis)
        vals=[r[axis] for r in rows]
        if not all(lo<=x<=hi for x in vals): raise RuntimeError("mapped range violation: "+axis)
    if sum(r["nonlinearActive"] for r in rows)!=nonlinear_count: raise RuntimeError("nonlinear count mismatch")
    hum=[r for r in rows if r["humActive"]]
    if len(hum)!=hum_count: raise RuntimeError("hum count mismatch")
    c50=sum(r["humFundamentalHz"]==50 for r in hum); c60=sum(r["humFundamentalHz"]==60 for r in hum)
    if abs(c50-c60)>1: raise RuntimeError("hum frequency imbalance")

def build_manifest(control_path):
    if _sha256_file(control_path)!=EXPECTED_CONTROL_SHA256:
        raise RuntimeError("frozen control dataset file hash mismatch")
    c=np.load(control_path,allow_pickle=False)
    if len(c["features"])!=294: raise RuntimeError("unexpected control row count")
    train=[]; challenge=[]
    for fam in FAMILIES:
        tr=np.flatnonzero((c["family"]==fam)&(c["split"]=="train"))
        te=np.flatnonzero((c["family"]==fam)&(c["split"]=="test"))
        a=_rows_for_family(tr,"train",fam); b=_rows_for_family(te,"challenge",fam)
        _validate_group(a,30,15,11); _validate_group(b,6,3,2)
        train.extend(a); challenge.extend(b)
    if len(train)!=210 or len(challenge)!=42: raise RuntimeError("manifest row count mismatch")
    train_keys={_vector_key(r) for r in train}; challenge_keys={_vector_key(r) for r in challenge}
    duplicates=sorted(train_keys & challenge_keys)
    if duplicates: raise RuntimeError("train/challenge full parameter vector duplicate")
    chord_train=np.flatnonzero((c["family"]=="chords")&(c["split"]=="train"))
    historical=(
      len(chord_train)==30
      and all(str(x).startswith("s9-chords:") for x in c["template_id"][chord_train])
      and all(len(str(x))==625 for x in c["refs_json"][chord_train])
    )
    if not historical: raise RuntimeError("historical S9 metadata identity changed")
    manifest={
      "schema":SCHEMA,
      "controlFileSha256":EXPECTED_CONTROL_SHA256,
      "trainRows":train,
      "primaryChallengeRows":challenge,
      "admission":{
        "trainRowCount":len(train),"challengeRowCount":len(challenge),
        "rowsPerFamilyTrain":30,"rowsPerFamilyChallenge":6,
        "allContinuousMarginalStrataExact":True,
        "categoricalCountsExact":True,
        "trainChallengeFullVectorDuplicates":0,
        "historicalS9MetadataPreserved":True,
        "waveformRenders":0,"modelLoads":0,"modelInference":False,"optimizerSteps":0,
        "p1Access":False,"p2Access":False,"p3Access":False
      }
    }
    payload=json.dumps(manifest,sort_keys=True,separators=(",",":")).encode()
    manifest["manifestContentSha256"]=hashlib.sha256(payload).hexdigest()
    return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--control",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args()
    out=Path(a.out)
    if out.exists(): raise RuntimeError("refusing existing manifest output")
    m=build_manifest(a.control)
    out.write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_V2_MANIFEST="+json.dumps({"manifestContentSha256":m["manifestContentSha256"],"admission":m["admission"]},sort_keys=True))

if __name__=="__main__": main()
