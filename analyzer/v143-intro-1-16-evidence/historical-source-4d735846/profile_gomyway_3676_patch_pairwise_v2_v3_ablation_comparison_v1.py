from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
V3_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-ablate-lowmiddecay60-nested-cv-v3.json"
OUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v3-ablation-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v3-ablation-comparison-v1-manifest.json"


def rows(payload):
    out = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        for r in payload.get(scheme) or []:
            out[(scheme, int(r.get("fold")))] = r
    return out


def lift(r):
    return float(r.get("heldoutPrecisionLift", 0.0))


def passed(r):
    return bool(r.get("passed"))


def main():
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    v3 = json.loads(V3_PATH.read_text(encoding="utf-8"))
    a = rows(v2)
    b = rows(v3)
    keys = sorted(set(a) & set(b))
    if len(keys) != 15:
        raise RuntimeError(f"Expected 15 matched folds, found {len(keys)}")

    comps = []
    for key in keys:
        r2, r3 = a[key], b[key]
        p2, p3 = passed(r2), passed(r3)
        if p2 and not p3:
            flip = "passToFail"
        elif not p2 and p3:
            flip = "failToPass"
        else:
            flip = "none"
        d = round(lift(r3) - lift(r2), 3)
        outcome = "improved" if d > 1e-9 else ("degraded" if d < -1e-9 else "same")
        row = {
            "scheme": key[0],
            "fold": key[1],
            "v2Passed": p2,
            "v3Passed": p3,
            "v2Lift": round(lift(r2), 3),
            "v3Lift": round(lift(r3), 3),
            "liftDeltaV3MinusV2": d,
            "flip": flip,
            "outcome": outcome,
        }
        comps.append(row)
        print("COMPARE", row)

    summary = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        rs = [r for r in comps if r["scheme"] == scheme]
        summary[scheme] = {
            "folds": len(rs),
            "v2Passes": sum(r["v2Passed"] for r in rs),
            "v3Passes": sum(r["v3Passed"] for r in rs),
            "failToPass": sum(r["flip"] == "failToPass" for r in rs),
            "passToFail": sum(r["flip"] == "passToFail" for r in rs),
            "improved": sum(r["outcome"] == "improved" for r in rs),
            "degraded": sum(r["outcome"] == "degraded" for r in rs),
            "same": sum(r["outcome"] == "same" for r in rs),
            "meanLiftDelta": round(sum(r["liftDeltaV3MinusV2"] for r in rs) / len(rs), 3),
        }
    overall = {
        "folds": 15,
        "v2Passes": sum(r["v2Passed"] for r in comps),
        "v3Passes": sum(r["v3Passed"] for r in comps),
        "failToPass": sum(r["flip"] == "failToPass" for r in comps),
        "passToFail": sum(r["flip"] == "passToFail" for r in comps),
        "improved": sum(r["outcome"] == "improved" for r in comps),
        "degraded": sum(r["outcome"] == "degraded" for r in comps),
        "same": sum(r["outcome"] == "same" for r in comps),
        "meanLiftDelta": round(sum(r["liftDeltaV3MinusV2"] for r in comps) / len(comps), 3),
    }
    hypothesis_supported = bool(overall["v3Passes"] > overall["v2Passes"] and overall["failToPass"] > overall["passToFail"])
    retire_ablation = not hypothesis_supported

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-v3-ablation-comparison",
        "matchedFoldPairs": 15,
        "comparisons": comps,
        "schemeSummary": summary,
        "overall": overall,
        "lowMidDecay60AblationSupported": hypothesis_supported,
        "retireLowMidDecay60Ablation": retire_ablation,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUT_PATH.relative_to(ROOT)),
        "matchedFoldPairs": 15,
        "lowMidDecay60AblationSupported": hypothesis_supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 VS V3 ABLATION COMPARISON V1 COMPLETE")
    print("Matched fold pairs: 15")
    print("SCHEME SUMMARY", summary)
    print("OVERALL", overall)
    print("LowMidDecay60 ablation supported:", hypothesis_supported)
    print("Retire LowMidDecay60 ablation:", retire_ablation)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
