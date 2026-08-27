#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, platform, subprocess, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
for entry in (ROOT/'validation/v144_rhythm_calibration', ROOT/'validation/rhythm_holdout'):
    if str(entry) not in sys.path: sys.path.insert(0,str(entry))
import score_selected_conjunction_candidate as historical_wrapper  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402

E={
 'candidate':'debug/v152-active-recurrence/candidate/candidate.json','candidateBlob':'8486188bc7c2f5d0d7649e98b0970b64dd0eebed','candidateFileSha':'9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb','candidateEventSha':'5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6',
 'proof':'debug/v152-active-recurrence/candidate/construction-proof.json','proofBlob':'3530c931bee9ab5888f350cd30d793388ebb5eca','proofSha':'e30a7a43d77c28760d2e8cd9e2df6c5114ad05cfc4e40f2bf59af15721186127',
 'pdf':'debug/v152-active-recurrence/candidate/pdf-event-fidelity.json','pdfBlob':'d6d4e287d7165ba52e7c1f58cf046a3328af6b29','pdfSha':'82872d9a3e7cb5a56c4a85db12ac8805aed49c88876227a57f1161de85fa500c',
 'completion':'debug/v152-active-recurrence/phase-b-complete-sentinel.json','completionBlob':'c39828b7e829918106f43d14cdd1790a87c32934',
 'auth':'debug/v152-active-recurrence/phase-c-scoring-authorization.json','authBlob':'c6fdcd4e56f6c8a2129912508ae1dc444e303c2c',
 'prior':'debug/v151-positive-consensus/phase-c-score/score-result.json','priorBlob':'23c451cf570a82333940e7dcc7f08afa583f52af','priorSha':'3dadedfe887612be86518e3c7b8e8c96a58e3e5ed7d8c12fd68e026b1aaf5f68',
 'baseline':'debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json','baselineBlob':'acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68',
 'wrapper':'validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py','wrapperBlob':'1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb',
 'core':'validation/rhythm_holdout/score_rhythm_holdout.py','coreBlob':'cc4bf61a99f22bf87a6c255e5a81220fbc82223b',
 'adapter':'validation/rhythm_holdout/canonical.py','adapterBlob':'088d44827fb23e20d9aeeb4944a672989af5846c',
 'gold':'debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json'
}
METRICS=('pitchContentF1','pitchTimingTolerantF1','stringFretTimingTolerantF1','chordPitchSetTolerantF1','exactVoicingTolerantF1','measureCoverageRecall')
DISPLAY=('pitchContentF1','pitchTimingTolerantF1','stringFretTimingTolerantF1','chordPitchSetTolerantF1','measureCoverageRecall')

