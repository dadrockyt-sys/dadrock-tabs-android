from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
V4_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-available-measure-balanced-nested-cv-v4.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v4-sampler-comparison-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v4-sampler-comparison-v1-manifest.json"
SCHEMES = ["normal", "section", "shiftedWindow"]
EXPECTED_FOLDS = 15


def rows_by_key(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for scheme in SCHEMES:
        rows = payload.get(scheme) or []
        for row in rows:
            out[(scheme, int(row["fold"]))] = row
    return out


def lift(row: dict[str, Any]) -> float:
    return float(row.get("heldoutPrecisionLift", 0.0))


def passed(row: dict[str, Any]) -> bool:
    return bool(row.get("passed", False))


def chosen(row: dict[str, Any], key: str, default: Any = None) -> Any:
    return (row.get("chosen") or {}).get(key, default)


def held(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("heldoutCandidate") or {}


def compare_row(v2: dict[str, Any], v4: dict[str, Any]) -> dict[str, Any]:
    v2p, v4p = passed(v2), passed(v4)
    if not v2p and v4p:
        flip = "failToPass"
    elif v2p and not v4p:
        flip = "passToFail"
    else:
        flip = "none"
    delta = round(lift(v4) - lift(v2), 2)
    outcome = "improved" if delta > 1e-9 else "degraded" if delta < -1e-9 else "same"
    return {
        "scheme": str(v2["scheme"]),
        "fold": int(v2["fold"]),
        "outcome": outcome,
        "flip": flip,
        "v2": {
            "passed": v2p,
            "lift": lift(v2),
            "true": int(held(v2).get("true", 0)),
            "false": int(held(v2).get("false", 0)),
            "precision": float(held(v2).get("precision", 0.0)),
            "selectedPct": float(held(v2).get("selectedPct", 0.0)),
            "pairRadius": chosen(v2, "pairRadius"),
            "lambda": chosen(v2, "lambda"),
            "tailQuantile": chosen(v2, "tailQuantile"),
        },
        "v4": {
            "passed": v4p,
            "lift": lift(v4),
            "true": int(held(v4).get("true", 0)),
            "false": int(held(v4).get("false", 0)),
            "precision": float(held(v4).get("precision", 0.0)),
            "selectedPct": float(held(v4).get("selectedPct", 0.0)),
            "pairRadius": chosen(v4, "pairRadius"),
            "lambda": chosen(v4, "lambda"),
            "tailQuantile": chosen(v4, "tailQuantile"),
        },
        "liftDeltaV4MinusV2": delta,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "folds": len(rows),
        "v2Passes": sum(int(r["v2"]["passed"]) for r in rows),
        "v4Passes": sum(int(r["v4"]["passed"]) for r in rows),
        "failToPass": sum(r["flip"] == "failToPass" for r in rows),
        "passToFail": sum(r["flip"] == "passToFail" for r in rows),
        "improved": sum(r["outcome"] == "improved" for r in rows),
        "degraded": sum(r["outcome"] == "degraded" for r in rows),
        "same": sum(r["outcome"] == "same" for r in rows),
        "meanLiftDelta": round(sum(float(r["liftDeltaV4MinusV2"]) for r in rows) / len(rows), 3) if rows else 0.0,
    }


def main() -> None:
    if not V2_PATH.exists() or not V4_PATH.exists():
        raise RuntimeError("Run both V2 and V4 pairwise benchmarks before this comparison profiler")

    v2_payload = json.loads(V2_PATH.read_text(encoding="utf-8"))
    v4_payload = json.loads(V4_PATH.read_text(encoding="utf-8"))
    v2_rows = rows_by_key(v2_payload)
    v4_rows = rows_by_key(v4_payload)
    keys = sorted(set(v2_rows) & set(v4_rows))
    print("Matched fold pairs:", len(keys), flush=True)
    if len(keys) != EXPECTED_FOLDS:
        raise RuntimeError(f"Expected {EXPECTED_FOLDS} matched fold pairs, got {len(keys)}")

    comparisons: list[dict[str, Any]] = []
    for key in keys:
        row = compare_row(v2_rows[key], v4_rows[key])
        comparisons.append(row)
        print("COMPARE", row, flush=True)

    scheme_summary = {
        scheme: summarize([r for r in comparisons if r["scheme"] == scheme])
        for scheme in SCHEMES
    }
    overall = summarize(comparisons)

    section = scheme_summary["section"]
    section_materially_helped = (
        int(section["v4Passes"]) > int(section["v2Passes"])
        and int(section["failToPass"]) > int(section["passToFail"])
        and float(section["meanLiftDelta"]) > 0.0
    )
    sampler_v4_supported = (
        int(overall["v4Passes"]) > int(overall["v2Passes"])
        and int(overall["failToPass"]) > int(overall["passToFail"])
        and float(overall["meanLiftDelta"]) > 0.0
    )

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-v4-sampler-comparison",
        "matchedFoldPairs": len(keys),
        "schemeSummary": scheme_summary,
        "overall": overall,
        "sectionMateriallyHelped": section_materially_helped,
        "availableMeasureSamplerV4Supported": sampler_v4_supported,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "comparisons": comparisons,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "matchedFoldPairs": len(keys),
        "sectionMateriallyHelped": section_materially_helped,
        "availableMeasureSamplerV4Supported": sampler_v4_supported,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 VS V4 SAMPLER COMPARISON V1 COMPLETE")
    print("SCHEME SUMMARY", scheme_summary)
    print("OVERALL", overall)
    print("Section materially helped:", section_materially_helped)
    print("Available-measure sampler V4 supported:", sampler_v4_supported)
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
