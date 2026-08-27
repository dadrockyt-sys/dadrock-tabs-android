#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT=Path(__file__).resolve().parents[2]
HOLDOUT=ROOT/'validation/rhythm_holdout'
for e in (ROOT,HOLDOUT):
    if str(e) not in sys.path: sys.path.insert(0,str(e))
import score_rhythm_holdout as scorer  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import materialize_accepted_family  # noqa: E402

PREREG=ROOT/'debug/v153-reference-free-strength/phase-e-measure35-temporal-map-preregistration.json'
PHASED=ROOT/'debug/v153-reference-free-strength/phase-d-event347-attribution.json'
CAND=ROOT/'debug/v153-reference-free-strength/candidate/candidate.json'
GOLD=ROOT/'debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json'
V5=ROOT/'debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json'
E={
 'preregBlob':'57eca109b51bc3f5c0685c3771d92b369a6d1c80','phaseDBlob':'46d934ee48e125ec91b6fd5a070b081477f34472',
 'candidateBlob':'975ab36c234b423d1b56e59588e960f7d9d7103f','candidateSha':'df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b',
 'acceptedSha':'4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881','goldSha':'18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac',
 'coreBlob':'cc4bf61a99f22bf87a6c255e5a81220fbc82223b','canonicalBlob':'088d44827fb23e20d9aeeb4944a672989af5846c','supportBlob':'f4278ffaacaca3f66baf7a3112e2af0f3bc387cf'}

def load(p:Path)->Any:return json.loads(p.read_text())
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p:Path)->str:return subprocess.check_output(['git','hash-object',str(p.relative_to(ROOT))],cwd=ROOT,text=True).strip()
def req(p:Path,x:str):
    a=blob(p)
    if a!=x: raise RuntimeError(f'blob mismatch {p}: {a} != {x}')

def nearest(ref:Sequence[Mapping[str,Any]], measure:int, step:int, midi:int):
    rows=[r for r in ref if int(r['measure'])==measure and int(r['midi'])==midi]
    if not rows:return {'exists':False,'distanceSteps':None,'notes':[],'timingClass':'ABSENT_FROM_GOLD_MEASURE'}
    d=min(abs(int(r['step'])-step) for r in rows)
    cls='TOLERANT_LOCAL' if d<=scorer.STEP_TOLERANCE else ('GROSS_LOCAL' if d<=scorer.GROSS_STEP_TOLERANCE else 'MEASURE_LEVEL_ONLY')
    return {'exists':True,'distanceSteps':d,'notes':[dict(r) for r in rows],'timingClass':cls}

