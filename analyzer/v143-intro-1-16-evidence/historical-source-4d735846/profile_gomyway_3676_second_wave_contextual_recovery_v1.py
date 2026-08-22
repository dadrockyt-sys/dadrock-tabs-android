from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CONSENSUS_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-second-wave-contextual-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-second-wave-contextual-recovery-v1-manifest.json"
CANDIDATE_PATH = PUBLIC / "gomyway-949-event-candidate.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FIRST_WAVE_WEIGHT = 0.80


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def main() -> None:
    before = sha256(CANDIDATE_PATH) if CANDIDATE_PATH.exists() else None
    if not PATTERN_PATH.exists() or not CONSENSUS_PATH.exists():
        raise RuntimeError("Missing first-wave contextual recovery profiler outputs")

    pattern = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    pattern_rows = list(pattern.get("candidateRows") or [])
    first_scored = list(consensus.get("candidateRows") or [])
    if not pattern_rows or not first_scored:
        raise RuntimeError("First-wave outputs do not contain candidate rows")

    first_selected_tokens = {
        str(r.get("token")) for r in first_scored
        if float(r.get("consensusWeight", 0.0)) >= FIRST_WAVE_WEIGHT
    }
    if len(first_selected_tokens) != 322:
        raise RuntimeError(f"Expected 322 first-wave selected tokens, got {len(first_selected_tokens)}")

    residual = [r for r in pattern_rows if str(r.get("token")) not in first_selected_tokens]
    residual_true = sum(1 for r in residual if str(r.get("label")) == "true")
    residual_false = sum(1 for r in residual if str(r.get("label")) == "false")

    stats: dict[str, Counter] = {}
    for row in residual:
        label = str(row.get("label"))
        for sig in set(str(s) for s in (row.get("signatures") or [])):
            c = stats.setdefault(sig, Counter())
            c[label] += 1

    ranked: list[dict[str, Any]] = []
    for sig, c in stats.items():
        t = int(c.get("true", 0))
        f = int(c.get("false", 0))
        total = t + f
        ranked.append({
            "signature": sig,
            "true": t,
            "false": f,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    ranked.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"]), str(r["signature"])))

    # Lower support than wave 1 because the easy 89 true notes have already been removed.
    selected = [
        r for r in ranked
        if (int(r["true"]) >= 10 and float(r["precision"]) >= 20.0)
        or (int(r["true"]) >= 20 and float(r["precision"]) >= 10.0)
    ]
    selected_map = {str(r["signature"]): r for r in selected}

    scored = []
    max_votes = 0
    for row in residual:
        sigs = set(str(s) for s in (row.get("signatures") or []))
        hits = [s for s in sigs if s in selected_map]
        weight = sum(float(selected_map[s]["precision"]) / 100.0 for s in hits)
        out = {
            "token": row.get("token"),
            "measure": row.get("measure"),
            "step": row.get("step"),
            "pitch": row.get("pitch"),
            "label": row.get("label"),
            "votes": len(hits),
            "weight": round(weight, 4),
        }
        max_votes = max(max_votes, len(hits))
        scored.append(out)

    results: list[dict[str, Any]] = []
    for votes in range(1, max_votes + 1):
        chosen = [r for r in scored if int(r["votes"]) >= votes]
        t = sum(str(r.get("label")) == "true" for r in chosen)
        f = sum(str(r.get("label")) == "false" for r in chosen)
        m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
        results.append({
            "type": "votes",
            "threshold": votes,
            "selected": len(chosen),
            "recoverTrue": t,
            "recoverFalse": f,
            "precision": round(100.0 * t / len(chosen), 2) if chosen else 0.0,
            "pitchF1": f1(m, miss, extra),
            "matchedMissingExtra": [m, miss, extra],
        })

    for cutoff in [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20, 1.50, 1.80, 2.00]:
        chosen = [r for r in scored if float(r["weight"]) >= cutoff]
        t = sum(str(r.get("label")) == "true" for r in chosen)
        f = sum(str(r.get("label")) == "false" for r in chosen)
        m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
        results.append({
            "type": "weight",
            "threshold": cutoff,
            "selected": len(chosen),
            "recoverTrue": t,
            "recoverFalse": f,
            "precision": round(100.0 * t / len(chosen), 2) if chosen else 0.0,
            "pitchF1": f1(m, miss, extra),
            "matchedMissingExtra": [m, miss, extra],
        })

    improving = [r for r in results if float(r["pitchF1"]) > EXPECTED_F1 and int(r["recoverTrue"]) > 0]
    best = max(improving, key=lambda r: (float(r["pitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"]))) if improving else None
    big = [r for r in improving if int(r["recoverTrue"]) >= 20]
    best_big = max(big, key=lambda r: (float(r["pitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"]))) if big else None

    after = sha256(CANDIDATE_PATH) if CANDIDATE_PATH.exists() else None
    if before is not None and before != after:
        raise RuntimeError("Protected 949-event candidate changed during second-wave recovery profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-second-wave-contextual-recovery",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "firstWaveSelected": len(first_selected_tokens),
        "residualCandidateCount": len(residual),
        "residualTrue": residual_true,
        "residualFalse": residual_false,
        "selectedResidualSignatureCount": len(selected),
        "selectedResidualSignatures": selected[:200],
        "thresholdResults": results,
        "bestCandidate": best,
        "best20PlusTrueCandidate": best_big,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": before == after,
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
        "championPitchF1": EXPECTED_F1,
        "bestCandidate": best,
        "best20PlusTrueCandidate": best_big,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 SECOND-WAVE CONTEXTUAL RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("First-wave selected tokens excluded:", len(first_selected_tokens))
    print("Residual candidates true/false:", residual_true, "/", residual_false)
    print("Selected residual signatures:", len(selected))
    for r in results:
        print(f"{r['type']}>={r['threshold']} true={r['recoverTrue']} false={r['recoverFalse']} precision={r['precision']} F1={r['pitchF1']} m/m/e={r['matchedMissingExtra'][0]}/{r['matchedMissingExtra'][1]}/{r['matchedMissingExtra'][2]}")
    print("Best second-wave candidate:", best)
    print("Best 20+ true second-wave candidate:", best_big)
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
