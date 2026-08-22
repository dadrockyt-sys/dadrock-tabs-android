from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V65_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v64-bottleneck-failure-anatomy-v65.json"
V67_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v66-nonepass-extended-q-recoverability-v67.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v67-nonepass-training-edge-pressure-v68.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v67-nonepass-training-edge-pressure-v68-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_signature(s: dict[str, Any]) -> dict[str, Any]:
    tp = int(s.get("tightPasses", 0))
    ap = int(s.get("anchorPasses", 0))
    bp = int(s.get("broadPasses", 0))
    tl = float(s.get("meanTightLift", 0.0))
    al = float(s.get("meanAnchorLift", 0.0))
    bl = float(s.get("meanBroadLift", 0.0))
    return {
        "scheme": s.get("scheme"),
        "passes": [tp, ap, bp],
        "liftDeltasVsAnchor": [round(tl - al, 6), 0.0, round(bl - al, 6)],
        "tightNonWorsePass": tp >= ap,
        "broadNonWorsePass": bp >= ap,
        "tightLiftBetter": tl > al,
        "broadLiftBetter": bl > al,
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v65 = json.loads(V65_PATH.read_text(encoding="utf-8"))
    v67 = json.loads(V67_PATH.read_text(encoding="utf-8"))

    failures = {(float(x["phase"]), int(x["fold"])): x for x in v65.get("bottleneckFailures") or []}
    diagnostics = []
    pressure_counts = Counter()

    for d in v67.get("diagnostics") or []:
        phase = float(d["phase"])
        fold = int(d["fold"])
        base = failures.get((phase, fold))
        if base is None:
            raise RuntimeError(f"Missing V65 failure row for phase={phase} fold={fold}")

        sigs = [scheme_signature(s) for s in (base.get("schemes") or [])]
        tight_votes = sum(1 for s in sigs if s["tightNonWorsePass"] and s["tightLiftBetter"])
        broad_votes = sum(1 for s in sigs if s["broadNonWorsePass"] and s["broadLiftBetter"])
        tight_pass_votes = sum(1 for s in sigs if s["tightNonWorsePass"])
        broad_pass_votes = sum(1 for s in sigs if s["broadNonWorsePass"])

        if broad_votes == len(sigs) and tight_votes < len(sigs):
            pressure = "unanimous-broad-edge-pressure"
        elif tight_votes == len(sigs) and broad_votes < len(sigs):
            pressure = "unanimous-tight-edge-pressure"
        elif broad_votes == len(sigs) and tight_votes == len(sigs):
            pressure = "unanimous-both-edge-pressure"
        elif broad_votes >= 2 and tight_votes >= 2:
            pressure = "mixed-bidirectional-edge-pressure"
        elif broad_votes >= 2:
            pressure = "broad-edge-pressure"
        elif tight_votes >= 2:
            pressure = "tight-edge-pressure"
        else:
            pressure = "no-clear-training-edge-pressure"
        pressure_counts[pressure] += 1

        diagnostics.append({
            "phase": phase,
            "fold": fold,
            "v67RecoveryClass": d.get("recoveryClass"),
            "v67PassingQRange": d.get("passingQRange"),
            "v64Branch": base.get("newBranch"),
            "v64Decision": base.get("decision"),
            "trainingEdgePressure": pressure,
            "tightVoteCount": tight_votes,
            "broadVoteCount": broad_votes,
            "tightPassNonWorseVoteCount": tight_pass_votes,
            "broadPassNonWorseVoteCount": broad_pass_votes,
            "schemeSignatures": sigs,
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V68")

    out = {
        "schemaVersion": 68,
        "profileType": "v67-nonepass-training-edge-pressure-diagnostic",
        "diagnosticScope": "already-exposed-v67-nonepass-folds-only",
        "edgePressureCounts": dict(pressure_counts),
        "diagnostics": diagnostics,
        "v67ExtendedQOutcomesTaintedForSelection": True,
        "trainingSignalsOnlyUsedForEdgePressure": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 68,
        "diagnosticCount": len(diagnostics),
        "edgePressureCounts": dict(pressure_counts),
        "v67ExtendedQOutcomesTaintedForSelection": True,
        "trainingSignalsOnlyUsedForEdgePressure": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V67 NONE-PASS TRAINING EDGE PRESSURE V68 COMPLETE")
    print("Edge pressure counts:", dict(pressure_counts))
    for d in diagnostics:
        print("Failure", d["phase"], "fold", d["fold"],
              "V67", d["v67RecoveryClass"], d["v67PassingQRange"],
              "=> training", d["trainingEdgePressure"],
              "tightVotes", d["tightVoteCount"],
              "broadVotes", d["broadVoteCount"])
    print("V67 extended-q outcomes tainted for selection: True")
    print("Training signals only used for edge pressure: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
