#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from huggingface_hub import hf_hub_download, list_repo_files

REPO="xavriley/GAPS"
REV="b4c89a33a639c7ae903e74102dfbb3e147e1417f"
PREFIXES=(19,27,31,43,51,63,100,104,111,112,118,126,142,179,201,208,212,222,235,247,263,270,291,294,303,341,354,358,373,375)

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); a=ap.parse_args()
    files=list_repo_files(REPO,repo_type="dataset",revision=REV)
    chosen=[]
    for x in PREFIXES:
        hits=[p for p in files if p.startswith(f"audio/{x:03d}_") and p.endswith(".wav")]
        if len(hits)!=1: raise RuntimeError(f"audio prefix {x}: {hits}")
        chosen.append(hits[0])
    a.output_dir.mkdir(parents=True,exist_ok=True); rows=[]
    for rp in chosen:
        src=Path(hf_hub_download(REPO,rp,repo_type="dataset",revision=REV))
        dst=a.output_dir/src.name; dst.write_bytes(src.read_bytes())
        rows.append({"repoPath":rp,"file":dst.name,"stem":dst.stem,"sha256":sha256_file(dst),"bytes":dst.stat().st_size})
    mp=a.output_dir/"audio-manifest.json"
    mp.write_text(json.dumps({"schema":"astra-fresh-front-end-gaps-audio-v1","repo":REPO,"revision":REV,"trackCount":len(rows),"prefixes":list(PREFIXES),"files":rows},indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"GAPS_FROZEN_TEST_AUDIO_PASS","trackCount":len(rows),"manifestSha256":sha256_file(mp)},sort_keys=True))
if __name__=="__main__": main()
