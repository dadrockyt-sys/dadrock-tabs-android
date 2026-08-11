from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
RAW_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
NORM_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-normalization-impact-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-normalization-impact-v2-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
EXPECTED_PAIRS = 15


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows_for(payload: dict[str, Any], scheme: str) -> list[dict[str, Any]]:
    aliases = {
        "normal": ["normal", "normalCv", "normalFolds"],
        "section": ["section", "sectionCv", "sectionFolds"],
        "shiftedWindow": ["shiftedWindow", "shiftedWindowCv", "shifted", "shiftedFolds"],
    }
    for key in aliases[scheme]:
        rows = payload.get(key)
        if isinstance(rows, list):
            return [dict(r) for r in rows]
    return []


def fold_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        for row in _rows_for(payload, scheme):
            row.setdefault("scheme", scheme)
            out.append(row)
    if out:
        return out
    return [dict(r) for r in (payload.get("folds") or [])]


def held(row: dict[str, Any]) -> dict[str, Any]:
    return dict(row.get("heldoutCandidate") or row.get("held") or {})


def base(row: dict[str, Any]) -> dict[str, Any]:
    return dict(row.get("heldoutBase") or row.get("base") or {})


def get_lift(row: dict[str, Any]) -> float:
    if "heldoutPrecisionLift" in row:
        return float(row["heldoutPrecisionLift"])
    if "lift" in row:
        return float(row["lift"])
    h = held(row)
    b = base(row)
    return float(h.get("precision", 0.0)) - float(b.get("precision", 0.0))


def chosen(row: dict[str, Any]) -> dict[str, Any]:
    return dict(row.get("chosen") or {})


def norm_radius(row: dict[str, Any]) -> int | None:
    normalization = row.get("normalization")
    if isinstance(normalization, dict) and normalization.get("radius") is not None:
        return int(normalization["radius"])
    for key in ("radius", "localRobustRadius", "chosenRadius"):
        if row.get(key) is not None:
            return int(row[key])
    c = chosen(row)
    for key in ("radius", "localRobustRadius", "chosenRadius"):
        if c.get(key) is not None:
            return int(c[key])
    return None


def meta(row: dict[str, Any]) -> dict[str, Any]:
    c = chosen(row)
    gate = row.get("featureGate") or []
    feature_count = c.get("featureCount")
    if feature_count is None and isinstance(gate, list):
        feature_count = len(gate)
    return {
        "lambda": row.get("lambda", c.get("lambda")),
        "tailQuantile": row.get("tailQuantile", c.get("tailQuantile")),
        "gateLambda": c.get("gateLambda"),
        "support": c.get("support"),
        "featureCount": feature_count,
        "radius": norm_radius(row),
    }


def main() -> None:
    if not RAW_PATH.exists() or not NORM_PATH.exists():
        raise RuntimeError("Required benchmark outputs are missing")

    raw_payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    norm_payload = json.loads(NORM_PATH.read_text(encoding="utf-8"))

    raw_anchor = tuple(raw_payload.get("baselineMatchedMissingExtra") or raw_payload.get("frozenChampionMatchedMissingExtra") or [])
    norm_anchor = tuple(norm_payload.get("baselineMatchedMissingExtra") or norm_payload.get("frozenChampionMatchedMissingExtra") or [])
    if raw_anchor != EXPECTED or norm_anchor != EXPECTED:
        raise RuntimeError("Benchmark outputs are not both anchored to frozen 36.76 champion")

    raw_rows = {(str(r.get("scheme")), int(r.get("fold", -1))): r for r in fold_rows(raw_payload)}
    norm_rows = {(str(r.get("scheme")), int(r.get("fold", -1))): r for r in fold_rows(norm_payload)}
    keys = sorted(set(raw_rows) & set(norm_rows))

    print("Raw fold rows:", len(raw_rows), "Normalized fold rows:", len(norm_rows), "Matched:", len(keys), flush=True)
    if len(keys) != EXPECTED_PAIRS:
        missing_raw = sorted(set(norm_rows) - set(raw_rows))
        missing_norm = sorted(set(raw_rows) - set(norm_rows))
        raise RuntimeError(
            f"Expected {EXPECTED_PAIRS} matched fold pairs; got {len(keys)}. "
            f"Missing raw={missing_raw} missing normalized={missing_norm}"
        )

    comparisons: list[dict[str, Any]] = []
    by_scheme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    radius_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"improved": 0, "degraded": 0, "same": 0, "total": 0})

    for key in keys:
        rr, nr = raw_rows[key], norm_rows[key]
        raw_lift, norm_lift = get_lift(rr), get_lift(nr)
        delta = norm_lift - raw_lift
        outcome = "improved" if delta > 0.5 else "degraded" if delta < -0.5 else "same"
        rh, nh = held(rr), held(nr)
        row = {
            "scheme": key[0],
            "fold": key[1],
            "raw": {
                "true": int(rh.get("true", 0)),
                "false": int(rh.get("false", 0)),
                "precision": float(rh.get("precision", 0.0)),
                "lift": round(raw_lift, 2),
                "passed": bool(rr.get("passed", False)),
                "meta": meta(rr),
            },
            "normalized": {
                "true": int(nh.get("true", 0)),
                "false": int(nh.get("false", 0)),
                "precision": float(nh.get("precision", 0.0)),
                "lift": round(norm_lift, 2),
                "passed": bool(nr.get("passed", False)),
                "meta": meta(nr),
            },
            "liftDeltaNormalizedMinusRaw": round(delta, 2),
            "outcome": outcome,
        }
        comparisons.append(row)
        by_scheme[key[0]].append(row)
        radius = str(row["normalized"]["meta"].get("radius"))
        radius_stats[radius]["total"] += 1
        radius_stats[radius][outcome] += 1
        print("COMPARE", row, flush=True)

    scheme_summary: dict[str, Any] = {}
    for scheme, rows in by_scheme.items():
        deltas = [float(r["liftDeltaNormalizedMinusRaw"]) for r in rows]
        scheme_summary[scheme] = {
            "folds": len(rows),
            "improved": sum(r["outcome"] == "improved" for r in rows),
            "degraded": sum(r["outcome"] == "degraded" for r in rows),
            "same": sum(r["outcome"] == "same" for r in rows),
            "rawPasses": sum(bool(r["raw"]["passed"]) for r in rows),
            "normalizedPasses": sum(bool(r["normalized"]["passed"]) for r in rows),
            "meanLiftDelta": round(sum(deltas) / len(deltas), 3),
        }

    total_improved = sum(r["outcome"] == "improved" for r in comparisons)
    total_degraded = sum(r["outcome"] == "degraded" for r in comparisons)
    consistent_help = total_improved >= 10 and total_degraded <= 3

    output = {
        "schemaVersion": 2,
        "profileType": "36.76-patch-ridge-local-normalization-impact-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "foldPairs": len(comparisons),
        "comparisons": comparisons,
        "schemeSummary": scheme_summary,
        "radiusSummary": dict(radius_stats),
        "localNormalizationConsistentlyHelps": consistent_help,
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
        "schemaVersion": 2,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldPairs": len(comparisons),
        "localNormalizationConsistentlyHelps": consistent_help,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE LOCAL NORMALIZATION IMPACT V2 COMPLETE")
    print("SCHEME SUMMARY", scheme_summary)
    print("RADIUS SUMMARY", dict(radius_stats))
    print("Local normalization consistently helps:", consistent_help)
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
