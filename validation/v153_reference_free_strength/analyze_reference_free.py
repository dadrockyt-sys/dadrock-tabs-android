#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "debug/v153-reference-free-strength/phase-a-preregistration.json"
AUTH = ROOT / "debug/v153-reference-free-strength/phase-a-authorization.json"
V150 = ROOT / "debug/v150-contextual-singleton/phase-a-analysis.json"
V149 = ROOT / "debug/v149-singleton-confidence/phase-a-analysis.json"
V152_PROOF = ROOT / "debug/v152-active-recurrence/candidate/construction-proof.json"

EXPECTED = {
    "preregBlob": "449d668c5959e97f8f1172bc697a9578c4df03f6",
    "authorizationBlob": "46f38b384d47e9ffc38de3e2bc6c3cfe60bf9642",
    "v150AnalysisBlob": "67ad55d005415be2248a57238109a3d8745e4061",
    "v149AnalysisBlob": "cd3b52493aa5e3b1945b0a30ba8d6d9dbf492f1a",
    "v152ProofBlob": "3530c931bee9ab5888f350cd30d793388ebb5eca",
    "v152CandidateEventSha": "5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6",
}
EXPECTED_INDICES = [132, 347, 457]


def git_blob(path: Path) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(path.relative_to(ROOT))], cwd=ROOT, text=True
    ).strip()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="V153 reference-free strength ranking")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"output already exists: {output}")

    expected_blobs = {
        PREREG: EXPECTED["preregBlob"],
        AUTH: EXPECTED["authorizationBlob"],
        V150: EXPECTED["v150AnalysisBlob"],
        V149: EXPECTED["v149AnalysisBlob"],
        V152_PROOF: EXPECTED["v152ProofBlob"],
    }
    observed_blobs = {}
    for path, expected in expected_blobs.items():
        observed = git_blob(path)
        observed_blobs[str(path.relative_to(ROOT))] = observed
        if observed != expected:
            raise RuntimeError(f"Git blob mismatch for {path.relative_to(ROOT)}: {observed} != {expected}")

    prereg = load(PREREG)
    auth = load(AUTH)
    if prereg.get("populationEventIndices") != EXPECTED_INDICES:
        raise RuntimeError("preregistration population mismatch")
    if auth.get("authorizedPopulationEventIndices") != EXPECTED_INDICES:
        raise RuntimeError("authorization population mismatch")

    proof = load(V152_PROOF)
    if proof.get("candidateEventSha256") != EXPECTED["v152CandidateEventSha"]:
        raise RuntimeError("V152 candidate identity mismatch")
    if sorted(int(x) for x in proof.get("bothSelectedEventIndices", [])) != EXPECTED_INDICES:
        raise RuntimeError("V152 both-selected population mismatch")
    if sorted(int(x) for x in (proof.get("metrics") or {}).get("changedEventIndices", [])) != EXPECTED_INDICES:
        raise RuntimeError("V152 changed-event population mismatch")
    if int((proof.get("metrics") or {}).get("polyphonicChangedEventsVersusAccepted", -1)) != 0:
        raise RuntimeError("V152 population is not singleton-only")

    v150 = load(V150)
    v149 = load(V149)
    context_by = {int(row["eventIndex"]): row for row in v150.get("allRows", [])}
    confidence_by = {int(row["eventIndex"]): row for row in v149.get("allRows", [])}

    rows = []
    for idx in EXPECTED_INDICES:
        if idx not in context_by or idx not in confidence_by:
            raise RuntimeError(f"missing preserved evidence for event {idx}")
        c = context_by[idx]
        e = confidence_by[idx]
        if c.get("contextRelationship") != "strict-both-sides-better":
            raise RuntimeError(f"event {idx} lost frozen positive voice-leading context")
        if c.get("exactPitchSupportClass") != "selected-exact-pitch-more-supported":
            raise RuntimeError(f"event {idx} is not selected-supported in exact-pitch recurrence")
        if c.get("pitchClassSupportClass") != "selected-pitch-class-more-supported":
            raise RuntimeError(f"event {idx} is not selected-supported in pitch-class recurrence")

        exact_delta = int(c["windowSelectedExactMidiCount"]) - int(c["windowOriginalExactMidiCount"])
        pc_delta = int(c["windowSelectedPitchClassCount"]) - int(c["windowOriginalPitchClassCount"])
        voice_improvement = -int(c["totalVoiceLeadingCostDelta"])
        nearest_gate = float(e["nearestGateExcessDb"])
        evidence_tuple = [exact_delta, pc_delta, voice_improvement, nearest_gate]
        rows.append({
            "eventIndex": idx,
            "measure": int(c["measure"]),
            "step": int(c["step"]),
            "originalMidi": int(c["originalMidi"]),
            "selectedMidi": int(c["selectedMidi"]),
            "selectedMinusOriginalExactPitchRecurrenceCount": exact_delta,
            "selectedMinusOriginalPitchClassRecurrenceCount": pc_delta,
            "twoSidedVoiceLeadingImprovementSemitones": voice_improvement,
            "nearestFrozenV147GateExcessDb": nearest_gate,
            "evidenceTuple": evidence_tuple,
        })

    ranked = sorted(rows, key=lambda row: (tuple(row["evidenceTuple"]), -int(row["eventIndex"])), reverse=True)
    top_tuple = tuple(ranked[0]["evidenceTuple"])
    second_tuple = tuple(ranked[1]["evidenceTuple"])
    unique = top_tuple != second_tuple
    winner = int(ranked[0]["eventIndex"]) if unique else None

    result = {
        "schema": "dadrock.tabs.v153.reference-free-strength.phase-a-analysis.v1",
        "classification": "reference-free-deterministic-strength-ranking",
        "gate": "GO_UNIQUE_WINNER" if unique else "STOP_NO_UNIQUE_WINNER",
        "populationEventIndices": EXPECTED_INDICES,
        "v152CandidateCanonicalEventSha256": EXPECTED["v152CandidateEventSha"],
        "rankingRule": prereg["rankingRule"],
        "rankedEventIndices": [int(row["eventIndex"]) for row in ranked],
        "uniqueStrongestEvent": unique,
        "uniqueStrongestEventIndex": winner,
        "rows": ranked,
        "inputGitBlobs": observed_blobs,
        "safety": {
            "goldOrReferenceRead": False,
            "professionalImageRead": False,
            "priorScoreResultRead": False,
            "candidateConstructed": False,
            "candidateSearchOrVariants": False,
            "thresholdOrWeightTuning": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalL4CudaOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
            "scoreCallCount": 0,
        },
        "nextBoundary": (
            "STOP_BEFORE_CONSTRUCTION_FRESH_AUTHORIZATION_REQUIRED"
            if unique else "STOP_NO_CONSTRUCTION"
        ),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
