from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_quarter_phase_training_q_selector_v20 as v20

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v20-training-geometry-q-preference-v22.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v20-training-geometry-q-preference-v22-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
PHASE = 0.25
Q_A = 0.025
Q_B = 0.03


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_geometry(scores: np.ndarray, q: float) -> dict[str, float]:
    s = np.asarray(scores, dtype=np.float64)
    if len(s) == 0:
        return {}
    order = np.sort(s)[::-1]
    n = len(order)
    k = max(1, int(np.ceil(q * n)))
    cutoff = float(order[min(k - 1, n - 1)])
    next_score = float(order[k]) if k < n else cutoff
    top5 = float(np.mean(order[: max(1, int(np.ceil(0.05 * n)))]))
    top10 = float(np.mean(order[: max(1, int(np.ceil(0.10 * n)))]))
    return {
        "scoreStd": float(np.std(s)),
        "scoreMedian": float(np.median(s)),
        "scoreP90": float(np.quantile(s, 0.90)),
        "scoreP95": float(np.quantile(s, 0.95)),
        "boundaryGap": cutoff - next_score,
        "top5VsTop10Gap": top5 - top10,
        "upperTailSpread": float(np.quantile(s, 0.95) - np.median(s)),
    }


def summarize(rows: list[dict[str, Any]], key: str) -> dict[str, float]:
    vals = [float(r["geometry"].get(key, 0.0)) for r in rows if key in r.get("geometry", {})]
    if not vals:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0}
    a = np.asarray(vals, dtype=np.float64)
    return {
        "mean": round(float(np.mean(a)), 6),
        "median": round(float(np.median(a)), 6),
        "min": round(float(np.min(a)), 6),
        "max": round(float(np.max(a)), 6),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v20.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))
    outer_ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, PHASE) for m in measures], dtype=np.int16)

    print("Starting V22 training-only geometry vs q-preference diagnostic", flush=True)
    print("Diagnostic only; compares q=0.025 vs q=0.03 on inner quarter-phase folds", flush=True)

    observations: list[dict[str, Any]] = []

    for outer_fold in range(OUTER_FOLDS):
        outer_train = outer_ids != outer_fold
        xt = x[outer_train]
        yt = y[outer_train]
        mt = measures[outer_train]

        chosen = v5.choose_model(xt, yt, mt)
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])

        ilo, ihi = int(np.min(mt)), int(np.max(mt))
        inner_ids = np.asarray([v18.phased_fold(int(m), ilo, ihi, INNER_FOLDS, PHASE) for m in mt], dtype=np.int16)

        for inner_fold in range(INNER_FOLDS):
            val = inner_ids == inner_fold
            subtrain = ~val
            if int(np.sum(val)) == 0 or int(np.sum(subtrain)) == 0:
                continue

            model = v2.fit_pairwise_ranker(xt[subtrain], yt[subtrain], mt[subtrain], radius, lam)
            scores = v2.scores_for(xt[val], model)
            p25, lift25, held25, _ = v20.pass_at_q(scores, yt[val], Q_A)
            p30, lift30, held30, _ = v20.pass_at_q(scores, yt[val], Q_B)

            if p30 and not p25:
                preference = "q0030-only-pass"
            elif p25 and not p30:
                preference = "q0025-only-pass"
            elif p25 and p30:
                preference = "both-pass"
            else:
                preference = "both-fail"

            obs = {
                "outerFold": outer_fold,
                "innerFold": inner_fold,
                "preference": preference,
                "q0025Passed": bool(p25),
                "q0030Passed": bool(p30),
                "q0025Lift": round(float(lift25), 2),
                "q0030Lift": round(float(lift30), 2),
                "q0025Candidate": held25,
                "q0030Candidate": held30,
                "geometry": score_geometry(scores, Q_A),
            }
            observations.append(obs)
            print(
                f"heartbeat V22 outer={outer_fold} inner={inner_fold} pref={preference} "
                f"lift25={round(lift25,2)} lift30={round(lift30,2)}",
                flush=True,
            )

    groups: dict[str, list[dict[str, Any]]] = {}
    for obs in observations:
        groups.setdefault(str(obs["preference"]), []).append(obs)

    geometry_keys = ["scoreStd", "scoreMedian", "scoreP90", "scoreP95", "boundaryGap", "top5VsTop10Gap", "upperTailSpread"]
    group_summary = {
        name: {
            "count": len(items),
            "geometry": {k: summarize(items, k) for k in geometry_keys},
            "meanLiftDeltaQ0030MinusQ0025": round(float(np.mean([r["q0030Lift"] - r["q0025Lift"] for r in items])), 4) if items else 0.0,
        }
        for name, items in groups.items()
    }

    q30_only = groups.get("q0030-only-pass", [])
    q25_only = groups.get("q0025-only-pass", [])
    both_pass = groups.get("both-pass", [])
    both_fail = groups.get("both-fail", [])

    # This profiler does not invent a selector. It only declares whether enough
    # training-only examples exist to justify a subsequent predeclared rule test.
    signal_ready = len(q30_only) >= 2 and (len(q25_only) >= 1 or len(both_pass) >= 2)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V22")

    output = {
        "schemaVersion": 22,
        "profileType": "36.76-rhythm24-v20-training-only-geometry-q-preference-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "phase": PHASE,
        "comparedQs": [Q_A, Q_B],
        "observationCount": len(observations),
        "preferenceCounts": {k: len(v) for k, v in groups.items()},
        "groupSummary": group_summary,
        "observations": observations,
        "trainingGeometrySignalReady": bool(signal_ready),
        "nextTarget": "predeclare-geometry-selector-test" if signal_ready else "freeze-v17-and-stop-quarter-phase-retuning",
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 22,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "observationCount": len(observations),
        "preferenceCounts": output["preferenceCounts"],
        "trainingGeometrySignalReady": bool(signal_ready),
        "nextTarget": output["nextTarget"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V20 TRAINING GEOMETRY Q PREFERENCE V22 COMPLETE")
    print("Observations:", len(observations))
    print("Preference counts:", output["preferenceCounts"])
    print("Training geometry signal ready:", signal_ready)
    print("Next target:", output["nextTarget"])
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
