from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/workspaces/dadrock-tabs-android")
DEV_DIR = ROOT / "public" / "training" / "v143-final-multifamily-development"
SPEC_PATH = DEV_DIR / "v143-final-multifamily-spec.json"
SELECTOR_PATH = DEV_DIR / "v143-training-only-selector.json"
OUT_PATH = DEV_DIR / "v143-frozen-selector.json"

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
EXPECTED_FAMILIES = {
    "normalized_temporal_contrast": 20,
    "adjacent_band_balance": 20,
    "spectral_shape": 10,
    "attack_sustain_summary": 15,
    "temporal_extrema": 15,
}
EXPECTED_PHASE_OFFSETS = [0.0, 0.125]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


require(SPEC_PATH.is_file(), f"Missing frozen V143 spec: {SPEC_PATH}")
require(SELECTOR_PATH.is_file(), f"Missing V143 training-only selector: {SELECTOR_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
selector = json.loads(SELECTOR_PATH.read_text(encoding="utf-8"))

require(int(spec.get("schemaVersion", -1)) == 143, "V143 spec schema mismatch")
require(spec.get("frozenBeforeDevelopmentRun") is True, "V143 family menu was not frozen before development")
require(spec.get("finalSweep") is True, "V143 spec is not marked finalSweep")
require(spec.get("stopAfterV143") is True, "V143 spec does not require stopping after V143")
require(int(spec.get("totalMenuFeatureCount", -1)) == 80, "V143 menu feature count changed")

family_meta = dict(spec.get("families") or {})
actual_family_counts = {name: int(meta.get("featureCount", -1)) for name, meta in family_meta.items()}
require(actual_family_counts == EXPECTED_FAMILIES, f"V143 frozen family menu changed: {actual_family_counts}")

rule = dict(spec.get("selectionRule") or {})
phase_offsets = [float(x) for x in (rule.get("validationPhaseOffsets") or [])]
require(phase_offsets == EXPECTED_PHASE_OFFSETS, f"V143 phase offsets changed: {phase_offsets}")
require(int(rule.get("innerFolds", -1)) == 4, "V143 inner-fold count changed")
require(int(rule.get("minimumValidInnerFoldsPerView", -1)) == 3, "V143 minimum valid-fold rule changed")
require(int(rule.get("minimumPassGainsPerView", -1)) == 1, "V143 minimum-gain rule changed")
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

require(selector.get("experiment") == "V143-final-multifamily-training-only-sweep", "Unexpected V143 selector experiment")
baseline = dict(selector.get("baselineChampion") or {})
require(baseline.get("name") == "V134", "V143 selector baseline is not V134")
require(int(baseline.get("passes", -1)) == 311, "V143 selector baseline is not 311/320")
require(int(baseline.get("total", -1)) == EXPECTED_TOTAL, "V143 selector baseline total changed")

frozen_spec_record = dict(selector.get("frozenMultiFamilySpec") or {})
require(frozen_spec_record.get("sha256") == sha256(SPEC_PATH), "V143 selector/spec SHA mismatch")
require(int(frozen_spec_record.get("totalMenuFeatureCount", -1)) == 80, "V143 selector menu count mismatch")
require(dict(frozen_spec_record.get("familyFeatureCounts") or {}) == EXPECTED_FAMILIES, "V143 selector family counts mismatch")

selector_summary = dict(selector.get("selector") or {})
require(int(selector_summary.get("selectedCarriers", -1)) == EXPECTED_SELECTED, "V143 selected-carrier count changed")
require(dict(selector_summary.get("selectedByFamily") or {}) == EXPECTED_BY_FAMILY, f"V143 family split changed: {selector_summary.get('selectedByFamily')}")
require(dict(selector_summary.get("selectedByRepresentation") or {}) == EXPECTED_BY_REP, f"V143 representation split changed: {selector_summary.get('selectedByRepresentation')}")

for key in (
    "heldoutV134FoldScored",
    "heldoutOutcomeFieldsUsedForSelection",
    "v136dEvaluationRowsRead",
    "v137HeldoutEvaluationRowsRead",
    "v138HeldoutEvaluationRowsRead",
    "v139HeldoutEvaluationRowsRead",
    "v140HeldoutEvaluationRowsRead",
    "v141HeldoutEvaluationRowsRead",
    "v142HeldoutEvaluationRowsRead",
    "professionalMidtermAnswersUsed",
    "reserve11mod16Inspected",
    "newQHyperparameterTuningPerformed",
    "newLambdaHyperparameterTuningPerformed",
    "newPairRadiusTuningPerformed",
    "candidateEventsModified",
    "productionPromotionAllowed",
    "frozenForEvaluation",
):
    require(selector.get(key) is False, f"V143 selector safety violation: {key}={selector.get(key)}")
require(selector.get("protected949CandidateHashUnchanged") is True, "Protected 949-event candidate changed during V143 development")
require(selector.get("finalRhythmSustainSweep") is True, "V143 selector is not marked final sweep")
require(selector.get("stopAfterV143") is True, "V143 selector does not enforce stop after V143")

decisions = list(selector.get("decisions") or [])
require(len(decisions) == EXPECTED_TOTAL, f"Expected {EXPECTED_TOTAL} V143 decisions, found {len(decisions)}")
selected = [item for item in decisions if item.get("selected") is True]
require(len(selected) == EXPECTED_SELECTED, f"Expected {EXPECTED_SELECTED} selected V143 decisions, found {len(selected)}")

for item in selected:
    family = str(item.get("selectedFamily"))
    require(family in EXPECTED_FAMILIES, f"Unknown selected V143 family: {family}")
    require(int(item.get("qualifiedFamilyCount", 0)) >= 1, "Selected V143 decision has no qualified family")

    family_results = list(item.get("familyResults") or [])
    require(len(family_results) == len(EXPECTED_FAMILIES), "Selected V143 decision does not contain all frozen family results")
    results_by_family = {str(result.get("family")): result for result in family_results}
    require(set(results_by_family) == set(EXPECTED_FAMILIES), "Selected V143 decision family result set changed")

    qualified = [result for result in family_results if result.get("qualified") is True]
    require(qualified, "Selected V143 decision has no qualified family result")
    qualified.sort(
        key=lambda result: (
            -float(result.get("minimumMeanLiftDeltaAcrossViews", 0.0)),
            -int(result.get("totalInnerGainsAcrossViews", 0)),
            -float(result.get("minimumMedianLiftDeltaAcrossViews", 0.0)),
            -float(result.get("sumMeanLiftDeltaAcrossViews", 0.0)),
            str(result.get("family")),
        )
    )
    require(str(qualified[0].get("family")) == family, "Selected V143 family no longer matches frozen winner ordering")

    winner = results_by_family[family]
    require(winner.get("qualified") is True, "Selected V143 winning family is not qualified")
    require(int(winner.get("totalInnerLossesAcrossViews", -1)) == 0, "Selected V143 winner has an inner-CV loss")

    views = list(winner.get("replicatedViews") or [])
    require(len(views) == 2, "Selected V143 winner does not have exactly two replicated views")
    require([float(view.get("phaseOffset")) for view in views] == EXPECTED_PHASE_OFFSETS, "Selected V143 winner phase offsets changed")
    for view in views:
        require(view.get("viewRulePassed") is True, "Selected V143 winner has a failed replicated view")
        require(int(view.get("validInnerFolds", 0)) >= 3, "Selected V143 winner has too few valid inner folds")
        require(int(view.get("innerGains", 0)) >= 1, "Selected V143 winner lacks the required pass gain")
        require(int(view.get("innerLosses", -1)) == 0, "Selected V143 winner has an inner loss")
        require(float(view.get("meanInnerLiftDelta", 0.0)) > 0.0, "Selected V143 winner lacks positive mean lift delta")
        require(float(view.get("medianInnerLiftDelta", -1.0)) >= 0.0, "Selected V143 winner has negative median lift delta")
        require(int(view.get("nonnegativeLiftFolds", 0)) >= int(view.get("requiredNonnegativeLiftFolds", 999)), "Selected V143 winner fails nonnegative-fold requirement")

    score = dict(item.get("selectedFamilyScore") or {})
    for key in (
        "minimumMeanLiftDeltaAcrossViews",
        "totalInnerGainsAcrossViews",
        "minimumMedianLiftDeltaAcrossViews",
        "sumMeanLiftDeltaAcrossViews",
    ):
        require(score.get(key) == winner.get(key), f"Selected V143 frozen winner score mismatch for {key}")

actual_by_family: dict[str, int] = {}
actual_by_rep: dict[str, int] = {}
for item in selected:
    family = str(item["selectedFamily"])
    rep = str(item["v134Representation"])
    actual_by_family[family] = actual_by_family.get(family, 0) + 1
    actual_by_rep[rep] = actual_by_rep.get(rep, 0) + 1
require(actual_by_family == EXPECTED_BY_FAMILY, f"Selected V143 family recount mismatch: {actual_by_family}")
require(actual_by_rep == EXPECTED_BY_REP, f"Selected V143 representation recount mismatch: {actual_by_rep}")

out = {
    "experiment": "V143-final-multifamily-frozen-selector",
    "baselineChampion": baseline,
    "sourceTrainingOnlySelector": {
        "path": str(SELECTOR_PATH.relative_to(ROOT)),
        "sha256": sha256(SELECTOR_PATH),
    },
    "frozenMultiFamilySpec": {
        "path": str(SPEC_PATH.relative_to(ROOT)),
        "sha256": sha256(SPEC_PATH),
        "familyFeatureCounts": EXPECTED_FAMILIES,
        "totalMenuFeatureCount": 80,
    },
    "selector": {
        "selectedCarriers": EXPECTED_SELECTED,
        "selectedByFamily": EXPECTED_BY_FAMILY,
        "selectedByRepresentation": EXPECTED_BY_REP,
        "validationPhaseOffsets": EXPECTED_PHASE_OFFSETS,
        "maximumPassLossesAcrossAllViewsForWinningFamily": 0,
    },
    "selections": selected,
    "heldoutV134FoldScoredBeforeFreeze": False,
    "priorHeldoutEvaluationRowsUsedToFreeze": False,
    "professionalMidtermAnswersUsedToFreeze": False,
    "reserve11mod16InspectedBeforeFreeze": False,
    "candidateEventsModified": False,
    "protected949CandidateHashUnchangedDuringDevelopment": True,
    "frozenBeforeHeldoutEvaluation": True,
    "oneShotHeldoutEvaluationAllowed": True,
    "productionPromotionAllowed": False,
    "finalRhythmSustainSweep": True,
    "stopAfterV143": True,
}

OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print("=== V143 FINAL MULTI-FAMILY SELECTOR FROZEN ===")
print("Frozen selections:", EXPECTED_SELECTED)
print("By family:", EXPECTED_BY_FAMILY)
print("By representation:", EXPECTED_BY_REP)
print("Replicated validation phase offsets:", EXPECTED_PHASE_OFFSETS)
print("Held-out V134 folds scored before freeze: False")
print("Prior held-out evaluation rows used to freeze: False")
print("Professional/midterm answers used to freeze: False")
print("11-mod-16 reserve inspected before freeze: False")
print("Frozen before held-out evaluation: True")
print("FINAL RHYTHM/SUSTAIN SWEEP: True")
print("STOP AFTER V143: True")
print("Saved:", OUT_PATH)
