from __future__ import annotations

import hashlib
import json
import math
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
DEV_DIR = PUBLIC / "training" / "v143-final-multifamily-development"
V143_SPEC_PATH = DEV_DIR / "v143-final-multifamily-spec.json"
V143_FREEZE_PATH = DEV_DIR / "v143-frozen-selector.json"
V143_HELDOUT_PATH = DEV_DIR / "v143-heldout-evaluation.json"
BLIND_SPEC_PATH = DEV_DIR / "v143-blind-11mod16-confirmation-spec.json"
OUT_PATH = DEV_DIR / "v143-blind-11mod16-confirmation.json"

RESERVED_PHASES = tuple((11 + 16 * k) / 1024.0 for k in range(64))
EXPECTED_TOTAL = 320
EXPECTED_FAMILIES = {
    "normalized_temporal_contrast": 20,
    "adjacent_band_balance": 20,
    "spectral_shape": 10,
    "attack_sustain_summary": 15,
    "temporal_extrema": 15,
}
EXPECTED_PHASE_OFFSETS = [0.0, 0.125]
INNER_FOLDS = 4
MIN_VALID = 3
MIN_GAINS = 1
MAX_TOTAL_LOSSES = 0
EPS = 1e-9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


if OUT_PATH.exists():
    raise RuntimeError(
        f"V143 blind 11-mod-16 confirmation already exists at {OUT_PATH}; "
        "refusing to inspect the reserve a second time."
    )

for path in (V143_SPEC_PATH, V143_FREEZE_PATH, V143_HELDOUT_PATH, BLIND_SPEC_PATH):
    require(path.is_file(), f"Required frozen artifact missing: {path}")

spec = json.loads(V143_SPEC_PATH.read_text(encoding="utf-8"))
freeze = json.loads(V143_FREEZE_PATH.read_text(encoding="utf-8"))
heldout = json.loads(V143_HELDOUT_PATH.read_text(encoding="utf-8"))
blind_spec = json.loads(BLIND_SPEC_PATH.read_text(encoding="utf-8"))

require(int(blind_spec.get("schemaVersion", -1)) == 14311, "Blind confirmation spec schema mismatch")
require(blind_spec.get("frozenBeforeReserveInspection") is True, "Blind confirmation protocol was not frozen before reserve inspection")
require(blind_spec.get("reservePhaseFamily") == "numerators-11-mod-16-over-1024", "Unexpected blind reserve family")
require(int(blind_spec.get("reservePhaseCount", -1)) == 64, "Blind reserve phase count changed")
require(int(blind_spec.get("outerFoldsPerPhase", -1)) == 5, "Blind reserve fold count changed")
require(int(blind_spec.get("expectedCarrierCount", -1)) == EXPECTED_TOTAL, "Blind reserve carrier count changed")
require(blind_spec.get("baseline") == "V134" and blind_spec.get("challenger") == "V143", "Blind confirmation baseline/challenger changed")
require(blind_spec.get("oneShotReserveEvaluation") is True, "Blind confirmation is not one-shot")
require(blind_spec.get("priorHeldoutRowsAllowedForReserveSelection") is False, "Blind protocol allows prior held-out rows in reserve selection")
require(blind_spec.get("v143HeldoutOutcomeAllowedForReserveSelection") is False, "Blind protocol allows V143 held-out outcome in reserve selection")
require(blind_spec.get("professionalMidtermAnswersAllowed") is False, "Blind protocol allows professional answers")
require(blind_spec.get("candidateModificationAllowed") is False, "Blind protocol allows candidate modification")
require(blind_spec.get("productionPromotionBeforeBlindConfirmationAllowed") is False, "Blind protocol allows pre-confirmation promotion")
require(blind_spec.get("finalRhythmSustainSweep") is True, "Blind protocol is not marked final")
require(blind_spec.get("stopAfterV143") is True, "Blind protocol does not stop after V143")
require(blind_spec.get("noV144RhythmSustainSweepAllowed") is True, "Blind protocol improperly allows V144")

