"""Score frozen bass-only octave resolver V2 against professional bass reference."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

EXPECTED="39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1"
TOL=0.05

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def excluded(ref):
    p=ref.get("normalizationPolicy",{});s=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True:s.add(88)
    return s

def targets(ref,timing):
    bm={int(r["measureNumber"]):r for r in timing["measureBoundaries"]};ex=excluded(ref);out=[]
    for i,n in enumerate(ref["notes"]):
        m=int(n["measure"])
        if m in ex:continue
        b=bm[m];step=float(n["step"])
        st=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        out.append({"midi":int(n["midi"]),"start":st,"measure":m})
    return out,ex

def mfor(t,timing):
    for r in timing["measureBoundaries"]:
        if float(r["startSeconds"])<=t<float(r["endSeconds"]):return int(r["measureNumber"])
    return None

def filt(preds,timing,ex):
    lo=float(timing["measureBoundaries"][0]["startSeconds"]);hi=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in preds:
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
            "precision":tp/(tp+fp) if tp+fp else None,"recall":tp/(tp+fn) if tp+fn else None,
            "f1":2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True);ap.add_argument("--candidate",required=True)
    ap.add_argument("--timing-map",required=True);ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    if sha(a.bass_reference)!=EXPECTED:raise RuntimeError("bass reference hash mismatch")
    ev=json.loads(Path(a.note_evidence).read_text());cand=json.loads(Path(a.candidate).read_text())
    timing=json.loads(Path(a.timing_map).read_text());ref=json.loads(Path(a.bass_reference).read_text())
    t,ex=targets(ref,timing)
    old=filt(ev["predictions"]["bass"],timing,ex);new=filt(cand["predictions"]["bass"],timing,ex)
    so=score(old,t);sn=score(new,t)
    out={"kind":"gomyway-reference-blind-bass-octave-resolver-v2-score",
         "candidateSha256":sha(a.candidate),"original":so,"corrected":sn,
         "delta":{"tp":sn["tp"]-so["tp"],"f1":(sn["f1"] or 0)-(so["f1"] or 0)}}
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":main()
