from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import benchmark_gomyway_3676_patch_rhythm24_v28_exact_anchor_unanimous_training_tighten_v38 as v38

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46-manifest.json"
EXPECTED = (272,595,341)
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal","section","shiftedWindow")
ANCHOR_Q = float(v28.FROZEN_Q)
BROAD_Q = 0.225
# V46 is exploratory only. Its gate architecture is informed by V45 diagnostic outcomes,
# so it must earn a fresh confirmation later on the separately reserved untouched 1/64 family.
EXPOSED_PHASES = tuple(v28.CONFIRM_PHASES) + (
    0.03125, 0.09375, 0.15625, 0.21875, 0.28125, 0.34375, 0.40625, 0.46875,
    0.53125, 0.59375, 0.65625, 0.71875, 0.78125, 0.84375, 0.90625, 0.96875,
)

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def choose_q_train_only(xtr,ytr,mtr,radius,lam):
    strict_count=0; rows=[]
    for scheme in INNER_SCHEMES:
        ids=v38.inner_ids(mtr,scheme); ap=bp=0; al=[]; bl=[]
        for fold in range(INNER_FOLDS):
            val=ids==fold; sub=~val
            if not np.any(val) or not np.any(sub): continue
            model=v2.fit_pairwise_ranker(xtr[sub],ytr[sub],mtr[sub],radius,lam)
            scores=v2.scores_for(xtr[val],model)
            a,la,*_=v17.pass_at_q(scores,ytr[val],ANCHOR_Q)
            b,lb,*_=v17.pass_at_q(scores,ytr[val],BROAD_Q)
            ap+=int(a); bp+=int(b); al.append(float(la)); bl.append(float(lb))
        strict=bp>ap; strict_count+=int(strict)
        rows.append({"scheme":scheme,"anchorPasses":ap,"broadPasses":bp,"strictPassPreferenceForBroad":strict,
                     "meanAnchorLift":float(np.mean(al)),"meanBroadLift":float(np.mean(bl))})
    q=BROAD_Q if strict_count>=1 else ANCHOR_Q
    return q,{"architecture":"exact-v28-anchor-broaden-on-any-strict-training-support",
              "strictSupportCount":strict_count,"chosenQ":q,"broadenedAboveAnchorQ":bool(q>ANCHOR_Q),
              "outerHeldoutLabelsUsed":False,"v45DiagnosticInformedArchitecture":True,"schemes":rows}

def main():
    cp=v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH; before=sha256(cp)
    payload=json.loads(SOURCE_PATH.read_text(encoding='utf-8')); rows=list(payload.get('candidateSlots') or [])
    if not rows or tuple(payload.get('frozenChampionMatchedMissingExtra') or [])!=EXPECTED: raise RuntimeError('bad source anchor')
    names=sorted((rows[0].get('features') or {}).keys())
    xb=np.asarray([[float((r.get('features') or {}).get(f,0.0)) for f in names] for r in rows],dtype=np.float64)
    x=np.concatenate([xb,v17.phase_features(rows)],axis=1)
    y=np.asarray([str(r.get('label'))=='true' for r in rows],dtype=bool)
    measures=np.asarray([int(r['measure']) for r in rows],dtype=np.int32)

    schemes=[]; total=v28total=rescues=regressions=broadened=folds_total=0
    for phase in EXPOSED_PHASES:
        lo,hi=int(np.min(measures)),int(np.max(measures))
        ids=np.asarray([v18.phased_fold(int(m),lo,hi,OUTER_FOLDS,float(phase)) for m in measures],dtype=np.int16)
        pp=pv=0; prows=[]
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold+1}/{OUTER_FOLDS} ...",flush=True)
            test=ids==fold; train=~test
            cm=v5.choose_model(x[train],y[train],measures[train]); radius=int(cm['pairRadius']); lam=float(cm['lambda'])
            q,sel=choose_q_train_only(x[train],y[train],measures[train],radius,lam)
            model=v2.fit_pairwise_ranker(x[train],y[train],measures[train],radius,lam); scores=v2.scores_for(x[test],model)
            passed,lift,held,base=v17.pass_at_q(scores,y[test],q); vp,vl,vh,_=v17.pass_at_q(scores,y[test],ANCHOR_Q)
            pp+=int(passed); pv+=int(vp); broadened+=int(q>ANCHOR_Q); rescues+=int(passed and not vp); regressions+=int(vp and not passed)
            prows.append({"phase":float(phase),"fold":int(fold),"selector":sel,"outerQ":float(q),"passed":bool(passed),
                          "heldoutPrecisionLift":round(float(lift),2),"heldoutCandidate":held,"heldoutBase":base,
                          "v28Comparison":{"passed":bool(vp),"heldoutPrecisionLift":round(float(vl),2),"heldoutCandidate":vh}})
            print(f"  V46 q={q:.3f} strict={sel['strictSupportCount']}/3 pass={passed}; V28 pass={vp}",flush=True)
        schemes.append({"phase":float(phase),"passes":pp,"v28Passes":pv,"folds":prows}); total+=pp; v28total+=pv; folds_total+=len(prows)
    minp=min(s['passes'] for s in schemes); promising=total>v28total and minp>=4 and regressions<=rescues
    after=sha256(cp)
    if before!=after: raise RuntimeError('protected candidate changed')
    out={"schemaVersion":46,"profileType":"v45-strict-support-only-broaden","challengeSource":"combined-already-exposed-v28-and-v44-phases",
         "foldsPassed":total,"foldsTotal":folds_total,"minimumPhasePasses":minp,"v28ComparisonPasses":v28total,
         "rescuesVsV28":rescues,"regressionsVsV28":regressions,"foldsBroadenedAboveV28Q":broadened,
         "exploratoryPromising":promising,"architectureTaintedByV45Diagnostic":True,"requiresFreshUntouchedConfirmation":True,
         "newReserved1over64OddPhasesReferenced":False,"reservedUntouchedPhasesConsumed":False,
         "validatedNewChampion":False,"schemes":schemes,"protected949CandidateHashUnchanged":before==after,"productionPromotionAllowed":False}
    OUTPUT_PATH.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    MANIFEST_PATH.write_text(json.dumps({k:out[k] for k in ['schemaVersion','foldsPassed','foldsTotal','minimumPhasePasses','v28ComparisonPasses','rescuesVsV28','regressionsVsV28','foldsBroadenedAboveV28Q','exploratoryPromising','architectureTaintedByV45Diagnostic','requiresFreshUntouchedConfirmation','newReserved1over64OddPhasesReferenced','reservedUntouchedPhasesConsumed','validatedNewChampion','protected949CandidateHashUnchanged','productionPromotionAllowed']},indent=2)+'\n',encoding='utf-8')
    print('GOMYWAY 36.76 RHYTHM24 V45 STRICT-SUPPORT-ONLY BROADEN V46 COMPLETE')
    print('V46 folds passed:',total,'/',folds_total); print('Minimum V46 phase passes:',minp,'/ 5'); print('V28 comparison passes:',v28total,'/',folds_total)
    print('Rescues vs V28:',rescues); print('Regressions vs V28:',regressions); print('Folds broadened above V28 q:',broadened); print('Exploratory promising:',promising)
    print('New reserved 1/64 odd phases referenced: False'); print('Protected 949-event candidate hash unchanged:',before==after); print('Production promotion allowed: False')
    print('Output:',OUTPUT_PATH.relative_to(ROOT)); print('Manifest:',MANIFEST_PATH.relative_to(ROOT))
if __name__=='__main__': main()
