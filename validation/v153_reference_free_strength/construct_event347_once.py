#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, hashlib, json, subprocess, sys, tempfile
from collections import Counter
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
V152_PATH = ROOT / "debug/v152-active-recurrence/candidate/candidate.json"
PHASE_A_PATH = ROOT / "debug/v153-reference-free-strength/phase-a-analysis.json"
PREREG_PATH = ROOT / "debug/v153-reference-free-strength/phase-b-construction-preregistration.json"
AUTH_PATH = ROOT / "debug/v153-reference-free-strength/phase-b-construction-authorization.json"
KEEP = [347]
V152_CHANGED = [132, 347, 457]
MAX_FRET = 24

EXPECTED = {
    "acceptedSha": "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881",
    "v152FileSha": "9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb",
    "v152Blob": "8486188bc7c2f5d0d7649e98b0970b64dd0eebed",
    "v152EventSha": "5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6",
    "phaseAFileSha": "cd2cef3fd1491f950ad795cab6e39b4013d137abfa2f4c94c1d96db133783c53",
    "phaseABlob": "012353df21573a4e34f50500c1fa5deb4b63422b",
    "preregBlob": "524a53b19c2ea737d2a01c9b959cfadd5b6cb9d8",
    "authBlob": "ee74c80e0d50c01a8ca5deddee0fd04d7c9d005d",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "renderContractBlob": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
}


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True
    ).strip()


def verify_frozen_inputs() -> None:
    checks = {
        V152_PATH: EXPECTED["v152Blob"],
        PHASE_A_PATH: EXPECTED["phaseABlob"],
        PREREG_PATH: EXPECTED["preregBlob"],
        AUTH_PATH: EXPECTED["authBlob"],
        ROOT / "modal/v147_phase_c_artifact_support.py": EXPECTED["supportBlob"],
        ROOT / "validation/rhythm_holdout/canonical.py": EXPECTED["canonicalBlob"],
        ROOT / "lib/v143RenderContract.js": EXPECTED["renderContractBlob"],
    }
    for path, expected in checks.items():
        actual = git_blob(path)
        if actual != expected:
            raise RuntimeError(f"blob mismatch {path}: {actual} != {expected}")
    if sha256_bytes(V152_PATH.read_bytes()) != EXPECTED["v152FileSha"]:
        raise RuntimeError("V152 candidate file SHA mismatch")
    if sha256_bytes(PHASE_A_PATH.read_bytes()) != EXPECTED["phaseAFileSha"]:
        raise RuntimeError("V153 Phase A file SHA mismatch")
    phase_a = load_json(PHASE_A_PATH)
    if phase_a.get("gate") != "GO_UNIQUE_WINNER":
        raise RuntimeError("V153 Phase A gate mismatch")
    if int(phase_a.get("uniqueStrongestEventIndex")) != 347:
        raise RuntimeError("V153 unique winner mismatch")
    ranked = [int(x) for x in phase_a.get("rankedEventIndices", [])]
    if ranked != [347, 132, 457]:
        raise RuntimeError("V153 ranking mismatch")
    auth = load_json(AUTH_PATH)
    if auth.get("authorizedBoundary") != "exactly one V153 event-347 candidate construction":
        raise RuntimeError("construction authorization mismatch")


def accepted_events() -> list[dict[str, Any]]:
    rows = canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(rows) != EXPECTED_ACCEPTED_EVENT_COUNT:
        raise RuntimeError("accepted count mismatch")
    if sha256_json(rows) != EXPECTED["acceptedSha"] or sha256_json(rows) != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise RuntimeError("accepted event identity mismatch")
    if len({int(r["measure"]) for r in rows}) != EXPECTED_MEASURE_COUNT:
        raise RuntimeError("accepted measure mismatch")
    return rows


def v152_events() -> list[dict[str, Any]]:
    rows = canonical_events(load_json(V152_PATH).get("renderEvents") or [])
    if len(rows) != EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(rows) != EXPECTED["v152EventSha"]:
        raise RuntimeError("V152 event identity mismatch")
    return rows


def changed_indices(base: Sequence[Mapping[str, Any]], other: Sequence[Mapping[str, Any]]) -> list[int]:
    return [int(b["eventIndex"]) for b, a in zip(base, other) if dict(b) != dict(a)]


