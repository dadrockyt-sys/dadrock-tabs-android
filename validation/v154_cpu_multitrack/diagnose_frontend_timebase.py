#!/usr/bin/env python3
"""Post-score diagnostic of V154 grid-origin vs tempo-drift failure.

Reads only the permanently consumed V154 candidate and frozen private reference.
Does NOT import/call the official scorer and never writes a candidate.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json"
REF = ROOT / "research/v154-professional-references/scorer-ready/frontend-reference-payload.json"
SCORE = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json"
ARCH = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json"
OUT = ROOT / "debug/v154-cpu-autonomous/v154-frontend-reference-score/timebase-diagnostic.json"
EXPECTED = {
    GEN: "1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37",
    REF: "b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7",
    SCORE: "c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b",
    ARCH: "bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd",
}
TEMPO = 129.19921875
SECTIONS = [
    ("intro_riff", 1, 16),
    ("verse1", 17, 32),
    ("chorus1", 33, 38),
    ("riff_return1", 39, 46),
    ("verse2", 47, 62),
    ("chorus2", 63, 69),
    ("bridge", 70, 77),
    ("solo", 78, 94),
    ("outro", 95, 113),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    actual = sha(path)
    if actual != EXPECTED[path]:
        raise RuntimeError(f"identity drift {path}: {actual}")
    return json.loads(path.read_text())


def abs_rows(raw):
    out=[]
    for n in raw:
        if bool(n.get("excludeFromScoring", False)):
            continue
        out.append({"t": (int(n["measure"])-1)*16.0 + float(n["step"]), "midi": int(n["midi"]), "measure": int(n["measure"])})
    return out


def match_sorted(gs, rs, tol=0.5):
    i=j=m=0
    while i<len(gs) and j<len(rs):
        if gs[i] < rs[j]-tol:
            i+=1
        elif rs[j] < gs[i]-tol:
            j+=1
        else:
            m+=1; i+=1; j+=1
    return m


def shifted_match_count(g, r, shift, tol=0.5):
    gg=defaultdict(list); rr=defaultdict(list)
    for n in g: gg[n["midi"]].append(n["t"]+shift)
    for n in r: rr[n["midi"]].append(n["t"])
    return sum(match_sorted(sorted(gg[k]), sorted(rr[k]), tol) for k in set(gg)&set(rr))


def scan(g, r, lo=-32.0, hi=8.0, inc=0.25):
    vals=[]
    count=int(round((hi-lo)/inc))+1
    for i in range(count):
        s=lo+i*inc
        m=shifted_match_count(g,r,s)
        vals.append((m,s))
    vals.sort(key=lambda x:(-x[0],abs(x[1]+13.25),abs(x[1]),x[1]))
    best_m,best_s=vals[0]
    return {"bestShiftSteps":best_s,"matched":best_m,"generated":len(g),"reference":len(r),"top":[{"shift":s,"matched":m} for m,s in vals[:8]]}


def section_scans(g, r):
    out=[]
    for name,mlo,mhi in SECTIONS:
        alo=(mlo-1)*16.0; ahi=mhi*16.0
        gg=[n for n in g if alo-16.0 <= n["t"] < ahi+16.0]
        rr=[n for n in r if alo-32.0 <= n["t"] < ahi+32.0]
        d=scan(gg,rr)
        d.update({"section":name,"measures":[mlo,mhi],"centerAbsoluteStep":(alo+ahi)/2})
        out.append(d)
    return out


def weighted_linear(points):
    pts=[p for p in points if p[2]>0]
    sw=sum(w for _,_,w in pts)
    sx=sum(x*w for x,_,w in pts); sy=sum(y*w for _,y,w in pts)
    sxx=sum(x*x*w for x,_,w in pts); sxy=sum(x*y*w for x,y,w in pts)
    den=sw*sxx-sx*sx
    if not pts or abs(den)<1e-12: return {"intercept":None,"slope":None}
    slope=(sw*sxy-sx*sy)/den
    intercept=(sy-slope*sx)/sw
    return {"intercept":intercept,"slope":slope}


def diagnose(label,g,r):
    secs=section_scans(g,r)
    pts=[(s["centerAbsoluteStep"],s["bestShiftSteps"],max(1,s["matched"])) for s in secs]
    fit=weighted_linear(pts)
    slope=fit["slope"]
    implied=None if slope is None else TEMPO*(1.0+slope)
    early=[s["bestShiftSteps"] for s in secs[:3]]
    late=[s["bestShiftSteps"] for s in secs[-3:]]
    return {
        "global":scan(g,r),
        "sections":secs,
        "weightedShiftVsAbsoluteStepFit":{**fit,"impliedReferenceTempoBpmIfPureTempoError":implied},
        "earlyMedianShiftSteps":median(early),
        "lateMedianShiftSteps":median(late),
        "lateMinusEarlyShiftSteps":median(late)-median(early),
    }


def main():
    if OUT.exists(): raise RuntimeError("write-once output already exists")
    gen=load(GEN); ref=load(REF); _=load(SCORE); __=load(ARCH)
    gg=abs_rows(gen["streams"]["combinedGuitar"])
    bg=abs_rows(gen["streams"]["bass"])
    gr=abs_rows(ref["parts"]["rhythm"]+ref["parts"]["lead"])
    br=abs_rows(ref["parts"]["bass"])
    guitar=diagnose("combinedGuitar",gg,gr)
    bass=diagnose("bass",bg,br)
    slopes=[x["weightedShiftVsAbsoluteStepFit"]["slope"] for x in (guitar,bass) if x["weightedShiftVsAbsoluteStepFit"]["slope"] is not None]
    finding=[]
    for label,d in (("combinedGuitar",guitar),("bass",bass)):
        finding.append(f"{label}: section shifts move from early median {d['earlyMedianShiftSteps']:+.2f} to late median {d['lateMedianShiftSteps']:+.2f} steps (delta {d['lateMinusEarlyShiftSteps']:+.2f}); a constant origin error alone is therefore insufficient." if abs(d['lateMinusEarlyShiftSteps'])>=1.0 else f"{label}: section shifts are roughly stationary; fixed origin dominates over tempo drift.")
        fit=d["weightedShiftVsAbsoluteStepFit"]
        finding.append(f"{label}: weighted shift-vs-time slope={fit['slope']:+.6f}, corresponding to {fit['impliedReferenceTempoBpmIfPureTempoError']:.3f} BPM if interpreted purely as tempo mismatch; treat this only as diagnosis, not a reference-tuned future parameter.")
    if len(slopes)==2 and abs(slopes[0]-slopes[1])<0.003:
        finding.append("Guitar and Bass show similar timebase slope, strengthening the diagnosis of a shared grid/timebase architecture error upstream of stream-specific pitch recognition.")
    report={
        "schema":"dadrock.tabs.v154.post-score-timebase-diagnostic.v1",
        "validation":"PASS",
        "frozenInputs":{str(p.relative_to(ROOT)):EXPECTED[p] for p in EXPECTED},
        "policy":{"diagnosticOnly":True,"officialScorerImportedOrCalled":False,"additionalOfficialReferenceFacingScoreCalls":0,"candidateModified":False,"candidateCorrectionWritten":False,"futureCandidateParameterTuningFromReferenceForbidden":True,"cpuOnly":True,"gpuUsed":False,"mainOrProductionModified":False},
        "historicalTranscriberTimebase":{"tempoBpm":TEMPO,"gridOrigin":"audio/stem timestamp 0.000 s","latencyCompensation":"none","downbeatOrMusicalOriginDetection":"none"},
        "combinedGuitar":guitar,"bass":bass,"findings":finding,
    }
    OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"validation":"PASS","output":str(OUT.relative_to(ROOT)),"sha256":sha(OUT),"findings":finding},indent=2))

if __name__=="__main__": main()
