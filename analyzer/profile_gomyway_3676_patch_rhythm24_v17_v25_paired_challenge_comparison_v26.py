from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V23_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23.json"
V25_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-multiphase-training-q-selector-v25.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-v25-paired-challenge-comparison-v26.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v17-v25-paired-challenge-comparison-v26-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Required prior result missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def key(phase: float, fold: int) -> tuple[float, int]:
    return (round(float(phase), 6), int(fold))


def main() -> None:
    v23 = load(V23_PATH)
    v25 = load(V25_PATH)

    # V23 contains duplicate section-like and shifted-like evaluations of the same
    # phase/fold geometry. For a fair adaptive-policy comparison, use the frozen
    # V17 shifted-policy rows because V25 is itself an adaptive q policy.
    frozen: dict[tuple[float, int], dict[str, Any]] = {}
    for scheme in v23.get("schemes", []):
        if not str(scheme.get("name", "")).startswith("shiftedConfirmPhase"):
            continue
        for row in scheme.get("folds", []):
            frozen[key(row["phase"], row["fold"])] = row

    challenger: dict[tuple[float, int], dict[str, Any]] = {}
    for scheme in v25.get("schemes", []):
        phase = float(scheme["phase"])
        for row in scheme.get("folds", []):
            challenger[key(phase, row["fold"])] = row

    common = sorted(set(frozen) & set(challenger))
    if len(common) != 20:
        raise RuntimeError(f"Expected 20 matched challenge partitions, found {len(common)}")

    pairs = []
    rescues = []
    regressions = []
    same_pass = []
    same_fail = []

    for k in common:
        a = frozen[k]
        b = challenger[k]
        a_pass = bool(a["passed"])
        b_pass = bool(b["passed"])
        row = {
            "phase": k[0],
            "fold": k[1],
            "v17Passed": a_pass,
            "v25Passed": b_pass,
            "v17Q": float(a["outerQ"]),
            "v25Q": float(b["outerQ"]),
            "v17Lift": float(a["heldoutPrecisionLift"]),
            "v25Lift": float(b["heldoutPrecisionLift"]),
            "qChanged": abs(float(a["outerQ"]) - float(b["outerQ"])) > 1e-12,
        }
        pairs.append(row)
        if (not a_pass) and b_pass:
            rescues.append(row)
        elif a_pass and (not b_pass):
            regressions.append(row)
        elif a_pass and b_pass:
            same_pass.append(row)
        else:
            same_fail.append(row)

    v17_passes = sum(int(r["v17Passed"]) for r in pairs)
    v25_passes = sum(int(r["v25Passed"]) for r in pairs)
    net_gain = len(rescues) - len(regressions)
    q_changed = sum(int(r["qChanged"]) for r in pairs)

    # A narrow gate is only worth pursuing if the challenger produces a positive
    # net gain and its rescues are not offset by regressions. This diagnostic does
    # not invent or fit such a gate.
    narrow_gate_warranted = len(rescues) > 0 and len(regressions) == 0 and net_gain > 0
    retire_v25 = v25_passes <= v17_passes and len(regressions) >= len(rescues)

    output = {
        "schemaVersion": 26,
        "profileType": "36.76-rhythm24-v17-v25-paired-challenge-comparison",
        "matchedPartitions": len(pairs),
        "frozenReference": "V17 shifted-policy on V23 unseen phases",
        "challenger": "V25 multiphase training-only q selector",
        "v17Passes": v17_passes,
        "v25Passes": v25_passes,
        "rescues": len(rescues),
        "regressions": len(regressions),
        "samePass": len(same_pass),
        "sameFail": len(same_fail),
        "netGain": net_gain,
        "qChangedPartitions": q_changed,
        "narrowGateWarranted": narrow_gate_warranted,
        "retireV25": retire_v25,
        "pairs": pairs,
        "rescueRows": rescues,
        "regressionRows": regressions,
        "sameFailRows": same_fail,
        "newTuningPerformed": False,
        "outerHeldoutLabelsUsedToChoosePolicy": False,
        "protectedCandidateModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 26,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "matchedPartitions": len(pairs),
        "v17Passes": v17_passes,
        "v25Passes": v25_passes,
        "rescues": len(rescues),
        "regressions": len(regressions),
        "netGain": net_gain,
        "narrowGateWarranted": narrow_gate_warranted,
        "retireV25": retire_v25,
        "newTuningPerformed": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V17 VS V25 PAIRED CHALLENGE COMPARISON V26 COMPLETE")
    print("Matched partitions:", len(pairs))
    print("Frozen V17 passes:", v17_passes, "/", len(pairs))
    print("V25 passes:", v25_passes, "/", len(pairs))
    print("Rescues:", len(rescues))
    print("Regressions:", len(regressions))
    print("Same-pass:", len(same_pass))
    print("Same-fail:", len(same_fail))
    print("Net gain:", net_gain)
    print("Partitions where q changed:", q_changed)
    print("Narrow gate warranted:", narrow_gate_warranted)
    print("Retire V25:", retire_v25)
    if rescues:
        print("RESCUE ROWS")
        for r in rescues:
            print(r)
    if regressions:
        print("REGRESSION ROWS")
        for r in regressions:
            print(r)
    if same_fail:
        print("SAME-FAIL ROWS")
        for r in same_fail:
            print(r)
    print("New tuning performed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
