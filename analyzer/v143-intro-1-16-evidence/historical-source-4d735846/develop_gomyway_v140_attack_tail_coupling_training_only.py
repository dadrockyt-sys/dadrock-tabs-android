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

SPEC_PATH = (
    PUBLIC
    / "training"
    / "v140-attack-tail-coupling-development"
    / "v140-attack-tail-spec.json"
)
OUT_PATH = (
    PUBLIC
    / "training"
    / "v140-attack-tail-coupling-development"
    / "v140-training-only-selector.json"
)

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


candidate_path = (
    v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
)
candidate_before = sha256(candidate_path)

if not SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V140 attack-tail spec missing: {SPEC_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
if int(spec.get("schemaVersion", -1)) != 140:
    raise RuntimeError("V140 attack-tail spec schema mismatch")
if spec.get("frozenBeforeDevelopmentRun") is not True:
    raise RuntimeError("V140 feature recipe was not frozen before development")
if int(spec.get("featureCount", -1)) != 15:
    raise RuntimeError("Expected exactly 15 frozen V140 attack-tail features")
if spec.get("heldoutV134ScoringAllowedDuringDevelopment") is not False:
    raise RuntimeError("V140 spec allows held-out V134 scoring during development")
for key in (
    "v136dEvaluationRowsAllowed",
    "v137HeldoutEvaluationRowsAllowed",
    "v138HeldoutEvaluationRowsAllowed",
    "v139HeldoutEvaluationRowsAllowed",
    "professionalMidtermAnswersAllowed",
    "reserve11mod16InspectionAllowed",
    "candidateModificationAllowed",
    "productionPromotionAllowed",
):
    if spec.get(key) is not False:
        raise RuntimeError(f"V140 frozen safety spec violation: {key}={spec.get(key)}")

rule = dict(spec.get("selectionRule") or {})
INNER_FOLDS = int(rule.get("innerFolds", 4))
PHASE_OFFSETS = [float(x) for x in (rule.get("validationPhaseOffsets") or [])]
MIN_VALID = int(rule.get("minimumValidInnerFoldsPerView", 3))
MIN_GAINS = int(rule.get("minimumPassGainsPerView", 1))
MAX_TOTAL_LOSSES = int(rule.get("maximumPassLossesAcrossAllViews", 0))
if PHASE_OFFSETS != [0.0, 0.125]:
    raise RuntimeError(f"Unexpected frozen V140 phase offsets: {PHASE_OFFSETS}")

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
        [float((row.get("features") or {}).get(name, 0.0)) for name in names]
        for row in rows
    ],
    dtype=np.float64,
)

pf = np.asarray(v124.v17.phase_features(rows), dtype=np.float64)
phase_interactions, _phase_names = v124.v112.build_phase_interactions(
    xb, names, pf
)

matrices = {
    "base": xb,
    "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
    "full_phase": np.concatenate([xb, pf], axis=1),
    "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
    "v112_interactions": np.concatenate(
        [xb, pf[:, [1, 3]], phase_interactions], axis=1
    ),
}

y = np.asarray(
    [str(row.get("label")) == "true" for row in rows], dtype=bool
)
measures = np.asarray([int(row["measure"]) for row in rows], dtype=np.int32)
lo = int(np.min(measures))
hi = int(np.max(measures))

bands = [str(x) for x in (spec.get("bands") or [])]
if bands != ["low", "lowMid", "mid", "highMid", "high"]:
    raise RuntimeError(f"Unexpected frozen V140 bands: {bands}")

coupling_cols: list[np.ndarray] = []
coupling_names: list[str] = []
for band in bands:
    burst = f"mean::{band}Burst"
    rise = f"mean::{band}Rise"
    decay60 = f"mean::{band}Decay60"
    post = f"mean::{band}PostSlope"
    missing = [n for n in (burst, rise, decay60, post) if n not in name_to_idx]
    if missing:
        raise RuntimeError(f"Missing V140 source columns for {band}: {missing}")

    burst_x = xb[:, name_to_idx[burst]]
    rise_x = xb[:, name_to_idx[rise]]
    decay60_x = xb[:, name_to_idx[decay60]]
    post_x = xb[:, name_to_idx[post]]

    coupling_cols.append(burst_x * decay60_x)
    coupling_names.append(f"v140::{band}::burst_x_decay60")
    coupling_cols.append(rise_x * decay60_x)
    coupling_names.append(f"v140::{band}::rise_x_decay60")
    coupling_cols.append(rise_x * post_x)
    coupling_names.append(f"v140::{band}::rise_x_postSlope")

coupling_x = np.column_stack(coupling_cols)
if coupling_x.shape[1] != 15:
    raise RuntimeError(
        f"Expected 15 V140 attack-tail columns, got {coupling_x.shape[1]}"
    )
