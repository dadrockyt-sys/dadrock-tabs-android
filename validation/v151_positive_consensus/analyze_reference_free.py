#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS_PATH = ROOT / "debug/v150-contextual-singleton/phase-a-analysis.json"
PROOF_PATH = ROOT / "debug/v150-contextual-singleton/candidate/construction-proof.json"

EXPECTED_V150_EVENT_SHA = "72a0582cfc7d03d84cd2f878f191a69b7262b200ce248d1a896207444a3c5e4e"
EXPECTED_V150_CHANGED = 33


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    proof = load_json(PROOF_PATH)
    if proof.get("candidateEventSha256") != EXPECTED_V150_EVENT_SHA:
        raise SystemExit("unexpected V150 candidate event SHA")
    changed = list(proof.get("metrics", {}).get("changedEventIndices", []))
    if len(changed) != EXPECTED_V150_CHANGED or len(set(changed)) != EXPECTED_V150_CHANGED:
        raise SystemExit("unexpected V150 changed-event set")

    analysis = load_json(ANALYSIS_PATH)
    rows_by_index = {int(row["eventIndex"]): row for row in analysis.get("allRows", [])}
    if set(changed) - set(rows_by_index):
        raise SystemExit("V150 changed event missing from contextual analysis")

    rows = []
    for idx in changed:
        row = rows_by_index[idx]
        voice = row.get("contextRelationship") == "strict-both-sides-better"
        pc = row.get("pitchClassSupportClass") != "original-pitch-class-more-supported"
        exact = row.get("exactPitchSupportClass") != "original-exact-pitch-more-supported"
        rows.append({
            "eventIndex": idx,
            "measure": row.get("measure"),
            "step": row.get("step"),
            "originalMidi": row.get("originalMidi"),
            "selectedMidi": row.get("selectedMidi"),
            "contextRelationship": row.get("contextRelationship"),
            "pitchClassSupportClass": row.get("pitchClassSupportClass"),
            "exactPitchSupportClass": row.get("exactPitchSupportClass"),
            "voiceLeadingPositive": voice,
            "pitchClassNotAgainst": pc,
            "exactPitchNotAgainst": exact,
            "positiveConsensus": bool(voice and pc and exact),
        })

    positive = [r for r in rows if r["positiveConsensus"]]
    result = {
        "schema": "dadrock.tabs.v151.positive-consensus.phase-a-analysis.v1",
        "classification": "reference-free-positive-consensus-analysis",
        "population": len(rows),
        "v150CandidateEventSha256": EXPECTED_V150_EVENT_SHA,
        "v150ChangedEventIndices": changed,
        "counts": {
            "voiceLeadingPositive": sum(r["voiceLeadingPositive"] for r in rows),
            "pitchClassNotAgainst": sum(r["pitchClassNotAgainst"] for r in rows),
            "exactPitchNotAgainst": sum(r["exactPitchNotAgainst"] for r in rows),
            "positiveConsensus": len(positive),
        },
        "percentages": {
            "voiceLeadingPositive": 100.0 * sum(r["voiceLeadingPositive"] for r in rows) / len(rows),
            "pitchClassNotAgainst": 100.0 * sum(r["pitchClassNotAgainst"] for r in rows) / len(rows),
            "exactPitchNotAgainst": 100.0 * sum(r["exactPitchNotAgainst"] for r in rows) / len(rows),
            "positiveConsensus": 100.0 * len(positive) / len(rows),
        },
        "contextRelationshipCounts": dict(Counter(r["contextRelationship"] for r in rows)),
        "pitchClassSupportCounts": dict(Counter(r["pitchClassSupportClass"] for r in rows)),
        "exactPitchSupportCounts": dict(Counter(r["exactPitchSupportClass"] for r in rows)),
        "positiveConsensusEventIndices": [r["eventIndex"] for r in positive],
        "rows": rows,
        "inputSha256": {
            "v150ContextAnalysis": sha256_file(ANALYSIS_PATH),
            "v150ConstructionProof": sha256_file(PROOF_PATH),
        },
        "safety": {
            "goldOrReferenceRead": False,
            "priorScoreResultRead": False,
            "candidateConstructed": False,
            "candidateSearchRun": False,
            "thresholdSweep": False,
            "audioReadOrDecoded": False,
            "hpssOrCqtRecomputed": False,
            "modalOrGpuUsed": False,
            "mainOrProductionModified": False,
            "automaticPromotion": False,
            "scoreCallCount": 0,
        },
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
