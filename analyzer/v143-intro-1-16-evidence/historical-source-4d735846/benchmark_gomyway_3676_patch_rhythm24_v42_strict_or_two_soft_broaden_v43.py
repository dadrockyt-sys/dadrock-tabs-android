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

ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
SOURCE_PATH=PUBLIC/'gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json'
OUTPUT_PATH=PUBLIC/'gomyway-3676-patch-rhythm24-v42-strict-or-two-soft-broaden-v43.json'
MANIFEST_PATH=PUBLIC/'gomyway-3676-patch-rhythm24-v42-strict-or-two-soft-broaden-v43-manifest.json'
EXPECTED=(272,595,341); OUTER_FOLDS=5; INNER_FOLDS=4; INNER_SCHEMES=('normal','section','shiftedWindow')
CHALLENGE_PHASES=v28.CONFIRM_PHASES; ANCHOR_Q=float(v28.FROZEN_Q); BROAD_Q=0.225

def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def choose_q(xtr,ytr,mtr,radius,lam):
    strict_count=soft_count=0; scheme_rows=[]
    for scheme in INNER_SCHEMES:
        ids=v38.inner_ids(mtr,scheme); ap=bp=0; al=[]; bl=[]
        for fold in range(INNER_FOLDS):
            val=ids==fold; sub=~val
            if not np.any(val) or not np.any(sub): continue
            model=v2.fit_pairwise_ranker(xtr[sub],ytr[sub],mtr[sub],radius,lam); scores=v2.scores_for(xtr[val],model)
            a,la,*_=v17.pass_at_q(scores,ytr[val],ANCHOR_Q); b,lb,*_=v17.pass_at_q(scores,ytr[val],BROAD_Q)
            ap+=int(a); bp+=int(b); al.append(float(la)); bl.append(float(lb))
        strict=bp>ap; tied=bp==ap and float(np.mean(bl))>float(np.mean(al)); soft=strict or tied
        strict_count+=int(strict); soft_count+=int(soft)
        scheme_rows.append({'scheme':scheme,'anchorPasses':ap,'broadPasses':bp,'strict':strict,'soft':soft,'meanAnchorLift':float(np.mean(al)),'meanBroadLift':float(np.mean(bl))})
    # V41 predeclared evidence: strict support existed on 18/40, while V42 proved 2-soft is useful.
    # V43 broadens when either signal is present: >=1 strict scheme OR >=2 soft schemes.
    gate=(strict_count>=1) or (soft_count>=2); q=BROAD_Q if gate else ANCHOR_Q
    return q,{'strictSupportCount':strict_count,'softSupportCount':soft_count,'gatePassed':gate,'chosenQ':q,'schemes':scheme_rows,'outerHeldoutLabelsUsed':False}

def main():
    cp=v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH; before=sha256(cp)
    payload=json.loads(SOURCE_PATH.read_text()); rows=list(payload.get('candidateSlots') or [])
    if not rows or tuple(payload.get('frozenChampionMatchedMissingExtra') or [])!=EXPECTED: raise RuntimeError('bad source anchor')
    names=sorted((rows[0].get('features') or {}).keys()); xb=np.asarray([[float((r.get('features') or {}).get(f,0.0)) for f in names] for r in rows])
    x=np.concatenate([xb,v17.phase_features(rows)],axis=1); y=np.asarray([str(r.get('label'))=='true' for r in rows],dtype=bool); measures=np.asarray([int(r['measure']) for r in rows],dtype=np.int32)
    schemes=[]; total=v28total=rescues=regressions=broadened=folds_total=0
    for phase in CHALLENGE_PHASES:
        lo,hi=int(np.min(measures)),int(np.max(measures)); ids=np.asarray([v18.phased_fold(int(m),lo,hi,OUTER_FOLDS,float(phase)) for m in measures])
        prows=[]; pp=pv=0
        for fold in range(OUTER_FOLDS):
            print(f'phase={phase} outer fold {fold+1}/{OUTER_FOLDS} ...',flush=True); test=ids==fold; train=~test
            cm=v5.choose_model(x[train],y[train],measures[train]); radius=int(cm['pairRadius']); lam=float(cm['lambda'])
            q,sel=choose_q(x[train],y[train],measures[train],radius,lam); model=v2.fit_pairwise_ranker(x[train],y[train],measures[train],radius,lam); scores=v2.scores_for(x[test],model)
            passed,lift,held,base=v17.pass_at_q(scores,y[test],q); vp,vl,vh,_=v17.pass_at_q(scores,y[test],ANCHOR_Q)
            pp+=int(passed); pv+=int(vp); broadened+=int(q>BROAD_Q-1e-12); rescues+=int(passed and not vp); regressions+=int(vp and not passed)
            prows.append({'phase':float(phase),'fold':fold,'selector':sel,'outerQ':q,'passed':bool(passed),'heldoutPrecisionLift':round(float(lift),2),'heldoutCandidate':held,'heldoutBase':base,'v28Comparison':{'passed':bool(vp),'heldoutPrecisionLift':round(float(vl),2),'heldoutCandidate':vh}})
            print(f"  V43 q={q:.3f} strict={sel['strictSupportCount']}/3 soft={sel['softSupportCount']}/3 pass={passed}; V28 pass={vp}",flush=True)
        schemes.append({'phase':float(phase),'passes':pp,'v28Passes':pv,'folds':prows}); total+=pp; v28total+=pv; folds_total+=len(prows)
    minp=min(s['passes'] for s in schemes); promising=total>v28total and minp>=4 and regressions<=rescues; after=sha256(cp)
    if before!=after: raise RuntimeError('protected candidate changed')
    out={'schemaVersion':43,'profileType':'v42-strict-or-two-soft-broaden','anchorQ':ANCHOR_Q,'broadQ':BROAD_Q,'foldsPassed':total,'foldsTotal':folds_total,'minimumPhasePasses':minp,'v28ComparisonPasses':v28total,'rescuesVsV28':rescues,'regressionsVsV28':regressions,'foldsBroadenedAboveV28Q':broadened,'exploratoryPromising':promising,'reservedUntouchedPhasesConsumed':False,'outerHeldoutLabelsUsedToChooseCalibrationParameters':False,'validatedNewChampion':False,'schemes':schemes,'protected949CandidateHashUnchanged':before==after,'productionPromotionAllowed':False}
    OUTPUT_PATH.write_text(json.dumps(out,indent=2)+'\n'); MANIFEST_PATH.write_text(json.dumps({k:out[k] for k in ['schemaVersion','foldsPassed','foldsTotal','minimumPhasePasses','v28ComparisonPasses','rescuesVsV28','regressionsVsV28','foldsBroadenedAboveV28Q','exploratoryPromising','reservedUntouchedPhasesConsumed','validatedNewChampion','protected949CandidateHashUnchanged','productionPromotionAllowed']},indent=2)+'\n')
    print('GOMYWAY 36.76 RHYTHM24 V42 STRICT-OR-TWO-SOFT BROADEN V43 COMPLETE'); print('V43 folds passed:',total,'/',folds_total); print('Minimum V43 phase passes:',minp,'/ 5'); print('V28 comparison passes:',v28total,'/',folds_total); print('Rescues vs V28:',rescues); print('Regressions vs V28:',regressions); print('Folds broadened above V28 q:',broadened); print('Exploratory promising:',promising); print('Reserved untouched phases consumed: False'); print('Protected 949-event candidate hash unchanged:',before==after); print('Production promotion allowed: False'); print('Output:',OUTPUT_PATH.relative_to(ROOT)); print('Manifest:',MANIFEST_PATH.relative_to(ROOT))
if __name__=='__main__': main()