if not np.isfinite(coupling_x).all():
    raise RuntimeError("Non-finite V140 attack-tail feature values")

carriers = []
for scheme in artifact.get("schemes") or []:
    for row in scheme.get("folds") or []:
        carriers.append(row)
if len(carriers) != EXPECTED_TOTAL:
    raise RuntimeError(f"Expected 320 V134 carriers, found {len(carriers)}")


def actual_rep(row: dict) -> str:
    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])
    bucket = str(row["originalQBucket"])
    decision = str(row["v96Decision"])
    selected = bool(row["selectedForV112"])

    use_tight = bucket == "tight"
    use_safe_broad = (
        bucket == "broad" and decision == "keep-broad-low-dispersion"
    )
    excluded_safe_broad = bool(
        use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12
    )
    use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

    if use_v96:
        v115_rep = "v112_interactions" if selected else "cosine"
    else:
        v115_rep = "full_phase"

    dangerous = bool(
        selected
        and use_v96
        and v124.is_v118_dangerous_signature(bucket, decision, radius, lam)
    )
    v118_rep = "cosine" if dangerous else v115_rep

    structural_rep = row.get("structuralRepresentation")
    v122_rep = str(structural_rep) if structural_rep else v118_rep
    v128_rep = v118_rep if bool(row.get("v127GuardApplied")) else v122_rep

    if bool(row.get("v134SelectiveInterventionApplied")):
        return "v112_interactions"
    return v128_rep


def q_for(row: dict) -> float:
    old_q = float(row["originalTrainingOnlyQ"])
    bucket = str(row["originalQBucket"])
    selector = row["selector"]
    candidate_q, decision, _dispersion = v124.v80.selected_q(
        {"outerQ": old_q, "selector": selector}
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
    if (
        excluded_safe_broad
        and row.get("finalRepresentation") == "full_phase"
        and not bool(row.get("structuralPolicyApplied"))
        and not bool(row.get("v127GuardApplied"))
        and not bool(row.get("v134SelectiveInterventionApplied"))
    ):
        return float(v124.ANCHOR_Q)

    q = float(candidate_q) if bucket == "tight" else float(v124.ANCHOR_Q)
    if bucket == "broad" and recorded_decision == "keep-broad-low-dispersion":
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
        matrix[train_mask], y[train_mask], measures[train_mask], radius, lam
    )
    scores = v124.v2.scores_for(matrix[val_mask], model)
    passed, lift, _held, _stats = v124.v17.pass_at_q(scores, y[val_mask], q)
    return {"pass": bool(passed), "lift": round(float(lift), 6)}


