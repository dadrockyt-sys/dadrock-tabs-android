from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
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
    / "v138-cross-band-sustain-development"
    / "v138-structure-spec.json"
)
FREEZE_PATH = (
    PUBLIC
    / "training"
    / "v138-cross-band-sustain-development"
    / "v138-frozen-selector.json"
)
OUT_PATH = (
    PUBLIC
    / "training"
    / "v138-cross-band-sustain-development"
    / "v138-heldout-evaluation.json"
)

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320
EXPECTED_SELECTED = 28
EXPECTED_BY_REP = {
    "full_phase": 6,
    "cosine": 14,
    "v112_interactions": 8,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if OUT_PATH.exists():
    raise RuntimeError(
        f"V138 held-out evaluation already exists at {OUT_PATH}; "
        "refusing to score the held-out folds again."
    )

candidate_path = (
    v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
)
candidate_before = sha256(candidate_path)

if not SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V138 structure spec missing: {SPEC_PATH}")
if not FREEZE_PATH.is_file():
    raise RuntimeError(f"Frozen V138 selector missing: {FREEZE_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

if int(spec.get("schemaVersion", -1)) != 138:
    raise RuntimeError("V138 structure spec schema mismatch")
if spec.get("frozenBeforeDevelopmentRun") is not True:
    raise RuntimeError("V138 structure recipe was not frozen before development")
if int(spec.get("featureCount", -1)) != 16:
    raise RuntimeError("Expected exactly 16 frozen V138 structure features")
if len(spec.get("features") or []) != 16:
    raise RuntimeError("Frozen V138 feature list is not length 16")
if spec.get("qTuningAllowed") is not False:
    raise RuntimeError("V138 spec allows Q tuning")
if spec.get("lambdaTuningAllowed") is not False:
    raise RuntimeError("V138 spec allows lambda tuning")
if spec.get("pairRadiusTuningAllowed") is not False:
    raise RuntimeError("V138 spec allows pair-radius tuning")
if spec.get("professionalMidtermAnswersAllowed") is not False:
    raise RuntimeError("V138 structure spec allows professional/midterm answers")
if spec.get("reserve11mod16InspectionAllowed") is not False:
    raise RuntimeError("V138 structure spec allows reserve inspection")
if spec.get("candidateModificationAllowed") is not False:
    raise RuntimeError("V138 structure spec allows candidate modification")

if int(freeze.get("schemaVersion", -1)) != 138:
    raise RuntimeError("V138 frozen selector schema mismatch")
if freeze.get("frozenBeforeHeldoutEvaluation") is not True:
    raise RuntimeError("V138 selector was not frozen before held-out evaluation")
if freeze.get("heldoutV134FoldScoredDuringDevelopment") is not False:
    raise RuntimeError("V138 development scored V134 held-out folds")
if freeze.get("heldoutOutcomeFieldsUsedForSelection") is not False:
    raise RuntimeError("V138 selector used held-out outcome fields")
if freeze.get("v136dEvaluationRowsUsed") is not False:
    raise RuntimeError("V138 selector used V136D evaluation rows")
if freeze.get("v137HeldoutEvaluationRowsUsed") is not False:
    raise RuntimeError("V138 selector used V137 held-out evaluation rows")
if freeze.get("professionalMidtermAnswersUsed") is not False:
    raise RuntimeError("V138 selector used professional/midterm answers")
if freeze.get("reserve11mod16Inspected") is not False:
    raise RuntimeError("V138 selector inspected the 11-mod-16 reserve")

stored_spec = freeze.get("structureSpec") or {}
if int(stored_spec.get("featureCount", -1)) != 16:
    raise RuntimeError("Frozen selector does not record the 16-feature spec")
if str(stored_spec.get("sha256") or "") != sha256(SPEC_PATH):
    raise RuntimeError("Frozen selector structure-spec SHA256 mismatch")

selected_rows = list(freeze.get("selected") or [])
if len(selected_rows) != EXPECTED_SELECTED:
    raise RuntimeError(
        f"Expected exactly {EXPECTED_SELECTED} frozen V138 selections, "
        f"got {len(selected_rows)}"
    )

selected_keys = {
    (round(float(item["phase"]), 12), int(item["fold"]))
    for item in selected_rows
}
if len(selected_keys) != EXPECTED_SELECTED:
    raise RuntimeError("Frozen V138 selections are not unique")

by_rep = Counter(str(item.get("v134Representation") or "") for item in selected_rows)
if dict(by_rep) != EXPECTED_BY_REP:
    raise RuntimeError(
        f"Frozen V138 representation counts changed: {dict(by_rep)}"
    )

for item in selected_rows:
    if int(item.get("innerLosses", -1)) != 0:
        raise RuntimeError("Frozen V138 selection contains an inner-CV pass loss")
    if int(item.get("innerGains", 0)) < 1:
        raise RuntimeError("Frozen V138 selection lacks an inner-CV pass gain")
    if float(item.get("meanInnerLiftDelta", 0.0)) <= 0.0:
        raise RuntimeError("Frozen V138 selection lacks positive mean lift delta")
    if float(item.get("medianInnerLiftDelta", -1.0)) < 0.0:
        raise RuntimeError("Frozen V138 selection has negative median lift delta")
    if int(item.get("nonnegativeLiftFolds", -1)) < int(
        item.get("requiredNonnegativeLiftFolds", 999)
    ):
        raise RuntimeError("Frozen V138 selection violates nonnegative-fold guard")

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
        [xb, pf[:, [1, 3]], phase_interactions],
        axis=1,
    ),
}

