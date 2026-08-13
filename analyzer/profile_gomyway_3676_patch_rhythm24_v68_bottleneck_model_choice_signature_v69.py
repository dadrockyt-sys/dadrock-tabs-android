from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
V65_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65.json"
V68_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v67-nonepass-training-edge-pressure-v68.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v68-bottleneck-model-choice-signature-v69.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v68-bottleneck-model-choice-signature-v69-manifest.json"

TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225
TIGHT_STD_MIN = 0.50
BROAD_STD_MAX = 0.90


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lift_std(selector: dict[str, Any], side: str) -> float | None:
    vals = []
    for s in selector.get("schemes") or []:
        anchor = s.get("meanAnchorLift")
        other = s.get("meanTightLift") if side == "tight" else s.get("meanBroadLift")
        if anchor is None or other is None:
            return None
        vals.append(float(other) - float(anchor))
    if len(vals) < 2:
        return None
    return float(statistics.pstdev(vals))


def branch(q: float) -> str:
    if abs(q - TIGHT_Q) < 1e-12:
        return "tight"
    if abs(q - BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def model_key(model: dict[str, Any]) -> str:
    return f"r={int(model.get('pairRadius', -1))}|lambda={float(model.get('lambda', float('nan'))):.12g}"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    v65 = json.loads(V65_PATH.read_text(encoding="utf-8"))
    v68 = json.loads(V68_PATH.read_text(encoding="utf-8"))

    bottleneck_phases = {float(x) for x in (v65.get("bottleneckPhases") or [])}
    if not bottleneck_phases:
        raise RuntimeError("No V65 bottleneck phases found")

    nonepass_keys = {(float(x["phase"]), int(x["fold"])) for x in (v68.get("diagnostics") or [])}

    rows = []
    counts_by_status: dict[str, Counter] = defaultdict(Counter)
    counts_by_phase: dict[str, Counter] = defaultdict(Counter)

    for phase in v57.get("schemes") or []:
        ph = float(phase["phase"])
        if ph not in bottleneck_phases:
            continue
        for row in phase.get("folds") or []:
            fold = int(row.get("fold", -1))
            old_pass = bool(row.get("passed"))
            v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
            q = float(row.get("outerQ", ANCHOR_Q))
            selector = row.get("selector") or {}
            old_branch = branch(q)
            new_pass = old_pass
            new_branch = old_branch
            decision = "keep-current"
            dispersion = None

            if old_branch == "tight":
                dispersion = lift_std(selector, "tight")
                if dispersion is None:
                    raise RuntimeError("Missing tight dispersion inputs")
                if dispersion < TIGHT_STD_MIN:
                    new_pass = v28_pass
                    new_branch = "anchor"
                    decision = "revert-tight-to-anchor-low-dispersion"
                else:
                    decision = "keep-tight-high-dispersion"
            elif old_branch == "broad":
                dispersion = lift_std(selector, "broad")
                if dispersion is None:
                    raise RuntimeError("Missing broad dispersion inputs")
                if dispersion > BROAD_STD_MAX:
                    new_pass = v28_pass
                    new_branch = "anchor"
                    decision = "revert-broad-to-anchor-high-dispersion"
                else:
                    decision = "keep-broad-low-dispersion"

            status = "pass" if new_pass else "fail"
            key = model_key(row.get("chosenModel") or {})
            counts_by_status[status][key] += 1
            counts_by_phase[str(ph)][key] += 1

            rows.append({
                "phase": ph,
                "fold": fold,
                "statusAfterV64Gate": status,
                "isV67NonePassFold": (ph, fold) in nonepass_keys,
                "modelKey": key,
                "chosenModel": row.get("chosenModel") or {},
                "oldBranch": old_branch,
                "newBranch": new_branch,
                "decision": decision,
                "dispersion": dispersion,
                "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                "unanimousTightEscape": selector.get("unanimousTightEscape"),
            })

    failure_models = Counter(r["modelKey"] for r in rows if r["statusAfterV64Gate"] == "fail")
    pass_models = Counter(r["modelKey"] for r in rows if r["statusAfterV64Gate"] == "pass")
    nonepass_models = Counter(r["modelKey"] for r in rows if r["isV67NonePassFold"])

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V69")

    out = {
        "schemaVersion": 69,
        "profileType": "v68-bottleneck-model-choice-signature-diagnostic",
        "bottleneckPhases": sorted(bottleneck_phases),
        "rows": rows,
        "modelCountsByStatus": {k: dict(v) for k, v in counts_by_status.items()},
        "modelCountsByPhase": {k: dict(v) for k, v in counts_by_phase.items()},
        "failureModelCounts": dict(failure_models),
        "passModelCounts": dict(pass_models),
        "v67NonePassModelCounts": dict(nonepass_models),
        "diagnosticUsesAlreadyExposedV57Outcomes": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 69,
        "bottleneckPhases": sorted(bottleneck_phases),
        "rowCount": len(rows),
        "failureModelCounts": dict(failure_models),
        "passModelCounts": dict(pass_models),
        "v67NonePassModelCounts": dict(nonepass_models),
        "diagnosticUsesAlreadyExposedV57Outcomes": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V68 BOTTLENECK MODEL-CHOICE SIGNATURE V69 COMPLETE")
    print("Bottleneck phases:", sorted(bottleneck_phases))
    print("Failure model counts:", dict(failure_models))
    print("Pass model counts:", dict(pass_models))
    print("V67 none-pass model counts:", dict(nonepass_models))
    for r in rows:
        if r["statusAfterV64Gate"] == "fail":
            print("Failure", r["phase"], "fold", r["fold"], "model", r["modelKey"],
                  "branch", r["newBranch"], "decision", r["decision"],
                  "V67-nonepass", r["isV67NonePassFold"])
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
