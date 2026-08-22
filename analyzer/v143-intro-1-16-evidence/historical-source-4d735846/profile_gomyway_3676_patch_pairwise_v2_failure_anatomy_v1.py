from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-failure-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-failure-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def family(feature: str) -> str:
    parts = str(feature).split("::")
    if len(parts) < 2:
        return str(feature)
    stem, feat = parts[0], parts[1]
    if feat.startswith("lowMid"):
        band = "lowMid"
    elif feat.startswith("highMid"):
        band = "highMid"
    elif feat.startswith("low"):
        band = "low"
    elif feat.startswith("mid"):
        band = "mid"
    elif feat.startswith("high"):
        band = "high"
    else:
        band = feat
    shape = "timebin" if any(f"T{i}" in feat for i in range(6)) else (
        "burst" if "Burst" in feat else (
            "rise" if "Rise" in feat else (
                "decay" if "Decay" in feat else "other"
            )
        )
    )
    return f"{stem}:{band}:{shape}"


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    lifts = [float(r.get("heldoutPrecisionLift", 0.0)) for r in rows]
    selected = [float((r.get("heldoutCandidate") or {}).get("selectedPct", 0.0)) for r in rows]
    base = [float((r.get("heldoutBase") or {}).get("precision", 0.0)) for r in rows]
    true = [int((r.get("heldoutCandidate") or {}).get("true", 0)) for r in rows]
    false = [int((r.get("heldoutCandidate") or {}).get("false", 0)) for r in rows]
    radii = Counter(int((r.get("chosen") or {}).get("pairRadius", -1)) for r in rows)
    lambdas = Counter(str((r.get("chosen") or {}).get("lambda")) for r in rows)
    qs = Counter(str((r.get("chosen") or {}).get("tailQuantile")) for r in rows)
    fams = Counter()
    for r in rows:
        for w in r.get("topWeights") or []:
            fams[family(str(w.get("feature", "")))] += 1
    return {
        "folds": len(rows),
        "meanLift": round(sum(lifts) / len(lifts), 3),
        "meanSelectedPct": round(sum(selected) / len(selected), 3),
        "meanBasePrecision": round(sum(base) / len(base), 3),
        "recoveredTrue": sum(true),
        "recoveredFalse": sum(false),
        "pairRadiusCounts": dict(sorted(radii.items())),
        "lambdaCounts": dict(sorted(lambdas.items())),
        "tailQuantileCounts": dict(sorted(qs.items())),
        "topFamilies": [{"family": k, "count": v} for k, v in fams.most_common(12)],
    }


def main() -> None:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("V2 pairwise output is not anchored to frozen 36.76 champion")

    all_rows: list[dict[str, Any]] = []
    for key in ("normal", "section", "shiftedWindow"):
        for row in payload.get(key) or []:
            all_rows.append(row)
    if len(all_rows) != 15:
        raise RuntimeError(f"Expected 15 V2 outer folds, found {len(all_rows)}")

    passing = [r for r in all_rows if bool(r.get("passed"))]
    failing = [r for r in all_rows if not bool(r.get("passed"))]

    fail_details = []
    for r in failing:
        ch = r.get("chosen") or {}
        held = r.get("heldoutCandidate") or {}
        base = r.get("heldoutBase") or {}
        fail_details.append({
            "scheme": r.get("scheme"),
            "fold": r.get("fold"),
            "pairRadius": ch.get("pairRadius"),
            "lambda": ch.get("lambda"),
            "tailQuantile": ch.get("tailQuantile"),
            "innerPassCount": ch.get("innerPassCount"),
            "innerFoldCount": ch.get("innerFoldCount"),
            "innerMeanLift": ch.get("meanLift"),
            "heldTrue": held.get("true"),
            "heldFalse": held.get("false"),
            "heldPrecision": held.get("precision"),
            "heldSelectedPct": held.get("selectedPct"),
            "basePrecision": base.get("precision"),
            "heldLift": r.get("heldoutPrecisionLift"),
            "topWeights": r.get("topWeights") or [],
        })

    feature_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"passTop8": 0, "failTop8": 0})
    for r in passing:
        for w in r.get("topWeights") or []:
            feature_stats[str(w.get("feature"))]["passTop8"] += 1
    for r in failing:
        for w in r.get("topWeights") or []:
            feature_stats[str(w.get("feature"))]["failTop8"] += 1
    recurrent = []
    for feat, counts in feature_stats.items():
        if counts["passTop8"] + counts["failTop8"] >= 2:
            recurrent.append({"feature": feat, **counts, "family": family(feat)})
    recurrent.sort(key=lambda d: (d["passTop8"] - d["failTop8"], d["passTop8"], -d["failTop8"]), reverse=True)

    scheme_failures = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        rows = [r for r in all_rows if r.get("scheme") == scheme]
        scheme_failures[scheme] = {
            "passes": sum(bool(r.get("passed")) for r in rows),
            "fails": sum(not bool(r.get("passed")) for r in rows),
            "failedFolds": [int(r.get("fold")) for r in rows if not bool(r.get("passed"))],
        }

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-failure-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "passingFoldCount": len(passing),
        "failingFoldCount": len(failing),
        "schemeFailures": scheme_failures,
        "passingSummary": summarize(passing),
        "failingSummary": summarize(failing),
        "failureDetails": fail_details,
        "recurrentTopWeights": recurrent[:24],
        "v3HypothesisReady": False,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }

    # Conservative heuristic: only call V3 hypothesis-ready when failures clearly cluster.
    fs = output["failingSummary"]
    ps = output["passingSummary"]
    clustered_radius = False
    if fs.get("pairRadiusCounts"):
        max_fail_radius = max(fs["pairRadiusCounts"].values())
        clustered_radius = max_fail_radius >= max(3, len(failing) - 1)
    selected_gap = abs(float(fs.get("meanSelectedPct", 0.0)) - float(ps.get("meanSelectedPct", 0.0))) >= 2.0
    family_signal = any((r["passTop8"] >= 4 and r["failTop8"] == 0) or (r["failTop8"] >= 3 and r["passTop8"] <= 1) for r in recurrent)
    output["v3HypothesisReady"] = bool(clustered_radius or selected_gap or family_signal)

    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "passingFoldCount": len(passing),
        "failingFoldCount": len(failing),
        "v3HypothesisReady": output["v3HypothesisReady"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 FAILURE ANATOMY V1 COMPLETE")
    print("Passing folds:", len(passing), "Failing folds:", len(failing))
    print("SCHEME FAILURES", scheme_failures)
    print("PASS SUMMARY", output["passingSummary"])
    print("FAIL SUMMARY", output["failingSummary"])
    for row in fail_details:
        print("FAIL", row)
    print("TOP RECURRENT WEIGHTS")
    for row in recurrent[:16]:
        print("WEIGHT", row)
    print("V3 hypothesis ready:", output["v3HypothesisReady"])
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
