"""Reference-blind guitar chord-cluster role decoder V1.

Uses frozen guitar predictions only.
- groups near-simultaneous notes into chord clusters
- assigns notes to rhythm/lead candidates using local register and continuity
- does not invent pitches
- does not read professional references
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

CLUSTER_TOL=0.06
CONTEXT_WINDOW=1.5
RHYTHM_MAX_NOTES_PER_CLUSTER=3
LEAD_MAX_NOTES_PER_CLUSTER=1

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def cluster(preds):
    rows=sorted(preds,key=lambda p:float(p["start"]))
    out=[]
    for p in rows:
        t=float(p["start"])
        if out and t-out[-1]["anchor"]<=CLUSTER_TOL:
            out[-1]["notes"].append(p)
            ts=[float(x["start"]) for x in out[-1]["notes"]]
            out[-1]["anchor"]=sum(ts)/len(ts)
        else:
            out.append({"anchor":t,"notes":[p]})
    return out

def local_median(clusters,i):
    t=clusters[i]["anchor"]; vals=[]
    for j,c in enumerate(clusters):
        if j==i: continue
        if abs(c["anchor"]-t)<=CONTEXT_WINDOW:
            vals.extend(int(n["midi"]) for n in c["notes"])
    if not vals: return None
    vals=sorted(vals)
    return vals[len(vals)//2]

def previous_selected(selected,role,t):
    xs=[x for x in selected[role] if float(x["start"])<t]
    return xs[-1] if xs else None

def continuity_cost(midi,prev):
    if prev is None:return 0.0
    return abs(midi-int(prev["midi"]))

def decode(clusters):
    selected={"rhythm":[],"lead":[]}
    decisions=[]
    for i,c in enumerate(clusters):
        notes=sorted(c["notes"],key=lambda n:int(n["midi"]))
        t=float(c["anchor"]); med=local_median(clusters,i)
        prev_r=previous_selected(selected,"rhythm",t)
        prev_l=previous_selected(selected,"lead",t)

        # Rhythm prefers lower/central notes and continuity.
        ranked_r=sorted(
          notes,
          key=lambda n:(
            continuity_cost(int(n["midi"]),prev_r),
            abs(int(n["midi"])-(med if med is not None else int(n["midi"]))),
            int(n["midi"])
          )
        )
        rhythm_pick=ranked_r[:min(RHYTHM_MAX_NOTES_PER_CLUSTER,len(ranked_r))]

        # Lead prefers one upper/mobile voice, but continuity still matters.
        ranked_l=sorted(
          notes,
          key=lambda n:(
            continuity_cost(int(n["midi"]),prev_l),
            -int(n["midi"])
          )
        )
        lead_pick=ranked_l[:min(LEAD_MAX_NOTES_PER_CLUSTER,len(ranked_l))]

        # Avoid exact duplicate assignment only for singleton clusters.
        if len(notes)==1:
            lead_pick=[]

        for n in rhythm_pick:
            q=dict(n); q["assignedRole"]="rhythm"; selected["rhythm"].append(q)
        for n in lead_pick:
            q=dict(n); q["assignedRole"]="lead"; selected["lead"].append(q)

        decisions.append({
          "anchor":t,
          "clusterMidis":[int(n["midi"]) for n in notes],
          "localMedianMidi":med,
          "rhythmMidis":[int(n["midi"]) for n in rhythm_pick],
          "leadMidis":[int(n["midi"]) for n in lead_pick]
        })
    return selected,decisions

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text())
    clusters=cluster(ev["predictions"]["guitar"])
    selected,decisions=decode(clusters)
    out={
      "schemaVersion":1,
      "kind":"gomyway-reference-blind-guitar-chord-role-decoder-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "noteEvidenceSha256":sha(a.note_evidence),
      "parameters":{
        "clusterToleranceSeconds":CLUSTER_TOL,
        "contextWindowSeconds":CONTEXT_WINDOW,
        "rhythmMaxNotesPerCluster":RHYTHM_MAX_NOTES_PER_CLUSTER,
        "leadMaxNotesPerCluster":LEAD_MAX_NOTES_PER_CLUSTER
      },
      "clusterCount":len(clusters),
      "predictionCounts":{
        "inputGuitar":len(ev["predictions"]["guitar"]),
        "rhythmCandidate":len(selected["rhythm"]),
        "leadCandidate":len(selected["lead"])
      },
      "predictions":selected,
      "decisions":decisions,
      "interpretationBoundary":"Reference-blind selection/reassignment only; no pitch invention."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"clusterCount":len(clusters),"predictionCounts":out["predictionCounts"]},indent=2))
if __name__=="__main__":main()
