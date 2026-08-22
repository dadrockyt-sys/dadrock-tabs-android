from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V36_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-trainingonly-tighten-v36.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v36-percentile-anchor-equivalence-v37.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v36-percentile-anchor-equivalence-v37-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V36_PATH.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    status_counts = {"bothPass": 0, "rescue": 0, "regression": 0, "bothFail": 0}
    selection_direction = {"v36More": 0, "same": 0, "v36Less": 0}
    selected_deltas = []
    tightened_rows = 0

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

            v36_sel = int(row["heldoutCandidate"]["selected"])
            v28_sel = int(row["v28Comparison"]["heldoutCandidate"]["selected"])
            delta = v36_sel - v28_sel
            selected_deltas.append(delta)
            if delta > 0:
                direction = "v36More"
            elif delta < 0:
                direction = "v36Less"
            else:
                direction = "same"
            selection_direction[direction] += 1

            calibration = row["trainingOnlyCalibration"]
            tightened = bool(calibration["tightenedBeyondV28Floor"])
            tightened_rows += int(tightened)
            rows.append({
                "phase": phase,
                "fold": int(row["fold"]),
                "status": status,
                "v36Cutoff": float(calibration["derivedPercentileCutoff"]),
                "v28PercentileFloor": float(calibration["v28PercentileFloor"]),
                "trainingOnlyConservativeCutoff": float(calibration["trainingOnlyConservativeCutoff"]),
                "tightenedBeyondV28Floor": tightened,
                "v36Selected": v36_sel,
                "v28Selected": v28_sel,
                "selectedDelta": delta,
                "selectionDirection": direction,
                "v36Lift": float(row["heldoutPrecisionLift"]),
                "v28Lift": float(row["v28Comparison"]["heldoutPrecisionLift"]),
                "liftDelta": float(row["heldoutPrecisionLift"]) - float(row["v28Comparison"]["heldoutPrecisionLift"]),
            })

    changed_status_rows = [r for r in rows if r["status"] in ("rescue", "regression")]
    changed_selection_count_rows = [r for r in rows if r["selectedDelta"] != 0]
    same_count_status_changes = [r for r in changed_status_rows if r["selectedDelta"] == 0]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V37")

    output = {
        "schemaVersion": 37,
        "profileType": "36.76-rhythm24-v36-percentile-anchor-equivalence-diagnostic",
        "diagnosticScope": "already-exposed-V28-phases-only",
        "source": str(V36_PATH.relative_to(ROOT)),
        "purpose": "determine why fixed percentile floor 0.80 differs from frozen V28 top-fraction q=0.20 when no training-only tightening occurred",
        "statusCounts": status_counts,
        "selectionDirectionAllRows": selection_direction,
        "foldsTightenedBeyondV28Floor": int(tightened_rows),
        "statusChangedRows": len(changed_status_rows),
        "selectedCountChangedRows": len(changed_selection_count_rows),
        "statusChangedWithSameSelectedCountRows": len(same_count_status_changes),
        "selectedDeltaSummary": {
            "min": int(np.min(selected_deltas)) if selected_deltas else 0,
            "median": float(np.median(selected_deltas)) if selected_deltas else 0.0,
            "max": int(np.max(selected_deltas)) if selected_deltas else 0,
        },
        "rows": rows,
        "interpretationConstraint": "diagnostic only; do not use status-change outcomes to tune a new cutoff",
        "reservedUntouchedPhasesConsumed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "qSearchPerformed": False,
        "calibrationParameterSearchPerformed": False,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 37,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "statusCounts": status_counts,
        "foldsTightenedBeyondV28Floor": int(tightened_rows),
        "statusChangedRows": len(changed_status_rows),
        "selectedCountChangedRows": len(changed_selection_count_rows),
        "statusChangedWithSameSelectedCountRows": len(same_count_status_changes),
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V36 PERCENTILE ANCHOR EQUIVALENCE V37 COMPLETE")
    print("Status counts:", status_counts)
    print("Folds tightened beyond V28 floor:", tightened_rows)
    print("Selection direction all rows:", selection_direction)
    print("Status-changed rows:", len(changed_status_rows))
    print("Selected-count-changed rows:", len(changed_selection_count_rows))
    print("Status changes with same selected count:", len(same_count_status_changes))
    print("Selected delta summary:", output["selectedDeltaSummary"])
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
