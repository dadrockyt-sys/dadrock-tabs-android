#!/usr/bin/env python3
"""V3A model-free frontend distribution audit.

No model loading, inference, training, thresholding, decoding, or tuning.
Compares frozen synthetic CQT features with freshly decoded V2B real-audio
features using the existing frontend preprocessing math.
"""
from __future__ import annotations

import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import librosa
from scipy.stats import wasserstein_distance

from tabcnn_runtime.preprocessing import (
    SAMPLE_RATE_HZ, CQT_BINS, extract_cqt_features, rms_normalize
)

SCHEMA="astra-v3a-frontend-distribution-audit-result-v1"
FLOOR_EPS=1e-6

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def _finite(a,name):
    a=np.asarray(a)
    if not np.isfinite(a).all():
        raise RuntimeError(f"nonfinite {name}")
    return a

def summarize_frames(x):
    x=_finite(np.asarray(x,dtype=np.float64),"features")
    if x.ndim!=2 or x.shape[1]!=CQT_BINS:
        raise ValueError("features must be frames x 192")
    med=np.median(x,axis=0)
    return {
      "frames":int(x.shape[0]),
      "mean":np.mean(x,axis=0).tolist(),
      "std":np.std(x,axis=0).tolist(),
      "median":med.tolist(),
      "mad":np.median(np.abs(x-med),axis=0).tolist(),
      "floorOccupancy":np.mean(x<=FLOOR_EPS,axis=0).tolist(),
      "percentiles":{
        "p01":np.percentile(x,1,axis=0).tolist(),
        "p05":np.percentile(x,5,axis=0).tolist(),
        "p50":np.percentile(x,50,axis=0).tolist(),
        "p95":np.percentile(x,95,axis=0).tolist(),
        "p99":np.percentile(x,99,axis=0).tolist()
      },
      "frameL2Percentiles":{
        "p05":float(np.percentile(np.linalg.norm(x,axis=1),5)),
        "p50":float(np.percentile(np.linalg.norm(x,axis=1),50)),
        "p95":float(np.percentile(np.linalg.norm(x,axis=1),95))
      },
      "temporalDiffL2Percentiles":{
        "p05":float(np.percentile(np.linalg.norm(np.diff(x,axis=0),axis=1),5)) if x.shape[0]>1 else 0.0,
        "p50":float(np.percentile(np.linalg.norm(np.diff(x,axis=0),axis=1),50)) if x.shape[0]>1 else 0.0,
        "p95":float(np.percentile(np.linalg.norm(np.diff(x,axis=0),axis=1),95)) if x.shape[0]>1 else 0.0
      }
    }

def context_norms(x):
    x=np.asarray(x,dtype=np.float64)
    if x.shape[0]==0: return {"p05":0.0,"p50":0.0,"p95":0.0}
    p=np.pad(x,((2,2),(0,0)),mode="edge")
    ctx=np.concatenate([p[i:i+x.shape[0]] for i in range(5)],axis=1)
    n=np.linalg.norm(ctx,axis=1)
    return {"p05":float(np.percentile(n,5)),"p50":float(np.percentile(n,50)),"p95":float(np.percentile(n,95))}

def load_real(manifest_path, real_dir):
    m=json.loads(Path(manifest_path).read_text())
    rows=[]
    clips=[]
    for c in m["clips"]:
        if c.get("kind")!="positive" and c.get("kind")!="negative-only":
            raise RuntimeError("unknown clip kind")
        path=Path(real_dir)/c["file"]
        if not path.exists():
            raise FileNotFoundError(path)
        got=sha256_file(path)
        if got!=c["sha256"]:
            raise RuntimeError(f"hash mismatch {c['id']}")
        y,sr=librosa.load(path,sr=None,mono=True)
        start=float(c["evaluationStartSeconds"]); end=float(c["evaluationEndSeconds"])
        lo=max(0,int(round(start*sr))); hi=min(len(y),int(round(end*sr)))
        if hi<=lo: raise RuntimeError(f"empty crop {c['id']}")
        y=librosa.resample(y[lo:hi],orig_sr=sr,target_sr=SAMPLE_RATE_HZ)
        feat=extract_cqt_features(rms_normalize(y)).squeeze(0).T.astype(np.float64,copy=False)
        _finite(feat,c["id"])
        rows.append(feat)
        clips.append({"id":c["id"],"kind":c["kind"],"frames":int(feat.shape[0]),"featureSha256":hashlib.sha256(np.ascontiguousarray(feat).tobytes()).hexdigest()})
    return np.concatenate(rows,axis=0),clips

