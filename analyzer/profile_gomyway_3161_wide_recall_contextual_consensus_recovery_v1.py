from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_3161_wide_recall_contextual_pattern_recovery_v1 as ctxprof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61

recall = ctxprof.recall
recur = ctxprof.recur
v2 = ctxprof.v2
v3 = ctxprof.v3


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_from_counts(matched: int, missing: int, extra: int) -> float:
    precision = matched / (matched + extra) if (matched + extra) else 0.0
    recall = matched / (matched + missing) if (matched + missing) else 0.0
    return round(100.0 * (2.0 * precision * recall / (precision + recall) if (precision + recall) else 0.0), 2)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite profiler output: {INPUT_PATH.relative_to(ROOT)}")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    baseline = data.get("champion3161Score") or {}
    actual = (int(baseline.get("matched", -1)), int(baseline.get("missing", -1)), int(baseline.get("extra", -1)))
    if actual != EXPECTED or abs(float(baseline.get("pitchF1", -1.0)) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline.get('pitchF1')}")

    ranked = list(data.get("rankedSignatures") or [])
    rows = list(data.get("candidateRows") or [])
    if not ranked or not rows:
        raise RuntimeError("Contextual pattern profiler output does not contain ranked signatures/candidate rows")

    # Training-label selection only: choose broad signatures with meaningful true support.
    # Candidate scoring below uses only detection-side signatures already attached to each row.
    selected: list[dict[str, Any]] = []
    for r in ranked:
        t = int(r.get("true", 0))
        f = int(r.get("false", 0))
        p = float(r.get("precision", 0.0))
        if (t >= 20 and p >= 20.0) or (t >= 35 and p >= 10.0):
            selected.append(r)

    if not selected:
        raise RuntimeError("No broad contextual signatures available for consensus profiling")

    selected_sigs = {str(r["signature"]): r for r in selected}

    scored_rows: list[dict[str, Any]] = []
    max_votes = 0
    for row in rows:
        sigs = set(str(s) for s in row.get("signatures") or [])
        hits = [s for s in sigs if s in selected_sigs]
        # Weighted score rewards signatures that are both broad and relatively precise.
        weight = 0.0
        for s in hits:
            r = selected_sigs[s]
            weight += float(r["precision"]) / 100.0
        out = {
            "token": row.get("token"),
            "measure": row.get("measure"),
            "step": row.get("step"),
            "pitch": row.get("pitch"),
            "label": row.get("label"),
            "consensusVotes": len(hits),
            "consensusWeight": round(weight, 4),
            "matchedBroadSignatures": sorted(hits),
        }
        max_votes = max(max_votes, len(hits))
        scored_rows.append(out)

    vote_results: list[dict[str, Any]] = []
    for threshold in range(1, max_votes + 1):
        chosen = [r for r in scored_rows if int(r["consensusVotes"]) >= threshold]
        true = sum(1 for r in chosen if r["label"] == "true")
        false = sum(1 for r in chosen if r["label"] == "false")
        total = true + false
        matched = EXPECTED[0] + true
        missing = EXPECTED[1] - true
        extra = EXPECTED[2] + false
        vote_results.append(
            {
                "minVotes": threshold,
                "selected": total,
                "recoverTrue": true,
                "recoverFalse": false,
                "precision": round(100.0 * true / total, 2) if total else 0.0,
                "candidatePitchF1": score_from_counts(matched, missing, extra),
                "matchedMissingExtra": [matched, missing, extra],
            }
        )

    # Also sweep weighted consensus cutoffs. These are intentionally coarse profiler thresholds.
    weight_results: list[dict[str, Any]] = []
    for cutoff in [0.40, 0.60, 0.80, 1.00, 1.20, 1.50, 1.80, 2.00, 2.50, 3.00]:
        chosen = [r for r in scored_rows if float(r["consensusWeight"]) >= cutoff]
        true = sum(1 for r in chosen if r["label"] == "true")
        false = sum(1 for r in chosen if r["label"] == "false")
        total = true + false
        matched = EXPECTED[0] + true
        missing = EXPECTED[1] - true
        extra = EXPECTED[2] + false
        weight_results.append(
            {
                "minWeight": cutoff,
                "selected": total,
                "recoverTrue": true,
                "recoverFalse": false,
                "precision": round(100.0 * true / total, 2) if total else 0.0,
                "candidatePitchF1": score_from_counts(matched, missing, extra),
                "matchedMissingExtra": [matched, missing, extra],
            }
        )

    candidates = vote_results + weight_results
    best_f1 = max(candidates, key=lambda r: (float(r["candidatePitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"])))
    big_jump = [
        r for r in candidates
        if int(r["recoverTrue"]) >= 20 and float(r["candidatePitchF1"]) > EXPECTED_F1
    ]
    best_big = max(big_jump, key=lambda r: (float(r["candidatePitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"]))) if big_jump else None

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during contextual consensus recovery profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "31.61-wide-recall-contextual-consensus-recovery",
        "champion3161Score": baseline,
        "selectedBroadSignatureCount": len(selected),
        "selectedBroadSignatures": selected,
        "candidateCount": len(scored_rows),
        "voteThresholdResults": vote_results,
        "weightThresholdResults": weight_results,
        "bestF1Candidate": best_f1,
        "bestBigJumpCandidate": best_big,
        "candidateRows": scored_rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": baseline["pitchF1"],
        "selectedBroadSignatureCount": len(selected),
        "bestF1Candidate": best_f1,
        "bestBigJumpCandidate": best_big,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 WIDE-RECALL CONTEXTUAL CONSENSUS RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", baseline["pitchF1"])
    print("Champion matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Selected broad contextual signatures:", len(selected))
    print("Vote threshold sweep:")
    for r in vote_results:
        print(
            f"votes>={r['minVotes']}",
            f"true={r['recoverTrue']}",
            f"false={r['recoverFalse']}",
            f"precision={r['precision']}",
            f"F1={r['candidatePitchF1']}",
            f"m/m/e={r['matchedMissingExtra'][0]}/{r['matchedMissingExtra'][1]}/{r['matchedMissingExtra'][2]}",
        )
    print("Weight threshold sweep:")
    for r in weight_results:
        print(
            f"weight>={r['minWeight']}",
            f"true={r['recoverTrue']}",
            f"false={r['recoverFalse']}",
            f"precision={r['precision']}",
            f"F1={r['candidatePitchF1']}",
            f"m/m/e={r['matchedMissingExtra'][0]}/{r['matchedMissingExtra'][1]}/{r['matchedMissingExtra'][2]}",
        )
    print("Best F1 candidate:", best_f1)
    print("Best 20+ true big-jump candidate:", best_big)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
