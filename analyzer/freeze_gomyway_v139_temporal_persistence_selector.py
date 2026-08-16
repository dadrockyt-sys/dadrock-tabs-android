from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("/workspaces/dadrock-tabs-android")
PUBLIC = ROOT / "public"
DEV_DIR = PUBLIC / "training" / "v139-temporal-persistence-development"
SPEC_PATH = DEV_DIR / "v139-persistence-spec.json"
DEV_PATH = DEV_DIR / "v139-training-only-selector.json"
OUT_PATH = DEV_DIR / "v139-frozen-selector.json"

EXPECTED_SELECTED = 3
EXPECTED_BY_REP = {
    "full_phase": 2,
    "v112_interactions": 1,
}
EXPECTED_KEYS = {
    (0.5712890625, 3, "full_phase"),
    (0.6494140625, 3, "full_phase"),
    (0.6962890625, 2, "v112_interactions"),
}
EXPECTED_OFFSETS = [0.0, 0.125]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if OUT_PATH.exists():
    raise RuntimeError(
        f"Frozen V139 selector already exists at {OUT_PATH}; refusing to overwrite it."
    )

if not SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V139 persistence spec missing: {SPEC_PATH}")
if not DEV_PATH.is_file():
    raise RuntimeError(f"V139 training-only development output missing: {DEV_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
dev = json.loads(DEV_PATH.read_text(encoding="utf-8"))

if int(spec.get("schemaVersion", -1)) != 139:
    raise RuntimeError("V139 persistence spec schema mismatch")
if spec.get("frozenBeforeDevelopmentRun") is not True:
    raise RuntimeError("V139 persistence spec was not frozen before development")
if int(spec.get("featureCount", -1)) != 14:
    raise RuntimeError("V139 frozen persistence feature count is not 14")

spec_rule = dict(spec.get("selectionRule") or {})
if [float(x) for x in spec_rule.get("validationPhaseOffsets", [])] != EXPECTED_OFFSETS:
    raise RuntimeError("V139 replicated validation phase offsets changed")

required_false = {
    "heldoutV134FoldScored": dev.get("heldoutV134FoldScored"),
    "heldoutOutcomeFieldsUsedForSelection": dev.get("heldoutOutcomeFieldsUsedForSelection"),
    "v136dEvaluationRowsRead": dev.get("v136dEvaluationRowsRead"),
    "v137HeldoutEvaluationRowsRead": dev.get("v137HeldoutEvaluationRowsRead"),
    "v138HeldoutEvaluationRowsRead": dev.get("v138HeldoutEvaluationRowsRead"),
    "professionalMidtermAnswersUsed": dev.get("professionalMidtermAnswersUsed"),
    "reserve11mod16Inspected": dev.get("reserve11mod16Inspected"),
    "newQHyperparameterTuningPerformed": dev.get("newQHyperparameterTuningPerformed"),
    "newLambdaHyperparameterTuningPerformed": dev.get("newLambdaHyperparameterTuningPerformed"),
    "newPairRadiusTuningPerformed": dev.get("newPairRadiusTuningPerformed"),
    "candidateEventsModified": dev.get("candidateEventsModified"),
    "productionPromotionAllowed": dev.get("productionPromotionAllowed"),
    "frozenForEvaluation": dev.get("frozenForEvaluation"),
}
for name, value in required_false.items():
    if value is not False:
        raise RuntimeError(
            f"V139 development contamination/safety guard failed: {name}={value}"
        )

if dev.get("protected949CandidateHashUnchanged") is not True:
    raise RuntimeError(
        "Protected 949-event candidate was not unchanged during V139 development"
    )

baseline = dict(dev.get("baselineChampion") or {})
if int(baseline.get("passes", -1)) != 311 or int(baseline.get("total", -1)) != 320:
    raise RuntimeError("V139 development is not anchored to V134 311/320")

frozen_spec = dict(dev.get("frozenPersistenceSpec") or {})
if str(frozen_spec.get("sha256") or "") != sha256(SPEC_PATH):
    raise RuntimeError(
        "V139 development output does not match the current frozen persistence spec"
    )
if int(frozen_spec.get("featureCount", -1)) != 14:
    raise RuntimeError("V139 development output does not contain 14 persistence features")

rule = dict((dev.get("selector") or {}).get("rule") or {})
if rule != spec_rule:
    raise RuntimeError("V139 development selector rule does not match frozen spec")

min_valid = int(rule.get("minimumValidInnerFoldsPerView", 3))
min_gains = int(rule.get("minimumPassGainsPerView", 1))
max_total_losses = int(rule.get("maximumPassLossesAcrossAllViews", 0))

selected = [
    item
    for item in (dev.get("decisions") or [])
    if bool(item.get("selected"))
]

if len(selected) != EXPECTED_SELECTED:
    raise RuntimeError(
        f"Expected exactly {EXPECTED_SELECTED} V139 selections, got {len(selected)}"
    )

keys = {
    (
        round(float(item["phase"]), 12),
        int(item["fold"]),
        str(item["v134Representation"]),
    )
    for item in selected
}
if keys != EXPECTED_KEYS:
    raise RuntimeError(f"V139 selected carrier keys changed: {keys} != {EXPECTED_KEYS}")

by_rep = Counter(str(item.get("v134Representation") or "") for item in selected)
if dict(by_rep) != EXPECTED_BY_REP:
    raise RuntimeError(
        f"V139 selected-by-representation changed: {dict(by_rep)} != {EXPECTED_BY_REP}"
    )

for item in selected:
    if int(item.get("totalInnerLossesAcrossViews", -1)) > max_total_losses:
        raise RuntimeError(f"Selected V139 row violates total-loss rule: {item}")

    views = list(item.get("replicatedViews") or [])
    if len(views) != len(EXPECTED_OFFSETS):
        raise RuntimeError(f"Selected V139 row missing replicated views: {item}")

    offsets = [float(view.get("phaseOffset", 999.0)) for view in views]
    if offsets != EXPECTED_OFFSETS:
        raise RuntimeError(f"Selected V139 row phase offsets changed: {offsets}")

    for view in views:
        valid = int(view.get("validInnerFolds", 0))
        gains = int(view.get("innerGains", 0))
        losses = int(view.get("innerLosses", 0))
        mean_delta = float(view.get("meanInnerLiftDelta", 0.0))
        median_delta = float(view.get("medianInnerLiftDelta", 0.0))
        nonnegative = int(view.get("nonnegativeLiftFolds", 0))
        required_nonnegative = int(view.get("requiredNonnegativeLiftFolds", 0))

        if view.get("viewRulePassed") is not True:
            raise RuntimeError(f"Selected V139 row has failed replicated view: {view}")
        if valid < min_valid:
            raise RuntimeError(f"Selected V139 view violates min-valid rule: {view}")
        if gains < min_gains:
            raise RuntimeError(f"Selected V139 view violates min-gains rule: {view}")
        if losses != 0:
            raise RuntimeError(f"Selected V139 view contains a pass loss: {view}")
        if mean_delta <= 0.0:
            raise RuntimeError(f"Selected V139 view violates positive-mean rule: {view}")
        if median_delta < 0.0:
            raise RuntimeError(f"Selected V139 view violates nonnegative-median rule: {view}")
        if nonnegative < required_nonnegative:
            raise RuntimeError(
                f"Selected V139 view violates nonnegative-fold rule: {view}"
            )

frozen_rows = []
for item in selected:
    frozen_rows.append(
        {
            "phase": float(item["phase"]),
            "fold": int(item["fold"]),
            "v134Representation": str(item["v134Representation"]),
            "totalInnerLossesAcrossViews": int(item["totalInnerLossesAcrossViews"]),
            "replicatedViews": [
                {
                    "phaseOffset": float(view["phaseOffset"]),
                    "innerPhase": float(view["innerPhase"]),
                    "validInnerFolds": int(view["validInnerFolds"]),
                    "innerGains": int(view["innerGains"]),
                    "innerLosses": int(view["innerLosses"]),
                    "meanInnerLiftDelta": float(view["meanInnerLiftDelta"]),
                    "medianInnerLiftDelta": float(view["medianInnerLiftDelta"]),
                    "nonnegativeLiftFolds": int(view["nonnegativeLiftFolds"]),
                    "requiredNonnegativeLiftFolds": int(
                        view["requiredNonnegativeLiftFolds"]
                    ),
                    "viewRulePassed": bool(view["viewRulePassed"]),
                }
                for view in item["replicatedViews"]
            ],
        }
    )

out = {
    "schemaVersion": 139,
    "experiment": "V139-frozen-temporal-persistence-selector",
    "baselineChampion": {
        "name": "V134",
        "passes": 311,
        "total": 320,
        "scorePercent": 97.1875,
    },
    "persistenceSpec": {
        "path": str(SPEC_PATH.relative_to(ROOT)),
        "sha256": sha256(SPEC_PATH),
        "featureCount": 14,
    },
    "developmentEvidence": {
        "path": str(DEV_PATH.relative_to(ROOT)),
        "sha256": sha256(DEV_PATH),
        "selectedCarriers": len(frozen_rows),
        "selectedByRepresentation": dict(by_rep),
        "selectionRule": rule,
    },
    "selected": frozen_rows,
    "frozenBeforeHeldoutEvaluation": True,
    "heldoutV134FoldScoredDuringDevelopment": False,
    "heldoutOutcomeFieldsUsedForSelection": False,
    "v136dEvaluationRowsUsed": False,
    "v137HeldoutEvaluationRowsUsed": False,
    "v138HeldoutEvaluationRowsUsed": False,
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "candidateEventsModified": False,
    "productionPromotionAllowed": False,
}

OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print("=== V139 SELECTOR FROZEN ===")
print("Frozen selections:", len(frozen_rows))
print("By representation:", dict(by_rep))
print("Replicated validation phase offsets:", EXPECTED_OFFSETS)
print("Held-out V134 folds scored during development: False")
print("V136D evaluation rows used: False")
print("V137 held-out rows used: False")
print("V138 held-out rows used: False")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print("Frozen before held-out evaluation: True")
print("Saved:", OUT_PATH)
