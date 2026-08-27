#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
for entry in (ROOT, HOLDOUT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import (  # noqa: E402
    EXPECTED_ACCEPTED_EVENT_COUNT, EXPECTED_ACCEPTED_EVENT_SHA256, EXPECTED_MEASURE_COUNT,
    OPEN_MIDI_BY_STRING_INDEX, materialize_accepted_family, timing_and_metadata_violations,
)

V5_PATH = ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"
V151_PATH = ROOT / "debug/v151-positive-consensus/candidate/candidate.json"
ANALYSIS_PATH = ROOT / "debug/v152-active-recurrence/phase-a-analysis.json"
PREREG_PATH = ROOT / "debug/v152-active-recurrence/phase-b-preregistration.json"
AUTH_PATH = ROOT / "debug/v152-active-recurrence/phase-b-construction-authorization.json"
KEEP = [132, 347, 457]
EXPECTED = {
    "v151FileSha": "ac96ec4edc3e9b67c047e7e9012139bfa46d0d6d164ffa1443960f8fbcb19ae9",
    "v151EventSha": "e6c437f534dfb5523610797c67f8f69176be903456ef4940c3032567b949156b",
    "analysisFileSha": "d56fb557406a986b3026e698ded9aa1820b062f13ab82175e249abd421c7137c",
    "analysisBlob": "5f0eb3e1ade41d0c4ab2debac1b5e2ac1b958697",
    "preregBlob": "b16e730eb5e647a6d06f36e2a7e9902451a1cd76",
    "authBlob": "e8ff4dc4dca664a0ba76678bf7049769dd701d7e",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "renderContractBlob": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
}
MAX_FRET = 24


def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def load_json(p: Path) -> Any: return json.loads(p.read_text(encoding="utf-8"))
def write_json(p: Path, x: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(x, indent=2, sort_keys=True)+"\n", encoding="utf-8")
def git_blob(p: Path) -> str: return subprocess.check_output(["git","hash-object",str(p.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def verify() -> None:
    for p,e in {
        ANALYSIS_PATH: EXPECTED["analysisBlob"], PREREG_PATH: EXPECTED["preregBlob"], AUTH_PATH: EXPECTED["authBlob"],
        ROOT/"modal/v147_phase_c_artifact_support.py": EXPECTED["supportBlob"],
        ROOT/"validation/rhythm_holdout/canonical.py": EXPECTED["canonicalBlob"],
        ROOT/"lib/v143RenderContract.js": EXPECTED["renderContractBlob"],
    }.items():
        if git_blob(p) != e: raise RuntimeError(f"blob mismatch {p}")
    if sha256_bytes(ANALYSIS_PATH.read_bytes()) != EXPECTED["analysisFileSha"]: raise RuntimeError("analysis SHA mismatch")
    a=load_json(ANALYSIS_PATH)
    if sorted(int(x) for x in (a.get("eventIndicesByStrength") or {}).get("both-selected", [])) != KEEP: raise RuntimeError("both-selected set mismatch")
    auth=load_json(AUTH_PATH)
    if (auth.get("authorization") or {}).get("received") is not True or auth.get("referenceFacingScoringAuthorization") is not False: raise RuntimeError("auth mismatch")


def accepted() -> list[dict[str,Any]]:
    rows=canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(rows)!=EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows)!=EXPECTED_ACCEPTED_EVENT_SHA256: raise RuntimeError("accepted identity mismatch")
    if len({int(r['measure']) for r in rows})!=EXPECTED_MEASURE_COUNT: raise RuntimeError("accepted measure mismatch")
    return rows


def prior() -> list[dict[str,Any]]:
    b=V151_PATH.read_bytes()
    if sha256_bytes(b)!=EXPECTED["v151FileSha"]: raise RuntimeError("V151 file SHA mismatch")
    rows=canonical_events(json.loads(b).get("renderEvents") or [])
    if len(rows)!=EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows)!=EXPECTED["v151EventSha"]: raise RuntimeError("V151 event identity mismatch")
    return rows


def construct(base: Sequence[Mapping[str,Any]], src: Sequence[Mapping[str,Any]]) -> list[dict[str,Any]]:
    by={int(r['eventIndex']):r for r in src}; keep=set(KEEP)
    return canonical_events([copy.deepcopy(dict(by[int(r['eventIndex'])] if int(r['eventIndex']) in keep else r)) for r in base])


def validate(base, src, cand) -> dict[str,Any]:
    if timing_and_metadata_violations(base,cand): raise RuntimeError("timing/metadata violation")
    src_by={int(r['eventIndex']):r for r in src}; changed=[]; onsets=set(); pos=[]; proj=[]
    for b,a in zip(base,cand):
        idx=int(b['eventIndex'])
        if dict(b)!=dict(a): changed.append(idx); onsets.add((int(b['measure']),int(b['step'])))
        exp=src_by[idx] if idx in KEEP else b
        if dict(a)!=dict(exp): proj.append(idx)
        s,f,m=int(a['stringIndex']),int(a['fret']),int(a['midi'])
        if s not in OPEN_MIDI_BY_STRING_INDEX or not 0<=f<=MAX_FRET or OPEN_MIDI_BY_STRING_INDEX[s]+f!=m: pos.append(idx)
    if changed!=KEEP or len(onsets)!=3: raise RuntimeError(f"changed set mismatch {changed}")
    if pos or proj: raise RuntimeError(f"position/projection violation {pos[:3]} {proj[:3]}")
    return {"eventCount":len(cand),"generatedMeasureCount":len({int(r['measure']) for r in cand}),"changedEventCountVersusAccepted":3,"changedOnsetCountVersusAccepted":3,"polyphonicChangedEventsVersusAccepted":0,"retainedPercentOfV151Changes":25.0,"revertedFromV151":9,"timingMetadataInvariantViolations":0,"positionIdentityViolations":0,"v151ProjectionViolations":0,"changedEventIndices":changed}


def pdf_fidelity(cand, sha):
    with tempfile.TemporaryDirectory(prefix="v152-pdf-") as td:
        src=Path(td)/"c.json"; out=Path(td)/"p.json"; write_json(src,{"renderEvents":cand})
        script="""import fs from 'node:fs'; import { projectV143RenderEvents } from './lib/v143RenderContract.js'; const x=JSON.parse(fs.readFileSync(process.argv[1],'utf8')); fs.writeFileSync(process.argv[2],JSON.stringify({renderEvents:projectV143RenderEvents(x.renderEvents||[])}));"""
        subprocess.check_call(["node","--input-type=module","-e",script,str(src),str(out)],cwd=ROOT)
        projected=canonical_events(load_json(out).get("renderEvents") or [])
    psha=sha256_json(projected)
    if len(projected)!=len(cand) or psha!=sha: raise RuntimeError("PDF fidelity mismatch")
    return {"schema":"dadrock.tabs.v152.pdf-event-fidelity.v1","passed":True,"candidateEventCount":len(cand),"candidateEventSha256":sha,"pdfEventCount":len(projected),"pdfEventSha256":psha,"pdfEventFidelity":1.0,"referenceOpened":False,"rendererProjection":"lib/v143RenderContract.js::projectV143RenderEvents"}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True,type=Path); args=ap.parse_args(); od=args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    if od.exists(): raise RuntimeError("output exists")
    verify(); base=accepted(); src=prior(); cand=construct(base,src); metrics=validate(base,src,cand); sha=sha256_json(cand)
    replay=construct(base,src)
    if replay!=cand or sha256_json(replay)!=sha: raise RuntimeError("determinism mismatch")
    pdf=pdf_fidelity(cand,sha); od.mkdir(parents=True)
    write_json(od/"candidate.json",{"instrument":"rhythm","renderEvents":cand})
    proof={"schema":"dadrock.tabs.v152.active-recurrence-construction-proof.v1","classification":"reference-free-single-candidate-construction","gate":"GO","policy":"accepted-baseline-plus-v151-both-selected-active-recurrence-only","candidateEventSha256":sha,"deterministic":True,"deterministicReplayEventSha256":sha,"metrics":metrics,"bothSelectedEventIndices":KEEP,"pdfEventFidelity":1.0,"frozenInputs":{"phaseAAnalysisSha256":EXPECTED["analysisFileSha"],"analysisGitBlob":EXPECTED["analysisBlob"],"preregistrationGitBlob":EXPECTED["preregBlob"],"authorizationGitBlob":EXPECTED["authBlob"],"v151EventSha256":EXPECTED["v151EventSha"]},"safety":{"goldOrReferenceRead":False,"priorScoreResultRead":False,"scorerInvoked":False,"scoreCallCount":0,"candidateVariantsConstructed":1,"candidateSearchRun":False,"alternateClassCombinationTested":False,"additionalFilterTested":False,"thresholdSweep":False,"retuningRun":False,"audioReadOrDecoded":False,"hpssOrCqtRecomputed":False,"modalOrGpuUsed":False,"mainOrProductionModified":False,"automaticPromotion":False}}
    write_json(od/"construction-proof.json",proof); write_json(od/"pdf-event-fidelity.json",pdf)
    files={}
    for n in ("candidate.json","construction-proof.json","pdf-event-fidelity.json"):
        b=(od/n).read_bytes(); files[n]={"bytes":len(b),"sha256":sha256_bytes(b)}
    write_json(od/"preservation-manifest.json",{"schema":"dadrock.tabs.v152.active-recurrence-preservation.v1","candidateEventSha256":sha,"files":files,"referenceFacingScoringAuthorization":False})
    print(json.dumps({"gate":"GO","candidateEventSha256":sha,"changedEvents":3,"changedOnsets":3,"polyphonicChangedEvents":0,"pdfEventFidelity":1.0,"scoreCallCount":0},indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