def pairs_in_measure(pairs, gen_rows, ref_rows, measure=35):
    out=[]
    for gi,ri in pairs:
        if int(gen_rows[gi]['measure'])==measure or int(ref_rows[ri]['measure'])==measure:
            out.append({'generatedIndex':gi,'generated':dict(gen_rows[gi]),'referenceIndex':ri,'reference':dict(ref_rows[ri]),'stepDelta':abs(float(gen_rows[gi]['step'])-float(ref_rows[ri]['step']))})
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True,type=Path); args=ap.parse_args(); out=args.output if args.output.is_absolute() else ROOT/args.output
    if out.exists(): raise RuntimeError('output exists')
    for p,x in ((PREREG,E['preregBlob']),(PHASED,E['phaseDBlob']),(CAND,E['candidateBlob']),(ROOT/'validation/rhythm_holdout/score_rhythm_holdout.py',E['coreBlob']),(ROOT/'validation/rhythm_holdout/canonical.py',E['canonicalBlob']),(ROOT/'modal/v147_phase_c_artifact_support.py',E['supportBlob'])): req(p,x)
    if sha(GOLD)!=E['goldSha']: raise RuntimeError('gold SHA mismatch')
    accepted=canonical_events(materialize_accepted_family(load(V5))); cand=canonical_events(load(CAND).get('renderEvents') or [])
    if sha256_json(accepted)!=E['acceptedSha'] or sha256_json(cand)!=E['candidateSha']: raise RuntimeError('event SHA mismatch')
    changed=[int(a['eventIndex']) for a,b in zip(accepted,cand) if dict(a)!=dict(b)]
    if changed!=[347]: raise RuntimeError('changed set mismatch')
    ref=scorer.validate_reference(load(GOLD)); an,_=scorer.flatten_generated(accepted); cn,_=scorer.flatten_generated(cand); rn,_,_=scorer.flatten_reference(ref)
    am=[{**dict(n),'eventIndex':int(accepted[i]['eventIndex'])} for i,n in enumerate(an) if int(n['measure'])==35]
    cm=[{**dict(n),'eventIndex':int(cand[i]['eventIndex'])} for i,n in enumerate(cn) if int(n['measure'])==35]
    rm=[dict(n) for n in rn if int(n['measure'])==35]
    am.sort(key=lambda x:(x['step'],x['midi'],x['eventIndex'])); cm.sort(key=lambda x:(x['step'],x['midi'],x['eventIndex'])); rm.sort(key=lambda x:(x['step'],x['midi'],x['stringIndex']))
    pos=next(i for i,r in enumerate(accepted) if int(r['eventIndex'])==347); a347=accepted[pos]; c347=cand[pos]
    pa=scorer.greedy_match(an,rn,lambda g,r:g['midi']==r['midi'],scorer.STEP_TOLERANCE); pc=scorer.greedy_match(cn,rn,lambda g,r:g['midi']==r['midi'],scorer.STEP_TOLERANCE)
    ga=scorer.greedy_match(an,rn,lambda g,r:g['midi']==r['midi'],scorer.GROSS_STEP_TOLERANCE); gc=scorer.greedy_match(cn,rn,lambda g,r:g['midi']==r['midi'],scorer.GROSS_STEP_TOLERANCE)
    posa=scorer.greedy_match(an,rn,lambda g,r:g['midi']==r['midi'] and g['stringIndex']==r['stringIndex'] and g['fret']==r['fret'],scorer.STEP_TOLERANCE)
    posc=scorer.greedy_match(cn,rn,lambda g,r:g['midi']==r['midi'] and g['stringIndex']==r['stringIndex'] and g['fret']==r['fret'],scorer.STEP_TOLERANCE)
    def gen_map(rows, canonical):
        out=[]
        for i,n in enumerate(rows):
            if int(n['measure'])!=35: continue
            near=nearest(rn,35,int(n['step']),int(n['midi']))
            out.append({'eventIndex':int(canonical[i]['eventIndex']),'step':int(n['step']),'midi':int(n['midi']),'stringIndex':int(n['stringIndex']),'fret':int(n['fret']),'nearestSameMidiGold':near})
        return out
    na=nearest(rn,35,int(a347['step']),int(a347['midi'])); nc=nearest(rn,35,int(c347['step']),int(c347['midi']))
    accepted_timing=any(gi==pos for gi,_ in ga); candidate_timing=any(gi==pos for gi,_ in gc)
    classification='MEASURE_LEVEL_ONLY_CREDIT_NO_LOCAL_TIMING_SUPPORT' if na['timingClass']=='MEASURE_LEVEL_ONLY' and not accepted_timing and not candidate_timing else 'AMBIGUOUS'
    result={'schema':'dadrock.tabs.v153.phase-e-measure35-temporal-map.v1','classification':'cpu-reference-facing-measure-temporal-diagnostic','gate':'GO_MAPPED','measure':35,
      'event347':{'accepted':dict(a347),'candidate':dict(c347),'acceptedNearestSameMidiGold':na,'candidateNearestSameMidiGold':nc,'acceptedGrossMatched':accepted_timing,'candidateGrossMatched':candidate_timing,'pitchContentCreditClassification':classification},
      'acceptedGeneratedMeasure35':am,'candidateGeneratedMeasure35':cm,'goldMeasure35':rm,
      'acceptedGeneratedNearestSameMidiGold':gen_map(an,accepted),'candidateGeneratedNearestSameMidiGold':gen_map(cn,cand),
      'matchPairsMeasure35':{'acceptedTolerantPitch':pairs_in_measure(pa,an,rn),'candidateTolerantPitch':pairs_in_measure(pc,cn,rn),'acceptedTolerantPosition':pairs_in_measure(posa,an,rn),'candidateTolerantPosition':pairs_in_measure(posc,cn,rn),'acceptedGrossPitch':pairs_in_measure(ga,an,rn),'candidateGrossPitch':pairs_in_measure(gc,cn,rn)},
      'goldMidi62':[dict(n) for n in rn if int(n['measure'])==35 and int(n['midi'])==62],'goldMidi61':[dict(n) for n in rn if int(n['measure'])==35 and int(n['midi'])==61],
      'interpretation':{'measureLevelPitchContentShouldBeDiagnosticOnlyForThisEvent':classification=='MEASURE_LEVEL_ONLY_CREDIT_NO_LOCAL_TIMING_SUPPORT','reason':'The accepted D4 receives measure-level pitch-content credit from a Gold D4 outside gross timing tolerance; neither accepted nor selected event 347 is locally timing-matched.'},
      'safety':{'scoreWrapperInvoked':False,'scoreCallCount':0,'candidateModified':False,'candidateConstructed':False,'candidateVariantsConstructed':0,'candidateSearchRun':False,'thresholdWeightFilterRuleTuning':False,'audioReadOrDecoded':False,'hpssOrCqtRecomputed':False,'modalL4CudaGpuUsed':False,'mainOrProductionModified':False,'automaticPromotion':False}}
    if len(result['goldMidi62'])!=1 or len(result['goldMidi61'])!=0: raise RuntimeError('Gold midi count cross-check failed')
    if classification!='MEASURE_LEVEL_ONLY_CREDIT_NO_LOCAL_TIMING_SUPPORT': raise RuntimeError(f'unexpected classification {classification}')
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'gate':result['gate'],'goldMidi62Step':int(result['goldMidi62'][0]['step']),'event347Step':9,'acceptedNearestDistance':na['distanceSteps'],'candidateNearestDistance':nc['distanceSteps'],'classification':classification,'scoreCallCount':0,'modalL4CudaGpuUsed':False},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
