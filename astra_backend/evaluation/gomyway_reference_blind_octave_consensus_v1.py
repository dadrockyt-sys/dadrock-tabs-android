"""Reference-blind local octave consensus resolver V1.

Uses frozen prediction evidence only. No professional reference is read.
Shifts MIDI by +/-12 only when nearby pitch-class evidence strongly favors the alternate octave.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import math

WINDOW_SECONDS=2.0
MIN_SUPPORT=2
MARGIN=1.25
RANGES={"guitar":(40,88),"bass":(28,67)}

def sha256_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def amp_weight(p):
    for k in ("amplitude","confidence","velocity"):
        if k in p:
            try: return max(0.05,float(p[k]))
            except: pass
    return 1.0

def support(events,i,candidate):
    t=float(events[i]["start"])
    pc=candidate%12
    s=0.0; n=0
    for j,q in enumerate(events):
        if j==i: continue
        dt=abs(float(q["start"])-t)
        if dt>WINDOW_SECONDS: continue
        qm=int(q["midi"])
        if qm%12 != pc: continue
        # octave-local support: closer octaves count more; temporal distance decays.
        oct_dist=abs(qm-candidate)/12.0
        w=amp_weight(q)*math.exp(-dt/WINDOW_SECONDS)/(1.0+oct_dist)
        s+=w; n+=1
    return s,n

def resolve_stream(events,source):
    lo,hi=RANGES[source]
    out=[]; changes=[]
    for i,p in enumerate(events):
        midi=int(p["midi"])
        candidates=[m for m in (midi-12,midi,midi+12) if lo<=m<=hi]
        scored=[]
        for m in candidates:
            s,n=support(events,i,m)
            scored.append((s,n,m))
        scored.sort(reverse=True)
        best_s,best_n,best_m=scored[0]
        cur_s,cur_n=next((s,n) for s,n,m in scored if m==midi)
        change=False
        if best_m!=midi and best_n>=MIN_SUPPORT and best_s>=max(MARGIN*cur_s,cur_s+0.15):
            change=True
        q=dict(p)
        q["originalMidi"]=midi
        q["octaveResolverApplied"]=bool(change)
        q["octaveResolverSupport"]={"current":cur_s,"best":best_s,"bestMidi":best_m,"bestNeighborCount":best_n}
        if change:
            q["midi"]=best_m
            changes.append({"id":p.get("id"),"start":float(p["start"]),"fromMidi":midi,"toMidi":best_m,
                            "currentSupport":cur_s,"bestSupport":best_s,"bestNeighborCount":best_n})
        out.append(q)
    return out,changes

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text())
    pred=ev["predictions"]
    guitar,gchg=resolve_stream(pred["guitar"],"guitar")
    bass,bchg=resolve_stream(pred["bass"],"bass")
    out={
      "schemaVersion":1,
      "kind":"gomyway-reference-blind-local-octave-consensus-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "noteEvidenceSha256":sha256_file(a.note_evidence),
      "parameters":{
        "windowSeconds":WINDOW_SECONDS,"minSupport":MIN_SUPPORT,"margin":MARGIN,
        "instrumentMidiRanges":RANGES
      },
      "predictionCounts":{"guitar":len(guitar),"bass":len(bass)},
      "changeCounts":{"guitar":len(gchg),"bass":len(bchg)},
      "changes":{"guitar":gchg,"bass":bchg},
      "predictions":{"guitar":guitar,"bass":bass},
      "interpretationBoundary":"Reference-blind development candidate. Must be frozen before professional scoring."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"changeCounts":out["changeCounts"],"parameters":out["parameters"]},indent=2))

if __name__=="__main__":main()
