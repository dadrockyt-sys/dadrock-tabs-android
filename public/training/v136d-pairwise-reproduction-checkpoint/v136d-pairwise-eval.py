from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/workspaces/dadrock-tabs-android")
ANALYZER = ROOT / "analyzer"
sys.path.insert(0, str(ANALYZER))

import confirm_gomyway_3676_patch_rhythm24_v133_conjunction_guard_reserved_9mod16_over1024_v134 as v134
import benchmark_gomyway_3676_patch_ridge_relative_rank_calibration_nested_cv_v1 as legacy

v124 = v134.v124

SPEC_PATH = Path("/tmp/v136b-fixed-interaction-spec.json")
OUT_PATH = Path("/tmp/v136d-eval.json")

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320
KNOWN_PHASE = 0.3212890625
KNOWN_FOLD = 0
KNOWN_LIFT = 4.02


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


candidate_path = (
    v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
)
candidate_before = sha256(candidate_path)

if not SPEC_PATH.exists():
    raise RuntimeError("Frozen V136D interaction spec missing")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))

if spec.get("tuningAfterFreezeAllowed") is not False:
    raise RuntimeError("V136D spec is not frozen")

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
name_to_idx = {n: i for i, n in enumerate(names)}

xb = np.asarray(
    [
        [
            float((r.get("features") or {}).get(f, 0.0))
            for f in names
        ]
        for r in rows
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
    [str(r.get("label")) == "true" for r in rows],
    dtype=bool,
)

measures = np.asarray(
    [int(r["measure"]) for r in rows],
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
            f"Frozen V136D source column missing: {left} / {right}"
        )

    new_cols.append(
        xb[:, name_to_idx[left]] * xb[:, name_to_idx[right]]
    )
    new_names.append(new_name)

sustain_x = np.column_stack(new_cols)

if sustain_x.shape[1] != 15:
    raise RuntimeError(
        f"Expected 15 frozen sustain interactions, got {sustain_x.shape[1]}"
    )

if not np.isfinite(sustain_x).all():
    raise RuntimeError("Non-finite V136D interaction values")

aug_matrices = {
    name: (
        np.concatenate([matrix, sustain_x], axis=1)
        if name == "full_phase"
        else matrix.copy()
    )
    for name, matrix in matrices.items()
}

# V136D: isolate the frozen sustain intervention to full_phase only.
for name in ("base", "cosine", "v112_interactions"):
    if not np.array_equal(aug_matrices[name], matrices[name]):
        raise RuntimeError(
            f"V136D GUARD FAILED: preserved representation changed: {name}"
        )

if aug_matrices["full_phase"].shape[1] != matrices["full_phase"].shape[1] + 15:
    raise RuntimeError(
        "V136D GUARD FAILED: full_phase did not receive exactly 15 frozen interactions"
    )

print("V136D representation gate:")
print("  base: PRESERVED")
print("  cosine: PRESERVED")
print("  full_phase: +15 frozen sustain interactions")
print("  v112_interactions: PRESERVED")
print()


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

    # Authentic V134 behavior:
    # excluded safe-broad carriers fall back to the original
    # full_phase V28 result, which was evaluated at ANCHOR_Q.
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
                int(m),
                lo,
                hi,
                v124.OUTER_FOLDS,
                phase,
            )
            for m in measures
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

    scores = v124.v2.scores_for(
        matrix[test],
        model,
    )

    passed, lift, held, stats = v124.v17.pass_at_q(
        scores,
        y[test],
        q,
    )

    return {
        "phase": phase,
        "fold": fold,
        "pairRadius": radius,
        "lambda": lam,
        "q": q,
        "representation": actual_rep(row),
        "pass": bool(passed),
        "lift": round(float(lift), 2),
        "held": held,
        "stats": stats,
    }


print("=== V136D BASELINE REPRODUCTION GUARD ===", flush=True)

base_results = []
pass_mismatches = []
known = None

for i, row in enumerate(carriers, 1):
    rep = actual_rep(row)

    if rep not in matrices:
        raise RuntimeError(
            f"Unknown reconstructed representation: {rep}"
        )

    result = evaluate_one(row, matrices[rep])
    base_results.append(result)

    artifact_pass = bool(row["v134Passed"])

    if result["pass"] != artifact_pass:
        pass_mismatches.append({
            "phase": result["phase"],
            "fold": result["fold"],
            "artifactPass": artifact_pass,
            "reproducedPass": result["pass"],
            "artifactLift": row.get("heldoutPrecisionLift"),
            "reproducedLift": result["lift"],
            "representation": rep,
        })

    if (
        abs(result["phase"] - KNOWN_PHASE) < 1e-15
        and result["fold"] == KNOWN_FOLD
    ):
        known = result

    if i % 40 == 0:
        print(f"baseline heartbeat {i}/320", flush=True)

base_passes = sum(int(r["pass"]) for r in base_results)

