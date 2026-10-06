#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, re
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files

REPO="xavriley/GAPS"
REV="b4c89a33a639c7ae903e74102dfbb3e147e1417f"
PREFIXES=(19,27,31,43,51,63,100,104,111,112,118,126,142,179,201,208,212,222,235,247,263,270,291,294,303,341,354,358,373,375)
FROZEN_PERFORMERS={"Maria Linnemann","Mateusz Kowalski","Massimo Agostinelli","Andrew Flory","Rachel Ginebra","Dionisio Aguado","Stephanie Jones","Edson Lopes","Yoo Sik Ro","Samantha Muir","Svetlana Alshanskaya","Seth Chiow","Han Eun","David Russell","Ingrid Riollot","Bob Hooper","Sanja Plohl","Edwin Jean-Baptiste-Erpenbach","Chris Saunders","Sanel Redzic","Thu Le","Damien Kelly","Aleksandar Antic","Petra Poláčková","Jacopo Dutti","Gian Marco Ciampa","Roland Dyens"}

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def choose_performer(row:dict)->str:
    vals=[str(v).strip() for v in row.values() if v is not None]
    exact=[v for v in vals if v in FROZEN_PERFORMERS]
    if len(exact)==1: return exact[0]
    for k,v in row.items():
        if any(t in k.lower() for t in ("performer","artist","player","guitarist")) and str(v).strip():
            return str(v).strip()
    raise RuntimeError(f"cannot identify performer from metadata row keys={list(row)}")

def row_for_prefix(rows,prefix:int):
    pat=re.compile(rf"(^|[^0-9]){prefix:03d}_")
    hits=[]
    for row in rows:
        joined=" | ".join(str(v) for v in row.values())
        if pat.search(joined): hits.append(row)
    if len(hits)!=1:
        # fallback: any integer-valued cell equal to prefix
        hits=[row for row in rows if any(str(v).strip().isdigit() and int(str(v).strip())==prefix for v in row.values())]
    if len(hits)!=1: raise RuntimeError(f"metadata prefix {prefix}: {len(hits)} hits")
    return hits[0]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); a=ap.parse_args()
    files=list_repo_files(REPO,repo_type="dataset",revision=REV)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    meta_src=Path(hf_hub_download(REPO,"gaps_metadata_with_splits.csv",repo_type="dataset",revision=REV))
    meta_dst=a.output_dir/"gaps_metadata_with_splits.csv"; meta_dst.write_bytes(meta_src.read_bytes())
    with meta_dst.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    receipts=[]; performers=[]
    for x in PREFIXES:
        audio_hits=[p for p in files if p.startswith(f"audio/{x:03d}_") and p.endswith(".wav")]
        if len(audio_hits)!=1: raise RuntimeError(f"audio prefix {x}: {audio_hits}")
        stem=Path(audio_hits[0]).stem
        midi_hits=[p for p in files if p.startswith("midi/") and Path(p).stem==stem and Path(p).suffix.lower() in (".mid",".midi")]
        if len(midi_hits)!=1: raise RuntimeError(f"midi {stem}: {midi_hits}")
        src=Path(hf_hub_download(REPO,midi_hits[0],repo_type="dataset",revision=REV))
        dst=a.output_dir/(stem+src.suffix); dst.write_bytes(src.read_bytes())
        row=row_for_prefix(rows,x)
        perf=choose_performer(row); performers.append(perf)
        receipts.append({"prefix":x,"stem":stem,"repoPath":midi_hits[0],"file":dst.name,"sha256":sha256_file(dst),"performer":perf})
    if set(performers)!=FROZEN_PERFORMERS: raise RuntimeError(f"performer set mismatch missing={sorted(FROZEN_PERFORMERS-set(performers))} extra={sorted(set(performers)-FROZEN_PERFORMERS)}")
    manifest={"schema":"astra-fresh-front-end-gaps-reference-v1","repo":REPO,"revision":REV,"trackCount":len(receipts),"performerCount":len(set(performers)),"metadataSha256":sha256_file(meta_dst),"files":receipts}
    mp=a.output_dir/"reference-manifest.json"; mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"GAPS_FROZEN_TEST_REFERENCES_PASS","trackCount":len(receipts),"performerCount":len(set(performers)),"manifestSha256":sha256_file(mp)},sort_keys=True))
if __name__=="__main__": main()
