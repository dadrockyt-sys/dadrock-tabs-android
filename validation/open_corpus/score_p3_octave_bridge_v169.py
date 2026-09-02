#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
from statistics import mean
import pretty_midi

TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def refs(path: Path):
    pm=pretty_midi.PrettyMIDI(str(path)); out=[]
    for inst in pm.instruments:
        if inst.is_drum: continue
        out += [{"pitch":int(n.pitch),"start":float(n.start)} for n in inst.notes]
    return sorted(out,key=lambda r:(r['pitch'],r['start']))

def matches(pred, ref, tol):
    p=defaultdict(list); r=defaultdict(list)
    for x in pred: p[int(x['pitch'])].append(float(x['start']))
    for x in ref: r[int(x['pitch'])].append(float(x['start']))
    total=0
    for pitch in sorted(set(p)|set(r)):
        a=sorted(p[pitch]); b=sorted(r[pitch]); i=j=0
        while i<len(a) and j<len(b):
            d=a[i]-b[j]
            if abs(d)<=tol: total+=1; i+=1; j+=1
            elif d < -tol: i+=1
            else: j+=1
    return total

def metric(tp,pred,ref):
    pr=tp/pred if pred else (1.0 if ref==0 else 0.0)
    rc=tp/ref if ref else (1.0 if pred==0 else 0.0)
    f=2*pr*rc/(pr+rc) if pr+rc else 0.0
    return {"tp":tp,"pred":pred,"ref":ref,"precisionPct":100*pr,"recallPct":100*rc,"f1Pct":100*f}

def score(events, ref, tol): return metric(matches(events,ref,tol),len(events),len(ref))

def verify(root: Path):
    mpath=root/'candidate-freeze-manifest.json'; m=json.loads(mpath.read_text())
    if m.get('candidateFileCount')!=24: raise RuntimeError('candidateFileCount != 24')
    expected={f'{c}-{i:02d}.json' for c in ('directInput','micAmp') for i in range(1,13)}
    if {x['file'] for x in m['files']} != expected: raise RuntimeError('candidate file set mismatch')
    payloads=[]
    for x in m['files']:
        path=root/x['file']
        if sha(path)!=x['sha256']: raise RuntimeError(f'hash mismatch {path.name}')
        p=json.loads(path.read_text())
        if p.get('referenceRead') is not False: raise RuntimeError('candidate referenceRead guard')
        if len(p['baselineEvents'])!=len(p['correctedEvents']): raise RuntimeError('event count mismatch')
        payloads.append(p)
    return m,payloads

def micro(rows, section, stream):
    return metric(sum(x[section][stream]['tp'] for x in rows),sum(x[section][stream]['pred'] for x in rows),sum(x[section][stream]['ref'] for x in rows))

