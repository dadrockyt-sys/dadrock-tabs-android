#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, hashlib, json, math
from array import array
from pathlib import Path

TOL=0.05
EXPECTED_TRACKS=30

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def read_candidate_dir(root:Path):
    manifests=list(root.glob("*-candidate-freeze-manifest.json"))
    if len(manifests)!=2: raise RuntimeError(f"expected two candidate manifests, got {len(manifests)}")
    out={}
    for mp in manifests:
        m=json.loads(mp.read_text())
        if m["trackCount"]!=EXPECTED_TRACKS or m.get("referenceRead") is not False or m.get("predictionMutation") is not False or m.get("thresholdSearch") is not False or m.get("optimizerSteps")!=0:
            raise RuntimeError(f"candidate guard failed {mp.name}")
        fe=m["frontEnd"]; payloads={}
        for rec in m["files"]:
            p=root/fe/rec["file"]
            if sha256_file(p)!=rec["sha256"]: raise RuntimeError(f"hash mismatch {p}")
            d=json.loads(p.read_text())
            if d["eventCount"]!=len(d["events"]) or d.get("referenceRead") is not False: raise RuntimeError(f"candidate payload guard {p}")
            payloads[d["trackStem"]]=d["events"]
        if len(payloads)!=EXPECTED_TRACKS: raise RuntimeError(f"candidate track count {fe}")
        out[fe]={"manifestSha256":sha256_file(mp),"events":payloads}
    if set(out)!={"basic_pitch","guitar_fl"}: raise RuntimeError(set(out))
    return out

def midi_refs(path:Path):
    import mido
    mid=mido.MidiFile(path)
    tempo=500000; abs_ticks=0; out=[]
    active=collections.defaultdict(list)
    for msg in mido.merge_tracks(mid.tracks):
        abs_ticks+=msg.time
        sec=mido.tick2second(abs_ticks,mid.ticks_per_beat,tempo)
        if msg.type=="set_tempo": tempo=msg.tempo
        elif msg.type=="note_on" and msg.velocity>0: active[int(msg.note)].append(sec)
        elif msg.type in ("note_off","note_on") and (msg.type=="note_off" or msg.velocity==0):
            q=active[int(msg.note)]
            if q:
                st=q.pop(0); out.append({"start":float(st),"pitch":int(msg.note)})
    out.sort(key=lambda x:(x["start"],x["pitch"]))
    return out

def _better(ca,ea,aa,cb,eb,ab):
    if ca!=cb:return ca>cb
    if abs(ea-eb)>1e-12:return ea<eb
    return aa>ab

def onset_match(preds,refs):
    po=sorted(range(len(preds)),key=lambda i:(float(preds[i]["start"]),i))
    ro=sorted(range(len(refs)),key=lambda i:(float(refs[i]["start"]),i))
    n=len(po);m=len(ro)
    counts=[array("H",[0])*(m+1) for _ in range(n+1)]
    costs=[array("d",[0.0])*(m+1) for _ in range(n+1)]
    acts=[bytearray(m+1) for _ in range(n+1)]
    for i in range(1,n+1):
        pi=po[i-1]; ps=float(preds[pi]["start"])
        for j in range(1,m+1):
            ri=ro[j-1]; rs=float(refs[ri]["start"])
            bc,be,ba=counts[i-1][j],costs[i-1][j],1
            c2,e2=counts[i][j-1],costs[i][j-1]
            if _better(c2,e2,2,bc,be,ba): bc,be,ba=c2,e2,2
            dt=abs(ps-rs)
            if dt<=TOL+1e-12:
                c3,e3=counts[i-1][j-1]+1,costs[i-1][j-1]+dt
                if _better(c3,e3,3,bc,be,ba): bc,be,ba=c3,e3,3
            counts[i][j]=bc; costs[i][j]=be; acts[i][j]=ba
    chosen=[];i=n;j=m
    while i>0 and j>0:
        a=acts[i][j]
        if a==3:
            chosen.append((po[i-1],ro[j-1]));i-=1;j-=1
        elif a==1:i-=1
        elif a==2:j-=1
        else: raise RuntimeError("traceback failure")
    chosen.reverse();return chosen

def summarize(preds,refs):
    pairs=onset_match(preds,refs)
    exact=sum(int(preds[pi]["pitch"])==int(refs[ri]["pitch"]) for pi,ri in pairs)
    p=exact/len(preds) if preds else (1.0 if not refs else 0.0)
    r=exact/len(refs) if refs else (1.0 if not preds else 0.0)
    f=2*p*r/(p+r) if p+r else 0.0
    return {"predictionCount":len(preds),"referenceCount":len(refs),"onsetMatchedCount":len(pairs),"exactPitchOnsetCount":exact,"precision":p,"recall":r,"f1":f,"assignmentDependentWrongPitchCount":len(pairs)-exact,"unmatchedReferenceCount":len(refs)-len(pairs)}

