#!/usr/bin/env python3
"""Materialize GuitarSet evaluation note references from a pinned v1.1.0 mirror.

This is transport/provenance recovery only. It fetches canonical note labels for
players 00/01/03 from the single-commit jhartquist/guitarset mirror and writes
minimal JAMS files consumed by the already-frozen scorer.
"""
from __future__ import annotations
import argparse, hashlib, json, math, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

EXPECTED_REVISION="4aca25487bef5cb0d2c4ec146218f9145402a776"
PLAYERS=(0,1,3)
EXPECTED_PER_PLAYER=60
EXPECTED_TOTAL=180
ERRATA_TRACKS={"04_BN3-154-E_comp","04_Jazz1-200-B_comp","02_Funk2-119-G_comp"}

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def get_json(url:str):
    last=None
    for attempt in range(10):
        req=urllib.request.Request(url,headers={"User-Agent":"dadrock-tabs-astra-guitarset-recovery/1"})
        try:
            with urllib.request.urlopen(req,timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            last=exc
            if attempt==9:
                break
            time.sleep(min(15,2+attempt*2))
    raise RuntimeError(f"mirror request failed after retries: {url}: {last}")

def verify_revision():
    info=get_json("https://huggingface.co/api/datasets/jhartquist/guitarset/revision/main")
    actual=str(info.get("sha",""))
    if actual!=EXPECTED_REVISION:
        raise RuntimeError(f"HuggingFace mirror revision mismatch: {actual}")
    return actual

def fetch_eval_rows():
    selected=[]
    page_size=5
    total_expected=360
    for offset in range(0,total_expected,page_size):
        params={
          "dataset":"jhartquist/guitarset",
          "config":"default","split":"train",
          "offset":str(offset),"length":str(page_size),
        }
        url="https://datasets-server.huggingface.co/rows?"+urllib.parse.urlencode(params)
        payload=get_json(url)
        if payload.get("partial") is True:
            raise RuntimeError("mirror rows response is partial")
        if int(payload.get("num_rows_total",-1))!=total_expected:
            raise RuntimeError(f"mirror total row count mismatch: {payload.get('num_rows_total')}")
        rows=payload.get("rows",[])
        if len(rows)!=page_size:
            raise RuntimeError(f"mirror page offset {offset}: expected {page_size} rows, got {len(rows)}")
        for wrapped in rows:
            row=wrapped["row"]
            if int(row["player"]) in PLAYERS:
                selected.append(row)
    if len(selected)!=EXPECTED_TOTAL:
        raise RuntimeError(f"expected {EXPECTED_TOTAL} evaluation rows, got {len(selected)}")
    counts={p:sum(int(r["player"])==p for r in selected) for p in PLAYERS}
    if counts!={0:60,1:60,3:60}:
        raise RuntimeError(f"evaluation player counts mismatch {counts}")
    selected.sort(key=lambda r:str(r["track_id"]))
    return selected

def materialize_row(row:dict,out_dir:Path):
    import jams
    track=str(row["track_id"])
    player=int(row["player"])
    if player not in PLAYERS or not track.startswith(f"{player:02d}_"):
        raise RuntimeError(f"track/player mismatch: {track} / {player}")
    if track in ERRATA_TRACKS:
        raise RuntimeError(f"evaluation unexpectedly intersects mirror errata: {track}")
    notes=row.get("notes",[])
    jam=jams.JAMS()
    by_string={i:[] for i in range(6)}
    for i,n in enumerate(notes):
        s=int(n["string"]); onset=float(n["onset_s"]); offset=float(n["offset_s"]); midi=float(n["midi"])
        if s not in by_string or not all(math.isfinite(x) for x in (onset,offset,midi)) or offset<onset:
            raise RuntimeError(f"invalid mirror note {track} index {i}")
        by_string[s].append((onset,offset,midi))
    jam.file_metadata.duration=max((x[1] for rows in by_string.values() for x in rows), default=0.0)
    for s in range(6):
        ann=jams.Annotation(namespace="note_midi")
        ann.annotation_metadata.data_source=f"jhartquist/guitarset@{EXPECTED_REVISION}:notes:string{s}"
        for onset,offset,midi in sorted(by_string[s],key=lambda x:(x[0],x[2],x[1])):
            ann.append(time=onset,duration=offset-onset,value=midi,confidence=None)
        jam.annotations.append(ann)
    path=out_dir/f"{track}.jams"
    jam.save(str(path))
    return {"trackStem":track,"player":f"{player:02d}","noteCount":len(notes),"sha256":sha256_file(path)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    rev=verify_revision()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    receipts=[]
    for row in fetch_eval_rows():
        receipts.append(materialize_row(row,a.output_dir))
    if len(receipts)!=EXPECTED_TOTAL or len({r["trackStem"] for r in receipts})!=EXPECTED_TOTAL:
        raise RuntimeError("evaluation mirror materialization count/uniqueness failure")
    counts={p:sum(r["player"]==p for r in receipts) for p in ("00","01","03")}
    if counts!={"00":60,"01":60,"03":60}: raise RuntimeError(f"player counts mismatch {counts}")
    manifest={
      "schema":"astra-guitarset-v1.1.0-hf-mirror-reference-materialization-v1",
      "mirror":"jhartquist/guitarset","mirrorRevision":rev,
      "upstream":"GuitarSet v1.1.0 Zenodo record 3371780",
      "canonicalLabelsDerivedFromOriginalJams":True,
      "mirrorErrataTracks":sorted(ERRATA_TRACKS),
      "evaluationPlayers":["00","01","03"],
      "evaluationIntersectsMirrorErrata":False,
      "trackCount":len(receipts),"playerCounts":counts,
      "files":sorted(receipts,key=lambda x:x["trackStem"]),
      "purpose":"transport-only recovery after repeated Zenodo annotation.zip HTTP 503; no score or prediction used to select this source",
    }
    mp=a.output_dir/"mirror-reference-manifest.json"
    mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"GUITARSET_HF_MIRROR_REFERENCE_MATERIALIZATION_PASS","mirrorRevision":rev,"trackCount":len(receipts),"playerCounts":counts,"manifestSha256":sha256_file(mp)},indent=2,sort_keys=True))

if __name__=="__main__": main()
