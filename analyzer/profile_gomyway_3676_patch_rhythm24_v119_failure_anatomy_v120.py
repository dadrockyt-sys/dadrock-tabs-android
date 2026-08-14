from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V119_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v119-failure-anatomy-v120.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v119-failure-anatomy-v120-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_bits(row: dict) -> tuple[int | None, float | None]:
    model = row.get("chosenModel") or {}
    radius = model.get("pairRadius")
    lam = model.get("lambda")
    return (
        None if radius is None else int(radius),
        None if lam is None else float(lam),
    )


def sig(row: dict) -> tuple:
    radius, lam = model_bits(row)
    return (
        row.get("originalQBucket"),
        row.get("v96Decision"),
        radius,
        lam,
        bool(row.get("selectedForV112")),
        row.get("v118Representation") or row.get("finalRepresentation") or row.get("v115Representation"),
    )


def sig_dict(s: tuple) -> dict:
    return {
        "originalQBucket": s[0],
        "v96Decision": s[1],
        "pairRadius": s[2],
        "lambda": s[3],
        "selectedForV112": s[4],
        "representation": s[5],
    }


def main() -> None:
    d = json.loads(V119_PATH.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 119 or not bool(d.get("validatedNewChampion")):
        raise RuntimeError("Expected validated V119 confirmation output")
    if int(d.get("v118Passes", -1)) != 293 or int(d.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V119 does not match frozen 293/320 champion confirmation")

    rows: list[dict] = []
    for scheme in d.get("schemes") or []:
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", scheme.get("phase"))
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V119 rows, got {len(rows)}")

    fails = [r for r in rows if not bool(r.get("v118Passed"))]
    passes = [r for r in rows if bool(r.get("v118Passed"))]
    if len(fails) != 27 or len(passes) != 293:
        raise RuntimeError(f"Expected 27 failures / 293 passes, got {len(fails)} / {len(passes)}")

    def count_by(key_fn):
        return Counter(key_fn(r) for r in fails)

    by_q = count_by(lambda r: r.get("originalQBucket"))
    by_decision = count_by(lambda r: r.get("v96Decision"))
    by_radius = count_by(lambda r: model_bits(r)[0])
    by_lambda = count_by(lambda r: model_bits(r)[1])
    by_selected = count_by(lambda r: bool(r.get("selectedForV112")))
    by_rep = count_by(lambda r: r.get("v118Representation") or r.get("finalRepresentation") or r.get("v115Representation"))

    sig_all = defaultdict(lambda: {"rows": 0, "failures": 0, "passes": 0})
    for r in rows:
        s = sig(r)
        sig_all[s]["rows"] += 1
        if bool(r.get("v118Passed")):
            sig_all[s]["passes"] += 1
        else:
            sig_all[s]["failures"] += 1

    signature_rows = []
    for s, stats in sig_all.items():
        if stats["failures"] <= 0:
            continue
        rate = stats["failures"] / stats["rows"]
        overall = len(fails) / len(rows)
        signature_rows.append({
            **sig_dict(s),
            **stats,
            "failureRate": round(rate, 6),
            "liftVsOverallFailureRate": round(rate / overall, 3) if overall else None,
        })
    signature_rows.sort(key=lambda x: (-x["failures"], -x["liftVsOverallFailureRate"], -x["rows"]))

    bottleneck = float((d.get("v118BottleneckPhases") or [0.7060546875])[0])
    bottleneck_rows = [r for r in rows if abs(float(r.get("phase", -999)) - bottleneck) < 1e-12]

    failure_detail = []
    for r in fails:
        radius, lam = model_bits(r)
        failure_detail.append({
            "phase": float(r.get("phase")),
            "fold": int(r.get("fold")),
            "gateScore": r.get("gateScore"),
            "selectedForV112": bool(r.get("selectedForV112")),
            "originalQBucket": r.get("originalQBucket"),
            "v96Decision": r.get("v96Decision"),
            "dispersion": r.get("dispersion"),
            "pairRadius": radius,
            "lambda": lam,
            "dangerousSignature": bool(r.get("dangerousSignature")),
            "exclusionApplied": bool(r.get("exclusionApplied")),
            "v28Passed": bool(r.get("v28Passed")),
            "v96Passed": bool(r.get("v96Passed")),
            "v115Passed": bool(r.get("v115Passed")),
            "v118Passed": bool(r.get("v118Passed")),
            "v115Representation": r.get("v115Representation"),
            "v118Representation": r.get("v118Representation"),
            "heldoutPrecisionLift": r.get("heldoutPrecisionLift"),
        })

    summary = {
        "foldsTotal": len(rows),
        "v118Passes": len(passes),
        "v118Failures": len(fails),
        "v118ScorePercent": round(100.0 * len(passes) / len(rows), 4),
        "failuresWhereV96Passed": sum(bool(r.get("v96Passed")) for r in fails),
        "failuresWhereV115Passed": sum(bool(r.get("v115Passed")) for r in fails),
        "failuresWhereV28Passed": sum(bool(r.get("v28Passed")) for r in fails),
        "failuresSelectedForV112": sum(bool(r.get("selectedForV112")) for r in fails),
        "failuresNotSelectedForV112": sum(not bool(r.get("selectedForV112")) for r in fails),
        "bottleneckPhase": bottleneck,
        "bottleneckPasses": sum(bool(r.get("v118Passed")) for r in bottleneck_rows),
        "bottleneckFailures": sum(not bool(r.get("v118Passed")) for r in bottleneck_rows),
    }

    output = {
        "schemaVersion": 120,
        "profileType": "post-v119-v118-failure-anatomy-diagnostic",
        "summary": summary,
        "failureCountsByQBucket": dict(by_q),
        "failureCountsByDecision": dict(by_decision),
        "failureCountsByPairRadius": {str(k): v for k, v in by_radius.items()},
        "failureCountsByLambda": {str(k): v for k, v in by_lambda.items()},
        "failureCountsBySelectedForV112": {str(k): v for k, v in by_selected.items()},
        "failureCountsByRepresentation": {str(k): v for k, v in by_rep.items()},
        "failureSignatures": signature_rows,
        "failureDetail": failure_detail,
        "bottleneckRows": bottleneck_rows,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "protected949CandidateHashUnchanged": bool(d.get("protected949CandidateHashUnchanged")),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in output.items() if k not in {"failureDetail", "bottleneckRows"}}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V120 V119 FAILURE ANATOMY DIAGNOSTIC COMPLETE")
    print(f"V118 scoreboard: {len(passes)}/{len(rows)} = {100.0*len(passes)/len(rows):.4f}%")
    print(f"Remaining failures: {len(fails)}")
    print(f"Failures where V96 passed: {summary['failuresWhereV96Passed']}")
    print(f"Failures where V115 passed: {summary['failuresWhereV115Passed']}")
    print(f"Failures selected for V112: {summary['failuresSelectedForV112']}")
    print(f"Failures not selected for V112: {summary['failuresNotSelectedForV112']}")
    print(f"Bottleneck phase {bottleneck:.10f}: {summary['bottleneckPasses']}/5 passes")

    print("\n=== FAILURE COUNTS ===")
    print("qBucket:", dict(by_q))
    print("decision:", dict(by_decision))
    print("pairRadius:", dict(by_radius))
    print("lambda:", dict(by_lambda))
    print("selectedForV112:", dict(by_selected))
    print("representation:", dict(by_rep))

    print("\n=== TOP FAILURE SIGNATURES ===")
    for i, r in enumerate(signature_rows[:15], 1):
        print(f"#{i}", r)

    print("\nHeld-out labels used for diagnosis only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Candidate policy changed: False")
    print("Protected candidate unchanged:", bool(d.get("protected949CandidateHashUnchanged")))
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