def aggregate(rows):
    pred=sum(x["predictionCount"] for x in rows); ref=sum(x["referenceCount"] for x in rows); exact=sum(x["exactPitchOnsetCount"] for x in rows); matched=sum(x["onsetMatchedCount"] for x in rows)
    p=exact/pred if pred else (1.0 if not ref else 0.0); r=exact/ref if ref else (1.0 if not pred else 0.0); f=2*p*r/(p+r) if p+r else 0.0
    return {"predictionCount":pred,"referenceCount":ref,"onsetMatchedCount":matched,"exactPitchOnsetCount":exact,"precision":p,"recall":r,"f1":f,"predictionReferenceRatio":pred/ref if ref else None}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate-root",type=Path,required=True); ap.add_argument("--reference-dir",type=Path,required=True); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    cand=read_candidate_dir(a.candidate_root)
    rm=json.loads((a.reference_dir/"reference-manifest.json").read_text())
    if rm["trackCount"]!=EXPECTED_TRACKS or rm["performerCount"]!=27: raise RuntimeError("reference manifest guard")
    refs={}
    performer={}
    for rec in rm["files"]:
        p=a.reference_dir/rec["file"]
        if sha256_file(p)!=rec["sha256"]: raise RuntimeError(f"reference hash mismatch {p.name}")
        refs[rec["stem"]]=midi_refs(p); performer[rec["stem"]]=rec["performer"]
    results={}
    for fe in ("basic_pitch","guitar_fl"):
        tracks=[]
        for stem in sorted(refs):
            if stem not in cand[fe]["events"]: raise RuntimeError(f"missing candidate {fe} {stem}")
            s=summarize(cand[fe]["events"][stem],refs[stem]); tracks.append({"stem":stem,"performer":performer[stem],**s})
        pooled=aggregate(tracks)
        perfs={}
        for perf in sorted(set(performer.values())):
            perfs[perf]=aggregate([x for x in tracks if x["performer"]==perf])
        results[fe]={"tracks":tracks,"pooled":pooled,"performers":perfs,"contentFamilyMacroF1":sum(x["f1"] for x in tracks)/len(tracks),"candidateManifestSha256":cand[fe]["manifestSha256"]}
    c=results["basic_pitch"]; i=results["guitar_fl"]
    checks={
      "aggregateF1":i["pooled"]["f1"]>=c["pooled"]["f1"]+0.10 and i["pooled"]["f1"]>=0.60,
      "aggregatePrecision":i["pooled"]["precision"]>=c["pooled"]["precision"]+0.10 and i["pooled"]["precision"]>=0.50,
      "aggregateRecall":i["pooled"]["recall"]>=c["pooled"]["recall"]-0.05 and i["pooled"]["recall"]>=0.65,
      "predictionReferenceRatio":0.75<=i["pooled"]["predictionReferenceRatio"]<=1.50,
      "performerFloor":all(i["performers"][p]["f1"]>=c["performers"][p]["f1"]-0.10 for p in c["performers"]),
      "contentFamilyFloor":i["contentFamilyMacroF1"]>=c["contentFamilyMacroF1"]+0.10 and i["contentFamilyMacroF1"]>=0.60,
      "optimizerSteps":True,"thresholdSearch":True,"referenceDerivedPredictionMutation":True
    }
    report={"schema":"astra-fresh-front-end-feasibility-result-v1","onsetToleranceSeconds":TOL,"trackCount":EXPECTED_TRACKS,"performerCount":27,"referenceManifestSha256":sha256_file(a.reference_dir/"reference-manifest.json"),"results":results,"gate":{"checks":checks,"passed":all(checks.values()),"automaticRetry":False,"automaticIntegration":False},"execution":{"optimizerSteps":0,"thresholdSearch":False,"referenceDerivedPredictionMutation":False}}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"FRESH_FRONT_END_FEASIBILITY_COMPLETE","basicPitch":c["pooled"],"guitarFl":i["pooled"],"contentMacro":{"basicPitch":c["contentFamilyMacroF1"],"guitarFl":i["contentFamilyMacroF1"]},"gate":report["gate"]},indent=2,sort_keys=True))
if __name__=="__main__": main()
