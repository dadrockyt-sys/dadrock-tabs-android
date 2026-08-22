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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-q-shape-predictive-signal-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-q-shape-predictive-signal-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _section_lifts(qrow: dict[str, Any]) -> list[float]:
    return [float(f.get("lift", 0.0)) for f in (qrow.get("folds") or []) if str(f.get("family")) == "section"]


def _metric(qrow: dict[str, Any]) -> dict[str, Any]:
    lifts = _section_lifts(qrow)
    return {
        "q": float(qrow.get("tailQuantile", 0.0)),
        "sectionPass": int(qrow.get("sectionPassCount", 0)),
        "sectionMean": float(qrow.get("sectionMeanLift", -999.0)),
        "sectionMedian": float(np.median(lifts)) if lifts else -999.0,
        "sectionMin": float(np.min(lifts)) if lifts else -999.0,
        "sectionStd": float(np.std(lifts)) if lifts else 999.0,
        "overallPass": int(qrow.get("overallPassCount", 0)),
        "overallMean": float(qrow.get("overallMeanLift", -999.0)),
    }


def analyze_shape(qdiag: list[dict[str, Any]], chosen_q: float) -> dict[str, Any]:
    ms = sorted((_metric(q) for q in qdiag), key=lambda r: r["q"])
    if not ms:
        raise RuntimeError("Empty q diagnostics")
    idx = next((i for i, r in enumerate(ms) if abs(r["q"] - chosen_q) < 1e-12), None)
    if idx is None:
        raise RuntimeError(f"Chosen q {chosen_q} missing from q diagnostics")
    c = ms[idx]
    left = ms[idx - 1] if idx > 0 else None
    right = ms[idx + 1] if idx + 1 < len(ms) else None

    section_best = max(ms, key=lambda r: (r["sectionPass"], r["sectionMean"], r["overallPass"], r["overallMean"], -r["q"]))
    overall_best = max(ms, key=lambda r: (r["overallPass"], r["overallMean"], r["sectionPass"], r["sectionMean"], -r["q"]))

    neighbors = [r for r in (left, right) if r is not None]
    nearest_section_drop = min((c["sectionMean"] - r["sectionMean"] for r in neighbors), default=0.0)
    nearest_abs_section_delta = min((abs(c["sectionMean"] - r["sectionMean"]) for r in neighbors), default=0.0)
    local_section_slope = 0.0
    if left is not None and right is not None:
        dq = right["q"] - left["q"]
        local_section_slope = (right["sectionMean"] - left["sectionMean"]) / dq if dq else 0.0
    elif right is not None:
        dq = right["q"] - c["q"]
        local_section_slope = (right["sectionMean"] - c["sectionMean"]) / dq if dq else 0.0
    elif left is not None:
        dq = c["q"] - left["q"]
        local_section_slope = (c["sectionMean"] - left["sectionMean"]) / dq if dq else 0.0

    same_pass = [r for r in ms if r["sectionPass"] == c["sectionPass"]]
    near_plateau = [r for r in same_pass if abs(r["sectionMean"] - c["sectionMean"]) <= 1.0]
    qvals = [r["q"] for r in near_plateau]
    plateau_width = (max(qvals) - min(qvals)) if qvals else 0.0

    return {
        "chosenQ": c["q"],
        "chosenIndex": idx,
        "gridSize": len(ms),
        "chosenAtGridEdge": idx == 0 or idx == len(ms) - 1,
        "chosenSectionPass": c["sectionPass"],
        "chosenSectionMeanLift": round(c["sectionMean"], 3),
        "chosenSectionMinLift": round(c["sectionMin"], 3),
        "chosenSectionLiftStd": round(c["sectionStd"], 3),
        "chosenOverallPass": c["overallPass"],
        "chosenOverallMeanLift": round(c["overallMean"], 3),
        "nearestSectionDrop": round(float(nearest_section_drop), 3),
        "nearestAbsSectionDelta": round(float(nearest_abs_section_delta), 3),
        "localSectionSlopePerQ": round(float(local_section_slope), 3),
        "plateauWidthQ": round(float(plateau_width), 3),
        "sectionBestQ": section_best["q"],
        "overallBestQ": overall_best["q"],
        "sectionOverallBestQDisagree": abs(section_best["q"] - overall_best["q"]) > 1e-12,
        "chosenVsOverallBestQDelta": round(c["q"] - overall_best["q"], 3),
        "sectionBestVsSecondGap": round(float(section_best["sectionMean"] - sorted([r["sectionMean"] for r in ms], reverse=True)[1]), 3) if len(ms) > 1 else 0.0,
    }


