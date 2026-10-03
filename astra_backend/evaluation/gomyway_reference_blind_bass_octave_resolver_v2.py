"""Reference-blind bass-only octave resolver V2.

Uses frozen bass predictions only. Guitar is never modified.
Only permits -12 octave correction, motivated by measured bass residuals.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

WINDOW_SECONDS=1.5
MIN_SUPPORT=3
MARGIN=1.5
BASS_RANGE=(28,67)
HIGH_MIDI_THRESHOLD=48

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def weight(p):
    for k in ("amplitude","confidence","velocity"):
        if k in p:
            try:return max(0.05,float(p[k]))
            except:pass
    return 1.0

def local_support(events,i,candidate):
    t=float(events[i]["start"]); pc=candidate%12
    score=0.0; n=0
    for j,q in enumerate(events):
        if i==j:continue
        dt=abs(float(q["start"])-t)
        if dt>WINDOW_SECONDS:continue
        qm=int(q["midi"])
        if qm%12!=pc:continue
        oct_dist=abs(qm-candidate)/12.0
        score += weight(q)*math.exp(-dt/WINDOW_SECONDS)/(1+oct_dist)
        n+=1
    return score,n

def local_register(events,i):
    t=float(events[i]["start"])
    vals=[]
    for j,q in enumerate(events):
        if i==j:continue
        dt=abs(float(q["start"])-t)
        if dt<=WINDOW_SECONDS:
            vals.append(int(q["midi"]))
    if not vals:return None
    vals=sorted(vals)
    return vals[len(vals)//2]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text())
    bass=ev["predictions"]["bass"]
    out=[];changes=[]
    lo,hi=BASS_RANGE
    for i,p in enumerate(bass):
        midi=int(p["midi"]); q=dict(p)
        q["originalMidi"]=midi; q["octaveResolverApplied"]=False
        reason="not-eligible"
        if lo<=midi<=hi and midi>=HIGH_MIDI_THRESHOLD and midi-12>=lo:
            cur_s,cur_n=local_support(bass,i,midi)
            low_s,low_n=local_support(bass,i,midi-12)
            reg=local_register(bass,i)
            register_support = reg is not None and abs((midi-12)-reg) < abs(midi-reg)
            if low_n>=MIN_SUPPORT and register_support and low_s>=max(MARGIN*cur_s,cur_s+0.2):
                q["midi"]=midi-12
                q["octaveResolverApplied"]=True
                changes.append({
                  "id":p.get("id"),"start":float(p["start"]),"fromMidi":midi,"toMidi":midi-12,
                  "currentSupport":cur_s,"lowerSupport":low_s,"lowerNeighborCount":low_n,
                  "localMedianMidi":reg
                })
                reason="lower-octave-supported"
            else:
                reason="insufficient-lower-octave-evidence"
            q["octaveResolverSupport"]={
              "currentSupport":cur_s,"lowerSupport":low_s,"lowerNeighborCount":low_n,
              "localMedianMidi":reg,"reason":reason
            }
        else:
            q["octaveResolverSupport"]={"reason":reason}
        out.append(q)
    result={
      "schemaVersion":2,
      "kind":"gomyway-reference-blind-bass-octave-resolver-v2",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "noteEvidenceSha256":sha(a.note_evidence),
      "parameters":{"windowSeconds":WINDOW_SECONDS,"minSupport":MIN_SUPPORT,"margin":MARGIN,
                    "bassMidiRange":BASS_RANGE,"highMidiThreshold":HIGH_MIDI_THRESHOLD,
                    "allowedShiftSemitones":[-12]},
      "predictionCount":len(out),"changeCount":len(changes),
      "changes":changes,"predictions":{"bass":out},
      "interpretationBoundary":"Bass-only reference-blind development candidate. Guitar unchanged by construction."
    }
    Path(a.output_json).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"changeCount":len(changes),"parameters":result["parameters"]},indent=2))
if __name__=="__main__":main()
