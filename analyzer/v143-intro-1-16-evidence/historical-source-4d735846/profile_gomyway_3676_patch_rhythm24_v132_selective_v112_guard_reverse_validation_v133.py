from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import profile_gomyway_3676_patch_rhythm24_v79_cosine_dual_dispersion_combined_v80 as v80
import profile_gomyway_3676_patch_rhythm24_v111_lowband_phase_interaction_augmentation_v112 as v112

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
V122_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v121-structural-representation-utility-v122.json"
V128_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
V131_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v130-structural-representation-utility-v131.json"
V132_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v131-neutral-intervention-selectivity-v132.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v132-selective-v112-guard-reverse-validation-v133.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v132-selective-v112-guard-reverse-validation-v133-manifest.json"

OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
TARGET = ("anchor", "keep-anchor", 4, 1.0)
TARGET_REP = "v112_interactions"
GATE_THRESHOLD = -5.4
PHASE_THRESHOLD = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structural_key(row: dict) -> tuple[str, str, int, float]:
    model = row.get("chosenModel") or {}
    return (
        str(row.get("originalQBucket")),
        str(row.get("v96Decision")),
        int(model.get("pairRadius")),
        float(model.get("lambda")),
    )


def dangerous_v118_exclusion(row: dict) -> bool:
    return bool(
        bool(row.get("selectedForV112"))
        and structural_key(row) == ("tight", "revert-tight-to-anchor-low-dispersion", 8, 1.0)
    )


def phasecol3_selected_guard(row: dict, rep: str | None) -> bool:
    return bool(
        rep == "phase_col3"
        and structural_key(row) == ("tight", "revert-tight-to-anchor-low-dispersion", 4, 1.0)
        and bool(row.get("selectedForV112"))
    )


def load_policy(v122: dict) -> dict:
    policy = {}
    for row in v122.get("positiveBestPerStructuralGroup") or []:
        key = (
            str(row.get("originalQBucket")),
            str(row.get("v96Decision")),
            int(row.get("pairRadius")),
            float(row.get("lambda")),
        )
        policy[key] = str(row.get("representation"))
    if not policy:
        raise RuntimeError("V122 has no frozen structural policy")
    if policy.get(TARGET) != "cosine":
        raise RuntimeError(f"Expected frozen V122 target representation cosine, got {policy.get(TARGET)}")
    return policy