def evaluate_view(
    row: dict,
    base_matrix: np.ndarray,
    challenger_matrix: np.ndarray,
    outer_train: np.ndarray,
    phase_offset: float,
) -> dict:
    phase = float(row["phase"])
    inner_phase = (phase + phase_offset) % 1.0
    inner_ids = np.asarray(
        [
            v124.v18.phased_fold(
                int(measure), lo, hi, INNER_FOLDS, inner_phase
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
        if not np.any(y[val_mask]) or not np.any(~y[val_mask]):
            continue

        base = inner_eval(row, base_matrix, train_mask, val_mask)
        challenger = inner_eval(row, challenger_matrix, train_mask, val_mask)
        inner_rows.append(
            {
                "innerFold": inner_fold,
                "trainCount": train_count,
                "validationCount": val_count,
                "v134Pass": base["pass"],
                "v140Pass": challenger["pass"],
                "v134Lift": base["lift"],
                "v140Lift": challenger["lift"],
                "liftDelta": round(challenger["lift"] - base["lift"], 6),
            }
        )

    gains = sum(
        int(item["v140Pass"] and not item["v134Pass"])
        for item in inner_rows
    )
    losses = sum(
        int(item["v134Pass"] and not item["v140Pass"])
        for item in inner_rows
    )
    deltas = [float(item["liftDelta"]) for item in inner_rows]
    mean_delta = float(np.mean(deltas)) if deltas else 0.0
    median_delta = float(np.median(deltas)) if deltas else 0.0
    nonnegative = sum(int(delta >= 0.0) for delta in deltas)
    required_nonnegative = max(0, len(inner_rows) - 1)

    passed_rule = bool(
        len(inner_rows) >= MIN_VALID
        and gains >= MIN_GAINS
        and losses == 0
        and mean_delta > 0.0
        and median_delta >= 0.0
        and nonnegative >= required_nonnegative
    )

    return {
        "phaseOffset": phase_offset,
        "innerPhase": inner_phase,
        "validInnerFolds": len(inner_rows),
        "innerGains": gains,
        "innerLosses": losses,
        "meanInnerLiftDelta": round(mean_delta, 6),
        "medianInnerLiftDelta": round(median_delta, 6),
        "nonnegativeLiftFolds": nonnegative,
        "requiredNonnegativeLiftFolds": required_nonnegative,
        "viewRulePassed": passed_rule,
        "innerResults": inner_rows,
    }


def training_only_decision(row: dict) -> dict:
    phase = float(row["phase"])
    outer_fold = int(row["fold"])
    rep = actual_rep(row)
    if rep not in matrices:
        raise RuntimeError(f"Unknown V134 representation: {rep}")

    base_matrix = matrices[rep]
    challenger_matrix = np.concatenate([base_matrix, coupling_x], axis=1)

    outer_ids = np.asarray(
        [
            v124.v18.phased_fold(
                int(measure), lo, hi, v124.OUTER_FOLDS, phase
            )
            for measure in measures
        ],
        dtype=np.int16,
    )
    outer_train = outer_ids != outer_fold

    views = [
        evaluate_view(row, base_matrix, challenger_matrix, outer_train, offset)
        for offset in PHASE_OFFSETS
    ]
    total_losses = sum(int(view["innerLosses"]) for view in views)
    selected = bool(
        all(bool(view["viewRulePassed"]) for view in views)
        and total_losses <= MAX_TOTAL_LOSSES
    )

    return {
        "phase": phase,
        "fold": outer_fold,
        "v134Representation": rep,
        "selected": selected,
        "replicatedViews": views,
        "totalInnerLossesAcrossViews": total_losses,
        "reason": (
            "replicated frozen V140 training-only dominance"
            if selected
            else "replicated V140 dominance rule not met"
        ),
    }


print("=== V140 ATTACK-TAIL COUPLING TRAINING-ONLY DEVELOPMENT ===")
print("Frozen feature recipe loaded before scoring: True")
print("Attack-tail coupling features:", coupling_x.shape[1])
print("Replicated inner-CV phase offsets:", PHASE_OFFSETS)
print("V134 held-out fold scoring: DISABLED")
print("V136D evaluation rows: NOT READ")
print("V137 held-out evaluation rows: NOT READ")
print("V138 held-out evaluation rows: NOT READ")
print("V139 held-out evaluation rows: NOT READ")
print("Professional/midterm answers: NOT READ")
print("11-mod-16 reserve: NOT READ")
print("Candidate events: READ ONLY")
print("Eligible V134 representations: ALL FROZEN FAMILIES")
print()

decisions = []
for index, row in enumerate(carriers, 1):
    decisions.append(training_only_decision(row))
    if index % 40 == 0:
        print(f"training heartbeat {index}/320", flush=True)

selected = [item for item in decisions if item["selected"]]
by_rep: dict[str, int] = {}
for item in selected:
    rep = str(item["v134Representation"])
    by_rep[rep] = by_rep.get(rep, 0) + 1

candidate_after = sha256(candidate_path)
if candidate_before != candidate_after:
    raise RuntimeError(
        "Protected 949-event candidate changed during V140 development"
    )

out = {
    "experiment": "V140-attack-tail-coupling-training-only-development",
    "baselineChampion": {
        "name": "V134",
        "passes": 311,
        "total": 320,
        "scorePercent": 97.1875,
    },
    "frozenAttackTailSpec": {
        "path": str(SPEC_PATH.relative_to(ROOT)),
        "sha256": sha256(SPEC_PATH),
        "featureCount": int(coupling_x.shape[1]),
        "featureNames": coupling_names,
    },
    "selector": {
        "rule": rule,
        "selectedCarriers": len(selected),
        "selectedByRepresentation": by_rep,
    },
    "decisions": decisions,
    "heldoutV134FoldScored": False,
    "heldoutOutcomeFieldsUsedForSelection": False,
    "v136dEvaluationRowsRead": False,
    "v137HeldoutEvaluationRowsRead": False,
    "v138HeldoutEvaluationRowsRead": False,
    "v139HeldoutEvaluationRowsRead": False,
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "newQHyperparameterTuningPerformed": False,
    "newLambdaHyperparameterTuningPerformed": False,
    "newPairRadiusTuningPerformed": False,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchanged": candidate_before == candidate_after,
    "productionPromotionAllowed": False,
    "frozenForEvaluation": False,
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print()
print("=== V140 DEVELOPMENT COMPLETE ===")
print(f"Training-only attack-tail selections: {len(selected)}/320")
print("Selected by representation:", by_rep)
print("Held-out V134 folds scored: False")
print("V136D evaluation rows used: False")
print("V137 held-out evaluation rows used: False")
print("V138 held-out evaluation rows used: False")
print("V139 held-out evaluation rows used: False")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print("Protected 949-event candidate hash unchanged:", candidate_before == candidate_after)
print("Production promotion: False")
print("Frozen for evaluation: False")
print("Saved:", OUT_PATH)
