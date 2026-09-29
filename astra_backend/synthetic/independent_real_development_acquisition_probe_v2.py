#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from pathlib import Path
from mutagen.mp3 import MP3

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-url",required=True)
    ap.add_argument("--audio-url",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(a.audio_url,headers={"User-Agent":"Mozilla/5.0","Referer":a.source_url})
    with urllib.request.urlopen(req,timeout=90) as r:
        data=r.read()
        status=getattr(r,"status",200)
        ctype=r.headers.get("Content-Type")
    if status!=200: raise RuntimeError(f"audio HTTP status {status}")
    if len(data)<1024: raise RuntimeError("audio response unexpectedly small")
    path=out/"P01.mp3"; path.write_bytes(data)
    duration=float(MP3(path).info.length)
    if not (4.0 <= duration <= 10.5):
        raise RuntimeError(f"duration outside frozen range: {duration}")
    result={
      "schema":"astra-independent-realdev-acquisition-probe-result-v2",
      "candidateId":"P01",
      "sourceUrl":a.source_url,
      "audioUrl":a.audio_url,
      "contentType":ctype,
      "bytes":len(data),
      "sha256":hashlib.sha256(data).hexdigest(),
      "durationSeconds":duration,
      "audioDownloaded":True,
      "modelInference":False,
      "optimizerSteps":0,
      "p1Accessed":False,"p2Accessed":False,"p3Accessed":False
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("ACQUISITION_V2="+json.dumps(result,sort_keys=True))

if __name__=="__main__": main()
