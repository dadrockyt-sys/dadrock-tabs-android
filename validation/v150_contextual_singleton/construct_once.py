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
V149_PATH = ROOT / "debug/v149-singleton-confidence/candidate/candidate.json"
ANALYSIS_PATH = ROOT / "debug/v150-contextual-singleton/phase-a-analysis.json"
PREREG_PATH = ROOT / "debug/v150-contextual-singleton/phase-b-preregistration.json"
AUTH_PATH = ROOT / "debug/v150-contextual-singleton/phase-b-construction-authorization.json"
EXPECTED = {
    "v149FileSha": "1add3ffacf9048dd597a47820baeb3ef8cb0e67fa83d12b1b8d8303a8d808278",
    "v149EventSha": "4dd13556d580a315c728e7333823eec9644195da5a345689cc44a566ef33d998",
    "analysisFileSha": "f1e61d3f16d69aab3f6ac9fa5aabaa6ae12839be3061a8ec3521e94d1529b396",
    "analysisBlob": "67ad55d005415be2248a57238109a3d8745e4061",
    "preregBlob": "56f19421897cee8f4d991a982dfdadfaef94c19c",
    "authBlob": "fa7ce907c580bde9d6b109024724161cc31a43e2",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "renderContractBlob": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
    "changedEvents": 33,
    "revertedFromV149": 21,
}
MAX_FRET = 24


def sha256_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def load_json(p: Path) -> Any: return json.loads(p.read_text(encoding="utf-8"))
def write_json(p: Path, x: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(x, indent=2, sort_keys=True)+"\n", encoding="utf-8")
def git_blob(p: Path) -> str:
    return subprocess.check_output(["git","hash-object",str(p.relative_to(ROOT))],cwd=ROOT,text=True).strip()


def verify() -> None:
    for p, e in {
        PREREG_PATH: EXPECTED["preregBlob"], AUTH_PATH: EXPECTED["authBlob"], ANALYSIS_PATH: EXPECTED["analysisBlob"],
        ROOT/"modal/v147_phase_c_artifact_support.py": EXPECTED["supportBlob"],
        ROOT/"validation/rhythm_holdout/canonical.py": EXPECTED["canonicalBlob"],
        ROOT/"lib/v143RenderContract.js": EXPECTED["renderContractBlob"],
    }.items():
        a=git_blob(p)
        if a!=e: raise RuntimeError(f"blob mismatch {p}: {a} != {e}")
    if sha256_bytes(ANALYSIS_PATH.read_bytes()) != EXPECTED["analysisFileSha"]: raise RuntimeError("analysis SHA mismatch")
    auth=load_json(AUTH_PATH)
    if (auth.get("authorization") or {}).get("received") is not True or auth.get("referenceFacingScoringAuthorization") is not False:
        raise RuntimeError("construction authorization mismatch")


def accepted() -> list[dict[str,Any]]:
    rows=canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(rows)!=EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows)!=EXPECTED_ACCEPTED_EVENT_SHA256: raise RuntimeError("accepted identity mismatch")
    if len({int(r['measure']) for r in rows})!=EXPECTED_MEASURE_COUNT: raise RuntimeError("measure count mismatch")
    return rows


def v149() -> list[dict[str,Any]]:
    b=V149_PATH.read_bytes()
    if sha256_bytes(b)!=EXPECTED["v149FileSha"]: raise RuntimeError("V149 file SHA mismatch")
    rows=canonical_events(json.loads(b).get("renderEvents") or [])
    if len(rows)!=EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows)!=EXPECTED["v149EventSha"]: raise RuntimeError("V149 event identity mismatch")
    return rows


def selected_indices() -> tuple[list[int],list[int]]:
    a=load_json(ANALYSIS_PATH)
    if a.get("gate")!="GO" or (a.get("population") or {}).get("eventCount")!=54: raise RuntimeError("V150 analysis gate mismatch")
    rows=a.get("allRows") or []
    if len(rows)!=54: raise RuntimeError("V150 analysis rows mismatch")
    reverted=sorted(int(r["eventIndex"]) for r in rows if r["contextRelationship"]=="strict-both-sides-worse")
    kept=sorted(int(r["eventIndex"]) for r in rows if r["contextRelationship"]!="strict-both-sides-worse")
    if len(reverted)!=21 or len(kept)!=33: raise RuntimeError(f"context split mismatch kept={len(kept)} reverted={len(reverted)}")
    return kept,reverted


def construct(base: Sequence[Mapping[str,Any]], prior: Sequence[Mapping[str,Any]], keep: Sequence[int]) -> list[dict[str,Any]]:
    pby={int(r['eventIndex']):r for r in prior}; k=set(keep); out=[]
    for r in base:
        idx=int(r['eventIndex']); out.append(copy.deepcopy(dict(pby[idx] if idx in k else r)))
    return canonical_events(out)


