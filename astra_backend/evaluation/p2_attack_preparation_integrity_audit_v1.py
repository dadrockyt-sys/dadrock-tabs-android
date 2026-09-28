#!/usr/bin/env python3
"""Model-free integrity audit for the frozen Astra P1/P2 preparation path.

No model import, model load, inference, optimizer, threshold search, or training.
The real-data command is intentionally usable only by a separately authorized
workflow; pure measurement helpers are covered by synthetic tests.
"""
from __future__ import annotations

import argparse, hashlib, json, math, subprocess
from collections import defaultdict
from pathlib import Path
import numpy as np

from guitartechs_real_training.real_training import midi_string_events, performance_key, visible_files
from tabcnn_runtime.preprocessing import SAMPLE_RATE_HZ, HOP_LENGTH_SAMPLES, rms_normalize

SCHEMA="astra-p2-attack-preparation-integrity-audit-v1"

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def finite_audio(x):
    x=np.asarray(x,dtype=np.float64)
    if x.ndim not in (1,2) or x.size==0 or not np.isfinite(x).all():
        raise ValueError("audio must be nonempty finite mono or frames-by-channels")
    return x

def mean_mix(x):
    x=finite_audio(x)
    return x if x.ndim==1 else np.mean(x,axis=1)

def rms(x):
    x=np.asarray(x,dtype=np.float64)
    return float(np.sqrt(np.mean(x*x))) if x.size else None

def seconds_to_index(seconds,sr):
    return int(round(float(seconds)*int(sr)))

def crop_coordinate(source_seconds,lag_ms,crop_start_frame,hop_seconds):
    aligned=float(source_seconds)+float(lag_ms)/1000.0
    crop_start=float(crop_start_frame)*float(hop_seconds)
    local=aligned-crop_start
    frame=int(round(local/float(hop_seconds)))
    return {"sourceSeconds":float(source_seconds),"lagSeconds":float(lag_ms)/1000.0,
            "alignedSeconds":aligned,"cropStartSeconds":crop_start,
            "cropLocalSeconds":local,"preparedFrame":frame}

def _slice_seconds(x,sr,a,b):
    lo=max(0,seconds_to_index(a,sr)); hi=min(len(x),seconds_to_index(b,sr))
    return np.asarray(x[lo:hi],dtype=np.float64)

def attack_metrics(audio,sr,t,spec):
    x=mean_mix(audio)
    pre=float(spec["rmsPreSeconds"]); post=float(spec["rmsPostSeconds"])
    pre_gap=float(spec["rmsPreGapSeconds"])
    before=_slice_seconds(x,sr,t-pre,t-pre_gap)
    after=_slice_seconds(x,sr,t,t+post)
    post_rms=rms(after); pre_rms=rms(before)
    diff=np.diff(after)
    return {
      "preRms":pre_rms,"postRms":post_rms,
      "postToPreRmsRatio":(post_rms/pre_rms if pre_rms not in (None,0.0) else None),
      "firstDifferenceEnergy":float(np.mean(diff*diff)) if diff.size else None,
    }

def stft_positive_flux(audio,sr,spec):
    x=mean_mix(audio)
    n=int(spec["stftNfft"]); hop=int(spec["stftHopSamples"])
    if len(x)<n: return np.empty((0,),dtype=np.float64), np.empty((0,),dtype=np.float64)
    win=np.hanning(n)
    frames=np.stack([x[i:i+n]*win for i in range(0,len(x)-n+1,hop)])
    mag=np.abs(np.fft.rfft(frames,axis=1))
    flux=np.zeros(len(mag),dtype=np.float64)
    if len(mag)>1: flux[1:]=np.maximum(mag[1:]-mag[:-1],0.0).sum(axis=1)
    times=(np.arange(len(mag))*hop+n/2.0)/float(sr)
    return flux,times

def local_peaks(values):
    v=np.asarray(values,dtype=np.float64)
    if len(v)<3: return np.empty((0,),dtype=np.int64)
    return np.flatnonzero((v[1:-1]>v[:-2]) & (v[1:-1]>=v[2:]))+1

def qualified_nearest_peak(values,times,target,search_seconds,context_seconds,mad_multiplier):
    v=np.asarray(values,dtype=np.float64); tm=np.asarray(times,dtype=np.float64)
    if len(v)!=len(tm) or not len(v): return None
    context=np.abs(tm-target)<=float(context_seconds)
    search=np.abs(tm-target)<=float(search_seconds)
    if np.sum(context)<3 or np.sum(search)<1: return None
    med=float(np.median(v[context])); mad=float(np.median(np.abs(v[context]-med)))
    threshold=med+float(mad_multiplier)*max(mad,1e-12)
    ids=[int(i) for i in local_peaks(v) if search[i] and v[i]>threshold]
    if not ids: return None
    i=min(ids,key=lambda j:(abs(tm[j]-target),-v[j],j))
    return {"offsetSeconds":float(tm[i]-target),"peakTimeSeconds":float(tm[i]),
            "peakValue":float(v[i]),"threshold":threshold}

