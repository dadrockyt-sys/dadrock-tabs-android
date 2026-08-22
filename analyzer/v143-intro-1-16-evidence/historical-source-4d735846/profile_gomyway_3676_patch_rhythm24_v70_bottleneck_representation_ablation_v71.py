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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v70-bottleneck-representation-ablation-v71.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v70-bottleneck-representation-ablation-v71-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
BOTTLENECK_PHASES = (0.328125, 0.703125, 0.984375)
ANCHOR_Q = float(v28.FROZEN_Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(source.get("candidateSlots") or [])
    if not rows or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    by_phase = {round(float(s["phase"]), 12): s for s in (v57.get("schemes") or [])}

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    xp = np.concatenate([xb, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    diagnostics = []
    flips = Counter()
    base_pass_total = phase_pass_total = 0

    for phase in BOTTLENECK_PHASES:
        scheme = by_phase.get(round(float(phase), 12))
        if scheme is None:
            raise RuntimeError(f"Missing V57 scheme for phase {phase}")
        folds = {int(f["fold"]): f for f in (scheme.get("folds") or [])}
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)

        for fold in range(OUTER_FOLDS):
            vf = folds.get(fold)
            if vf is None:
                raise RuntimeError(f"Missing V57 fold row phase={phase} fold={fold}")
            chosen_model = vf.get("chosenModel") or {}
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])
            test = ids == fold
            train = ~test

            print(f"phase={phase} fold={fold} representation ablation ...", flush=True)

            base_model = v2.fit_pairwise_ranker(xb[train], y[train], measures[train], radius, lam)
            base_scores = v2.scores_for(xb[test], base_model)
            bp, bl, bh, bb = v17.pass_at_q(base_scores, y[test], ANCHOR_Q)

            phase_model = v2.fit_pairwise_ranker(xp[train], y[train], measures[train], radius, lam)
            phase_scores = v2.scores_for(xp[test], phase_model)
            pp, pl, ph, pb = v17.pass_at_q(phase_scores, y[test], ANCHOR_Q)

            base_pass_total += int(bp)
            phase_pass_total += int(pp)
            if bp and not pp:
                flip = "base-rescue"
            elif pp and not bp:
                flip = "phase-rescue"
            elif bp and pp:
                flip = "both-pass"
            else:
                flip = "both-fail"
            flips[flip] += 1

            diagnostics.append({
                "phase": float(phase),
                "fold": int(fold),
                "pairRadius": radius,
                "lambda": lam,
                "frozenAnchorQ": ANCHOR_Q,
                "v57OuterQ": float(vf.get("outerQ", ANCHOR_Q)),
                "v57Passed": bool(vf.get("passed")),
                "baseRepresentation": {
                    "passed": bool(bp),
                    "heldoutPrecisionLift": round(float(bl), 2),
                    "heldoutCandidate": bh,
                    "heldoutBase": bb,
                },
                "phaseAugmentedRepresentation": {
                    "passed": bool(pp),
                    "heldoutPrecisionLift": round(float(pl), 2),
                    "heldoutCandidate": ph,
                    "heldoutBase": pb,
                },
                "flipClass": flip,
            })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V71")

    out = {
        "schemaVersion": 71,
        "profileType": "v70-bottleneck-representation-ablation-diagnostic",
        "diagnosticScope": "already-exposed-v57-bottleneck-phases-only",
        "bottleneckPhases": list(BOTTLENECK_PHASES),
        "comparison": "base-source-features-vs-frozen-v17-phase-augmented-features",
        "modelHyperparametersFrozenPerFoldFromV57": True,
        "frozenAnchorQ": ANCHOR_Q,
        "baseRepresentationPasses": int(base_pass_total),
        "phaseAugmentedRepresentationPasses": int(phase_pass_total),
        "flipCounts": dict(flips),
        "diagnostics": diagnostics,
        "heldoutLabelsUsedForRepresentationDiagnostic": True,
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 71,
        "bottleneckPhases": list(BOTTLENECK_PHASES),
        "baseRepresentationPasses": int(base_pass_total),
        "phaseAugmentedRepresentationPasses": int(phase_pass_total),
        "flipCounts": dict(flips),
        "modelHyperparametersFrozenPerFoldFromV57": True,
        "heldoutLabelsUsedForRepresentationDiagnostic": True,
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V70 BOTTLENECK REPRESENTATION ABLATION V71 COMPLETE")
    print("Base representation passes:", base_pass_total, "/ 15")
    print("Phase-augmented representation passes:", phase_pass_total, "/ 15")
    print("Flip counts:", dict(flips))
    for d in diagnostics:
        if d["flipClass"] not in ("both-pass", "both-fail"):
            print("Flip", d["phase"], "fold", d["fold"], "=>", d["flipClass"],
                  "baseLift", d["baseRepresentation"]["heldoutPrecisionLift"],
                  "phaseLift", d["phaseAugmentedRepresentation"]["heldoutPrecisionLift"])
    print("Diagnostic outcomes tainted for selection: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
