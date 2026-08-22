from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V80_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v79-cosine-dual-dispersion-combined-v80.json"
SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v80-flip-and-floor-anatomy-v81.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v80-flip-and-floor-anatomy-v81-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
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


def selected_q(row: dict[str, Any]) -> tuple[float, str, float | None]:
    old_q = float(row.get("outerQ", ANCHOR_Q))
    selector = row.get("selector") or {}
    if abs(old_q - TIGHT_Q) < 1e-12:
        std = lift_std(selector, "tight")
        if std is None:
            raise RuntimeError("Missing tight dispersion inputs")
        if std >= TIGHT_STD_MIN:
            return TIGHT_Q, "keep-tight-high-dispersion", std
        return ANCHOR_Q, "revert-tight-to-anchor-low-dispersion", std
    if abs(old_q - BROAD_Q) < 1e-12:
        std = lift_std(selector, "broad")
        if std is None:
            raise RuntimeError("Missing broad dispersion inputs")
        if std <= BROAD_STD_MAX:
            return BROAD_Q, "keep-broad-low-dispersion", std
        return ANCHOR_Q, "revert-broad-to-anchor-high-dispersion", std
    return ANCHOR_Q, "keep-anchor", None


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float) -> tuple[bool, float]:
    held = v1.select_top_fraction(scores, yy, q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(held["true"] > 0 and lift >= 5.0), lift


def q_bucket(q: float) -> str:
    if abs(q - TIGHT_Q) < 1e-12:
        return "tight"
    if abs(q - BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v80 = json.loads(V80_PATH.read_text(encoding="utf-8"))
    if int(v80.get("schemaVersion", -1)) != 80:
        raise RuntimeError("V80 output missing or wrong schema")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    v80_bottlenecks = {
        str(r["source"]): set(float(x) for x in (r.get("bottleneckPhases") or []))
        for r in (v80.get("results") or [])
    }

    changed_rows = []
    floor_failure_rows = []
    status_decision = Counter()
    status_model = Counter()
    status_old_branch = Counter()
    status_strict = Counter()
    status_unanimous = Counter()

    total = v28_total = rescues = regressions = 0
    print("Starting V81 V80 flip + floor anatomy on already-exposed V56/V57 families", flush=True)

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text(encoding="utf-8"))
        bottleneck_set = v80_bottlenecks.get(source_name, set())

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                test = ids == fold
                train = ~test
                cm = row.get("chosenModel") or {}
                if "pairRadius" in cm and "lambda" in cm:
                    radius = int(cm["pairRadius"])
                    lam = float(cm["lambda"])
                    model_source = "saved"
                else:
                    cm = v5.choose_model(x_full[train], y[train], measures[train])
                    radius = int(cm["pairRadius"])
                    lam = float(cm["lambda"])
                    model_source = "training-only-reconstructed"

                q, decision, dispersion = selected_q(row)
                model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                passed, lift = pass_at_q(v2.scores_for(x_cos[test], model), y[test], q)
                cmp = row.get("v28Comparison") or {}
                v28_pass = bool(cmp.get("passed"))
                v28_lift = float(cmp.get("heldoutPrecisionLift", 0.0))

                total += int(passed)
                v28_total += int(v28_pass)
                rescues += int(passed and not v28_pass)
                regressions += int(v28_pass and not passed)

                if passed and not v28_pass:
                    status = "rescue"
                elif v28_pass and not passed:
                    status = "regression"
                elif passed:
                    status = "bothPass"
                else:
                    status = "bothFail"

                selector = row.get("selector") or {}
                base_record = {
                    "source": source_name,
                    "phase": phase,
                    "fold": int(fold),
                    "status": status,
                    "passed": bool(passed),
                    "v28Passed": bool(v28_pass),
                    "v80Q": float(q),
                    "v80QBucket": q_bucket(q),
                    "v80Decision": decision,
                    "dispersion": None if dispersion is None else float(dispersion),
                    "oldOuterQ": float(row.get("outerQ", ANCHOR_Q)),
                    "oldQBucket": q_bucket(float(row.get("outerQ", ANCHOR_Q))),
                    "selectionReason": selector.get("selectionReason"),
                    "strictBroadSupportCount": int(selector.get("strictBroadSupportCount", 0)),
                    "unanimousTightEscape": bool(selector.get("unanimousTightEscape", False)),
                    "pairRadius": radius,
                    "lambda": lam,
                    "modelSource": model_source,
                    "v80HeldoutPrecisionLift": round(float(lift), 4),
                    "v28HeldoutPrecisionLift": round(float(v28_lift), 4),
                    "isV80BottleneckPhase": phase in bottleneck_set,
                }

                if status in ("rescue", "regression"):
                    changed_rows.append(base_record)
                    status_decision[(status, decision)] += 1
                    status_model[(status, f"r{radius}|lambda{lam:g}")] += 1
                    status_old_branch[(status, q_bucket(float(row.get("outerQ", ANCHOR_Q))))] += 1
                    status_strict[(status, int(selector.get("strictBroadSupportCount", 0)))] += 1
                    status_unanimous[(status, bool(selector.get("unanimousTightEscape", False)))] += 1

                if phase in bottleneck_set and not passed:
                    floor_failure_rows.append(base_record)

    if total != int((v80.get("combined") or {}).get("foldsPassed", -1)):
        raise RuntimeError(f"V81 reproduction mismatch: got {total}, V80 says {(v80.get('combined') or {}).get('foldsPassed')}")

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V81")

    out = {
        "schemaVersion": 81,
        "profileType": "v80-flip-and-floor-anatomy-diagnostic",
        "reproducedV80": {
            "foldsPassed": total,
            "v28ComparisonPasses": v28_total,
            "rescuesVsV28": rescues,
            "regressionsVsV28": regressions,
        },
        "changedOutcomeCount": len(changed_rows),
        "floorFailureCount": len(floor_failure_rows),
        "changedByDecisionStatus": {f"{k[0]}|{k[1]}": v for k, v in status_decision.items()},
        "changedByModelStatus": {f"{k[0]}|{k[1]}": v for k, v in status_model.items()},
        "changedByOldBranchStatus": {f"{k[0]}|{k[1]}": v for k, v in status_old_branch.items()},
        "changedByStrictSupportStatus": {f"{k[0]}|{k[1]}": v for k, v in status_strict.items()},
        "changedByUnanimousTightStatus": {f"{k[0]}|{k[1]}": v for k, v in status_unanimous.items()},
        "changedRows": changed_rows,
        "floorFailureRows": floor_failure_rows,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "reproducedV80", "changedOutcomeCount", "floorFailureCount",
        "changedByDecisionStatus", "changedByModelStatus", "changedByOldBranchStatus",
        "changedByStrictSupportStatus", "changedByUnanimousTightStatus",
        "diagnosticOutcomesTaintedForSelection", "newReserved1over128OddNumeratorPhasesReferenced",
        "newTuningPerformed", "validatedNewChampion", "protected949CandidateHashUnchanged",
        "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V81 V80 FLIP + FLOOR ANATOMY COMPLETE")
    print("Reproduced V80:", out["reproducedV80"])
    print("Changed outcome count:", len(changed_rows))
    print("Floor failure count:", len(floor_failure_rows))
    print("Changed by decision/status:", out["changedByDecisionStatus"])
    print("Changed by model/status:", out["changedByModelStatus"])
    print("Changed by old branch/status:", out["changedByOldBranchStatus"])
    print("Changed by strict support/status:", out["changedByStrictSupportStatus"])
    print("Changed by unanimous-tight/status:", out["changedByUnanimousTightStatus"])
    for r in changed_rows:
        print("Changed:", r)
    for r in floor_failure_rows:
        print("FloorFailure:", r)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
