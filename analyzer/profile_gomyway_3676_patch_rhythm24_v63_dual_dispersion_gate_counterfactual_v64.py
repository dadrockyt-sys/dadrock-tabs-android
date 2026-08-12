from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v63-dual-dispersion-gate-counterfactual-v64.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v63-dual-dispersion-gate-counterfactual-v64-manifest.json"

TIGHT_Q = 0.175
ANCHOR_Q = 0.20
BROAD_Q = 0.225
TIGHT_STD_MIN = 0.50
BROAD_STD_MAX = 0.90


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lift_std(selector: dict[str, Any], side: str) -> float | None:
    vals = []
    for s in selector.get("schemes") or []:
        anchor = s.get("meanAnchorLift")
        other = s.get("meanTightLift") if side == "tight" else s.get("meanBroadLift")
        if anchor is None or other is None:
            return None
        vals.append(float(other) - float(anchor))
    if len(vals) < 2:
        return None
    return float(statistics.pstdev(vals))


def evaluate_source(name: str, path: Path) -> dict[str, Any]:
    src = json.loads(path.read_text(encoding="utf-8"))
    total = v28_total = rescues = regressions = 0
    tight_kept = tight_reverted = broad_kept = broad_reverted = 0
    changed = []
    phase_rows = []

    for phase in src.get("schemes") or []:
        pp = pv = 0
        phase_changed = []
        for row in phase.get("folds") or []:
            old_pass = bool(row.get("passed"))
            v28_pass = bool((row.get("v28Comparison") or {}).get("passed"))
            q = float(row.get("outerQ", ANCHOR_Q))
            selector = row.get("selector") or {}
            new_pass = old_pass
            decision = "keep-current"
            std = None

            if abs(q - TIGHT_Q) < 1e-12:
                std = lift_std(selector, "tight")
                if std is None:
                    raise RuntimeError(f"Missing tight dispersion inputs in {name}")
                if std >= TIGHT_STD_MIN:
                    tight_kept += 1
                    decision = "keep-tight-high-dispersion"
                else:
                    tight_reverted += 1
                    decision = "revert-tight-to-anchor-low-dispersion"
                    new_pass = v28_pass

            elif abs(q - BROAD_Q) < 1e-12:
                std = lift_std(selector, "broad")
                if std is None:
                    raise RuntimeError(f"Missing broad dispersion inputs in {name}")
                if std <= BROAD_STD_MAX:
                    broad_kept += 1
                    decision = "keep-broad-low-dispersion"
                else:
                    broad_reverted += 1
                    decision = "revert-broad-to-anchor-high-dispersion"
                    new_pass = v28_pass

            pp += int(new_pass)
            pv += int(v28_pass)
            total += int(new_pass)
            v28_total += int(v28_pass)
            rescues += int(new_pass and not v28_pass)
            regressions += int(v28_pass and not new_pass)

            if new_pass != old_pass:
                item = {
                    "phase": float(phase["phase"]),
                    "fold": int(row.get("fold", -1)),
                    "oldPass": old_pass,
                    "newPass": new_pass,
                    "v28Pass": v28_pass,
                    "oldQ": q,
                    "dispersion": std,
                    "decision": decision,
                }
                changed.append(item)
                phase_changed.append(item)

        phase_rows.append({
            "phase": float(phase["phase"]),
            "passes": pp,
            "v28Passes": pv,
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
        "tightKept": tight_kept,
        "tightReverted": tight_reverted,
        "broadKept": broad_kept,
        "broadReverted": broad_reverted,
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
        "tightKept": sum(r["tightKept"] for r in results),
        "tightReverted": sum(r["tightReverted"] for r in results),
        "broadKept": sum(r["broadKept"] for r in results),
        "broadReverted": sum(r["broadReverted"] for r in results),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V64")

    out = {
        "schemaVersion": 64,
        "profileType": "v63-dual-dispersion-gate-counterfactual",
        "fixedTightLiftDeltaStdMinimum": TIGHT_STD_MIN,
        "fixedBroadLiftDeltaStdMaximum": BROAD_STD_MAX,
        "gateMeaning": "keep tight only for std>=0.50; keep broad only for std<=0.90; otherwise revert to frozen q=0.20 anchor",
        "thresholdsChosenFromExposedDiagnostics": True,
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
        "schemaVersion": 64,
        "fixedTightLiftDeltaStdMinimum": TIGHT_STD_MIN,
        "fixedBroadLiftDeltaStdMaximum": BROAD_STD_MAX,
        "results": [{k: r[k] for k in ["source","foldsPassed","foldsTotal","v28ComparisonPasses","minimumPhasePasses","rescuesVsV28","regressionsVsV28","tightKept","tightReverted","broadKept","broadReverted","changedOutcomeCountVsSource"]} for r in results],
        "combined": combined,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V63 DUAL-DISPERSION GATE COUNTERFACTUAL V64 COMPLETE")
    print("Fixed tight std minimum:", TIGHT_STD_MIN)
    print("Fixed broad std maximum:", BROAD_STD_MAX)
    for r in results:
        print(r["source"], "passes", r["foldsPassed"], "/", r["foldsTotal"],
              "V28", r["v28ComparisonPasses"], "min", r["minimumPhasePasses"],
              "rescues", r["rescuesVsV28"], "regressions", r["regressionsVsV28"],
              "tight-kept", r["tightKept"], "tight-reverted", r["tightReverted"],
              "broad-kept", r["broadKept"], "broad-reverted", r["broadReverted"])
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
