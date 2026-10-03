"""Reference-independent long-range timebase V3 for Go My Way.

Generation is audio-only:
- fixed source audio
- fixed BS-Roformer separator
- librosa beat tracking on rhythm-bearing signals
- audio-only candidate selection
No professional timing/reference data is read until compare mode.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import soundfile as sf
import librosa

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from v143_reference_free_timing import (
    _finite_audio, _resample_audio, _normalized_onset_envelope,
    _bar_phase_from_accents, TIMING_SAMPLE_RATE, STFT_HOP_SAMPLES
)
from v143_candidate_timing_adapter import build_subdivision_grid

EXPECTED_AUDIO_SOURCE="public/gomywayfullaitest.m4a"
EXPECTED_AUDIO_GIT_BLOB="5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def write_json(path: Path, d: dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def summarize(v):
    x=np.asarray(list(v),dtype=float)
    if x.size==0:return {"count":0,"mean":None,"median":None,"min":None,"max":None,"std":None}
    return {"count":int(x.size),"mean":float(x.mean()),"median":float(np.median(x)),
            "min":float(x.min()),"max":float(x.max()),"std":float(x.std())}

def onset_features(samples, sr):
    mono=_finite_audio(samples)
    ana=_resample_audio(mono,int(sr),TIMING_SAMPLE_RATE)
    onset,low,frame_times=_normalized_onset_envelope(ana,TIMING_SAMPLE_RATE)
    return onset,low,frame_times

def nearest_frame_indices(times, frame_times):
    idx=np.searchsorted(frame_times,times)
    idx=np.clip(idx,0,len(frame_times)-1)
    left=np.maximum(idx-1,0)
    choose_left=np.abs(frame_times[left]-times)<np.abs(frame_times[idx]-times)
    return np.where(choose_left,left,idx).astype(int)

def build_candidate(name,samples,sr,tightness,source_kind):
    mono=np.mean(samples,axis=1) if samples.ndim==2 else samples
    onset_env=librosa.onset.onset_strength(y=mono.astype(np.float32),sr=sr,hop_length=512,aggregate=np.median)
    tempo,beats=librosa.beat.beat_track(
        onset_envelope=onset_env,sr=sr,hop_length=512,
        tightness=float(tightness),trim=False,units="time",sparse=True
    )
    beats=np.asarray(beats,dtype=float)
    if beats.size<32: raise RuntimeError(f"{name}: too few beats {beats.size}")
    tempo_value=float(np.asarray(tempo).reshape(-1)[0])

    onset,low,frame_times=onset_features(samples,sr)
    fi=nearest_frame_indices(beats,frame_times)
    accents=onset[fi]+0.25*low[fi]
    first_beat,downbeat_mod4,bar_conf=_bar_phase_from_accents(accents)

    intervals=np.diff(beats)
    median_interval=float(np.median(intervals))
    interval_cv=float(np.std(intervals)/max(np.mean(intervals),1e-9))
    beat_activity=float(np.mean(onset[fi]))
    bg=float(np.mean(onset))
    activity_ratio=beat_activity/max(bg,1e-9)
    activity_score=float(np.clip((activity_ratio-1.0)/2.0,0.0,1.0))
    regularity_score=float(np.clip(1.0-interval_cv/0.20,0.0,1.0))
    quality=float(0.50*activity_score+0.30*regularity_score+0.20*bar_conf)

    slots=build_subdivision_grid(
        beats,beats_per_measure=4,subdivisions_per_beat=4,
        measure_start=1,first_beat_in_measure=int(first_beat)
    )
    measures={}
    for s in slots:
        row=measures.setdefault(int(s.measure),{"measure":int(s.measure),"steps":{}})
        row["steps"][str(int(s.step))]=float(s.time_seconds)
    normalized=[]
    for m in sorted(measures):
        st=measures[m]["steps"]
        normalized.append({"measure":m,"availableStepCount":len(st),
                           "stepTimesSeconds":st,"startSeconds":st.get("0")})

    local_bpm=60.0/intervals
    return {
      "name":name,"sourceKind":source_kind,"tightness":float(tightness),
      "estimator":{"name":"librosa-beat-track-long-range-v3","reportedTempoBpm":tempo_value,
                   "medianTrackedTempoBpm":float(60.0/median_interval),
                   "barConfidence":float(bar_conf),"firstBeatInMeasure":int(first_beat),
                   "downbeatIndexMod4":int(downbeat_mod4),"meterAssumption":{"numerator":4,"denominator":4}},
      "audioOnlySelectionEvidence":{"beatActivityRatio":float(activity_ratio),
                   "activityScore":activity_score,"intervalCv":interval_cv,
                   "regularityScore":regularity_score,"barConfidence":float(bar_conf),
                   "qualityScore":quality},
      "grid":{"beatCount":int(beats.size),"beatTimesSeconds":[float(x) for x in beats],
              "beatIntervalSummarySeconds":summarize(intervals),
              "localTempoSummaryBpm":summarize(local_bpm),
              "measureCountWithAnySlots":len(normalized),"slotCount":len(slots),"measures":normalized}
    }

def generate(args):
    source=Path(args.audio_source); wav=Path(args.audio_wav); model=Path(args.model)
    samples,sr=sf.read(str(wav),dtype="float32",always_2d=True)
    if int(sr)!=44100: raise RuntimeError(sr)
    sep=BsRoformer6StemOnnxAdapter(model)
    stems=sep.separate_array(samples,int(sr))
    specs=[
      ("raw_drums_t100",stems["drums"],100.0,"separator-drums"),
      ("raw_drums_t300",stems["drums"],300.0,"separator-drums"),
      ("raw_mix_t100",samples,100.0,"raw-mix"),
      ("raw_mix_t300",samples,300.0,"raw-mix"),
    ]
    candidates=[build_candidate(n,a,int(sr),t,k) for n,a,t,k in specs]
    ranked=sorted(candidates,key=lambda c:(
        c["audioOnlySelectionEvidence"]["qualityScore"],
        c["audioOnlySelectionEvidence"]["barConfidence"],
        c["audioOnlySelectionEvidence"]["regularityScore"]
    ),reverse=True)
    primary=ranked[0]["name"]
    out={
      "schemaVersion":3,"kind":"gomyway-reference-independent-timebase-v3-bundle",
      "status":"frozen-before-professional-comparison",
      "referenceBlindGeneration":True,
      "professionalTimingMapReadDuringGeneration":False,
      "professionalScorerRowsReadDuringGeneration":False,
      "primarySelectionRule":"max audioOnlySelectionEvidence.qualityScore; tie barConfidence then regularityScore",
      "primaryCandidateName":primary,
      "audio":{"sourcePath":EXPECTED_AUDIO_SOURCE,"expectedRepositoryGitBlob":EXPECTED_AUDIO_GIT_BLOB,
               "sourceSha256":sha256_file(source),"decodedWavSha256":sha256_file(wav),
               "sampleRate":int(sr),"durationSeconds":float(len(samples)/sr)},
      "separator":{"name":"BS-Roformer-SW 6-stem ONNX","modelSha256":FP16_SHA256},
      "candidates":candidates,
      "interpretationBoundary":"V3 replaces coarse integer-frame tempo dependence with long-range beat tracking. All candidates and primary selection are frozen before reference access. 4/4 measure labeling remains provisional and is evaluated separately."
    }
    write_json(Path(args.output_json),out)
    print(json.dumps({"primaryCandidateName":primary,"candidates":[{
      "name":c["name"],"tempo":c["estimator"]["medianTrackedTempoBpm"],
      "quality":c["audioOnlySelectionEvidence"]["qualityScore"],
      "barConfidence":c["estimator"]["barConfidence"],
      "beatCount":c["grid"]["beatCount"]} for c in candidates]},indent=2))

def candidate_starts(c):
    return {int(r["measure"]):float(r["startSeconds"]) for r in c["grid"]["measures"] if r.get("startSeconds") is not None}
def reference_starts(ref):
    return {int(r["measureNumber"]):float(r["startSeconds"]) for r in ref["measureBoundaries"]}

def shift_diag(cs,rs,shift):
    pairs=[]
    for cm,ct in cs.items():
        rm=cm+shift
        if rm in rs:pairs.append({"candidateMeasure":cm,"referenceMeasure":rm,"signedErrorSeconds":ct-rs[rm]})
    if not pairs:return None
    e=np.array([p["signedErrorSeconds"] for p in pairs]); a=np.abs(e)
    return {"measureShift":int(shift),"pairCount":len(pairs),
            "meanSignedErrorSeconds":float(e.mean()),"medianSignedErrorSeconds":float(np.median(e)),
            "meanAbsoluteErrorSeconds":float(a.mean()),"medianAbsoluteErrorSeconds":float(np.median(a)),
            "maxAbsoluteErrorSeconds":float(a.max()),"pairs":pairs}

def reference_beats(ref):
    out=[]
    for r in ref["measureBoundaries"]:
        start=float(r["startSeconds"]); dur=float(r["durationSeconds"]); n=int(r["meter"]["numerator"])
        for b in range(n): out.append(start+dur*b/n)
    return np.asarray(out,dtype=float)

def nearest_errors(candidate_times, reference_times):
    errs=[]
    for t in candidate_times:
        j=int(np.searchsorted(reference_times,t))
        choices=[]
        if j<len(reference_times):choices.append(reference_times[j])
        if j>0:choices.append(reference_times[j-1])
        errs.append(float(t-min(choices,key=lambda x:abs(x-t))))
    e=np.asarray(errs,dtype=float); a=np.abs(e)
    return {"pairCount":len(e),"meanAbsoluteErrorSeconds":float(a.mean()),
            "medianAbsoluteErrorSeconds":float(np.median(a)),
            "p95AbsoluteErrorSeconds":float(np.quantile(a,0.95)),
            "meanSignedErrorSeconds":float(e.mean())}

def compare(args):
    p=Path(args.candidate_json); frozen_sha=sha256_file(p); bundle=json.loads(p.read_text())
    if bundle.get("referenceBlindGeneration") is not True: raise RuntimeError("not blind")
    refp=Path(args.professional_timing_map); ref=json.loads(refp.read_text())
    rs=reference_starts(ref); rb=reference_beats(ref)
    results=[]
    for c in bundle["candidates"]:
        ds=[d for d in (shift_diag(candidate_starts(c),rs,s) for s in range(-8,9)) if d]
        best=min(ds,key=lambda d:(d["medianAbsoluteErrorSeconds"],d["meanAbsoluteErrorSeconds"],abs(d["measureShift"])))
        drift=None
        if len(best["pairs"])>=2:
            x=np.array([q["referenceMeasure"] for q in best["pairs"]],dtype=float)
            y=np.array([q["signedErrorSeconds"] for q in best["pairs"]],dtype=float)
            slope,intercept=np.polyfit(x,y,1)
            drift={"secondsPerReferenceMeasure":float(slope),"interceptSeconds":float(intercept),
                   "predictedDriftAcross113MeasuresSeconds":float(slope*112)}
        results.append({"name":c["name"],"tempoBpm":c["estimator"]["medianTrackedTempoBpm"],
          "beatTimingNearestReferenceDiagnostic":nearest_errors(c["grid"]["beatTimesSeconds"],rb),
          "bestIntegerMeasureShiftDiagnostic":{k:v for k,v in best.items() if k!="pairs"},
          "bestShiftDrift":drift})
    out={"schemaVersion":3,"kind":"gomyway-reference-independent-timebase-v3-professional-comparison",
         "candidateFrozenSha256BeforeReferenceRead":frozen_sha,"candidateMutatedAfterComparison":False,
         "comparisonIsDiagnosticOnly":True,
         "primaryCandidateNameFrozenBeforeReferenceRead":bundle["primaryCandidateName"],
         "professionalTimingMapSha256":sha256_file(refp),"results":results,
         "interpretationBoundary":"Beat-level diagnostics separate beat tracking quality from provisional 4/4 measure labeling. Comparison may not alter the frozen V3 bundle."}
    write_json(Path(args.output_json),out)
    print(json.dumps({"candidateSha256":frozen_sha,"primaryCandidateName":bundle["primaryCandidateName"],"results":[{
      "name":r["name"],"tempoBpm":r["tempoBpm"],
      "beat":r["beatTimingNearestReferenceDiagnostic"],
      "measure":r["bestIntegerMeasureShiftDiagnostic"],"drift":r["bestShiftDrift"]} for r in results]},indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="mode",required=True)
    g=sub.add_parser("generate"); g.add_argument("--audio-source",required=True); g.add_argument("--audio-wav",required=True)
    g.add_argument("--model",required=True); g.add_argument("--output-json",required=True); g.set_defaults(func=generate)
    c=sub.add_parser("compare"); c.add_argument("--candidate-json",required=True); c.add_argument("--professional-timing-map",required=True)
    c.add_argument("--output-json",required=True); c.set_defaults(func=compare)
    a=ap.parse_args(); a.func(a)
if __name__=="__main__": main()