def mean(rows: list[dict[str, Any]], key: str) -> float:
    return round(float(np.mean([float(r[key]) for r in rows])), 3) if rows else 0.0


def rate(rows: list[dict[str, Any]], key: str) -> float:
    return round(100.0 * sum(bool(r[key]) for r in rows) / len(rows), 2) if rows else 0.0


def main() -> None:
    before = sha256(V5_PATH)
    payload = json.loads(V5_PATH.read_text(encoding="utf-8"))
    if int(payload.get("outerFoldsPassed", -1)) != 11:
        raise RuntimeError("Expected V5 11/15 baseline before q-shape diagnostic")

    rows: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        for row in payload.get(scheme) or []:
            chosen = row.get("chosen") or {}
            shape = analyze_shape(chosen.get("qDiagnostics") or [], float(chosen.get("tailQuantile")))
            rec = {
                "scheme": scheme,
                "fold": int(row.get("fold", -1)),
                "heldoutPassed": bool(row.get("passed")),
                "heldoutLift": float(row.get("heldoutPrecisionLift", 0.0)),
                **shape,
            }
            rows.append(rec)
            print("QSHAPE", rec)

    passed = [r for r in rows if r["heldoutPassed"]]
    failed = [r for r in rows if not r["heldoutPassed"]]

    summary = {
        "passingFolds": len(passed),
        "failingFolds": len(failed),
        "passingEdgePct": rate(passed, "chosenAtGridEdge"),
        "failingEdgePct": rate(failed, "chosenAtGridEdge"),
        "passingBestQDisagreementPct": rate(passed, "sectionOverallBestQDisagree"),
        "failingBestQDisagreementPct": rate(failed, "sectionOverallBestQDisagree"),
        "passingMeanNearestAbsSectionDelta": mean(passed, "nearestAbsSectionDelta"),
        "failingMeanNearestAbsSectionDelta": mean(failed, "nearestAbsSectionDelta"),
        "passingMeanPlateauWidthQ": mean(passed, "plateauWidthQ"),
        "failingMeanPlateauWidthQ": mean(failed, "plateauWidthQ"),
        "passingMeanAbsLocalSlope": round(float(np.mean([abs(float(r["localSectionSlopePerQ"])) for r in passed])), 3) if passed else 0.0,
        "failingMeanAbsLocalSlope": round(float(np.mean([abs(float(r["localSectionSlopePerQ"])) for r in failed])), 3) if failed else 0.0,
        "passingChosenQCounts": dict(Counter(str(r["chosenQ"]) for r in passed)),
        "failingChosenQCounts": dict(Counter(str(r["chosenQ"]) for r in failed)),
        "schemeFailureCounts": dict(Counter(str(r["scheme"]) for r in failed)),
    }

    signals: list[str] = []
    if summary["failingEdgePct"] >= summary["passingEdgePct"] + 30.0 and summary["failingEdgePct"] >= 50.0:
        signals.append("edgeChoice")
    if summary["failingBestQDisagreementPct"] >= summary["passingBestQDisagreementPct"] + 30.0 and summary["failingBestQDisagreementPct"] >= 50.0:
        signals.append("sectionOverallDisagreement")
    if summary["failingMeanAbsLocalSlope"] >= summary["passingMeanAbsLocalSlope"] * 1.5 and summary["failingMeanAbsLocalSlope"] >= 20.0:
        signals.append("sharpLocalSlope")
    if summary["failingMeanPlateauWidthQ"] <= summary["passingMeanPlateauWidthQ"] * 0.5 and summary["passingMeanPlateauWidthQ"] >= 0.025:
        signals.append("narrowPeak")
    if summary["failingMeanNearestAbsSectionDelta"] >= summary["passingMeanNearestAbsSectionDelta"] * 1.5 and summary["failingMeanNearestAbsSectionDelta"] >= 2.0:
        signals.append("neighborSensitivity")

    predictive = len(signals) >= 1
    next_target = "derive-training-only-q-direction-rule-from-active-shape-signal" if predictive else "no-learnable-q-shape-signal-retire-further-selector-tuning"

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-q-shape-predictive-signal-diagnostic",
        "rows": rows,
        "summary": summary,
        "activePredictiveSignals": signals,
        "qShapePredictiveSignalReady": predictive,
        "nextTarget": next_target,
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
        "qShapePredictiveSignalReady": predictive,
        "activePredictiveSignals": signals,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    if before != sha256(V5_PATH):
        raise RuntimeError("V5 result changed during q-shape diagnostic")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 Q SHAPE PREDICTIVE SIGNAL V1 COMPLETE")
    print("SUMMARY", summary)
    print("Active predictive signals:", signals)
    print("Q-shape predictive signal ready:", predictive)
    print("Next target:", next_target)
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
