from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
ROOT=Path(__file__).resolve().parents[1]; PUBLIC=ROOT/'public'
SOURCE_PATH=PUBLIC/'gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json'
V57_PATH=PUBLIC/'gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json'
OUTPUT_PATH=PUBLIC/'gomyway-3676-patch-rhythm24-v74-v57-phase-leave-one-out-global-v75.json'
MANIFEST_PATH=PUBLIC/'gomyway-3676-patch-rhythm24-v74-v57-phase-leave-one-out-global-v75-manifest.json'
EXPECTED=(272,595,341); OUTER_FOLDS=5; Q=float(v28.FROZEN_Q)
NAMES=['p2-sin','p2-cos','p4-sin','p4-cos']
def sha256(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 c=v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH; before=sha256(c)
 p=json.loads(SOURCE_PATH.read_text()); rows=list(p.get('candidateSlots') or [])
 if not rows or tuple(p.get('frozenChampionMatchedMissingExtra') or [])!=EXPECTED: raise RuntimeError('bad source')
 v57=json.loads(V57_PATH.read_text()); bn=sorted((rows[0].get('features') or {}).keys())
 xb=np.asarray([[float((r.get('features') or {}).get(f,0.0)) for f in bn] for r in rows],dtype=float)
 pf=v17.phase_features(rows); y=np.asarray([str(r.get('label'))=='true' for r in rows],dtype=bool); m=np.asarray([int(r['measure']) for r in rows],dtype=np.int32)
 lo,hi=int(m.min()),int(m.max()); variants={}
 for d in range(4):
  keep=[i for i in range(4) if i!=d]; variants[d]={'x':np.concatenate([xb,pf[:,keep]],axis=1),'passes':0,'rescues':0,'regressions':0,'ph':{}}
 full=0
 for s in v57.get('schemes') or []:
  phase=float(s['phase']); ids=np.asarray([v18.phased_fold(int(mm),lo,hi,OUTER_FOLDS,phase) for mm in m],dtype=np.int16); sf={int(r['fold']):r for r in s.get('folds') or []}; pc={d:0 for d in variants}
  for fold in range(OUTER_FOLDS):
   z=sf[fold]; cm=z.get('chosenModel') or {}; rad=int(cm['pairRadius']); lam=float(cm['lambda']); test=ids==fold; train=~test; fp=bool((z.get('v28Comparison') or {}).get('passed')); full+=int(fp)
   print(f'phase={phase} fold={fold} V75 leave-one-out',flush=True)
   for d,r in variants.items():
    model=v2.fit_pairwise_ranker(r['x'][train],y[train],m[train],rad,lam); scores=v2.scores_for(r['x'][test],model); held=v1.select_top_fraction(scores,y[test],Q); base=v1.base_stats(y[test]); passed=bool(held['true']>0 and float(held['precision'])-float(base['precision'])>=5.0)
    r['passes']+=int(passed); pc[d]+=int(passed); r['rescues']+=int(passed and not fp); r['regressions']+=int(fp and not passed)
  for d,n in pc.items(): variants[d]['ph'][str(phase)]=n
 sums=[]
 for d,r in variants.items():
  vals=list(r['ph'].values()); mn=min(vals); sums.append({'dropIndex':d,'droppedFeature':NAMES[d],'passes':r['passes'],'rescues':r['rescues'],'regressions':r['regressions'],'minimumPhasePasses':mn,'bottleneckPhases':[float(k) for k,v in r['ph'].items() if v==mn]})
 sums.sort(key=lambda x:(-x['minimumPhasePasses'],-x['passes'],x['regressions']))
 after=sha256(c)
 out={'schemaVersion':75,'fullPhaseAnchorPasses':full,'rankedVariants':sums,'diagnosticOutcomesTaintedForSelection':True,'newReserved1over128OddNumeratorPhasesReferenced':False,'newTuningPerformed':False,'validatedNewChampion':False,'protected949CandidateHashUnchanged':before==after,'productionPromotionAllowed':False}
 OUTPUT_PATH.write_text(json.dumps(out,indent=2)+'\n'); MANIFEST_PATH.write_text(json.dumps(out,indent=2)+'\n')
 print('GOMYWAY V75 PHASE LEAVE-ONE-OUT GLOBAL COMPLETE'); print('Full-phase anchor passes:',full,'/ 160')
 for x in sums: print(x)
 print('New reserved 1/128 odd-numerator phases referenced: False'); print('Protected 949-event candidate hash unchanged:',before==after); print('Production promotion allowed: False')
if __name__=='__main__': main()
