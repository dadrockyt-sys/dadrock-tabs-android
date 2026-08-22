from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V6_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-dense-q-nested-cv-v6.json"
OUT = PUBLIC / "gomyway-3676-patch-pairwise-v5-v6-dense-q-comparison-v1.json"
MANIFEST = PUBLIC / "gomyway-3676-patch-pairwise-v5-v6-dense-q-comparison-v1-manifest.json"
SCHEMES = ["normal", "section", "shiftedWindow"]
NEW_Q = {0.025, 0.125, 0.20}


def rows(payload: dict) -> dict[tuple[str,int], dict]:
    out = {}
    for scheme in SCHEMES:
        vals = payload.get(scheme) or []
        for r in vals:
            out[(scheme, int(r["fold"]))] = r
    return out


def q_of(r: dict) -> float:
    ch = r.get("chosen") or {}
    for k in ("tailQuantile", "q"):
        if k in ch:
            return float(ch[k])
    return float(r.get("q", -1))


def lift_of(r: dict) -> float:
    for k in ("heldoutPrecisionLift", "lift"):
        if k in r:
            return float(r[k])
    held = r.get("heldoutCandidate") or {}
    base = r.get("heldoutBase") or {}
    return float(held.get("precision",0.0)) - float(base.get("precision",0.0))


def main():
    v5 = json.loads(V5_PATH.read_text())
    v6 = json.loads(V6_PATH.read_text())
    a, b = rows(v5), rows(v6)
    keys = sorted(set(a) & set(b))
    print("Matched fold pairs:", len(keys))
    if len(keys) != 15:
        raise RuntimeError(f"Expected 15 matched folds, got {len(keys)}")

    scheme_stats = defaultdict(lambda: Counter(folds=0, v5Passes=0, v6Passes=0, failToPass=0, passToFail=0, improved=0, degraded=0, same=0, newQChosen=0, newQRegressions=0, newQRescues=0))
    overall = Counter(folds=0, v5Passes=0, v6Passes=0, failToPass=0, passToFail=0, improved=0, degraded=0, same=0, newQChosen=0, newQRegressions=0, newQRescues=0)
    comps=[]
    new_q_counts=Counter()
    for key in keys:
        scheme, fold = key
        r5, r6 = a[key], b[key]
        p5, p6 = bool(r5.get("passed")), bool(r6.get("passed"))
        l5, l6 = lift_of(r5), lift_of(r6)
        q5, q6 = q_of(r5), q_of(r6)
        delta = round(l6-l5, 3)
        if (not p5) and p6: flip="failToPass"
        elif p5 and (not p6): flip="passToFail"
        else: flip="none"
        if delta > 1e-9: outcome="improved"
        elif delta < -1e-9: outcome="degraded"
        else: outcome="same"
        item={"scheme":scheme,"fold":fold,"v5Passed":p5,"v6Passed":p6,"v5Lift":round(l5,2),"v6Lift":round(l6,2),"liftDeltaV6MinusV5":delta,"v5Q":q5,"v6Q":q6,"flip":flip,"outcome":outcome,"v6UsesNewQ":q6 in NEW_Q}
        comps.append(item)
        print("COMPARE", item)
        for stat in (scheme_stats[scheme], overall):
            stat["folds"] += 1
            stat["v5Passes"] += int(p5)
            stat["v6Passes"] += int(p6)
            stat[flip] += int(flip != "none")
            stat[outcome] += 1
            if q6 in NEW_Q:
                stat["newQChosen"] += 1
                stat["newQRegressions"] += int(p5 and not p6)
                stat["newQRescues"] += int((not p5) and p6)
        if q6 in NEW_Q:
            new_q_counts[str(q6)] += 1

    summary={k:dict(v) for k,v in scheme_stats.items()}
    for scheme in SCHEMES:
        vals=[c["liftDeltaV6MinusV5"] for c in comps if c["scheme"]==scheme]
        summary[scheme]["meanLiftDelta"] = round(sum(vals)/len(vals),3)
    overall_dict=dict(overall)
    overall_dict["meanLiftDelta"] = round(sum(c["liftDeltaV6MinusV5"] for c in comps)/15,3)

    dense_grid_supported = overall_dict["v6Passes"] > overall_dict["v5Passes"] and overall_dict["passToFail"] <= overall_dict["failToPass"]
    dense_grid_overfit_suspected = overall_dict["v6Passes"] < overall_dict["v5Passes"] and overall_dict["newQRegressions"] >= overall_dict["newQRescues"]
    retire_dense_grid = not dense_grid_supported
    payload={
        "profileType":"36.76-patch-pairwise-v5-v6-dense-q-comparison",
        "matchedFoldPairs":15,
        "schemeSummary":summary,
        "overall":overall_dict,
        "newQChoiceCounts":dict(new_q_counts),
        "denseQGridSupported":dense_grid_supported,
        "denseQOverfitSuspected":dense_grid_overfit_suspected,
        "retireDenseQGrid":retire_dense_grid,
        "validatedNewChampion":False,
        "professionalReferenceUsedDuringDetection":False,
        "candidateEventsModified":False,
        "v7EventsModified":False,
        "rendererModified":False,
        "protectedBaselinesChanged":False,
        "productionSeparatorChanged":False,
        "productionPromotionAllowed":False,
        "comparisons":comps,
    }
    OUT.write_text(json.dumps(payload,indent=2)+"\n")
    MANIFEST.write_text(json.dumps({"output":str(OUT.relative_to(ROOT)),"denseQGridSupported":dense_grid_supported,"denseQOverfitSuspected":dense_grid_overfit_suspected,"retireDenseQGrid":retire_dense_grid,"validatedNewChampion":False,"productionPromotionAllowed":False},indent=2)+"\n")
    print("GOMYWAY 36.76 PATCH PAIRWISE V5 VS V6 DENSE-Q COMPARISON V1 COMPLETE")
    print("SCHEME SUMMARY", summary)
    print("OVERALL", overall_dict)
    print("NEW Q CHOICES", dict(new_q_counts))
    print("Dense-q grid supported:", dense_grid_supported)
    print("Dense-q overfit suspected:", dense_grid_overfit_suspected)
    print("Retire dense-q grid:", retire_dense_grid)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUT.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))

if __name__ == "__main__":
    main()
