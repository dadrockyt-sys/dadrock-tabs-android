"""Go My Way reference-independent timebase V6.

Independent estimator-family test using Essentia RhythmExtractor2013.
Generation:
- source audio + fixed BS-Roformer only
- full mix and raw drums as independent rhythm inputs
- no professional reference access
Comparison:
- diagnostics only after candidate bundle freeze
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from v143_reference_free_timing import _finite_audio, _resample_audio, _normalized_onset_envelope, _bar_phase_from_accents, TIMING_SAMPLE_RATE
from v143_candidate_timing_adapter import build_subdivision_grid

EXPECTED_AUDIO_SOURCE="public/gomywayfullaitest.m4a"
EXPECTED_AUDIO_GIT_BLOB="5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def write_json(p: Path,d: dict):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def summarize(v):
    x=np.asarray(v,float)
    if x.size==0:return {"count":0,"mean":None,"median":None,"min":None,"max":None,"std":None}
    return {"count":int(x.size),"mean":float(x.mean()),"median":float(np.median(x)),
            "min":float(x.min()),"max":float(x.max()),"std":float(x.std())}

def onset_for_bar_phase(samples,sr):
    mono=_finite_audio(samples)
    ana=_resample_audio(mono,int(sr),TIMING_SAMPLE_RATE)
    onset,low,times=_normalized_onset_envelope(ana,TIMING_SAMPLE_RATE)
    return onset,low,times

def nearest_indices(values, axis):
    idx=np.searchsorted(axis,values)
    idx=np.clip(idx,0,len(axis)-1)
    left=np.maximum(idx-1,0)
    choose=np.abs(axis[left]-values)<np.abs(axis[idx]-values)
    return np.where(choose,left,idx).astype(int)

def build_candidate(name,samples,sr,method,source_kind):
    import essentia
    import essentia.standard as es
    mono=np.mean(samples,axis=1) if samples.ndim==2 else np.asarray(samples)
    mono=np.asarray(mono,dtype=np.float32)
    algo=es.RhythmExtractor2013(method=method)
    bpm,ticks,confidence,estimates,bpm_intervals=algo(mono)
    beats=np.asarray(ticks,dtype=float)
    if beats.size<32:
        raise RuntimeError(f"{name}: too few beat ticks {beats.size}")
    intervals=np.diff(beats)
    onset,low,times=onset_for_bar_phase(samples,sr)
    fi=nearest_indices(beats,times)
    accents=onset[fi]+0.25*low[fi]
    first,mod4,barconf=_bar_phase_from_accents(accents)
    support=float(np.mean(onset[fi]))
    bg=float(np.mean(onset))
    support_ratio=support/max(bg,1e-9)
    interval_cv=float(np.std(intervals)/max(np.mean(intervals),1e-9))
    regularity=float(np.clip(1.0-interval_cv/0.20,0.0,1.0))
    quality=float(0.55*np.clip(float(confidence),0,1)+0.25*np.clip((support_ratio-1)/2,0,1)+0.20*barconf)

    slots=build_subdivision_grid(
      beats,beats_per_measure=4,subdivisions_per_beat=4,
      measure_start=1,first_beat_in_measure=int(first)
    )
    measures={}
    for s in slots:
        row=measures.setdefault(int(s.measure),{"measure":int(s.measure),"steps":{}})
        row["steps"][str(int(s.step))]=float(s.time_seconds)
    norm=[]
    for m in sorted(measures):
        st=measures[m]["steps"]
        norm.append({"measure":m,"availableStepCount":len(st),"stepTimesSeconds":st,"startSeconds":st.get("0")})

    return {
      "name":name,"sourceKind":source_kind,"method":method,
      "estimator":{
        "name":"Essentia RhythmExtractor2013",
        "essentiaVersion":getattr(essentia,"__version__","unknown"),
        "reportedTempoBpm":float(bpm),
        "confidence":float(confidence),
        "barConfidence":float(barconf),
        "firstBeatInMeasure":int(first),
        "downbeatIndexMod4":int(mod4),
        "meterAssumption":{"numerator":4,"denominator":4},
        "tempoEstimatesBpm":[float(x) for x in np.asarray(estimates).reshape(-1)],
        "bpmIntervalsSeconds":[float(x) for x in np.asarray(bpm_intervals).reshape(-1)]
      },
      "audioOnlySelectionEvidence":{
        "qualityScore":quality,
        "supportRatio":float(support_ratio),
        "regularityScore":regularity,
        "intervalCv":interval_cv
      },
      "grid":{
        "beatCount":int(beats.size),
        "beatTimesSeconds":[float(x) for x in beats],
        "beatIntervalSummarySeconds":summarize(intervals),
        "trackedTempoSummaryBpm":summarize(60.0/intervals),
        "measureCountWithAnySlots":len(norm),
        "slotCount":len(slots),
        "measures":norm
      }
    }

def generate(args):
    source=Path(args.audio_source); wav=Path(args.audio_wav); model=Path(args.model)
    samples,sr=sf.read(str(wav),dtype="float32",always_2d=True)
    if int(sr)!=44100: raise RuntimeError(f"expected 44100 Hz, got {sr}")
    sep=BsRoformer6StemOnnxAdapter(model)
    stems=sep.separate_array(samples,int(sr))
    specs=[
      ("mix_multifeature",samples,"multifeature","raw-mix"),
      ("drums_multifeature",stems["drums"],"multifeature","separator-drums"),
      ("mix_degap",samples,"degara","raw-mix"),
      ("drums_degap",stems["drums"],"degara","separator-drums")
    ]
    candidates=[build_candidate(n,a,int(sr),m,k) for n,a,m,k in specs]
    primary=max(candidates,key=lambda c:(
      c["audioOnlySelectionEvidence"]["qualityScore"],
      c["estimator"]["confidence"],
      c["estimator"]["barConfidence"]
    ))["name"]
    out={
      "schemaVersion":6,
      "kind":"gomyway-reference-independent-timebase-v6-bundle",
      "status":"frozen-before-professional-comparison",
      "referenceBlindGeneration":True,
      "professionalTimingMapReadDuringGeneration":False,
      "professionalScorerRowsReadDuringGeneration":False,
      "primaryCandidateName":primary,
      "primarySelectionRule":"max audioOnly qualityScore; tie estimator confidence then barConfidence",
      "audio":{
        "sourcePath":EXPECTED_AUDIO_SOURCE,
        "expectedRepositoryGitBlob":EXPECTED_AUDIO_GIT_BLOB,
        "sourceSha256":sha256_file(source),
        "decodedWavSha256":sha256_file(wav),
        "sampleRate":int(sr),
        "durationSeconds":float(len(samples)/sr)
      },
      "separator":{"name":"BS-Roformer-SW 6-stem ONNX","modelSha256":FP16_SHA256},
      "candidates":candidates,
      "interpretationBoundary":"V6 is an independent multi-feature beat-tracker family. Candidate generation and primary selection are audio-only and frozen before professional-reference comparison."
    }
    write_json(Path(args.output_json),out)
    print(json.dumps({
      "primaryCandidateName":primary,
      "candidates":[{
        "name":c["name"],
        "reportedTempoBpm":c["estimator"]["reportedTempoBpm"],
        "confidence":c["estimator"]["confidence"],
        "quality":c["audioOnlySelectionEvidence"]["qualityScore"],
        "barConfidence":c["estimator"]["barConfidence"],
        "beatCount":c["grid"]["beatCount"],
        "trackedTempoSummary":c["grid"]["trackedTempoSummaryBpm"]
      } for c in candidates]
    },indent=2))

def ref_beats(ref):
    out=[]
    for r in ref["measureBoundaries"]:
        st=float(r["startSeconds"]); dur=float(r["durationSeconds"]); n=int(r["meter"]["numerator"])
        for b in range(n):out.append(st+dur*b/n)
    return np.asarray(out,float)

def beat_diag(cb,rb,shift):
    pairs=[]
    for i,t in enumerate(cb):
        j=i+shift
        if 0<=j<len(rb):pairs.append((j,float(t-rb[j])))
    if len(pairs)<2:return None
    x=np.asarray([p[0] for p in pairs],float)
    e=np.asarray([p[1] for p in pairs],float); a=np.abs(e)
    slope,inter=np.polyfit(x,e,1)
    thirds=np.array_split(np.arange(len(e)),3)
    seg={}
    for lab,ix in zip(("early","middle","late"),thirds):
        seg[lab]={
          "meanSignedErrorSeconds":float(np.mean(e[ix])),
          "medianAbsoluteErrorSeconds":float(np.median(np.abs(e[ix])))
        }
    return {
      "beatIndexShift":int(shift),"pairCount":len(e),
      "meanSignedErrorSeconds":float(e.mean()),
      "medianSignedErrorSeconds":float(np.median(e)),
      "meanAbsoluteErrorSeconds":float(a.mean()),
      "medianAbsoluteErrorSeconds":float(np.median(a)),
      "p95AbsoluteErrorSeconds":float(np.quantile(a,.95)),
      "maxAbsoluteErrorSeconds":float(a.max()),
      "secondsPerReferenceBeat":float(slope),
      "predictedDriftAcrossSongSeconds":float(slope*max(len(rb)-1,1)),
      "segments":seg
    }

def measure_starts(c):
    return {int(r["measure"]):float(r["startSeconds"]) for r in c["grid"]["measures"] if r.get("startSeconds") is not None}
def ref_starts(ref):
    return {int(r["measureNumber"]):float(r["startSeconds"]) for r in ref["measureBoundaries"]}

def measure_diag(cs,rs,shift):
    pairs=[]
    for cm,t in cs.items():
        rm=cm+shift
        if rm in rs:pairs.append((rm,float(t-rs[rm])))
    if len(pairs)<2:return None
    x=np.asarray([p[0] for p in pairs],float); e=np.asarray([p[1] for p in pairs]); a=np.abs(e)
    slope,inter=np.polyfit(x,e,1)
    return {
      "measureShift":int(shift),"pairCount":len(e),
      "meanAbsoluteErrorSeconds":float(a.mean()),
      "medianAbsoluteErrorSeconds":float(np.median(a)),
      "meanSignedErrorSeconds":float(e.mean()),
      "secondsPerReferenceMeasure":float(slope),
      "predictedDriftAcross113MeasuresSeconds":float(slope*112)
    }

def compare(args):
    p=Path(args.candidate_json); frozen=sha256_file(p); bundle=json.loads(p.read_text())
    if bundle.get("referenceBlindGeneration") is not True:raise RuntimeError("not blind")
    refp=Path(args.professional_timing_map); ref=json.loads(refp.read_text())
    rb=ref_beats(ref); rs=ref_starts(ref)
    results=[]
    for c in bundle["candidates"]:
        cb=np.asarray(c["grid"]["beatTimesSeconds"],float)
        bds=[beat_diag(cb,rb,s) for s in range(-24,25)]
        bds=[x for x in bds if x]
        bestb=min(bds,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["beatIndexShift"])))
        mds=[measure_diag(measure_starts(c),rs,s) for s in range(-8,9)]
        mds=[x for x in mds if x]
        bestm=min(mds,key=lambda x:(x["medianAbsoluteErrorSeconds"],x["meanAbsoluteErrorSeconds"],abs(x["measureShift"])))
        results.append({
          "name":c["name"],
          "reportedTempoBpm":c["estimator"]["reportedTempoBpm"],
          "candidateBeatCount":len(cb),
          "referenceBeatCount":len(rb),
          "beatCountDifference":int(len(cb)-len(rb)),
          "bestBeatIndexShiftDiagnostic":bestb,
          "bestMeasureShiftDiagnostic":bestm
        })
    out={
      "schemaVersion":6,
      "kind":"gomyway-reference-independent-timebase-v6-professional-comparison",
      "candidateFrozenSha256BeforeReferenceRead":frozen,
      "candidateMutatedAfterComparison":False,
      "comparisonIsDiagnosticOnly":True,
      "primaryCandidateNameFrozenBeforeReferenceRead":bundle["primaryCandidateName"],
      "professionalTimingMapSha256":sha256_file(refp),
      "results":results,
      "interpretationBoundary":"All comparison metrics are diagnostic only. V6 remains frozen."
    }
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
