"""Guitar chord/voicing structure diagnostic under V4-origin timing.

Diagnostic only:
- reads frozen guitar predictions
- groups near-simultaneous predicted notes into local chord clusters
- compares target pitch classes against the whole local cluster
- does not mutate predictions
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from collections import Counter,defaultdict

EXPECTED={
 "rhythm":"d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555",
 "lead":"8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be",
}
ONSET_TOL=0.05
CLUSTER_TOL=0.06

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def load_ref(role,path):
    if sha(path)!=EXPECTED[role]: raise RuntimeError(f"{role} hash mismatch")
    return json.loads(Path(path).read_text())

def excluded(ref):
    p=ref.get("normalizationPolicy",{}); out=set(int(x) for x in p.get("excludedSourceMeasures",[]))
    if p.get("measure88Excluded") is True: out.add(88)
    return out

def targets(role,ref,timing):
    bm={int(r["measureNumber"]):r for r in timing["measureBoundaries"]}
    ex=excluded(ref); out=[]
    for i,n in enumerate(ref["notes"]):
        m=int(n["measure"])
        if m in ex: continue
        b=bm[m]; step=float(n["step"])
        st=float(b["startSeconds"])+(step/16.0)*float(b["durationSeconds"])
        out.append({"id":f"{role}:{i}","midi":int(n["midi"]),"start":st,"measure":m,"step":step})
    return out,ex

def measure_for_time(t,timing):
    for r in timing["measureBoundaries"]:
        if float(r["startSeconds"])<=t<float(r["endSeconds"]): return int(r["measureNumber"])
    return None

def filter_preds(preds,timing,ex):
    lo=float(timing["measureBoundaries"][0]["startSeconds"]);hi=float(timing["measureBoundaries"][-1]["endSeconds"])
    out=[]
    for p in preds:
        t=float(p["start"])
        if not(lo<=t<hi):continue
        m=measure_for_time(t,timing)
        if m is None or m in ex:continue
        q=dict(p);q["measure"]=m;out.append(q)
    return sorted(out,key=lambda x:float(x["start"]))

def cluster_predictions(preds):
    clusters=[]
    for p in preds:
        t=float(p["start"])
        if clusters and t-clusters[-1]["anchor"]<=CLUSTER_TOL:
            clusters[-1]["notes"].append(p)
            ts=[float(x["start"]) for x in clusters[-1]["notes"]]
            clusters[-1]["anchor"]=sum(ts)/len(ts)
        else:
            clusters.append({"anchor":t,"notes":[p]})
    for c in clusters:
        c["midis"]=sorted(int(x["midi"]) for x in c["notes"])
        c["pitchClasses"]=sorted(set(m%12 for m in c["midis"]))
    return clusters

def nearest_cluster(t,clusters):
    best=None
    for c in clusters:
        d=abs(float(c["anchor"])-t)
        if d<=ONSET_TOL and (best is None or d<best[0]): best=(d,c)
    return best

def target_group_stats(role,targs,clusters):
    onset_found=0; exact_any=0; pc_any=0; multiplicities=Counter(); extra_counts=[]; rows=[]
    interval_missing=Counter(); interval_extra=Counter()
    for t in targs:
        hit=nearest_cluster(float(t["start"]),clusters)
        if not hit: 
            rows.append({"targetId":t["id"],"foundCluster":False})
            continue
        onset_found+=1;d,c=hit; mids=c["midis"]; pcs=c["pitchClasses"]
        exact=int(t["midi"]) in mids
        pc=(int(t["midi"])%12) in pcs
        exact_any+=int(exact);pc_any+=int(pc)
        multiplicities[len(mids)]+=1
        extra_counts.append(max(0,len(mids)-1))
        if not exact:
            for m in mids:
                interval_missing[abs(int(m)-int(t["midi"]))]+=1
        rows.append({"targetId":t["id"],"targetMidi":int(t["midi"]),"targetStart":float(t["start"]),
                     "foundCluster":True,"onsetErrorSeconds":d,"clusterMidis":mids,
                     "clusterPitchClasses":pcs,"exactMidiPresent":exact,"targetPitchClassPresent":pc})
    return {
      "targetCount":len(targs),
      "targetWithPredictionClusterCount":onset_found,
      "targetWithPredictionClusterRate":onset_found/len(targs) if targs else None,
      "exactMidiPresentAnywhereInClusterCount":exact_any,
      "exactMidiPresentAnywhereInClusterRateAmongFound":exact_any/onset_found if onset_found else None,
      "targetPitchClassPresentAnywhereInClusterCount":pc_any,
      "targetPitchClassPresentAnywhereInClusterRateAmongFound":pc_any/onset_found if onset_found else None,
      "clusterMultiplicityHistogram":dict(sorted((str(k),v) for k,v in multiplicities.items())),
      "meanExtraPredictedNotesPerFoundCluster":sum(extra_counts)/len(extra_counts) if extra_counts else None,
      "topAbsoluteIntervalsWhenExactMissing":[{"semitones":k,"count":v} for k,v in interval_missing.most_common(12)],
      "rows":rows
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--note-evidence",required=True);ap.add_argument("--timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True);ap.add_argument("--lead-reference",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    ev=json.loads(Path(a.note_evidence).read_text());tim=json.loads(Path(a.timing_map).read_text())
    if ev["timingMap"]["sha256"]!=sha(a.timing_map): raise RuntimeError("timing mismatch")
    roles={}
    for role in ("rhythm","lead"):
        ref=load_ref(role,getattr(a,f"{role}_reference"));targs,ex=targets(role,ref,tim)
        preds=filter_preds(ev["predictions"]["guitar"],tim,ex)
        clusters=cluster_predictions(preds)
        roles[role]={
          "predictionCount":len(preds),
          "clusterCount":len(clusters),
          "meanClusterSize":sum(len(c["notes"]) for c in clusters)/len(clusters) if clusters else None,
          "maxClusterSize":max((len(c["notes"]) for c in clusters),default=0),
          "targetClusterDiagnostics":target_group_stats(role,targs,clusters)
        }
    out={"schemaVersion":1,"kind":"gomyway-v4-origin-guitar-chord-voicing-diagnostic-v1",
         "noteEvidenceSha256":sha(a.note_evidence),"timingMapSha256":sha(a.timing_map),
         "predictionMutation":False,"clusterToleranceSeconds":CLUSTER_TOL,
         "targetOnsetToleranceSeconds":ONSET_TOL,"roles":roles,
         "interpretationBoundary":"Diagnostic only; no correction or promotion."}
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    summary={}
    for r,v in roles.items():
        d=v["targetClusterDiagnostics"]
        summary[r]={k:d[k] for k in (
          "targetCount","targetWithPredictionClusterCount","targetWithPredictionClusterRate",
          "exactMidiPresentAnywhereInClusterCount","exactMidiPresentAnywhereInClusterRateAmongFound",
          "targetPitchClassPresentAnywhereInClusterCount","targetPitchClassPresentAnywhereInClusterRateAmongFound",
          "clusterMultiplicityHistogram","meanExtraPredictedNotesPerFoundCluster",
          "topAbsoluteIntervalsWhenExactMissing"
        )}
    print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
