from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V1_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nested-cv-v1.json"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v1-v2-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v1-v2-comparison-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows_by_key(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        for row in payload.get(scheme, []) or []:
            out[(scheme, int(row["fold"]))] = row
    return out


def main() -> None:
    if not V1_PATH.exists() or not V2_PATH.exists():
        raise RuntimeError("Run both pairwise V1 and stratified V2 benchmarks first")

    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))
    if tuple(v1.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("V1 not anchored to frozen 36.76 champion")
    if tuple(v2.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("V2 not anchored to frozen 36.76 champion")

    r1 = rows_by_key(v1)
    r2 = rows_by_key(v2)
    keys = sorted(set(r1) & set(r2))
    if len(keys) != 15:
        raise RuntimeError(f"Expected 15 matched outer folds, found {len(keys)}")

    comparisons: list[dict[str, Any]] = []
    scheme_summary: dict[str, dict[str, Any]] = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        scheme_summary[scheme] = {
            "folds": 0,
            "improved": 0,
            "degraded": 0,
            "same": 0,
            "v1Passes": 0,
            "v2Passes": 0,
            "flippedFailToPass": 0,
            "flippedPassToFail": 0,
            "meanLiftDelta": 0.0,
        }

    for key in keys:
        a, b = r1[key], r2[key]
        scheme, fold = key
        lift1 = float(a.get("heldoutPrecisionLift", 0.0))
        lift2 = float(b.get("heldoutPrecisionLift", 0.0))
        delta = round(lift2 - lift1, 2)
        if delta > 1e-9:
            outcome = "improved"
        elif delta < -1e-9:
            outcome = "degraded"
        else:
            outcome = "same"
        p1, p2 = bool(a.get("passed")), bool(b.get("passed"))
        c1, c2 = a.get("chosen", {}) or {}, b.get("chosen", {}) or {}
        row = {
            "scheme": scheme,
            "fold": fold,
            "outcome": outcome,
            "v1": {
                "lift": lift1,
                "passed": p1,
                "true": int((a.get("heldoutCandidate") or {}).get("true", 0)),
                "false": int((a.get("heldoutCandidate") or {}).get("false", 0)),
                "precision": float((a.get("heldoutCandidate") or {}).get("precision", 0.0)),
                "pairRadius": c1.get("pairRadius"),
                "lambda": c1.get("lambda"),
                "tailQuantile": c1.get("tailQuantile"),
            },
            "v2": {
                "lift": lift2,
                "passed": p2,
                "true": int((b.get("heldoutCandidate") or {}).get("true", 0)),
                "false": int((b.get("heldoutCandidate") or {}).get("false", 0)),
                "precision": float((b.get("heldoutCandidate") or {}).get("precision", 0.0)),
                "pairRadius": c2.get("pairRadius"),
                "lambda": c2.get("lambda"),
                "tailQuantile": c2.get("tailQuantile"),
            },
            "liftDeltaV2MinusV1": delta,
            "passFlip": "failToPass" if (not p1 and p2) else "passToFail" if (p1 and not p2) else "none",
        }
        comparisons.append(row)
        s = scheme_summary[scheme]
        s["folds"] += 1
        s[outcome] += 1
        s["v1Passes"] += int(p1)
        s["v2Passes"] += int(p2)
        s["flippedFailToPass"] += int((not p1) and p2)
        s["flippedPassToFail"] += int(p1 and (not p2))
        s["meanLiftDelta"] += delta

    for s in scheme_summary.values():
        s["meanLiftDelta"] = round(s["meanLiftDelta"] / max(1, s["folds"]), 3)

    overall = {
        "folds": len(comparisons),
        "improved": sum(r["outcome"] == "improved" for r in comparisons),
        "degraded": sum(r["outcome"] == "degraded" for r in comparisons),
        "same": sum(r["outcome"] == "same" for r in comparisons),
        "v1Passes": sum(bool(r["v1"]["passed"]) for r in comparisons),
        "v2Passes": sum(bool(r["v2"]["passed"]) for r in comparisons),
        "failToPass": sum(r["passFlip"] == "failToPass" for r in comparisons),
        "passToFail": sum(r["passFlip"] == "passToFail" for r in comparisons),
        "meanLiftDelta": round(sum(float(r["liftDeltaV2MinusV1"]) for r in comparisons) / len(comparisons), 3),
    }
    materially_helped = overall["v2Passes"] > overall["v1Passes"] and overall["failToPass"] > overall["passToFail"]

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v1-v2-comparison-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "matchedFoldPairs": len(comparisons),
        "schemeSummary": scheme_summary,
        "overall": overall,
        "comparisons": comparisons,
        "stratifiedSamplingMateriallyHelped": materially_helped,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "matchedFoldPairs": len(comparisons),
        "stratifiedSamplingMateriallyHelped": materially_helped,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V1 VS V2 COMPARISON V1 COMPLETE")
    print("Matched fold pairs:", len(comparisons))
    for row in comparisons:
        print("COMPARE", row)
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Stratified sampling materially helped:", materially_helped)
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
