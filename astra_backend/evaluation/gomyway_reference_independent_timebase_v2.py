"""Go My Way reference-independent timebase V2.

Generate phase:
- reads only source audio + fixed BS-Roformer + fixed cleanup math;
- creates multiple raw/cleaned rhythm-bearing timing candidates;
- chooses the primary candidate using audio-only confidence before any reference read.

Compare phase:
- reads the already frozen bundle and professional timing map;
- diagnostics only; never rewrites candidate bundle.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import soundfile as sf

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from stem_bleed_cleanup_v1 import CleanupConfig, suppress_cross_stem_bleed
from v143_candidate_timing_adapter import build_subdivision_grid
from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
from v143_reference_free_timing import estimate_reference_free_timing_from_samples

EXPECTED_AUDIO_SOURCE="public/gomywayfullaitest.m4a"
EXPECTED_AUDIO_GIT_BLOB="5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"
BEATS_PER_MEASURE=4
SUBDIVISIONS_PER_BEAT=4
CLEANUP_CONFIG=CleanupConfig(n_fft=2048,hop=512,power=2.0,competition=0.50,floor_gain=0.60)

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

def summarize(vals):
    vals=[float(v) for v in vals if math.isfinite(float(v))]
    if not vals: return {"count":0,"mean":None,"median":None,"min":None,"max":None}
    return {"count":len(vals),"mean":float(np.mean(vals)),"median":float(np.median(vals)),
            "min":float(np.min(vals)),"max":float(np.max(vals))}

def timing_candidate(name: str, samples: np.ndarray, sr: int, provenance: dict) -> dict:
    timing=estimate_reference_free_timing_from_samples(samples,sr)
    repair=repair_reference_free_beat_grid_from_samples(samples,sr,timing)
    repaired=repair.timing
    slots=build_subdivision_grid(repaired.beat_times,beats_per_measure=4,
        subdivisions_per_beat=4,measure_start=1,first_beat_in_measure=repaired.first_beat_in_measure)
    measures={}
    for slot in slots:
        row=measures.setdefault(int(slot.measure),{"measure":int(slot.measure),"steps":{}})
        row["steps"][str(int(slot.step))]=float(slot.time_seconds)
    normalized=[]
    for m in sorted(measures):
        steps=measures[m]["steps"]
        normalized.append({"measure":m,"availableStepCount":len(steps),
                           "stepTimesSeconds":steps,"startSeconds":steps.get("0")})
    bt=[float(x) for x in repaired.beat_times]
    bi=[b-a for a,b in zip(bt[:-1],bt[1:])]
    return {
      "name":name,
      "provenance":provenance,
      "estimator":{
        "name":"v143-reference-free-timing-plus-beat-grid-repair",
        "tempoBpm":float(repaired.tempo_bpm),
        "beatConfidence":float(repaired.beat_confidence),
        "barConfidence":float(repaired.bar_confidence),
        "firstBeatInMeasure":int(repaired.first_beat_in_measure),
        "downbeatIndexMod4":int(repaired.downbeat_index_mod4),
        "meterAssumption":{"numerator":4,"denominator":4},
        "stepsPerMeasure":16
      },
      "grid":{
        "beatCount":len(bt),"beatTimesSeconds":bt,
        "beatIntervalSummarySeconds":summarize(bi),
        "measureCountWithAnySlots":len(normalized),
        "firstMeasureNumber":min(measures) if measures else None,
        "lastMeasureNumber":max(measures) if measures else None,
        "slotCount":len(slots),"measures":normalized
      },
      "repairDiagnostics":repair.diagnostics()
    }

def generate(args):
    source=Path(args.audio_source); wav=Path(args.audio_wav); model=Path(args.model)
    samples,sr=sf.read(str(wav),dtype="float32",always_2d=True)
    if int(sr)!=44100: raise RuntimeError(f"expected 44100 Hz, got {sr}")
    sep=BsRoformer6StemOnnxAdapter(model)
    stems=sep.separate_array(samples,int(sr))
    cleaned,masks=suppress_cross_stem_bleed(stems,int(sr),CLEANUP_CONFIG)

    variants={
      "raw_mix":(samples,{"kind":"raw-source-mix"}),
      "raw_guitar":(stems["guitar"],{"kind":"separator-stem","stem":"guitar"}),
      "raw_drums":(stems["drums"],{"kind":"separator-stem","stem":"drums"}),
      "raw_guitar_drums_sum":(stems["guitar"]+stems["drums"],{"kind":"separator-stem-sum","stems":["guitar","drums"]}),
      "cleaned_guitar":(cleaned["guitar"],{"kind":"fixed-soft-bleed-cleanup","stem":"guitar"}),
      "cleaned_drums":(cleaned["drums"],{"kind":"fixed-soft-bleed-cleanup","stem":"drums"}),
      "cleaned_guitar_drums_sum":(cleaned["guitar"]+cleaned["drums"],{"kind":"fixed-soft-bleed-cleanup-sum","stems":["guitar","drums"]}),
    }
    candidates=[]
    for name,(audio,prov) in variants.items():
        prov=dict(prov)
        prov["audioSha256"]=hashlib.sha256(np.asarray(audio,dtype=np.float32).tobytes()).hexdigest()
        candidates.append(timing_candidate(name,audio,int(sr),prov))

    ranked=sorted(candidates,key=lambda c:(c["estimator"]["barConfidence"],c["estimator"]["beatConfidence"],
                                           c["grid"]["beatCount"]),reverse=True)
    primary=ranked[0]["name"]
    bundle={
      "schemaVersion":2,"kind":"gomyway-reference-independent-full-song-grid-v2-bundle",
      "status":"frozen-before-professional-comparison",
      "referenceBlindGeneration":True,
      "professionalTimingMapReadDuringGeneration":False,
      "professionalScorerRowsReadDuringGeneration":False,
      "primarySelectionRule":"max(barConfidence, then beatConfidence, then beatCount), audio-only",
      "primaryCandidateName":primary,
      "audio":{"sourcePath":EXPECTED_AUDIO_SOURCE,"expectedRepositoryGitBlob":EXPECTED_AUDIO_GIT_BLOB,
               "sourceSha256":sha256_file(source),"decodedWavSha256":sha256_file(wav),
               "sampleRate":int(sr),"durationSeconds":float(len(samples)/sr)},
      "separator":{"name":"BS-Roformer-SW 6-stem ONNX","modelSha256":FP16_SHA256},
      "cleanup":{"status":"experimental-not-trusted-correction",
                 "evidenceBoundary":"fixed configuration previously passed synthetic injected-bleed unit test only; recognizer-gated real evaluation applied zero cleanups",
                 "config":CLEANUP_CONFIG.to_dict()},
      "candidates":candidates,
      "interpretationBoundary":"All V2 candidates and primary selection are frozen from audio-side evidence before professional timing comparison. Cleanup variants are experimental inputs, not assumed improvements."
    }
    write_json(Path(args.output_json),bundle)
    print(json.dumps({"primaryCandidateName":primary,
      "candidates":[{"name":c["name"],"tempoBpm":c["estimator"]["tempoBpm"],
                     "beatConfidence":c["estimator"]["beatConfidence"],
                     "barConfidence":c["estimator"]["barConfidence"],
                     "beatCount":c["grid"]["beatCount"]} for c in candidates]},indent=2))

def candidate_starts(c):
    return {int(r["measure"]):float(r["startSeconds"]) for r in c["grid"]["measures"] if r.get("startSeconds") is not None}
def reference_starts(r):
    return {int(x["measureNumber"]):float(x["startSeconds"]) for x in r["measureBoundaries"]}

def shift_diag(cs,rs,shift):
    pairs=[]
    for c,ct in cs.items():
        r=c+shift
        if r in rs: pairs.append({"candidateMeasure":c,"referenceMeasure":r,"signedErrorSeconds":ct-rs[r]})
    if not pairs:return None
    e=np.array([p["signedErrorSeconds"] for p in pairs],dtype=float); a=np.abs(e)
    return {"measureShift":shift,"pairCount":len(pairs),"meanSignedErrorSeconds":float(e.mean()),
      "medianSignedErrorSeconds":float(np.median(e)),"meanAbsoluteErrorSeconds":float(a.mean()),
      "medianAbsoluteErrorSeconds":float(np.median(a)),"maxAbsoluteErrorSeconds":float(a.max()),"pairs":pairs}

def compare(args):
    p=Path(args.candidate_json); frozen_sha=sha256_file(p); bundle=json.loads(p.read_text())
    if bundle.get("referenceBlindGeneration") is not True: raise RuntimeError("not reference-blind")
    refp=Path(args.professional_timing_map); ref=json.loads(refp.read_text())
    if ref.get("audioSource")!=EXPECTED_AUDIO_SOURCE: raise RuntimeError("timing map binding mismatch")
    rs=reference_starts(ref); results=[]
    for c in bundle["candidates"]:
        ds=[d for d in (shift_diag(candidate_starts(c),rs,s) for s in range(-8,9)) if d]
        best=min(ds,key=lambda d:(d["medianAbsoluteErrorSeconds"],d["meanAbsoluteErrorSeconds"],abs(d["measureShift"])))
        zero=next((d for d in ds if d["measureShift"]==0),None)
        drift=None
        if len(best["pairs"])>=2:
            xs=np.array([q["referenceMeasure"] for q in best["pairs"]],dtype=float)
            ys=np.array([q["signedErrorSeconds"] for q in best["pairs"]],dtype=float)
            slope,intercept=np.polyfit(xs,ys,1)
            drift={"secondsPerReferenceMeasure":float(slope),"interceptSeconds":float(intercept),
                   "predictedDriftAcross113MeasuresSeconds":float(slope*112)}
        results.append({"name":c["name"],"tempoBpm":c["estimator"]["tempoBpm"],
          "beatConfidence":c["estimator"]["beatConfidence"],"barConfidence":c["estimator"]["barConfidence"],
          "sameNumberingDiagnostic":zero,
          "bestIntegerMeasureShiftDiagnostic":{k:v for k,v in best.items() if k!="pairs"},
          "bestShiftDrift":drift})
    out={"schemaVersion":2,"kind":"gomyway-reference-independent-full-song-grid-v2-professional-comparison",
         "candidateFrozenSha256BeforeReferenceRead":frozen_sha,"candidateMutatedAfterComparison":False,
         "comparisonIsDiagnosticOnly":True,"primaryCandidateNameFrozenBeforeReferenceRead":bundle["primaryCandidateName"],
         "professionalTimingMapSha256":sha256_file(refp),"results":results,
         "interpretationBoundary":"Comparison is diagnostic only. Do not use these results to rewrite V2 or retroactively change its primary candidate."}
    write_json(Path(args.output_json),out)
    print(json.dumps({"candidateSha256":frozen_sha,"primaryCandidateName":bundle["primaryCandidateName"],
      "results":[{"name":r["name"],**r["bestIntegerMeasureShiftDiagnostic"],"drift":r["bestShiftDrift"]} for r in results]},indent=2))

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="mode",required=True)
    g=sub.add_parser("generate"); g.add_argument("--audio-source",required=True); g.add_argument("--audio-wav",required=True)
    g.add_argument("--model",required=True); g.add_argument("--output-json",required=True); g.set_defaults(func=generate)
    c=sub.add_parser("compare"); c.add_argument("--candidate-json",required=True); c.add_argument("--professional-timing-map",required=True)
    c.add_argument("--output-json",required=True); c.set_defaults(func=compare)
    a=ap.parse_args(); a.func(a)
if __name__=="__main__": main()
