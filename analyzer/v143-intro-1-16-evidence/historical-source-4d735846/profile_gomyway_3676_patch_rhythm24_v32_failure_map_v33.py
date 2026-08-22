from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V32_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-robust-pass-threshold-consensus-v32.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v32-failure-map-v33.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v32-failure-map-v33-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V32_PATH.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    status_counts = {"bothPass": 0, "rescue": 0, "regression": 0, "bothFail": 0}
    regression_directions = {"v32SelectedMoreThanV28": 0, "v32SelectedSameAsV28": 0, "v32SelectedLessThanV28": 0}
    rescue_directions = {"v32SelectedMoreThanV28": 0, "v32SelectedSameAsV28": 0, "v32SelectedLessThanV28": 0}
    cutoffs = []

    for scheme in payload.get("schemes", []):
        phase = float(scheme["phase"])
        for row in scheme.get("folds", []):
            vp = bool(row["passed"])
            bp = bool(row["v28Comparison"]["passed"])
            if vp and bp:
                status = "bothPass"
            elif vp and not bp:
                status = "rescue"
            elif (not vp) and bp:
                status = "regression"
            else:
                status = "bothFail"
            status_counts[status] += 1

            v32_sel = int(row["heldoutCandidate"]["selected"])
            v28_sel = int(row["v28Comparison"]["heldoutCandidate"]["selected"])
            if v32_sel > v28_sel:
                direction = "v32SelectedMoreThanV28"
            elif v32_sel < v28_sel:
                direction = "v32SelectedLessThanV28"
            else:
                direction = "v32SelectedSameAsV28"
            if status == "regression":
                regression_directions[direction] += 1
            if status == "rescue":
                rescue_directions[direction] += 1

            cutoff = float(row["trainingOnlyCalibration"]["derivedPercentileCutoff"])
            cutoffs.append(cutoff)
            rows.append({
                "phase": phase,
                "fold": int(row["fold"]),
                "status": status,
                "trainingOnlyDerivedPercentileCutoff": cutoff,
                "v32Selected": v32_sel,
                "v28Selected": v28_sel,
                "selectedDelta": v32_sel - v28_sel,
                "selectionDirection": direction,
                "v32Lift": float(row["heldoutPrecisionLift"]),
                "v28Lift": float(row["v28Comparison"]["heldoutPrecisionLift"]),
                "liftDelta": float(row["heldoutPrecisionLift"]) - float(row["v28Comparison"]["heldoutPrecisionLift"]),
            })

    cutoff_summary = {
        "min": float(np.min(cutoffs)),
        "median": float(np.median(cutoffs)),
        "max": float(np.max(cutoffs)),
        "spread": float(np.max(cutoffs) - np.min(cutoffs)),
    }
    regression_rows = [r for r in rows if r["status"] == "regression"]
    rescue_rows = [r for r in rows if r["status"] == "rescue"]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V33")

    output = {
        "schemaVersion": 33,
        "profileType": "36.76-rhythm24-v32-failure-map",
        "diagnosticScope": "already-exposed-V28-phases-only",
        "source": str(V32_PATH.relative_to(ROOT)),
        "statusCounts": status_counts,
        "regressionSelectionDirection": regression_directions,
        "rescueSelectionDirection": rescue_directions,
        "derivedCutoffSummary": cutoff_summary,
        "regressionMeanSelectedDelta": float(np.mean([r["selectedDelta"] for r in regression_rows])) if regression_rows else 0.0,
        "rescueMeanSelectedDelta": float(np.mean([r["selectedDelta"] for r in rescue_rows])) if rescue_rows else 0.0,
        "rows": rows,
        "reservedUntouchedPhasesConsumed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "qSearchPerformed": False,
        "calibrationParameterSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 33,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "statusCounts": status_counts,
        "regressionSelectionDirection": regression_directions,
        "derivedCutoffSpread": cutoff_summary["spread"],
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V32 FAILURE MAP V33 COMPLETE")
    print("Status counts:", status_counts)
    print("Regression selection direction:", regression_directions)
    print("Rescue selection direction:", rescue_directions)
    print("Derived cutoff summary:", cutoff_summary)
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
