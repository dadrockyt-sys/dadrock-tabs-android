from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V81_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v80-flip-and-floor-anatomy-v81.json"
SOURCES = {
    "v56_exposed_120": PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json",
    "v57_exposed_160": PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json",
}
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v82-old-tight-guarded-v80-summary-v83.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v82-old-tight-guarded-v80-summary-v83-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def baseline_pass(row: dict) -> bool:
    return bool((row.get("v28Comparison") or {}).get("passed"))


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v81 = json.loads(V81_PATH.read_text(encoding="utf-8"))
    if int(v81.get("schemaVersion", -1)) != 81:
        raise RuntimeError("V81 output missing or wrong schema")

    changed = list(v81.get("changedRows") or [])
    # Freeze the simplest strongest zero-regression V82 guard: use V80 only on folds
    # whose original exposed selector branch was tight; otherwise fall back to V28.
    # This architecture is explicitly tainted by exposed V82 outcomes and therefore
    # requires fresh untouched confirmation before any validation claim.
    changed_map = {
        (str(r["source"]), float(r["phase"]), int(r["fold"])): r
        for r in changed
    }

    per_source = []
    combined_passes = combined_base = combined_rescues = combined_regressions = 0

    for source_name, path in SOURCES.items():
        src = json.loads(path.read_text(encoding="utf-8"))
        phase_counts: dict[float, list[int]] = defaultdict(lambda: [0, 0])
        passes = base_passes = rescues = regressions = folds_total = guarded_v80_count = 0

        for scheme in src.get("schemes") or []:
            phase = float(scheme["phase"])
            for row in scheme.get("folds") or []:
                fold = int(row["fold"])
                base = baseline_pass(row)
                key = (source_name, phase, fold)
                ch = changed_map.get(key)

                use_v80 = bool(ch is not None and ch.get("oldQBucket") == "tight")
                if use_v80:
                    final_pass = bool(ch.get("passed"))
                    guarded_v80_count += 1
                else:
                    final_pass = base

                passes += int(final_pass)
                base_passes += int(base)
                rescues += int(final_pass and not base)
                regressions += int(base and not final_pass)
                folds_total += 1
                phase_counts[phase][0] += int(final_pass)
                phase_counts[phase][1] += int(base)

        phase_rows = [
            {"phase": p, "guardedPasses": vals[0], "v28Passes": vals[1]}
            for p, vals in sorted(phase_counts.items())
        ]
        minimum = min(r["guardedPasses"] for r in phase_rows)
        bottlenecks = [r["phase"] for r in phase_rows if r["guardedPasses"] == minimum]

        result = {
            "source": source_name,
            "foldsPassed": passes,
            "foldsTotal": folds_total,
            "v28ComparisonPasses": base_passes,
            "rescuesVsV28": rescues,
            "regressionsVsV28": regressions,
            "minimumPhasePasses": minimum,
            "bottleneckPhases": bottlenecks,
            "guardedV80ChangedFoldsApplied": guarded_v80_count,
            "phaseRows": phase_rows,
        }
        per_source.append(result)
        combined_passes += passes
        combined_base += base_passes
        combined_rescues += rescues
        combined_regressions += regressions

    combined = {
        "foldsPassed": combined_passes,
        "foldsTotal": sum(r["foldsTotal"] for r in per_source),
        "v28ComparisonPasses": combined_base,
        "rescuesVsV28": combined_rescues,
        "regressionsVsV28": combined_regressions,
        "minimumPhasePassesAcrossSources": min(r["minimumPhasePasses"] for r in per_source),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V83")

    out = {
        "schemaVersion": 83,
        "profileType": "v82-old-tight-guarded-v80-exposed-family-summary",
        "guard": "apply-v80-only-when-original-oldQBucket-is-tight-else-v28",
        "guardSelectedFromExposedV82Outcomes": True,
        "results": per_source,
        "combined": combined,
        "requiresFreshUntouchedConfirmation": True,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "guard", "guardSelectedFromExposedV82Outcomes", "combined",
        "requiresFreshUntouchedConfirmation", "diagnosticOutcomesTaintedForSelection",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "validatedNewChampion", "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V83 OLD-TIGHT GUARDED V80 SUMMARY COMPLETE")
    for r in per_source:
        print(r["source"], "passes", r["foldsPassed"], "/", r["foldsTotal"],
              "V28", r["v28ComparisonPasses"], "rescues", r["rescuesVsV28"],
              "regressions", r["regressionsVsV28"], "min", r["minimumPhasePasses"],
              "bottlenecks", r["bottleneckPhases"], "guarded-changed", r["guardedV80ChangedFoldsApplied"])
    print("Combined:", combined)
    print("Requires fresh untouched confirmation: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
