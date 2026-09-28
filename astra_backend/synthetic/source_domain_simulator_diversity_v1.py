#!/usr/bin/env python3
"""Model-free source-domain simulator diversity V1.

Waveform-level procedural diversity applied before the frozen CQT frontend.
No model loading, inference, optimizer, corpus media, P1/P2/P3, or production mutation.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.signal import butter, hilbert, lfilter, resample_poly, sosfilt

from synthetic.s0_pilot_v1 import (
    INTERNAL_SR, OUTPUT_SR, CLIP_SECONDS, OPEN_MIDI,
    build_template, render_waveform, targets_for_template,
)
from tabcnn_runtime.preprocessing import extract_cqt_features, rms_normalize

SCHEMA="astra-source-domain-simulator-diversity-review-v1"
ROOT_NAMESPACE="astra-source-domain-diversity-v1"
FIXTURE_FAMILIES=("isolated","repeated","scales","chords","palmmute","legato","negative-only")
FINAL_PEAK=0.78

def _seed(*parts):
    raw="|".join(str(x) for x in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") & 0x7fffffff

def _rng(template_id,variant,stream,event_index=None):
    parts=[ROOT_NAMESPACE,template_id,int(variant),"source-domain-v1",stream]
    if event_index is not None: parts.append(int(event_index))
    return np.random.RandomState(_seed(*parts))

def _log_uniform(rng,lo,hi):
    return float(np.exp(rng.uniform(np.log(lo),np.log(hi))))

def source_parameters(template_id,variant):
    a=_rng(template_id,variant,"attack")
    d=_rng(template_id,variant,"decay")
    b=_rng(template_id,variant,"brightness")
    p=_rng(template_id,variant,"pickup")
    nl=_rng(template_id,variant,"nonlinear")
    n=_rng(template_id,variant,"noise")
    return {
      "attackBaseRiseSeconds":_log_uniform(a,.0015,.050),
      "transientNoiseGain":float(a.uniform(0.0,.20)),
      "transientDecaySeconds":_log_uniform(a,.003,.020),
      "dampingMultiplier":_log_uniform(d,.60,1.80),
      "brightness":float(b.uniform(.55,.92)),
      "pickPosition":float(b.uniform(.08,.48)),
      "lowpassCutoffHz":_log_uniform(p,2800.0,12000.0),
      "spectralTiltDb":float(p.uniform(-6.0,6.0)),
      "highpassCornerHz":float(p.uniform(20.0,80.0)),
      "nonlinearActive":bool(nl.uniform()<.50),
      "nonlinearDrive":float(nl.uniform(1.0,2.5)),
      "nonlinearWet":float(nl.uniform(0.0,.30)),
      "broadbandNoiseRmsRelative":_log_uniform(n,1e-5,3e-3),
      "humActive":bool(n.uniform()<.35),
      "humFundamentalHz":int(50 if n.uniform()<.5 else 60),
      "humCombinedRmsRelative":float(n.uniform(0.0,1e-3)),
    }

CHALLENGE_PROFILE={
  "attackBaseRiseSeconds":.045,
  "transientNoiseGain":.03,
  "transientDecaySeconds":.012,
  "dampingMultiplier":1.45,
  "brightness":.60,
  "pickPosition":.42,
  "lowpassCutoffHz":3500.0,
  "spectralTiltDb":-4.0,
  "highpassCornerHz":45.0,
  "nonlinearActive":True,
  "nonlinearDrive":1.8,
  "nonlinearWet":.20,
  "broadbandNoiseRmsRelative":1e-3,
  "humActive":False,
  "humFundamentalHz":60,
  "humCombinedRmsRelative":0.0,
}

def _note_params(template_id,variant,event_index,profile=None):
    if profile=="challenge":
        rise_mult=(.90,1.10)[event_index%2]
        amp=(.70,1.00,1.30,.85)[event_index%4]
        damping=1.0
    else:
        ar=_rng(template_id,variant,"attack",event_index)
        dr=_rng(template_id,variant,"decay",event_index)
        yr=_rng(template_id,variant,"dynamics",event_index)
        rise_mult=_log_uniform(ar,.75,1.35)
        damping=_log_uniform(dr,.85,1.20)
        amp=float(np.clip(np.exp(yr.normal(0.0,.18)),.55,1.60))
    return {"riseMultiplier":rise_mult,"dampingMultiplier":damping,"amplitudeMultiplier":amp}

def _component(freq,duration,sr,rng,*,damping,pick_position,brightness,attack_rise,
               transient,transient_gain,transient_decay,soft):
    n=max(1,int(round(duration*sr))); t=np.arange(n,dtype=np.float64)/sr
    wave=np.zeros(n,dtype=np.float64); phase0=rng.uniform(0,2*np.pi)
    for h in range(1,7):
        pick=max(.08,abs(math.sin(math.pi*h*pick_position)))
        amp=(brightness**(h-1))*pick/(h**1.15)
        decay=np.exp(-(damping*(.78+.20*h))*t)
        wave += amp*np.sin(2*np.pi*freq*h*t+phase0/h)*decay
    tau=max(float(attack_rise),1e-5)
    if soft: tau=max(tau,.045)
    wave *= (1-np.exp(-t/tau))
    if transient and transient_gain>0:
        wave += transient_gain*rng.normal(0,1,n)*np.exp(-t/max(float(transient_decay),1e-5))
    return wave

def _apply_color(audio,sr,params):
    y=np.asarray(audio,dtype=np.float64)
    hp=butter(2,float(params["highpassCornerHz"])/(sr/2),btype="highpass",output="sos")
    lp=butter(2,min(.99,float(params["lowpassCutoffHz"])/(sr/2)),btype="lowpass",output="sos")
    y=sosfilt(hp,y)
    low=sosfilt(lp,y)
    residual=y-low
    high_gain=10.0**(float(params["spectralTiltDb"])/20.0)
    y=low+high_gain*residual
    if params["nonlinearActive"] and params["nonlinearWet"]>0:
        drive=float(params["nonlinearDrive"]); wet=float(params["nonlinearWet"])
        shaped=np.tanh(drive*y)/max(np.tanh(drive),1e-12)
        y=(1-wet)*y+wet*shaped
    return y

def render_source_domain(template,variant,*,profile="intervention",override=None,return_metadata=False):
    if profile not in ("intervention","challenge"):
        raise ValueError("profile must be intervention or challenge")
    params=dict(CHALLENGE_PROFILE if profile=="challenge" else source_parameters(template["templateId"],variant))
    if override: params.update(override)
    n=int(round(CLIP_SECONDS*INTERNAL_SR)); audio=np.zeros(n,dtype=np.float64)
    meta={"profile":profile,"params":params,"events":[]}
    base_damping=1.15*float(params["dampingMultiplier"])
    for i,row in enumerate(template["segments"]):
        start=int(round(row["start"]*INTERNAL_SR)); end=min(n,int(round(row["end"]*INTERNAL_SR)))
        if end<=start or start>=n: continue
        note=_note_params(template["templateId"],variant,i,profile if profile=="challenge" else None)
        pitch=OPEN_MIDI[row["string"]]+row["fret"]; freq=440.0*(2.0**((pitch-69)/12.0))
        d=base_damping*note["dampingMultiplier"]*(4.5 if row["palm"] else 1.0)*(1.0+.04*row["string"])
        rise=float(np.clip(float(params["attackBaseRiseSeconds"])*note["riseMultiplier"],.001,.060))
        erng=_rng(template["templateId"],variant,"component",i)
        comp=_component(freq,(end-start)/INTERNAL_SR,INTERNAL_SR,erng,
          damping=d,pick_position=float(params["pickPosition"]),brightness=float(params["brightness"]),
          attack_rise=rise,transient=bool(row["attack"]),
          transient_gain=float(params["transientNoiseGain"]) if row["attack"] else 0.0,
          transient_decay=float(params["transientDecaySeconds"]),soft=bool(row["soft"]))
        audio[start:end]+=note["amplitudeMultiplier"]*comp[:end-start]
        meta["events"].append({"index":i,"attack":bool(row["attack"]),"riseSeconds":rise,
          "transientApplied":bool(row["attack"] and params["transientNoiseGain"]>0),
          "pitch":pitch,"start":float(row["start"]),"end":float(row["end"])})
    if template["hasNegativeStructure"]:
        nrng=_rng(template["templateId"],variant,"negative-structure")
        center=int(round((1.70+.03*(variant-1))*INTERNAL_SR)); width=max(8,int(.018*INTERNAL_SR))
        lo=max(0,center-width//2); hi=min(n,lo+width)
        audio[lo:hi]+=0.12*nrng.normal(0,1,hi-lo)*np.hanning(hi-lo)
    audio=_apply_color(audio,INTERNAL_SR,params)
    rms=float(np.sqrt(np.mean(audio**2)))
    nrng=_rng(template["templateId"],variant,"noise-final")
    if rms>0:
        noise_rms=float(params["broadbandNoiseRmsRelative"])*rms
        audio += nrng.normal(0,noise_rms,n)
        if params["humActive"] and params["humCombinedRmsRelative"]>0:
            t=np.arange(n,dtype=np.float64)/INTERNAL_SR; f=float(params["humFundamentalHz"])
            h=np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*2*f*t)+.25*np.sin(2*np.pi*3*f*t)
            hr=np.sqrt(np.mean(h*h))
            audio += h*(float(params["humCombinedRmsRelative"])*rms/max(hr,1e-12))
    body_a=.88
    audio=lfilter([1.0-body_a],[1.0,-body_a],audio)
    peak=float(np.max(np.abs(audio)))
    if peak>0: audio=FINAL_PEAK*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(CLIP_SECONDS*OUTPUT_SR))
    out=np.pad(out,(0,max(0,want-len(out))))[:want]
    if not np.isfinite(out).all(): raise RuntimeError("nonfinite source-domain audio")
    # Polyphase resampling can overshoot the pre-resample peak slightly. The frozen
    # admission rule is on final output, so enforce the same deterministic peak
    # bound once more after resampling rather than weakening the test.
    final_peak=float(np.max(np.abs(out)))
    if final_peak>FINAL_PEAK:
        out=(out*(FINAL_PEAK/final_peak)).astype(np.float32,copy=False)
    if float(np.max(np.abs(out)))>=.999: raise RuntimeError("source-domain clipping guard")
    return (out,meta) if return_metadata else out

def _hash_array(x):
    a=np.ascontiguousarray(x); h=hashlib.sha256()
    h.update(str(a.dtype).encode()); h.update(b"\0")
    h.update(",".join(map(str,a.shape)).encode()); h.update(b"\0"); h.update(a.tobytes())
    return h.hexdigest()

def _features(audio):
    return extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)

def _fundamental_cents(audio,freq,start,end,sr=OUTPUT_SR):
    lo=max(0,int(round(start*sr))); hi=min(len(audio),int(round(end*sr)))
    x=np.asarray(audio[lo:hi],dtype=float)
    if len(x)<1024 or not np.any(np.abs(x)>1e-8): return None
    x=x*np.hanning(len(x)); nfft=1
    while nfft<len(x)*4: nfft*=2
    spec=np.abs(np.fft.rfft(x,nfft)); freqs=np.fft.rfftfreq(nfft,1/sr)
    band=(freqs>=freq*.85)&(freqs<=freq*1.15)
    if not np.any(band): return None
    est=float(freqs[band][np.argmax(spec[band])])
    return float(1200*np.log2(est/freq))

def _rise_time(audio,start,sr=OUTPUT_SR,window=.080):
    lo=max(0,int(round(start*sr))); hi=min(len(audio),lo+int(round(window*sr)))
    x=np.asarray(audio[lo:hi],dtype=float)
    if len(x)<8:return None
    env=np.abs(hilbert(x))
    smooth=max(1,int(round(.0015*sr)))
    if smooth>1: env=np.convolve(env,np.ones(smooth)/smooth,mode="same")
    peak=float(np.max(env))
    if peak<=1e-8:return None
    i10=np.flatnonzero(env>=.10*peak); i90=np.flatnonzero(env>=.90*peak)
    if not len(i10) or not len(i90):return None
    j10=int(i10[0]); later=i90[i90>=j10]
    if not len(later):return None
    return float((int(later[0])-j10)/sr)

def _first_difference_energy(audio,start,sr=OUTPUT_SR,window=.060):
    lo=max(1,int(round(start*sr))); hi=min(len(audio),lo+int(round(window*sr)))
    d=np.diff(np.asarray(audio[lo-1:hi],dtype=float))
    return float(np.mean(d*d)) if len(d) else 0.0

def _cqt_flux(feat,frame):
    if frame<=0 or frame>=len(feat):return 0.0
    return float(np.maximum(feat[frame]-feat[frame-1],0).sum())

def _fixture_template(name):
    mapping={"isolated":("isolated",0),"repeated":("repeated",0),"scales":("scales",0),
             "chords":("chords",0),"palmmute":("palmmute",0),"legato":("legato",0),
             "negative-only":("mixed",0)}
    fam,bi=mapping[name]
    return build_template(fam,bi)

def build_review_evidence():
    cases={}
    positive_rises=[]
    for fi,name in enumerate(FIXTURE_FAMILIES):
        template=_fixture_template(name); variant=fi%3
        control=render_waveform(template,variant)
        intervention,meta=render_source_domain(template,variant,profile="intervention",return_metadata=True)
        intervention2=render_source_domain(template,variant,profile="intervention")
        if not np.array_equal(intervention,intervention2): raise RuntimeError("nondeterministic rerender")
        cf=_features(control); xf=_features(intervention)
        if cf.shape!=xf.shape: raise RuntimeError("frontend shape changed")
        cs,co,cr=targets_for_template(template,len(cf)); xs,xo,xr=targets_for_template(template,len(xf))
        label_identity=bool(np.array_equal(cs,xs) and np.array_equal(co,xo) and cr==xr)
        attacked=[e for e in meta["events"] if e["attack"]]
        unlabeled_transients=[e for e in meta["events"] if (not e["attack"]) and e["transientApplied"]]
        metrics=[]
        for e in attacked:
            freq=440.0*(2.0**((e["pitch"]-69)/12.0))
            stable_start=min(e["end"]-.04,e["start"]+.10); stable_end=min(e["end"],stable_start+.12)
            hop=512/22050; frame=int(round(e["start"]/hop))
            rt=_rise_time(intervention,e["start"])
            if rt is not None: positive_rises.append(rt)
            metrics.append({"eventIndex":e["index"],"riseSeconds":rt,
              "firstDifferenceEnergy":_first_difference_energy(intervention,e["start"]),
              "fundamentalCents":_fundamental_cents(intervention,freq,stable_start,stable_end),
              "cqtPositiveFlux":_cqt_flux(xf,frame)})
        cases[name]={
          "controlWaveformSha256":_hash_array(control),"interventionWaveformSha256":_hash_array(intervention),
          "controlCqtSha256":_hash_array(cf),"interventionCqtSha256":_hash_array(xf),
          "labelIdentity":label_identity,"peak":float(np.max(np.abs(intervention))),
          "rms":float(np.sqrt(np.mean(intervention.astype(float)**2))),
          "unlabeledTransientCount":len(unlabeled_transients),"attackedEvents":metrics,
          "cqtChanged":bool(not np.array_equal(cf,xf)),
        }
    # deterministic explicit boundary fixtures validate the frozen attack-span range itself.
    iso=_fixture_template("isolated")
    fast,_=render_source_domain(iso,0,override={"attackBaseRiseSeconds":.0015,"transientNoiseGain":0.0},return_metadata=True)
    slow,_=render_source_domain(iso,0,override={"attackBaseRiseSeconds":.050,"transientNoiseGain":0.0},return_metadata=True)
    start=iso["segments"][0]["start"]
    fast_rt=_rise_time(fast,start); slow_rt=_rise_time(slow,start)
    span=(slow_rt/fast_rt) if fast_rt and slow_rt else None
    all_cents=[abs(e["fundamentalCents"]) for c in cases.values() for e in c["attackedEvents"] if e["fundamentalCents"] is not None]
    criteria={
      "deterministicRerender":True,
      "labelsReferencesBitIdentical":all(c["labelIdentity"] for c in cases.values()),
      "finiteAndPeakBounded":all(np.isfinite(c["peak"]) and c["peak"]<.999 for c in cases.values()),
      "noUnlabeledTransientInjection":all(c["unlabeledTransientCount"]==0 for c in cases.values()),
      "fundamentalWithin15Cents":bool(all_cents and max(all_cents)<=15.0),
      "attackRiseSpanAtLeast4x":bool(span is not None and span>=4.0),
      "cqtEffectEveryPositiveFixture":all(c["cqtChanged"] for n,c in cases.items() if n!="negative-only"),
      "negativeFixtureUnlabeled":bool(len(cases["negative-only"]["attackedEvents"])==0),
    }
    return {
      "schema":SCHEMA,"modelRun":False,"optimizerSteps":0,
      "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
      "fixtureRenderCount":len(FIXTURE_FAMILIES)*3+2,
      "attackBoundaryMeasuredRiseSeconds":{"fast":fast_rt,"slow":slow_rt,"ratio":span},
      "maxAbsoluteFundamentalErrorCents":max(all_cents) if all_cents else None,
      "cases":cases,"criteria":criteria,"admissionPassed":all(criteria.values()),
    }

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True)
    a=ap.parse_args(); e=build_review_evidence()
    Path(a.out).write_text(json.dumps(e,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_REVIEW="+json.dumps(e,sort_keys=True))
    if not e["admissionPassed"]: raise SystemExit("model-free source-domain admission failed")

if __name__=="__main__": main()