def construct(base: Sequence[Mapping[str, Any]], source: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    source_by = {int(r["eventIndex"]): r for r in source}
    return canonical_events([
        copy.deepcopy(dict(source_by[int(row["eventIndex"])] if int(row["eventIndex"]) == 347 else row))
        for row in base
    ])


def validate(base: Sequence[Mapping[str, Any]], source: Sequence[Mapping[str, Any]], cand: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if changed_indices(base, source) != V152_CHANGED:
        raise RuntimeError("V152 changed-event set mismatch")
    if timing_and_metadata_violations(base, cand):
        raise RuntimeError("timing/metadata invariant violation")
    source_by = {int(r["eventIndex"]): r for r in source}
    changed = changed_indices(base, cand)
    if changed != KEEP:
        raise RuntimeError(f"candidate changed-event set mismatch: {changed}")
    onset_counts = Counter((int(r["measure"]), int(r["step"])) for r in base)
    b347 = next(r for r in base if int(r["eventIndex"]) == 347)
    onset347 = (int(b347["measure"]), int(b347["step"]))
    if onset_counts[onset347] != 1:
        raise RuntimeError("event 347 accepted onset is not singleton")
    changed_onsets = {(int(b["measure"]), int(b["step"])) for b, a in zip(base, cand) if dict(b) != dict(a)}
    if changed_onsets != {onset347}:
        raise RuntimeError("changed onset mismatch")
    pos_violations: list[int] = []
    projection_violations: list[int] = []
    for b, a in zip(base, cand):
        idx = int(b["eventIndex"])
        expected = source_by[idx] if idx == 347 else b
        if dict(a) != dict(expected):
            projection_violations.append(idx)
        s, f, m = int(a["stringIndex"]), int(a["fret"]), int(a["midi"])
        if s not in OPEN_MIDI_BY_STRING_INDEX or not 0 <= f <= MAX_FRET or OPEN_MIDI_BY_STRING_INDEX[s] + f != m:
            pos_violations.append(idx)
    if pos_violations or projection_violations:
        raise RuntimeError(f"position/projection violation {pos_violations[:3]} {projection_violations[:3]}")
    return {
        "eventCount": len(cand),
        "generatedMeasureCount": len({int(r["measure"]) for r in cand}),
        "changedEventCountVersusAccepted": 1,
        "changedEventIndices": changed,
        "changedOnsetCountVersusAccepted": 1,
        "polyphonicChangedEventsVersusAccepted": 0,
        "retainedPercentOfV152Changes": 100.0 / 3.0,
        "revertedFromV152": 2,
        "timingMetadataInvariantViolations": 0,
        "positionIdentityViolations": 0,
        "v152ProjectionViolations": 0,
    }


def pdf_fidelity(cand: Sequence[Mapping[str, Any]], candidate_sha: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v153-pdf-") as td:
        src = Path(td) / "candidate.json"
        out = Path(td) / "projected.json"
        write_json(src, {"renderEvents": list(cand)})
        script = """import fs from 'node:fs'; import { projectV143RenderEvents } from './lib/v143RenderContract.js'; const x=JSON.parse(fs.readFileSync(process.argv[1],'utf8')); fs.writeFileSync(process.argv[2],JSON.stringify({renderEvents:projectV143RenderEvents(x.renderEvents||[])}));"""
        subprocess.check_call(["node", "--input-type=module", "-e", script, str(src), str(out)], cwd=ROOT)
        projected = canonical_events(load_json(out).get("renderEvents") or [])
    projected_sha = sha256_json(projected)
    if len(projected) != len(cand) or projected_sha != candidate_sha:
        raise RuntimeError("PDF event fidelity mismatch")
    return {
        "schema": "dadrock.tabs.v153.event347.pdf-event-fidelity.v1",
        "passed": True,
        "candidateEventCount": len(cand),
        "candidateEventSha256": candidate_sha,
        "pdfEventCount": len(projected),
        "pdfEventSha256": projected_sha,
        "pdfEventFidelity": 1.0,
        "referenceOpened": False,
        "rendererProjection": "lib/v143RenderContract.js::projectV143RenderEvents",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Construct the single frozen V153 event-347 candidate once")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output_dir.exists():
        raise RuntimeError(f"output already exists: {output_dir}")
    verify_frozen_inputs()
    base = accepted_events()
    source = v152_events()
    candidate = construct(base, source)
    metrics = validate(base, source, candidate)
    candidate_sha = sha256_json(candidate)
    replay = construct(base, source)
    if replay != candidate or sha256_json(replay) != candidate_sha:
        raise RuntimeError("deterministic replay mismatch")
    pdf = pdf_fidelity(candidate, candidate_sha)
    output_dir.mkdir(parents=True)
    write_json(output_dir / "candidate.json", {"instrument": "rhythm", "renderEvents": candidate})
    proof = {
        "schema": "dadrock.tabs.v153.event347.construction-proof.v1",
        "classification": "reference-free-single-candidate-construction",
        "gate": "GO",
        "policy": "accepted-baseline-plus-only-v152-event-347",
        "candidateEventSha256": candidate_sha,
        "deterministic": True,
        "deterministicReplayEventSha256": candidate_sha,
        "metrics": metrics,
        "selectedEventIndex": 347,
        "pdfEventFidelity": 1.0,
        "frozenInputs": {
            "v152CandidateFileSha256": EXPECTED["v152FileSha"],
            "v152CandidateGitBlob": EXPECTED["v152Blob"],
            "v152CandidateEventSha256": EXPECTED["v152EventSha"],
            "v153PhaseAFileSha256": EXPECTED["phaseAFileSha"],
            "v153PhaseAResultGitBlob": EXPECTED["phaseABlob"],
            "constructionPreregistrationGitBlob": EXPECTED["preregBlob"],
            "constructionAuthorizationGitBlob": EXPECTED["authBlob"],
        },
        "safety": {
            "goldOrReferenceRead": False,
            "professionalImageRead": False,
            "priorScoreResultRead": False,
            "scorerInvoked": False,
            "scoreCallCount": 0,
            "candidateVariantsConstructed": 1,
            "candidateSearchRun": False,
            "thresholdOrWeightFilterRuleTuning": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalL4CudaOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }
    write_json(output_dir / "construction-proof.json", proof)
    write_json(output_dir / "pdf-event-fidelity.json", pdf)
    files: dict[str, Any] = {}
    for name in ("candidate.json", "construction-proof.json", "pdf-event-fidelity.json"):
        payload = (output_dir / name).read_bytes()
        files[name] = {"bytes": len(payload), "sha256": sha256_bytes(payload)}
    write_json(output_dir / "preservation-manifest.json", {
        "schema": "dadrock.tabs.v153.event347.preservation.v1",
        "candidateEventSha256": candidate_sha,
        "files": files,
        "referenceFacingScoringAuthorization": False,
    })
    print(json.dumps({
        "gate": "GO",
        "candidateEventSha256": candidate_sha,
        "changedEventIndices": [347],
        "changedEvents": 1,
        "changedOnsets": 1,
        "polyphonicChangedEvents": 0,
        "pdfEventFidelity": 1.0,
        "scoreCallCount": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