transport = dict(blind_spec.get("v143TransportPolicy") or {})
require(int(transport.get("familyMenuFeatureCount", -1)) == 80, "Blind V143 family menu count changed")
require(dict(transport.get("families") or {}) == EXPECTED_FAMILIES, "Blind V143 family menu changed")
require(int(transport.get("innerFolds", -1)) == INNER_FOLDS, "Blind inner-fold count changed")
require([float(x) for x in (transport.get("replicatedValidationPhaseOffsets") or [])] == EXPECTED_PHASE_OFFSETS, "Blind phase offsets changed")
require(int(transport.get("minimumValidInnerFoldsPerView", -1)) == MIN_VALID, "Blind minimum-valid rule changed")
require(int(transport.get("minimumPassGainsPerView", -1)) == MIN_GAINS, "Blind minimum-gain rule changed")
require(int(transport.get("maximumPassLossesAcrossAllViews", -1)) == MAX_TOTAL_LOSSES, "Blind zero-loss rule changed")
require(transport.get("requirePositiveMeanLiftDeltaPerView") is True, "Blind mean-lift rule changed")
require(transport.get("requireNonnegativeMedianLiftDeltaPerView") is True, "Blind median-lift rule changed")
require(transport.get("allowAtMostOneNegativeLiftFoldPerView") is True, "Blind nonnegative-fold rule changed")
require(transport.get("qTuningAllowed") is False, "Blind protocol allows Q tuning")
require(transport.get("lambdaTuningAllowed") is False, "Blind protocol allows lambda tuning")
require(transport.get("pairRadiusTuningAllowed") is False, "Blind protocol allows pair-radius tuning")

promotion_rule = dict(blind_spec.get("promotionRule") or {})
require(promotion_rule.get("requireV143PassesGreaterThanV134") is True, "Blind promotion strict-improvement rule changed")
require(int(promotion_rule.get("minimumBlindGains", -1)) == 1, "Blind minimum-gain promotion rule changed")
require(int(promotion_rule.get("maximumBlindLosses", -1)) == 0, "Blind zero-loss promotion rule changed")
require(int(promotion_rule.get("minimumV143PassesPerPhase", -1)) == 3, "Blind minimum-phase promotion rule changed")
require(promotion_rule.get("validatedNewChampionOnlyIfAllConditionsPass") is True, "Blind all-conditions promotion rule changed")

require(int(spec.get("schemaVersion", -1)) == 143, "Frozen V143 multi-family spec mismatch")
require(spec.get("frozenBeforeDevelopmentRun") is True, "V143 family menu was not frozen before development")
require(spec.get("finalSweep") is True and spec.get("stopAfterV143") is True, "V143 spec is not final")
require(int(spec.get("totalMenuFeatureCount", -1)) == 80, "V143 family menu count changed")
require({name: int(meta.get("featureCount", -1)) for name, meta in dict(spec.get("families") or {}).items()} == EXPECTED_FAMILIES, "V143 family counts changed")

rule = dict(spec.get("selectionRule") or {})
require(int(rule.get("innerFolds", -1)) == INNER_FOLDS, "V143 inner-fold rule changed")
require([float(x) for x in (rule.get("validationPhaseOffsets") or [])] == EXPECTED_PHASE_OFFSETS, "V143 phase offsets changed")
require(int(rule.get("minimumValidInnerFoldsPerView", -1)) == MIN_VALID, "V143 minimum-valid rule changed")
require(int(rule.get("minimumPassGainsPerView", -1)) == MIN_GAINS, "V143 minimum-gain rule changed")
require(int(rule.get("maximumPassLossesAcrossAllViewsForWinningFamily", -1)) == MAX_TOTAL_LOSSES, "V143 maximum-loss rule changed")

require(freeze.get("experiment") == "V143-final-multifamily-frozen-selector", "Unexpected V143 freeze artifact")
require(freeze.get("frozenBeforeHeldoutEvaluation") is True, "V143 selector was not frozen before held-out")
require(freeze.get("finalRhythmSustainSweep") is True and freeze.get("stopAfterV143") is True, "V143 freeze is not final")