def cqt_novelty(features):
    x=np.asarray(features,dtype=np.float64)
    if x.ndim!=2: raise ValueError("prepared CQT must be frames x bins")
    d=np.diff(x,axis=0,prepend=x[:1])
    return np.maximum(d,0.0).sum(axis=1), np.linalg.norm(d,axis=1)

def nearest_cqt_peak(features,ref_frame,hop_seconds,spec):
    flux,_=cqt_novelty(features); n=len(flux)
    times=np.arange(n,dtype=np.float64)*float(hop_seconds)
    target=float(ref_frame)*float(hop_seconds)
    return qualified_nearest_peak(flux,times,target,
        float(spec["cqtPeakSearchFrames"])*float(hop_seconds),
        float(spec["cqtPeakContextFrames"])*float(hop_seconds),
        spec["peakMadMultiplier"])

def group_simultaneous_events(events,tolerance_seconds):
    rows=sorted(events,key=lambda e:(float(e["sourceStart"]),str(e["id"])))
    out=[]
    for e in rows:
        if not out or abs(float(e["sourceStart"])-out[-1]["sourceStart"])>tolerance_seconds:
            out.append({"sourceStart":float(e["sourceStart"]),"events":[e]})
        else: out[-1]["events"].append(e)
    return out

def _ffprobe(path):
    cmd=["ffprobe","-v","error","-select_streams","a:0","-show_entries",
         "stream=sample_rate,channels,channel_layout","-of","json",str(path)]
    j=json.loads(subprocess.check_output(cmd,text=True))
    if len(j.get("streams",[]))!=1: raise RuntimeError("expected one audio stream")
    s=j["streams"][0]
    return {"sampleRate":int(s["sample_rate"]),"channels":int(s["channels"]),
            "channelLayout":s.get("channel_layout")}

def decode_native_channels(path):
    meta=_ffprobe(path); sr=meta["sampleRate"]; ch=meta["channels"]
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",str(path),"-vn",
         "-f","f32le","-acodec","pcm_f32le","pipe:1"]
    raw=subprocess.check_output(cmd)
    x=np.frombuffer(raw,dtype="<f4").copy()
    if x.size%ch: raise RuntimeError("native decode channel alignment mismatch")
    return x.reshape(-1,ch),meta

def decode_frozen_mono(path):
    cmd=["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-i",str(path),"-vn",
         "-ac","1","-ar",str(SAMPLE_RATE_HZ),"-f","f32le","-acodec","pcm_f32le","pipe:1"]
    x=np.frombuffer(subprocess.check_output(cmd),dtype="<f4").copy()
    if not x.size or not np.isfinite(x).all(): raise RuntimeError("invalid frozen decoded audio")
    return x

def _source_paths(root,capture_key):
    _,_,pkey,view=capture_key.split("|")
    midis=[]; audios=[]
    for p in visible_files(root):
        if performance_key(p)!=pkey: continue
        if p.suffix.lower() in (".mid",".midi"): midis.append(p)
        elif p.suffix.lower() in (".wav",".mp3") and p.parent.name==view: audios.append(p)
    if len(midis)!=1 or len(audios)!=1:
        raise RuntimeError(f"source ambiguity for {capture_key}: midi={len(midis)} audio={len(audios)}")
    return midis[0],audios[0]

def load_prepared(root,performer,spec):
    found=[]
    expected={x["captureKey"]:x for x in spec["captures"] if x["performer"]==performer}
    for mp in sorted(Path(root).glob("*/meta.json")):
        m=json.loads(mp.read_text()); fp=mp.parent/"features.npy"
        key=m.get("captureKey")
        if key not in expected: raise RuntimeError("unexpected prepared capture")
        e=expected[key]
        if sha256_file(fp)!=e["featureSha256"] or m["prepared"]["targetSha256"]!=e["targetSha256"]:
            raise RuntimeError("prepared crop identity mismatch")
        if m.get("alignmentCorrectionsSha256")!=spec["pins"]["alignmentCorrectionsFileSha256"]:
            raise RuntimeError("correction identity mismatch")
        x=np.load(fp,allow_pickle=False).astype(np.float32,copy=False)
        if x.shape!=tuple(spec["preparedShape"]) or not np.isfinite(x).all():
            raise RuntimeError("prepared feature shape/finite mismatch")
        found.append((m,x))
    keys=[m["captureKey"] for m,_ in found]
    if len(keys)!=4 or len(set(keys))!=4 or set(keys)!=set(expected):
        raise RuntimeError("population must contain exactly four unique frozen captures")
    return found

