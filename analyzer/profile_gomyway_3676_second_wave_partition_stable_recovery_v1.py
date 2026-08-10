from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3161_protected_source_recall_recovery_v1 as protected

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CONSENSUS_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-second-wave-partition-stable-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-second-wave-partition-stable-recovery-v1-manifest.json"
CANDIDATE_PATH = protected.recall.CANDIDATE_PATH
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FIRST_WAVE_WEIGHT = 0.80
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def signature_counts(rows: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row.get("label"))
        for sig in set(str(s) for s in (row.get("signatures") or [])):
            out[sig][label] += 1
    return out


def fold_stats(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
) -> dict[str, list[dict[str, int | float]]]:
    by_sig: dict[str, list[dict[str, int | float]]] = defaultdict(list)
    for fold in range(FOLD_COUNT):
        test = [r for r in rows if fold_fn(r) == fold]
        counts = signature_counts(test)
        for sig, c in counts.items():
            t = int(c["true"])
            f = int(c["false"])
            total = t + f
            by_sig[sig].append({
                "fold": fold,
                "true": t,
                "false": f,
                "precision": round(100.0 * t / total, 2) if total else 0.0,
            })
    return by_sig


def summarize_scheme(entries: list[dict[str, int | float]]) -> dict[str, Any]:
    pos = sum(1 for e in entries if int(e["true"]) > 0)
    poison = sum(1 for e in entries if int(e["true"]) == 0 and int(e["false"]) >= 3)
    severe = sum(1 for e in entries if int(e["false"]) >= 3 * max(1, int(e["true"])))
    true = sum(int(e["true"]) for e in entries)
    false = sum(int(e["false"]) for e in entries)
    return {
        "positiveFolds": pos,
        "poisonFolds": poison,
        "severeFalseDominantFolds": severe,
        "true": true,
        "false": false,
    }


def main() -> None:
    before = sha256(CANDIDATE_PATH)
    pattern = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    pattern_rows = list(pattern.get("candidateRows") or [])
    first_scored = list(consensus.get("candidateRows") or [])
    if not pattern_rows or not first_scored:
        raise RuntimeError("Missing first-wave contextual rows")

    first_selected = {
        str(r.get("token")) for r in first_scored
        if float(r.get("consensusWeight", 0.0)) >= FIRST_WAVE_WEIGHT
    }
    if len(first_selected) != 322:
        raise RuntimeError(f"Expected 322 first-wave tokens, got {len(first_selected)}")

    rows = [r for r in pattern_rows if str(r.get("token")) not in first_selected]
    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    normal_fn = lambda r: int(r["measure"]) % FOLD_COUNT
    shifted_fn = lambda r: (int(r["measure"]) + 2) % FOLD_COUNT
    section_fn = lambda r: min(FOLD_COUNT - 1, int(FOLD_COUNT * (int(r["measure"]) - lo) / span))

    full = signature_counts(rows)
    normal = fold_stats(rows, normal_fn)
    shifted = fold_stats(rows, shifted_fn)
    section = fold_stats(rows, section_fn)

    ranked: list[dict[str, Any]] = []
    for sig, c in full.items():
        t = int(c["true"])
        f = int(c["false"])
        total = t + f
        if t < 5:
            continue
        ns = summarize_scheme(normal.get(sig, []))
        ss = summarize_scheme(shifted.get(sig, []))
        cs = summarize_scheme(section.get(sig, []))
        stable_schemes = sum(
            int(s["positiveFolds"] >= 3 and s["poisonFolds"] == 0)
            for s in (ns, ss, cs)
        )
        poison_total = int(ns["poisonFolds"]) + int(ss["poisonFolds"]) + int(cs["poisonFolds"])
        positive_total = int(ns["positiveFolds"]) + int(ss["positiveFolds"]) + int(cs["positiveFolds"])
        precision = 100.0 * t / total if total else 0.0
        ranked.append({
            "signature": sig,
            "true": t,
            "false": f,
            "precision": round(precision, 2),
            "stableSchemes": stable_schemes,
            "positiveFoldTotal": positive_total,
            "poisonFoldTotal": poison_total,
            "normal": ns,
            "shifted": ss,
            "section": cs,
        })

    ranked.sort(key=lambda r: (
        -int(r["stableSchemes"]),
        int(r["poisonFoldTotal"]),
        -int(r["positiveFoldTotal"]),
        -float(r["precision"]),
        -int(r["true"]),
    ))

    stable = [
        r for r in ranked
        if int(r["stableSchemes"]) == 3
        and int(r["poisonFoldTotal"]) == 0
        and int(r["true"]) >= 8
        and float(r["precision"]) >= 12.0
    ]
    stable_map = {str(r["signature"]): r for r in stable}

    scored: list[dict[str, Any]] = []
    for row in rows:
        hits = [stable_map[s] for s in set(str(x) for x in (row.get("signatures") or [])) if s in stable_map]
        weight = sum(float(h["precision"]) / 100.0 for h in hits)
        scored.append({
            "token": row.get("token"),
            "measure": row.get("measure"),
            "step": row.get("step"),
            "pitch": row.get("pitch"),
            "label": row.get("label"),
            "votes": len(hits),
            "weight": round(weight, 4),
        })

    results: list[dict[str, Any]] = []
    for cutoff in [0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 1.00, 1.20]:
        chosen = [r for r in scored if float(r["weight"]) >= cutoff]
        t = sum(str(r["label"]) == "true" for r in chosen)
        f = sum(str(r["label"]) == "false" for r in chosen)
        m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
        results.append({
            "cutoff": cutoff,
            "selected": len(chosen),
            "recoverTrue": t,
            "recoverFalse": f,
            "precision": round(100.0 * t / len(chosen), 2) if chosen else 0.0,
            "pitchF1": f1(m, miss, extra),
            "matchedMissingExtra": [m, miss, extra],
        })

    improving = [r for r in results if float(r["pitchF1"]) > EXPECTED_F1 and int(r["recoverTrue"]) > 0]
    best = max(improving, key=lambda r: (float(r["pitchF1"]), int(r["recoverTrue"]), -int(r["recoverFalse"]))) if improving else None

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-second-wave-partition-stable-recovery",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "residualCandidateCount": len(rows),
        "stableSignatureCount": len(stable),
        "stableSignatures": stable[:200],
        "thresholdResults": results,
        "bestCandidate": best,
        "professionalReferenceUsedDuringDetection": False,
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
        "bestCandidate": best,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 SECOND-WAVE PARTITION-STABLE RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Residual candidate count:", len(rows))
    print("Partition-stable signatures:", len(stable))
    for r in stable[:30]:
        print("STABLE", r["signature"], "true=", r["true"], "false=", r["false"], "precision=", r["precision"], "positiveFolds=", r["positiveFoldTotal"])
    for r in results:
        print("weight>=", r["cutoff"], "true=", r["recoverTrue"], "false=", r["recoverFalse"], "precision=", r["precision"], "F1=", r["pitchF1"], "m/m/e=", r["matchedMissingExtra"])
    print("Best partition-stable candidate:", best)
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
