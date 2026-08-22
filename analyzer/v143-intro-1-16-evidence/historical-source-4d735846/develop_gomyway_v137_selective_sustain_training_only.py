from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/workspaces/dadrock-tabs-android")
ANALYZER = ROOT / "analyzer"
PUBLIC = ROOT / "public"
sys.path.insert(0, str(ANALYZER))

import confirm_gomyway_3676_patch_rhythm24_v133_conjunction_guard_reserved_9mod16_over1024_v134 as v134

v124 = v134.v124

SUSTAIN_SPEC_PATH = (
    PUBLIC
    / "training"
    / "v136d-pairwise-reproduction-checkpoint"
    / "v136b-fixed-interaction-spec.json"
)
OUT_DIR = PUBLIC / "training" / "v137-selective-sustain-development"
OUT_PATH = OUT_DIR / "v137-training-only-selector.json"

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320
INNER_FOLDS = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


candidate_path = (
    v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
)
candidate_before = sha256(candidate_path)

if not SUSTAIN_SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V136 sustain spec missing: {SUSTAIN_SPEC_PATH}")

spec = json.loads(SUSTAIN_SPEC_PATH.read_text(encoding="utf-8"))

if int(spec.get("interactionCount", -1)) != 15:
    raise RuntimeError("Expected exactly 15 frozen V136 sustain interactions")

if len(spec.get("interactions") or []) != 15:
    raise RuntimeError("Frozen V136 sustain interaction list is not length 15")

if spec.get("tuningAfterFreezeAllowed") is not False:
    raise RuntimeError("Frozen V136 sustain spec allows tuning after freeze")

if spec.get("professionalMidtermAnswersUsed") is not False:
    raise RuntimeError("Frozen V136 sustain spec is not clean of professional answers")

payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
rows = list(payload.get("candidateSlots") or [])

if not rows:
    raise RuntimeError("candidateSlots missing")

if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != v124.EXPECTED:
    raise RuntimeError("candidateSlots not anchored to frozen 36.76 champion")

artifact = json.loads(v134.OUTPUT_PATH.read_text(encoding="utf-8"))

if int(artifact.get("v134Passes", -1)) != EXPECTED_BASE_PASSES:
    raise RuntimeError(
        f"V134 artifact is not authoritative 311/320: "
        f"{artifact.get('v134Passes')}/{artifact.get('foldsTotal')}"
    )

if int(artifact.get("foldsTotal", -1)) != EXPECTED_TOTAL:
    raise RuntimeError("V134 artifact does not contain 320 carriers")


names = sorted((rows[0].get("features") or {}).keys())
name_to_idx = {name: i for i, name in enumerate(names)}

xb = np.asarray(
    [
        [
            float((row.get("features") or {}).get(name, 0.0))
            for name in names
        ]
        for row in rows
    ],
    dtype=np.float64,
)

pf = np.asarray(v124.v17.phase_features(rows), dtype=np.float64)

phase_interactions, _phase_interaction_names = (
    v124.v112.build_phase_interactions(xb, names, pf)
)

matrices = {
    "base": xb,
    "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
    "full_phase": np.concatenate([xb, pf], axis=1),
    "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
    "v112_interactions": np.concatenate(
        [xb, pf[:, [1, 3]], phase_interactions],
        axis=1,
    ),
}

y = np.asarray(
    [str(row.get("label")) == "true" for row in rows],
    dtype=bool,
)

measures = np.asarray(
    [int(row["measure"]) for row in rows],
    dtype=np.int32,
)

lo = int(np.min(measures))
hi = int(np.max(measures))


new_cols = []
new_names = []

for item in spec["interactions"]:
    new_name = str(item["name"])
    left = str(item["left"])
    right = str(item["right"])

    if left not in name_to_idx or right not in name_to_idx:
        raise RuntimeError(
            f"Frozen V136 sustain source column missing: {left} / {right}"
        )

    new_cols.append(
        xb[:, name_to_idx[left]] * xb[:, name_to_idx[right]]
    )
    new_names.append(new_name)

sustain_x = np.column_stack(new_cols)

if sustain_x.shape[1] != 15:
    raise RuntimeError(
        f"Expected 15 frozen sustain columns, got {sustain_x.shape[1]}"
    )

if not np.isfinite(sustain_x).all():
    raise RuntimeError("Non-finite V136 sustain interaction values")

full_phase_sustain = np.concatenate(
    [matrices["full_phase"], sustain_x],
    axis=1,
)


carriers = []

for scheme in artifact.get("schemes") or []:
    for row in scheme.get("folds") or []:
        carriers.append(row)

if len(carriers) != EXPECTED_TOTAL:
    raise RuntimeError(
        f"Expected 320 V134 carriers, found {len(carriers)}"
    )


