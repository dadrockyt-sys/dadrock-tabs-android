"""Score frozen specialized-guitar AMT events after candidate freeze."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED={
 "rhythm":"d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
 "lead":"8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}
TOL=0.05

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def excluded(ref):
    p=ref.get("normalizationPolicy",{})
    s=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True:s.add(88)
    return s

def targets(role,ref,timing):
    bm={int(r["measureNumber"]):r for r in timing["measureBoundaries"]}
    ex=excluded(ref);out=[]
    for i,n in enumerate(ref["notes"]):
        m=int(n["measure"])
        if m in ex:continue
        b=bm[m];step=float(n["step"])
        st=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        out.append({"id":f"{role}:{i}","midi":int(n["midi"]),"start":st,"measure":m})
    return out,ex

def mfor(t,timing):
    for r in timing["measureBoundaries"]:
        if float(r["startSeconds"])<=t<float(r["endSeconds"]):return int(r["measureNumber"])
    return None

def filt(events,timing,ex):
    lo=float(timing["measureBoundaries"][0]["startSeconds"])
    hi=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in events:
        t=float(p["start"])
        if not(lo<=t<hi):continue
        m=mfor(t,timing)
        if m is None or m in ex:continue
        out.append(p)
    return out

def score(preds,targs):
    c=[]
    for pi,p in enumerate(preds):
        for ti,t in enumerate(targs):
            if int(p["midi"])!=int(t["midi"]):continue
            d=abs(float(p["start"])-float(t["start"]))
            if d<=TOL:c.append((d,pi,ti))
    c.sort();up=set();ut=set();tp=0
    for d,pi,ti in c:
        if pi in up or ti in ut:continue
        up.add(pi);ut.add(ti);tp+=1
    fp=len(preds)-tp;fn=len(targs)-tp
    return {"predictions":len(preds),"targets":len(targs),"tp":tp,"fp":fp,"fn":fn,
            "precision":tp/(tp+fp) if tp+fp else None,
            "recall":tp/(tp+fn) if tp+fn else None,
            "f1":2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True)
    ap.add_argument("--lead-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    cand=json.loads(Path(a.candidate).read_text())
    tim=json.loads(Path(a.timing_map).read_text())
    refs={}
    for role in ("rhythm","lead"):
        p=getattr(a,f"{role}_reference")
        if sha(p)!=EXPECTED[role]:raise RuntimeError(f"{role} hash mismatch")
        refs[role]=json.loads(Path(p).read_text())

    tr,er=targets("rhythm",refs["rhythm"],tim)
    tl,el=targets("lead",refs["lead"],tim)
    events=cand["events"]
    sr=score(filt(events,tim,er),tr)
    sl=score(filt(events,tim,el),tl)
    comb_t=sorted(tr+tl,key=lambda x:(x["start"],x["midi"]))
    comb_e=er|el
    sc=score(filt(events,tim,comb_e),comb_t)

    out={"kind":"gomyway-specialized-guitar-amt-score-v1",
         "candidateSha256":sha(a.candidate),
         "inputLabel":cand["input"]["label"],
         "roles":{"rhythm":sr,"lead":sl,"combinedGuitar":sc}}
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
