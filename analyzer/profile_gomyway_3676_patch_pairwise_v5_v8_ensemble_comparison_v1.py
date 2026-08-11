from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V8_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-ensemble-nested-cv-v8.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v8-ensemble-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v8-ensemble-comparison-v1-manifest.json"
SCHEMES = ["normal", "section", "shiftedWindow"]


def rows_for(payload: dict, scheme: str) -> list[dict]:
    rows = list(payload.get(scheme) or [])
    if len(rows) != 5:
        raise RuntimeError(f"Expected 5 {scheme} folds, found {len(rows)}")
    return sorted(rows, key=lambda r: int(r.get("fold", -1)))


def lift_of(row: dict) -> float:
    for key in ("heldoutPrecisionLift", "lift"):
        if key in row:
            return float(row[key])
    cand = row.get("heldoutCandidate") or {}
    base = row.get("heldoutBase") or {}
    if "precision" in cand and "precision" in base:
        return float(cand["precision"]) - float(base["precision"])
    return 0.0


def chosen_q(row: dict):
    chosen = row.get("chosen") or {}
    for key in ("tailQuantile", "q"):
        if key in chosen:
            return chosen[key]
    for key in ("chosenQ", "q"):
        if key in row:
            return row[key]
    return None


def main() -> None:
    if not V5_PATH.exists():
        raise RuntimeError(f"Missing V5 output: {V5_PATH.relative_to(ROOT)}")
    if not V8_PATH.exists():
        raise RuntimeError(f"Missing V8 output: {V8_PATH.relative_to(ROOT)}")

    v5 = json.loads(V5_PATH.read_text(encoding="utf-8"))
    v8 = json.loads(V8_PATH.read_text(encoding="utf-8"))

    compares: list[dict] = []
    scheme_summary: dict[str, dict] = {}

    for scheme in SCHEMES:
        a_rows = rows_for(v5, scheme)
        b_rows = rows_for(v8, scheme)
        stats = {
            "folds": 5,
            "v5Passes": 0,
            "v8Passes": 0,
            "failToPass": 0,
            "passToFail": 0,
            "improved": 0,
            "degraded": 0,
            "same": 0,
            "meanLiftDelta": 0.0,
        }
        deltas: list[float] = []
        for a, b in zip(a_rows, b_rows):
            if int(a.get("fold", -1)) != int(b.get("fold", -2)):
                raise RuntimeError(f"Fold mismatch in {scheme}")
            a_pass = bool(a.get("passed"))
            b_pass = bool(b.get("passed"))
            a_lift = lift_of(a)
            b_lift = lift_of(b)
            delta = b_lift - a_lift
            if (not a_pass) and b_pass:
                flip = "failToPass"
                outcome = "improved"
            elif a_pass and (not b_pass):
                flip = "passToFail"
                outcome = "degraded"
            else:
                flip = "none"
                if delta > 1e-9:
                    outcome = "improved"
                elif delta < -1e-9:
                    outcome = "degraded"
                else:
                    outcome = "same"
            stats["v5Passes"] += int(a_pass)
            stats["v8Passes"] += int(b_pass)
            if flip == "failToPass":
                stats["failToPass"] += 1
            elif flip == "passToFail":
                stats["passToFail"] += 1
            stats[outcome] += 1
            deltas.append(delta)
            row = {
                "scheme": scheme,
                "fold": int(a["fold"]),
                "v5Passed": a_pass,
                "v8Passed": b_pass,
                "v5Lift": round(a_lift, 2),
                "v8Lift": round(b_lift, 2),
                "liftDeltaV8MinusV5": round(delta, 2),
                "v5Q": chosen_q(a),
                "v8Q": chosen_q(b),
                "flip": flip,
                "outcome": outcome,
            }
            compares.append(row)
            print("COMPARE", row)
        stats["meanLiftDelta"] = round(sum(deltas) / len(deltas), 3)
        scheme_summary[scheme] = stats

    matched = len(compares)
    if matched != 15:
        raise RuntimeError(f"Expected 15 matched fold pairs, found {matched}")

    overall = {
        "folds": 15,
        "v5Passes": sum(int(r["v5Passed"]) for r in compares),
        "v8Passes": sum(int(r["v8Passed"]) for r in compares),
        "failToPass": sum(r["flip"] == "failToPass" for r in compares),
        "passToFail": sum(r["flip"] == "passToFail" for r in compares),
        "improved": sum(r["outcome"] == "improved" for r in compares),
        "degraded": sum(r["outcome"] == "degraded" for r in compares),
        "same": sum(r["outcome"] == "same" for r in compares),
        "meanLiftDelta": round(sum(float(r["liftDeltaV8MinusV5"]) for r in compares) / 15.0, 3),
    }

    unique_rescues = int(overall["failToPass"])
    collateral_losses = int(overall["passToFail"])
    ensemble_has_unique_rescue = unique_rescues > 0
    ensemble_net_help = unique_rescues > collateral_losses and int(overall["v8Passes"]) > int(overall["v5Passes"])
    ensemble_supported = ensemble_net_help

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-v8-ensemble-comparison",
        "matchedFoldPairs": matched,
        "schemeSummary": scheme_summary,
        "overall": overall,
        "compares": compares,
        "uniqueV5FailureRescues": unique_rescues,
        "collateralV5PassLosses": collateral_losses,
        "ensembleHasUniqueRescue": ensemble_has_unique_rescue,
        "ensembleNetHelp": ensemble_net_help,
        "ensembleV8Supported": ensemble_supported,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "matchedFoldPairs": matched,
        "v5Passes": overall["v5Passes"],
        "v8Passes": overall["v8Passes"],
        "ensembleV8Supported": ensemble_supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 VS V8 ENSEMBLE COMPARISON V1 COMPLETE")
    print("Matched fold pairs:", matched)
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Unique V5-failure rescues:", unique_rescues)
    print("Collateral V5-pass losses:", collateral_losses)
    print("Ensemble has unique rescue:", ensemble_has_unique_rescue)
    print("Ensemble net help:", ensemble_net_help)
    print("Ensemble V8 supported:", ensemble_supported)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
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
