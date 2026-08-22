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
DEV_DIR = PUBLIC / "training" / "v143-final-multifamily-development"
SPEC_PATH = DEV_DIR / "v143-final-multifamily-spec.json"
SELECTOR_PATH = DEV_DIR / "v143-training-only-selector.json"
FREEZE_PATH = DEV_DIR / "v143-frozen-selector.json"
OUT_PATH = DEV_DIR / "v143-heldout-evaluation.json"

EXPECTED_BASE_PASSES = 311
EXPECTED_TOTAL = 320
EXPECTED_SELECTED = 18
EXPECTED_BY_FAMILY = {
    "attack_sustain_summary": 3,
    "normalized_temporal_contrast": 4,
    "spectral_shape": 10,
    "temporal_extrema": 1,
}
EXPECTED_BY_REP = {
    "base": 4,
    "cosine": 6,
    "full_phase": 5,
    "phase_col3": 1,
    "v112_interactions": 2,
}
EXPECTED_FAMILY_COUNTS = {
    "normalized_temporal_contrast": 20,
    "adjacent_band_balance": 20,
    "spectral_shape": 10,
    "attack_sustain_summary": 15,
    "temporal_extrema": 15,
}
EXPECTED_PHASE_OFFSETS = [0.0, 0.125]
EPS = 1e-9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


if OUT_PATH.exists():
    raise RuntimeError(
        f"V143 held-out evaluation already exists at {OUT_PATH}; "
        "refusing to score the held-out folds again."
    )

candidate_path = v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
candidate_before = sha256(candidate_path)

