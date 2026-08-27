#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
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
V148_PATH = ROOT / "debug/v148-singleton-only/candidate/candidate.json"
ANALYSIS_PATH = ROOT / "debug/v149-singleton-confidence/phase-a-analysis.json"
PREREG_PATH = ROOT / "debug/v149-singleton-confidence/phase-b-high-confidence-preregistration.json"
AUTH_PATH = ROOT / "debug/v149-singleton-confidence/phase-b-construction-authorization.json"

EXPECTED = {
    "v148FileSha": "b45034e2a4dd10a3d7784e584fccdbc7e49667a5b93c9a77ea42f5562ae139bb",
    "v148EventSha": "1be67004dea62b14740241b536339bb7cad2ecf3ee9e98bfb6109f67e4e1b1fa",
    "analysisFileSha": "e18a4a3a3fa41b20793ef742e4f2ffad0e3e4ee1b41a90997ba85d7db4bace08",
    "analysisBlob": "cd3b52493aa5e3b1945b0a30ba8d6d9dbf492f1a",
    "preregBlob": "d8ebc3d4535ec1484ef64e946089027792715c5c",
    "authBlob": "7f1d47ecee87cd7508addcf86bed5ae56230835e",
    "supportBlob": "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf",
    "canonicalBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "renderContractBlob": "ccbb93c48982798cc474309fd981f6ca02d5c8d4",
    "changedEvents": 54,
    "changedOnsets": 54,
    "thresholdDb": 3.0,
}
MAX_FRET = 24


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_frozen_inputs() -> None:
    checks = {
        PREREG_PATH: EXPECTED["preregBlob"],
        AUTH_PATH: EXPECTED["authBlob"],
        ANALYSIS_PATH: EXPECTED["analysisBlob"],
        ROOT / "modal/v147_phase_c_artifact_support.py": EXPECTED["supportBlob"],
        ROOT / "validation/rhythm_holdout/canonical.py": EXPECTED["canonicalBlob"],
        ROOT / "lib/v143RenderContract.js": EXPECTED["renderContractBlob"],
    }
    for path, expected in checks.items():
        actual = git_blob(path)
        if actual != expected:
            raise RuntimeError(f"Git blob mismatch for {path}: {actual} != {expected}")
    if sha256_bytes(ANALYSIS_PATH.read_bytes()) != EXPECTED["analysisFileSha"]:
        raise RuntimeError("analysis byte SHA mismatch")
    auth = load_json(AUTH_PATH)
    if (auth.get("authorization") or {}).get("received") is not True:
        raise RuntimeError("construction authorization missing")
    if auth.get("referenceFacingScoringAuthorization") is not False:
        raise RuntimeError("construction auth unexpectedly authorizes scoring")


def load_accepted() -> list[dict[str, Any]]:
    accepted = canonical_events(materialize_accepted_family(load_json(V5_PATH)))
    if len(accepted) != EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(accepted) != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise RuntimeError("accepted family identity mismatch")
    measures = sorted({int(row["measure"]) for row in accepted})
    if measures != list(range(1, EXPECTED_MEASURE_COUNT + 1)):
        raise RuntimeError("accepted measure identity mismatch")
    return accepted


def load_v148() -> list[dict[str, Any]]:
    payload = V148_PATH.read_bytes()
    if sha256_bytes(payload) != EXPECTED["v148FileSha"]:
        raise RuntimeError("V148 candidate file SHA mismatch")
    doc = json.loads(payload)
    events = canonical_events(doc.get("renderEvents") or [])
    if len(events) != EXPECTED_ACCEPTED_EVENT_COUNT or sha256_json(events) != EXPECTED["v148EventSha"]:
        raise RuntimeError("V148 candidate canonical identity mismatch")
    return events


