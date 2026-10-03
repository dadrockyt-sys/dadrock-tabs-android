"""Score frozen octave-consensus candidate against professional references.

Reads already-frozen candidate and compares original frozen predictions vs corrected predictions.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED={
 "rhythm":"d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
 "lead":"8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
 "bass":"39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1",
}
TOL=0.05

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def load_ref(role,path):
    if sha(path)!=EXPECTED[role]: raise RuntimeError(f"{role} hash mismatch")
    return json.loads(Path(path).read_text())

def ex(ref):
    p=ref.get("normalizationPolicy",{}); s=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True:s.add(88)
    return s

def targets(role,ref,timing):
    bm={int(r["measureNumber"]):r for r in timing["measureBoundaries"]}; out=[]; excluded=ex(ref)
    for i,n in enumerate(ref["notes"]):
        m=int(n["measure"])
        if m in excluded:continue
        b=bm[m]; step=float(n["step"])
        st=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        out.append({"id":f"{role}:{i}","midi":int(n["midi"]),"start":st,"measure":m})
    return out,excluded

def mfor(t,timing):
    for r in timing["measureBoundaries"]:
        if float(r["startSeconds"])<=t<float(r["endSeconds"]):return int(r["measureNumber"])
    return None

def filt(preds,timing,excluded):
    lo=float(timing["measureBoundaries"][0]["startSeconds"]);hi=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in preds:
        t=float(p["start"])
        if not(lo<=t<hi):continue
        m=mfor(t,timing)
        if m is None or m in excluded:continue
        out.append(p)
    return out

def score(preds,targs):
    cand=[]
    for pi,p in enumerate(preds):
        for ti,t in enumerate(targs):
            if int(p["midi"])!=int(t["midi"]):continue
            d=abs(float(p["start"])-float(t["start"]))
            if d<=TOL:cand.append((d,pi,ti))
    cand.sort();up=set();ut=set();n=0
    for d,pi,ti in cand:
        if pi in up or ti in ut:continue
        up.add(pi);ut.add(ti);n+=1
    fp=len(preds)-n;fn=len(targs)-n
    return {"predictions":len(preds),"targets":len(targs),"tp":n,"fp":fp,"fn":fn,
            "precision":n/(n+fp) if n+fp else None,"recall":n/(n+fn) if n+fn else None,
            "f1":2*n/(2*n+fp+fn) if 2*n+fp+fn else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True);ap.add_argument("--candidate",required=True);ap.add_argument("--timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True);ap.add_argument("--lead-reference",required=True);ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text());cand=json.loads(Path(a.candidate).read_text());tim=json.loads(Path(a.timing_map).read_text())
    roles={}; src={"rhythm":"guitar","lead":"guitar","bass":"bass"}
    for role in ("rhythm","lead","bass"):
        ref=load_ref(role,getattr(a,f"{role}_reference"));t,e=targets(role,ref,tim)
        old=filt(ev["predictions"][src[role]],tim,e);new=filt(cand["predictions"][src[role]],tim,e)
        so=score(old,t);sn=score(new,t)
        roles[role]={"original":so,"corrected":sn,"delta":{"tp":sn["tp"]-so["tp"],"f1":(sn["f1"] or 0)-(so["f1"] or 0)}}
    out={"kind":"gomyway-reference-blind-octave-consensus-v1-score","candidateSha256":sha(a.candidate),
         "noteEvidenceSha256":sha(a.note_evidence),"timingMapSha256":sha(a.timing_map),"roles":roles}
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(roles,indent=2))
if __name__=="__main__":main()
