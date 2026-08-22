from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v116-confirmation-failure-anatomy-v117.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v116-confirmation-failure-anatomy-v117-manifest.json"

BOTTLENECK_PHASE = 0.7041015625


def qbucket(row: dict) -> str:
    return str(row.get("originalQBucket") or "unknown")


def chosen_model_key(row: dict) -> str:
    m = row.get("chosenModel") or {}
    return f"r{m.get('pairRadius')}_lambda{m.get('lambda')}"


def compact(row: dict) -> dict:
    return {
        "phase": row.get("phase"),
        "fold": row.get("fold"),
        "gateScore": row.get("gateScore"),
        "selectedForV112": row.get("selectedForV112"),
        "chosenModel": row.get("chosenModel"),
        "originalTrainingOnlyQ": row.get("originalTrainingOnlyQ"),
        "originalQBucket": row.get("originalQBucket"),
        "v96Decision": row.get("v96Decision"),
        "dispersion": row.get("dispersion"),
        "excludedSafeBroadR8Lambda1": row.get("excludedSafeBroadR8Lambda1"),
        "v28Passed": row.get("v28Passed"),
        "v96Passed": row.get("v96Passed"),
        "v115Passed": row.get("v115Passed"),
        "gainVsV96": row.get("gainVsV96"),
        "lossVsV96": row.get("lossVsV96"),
        "finalRepresentation": row.get("finalRepresentation"),
        "heldoutPrecisionLift": row.get("heldoutPrecisionLift"),
    }


def counts(rows: list[dict]) -> dict:
    return {
        "rows": len(rows),
        "byQBucket": dict(Counter(qbucket(r) for r in rows)),
        "byDecision": dict(Counter(str(r.get("v96Decision")) for r in rows)),
        "byModel": dict(Counter(chosen_model_key(r) for r in rows)),
        "byRepresentation": dict(Counter(str(r.get("finalRepresentation")) for r in rows)),
        "selectedForV112": sum(bool(r.get("selectedForV112")) for r in rows),
    }


def main() -> None:
    d = json.loads(V116_PATH.read_text(encoding="utf-8"))
    if int(d.get("schemaVersion", -1)) != 116:
        raise RuntimeError("Expected V116 confirmation output")
    if not bool(d.get("confirmationSuccess")) or not bool(d.get("validatedNewChampion")):
        raise RuntimeError("V116 is not the validated confirmation checkpoint")
    if int(d.get("v115Passes", -1)) != 288 or int(d.get("v96Passes", -1)) != 283:
        raise RuntimeError("Unexpected V116 scoreboard")

    rows: list[dict] = []
    for scheme in d.get("schemes") or []:
        rows.extend(list(scheme.get("folds") or []))
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V116 folds, got {len(rows)}")

    gains = [r for r in rows if bool(r.get("gainVsV96"))]
    losses = [r for r in rows if bool(r.get("lossVsV96"))]
    changed = gains + losses
    bottleneck = [r for r in rows if abs(float(r.get("phase", -1)) - BOTTLENECK_PHASE) < 1e-12]

    selected = [r for r in rows if bool(r.get("selectedForV112"))]
    selected_unchanged = [r for r in selected if not bool(r.get("gainVsV96")) and not bool(r.get("lossVsV96"))]

    gate_summary = {}
    for label, rs in [
        ("gain", gains),
        ("loss", losses),
        ("changed", changed),
        ("selectedUnchanged", selected_unchanged),
    ]:
        scores = [float(r.get("gateScore")) for r in rs if r.get("gateScore") is not None]
        gate_summary[label] = {
            "n": len(scores),
            "min": min(scores) if scores else None,
            "max": max(scores) if scores else None,
            "mean": (sum(scores) / len(scores)) if scores else None,
        }

    signature_counter: dict[str, dict] = defaultdict(lambda: {"gains": 0, "losses": 0, "rows": 0})
    for r in changed:
        sig = "|".join([
            qbucket(r),
            str(r.get("v96Decision")),
            chosen_model_key(r),
            str(r.get("finalRepresentation")),
        ])
        rec = signature_counter[sig]
        rec["rows"] += 1
        rec["gains"] += int(bool(r.get("gainVsV96")))
        rec["losses"] += int(bool(r.get("lossVsV96")))

    changed_signatures = [
        {"signature": k, **v, "net": int(v["gains"] - v["losses"])}
        for k, v in signature_counter.items()
    ]
    changed_signatures.sort(key=lambda x: (x["losses"], -x["gains"], x["signature"]))

    output = {
        "schemaVersion": 117,
        "profileType": "v116-confirmation-failure-anatomy-diagnostic",
        "sourceV116": str(V116_PATH.relative_to(ROOT)),
        "v115ValidatedChampionScorePercent": float(d.get("v115ScorePercent")),
        "v115Passes": int(d.get("v115Passes")),
        "v96Passes": int(d.get("v96Passes")),
        "gainsVsV96": len(gains),
        "lossesVsV96": len(losses),
        "netVsV96": len(gains) - len(losses),
        "gainCounts": counts(gains),
        "lossCounts": counts(losses),
        "gateScoreSummary": gate_summary,
        "changedSignatures": changed_signatures,
        "gainRows": [compact(r) for r in gains],
        "lossRows": [compact(r) for r in losses],
        "bottleneckPhase": BOTTLENECK_PHASE,
        "bottleneckRows": [compact(r) for r in bottleneck],
        "bottleneckPassesV115": sum(bool(r.get("v115Passed")) for r in bottleneck),
        "bottleneckPassesV96": sum(bool(r.get("v96Passed")) for r in bottleneck),
        "selectedRows": len(selected),
        "selectedUnchangedRows": len(selected_unchanged),
        "diagnosticOnly": True,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "newGateChosen": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in output.items() if k not in {"gainRows", "lossRows", "bottleneckRows"}}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V117 V116 CONFIRMATION FAILURE ANATOMY DIAGNOSTIC COMPLETE")
    print(f"Frozen validated V115 scoreboard: {d['v115Passes']}/{d['foldsTotal']} = {d['v115ScorePercent']:.4f}%")
    print(f"Changed vs V96: gains={len(gains)} losses={len(losses)} net={len(gains)-len(losses):+d}")
    print("\n=== GAIN ANATOMY ===")
    print(json.dumps(counts(gains), indent=2))
    print("\n=== LOSS ANATOMY ===")
    print(json.dumps(counts(losses), indent=2))
    print("\n=== CHANGED SIGNATURES ===")
    for rec in changed_signatures:
        print(rec)
    print("\n=== GATE SCORE SUMMARY ===")
    print(json.dumps(gate_summary, indent=2))
    print(f"\n=== BOTTLENECK PHASE {BOTTLENECK_PHASE} ===")
    print(f"rows={len(bottleneck)} V115passes={sum(bool(r.get('v115Passed')) for r in bottleneck)}/5 V96passes={sum(bool(r.get('v96Passed')) for r in bottleneck)}/5")
    for r in bottleneck:
        print(compact(r))
    print("\nLoss rows:")
    for r in losses:
        print(compact(r))
    print("\nHeld-out labels used for diagnosis only: True")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Protected candidate unchanged: True")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