print("baseline reproduced passes:", f"{base_passes}/320")
print("artifact pass mismatches:", len(pass_mismatches))

print()
print("=== CURRENT REPRODUCIBLE BASELINE FROZEN FOR THIS RUN ===")
if known is None:
    print("Known historical diagnostic carrier: not found")
else:
    print(
        "Known historical diagnostic carrier:",
        f"phase={known['phase']}",
        f"fold={known['fold']}",
        f"currentLift={known['lift']}",
        f"historicalLift={KNOWN_LIFT}",
    )
print(f"Current baseline passes: {base_passes}/320")
print(f"Historical-artifact pass mismatches: {len(pass_mismatches)}")
if pass_mismatches:
    print("First historical-artifact mismatches (diagnostic only):")
    for r in pass_mismatches[:12]:
        print(r)
if base_passes != EXPECTED_BASE_PASSES or pass_mismatches:
    raise RuntimeError(
        f"PAIRWISE V134 BASELINE GATE FAILED: "
        f"{base_passes}/320 with {len(pass_mismatches)} mismatches"
    )

print("PAIRWISE V134 BASELINE GATE PASSED: 311/320")
print("Historical-artifact pass mismatches: 0")
print("Frozen sustain evaluation may proceed.")
print()
print()


print("=== V136D 320-FOLD FIXED REPRESENTATION EVALUATION ===")
print("NO Q TUNING")
print("NO LAMBDA TUNING")
print("NO FAILURE-ONLY FITTING")
print("15 INTERACTIONS FROZEN BEFORE THIS EVALUATION")
print()

aug_results = []

for i, row in enumerate(carriers, 1):
    rep = actual_rep(row)

    result = evaluate_one(
        row,
        aug_matrices[rep],
    )

    aug_results.append(result)

    if i % 40 == 0:
        print(f"V136D heartbeat {i}/320", flush=True)

aug_passes = sum(int(r["pass"]) for r in aug_results)

gains = 0
losses = 0
changed = []

for base_r, aug_r in zip(base_results, aug_results):
    if aug_r["pass"] and not base_r["pass"]:
        gains += 1
        changed.append({
            "change": "GAIN",
            "phase": base_r["phase"],
            "fold": base_r["fold"],
            "baseLift": base_r["lift"],
            "v136dLift": aug_r["lift"],
            "representation": base_r["representation"],
        })

    elif base_r["pass"] and not aug_r["pass"]:
        losses += 1
        changed.append({
            "change": "LOSS",
            "phase": base_r["phase"],
            "fold": base_r["fold"],
            "baseLift": base_r["lift"],
            "v136dLift": aug_r["lift"],
            "representation": base_r["representation"],
        })

net = gains - losses

candidate_after = sha256(candidate_path)

if candidate_before != candidate_after:
    raise RuntimeError(
        "Protected candidate changed during V136D"
    )

out = {
    "experiment": "V136D-full-phase-only-fixed-sustain-envelope-interactions",
    "baseline": {
        "passes": base_passes,
        "total": EXPECTED_TOTAL,
        "knownCarrierLift": known["lift"],
        "rowPassMismatches": len(pass_mismatches),
    },
    "v136d": {
        "passes": aug_passes,
        "total": EXPECTED_TOTAL,
        "gains": gains,
        "losses": losses,
        "net": net,
        "crosses95Percent": (
            100.0 * aug_passes / EXPECTED_TOTAL >= 95.0
        ),
    },
    "interactionSpec": spec,
    "changedRows": changed,
    "candidateHashUnchanged": candidate_before == candidate_after,
    "reserve11mod16Inspected": False,
    "professionalMidtermAnswersUsed": False,
    "productionPromotionAllowed": False,
    "newHyperparameterTuningPerformed": False,
}

OUT_PATH.write_text(
    json.dumps(out, indent=2) + "\n",
    encoding="utf-8",
)

print()
print("=== V136D COMPLETE ===")
print(f"Current reproducible baseline: {base_passes}/320")
print(f"V136D fixed interactions: {aug_passes}/320")
print(f"Gains/losses vs current baseline: +{gains}/-{losses} net={net:+d}")
print(
    "Crosses 95 percent:",
    out["v136d"]["crosses95Percent"],
)
print(
    "Protected candidate hash unchanged:",
    candidate_before == candidate_after,
)
print("11-mod-16-over-1024 reserve inspected: False")
print("Professional/midterm answers used: False")
print("New hyperparameter tuning performed: False")
print("Production promotion: False")
print()

print("Changed carriers:")
if changed:
    for r in changed:
        print(
            f"{r['change']:4s} "
            f"phase={r['phase']:.12f} "
            f"fold={r['fold']} "
            f"baseLift={r['baseLift']:.2f} "
            f"v136dLift={r['v136dLift']:.2f} "
            f"rep={r['representation']}"
        )
else:
    print("none")

print()
print("saved:", OUT_PATH)
