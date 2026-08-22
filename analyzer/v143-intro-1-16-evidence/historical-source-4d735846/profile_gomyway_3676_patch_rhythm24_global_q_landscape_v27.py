from __future__ import annotations

import hashlib
import json
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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-global-q-landscape-v27.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-global-q-landscape-v27-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
CHALLENGE_PHASES = (0.125, 0.375, 0.625, 0.875)
Q_GRID = (0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.075, 0.10, 0.15, 0.20)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_at_q(scores: np.ndarray, yy: np.ndarray, q: float):
    return v17.pass_at_q(scores, yy, q)


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V27 frozen-V17 global q landscape diagnostic", flush=True)
    print("Diagnostic only: challenge labels are used to map the global q landscape", flush=True)
    print("No selector is trained and no production rule is created", flush=True)

    landscape = {
        float(q): {
            "q": float(q),
            "passes": 0,
            "total": 0,
            "liftSum": 0.0,
            "phasePasses": {str(p): 0 for p in CHALLENGE_PHASES},
            "rows": [],
        }
        for q in Q_GRID
    }

    partitions: list[dict[str, Any]] = []

    for phase in CHALLENGE_PHASES:
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test

            print("    heartbeat V27 frozen V17 model-selection policy", flush=True)
            chosen = v5.choose_model(x[train], y[train], measures[train])
            radius = int(chosen["pairRadius"])
            lam = float(chosen["lambda"])
            base_q = float(chosen["tailQuantile"])

            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)

            part = {
                "phase": float(phase),
                "fold": int(fold),
                "baseQ": base_q,
                "chosenModel": chosen,
                "q": {},
            }

            for q in Q_GRID:
                passed, lift, held, base = pass_at_q(scores, y[test], float(q))
                st = landscape[float(q)]
                st["passes"] += int(passed)
                st["total"] += 1
                st["liftSum"] += float(lift)
                st["phasePasses"][str(phase)] += int(passed)
                row = {
                    "phase": float(phase),
                    "fold": int(fold),
                    "passed": bool(passed),
                    "lift": round(float(lift), 2),
                    "selected": int(held["selected"]),
                    "true": int(held["true"]),
                    "false": int(held["false"]),
                    "precision": float(held["precision"]),
                    "basePrecision": float(base["precision"]),
                }
                st["rows"].append(row)
                part["q"][str(q)] = row

            partitions.append(part)

    summaries = []
    best = None
    for q in Q_GRID:
        st = landscape[float(q)]
        min_phase = min(st["phasePasses"].values())
        mean_lift = st["liftSum"] / max(1, st["total"])
        summary = {
            "q": float(q),
            "passes": int(st["passes"]),
            "total": int(st["total"]),
            "phasePasses": st["phasePasses"],
            "minimumPhasePasses": int(min_phase),
            "meanLift": round(float(mean_lift), 3),
        }
        summaries.append(summary)
        key = (min_phase, st["passes"], mean_lift, -abs(float(q) - 0.05))
        if best is None or key > best[0]:
            best = (key, summary)

    winner = best[1]
    universal_q_promising = winner["passes"] >= 18 and winner["minimumPhasePasses"] >= 4

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V27")

    output = {
        "schemaVersion": 27,
        "profileType": "36.76-rhythm24-global-q-landscape-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceChampion": "V17",
        "challengePhases": list(CHALLENGE_PHASES),
        "qGrid": list(Q_GRID),
        "heldoutChallengeLabelsUsedForDiagnostic": True,
        "newSelectorTrained": False,
        "bestQ": winner["q"],
        "bestPasses": winner["passes"],
        "bestMinimumPhasePasses": winner["minimumPhasePasses"],
        "universalQPromising": universal_q_promising,
        "qSummaries": summaries,
        "partitions": partitions,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 27,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "bestQ": winner["q"],
        "bestPasses": winner["passes"],
        "bestMinimumPhasePasses": winner["minimumPhasePasses"],
        "universalQPromising": universal_q_promising,
        "heldoutChallengeLabelsUsedForDiagnostic": True,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 GLOBAL Q LANDSCAPE V27 COMPLETE")
    for s in summaries:
        print("q", s["q"], "passes", s["passes"], "/20 phases", s["phasePasses"], "min", s["minimumPhasePasses"], flush=True)
    print("Best q:", winner["q"])
    print("Best passes:", winner["passes"], "/ 20")
    print("Best minimum phase passes:", winner["minimumPhasePasses"], "/ 5")
    print("Universal q promising:", universal_q_promising)
    print("Heldout challenge labels used for diagnostic: True")
    print("New selector trained: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