def run(synthetic_npz,real_manifest,real_dir,out):
    d=np.load(synthetic_npz,allow_pickle=False)
    if "features" not in d.files: raise RuntimeError("synthetic features missing")
    sx=np.asarray(d["features"],dtype=np.float64).reshape(-1,CQT_BINS)
    rx,clips=load_real(real_manifest,real_dir)
    ssum=summarize_frames(sx); rsum=summarize_frames(rx)
    sm=np.asarray(ssum["mean"]); rm=np.asarray(rsum["mean"])
    ss=np.asarray(ssum["std"]); rs=np.asarray(rsum["std"])
    pooled=np.sqrt((ss**2+rs**2)/2.0)
    smd=np.divide(rm-sm,pooled,out=np.zeros_like(sm),where=pooled>1e-12)
    wass=np.array([wasserstein_distance(sx[:,i],rx[:,i]) for i in range(CQT_BINS)])
    slo=np.percentile(sx,1,axis=0); shi=np.percentile(sx,99,axis=0)
    rlo=np.percentile(rx,1,axis=0); rhi=np.percentile(rx,99,axis=0)
    overlap=np.maximum(0,np.minimum(shi,rhi)-np.maximum(slo,rlo))
    union=np.maximum(shi,rhi)-np.minimum(slo,rlo)
    overlap_ratio=np.divide(overlap,union,out=np.ones_like(overlap),where=union>1e-12)
    result={
      "schema":SCHEMA,
      "synthetic":{"path":str(synthetic_npz),"sha256":sha256_file(synthetic_npz),"summary":ssum,"contextWindowL2Percentiles":context_norms(sx)},
      "real":{"manifest":str(real_manifest),"clips":clips,"summary":rsum,"contextWindowL2Percentiles":context_norms(rx)},
      "distances":{
        "standardizedMeanDifference":smd.tolist(),
        "medianAbsoluteSmd":float(np.median(np.abs(smd))),
        "fractionAbsSmdAtLeast1":float(np.mean(np.abs(smd)>=1)),
        "fractionAbsSmdAtLeast2":float(np.mean(np.abs(smd)>=2)),
        "wassersteinPerBin":wass.tolist(),
        "wassersteinMedian":float(np.median(wass)),
        "wassersteinP95":float(np.percentile(wass,95)),
        "rangeOverlapPerBin":overlap_ratio.tolist(),
        "rangeOverlapMedian":float(np.median(overlap_ratio))
      },
      "execution":{"modelImports":0,"modelInferenceCount":0,"optimizerSteps":0,"thresholdSearch":False,"frontendChanged":False},
      "guards":{"v1_1Used":False,"p1Accessed":False,"p2Accessed":False,"p3Accessed":False,"a2Opened":False}
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V3A_RESULT="+json.dumps({
      "medianAbsoluteSmd":result["distances"]["medianAbsoluteSmd"],
      "fractionAbsSmdAtLeast1":result["distances"]["fractionAbsSmdAtLeast1"],
      "fractionAbsSmdAtLeast2":result["distances"]["fractionAbsSmdAtLeast2"],
      "wassersteinMedian":result["distances"]["wassersteinMedian"],
      "rangeOverlapMedian":result["distances"]["rangeOverlapMedian"]
    },sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--synthetic-npz",required=True)
    ap.add_argument("--real-manifest",required=True)
    ap.add_argument("--real-dir",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    run(a.synthetic_npz,a.real_manifest,a.real_dir,a.out)

if __name__=="__main__":
    main()
