from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v75-drop-p4sin-flip-anatomy-v76.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v75-drop-p4sin-flip-anatomy-v76-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
Q = float(v28.FROZEN_Q)
DROP_INDEX = 2  # V17 order: p2-sin, p2-cos, p4-sin, p4-cos


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_at_q(scores: np.ndarray, yy: np.ndarray):
    held = v1.select_top_fraction(scores, yy, Q)
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = bool(held["true"] > 0 and lift >= 5.0)
    return passed, lift, held, base


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    base_names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    pf = v17.phase_features(rows)
    keep = [0, 1, 3]
    x_drop = np.concatenate([xb, pf[:, keep]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    total = full_total = rescues = regressions = 0
    changed = []
    status_counts = Counter()
    reason_status = Counter()
    model_status = Counter()
    strict_status = Counter()
    tight_escape_status = Counter()
    phase_rows = []

    print("Starting V76 drop-p4-sin flip anatomy on already-exposed V57 family", flush=True)
    print("Representation fixed to V75 drop-p4-sin; model radius/lambda frozen from V57; q fixed at 0.20", flush=True)

    for scheme in v57.get("schemes") or []:
        phase = float(scheme["phase"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        saved_folds = {int(r["fold"]): r for r in (scheme.get("folds") or [])}
        drop_phase = full_phase = 0

        for fold in range(OUTER_FOLDS):
            saved = saved_folds[fold]
            chosen = saved.get("chosenModel") or {}
            radius = int(chosen["pairRadius"])
            lam = float(chosen["lambda"])
            test = ids == fold
            train = ~test

            print(f"phase={phase} fold={fold} V76 drop-p4-sin flip anatomy ...", flush=True)
            model = v2.fit_pairwise_ranker(x_drop[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x_drop[test], model)
            dp, dl, dh, db = pass_at_q(scores, y[test])

            full_cmp = saved.get("v28Comparison") or {}
            fp = bool(full_cmp.get("passed"))
            fl = float(full_cmp.get("heldoutPrecisionLift", 0.0))
            selector = saved.get("selector") or {}
            reason = str(selector.get("selectionReason", "unknown"))
            strict = int(selector.get("strictBroadSupportCount", -1))
            tight_escape = bool(selector.get("unanimousTightEscape", False))
            model_key = f"r={radius}|lambda={lam:g}"

            total += int(dp)
            full_total += int(fp)
            drop_phase += int(dp)
            full_phase += int(fp)

            if dp and not fp:
                status = "rescue"
                rescues += 1
            elif fp and not dp:
                status = "regression"
                regressions += 1
            elif dp and fp:
                status = "bothPass"
            else:
                status = "bothFail"

            status_counts[status] += 1
            reason_status[(reason, status)] += 1
            model_status[(model_key, status)] += 1
            strict_status[(strict, status)] += 1
            tight_escape_status[(tight_escape, status)] += 1

            if status in ("rescue", "regression"):
                changed.append({
                    "phase": phase,
                    "fold": fold,
                    "status": status,
                    "pairRadius": radius,
                    "lambda": lam,
                    "selectionReason": reason,
                    "strictBroadSupportCount": strict,
                    "unanimousTightEscape": tight_escape,
                    "savedV57OuterQ": float(saved.get("outerQ", Q)),
                    "dropP4SinAnchorLift": round(float(dl), 4),
                    "fullPhaseAnchorLift": fl,
                    "dropP4SinCandidate": dh,
                    "fullPhaseCandidate": full_cmp.get("heldoutCandidate"),
                    "heldoutBase": db,
                    "selectorTrainingSummary": {
                        "unanimousTightPassCountNonWorse": selector.get("unanimousTightPassCountNonWorse"),
                        "unanimousTightMeanLiftBetter": selector.get("unanimousTightMeanLiftBetter"),
                        "schemes": selector.get("schemes"),
                    },
                })

        phase_rows.append({"phase": phase, "dropP4SinPasses": drop_phase, "fullPhaseAnchorPasses": full_phase})

    min_drop = min(r["dropP4SinPasses"] for r in phase_rows)
    bottlenecks = [r["phase"] for r in phase_rows if r["dropP4SinPasses"] == min_drop]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V76")

    def flatten(counter: Counter):
        return {str(k): int(v) for k, v in counter.items()}

    out = {
        "schemaVersion": 76,
        "profileType": "v75-drop-p4sin-flip-anatomy-diagnostic",
        "diagnosticScope": "already-exposed-v57-1over64-family-only",
        "representation": "base+p2-sin+p2-cos+p4-cos",
        "qFrozen": Q,
        "modelHyperparametersFrozenFromV57": True,
        "dropP4SinPasses": total,
        "fullPhaseAnchorPasses": full_total,
        "rescuesVsFullPhaseAnchor": rescues,
        "regressionsVsFullPhaseAnchor": regressions,
        "minimumDropP4SinPhasePasses": min_drop,
        "dropP4SinBottleneckPhases": bottlenecks,
        "statusCounts": dict(status_counts),
        "changedOutcomeCount": len(changed),
        "changedOutcomesBySelectionReasonStatus": flatten(reason_status),
        "changedOutcomesByModelStatus": flatten(model_status),
        "changedOutcomesByStrictSupportStatus": flatten(strict_status),
        "changedOutcomesByUnanimousTightEscapeStatus": flatten(tight_escape_status),
        "changedOutcomes": changed,
        "phaseRows": phase_rows,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    manifest = {k: out[k] for k in [
        "schemaVersion", "representation", "qFrozen", "modelHyperparametersFrozenFromV57",
        "dropP4SinPasses", "fullPhaseAnchorPasses", "rescuesVsFullPhaseAnchor",
        "regressionsVsFullPhaseAnchor", "minimumDropP4SinPhasePasses", "dropP4SinBottleneckPhases",
        "statusCounts", "changedOutcomeCount", "changedOutcomesBySelectionReasonStatus",
        "changedOutcomesByModelStatus", "changedOutcomesByStrictSupportStatus",
        "changedOutcomesByUnanimousTightEscapeStatus", "diagnosticOutcomesTaintedForSelection",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "validatedNewChampion", "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V76 DROP-P4-SIN FLIP ANATOMY COMPLETE")
    print("Drop-p4-sin passes:", total, "/ 160")
    print("Full-phase anchor passes:", full_total, "/ 160")
    print("Rescues:", rescues, "Regressions:", regressions)
    print("Minimum drop-p4-sin phase passes:", min_drop, "/ 5")
    print("Drop-p4-sin bottleneck phases:", bottlenecks)
    print("Changed outcome count:", len(changed))
    print("Changed outcomes by selection reason/status:", flatten(reason_status))
    print("Changed outcomes by model/status:", flatten(model_status))
    print("Changed outcomes by strict support/status:", flatten(strict_status))
    print("Changed outcomes by unanimous tight escape/status:", flatten(tight_escape_status))
    for row in changed:
        print("Changed:", {k: row[k] for k in ["phase", "fold", "status", "pairRadius", "lambda", "selectionReason", "strictBroadSupportCount", "unanimousTightEscape", "dropP4SinAnchorLift", "fullPhaseAnchorLift"]})
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
