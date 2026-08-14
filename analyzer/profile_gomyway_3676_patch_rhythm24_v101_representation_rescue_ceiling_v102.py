from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v100-representation-rescue-counterfactual-v101.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v101-representation-rescue-ceiling-v102.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v101-representation-rescue-ceiling-v102-manifest.json"

ALT_REPS = ("full_phase", "phase_col3", "base")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    d = json.loads(INPUT_PATH.read_text())
    rows = list(d.get("rows") or [])
    baseline = d.get("baseline") or {}
    if not rows:
        raise RuntimeError("V101 rows missing; run and preserve V101 first")

    total = len(rows)
    current_passes = sum(int(bool(r.get("v96Passed"))) for r in rows)
    failures = [r for r in rows if not bool(r.get("v96Passed"))]

    rescue_sets = {rep: set() for rep in ALT_REPS}
    loss_sets = {rep: set() for rep in ALT_REPS}
    pattern_counts = Counter()
    rescue_rows = []

    for idx, r in enumerate(rows):
        rep_passes = r.get("representationPasses") or {}
        current = bool(r.get("v96Passed"))
        bits = []
        for rep in ALT_REPS:
            p = bool(rep_passes.get(rep, current))
            if (not current) and p:
                rescue_sets[rep].add(idx)
            if current and (not p):
                loss_sets[rep].add(idx)
            bits.append(f"{rep}={int(p)}")
        if not current:
            pattern_counts["|".join(bits)] += 1
            rescued_by = [rep for rep in ALT_REPS if idx in rescue_sets[rep]]
            if rescued_by:
                rescue_rows.append({
                    "source": r.get("source"),
                    "phase": r.get("phase"),
                    "fold": r.get("fold"),
                    "decision": r.get("decision"),
                    "pairRadius": r.get("pairRadius"),
                    "lambda": r.get("lambda"),
                    "rescuedBy": rescued_by,
                    "v28Passed": bool(r.get("v28Passed")),
                })

    oracle_rescued = set().union(*(rescue_sets[rep] for rep in ALT_REPS))
    oracle_passes = current_passes + len(oracle_rescued)

    # A conservative practical ceiling: only allow a representation switch on a
    # structural (decision, radius, lambda) group if that representation has
    # more rescues than losses in that same group. This is diagnostic only and
    # is NOT a deployable selector or a tuned policy.
    grouped = defaultdict(lambda: {rep: {"rows": 0, "rescues": 0, "losses": 0} for rep in ALT_REPS})
    for idx, r in enumerate(rows):
        key = (str(r.get("decision")), r.get("pairRadius"), r.get("lambda"))
        current = bool(r.get("v96Passed"))
        rep_passes = r.get("representationPasses") or {}
        for rep in ALT_REPS:
            p = bool(rep_passes.get(rep, current))
            g = grouped[key][rep]
            g["rows"] += 1
            g["rescues"] += int((not current) and p)
            g["losses"] += int(current and (not p))

    positive_groups = []
    for key, by_rep in grouped.items():
        for rep, s in by_rep.items():
            net = s["rescues"] - s["losses"]
            if s["rescues"] > 0:
                positive_groups.append({
                    "decision": key[0],
                    "pairRadius": key[1],
                    "lambda": key[2],
                    "representation": rep,
                    **s,
                    "net": net,
                })
    positive_groups.sort(key=lambda x: (-x["net"], -x["rescues"], x["losses"], str(x["decision"])))

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V102")

    summary = {
        "rows": total,
        "v96Passes": current_passes,
        "v96ScorePercent": round(100.0 * current_passes / total, 4),
        "v96Failures": len(failures),
        "rescuedFailuresByRepresentation": {rep: len(rescue_sets[rep]) for rep in ALT_REPS},
        "lossesByRepresentation": {rep: len(loss_sets[rep]) for rep in ALT_REPS},
        "oracleUnionRescuedFailures": len(oracle_rescued),
        "oracleUnionPasses": oracle_passes,
        "oracleUnionScorePercent": round(100.0 * oracle_passes / total, 4),
        "remainingFailuresEvenWithPerfectPerFoldRepresentationOracle": len(failures) - len(oracle_rescued),
        "failureRescuePatterns": dict(pattern_counts),
    }

    out = {
        "schemaVersion": 102,
        "profileType": "saved-v101-representation-rescue-oracle-ceiling-diagnostic",
        "summary": summary,
        "positiveStructuralGroups": positive_groups,
        "rescueRows": rescue_rows,
        "usesSavedV101Only": True,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rescueRows"}, indent=2) + "\n")

    print("GOMYWAY V102 REPRESENTATION RESCUE CEILING DIAGNOSTIC COMPLETE")
    print(f"Jimmy exposed V96 scoreboard: {current_passes}/{total} = {100.0*current_passes/total:.4f}%")
    print(f"Failures: {len(failures)}")
    for rep in ALT_REPS:
        print(f"{rep}: rescues={len(rescue_sets[rep])} losses={len(loss_sets[rep])}")
    print(f"Perfect per-fold representation oracle: {oracle_passes}/{total} = {100.0*oracle_passes/total:.4f}%")
    print(f"Failures not rescued by ANY tested representation: {len(failures)-len(oracle_rescued)}")
    print("\n=== FAILURE RESCUE PATTERNS ===")
    for k, v in pattern_counts.most_common():
        print(k, v)
    print("\n=== STRUCTURAL GROUPS WITH AT LEAST ONE RESCUE ===")
    for g in positive_groups:
        print(g)
    print("\nUses saved V101 only: True")
    print("V97 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
