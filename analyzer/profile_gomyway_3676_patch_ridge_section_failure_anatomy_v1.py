from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-ridge-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-section-failure-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-section-failure-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_family(name: str) -> str:
    if "::" in name:
        prefix, rest = name.split("::", 1)
    else:
        prefix, rest = "other", name
    band = "other"
    for token in ("lowMid", "highMid", "low", "mid", "high"):
        if rest.startswith(token):
            band = token
            break
    shape = "timebin"
    for token in ("Rise", "Decay30", "Decay60", "PostSlope", "Burst"):
        if token in rest:
            shape = token
            break
    return f"{prefix}:{band}:{shape}"


def fold_summary(row: dict[str, Any]) -> dict[str, Any]:
    tops = list(row.get("topWeights") or [])
    return {
        "scheme": row.get("scheme"),
        "fold": row.get("fold"),
        "passed": bool(row.get("passed")),
        "lift": float(row.get("heldoutPrecisionLift") or 0.0),
        "lambda": float(row.get("lambda") or 0.0),
        "tailQuantile": float(row.get("tailQuantile") or 0.0),
        "true": int(((row.get("heldoutCandidate") or {}).get("true")) or 0),
        "false": int(((row.get("heldoutCandidate") or {}).get("false")) or 0),
        "topFeatures": [str(x.get("feature")) for x in tops],
        "topWeights": tops,
    }


def overlap(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def main() -> None:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch ridge result is not anchored to frozen 36.76 champion")

    folds: list[dict[str, Any]] = []
    for key in ("normalCv", "sectionCv", "shiftedWindowCv"):
        folds.extend(fold_summary(r) for r in list(payload.get(key) or []))
    if len(folds) != 15:
        raise RuntimeError(f"Expected 15 outer folds, found {len(folds)}")

    feature_counts_all: Counter[str] = Counter()
    feature_counts_pass: Counter[str] = Counter()
    feature_counts_fail: Counter[str] = Counter()
    family_counts_pass: Counter[str] = Counter()
    family_counts_fail: Counter[str] = Counter()
    hyper_by_scheme: dict[str, dict[str, Any]] = {}

    by_scheme: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in folds:
        by_scheme[str(f["scheme"])].append(f)
        for feat in f["topFeatures"]:
            feature_counts_all[feat] += 1
            fam = feature_family(feat)
            if f["passed"]:
                feature_counts_pass[feat] += 1
                family_counts_pass[fam] += 1
            else:
                feature_counts_fail[feat] += 1
                family_counts_fail[fam] += 1

    scheme_summaries: dict[str, Any] = {}
    for scheme, rows in by_scheme.items():
        lambdas = Counter(str(r["lambda"]) for r in rows)
        tails = Counter(str(r["tailQuantile"]) for r in rows)
        mean_lift = sum(float(r["lift"]) for r in rows) / len(rows)
        pass_rows = [r for r in rows if r["passed"]]
        fail_rows = [r for r in rows if not r["passed"]]
        pairs = []
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                pairs.append(overlap(rows[i]["topFeatures"], rows[j]["topFeatures"]))
        scheme_summaries[scheme] = {
            "folds": len(rows),
            "passed": len(pass_rows),
            "failed": len(fail_rows),
            "meanLift": round(mean_lift, 3),
            "minLift": round(min(float(r["lift"]) for r in rows), 3),
            "maxLift": round(max(float(r["lift"]) for r in rows), 3),
            "lambdaCounts": dict(lambdas),
            "tailQuantileCounts": dict(tails),
            "meanTopWeightJaccard": round(sum(pairs) / len(pairs), 3) if pairs else 0.0,
            "foldResults": rows,
        }

    recurrent = []
    for feat, count in feature_counts_all.most_common():
        recurrent.append({
            "feature": feat,
            "allTop8Folds": count,
            "passingTop8Folds": feature_counts_pass[feat],
            "failingTop8Folds": feature_counts_fail[feat],
            "family": feature_family(feat),
        })

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-section-failure-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "source": str(SOURCE_PATH.relative_to(ROOT)),
        "sourceSha256": sha256(SOURCE_PATH),
        "schemeSummaries": scheme_summaries,
        "recurrentTopFeatures": recurrent[:30],
        "passingFeatureFamilies": [{"family": k, "count": v} for k, v in family_counts_pass.most_common(20)],
        "failingFeatureFamilies": [{"family": k, "count": v} for k, v in family_counts_fail.most_common(20)],
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
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "sourceSha256": output["sourceSha256"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE SECTION FAILURE ANATOMY V1 COMPLETE")
    for scheme, s in scheme_summaries.items():
        print("SCHEME", scheme, {
            "passed": s["passed"],
            "failed": s["failed"],
            "meanLift": s["meanLift"],
            "minLift": s["minLift"],
            "maxLift": s["maxLift"],
            "lambdaCounts": s["lambdaCounts"],
            "tailCounts": s["tailQuantileCounts"],
            "meanTopWeightJaccard": s["meanTopWeightJaccard"],
        })
    print("TOP RECURRENT WEIGHTS")
    for item in recurrent[:12]:
        print("WEIGHT", item)
    print("PASS FAMILIES", output["passingFeatureFamilies"][:8])
    print("FAIL FAMILIES", output["failingFeatureFamilies"][:8])
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
