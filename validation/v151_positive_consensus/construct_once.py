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
    EXPECTED_ACCEPTED_EVENT_COUNT,
    EXPECTED_ACCEPTED_EVENT_SHA256,
    EXPECTED_MEASURE_COUNT,
    OPEN_MIDI_BY_STRING_INDEX,
    materialize_accepted_family,
    timing_and_metadata_violations,
)

V5_PATH = ROOT / "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"
V150_PATH = ROOT / "debug/v150-contextual-singleton/candidate/candidate.json"
ANALYSIS_PATH = ROOT / "debug/v151-positive-consensus/phase-a-analysis.json"
PREREG_PATH = ROOT / "debug/v151-positive-consensus/phase-b-preregistration.json"
AUTH_PATH = ROOT / "debug/v151-positive-consensus/phase-b-construction-authorization.json"
KEEP = [46, 132, 141, 282, 347, 457, 610, 811, 1004, 1049, 1206, 1207]
EXPECTED = {
    "v150FileSha": "8366b8bd0f3df71ca38dee7ffd1274761e73521bfde740eff9c46637651187b5",
    "v150EventSha": "72a0582cfc7d03d84cd2f878f191a69b7262b200ce248d1a896207444a3c5e4e",
    "analysisFileSha": "701a46ffa8c0b50eb829fa64e7b192f6ae29e00bca7340856956d22bff5dc6d9",
    "preregBlob": "b8a91fbe7c8cb03be2905e86508a921a2ed2759d",
    "authBlob": "2882c1daee695dcb14824e18d1a6ec62f9609405",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "renderContractBlob": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
    "changedEvents": 12,
}
MAX_FRET = 24


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(p: Path, x: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_blob(p: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(p.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def verify() -> None:
    for p, expected in {
        PREREG_PATH: EXPECTED["preregBlob"],
        AUTH_PATH: EXPECTED["authBlob"],
        ROOT / "modal/v147_phase_c_artifact_support.py": EXPECTED["supportBlob"],
        ROOT / "validation/rhythm_holdout/canonical.py": EXPECTED["canonicalBlob"],
        ROOT / "lib/v143RenderContract.js": EXPECTED["renderContractBlob"],
    }.items():
        actual = git_blob(p)
        if actual != expected:
            raise RuntimeError(f"blob mismatch {p}: {actual} != {expected}")
    if sha256_bytes(ANALYSIS_PATH.read_bytes()) != EXPECTED["analysisFileSha"]:
        raise RuntimeError("V151 analysis SHA mismatch")
    analysis = load_json(ANALYSIS_PATH)
    if sorted(int(x) for x in analysis.get("positiveConsensusEventIndices", [])) != KEEP:
        raise RuntimeError("positive consensus set mismatch")
    if int((analysis.get("counts") or {}).get("positiveConsensus", -1)) != 12:
        raise RuntimeError("positive consensus count mismatch")
    auth = load_json(AUTH_PATH)
    if (auth.get("authorization") or {}).get("received") is not True:
        raise RuntimeError("construction authorization missing")
    if auth.get("referenceFacingScoringAuthorization") is not False:
        raise RuntimeError("construction authorization crossed score boundary")


def accepted() -> list[dict[str, Any]]:
    rows = canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(rows) != EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows) != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise RuntimeError("accepted identity mismatch")
    if len({int(r["measure"]) for r in rows}) != EXPECTED_MEASURE_COUNT:
        raise RuntimeError("accepted measure count mismatch")
    return rows


def v150() -> list[dict[str, Any]]:
    b = V150_PATH.read_bytes()
    if sha256_bytes(b) != EXPECTED["v150FileSha"]:
        raise RuntimeError("V150 candidate file SHA mismatch")
    rows = canonical_events(json.loads(b).get("renderEvents") or [])
    if len(rows) != EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows) != EXPECTED["v150EventSha"]:
        raise RuntimeError("V150 candidate event identity mismatch")
    return rows


def construct(base: Sequence[Mapping[str, Any]], prior: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    pby = {int(r["eventIndex"]): r for r in prior}
    keep = set(KEEP)
    out = []
    for r in base:
        idx = int(r["eventIndex"])
        out.append(copy.deepcopy(dict(pby[idx] if idx in keep else r)))
    return canonical_events(out)


def validate(base: Sequence[Mapping[str, Any]], prior: Sequence[Mapping[str, Any]], cand: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    violations = timing_and_metadata_violations(base, cand)
    if violations:
        raise RuntimeError(f"timing/metadata violations {violations[:3]}")
    changed, onsets, position_bad, copy_bad = [], set(), [], []
    prior_by = {int(r["eventIndex"]): r for r in prior}
    keep = set(KEEP)
    for b, a in zip(base, cand):
        idx = int(b["eventIndex"])
        if dict(b) != dict(a):
            changed.append(idx)
            onsets.add((int(b["measure"]), int(b["step"])))
        expected = prior_by[idx] if idx in keep else b
        if dict(a) != dict(expected):
            copy_bad.append(idx)
        s, f, m = int(a["stringIndex"]), int(a["fret"]), int(a["midi"])
        if s not in OPEN_MIDI_BY_STRING_INDEX or not 0 <= f <= MAX_FRET or OPEN_MIDI_BY_STRING_INDEX[s] + f != m:
            position_bad.append(idx)
    if changed != KEEP or len(changed) != 12 or len(onsets) != 12:
        raise RuntimeError(f"changed set/count mismatch {changed}")
    if copy_bad:
        raise RuntimeError(f"projection mismatch {copy_bad[:5]}")
    if position_bad:
        raise RuntimeError(f"position violations {position_bad[:5]}")
    return {
        "eventCount": len(cand),
        "generatedMeasureCount": len({int(r["measure"]) for r in cand}),
        "changedEventCountVersusAccepted": 12,
        "changedOnsetCountVersusAccepted": 12,
        "polyphonicChangedEventsVersusAccepted": 0,
        "retainedPercentOfV150Changes": 100.0 * 12 / 33,
        "revertedFromV150": 21,
        "timingMetadataInvariantViolations": 0,
        "positionIdentityViolations": 0,
        "v150ProjectionViolations": 0,
        "changedEventIndices": changed,
    }


def pdf_fidelity(cand: Sequence[Mapping[str, Any]], sha: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v151-pdf-") as td:
        src = Path(td) / "candidate.json"
        out = Path(td) / "projected.json"
        write_json(src, {"renderEvents": list(cand)})
        script = """import fs from 'node:fs'; import { projectV143RenderEvents } from './lib/v143RenderContract.js'; const x=JSON.parse(fs.readFileSync(process.argv[1],'utf8')); fs.writeFileSync(process.argv[2],JSON.stringify({renderEvents:projectV143RenderEvents(x.renderEvents||[])}));"""
        subprocess.check_call(["node", "--input-type=module", "-e", script, str(src), str(out)], cwd=ROOT)
        projected = canonical_events(load_json(out).get("renderEvents") or [])
    projected_sha = sha256_json(projected)
    if len(projected) != len(cand) or projected_sha != sha:
        raise RuntimeError("PDF/render projection fidelity mismatch")
    return {
        "schema": "dadrock.tabs.v151.pdf-event-fidelity.v1",
        "passed": True,
        "candidateEventCount": len(cand),
        "candidateEventSha256": sha,
        "pdfEventCount": len(projected),
        "pdfEventSha256": projected_sha,
        "pdfEventFidelity": 1.0,
        "referenceOpened": False,
        "rendererProjection": "lib/v143RenderContract.js::projectV143RenderEvents",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output_dir.exists():
        raise RuntimeError(f"output already exists: {output_dir}")
    verify()
    base = accepted()
    prior = v150()
    cand = construct(base, prior)
    metrics = validate(base, prior, cand)
    sha = sha256_json(cand)
    replay = construct(base, prior)
    if replay != cand or sha256_json(replay) != sha:
        raise RuntimeError("determinism mismatch")
    pdf = pdf_fidelity(cand, sha)
    output_dir.mkdir(parents=True)
    write_json(output_dir / "candidate.json", {"instrument": "rhythm", "renderEvents": cand})
    proof = {
        "schema": "dadrock.tabs.v151.positive-consensus-construction-proof.v1",
        "classification": "reference-free-single-candidate-construction",
        "gate": "GO",
        "policy": "accepted-baseline-plus-v150-positive-consensus-only",
        "candidateEventSha256": sha,
        "deterministic": True,
        "deterministicReplayEventSha256": sha,
        "metrics": metrics,
        "positiveConsensusEventIndices": KEEP,
        "pdfEventFidelity": 1.0,
        "frozenInputs": {
            "phaseAAnalysisSha256": EXPECTED["analysisFileSha"],
            "preregistrationGitBlob": EXPECTED["preregBlob"],
            "authorizationGitBlob": EXPECTED["authBlob"],
            "v150EventSha256": EXPECTED["v150EventSha"],
            "v150FileSha256": EXPECTED["v150FileSha"],
        },
        "safety": {
            "goldOrReferenceRead": False,
            "priorScoreResultRead": False,
            "scorerInvoked": False,
            "scoreCallCount": 0,
            "candidateVariantsConstructed": 1,
            "candidateSearchRun": False,
            "alternateSubsetTested": False,
            "additionalFilterTested": False,
            "thresholdSweep": False,
            "retuningRun": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }
    write_json(output_dir / "construction-proof.json", proof)
    write_json(output_dir / "pdf-event-fidelity.json", pdf)
    files = {}
    for name in ("candidate.json", "construction-proof.json", "pdf-event-fidelity.json"):
        b = (output_dir / name).read_bytes()
        files[name] = {"bytes": len(b), "sha256": sha256_bytes(b)}
    write_json(output_dir / "preservation-manifest.json", {
        "schema": "dadrock.tabs.v151.positive-consensus-preservation.v1",
        "candidateEventSha256": sha,
        "files": files,
        "referenceFacingScoringAuthorization": False,
    })
    print(json.dumps({
        "gate": "GO",
        "candidateEventSha256": sha,
        "changedEvents": 12,
        "changedOnsets": 12,
        "polyphonicChangedEvents": 0,
        "retainedPercentOfV150Changes": 100.0 * 12 / 33,
        "pdfEventFidelity": 1.0,
        "scoreCallCount": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
