from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import profile_gomyway_3676_patch_rhythm24_v87_old_tight_radius2_counterfactual_v88 as v88

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v94-safe-broad-r8-l1-exposed-support-v95.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v94-safe-broad-r8-l1-exposed-support-v95-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(old_q: float) -> str:
    if abs(old_q - v88.TIGHT_Q) < 1e-12:
        return "tight"
    if abs(old_q - v88.BROAD_Q) < 1e-12:
        return "broad"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text())
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

    signature_rows = []
    all_safe_broad_rows = []

    for source_name, source_path in SOURCES.items():
        src = json.loads(source_path.read_text())
        phase_passes = []
        source_rows = []

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
            folds = {int(r["fold"]): r for r in scheme.get("folds") or []}
            passes = 0

            for fold in range(OUTER_FOLDS):
                row = folds[fold]
                train = ids != fold
                test = ~train
                v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
                old_q = float(row.get("outerQ", v88.ANCHOR_Q))
                old_bucket = bucket(old_q)
                q, decision = v88.selected_q(row)
                safe_broad = old_bucket == "broad" and decision == "keep-broad-low-dispersion"

                if not safe_broad:
                    continue

                selector = row.get("selector") or {}
                cm = row.get("chosenModel") or {}
                radius = cm.get("pairRadius")
                lam = cm.get("lambda")
                if radius is None or lam is None:
                    chosen = v5.choose_model(x_full[train], y[train], measures[train])
                    radius = int(chosen["pairRadius"])
                    lam = float(chosen["lambda"])
                else:
                    radius = int(radius)
                    lam = float(lam)

                model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                v90_pass, _ = v88.pass_at_q(v2.scores_for(x_cos[test], model), y[test], q)
                passes += int(v90_pass)

                rec = {
                    "source": source_name,
                    "phase": phase,
                    "fold": fold,
                    "v90Passed": bool(v90_pass),
                    "v28Passed": bool(v28_pass),
                    "pairRadius": radius,
                    "lambda": lam,
                    "selectionReason": selector.get("selectionReason"),
                    "strictBroadSupportCount": selector.get("strictBroadSupportCount"),
                    "unanimousTightEscape": selector.get("unanimousTightEscape"),
                    "isV93RegressionSignature": bool(radius == 8 and abs(lam - 1.0) < 1e-12),
                }
                source_rows.append(rec)
                all_safe_broad_rows.append(rec)
                if rec["isV93RegressionSignature"]:
                    signature_rows.append(rec)

            phase_passes.append({"phase": phase, "passesAmongSafeBroad": passes})

    def summarize(items):
        return {
            "rows": len(items),
            "v90Passes": sum(int(r["v90Passed"]) for r in items),
            "v28Passes": sum(int(r["v28Passed"]) for r in items),
            "rescuesVsV28": sum(int(r["v90Passed"] and not r["v28Passed"]) for r in items),
            "regressionsVsV28": sum(int(r["v28Passed"] and not r["v90Passed"]) for r in items),
            "bothPass": sum(int(r["v90Passed"] and r["v28Passed"]) for r in items),
            "bothFail": sum(int((not r["v90Passed"]) and (not r["v28Passed"])) for r in items),
            "bySource": dict(Counter(r["source"] for r in items)),
        }

    safe_summary = summarize(all_safe_broad_rows)
    signature_summary = summarize(signature_rows)
    other_summary = summarize([r for r in all_safe_broad_rows if not r["isV93RegressionSignature"]])

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V95")

    out = {
        "schemaVersion": 95,
        "profileType": "v93-regression-signature-independent-exposed-support-diagnostic",
        "hypothesisFromOpenedV93": "safe-broad keep-broad-low-dispersion with pairRadius=8 and lambda=1.0",
        "allSafeBroad": safe_summary,
        "v93RegressionSignatureOnPreviouslyExposedV56V57": signature_summary,
        "otherSafeBroad": other_summary,
        "signatureRows": signature_rows,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v93OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 95,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "allSafeBroad": safe_summary,
        "v93RegressionSignatureOnPreviouslyExposedV56V57": signature_summary,
        "otherSafeBroad": other_summary,
        "usesOnlyPreviouslyExposedV56V57Families": True,
        "v93OpenedConfirmationUsedForOutcomeSelection": False,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n")

    print("GOMYWAY V95 V93 REGRESSION-SIGNATURE EXPOSED SUPPORT DIAGNOSTIC COMPLETE")
    print("All safe-broad:", safe_summary)
    print("V93 regression signature on exposed V56/V57:", signature_summary)
    print("Other safe-broad:", other_summary)
    print("Signature rows:")
    for r in signature_rows:
        print("SignatureRow:", r)
    print("Previously exposed V56/V57 only: True")
    print("V93 opened confirmation used for outcome selection: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")


if __name__ == "__main__":
    main()
