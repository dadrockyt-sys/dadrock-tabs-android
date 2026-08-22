from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCES = (
    ("v56_exposed_120", PUBLIC / "gomyway-3676-patch-rhythm24-v55-unanimous-tight-lift-escape-v56.json"),
    ("v57_exposed_160", PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"),
)
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v62-broad-support-margin-distribution-v63.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v62-broad-support-margin-distribution-v63-manifest.json"
BROAD_Q = 0.225


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status(row: dict) -> str:
    p = bool(row.get("passed"))
    vp = bool((row.get("v28Comparison") or {}).get("passed"))
    if p and vp:
        return "bothPass"
    if p and not vp:
        return "rescue"
    if (not p) and vp:
        return "regression"
    return "bothFail"


def summary(vals: list[float]) -> dict:
    if not vals:
        return {"count": 0, "min": None, "q25": None, "median": None, "q75": None, "max": None, "mean": None}
    a = np.asarray(vals, dtype=np.float64)
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

    metrics = defaultdict(lambda: defaultdict(list))
    counts = Counter()
    rows_out = []

    for source_name, source_path in SOURCES:
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        src = json.loads(source_path.read_text(encoding="utf-8"))
        for phase in src.get("schemes") or []:
            ph = float(phase.get("phase"))
            for row in phase.get("folds") or []:
                q = float(row.get("outerQ", 0.2))
                if abs(q - BROAD_Q) > 1e-12:
                    continue
                st = status(row)
                sel = row.get("selector") or {}
                schemes = sel.get("schemes") or []
                broad_deltas = []
                pass_deltas = []
                for s in schemes:
                    mb = float(s.get("meanBroadLift", 0.0))
                    ma = float(s.get("meanAnchorLift", 0.0))
                    broad_deltas.append(mb - ma)
                    bp = int(s.get("broadPasses", 0))
                    ap = int(s.get("anchorPasses", 0))
                    pass_deltas.append(bp - ap)

                if broad_deltas:
                    mean_delta = float(np.mean(broad_deltas))
                    min_delta = float(np.min(broad_deltas))
                    max_delta = float(np.max(broad_deltas))
                    std_delta = float(np.std(broad_deltas))
                else:
                    mean_delta = min_delta = max_delta = std_delta = 0.0

                strict_count = int(sel.get("strictBroadSupportCount", sum(int(d > 0) for d in pass_deltas)))
                nonneg_pass_count = sum(int(d >= 0) for d in pass_deltas)
                positive_lift_count = sum(int(d > 0) for d in broad_deltas)

                counts[(source_name, st)] += 1
                for name, value in (
                    ("broadMeanLiftDelta", mean_delta),
                    ("broadMinLiftDelta", min_delta),
                    ("broadMaxLiftDelta", max_delta),
                    ("broadLiftDeltaStd", std_delta),
                    ("strictBroadSupportCount", float(strict_count)),
                    ("nonnegativeBroadPassDeltaSchemeCount", float(nonneg_pass_count)),
                    ("positiveBroadLiftDeltaSchemeCount", float(positive_lift_count)),
                ):
                    metrics[st][name].append(value)

                rows_out.append({
                    "source": source_name,
                    "phase": ph,
                    "fold": int(row.get("fold", -1)),
                    "status": st,
                    "strictBroadSupportCount": strict_count,
                    "broadPassDeltasByScheme": pass_deltas,
                    "broadLiftDeltasByScheme": broad_deltas,
                    "broadMeanLiftDelta": mean_delta,
                    "broadMinLiftDelta": min_delta,
                    "broadMaxLiftDelta": max_delta,
                    "broadLiftDeltaStd": std_delta,
                    "positiveBroadLiftDeltaSchemeCount": positive_lift_count,
                    "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
                    "v28HeldoutPrecisionLift": (row.get("v28Comparison") or {}).get("heldoutPrecisionLift"),
                })

    by_status = {}
    for st in ("bothPass", "rescue", "regression", "bothFail"):
        by_status[st] = {name: summary(vals) for name, vals in metrics[st].items()}

    changed_rows = [r for r in rows_out if r["status"] in ("rescue", "regression")]

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V63")

    out = {
        "schemaVersion": 63,
        "profileType": "v62-broad-support-margin-distribution",
        "broadQ": BROAD_Q,
        "broadRows": len(rows_out),
        "statusCounts": {st: sum(1 for r in rows_out if r["status"] == st) for st in ("bothPass", "rescue", "regression", "bothFail")},
        "distributionByStatus": by_status,
        "changedRows": changed_rows,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "heldoutLabelsDiagnosticOnly": True,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 63,
        "broadRows": len(rows_out),
        "statusCounts": out["statusCounts"],
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "newTuningPerformed": False,
        "protected949CandidateHashUnchanged": before == after,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V62 BROAD-SUPPORT MARGIN DISTRIBUTION V63 COMPLETE")
    print("Broad status counts:", out["statusCounts"])
    for st in ("bothPass", "rescue", "regression", "bothFail"):
        print(f"Status {st}:")
        for name, sm in by_status[st].items():
            print(f"  {name}: {sm}")
    print("Changed broad rows:")
    for r in changed_rows:
        print(" ", r)
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