def actual_rep(row: dict) -> str:
    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])

    bucket = str(row["originalQBucket"])
    decision = str(row["v96Decision"])
    selected = bool(row["selectedForV112"])

    use_tight = bucket == "tight"

    use_safe_broad = (
        bucket == "broad"
        and decision == "keep-broad-low-dispersion"
    )

    excluded_safe_broad = bool(
        use_safe_broad
        and radius == 8
        and abs(lam - 1.0) < 1e-12
    )

    use_v96 = (
        use_tight
        or (use_safe_broad and not excluded_safe_broad)
    )

    if use_v96:
        v115_rep = (
            "v112_interactions"
            if selected
            else "cosine"
        )
    else:
        v115_rep = "full_phase"

    dangerous = bool(
        selected
        and use_v96
        and v124.is_v118_dangerous_signature(
            bucket, decision, radius, lam
        )
    )

    v118_rep = "cosine" if dangerous else v115_rep

    structural_rep = row.get("structuralRepresentation")

    if structural_rep:
        v122_rep = str(structural_rep)
    else:
        v122_rep = v118_rep

    if bool(row.get("v127GuardApplied")):
        v128_rep = v118_rep
    else:
        v128_rep = v122_rep

    if bool(row.get("v134SelectiveInterventionApplied")):
        return "v112_interactions"

    return v128_rep


def q_for(row: dict) -> float:
    old_q = float(row["originalTrainingOnlyQ"])
    bucket = str(row["originalQBucket"])
    selector = row["selector"]

    candidate_q, decision, _dispersion = v124.v80.selected_q(
        {
            "outerQ": old_q,
            "selector": selector,
        }
    )

    recorded_decision = str(row["v96Decision"])

    if str(decision) != recorded_decision:
        raise RuntimeError(
            f"Q decision mismatch: {decision} != {recorded_decision}"
        )

    radius = int(row["chosenModel"]["pairRadius"])
    lam = float(row["chosenModel"]["lambda"])

    excluded_safe_broad = bool(
        bucket == "broad"
        and recorded_decision == "keep-broad-low-dispersion"
        and radius == 8
        and abs(lam - 1.0) < 1e-12
    )

    # Authentic V134 behavior.
    if (
        excluded_safe_broad
        and row.get("finalRepresentation") == "full_phase"
        and not bool(row.get("structuralPolicyApplied"))
        and not bool(row.get("v127GuardApplied"))
        and not bool(row.get("v134SelectiveInterventionApplied"))
    ):
        return float(v124.ANCHOR_Q)

    q = (
        float(candidate_q)
        if bucket == "tight"
        else float(v124.ANCHOR_Q)
    )

    if (
        bucket == "broad"
        and recorded_decision == "keep-broad-low-dispersion"
    ):
        q = float(candidate_q)

    return q


def inner_eval(
    row: dict,
    matrix: np.ndarray,
    train_mask: np.ndarray,
    val_mask: np.ndarray,
) -> dict:
    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])
    q = q_for(row)

    model = v124.v2.fit_pairwise_ranker(
        matrix[train_mask],
        y[train_mask],
        measures[train_mask],
        radius,
        lam,
    )

    scores = v124.v2.scores_for(
        matrix[val_mask],
        model,
    )

    passed, lift, _held, _stats = v124.v17.pass_at_q(
        scores,
        y[val_mask],
        q,
    )

    return {
        "pass": bool(passed),
        "lift": round(float(lift), 6),
    }