def guard_match(row: dict, mode: str) -> bool:
    if structural_key(row) != TARGET:
        return False
    gate = row.get("gateScore")
    phase = float(row.get("phase"))
    if mode == "gate":
        return gate is not None and float(gate) <= GATE_THRESHOLD
    if mode == "phase":
        return phase < PHASE_THRESHOLD
    if mode == "conjunction":
        return gate is not None and float(gate) <= GATE_THRESHOLD and phase < PHASE_THRESHOLD
    raise ValueError(mode)


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))
    v122 = json.loads(V122_PATH.read_text(encoding="utf-8"))
    v128 = json.loads(V128_PATH.read_text(encoding="utf-8"))
    v131 = json.loads(V131_PATH.read_text(encoding="utf-8"))
    v132 = json.loads(V132_PATH.read_text(encoding="utf-8"))
    if int(v116.get("schemaVersion", -1)) != 116:
        raise RuntimeError("V116 result required")
    if int(v122.get("schemaVersion", -1)) != 122:
        raise RuntimeError("V122 structural policy required")
    if int(v128.get("schemaVersion", -1)) != 128 or not bool(v128.get("validatedNewChampion")):
        raise RuntimeError("Validated V128 champion required")
    if int(v128.get("v128Passes", -1)) != 309:
        raise RuntimeError("V128 must be frozen 309/320 champion")
    if int(v131.get("schemaVersion", -1)) != 131 or int(v132.get("schemaVersion", -1)) != 132:
        raise RuntimeError("V131/V132 diagnostics required")

    policy = load_policy(v122)
    modes = ("gate", "phase", "conjunction")

    # Locate the already-computed V131 candidate outcomes on consumed V128.
    v128_lookup = {}
    for scheme in v128.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            v128_lookup[(round(phase, 12), int(r.get("fold")))] = r

    target_rows = []
    for rr in v131.get("rowResults") or []:
        sk = rr.get("structuralKey") or {}
        key = (str(sk.get("originalQBucket")), str(sk.get("v96Decision")), int(sk.get("pairRadius")), float(sk.get("lambda")))
        if key != TARGET:
            continue
        cand = (rr.get("candidateRepresentations") or {}).get(TARGET_REP)
        if cand is None:
            continue
        phase = float(rr.get("phase"))
        fold = int(rr.get("fold"))
        src = dict(v128_lookup.get((round(phase, 12), fold)) or {})
        src.setdefault("phase", phase)
        src.setdefault("fold", fold)
        target_rows.append((src, bool(rr.get("baselineV128Passed")), bool(cand.get("passed"))))
    if not target_rows:
        raise RuntimeError("Could not reconstruct V131 target rows")

    consumed = {}
    for mode in modes:
        passes = 309
        gains = losses = applied = 0
        for row, base, cand in target_rows:
            if not guard_match(row, mode):
                continue
            applied += 1
            passes += int(cand) - int(base)
            gains += int(cand and not base)
            losses += int(base and not cand)
        consumed[mode] = {"passes": passes, "gains": gains, "losses": losses, "net": gains-losses, "appliedRows": applied}

    # Reverse validation on old consumed V116. Reconstruct the frozen V128
    # baseline (V122 policy plus V127 phase_col3 selectedForV112 guard), then
    # apply each V133 candidate selector without using a fresh reserve.
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    names = sorted((source_rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in source_rows], dtype=np.float64)
    pf = np.asarray(v17.phase_features(source_rows), dtype=np.float64)
    interactions, _ = v112.build_phase_interactions(xb, names, pf)
    matrices = {
        "base": xb,
        "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
        "full_phase": np.concatenate([xb, pf], axis=1),
        "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
        "v112_interactions": np.concatenate([xb, pf[:, [1, 3]], interactions], axis=1),
    }
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    rows = []
    for scheme in v116.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V116 rows, got {len(rows)}")

    reverse = {m: {"baselinePasses": 0, "passes": 0, "gains": 0, "losses": 0, "appliedRows": 0} for m in modes}

    print("GOMYWAY V133 SELECTIVE V112-INTERACTIONS GUARD REVERSE VALIDATION", flush=True)
    print(f"Target={TARGET} rep={TARGET_REP} gate<={GATE_THRESHOLD} phase<{PHASE_THRESHOLD}", flush=True)
    print("Consumed V128 used for development; V116 used only for reverse validation; fresh reserve untouched", flush=True)

    for idx, r in enumerate(rows, 1):
        key = structural_key(r)
        baseline_v118 = bool(r.get("v96Passed")) if dangerous_v118_exclusion(r) else bool(r.get("v115Passed"))
        rep = policy.get(key)
        phase = float(r["phase"])
        fold = int(r["fold"])
        model_bits = r.get("chosenModel") or {}
        radius = int(model_bits["pairRadius"])
        lam = float(model_bits["lambda"])
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
        train = ids != fold
        test = ids == fold
        old_q = float(r.get("originalTrainingOnlyQ"))
        selector = r.get("selector") or {}
        candidate_q, _, _ = v80.selected_q({"outerQ": old_q, "selector": selector})
        bucket = str(r.get("originalQBucket"))
        decision = str(r.get("v96Decision"))
        q_to_use = candidate_q if bucket == "tight" else ANCHOR_Q
        if bucket == "broad" and decision == "keep-broad-low-dispersion":
            q_to_use = candidate_q

        if rep is None:
            v122_pass = baseline_v118
        else:
            x = matrices[rep]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            v122_pass, _, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            v122_pass = bool(v122_pass)

        v128_base = baseline_v118 if phasecol3_selected_guard(r, rep) else v122_pass

        # Only fit the alternative v112-interactions candidate when this is the
        # target structural group and at least one selector would apply.
        alt_pass = v128_base
        if key == TARGET and any(guard_match(r, m) for m in modes):
            x = matrices[TARGET_REP]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            alt_pass, _, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            alt_pass = bool(alt_pass)

        for mode in modes:
            s = reverse[mode]
            s["baselinePasses"] += int(v128_base)
            final = alt_pass if guard_match(r, mode) else v128_base
            s["passes"] += int(final)
            s["appliedRows"] += int(guard_match(r, mode))
            s["gains"] += int(final and not v128_base)
            s["losses"] += int(v128_base and not final)

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    for mode in modes:
        reverse[mode]["net"] = reverse[mode]["gains"] - reverse[mode]["losses"]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V133")

    out = {
        "schemaVersion": 133,
        "profileType": "selective-v112-interactions-consumed-development-plus-v116-reverse-validation",
        "targetStructuralKey": {"originalQBucket": TARGET[0], "v96Decision": TARGET[1], "pairRadius": TARGET[2], "lambda": TARGET[3]},
        "targetRepresentation": TARGET_REP,
        "candidateSelectors": {
            "gate": f"gateScore <= {GATE_THRESHOLD}",
            "phase": f"phase < {PHASE_THRESHOLD}",
            "conjunction": f"gateScore <= {GATE_THRESHOLD} AND phase < {PHASE_THRESHOLD}",
        },
        "consumedV128Development": consumed,
        "v116ReverseValidation": reverse,
        "v132MotivatedSelectorsFromConsumedOutcomes": True,
        "noSelectorChosenByV133": True,
        "reverseValidationIsCorroborativeNotFreshConfirmation": True,
        "newReservedPhaseFamilyReferenced": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V133 COMPLETE")
    for mode in modes:
        c = consumed[mode]
        r = reverse[mode]
        print(f"{mode}: consumed V128 309/320 -> {c['passes']}/320 +{c['gains']}/-{c['losses']} net={c['net']:+d} applied={c['appliedRows']}")
        print(f"{mode}: reverse V116 {r['baselinePasses']}/320 -> {r['passes']}/320 +{r['gains']}/-{r['losses']} net={r['net']:+d} applied={r['appliedRows']}")
    print("No selector chosen by V133: True")
    print("New reserved phase family referenced: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
