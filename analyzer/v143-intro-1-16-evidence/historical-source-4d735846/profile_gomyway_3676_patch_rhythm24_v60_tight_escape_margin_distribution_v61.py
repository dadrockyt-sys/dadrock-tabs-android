from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v57-confirmation-failure-map-v58.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v60-tight-escape-margin-distribution-v61.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v60-tight-escape-margin-distribution-v61-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status_from_row(row: dict) -> str:
    return str(row.get("status") or "unknown")


def summarize(values: list[float]) -> dict:
    if not values:
        return {"count": 0, "min": None, "q25": None, "median": None, "q75": None, "max": None, "mean": None}
    a = np.asarray(values, dtype=float)
    return {
        "count": int(len(a)),
        "min": float(np.min(a)),
        "q25": float(np.quantile(a, 0.25)),
        "median": float(np.median(a)),
        "q75": float(np.quantile(a, 0.75)),
        "max": float(np.max(a)),
        "mean": float(np.mean(a)),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(SOURCE_PATH)
    src = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

    groups = defaultdict(lambda: defaultdict(list))
    rows_out = []

    for row in src.get("allRows") or src.get("all_rows") or []:
        selector = row.get("selector") or {}
        if not bool(selector.get("unanimousTightEscape")):
            continue
        schemes = selector.get("schemes") or []
        tight_deltas = [float(s.get("meanTightLift", 0.0)) - float(s.get("meanAnchorLift", 0.0)) for s in schemes]
        broad_deltas = [float(s.get("meanBroadLift", 0.0)) - float(s.get("meanAnchorLift", 0.0)) for s in schemes]
        st = status_from_row(row)
        metrics = {
            "tightMeanLiftDelta": float(np.mean(tight_deltas)) if tight_deltas else 0.0,
            "tightMinLiftDelta": float(np.min(tight_deltas)) if tight_deltas else 0.0,
            "tightMaxLiftDelta": float(np.max(tight_deltas)) if tight_deltas else 0.0,
            "tightLiftDeltaStd": float(np.std(tight_deltas)) if tight_deltas else 0.0,
            "broadMeanLiftDelta": float(np.mean(broad_deltas)) if broad_deltas else 0.0,
            "broadMinLiftDelta": float(np.min(broad_deltas)) if broad_deltas else 0.0,
        }
        for k, v in metrics.items():
            groups[st][k].append(v)
        rows_out.append({
            "phase": row.get("phase"), "fold": row.get("fold"), "status": st,
            **metrics,
            "tightLiftDeltasByScheme": tight_deltas,
            "broadLiftDeltasByScheme": broad_deltas,
        })

    # V58 only persisted changed rows in some early revisions. If allRows is absent,
    # fall back to the full V57 confirmation file so the distribution covers every tight escape.
    if not rows_out:
        v57 = json.loads((PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json").read_text(encoding="utf-8"))
        for phase in v57.get("schemes") or []:
            for row in phase.get("folds") or []:
                selector = row.get("selector") or {}
                if not bool(selector.get("unanimousTightEscape")):
                    continue
                p = bool(row.get("passed")); vp = bool((row.get("v28Comparison") or {}).get("passed"))
                st = "bothPass" if p and vp else "rescue" if p and not vp else "regression" if (not p and vp) else "bothFail"
                schemes = selector.get("schemes") or []
                tight_deltas = [float(s.get("meanTightLift", 0.0)) - float(s.get("meanAnchorLift", 0.0)) for s in schemes]
                broad_deltas = [float(s.get("meanBroadLift", 0.0)) - float(s.get("meanAnchorLift", 0.0)) for s in schemes]
                metrics = {
                    "tightMeanLiftDelta": float(np.mean(tight_deltas)),
                    "tightMinLiftDelta": float(np.min(tight_deltas)),
                    "tightMaxLiftDelta": float(np.max(tight_deltas)),
                    "tightLiftDeltaStd": float(np.std(tight_deltas)),
                    "broadMeanLiftDelta": float(np.mean(broad_deltas)),
                    "broadMinLiftDelta": float(np.min(broad_deltas)),
                }
                for k, v in metrics.items(): groups[st][k].append(v)
                rows_out.append({"phase": float(phase["phase"]), "fold": int(row.get("fold", -1)), "status": st, **metrics,
                                 "tightLiftDeltasByScheme": tight_deltas, "broadLiftDeltasByScheme": broad_deltas})

    summary = {st: {metric: summarize(vals) for metric, vals in metric_map.items()} for st, metric_map in groups.items()}
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V61")

    out = {
        "schemaVersion": 61,
        "profileType": "v60-tight-escape-margin-distribution",
        "tightEscapeRowCount": len(rows_out),
        "summaryByStatus": summary,
        "rows": rows_out,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsDiagnosticOnly": True,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "tightEscapeRowCount", "summaryByStatus",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "protected949CandidateHashUnchanged", "validatedNewChampion", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V60 TIGHT-ESCAPE MARGIN DISTRIBUTION V61 COMPLETE")
    print("Tight-escape row count:", len(rows_out))
    for st in sorted(summary):
        print(f"Status {st}:")
        for metric, stats in summary[st].items():
            print(" ", metric, stats)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
