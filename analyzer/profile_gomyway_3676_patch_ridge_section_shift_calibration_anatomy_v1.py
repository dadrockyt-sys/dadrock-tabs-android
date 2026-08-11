from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_onset_slot_spectro_temporal_patch_stability_v1 as patch

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-section-shift-calibration-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-section-shift-calibration-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_rows(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    rows = payload.get(key)
    return list(rows) if isinstance(rows, list) else []


def summarize_scheme(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    lifts: list[float] = []
    bases: list[float] = []
    selected_rates: list[float] = []
    true_total = 0
    false_total = 0
    pass_count = 0
    lambda_counts: Counter[str] = Counter()
    q_counts: Counter[str] = Counter()
    folds: list[dict[str, Any]] = []

    for row in rows:
        test_rows = max(1, int(row.get("testRows") or 0))
        held = dict(row.get("heldoutCandidate") or {})
        base = dict(row.get("heldoutBase") or {})
        selected = int(held.get("selected") or 0)
        true = int(held.get("true") or 0)
        false = int(held.get("false") or 0)
        lift = float(row.get("heldoutPrecisionLift") or 0.0)
        base_precision = float(base.get("precision") or 0.0)
        passed = bool(row.get("passed"))
        lam = float(row.get("lambda") or row.get("gateLambda") or 0.0)
        q = float(row.get("tailQuantile") or row.get("q") or 0.0)

        lifts.append(lift)
        bases.append(base_precision)
        selected_rates.append(100.0 * selected / test_rows)
        true_total += true
        false_total += false
        pass_count += int(passed)
        lambda_counts[str(lam)] += 1
        q_counts[str(q)] += 1
        folds.append({
            "fold": int(row.get("fold") or 0),
            "testRows": test_rows,
            "basePrecision": round(base_precision, 2),
            "selected": selected,
            "selectedPct": round(100.0 * selected / test_rows, 2),
            "true": true,
            "false": false,
            "precision": float(held.get("precision") or 0.0),
            "lift": round(lift, 2),
            "passed": passed,
            "lambda": lam,
            "tailQuantile": q,
        })

    return {
        "scheme": name,
        "foldCount": len(rows),
        "passCount": pass_count,
        "meanLift": round(sum(lifts) / len(lifts), 3) if lifts else 0.0,
        "minLift": round(min(lifts), 3) if lifts else 0.0,
        "maxLift": round(max(lifts), 3) if lifts else 0.0,
        "meanBasePrecision": round(sum(bases) / len(bases), 3) if bases else 0.0,
        "meanSelectedPct": round(sum(selected_rates) / len(selected_rates), 3) if selected_rates else 0.0,
        "recoveredTrue": true_total,
        "recoveredFalse": false_total,
        "lambdaCounts": dict(lambda_counts),
        "tailQuantileCounts": dict(q_counts),
        "folds": folds,
    }


def calibration_flags(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    by_name = {str(s["scheme"]): s for s in summaries}
    normal = by_name.get("normal", {})
    section = by_name.get("section", {})
    shifted = by_name.get("shiftedWindow", {})

    normal_sel = float(normal.get("meanSelectedPct") or 0.0)
    section_sel = float(section.get("meanSelectedPct") or 0.0)
    shifted_sel = float(shifted.get("meanSelectedPct") or 0.0)
    normal_base = float(normal.get("meanBasePrecision") or 0.0)
    section_base = float(section.get("meanBasePrecision") or 0.0)
    shifted_base = float(shifted.get("meanBasePrecision") or 0.0)

    selection_shift = max(abs(section_sel - normal_sel), abs(shifted_sel - normal_sel))
    base_shift = max(abs(section_base - normal_base), abs(shifted_base - normal_base))
    return {
        "normalMeanSelectedPct": round(normal_sel, 3),
        "sectionMeanSelectedPct": round(section_sel, 3),
        "shiftedMeanSelectedPct": round(shifted_sel, 3),
        "maxSelectedPctShiftVsNormal": round(selection_shift, 3),
        "normalMeanBasePrecision": round(normal_base, 3),
        "sectionMeanBasePrecision": round(section_base, 3),
        "shiftedMeanBasePrecision": round(shifted_base, 3),
        "maxBasePrecisionShiftVsNormal": round(base_shift, 3),
        "calibrationShiftSuspected": bool(selection_shift >= 2.0 or base_shift >= 3.0),
    }


def main() -> None:
    before = sha256(patch.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Recurrent-gate benchmark is not anchored to frozen 36.76 champion")

    summaries = [
        summarize_scheme("normal", scheme_rows(payload, "normalCv")),
        summarize_scheme("section", scheme_rows(payload, "sectionCv")),
        summarize_scheme("shiftedWindow", scheme_rows(payload, "shiftedWindowCv")),
    ]
    flags = calibration_flags(summaries)

    after = sha256(patch.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during calibration anatomy profiler")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-section-shift-calibration-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "schemeSummaries": summaries,
        "calibrationFlags": flags,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": before == after,
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
        "candidateSha256": after,
        "calibrationShiftSuspected": bool(flags["calibrationShiftSuspected"]),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE SECTION SHIFT CALIBRATION ANATOMY V1 COMPLETE")
    for summary in summaries:
        print("SCHEME", {
            "scheme": summary["scheme"],
            "passCount": summary["passCount"],
            "meanLift": summary["meanLift"],
            "meanBasePrecision": summary["meanBasePrecision"],
            "meanSelectedPct": summary["meanSelectedPct"],
            "recoveredTrue": summary["recoveredTrue"],
            "recoveredFalse": summary["recoveredFalse"],
            "lambdaCounts": summary["lambdaCounts"],
            "tailQuantileCounts": summary["tailQuantileCounts"],
        })
        for fold in summary["folds"]:
            print("FOLD", summary["scheme"], fold)
    print("CALIBRATION", flags)
    print("Validated new champion: False")
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
