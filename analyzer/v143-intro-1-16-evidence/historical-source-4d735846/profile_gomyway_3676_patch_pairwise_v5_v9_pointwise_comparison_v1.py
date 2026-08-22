from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V9_PATH = PUBLIC / "gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v9-pointwise-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v9-pointwise-comparison-v1-manifest.json"

SCHEMES = ["normal", "section", "shiftedWindow"]


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required result: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def fold_map(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in SCHEMES:
        for row in payload.get(scheme, []) or []:
            key = (scheme, int(row["fold"]))
            out[key] = row
    return out


def lift(row: dict[str, Any]) -> float:
    for key in ("heldoutPrecisionLift", "lift"):
        if key in row:
            return float(row[key])
    return 0.0


def chosen_summary(row: dict[str, Any]) -> dict[str, Any]:
    chosen = row.get("chosen") or {}
    return {
        "lambda": chosen.get("lambda"),
        "q": chosen.get("tailQuantile"),
        "pairRadius": chosen.get("pairRadius"),
    }


def main() -> None:
    v5 = load(V5_PATH)
    v9 = load(V9_PATH)
    a = fold_map(v5)
    b = fold_map(v9)
    keys = sorted(set(a) | set(b))
    if len(keys) != 15 or set(a) != set(b):
        raise RuntimeError(f"Expected exact 15-fold match; V5={len(a)} V9={len(b)} matched={len(set(a)&set(b))}")

    comparisons: list[dict[str, Any]] = []
    scheme_summary: dict[str, dict[str, Any]] = {}
    unique_rescues = 0
    collateral_losses = 0

    for scheme in SCHEMES:
        scheme_rows = []
        for key in [k for k in keys if k[0] == scheme]:
            r5, r9 = a[key], b[key]
            p5, p9 = bool(r5.get("passed")), bool(r9.get("passed"))
            if not p5 and p9:
                flip = "failToPass"
                outcome = "improved"
                unique_rescues += 1
            elif p5 and not p9:
                flip = "passToFail"
                outcome = "degraded"
                collateral_losses += 1
            else:
                flip = "none"
                outcome = "samePass" if p5 else "sameFail"
            row = {
                "scheme": scheme,
                "fold": int(key[1]),
                "v5Passed": p5,
                "v9Passed": p9,
                "v5Lift": round(lift(r5), 2),
                "v9Lift": round(lift(r9), 2),
                "liftDeltaV9MinusV5": round(lift(r9) - lift(r5), 2),
                "v5Chosen": chosen_summary(r5),
                "v9Chosen": chosen_summary(r9),
                "flip": flip,
                "outcome": outcome,
            }
            comparisons.append(row)
            scheme_rows.append(row)
            print("COMPARE", row)

        v5_passes = sum(r["v5Passed"] for r in scheme_rows)
        v9_passes = sum(r["v9Passed"] for r in scheme_rows)
        scheme_summary[scheme] = {
            "folds": len(scheme_rows),
            "v5Passes": v5_passes,
            "v9Passes": v9_passes,
            "failToPass": sum(r["flip"] == "failToPass" for r in scheme_rows),
            "passToFail": sum(r["flip"] == "passToFail" for r in scheme_rows),
            "improved": sum(r["outcome"] == "improved" for r in scheme_rows),
            "degraded": sum(r["outcome"] == "degraded" for r in scheme_rows),
            "same": sum(r["flip"] == "none" for r in scheme_rows),
            "meanLiftDelta": round(sum(r["liftDeltaV9MinusV5"] for r in scheme_rows) / len(scheme_rows), 3),
        }

    overall = {
        "folds": len(comparisons),
        "v5Passes": sum(r["v5Passed"] for r in comparisons),
        "v9Passes": sum(r["v9Passed"] for r in comparisons),
        "failToPass": unique_rescues,
        "passToFail": collateral_losses,
        "improved": sum(r["outcome"] == "improved" for r in comparisons),
        "degraded": sum(r["outcome"] == "degraded" for r in comparisons),
        "same": sum(r["flip"] == "none" for r in comparisons),
        "meanLiftDelta": round(sum(r["liftDeltaV9MinusV5"] for r in comparisons) / len(comparisons), 3),
    }

    has_unique_rescue = unique_rescues > 0
    net_help = overall["v9Passes"] > overall["v5Passes"]
    supported = net_help or (has_unique_rescue and collateral_losses == 0)
    retire = not supported

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-v9-pointwise-comparison",
        "matchedFoldPairs": len(comparisons),
        "schemeSummary": scheme_summary,
        "overall": overall,
        "comparisons": comparisons,
        "uniqueV5FailureRescues": unique_rescues,
        "collateralV5PassLosses": collateral_losses,
        "pointwiseHasUniqueRescue": has_unique_rescue,
        "pointwiseNetHelp": net_help,
        "pointwiseV9Supported": supported,
        "retirePointwiseV9": retire,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "matchedFoldPairs": len(comparisons),
        "uniqueV5FailureRescues": unique_rescues,
        "collateralV5PassLosses": collateral_losses,
        "pointwiseV9Supported": supported,
        "retirePointwiseV9": retire,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 VS POINTWISE V9 COMPARISON V1 COMPLETE")
    print("Matched fold pairs:", len(comparisons))
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Unique V5-failure rescues:", unique_rescues)
    print("Collateral V5-pass losses:", collateral_losses)
    print("Pointwise has unique rescue:", has_unique_rescue)
    print("Pointwise net help:", net_help)
    print("Pointwise V9 supported:", supported)
    print("Retire pointwise V9:", retire)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
