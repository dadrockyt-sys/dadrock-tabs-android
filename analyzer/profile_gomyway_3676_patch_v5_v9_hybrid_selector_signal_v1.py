from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V9_PATH = PUBLIC / "gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-selector-signal-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-selector-signal-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        for row in payload.get(scheme, []) or []:
            out[(scheme, int(row["fold"]))] = row
    return out


def num(d: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(d.get(key, default))
    except Exception:
        return float(default)


def inner_signature(row: dict[str, Any]) -> dict[str, float]:
    chosen = dict(row.get("chosen") or {})
    return {
        "sectionPassCount": num(chosen, "sectionPassCount"),
        "sectionMeanLift": num(chosen, "sectionMeanLift"),
        "overallPassCount": num(chosen, "overallPassCount"),
        "overallMeanLift": num(chosen, "overallMeanLift"),
        "tailQuantile": num(chosen, "tailQuantile"),
    }


def signal_flags(v5s: dict[str, float], v9s: dict[str, float]) -> dict[str, bool]:
    d_section_pass = v9s["sectionPassCount"] - v5s["sectionPassCount"]
    d_section_lift = v9s["sectionMeanLift"] - v5s["sectionMeanLift"]
    d_overall_pass = v9s["overallPassCount"] - v5s["overallPassCount"]
    d_overall_lift = v9s["overallMeanLift"] - v5s["overallMeanLift"]

    # Predeclared rules only. These thresholds are fixed before held-out outcomes are graded.
    return {
        "v9HigherSectionPass": d_section_pass >= 1.0,
        "v9HigherOverallPass": d_overall_pass >= 1.0,
        "v9SectionLiftPlus2": d_section_lift >= 2.0,
        "v9OverallLiftPlus2": d_overall_lift >= 2.0,
        "v9SectionAndOverallLiftPlus2": d_section_lift >= 2.0 and d_overall_lift >= 2.0,
        "v9PassOrStrongLift": d_section_pass >= 1.0 or (d_section_lift >= 3.0 and d_overall_lift >= 2.0),
        "v9LexicographicInnerDominance": (
            v9s["sectionPassCount"],
            v9s["sectionMeanLift"],
            v9s["overallPassCount"],
            v9s["overallMeanLift"],
        ) > (
            v5s["sectionPassCount"],
            v5s["sectionMeanLift"],
            v5s["overallPassCount"],
            v5s["overallMeanLift"],
        ),
    }


def main() -> None:
    v5 = json.loads(V5_PATH.read_text(encoding="utf-8"))
    v9 = json.loads(V9_PATH.read_text(encoding="utf-8"))

    if tuple(v5.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("V5 output not anchored to frozen 36.76 champion")
    if tuple(v9.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("V9 output not anchored to frozen 36.76 champion")

    a = flatten(v5)
    b = flatten(v9)
    if set(a) != set(b) or len(a) != 15:
        raise RuntimeError(f"Expected 15 matched V5/V9 folds, got {len(a)} and {len(b)}")

    rows: list[dict[str, Any]] = []
    signal_names: list[str] | None = None
    for key in sorted(a):
        r5, r9 = a[key], b[key]
        s5, s9 = inner_signature(r5), inner_signature(r9)
        flags = signal_flags(s5, s9)
        if signal_names is None:
            signal_names = list(flags)
        p5 = bool(r5.get("passed"))
        p9 = bool(r9.get("passed"))
        if (not p5) and p9:
            outcome = "v9OnlyRescue"
        elif p5 and (not p9):
            outcome = "v5OnlyCollateralLoss"
        elif p5 and p9:
            outcome = "bothPass"
        else:
            outcome = "bothFail"
        rows.append({
            "scheme": key[0],
            "fold": key[1],
            "v5Passed": p5,
            "v9Passed": p9,
            "outcome": outcome,
            "v5Inner": s5,
            "v9Inner": s9,
            "deltasV9MinusV5": {k: round(s9[k] - s5[k], 3) for k in s5},
            "signals": flags,
        })

    signal_summary: dict[str, Any] = {}
    useful: list[str] = []
    for name in signal_names or []:
        selected = [r for r in rows if bool(r["signals"][name])]
        rescue_hits = sum(r["outcome"] == "v9OnlyRescue" for r in selected)
        collateral_hits = sum(r["outcome"] == "v5OnlyCollateralLoss" for r in selected)
        both_pass_hits = sum(r["outcome"] == "bothPass" for r in selected)
        both_fail_hits = sum(r["outcome"] == "bothFail" for r in selected)
        # With only one rescue, demand exact rescue capture and zero collateral losses.
        ready = rescue_hits == 1 and collateral_hits == 0
        if ready:
            useful.append(name)
        signal_summary[name] = {
            "selectedFolds": len(selected),
            "rescueHits": rescue_hits,
            "collateralLossHits": collateral_hits,
            "bothPassHits": both_pass_hits,
            "bothFailHits": both_fail_hits,
            "isolatesRescueWithoutCollateral": ready,
        }

    v5_passes = sum(bool(r["v5Passed"]) for r in rows)
    v9_passes = sum(bool(r["v9Passed"]) for r in rows)
    oracle_union = sum(bool(r["v5Passed"] or r["v9Passed"]) for r in rows)
    unique_rescues = sum(r["outcome"] == "v9OnlyRescue" for r in rows)
    collateral = sum(r["outcome"] == "v5OnlyCollateralLoss" for r in rows)
    hybrid_signal_ready = len(useful) > 0

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v5-v9-hybrid-selector-signal-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "matchedFolds": len(rows),
        "v5Passes": v5_passes,
        "v9Passes": v9_passes,
        "oracleUnionPasses": oracle_union,
        "uniqueV9Rescues": unique_rescues,
        "collateralV5PassLosses": collateral,
        "predeclaredSignalSummary": signal_summary,
        "usefulSignals": useful,
        "hybridSelectorSignalReady": hybrid_signal_ready,
        "nextTarget": (
            "strict-training-only-v5-v9-hybrid-selector-cv" if hybrid_signal_ready
            else "no-reliable-hybrid-selector-signal-retire-v9-complementarity"
        ),
        "folds": rows,
        "validatedNewChampion": False,
        "professionalReferenceUsedToChooseHybrid": False,
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
        "v5Passes": v5_passes,
        "v9Passes": v9_passes,
        "oracleUnionPasses": oracle_union,
        "hybridSelectorSignalReady": hybrid_signal_ready,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V5/V9 HYBRID SELECTOR SIGNAL V1 COMPLETE")
    print("Matched folds:", len(rows))
    print("V5 passes:", v5_passes)
    print("V9 passes:", v9_passes)
    print("Oracle V5-or-V9 union passes:", oracle_union, "/ 15")
    print("Unique V9 rescues:", unique_rescues)
    print("Collateral V5-pass losses under V9:", collateral)
    print("PREDECLARED SIGNAL SUMMARY")
    for name, stats in signal_summary.items():
        print("SIGNAL", name, stats)
    print("Useful signals:", useful)
    print("Hybrid selector signal ready:", hybrid_signal_ready)
    print("Next target:", output["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used to choose hybrid: False")
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
