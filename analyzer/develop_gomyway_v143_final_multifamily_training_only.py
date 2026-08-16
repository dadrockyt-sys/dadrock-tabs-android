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
DEV_DIR = PUBLIC / "training" / "v143-final-multifamily-development"
SPEC_PATH = DEV_DIR / "v143-final-multifamily-spec.json"
OUT_PATH = DEV_DIR / "v143-training-only-selector.json"

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320
EPS = 1e-9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


candidate_path = v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
candidate_before = sha256(candidate_path)

if not SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V143 final multi-family spec missing: {SPEC_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
if int(spec.get("schemaVersion", -1)) != 143:
    raise RuntimeError("V143 final multi-family spec schema mismatch")
if spec.get("frozenBeforeDevelopmentRun") is not True:
    raise RuntimeError("V143 family menu was not frozen before development")
if spec.get("finalSweep") is not True or spec.get("stopAfterV143") is not True:
    raise RuntimeError("V143 is not marked as the final rhythm/sustain sweep")
if int(spec.get("totalMenuFeatureCount", -1)) != 80:
    raise RuntimeError("Expected exactly 80 features across the frozen V143 family menu")
if spec.get("heldoutV134ScoringAllowedDuringDevelopment") is not False:
    raise RuntimeError("V143 spec allows held-out V134 scoring during development")
for key in (
    "v136dEvaluationRowsAllowed",
    "v137HeldoutEvaluationRowsAllowed",
    "v138HeldoutEvaluationRowsAllowed",
    "v139HeldoutEvaluationRowsAllowed",
    "v140HeldoutEvaluationRowsAllowed",
    "v141HeldoutEvaluationRowsAllowed",
    "v142HeldoutEvaluationRowsAllowed",
    "professionalMidtermAnswersAllowed",
    "reserve11mod16InspectionAllowed",
    "candidateModificationAllowed",
    "productionPromotionAllowedDuringDevelopment",
):
    if spec.get(key) is not False:
        raise RuntimeError(f"V143 frozen safety spec violation: {key}={spec.get(key)}")
if spec.get("qTuningAllowed") is not False:
    raise RuntimeError("V143 spec allows Q tuning")
if spec.get("lambdaTuningAllowed") is not False:
    raise RuntimeError("V143 spec allows lambda tuning")
if spec.get("pairRadiusTuningAllowed") is not False:
    raise RuntimeError("V143 spec allows pair-radius tuning")

rule = dict(spec.get("selectionRule") or {})
INNER_FOLDS = int(rule.get("innerFolds", 4))
PHASE_OFFSETS = [float(x) for x in (rule.get("validationPhaseOffsets") or [])]
MIN_VALID = int(rule.get("minimumValidInnerFoldsPerView", 3))
MIN_GAINS = int(rule.get("minimumPassGainsPerView", 1))
MAX_TOTAL_LOSSES = int(rule.get("maximumPassLossesAcrossAllViewsForWinningFamily", 0))
if PHASE_OFFSETS != [0.0, 0.125]:
    raise RuntimeError(f"Unexpected frozen V143 phase offsets: {PHASE_OFFSETS}")

payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
rows = list(payload.get("candidateSlots") or [])
if not rows:
    raise RuntimeError("candidateSlots missing")
if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != v124.EXPECTED:
    raise RuntimeError("candidateSlots not anchored to frozen 36.76 champion")

artifact = json.loads(v134.OUTPUT_PATH.read_text(encoding="utf-8"))
if int(artifact.get("v134Passes", -1)) != EXPECTED_BASE_PASSES:
    raise RuntimeError(
        f"V134 artifact is not authoritative 311/320: {artifact.get('v134Passes')}/{artifact.get('foldsTotal')}"
    )
if int(artifact.get("foldsTotal", -1)) != EXPECTED_TOTAL:
    raise RuntimeError("V134 artifact does not contain 320 carriers")

names = sorted((rows[0].get("features") or {}).keys())
name_to_idx = {name: i for i, name in enumerate(names)}
xb = np.asarray(
    [[float((row.get("features") or {}).get(name, 0.0)) for name in names] for row in rows],
    dtype=np.float64,
)
pf = np.asarray(v124.v17.phase_features(rows), dtype=np.float64)
phase_interactions, _phase_names = v124.v112.build_phase_interactions(xb, names, pf)
matrices = {
    "base": xb,
    "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
    "full_phase": np.concatenate([xb, pf], axis=1),
    "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
    "v112_interactions": np.concatenate([xb, pf[:, [1, 3]], phase_interactions], axis=1),
}

y = np.asarray([str(row.get("label")) == "true" for row in rows], dtype=bool)
measures = np.asarray([int(row["measure"]) for row in rows], dtype=np.int32)
lo = int(np.min(measures))
hi = int(np.max(measures))

bands = [str(x) for x in (spec.get("bands") or [])]
stages = [str(x) for x in (spec.get("stages") or [])]
if bands != ["low", "lowMid", "mid", "highMid", "high"]:
    raise RuntimeError(f"Unexpected frozen V143 bands: {bands}")
if stages != ["Burst", "Rise", "Decay30", "Decay60", "PostSlope"]:
    raise RuntimeError(f"Unexpected frozen V143 stages: {stages}")

source: dict[str, dict[str, np.ndarray]] = {}
for band in bands:
    source[band] = {}
    for stage in stages:
        name = f"mean::{band}{stage}"
        if name not in name_to_idx:
            raise RuntimeError(f"Missing frozen V143 source column: {name}")
        source[band][stage] = xb[:, name_to_idx[name]]

family_features: dict[str, np.ndarray] = {}
family_names: dict[str, list[str]] = {}

# 1) Stabilized normalized temporal contrasts: 4 per band = 20.
cols: list[np.ndarray] = []
fnames: list[str] = []
for band in bands:
    seq = [source[band][stage] for stage in stages]
    for left_name, right_name, left, right in zip(stages[:-1], stages[1:], seq[:-1], seq[1:]):
        cols.append((right - left) / (np.abs(right) + np.abs(left) + EPS))
        fnames.append(f"v143::normalized_temporal_contrast::{band}::{right_name}_minus_{left_name}")
family_features["normalized_temporal_contrast"] = np.column_stack(cols)
family_names["normalized_temporal_contrast"] = fnames

# 2) Adjacent-band balance at each temporal stage: 4 per stage = 20.
cols = []
fnames = []
for stage in stages:
    for left_band, right_band in zip(bands[:-1], bands[1:]):
        cols.append(source[right_band][stage] - source[left_band][stage])
        fnames.append(f"v143::adjacent_band_balance::{stage}::{right_band}_minus_{left_band}")
family_features["adjacent_band_balance"] = np.column_stack(cols)
family_names["adjacent_band_balance"] = fnames

# 3) Spectral shape: absolute-energy centroid and spread at each stage = 10.
cols = []
fnames = []
band_axis = np.asarray([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)
for stage in stages:
    stage_values = np.column_stack([source[band][stage] for band in bands])
    energy = np.abs(stage_values) + EPS
    denom = np.sum(energy, axis=1)
    centroid = np.sum(energy * band_axis[None, :], axis=1) / denom
    spread = np.sum(energy * np.square(band_axis[None, :] - centroid[:, None]), axis=1) / denom
    cols.extend([centroid, spread])
    fnames.extend([f"v143::spectral_shape::{stage}::centroid", f"v143::spectral_shape::{stage}::spread"])
family_features["spectral_shape"] = np.column_stack(cols)
family_names["spectral_shape"] = fnames

# 4) Attack/sustain summary: attack mean, sustain mean, normalized contrast = 15.
cols = []
fnames = []
for band in bands:
    attack = 0.5 * (source[band]["Burst"] + source[band]["Rise"])
    sustain = (source[band]["Decay30"] + source[band]["Decay60"] + source[band]["PostSlope"]) / 3.0
    contrast = (sustain - attack) / (np.abs(sustain) + np.abs(attack) + EPS)
    cols.extend([attack, sustain, contrast])
    fnames.extend([
        f"v143::attack_sustain_summary::{band}::attack_mean",
        f"v143::attack_sustain_summary::{band}::sustain_mean",
        f"v143::attack_sustain_summary::{band}::normalized_sustain_minus_attack",
    ])
family_features["attack_sustain_summary"] = np.column_stack(cols)
family_names["attack_sustain_summary"] = fnames

# 5) Temporal extrema: range, standard deviation, stabilized endpoint contrast = 15.
cols = []
fnames = []
for band in bands:
    temporal = np.column_stack([source[band][stage] for stage in stages])
    temporal_range = np.max(temporal, axis=1) - np.min(temporal, axis=1)
    temporal_std = np.std(temporal, axis=1)
    burst = source[band]["Burst"]
    post = source[band]["PostSlope"]
    endpoint = (post - burst) / (np.abs(post) + np.abs(burst) + EPS)
    cols.extend([temporal_range, temporal_std, endpoint])
    fnames.extend([
        f"v143::temporal_extrema::{band}::range",
        f"v143::temporal_extrema::{band}::std",
        f"v143::temporal_extrema::{band}::normalized_endpoint_contrast",
    ])
family_features["temporal_extrema"] = np.column_stack(cols)
family_names["temporal_extrema"] = fnames

expected_counts = {name: int(meta["featureCount"]) for name, meta in dict(spec.get("families") or {}).items()}
if set(expected_counts) != set(family_features):
    raise RuntimeError(f"Frozen V143 family set mismatch: {sorted(expected_counts)} != {sorted(family_features)}")
for family, matrix in family_features.items():
    if matrix.shape[1] != expected_counts[family]:
        raise RuntimeError(f"V143 {family} expected {expected_counts[family]} columns, got {matrix.shape[1]}")
    if not np.isfinite(matrix).all():
        raise RuntimeError(f"Non-finite V143 feature values in {family}")
if sum(matrix.shape[1] for matrix in family_features.values()) != 80:
    raise RuntimeError("V143 frozen family menu does not total 80 features")

carriers = []
for scheme in artifact.get("schemes") or []:
    carriers.extend(scheme.get("folds") or [])
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
    use_safe_broad = bucket == "broad" and decision == "keep-broad-low-dispersion"
    excluded_safe_broad = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
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
    candidate_q, decision, _dispersion = v124.v80.selected_q({"outerQ": old_q, "selector": selector})
    recorded_decision = str(row["v96Decision"])
    if str(decision) != recorded_decision:
        raise RuntimeError(f"Q decision mismatch: {decision} != {recorded_decision}")

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


def inner_eval(row: dict, matrix: np.ndarray, train_mask: np.ndarray, val_mask: np.ndarray) -> dict:
    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])
    q = q_for(row)
    model = v124.v2.fit_pairwise_ranker(matrix[train_mask], y[train_mask], measures[train_mask], radius, lam)
    scores = v124.v2.scores_for(matrix[val_mask], model)
    passed, lift, _held, _stats = v124.v17.pass_at_q(scores, y[val_mask], q)
    return {"pass": bool(passed), "lift": round(float(lift), 6)}


