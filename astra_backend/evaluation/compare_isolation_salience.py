"""Compare reviewed target-pitch salience before/after isolation; never read predictions."""
from __future__ import annotations
import argparse, hashlib, json, math, statistics, wave
from pathlib import Path
import numpy as np

def require(ok,msg):
    if not ok: raise ValueError(msg)
def finite(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def load_wav(path, expected_sha256):
    raw=Path(path).read_bytes(); digest=hashlib.sha256(raw).hexdigest(); require(digest==expected_sha256,'Audio SHA256 mismatch')
    with wave.open(str(path),'rb') as w:
        require((w.getnchannels(),w.getsampwidth(),w.getcomptype())==(1,2,'NONE'),'Expected mono PCM16 WAV')
        sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float64)/32768
    return x,sr,digest
def source_time(segments, beat):
    require(finite(beat),'Invalid beat')
    for s in segments:
        if s['beatStart']<=beat<=s['beatEnd']:
            q=(beat-s['beatStart'])/(s['beatEnd']-s['beatStart']); return s['timeStart']+q*(s['timeEnd']-s['timeStart'])
    raise ValueError('Event outside timing map')
def harmonic_contrast(x,sr,t,midi):
    n=int(round(.09*sr)); start=max(0,int(round((t+.015)*sr))); frame=x[start:start+n]
    require(len(frame)==n,'Diagnostic frame outside audio')
    N=32768; spec=np.abs(np.fft.rfft(frame*np.hanning(n),n=N));freq=np.fft.rfftfreq(N,1/sr)
    f0=440*2**((midi-69)/12); vals=[]
    for h in range(1,6):
        f=h*f0
        if f>1800: break
        sig=(freq>=f-3)&(freq<=f+3); noise=(freq>=f-28)&(freq<=f+28)&~((freq>=f-6)&(freq<=f+6))
        require(bool(sig.any() and noise.any()),'Harmonic band unavailable')
        peak=float(np.max(spec[sig])); base=float(np.median(spec[noise]))+1e-12
        vals.append(20*math.log10((peak+1e-12)/base))
    require(vals,'No harmonic contrast values')
    return float(statistics.median(vals))
def compare(source_wav, isolated_wav, labels_path, alignment_path, *, source_sha256, isolated_sha256, offset, scale):
    require(finite(offset) and finite(scale) and scale>0,'Invalid isolated timing transform')
    source,sr,source_digest=load_wav(source_wav,source_sha256); isolated,sr2,isolated_digest=load_wav(isolated_wav,isolated_sha256)
    require(sr==sr2,'Sample-rate mismatch')
    labels=json.loads(Path(labels_path).read_text()); alignment=json.loads(Path(alignment_path).read_text())
    require(labels.get('reviewStatus')=='complete' and labels.get('unresolvedItems')==[] and labels.get('coverageReviewed') is True,'Labels not complete')
    require(alignment.get('reviewStatus')=='complete' and alignment.get('unresolvedItems')==[] and alignment.get('independentOfPredictions') is True,'Source alignment incomplete')
    require(labels.get('audioSha256')==source_digest and alignment.get('audioSha256')==source_digest,'Source identity mismatch')
    segments=alignment.get('segments'); require(isinstance(segments,list) and segments,'Missing source timing segments')
    rows=[]
    for e in labels.get('events',[]):
        if e.get('kind')!='attack': continue
        midi=e.get('midi'); require(isinstance(midi,int) and not isinstance(midi,bool) and 0<=midi<=127,'Invalid reviewed MIDI')
        ts=source_time(segments,e.get('beat')); ti=offset+scale*ts
        cs=harmonic_contrast(source,sr,ts,midi); ci=harmonic_contrast(isolated,sr,ti,midi)
        rows.append((midi,cs,ci,ci-cs))
    require(rows,'No reviewed attacks')
    summary={}
    for midi in sorted({r[0] for r in rows}):
        rr=[r for r in rows if r[0]==midi]; gains=[r[3] for r in rr]
        summary[str(midi)]={'targets':len(rr),'sourceMedianContrastDb':statistics.median(r[1] for r in rr),'isolatedMedianContrastDb':statistics.median(r[2] for r in rr),'medianGainDb':statistics.median(gains),'positiveGainCount':sum(g>0 for g in gains)}
    gains=[r[3] for r in rows]
    return {'kind':'paired-target-harmonic-salience-diagnostic','version':1,'sourceAudioSha256':source_digest,'isolatedAudioSha256':isolated_digest,'timingTransform':{'isolatedSeconds':'offset + scale * sourceSeconds','offsetSeconds':offset,'scale':scale},'targetCount':len(rows),'summaryByMidi':summary,'overallMedianGainDb':statistics.median(gains),'overallPositiveGainCount':sum(g>0 for g in gains),'reviewStatus':'diagnostic-only','predictionsRead':False,'privateReviewedLabelsRead':True,'customerDeliveryEligible':False,'limitations':['Harmonic contrast is an audio-salience diagnostic, not transcription accuracy.','The isolated asset is a development oracle, not evidence that an approved product separator can reproduce it.','Timing transform must be established independently of prediction matching.']}
def main():
    p=argparse.ArgumentParser()
    for x in ['source-wav','isolated-wav','labels','alignment','source-sha256','isolated-sha256','output']:p.add_argument('--'+x,required=True)
    p.add_argument('--offset',required=True,type=float);p.add_argument('--scale',required=True,type=float);a=p.parse_args()
    out=Path(a.output);require(not out.exists(),'Refusing to overwrite existing diagnostic')
    result=compare(a.source_wav,a.isolated_wav,a.labels,a.alignment,source_sha256=a.source_sha256,isolated_sha256=a.isolated_sha256,offset=a.offset,scale=a.scale)
    out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'targetCount':result['targetCount'],'overallMedianGainDb':result['overallMedianGainDb'],'overallPositiveGainCount':result['overallPositiveGainCount']},sort_keys=True))
if __name__=='__main__':main()
