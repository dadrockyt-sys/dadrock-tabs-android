from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_3161_wide_recall_contextual_consensus_recovery_cv_v1 as cv

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CV_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-consensus-recovery-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-recovery-precision-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-recovery-precision-survivors-v1-manifest.json"
EXPECTED_OLD = (183, 684, 108)
EXPECTED_NEW = (272, 595, 341)
EXPECTED_NEW_F1 = 36.76

recall = cv.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig, c in groups.items():
        true = int(c["true"])
        false = int(c["false"])
        total = true + false
        rows.append({
            "signature": sig,
            "true": true,
            "false": false,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (int(r["true"]), -int(r["false"]), str(r["signature"])))


def extra_cleanup_signatures(row: dict[str, Any], weight: float, votes: int) -> set[str]:
    step = int(row["step"])
    pitch = int(row["pitch"])
    reg = "low" if pitch < 48 else ("mid" if pitch < 60 else "high")
    p = int(row.get("sweepPersistence", 0))
    stems = int(row.get("stemCountAtWide", 0))
    strict = int(row.get("strictestSweepIndex", 9))
    ssp = int(row.get("sameStepPitchCount", 0))
    sspc = int(row.get("sameStepPcCount", 0))
    lex = int(row.get("localExactNeighborCount", 0))
    ncp = int(row.get("neighborClosePitchCount", 0))
    rms = int(row.get("repeatMeasureSupport", 0))
    rmpc = int(row.get("repeatMeasurePcSupport", 0))
    slot = int(row.get("sameSlotChampionPitchCount", 0))
    chord = int(row.get("chordToneLike", 0))

    wb = "w08_12" if weight < 1.2 else ("w12_18" if weight < 1.8 else ("w18_25" if weight < 2.5 else "w25p"))
    vb = "v1_2" if votes <= 2 else ("v3_4" if votes <= 4 else ("v5_7" if votes <= 7 else "v8p"))
    sspb = "0" if ssp == 0 else ("1_2" if ssp <= 2 else ("3_5" if ssp <= 5 else "6p"))
    pcb = "0" if sspc == 0 else ("1_2" if sspc <= 2 else ("3_5" if sspc <= 5 else "6p"))
    nb = "0" if ncp == 0 else ("1_2" if ncp <= 2 else "3p")
    rb = "0" if rms == 0 else ("1" if rms == 1 else "2p")
    rpcb = "0" if rmpc == 0 else ("1" if rmpc == 1 else "2p")

    return {
        f"recWeight::{wb}",
        f"recVotes::{vb}",
        f"recWeightVotes::{wb}|{vb}",
        f"recDetector::p{p}|s{stems}|i{strict}",
        f"recRhythm::q{step % 4}|par{step % 2}|{reg}",
        f"recSameStep::{sspb}|pc{pcb}|{reg}",
        f"recNeighbor::lex{lex}|ncp{nb}|{reg}",
        f"recRepeat::r{rb}|pc{rpcb}|{reg}",
        f"recSlot::slot{slot}|ch{chord}|{reg}",
        f"recCross::{wb}|{vb}|p{p}|s{stems}",
        f"recCross::{wb}|ssp{sspb}|pc{pcb}|{reg}",
        f"recCross::{vb}|ncp{nb}|r{rb}|pc{rpcb}",
        f"recCross::q{step % 4}|ssp{sspb}|ncp{nb}|slot{slot}",
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists() or not CV_PATH.exists():
        raise RuntimeError("Missing prerequisite contextual recovery outputs")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    cvdata = json.loads(CV_PATH.read_text(encoding="utf-8"))
    if cvdata.get("validatedNewChampion") is not True:
        raise RuntimeError("36.76 recovery candidate is not validated")

    full = cvdata.get("fullDataBestCandidate") or {}
    new_counts = tuple(int(x) for x in full.get("matchedMissingExtra", []))
    if new_counts != EXPECTED_NEW or abs(float(full.get("candidatePitchF1", -1)) - EXPECTED_NEW_F1) > 0.01:
        raise RuntimeError(f"Expected validated 36.76 champion {EXPECTED_NEW}, got {new_counts}/{full.get('candidatePitchF1')}")

    rows = list(data.get("candidateRows") or [])
    stats = cv.signature_stats(rows)
    selected = cv.select_broad(stats, 1.0)
    chosen_cutoff = float(full["cutoff"])

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    chosen_rows: list[dict[str, Any]] = []
    true_count = false_count = 0

    for row in rows:
        hits = []
        weight = 0.0
        for sig in row.get("signatures") or []:
            sr = selected.get(str(sig))
            if sr is None:
                continue
            hits.append(str(sig))
            weight += float(sr["precision"]) / 100.0
        if weight < chosen_cutoff:
            continue
        label = str(row.get("label"))
        if label == "true":
            true_count += 1
        else:
            false_count += 1
        sigs = set(str(s) for s in row.get("signatures") or [])
        sigs.update(extra_cleanup_signatures(row, weight, len(hits)))
        for sig in sigs:
            groups[sig][label] += 1
        chosen_rows.append({
            "token": row.get("token"),
            "measure": row.get("measure"),
            "step": row.get("step"),
            "pitch": row.get("pitch"),
            "label": label,
            "recoveryWeight": round(weight, 4),
            "recoveryVotes": len(hits),
            "signatures": sorted(sigs),
        })

    if (true_count, false_count) != (89, 233):
        raise RuntimeError(f"Expected selected recovery 89/233, got {true_count}/{false_count}")

    ranked = rank(groups)
    zero5 = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero3 = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 3]
    near = [r for r in ranked if int(r["true"]) <= 1 and int(r["false"]) >= 8]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 36.76 precision survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-recovery-precision-survivors",
        "championPitchF1": EXPECTED_NEW_F1,
        "championMatchedMissingExtra": list(EXPECTED_NEW),
        "recoveryCutoff": chosen_cutoff,
        "selectedRecoveryTrue": true_count,
        "selectedRecoveryFalse": false_count,
        "zeroPrecisionSignaturesMin5False": zero5,
        "zeroPrecisionSignaturesMin3False": zero3,
        "nearZeroSignaturesMax1TrueMin8False": near,
        "rankedSignatures": ranked,
        "selectedRecoveryRows": chosen_rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "championPitchF1": EXPECTED_NEW_F1,
        "championMatchedMissingExtra": list(EXPECTED_NEW),
        "zeroPrecisionMin5Count": len(zero5),
        "zeroPrecisionMin3Count": len(zero3),
        "nearZeroCount": len(near),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RECOVERY PRECISION SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_NEW_F1)
    print("Champion matched/missing/extra:", *EXPECTED_NEW)
    print("Selected recovery true/false:", true_count, "/", false_count)
    print("Zero-precision signatures (5+ false, 0 true):", len(zero5))
    for r in zero5[:40]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("Zero-precision signatures (3+ false, 0 true):", len(zero3))
    print("Near-zero signatures (8+ false, <=1 true):", len(near))
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
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
