#!/usr/bin/env python3
"""Model-free source-domain joint coverage review V1."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

from synthetic.source_domain_simulator_diversity_v1 import source_parameters, CHALLENGE_PROFILE
from synthetic.source_domain_simulator_preparation_v1 import _template_and_variant
from synthetic.source_domain_simulator_training_v1 import validate_datasets

SCHEMA="astra-source-domain-joint-coverage-review-v1"
NUMERIC_AXES=("attackBaseRiseSeconds","transientNoiseGain","transientDecaySeconds","dampingMultiplier",
              "brightness","pickPosition","lowpassCutoffHz","spectralTiltDb","highpassCornerHz",
              "nonlinearDrive","nonlinearWet","broadbandNoiseRmsRelative")
FAMILIES=("isolated","scales","chords","repeated","legato","palmmute","mixed")

def empirical_percentile(train,value):
    a=np.asarray(train,dtype=float)
    if a.size==0: return None
    return float(np.mean(a<=float(value)))

def summarize(a):
    x=np.asarray(a,dtype=float)
    if x.size==0: return {"count":0,"min":None,"median":None,"max":None}
    if not np.isfinite(x).all(): raise RuntimeError("nonfinite coverage values")
    return {"count":int(x.size),"min":float(x.min()),"median":float(np.median(x)),"max":float(x.max())}

def training_parameter_rows(control):
    c=control
    train_rows=np.flatnonzero(c["split"]=="train")
    chord_train=np.flatnonzero((c["family"]=="chords")&(c["split"]=="train"))
    chord_slot={int(r):slot for slot,r in enumerate(chord_train.tolist())}
    occurrences={}
    out=[]
    for i in train_rows:
        fam=str(c["family"][i]); tid=str(c["template_id"][i])
        occ=occurrences.get(tid,0); occurrences[tid]=occ+1
        slot=chord_slot.get(int(i))
        template,variant=_template_and_variant(fam,tid,occ,s9_slot=slot)
        p=source_parameters(template["templateId"],variant)
        out.append({"rowIndex":int(i),"family":fam,"templateId":template["templateId"],"variant":int(variant),**p})
    if len(out)!=210: raise RuntimeError("expected 210 training parameter rows")
    return out

def conjunction_flags(row):
    return [
      row["attackBaseRiseSeconds"]>=.045,
      row["transientNoiseGain"]<=.03,
      row["dampingMultiplier"]>=1.45,
      row["brightness"]<=.60,
      row["pickPosition"]>=.42,
      row["lowpassCutoffHz"]<=3500,
      row["spectralTiltDb"]<=-4.0,
      row["broadbandNoiseRmsRelative"]>=.001,
      bool(row["nonlinearActive"]) and row["nonlinearWet"]>=.20,
    ]

def onset_flux_by_family(features,onset,family,mask):
    values={f:[] for f in FAMILIES}; pooled=[]
    for idx in np.flatnonzero(mask):
        frames=np.flatnonzero(np.any(onset[idx]>0,axis=0))
        for fr in frames:
            if fr<=0: continue
            v=float(np.maximum(features[idx,fr]-features[idx,fr-1],0).sum())
            values[str(family[idx])].append(v); pooled.append(v)
    return values,pooled

def displacement_by_family(changed,control,family,mask):
    values={f:[] for f in FAMILIES}; pooled=[]
    for idx in np.flatnonzero(mask):
        v=float(np.abs(changed[idx]-control[idx]).mean())
        values[str(family[idx])].append(v); pooled.append(v)
    return values,pooled

def feature_coverage(c,i,q):
    train=(c["split"]=="train"); test=(c["split"]=="test")
    train_flux,train_flux_all=onset_flux_by_family(i["features"],c["onset"],c["family"],train)
    chal_flux,chal_flux_all=onset_flux_by_family(q["features"],c["onset"],c["family"],test)
    train_disp,train_disp_all=displacement_by_family(i["features"],c["features"],c["family"],train)
    chal_disp,chal_disp_all=displacement_by_family(q["features"],c["features"],c["family"],test)

    fams={}
    for fam in FAMILIES:
        tf=train_flux[fam]; qf=chal_flux[fam]; td=train_disp[fam]; qd=chal_disp[fam]
        fams[fam]={
          "interventionTrainOnsetFlux":summarize(tf),
          "challengeTestOnsetFlux":summarize(qf),
          "challengeOnsetFluxPercentilesInTraining":[empirical_percentile(tf,x) for x in qf],
          "medianChallengeOnsetFluxPercentile":float(np.median([empirical_percentile(tf,x) for x in qf])) if qf else None,
          "interventionTrainRowDisplacement":summarize(td),
          "challengeTestRowDisplacement":summarize(qd),
          "challengeRowDisplacementPercentilesInTraining":[empirical_percentile(td,x) for x in qd],
          "medianChallengeRowDisplacementPercentile":float(np.median([empirical_percentile(td,x) for x in qd])) if qd else None,
        }
    return {
      "families":fams,
      "pooled":{
        "interventionTrainOnsetFlux":summarize(train_flux_all),
        "challengeTestOnsetFlux":summarize(chal_flux_all),
        "medianChallengeOnsetFluxPercentile":float(np.median([empirical_percentile(train_flux_all,x) for x in chal_flux_all])),
        "interventionTrainRowDisplacement":summarize(train_disp_all),
        "challengeTestRowDisplacement":summarize(chal_disp_all),
        "medianChallengeRowDisplacementPercentile":float(np.median([empirical_percentile(train_disp_all,x) for x in chal_disp_all])),
      }
    }

def run(control_path,intervention_path,challenge_path,out):
    identity=validate_datasets(control_path,intervention_path,challenge_path)
    c=np.load(control_path,allow_pickle=False); i=np.load(intervention_path,allow_pickle=False); q=np.load(challenge_path,allow_pickle=False)
    rows=training_parameter_rows(c)

    numeric={}
    for axis in NUMERIC_AXES:
        vals=[float(r[axis]) for r in rows]
        cv=float(CHALLENGE_PROFILE[axis])
        numeric[axis]={**summarize(vals),"challengeValue":cv,"challengeEmpiricalPercentile":empirical_percentile(vals,cv)}

    categorical={
      "nonlinearActive":{"trainingTrueCount":int(sum(bool(r["nonlinearActive"]) for r in rows)),
                         "trainingFalseCount":int(sum(not bool(r["nonlinearActive"]) for r in rows)),
                         "challenge":bool(CHALLENGE_PROFILE["nonlinearActive"])},
      "humActive":{"trainingTrueCount":int(sum(bool(r["humActive"]) for r in rows)),
                   "trainingFalseCount":int(sum(not bool(r["humActive"]) for r in rows)),
                   "challenge":bool(CHALLENGE_PROFILE["humActive"])},
      "humFundamentalHz":{"training50Count":int(sum(int(r["humFundamentalHz"])==50 for r in rows)),
                          "training60Count":int(sum(int(r["humFundamentalHz"])==60 for r in rows)),
                          "challenge":int(CHALLENGE_PROFILE["humFundamentalHz"])},
    }

    cumulative=[]
    alive=np.ones(len(rows),dtype=bool)
    for k in range(9):
        alive &= np.array([conjunction_flags(r)[k] for r in rows],dtype=bool)
        cumulative.append({"throughCondition":k+1,"count":int(alive.sum()),"fraction":float(alive.mean())})
    by_family={}
    final=np.array([all(conjunction_flags(r)) for r in rows],dtype=bool)
    for fam in FAMILIES:
        mask=np.array([r["family"]==fam for r in rows])
        by_family[fam]={"trainingRows":int(mask.sum()),"fullConjunctionCount":int((mask&final).sum()),
                        "fullConjunctionFraction":float((mask&final).sum()/mask.sum()) if mask.sum() else None}

    result={
      "schema":SCHEMA,
      "identity":identity,
      "trainingRowCount":len(rows),
      "numericMarginals":numeric,
      "categoricalMarginals":categorical,
      "challengeSideConjunction":{"cumulative":cumulative,"fullByFamily":by_family},
      "featureCoverage":feature_coverage(c,i,q),
      "execution":{"modelRun":False,"modelsLoaded":0,"modelInference":False,"optimizerSteps":0,
                   "waveformRenders":0,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                   "thresholdSearch":False,"thresholdRetuning":False},
      "interpretationLimit":"Descriptive coverage review only; no simulator/challenge/model parameter selection is authorized."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_COVERAGE="+json.dumps(result,sort_keys=True))
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--control",required=True); ap.add_argument("--intervention",required=True)
    ap.add_argument("--challenge",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); run(a.control,a.intervention,a.challenge,a.out)

if __name__=="__main__": main()