require(heldout.get("experiment") == "V143-frozen-final-multifamily-heldout-evaluation", "Unexpected V143 held-out artifact")
require(int((heldout.get("baseline") or {}).get("passes", -1)) == 311, "V143 held-out baseline is not 311/320")
require(int((heldout.get("v143") or {}).get("passes", -1)) == 312, "V143 held-out result is not 312/320")
require(int((heldout.get("v143") or {}).get("gains", -1)) == 1, "V143 held-out did not record +1 gain")
require(int((heldout.get("v143") or {}).get("losses", -1)) == 0, "V143 held-out did not record zero losses")
require((heldout.get("v143") or {}).get("promotionCandidate") is True, "V143 held-out is not a promotion candidate")
require(heldout.get("reserve11mod16Inspected") is False, "11-mod-16 reserve was already inspected before blind confirmation")
require(heldout.get("blind11mod16ConfirmationAllowed") is True, "V143 held-out does not authorize blind confirmation")
require(heldout.get("productionPromotionAllowed") is False, "V143 was promoted before blind confirmation")
require(heldout.get("noV144RhythmSustainSweepAllowed") is True, "V143 held-out improperly allows V144")

candidate_path = v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
candidate_before = sha256(candidate_path)

# Prove the fresh 11-mod-16 family is disjoint from every previously consumed reserve.
consumed: set[float] = set()
for path in (v134.V116_PATH, v134.V119_PATH, v134.V124_PATH, v134.V128_PATH, v134.OUTPUT_PATH):
    record = json.loads(path.read_text(encoding="utf-8"))
    consumed |= {round(float(p), 12) for p in (record.get("reservedPhases") or [])}
new_phases = {round(float(p), 12) for p in RESERVED_PHASES}
require(not (consumed & new_phases), "11-mod-16 reserve overlaps a previously consumed reserve")

# Load the frozen V122/V127/V134 structural policy, without reading any V143 held-out row outcomes.
v124_result = json.loads(v134.V124_PATH.read_text(encoding="utf-8"))
require(int(v124_result.get("schemaVersion", -1)) == 124 and bool(v124_result.get("validatedNewChampion")), "Validated V124 structural policy required")
policy: dict[tuple[str, str, int, float], str] = {}
for row in v124_result.get("frozenStructuralPolicy") or []:
    key = (
        str(row.get("originalQBucket")),
        str(row.get("v96Decision")),
        int(row.get("pairRadius")),
        float(row.get("lambda")),
    )
    rep = str(row.get("representation"))
    require(rep in v124.REPRESENTATIONS, f"Unexpected frozen structural representation: {rep}")
    policy[key] = rep
require(len(policy) == 7, f"Expected seven frozen V122 structural groups, got {len(policy)}")
require(policy.get(v134.V127_GUARD_KEY) == v134.V127_GUARD_REP, "Frozen V127 guard target mismatch")
require(policy.get(v134.V134_TARGET_KEY) == "cosine", "V134 target must begin from frozen cosine representation")

payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
rows = list(payload.get("candidateSlots") or [])
require(bool(rows), "candidateSlots missing")
require(tuple(payload.get("frozenChampionMatchedMissingExtra") or []) == v124.EXPECTED, "candidateSlots not anchored to frozen champion")

names = sorted((rows[0].get("features") or {}).keys())
name_to_idx = {name: i for i, name in enumerate(names)}
xb = np.asarray([[float((row.get("features") or {}).get(name, 0.0)) for name in names] for row in rows], dtype=np.float64)
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
require(bands == ["low", "lowMid", "mid", "highMid", "high"], f"Unexpected V143 bands: {bands}")
require(stages == ["Burst", "Rise", "Decay30", "Decay60", "PostSlope"], f"Unexpected V143 stages: {stages}")

source: dict[str, dict[str, np.ndarray]] = {}
for band in bands:
    source[band] = {}
    for stage in stages:
        source_name = f"mean::{band}{stage}"
        require(source_name in name_to_idx, f"Missing V143 source column: {source_name}")
        source[band][stage] = xb[:, name_to_idx[source_name]]

family_features: dict[str, np.ndarray] = {}

