from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("/workspaces/dadrock-tabs-android")
PUBLIC = ROOT / "public"
DEV_DIR = PUBLIC / "training" / "v138-cross-band-sustain-development"
SPEC_PATH = DEV_DIR / "v138-structure-spec.json"
DEV_PATH = DEV_DIR / "v138-training-only-selector.json"
OUT_PATH = DEV_DIR / "v138-frozen-selector.json"

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
        f"Frozen V138 selector already exists at {OUT_PATH}; refusing to overwrite it."
    )

if not SPEC_PATH.is_file():
    raise RuntimeError(f"Frozen V138 structure spec missing: {SPEC_PATH}")
if not DEV_PATH.is_file():
    raise RuntimeError(f"V138 training-only development output missing: {DEV_PATH}")

spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
dev = json.loads(DEV_PATH.read_text(encoding="utf-8"))

if int(spec.get("schemaVersion", -1)) != 138:
    raise RuntimeError("V138 structure spec schema mismatch")
if spec.get("frozenBeforeDevelopmentRun") is not True:
    raise RuntimeError("V138 structure spec was not frozen before development")
if int(spec.get("featureCount", -1)) != 16:
    raise RuntimeError("V138 frozen structure feature count is not 16")

required_false = {
    "heldoutV134FoldScored": dev.get("heldoutV134FoldScored"),
    "heldoutOutcomeFieldsUsedForSelection": dev.get("heldoutOutcomeFieldsUsedForSelection"),
    "v136dEvaluationRowsRead": dev.get("v136dEvaluationRowsRead"),
    "v136dEvaluationLossesUsed": dev.get("v136dEvaluationLossesUsed"),
    "v137HeldoutEvaluationRowsRead": dev.get("v137HeldoutEvaluationRowsRead"),
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
        raise RuntimeError(f"V138 development contamination/safety guard failed: {name}={value}")

if dev.get("protected949CandidateHashUnchanged") is not True:
    raise RuntimeError("Protected 949-event candidate was not unchanged during V138 development")

baseline = dict(dev.get("baselineChampion") or {})
if int(baseline.get("passes", -1)) != 311 or int(baseline.get("total", -1)) != 320:
    raise RuntimeError("V138 development is not anchored to V134 311/320")

frozen_spec = dict(dev.get("frozenStructureSpec") or {})
if str(frozen_spec.get("sha256") or "") != sha256(SPEC_PATH):
    raise RuntimeError("V138 development output does not match the current frozen structure spec")

rule = dict((dev.get("selector") or {}).get("rule") or {})
min_valid = int(rule.get("minimumValidInnerFolds", 3))
min_gains = int(rule.get("minimumPassGains", 1))
max_losses = int(rule.get("maximumPassLosses", 0))

selected = [
    item
    for item in (dev.get("decisions") or [])
    if bool(item.get("selected"))
]

if len(selected) != EXPECTED_SELECTED:
    raise RuntimeError(
        f"Expected exactly {EXPECTED_SELECTED} V138 selections, got {len(selected)}"
    )

keys = [
    (round(float(item["phase"]), 12), int(item["fold"]))
    for item in selected
]
if len(set(keys)) != len(keys):
    raise RuntimeError("V138 selected carrier keys are not unique")

by_rep = Counter(str(item.get("v134Representation") or "") for item in selected)
if dict(by_rep) != EXPECTED_BY_REP:
    raise RuntimeError(
        f"V138 selected-by-representation changed: {dict(by_rep)} != {EXPECTED_BY_REP}"
    )

for item in selected:
    valid = int(item.get("validInnerFolds", 0))
    gains = int(item.get("innerGains", 0))
    losses = int(item.get("innerLosses", 0))
    mean_delta = float(item.get("meanInnerLiftDelta", 0.0))
    median_delta = float(item.get("medianInnerLiftDelta", 0.0))
    nonnegative = int(item.get("nonnegativeLiftFolds", 0))
    required_nonnegative = int(item.get("requiredNonnegativeLiftFolds", 0))

    if valid < min_valid:
        raise RuntimeError(f"Selected V138 row violates min-valid rule: {item}")
    if gains < min_gains:
        raise RuntimeError(f"Selected V138 row violates min-gains rule: {item}")
    if losses > max_losses:
        raise RuntimeError(f"Selected V138 row violates max-losses rule: {item}")
    if mean_delta <= 0.0:
        raise RuntimeError(f"Selected V138 row violates positive-mean rule: {item}")
    if median_delta < 0.0:
        raise RuntimeError(f"Selected V138 row violates nonnegative-median rule: {item}")
    if nonnegative < required_nonnegative:
        raise RuntimeError(f"Selected V138 row violates nonnegative-fold rule: {item}")

frozen_rows = [
    {
        "phase": float(item["phase"]),
        "fold": int(item["fold"]),
        "v134Representation": str(item["v134Representation"]),
        "validInnerFolds": int(item["validInnerFolds"]),
        "innerGains": int(item["innerGains"]),
        "innerLosses": int(item["innerLosses"]),
        "meanInnerLiftDelta": float(item["meanInnerLiftDelta"]),
        "medianInnerLiftDelta": float(item["medianInnerLiftDelta"]),
        "nonnegativeLiftFolds": int(item["nonnegativeLiftFolds"]),
        "requiredNonnegativeLiftFolds": int(item["requiredNonnegativeLiftFolds"]),
    }
    for item in selected
]

out = {
    "schemaVersion": 138,
    "experiment": "V138-frozen-cross-band-sustain-selector",
    "baselineChampion": {
        "name": "V134",
        "passes": 311,
        "total": 320,
        "scorePercent": 97.1875,
    },
    "structureSpec": {
        "path": str(SPEC_PATH.relative_to(ROOT)),
        "sha256": sha256(SPEC_PATH),
        "featureCount": 16,
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
    "professionalMidtermAnswersUsed": False,
    "reserve11mod16Inspected": False,
    "candidateEventsModified": False,
    "productionPromotionAllowed": False,
}

OUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

print("=== V138 SELECTOR FROZEN ===")
print("Frozen selections:", len(frozen_rows))
print("By representation:", dict(by_rep))
print("Held-out V134 folds scored during development: False")
print("V136D evaluation rows used: False")
print("V137 held-out rows used: False")
print("Professional/midterm answers used: False")
print("11-mod-16 reserve inspected: False")
print("Frozen before held-out evaluation: True")
print("Saved:", OUT_PATH)
