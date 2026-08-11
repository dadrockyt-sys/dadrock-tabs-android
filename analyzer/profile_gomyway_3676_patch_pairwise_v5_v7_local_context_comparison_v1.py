from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
V7_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-local-context-nested-cv-v7.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v7-local-context-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-v7-local-context-comparison-v1-manifest.json"
SCHEMES = ["normal", "section", "shiftedWindow"]


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fold_map(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in SCHEMES:
        for row in payload.get(scheme) or []:
            out[(scheme, int(row["fold"]))] = row
    return out


def chosen_q(row: dict[str, Any]) -> float | None:
    chosen = row.get("chosen") or {}
    q = chosen.get("tailQuantile")
    return float(q) if q is not None else None


def lift(row: dict[str, Any]) -> float:
    return float(row.get("heldoutPrecisionLift", 0.0))


def main() -> None:
    v5 = load(V5_PATH)
    v7 = load(V7_PATH)
    a = fold_map(v5)
    b = fold_map(v7)
    keys = sorted(set(a) & set(b), key=lambda k: (SCHEMES.index(k[0]), k[1]))
    if len(keys) != 15:
        raise RuntimeError(f"Expected 15 matched folds, got {len(keys)}")

    rows: list[dict[str, Any]] = []
    for key in keys:
        r5, r7 = a[key], b[key]
        p5, p7 = bool(r5.get("passed")), bool(r7.get("passed"))
        if not p5 and p7:
            flip = "failToPass"
            outcome = "improved"
        elif p5 and not p7:
            flip = "passToFail"
            outcome = "degraded"
        elif p5 and p7:
            flip = "none"
            outcome = "samePass"
        else:
            flip = "none"
            outcome = "sameFail"
        row = {
            "scheme": key[0],
            "fold": key[1],
            "v5Passed": p5,
            "v7Passed": p7,
            "v5Lift": round(lift(r5), 2),
            "v7Lift": round(lift(r7), 2),
            "liftDeltaV7MinusV5": round(lift(r7) - lift(r5), 2),
            "v5Q": chosen_q(r5),
            "v7Q": chosen_q(r7),
            "flip": flip,
            "outcome": outcome,
        }
        rows.append(row)
        print("COMPARE", row)

    scheme_summary: dict[str, Any] = {}
    for scheme in SCHEMES:
        rs = [r for r in rows if r["scheme"] == scheme]
        scheme_summary[scheme] = {
            "folds": len(rs),
            "v5Passes": sum(r["v5Passed"] for r in rs),
            "v7Passes": sum(r["v7Passed"] for r in rs),
            "failToPass": sum(r["flip"] == "failToPass" for r in rs),
            "passToFail": sum(r["flip"] == "passToFail" for r in rs),
            "improved": sum(r["outcome"] == "improved" for r in rs),
            "degraded": sum(r["outcome"] == "degraded" for r in rs),
            "same": sum(r["outcome"].startswith("same") for r in rs),
            "meanLiftDelta": round(sum(r["liftDeltaV7MinusV5"] for r in rs) / len(rs), 3),
        }

    overall = {
        "folds": len(rows),
        "v5Passes": sum(r["v5Passed"] for r in rows),
        "v7Passes": sum(r["v7Passed"] for r in rows),
        "failToPass": sum(r["flip"] == "failToPass" for r in rows),
        "passToFail": sum(r["flip"] == "passToFail" for r in rows),
        "improved": sum(r["outcome"] == "improved" for r in rows),
        "degraded": sum(r["outcome"] == "degraded" for r in rows),
        "same": sum(r["outcome"].startswith("same") for r in rows),
        "meanLiftDelta": round(sum(r["liftDeltaV7MinusV5"] for r in rows) / len(rows), 3),
    }

    residual_rescues = [r for r in rows if not r["v5Passed"] and r["v7Passed"]]
    collateral_losses = [r for r in rows if r["v5Passed"] and not r["v7Passed"]]
    local_context_has_unique_rescue = len(residual_rescues) > 0
    local_context_net_help = overall["v7Passes"] > overall["v5Passes"] and overall["failToPass"] > overall["passToFail"]
    local_context_supported = local_context_net_help

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-v7-local-context-comparison",
        "matchedFoldPairs": len(rows),
        "rows": rows,
        "schemeSummary": scheme_summary,
        "overall": overall,
        "v5ResidualRescues": residual_rescues,
        "v7CollateralLosses": collateral_losses,
        "localContextHasUniqueRescue": local_context_has_unique_rescue,
        "localContextNetHelp": local_context_net_help,
        "localContextV7Supported": local_context_supported,
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
        "v5Passes": overall["v5Passes"],
        "v7Passes": overall["v7Passes"],
        "failToPass": overall["failToPass"],
        "passToFail": overall["passToFail"],
        "localContextV7Supported": local_context_supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 VS V7 LOCAL CONTEXT COMPARISON V1 COMPLETE")
    print("Matched fold pairs:", len(rows))
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Unique V5-failure rescues:", len(residual_rescues))
    print("Collateral V5-pass losses:", len(collateral_losses))
    print("Local context has unique rescue:", local_context_has_unique_rescue)
    print("Local context net help:", local_context_net_help)
    print("Local-context V7 supported:", local_context_supported)
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
