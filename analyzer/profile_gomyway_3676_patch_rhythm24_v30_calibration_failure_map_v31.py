from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V30_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v30-calibration-failure-map-v31.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v30-calibration-failure-map-v31-manifest.json"

# Reserved before V30. V31 diagnostic must never inspect these phases.
RESERVED_UNTOUCHED_PHASES = (
    0.03125, 0.09375, 0.15625, 0.21875,
    0.28125, 0.34375, 0.40625, 0.46875,
    0.53125, 0.59375, 0.65625, 0.71875,
    0.78125, 0.84375, 0.90625, 0.96875,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_float(value: Any) -> float | None:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def cutoff_diagnostics(calibration: dict[str, Any]) -> dict[str, Any]:
    calibrator = dict(calibration.get("calibrator") or {})
    intercept = safe_float(calibrator.get("intercept"))
    slope = safe_float(calibrator.get("slope"))
    if intercept is None or slope is None or abs(slope) < 1e-12:
        return {
            "intercept": intercept,
            "slope": slope,
            "effectivePercentileCutoff": None,
            "impliedTopFraction": None,
            "selectionDirection": "undefined",
        }

    cutoff = -intercept / slope
    if slope > 0:
        implied = 1.0 - cutoff
        direction = "high-percentile"
    else:
        implied = cutoff
        direction = "low-percentile"

    return {
        "intercept": round(intercept, 8),
        "slope": round(slope, 8),
        "effectivePercentileCutoff": round(float(cutoff), 8),
        "impliedTopFraction": round(float(implied), 8),
        "selectionDirection": direction,
        "cutoffInsideUnitInterval": bool(0.0 <= cutoff <= 1.0),
        "impliedTopFractionInsideUnitInterval": bool(0.0 <= implied <= 1.0),
    }


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cutoffs = [r["calibrationCutoff"]["effectivePercentileCutoff"] for r in rows]
    cutoffs = [float(x) for x in cutoffs if x is not None]
    implied = [r["calibrationCutoff"]["impliedTopFraction"] for r in rows]
    implied = [float(x) for x in implied if x is not None]
    selected = [int(r["v30HeldoutCandidate"]["selected"]) for r in rows]
    v28_selected = [int(r["v28HeldoutCandidate"]["selected"]) for r in rows]
    lifts = [float(r["v30HeldoutPrecisionLift"]) for r in rows]
    v28_lifts = [float(r["v28HeldoutPrecisionLift"]) for r in rows]

    def stats(values: list[float]) -> dict[str, Any]:
        if not values:
            return {"count": 0, "min": None, "median": None, "max": None, "mean": None}
        arr = np.asarray(values, dtype=np.float64)
        return {
            "count": int(arr.size),
            "min": round(float(np.min(arr)), 8),
            "median": round(float(np.median(arr)), 8),
            "max": round(float(np.max(arr)), 8),
            "mean": round(float(np.mean(arr)), 8),
        }

    return {
        "folds": len(rows),
        "effectivePercentileCutoff": stats(cutoffs),
        "impliedTopFraction": stats(implied),
        "v30Selected": stats([float(x) for x in selected]),
        "v28Selected": stats([float(x) for x in v28_selected]),
        "v30Lift": stats(lifts),
        "v28Lift": stats(v28_lifts),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(V30_PATH.read_text(encoding="utf-8"))
    if int(payload.get("schemaVersion", -1)) != 30:
        raise RuntimeError("Expected V30 payload")
    if bool(payload.get("exploratoryPromising")):
        raise RuntimeError("V31 failure-map diagnostic is only valid for retired/non-promising V30")
    if bool(payload.get("validatedNewChampion")):
        raise RuntimeError("V30 must not be a validated champion")

    challenge_phases = tuple(float(x) for x in payload.get("challengePhases") or [])
    expected_exposed = tuple(float(x) for x in v28.CONFIRM_PHASES)
    if challenge_phases != expected_exposed:
        raise RuntimeError("V30 challenge phases no longer match the already-exposed V28 phase family")
    if set(challenge_phases) & set(RESERVED_UNTOUCHED_PHASES):
        raise RuntimeError("Reserved untouched confirmation phase leaked into V31 diagnostic")

    rows: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    phase_counts: dict[float, Counter[str]] = defaultdict(Counter)

    for scheme in payload.get("schemes") or []:
        phase = float(scheme["phase"])
        if phase in RESERVED_UNTOUCHED_PHASES:
            raise RuntimeError("Reserved phase encountered")
        for fold in scheme.get("folds") or []:
            v30_pass = bool(fold.get("passed"))
            v28_cmp = dict(fold.get("v28Comparison") or {})
            v28_pass = bool(v28_cmp.get("passed"))
            if v30_pass and not v28_pass:
                status = "rescue"
            elif v28_pass and not v30_pass:
                status = "regression"
            elif v30_pass and v28_pass:
                status = "both-pass"
            else:
                status = "both-fail"

            status_counts[status] += 1
            phase_counts[phase][status] += 1
            row = {
                "phase": phase,
                "fold": int(fold["fold"]),
                "status": status,
                "v30Passed": v30_pass,
                "v28Passed": v28_pass,
                "chosenModel": fold.get("chosenModel"),
                "calibrationCutoff": cutoff_diagnostics(dict(fold.get("calibration") or {})),
                "v30HeldoutBase": fold.get("heldoutBase"),
                "v30HeldoutCandidate": fold.get("heldoutCandidate"),
                "v30HeldoutPrecisionLift": float(fold.get("heldoutPrecisionLift", 0.0)),
                "v28FrozenQ": float(v28_cmp.get("frozenQ", v28.FROZEN_Q)),
                "v28HeldoutCandidate": v28_cmp.get("heldoutCandidate"),
                "v28HeldoutPrecisionLift": float(v28_cmp.get("heldoutPrecisionLift", 0.0)),
            }
            rows.append(row)

    regressions = [r for r in rows if r["status"] == "regression"]
    rescues = [r for r in rows if r["status"] == "rescue"]
    both_pass = [r for r in rows if r["status"] == "both-pass"]
    both_fail = [r for r in rows if r["status"] == "both-fail"]

    # Diagnostic interpretation only. No threshold/model parameter is selected here.
    reg_selected_delta = [
        int(r["v30HeldoutCandidate"]["selected"]) - int(r["v28HeldoutCandidate"]["selected"])
        for r in regressions
    ]
    regression_selection_direction = {
        "v30SelectedMoreThanV28": int(sum(x > 0 for x in reg_selected_delta)),
        "v30SelectedSameAsV28": int(sum(x == 0 for x in reg_selected_delta)),
        "v30SelectedLessThanV28": int(sum(x < 0 for x in reg_selected_delta)),
    }

    cutoff_values = [
        r["calibrationCutoff"]["effectivePercentileCutoff"]
        for r in rows
        if r["calibrationCutoff"]["effectivePercentileCutoff"] is not None
    ]
    cutoff_spread = None
    if cutoff_values:
        cutoff_spread = float(max(cutoff_values) - min(cutoff_values))

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V31 diagnostic")

    output = {
        "schemaVersion": 31,
        "profileType": "36.76-rhythm24-v30-calibration-failure-map-diagnostic",
        "source": str(V30_PATH.relative_to(ROOT)),
        "diagnosticScope": "already-exposed-V28-phases-only",
        "challengePhases": list(challenge_phases),
        "reservedUntouchedPhasesConsumed": False,
        "reservedUntouchedPhases": list(RESERVED_UNTOUCHED_PHASES),
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "qSearchPerformed": False,
        "calibrationParameterSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "foldsTotal": len(rows),
        "statusCounts": dict(status_counts),
        "phaseStatusCounts": {
            str(k): dict(v) for k, v in sorted(phase_counts.items(), key=lambda kv: kv[0])
        },
        "groupSummaries": {
            "regressions": summarize_group(regressions),
            "rescues": summarize_group(rescues),
            "bothPass": summarize_group(both_pass),
            "bothFail": summarize_group(both_fail),
            "all": summarize_group(rows),
        },
        "regressionSelectionDirection": regression_selection_direction,
        "effectivePercentileCutoffSpread": None if cutoff_spread is None else round(cutoff_spread, 8),
        "diagnosticRows": rows,
        "diagnosticConclusionRule": (
            "Characterize whether V30 regressions align with unstable/effectively broad or narrow "
            "training-only percentile cutoffs. Do not select any new cutoff or architecture from held-out outcomes."
        ),
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 31,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsTotal": len(rows),
        "statusCounts": dict(status_counts),
        "regressionSelectionDirection": regression_selection_direction,
        "effectivePercentileCutoffSpread": None if cutoff_spread is None else round(cutoff_spread, 8),
        "reservedUntouchedPhasesConsumed": False,
        "heldoutLabelsUsedForDiagnosticComparison": True,
        "newTuningPerformed": False,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V30 CALIBRATION FAILURE MAP V31 COMPLETE")
    print("Status counts:", dict(status_counts))
    print("Regression selection direction:", regression_selection_direction)
    print("Effective percentile cutoff spread:", cutoff_spread)
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
