#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V151_ANALYSIS = ROOT / "debug/v151-positive-consensus/phase-a-analysis.json"
V151_PROOF = ROOT / "debug/v151-positive-consensus/candidate/construction-proof.json"
EXPECTED_ANALYSIS_SHA = "701a46ffa8c0b50eb829fa64e7b192f6ae29e00bca7340856956d22bff5dc6d9"
EXPECTED_V151_EVENT_SHA = "e6c437f534dfb5523610797c67f8f69176be903456ef4940c3032567b949156b"
EXPECTED_INDICES = [46, 132, 141, 282, 347, 457, 610, 811, 1004, 1049, 1206, 1207]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def classify(row: dict) -> str:
    exact = row.get("exactPitchSupportClass")
    pc = row.get("pitchClassSupportClass")
    e_sel = exact == "selected-exact-pitch-more-supported"
    p_sel = pc == "selected-pitch-class-more-supported"
    e_tied = exact == "exact-pitch-support-tied"
    p_tied = pc == "pitch-class-support-tied"
    if e_sel and p_sel:
        return "both-selected"
    if (e_sel and p_tied) or (p_sel and e_tied):
        return "one-selected"
    if e_tied and p_tied:
        return "both-tied"
    raise RuntimeError(f"unexpected recurrence combination for event {row.get('eventIndex')}: {exact} / {pc}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    if sha256_file(V151_ANALYSIS) != EXPECTED_ANALYSIS_SHA:
        raise RuntimeError("V151 analysis SHA mismatch")
    analysis = load(V151_ANALYSIS)
    if sorted(int(x) for x in analysis.get("positiveConsensusEventIndices", [])) != EXPECTED_INDICES:
        raise RuntimeError("V151 positive-consensus set mismatch")
    proof = load(V151_PROOF)
    if proof.get("candidateEventSha256") != EXPECTED_V151_EVENT_SHA:
        raise RuntimeError("V151 candidate event SHA mismatch")
    if sorted(int(x) for x in (proof.get("metrics") or {}).get("changedEventIndices", [])) != EXPECTED_INDICES:
        raise RuntimeError("V151 construction changed-event set mismatch")
    rows_by = {int(r["eventIndex"]): r for r in analysis.get("rows", [])}
    rows = []
    for idx in EXPECTED_INDICES:
        r = rows_by[idx]
        if r.get("positiveConsensus") is not True or r.get("contextRelationship") != "strict-both-sides-better":
            raise RuntimeError(f"event {idx} is not V151 positive consensus")
        strength = classify(r)
        rows.append({
            "eventIndex": idx,
            "measure": r.get("measure"),
            "step": r.get("step"),
            "originalMidi": r.get("originalMidi"),
            "selectedMidi": r.get("selectedMidi"),
            "exactPitchSupportClass": r.get("exactPitchSupportClass"),
            "pitchClassSupportClass": r.get("pitchClassSupportClass"),
            "strengthClass": strength,
        })
    counts = Counter(r["strengthClass"] for r in rows)
    groups = {k: [r["eventIndex"] for r in rows if r["strengthClass"] == k] for k in ("both-selected", "one-selected", "both-tied")}
    result = {
        "schema": "dadrock.tabs.v152.active-recurrence.phase-a-analysis.v1",
        "classification": "reference-free-active-recurrence-analysis",
        "population": 12,
        "v151CandidateEventSha256": EXPECTED_V151_EVENT_SHA,
        "counts": {k: int(counts.get(k, 0)) for k in ("both-selected", "one-selected", "both-tied")},
        "percentages": {k: 100.0 * counts.get(k, 0) / 12 for k in ("both-selected", "one-selected", "both-tied")},
        "eventIndicesByStrength": groups,
        "rows": rows,
        "inputSha256": {"v151PhaseAAnalysis": sha256_file(V151_ANALYSIS), "v151ConstructionProof": sha256_file(V151_PROOF)},
        "safety": {
            "goldOrReferenceRead": False,
            "v151ScoreResultRead": False,
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
    if not out.is_absolute(): out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