def training_only_decision(row: dict) -> dict:
    phase = float(row["phase"])
    outer_fold = int(row["fold"])
    rep = actual_rep(row)

    result = {
        "phase": phase,
        "fold": outer_fold,
        "v134Representation": rep,
        "eligible": rep == "full_phase",
        "selected": False,
        "selectionRule": (
            "select sustain only when inner-CV has >=3 valid folds, "
            ">=1 pass gain, 0 pass losses, and positive mean lift delta"
        ),
    }

    if rep != "full_phase":
        result["reason"] = "V137 preserves non-full-phase V134 representations"
        return result

    outer_ids = np.asarray(
        [
            v124.v18.phased_fold(
                int(measure),
                lo,
                hi,
                v124.OUTER_FOLDS,
                phase,
            )
            for measure in measures
        ],
        dtype=np.int16,
    )

    # The V134 held-out fold is excluded before any V137 selection work.
    outer_train = outer_ids != outer_fold

    inner_ids = np.asarray(
        [
            v124.v18.phased_fold(
                int(measure),
                lo,
                hi,
                INNER_FOLDS,
                phase,
            )
            for measure in measures
        ],
        dtype=np.int16,
    )

    inner_rows = []

    for inner_fold in range(INNER_FOLDS):
        train_mask = outer_train & (inner_ids != inner_fold)
        val_mask = outer_train & (inner_ids == inner_fold)

        train_count = int(np.sum(train_mask))
        val_count = int(np.sum(val_mask))

        if train_count < 20 or val_count < 5:
            continue

        # Skip degenerate validation slices rather than inventing a score.
        if not np.any(y[val_mask]) or not np.any(~y[val_mask]):
            continue

        base = inner_eval(
            row,
            matrices["full_phase"],
            train_mask,
            val_mask,
        )

        sustain = inner_eval(
            row,
            full_phase_sustain,
            train_mask,
            val_mask,
        )

        inner_rows.append(
            {
                "innerFold": inner_fold,
                "trainCount": train_count,
                "validationCount": val_count,
                "v134Pass": base["pass"],
                "sustainPass": sustain["pass"],
                "v134Lift": base["lift"],
                "sustainLift": sustain["lift"],
                "liftDelta": round(
                    sustain["lift"] - base["lift"],
                    6,
                ),
            }
        )

    gains = sum(
        int(item["sustainPass"] and not item["v134Pass"])
        for item in inner_rows
    )
    losses = sum(
        int(item["v134Pass"] and not item["sustainPass"])
        for item in inner_rows
    )
    mean_lift_delta = (
        float(np.mean([item["liftDelta"] for item in inner_rows]))
        if inner_rows
        else 0.0
    )

    selected = bool(
        len(inner_rows) >= 3
        and gains >= 1
        and losses == 0
        and mean_lift_delta > 0.0
    )

    result.update(
        {
            "validInnerFolds": len(inner_rows),
            "innerGains": gains,
            "innerLosses": losses,
            "meanInnerLiftDelta": round(mean_lift_delta, 6),
            "selected": selected,
            "reason": (
                "strict training-only dominance"
                if selected
                else "training-only dominance rule not met"
            ),
            "innerResults": inner_rows,
        }
    )

    return result


print("=== V137 TRAINING-ONLY SELECTIVE SUSTAIN DEVELOPMENT ===")
print("V134 held-out fold scoring: DISABLED")
print("V136D changed/loss rows: NOT READ")
print("Professional/midterm answers: NOT READ")
print("Untouched reserve: NOT READ")
print("Candidate events: READ ONLY")
print("Eligible representation: full_phase only")
print("Selection: strict inner-CV dominance only")
print()

decisions = []

for index, row in enumerate(carriers, 1):
    decisions.append(training_only_decision(row))

    if index % 40 == 0:
        print(f"training heartbeat {index}/320", flush=True)

eligible = [item for item in decisions if item["eligible"]]
selected = [item for item in decisions if item["selected"]]

candidate_after = sha256(candidate_path)

if candidate_before != candidate_after:
    raise RuntimeError(
        "Protected 949-event candidate changed during V137 development"
    )

out = {
    "experiment": "V137-selective-sustain-training-only-development",
    "baselineChampion": {
        "name": "V134",
        "passes": 311,
        "total": 320,
        "scorePercent": 97.1875,
    },
    "sustainSource": {
        "name": str(spec.get("name") or ""),
        "interactionCount": 15,
        "specPath": str(SUSTAIN_SPEC_PATH.relative_to(ROOT)),
        "specSha256": sha256(SUSTAIN_SPEC_PATH),
    },
    "selector": {
        "eligibleRepresentation": "full_phase",
        "innerFolds": INNER_FOLDS,
        "rule": (
            "select sustain only when >=3 valid inner folds, "
            ">=1 sustain pass gain, 0 sustain pass losses, "
            "and positive mean sustain-minus-V134 lift"
        ),
        "eligibleCarriers": len(eligible),
        "selectedCarriers": len(selected),
    },
    "decisions": decisions,
    "heldoutV134FoldScored": False,
    "v136dEvaluationRowsRead": False,
    "v136dEvaluationLossesUsed": False,
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "newQHyperparameterTuningPerformed": False,
    "newLambdaHyperparameterTuningPerformed": False,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchanged": (
        candidate_before == candidate_after
    ),
    "productionPromotionAllowed": False,
    "frozenForEvaluation": False,
}

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(
    json.dumps(out, indent=2) + "\n",
    encoding="utf-8",
)

print()
print("=== V137 DEVELOPMENT COMPLETE ===")
print(f"Eligible full_phase carriers: {len(eligible)}/320")
print(f"Training-only sustain selections: {len(selected)}/320")
print("Held-out V134 folds scored: False")
print("V136D evaluation losses used: False")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print(
    "Protected 949-event candidate hash unchanged:",
    candidate_before == candidate_after,
)
print("Production promotion: False")
print("Frozen for evaluation: False")
print("Saved:", OUT_PATH)
