from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_3676_votes3_low_complexity_acoustic_rule_cv_v1 as base

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-duration-guard-refinement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-duration-guard-refinement-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76

recall = base.recall
GUARD_FEATURES = (
    "maxAmplitude",
    "meanAmplitude",
    "minGridError",
    "sweepPersistence",
    "stemCountAtWide",
    "strictestSweepIndex",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_value(row: dict[str, Any], feature: str) -> float:
    value = row.get(feature)
    return 0.0 if value is None else float(value)


def thresholds(rows: list[dict[str, Any]], feature: str) -> list[float]:
    vals = sorted({feature_value(r, feature) for r in rows})
    if len(vals) <= 1:
        return vals
    mids = [(a + b) / 2.0 for a, b in zip(vals[:-1], vals[1:]) if a != b]
    return sorted(set(vals + mids))


def primitive(feature: str, direction: str, threshold: float) -> tuple[str, Callable[[dict[str, Any]], bool]]:
    if direction == "le":
        return f"{feature}<={threshold:.8g}", lambda r: feature_value(r, feature) <= threshold
    return f"{feature}>={threshold:.8g}", lambda r: feature_value(r, feature) >= threshold


def fold_of(row: dict[str, Any], measures: list[int], scheme: str) -> int:
    m = int(row["measure"])
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)
    if scheme == "normal":
        return m % 5
    if scheme == "shifted":
        return (m + 2) % 5
    return min(4, int(5 * (m - lo) / span))


def token_key(row: dict[str, Any]) -> str:
    token = row.get("token")
    return str(token) if token is not None else f"m{row['measure']}|s{row['step']}|p{row['pitch']}"


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {INPUT_PATH.relative_to(ROOT)}")
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    if tuple(int(x) for x in data.get("championMatchedMissingExtra", [])) != EXPECTED:
        raise RuntimeError("Unexpected champion counts")

    rows = list(data.get("targetRows") or [])
    measures = sorted({int(r["measure"]) for r in rows})
    if (sum(str(r.get("label")) == "true" for r in rows), sum(str(r.get("label")) == "false" for r in rows)) != (7, 31):
        raise RuntimeError("Expected 7 true / 31 false target pocket")

    # Collect out-of-fold decisions made by the unstable low-complexity learner.
    oof: dict[str, dict[str, Any]] = {}
    decision_rows = []
    for scheme in ("normal", "shifted", "section"):
        for fold in range(5):
            train = [r for r in rows if fold_of(r, measures, scheme) != fold]
            test = [r for r in rows if fold_of(r, measures, scheme) == fold]
            rule = base.learn_rule(train)
            if rule is None:
                continue
            for r in test:
                if not rule["fn"](r):
                    continue
                k = token_key(r)
                entry = oof.setdefault(k, {
                    "row": r,
                    "label": str(r.get("label")),
                    "votes": 0,
                    "schemes": set(),
                    "rules": [],
                })
                entry["votes"] += 1
                entry["schemes"].add(scheme)
                entry["rules"].append(rule["rule"])
                decision_rows.append((scheme, fold, r, rule["rule"]))

    true_mispruned = [v for v in oof.values() if v["label"] == "true"]
    false_pruned = [v for v in oof.values() if v["label"] == "false"]

    guard_rules = []
    for feature in GUARD_FEATURES:
        for t in thresholds(rows, feature):
            for direction in ("le", "ge"):
                name, fn = primitive(feature, direction, t)
                true_saved = sum(1 for v in true_mispruned if fn(v["row"]))
                false_saved = sum(1 for v in false_pruned if fn(v["row"]))
                if true_saved == 0:
                    continue
                score = 10 * true_saved - false_saved
                guard_rules.append({
                    "guard": name,
                    "trueSaved": true_saved,
                    "falseSaved": false_saved,
                    "netScore": score,
                    "trueCoverage": round(100.0 * true_saved / max(1, len(true_mispruned)), 2),
                    "falseCost": round(100.0 * false_saved / max(1, len(false_pruned)), 2),
                })

    guard_rules.sort(key=lambda r: (-int(r["trueSaved"]), int(r["falseSaved"]), -int(r["netScore"]), str(r["guard"])))
    strong = [r for r in guard_rules if int(r["trueSaved"]) == len(true_mispruned) and int(r["falseSaved"]) <= max(2, len(false_pruned) // 3)]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during duration-guard refinement")

    def pack(v: dict[str, Any]) -> dict[str, Any]:
        r = v["row"]
        return {
            "token": r.get("token"),
            "measure": int(r["measure"]),
            "step": int(r["step"]),
            "pitch": int(r["pitch"]),
            "label": v["label"],
            "votes": int(v["votes"]),
            "schemes": sorted(v["schemes"]),
            "maxAmplitude": r.get("maxAmplitude"),
            "meanAmplitude": r.get("meanAmplitude"),
            "minGridError": r.get("minGridError"),
            "maxDuration": r.get("maxDuration"),
            "sweepPersistence": r.get("sweepPersistence"),
            "stemCountAtWide": r.get("stemCountAtWide"),
            "strictestSweepIndex": r.get("strictestSweepIndex"),
        }

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-votes3-duration-guard-refinement",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "oofUniquePruned": len(oof),
        "oofTrueMispruned": len(true_mispruned),
        "oofFalsePruned": len(false_pruned),
        "trueMisprunedRows": [pack(v) for v in true_mispruned],
        "falsePrunedRows": [pack(v) for v in false_pruned],
        "strongProtectiveGuards": strong[:50],
        "rankedProtectiveGuards": guard_rules[:100],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "oofTrueMispruned": len(true_mispruned),
        "oofFalsePruned": len(false_pruned),
        "strongProtectiveGuardCount": len(strong),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 VOTES3 DURATION GUARD REFINEMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("OOF unique pruned:", len(oof))
    print("OOF true mispruned:", len(true_mispruned))
    print("OOF false pruned:", len(false_pruned))
    print("Strong protective guards:", len(strong))
    for r in guard_rules[:30]:
        print(f"GUARD {r['guard']} trueSaved={r['trueSaved']} falseSaved={r['falseSaved']} score={r['netScore']}")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
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