def evaluate(croot: Path, rroot: Path):
    manifest,payloads=verify(croot); rows=[]
    for p in sorted(payloads,key=lambda x:(x['capture'],x['workIndex'])):
        ref=refs(rroot/f"midi_{p['workIndex']}.mid")
        row={"capture":p['capture'],"workIndex":p['workIndex'],"changedPitchCount":p['changedPitchCount'],"baselineEventCount":len(p['baselineEvents']),"correctedEventCount":len(p['correctedEvents']),"referenceNoteCount":len(ref)}
        for name,tol in TOLS.items():
            row[name]={"baseline":score(p['baselineEvents'],ref,tol),"corrected":score(p['correctedEvents'],ref,tol)}
        rows.append(row)
    ident=all(x['baselineEventCount']==x['correctedEventCount'] for x in rows)
    agg={}
    for section in TOLS:
        b=micro(rows,section,'baseline'); c=micro(rows,section,'corrected')
        cap={}
        for capture in ('directInput','micAmp'):
            z=[x for x in rows if x['capture']==capture]
            bm=micro(z,section,'baseline'); cm=micro(z,section,'corrected')
            cap[capture]={"baselineMicro":bm,"correctedMicro":cm,"deltaMicroF1PP":cm['f1Pct']-bm['f1Pct'],"baselineMacroF1Pct":mean(x[section]['baseline']['f1Pct'] for x in z),"correctedMacroF1Pct":mean(x[section]['corrected']['f1Pct'] for x in z)}
        bm=mean(x[section]['baseline']['f1Pct'] for x in rows); cm=mean(x[section]['corrected']['f1Pct'] for x in rows)
        agg[section]={"baselineMicro":b,"correctedMicro":c,"deltaMicroF1PP":c['f1Pct']-b['f1Pct'],"baselineCombinedMacroF1Pct":bm,"correctedCombinedMacroF1Pct":cm,"deltaCombinedMacroF1PP":cm-bm,"captures":cap}
    pri=agg['primary100ms']; strict=agg['strict50ms']
    passc={"combinedMacroGainAtLeast0_25PP":pri['deltaCombinedMacroF1PP']>=0.25,"directInputMicroNotLower":pri['captures']['directInput']['deltaMicroF1PP']>=0,"micAmpMicroNotLower":pri['captures']['micAmp']['deltaMicroF1PP']>=0,"strict50msCombinedMicroNotLower":strict['deltaMicroF1PP']>=0,"eventCountIdentity":ident}
    failc={"combinedMacroLossGreaterThan0_25PP":pri['deltaCombinedMacroF1PP'] < -0.25,"directInputMicroLossGreaterThan0_10PP":pri['captures']['directInput']['deltaMicroF1PP'] < -0.10,"micAmpMicroLossGreaterThan0_10PP":pri['captures']['micAmp']['deltaMicroF1PP'] < -0.10,"strict50msCombinedMicroLossGreaterThan0_10PP":strict['deltaMicroF1PP'] < -0.10,"eventCountIdentityFailed":not ident}
    status='REFERENCE_BLIND_OCTAVE_CORRECTION_PASS' if all(passc.values()) else ('REFERENCE_BLIND_OCTAVE_CORRECTION_FAIL' if any(failc.values()) else 'INCONCLUSIVE_NO_MATERIAL_GAIN')
    return {"schema":"dadrock.tabs.open-corpus.p3-reference-blind-octave-score.v1","status":status,"candidateFreezeManifestSha256":sha(croot/'candidate-freeze-manifest.json'),"candidateFileCount":manifest['candidateFileCount'],"totalChangedPitchCount":manifest['totalChangedPitchCount'],"totalBoundaryUnscoredCount":manifest['totalBoundaryUnscoredCount'],"eventCountIdentity":ident,**agg,"passConditions":passc,"failConditions":failc,"units":rows,"candidateRegeneratedByScorer":False,"audioReadByScorer":False,"referenceReadByScorer":True,"v168ReferenceFacingScoreCalls":0,"v168PoliciesModified":False,"goatHoldoutSelectionModified":False}

def selftest():
    p=[{"pitch":60,"start":.04},{"pitch":60,"start":1.08},{"pitch":61,"start":2.0}]; r=[{"pitch":60,"start":0.0},{"pitch":60,"start":1.0},{"pitch":61,"start":2.2}]
    if matches(p,r,.10)!=2 or matches(p,r,.05)!=1: raise RuntimeError('matcher self-test failed')
    return {"status":"P3_SCORER_SELF_TEST_PASS","audioRead":False,"candidateRegenerated":False,"v168ReferenceFacingScoreCalls":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate-dir',type=Path); ap.add_argument('--reference-dir',type=Path); ap.add_argument('--output',type=Path); ap.add_argument('--self-test',action='store_true'); a=ap.parse_args()
    if a.self_test: print(json.dumps(selftest(),indent=2,sort_keys=True)); return 0
    if not all((a.candidate_dir,a.reference_dir,a.output)): raise SystemExit('required inputs missing')
    out=evaluate(a.candidate_dir,a.reference_dir); a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out,indent=2,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