def selected_event_indices() -> list[int]:
    analysis = load_json(ANALYSIS_PATH)
    if analysis.get("gate") != "GO" or (analysis.get("population") or {}).get("eventCount") != 106:
        raise RuntimeError("V149 Phase A analysis gate mismatch")
    rows = analysis.get("allRows") or []
    if len(rows) != 106:
        raise RuntimeError("V149 analysis row count mismatch")
    selected = sorted(int(row["eventIndex"]) for row in rows if float(row["nearestGateExcessDb"]) >= EXPECTED["thresholdDb"])
    rejected = sorted(int(row["eventIndex"]) for row in rows if float(row["nearestGateExcessDb"]) < EXPECTED["thresholdDb"])
    if len(selected) != EXPECTED["changedEvents"] or len(rejected) != 52:
        raise RuntimeError(f"frozen 3 dB split mismatch: selected={len(selected)} rejected={len(rejected)}")
    return selected


def construct(accepted: Sequence[Mapping[str, Any]], v148: Sequence[Mapping[str, Any]], selected: Sequence[int]) -> list[dict[str, Any]]:
    accepted_by = {int(row["eventIndex"]): row for row in accepted}
    v148_by = {int(row["eventIndex"]): row for row in v148}
    selected_set = set(selected)
    output: list[dict[str, Any]] = []
    for row in accepted:
        idx = int(row["eventIndex"])
        if idx in selected_set:
            vrow = v148_by[idx]
            if int(vrow["measure"]) != int(row["measure"]) or int(vrow["step"]) != int(row["step"]):
                raise RuntimeError(f"V148 timing mismatch eventIndex={idx}")
            if abs(int(vrow["midi"]) - int(row["midi"])) != 1:
                raise RuntimeError(f"V148 pitch delta mismatch eventIndex={idx}")
            output.append(copy.deepcopy(dict(vrow)))
        else:
            output.append(copy.deepcopy(dict(accepted_by[idx])))
    return canonical_events(output)


def validate(accepted: Sequence[Mapping[str, Any]], candidate: Sequence[Mapping[str, Any]], selected: Sequence[int]) -> dict[str, Any]:
    timing = timing_and_metadata_violations(accepted, candidate)
    if timing:
        raise RuntimeError(f"timing/metadata violations: {timing[:3]}")
    selected_set = set(selected)
    changed: list[int] = []
    onsets: set[tuple[int, int]] = set()
    position_violations: list[int] = []
    for before, after in zip(accepted, candidate):
        idx = int(before["eventIndex"])
        if dict(before) != dict(after):
            changed.append(idx)
            onsets.add((int(before["measure"]), int(before["step"])))
        string_index = int(after["stringIndex"])
        fret = int(after["fret"])
        midi = int(after["midi"])
        if string_index not in OPEN_MIDI_BY_STRING_INDEX or not (0 <= fret <= MAX_FRET) or OPEN_MIDI_BY_STRING_INDEX[string_index] + fret != midi:
            position_violations.append(idx)
    if changed != list(selected):
        raise RuntimeError("changed indices differ from frozen selected indices")
    if len(changed) != EXPECTED["changedEvents"] or len(onsets) != EXPECTED["changedOnsets"]:
        raise RuntimeError("V149 changed event/onset count mismatch")
    if position_violations:
        raise RuntimeError(f"position violations: {position_violations[:5]}")
    return {
        "eventCount": len(candidate),
        "generatedMeasureCount": len({int(row["measure"]) for row in candidate}),
        "changedEventCountVersusAccepted": len(changed),
        "changedOnsetCountVersusAccepted": len(onsets),
        "polyphonicChangedEventsVersusAccepted": 0,
        "thresholdDb": EXPECTED["thresholdDb"],
        "retainedPercentOfV148Changes": 100.0 * len(changed) / 106.0,
        "revertedV148ChangeCount": 106 - len(changed),
        "timingMetadataInvariantViolations": len(timing),
        "positionIdentityViolations": len(position_violations),
        "changedEventIndices": changed,
        "selectedIndexSetMatchesFrozenAnalysis": set(changed) == selected_set,
    }


