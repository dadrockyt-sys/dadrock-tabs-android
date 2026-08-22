from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v61-tight-dispersion-gate-counterfactual-v62.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v61-tight-dispersion-gate-counterfactual-v62-manifest.json"

TIGHT_Q = 0.175
ANCHOR_Q = 0.20
STD_GATE = 0.50


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tight_std(selector: dict[str, Any]) -> float | None:
    vals = []
    for s in selector.get("schemes") or []:
        if "meanTightLift" not in s or "meanAnchorLift" not in s:
            return None
        vals.append(float(s["meanTightLift"]) - float(s["meanAnchorLift"]))
    if len(vals) < 2:
        return None
    return float(statistics.pstdev(vals))


def evaluate_source(name: str, path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    src = json.loads(path.read_text(encoding="utf-8"))
    total = v28_total = rescues = regressions = 0
    tight_kept = tight_reverted = 0
    phase_rows = []
    changed = []

    for phase in src.get("schemes") or []:
        pp = pv = 0
        phase_changed = []
        for row in phase.get("folds") or []:
            current_pass = bool(row.get("passed"))
            v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
            q = float(row.get("outerQ", ANCHOR_Q))
            selector = row.get("selector") or {}
            new_pass = current_pass
            decision = "keep-current"
            std = None

            if abs(q - TIGHT_Q) < 1e-12:
                std = tight_std(selector)
                if std is None:
                    raise RuntimeError(f"Missing tight dispersion inputs in {name}")
                if std >= STD_GATE:
                    tight_kept += 1
                    decision = "keep-tight-high-dispersion"
                else:
                    tight_reverted += 1
                    decision = "revert-tight-to-anchor-low-dispersion"
                    new_pass = v28_pass

            pp += int(new_pass)
            pv += int(v28_pass)
            rescues += int(new_pass and not v28_pass)
            regressions += int(v28_pass and not new_pass)
            total += int(new_pass)
            v28_total += int(v28_pass)

            if new_pass != current_pass:
                item = {
                    "phase": float(phase["phase"]), "fold": int(row.get("fold", -1)),
                    "oldPass": current_pass, "newPass": new_pass, "v28Pass": v28_pass,
                    "tightLiftDeltaStd": std, "decision": decision,
                }
                changed.append(item)
                phase_changed.append(item)

        phase_rows.append({
            "phase": float(phase["phase"]), "passes": pp, "v28Passes": pv,
            "changedRows": phase_changed,
        })

    min_phase = min(r["passes"] for r in phase_rows)
    bottlenecks = [r for r in phase_rows if r["passes"] == min_phase]
    return {
        "source": name,
        "foldsPassed": total,
        "foldsTotal": sum(len(p.get("folds") or []) for p in src.get("schemes") or []),
        "v28ComparisonPasses": v28_total,
        "minimumPhasePasses": min_phase,
        "rescuesVsV28": rescues,
        "regressionsVsV28": regressions,
        "tightKeptByDispersionGate": tight_kept,
        "tightRevertedToAnchor": tight_reverted,
        "changedOutcomeCountVsSource": len(changed),
        "changedOutcomesVsSource": changed,
        "bottleneckPhases": bottlenecks,
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    results = [evaluate_source(name, path) for name, path in SOURCES.items()]
    combined = {
        "foldsPassed": sum(r["foldsPassed"] for r in results),
        "foldsTotal": sum(r["foldsTotal"] for r in results),
        "v28ComparisonPasses": sum(r["v28ComparisonPasses"] for r in results),
        "rescuesVsV28": sum(r["rescuesVsV28"] for r in results),
        "regressionsVsV28": sum(r["regressionsVsV28"] for r in results),
        "minimumPhasePassesAcrossSources": min(r["minimumPhasePasses"] for r in results),
        "tightKeptByDispersionGate": sum(r["tightKeptByDispersionGate"] for r in results),
        "tightRevertedToAnchor": sum(r["tightRevertedToAnchor"] for r in results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V62")

    out = {
        "schemaVersion": 62,
        "profileType": "v61-tight-dispersion-gate-counterfactual",
        "fixedTightLiftDeltaStdGate": STD_GATE,
        "gateMeaning": "keep q=0.175 only when cross-scheme std of mean tight-minus-anchor lift is >= 0.50; otherwise revert that fold to frozen q=0.20 anchor",
        "thresholdChosenFromExposedV61Diagnostic": True,
        "diagnosticOnly": True,
        "results": results,
        "combined": combined,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 62,
        "fixedTightLiftDeltaStdGate": STD_GATE,
        "results": [{k: r[k] for k in ["source","foldsPassed","foldsTotal","v28ComparisonPasses","minimumPhasePasses","rescuesVsV28","regressionsVsV28","tightKeptByDispersionGate","tightRevertedToAnchor","changedOutcomeCountVsSource"]} for r in results],
        "combined": combined,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V61 TIGHT-DISPERSION GATE COUNTERFACTUAL V62 COMPLETE")
    print("Fixed tight dispersion gate:", STD_GATE)
    for r in results:
        print(r["source"], "passes", r["foldsPassed"], "/", r["foldsTotal"],
              "V28", r["v28ComparisonPasses"],
              "min", r["minimumPhasePasses"],
              "rescues", r["rescuesVsV28"],
              "regressions", r["regressionsVsV28"],
              "tight-kept", r["tightKeptByDispersionGate"],
              "tight-reverted", r["tightRevertedToAnchor"])
        print("  Bottleneck phases:", [x["phase"] for x in r["bottleneckPhases"]])
    print("Combined:", combined)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