def _midi_source_starts(midi_path,capture_key,lag_ms):
    notes=midi_string_events(midi_path)
    # Map IDs exactly as prepared_event_adapter_v1 does: one canonical event per source note.
    # We match prepared scorable events by string/fret/aligned start instead of relying on IDs.
    open_midi={"E":40,"A":45,"D":50,"G":55,"B":59,"e":64}
    order=["E","A","D","G","B","e"]
    rows=[]
    for s,name in enumerate(order):
        for i,(st,en,pitch) in enumerate(notes.get(name,[])):
            fret=int(pitch)-open_midi[name]
            if 0<=fret<=19:
                rows.append({"id":f"{capture_key}:{name}:{i}","string":s,"fret":fret,
                             "sourceStart":float(st),"sourceEnd":float(en),
                             "alignedStart":float(st)+lag_ms/1000.0})
    return rows

def audit_capture(meta,features,source_root,spec):
    key=meta["captureKey"]; midi,audio=_source_paths(source_root,key)
    if sha256_file(midi)!=meta["midiSourceSha256"] or sha256_file(audio)!=meta["audioSourceSha256"]:
        raise RuntimeError("selected member hash differs from frozen prepared receipt")
    native,nmeta=decode_native_channels(audio)
    frozen=decode_frozen_mono(audio)
    norm=rms_normalize(frozen.copy())
    hop=float(meta["hopSeconds"])
    if not math.isclose(hop,HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ,rel_tol=0,abs_tol=1e-12):
        raise RuntimeError("prepared hop mismatch")
    if int(meta["prepared"]["crop"]["startFrame"])!=int(meta["cropSelection"]["startFrame"]):
        raise RuntimeError("crop start disagreement")
    src=_midi_source_starts(midi,key,float(meta["lagMs"]))
    by_sf=defaultdict(list)
    for r in src: by_sf[(r["string"],r["fret"])].append(r)
    used=set(); per_note=[]
    for e in meta["prepared"]["scorableEvents"]:
        aligned=float(e["start"])+float(meta["prepared"]["crop"]["startSeconds"])
        cands=by_sf[(int(e["string"]),int(e["fret"]))]
        cand=min(cands,key=lambda r:abs(r["alignedStart"]-aligned))
        if abs(cand["alignedStart"]-aligned)>1e-6: raise RuntimeError("source/prepared event coordinate mismatch")
        ident=(cand["id"],e["id"])
        if ident in used: raise RuntimeError("duplicate event mapping")
        used.add(ident)
        source_t=cand["sourceStart"]; aligned_t=cand["alignedStart"]
        coord=crop_coordinate(source_t,meta["lagMs"],meta["prepared"]["crop"]["startFrame"],hop)
        ref_frame=int(round(float(e["start"])/hop))
        raw=attack_metrics(frozen,SAMPLE_RATE_HZ,aligned_t,spec["measurement"])
        raw_norm=attack_metrics(norm,SAMPLE_RATE_HZ,aligned_t,spec["measurement"])
        flux,times=stft_positive_flux(frozen,SAMPLE_RATE_HZ,spec["measurement"])
        peak=qualified_nearest_peak(flux,times,aligned_t,spec["measurement"]["rawPeakSearchSeconds"],
                                    spec["measurement"]["rawPeakContextSeconds"],spec["measurement"]["peakMadMultiplier"])
        cf,cl2=cqt_novelty(features)
        cpeak=nearest_cqt_peak(features,ref_frame,hop,spec["measurement"])
        row={"id":e["id"],"string":int(e["string"]),"fret":int(e["fret"]),
             "sourceAnnotationSeconds":source_t,"alignedAnnotationSeconds":aligned_t,
             "cropLocalAnnotationSeconds":float(e["start"]),"preparedFrame":ref_frame,
             "coordinate":coord,"rawResampled":raw,"rmsNormalizedResampled":raw_norm,
             "rawTransientPeak":peak,"preparedCqtPositiveFluxAtReference":float(cf[ref_frame]),
             "preparedCqtFrameDifferenceL2AtReference":float(cl2[ref_frame]),"preparedCqtNoveltyPeak":cpeak}
        per_note.append(row)
    attacks=group_simultaneous_events(
        [{"id":r["id"],"sourceStart":r["sourceAnnotationSeconds"],"row":r} for r in per_note],
        spec["measurement"]["simultaneousToleranceSeconds"])
    per_attack=[]
    for g in attacks:
        rows=[x["row"] for x in g["events"]]
        first=min(rows,key=lambda r:r["id"])
        per_attack.append({"sourceAnnotationSeconds":g["sourceStart"],"noteCount":len(rows),
                           "eventIds":sorted(r["id"] for r in rows),
                           "rawResampled":first["rawResampled"],
                           "rmsNormalizedResampled":first["rmsNormalizedResampled"],
                           "rawTransientPeak":first["rawTransientPeak"],
                           "preparedCqtPositiveFluxAtReference":first["preparedCqtPositiveFluxAtReference"],
                           "preparedCqtFrameDifferenceL2AtReference":first["preparedCqtFrameDifferenceL2AtReference"],
                           "preparedCqtNoveltyPeak":first["preparedCqtNoveltyPeak"]})
    # Native channels are descriptive only; report channel and mixed global levels, never model inputs.
    native_rms=[rms(native[:,i]) for i in range(native.shape[1])]
    mono_native=mean_mix(native)
    return {"captureKey":key,"performer":meta["performer"],"category":meta["category"],
            "source":{"midiSha256":sha256_file(midi),"audioSha256":sha256_file(audio),
                      **nmeta,"nativeFrames":int(native.shape[0]),"nativeChannelRms":native_rms,
                      "nativeMeanMixRms":rms(mono_native),
                      "frozenResampledSampleRate":SAMPLE_RATE_HZ,"frozenResampledFrames":len(frozen)},
            "preparation":{"lagMs":meta["lagMs"],"hopSeconds":hop,
                           "cropStartFrame":meta["prepared"]["crop"]["startFrame"],
                           "cropStartSeconds":meta["prepared"]["crop"]["startSeconds"],
                           "cropEndSeconds":meta["prepared"]["crop"]["endSeconds"],
                           "featureSha256":meta["featureSha256"],
                           "targetSha256":meta["prepared"]["targetSha256"]},
            "perNoteEvents":per_note,"acousticAttacks":per_attack}

