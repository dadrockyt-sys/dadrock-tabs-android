from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-1417-champion-joint-recall-additions-profile-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1417-champion-joint-recall-addition-details-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1417-champion-joint-recall-addition-details-v1-manifest.json"


def main() -> None:
    if not INPUT_PATH.exists():
        raise RuntimeError(
            f"Missing cached additions profile: {INPUT_PATH.relative_to(ROOT)}. "
            "Run profile_gomyway_1417_champion_joint_recall_additions_v1.py first."
        )

    payload = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if payload.get("passed") is not True:
        raise RuntimeError("Cached 14.17 additions profile is not marked passed.")
    if payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cached additions profile does not preserve reference-free detection.")

    champion = payload.get("championScore") or {}
    actual = (
        int(champion.get("matched", -1)),
        int(champion.get("missing", -1)),
        int(champion.get("extra", -1)),
    )
    if actual != (178, 689, 1467) or abs(float(champion.get("pitchF1", -1.0)) - 14.17) > 0.01:
        raise RuntimeError(f"Expected 14.17 champion, got {actual}/{champion.get('pitchF1')}")

    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != 8:
        raise RuntimeError(f"Expected 8 cached winner additions, found {len(rows) if isinstance(rows, list) else 'invalid'}")

    details = []
    for row in rows:
        details.append(
            {
                "token": row["token"],
                "trueMissingReference": bool(row["trueMissingReference"]),
                "winnerSignatures": list(row.get("winnerSignatures") or []),
                "recurrence": int(row["recurrence"]),
                "rmsBucket": row["rmsBucket"],
                "fluxBucket": row["fluxBucket"],
                "ratioBucket": row["ratioBucket"],
                "templateBucket": row["templateBucket"],
                "minRmsLog2Rise": float(row["minRmsLog2Rise"]),
                "minPositiveFlux": float(row["minPositiveFlux"]),
                "minTargetVsSubharmonicRatio": float(row["minTargetVsSubharmonicRatio"]),
                "minTemplateRatio": float(row["minTemplateRatio"]),
            }
        )

    details.sort(
        key=lambda r: (
            0 if r["trueMissingReference"] else 1,
            "+".join(r["winnerSignatures"]),
            tuple(r["token"]),
        )
    )

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "cached-14.17-joint-recall-addition-continuous-feature-details",
        "championScore": champion,
        "additionCount": len(details),
        "rows": details,
        "cachedFeatureExtractionReused": True,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-reference-free-subsplit-of-sig-d-and-sig-e-only-if-continuous-feature-separation-is-visible",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "input": str(INPUT_PATH.relative_to(ROOT)),
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": champion["pitchF1"],
        "cachedFeatureExtractionReused": True,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.17 CHAMPION JOINT RECALL ADDITION DETAILS V1 COMPLETE")
    print("Passed: True")
    print("Cached feature extraction reused: True")
    print("Champion pitch F1:", champion["pitchF1"])
    print("Champion matched/missing/extra:", champion["matched"], "/", champion["missing"], "/", champion["extra"])
    print("Addition detail rows:")
    for row in details:
        label = "TRUE " if row["trueMissingReference"] else "FALSE"
        sig = "+".join(row["winnerSignatures"]) or "none"
        print(
            f"  {label} token={row['token']} sig={sig} recur={row['recurrence']} "
            f"rms={row['minRmsLog2Rise']:.6f} flux={row['minPositiveFlux']:.6f} "
            f"ratio={row['minTargetVsSubharmonicRatio']:.6f} template={row['minTemplateRatio']:.6f}"
        )
    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
