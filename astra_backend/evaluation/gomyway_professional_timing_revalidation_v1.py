"""Revalidate Go My Way professional timing from frozen V6 audio beat evidence.

Important:
- preserves old timing map untouched
- reads old map ONLY for notation structure (measure count + meter regions)
- does not use old measure times, old offset, base tempo, or resolved tempo to fit the new map
- derives a 450-quarter-beat sequence from frozen V6 mix+drum beat ticks
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np

CLUSTER_TOLERANCE_SECONDS=0.15
SINGLE_SOURCE_PENALTY=0.15
SKIP_PENALTY=0.12
START_END_SKIP_PENALTY=0.15
INTERVAL_SIGMA_SECONDS=0.06
MAX_CLUSTER_JUMP=3

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
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
    out=[]
    for c in clusters:
        out.append({
          "timeSeconds":float(np.mean(c["times"])),
          "sources":sorted(c["sources"]),
          "sourceCount":len(c["sources"]),
          "spreadSeconds":float(max(c["times"])-min(c["times"]))
        })
    return out

def select_exact_beats(clusters,target_count):
    times=np.asarray([c["timeSeconds"] for c in clusters],float)
    support=np.asarray([c["sourceCount"] for c in clusters],int)
    diffs=np.diff(times)
    stable=diffs[diffs>0.35]
    target_interval=float(np.median(stable if len(stable) else diffs))
    n=len(times); kmax=int(target_count); inf=1e30
    dp=np.full((kmax,n),inf,float)
    prev=np.full((kmax,n),-1,int)

    for i in range(min(n,24)):
        dp[0,i]=START_END_SKIP_PENALTY*i + (SINGLE_SOURCE_PENALTY if support[i]==1 else 0.0)

    for k in range(1,kmax):
        for i in range(k,n):
            for j in range(max(k-1,i-MAX_CLUSTER_JUMP),i):
                if not np.isfinite(dp[k-1,j]): continue
                dt=times[i]-times[j]
                interval_cost=((dt-target_interval)/INTERVAL_SIGMA_SECONDS)**2
                skipped=i-j-1
                cost=(dp[k-1,j]+interval_cost+SKIP_PENALTY*skipped+
                      (SINGLE_SOURCE_PENALTY if support[i]==1 else 0.0))
                if cost<dp[k,i]:
                    dp[k,i]=cost; prev[k,i]=j

    best_i=None; best_cost=inf
    for i in range(kmax-1,n):
        cost=dp[kmax-1,i]+START_END_SKIP_PENALTY*(n-1-i)
        if cost<best_cost:
            best_cost=cost; best_i=i
    if best_i is None: raise RuntimeError("no exact beat path")

    idx=[]; cur=int(best_i)
    for k in range(kmax-1,-1,-1):
        idx.append(cur)
        cur=int(prev[k,cur]) if k>0 else -1
    idx=idx[::-1]
    selected=[clusters[i] for i in idx]
    return selected, idx, target_interval, float(best_cost)

def meter_sequence(old_map):
    seq=[]
    for m in range(1,int(old_map["measureCount"])+1):
        found=None
        for r in old_map["meterRegions"]:
            if int(r["startMeasure"])<=m<=int(r["endMeasure"]):
                found={"numerator":int(r["numerator"]),"denominator":int(r["denominator"])}
                break
        if found is None: raise RuntimeError(f"no meter for measure {m}")
        seq.append(found)
    return seq

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v6-bundle",required=True)
    ap.add_argument("--old-timing-map",required=True)
    ap.add_argument("--output-map",required=True)
    ap.add_argument("--output-audit",required=True)
    a=ap.parse_args()

    v6=json.loads(Path(a.v6_bundle).read_text())
    old=json.loads(Path(a.old_timing_map).read_text())
    by={c["name"]:c for c in v6["candidates"]}
    mix=by["mix_multifeature"]["grid"]["beatTimesSeconds"]
    drums=by["drums_multifeature"]["grid"]["beatTimesSeconds"]

    meters=meter_sequence(old)
    expected_beats=sum(m["numerator"] for m in meters)
    clusters=cluster_beats(mix,drums)
    selected,indices,target_interval,path_cost=select_exact_beats(clusters,expected_beats)
    beat_times=np.asarray([b["timeSeconds"] for b in selected],float)
    intervals=np.diff(beat_times)
    avg_interval=float(np.mean(intervals))
    median_interval=float(np.median(intervals))
    avg_bpm=float(60.0/avg_interval)
    median_bpm=float(60.0/median_interval)

    # Last measure needs one beat beyond the final selected beat start.
    tail_intervals=intervals[-12:] if len(intervals)>=12 else intervals
    final_interval=float(np.median(tail_intervals))
    terminal_beat=float(beat_times[-1]+final_interval)

    boundaries=[]
    beat_cursor=0
    for measure,meter in enumerate(meters,start=1):
        n=int(meter["numerator"])
        start=float(beat_times[beat_cursor])
        next_cursor=beat_cursor+n
        end=float(beat_times[next_cursor]) if next_cursor<len(beat_times) else terminal_beat
        boundaries.append({
          "measureNumber":measure,
          "startSeconds":start,
          "endSeconds":end,
          "durationSeconds":end-start,
          "meter":meter
        })
        beat_cursor=next_cursor
    if beat_cursor != expected_beats: raise RuntimeError((beat_cursor,expected_beats))

    out={
      "schemaVersion":3,
      "timingMapType":"professional-structure-plus-frozen-audio-beat-consensus",
      "song":old["song"],
      "artist":old["artist"],
      "audioSource":old["audioSource"],
      "measureCount":old["measureCount"],
      "meterRegions":old["meterRegions"],
      "status":"revalidated-from-frozen-v6-audio-evidence",
      "supersedesForResearchOnly":"public/gomyway-professional-timing-map-v2.json",
      "oldMapPreserved":True,
      "productionPromotionAllowed":False,
      "protectedReference":True,
      "derivation":{
        "v6BundleSha256":sha256_file(Path(a.v6_bundle)),
        "oldTimingMapSha256":sha256_file(Path(a.old_timing_map)),
        "oldTimingValuesUsedForFit":False,
        "oldMapUsage":"measure count and meter regions only",
        "sourceCandidates":["mix_multifeature","drums_multifeature"],
        "clusterToleranceSeconds":CLUSTER_TOLERANCE_SECONDS,
        "clusterCount":len(clusters),
        "selectedBeatCount":len(selected),
        "expectedQuarterBeatCountFromNotation":expected_beats,
        "audioDerivedTargetIntervalSeconds":target_interval,
        "pathCost":path_cost,
        "averageTempoBpm":avg_bpm,
        "medianTempoBpm":median_bpm,
        "firstMeasureStartSeconds":float(boundaries[0]["startSeconds"]),
        "lastMeasureEndSeconds":float(boundaries[-1]["endSeconds"])
      },
      "measureBoundaries":boundaries,
      "validation":{
        "measureCount":len(boundaries),
        "quarterBeatCount":expected_beats,
        "meterChangeAt104Honored":meters[103]["numerator"]==2,
        "readyForDiagnosticRescoring":True,
        "productionPromotionAllowed":False
      },
      "notes":"This V3 map revalidates timing from frozen independent audio beat evidence plus professional meter/measure structure. It intentionally does not inherit V2's 133.8 BPM or 7.1 s offset."
    }
    Path(a.output_map).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")

    skipped=[i for i in range(len(clusters)) if i not in set(indices)]
    audit={
      "kind":"gomyway-professional-timing-revalidation-v1-audit",
      "v6BundleSha256":sha256_file(Path(a.v6_bundle)),
      "oldTimingMapSha256":sha256_file(Path(a.old_timing_map)),
      "clusterCount":len(clusters),
      "selectedBeatCount":len(selected),
      "skippedClusterCount":len(skipped),
      "skippedClusters":[clusters[i] for i in skipped],
      "firstSelectedBeatSeconds":float(beat_times[0]),
      "lastSelectedBeatSeconds":float(beat_times[-1]),
      "terminalBeatSeconds":terminal_beat,
      "averageBeatIntervalSeconds":avg_interval,
      "medianBeatIntervalSeconds":median_interval,
      "averageTempoBpm":avg_bpm,
      "medianTempoBpm":median_bpm,
      "intervalStdSeconds":float(np.std(intervals)),
      "singleSourceSelectedCount":sum(1 for x in selected if x["sourceCount"]==1),
      "dualSourceSelectedCount":sum(1 for x in selected if x["sourceCount"]==2),
      "interpretationBoundary":"Revalidation artifact only; old map remains unchanged and this new map is research-only until rescoring/anchor validation."
    }
    Path(a.output_audit).write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"map":out["derivation"],"audit":{k:v for k,v in audit.items() if k!="skippedClusters"}},indent=2))

if __name__=="__main__": main()