structure_cols = []
structure_names = []
for item in spec["features"]:
    operator = str(item.get("operator") or "")
    left = str(item.get("left") or "")
    right = str(item.get("right") or "")
    name = str(item.get("name") or "")

    if operator != "product":
        raise RuntimeError(f"Unsupported frozen V138 operator: {operator}")
    if left not in name_to_idx or right not in name_to_idx:
        raise RuntimeError(
            f"Frozen V138 source column missing: {left} / {right}"
        )

    structure_cols.append(
        xb[:, name_to_idx[left]] * xb[:, name_to_idx[right]]
    )
    structure_names.append(name)

structure_x = np.column_stack(structure_cols)
if structure_x.shape[1] != 16:
    raise RuntimeError(
        f"Expected 16 V138 structure columns, got {structure_x.shape[1]}"
    )
if not np.isfinite(structure_x).all():
    raise RuntimeError("Non-finite V138 structure feature values")

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
    use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

    if use_v96:
        v115_rep = "v112_interactions" if selected else "cosine"
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


def evaluate_one(row: dict, matrix: np.ndarray) -> dict:
    phase = float(row["phase"])
    fold = int(row["fold"])

    ids = np.asarray(
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
    train = ids != fold
    test = ids == fold

    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])
    q = q_for(row)

    model = v124.v2.fit_pairwise_ranker(
        matrix[train],
        y[train],
        measures[train],
        radius,
        lam,
    )
    scores = v124.v2.scores_for(matrix[test], model)
    passed, lift, _held, _stats = v124.v17.pass_at_q(
        scores,
        y[test],
        q,
    )

    return {
        "phase": phase,
        "fold": fold,
        "representation": actual_rep(row),
        "pass": bool(passed),
        "lift": round(float(lift), 2),
    }


print("=== V138 FROZEN CROSS-BAND SUSTAIN HELD-OUT EVALUATION ===")
print("Selector frozen before held-out scoring: True")
print("Frozen selected carriers:", len(selected_keys))
print("Frozen representation counts:", dict(by_rep))
print("Cross-band structure features:", len(structure_names))
print("V136D evaluation rows read: False")
print("V137 held-out evaluation rows read: False")
print("Professional/midterm answers read: False")
print("11-mod-16 reserve inspected: False")
print()

print("=== V134 BASELINE REPRODUCTION GUARD ===", flush=True)

base_results = []
mismatches = []
carrier_lookup = {}

for index, row in enumerate(carriers, 1):
    rep = actual_rep(row)
    if rep not in matrices:
        raise RuntimeError(f"Unknown V134 representation: {rep}")

    key = (round(float(row["phase"]), 12), int(row["fold"]))
    carrier_lookup[key] = row

    result = evaluate_one(row, matrices[rep])
    base_results.append(result)

    artifact_pass = bool(row["v134Passed"])
    if result["pass"] != artifact_pass:
        mismatches.append(
            {
                "phase": result["phase"],
                "fold": result["fold"],
                "artifactPass": artifact_pass,
                "reproducedPass": result["pass"],
                "artifactLift": row.get("heldoutPrecisionLift"),
                "reproducedLift": result["lift"],
                "representation": rep,
            }
        )

    if index % 40 == 0:
        print(f"baseline heartbeat {index}/320", flush=True)

base_passes = sum(int(item["pass"]) for item in base_results)
print(f"V134 reproduced baseline: {base_passes}/320")
print("Historical-artifact pass mismatches:", len(mismatches))

if base_passes != EXPECTED_BASE_PASSES or mismatches:
    raise RuntimeError(
        f"V134 BASELINE GATE FAILED: "
        f"{base_passes}/320 with {len(mismatches)} mismatches"
    )

for frozen_item in selected_rows:
    key = (
        round(float(frozen_item["phase"]), 12),
        int(frozen_item["fold"]),
    )
    row = carrier_lookup.get(key)
    if row is None:
        raise RuntimeError(f"Frozen V138 carrier not found: {key}")
    current_rep = actual_rep(row)
    frozen_rep = str(frozen_item["v134Representation"])
    if current_rep != frozen_rep:
        raise RuntimeError(
            f"Frozen V138 representation mismatch for {key}: "
            f"{current_rep} != {frozen_rep}"
        )

print("V134 BASELINE GATE PASSED: 311/320 with 0 mismatches")
print("Frozen selector representation guard passed: 28/28")
print()

