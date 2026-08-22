from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V81_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v80-flip-and-floor-anatomy-v81.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v81-v80-guard-separability-v82.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v81-v80-guard-separability-v82-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    d = json.loads(V81_PATH.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 81:
        raise RuntimeError("V81 output missing or wrong schema")

    changed = list(d.get("changedRows") or [])
    floors = list(d.get("floorFailureRows") or [])
    if not changed:
        raise RuntimeError("V81 changedRows missing")

    # These are deliberately simple training-side guards. This is diagnostic only:
    # V81 outcomes are already exposed, so any promising guard is tainted and cannot
    # be validated on the same families.
    guards: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
        ("all-v80", lambda r: True),
        ("decision-keep-anchor", lambda r: r.get("v80Decision") == "keep-anchor"),
        ("decision-keep-tight", lambda r: r.get("v80Decision") == "keep-tight-high-dispersion"),
        ("decision-keep-broad", lambda r: r.get("v80Decision") == "keep-broad-low-dispersion"),
        ("decision-revert-tight", lambda r: r.get("v80Decision") == "revert-tight-to-anchor-low-dispersion"),
        ("decision-revert-broad", lambda r: r.get("v80Decision") == "revert-broad-to-anchor-high-dispersion"),
        ("old-anchor", lambda r: r.get("oldQBucket") == "anchor"),
        ("old-tight", lambda r: r.get("oldQBucket") == "tight"),
        ("old-broad", lambda r: r.get("oldQBucket") == "broad"),
        ("strict-support-0", lambda r: int(r.get("strictBroadSupportCount", 0)) == 0),
        ("strict-support-ge1", lambda r: int(r.get("strictBroadSupportCount", 0)) >= 1),
        ("unanimous-tight-true", lambda r: bool(r.get("unanimousTightEscape", False))),
        ("unanimous-tight-false", lambda r: not bool(r.get("unanimousTightEscape", False))),
        ("radius-2", lambda r: int(r.get("pairRadius", -1)) == 2),
        ("radius-4", lambda r: int(r.get("pairRadius", -1)) == 4),
        ("radius-8", lambda r: int(r.get("pairRadius", -1)) == 8),
        ("lambda-1", lambda r: abs(float(r.get("lambda", -999.0)) - 1.0) < 1e-12),
        ("lambda-100", lambda r: abs(float(r.get("lambda", -999.0)) - 100.0) < 1e-12),
        ("dispersion-none", lambda r: r.get("dispersion") is None),
        ("dispersion-lt-0.5", lambda r: r.get("dispersion") is not None and float(r["dispersion"]) < 0.5),
        ("dispersion-0.5-to-0.9", lambda r: r.get("dispersion") is not None and 0.5 <= float(r["dispersion"]) <= 0.9),
        ("dispersion-gt-0.9", lambda r: r.get("dispersion") is not None and float(r["dispersion"]) > 0.9),
    ]

    results = []
    for name, fn in guards:
        selected = [r for r in changed if fn(r)]
        rescues = sum(r.get("status") == "rescue" for r in selected)
        regressions = sum(r.get("status") == "regression" for r in selected)
        floor_selected = sum(fn(r) for r in floors)
        results.append({
            "guard": name,
            "changedSelected": len(selected),
            "rescuesKept": int(rescues),
            "regressionsKept": int(regressions),
            "netVsV28AmongChanged": int(rescues - regressions),
            "v80FloorFailuresMatchingGuard": int(floor_selected),
        })

    zero_reg = [r for r in results if r["regressionsKept"] == 0 and r["rescuesKept"] > 0]
    best_net = max(r["netVsV28AmongChanged"] for r in results)
    best = [r for r in results if r["netVsV28AmongChanged"] == best_net]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V82")

    out = {
        "schemaVersion": 82,
        "profileType": "v81-v80-simple-training-side-guard-separability-diagnostic",
        "changedOutcomeCount": len(changed),
        "floorFailureCount": len(floors),
        "guardResults": results,
        "zeroRegressionGuards": zero_reg,
        "bestNetGuards": best,
        "diagnosticOutcomesTaintedForSelection": True,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "changedOutcomeCount", "floorFailureCount", "zeroRegressionGuards",
        "bestNetGuards", "diagnosticOutcomesTaintedForSelection",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "validatedNewChampion", "protected949CandidateHashUnchanged", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V82 V80 SIMPLE GUARD SEPARABILITY COMPLETE")
    print("Changed outcomes:", len(changed), "Floor failures:", len(floors))
    print("Guard results:")
    for r in results:
        print(" ", r)
    print("Zero-regression guards:", zero_reg)
    print("Best-net guards:", best)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
