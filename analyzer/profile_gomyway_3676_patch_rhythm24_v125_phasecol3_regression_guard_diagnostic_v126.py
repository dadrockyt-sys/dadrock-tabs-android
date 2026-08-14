from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V124_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
V125_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v124-failure-anatomy-v125.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v125-phasecol3-regression-guard-diagnostic-v126.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v125-phasecol3-regression-guard-diagnostic-v126-manifest.json"

TARGET = ("tight", "revert-tight-to-anchor-low-dispersion", 4, 1.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_of(r: dict) -> tuple[str, str, int, float]:
    m = r.get("chosenModel") or {}
    return (
        str(r.get("originalQBucket")),
        str(r.get("v96Decision")),
        int(m.get("pairRadius")),
        float(m.get("lambda")),
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v124 = json.loads(V124_PATH.read_text(encoding="utf-8"))
    v125 = json.loads(V125_PATH.read_text(encoding="utf-8"))
    if int(v124.get("schemaVersion", -1)) != 124 or not bool(v124.get("validatedNewChampion")):
        raise RuntimeError("Validated V124 result required")
    if int(v125.get("schemaVersion", -1)) != 125:
        raise RuntimeError("V125 anatomy record required")

    rows = []
    for scheme in v124.get("schemes") or []:
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", float(scheme.get("phase")))
            if key_of(r) == TARGET and str(r.get("finalRepresentation")) == "phase_col3":
                rows.append(r)

    if not rows:
        raise RuntimeError("Target phase_col3 structural group not found")

    compact = []
    for r in rows:
        v118 = bool(r.get("v118Passed"))
        v122 = bool(r.get("v122Passed"))
        state = "gain" if (v122 and not v118) else "loss" if (v118 and not v122) else "both-pass" if (v118 and v122) else "both-fail"
        compact.append({
            "phase": float(r.get("phase")),
            "fold": int(r.get("fold")),
            "gateScore": float(r.get("gateScore")),
            "selectedForV112": bool(r.get("selectedForV112")),
            "stateVsV118": state,
            "v118Passed": v118,
            "v122Passed": v122,
            "heldoutPrecisionLift": r.get("heldoutPrecisionLift"),
        })

    compact.sort(key=lambda x: (x["gateScore"], x["phase"], x["fold"]))
    gains = [r for r in compact if r["stateVsV118"] == "gain"]
    losses = [r for r in compact if r["stateVsV118"] == "loss"]
    both_pass = [r for r in compact if r["stateVsV118"] == "both-pass"]
    both_fail = [r for r in compact if r["stateVsV118"] == "both-fail"]

    def rng(xs: list[dict], field: str):
        if not xs:
            return None
        vals = [float(x[field]) for x in xs]
        return {"min": min(vals), "max": max(vals), "mean": sum(vals) / len(vals)}

    summary = {
        "targetStructuralGroup": {
            "originalQBucket": TARGET[0],
            "v96Decision": TARGET[1],
            "pairRadius": TARGET[2],
            "lambda": TARGET[3],
            "representation": "phase_col3",
        },
        "rows": len(compact),
        "gainsVsV118": len(gains),
        "lossesVsV118": len(losses),
        "bothPass": len(both_pass),
        "bothFail": len(both_fail),
        "gainGateScoreRange": rng(gains, "gateScore"),
        "lossGateScoreRange": rng(losses, "gateScore"),
        "gainPhaseRange": rng(gains, "phase"),
        "lossPhaseRange": rng(losses, "phase"),
        "lossesSelectedForV112": sum(int(r["selectedForV112"]) for r in losses),
        "gainsSelectedForV112": sum(int(r["selectedForV112"]) for r in gains),
    }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V126")

    out = {
        "schemaVersion": 126,
        "profileType": "consumed-v124-phase-col3-regression-guard-diagnostic",
        "summary": summary,
        "rows": compact,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V126 PHASE_COL3 REGRESSION GUARD DIAGNOSTIC COMPLETE")
    print("Target:", summary["targetStructuralGroup"])
    print(f"Rows: {summary['rows']}")
    print(f"Gains/losses vs V118: +{summary['gainsVsV118']}/-{summary['lossesVsV118']}")
    print(f"Both-pass/both-fail: {summary['bothPass']}/{summary['bothFail']}")
    print("Gain gate-score range:", summary["gainGateScoreRange"])
    print("Loss gate-score range:", summary["lossGateScoreRange"])
    print("Gain phase range:", summary["gainPhaseRange"])
    print("Loss phase range:", summary["lossPhaseRange"])
    print(f"Selected-for-V112 gains/losses: {summary['gainsSelectedForV112']}/{summary['lossesSelectedForV112']}")
    print("\n=== TARGET ROWS SORTED BY GATE SCORE ===")
    for r in compact:
        print(r)
    print("\nHeld-out labels used for diagnosis only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