cols: list[np.ndarray] = []
for band in bands:
    seq = [source[band][stage] for stage in stages]
    for left, right in zip(seq[:-1], seq[1:]):
        cols.append((right - left) / (np.abs(right) + np.abs(left) + EPS))
family_features["normalized_temporal_contrast"] = np.column_stack(cols)

cols = []
for stage in stages:
    for left_band, right_band in zip(bands[:-1], bands[1:]):
        cols.append(source[right_band][stage] - source[left_band][stage])
family_features["adjacent_band_balance"] = np.column_stack(cols)

cols = []
band_axis = np.asarray([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float64)
for stage in stages:
    stage_values = np.column_stack([source[band][stage] for band in bands])
    energy = np.abs(stage_values) + EPS
    denom = np.sum(energy, axis=1)
    centroid = np.sum(energy * band_axis[None, :], axis=1) / denom
    spread = np.sum(energy * np.square(band_axis[None, :] - centroid[:, None]), axis=1) / denom
    cols.extend([centroid, spread])
family_features["spectral_shape"] = np.column_stack(cols)

cols = []
for band in bands:
    attack = 0.5 * (source[band]["Burst"] + source[band]["Rise"])
    sustain = (source[band]["Decay30"] + source[band]["Decay60"] + source[band]["PostSlope"]) / 3.0
    contrast = (sustain - attack) / (np.abs(sustain) + np.abs(attack) + EPS)
    cols.extend([attack, sustain, contrast])
family_features["attack_sustain_summary"] = np.column_stack(cols)

cols = []
for band in bands:
    temporal = np.column_stack([source[band][stage] for stage in stages])
    temporal_range = np.max(temporal, axis=1) - np.min(temporal, axis=1)
    temporal_std = np.std(temporal, axis=1)
    burst = source[band]["Burst"]
    post = source[band]["PostSlope"]
    endpoint = (post - burst) / (np.abs(post) + np.abs(burst) + EPS)
    cols.extend([temporal_range, temporal_std, endpoint])
family_features["temporal_extrema"] = np.column_stack(cols)

require({name: matrix.shape[1] for name, matrix in family_features.items()} == EXPECTED_FAMILIES, "Constructed V143 family menu changed")
require(all(np.isfinite(matrix).all() for matrix in family_features.values()), "Non-finite V143 family features")

# Compute the frozen V115 gate ranking for the entire fresh family before any outer fold is scored.
gate_fit = v124.fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)
fold_specs: list[dict] = []
for phase in RESERVED_PHASES:
    ids = np.asarray([v124.v18.phased_fold(int(m), lo, hi, v124.OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
    for fold in range(v124.OUTER_FOLDS):
        train = ids != fold
        gx = np.asarray([v124.gate_features_for_mask(xb, names, pf, train)], dtype=np.float64)
        gate_score = float(v124.v110.predict(gx, gate_fit)[0])
        fold_specs.append({"phase": float(phase), "fold": int(fold), "ids": ids, "gateScore": gate_score})

require(len(fold_specs) == EXPECTED_TOTAL, f"Expected {EXPECTED_TOTAL} blind carriers, found {len(fold_specs)}")
select_k = int(math.ceil(len(fold_specs) * v124.GATE_NUM / v124.GATE_DEN))
order = np.argsort(-np.asarray([row["gateScore"] for row in fold_specs], dtype=np.float64))
selected_indices = set(int(i) for i in order[:select_k])
for i, row in enumerate(fold_specs):
    row["selectedForV112"] = i in selected_indices


def build_v134_training_metadata(spec_row: dict) -> dict:
    phase = float(spec_row["phase"])
    fold = int(spec_row["fold"])
    ids = spec_row["ids"]
    train = ids != fold

    x_full = matrices["full_phase"]
    chosen_model = v124.v5.choose_model(x_full[train], y[train], measures[train])
    radius = int(chosen_model["pairRadius"])
    lam = float(chosen_model["lambda"])
    old_q, selector = v124.v56.choose_q_train_only(x_full[train], y[train], measures[train], radius, lam)
    bucket = v124.q_bucket(old_q)
    candidate_q, decision, dispersion = v124.v80.selected_q({"outerQ": float(old_q), "selector": selector})

    use_tight = bucket == "tight"
    use_safe_broad = bucket == "broad" and decision == "keep-broad-low-dispersion"
    excluded_safe_broad = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
    use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

    if use_v96:
        v115_rep = "v112_interactions" if bool(spec_row["selectedForV112"]) else "cosine"
    else:
        v115_rep = "full_phase"

    dangerous = bool(
        bool(spec_row["selectedForV112"])
        and use_v96
        and v124.is_v118_dangerous_signature(bucket, decision, radius, lam)
    )
    v118_rep = "cosine" if dangerous else v115_rep

    key = v124.structural_key(bucket, decision, radius, lam)
    structural_rep = policy.get(key)
    v122_rep = structural_rep if structural_rep is not None else v118_rep
    v127_guard_applied = bool(key == v134.V127_GUARD_KEY and structural_rep == v134.V127_GUARD_REP and bool(spec_row["selectedForV112"]))
    v128_rep = v118_rep if v127_guard_applied else v122_rep

    v134_selective = v134.v134_selector(spec_row, key)
    final_rep = v134.V134_TARGET_REP if v134_selective else v128_rep

    q_to_use = float(candidate_q) if bucket == "tight" else float(v124.ANCHOR_Q)
    if bucket == "broad" and decision == "keep-broad-low-dispersion":
        q_to_use = float(candidate_q)

    return {
        "phase": phase,
        "fold": fold,
        "ids": ids,
        "gateScore": float(spec_row["gateScore"]),
        "selectedForV112": bool(spec_row["selectedForV112"]),
        "chosenModel": chosen_model,
        "radius": radius,
        "lambda": lam,
        "originalTrainingOnlyQ": float(old_q),
        "originalQBucket": bucket,
        "selector": selector,
        "v96Decision": str(decision),
        "dispersion": None if dispersion is None else float(dispersion),
        "structuralRepresentation": structural_rep,
        "v127GuardApplied": v127_guard_applied,
        "v134SelectiveInterventionApplied": v134_selective,
        "finalRepresentation": str(final_rep),
        "qToUse": q_to_use,
    }


def score_mask(meta: dict, matrix: np.ndarray, train_mask: np.ndarray, test_mask: np.ndarray) -> dict:
    model = v124.v2.fit_pairwise_ranker(
        matrix[train_mask],
        y[train_mask],
        measures[train_mask],
        int(meta["radius"]),
        float(meta["lambda"]),
    )
    scores = v124.v2.scores_for(matrix[test_mask], model)
    passed, lift, _held, _stats = v124.v17.pass_at_q(scores, y[test_mask], float(meta["qToUse"]))
    return {"pass": bool(passed), "lift": round(float(lift), 6)}


def evaluate_family_views(meta: dict, base_matrix: np.ndarray, challenger_matrix: np.ndarray, outer_train: np.ndarray) -> dict:
    views: list[dict] = []
    phase = float(meta["phase"])
    for phase_offset in EXPECTED_PHASE_OFFSETS:
        inner_phase = (phase + phase_offset) % 1.0
        inner_ids = np.asarray(
            [v124.v18.phased_fold(int(measure), lo, hi, INNER_FOLDS, inner_phase) for measure in measures],
            dtype=np.int16,
        )
        inner_rows: list[dict] = []
        for inner_fold in range(INNER_FOLDS):
            train_mask = outer_train & (inner_ids != inner_fold)
            val_mask = outer_train & (inner_ids == inner_fold)
            train_count = int(np.sum(train_mask))
            val_count = int(np.sum(val_mask))
            if train_count < 20 or val_count < 5:
                continue
            if not np.any(y[val_mask]) or not np.any(~y[val_mask]):
                continue
            base = score_mask(meta, base_matrix, train_mask, val_mask)
            challenger = score_mask(meta, challenger_matrix, train_mask, val_mask)
            inner_rows.append({
                "innerFold": inner_fold,
                "trainCount": train_count,
                "validationCount": val_count,
                "v134Pass": base["pass"],
                "v143Pass": challenger["pass"],
                "v134Lift": base["lift"],
                "v143Lift": challenger["lift"],
                "liftDelta": round(challenger["lift"] - base["lift"], 6),
            })

        gains = sum(int(row["v143Pass"] and not row["v134Pass"]) for row in inner_rows)
        losses = sum(int(row["v134Pass"] and not row["v143Pass"]) for row in inner_rows)
        deltas = [float(row["liftDelta"]) for row in inner_rows]
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
        views.append({
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
        })

    total_losses = sum(int(view["innerLosses"]) for view in views)
    total_gains = sum(int(view["innerGains"]) for view in views)
    minimum_mean = min(float(view["meanInnerLiftDelta"]) for view in views)
    minimum_median = min(float(view["medianInnerLiftDelta"]) for view in views)
    sum_mean = sum(float(view["meanInnerLiftDelta"]) for view in views)
    qualified = bool(all(bool(view["viewRulePassed"]) for view in views) and total_losses <= MAX_TOTAL_LOSSES)
    return {
        "qualified": qualified,
        "replicatedViews": views,
        "totalInnerGainsAcrossViews": total_gains,
        "totalInnerLossesAcrossViews": total_losses,
        "minimumMeanLiftDeltaAcrossViews": round(minimum_mean, 6),
        "minimumMedianLiftDeltaAcrossViews": round(minimum_median, 6),
        "sumMeanLiftDeltaAcrossViews": round(sum_mean, 6),
    }


def training_only_v143_choice(meta: dict) -> dict:
    outer_ids = meta["ids"]
    outer_train = outer_ids != int(meta["fold"])
    rep = str(meta["finalRepresentation"])
    require(rep in matrices, f"Unknown V134 final representation: {rep}")
    base_matrix = matrices[rep]

    summaries: list[dict] = []
    for family in sorted(family_features):
        challenger_matrix = np.concatenate([base_matrix, family_features[family]], axis=1)
        result = evaluate_family_views(meta, base_matrix, challenger_matrix, outer_train)
        result["family"] = family
        summaries.append(result)

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
    return {
        "selected": winner is not None,
        "selectedFamily": str(winner["family"]) if winner else None,
        "qualifiedFamilyCount": len(qualified),
        "selectedFamilyScore": {
            "minimumMeanLiftDeltaAcrossViews": winner["minimumMeanLiftDeltaAcrossViews"],
            "totalInnerGainsAcrossViews": winner["totalInnerGainsAcrossViews"],
            "minimumMedianLiftDeltaAcrossViews": winner["minimumMedianLiftDeltaAcrossViews"],
            "sumMeanLiftDeltaAcrossViews": winner["sumMeanLiftDeltaAcrossViews"],
        } if winner else None,
        "familyResults": summaries,
    }


print("=== V143 ONE-SHOT BLIND 11-MOD-16 CONFIRMATION ===")
print("Protocol frozen before reserve inspection: True")
print("Fresh reserve: numerators 11 mod 16 over 1024 = 64 phases / 320 folds")
print("Previously consumed reserve overlap: 0")
print("V143 selector transported using outer-training rows only: True")
print("V143 prior held-out outcomes used for reserve selection: False")
print("Professional/midterm answers used: False")
print("New Q/lambda/pair-radius tuning: False")
print("V112 selected before blind outer scoring:", select_k, "/", EXPECTED_TOTAL)
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print("NO V144 RHYTHM/SUSTAIN SWEEP: True")
print()

results: list[dict] = []
by_phase: dict[float, dict] = {
    float(phase): {"phase": float(phase), "v134Passes": 0, "v143Passes": 0, "folds": []}
    for phase in RESERVED_PHASES
}
selected_count = 0
selected_by_family: Counter[str] = Counter()
selected_by_rep: Counter[str] = Counter()
gains = 0
losses = 0
changed: list[dict] = []

for index, spec_row in enumerate(fold_specs, 1):
    meta = build_v134_training_metadata(spec_row)
    rep = str(meta["finalRepresentation"])
    base_matrix = matrices[rep]
    outer_ids = meta["ids"]
    outer_train = outer_ids != int(meta["fold"])
    outer_test = outer_ids == int(meta["fold"])

    # Freeze this unseen carrier's V143 family choice from outer-training rows only.
    choice = training_only_v143_choice(meta)

    # Only after the choice is frozen do we score the untouched outer fold.
    base_result = score_mask(meta, base_matrix, outer_train, outer_test)
    family = choice["selectedFamily"]
    if choice["selected"]:
        selected_count += 1
        selected_by_family[str(family)] += 1
        selected_by_rep[rep] += 1
        candidate_matrix = np.concatenate([base_matrix, family_features[str(family)]], axis=1)
        candidate_result = score_mask(meta, candidate_matrix, outer_train, outer_test)
    else:
        candidate_result = dict(base_result)

    if candidate_result["pass"] and not base_result["pass"]:
        gains += 1
        changed.append({
            "change": "GAIN",
            "phase": float(meta["phase"]),
            "fold": int(meta["fold"]),
            "baseLift": base_result["lift"],
            "v143Lift": candidate_result["lift"],
            "representation": rep,
            "selectedFamily": family,
        })
    elif base_result["pass"] and not candidate_result["pass"]:
        losses += 1
        changed.append({
            "change": "LOSS",
            "phase": float(meta["phase"]),
            "fold": int(meta["fold"]),
            "baseLift": base_result["lift"],
            "v143Lift": candidate_result["lift"],
            "representation": rep,
            "selectedFamily": family,
        })

    fold_record = {
        "phase": float(meta["phase"]),
        "fold": int(meta["fold"]),
        "gateScore": float(meta["gateScore"]),
        "selectedForV112": bool(meta["selectedForV112"]),
        "chosenModel": meta["chosenModel"],
        "originalTrainingOnlyQ": float(meta["originalTrainingOnlyQ"]),
        "originalQBucket": meta["originalQBucket"],
        "v96Decision": meta["v96Decision"],
        "structuralRepresentation": meta["structuralRepresentation"],
        "v127GuardApplied": bool(meta["v127GuardApplied"]),
        "v134SelectiveInterventionApplied": bool(meta["v134SelectiveInterventionApplied"]),
        "v134Representation": rep,
        "v143Selected": bool(choice["selected"]),
        "v143SelectedFamily": family,
        "v143QualifiedFamilyCount": int(choice["qualifiedFamilyCount"]),
        "v143SelectedFamilyScore": choice["selectedFamilyScore"],
        "v143FamilyResults": choice["familyResults"],
        "v134Pass": bool(base_result["pass"]),
        "v143Pass": bool(candidate_result["pass"]),
        "v134Lift": base_result["lift"],
        "v143Lift": candidate_result["lift"],
    }
    results.append(fold_record)
    phase_record = by_phase[float(meta["phase"])]
    phase_record["v134Passes"] += int(base_result["pass"])
    phase_record["v143Passes"] += int(candidate_result["pass"])
    phase_record["folds"].append(fold_record)

    if index % 20 == 0:
        print(f"blind heartbeat {index}/{EXPECTED_TOTAL}", flush=True)

v134_passes = sum(int(row["v134Pass"]) for row in results)
v143_passes = sum(int(row["v143Pass"]) for row in results)
phase_records = [by_phase[float(phase)] for phase in RESERVED_PHASES]
minimum_v134_phase = min(int(row["v134Passes"]) for row in phase_records)
minimum_v143_phase = min(int(row["v143Passes"]) for row in phase_records)

confirmation_success = bool(
    v143_passes > v134_passes
    and gains >= 1
    and losses == 0
    and minimum_v143_phase >= 3
)

candidate_after = sha256(candidate_path)
require(candidate_before == candidate_after, "Protected 949-event candidate changed during blind confirmation")

out = {
    "schemaVersion": 14311,
    "experiment": "V143-final-multifamily-blind-11mod16-confirmation",
    "protocolPath": str(BLIND_SPEC_PATH.relative_to(ROOT)),
    "protocolSha256": sha256(BLIND_SPEC_PATH),
    "v143SpecSha256": sha256(V143_SPEC_PATH),
    "v143FrozenSelectorSha256": sha256(V143_FREEZE_PATH),
    "v143HeldoutEvaluationSha256": sha256(V143_HELDOUT_PATH),
    "reservedPhaseFamily": "numerators-11-mod-16-over-1024",
    "reservedPhases": list(RESERVED_PHASES),
    "foldsTotal": EXPECTED_TOTAL,
    "previouslyConsumedReserveOverlap": 0,
    "selectedForV112BeforeBlindOuterScoring": int(select_k),
    "v143SelectorTransportedFromFrozenTrainingOnlyRule": True,
    "v143PriorHeldoutOutcomeUsedForReserveSelection": False,
    "professionalMidtermAnswersUsed": False,
    "newQHyperparameterTuningPerformed": False,
    "newLambdaHyperparameterTuningPerformed": False,
    "newPairRadiusTuningPerformed": False,
    "v134Passes": v134_passes,
    "v143Passes": v143_passes,
    "gainsVsV134": gains,
    "lossesVsV134": losses,
    "netVsV134": gains - losses,
    "v143SelectedCarriers": selected_count,
    "v143SelectedByFamily": dict(selected_by_family),
    "v143SelectedByRepresentation": dict(selected_by_rep),
    "minimumV134PhasePasses": minimum_v134_phase,
    "minimumV143PhasePasses": minimum_v143_phase,
    "changedCarriers": changed,
    "confirmationSuccess": confirmation_success,
    "validatedNewChampion": confirmation_success,
    "championAfterBlindConfirmation": "V143" if confirmation_success else "V134",
    "pipelineIntegrationChampion": "V143" if confirmation_success else "V134",
    "productionPromotionAllowed": confirmation_success,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchanged": True,
    "reserve11mod16Consumed": True,
    "oneShotReserveEvaluation": True,
    "finalRhythmSustainSweep": True,
    "stopAfterV143": True,
    "noV144RhythmSustainSweepAllowed": True,
    "rhythmSustainResearchClosed": True,
    "phases": phase_records,
}

OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print()
print("=== V143 BLIND 11-MOD-16 CONFIRMATION COMPLETE ===")
print(f"V134 blind baseline: {v134_passes}/{EXPECTED_TOTAL} = {100.0 * v134_passes / EXPECTED_TOTAL:.4f}%")
print(f"V143 blind challenger: {v143_passes}/{EXPECTED_TOTAL} = {100.0 * v143_passes / EXPECTED_TOTAL:.4f}%")
print(f"Gains/losses vs V134: +{gains}/-{losses} net={gains - losses:+d}")
print("Training-only V143 selections on blind carriers:", selected_count, "/", EXPECTED_TOTAL)
print("Selected by family:", dict(selected_by_family))
print("Selected by representation:", dict(selected_by_rep))
print("Minimum V134 phase passes:", minimum_v134_phase, "/5")
print("Minimum V143 phase passes:", minimum_v143_phase, "/5")
print("Confirmation success:", confirmation_success)
print("Validated new champion:", confirmation_success)
print("Champion after blind confirmation:", out["championAfterBlindConfirmation"])
print("Pipeline integration champion:", out["pipelineIntegrationChampion"])
print("Professional/midterm answers used: False")
print("V143 prior held-out outcome used for reserve selection: False")
print("Protected 949-event candidate hash unchanged: True")
print("Reserve 11-mod-16 consumed: True")
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print("NO V144 RHYTHM/SUSTAIN SWEEP: True")
print("RHYTHM/SUSTAIN RESEARCH CLOSED: True")
print()
print("Changed carriers:")
if changed:
    for item in changed:
        print(
            f"{item['change']:4s} phase={item['phase']:.12f} fold={item['fold']} "
            f"baseLift={item['baseLift']:.2f} v143Lift={item['v143Lift']:.2f} "
            f"rep={item['representation']} family={item['selectedFamily']}"
        )
else:
    print("none")
print()
print("Saved:", OUT_PATH)