require(SPEC_PATH.is_file(), f"Missing frozen V143 spec: {SPEC_PATH}")
require(SELECTOR_PATH.is_file(), f"Missing V143 training-only selector: {SELECTOR_PATH}")
require(FREEZE_PATH.is_file(), f"Missing frozen V143 selector: {FREEZE_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
selector = json.loads(SELECTOR_PATH.read_text(encoding="utf-8"))
freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

require(int(spec.get("schemaVersion", -1)) == 143, "V143 spec schema mismatch")
require(spec.get("frozenBeforeDevelopmentRun") is True, "V143 family menu was not frozen before development")
require(spec.get("finalSweep") is True, "V143 spec is not marked final")
require(spec.get("stopAfterV143") is True, "V143 spec does not require stopping after V143")
require(int(spec.get("totalMenuFeatureCount", -1)) == 80, "V143 feature-menu count changed")

families_meta = dict(spec.get("families") or {})
actual_family_counts = {name: int(meta.get("featureCount", -1)) for name, meta in families_meta.items()}
require(actual_family_counts == EXPECTED_FAMILY_COUNTS, f"V143 family menu changed: {actual_family_counts}")

rule = dict(spec.get("selectionRule") or {})
phase_offsets = [float(x) for x in (rule.get("validationPhaseOffsets") or [])]
require(phase_offsets == EXPECTED_PHASE_OFFSETS, f"V143 validation offsets changed: {phase_offsets}")
require(int(rule.get("maximumPassLossesAcrossAllViewsForWinningFamily", -1)) == 0, "V143 zero-loss rule changed")

for key in (
    "qTuningAllowed",
    "lambdaTuningAllowed",
    "pairRadiusTuningAllowed",
    "heldoutV134ScoringAllowedDuringDevelopment",
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
    require(spec.get(key) is False, f"V143 frozen safety spec violation: {key}={spec.get(key)}")

require(selector.get("experiment") == "V143-final-multifamily-training-only-sweep", "Unexpected V143 training selector")
require(selector.get("heldoutV134FoldScored") is False, "V143 development already scored V134 held-out folds")
require(selector.get("heldoutOutcomeFieldsUsedForSelection") is False, "V143 development used held-out outcome fields")
require(selector.get("professionalMidtermAnswersUsed") is False, "V143 development used professional answers")
require(selector.get("reserve11mod16Inspected") is False, "V143 development inspected reserve")
require(selector.get("protected949CandidateHashUnchanged") is True, "Protected candidate changed during V143 development")
require(selector.get("finalRhythmSustainSweep") is True, "V143 selector is not marked final")
require(selector.get("stopAfterV143") is True, "V143 selector does not enforce stop after V143")

require(freeze.get("experiment") == "V143-final-multifamily-frozen-selector", "Unexpected V143 frozen selector")
require(freeze.get("frozenBeforeHeldoutEvaluation") is True, "V143 selector was not frozen before held-out evaluation")
require(freeze.get("oneShotHeldoutEvaluationAllowed") is True, "V143 frozen selector does not allow the one-shot evaluation")
require(freeze.get("productionPromotionAllowed") is False, "V143 frozen selector improperly allows production promotion")
require(freeze.get("priorHeldoutEvaluationRowsUsedToFreeze") is False, "V143 freeze used prior held-out evaluation rows")
require(freeze.get("professionalMidtermAnswersUsedToFreeze") is False, "V143 freeze used professional answers")
require(freeze.get("reserve11mod16InspectedBeforeFreeze") is False, "V143 freeze inspected reserve")
require(freeze.get("candidateEventsModified") is False, "V143 freeze modified candidate events")
require(freeze.get("protected949CandidateHashUnchangedDuringDevelopment") is True, "Protected candidate changed before V143 freeze")
require(freeze.get("finalRhythmSustainSweep") is True, "V143 freeze is not marked final")
require(freeze.get("stopAfterV143") is True, "V143 freeze does not enforce stop after V143")

source_selector = dict(freeze.get("sourceTrainingOnlySelector") or {})
require(source_selector.get("sha256") == sha256(SELECTOR_PATH), "Frozen V143 selector/training selector SHA mismatch")
frozen_spec = dict(freeze.get("frozenMultiFamilySpec") or {})
require(frozen_spec.get("sha256") == sha256(SPEC_PATH), "Frozen V143 selector/spec SHA mismatch")
require(dict(frozen_spec.get("familyFeatureCounts") or {}) == EXPECTED_FAMILY_COUNTS, "Frozen V143 family counts changed")
require(int(frozen_spec.get("totalMenuFeatureCount", -1)) == 80, "Frozen V143 total feature count changed")

freeze_summary = dict(freeze.get("selector") or {})
require(int(freeze_summary.get("selectedCarriers", -1)) == EXPECTED_SELECTED, "Frozen V143 selected-carrier count changed")
require(dict(freeze_summary.get("selectedByFamily") or {}) == EXPECTED_BY_FAMILY, "Frozen V143 family split changed")
require(dict(freeze_summary.get("selectedByRepresentation") or {}) == EXPECTED_BY_REP, "Frozen V143 representation split changed")
require([float(x) for x in (freeze_summary.get("validationPhaseOffsets") or [])] == EXPECTED_PHASE_OFFSETS, "Frozen V143 phase offsets changed")

selected_rows = list(freeze.get("selections") or [])
require(len(selected_rows) == EXPECTED_SELECTED, f"Expected {EXPECTED_SELECTED} frozen selections, found {len(selected_rows)}")
selected_keys = {(round(float(item["phase"]), 12), int(item["fold"])) for item in selected_rows}
require(len(selected_keys) == EXPECTED_SELECTED, "Frozen V143 selections are not unique")

selected_by_key = {
    (round(float(item["phase"]), 12), int(item["fold"])): item
    for item in selected_rows
}

actual_by_family = Counter(str(item.get("selectedFamily") or "") for item in selected_rows)
actual_by_rep = Counter(str(item.get("v134Representation") or "") for item in selected_rows)
require(dict(actual_by_family) == EXPECTED_BY_FAMILY, f"Frozen V143 family recount changed: {dict(actual_by_family)}")
require(dict(actual_by_rep) == EXPECTED_BY_REP, f"Frozen V143 representation recount changed: {dict(actual_by_rep)}")

for item in selected_rows:
    family = str(item.get("selectedFamily") or "")
    require(family in EXPECTED_FAMILY_COUNTS, f"Unknown frozen V143 family: {family}")
    family_results = {str(result.get("family")): result for result in (item.get("familyResults") or [])}
    require(set(family_results) == set(EXPECTED_FAMILY_COUNTS), "Frozen V143 selection family-result set changed")
    winner = family_results[family]
    require(winner.get("qualified") is True, "Frozen V143 selected family is no longer qualified")
    require(int(winner.get("totalInnerLossesAcrossViews", -1)) == 0, "Frozen V143 selected family contains an inner-CV loss")
    views = list(winner.get("replicatedViews") or [])
    require(len(views) == 2, "Frozen V143 selected family lacks both replicated views")
    require([float(view.get("phaseOffset")) for view in views] == EXPECTED_PHASE_OFFSETS, "Frozen V143 selected family phase offsets changed")
    for view in views:
        require(view.get("viewRulePassed") is True, "Frozen V143 selected family has a failed replicated view")
        require(int(view.get("innerGains", 0)) >= 1, "Frozen V143 selected family lacks a replicated gain")
        require(int(view.get("innerLosses", -1)) == 0, "Frozen V143 selected family has a replicated loss")
        require(float(view.get("meanInnerLiftDelta", 0.0)) > 0.0, "Frozen V143 selected family lacks positive mean lift")
        require(float(view.get("medianInnerLiftDelta", -1.0)) >= 0.0, "Frozen V143 selected family has negative median lift")

payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
rows = list(payload.get("candidateSlots") or [])
require(bool(rows), "candidateSlots missing")
require(tuple(payload.get("frozenChampionMatchedMissingExtra") or []) == v124.EXPECTED, "candidateSlots not anchored to frozen champion")

artifact = json.loads(v134.OUTPUT_PATH.read_text(encoding="utf-8"))
require(int(artifact.get("v134Passes", -1)) == EXPECTED_BASE_PASSES, f"V134 artifact is not authoritative 311/320: {artifact.get('v134Passes')}/{artifact.get('foldsTotal')}")
require(int(artifact.get("foldsTotal", -1)) == EXPECTED_TOTAL, "V134 artifact does not contain 320 carriers")

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
require(bands == ["low", "lowMid", "mid", "highMid", "high"], f"Unexpected V143 bands: {bands}")
require(stages == ["Burst", "Rise", "Decay30", "Decay60", "PostSlope"], f"Unexpected V143 stages: {stages}")

source: dict[str, dict[str, np.ndarray]] = {}
for band in bands:
    source[band] = {}
    for stage in stages:
        source_name = f"mean::{band}{stage}"
        require(source_name in name_to_idx, f"Missing frozen V143 source column: {source_name}")
        source[band][stage] = xb[:, name_to_idx[source_name]]

family_features: dict[str, np.ndarray] = {}

# 1) Stabilized normalized temporal contrasts: 20.
cols: list[np.ndarray] = []
for band in bands:
    seq = [source[band][stage] for stage in stages]
    for left, right in zip(seq[:-1], seq[1:]):
        cols.append((right - left) / (np.abs(right) + np.abs(left) + EPS))
family_features["normalized_temporal_contrast"] = np.column_stack(cols)

# 2) Adjacent-band balance: 20.
cols = []
for stage in stages:
    for left_band, right_band in zip(bands[:-1], bands[1:]):
        cols.append(source[right_band][stage] - source[left_band][stage])
family_features["adjacent_band_balance"] = np.column_stack(cols)

# 3) Spectral centroid/spread: 10.
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

# 4) Attack/sustain summary: 15.
cols = []
for band in bands:
    attack = 0.5 * (source[band]["Burst"] + source[band]["Rise"])
    sustain = (source[band]["Decay30"] + source[band]["Decay60"] + source[band]["PostSlope"]) / 3.0
    contrast = (sustain - attack) / (np.abs(sustain) + np.abs(attack) + EPS)
    cols.extend([attack, sustain, contrast])
family_features["attack_sustain_summary"] = np.column_stack(cols)

# 5) Temporal extrema: 15.
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

require(set(family_features) == set(EXPECTED_FAMILY_COUNTS), "V143 evaluator family set changed")
for family, matrix in family_features.items():
    require(matrix.shape[1] == EXPECTED_FAMILY_COUNTS[family], f"V143 {family} feature count changed: {matrix.shape[1]}")
    require(np.isfinite(matrix).all(), f"Non-finite V143 feature values in {family}")
require(sum(matrix.shape[1] for matrix in family_features.values()) == 80, "V143 evaluator menu no longer totals 80 features")

carriers = []
for scheme in artifact.get("schemes") or []:
    carriers.extend(scheme.get("folds") or [])
require(len(carriers) == EXPECTED_TOTAL, f"Expected 320 V134 carriers, found {len(carriers)}")


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

    dangerous = bool(selected and use_v96 and v124.is_v118_dangerous_signature(bucket, decision, radius, lam))
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
    selector_payload = row["selector"]
    candidate_q, decision, _dispersion = v124.v80.selected_q({"outerQ": old_q, "selector": selector_payload})
    recorded_decision = str(row["v96Decision"])
    require(str(decision) == recorded_decision, f"Q decision mismatch: {decision} != {recorded_decision}")

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


def evaluate_one(row: dict, matrix: np.ndarray) -> dict:
    phase = float(row["phase"])
    fold = int(row["fold"])
    ids = np.asarray(
        [v124.v18.phased_fold(int(measure), lo, hi, v124.OUTER_FOLDS, phase) for measure in measures],
        dtype=np.int16,
    )
    train = ids != fold
    test = ids == fold

    chosen = row["chosenModel"]
    radius = int(chosen["pairRadius"])
    lam = float(chosen["lambda"])
    q = q_for(row)
    model = v124.v2.fit_pairwise_ranker(matrix[train], y[train], measures[train], radius, lam)
    scores = v124.v2.scores_for(matrix[test], model)
    passed, lift, _held, _stats = v124.v17.pass_at_q(scores, y[test], q)
    return {
        "phase": phase,
        "fold": fold,
        "representation": actual_rep(row),
        "pass": bool(passed),
        "lift": round(float(lift), 2),
    }


print("=== V143 FROZEN FINAL MULTI-FAMILY HELD-OUT EVALUATION ===")
print("Selector frozen before held-out scoring: True")
print("Frozen selected carriers:", len(selected_keys))
print("Frozen selected by family:", dict(actual_by_family))
print("Frozen selected by representation:", dict(actual_by_rep))
print("V136D evaluation rows read: False")
print("V137 held-out evaluation rows read: False")
print("V138 held-out evaluation rows read: False")
print("V139 held-out evaluation rows read: False")
print("V140 held-out evaluation rows read: False")
print("V141 held-out evaluation rows read: False")
print("V142 held-out evaluation rows read: False")
print("Professional/midterm answers read: False")
print("11-mod-16 reserve inspected: False")
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print()

print("=== V134 BASELINE REPRODUCTION GUARD ===", flush=True)
base_results = []
mismatches = []
carrier_lookup = {}

for index, row in enumerate(carriers, 1):
    rep = actual_rep(row)
    require(rep in matrices, f"Unknown V134 representation: {rep}")
    key = (round(float(row["phase"]), 12), int(row["fold"]))
    carrier_lookup[key] = row
    result = evaluate_one(row, matrices[rep])
    base_results.append(result)

    artifact_pass = bool(row["v134Passed"])
    if result["pass"] != artifact_pass:
        mismatches.append({
            "phase": result["phase"],
            "fold": result["fold"],
            "artifactPass": artifact_pass,
            "reproducedPass": result["pass"],
            "artifactLift": row.get("heldoutPrecisionLift"),
            "reproducedLift": result["lift"],
            "representation": rep,
        })
    if index % 40 == 0:
        print(f"baseline heartbeat {index}/320", flush=True)

base_passes = sum(int(item["pass"]) for item in base_results)
print(f"V134 reproduced baseline: {base_passes}/320")
print("Historical-artifact pass mismatches:", len(mismatches))
require(base_passes == EXPECTED_BASE_PASSES and not mismatches, f"V134 BASELINE GATE FAILED: {base_passes}/320 with {len(mismatches)} mismatches")

for frozen_item in selected_rows:
    key = (round(float(frozen_item["phase"]), 12), int(frozen_item["fold"]))
    row = carrier_lookup.get(key)
    require(row is not None, f"Frozen V143 carrier not found: {key}")
    current_rep = actual_rep(row)
    frozen_rep = str(frozen_item["v134Representation"])
    require(current_rep == frozen_rep, f"Frozen V143 representation mismatch for {key}: {current_rep} != {frozen_rep}")
    require(str(frozen_item["selectedFamily"]) in family_features, f"Frozen V143 family unavailable for {key}")

print("V134 BASELINE GATE PASSED: 311/320 with 0 mismatches")
print("Frozen selector carrier/representation/family guard passed: 18/18")
print()

print("=== V143 ONE-SHOT HELD-OUT SCORING ===", flush=True)
v143_results = []
applied = []

for index, row in enumerate(carriers, 1):
    phase = float(row["phase"])
    fold = int(row["fold"])
    rep = actual_rep(row)
    key = (round(phase, 12), fold)

    frozen_item = selected_by_key.get(key)
    if frozen_item is not None:
        family = str(frozen_item["selectedFamily"])
        matrix = np.concatenate([matrices[rep], family_features[family]], axis=1)
        applied.append({
            "phase": phase,
            "fold": fold,
            "v134Representation": rep,
            "selectedFamily": family,
        })
    else:
        matrix = matrices[rep]

    result = evaluate_one(row, matrix)
    v143_results.append(result)
    if index % 40 == 0:
        print(f"V143 heartbeat {index}/320", flush=True)

require(len(applied) == EXPECTED_SELECTED, f"Expected {EXPECTED_SELECTED} V143 interventions, applied {len(applied)}")
applied_by_family = Counter(item["selectedFamily"] for item in applied)
applied_by_rep = Counter(item["v134Representation"] for item in applied)
require(dict(applied_by_family) == EXPECTED_BY_FAMILY, f"Applied V143 family counts changed: {dict(applied_by_family)}")
require(dict(applied_by_rep) == EXPECTED_BY_REP, f"Applied V143 representation counts changed: {dict(applied_by_rep)}")

v143_passes = sum(int(item["pass"]) for item in v143_results)
gains = 0
losses = 0
changed = []
for base_result, candidate_result in zip(base_results, v143_results):
    key = (round(float(base_result["phase"]), 12), int(base_result["fold"]))
    frozen_item = selected_by_key.get(key)
    family = str(frozen_item["selectedFamily"]) if frozen_item is not None else None
    if candidate_result["pass"] and not base_result["pass"]:
        gains += 1
        changed.append({
            "change": "GAIN",
            "phase": base_result["phase"],
            "fold": base_result["fold"],
            "baseLift": base_result["lift"],
            "v143Lift": candidate_result["lift"],
            "representation": base_result["representation"],
            "selectedFamily": family,
        })
    elif base_result["pass"] and not candidate_result["pass"]:
        losses += 1
        changed.append({
            "change": "LOSS",
            "phase": base_result["phase"],
            "fold": base_result["fold"],
            "baseLift": base_result["lift"],
            "v143Lift": candidate_result["lift"],
            "representation": base_result["representation"],
            "selectedFamily": family,
        })

candidate_after = sha256(candidate_path)
require(candidate_before == candidate_after, "Protected 949-event candidate changed during V143 evaluation")

promotion_candidate = bool(v143_passes > EXPECTED_BASE_PASSES and gains >= 1 and losses == 0)
champion_after_v143 = "V143" if promotion_candidate else "V134"

out = {
    "experiment": "V143-frozen-final-multifamily-heldout-evaluation",
    "baseline": {
        "name": "V134",
        "passes": base_passes,
        "total": EXPECTED_TOTAL,
        "artifactPassMismatches": len(mismatches),
    },
    "v143": {
        "passes": v143_passes,
        "total": EXPECTED_TOTAL,
        "gains": gains,
        "losses": losses,
        "net": gains - losses,
        "selectedCarriers": len(selected_keys),
        "selectedByFamily": EXPECTED_BY_FAMILY,
        "selectedByRepresentation": EXPECTED_BY_REP,
        "appliedCarriers": applied,
        "promotionCandidate": promotion_candidate,
    },
    "changedCarriers": changed,
    "championAfterV143Heldout": champion_after_v143,
    "selectorFrozenBeforeHeldoutEvaluation": True,
    "multiFamilySpecSha256": sha256(SPEC_PATH),
    "trainingOnlySelectorSha256": sha256(SELECTOR_PATH),
    "frozenSelectorSha256": sha256(FREEZE_PATH),
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
    "protected949CandidateHashUnchanged": True,
    "productionPromotionAllowed": False,
    "blind11mod16ConfirmationAllowed": promotion_candidate,
    "finalRhythmSustainSweep": True,
    "stopAfterV143": True,
    "noV144RhythmSustainSweepAllowed": True,
}

OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print()
print("=== V143 HELD-OUT EVALUATION COMPLETE ===")
print(f"V134 baseline: {base_passes}/320")
print(f"V143 final multi-family: {v143_passes}/320")
print(f"Gains/losses vs V134: +{gains}/-{losses} net={gains - losses:+d}")
print("Frozen V143 interventions applied:", len(applied))
print("Applied by family:", dict(applied_by_family))
print("Applied by representation:", dict(applied_by_rep))
print("Promotion candidate:", promotion_candidate)
print("Champion after V143 held-out:", champion_after_v143)
print("Protected 949-event candidate hash unchanged: True")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print("Production promotion: False")
print("Blind 11-mod-16 confirmation allowed:", promotion_candidate)
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print("NO V144 RHYTHM/SUSTAIN SWEEP: True")
print()
print("Changed carriers:")
if changed:
    for item in changed:
        family_text = item["selectedFamily"] if item["selectedFamily"] is not None else "none"
        print(
            f"{item['change']:4s} "
            f"phase={item['phase']:.12f} "
            f"fold={item['fold']} "
            f"baseLift={item['baseLift']:.2f} "
            f"v143Lift={item['v143Lift']:.2f} "
            f"rep={item['representation']} "
            f"family={family_text}"
        )
else:
    print("none")

print()
print("Saved:", OUT_PATH)
