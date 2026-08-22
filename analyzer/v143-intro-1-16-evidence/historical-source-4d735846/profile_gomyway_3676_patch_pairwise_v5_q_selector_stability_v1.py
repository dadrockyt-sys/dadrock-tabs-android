from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-q-selector-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-q-selector-stability-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_folds(qrow: dict[str, Any]) -> list[dict[str, Any]]:
    return [f for f in (qrow.get("folds") or []) if str(f.get("family")) == "section"]


def q_metrics(qrow: dict[str, Any]) -> dict[str, Any]:
    sf = section_folds(qrow)
    lifts = [float(f.get("lift", 0.0)) for f in sf]
    passes = [bool(f.get("passed")) for f in sf]
    if not lifts:
        return {
            "q": float(qrow.get("tailQuantile", 0.0)),
            "sectionPassCount": 0,
            "sectionMeanLift": -999.0,
            "sectionMedianLift": -999.0,
            "sectionMinLift": -999.0,
            "sectionLiftStd": 999.0,
            "overallPassCount": int(qrow.get("overallPassCount", 0)),
            "overallMeanLift": float(qrow.get("overallMeanLift", -999.0)),
        }
    return {
        "q": float(qrow.get("tailQuantile", 0.0)),
        "sectionPassCount": int(sum(passes)),
        "sectionMeanLift": round(float(np.mean(lifts)), 3),
        "sectionMedianLift": round(float(np.median(lifts)), 3),
        "sectionMinLift": round(float(np.min(lifts)), 3),
        "sectionLiftStd": round(float(np.std(lifts)), 3),
        "overallPassCount": int(qrow.get("overallPassCount", 0)),
        "overallMeanLift": float(qrow.get("overallMeanLift", -999.0)),
    }


def robust_choice(qdiag: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = [q_metrics(q) for q in qdiag]
    return max(
        metrics,
        key=lambda r: (
            float(r["sectionMinLift"]),
            int(r["sectionPassCount"]),
            float(r["sectionMedianLift"]),
            -float(r["sectionLiftStd"]),
            int(r["overallPassCount"]),
            float(r["overallMeanLift"]),
            -float(r["q"]),
        ),
    )


def main() -> None:
    before = sha256(V5_PATH)
    payload = json.loads(V5_PATH.read_text(encoding="utf-8"))
    if int(payload.get("outerFoldsPassed", -1)) != 11:
        raise RuntimeError("Expected V5 11/15 baseline before selector stability analysis")

    rows: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        for row in payload.get(scheme) or []:
            chosen = row.get("chosen") or {}
            qdiag = chosen.get("qDiagnostics") or []
            if not qdiag:
                raise RuntimeError(f"Missing qDiagnostics for {scheme} fold {row.get('fold')}")
            chosen_q = float(chosen.get("tailQuantile"))
            selected_diag = next((q for q in qdiag if abs(float(q.get("tailQuantile")) - chosen_q) < 1e-12), None)
            if selected_diag is None:
                raise RuntimeError(f"Chosen q missing from diagnostics for {scheme} fold {row.get('fold')}")
            selected = q_metrics(selected_diag)
            robust = robust_choice(qdiag)
            differs = abs(float(robust["q"]) - chosen_q) > 1e-12
            rec = {
                "scheme": scheme,
                "fold": int(row.get("fold", -1)),
                "heldoutPassed": bool(row.get("passed")),
                "heldoutLift": float(row.get("heldoutPrecisionLift", 0.0)),
                "chosenQ": chosen_q,
                "chosenSectionPassCount": int(selected["sectionPassCount"]),
                "chosenSectionMeanLift": float(selected["sectionMeanLift"]),
                "chosenSectionMedianLift": float(selected["sectionMedianLift"]),
                "chosenSectionMinLift": float(selected["sectionMinLift"]),
                "chosenSectionLiftStd": float(selected["sectionLiftStd"]),
                "robustQ": float(robust["q"]),
                "robustSectionPassCount": int(robust["sectionPassCount"]),
                "robustSectionMeanLift": float(robust["sectionMeanLift"]),
                "robustSectionMedianLift": float(robust["sectionMedianLift"]),
                "robustSectionMinLift": float(robust["sectionMinLift"]),
                "robustSectionLiftStd": float(robust["sectionLiftStd"]),
                "robustQDiffers": bool(differs),
            }
            rows.append(rec)
            print("SELECTOR", rec)

    passed = [r for r in rows if r["heldoutPassed"]]
    failed = [r for r in rows if not r["heldoutPassed"]]

    def mean(rs: list[dict[str, Any]], key: str) -> float:
        return round(float(np.mean([float(r[key]) for r in rs])), 3) if rs else 0.0

    pass_diff = sum(bool(r["robustQDiffers"]) for r in passed)
    fail_diff = sum(bool(r["robustQDiffers"]) for r in failed)
    pass_rate = pass_diff / len(passed) if passed else 0.0
    fail_rate = fail_diff / len(failed) if failed else 0.0

    summary = {
        "passingFolds": len(passed),
        "failingFolds": len(failed),
        "passingChosenMeanMinSectionLift": mean(passed, "chosenSectionMinLift"),
        "failingChosenMeanMinSectionLift": mean(failed, "chosenSectionMinLift"),
        "passingChosenMeanSectionLiftStd": mean(passed, "chosenSectionLiftStd"),
        "failingChosenMeanSectionLiftStd": mean(failed, "chosenSectionLiftStd"),
        "passingRobustQDiffers": pass_diff,
        "failingRobustQDiffers": fail_diff,
        "passingRobustQDiffersPct": round(100.0 * pass_rate, 2),
        "failingRobustQDiffersPct": round(100.0 * fail_rate, 2),
        "chosenQCountsPassing": dict(Counter(str(r["chosenQ"]) for r in passed)),
        "chosenQCountsFailing": dict(Counter(str(r["chosenQ"]) for r in failed)),
        "robustQCountsFailing": dict(Counter(str(r["robustQ"]) for r in failed)),
    }

    instability_signal = (
        len(failed) == 4
        and fail_rate >= 0.75
        and fail_rate >= pass_rate + 0.20
    ) or (
        summary["failingChosenMeanSectionLiftStd"] >= summary["passingChosenMeanSectionLiftStd"] + 2.0
        and summary["failingChosenMeanMinSectionLift"] < summary["passingChosenMeanMinSectionLift"]
    )

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-q-selector-stability-diagnostic",
        "rows": rows,
        "summary": summary,
        "selectorInstabilityHypothesisReady": bool(instability_signal),
        "nextTarget": "training-only worst-section-first q selection" if instability_signal else "do-not-change-q-selector-without-new-evidence",
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
        "selectorInstabilityHypothesisReady": bool(instability_signal),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    after = sha256(V5_PATH)
    if before != after:
        raise RuntimeError("V5 result changed during selector stability diagnostic")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 Q SELECTOR STABILITY V1 COMPLETE")
    print("SUMMARY", summary)
    print("Selector instability hypothesis ready:", bool(instability_signal))
    print("Next target:", output["nextTarget"])
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
