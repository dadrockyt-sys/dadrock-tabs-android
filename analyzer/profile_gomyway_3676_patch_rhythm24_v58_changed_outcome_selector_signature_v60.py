from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v57-confirmation-failure-map-v58.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v58-changed-outcome-selector-signature-v60.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v58-changed-outcome-selector-signature-v60-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_row(row: dict) -> dict:
    sel = row.get("selector") or {}
    schemes = sel.get("schemes") or []
    strict = int(sel.get("strictBroadSupportCount", 0))
    unanimous = bool(sel.get("unanimousTightEscape", False))

    broad_deltas = []
    tight_deltas = []
    broad_pass_deltas = []
    tight_pass_deltas = []
    for s in schemes:
        ap = int(s.get("anchorPasses", 0))
        bp = int(s.get("broadPasses", ap))
        tp = int(s.get("tightPasses", ap))
        ma = float(s.get("meanAnchorLift", 0.0))
        mb = float(s.get("meanBroadLift", ma))
        mt = float(s.get("meanTightLift", ma))
        broad_pass_deltas.append(bp - ap)
        tight_pass_deltas.append(tp - ap)
        broad_deltas.append(mb - ma)
        tight_deltas.append(mt - ma)

    return {
        "phase": row.get("phase"),
        "fold": row.get("fold"),
        "status": row.get("status"),
        "branch": row.get("branch"),
        "reason": row.get("reason"),
        "strictSupportCount": strict,
        "unanimousTightEscape": unanimous,
        "broadPassDeltasByScheme": broad_pass_deltas,
        "tightPassDeltasByScheme": tight_pass_deltas,
        "broadLiftDeltasByScheme": [round(x, 6) for x in broad_deltas],
        "tightLiftDeltasByScheme": [round(x, 6) for x in tight_deltas],
        "broadMeanLiftDelta": round(sum(broad_deltas) / len(broad_deltas), 6) if broad_deltas else None,
        "tightMeanLiftDelta": round(sum(tight_deltas) / len(tight_deltas), 6) if tight_deltas else None,
        "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
        "v28HeldoutPrecisionLift": row.get("v28HeldoutPrecisionLift"),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Missing V58 output: {SOURCE_PATH}")

    src = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    changed = [summarize_row(r) for r in (src.get("changedOutcomeRows") or [])]

    by_branch_status = defaultdict(Counter)
    by_strict_status = defaultdict(Counter)
    by_unanimous_status = defaultdict(Counter)
    for r in changed:
        by_branch_status[r["branch"]][r["status"]] += 1
        by_strict_status[str(r["strictSupportCount"])][r["status"]] += 1
        by_unanimous_status[str(r["unanimousTightEscape"])][r["status"]] += 1

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V60")

    out = {
        "schemaVersion": 60,
        "profileType": "v58-changed-outcome-selector-signature",
        "changedOutcomeCount": len(changed),
        "changedOutcomesByBranchStatus": {k: dict(v) for k, v in by_branch_status.items()},
        "changedOutcomesByStrictSupportStatus": {k: dict(v) for k, v in by_strict_status.items()},
        "changedOutcomesByUnanimousEscapeStatus": {k: dict(v) for k, v in by_unanimous_status.items()},
        "changedOutcomeRows": changed,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsDiagnosticOnly": True,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: out[k] for k in [
        "schemaVersion", "changedOutcomeCount", "changedOutcomesByBranchStatus",
        "changedOutcomesByStrictSupportStatus", "changedOutcomesByUnanimousEscapeStatus",
        "newReserved1over128OddNumeratorPhasesReferenced", "newTuningPerformed",
        "protected949CandidateHashUnchanged", "validatedNewChampion", "productionPromotionAllowed"
    ]}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V58 CHANGED-OUTCOME SELECTOR SIGNATURE V60 COMPLETE")
    print("Changed outcome count:", len(changed))
    print("Changed outcomes by branch/status:", {k: dict(v) for k, v in by_branch_status.items()})
    print("Changed outcomes by strict-support/status:", {k: dict(v) for k, v in by_strict_status.items()})
    print("Changed outcomes by unanimous-escape/status:", {k: dict(v) for k, v in by_unanimous_status.items()})
    for r in changed:
        print("Row:", r)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
