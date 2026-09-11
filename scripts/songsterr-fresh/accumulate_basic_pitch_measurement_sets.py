#!/usr/bin/env python3
"""Combine validated fresh Basic Pitch measurement sets; never make admission decisions."""
import argparse, copy, hashlib, itertools, json, math, sys
from collections import defaultdict
from pathlib import Path

CONTRACT='songsterr-fresh-basic-pitch-cross-run-measurement-history-v1'
SET_CONTRACT='songsterr-fresh-basic-pitch-cross-run-variation-measurement-set-v1'
HASH_FIELDS=('guitarStemSha256','canonicalEvidenceSha256','noteInferenceSha256','activationBundleSha256','activationMatrixSha256','frameTimesSha256')
MAX_FIELDS=('maxAbsoluteEventCountDifference','maxSemanticKeysWithCountMismatch','maxTotalUnmatchedEventCount','maxAbsoluteSourceStartSeconds','maxAbsoluteOnsetConfidence','maxAbsoluteDiagnosticModelEndSeconds')
FALSE_FIELDS=('thresholdsApplied','admissionDecisionMade','modelValidationComplete','mayAdvanceDelivery','durationAuthorityChanged','referenceTabUsed','professionalScorerUsed','legacyV143ScorerImported','preferredOutputSelected','exactHashesAreAdmissionCriteria','runtimeProvenanceIsAdmissionCriterion','observedMaximaAreAdmissionCriteria')

class HistoryError(RuntimeError): pass

def canonical(v):
    try: return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    except (TypeError,ValueError) as e: raise HistoryError('CANONICAL_JSON_FAILED') from e