def _vals(rows,path):
    out=[]
    for r in rows:
        v=r
        for k in path: v=v.get(k) if isinstance(v,dict) else None
        if isinstance(v,(int,float)) and math.isfinite(v): out.append(float(v))
    return out

def summarize_capture(c):
    a=c["acousticAttacks"]
    def sm(path):
        v=_vals(a,path)
        return {"count":len(v),"median":float(np.median(v)) if v else None,
                "mean":float(np.mean(v)) if v else None,
                "min":min(v) if v else None,"max":max(v) if v else None}
    return {"captureKey":c["captureKey"],"attackCount":len(a),"noteEventCount":len(c["perNoteEvents"]),
            "postRms":sm(["rawResampled","postRms"]),
            "postToPreRmsRatio":sm(["rawResampled","postToPreRmsRatio"]),
            "firstDifferenceEnergy":sm(["rawResampled","firstDifferenceEnergy"]),
            "preparedCqtPositiveFlux":sm(["preparedCqtPositiveFluxAtReference"]),
            "rawPeakOffsetSeconds":sm(["rawTransientPeak","offsetSeconds"]),
            "cqtPeakOffsetSeconds":sm(["preparedCqtNoveltyPeak","offsetSeconds"])}

def run(args):
    spec=json.loads(Path(args.spec).read_text())
    if spec.get("schema")!="astra-p2-attack-preparation-integrity-audit-spec-v1":
        raise RuntimeError("spec schema mismatch")
    p1=load_prepared(args.p1_dir,"P1",spec); p2=load_prepared(args.p2_dir,"P2",spec)
    caps=[]
    for performer,pop,root in (("P1",p1,args.p1_source_root),("P2",p2,args.p2_source_root)):
        for m,x in pop: caps.append(audit_capture(m,x,root,spec))
    summaries=[summarize_capture(c) for c in caps]
    result={"schema":SCHEMA,"specSha256":sha256_file(args.spec),"captures":caps,
            "captureSummaries":summaries,
            "execution":{"optimizerSteps":0,"modelsLoaded":0,"modelInference":False,
                         "thresholdSearch":False,"thresholdRetuning":False,
                         "p1Accessed":True,"p2Accessed":True,"p3Opened":False},
            "interpretationPolicy":"Descriptive only. No parameter may be selected from P1/P2 outcomes."}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    for n in ("spec","p1-source-root","p2-source-root","p1-dir","p2-dir","out"):
        p.add_argument("--"+n,required=True)
    run(p.parse_args())

if __name__=="__main__": main()
