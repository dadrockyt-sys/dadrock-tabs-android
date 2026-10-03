"""Go My Way timing-origin V4 diagnostic candidate.

Uses the same frozen V6 mix+drum beat evidence as V3 revalidation.
Only change: require the earliest dual-source beat cluster as the origin hypothesis.
No tempo retuning. Old maps remain untouched.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np

CLUSTER_TOLERANCE_SECONDS=0.15
SINGLE_SOURCE_PENALTY=0.15
SKIP_PENALTY=0.12
INTERVAL_SIGMA_SECONDS=0.06
MAX_CLUSTER_JUMP=3

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def cluster_beats(mix,drums):
    events=sorted([(float(t),"mix") for t in mix]+[(float(t),"drums") for t in drums])
    clusters=[]
    for t,s in events:
        if clusters and t-clusters[-1]["times"][-1] <= CLUSTER_TOLERANCE_SECONDS:
            clusters[-1]["times"].append(t); clusters[-1]["sources"].add(s)
        else:
            clusters.append({"times":[t],"sources":{s}})
    return [{"timeSeconds":float(np.mean(c["times"])),"sources":sorted(c["sources"]),
             "sourceCount":len(c["sources"]),"spreadSeconds":float(max(c["times"])-min(c["times"]))}
            for c in clusters]

def meter_sequence(old):
    seq=[]
    for m in range(1,int(old["measureCount"])+1):
        for r in old["meterRegions"]:
            if int(r["startMeasure"])<=m<=int(r["endMeasure"]):
                seq.append({"numerator":int(r["numerator"]),"denominator":int(r["denominator"])})
                break
    return seq

def select_with_forced_origin(clusters,target_count):
    times=np.asarray([c["timeSeconds"] for c in clusters],float)
    support=np.asarray([c["sourceCount"] for c in clusters],int)
    origin=next((i for i,c in enumerate(clusters) if c["sourceCount"]==2),None)
    if origin is None: raise RuntimeError("no dual-source origin")
    diffs=np.diff(times)
    stable=diffs[(diffs>0.35)&(diffs<0.65)]
    target_interval=float(np.median(stable if len(stable) else diffs))
    n=len(times); kmax=target_count; inf=1e30
    dp=np.full((kmax,n),inf); prev=np.full((kmax,n),-1,int)
    dp[0,origin]=0.0
    for k in range(1,kmax):
        for i in range(origin+k,n):
            for j in range(max(origin+k-1,i-MAX_CLUSTER_JUMP),i):
                if not np.isfinite(dp[k-1,j]): continue
                dt=times[i]-times[j]
                cost=((dt-target_interval)/INTERVAL_SIGMA_SECONDS)**2
                cost += SKIP_PENALTY*(i-j-1)
                if support[i]==1: cost+=SINGLE_SOURCE_PENALTY
                v=dp[k-1,j]+cost
                if v<dp[k,i]: dp[k,i]=v; prev[k,i]=j
    best_i=min(range(origin+kmax-1,n),key=lambda i:dp[kmax-1,i]+0.15*(n-1-i))
    idx=[]; cur=best_i
    for k in range(kmax-1,-1,-1):
        idx.append(cur); cur=prev[k,cur] if k>0 else -1
    idx=idx[::-1]
    return [clusters[i] for i in idx],idx,target_interval,float(dp[kmax-1,best_i]),origin

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v6-bundle",required=True); ap.add_argument("--structure-map",required=True)
    ap.add_argument("--output-map",required=True); ap.add_argument("--output-audit",required=True)
    a=ap.parse_args()
    v6=json.loads(Path(a.v6_bundle).read_text()); old=json.loads(Path(a.structure_map).read_text())
    by={c["name"]:c for c in v6["candidates"]}
    clusters=cluster_beats(by["mix_multifeature"]["grid"]["beatTimesSeconds"],
                           by["drums_multifeature"]["grid"]["beatTimesSeconds"])
    meters=meter_sequence(old); expected=sum(m["numerator"] for m in meters)
    selected,idx,target_interval,path_cost,origin=select_with_forced_origin(clusters,expected)
    beats=np.asarray([x["timeSeconds"] for x in selected],float)
    ints=np.diff(beats)
    final_interval=float(np.median(ints[-12:]))
    terminal=float(beats[-1]+final_interval)
    boundaries=[]; cur=0
    for m,meter in enumerate(meters,1):
        n=meter["numerator"]; st=float(beats[cur]); nxt=cur+n
        en=float(beats[nxt]) if nxt<len(beats) else terminal
        boundaries.append({"measureNumber":m,"startSeconds":st,"endSeconds":en,
                           "durationSeconds":en-st,"meter":meter})
        cur=nxt
    out={
      "schemaVersion":4,
      "timingMapType":"professional-structure-plus-frozen-audio-beat-consensus-origin-diagnostic",
      "song":old["song"],"artist":old["artist"],"audioSource":old["audioSource"],
      "measureCount":old["measureCount"],"meterRegions":old["meterRegions"],
      "status":"diagnostic-origin-hypothesis","productionPromotionAllowed":False,
      "protectedReference":True,"oldMapsPreserved":True,
      "derivation":{"v6BundleSha256":sha256_file(a.v6_bundle),
                    "structureMapSha256":sha256_file(a.structure_map),
                    "forcedOriginClusterIndex":origin,
                    "forcedOriginSeconds":float(clusters[origin]["timeSeconds"]),
                    "forcedOriginSources":clusters[origin]["sources"],
                    "clusterCount":len(clusters),"selectedBeatCount":len(selected),
                    "expectedQuarterBeatCount":expected,
                    "audioDerivedTargetIntervalSeconds":target_interval,
                    "pathCost":path_cost,
                    "averageTempoBpm":float(60/np.mean(ints)),
                    "medianTempoBpm":float(60/np.median(ints)),
                    "firstMeasureStartSeconds":float(boundaries[0]["startSeconds"]),
                    "lastMeasureEndSeconds":float(boundaries[-1]["endSeconds"])},
      "measureBoundaries":boundaries,
      "validation":{"measureCount":len(boundaries),"quarterBeatCount":expected,
                    "meterChangeAt104Honored":meters[103]["numerator"]==2,
                    "readyForDiagnosticRescoring":True,"productionPromotionAllowed":False},
      "notes":"Post-hoc diagnostic origin hypothesis motivated by shared -1 beat guitar shift; not an independent prospective validation."
    }
    Path(a.output_map).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    skipped=[i for i in range(len(clusters)) if i not in set(idx)]
    audit={"kind":"gomyway-timing-origin-v4-diagnostic-audit","mapSha256":sha256_file(Path(a.output_map)),
           "originCluster":clusters[origin],"clusterCount":len(clusters),"selectedBeatCount":len(selected),
           "skippedClusterCount":len(skipped),"dualSourceSelectedCount":sum(x["sourceCount"]==2 for x in selected),
           "singleSourceSelectedCount":sum(x["sourceCount"]==1 for x in selected),
           "averageTempoBpm":float(60/np.mean(ints)),"medianTempoBpm":float(60/np.median(ints)),
           "interpretationBoundary":"Post-hoc diagnostic only."}
    Path(a.output_audit).write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"map":out["derivation"],"audit":audit},indent=2))

if __name__=="__main__":main()
