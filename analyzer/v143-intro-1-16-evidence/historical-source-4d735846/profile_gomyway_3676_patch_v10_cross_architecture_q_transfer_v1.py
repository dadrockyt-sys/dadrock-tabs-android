from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V10_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-cross-architecture-q-transfer-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-cross-architecture-q-transfer-v1-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % OUTER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def grade(scores: np.ndarray, y: np.ndarray, q: float) -> dict[str, Any]:
    held = v1.select_top_fraction(scores, y, float(q))
    base = v1.base_stats(y)
    lift = float(held["precision"]) - float(base["precision"])
    passed = int(held["true"]) > 0 and lift >= 5.0
    return {
        "q": float(q),
        "true": int(held["true"]),
        "false": int(held["false"]),
        "selectedPct": held["selectedPct"],
        "precision": held["precision"],
        "basePrecision": base["precision"],
        "lift": round(lift, 2),
        "passed": bool(passed),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")
    slots = list(source.get("candidateSlots") or [])
    if not slots:
        raise RuntimeError("candidateSlots missing")

    payload = json.loads(V10_PATH.read_text(encoding="utf-8"))
    feature_names = sorted((slots[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in slots],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)

    policies = ("v9Q", "minQ", "maxQ")
    records: list[dict[str, Any]] = []

    for scheme in ("normal", "section", "shiftedWindow"):
        ids = scheme_ids(measures, scheme)
        for row in list(payload.get(scheme) or []):
            fold = int(row["fold"])
            baseline_passed = bool(row["passed"])
            architecture = str(row["architectureChosen"])
            rec: dict[str, Any] = {
                "scheme": scheme,
                "fold": fold,
                "v10Architecture": architecture,
                "v10Passed": baseline_passed,
                "v10Lift": float(row.get("heldoutPrecisionLift", 0.0)),
            }

            # V9-selected folds remain exactly as V10. This diagnostic is only asking
            # whether V9's independently trained calibration can improve the V5 branch.
            if architecture != "v5":
                rec["eligibleV5Branch"] = False
                for p in policies:
                    rec[p] = {
                        "q": float(row["tailQuantile"]),
                        "passed": baseline_passed,
                        "lift": float(row.get("heldoutPrecisionLift", 0.0)),
                        "unchangedV9Branch": True,
                    }
                records.append(rec)
                continue

            rec["eligibleV5Branch"] = True
            test = ids == fold
            train = ~test
            v5_choice = dict(row["v5Choice"])
            v9_choice = dict(row["v9Choice"])
            v5_q = float(v5_choice["tailQuantile"])
            v9_q = float(v9_choice["tailQuantile"])

            model = v2.fit_pairwise_ranker(
                x[train], y[train], measures[train],
                int(v5_choice["pairRadius"]), float(v5_choice["lambda"]),
            )
            scores = v2.scores_for(x[test], model)

            rec["v5Q"] = v5_q
            rec["v9Q"] = v9_q
            rec["v5InnerSectionPass"] = int(v5_choice["sectionPassCount"])
            rec["v9InnerSectionPass"] = int(v9_choice["sectionPassCount"])
            rec["baselineRecomputed"] = grade(scores, y[test], v5_q)
            rec["v9Q"] = grade(scores, y[test], v9_q)
            rec["minQ"] = grade(scores, y[test], min(v5_q, v9_q))
            rec["maxQ"] = grade(scores, y[test], max(v5_q, v9_q))
            records.append(rec)
            print("TRANSFER", rec, flush=True)

    summary: dict[str, Any] = {
        "v10Passes": sum(bool(r["v10Passed"]) for r in records),
        "v10Total": len(records),
        "v5BranchFolds": sum(bool(r.get("eligibleV5Branch")) for r in records),
        "v9BranchFolds": sum(not bool(r.get("eligibleV5Branch")) for r in records),
        "policies": {},
    }

    supported: list[str] = []
    for p in policies:
        passes = sum(bool(r[p]["passed"]) for r in records)
        rescues = [
            {"scheme": r["scheme"], "fold": r["fold"]}
            for r in records if (not bool(r["v10Passed"])) and bool(r[p]["passed"])
        ]
        losses = [
            {"scheme": r["scheme"], "fold": r["fold"]}
            for r in records if bool(r["v10Passed"]) and (not bool(r[p]["passed"]))
        ]
        unchanged = sum(bool(r["v10Passed"]) == bool(r[p]["passed"]) for r in records)
        info = {
            "passes": passes,
            "rescues": rescues,
            "collateralLosses": losses,
            "unchangedFolds": unchanged,
            "strictlyBeatsV10": passes > int(summary["v10Passes"]),
            "noCollateralLosses": len(losses) == 0,
        }
        summary["policies"][p] = info
        if info["strictlyBeatsV10"] and info["noCollateralLosses"] and rescues:
            supported.append(p)

    summary["supportedPolicies"] = supported
    summary["crossArchitectureQTransferSignalReady"] = bool(supported)
    summary["nextTarget"] = (
        "lock-simplest-supported-q-transfer-rule-into-fresh-strict-nested-cv"
        if supported else
        "retire-cross-architecture-q-transfer-and-pivot-residual-strategy"
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during q-transfer diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-cross-architecture-q-transfer-diagnostic",
        "importantCaveat": "Outer labels grade fixed predeclared q-transfer policies only. Any supported policy must be locked before a fresh strict nested benchmark; this diagnostic itself is not promotable.",
        "summary": summary,
        "records": records,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseTransferQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "supportedPolicies": supported,
        "crossArchitectureQTransferSignalReady": bool(supported),
        "nextTarget": summary["nextTarget"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 CROSS-ARCHITECTURE Q TRANSFER V1 COMPLETE")
    print("V10 passes:", summary["v10Passes"], "/", summary["v10Total"])
    for p in policies:
        s = summary["policies"][p]
        print(p, "passes:", s["passes"], "rescues:", s["rescues"], "collateralLosses:", s["collateralLosses"])
    print("Supported policies:", supported)
    print("Cross-architecture q-transfer signal ready:", bool(supported))
    print("Next target:", summary["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose transfer q: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
