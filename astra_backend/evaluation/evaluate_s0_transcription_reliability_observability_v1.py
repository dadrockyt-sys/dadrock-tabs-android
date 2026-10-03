"""S0 no-reference transcription reliability observability V1.

Descriptive-only follow-up to transcription failure attribution V1.

For each untouched raw separator guitar/bass output, collect features that would be
available at inference time without reference audio:
- separator-output overlap/dominance diagnostics,
- relative stem energy,
- Basic Pitch event density/amplitude/duration/pitch concentration,
- near-synchronous octave-event behavior.

For S0 development analysis only, compare those no-reference features with the
oracle-audio transcription-agreement F1 from the same probe. No threshold, model,
classifier, or automatic accept/reject rule is fit here.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from evaluate_s0_transcription_failure_attribution_v1 import (
    ONSET_TOLERANCE_SECONDS,
    collapse_truth,
    load,
    run_probe,
    truth_stems,
)
from pretrained_note_front_end_v1 import (
    BASIC_PITCH_VERSION,
    FRAME_THRESHOLD,
    MIN_NOTE_LENGTH_MS,
    ONSET_THRESHOLD,
    basic_pitch_model_identity,
)
from score_note_onsets import score_note_onsets
from stem_bleed_cleanup_v1 import si_sdr
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems


def finite_mean(values):
    vals=[float(x) for x in values if x is not None and math.isfinite(float(x))]
    return float(np.mean(vals)) if vals else None


def percentile(values, q):
    vals=[float(x) for x in values if x is not None and math.isfinite(float(x))]
    return float(np.percentile(vals,q)) if vals else None


def corr(x,y):
    pairs=[(float(a),float(b)) for a,b in zip(x,y)
           if a is not None and b is not None and math.isfinite(float(a)) and math.isfinite(float(b))]
    if len(pairs)<3:
        return None
    a=np.asarray([p[0] for p in pairs],dtype=np.float64)
    b=np.asarray([p[1] for p in pairs],dtype=np.float64)
    a=a-a.mean(); b=b-b.mean()
    den=float(np.linalg.norm(a)*np.linalg.norm(b))
    return float(np.dot(a,b)/den) if den>1e-20 else None


def rankdata(values):
    order=np.argsort(values,kind="mergesort")
    ranks=np.empty(len(values),dtype=np.float64)
    i=0
    while i<len(values):
        j=i+1
        while j<len(values) and values[order[j]]==values[order[i]]:
            j+=1
        rank=(i+j-1)/2.0+1.0
        ranks[order[i:j]]=rank
        i=j
    return ranks


def spearman(x,y):
    pairs=[(float(a),float(b)) for a,b in zip(x,y)
           if a is not None and b is not None and math.isfinite(float(a)) and math.isfinite(float(b))]
    if len(pairs)<3:
        return None
    a=np.asarray([p[0] for p in pairs],dtype=np.float64)
    b=np.asarray([p[1] for p in pairs],dtype=np.float64)
    return corr(rankdata(a),rankdata(b))


def event_features(events,duration):
    count=len(events)
    amplitudes=[e.get("amplitude") for e in events if e.get("amplitude") is not None]
    durations=[e["end"]-e["start"] for e in events if e.get("end") is not None and e["end"]>e["start"]]
    midis=[e["midi"] for e in events]

    dominant_share=0.0
    if midis:
        counts={}
        for m in midis: counts[m]=counts.get(m,0)+1
        dominant_share=max(counts.values())/len(midis)

    octave_related=0
    for i,e in enumerate(events):
        found=False
        for j,o in enumerate(events):
            if i==j: continue
            if abs(e["start"]-o["start"])>ONSET_TOLERANCE_SECONDS: continue
            gap=abs(e["midi"]-o["midi"])
            if gap>=12 and gap%12==0:
                found=True; break
        octave_related+=int(found)

    return {
        "eventCount":count,
        "eventDensityPerSecond":count/max(duration,1e-12),
        "amplitudeMean":finite_mean(amplitudes),
        "amplitudeP10":percentile(amplitudes,10),
        "amplitudeP90":percentile(amplitudes,90),
        "durationMeanSeconds":finite_mean(durations),
        "durationP50Seconds":percentile(durations,50),
        "dominantMidiShare":float(dominant_share),
        "pitchRangeSemitones":float(max(midis)-min(midis)) if midis else 0.0,
        "octaveRelatedEventFraction":octave_related/count if count else 0.0,
    }


def flatten_observability(row):
    d=row["separatorDiagnostics"]
    e=row["transcriberDiagnostics"]
    return {
        "stemToMixtureEnergyDb":d["stemToMixtureEnergyDb"],
        "interferencePressure":d["interferencePressure"],
        "competitorDominanceFraction":d["competitorDominanceFraction"],
        "targetDominanceFraction":d["targetDominanceFraction"],
        "ambiguousFraction":d["ambiguousFraction"],
        "strongestCompetitorEnergyRatioDb":d["strongestCompetitorEnergyRatioDb"],
        "eventDensityPerSecond":e["eventDensityPerSecond"],
        "amplitudeMean":e["amplitudeMean"],
        "amplitudeP10":e["amplitudeP10"],
        "durationMeanSeconds":e["durationMeanSeconds"],
        "dominantMidiShare":e["dominantMidiShare"],
        "pitchRangeSemitones":e["pitchRangeSemitones"],
        "octaveRelatedEventFraction":e["octaveRelatedEventFraction"],
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--s0-root",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--output-json",required=True)
    args=ap.parse_args()

    identity=basic_pitch_model_identity()
    if identity["packageVersion"]!=BASIC_PITCH_VERSION:
        raise RuntimeError("Basic Pitch package version mismatch")
    if identity["modelSha256"]!="3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676":
        raise RuntimeError("Basic Pitch model SHA mismatch")

    adapter=BsRoformer6StemOnnxAdapter(Path(args.model))
    diag_cfg=DiagnosticConfig()
    root=Path(args.s0_root)
    rows=[]
    started=time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="astra_s0_observability_") as td:
        td=Path(td)
        for d in sorted(root.glob("S0M*")):
            mixes=list(d.glob("*_mix.wav"))
            if len(mixes)!=1: continue
            mix,fs=load(mixes[0])
            truth=truth_stems(d)
            raw=adapter.separate_array(mix,fs)
            stem_diag=diagnose_stems(mix,raw,fs,diag_cfg)
            length=len(mix)
            duration=length/float(fs)

            for target in ("guitar","bass"):
                oracle=collapse_truth(truth,target,length,mix.shape[1])
                present=float(np.mean(oracle.astype(np.float64)**2))>1e-12
                sep=raw[target][:length]
                sep_events=run_probe(sep,fs,td/f"{d.name}_{target}_sep.wav",f"{d.name}:{target}:sep")
                tx=event_features(sep_events,duration)

                sd=stem_diag[target]
                strongest=sd.get("strongestOverlapCompetitor")
                strongest_ratio=None
                if strongest and strongest in sd.get("perCompetitor",{}):
                    strongest_ratio=sd["perCompetitor"][strongest].get("energyRatioToTargetDb")
                obs={
                    "stemToMixtureEnergyDb":sd.get("stemToMixtureEnergyDb"),
                    "interferencePressure":sd.get("interferencePressure"),
                    "competitorDominanceFraction":sd.get("competitorDominanceFraction"),
                    "targetDominanceFraction":sd.get("targetDominanceFraction"),
                    "ambiguousFraction":sd.get("ambiguousFraction"),
                    "strongestOverlapCompetitor":strongest,
                    "strongestCompetitorEnergyRatioDb":strongest_ratio,
                }

                row={
                    "id":d.name,
                    "target":target,
                    "targetPresent":present,
                    "separatorDiagnostics":obs,
                    "transcriberDiagnostics":tx,
                }
                if present:
                    oracle_events=run_probe(oracle,fs,td/f"{d.name}_{target}_oracle.wav",f"{d.name}:{target}:oracle")
                    agreement=score_note_onsets(
                        sep_events,oracle_events,start=0.0,end=duration+1e-9,
                        tolerance=ONSET_TOLERANCE_SECONDS,
                    )
                    row["oracleEventCount"]=len(oracle_events)
                    row["rawSiSdrDb"]=float(si_sdr(oracle,sep))
                    row["transcriptionAgreementF1"]=agreement["f1"]
                    row["transcriptionAgreementPrecision"]=agreement["precision"]
                    row["transcriptionAgreementRecall"]=agreement["recall"]
                else:
                    row["oracleEventCount"]=0
                    row["rawSiSdrDb"]=None
                    row["transcriptionAgreementF1"]=None
                    row["transcriptionAgreementPrecision"]=None
                    row["transcriptionAgreementRecall"]=None
                rows.append(row)

    present=[r for r in rows if r["targetPresent"] and r["transcriptionAgreementF1"] is not None]
    feature_names=list(flatten_observability(present[0]).keys()) if present else []
    associations={}
    y=[r["transcriptionAgreementF1"] for r in present]
    for name in feature_names:
        x=[flatten_observability(r)[name] for r in present]
        associations[name]={
            "pearsonWithTranscriptionAgreementF1":corr(x,y),
            "spearmanWithTranscriptionAgreementF1":spearman(x,y),
            "finiteProbeCount":sum(v is not None and math.isfinite(float(v)) for v in x),
        }

    ranked=sorted(
        [{"feature":k,**v} for k,v in associations.items() if v["spearmanWithTranscriptionAgreementF1"] is not None],
        key=lambda z:abs(z["spearmanWithTranscriptionAgreementF1"]),
        reverse=True,
    )

    absent=[r for r in rows if not r["targetPresent"]]
    result={
        "schemaVersion":1,
        "kind":"s0-transcription-reliability-observability-v1",
        "descriptiveOnly":True,
        "thresholdFitPerformed":False,
        "automaticAcceptanceRuleDefined":False,
        "separatorOutputMutation":False,
        "separatorModelSha256":FP16_SHA256,
        "transcriber":{
            "name":"Basic Pitch",
            "packageVersion":BASIC_PITCH_VERSION,
            "modelSha256":identity["modelSha256"],
            "onsetThreshold":ONSET_THRESHOLD,
            "frameThreshold":FRAME_THRESHOLD,
            "minimumNoteLengthMs":MIN_NOTE_LENGTH_MS,
        },
        "diagnosticConfig":diag_cfg.to_dict(),
        "presentTargetProbeCount":len(present),
        "absentTargetProbeCount":len(absent),
        "featureAssociations":associations,
        "rankedByAbsoluteSpearmanDescriptiveOnly":ranked,
        "absentTargetObservations":[{
            "id":r["id"],"target":r["target"],
            "separatorDiagnostics":r["separatorDiagnostics"],
            "transcriberDiagnostics":r["transcriberDiagnostics"],
        } for r in absent],
        "results":rows,
        "totalWallSeconds":time.perf_counter()-started,
        "interpretationBoundary":(
            "Exploratory S0 descriptive analysis only. Associations may generate hypotheses but may not be "
            "converted into acceptance thresholds on these same fixtures. No automatic confidence gate is authorized."
        ),
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