print("=== V138 ONE-SHOT HELD-OUT SCORING ===", flush=True)

v138_results = []
applied = []

for index, row in enumerate(carriers, 1):
    phase = float(row["phase"])
    fold = int(row["fold"])
    rep = actual_rep(row)
    key = (round(phase, 12), fold)

    if key in selected_keys:
        matrix = np.concatenate([matrices[rep], structure_x], axis=1)
        applied.append(
            {
                "phase": phase,
                "fold": fold,
                "v134Representation": rep,
            }
        )
    else:
        matrix = matrices[rep]

    result = evaluate_one(row, matrix)
    v138_results.append(result)

    if index % 40 == 0:
        print(f"V138 heartbeat {index}/320", flush=True)

if len(applied) != EXPECTED_SELECTED:
    raise RuntimeError(
        f"Expected exactly {EXPECTED_SELECTED} V138 interventions, "
        f"applied {len(applied)}"
    )

applied_by_rep = Counter(item["v134Representation"] for item in applied)
if dict(applied_by_rep) != EXPECTED_BY_REP:
    raise RuntimeError(
        f"Applied V138 representation counts changed: {dict(applied_by_rep)}"
    )

v138_passes = sum(int(item["pass"]) for item in v138_results)

gains = 0
losses = 0
changed = []
for base_result, candidate_result in zip(base_results, v138_results):
    if candidate_result["pass"] and not base_result["pass"]:
        gains += 1
        changed.append(
            {
                "change": "GAIN",
                "phase": base_result["phase"],
                "fold": base_result["fold"],
                "baseLift": base_result["lift"],
                "v138Lift": candidate_result["lift"],
                "representation": base_result["representation"],
            }
        )
    elif base_result["pass"] and not candidate_result["pass"]:
        losses += 1
        changed.append(
            {
                "change": "LOSS",
                "phase": base_result["phase"],
                "fold": base_result["fold"],
                "baseLift": base_result["lift"],
                "v138Lift": candidate_result["lift"],
                "representation": base_result["representation"],
            }
        )

candidate_after = sha256(candidate_path)
if candidate_before != candidate_after:
    raise RuntimeError(
        "Protected 949-event candidate changed during V138 evaluation"
    )

promotion_candidate = bool(
    v138_passes > EXPECTED_BASE_PASSES
    and gains >= 1
    and losses == 0
)

out = {
    "experiment": "V138-frozen-cross-band-sustain-heldout-evaluation",
    "baseline": {
        "name": "V134",
        "passes": base_passes,
        "total": EXPECTED_TOTAL,
        "artifactPassMismatches": len(mismatches),
    },
    "v138": {
        "passes": v138_passes,
        "total": EXPECTED_TOTAL,
        "gains": gains,
        "losses": losses,
        "net": gains - losses,
        "selectedCarriers": len(selected_keys),
        "selectedByRepresentation": dict(by_rep),
        "appliedCarriers": applied,
        "promotionCandidate": promotion_candidate,
    },
    "changedCarriers": changed,
    "selectorFrozenBeforeHeldoutEvaluation": True,
    "structureSpecSha256": sha256(SPEC_PATH),
    "frozenSelectorSha256": sha256(FREEZE_PATH),
    "v136dEvaluationRowsRead": False,
    "v136dEvaluationLossesUsed": False,
    "v137HeldoutEvaluationRowsRead": False,
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "newQHyperparameterTuningPerformed": False,
    "newLambdaHyperparameterTuningPerformed": False,
    "newPairRadiusTuningPerformed": False,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchanged": True,
    "productionPromotionAllowed": False,
    "blind11mod16ConfirmationAllowed": promotion_candidate,
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(
    json.dumps(out, indent=2) + "\n",
    encoding="utf-8",
)

print()
print("=== V138 HELD-OUT EVALUATION COMPLETE ===")
print(f"V134 baseline: {base_passes}/320")
print(f"V138 cross-band sustain: {v138_passes}/320")
print(f"Gains/losses vs V134: +{gains}/-{losses} net={gains - losses:+d}")
print("Frozen V138 interventions applied:", len(applied))
print("Applied by representation:", dict(applied_by_rep))
print("Promotion candidate:", promotion_candidate)
print("Protected 949-event candidate hash unchanged: True")
print("Professional/midterm answers used: False")
print("V136D evaluation losses used: False")
print("V137 held-out evaluation rows used: False")
print("11-mod-16 reserve inspected: False")
print("Production promotion: False")
print("Blind 11-mod-16 confirmation allowed:", promotion_candidate)
print()
print("Changed carriers:")
if changed:
    for item in changed:
        print(
            f"{item['change']:4s} "
            f"phase={item['phase']:.12f} "
            f"fold={item['fold']} "
            f"baseLift={item['baseLift']:.2f} "
            f"v138Lift={item['v138Lift']:.2f} "
            f"rep={item['representation']}"
        )
else:
    print("none")

print()
print("Saved:", OUT_PATH)
