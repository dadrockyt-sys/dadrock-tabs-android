"""Go My Way reference-independent timebase V4.

High-resolution audio-only tempo/phase estimation:
- onset analysis at 22.05 kHz, 64-sample hop (~2.9 ms)
- fractional autocorrelation lag via parabolic interpolation
- constant-tempo and slowly-varying local-tempo candidates
- phase optimized against onset evidence only
Professional timing is comparison-only after freeze.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal, ndimage

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from v143_reference_free_timing import _bar_phase_from_accents
from v143_candidate_timing_adapter import build_subdivision_grid

EXPECTED_AUDIO_SOURCE="public/gomywayfullaitest.m4a"
EXPECTED_AUDIO_GIT_BLOB="5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"
ANALYSIS_SR=22050
NFFT=1024
HOP=64
MIN_BPM=80.0
MAX_BPM=180.0

def sha256_file(p: Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def write_json(p: Path,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def summary(v):
    x=np.asarray(v,dtype=float)
    if not len(x): return {"count":0,"mean":None,"median":None,"min":None,"max":None,"std":None}
    return {"count":int(len(x)),"mean":float(x.mean()),"median":float(np.median(x)),
            "min":float(x.min()),"max":float(x.max()),"std":float(x.std())}

def mono_resample(samples,sr):
    x=np.mean(samples,axis=1) if samples.ndim==2 else np.asarray(samples)
    x=x.astype(np.float64)-float(np.mean(x))
    if sr!=ANALYSIS_SR:
        g=math.gcd(int(sr),ANALYSIS_SR)
        x=signal.resample_poly(x,ANALYSIS_SR//g,int(sr)//g)
    return x

def onset_env(samples,sr):
    x=mono_resample(samples,sr)
    f,t,z=signal.stft(x,fs=ANALYSIS_SR,window="hann",nperseg=NFFT,
                      noverlap=NFFT-HOP,nfft=NFFT,boundary=None,padded=False)
    band=(f>=50)&(f<=8000)
    mag=np.log1p(20*np.abs(z[band]))
    flux=np.maximum(np.diff(mag,axis=1,prepend=mag[:,:1]),0).mean(axis=0)
    flux=ndimage.gaussian_filter1d(flux,1.5,mode="nearest")
    floor=np.quantile(flux,.2); env=np.maximum(flux-floor,0)
    s=np.quantile(env,.95)
    if s>1e-12: env=np.clip(env/s,0,4)
    low=(f>=40)&(f<=250)
    lowe=np.sqrt(np.mean(np.abs(z[low])**2,axis=0))
    ls=np.quantile(lowe,.95)
    lowe=np.clip(lowe/max(ls,1e-12),0,4)
    return env.astype(float),lowe.astype(float),t.astype(float)

def autocorr(v):
    x=np.asarray(v,float)-float(np.mean(v))
    n=len(x); m=1<<(2*n-1).bit_length()
    a=np.fft.irfft(np.fft.rfft(x,m)*np.conj(np.fft.rfft(x,m)),m)[:n].real
    a/=np.maximum(np.arange(n,0,-1),1)
    if a[0]>0:a/=a[0]
    return a

def parabolic_peak(y,i):
    if i<=0 or i>=len(y)-1:return float(i)
    ym, y0, yp=float(y[i-1]),float(y[i]),float(y[i+1])
    den=ym-2*y0+yp
    if abs(den)<1e-12:return float(i)
    delta=.5*(ym-yp)/den
    return float(i+np.clip(delta,-1,1))

def estimate_period(env):
    a=autocorr(env)
    hopsec=HOP/ANALYSIS_SR
    lo=int(math.floor(60/(MAX_BPM*hopsec)))
    hi=int(math.ceil(60/(MIN_BPM*hopsec)))
    lags=np.arange(lo,hi+1)
    scores=np.maximum(a[lags],0)
    # onset-interval support to reject half/double tempo ambiguities
    peaks,_=signal.find_peaks(env,distance=max(1,int(.08/hopsec)),prominence=max(.05,.12*np.std(env)))
    ioi=np.zeros_like(scores)
    if len(peaks)>=2:
        d=np.diff(peaks)
        for j,lag in enumerate(lags):
            tol=max(2,.05*lag)
            ioi[j]=np.sum(np.exp(-.5*((d-lag)/tol)**2))+0.35*np.sum(np.exp(-.5*((d-2*lag)/(2*tol))**2))
        if ioi.max()>0:ioi/=ioi.max()
    if scores.max()>0:scores/=scores.max()
    combined=.72*scores+.28*ioi
    k=int(np.argmax(combined))
    frac=parabolic_peak(combined,k)
    lag=float(lags[0]+frac)
    period=lag*hopsec
    bpm=60/period
    confidence=float(np.clip(combined[k],0,1))
    return period,bpm,confidence

def local_period_profile(env,times):
    win_s=24.0; hop_s=8.0
    centers=[]; periods=[]; confs=[]
    start=0.0; end=float(times[-1])
    while start<end:
        stop=min(end,start+win_s)
        mask=(times>=start)&(times<=stop)
        if int(mask.sum())>256:
            p,b,c=estimate_period(env[mask])
            centers.append(.5*(start+stop)); periods.append(p); confs.append(c)
        start+=hop_s
    if not centers: raise RuntimeError("no local tempo windows")
    centers=np.asarray(centers); periods=np.asarray(periods); confs=np.asarray(confs)
    # robustly suppress octave-level local outliers around weighted median period
    med=float(np.median(periods))
    good=(periods>.75*med)&(periods<1.25*med)
    periods=np.where(good,periods,med)
    periods=ndimage.gaussian_filter1d(periods,1.0,mode="nearest")
    return centers,periods,confs

def interp_env(t,env,times):
    return np.interp(t,times,env,left=0,right=0)

def grid_for_phase(start,period_fn,duration):
    beats=[]
    t=float(start)
    while t>-1.0:
        p=float(period_fn(max(t,0.0))); prev=t-p
        if prev<0: break
        t=prev
    while t<duration:
        if t>=0: beats.append(t)
        t+=float(period_fn(t))
        if len(beats)>5000:break
    return np.asarray(beats,float)

def optimize_phase(env,times,period_fn,duration,base_period):
    active=np.where(env>np.quantile(env,.65))[0]
    active_start=float(times[active[0]]) if len(active) else 0.0
    # search one beat cycle at sub-frame-like resolution (1 ms)
    offsets=np.arange(0,base_period,.001)
    best=None
    for o in offsets:
        start=active_start+o
        beats=grid_for_phase(start,period_fn,duration)
        if len(beats)<32:continue
        vals=interp_env(beats,env,times)
        score=float(np.mean(vals)+.25*np.quantile(vals,.25))
        if best is None or score>best[0]:best=(score,start,beats)
    if best is None:raise RuntimeError("phase search failed")
    return best

def build_candidate(name,samples,sr,mode,source_kind):
    env,low,times=onset_env(samples,sr)
    gp,gbpm,gconf=estimate_period(env)
    duration=float(times[-1])
    local=None
    if mode=="global":
        fn=lambda t:gp
    else:
        centers,periods,confs=local_period_profile(env,times)
        fn=lambda t:float(np.interp(t,centers,periods,left=periods[0],right=periods[-1]))
        local={"centersSeconds":[float(x) for x in centers],"periodSeconds":[float(x) for x in periods],
               "tempoBpm":[float(60/x) for x in periods],"confidence":[float(x) for x in confs]}
    phase_score,start,beats=optimize_phase(env,times,fn,duration,gp)
    fi=np.clip(np.searchsorted(times,beats),0,len(times)-1)
    accents=env[fi]+.25*low[fi]
    first,mod4,barconf=_bar_phase_from_accents(accents)
    intervals=np.diff(beats); bpm=60/intervals
    onsetvals=interp_env(beats,env,times)
    interval_cv=float(np.std(intervals)/max(np.mean(intervals),1e-9))
    quality=float(.55*np.clip(phase_score/1.5,0,1)+.25*np.clip(gconf,0,1)+.20*barconf)
    slots=build_subdivision_grid(beats,beats_per_measure=4,subdivisions_per_beat=4,
                                 measure_start=1,first_beat_in_measure=int(first))
    measures={}
    for s in slots:
        row=measures.setdefault(int(s.measure),{"measure":int(s.measure),"steps":{}})
        row["steps"][str(int(s.step))]=float(s.time_seconds)
    norm=[]
    for m in sorted(measures):
        st=measures[m]["steps"]; norm.append({"measure":m,"availableStepCount":len(st),
                                              "stepTimesSeconds":st,"startSeconds":st.get("0")})
    return {"name":name,"sourceKind":source_kind,"mode":mode,
      "estimator":{"name":"high-res-fractional-autocorr-v4","globalTempoBpm":float(gbpm),
                   "globalPeriodSeconds":float(gp),"tempoConfidence":float(gconf),
                   "phaseScore":float(phase_score),"barConfidence":float(barconf),
                   "firstBeatInMeasure":int(first),"downbeatIndexMod4":int(mod4),
                   "meterAssumption":{"numerator":4,"denominator":4}},
      "audioOnlySelectionEvidence":{"qualityScore":quality,"intervalCv":interval_cv,
                                    "meanBeatOnset":float(np.mean(onsetvals))},
      "localTempoProfile":local,
      "grid":{"beatCount":len(beats),"beatTimesSeconds":[float(x) for x in beats],
              "beatIntervalSummarySeconds":summary(intervals),"localTempoSummaryBpm":summary(bpm),
              "measureCountWithAnySlots":len(norm),"slotCount":len(slots),"measures":norm}}

def generate(args):
    source=Path(args.audio_source); wav=Path(args.audio_wav); model=Path(args.model)
    samples,sr=sf.read(str(wav),dtype="float32",always_2d=True)
    sep=BsRoformer6StemOnnxAdapter(model); stems=sep.separate_array(samples,int(sr))
    specs=[("raw_drums_global",stems["drums"],"global","separator-drums"),
           ("raw_drums_local",stems["drums"],"local","separator-drums"),
           ("raw_mix_global",samples,"global","raw-mix"),
           ("raw_mix_local",samples,"local","raw-mix")]
    candidates=[build_candidate(n,a,int(sr),m,k) for n,a,m,k in specs]
    primary=max(candidates,key=lambda c:(c["audioOnlySelectionEvidence"]["qualityScore"],
                                         c["estimator"]["barConfidence"],
                                         c["audioOnlySelectionEvidence"]["meanBeatOnset"]))["name"]
    out={"schemaVersion":4,"kind":"gomyway-reference-independent-timebase-v4-bundle",
         "status":"frozen-before-professional-comparison","referenceBlindGeneration":True,
         "professionalTimingMapReadDuringGeneration":False,"professionalScorerRowsReadDuringGeneration":False,
         "primarySelectionRule":"max audio-only qualityScore; tie barConfidence then meanBeatOnset",
         "primaryCandidateName":primary,
         "audio":{"sourcePath":EXPECTED_AUDIO_SOURCE,"expectedRepositoryGitBlob":EXPECTED_AUDIO_GIT_BLOB,
                  "sourceSha256":sha256_file(source),"decodedWavSha256":sha256_file(wav),
                  "sampleRate":int(sr),"durationSeconds":float(len(samples)/sr)},
         "separator":{"name":"BS-Roformer-SW 6-stem ONNX","modelSha256":FP16_SHA256},
         "analysis":{"sampleRate":ANALYSIS_SR,"hopSamples":HOP,"hopSeconds":HOP/ANALYSIS_SR,
                     "tempoSearchBpm":[MIN_BPM,MAX_BPM]},
         "candidates":candidates,
         "interpretationBoundary":"V4 uses only audio-side evidence and fractional/high-resolution tempo estimates. Professional reference is comparison-only."}
    write_json(Path(args.output_json),out)
    print(json.dumps({"primaryCandidateName":primary,"candidates":[{
        "name":c["name"],"tempo":c["estimator"]["globalTempoBpm"],
        "quality":c["audioOnlySelectionEvidence"]["qualityScore"],
        "barConfidence":c["estimator"]["barConfidence"],"beatCount":c["grid"]["beatCount"],
        "localTempo":c["grid"]["localTempoSummaryBpm"]} for c in candidates]},indent=2))

def ref_beats(ref):
    a=[]
    for r in ref["measureBoundaries"]:
        st=float(r["startSeconds"]); dur=float(r["durationSeconds"]); n=int(r["meter"]["numerator"])
        for b in range(n):a.append(st+dur*b/n)
    return np.asarray(a,float)

def seq_shift_diag(cb,rb,shift):
    pairs=[]
    for i,t in enumerate(cb):
        j=i+shift
        if 0<=j<len(rb):pairs.append((i,j,float(t-rb[j])))
    if not pairs:return None
    e=np.asarray([p[2] for p in pairs]); a=np.abs(e)
    x=np.asarray([p[1] for p in pairs],float)
    slope,inter=np.polyfit(x,e,1) if len(e)>=2 else (0,0)
    return {"beatIndexShift":shift,"pairCount":len(e),"meanSignedErrorSeconds":float(e.mean()),
            "medianSignedErrorSeconds":float(np.median(e)),"meanAbsoluteErrorSeconds":float(a.mean()),
            "medianAbsoluteErrorSeconds":float(np.median(a)),"p95AbsoluteErrorSeconds":float(np.quantile(a,.95)),
            "maxAbsoluteErrorSeconds":float(a.max()),"secondsPerReferenceBeat":float(slope),
            "predictedDriftAcrossSongSeconds":float(slope*max(len(rb)-1,1))}

def measure_starts(c):
    return {int(r["measure"]):float(r["startSeconds"]) for r in c["grid"]["measures"] if r.get("startSeconds") is not None}
def ref_starts(ref):
    return {int(r["measureNumber"]):float(r["startSeconds"]) for r in ref["measureBoundaries"]}

def measure_diag(cs,rs,shift):
    e=[]
    for cm,t in cs.items():
        rm=cm+shift
        if rm in rs:e.append((rm,t-rs[rm]))
    if not e:return None
    y=np.asarray([q[1] for q in e]); a=np.abs(y); x=np.asarray([q[0] for q in e],float)
    slope,inter=np.polyfit(x,y,1) if len(y)>=2 else (0,0)
    return {"measureShift":shift,"pairCount":len(y),"meanAbsoluteErrorSeconds":float(a.mean()),
            "medianAbsoluteErrorSeconds":float(np.median(a)),"meanSignedErrorSeconds":float(y.mean()),
            "secondsPerReferenceMeasure":float(slope),"predictedDriftAcross113MeasuresSeconds":float(slope*112)}

def compare(args):
    p=Path(args.candidate_json); frozen=sha256_file(p); bundle=json.loads(p.read_text())
    if bundle.get("referenceBlindGeneration") is not True:raise RuntimeError("not blind")
    refp=Path(args.professional_timing_map); ref=json.loads(refp.read_text())
    rb=ref_beats(ref); rs=ref_starts(ref); results=[]
    for c in bundle["candidates"]:
        cb=np.asarray(c["grid"]["beatTimesSeconds"],float)
        bd=[seq_shift_diag(cb,rb,s) for s in range(-16,17)]
        bd=[x for x in bd if x]
        bestb=min(bd,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["beatIndexShift"])))
        md=[measure_diag(measure_starts(c),rs,s) for s in range(-8,9)]; md=[x for x in md if x]
        bestm=min(md,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["measureShift"])))
        results.append({"name":c["name"],"globalTempoBpm":c["estimator"]["globalTempoBpm"],
                        "bestBeatIndexShiftDiagnostic":bestb,"bestMeasureShiftDiagnostic":bestm})
    out={"schemaVersion":4,"kind":"gomyway-reference-independent-timebase-v4-professional-comparison",
         "candidateFrozenSha256BeforeReferenceRead":frozen,"candidateMutatedAfterComparison":False,
         "comparisonIsDiagnosticOnly":True,"primaryCandidateNameFrozenBeforeReferenceRead":bundle["primaryCandidateName"],
         "professionalTimingMapSha256":sha256_file(refp),"results":results,
         "interpretationBoundary":"Sequence-aligned beat drift is diagnostic only and cannot modify V4."}
    write_json(Path(args.output_json),out)
    print(json.dumps({"candidateSha256":frozen,"primaryCandidateName":bundle["primaryCandidateName"],"results":results},indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="mode",required=True)
    g=sub.add_parser("generate"); g.add_argument("--audio-source",required=True); g.add_argument("--audio-wav",required=True)
    g.add_argument("--model",required=True); g.add_argument("--output-json",required=True); g.set_defaults(func=generate)
    c=sub.add_parser("compare"); c.add_argument("--candidate-json",required=True); c.add_argument("--professional-timing-map",required=True)
    c.add_argument("--output-json",required=True); c.set_defaults(func=compare)
    a=ap.parse_args();a.func(a)
if __name__=="__main__":main()