def evaluate_all_families(
    row: dict,
    base_matrix: np.ndarray,
    challenger_matrices: dict[str, np.ndarray],
    outer_train: np.ndarray,
    phase_offset: float,
) -> dict[str, dict]:
    phase = float(row["phase"])
    inner_phase = (phase + phase_offset) % 1.0
    inner_ids = np.asarray(
        [v124.v18.phased_fold(int(measure), lo, hi, INNER_FOLDS, inner_phase) for measure in measures],
        dtype=np.int16,
    )

    family_rows: dict[str, list[dict]] = {name: [] for name in challenger_matrices}
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
        for family, matrix in challenger_matrices.items():
            challenger = inner_eval(row, matrix, train_mask, val_mask)
            family_rows[family].append(
                {
                    "innerFold": inner_fold,
                    "trainCount": train_count,
                    "validationCount": val_count,
                    "v134Pass": base["pass"],
                    "v143Pass": challenger["pass"],
                    "v134Lift": base["lift"],
                    "v143Lift": challenger["lift"],
                    "liftDelta": round(challenger["lift"] - base["lift"], 6),
                }
            )

    out: dict[str, dict] = {}
    for family, inner_rows in family_rows.items():
        gains = sum(int(item["v143Pass"] and not item["v134Pass"]) for item in inner_rows)
        losses = sum(int(item["v134Pass"] and not item["v143Pass"]) for item in inner_rows)
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
        out[family] = {
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
    return out


def family_summary(family: str, views: list[dict]) -> dict:
    total_losses = sum(int(view["innerLosses"]) for view in views)
    total_gains = sum(int(view["innerGains"]) for view in views)
    minimum_mean = min(float(view["meanInnerLiftDelta"]) for view in views)
    minimum_median = min(float(view["medianInnerLiftDelta"]) for view in views)
    sum_mean = sum(float(view["meanInnerLiftDelta"]) for view in views)
    qualified = bool(all(bool(view["viewRulePassed"]) for view in views) and total_losses <= MAX_TOTAL_LOSSES)
    return {
        "family": family,
        "qualified": qualified,
        "replicatedViews": views,
        "totalInnerGainsAcrossViews": total_gains,
        "totalInnerLossesAcrossViews": total_losses,
        "minimumMeanLiftDeltaAcrossViews": round(minimum_mean, 6),
        "minimumMedianLiftDeltaAcrossViews": round(minimum_median, 6),
        "sumMeanLiftDeltaAcrossViews": round(sum_mean, 6),
    }


def training_only_decision(row: dict) -> dict:
    phase = float(row["phase"])
    outer_fold = int(row["fold"])
    rep = actual_rep(row)
    if rep not in matrices:
        raise RuntimeError(f"Unknown V134 representation: {rep}")
    base_matrix = matrices[rep]
    challenger_matrices = {
        family: np.concatenate([base_matrix, family_x], axis=1)
        for family, family_x in family_features.items()
    }
    outer_ids = np.asarray(
        [v124.v18.phased_fold(int(measure), lo, hi, v124.OUTER_FOLDS, phase) for measure in measures],
        dtype=np.int16,
    )
    outer_train = outer_ids != outer_fold

    by_view = [
        evaluate_all_families(row, base_matrix, challenger_matrices, outer_train, offset)
        for offset in PHASE_OFFSETS
    ]
    summaries: list[dict] = []
    for family in sorted(family_features):
        views = [view_result[family] for view_result in by_view]
        summaries.append(family_summary(family, views))

    qualified = [item for item in summaries if item["qualified"]]
    qualified.sort(
        key=lambda item: (
            -float(item["minimumMeanLiftDeltaAcrossViews"]),
            -int(item["totalInnerGainsAcrossViews"]),
            -float(item["minimumMedianLiftDeltaAcrossViews"]),
            -float(item["sumMeanLiftDeltaAcrossViews"]),
            str(item["family"]),
        )
    )
    winner = qualified[0] if qualified else None
    selected = winner is not None
    return {
        "phase": phase,
        "fold": outer_fold,
        "v134Representation": rep,
        "selected": selected,
        "selectedFamily": str(winner["family"]) if winner else None,
        "selectedFamilyScore": {
            "minimumMeanLiftDeltaAcrossViews": winner["minimumMeanLiftDeltaAcrossViews"],
            "totalInnerGainsAcrossViews": winner["totalInnerGainsAcrossViews"],
            "minimumMedianLiftDeltaAcrossViews": winner["minimumMedianLiftDeltaAcrossViews"],
            "sumMeanLiftDeltaAcrossViews": winner["sumMeanLiftDeltaAcrossViews"],
        } if winner else None,
        "qualifiedFamilyCount": len(qualified),
        "familyResults": summaries,
        "reason": "frozen V143 replicated multi-family winner" if selected else "no frozen V143 family met replicated dominance rule",
    }


print("=== V143 FINAL MULTI-FAMILY TRAINING-ONLY SWEEP ===")
print("Frozen family menu loaded before scoring: True")
print("Families:", {name: matrix.shape[1] for name, matrix in family_features.items()})
print("Total menu features:", sum(matrix.shape[1] for matrix in family_features.values()))
print("Replicated inner-CV phase offsets:", PHASE_OFFSETS)
print("V134 held-out fold scoring: DISABLED")
print("V136D evaluation rows: NOT READ")
print("V137 held-out evaluation rows: NOT READ")
print("V138 held-out evaluation rows: NOT READ")
print("V139 held-out evaluation rows: NOT READ")
print("V140 held-out evaluation rows: NOT READ")
print("V141 held-out evaluation rows: NOT READ")
print("V142 held-out evaluation rows: NOT READ")
print("Professional/midterm answers: NOT READ")
print("11-mod-16 reserve: NOT READ")
print("Candidate events: READ ONLY")
print("Eligible V134 representations: ALL FROZEN FAMILIES")
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print()

decisions = []
for index, row in enumerate(carriers, 1):
    decisions.append(training_only_decision(row))
    if index % 20 == 0:
        print(f"training heartbeat {index}/320", flush=True)

selected = [item for item in decisions if item["selected"]]
by_rep: dict[str, int] = {}
by_family: dict[str, int] = {}
for item in selected:
    rep = str(item["v134Representation"])
    family = str(item["selectedFamily"])
    by_rep[rep] = by_rep.get(rep, 0) + 1
    by_family[family] = by_family.get(family, 0) + 1

candidate_after = sha256(candidate_path)
if candidate_before != candidate_after:
    raise RuntimeError("Protected 949-event candidate changed during V143 development")

out = {
    "experiment": "V143-final-multifamily-training-only-sweep",
    "baselineChampion": {"name": "V134", "passes": 311, "total": 320, "scorePercent": 97.1875},
    "frozenMultiFamilySpec": {
        "path": str(SPEC_PATH.relative_to(ROOT)),
        "sha256": sha256(SPEC_PATH),
        "familyFeatureCounts": {name: int(matrix.shape[1]) for name, matrix in family_features.items()},
        "familyFeatureNames": family_names,
        "totalMenuFeatureCount": int(sum(matrix.shape[1] for matrix in family_features.values())),
    },
    "selector": {
        "rule": rule,
        "selectedCarriers": len(selected),
        "selectedByRepresentation": by_rep,
        "selectedByFamily": by_family,
    },
    "decisions": decisions,
    "heldoutV134FoldScored": False,
    "heldoutOutcomeFieldsUsedForSelection": False,
    "v136dEvaluationRowsRead": False,
    "v137HeldoutEvaluationRowsRead": False,
    "v138HeldoutEvaluationRowsRead": False,
    "v139HeldoutEvaluationRowsRead": False,
    "v140HeldoutEvaluationRowsRead": False,
    "v141HeldoutEvaluationRowsRead": False,
    "v142HeldoutEvaluationRowsRead": False,
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "newQHyperparameterTuningPerformed": False,
    "newLambdaHyperparameterTuningPerformed": False,
    "newPairRadiusTuningPerformed": False,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchanged": candidate_before == candidate_after,
    "productionPromotionAllowed": False,
    "frozenForEvaluation": False,
    "finalRhythmSustainSweep": True,
    "stopAfterV143": True,
}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print()
print("=== V143 DEVELOPMENT COMPLETE ===")
print(f"Training-only multi-family selections: {len(selected)}/320")
print("Selected by family:", by_family)
print("Selected by representation:", by_rep)
print("Held-out V134 folds scored: False")
print("V136D evaluation rows used: False")
print("V137 held-out evaluation rows used: False")
print("V138 held-out evaluation rows used: False")
print("V139 held-out evaluation rows used: False")
print("V140 held-out evaluation rows used: False")
print("V141 held-out evaluation rows used: False")
print("V142 held-out evaluation rows used: False")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print("Protected 949-event candidate hash unchanged:", candidate_before == candidate_after)
print("Production promotion: False")
print("Frozen for evaluation: False")
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print("Saved:", OUT_PATH)
