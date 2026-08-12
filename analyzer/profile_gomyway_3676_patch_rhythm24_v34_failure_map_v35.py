from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V34_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-conservative-allscheme-consensus-v34.json"
V32_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-robust-pass-threshold-consensus-v32.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v34-failure-map-v35.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v34-failure-map-v35-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(payload: dict[str, Any]) -> dict[tuple[float, int], dict[str, Any]]:
    out: dict[tuple[float, int], dict[str, Any]] = {}
    for scheme in payload.get("schemes", []):
        phase = float(scheme["phase"])
        for row in scheme.get("folds", []):
            out[(phase, int(row["fold"]))] = row
    return out


def direction(delta: int) -> str:
    if delta > 0:
        return "more"
    if delta < 0:
        return "less"
    return "same"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v34 = json.loads(V34_PATH.read_text(encoding="utf-8"))
    v32 = json.loads(V32_PATH.read_text(encoding="utf-8"))
    r34 = flatten(v34)
    r32 = flatten(v32)

    rows: list[dict[str, Any]] = []
    status_counts = Counter()
    regression_vs_v28_direction = Counter()
    rescue_vs_v28_direction = Counter()
    v34_vs_v32_selection_direction = Counter()
    limiting_scheme = Counter()
    cutoffs = []
    cutoff_shifts_vs_v32 = []

    for key in sorted(r34):
        row = r34[key]
        old = r32.get(key)
        vp = bool(row["passed"])
        bp = bool(row["v28Comparison"]["passed"])
        status = "bothPass" if vp and bp else "rescue" if vp else "regression" if bp else "bothFail"
        status_counts[status] += 1

        v34_sel = int(row["heldoutCandidate"]["selected"])
        v28_sel = int(row["v28Comparison"]["heldoutCandidate"]["selected"])
        delta28 = v34_sel - v28_sel
        if status == "regression":
            regression_vs_v28_direction[direction(delta28)] += 1
        elif status == "rescue":
            rescue_vs_v28_direction[direction(delta28)] += 1

        cal = row["trainingOnlyCalibration"]
        cutoff = float(cal["derivedPercentileCutoff"])
        cutoffs.append(cutoff)
        medians = list(cal.get("schemeMedians") or [])
        schemes = list(cal.get("innerSchemes") or ["normal", "section", "shiftedWindow"])
        limiter = None
        if medians and len(medians) == len(schemes):
            limiter = schemes[int(np.argmax(np.asarray(medians, dtype=np.float64)))]
            limiting_scheme[limiter] += 1

        v32_sel = None
        v32_cutoff = None
        if old is not None:
            v32_sel = int(old["heldoutCandidate"]["selected"])
            v34_vs_v32_selection_direction[direction(v34_sel - v32_sel)] += 1
            v32_cutoff = float(old["trainingOnlyCalibration"]["derivedPercentileCutoff"])
            cutoff_shifts_vs_v32.append(cutoff - v32_cutoff)

        rows.append({
            "phase": key[0],
            "fold": key[1],
            "status": status,
            "v34Selected": v34_sel,
            "v28Selected": v28_sel,
            "selectedDeltaVsV28": delta28,
            "selectionDirectionVsV28": direction(delta28),
            "v32Selected": v32_sel,
            "selectedDeltaVsV32": None if v32_sel is None else v34_sel - v32_sel,
            "v34Cutoff": cutoff,
            "v32Cutoff": v32_cutoff,
            "cutoffShiftVsV32": None if v32_cutoff is None else cutoff - v32_cutoff,
            "limitingScheme": limiter,
            "v34Lift": float(row["heldoutPrecisionLift"]),
            "v28Lift": float(row["v28Comparison"]["heldoutPrecisionLift"]),
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V35")

    cutoff_summary = {
        "min": float(np.min(cutoffs)),
        "median": float(np.median(cutoffs)),
        "max": float(np.max(cutoffs)),
        "spread": float(np.max(cutoffs) - np.min(cutoffs)),
    }
    shift_summary = {
        "mean": float(np.mean(cutoff_shifts_vs_v32)) if cutoff_shifts_vs_v32 else 0.0,
        "median": float(np.median(cutoff_shifts_vs_v32)) if cutoff_shifts_vs_v32 else 0.0,
        "min": float(np.min(cutoff_shifts_vs_v32)) if cutoff_shifts_vs_v32 else 0.0,
        "max": float(np.max(cutoff_shifts_vs_v32)) if cutoff_shifts_vs_v32 else 0.0,
    }

    output = {
        "schemaVersion": 35,
        "profileType": "36.76-rhythm24-v34-failure-map",
        "diagnosticScope": "already-exposed-V28-phases-only",
        "sourceV34": str(V34_PATH.relative_to(ROOT)),
        "sourceV32": str(V32_PATH.relative_to(ROOT)),
        "statusCounts": dict(status_counts),
        "regressionSelectionDirectionVsV28": dict(regression_vs_v28_direction),
        "rescueSelectionDirectionVsV28": dict(rescue_vs_v28_direction),
        "v34SelectionDirectionVsV32": dict(v34_vs_v32_selection_direction),
        "limitingSchemeCounts": dict(limiting_scheme),
        "derivedCutoffSummary": cutoff_summary,
        "cutoffShiftVsV32Summary": shift_summary,
        "rows": rows,
        "reservedUntouchedPhasesConsumed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "qSearchPerformed": False,
        "calibrationParameterSearchPerformed": False,
        "observedNumericCutoffAuthorizedForNextChallenger": False,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 35,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "statusCounts": dict(status_counts),
        "regressionSelectionDirectionVsV28": dict(regression_vs_v28_direction),
        "v34SelectionDirectionVsV32": dict(v34_vs_v32_selection_direction),
        "limitingSchemeCounts": dict(limiting_scheme),
        "derivedCutoffSpread": cutoff_summary["spread"],
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V34 FAILURE MAP V35 COMPLETE")
    print("Status counts:", dict(status_counts))
    print("Regression selection direction vs V28:", dict(regression_vs_v28_direction))
    print("V34 selection direction vs V32:", dict(v34_vs_v32_selection_direction))
    print("Limiting scheme counts:", dict(limiting_scheme))
    print("Derived cutoff summary:", cutoff_summary)
    print("Cutoff shift vs V32 summary:", shift_summary)
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
