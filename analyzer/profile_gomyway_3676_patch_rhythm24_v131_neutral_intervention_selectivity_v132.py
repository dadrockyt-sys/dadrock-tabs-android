from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V128_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
V131_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v130-structural-representation-utility-v131.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v131-neutral-intervention-selectivity-v132.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v131-neutral-intervention-selectivity-v132-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_tuple(d: dict) -> tuple[str, str, int, float]:
    return (
        str(d.get("originalQBucket")),
        str(d.get("v96Decision")),
        int(d.get("pairRadius")),
        float(d.get("lambda")),
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v128 = json.loads(V128_PATH.read_text(encoding="utf-8"))
    v131 = json.loads(V131_PATH.read_text(encoding="utf-8"))
    if int(v128.get("schemaVersion", -1)) != 128 or not bool(v128.get("validatedNewChampion")):
        raise RuntimeError("Validated V128 output required")
    if int(v128.get("v128Passes", -1)) != 309 or int(v128.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V128 must match frozen 309/320 champion")
    if int(v131.get("schemaVersion", -1)) != 131:
        raise RuntimeError("V131 structural utility diagnostic required")

    # Only inspect interventions that actually rescue exposed failures and are
    # near neutral on all consumed V128 rows. This remains diagnostic only.
    targets = []
    for r in v131.get("interventionUtility") or []:
        if int(r.get("gains", 0)) > 0 and int(r.get("net", -999)) >= -1:
            targets.append(r)
    targets.sort(key=lambda r: (-int(r.get("net", 0)), -int(r.get("gains", 0)), int(r.get("losses", 0))))
    if not targets:
        raise RuntimeError("No near-neutral V131 interventions with gains found")

    # Saved V128 rows supply only frozen/pre-heldout state for diagnostic
    # stratification (gate score, V112 selection, policy state, phase/fold).
    v128_rows = {}
    for scheme in v128.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            v128_rows[(round(phase, 12), int(r.get("fold")))] = r

    rows_by_key = defaultdict(list)
    for rr in v131.get("rowResults") or []:
        sk = rr.get("structuralKey") or {}
        rows_by_key[key_tuple(sk)].append(rr)

    diagnostics = []
    print("GOMYWAY V132 NEAR-NEUTRAL INTERVENTION SELECTIVITY DIAGNOSTIC", flush=True)
    print("Uses consumed V128/V131 outcomes only; untouched reserve remains sealed", flush=True)

    for t in targets:
        skey = key_tuple(t)
        rep = str(t.get("representation"))
        changed = []
        all_rows = []
        for rr in rows_by_key.get(skey, []):
            cand = (rr.get("candidateRepresentations") or {}).get(rep)
            if cand is None:
                continue
            phase = float(rr.get("phase"))
            fold = int(rr.get("fold"))
            src = v128_rows.get((round(phase, 12), fold)) or {}
            base = bool(rr.get("baselineV128Passed"))
            cp = bool(cand.get("passed"))
            state = "gain" if cp and not base else "loss" if base and not cp else "both-pass" if base and cp else "both-fail"
            row = {
                "phase": phase,
                "fold": fold,
                "state": state,
                "gateScore": src.get("gateScore"),
                "selectedForV112": bool(src.get("selectedForV112", False)),
                "baselineFinalRepresentation": rr.get("baselineFinalRepresentation"),
                "heldoutPrecisionLift": src.get("heldoutPrecisionLift"),
            }
            all_rows.append(row)
            if state in ("gain", "loss"):
                changed.append(row)

        by_selected = defaultdict(Counter)
        by_baseline_rep = defaultdict(Counter)
        for r in all_rows:
            by_selected[str(r["selectedForV112"])][r["state"]] += 1
            by_baseline_rep[str(r.get("baselineFinalRepresentation"))][r["state"]] += 1

        gains = [r for r in changed if r["state"] == "gain"]
        losses = [r for r in changed if r["state"] == "loss"]
        def rng(xs, field):
            vals = [float(r[field]) for r in xs if r.get(field) is not None]
            return [min(vals), max(vals)] if vals else None

        diag = {
            "structuralKey": {
                "originalQBucket": skey[0],
                "v96Decision": skey[1],
                "pairRadius": skey[2],
                "lambda": skey[3],
            },
            "representation": rep,
            "v131Utility": {
                "rows": int(t.get("rows", 0)),
                "gains": int(t.get("gains", 0)),
                "losses": int(t.get("losses", 0)),
                "net": int(t.get("net", 0)),
            },
            "gainGateScoreRange": rng(gains, "gateScore"),
            "lossGateScoreRange": rng(losses, "gateScore"),
            "gainPhaseRange": rng(gains, "phase"),
            "lossPhaseRange": rng(losses, "phase"),
            "changedRows": sorted(changed, key=lambda r: (float("inf") if r.get("gateScore") is None else float(r["gateScore"]), r["phase"], r["fold"])),
            "statesBySelectedForV112": {k: dict(v) for k, v in by_selected.items()},
            "statesByBaselineRepresentation": {k: dict(v) for k, v in by_baseline_rep.items()},
        }
        diagnostics.append(diag)

        print("\n=== TARGET INTERVENTION ===")
        print(diag["structuralKey"], "representation=", rep)
        print("utility:", diag["v131Utility"])
        print("gain gate-score range:", diag["gainGateScoreRange"])
        print("loss gate-score range:", diag["lossGateScoreRange"])
        print("gain phase range:", diag["gainPhaseRange"])
        print("loss phase range:", diag["lossPhaseRange"])
        print("states by selectedForV112:", diag["statesBySelectedForV112"])
        print("states by baseline representation:", diag["statesByBaselineRepresentation"])
        print("--- changed rows sorted by gate score ---")
        for r in diag["changedRows"]:
            print(r)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V132")

    out = {
        "schemaVersion": 132,
        "profileType": "consumed-v128-near-neutral-intervention-selectivity-diagnostic",
        "frozenV128Passes": 309,
        "frozenV128ScorePercent": 96.5625,
        "targetInterventionCount": len(diagnostics),
        "diagnostics": diagnostics,
        "usesHeldoutLabelsForDiagnosisOnly": True,
        "heldoutPrecisionLiftNeverProposedAsGuardFeature": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "diagnostics"}, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V132 SELECTIVITY DIAGNOSTIC COMPLETE")
    print(f"Near-neutral interventions inspected: {len(diagnostics)}")
    print("Important: no guard or threshold has been chosen; V132 is anatomy only")
    print("New reserved phase family referenced: False")
    print("Candidate policy changed: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