def digest(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(v): return isinstance(v,str) and len(v)==64 and all(c in '0123456789abcdef' for c in v)
def req_sha(v,l):
    if not sha(v): raise HistoryError(f'{l}:SHA256_INVALID')
    return v
def req_bool(v,e,l):
    if v is not e: raise HistoryError(f'{l}:EXPECTED_{str(e).upper()}')
def req_int(v,l):
    if not isinstance(v,int) or isinstance(v,bool) or v<0: raise HistoryError(f'{l}:NONNEGATIVE_INTEGER_REQUIRED')
    return v
def req_num(v,l):
    if isinstance(v,bool): raise HistoryError(f'{l}:FINITE_NONNEGATIVE_REQUIRED')
    try: n=float(v)
    except (TypeError,ValueError) as e: raise HistoryError(f'{l}:FINITE_NONNEGATIVE_REQUIRED') from e
    if not math.isfinite(n) or n<0: raise HistoryError(f'{l}:FINITE_NONNEGATIVE_REQUIRED')
    return n
def req_str(v,l):
    if not isinstance(v,str) or not v.strip(): raise HistoryError(f'{l}:NONEMPTY_STRING_REQUIRED')
    return v

def groups(obs,field,id_key='label'):
    g=defaultdict(list)
    for o in obs:
        v=o.get(field)
        if v is not None: g[req_sha(v,f'{id_key}.{field}')].append(o[id_key])
    return [{'sha256':h,'count':len(ids),'observations':sorted(ids)} for h,ids in sorted(g.items())]

def validate_groups(summary,obs,label):
    reported=summary.get('exactOutcomeGroups')
    if not isinstance(reported,dict): raise HistoryError(f'{label}.exactOutcomeGroups:MISSING')
    for field in HASH_FIELDS:
        exp=groups(obs,field)
        got=reported.get(field)
        if not isinstance(got,list): raise HistoryError(f'{label}.exactOutcomeGroups.{field}:LIST_REQUIRED')
        norm=[]
        for i,x in enumerate(got):
            if not isinstance(x,dict): raise HistoryError(f'{label}.{field}[{i}]:OBJECT_REQUIRED')
            h=req_sha(x.get('sha256'),f'{label}.{field}[{i}].sha256'); c=req_int(x.get('count'),f'{label}.{field}[{i}].count'); ids=x.get('observations')
            if not isinstance(ids,list) or len(ids)!=c or len(set(ids))!=len(ids): raise HistoryError(f'{label}.{field}[{i}]:COUNT_OR_IDS_MISMATCH')
            norm.append({'sha256':h,'count':c,'observations':sorted(ids)})
        if sorted(norm,key=lambda x:x['sha256'])!=exp: raise HistoryError(f'{label}.exactOutcomeGroups.{field}:RECOMPUTE_MISMATCH')

def pair_maxima(summary,labels,label):
    pairs=summary.get('pairwiseMeasurements')
    expected=set(itertools.combinations(sorted(labels),2))
    if not isinstance(pairs,list) or len(pairs)!=len(expected): raise HistoryError(f'{label}:PAIRWISE_COUNT_MISMATCH')
    seen=set(); m={f:(0.0 if 'Seconds' in f or 'Confidence' in f else 0) for f in MAX_FIELDS}
    for i,p in enumerate(pairs):
        pair=p.get('pair') if isinstance(p,dict) else None
        if not isinstance(pair,list) or len(pair)!=2 or pair[0]==pair[1] or any(x not in labels for x in pair): raise HistoryError(f'{label}.pair[{i}]:INVALID')
        k=tuple(sorted(pair))
        if k in seen: raise HistoryError(f'{label}:DUPLICATE_PAIR')
        seen.add(k); inv=p.get('inventory',{}); var=p.get('pairedNumericalVariation',{})
        m['maxAbsoluteEventCountDifference']=max(m['maxAbsoluteEventCountDifference'],req_int(inv.get('absoluteEventCountDifference'),f'{label}.{k}.eventDiff'))
        m['maxSemanticKeysWithCountMismatch']=max(m['maxSemanticKeysWithCountMismatch'],req_int(inv.get('semanticKeysWithCountMismatch'),f'{label}.{k}.keyDiff'))
        m['maxTotalUnmatchedEventCount']=max(m['maxTotalUnmatchedEventCount'],req_int(inv.get('totalUnmatchedEventCount'),f'{label}.{k}.unmatched'))
        for out,src in [('maxAbsoluteSourceStartSeconds','sourceStartSeconds'),('maxAbsoluteOnsetConfidence','onsetConfidence'),('maxAbsoluteDiagnosticModelEndSeconds','diagnosticModelEndSeconds')]:
            s=var.get(src,{}); x=s.get('maxAbsolute')
            if x is None:
                if req_int(s.get('count'),f'{label}.{k}.{src}.count')!=0: raise HistoryError(f'{label}.{k}.{src}:NULL_MAX')
                x=0.0
            m[out]=max(m[out],req_num(x,f'{label}.{k}.{src}.max'))
    if seen!=expected: raise HistoryError(f'{label}:PAIR_SET_INCOMPLETE')
    return m

def validate_set(s,i):
    l=f'set[{i}]'
    if not isinstance(s,dict) or s.get('contract')!=SET_CONTRACT or s.get('version')!=1: raise HistoryError(f'{l}:CONTRACT_OR_VERSION_MISMATCH')
    for f in ('referenceBlind','measurementOnly','completePairSetVerified'): req_bool(s.get(f),True,f'{l}.{f}')
    b=s.get('policyBoundary')
    if not isinstance(b,dict) or b.get('status')!='MEASURED_INDEPENDENT_RUN_VARIATION': raise HistoryError(f'{l}.policyBoundary:INVALID')
    for f in FALSE_FIELDS: req_bool(b.get(f),False,f'{l}.policyBoundary.{f}')
    fixed=s.get('fixedContract')
    if not isinstance(fixed,dict) or not fixed: raise HistoryError(f'{l}.fixedContract:MISSING')
    canonical(fixed)
    obs=s.get('observations')
    if not isinstance(obs,list) or len(obs)<2 or req_int(s.get('observationCount'),f'{l}.observationCount')!=len(obs): raise HistoryError(f'{l}:OBSERVATION_COUNT_MISMATCH')
    labels=set(); clean=[]
    for j,o in enumerate(obs):
        ol=f'{l}.observations[{j}]'
        if not isinstance(o,dict): raise HistoryError(f'{ol}:OBJECT_REQUIRED')
        name=req_str(o.get('label'),f'{ol}.label')
        if name in labels: raise HistoryError(f'{l}:DUPLICATE_LABEL')
        labels.add(name); r=o.get('runtimeProvenance')
        if not isinstance(r,dict): raise HistoryError(f'{ol}.runtimeProvenance:MISSING')
        for f in ('python','platform','machine','runnerOS','runnerArch','imageOS','imageVersion','ffmpegVersion'): req_str(r.get(f),f'{ol}.runtimeProvenance.{f}')
        if r.get('cpuModel') is not None: req_str(r.get('cpuModel'),f'{ol}.runtimeProvenance.cpuModel')
        c={'label':name,'eventCount':req_int(o.get('eventCount'),f'{ol}.eventCount'),'runtimeProvenance':copy.deepcopy(r)}
        for f in HASH_FIELDS: c[f]=req_sha(o.get(f),f'{ol}.{f}') if o.get(f) is not None else None
        clean.append(c)
    pair_count=len(obs)*(len(obs)-1)//2
    if req_int(s.get('pairwiseComparisonCount'),f'{l}.pairwiseComparisonCount')!=pair_count: raise HistoryError(f'{l}:PAIRWISE_COUNT_MISMATCH')
    maxima=pair_maxima(s,labels,l); env=s.get('descriptiveVariationEnvelope')
    if not isinstance(env,dict): raise HistoryError(f'{l}.descriptiveVariationEnvelope:MISSING')
    req_bool(env.get('descriptiveOnly'),True,f'{l}.envelope.descriptiveOnly'); req_bool(env.get('mayDefineTolerance'),False,f'{l}.envelope.mayDefineTolerance')
    for f,x in maxima.items():
        got=req_int(env.get(f),f'{l}.envelope.{f}') if isinstance(x,int) else req_num(env.get(f),f'{l}.envelope.{f}')
        if got!=x: raise HistoryError(f'{l}.envelope.{f}:RECOMPUTE_MISMATCH')
    validate_groups(s,clean,l)
    return {'sha256':digest(s),'fixedContract':copy.deepcopy(fixed),'observationCount':len(clean),'pairwiseComparisonCount':pair_count,'observations':clean,'envelope':maxima}

def build_history(summaries):
    if len(summaries)<2: raise HistoryError('AT_LEAST_TWO_MEASUREMENT_SETS_REQUIRED')
    sets=[validate_set(s,i) for i,s in enumerate(summaries)]
    if len({s['sha256'] for s in sets})!=len(sets): raise HistoryError('DUPLICATE_MEASUREMENT_SET')
    fixed=sets[0]['fixedContract']
    if any(s['fixedContract']!=fixed for s in sets[1:]): raise HistoryError('FIXED_CONTRACT_MISMATCH_ACROSS_SETS')
    sets.sort(key=lambda s:s['sha256']); all_obs=[]
    for s in sets:
        for o in s['observations']:
            q=copy.deepcopy(o); q['measurementSetSha256']=s['sha256']; q['qualifiedObservationId']=f"{s['sha256'][:12]}/{o['label']}"; all_obs.append(q)
    exact={}
    for f in HASH_FIELDS:
        g=defaultdict(list)
        for o in all_obs: g[o[f]].append(o['qualifiedObservationId'])
        exact[f]=[{'sha256':h,'count':len(ids),'observations':sorted(ids)} for h,ids in sorted(g.items())]
    cpu=defaultdict(lambda:defaultdict(list))
    for o in all_obs: cpu[o['runtimeProvenance'].get('cpuModel') or '<unknown>'][o['canonicalEvidenceSha256']].append(o['qualifiedObservationId'])
    env={f:(0.0 if 'Seconds' in f or 'Confidence' in f else 0) for f in MAX_FIELDS}
    for s in sets:
        for f in MAX_FIELDS: env[f]=max(env[f],s['envelope'][f])
    return {'contract':CONTRACT,'version':1,'referenceBlind':True,'measurementOnly':True,'measurementSetCount':len(sets),'totalObservationCount':sum(s['observationCount'] for s in sets),'totalWithinSetPairwiseComparisonCount':sum(s['pairwiseComparisonCount'] for s in sets),'fixedContract':fixed,'measurementSets':[{'measurementSetSha256':s['sha256'],'observationCount':s['observationCount'],'pairwiseComparisonCount':s['pairwiseComparisonCount'],'descriptiveVariationEnvelope':s['envelope']} for s in sets],'exactOutcomeGroups':exact,'runtimeAssociations':{'cpuModelToCanonicalEvidence':[{'cpuModel':c,'diagnosticOnly':True,'isAdmissionCriterion':False,'outcomes':[{'canonicalEvidenceSha256':h,'count':len(ids),'observations':sorted(ids)} for h,ids in sorted(out.items())]} for c,out in sorted(cpu.items())],'diagnosticOnly':True,'maySelectPreferredOutput':False},'crossSetDescription':{'allSetEnvelopesExactlyEqual':len({canonical(s['envelope']) for s in sets})==1,'uniqueCanonicalEvidenceOutcomeCount':len(exact['canonicalEvidenceSha256']),'uniqueStemOutcomeCount':len(exact['guitarStemSha256'])},'descriptiveVariationEnvelopeAcrossSets':{**env,'descriptiveOnly':True,'mayDefineTolerance':False},'policyBoundary':{'status':'ACCUMULATED_MEASUREMENT_ONLY_HISTORY','thresholdsApplied':False,'admissionDecisionMade':False,'modelValidationComplete':False,'mayAdvanceDelivery':False,'durationAuthorityChanged':False,'referenceTabUsed':False,'professionalScorerUsed':False,'legacyV143ScorerImported':False,'preferredOutputSelected':False,'exactHashesAreAdmissionCriteria':False,'runtimeProvenanceIsAdmissionCriterion':False,'observedMaximaAreAdmissionCriteria':False,'historicalFrequencyIsAdmissionCriterion':False}}

def fake(seed): return hashlib.sha256(seed.encode()).hexdigest()
def test_set(seed='same',changed=False):
    def o(label,v,cpu): return {'label':label,'eventCount':4 if v=='y' else 3,**{f:fake(f+v) for f in HASH_FIELDS[:-1]},'frameTimesSha256':fake('frames'),'runtimeProvenance':{'python':'3.10','platform':'linux','machine':'x86_64','processor':None,'cpuModel':cpu,'runnerOS':'Linux','runnerArch':'X64','imageOS':'ubuntu24','imageVersion':'x','ffmpegVersion':'x'}}
    obs=[o('a','x','cpu-a'),o('b','y' if changed else 'x','cpu-b'),o('c','x','cpu-a')]
    def p(a,b,v): return {'pair':[a,b],'inventory':{'absoluteEventCountDifference':int(v),'semanticKeysWithCountMismatch':int(v),'totalUnmatchedEventCount':int(v)},'pairedNumericalVariation':{'sourceStartSeconds':{'count':3,'maxAbsolute':0.0},'onsetConfidence':{'count':3,'maxAbsolute':0.01 if v else 0.0},'diagnosticModelEndSeconds':{'count':3,'maxAbsolute':0.2 if v else 0.0}}}
    pairs=[p('a','b',changed),p('a','c',False),p('b','c',changed)]
    env={'maxAbsoluteEventCountDifference':int(changed),'maxSemanticKeysWithCountMismatch':int(changed),'maxTotalUnmatchedEventCount':int(changed),'maxAbsoluteSourceStartSeconds':0.0,'maxAbsoluteOnsetConfidence':0.01 if changed else 0.0,'maxAbsoluteDiagnosticModelEndSeconds':0.2 if changed else 0.0,'descriptiveOnly':True,'mayDefineTolerance':False}
    return {'contract':SET_CONTRACT,'version':1,'referenceBlind':True,'measurementOnly':True,'completePairSetVerified':True,'observationCount':3,'pairwiseComparisonCount':3,'fixedContract':{'fixture':'x','seed':seed},'observations':obs,'pairwiseMeasurements':pairs,'exactOutcomeGroups':{f:groups(obs,f) for f in HASH_FIELDS},'descriptiveVariationEnvelope':env,'policyBoundary':{'status':'MEASURED_INDEPENDENT_RUN_VARIATION',**{f:False for f in FALSE_FIELDS}}}
def raises(fragment,fn):
    try: fn()
    except HistoryError as e:
        assert fragment in str(e),(fragment,str(e)); return
    raise AssertionError(fragment)
def self_test():
    a=test_set(changed=False); b=test_set(changed=True); h=build_history([a,b]); assert canonical(h)==canonical(build_history([b,a])); assert h['totalObservationCount']==6 and h['crossSetDescription']['uniqueCanonicalEvidenceOutcomeCount']==2; assert h['policyBoundary']['historicalFrequencyIsAdmissionCriterion'] is False
    raises('DUPLICATE_MEASUREMENT_SET',lambda:build_history([a,copy.deepcopy(a)])); raises('FIXED_CONTRACT_MISMATCH',lambda:build_history([a,test_set(seed='other',changed=True)])); x=copy.deepcopy(b); x['policyBoundary']['modelValidationComplete']=True; raises('modelValidationComplete',lambda:build_history([a,x])); x=copy.deepcopy(b); x['descriptiveVariationEnvelope']['maxAbsoluteOnsetConfidence']=0.009; raises('RECOMPUTE_MISMATCH',lambda:build_history([a,x])); x=copy.deepcopy(b); x['exactOutcomeGroups']['canonicalEvidenceSha256'][0]['count']+=1; raises('COUNT_OR_IDS_MISMATCH',lambda:build_history([a,x])); print(json.dumps({'contract':CONTRACT,'ok':True,'tests':['set-order-invariance','duplicate-set-rejected','fixed-contract-drift-fails-closed','promotional-boundary-fails-closed','envelope-recomputed','hash-groups-recomputed','complete-pair-set-required','no-preferred-output-or-historical-frequency-admission']},sort_keys=True))
def main():
    p=argparse.ArgumentParser(); p.add_argument('measurement_sets',nargs='*'); p.add_argument('--output'); p.add_argument('--self-test',action='store_true'); a=p.parse_args()
    if a.self_test: self_test(); return
    if len(a.measurement_sets)<2: raise HistoryError('AT_LEAST_TWO_MEASUREMENT_SETS_REQUIRED')
    s=[]
    for path in a.measurement_sets:
        try:
            with open(path,encoding='utf-8') as f: s.append(json.load(f,parse_constant=lambda x:(_ for _ in ()).throw(HistoryError(f'NONSTANDARD_JSON_CONSTANT:{x}'))))
        except HistoryError: raise
        except Exception as e: raise HistoryError(f'JSON_LOAD_FAILED:{path}') from e
    out=json.dumps(build_history(s),indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n'
    if a.output: Path(a.output).write_text(out,encoding='utf-8')
    else: sys.stdout.write(out)
if __name__=='__main__':
    try: main()
    except HistoryError as e: print(f'MEASUREMENT_HISTORY_ERROR:{e}',file=sys.stderr); raise SystemExit(2)
