from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v5-section-calibration-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v5-section-calibration-comparison-v1-manifest.json"
SCHEMES = ["normal", "section", "shiftedWindow"]
EXPECTED_PAIRS = 15


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required benchmark output: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def fold_map(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in SCHEMES:
        rows = list(payload.get(scheme) or [])
        for row in rows:
            key = (scheme, int(row["fold"]))
            out[key] = row
    return out


def lift(row: dict[str, Any]) -> float:
    return float(row.get("heldoutPrecisionLift", 0.0))


def q_of(row: dict[str, Any]) -> float:
    chosen = row.get("chosen") or {}
    return float(chosen.get("tailQuantile", 0.0))


def radius_of(row: dict[str, Any]) -> int:
    chosen = row.get("chosen") or {}
    return int(chosen.get("pairRadius", 0))


def lambda_of(row: dict[str, Any]) -> float:
    chosen = row.get("chosen") or {}
    return float(chosen.get("lambda", 0.0))


def main() -> None:
    v2 = load(V2_PATH)
    v5 = load(V5_PATH)

    v2m = fold_map(v2)
    v5m = fold_map(v5)
    keys = sorted(set(v2m).intersection(v5m))
    print("Matched fold pairs:", len(keys), flush=True)
    if len(keys) != EXPECTED_PAIRS:
        raise RuntimeError(f"Expected {EXPECTED_PAIRS}/15 matched folds, got {len(keys)}; refusing comparison")

    comparisons: list[dict[str, Any]] = []
    scheme_summary: dict[str, Any] = {}

    for scheme in SCHEMES:
        rows: list[dict[str, Any]] = []
        for fold in range(5):
            key = (scheme, fold)
            a = v2m[key]
            b = v5m[key]
            a_pass = bool(a.get("passed"))
            b_pass = bool(b.get("passed"))
            if (not a_pass) and b_pass:
                flip = "failToPass"
            elif a_pass and (not b_pass):
                flip = "passToFail"
            else:
                flip = "none"
            delta = round(lift(b) - lift(a), 2)
            q_delta = round(q_of(b) - q_of(a), 3)
            outcome = "improved" if delta > 1e-9 else "degraded" if delta < -1e-9 else "same"
            row = {
                "scheme": scheme,
                "fold": fold,
                "v2Passed": a_pass,
                "v5Passed": b_pass,
                "v2Lift": lift(a),
                "v5Lift": lift(b),
                "liftDeltaV5MinusV2": delta,
                "v2Q": q_of(a),
                "v5Q": q_of(b),
                "qDeltaV5MinusV2": q_delta,
                "v2Radius": radius_of(a),
                "v5Radius": radius_of(b),
                "v2Lambda": lambda_of(a),
                "v5Lambda": lambda_of(b),
                "flip": flip,
                "outcome": outcome,
            }
            rows.append(row)
            comparisons.append(row)
            print("COMPARE", row, flush=True)

        scheme_summary[scheme] = {
            "folds": len(rows),
            "v2Passes": sum(int(r["v2Passed"]) for r in rows),
            "v5Passes": sum(int(r["v5Passed"]) for r in rows),
            "failToPass": sum(r["flip"] == "failToPass" for r in rows),
            "passToFail": sum(r["flip"] == "passToFail" for r in rows),
            "improved": sum(r["outcome"] == "improved" for r in rows),
            "degraded": sum(r["outcome"] == "degraded" for r in rows),
            "same": sum(r["outcome"] == "same" for r in rows),
            "meanLiftDelta": round(float(np.mean([r["liftDeltaV5MinusV2"] for r in rows])), 3),
            "meanAbsQChange": round(float(np.mean([abs(r["qDeltaV5MinusV2"]) for r in rows])), 4),
            "qChangedFolds": sum(abs(r["qDeltaV5MinusV2"]) > 1e-9 for r in rows),
        }

    overall = {
        "folds": len(comparisons),
        "v2Passes": sum(int(r["v2Passed"]) for r in comparisons),
        "v5Passes": sum(int(r["v5Passed"]) for r in comparisons),
        "failToPass": sum(r["flip"] == "failToPass" for r in comparisons),
        "passToFail": sum(r["flip"] == "passToFail" for r in comparisons),
        "improved": sum(r["outcome"] == "improved" for r in comparisons),
        "degraded": sum(r["outcome"] == "degraded" for r in comparisons),
        "same": sum(r["outcome"] == "same" for r in comparisons),
        "meanLiftDelta": round(float(np.mean([r["liftDeltaV5MinusV2"] for r in comparisons])), 3),
        "qChangedFolds": sum(abs(r["qDeltaV5MinusV2"]) > 1e-9 for r in comparisons),
    }

    section = scheme_summary["section"]
    section_materially_helped = (
        int(section["v5Passes"]) > int(section["v2Passes"])
        and int(section["failToPass"]) > int(section["passToFail"])
        and float(section["meanLiftDelta"]) > 0.0
    )
    broad_damage = (
        scheme_summary["normal"]["v5Passes"] < scheme_summary["normal"]["v2Passes"]
        or scheme_summary["shiftedWindow"]["v5Passes"] < scheme_summary["shiftedWindow"]["v2Passes"]
    )
    v5_supported = (
        overall["v5Passes"] > overall["v2Passes"]
        and overall["failToPass"] > overall["passToFail"]
        and section_materially_helped
        and not broad_damage
    )

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 VS V5 SECTION CALIBRATION COMPARISON V1 COMPLETE")
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Section materially helped:", section_materially_helped)
    print("Broad normal/shifted damage:", broad_damage)
    print("Section-calibrated V5 supported:", v5_supported)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-v5-section-calibration-comparison",
        "matchedFoldPairs": len(keys),
        "comparisons": comparisons,
        "schemeSummary": scheme_summary,
        "overall": overall,
        "sectionMateriallyHelped": section_materially_helped,
        "broadNormalShiftedDamage": broad_damage,
        "sectionCalibratedV5Supported": v5_supported,
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
        "matchedFoldPairs": len(keys),
        "sectionMateriallyHelped": section_materially_helped,
        "sectionCalibratedV5Supported": v5_supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