def h(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def load(p:str)->Any:return json.loads((ROOT/p).read_text(encoding='utf-8'))
def blob(p:str)->str:return subprocess.check_output(['git','hash-object',p],cwd=ROOT,text=True).strip()
def req(p:str,e:str)->None:
    a=blob(p)
    if a!=e: raise RuntimeError(f'blob mismatch {p}: {a} != {e}')
def vec(m):return [100.0*float(m[k]) for k in DISPLAY]+[100.0]

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True,type=Path); args=ap.parse_args(); out=args.output if args.output.is_absolute() else ROOT/args.output
    if out.exists(): raise RuntimeError('one-use output exists')
    for p,k in ((E['candidate'],E['candidateBlob']),(E['proof'],E['proofBlob']),(E['pdf'],E['pdfBlob']),(E['completion'],E['completionBlob']),(E['auth'],E['authBlob']),(E['prior'],E['priorBlob']),(E['baseline'],E['baselineBlob']),(E['wrapper'],E['wrapperBlob']),(E['core'],E['coreBlob']),(E['adapter'],E['adapterBlob'])): req(p,k)
    auth=load(E['auth']); a=auth.get('authorization') or {}
    if auth.get('classification')!='one-use-reference-facing-score-authorized' or a.get('received') is not True or a.get('scope')!='exactly-one-v152-three-note-active-recurrence-gold-calibration-score': raise RuntimeError('authorization mismatch')
    for k in ('candidateSearchAllowed','alternateCandidateAllowed','alternateClassCombinationAllowed','additionalFilterAllowed','alternateThresholdAllowed','retuningAllowed','audioRecomputeAllowed','modalGpuAllowed','productionPromotionAllowed'):
        if a.get(k) is not False: raise RuntimeError(f'forbidden flag changed {k}')
    comp=load(E['completion'])
    if comp.get('status')!='COMPLETE_SEALED_STOP_BEFORE_SCORING' or comp.get('scoreCallCount')!=0 or comp.get('referenceFacingScoringAuthorization') is not False: raise RuntimeError('completion mismatch')
    pb=(ROOT/E['proof']).read_bytes(); cb=(ROOT/E['candidate']).read_bytes(); pdfb=(ROOT/E['pdf']).read_bytes(); priorb=(ROOT/E['prior']).read_bytes()
    if h(pb)!=E['proofSha'] or h(cb)!=E['candidateFileSha'] or h(pdfb)!=E['pdfSha'] or h(priorb)!=E['priorSha']: raise RuntimeError('byte identity mismatch')
    proof=json.loads(pb); pdf=json.loads(pdfb); prior=json.loads(priorb); candidate=canonical_events(json.loads(cb).get('renderEvents') or [])
    if len(candidate)!=1144 or sha256_json(candidate)!=E['candidateEventSha'] or proof.get('gate')!='GO' or (proof.get('metrics') or {}).get('changedEventCountVersusAccepted')!=3 or pdf.get('pdfEventFidelity')!=1.0: raise RuntimeError('candidate structural identity mismatch')
    baseline=load(E['baseline']); accepted=baseline.get('fullGoldCalibration') or {}; bm=accepted.get('gatedMetrics') or {}; bc=int(accepted['criticalMismatchCount'])
    pm=(prior.get('score') or {}).get('gatedMetrics') or {}; pc=int((prior.get('score') or {})['criticalMismatchCount'])
    expected_gold=str((prior.get('reference') or {}).get('sha256') or '')
    if len(expected_gold)!=64 or any(c not in '0123456789abcdef' for c in expected_gold): raise RuntimeError('prior reference SHA invalid')
    # Authorized reference boundary.
    gb=(ROOT/E['gold']).read_bytes(); actual=h(gb)
    if actual!=expected_gold: raise RuntimeError(f'Gold SHA mismatch: {actual}')
    reference=historical_wrapper.scorer.validate_reference(json.loads(gb)); score=historical_wrapper.score_full_candidate(candidate,reference); cm=score['gatedMetrics']
    report={
      'schemaVersion':15250,'classification':'v152-three-note-active-recurrence-authorized-single-gold-calibration-score','evaluationRole':'full-gold-calibration-not-unseen-holdout','authorizationScope':'exactly-one-v152-three-note-active-recurrence-gold-calibration-score',
      'candidate':{'eventCount':1144,'canonicalEventSha256':E['candidateEventSha'],'fileSha256':E['candidateFileSha'],'changedEventsVersusAccepted':3,'changedOnsetsVersusAccepted':3,'polyphonicChangedEventsVersusAccepted':0,'pdfEventFidelity':1.0},
      'reference':{'role':'gold-calibration-reference-not-unseen-holdout','sha256':actual,'identitySource':'persisted-v151-score-result-reference-sha256'},
      'score':score,'acceptedBaseline':{'name':baseline.get('name'),'gatedMetrics':bm,'criticalMismatchCount':bc},'priorV151':{'gatedMetrics':pm,'criticalMismatchCount':pc},
      'comparison':{'candidateDisplayVectorPercent':vec(cm),'acceptedBaselineDisplayVectorPercent':vec(bm),'v151DisplayVectorPercent':vec(pm),'gatedMetricDeltasVsAcceptedBaseline':{k:float(cm[k])-float(bm[k]) for k in METRICS},'gatedMetricDeltasVsV151':{k:float(cm[k])-float(pm[k]) for k in METRICS},'criticalMismatchDeltaVsAcceptedBaseline':int(score['criticalMismatchCount'])-bc,'criticalMismatchDeltaVsV151':int(score['criticalMismatchCount'])-pc,'displayVectorOrder':['pitch-content','pitch-timing','string-fret-timing','chord-pitch-set','measure-coverage','pdf-event-fidelity']},
      'scoringChain':{'fullCalibrationWrapperGitBlob':E['wrapperBlob'],'coreScorerGitBlob':E['coreBlob'],'canonicalAdapterGitBlob':E['adapterBlob'],'historicalFunction':'score_selected_conjunction_candidate.score_full_candidate','scoreCallCount':1},
      'environment':{'python':platform.python_version(),'platform':platform.platform(),'gitHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()},
      'safety':{'candidateSearchRun':False,'alternateCandidateConstructed':False,'alternateClassCombinationTested':False,'additionalFilterTested':False,'alternateThresholdTested':False,'retuningRun':False,'audioRecomputed':False,'modalGpuUsed':False,'productionIntegrated':False,'automaticPromotionAllowed':False,'scoreCallCount':1}
    }
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'candidateDisplayVectorPercent':report['comparison']['candidateDisplayVectorPercent'],'acceptedBaselineDisplayVectorPercent':report['comparison']['acceptedBaselineDisplayVectorPercent'],'v151DisplayVectorPercent':report['comparison']['v151DisplayVectorPercent'],'criticalMismatchCount':score['criticalMismatchCount'],'criticalMismatchDeltaVsAcceptedBaseline':report['comparison']['criticalMismatchDeltaVsAcceptedBaseline'],'criticalMismatchDeltaVsV151':report['comparison']['criticalMismatchDeltaVsV151'],'scoreCallCount':1},indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