def validate(base: Sequence[Mapping[str,Any]], cand: Sequence[Mapping[str,Any]], keep: Sequence[int]) -> dict[str,Any]:
    violations=timing_and_metadata_violations(base,cand)
    if violations: raise RuntimeError(f"timing violations {violations[:3]}")
    changed=[]; onsets=set(); pos_bad=[]
    for b,a in zip(base,cand):
        idx=int(b['eventIndex'])
        if dict(b)!=dict(a): changed.append(idx); onsets.add((int(b['measure']),int(b['step'])))
        s=int(a['stringIndex']); f=int(a['fret']); m=int(a['midi'])
        if s not in OPEN_MIDI_BY_STRING_INDEX or not 0<=f<=MAX_FRET or OPEN_MIDI_BY_STRING_INDEX[s]+f!=m: pos_bad.append(idx)
    if changed!=list(keep) or len(changed)!=33 or len(onsets)!=33: raise RuntimeError("changed set/count mismatch")
    if pos_bad: raise RuntimeError(f"position violations {pos_bad[:5]}")
    return {"eventCount":len(cand),"generatedMeasureCount":len({int(r['measure']) for r in cand}),"changedEventCountVersusAccepted":33,
            "changedOnsetCountVersusAccepted":33,"polyphonicChangedEventsVersusAccepted":0,"revertedFromV149":21,
            "retainedPercentOfV149Changes":100.0*33/54,"timingMetadataInvariantViolations":0,"positionIdentityViolations":0,"changedEventIndices":changed}


def pdf_fidelity(cand: Sequence[Mapping[str,Any]], sha: str) -> dict[str,Any]:
    with tempfile.TemporaryDirectory(prefix="v150-pdf-") as td:
        src=Path(td)/"c.json"; out=Path(td)/"p.json"; write_json(src,{"renderEvents":list(cand)})
        script="""import fs from 'node:fs'; import { projectV143RenderEvents } from './lib/v143RenderContract.js'; const x=JSON.parse(fs.readFileSync(process.argv[1],'utf8')); fs.writeFileSync(process.argv[2],JSON.stringify({renderEvents:projectV143RenderEvents(x.renderEvents||[])}));"""
        subprocess.check_call(["node","--input-type=module","-e",script,str(src),str(out)],cwd=ROOT)
        projected=canonical_events(load_json(out).get("renderEvents") or [])
    psha=sha256_json(projected)
    if len(projected)!=len(cand) or psha!=sha: raise RuntimeError("PDF fidelity mismatch")
    return {"schema":"dadrock.tabs.v150.pdf-event-fidelity.v1","passed":True,"candidateEventCount":len(cand),"candidateEventSha256":sha,
            "pdfEventCount":len(projected),"pdfEventSha256":psha,"pdfEventFidelity":1.0,"referenceOpened":False,"rendererProjection":"lib/v143RenderContract.js::projectV143RenderEvents"}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True,type=Path); args=ap.parse_args()
    od=args.output_dir if args.output_dir.is_absolute() else ROOT/args.output_dir
    if od.exists(): raise RuntimeError(f"output exists {od}")
    verify(); base=accepted(); prior=v149(); keep,reverted=selected_indices(); cand=construct(base,prior,keep); metrics=validate(base,cand,keep); sha=sha256_json(cand)
    replay=construct(base,prior,keep)
    if replay!=cand or sha256_json(replay)!=sha: raise RuntimeError("determinism mismatch")
    pdf=pdf_fidelity(cand,sha); od.mkdir(parents=True)
    write_json(od/"candidate.json",{"instrument":"rhythm","renderEvents":cand})
    proof={"schema":"dadrock.tabs.v150.contextual-prune-construction-proof.v1","classification":"reference-free-single-candidate-construction","gate":"GO",
           "policy":"v149-minus-strict-both-sides-worse-local-context-overrides","candidateEventSha256":sha,"deterministic":True,"deterministicReplayEventSha256":sha,
           "metrics":metrics,"revertedEventIndices":reverted,"pdfEventFidelity":1.0,
           "frozenInputs":{"analysisFileSha256":EXPECTED["analysisFileSha"],"analysisGitBlob":EXPECTED["analysisBlob"],"preregistrationGitBlob":EXPECTED["preregBlob"],"authorizationGitBlob":EXPECTED["authBlob"],"v149EventSha256":EXPECTED["v149EventSha"]},
           "safety":{"goldOrReferenceRead":False,"priorScoreResultRead":False,"scorerInvoked":False,"scoreCallCount":0,"candidateVariantsConstructed":1,"candidateSearchRun":False,"alternateContextRuleTested":False,"evidenceMarginThresholdSweep":False,"retuningRun":False,"audioReadOrDecoded":False,"hpssOrCqtRecomputed":False,"modalOrGpuUsed":False,"mainOrProductionModified":False,"automaticPromotion":False}}
    write_json(od/"construction-proof.json",proof); write_json(od/"pdf-event-fidelity.json",pdf)
    files={}
    for n in ("candidate.json","construction-proof.json","pdf-event-fidelity.json"):
        b=(od/n).read_bytes(); files[n]={"bytes":len(b),"sha256":sha256_bytes(b)}
    write_json(od/"preservation-manifest.json",{"schema":"dadrock.tabs.v150.contextual-prune-preservation.v1","candidateEventSha256":sha,"files":files,"referenceFacingScoringAuthorization":False})
    print(json.dumps({"gate":"GO","candidateEventSha256":sha,"changedEvents":33,"revertedFromV149":21,"retainedPercentOfV149Changes":100*33/54,"pdfEventFidelity":1.0,"scoreCallCount":0},indent=2,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
