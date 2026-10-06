#!/usr/bin/env python3
"""Score frozen GuitarSet baseline candidates for missing-event vs wrong-pitch attribution.

Reference-only scorer: no audio, no Basic Pitch import, no prediction mutation.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math
from array import array
from pathlib import Path
from typing import Any

EVAL_PLAYERS=("00","01","03")
DEV_PLAYERS=("02","04","05")
EXPECTED_TRACKS=180
TOL=0.05

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def player_from_stem(stem:str)->str:
    if len(stem)<3 or stem[2]!="_": raise RuntimeError(f"unexpected stem {stem}")
    return stem[:2]

def load_refs(path:Path)->list[dict[str,Any]]:
    import jams
    jam=jams.load(str(path))
    anns=list(jam.search(namespace="note_midi"))
    if not anns: anns=list(jam.search(namespace="pitch_midi"))
    if len(anns)!=6: raise RuntimeError(f"expected six string annotations in {path.name}, got {len(anns)}")
    rows=[]
    for si,ann in enumerate(anns):
        for ei,n in enumerate(ann):
            start=float(n.time); pitch=int(round(float(n.value)))
            if not math.isfinite(start) or not 0<=pitch<=127: raise RuntimeError(f"invalid reference event {path.name}")
            rows.append({"id":f"r:{si}:{ei}","start":start,"pitch":pitch,"stringIndex":si})
    rows.sort(key=lambda x:(x["start"],x["pitch"],x["id"]))
    return rows

def verify_candidates(root:Path):
    m=json.loads((root/"candidate-freeze-manifest.json").read_text())
    if m.get("candidateFileCount")!=EXPECTED_TRACKS: raise RuntimeError("candidate count mismatch")
    if tuple(m.get("players",[]))!=EVAL_PLAYERS: raise RuntimeError("player identity mismatch")
    if m.get("referenceRead") is not False or m.get("jamsNoteEventsRead")!=0: raise RuntimeError("candidate reference guard failed")
    if m.get("predictionMutation") is not False or m.get("thresholdSearch") is not False: raise RuntimeError("candidate mutation guard failed")
    payloads={}
    for rec in m["files"]:
        p=root/rec["file"]
        if sha256_file(p)!=rec["sha256"]: raise RuntimeError(f"candidate hash mismatch {p.name}")
        d=json.loads(p.read_text())
        stem=str(d["trackStem"]); player=player_from_stem(stem)
        if player not in EVAL_PLAYERS or player in DEV_PLAYERS: raise RuntimeError(f"non-eval candidate {stem}")
        if int(d["eventCount"])!=len(d["events"]): raise RuntimeError(f"event count mismatch {stem}")
        if d.get("referenceRead") is not False or d.get("predictionMutation") is not False: raise RuntimeError(f"candidate guard failed {stem}")
        payloads[stem]=d
    if len(payloads)!=EXPECTED_TRACKS: raise RuntimeError("duplicate/missing candidates")
    return m,payloads

def discover_refs(root:Path):
    rows={}
    for p in sorted(root.glob("*.jams")):
        stem=p.stem; player=player_from_stem(stem)
        if player in DEV_PLAYERS: raise RuntimeError(f"development reference present: {p.name}")
        if player not in EVAL_PLAYERS: raise RuntimeError(f"unexpected reference: {p.name}")
        rows[stem]=p
    if len(rows)!=EXPECTED_TRACKS: raise RuntimeError(f"expected {EXPECTED_TRACKS} refs, got {len(rows)}")
    counts={x:sum(player_from_stem(s)==x for s in rows) for x in EVAL_PLAYERS}
    if counts!={"00":60,"01":60,"03":60}: raise RuntimeError(f"reference counts mismatch {counts}")
    return rows

def _better(ca,ea,aa,cb,eb,ab):
    if ca!=cb: return ca>cb
    if abs(ea-eb)>1e-12: return ea<eb
    return aa>ab

def onset_match(preds,refs,tol=TOL):
    po=sorted(range(len(preds)),key=lambda i:(float(preds[i]["start"]),i))
    ro=sorted(range(len(refs)),key=lambda i:(float(refs[i]["start"]),i))
    n=len(po); m=len(ro)
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
            if dt<=tol+1e-12:
                c3,e3=counts[i-1][j-1]+1,costs[i-1][j-1]+dt
                if _better(c3,e3,3,bc,be,ba): bc,be,ba=c3,e3,3
            counts[i][j]=bc; costs[i][j]=be; acts[i][j]=ba
    chosen=[]; i=n; j=m
    while i>0 and j>0:
        a=acts[i][j]
        if a==3:
            pi=po[i-1]; ri=ro[j-1]
            chosen.append((pi,ri,abs(float(preds[pi]["start"])-float(refs[ri]["start"]))))
            i-=1; j-=1
        elif a==1: i-=1
        elif a==2: j-=1
        else: raise RuntimeError("traceback failure")
    chosen.reverse()
    return chosen

def ambiguity_components(preds,refs,tol=TOL):
    pa=collections.defaultdict(set); ra=collections.defaultdict(set)
    for pi,p in enumerate(preds):
        ps=float(p["start"])
        for ri,r in enumerate(refs):
            if abs(ps-float(r["start"]))<=tol+1e-12:
                pa[pi].add(ri); ra[ri].add(pi)
    seenp=set(); seenr=set(); comps=[]; membership={}
    for seed in sorted(pa):
        if seed in seenp: continue
        q=[("p",seed)]; pn=set(); rn=set()
        while q:
            side,idx=q.pop()
            if side=="p":
                if idx in seenp: continue
                seenp.add(idx); pn.add(idx)
                q.extend(("r",x) for x in pa[idx])
            else:
                if idx in seenr: continue
                seenr.add(idx); rn.add(idx)
                q.extend(("p",x) for x in ra[idx])
        cid=len(comps)
        for x in pn: membership[("p",x)]=cid
        for x in rn: membership[("r",x)]=cid
        pc=collections.Counter(int(preds[x]["pitch"]) for x in pn)
        rc=collections.Counter(int(refs[x]["pitch"]) for x in rn)
        overlap=sum(min(pc[k],rc[k]) for k in pc.keys()|rc.keys())
        amb=any(len(pa[x])>1 for x in pn) or any(len(ra[x])>1 for x in rn)
        comps.append({"componentId":cid,"predictionCount":len(pn),"referenceCount":len(rn),"ambiguous":amb,"pitchMultisetOverlap":overlap})
    return comps,membership

def summarize(preds,refs):
    pairs=onset_match(preds,refs)
    comps,mem=ambiguity_components(preds,refs)
    wrong=0; exact=0; amb_pairs=0; unamb_pairs=0; unamb_wrong=0
    matched_per_comp=collections.Counter()
    for pi,ri,_ in pairs:
        cid=mem.get(("p",pi)); matched_per_comp[cid]+=1
        isamb=bool(cid is not None and comps[cid]["ambiguous"])
        same=int(preds[pi]["pitch"])==int(refs[ri]["pitch"])
        exact+=int(same); wrong+=int(not same)
        if isamb: amb_pairs+=1
        else:
            unamb_pairs+=1; unamb_wrong+=int(not same)
    amb_lower=0; amb_overlap=0; amb_match_total=0
    for c in comps:
        if not c["ambiguous"]: continue
        mc=matched_per_comp[c["componentId"]]
        amb_match_total+=mc
        amb_overlap+=min(mc,c["pitchMultisetOverlap"])
        amb_lower+=max(0,mc-c["pitchMultisetOverlap"])
    unmatched_ref=len(refs)-len(pairs)
    return {
      "predictionCount":len(preds),"referenceCount":len(refs),
      "onsetMatchedCount":len(pairs),"unmatchedReferenceCount":unmatched_ref,
      "unmatchedPredictionCount":len(preds)-len(pairs),
      "onsetMatchedReferenceRecall":len(pairs)/len(refs) if refs else None,
      "assignmentDependentExactPitchCount":exact,
      "assignmentDependentWrongPitchCount":wrong,
      "assignmentDependentExactPitchRate":exact/len(pairs) if pairs else None,
      "unambiguousMatchedCount":unamb_pairs,
      "unambiguousWrongPitchCount":unamb_wrong,
      "ambiguousMatchedCount":amb_pairs,
      "ambiguousPitchMismatchLowerBound":amb_lower,
      "ambiguityStablePitchErrorLowerBound":unamb_wrong+amb_lower,
      "ambiguousPitchMultisetOverlapWithinMatchedUpperBound":amb_overlap,
    }

def aggregate(track_rows):
    keys=["predictionCount","referenceCount","onsetMatchedCount","unmatchedReferenceCount","unmatchedPredictionCount","assignmentDependentExactPitchCount","assignmentDependentWrongPitchCount","unambiguousMatchedCount","unambiguousWrongPitchCount","ambiguousMatchedCount","ambiguousPitchMismatchLowerBound","ambiguityStablePitchErrorLowerBound","ambiguousPitchMultisetOverlapWithinMatchedUpperBound"]
    out={k:sum(int(r[k]) for r in track_rows) for k in keys}
    out["onsetMatchedReferenceRecall"]=out["onsetMatchedCount"]/out["referenceCount"] if out["referenceCount"] else None
    out["assignmentDependentExactPitchRate"]=out["assignmentDependentExactPitchCount"]/out["onsetMatchedCount"] if out["onsetMatchedCount"] else None
    out["unmatchedToAssignmentDependentWrongRatio"]=out["unmatchedReferenceCount"]/out["assignmentDependentWrongPitchCount"] if out["assignmentDependentWrongPitchCount"] else None
    out["unmatchedToStablePitchErrorLowerBoundRatio"]=out["unmatchedReferenceCount"]/out["ambiguityStablePitchErrorLowerBound"] if out["ambiguityStablePitchErrorLowerBound"] else None
    return out

def self_test():
    p=[{"start":0.00,"pitch":60},{"start":0.03,"pitch":62}]
    r=[{"start":0.04,"pitch":60},{"start":0.08,"pitch":62}]
    if len(onset_match(p,r))!=2: raise RuntimeError("cardinality self-test failed")
    s=summarize([{"start":0.0,"pitch":60}],[{"start":0.05,"pitch":72}])
    if s["onsetMatchedCount"]!=1 or s["assignmentDependentWrongPitchCount"]!=1: raise RuntimeError("50ms/pitch self-test failed")
    return {"status":"GUITARSET_MISSING_EVENT_DIAGNOSTIC_V1_SELF_TEST_PASS","audioRead":False,"basicPitchImported":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-dir",type=Path)
    ap.add_argument("--reference-dir",type=Path)
    ap.add_argument("--output",type=Path)
    ap.add_argument("--self-test",action="store_true")
    a=ap.parse_args()
    if a.self_test:
        print(json.dumps(self_test(),sort_keys=True)); return 0
    if None in (a.candidate_dir,a.reference_dir,a.output): raise SystemExit("--candidate-dir --reference-dir --output required")
    manifest,payloads=verify_candidates(a.candidate_dir)
    refs=discover_refs(a.reference_dir)
    tracks=[]; per_player={p:[] for p in EVAL_PLAYERS}; total_ref_events=0
    for stem in sorted(payloads):
        if stem not in refs: raise RuntimeError(f"missing reference {stem}")
        ref=load_refs(refs[stem]); total_ref_events+=len(ref)
        pred=payloads[stem]["events"]
        s=summarize(pred,ref)
        row={"trackStem":stem,"player":player_from_stem(stem),**s}
        tracks.append(row); per_player[row["player"]].append(row)
    player_aggs={p:aggregate(rows) for p,rows in per_player.items()}
    pooled=aggregate(tracks)
    replicate_all_players=all(player_aggs[p]["unmatchedReferenceCount"]>player_aggs[p]["assignmentDependentWrongPitchCount"] for p in EVAL_PLAYERS)
    report={
      "schema":"astra-guitarset-missing-event-diagnostic-v1-result",
      "dataset":"GuitarSet","datasetVersion":"1.1.0",
      "players":list(EVAL_PLAYERS),"trackCount":len(tracks),"referenceEventCount":total_ref_events,
      "candidateFreezeManifestSha256":sha256_file(a.candidate_dir/"candidate-freeze-manifest.json"),
      "onsetToleranceSeconds":TOL,
      "matchingPolicy":"maximum-cardinality onset-only, then minimum total absolute onset error; pitch never selects primary pairs",
      "tracks":tracks,"playersSummary":player_aggs,"pooled":pooled,
      "predeclaredReplicationGate":{
        "rule":"unmatchedReferenceCount > assignmentDependentWrongPitchCount pooled AND separately for each player 00/01/03",
        "pooledPass":pooled["unmatchedReferenceCount"]>pooled["assignmentDependentWrongPitchCount"],
        "allPlayersPass":replicate_all_players,
        "passed":pooled["unmatchedReferenceCount"]>pooled["assignmentDependentWrongPitchCount"] and replicate_all_players,
      },
      "predictionMutation":False,"thresholdSearch":False,
      "holdoutConsumed":True,
      "interpretationBoundary":"Diagnostic-only replication. Ambiguous chord assignment can inflate or deflate assignment-dependent pitch counts; stable lower-bound pitch errors are reported separately. No correction is authorized by this result."
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"GUITARSET_MISSING_EVENT_DIAGNOSTIC_V1_COMPLETE","trackCount":len(tracks),"referenceEventCount":total_ref_events,"playersSummary":player_aggs,"pooled":pooled,"replicationGate":report["predeclaredReplicationGate"]},indent=2,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
