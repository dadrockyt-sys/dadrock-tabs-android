from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

V112_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112.json"
V115_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v114-selective-v112-top2over7-challenger-v115.json"
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v117-dangerous-signature-exclusion-counterfactual-v118.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v117-dangerous-signature-exclusion-counterfactual-v118-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_dangerous_signature(row: dict) -> bool:
    model = row.get("chosenModel") or {}
    return bool(
        row.get("originalQBucket") == "tight"
        and row.get("v96Decision") == "revert-tight-to-anchor-low-dispersion"
        and int(model.get("pairRadius", -1)) == 8
        and abs(float(model.get("lambda", -999.0)) - 1.0) < 1e-12
    )


def row_key(row: dict) -> tuple:
    return (row.get("source"), round(float(row.get("phase", 0.0)), 12), int(row.get("fold", -1)))


def summarize(rows: list[dict], label: str) -> dict:
    v96 = sum(bool(r["v96Passed"]) for r in rows)
    v115 = sum(bool(r["v115Passed"]) for r in rows)
    v118 = sum(bool(r["v118Passed"]) for r in rows)
    gains115 = sum(bool(r["v115Passed"] and not r["v96Passed"]) for r in rows)
    losses115 = sum(bool(r["v96Passed"] and not r["v115Passed"]) for r in rows)
    gains118 = sum(bool(r["v118Passed"] and not r["v96Passed"]) for r in rows)
    losses118 = sum(bool(r["v96Passed"] and not r["v118Passed"]) for r in rows)
    excluded = [r for r in rows if r.get("dangerousSignature") and r.get("selectedForV112")]
    excluded_gains = sum(bool(r["v115Passed"] and not r["v96Passed"]) for r in excluded)
    excluded_losses = sum(bool(r["v96Passed"] and not r["v115Passed"]) for r in excluded)
    return {
        "label": label,
        "foldsTotal": len(rows),
        "v96Passes": v96,
        "v115Passes": v115,
        "v118CounterfactualPasses": v118,
        "v96ScorePercent": round(100.0 * v96 / len(rows), 4),
        "v115ScorePercent": round(100.0 * v115 / len(rows), 4),
        "v118CounterfactualScorePercent": round(100.0 * v118 / len(rows), 4),
        "v115GainsVsV96": gains115,
        "v115LossesVsV96": losses115,
        "v118GainsVsV96": gains118,
        "v118LossesVsV96": losses118,
        "v118NetVsV96": gains118 - losses118,
        "excludedSelectedRows": len(excluded),
        "excludedV115Gains": excluded_gains,
        "excludedV115Losses": excluded_losses,
    }


def main() -> None:
    v112 = json.loads(V112_PATH.read_text(encoding="utf-8"))
    v115 = json.loads(V115_PATH.read_text(encoding="utf-8"))
    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))

    if int(v115.get("schemaVersion", -1)) != 115:
        raise RuntimeError("Expected V115 development output")
    if int(v116.get("schemaVersion", -1)) != 116 or not bool(v116.get("validatedNewChampion")):
        raise RuntimeError("Expected validated V116 confirmation output")

    # V116 confirmation rows already contain all structural metadata.
    confirm_rows: list[dict] = []
    for scheme in v116.get("schemes") or []:
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r["dangerousSignature"] = is_dangerous_signature(r)
            r["v118Passed"] = bool(r.get("v96Passed")) if (
                r.get("selectedForV112") and r["dangerousSignature"]
            ) else bool(r.get("v115Passed"))
            confirm_rows.append(r)

    # V115 development rows do not carry structural metadata, so join the
    # previously saved V112 development rows by source/phase/fold.
    v112_map = {row_key(r): r for r in (v112.get("rowsDetail") or [])}
    dev_rows: list[dict] = []
    missing = []
    for r0 in v115.get("rowsDetail") or []:
        r = dict(r0)
        meta = v112_map.get(row_key(r))
        if meta is None:
            missing.append(row_key(r))
            continue
        r["chosenModel"] = meta.get("chosenModel")
        r["originalQBucket"] = meta.get("originalQBucket")
        r["v96Decision"] = meta.get("v96Decision")
        r["dangerousSignature"] = is_dangerous_signature(r)
        r["v118Passed"] = bool(r.get("v96Passed")) if (
            r.get("selectedForV112") and r["dangerousSignature"]
        ) else bool(r.get("v115Passed"))
        dev_rows.append(r)
    if missing:
        raise RuntimeError(f"Could not join {len(missing)} V115 rows to V112 metadata; first={missing[0]}")

    dev = summarize(dev_rows, "previously-exposed-v115-development")
    confirm = summarize(confirm_rows, "consumed-v116-confirmation")

    output = {
        "schemaVersion": 118,
        "profileType": "post-v116-dangerous-signature-exclusion-counterfactual-diagnostic",
        "dangerousSignature": {
            "originalQBucket": "tight",
            "v96Decision": "revert-tight-to-anchor-low-dispersion",
            "pairRadius": 8,
            "lambda": 1.0,
        },
        "signatureChosenFromConsumedV116Outcomes": True,
        "developmentReverseValidation": dev,
        "consumedConfirmationCounterfactual": confirm,
        "candidatePolicy": "Use frozen V115 except do not activate V112 on the dangerous signature; use V96 there.",
        "candidatePolicyValidated": False,
        "diagnosticOutcomesTaintedForFutureSelection": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V118 DANGEROUS-SIGNATURE EXCLUSION COUNTERFACTUAL COMPLETE")
    print("Dangerous signature: tight | revert-tight-to-anchor-low-dispersion | r8 | lambda1")
    print("\n=== REVERSE VALIDATION ON OLD V115 DEVELOPMENT ===")
    print(f"V96:  {dev['v96Passes']}/{dev['foldsTotal']} = {dev['v96ScorePercent']:.4f}%")
    print(f"V115: {dev['v115Passes']}/{dev['foldsTotal']} = {dev['v115ScorePercent']:.4f}%")
    print(f"V118: {dev['v118CounterfactualPasses']}/{dev['foldsTotal']} = {dev['v118CounterfactualScorePercent']:.4f}%")
    print(f"V118 gains/losses vs V96: +{dev['v118GainsVsV96']}/-{dev['v118LossesVsV96']} net={dev['v118NetVsV96']:+d}")
    print(f"Excluded selected rows: {dev['excludedSelectedRows']} (V115 gains={dev['excludedV115Gains']}, losses={dev['excludedV115Losses']})")

    print("\n=== COUNTERFACTUAL ON CONSUMED V116 CONFIRMATION ===")
    print(f"V96:  {confirm['v96Passes']}/{confirm['foldsTotal']} = {confirm['v96ScorePercent']:.4f}%")
    print(f"V115: {confirm['v115Passes']}/{confirm['foldsTotal']} = {confirm['v115ScorePercent']:.4f}%")
    print(f"V118: {confirm['v118CounterfactualPasses']}/{confirm['foldsTotal']} = {confirm['v118CounterfactualScorePercent']:.4f}%")
    print(f"V118 gains/losses vs V96: +{confirm['v118GainsVsV96']}/-{confirm['v118LossesVsV96']} net={confirm['v118NetVsV96']:+d}")
    print(f"Excluded selected rows: {confirm['excludedSelectedRows']} (V115 gains={confirm['excludedV115Gains']}, losses={confirm['excludedV115Losses']})")

    print("\nSignature chosen from consumed V116 outcomes: True")
    print("Candidate policy validated: False")
    print("New reserved phase family referenced: False")
    print("New tuning performed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
