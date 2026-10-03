"""Go My Way reference-independent timebase V5.

Cross-source beat-lattice consensus:
- high-resolution onset envelopes from raw drums and raw mix
- continuous BPM/phase search using joint support
- optional slowly-varying local BPM profile constrained by global consensus
- no professional timing/reference access during generation
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
BPM_MIN=100.0
BPM_MAX=160.0

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def write_json(p,d):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def summarize(v):
    x=np.asarray(v,float)
    if not len(x): return {"count":0,"mean":None,"median":None,"min":None,"max":None,"std":None}
    return {"count":int(len(x)),"mean":float(x.mean()),"median":float(np.median(x)),
            "min":float(x.min()),"max":float(x.max()),"std":float(x.std())}

def mono_resample(samples,sr):
    x=np.mean(samples,axis=1) if samples.ndim==2 else np.asarray(samples)
    x=x.astype(np.float64)-float(np.mean(x))
    if int(sr)!=ANALYSIS_SR:
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
    flux=ndimage.gaussian_filter1d(flux,1.4,mode="nearest")
    floor=np.quantile(flux,.2)
    env=np.maximum(flux-floor,0)
    scale=np.quantile(env,.95)
    if scale>1e-12: env=np.clip(env/scale,0,4)
    low=(f>=40)&(f<=250)
    lowe=np.sqrt(np.mean(np.abs(z[low])**2,axis=0))
    ls=np.quantile(lowe,.95)
    lowe=np.clip(lowe/max(ls,1e-12),0,4)
    return env.astype(float),lowe.astype(float),t.astype(float)

def interp(t,env,times):
    return np.interp(t,times,env,left=0,right=0)

def active_bounds(cons,times):
    thr=float(np.quantile(cons,.60))
    idx=np.where(cons>=thr)[0]
    if not len(idx): return float(times[0]),float(times[-1])
    return float(times[idx[0]]),float(times[idx[-1]])

def lattice(start,period,end):
    k0=int(math.floor((0-start)/period))
    t=start+k0*period
    vals=[]
    while t<end+period:
        if t>=0: vals.append(t)
        t+=period
        if len(vals)>5000: break
    return np.asarray(vals,float)

def lattice_score(beats,drum_env,mix_env,times):
    d=interp(beats,drum_env,times); m=interp(beats,mix_env,times)
    joint=np.sqrt(np.maximum(d,0)*np.maximum(m,0))
    support=np.minimum(d,m)
    low_support=float(np.mean(support<0.15))
    return float(0.45*np.mean(joint)+0.35*np.mean(support)+0.20*np.quantile(joint,.25)-0.20*low_support)

def search_global(drum_env,mix_env,times):
    cons=np.sqrt(np.maximum(drum_env,0)*np.maximum(mix_env,0))
    a0,a1=active_bounds(cons,times)
    best=None
    # coarse
    for bpm in np.arange(BPM_MIN,BPM_MAX+1e-9,0.10):
        p=60.0/bpm
        for phase_frac in np.arange(0.0,1.0,1/48):
            st=a0+phase_frac*p
            b=lattice(st,p,a1)
            if len(b)<64: continue
            s=lattice_score(b,drum_env,mix_env,times)
            cand=(s,float(bpm),float(st),b)
            if best is None or cand[0]>best[0]: best=cand
    if best is None: raise RuntimeError("global search failed")
    _,bbpm,bst,_=best
    # fine
    best2=None
    for bpm in np.arange(max(BPM_MIN,bbpm-.35),min(BPM_MAX,bbpm+.35)+1e-9,0.005):
        p=60.0/bpm
        center_frac=((bst-a0)/p)%1.0
        for delta in np.arange(-.06,.0601,.002):
            frac=(center_frac+delta)%1.0
            st=a0+frac*p
            b=lattice(st,p,a1)
            if len(b)<64: continue
            s=lattice_score(b,drum_env,mix_env,times)
            cand=(s,float(bpm),float(st),b)
            if best2 is None or cand[0]>best2[0]: best2=cand
    return best2

def local_profile(drum_env,mix_env,times,global_bpm):
    centers=[]; bpms=[]; scores=[]
    start=float(times[0]); end=float(times[-1]); win=28.0; step=8.0
    while start<end:
        stop=min(end,start+win)
        mask=(times>=start)&(times<=stop)
        if int(mask.sum())<512: break
        td=times[mask]; de=drum_env[mask]; me=mix_env[mask]
        cons=np.sqrt(np.maximum(de,0)*np.maximum(me,0))
        a0,a1=active_bounds(cons,td)
        best=None
        lo=max(BPM_MIN,global_bpm-8); hi=min(BPM_MAX,global_bpm+8)
        for bpm in np.arange(lo,hi+1e-9,.05):
            p=60/bpm
            for frac in np.arange(0,1,1/32):
                b=lattice(a0+frac*p,p,a1)
                if len(b)<12: continue
                s=lattice_score(b,de,me,td)-0.0025*abs(bpm-global_bpm)
                cand=(s,float(bpm))
                if best is None or cand[0]>best[0]: best=cand
        if best:
            centers.append(.5*(start+stop)); scores.append(best[0]); bpms.append(best[1])
        start+=step
    if not centers: raise RuntimeError("local profile failed")
    bpms=np.asarray(bpms,float)
    # generic smoothness prior against rapid local tempo jumps
    med=ndimage.median_filter(bpms,size=3,mode="nearest")
    bpms=0.45*bpms+0.55*med
    bpms=ndimage.gaussian_filter1d(bpms,.8,mode="nearest")
    return np.asarray(centers),bpms,np.asarray(scores)

def integrate_local(start,centers,bpms,end):
    beats=[]; t=float(start)
    while t>-1:
        p=60/float(np.interp(max(t,0),centers,bpms,left=bpms[0],right=bpms[-1]))
        prev=t-p
        if prev<0: break
        t=prev
    while t<=end:
        if t>=0: beats.append(t)
        bpm=float(np.interp(t,centers,bpms,left=bpms[0],right=bpms[-1]))
        t+=60/bpm
        if len(beats)>5000: break
    return np.asarray(beats,float)

def build_candidate(name,beats,drum_env,mix_env,low_mix,times,global_bpm,mode,local=None):
    fi=np.clip(np.searchsorted(times,beats),0,len(times)-1)
    accents=mix_env[fi]+0.25*low_mix[fi]
    first,mod4,barconf=_bar_phase_from_accents(accents)
    intervals=np.diff(beats); bpms=60/intervals
    score=lattice_score(beats,drum_env,mix_env,times)
    interval_cv=float(np.std(intervals)/max(np.mean(intervals),1e-9))
    quality=float(0.75*np.clip(score/1.5,0,1)+0.15*np.clip(1-interval_cv/.15,0,1)+0.10*barconf)
    slots=build_subdivision_grid(beats,beats_per_measure=4,subdivisions_per_beat=4,
                                 measure_start=1,first_beat_in_measure=int(first))
    measures={}
    for s in slots:
        row=measures.setdefault(int(s.measure),{"measure":int(s.measure),"steps":{}})
        row["steps"][str(int(s.step))]=float(s.time_seconds)
    norm=[]
    for m in sorted(measures):
        st=measures[m]["steps"]
        norm.append({"measure":m,"availableStepCount":len(st),"stepTimesSeconds":st,"startSeconds":st.get("0")})
    return {"name":name,"mode":mode,
      "estimator":{"name":"cross-source-beat-lattice-consensus-v5","globalTempoBpm":float(global_bpm),
                   "barConfidence":float(barconf),"firstBeatInMeasure":int(first),"downbeatIndexMod4":int(mod4),
                   "meterAssumption":{"numerator":4,"denominator":4}},
      "audioOnlySelectionEvidence":{"qualityScore":quality,"jointLatticeScore":float(score),"intervalCv":interval_cv},
      "localTempoProfile":local,
      "grid":{"beatCount":len(beats),"beatTimesSeconds":[float(x) for x in beats],
              "beatIntervalSummarySeconds":summarize(intervals),"localTempoSummaryBpm":summarize(bpms),
              "measureCountWithAnySlots":len(norm),"slotCount":len(slots),"measures":norm}}

def generate(args):
    source=Path(args.audio_source); wav=Path(args.audio_wav); model=Path(args.model)
    samples,sr=sf.read(str(wav),dtype="float32",always_2d=True)
    sep=BsRoformer6StemOnnxAdapter(model); stems=sep.separate_array(samples,int(sr))
    de,dl,times=onset_env(stems["drums"],int(sr))
    me,ml,times2=onset_env(samples,int(sr))
    if len(times)!=len(times2) or np.max(np.abs(times-times2))>1e-9: raise RuntimeError("time axes differ")
    gs,gbpm,gstart,gbeats=search_global(de,me,times)
    centers,bpms,lscores=local_profile(de,me,times,gbpm)
    lbeats=integrate_local(gstart,centers,bpms,float(times[-1]))
    candidates=[
      build_candidate("consensus_global",gbeats,de,me,ml,times,gbpm,"global"),
      build_candidate("consensus_local",lbeats,de,me,ml,times,gbpm,"local",
        {"centersSeconds":[float(x) for x in centers],"tempoBpm":[float(x) for x in bpms],
         "scores":[float(x) for x in lscores]})
    ]
    primary=max(candidates,key=lambda c:(c["audioOnlySelectionEvidence"]["qualityScore"],
                                         c["estimator"]["barConfidence"]))["name"]
    out={"schemaVersion":5,"kind":"gomyway-reference-independent-timebase-v5-bundle",
         "status":"frozen-before-professional-comparison","referenceBlindGeneration":True,
         "professionalTimingMapReadDuringGeneration":False,"professionalScorerRowsReadDuringGeneration":False,
         "primaryCandidateName":primary,
         "primarySelectionRule":"max audio-only qualityScore; tie barConfidence",
         "audio":{"sourcePath":EXPECTED_AUDIO_SOURCE,"expectedRepositoryGitBlob":EXPECTED_AUDIO_GIT_BLOB,
                  "sourceSha256":sha256_file(source),"decodedWavSha256":sha256_file(wav),
                  "sampleRate":int(sr),"durationSeconds":float(len(samples)/sr)},
         "separator":{"name":"BS-Roformer-SW 6-stem ONNX","modelSha256":FP16_SHA256},
         "analysis":{"sampleRate":ANALYSIS_SR,"hopSamples":HOP,"bpmSearch":[BPM_MIN,BPM_MAX],
                     "globalSearchBpmStepCoarse":0.10,"globalSearchBpmStepFine":0.005},
         "candidates":candidates,
         "interpretationBoundary":"V5 uses joint transient support from independently derived raw drums and raw mix. All selection occurs before reference access."}
    write_json(args.output_json,out)
    print(json.dumps({"primaryCandidateName":primary,"globalSearchTempoBpm":gbpm,"globalSearchScore":gs,
      "candidates":[{"name":c["name"],"quality":c["audioOnlySelectionEvidence"]["qualityScore"],
                     "barConfidence":c["estimator"]["barConfidence"],"beatCount":c["grid"]["beatCount"],
                     "tempoSummary":c["grid"]["localTempoSummaryBpm"]} for c in candidates]},indent=2))

def ref_beats(ref):
    a=[]
    for r in ref["measureBoundaries"]:
        st=float(r["startSeconds"]); dur=float(r["durationSeconds"]); n=int(r["meter"]["numerator"])
        for b in range(n): a.append(st+dur*b/n)
    return np.asarray(a,float)

def beat_diag(cb,rb,shift):
    pairs=[]
    for i,t in enumerate(cb):
        j=i+shift
        if 0<=j<len(rb): pairs.append((j,float(t-rb[j])))
    if len(pairs)<2:return None
    x=np.asarray([p[0] for p in pairs],float); e=np.asarray([p[1] for p in pairs],float); a=np.abs(e)
    slope,inter=np.polyfit(x,e,1)
    n=len(e)
    thirds=np.array_split(np.arange(n),3)
    seg={}
    for lab,ix in zip(("early","middle","late"),thirds):
        seg[lab]={"meanSignedErrorSeconds":float(np.mean(e[ix])),
                  "medianAbsoluteErrorSeconds":float(np.median(np.abs(e[ix])))}
    return {"beatIndexShift":shift,"pairCount":n,"meanSignedErrorSeconds":float(e.mean()),
            "medianSignedErrorSeconds":float(np.median(e)),"meanAbsoluteErrorSeconds":float(a.mean()),
            "medianAbsoluteErrorSeconds":float(np.median(a)),"p95AbsoluteErrorSeconds":float(np.quantile(a,.95)),
            "maxAbsoluteErrorSeconds":float(a.max()),"secondsPerReferenceBeat":float(slope),
            "predictedDriftAcrossSongSeconds":float(slope*max(len(rb)-1,1)),"segments":seg}

def measure_starts(c):
    return {int(r["measure"]):float(r["startSeconds"]) for r in c["grid"]["measures"] if r.get("startSeconds") is not None}
def ref_starts(ref):
    return {int(r["measureNumber"]):float(r["startSeconds"]) for r in ref["measureBoundaries"]}

def measure_diag(cs,rs,shift):
    pairs=[]
    for cm,t in cs.items():
        rm=cm+shift
        if rm in rs:pairs.append((rm,t-rs[rm]))
    if len(pairs)<2:return None
    x=np.asarray([p[0] for p in pairs],float); e=np.asarray([p[1] for p in pairs],float); a=np.abs(e)
    slope,inter=np.polyfit(x,e,1)
    return {"measureShift":shift,"pairCount":len(e),"meanAbsoluteErrorSeconds":float(a.mean()),
            "medianAbsoluteErrorSeconds":float(np.median(a)),"meanSignedErrorSeconds":float(e.mean()),
            "secondsPerReferenceMeasure":float(slope),"predictedDriftAcross113MeasuresSeconds":float(slope*112)}

def compare(args):
    p=Path(args.candidate_json); frozen=sha256_file(p); bundle=json.loads(p.read_text())
    if bundle.get("referenceBlindGeneration") is not True: raise RuntimeError("not blind")
    refp=Path(args.professional_timing_map); ref=json.loads(refp.read_text())
    rb=ref_beats(ref); rs=ref_starts(ref); results=[]
    for c in bundle["candidates"]:
        cb=np.asarray(c["grid"]["beatTimesSeconds"],float)
        bd=[beat_diag(cb,rb,s) for s in range(-20,21)]; bd=[x for x in bd if x]
        bestb=min(bd,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["beatIndexShift"])))
        md=[measure_diag(measure_starts(c),rs,s) for s in range(-8,9)]; md=[x for x in md if x]
        bestm=min(md,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["measureShift"])))
        results.append({"name":c["name"],"candidateBeatCount":len(cb),"referenceBeatCount":len(rb),
                        "beatCountDifference":int(len(cb)-len(rb)),
                        "bestBeatIndexShiftDiagnostic":bestb,"bestMeasureShiftDiagnostic":bestm})
    out={"schemaVersion":5,"kind":"gomyway-reference-independent-timebase-v5-professional-comparison",
         "candidateFrozenSha256BeforeReferenceRead":frozen,"candidateMutatedAfterComparison":False,
         "comparisonIsDiagnosticOnly":True,"primaryCandidateNameFrozenBeforeReferenceRead":bundle["primaryCandidateName"],
         "professionalTimingMapSha256":sha256_file(refp),"results":results,
         "interpretationBoundary":"All comparison metrics are diagnostic only; V5 bundle remains frozen."}
    write_json(args.output_json,out)
    print(json.dumps({"candidateSha256":frozen,"primaryCandidateName":bundle["primaryCandidateName"],"results":results},indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="mode",required=True)
    g=sub.add_parser("generate"); g.add_argument("--audio-source",required=True); g.add_argument("--audio-wav",required=True)
    g.add_argument("--model",required=True); g.add_argument("--output-json",required=True); g.set_defaults(func=generate)
    c=sub.add_parser("compare"); c.add_argument("--candidate-json",required=True); c.add_argument("--professional-timing-map",required=True)
    c.add_argument("--output-json",required=True); c.set_defaults(func=compare)
    a=ap.parse_args();a.func(a)
if __name__=="__main__":main()
