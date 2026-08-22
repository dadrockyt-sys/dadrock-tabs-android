from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V10_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v5-v10-hybrid-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v5-v10-hybrid-comparison-v1-manifest.json"
SCHEMES = ("normal", "section", "shiftedWindow")


def rows_by_key(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in SCHEMES:
        for row in payload.get(scheme, []):
            key = (scheme, int(row["fold"]))
            if key in out:
                raise RuntimeError(f"Duplicate fold row: {key}")
            out[key] = row
    return out


def summarize(rows: list[dict[str, Any]], prefix: str) -> dict[str, Any]:
    return {
        "folds": len(rows),
        f"{prefix}Passes": sum(bool(r[f"{prefix}Passed"]) for r in rows),
        "failToPass": sum(r["flip"] == "failToPass" for r in rows),
        "passToFail": sum(r["flip"] == "passToFail" for r in rows),
        "samePass": sum(r["flip"] == "samePass" for r in rows),
        "sameFail": sum(r["flip"] == "sameFail" for r in rows),
        "meanLiftDelta": round(sum(float(r["liftDeltaV10MinusV5"]) for r in rows) / max(1, len(rows)), 3),
    }


def main() -> None:
    if not V5_PATH.exists():
        raise RuntimeError(f"Missing V5 output: {V5_PATH.relative_to(ROOT)}")
    if not V10_PATH.exists():
        raise RuntimeError(f"Missing V10 output: {V10_PATH.relative_to(ROOT)}")

    v5 = json.loads(V5_PATH.read_text(encoding="utf-8"))
    v10 = json.loads(V10_PATH.read_text(encoding="utf-8"))
    a = rows_by_key(v5)
    b = rows_by_key(v10)
    if set(a) != set(b):
        raise RuntimeError(f"Fold-key mismatch: V5={sorted(a)} V10={sorted(b)}")
    if len(a) != 15:
        raise RuntimeError(f"Expected 15 matched folds, got {len(a)}")

    compared: list[dict[str, Any]] = []
    for key in sorted(a):
        scheme, fold = key
        r5 = a[key]
        r10 = b[key]
        p5 = bool(r5["passed"])
        p10 = bool(r10["passed"])
        if not p5 and p10:
            flip = "failToPass"
        elif p5 and not p10:
            flip = "passToFail"
        elif p5 and p10:
            flip = "samePass"
        else:
            flip = "sameFail"

        lift5 = float(r5["heldoutPrecisionLift"])
        lift10 = float(r10["heldoutPrecisionLift"])
        row = {
            "scheme": scheme,
            "fold": fold,
            "v5Passed": p5,
            "v10Passed": p10,
            "v5Lift": round(lift5, 2),
            "v10Lift": round(lift10, 2),
            "liftDeltaV10MinusV5": round(lift10 - lift5, 2),
            "flip": flip,
            "v10ArchitectureChosen": str(r10.get("architectureChosen")),
            "v5Q": float((r5.get("chosen") or {}).get("tailQuantile", 0.0)),
            "v10Q": float(r10.get("tailQuantile", 0.0)),
            "v5SectionPass": int((r10.get("v5Choice") or {}).get("sectionPassCount", -1)),
            "v9SectionPass": int((r10.get("v9Choice") or {}).get("sectionPassCount", -1)),
        }
        compared.append(row)
        print("COMPARE", row)

    scheme_summary: dict[str, Any] = {}
    for scheme in SCHEMES:
        subset = [r for r in compared if r["scheme"] == scheme]
        scheme_summary[scheme] = {
            "folds": len(subset),
            "v5Passes": sum(bool(r["v5Passed"]) for r in subset),
            "v10Passes": sum(bool(r["v10Passed"]) for r in subset),
            "failToPass": sum(r["flip"] == "failToPass" for r in subset),
            "passToFail": sum(r["flip"] == "passToFail" for r in subset),
            "samePass": sum(r["flip"] == "samePass" for r in subset),
            "sameFail": sum(r["flip"] == "sameFail" for r in subset),
            "meanLiftDelta": round(sum(float(r["liftDeltaV10MinusV5"]) for r in subset) / max(1, len(subset)), 3),
        }

    v5_passes = sum(bool(r["v5Passed"]) for r in compared)
    v10_passes = sum(bool(r["v10Passed"]) for r in compared)
    fail_to_pass = [r for r in compared if r["flip"] == "failToPass"]
    pass_to_fail = [r for r in compared if r["flip"] == "passToFail"]
    v9_selected = [r for r in compared if r["v10ArchitectureChosen"] == "v9"]
    selector_counts = Counter(r["v10ArchitectureChosen"] for r in compared)

    strict_improvement = v10_passes > v5_passes and len(fail_to_pass) > len(pass_to_fail)
    no_collateral_loss = len(pass_to_fail) == 0
    rescue_by_v9 = len(fail_to_pass) > 0 and all(r["v10ArchitectureChosen"] == "v9" for r in fail_to_pass)
    supported = strict_improvement and no_collateral_loss and rescue_by_v9

    overall = {
        "folds": len(compared),
        "v5Passes": v5_passes,
        "v10Passes": v10_passes,
        "failToPass": len(fail_to_pass),
        "passToFail": len(pass_to_fail),
        "samePass": sum(r["flip"] == "samePass" for r in compared),
        "sameFail": sum(r["flip"] == "sameFail" for r in compared),
        "v5ToV10NetPassGain": v10_passes - v5_passes,
        "selectorCounts": dict(selector_counts),
        "v9SelectedFolds": [{"scheme": r["scheme"], "fold": r["fold"], "flip": r["flip"]} for r in v9_selected],
        "rescuedFolds": [{"scheme": r["scheme"], "fold": r["fold"], "architecture": r["v10ArchitectureChosen"]} for r in fail_to_pass],
        "collateralLossFolds": [{"scheme": r["scheme"], "fold": r["fold"], "architecture": r["v10ArchitectureChosen"]} for r in pass_to_fail],
    }

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v5-v10-hybrid-fold-comparison",
        "schemeSummary": scheme_summary,
        "overall": overall,
        "strictImprovement": strict_improvement,
        "noCollateralV5PassLosses": no_collateral_loss,
        "allRescuesUseV9": rescue_by_v9,
        "hybridV10SupportedOverV5": supported,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseHybrid": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "foldComparison": compared,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "v5Passes": v5_passes,
        "v10Passes": v10_passes,
        "netPassGain": v10_passes - v5_passes,
        "failToPass": len(fail_to_pass),
        "passToFail": len(pass_to_fail),
        "hybridV10SupportedOverV5": supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V5 VS V10 HYBRID COMPARISON V1 COMPLETE")
    print("Matched fold pairs:", len(compared))
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Strict improvement:", strict_improvement)
    print("No collateral V5-pass losses:", no_collateral_loss)
    print("All rescues use V9:", rescue_by_v9)
    print("Hybrid V10 supported over V5:", supported)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
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