def pdf_fidelity(candidate: Sequence[Mapping[str, Any]], candidate_sha: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="v149-pdf-") as temp:
        temp_dir = Path(temp)
        src = temp_dir / "candidate.json"
        out = temp_dir / "projected.json"
        write_json(src, {"renderEvents": list(candidate)})
        script = """
import fs from 'node:fs';
import { projectV143RenderEvents } from './lib/v143RenderContract.js';
const input = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
const renderEvents = projectV143RenderEvents(input.renderEvents || []);
fs.writeFileSync(process.argv[2], JSON.stringify({renderEvents}));
"""
        subprocess.check_call(["node", "--input-type=module", "-e", script, str(src), str(out)], cwd=ROOT)
        projected = canonical_events(load_json(out).get("renderEvents") or [])
    projected_sha = sha256_json(projected)
    if len(projected) != len(candidate) or projected_sha != candidate_sha:
        raise RuntimeError("V149 PDF/render projection fidelity mismatch")
    return {
        "schema": "dadrock.tabs.v149.pdf-event-fidelity.v1",
        "passed": True,
        "candidateEventCount": len(candidate),
        "candidateEventSha256": candidate_sha,
        "pdfEventCount": len(projected),
        "pdfEventSha256": projected_sha,
        "pdfEventFidelity": 1.0,
        "referenceOpened": False,
        "rendererProjection": "lib/v143RenderContract.js::projectV143RenderEvents",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Construct exactly one frozen V149 high-confidence singleton candidate.")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    out_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if out_dir.exists():
        raise RuntimeError(f"output directory already exists: {out_dir}")

    verify_frozen_inputs()
    accepted = load_accepted()
    v148 = load_v148()
    selected = selected_event_indices()
    candidate = construct(accepted, v148, selected)
    metrics = validate(accepted, candidate, selected)
    candidate_sha = sha256_json(candidate)

    replay = construct(accepted, v148, selected)
    replay_sha = sha256_json(replay)
    if replay_sha != candidate_sha or replay != candidate:
        raise RuntimeError("V149 deterministic replay mismatch")

    pdf = pdf_fidelity(candidate, candidate_sha)
    out_dir.mkdir(parents=True)
    candidate_doc = {"instrument": "rhythm", "renderEvents": candidate}
    proof = {
        "schema": "dadrock.tabs.v149.high-confidence-singleton-construction-proof.v1",
        "classification": "reference-free-single-candidate-construction",
        "gate": "GO",
        "policy": "accepted-baseline-plus-v148-singletons-nearest-gate-at-least-3db",
        "candidateEventSha256": candidate_sha,
        "deterministic": True,
        "deterministicReplayEventSha256": replay_sha,
        "metrics": metrics,
        "frozenInputs": {
            "analysisFileSha256": EXPECTED["analysisFileSha"],
            "analysisGitBlob": EXPECTED["analysisBlob"],
            "preregistrationGitBlob": EXPECTED["preregBlob"],
            "authorizationGitBlob": EXPECTED["authBlob"],
            "v148FileSha256": EXPECTED["v148FileSha"],
            "v148EventSha256": EXPECTED["v148EventSha"],
            "acceptedEventSha256": EXPECTED_ACCEPTED_EVENT_SHA256,
        },
        "pdfEventFidelity": 1.0,
        "safety": {
            "goldOrReferenceRead": False,
            "professionalImageRead": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "scorerInvoked": False,
            "scoreCallCount": 0,
            "candidateVariantsConstructed": 1,
            "candidateSearchRun": False,
            "retuningRun": False,
            "modalOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
        },
    }
    write_json(out_dir / "candidate.json", candidate_doc)
    write_json(out_dir / "construction-proof.json", proof)
    write_json(out_dir / "pdf-event-fidelity.json", pdf)
    manifest = {}
    for name in ("candidate.json", "construction-proof.json", "pdf-event-fidelity.json"):
        data = (out_dir / name).read_bytes()
        manifest[name] = {"bytes": len(data), "sha256": sha256_bytes(data)}
    write_json(out_dir / "preservation-manifest.json", {
        "schema": "dadrock.tabs.v149.high-confidence-singleton-preservation.v1",
        "candidateEventSha256": candidate_sha,
        "files": manifest,
        "referenceFacingScoringAuthorization": False,
    })
    print(json.dumps({
        "gate": "GO",
        "candidateEventSha256": candidate_sha,
        "changedEvents": metrics["changedEventCountVersusAccepted"],
        "retainedPercentOfV148Changes": metrics["retainedPercentOfV148Changes"],
        "pdfEventFidelity": 1.0,
        "scoreCallCount": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
