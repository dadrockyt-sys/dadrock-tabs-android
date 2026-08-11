from __future__ import annotations

import hashlib
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
RAW_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
NORM_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-normalization-impact-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-local-normalization-impact-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fold_rows(payload: dict) -> list[dict]:
    out: list[dict] = []
    for key in ("normal", "section", "shiftedWindow"):
        rows = payload.get(key)
        if rows is None:
            rows = payload.get(f"{key}Folds")
        if rows is None and key == "shiftedWindow":
            rows = payload.get("shifted")
        if rows is None:
            rows = []
        for row in rows:
            r = dict(row)
            r.setdefault("scheme", key)
            out.append(r)
    if out:
        return out
    for row in payload.get("folds") or []:
        out.append(dict(row))
    return out


def held(row: dict) -> dict:
    return dict(row.get("heldoutCandidate") or row.get("held") or {})


def base(row: dict) -> dict:
    return dict(row.get("heldoutBase") or row.get("base") or {})


def get_lift(row: dict) -> float:
    if "heldoutPrecisionLift" in row:
        return float(row["heldoutPrecisionLift"])
    if "lift" in row:
        return float(row["lift"])
    h = held(row)
    b = base(row)
    return float(h.get("precision", 0.0)) - float(b.get("precision", 0.0))


def chosen(row: dict) -> dict:
    return dict(row.get("chosen") or {})


def norm_radius(row: dict):
    for key in ("radius", "localRobustRadius", "chosenRadius"):
        if key in row:
            return row[key]
    c = chosen(row)
    for key in ("radius", "localRobustRadius", "chosenRadius"):
        if key in c:
            return c[key]
    return None


def meta(row: dict) -> dict:
    c = chosen(row)
    gate = row.get("featureGate") or []
    feature_count = c.get("featureCount")
    if feature_count is None:
        feature_count = len(gate) if isinstance(gate, list) else None
    return {
        "lambda": row.get("lambda", c.get("lambda")),
        "tailQuantile": row.get("tailQuantile", c.get("tailQuantile")),
        "gateLambda": c.get("gateLambda"),
        "support": c.get("support"),
        "featureCount": feature_count,
        "radius": norm_radius(row),
    }


def main() -> None:
    if not RAW_PATH.exists():
        raise RuntimeError(f"Missing raw benchmark output: {RAW_PATH.name}")
    if not NORM_PATH.exists():
        raise RuntimeError(f"Missing normalized benchmark output: {NORM_PATH.name}")

    raw_payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    norm_payload = json.loads(NORM_PATH.read_text(encoding="utf-8"))

    raw_anchor = tuple(raw_payload.get("baselineMatchedMissingExtra") or raw_payload.get("frozenChampionMatchedMissingExtra") or [])
    norm_anchor = tuple(norm_payload.get("baselineMatchedMissingExtra") or norm_payload.get("frozenChampionMatchedMissingExtra") or [])
    if raw_anchor and raw_anchor != EXPECTED:
        raise RuntimeError("Raw benchmark is not anchored to frozen 36.76 champion")
    if norm_anchor and norm_anchor != EXPECTED:
        raise RuntimeError("Normalized benchmark is not anchored to frozen 36.76 champion")

    raw_rows = {(str(r.get("scheme")), int(r.get("fold", -1))): r for r in fold_rows(raw_payload)}
    norm_rows = {(str(r.get("scheme")), int(r.get("fold", -1))): r for r in fold_rows(norm_payload)}
    keys = sorted(set(raw_rows) & set(norm_rows))
    if len(keys) < 15:
        print(f"Warning: matched only {len(keys)} fold pairs", flush=True)

    comparisons: list[dict] = []
    by_scheme: dict[str, list[dict]] = defaultdict(list)
    radius_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"improved": 0, "degraded": 0, "same": 0, "total": 0})

    for key in keys:
        rr = raw_rows[key]
        nr = norm_rows[key]
        raw_lift = get_lift(rr)
        norm_lift = get_lift(nr)
        delta = norm_lift - raw_lift
        if delta > 0.5:
            outcome = "improved"
        elif delta < -0.5:
            outcome = "degraded"
        else:
            outcome = "same"
        rh = held(rr)
        nh = held(nr)
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
        rs = radius_stats[radius]
        rs["total"] += 1
        rs[outcome] += 1
        print("COMPARE", row, flush=True)

    scheme_summary = {}
    for scheme, rows in by_scheme.items():
        deltas = [float(r["liftDeltaNormalizedMinusRaw"]) for r in rows]
        scheme_summary[scheme] = {
            "folds": len(rows),
            "improved": sum(r["outcome"] == "improved" for r in rows),
            "degraded": sum(r["outcome"] == "degraded" for r in rows),
            "same": sum(r["outcome"] == "same" for r in rows),
            "rawPasses": sum(bool(r["raw"]["passed"]) for r in rows),
            "normalizedPasses": sum(bool(r["normalized"]["passed"]) for r in rows),
            "meanLiftDelta": round(sum(deltas) / len(deltas), 3) if deltas else 0.0,
        }

    total_improved = sum(r["outcome"] == "improved" for r in comparisons)
    total_degraded = sum(r["outcome"] == "degraded" for r in comparisons)
    consistent_help = total_improved >= 10 and total_degraded <= 3

    output = {
        "schemaVersion": 1,
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
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldPairs": len(comparisons),
        "localNormalizationConsistentlyHelps": consistent_help,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE LOCAL NORMALIZATION IMPACT V1 COMPLETE")
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
