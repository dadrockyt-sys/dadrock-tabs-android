from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V38_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-exact-anchor-unanimous-training-tighten-v38.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v38-training-support-map-v39.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v38-training-support-map-v39-manifest.json"
ANCHOR_Q = 0.20
SCHEMES = ("normal", "section", "shiftedWindow")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(V38_PATH.read_text(encoding="utf-8"))

    rows: list[dict[str, Any]] = []
    support_count_hist = {"0": 0, "1": 0, "2": 0, "3": 0}
    scheme_support = {s: 0 for s in SCHEMES}
    scheme_values = {s: [] for s in SCHEMES}
    pair_support = {"normal+section": 0, "normal+shiftedWindow": 0, "section+shiftedWindow": 0}
    all_three = 0

    for phase_block in payload.get("schemes", []):
        phase = float(phase_block["phase"])
        for fold_row in phase_block.get("folds", []):
            cal = fold_row["trainingOnlyCalibration"]
            medians = {}
            for scheme_row in cal.get("schemes", []):
                name = str(scheme_row["scheme"])
                val = scheme_row.get("medianWidestPassingFraction")
                medians[name] = None if val is None else float(val)

            support = {s: bool(medians.get(s) is not None and medians[s] < ANCHOR_Q) for s in SCHEMES}
            count = int(sum(int(v) for v in support.values()))
            support_count_hist[str(count)] += 1
            for s in SCHEMES:
                if support[s]:
                    scheme_support[s] += 1
                if medians.get(s) is not None:
                    scheme_values[s].append(float(medians[s]))
            if support["normal"] and support["section"]:
                pair_support["normal+section"] += 1
            if support["normal"] and support["shiftedWindow"]:
                pair_support["normal+shiftedWindow"] += 1
            if support["section"] and support["shiftedWindow"]:
                pair_support["section+shiftedWindow"] += 1
            if count == 3:
                all_three += 1

            rows.append({
                "phase": phase,
                "fold": int(fold_row["fold"]),
                "schemeMedianWidestPassingFractions": medians,
                "schemeSupportsTighteningBelowAnchor": support,
                "supportingSchemeCount": count,
                "v38Passed": bool(fold_row["passed"]),
                "v28Passed": bool(fold_row["v28Comparison"]["passed"]),
            })

    summaries = {}
    for s in SCHEMES:
        vals = np.asarray(scheme_values[s], dtype=np.float64)
        summaries[s] = {
            "count": int(vals.size),
            "min": float(np.min(vals)) if vals.size else None,
            "median": float(np.median(vals)) if vals.size else None,
            "max": float(np.max(vals)) if vals.size else None,
            "belowAnchorCount": int(scheme_support[s]),
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V39")

    output = {
        "schemaVersion": 39,
        "profileType": "36.76-rhythm24-v38-training-support-map",
        "diagnosticScope": "training-only-calibration-records-from-already-exposed-V38-run",
        "source": str(V38_PATH.relative_to(ROOT)),
        "anchorQ": ANCHOR_Q,
        "supportingSchemeCountHistogram": support_count_hist,
        "schemeSupportCounts": scheme_support,
        "pairSupportCounts": pair_support,
        "allThreeSupportCount": int(all_three),
        "schemeMedianSummaries": summaries,
        "rows": rows,
        "reservedUntouchedPhasesConsumed": False,
        "heldoutLabelsUsedForNewTuning": False,
        "newTuningPerformed": False,
        "qSearchPerformed": False,
        "calibrationParameterSearchPerformed": False,
        "requiresTrainingOnlyEvidenceForNextChallenger": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 39,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "supportingSchemeCountHistogram": support_count_hist,
        "schemeSupportCounts": scheme_support,
        "pairSupportCounts": pair_support,
        "allThreeSupportCount": int(all_three),
        "reservedUntouchedPhasesConsumed": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V38 TRAINING SUPPORT MAP V39 COMPLETE")
    print("Supporting scheme count histogram:", support_count_hist)
    print("Scheme support counts:", scheme_support)
    print("Pair support counts:", pair_support)
    print("All three support count:", all_three)
    print("Scheme median summaries:", summaries)
    print("Reserved untouched phases consumed: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
