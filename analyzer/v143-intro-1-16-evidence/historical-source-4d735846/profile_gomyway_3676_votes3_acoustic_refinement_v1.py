from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_recovery_precision_survivors_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONTEXT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
CONSENSUS_PATH = PUBLIC / "gomyway-3676-recovery-fold-consensus-prune-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-votes3-acoustic-refinement-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
TARGET_TRUE = 7
TARGET_FALSE = 31

recall = prof.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_key(row: dict[str, Any]) -> str:
    token = row.get("token")
    if isinstance(token, list) and len(token) == 3:
        return str(token)
    return str(token) if token is not None else f"m{int(row['measure'])}|s{int(row['step'])}|p{int(row['pitch'])}"


def bucket(v: float, cuts: list[float], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if v <= cut:
            return label
    return labels[-1]


def count_bucket(n: int) -> str:
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    if n == 2:
        return "2"
    if n <= 4:
        return "3_4"
    if n <= 8:
        return "5_8"
    return "9p"


def refine_signatures(row: dict[str, Any]) -> set[str]:
    amp = float(row.get("maxAmplitude", 0.0))
    mean = float(row.get("meanAmplitude", 0.0))
    err = float(row.get("minGridError", 9.0))
    dur = float(row.get("maxDuration", 0.0))
    persistence = int(row.get("sweepPersistence", 0))
    stems = int(row.get("stemCountAtWide", 0))
    strict = int(row.get("strictestSweepIndex", 9))
    step = int(row["step"])
    pitch = int(row["pitch"])
    reg = "low" if pitch < 48 else ("mid" if pitch < 60 else "high")

    ssp = count_bucket(int(row.get("sameStepPitchCount", 0)))
    sspc = count_bucket(int(row.get("sameStepPcCount", 0)))
    lex = count_bucket(int(row.get("localExactNeighborCount", 0)))
    lpc = count_bucket(int(row.get("localPcNeighborCount", 0)))
    ncp = count_bucket(int(row.get("neighborClosePitchCount", 0)))
    slot = count_bucket(int(row.get("sameSlotChampionPitchCount", 0)))
    rms = count_bucket(int(row.get("repeatMeasureSupport", 0)))
    rmpc = count_bucket(int(row.get("repeatMeasurePcSupport", 0)))
    chord = int(row.get("chordToneLike", 0))

    ab = bucket(amp, [0.035, 0.05, 0.075, 0.10, 0.15, 0.25, 9.0], ["a035", "a050", "a075", "a100", "a150", "a250", "a250p"])
    mb = bucket(mean, [0.025, 0.04, 0.06, 0.08, 0.12, 0.20, 9.0], ["m025", "m040", "m060", "m080", "m120", "m200", "m200p"])
    eb = bucket(err, [0.008, 0.015, 0.025, 0.040, 0.060, 0.085, 9.0], ["e008", "e015", "e025", "e040", "e060", "e085", "e100"])
    db = bucket(dur, [0.035, 0.055, 0.080, 0.120, 0.180, 0.300, 9.0], ["d035", "d055", "d080", "d120", "d180", "d300", "d300p"])

    amp_ratio = amp / max(mean, 1e-9)
    arb = bucket(amp_ratio, [1.05, 1.15, 1.30, 1.60, 2.20, 99.0], ["r105", "r115", "r130", "r160", "r220", "r220p"])

    return {
        f"v3AcousticAmp::{ab}",
        f"v3AcousticMean::{mb}",
        f"v3AcousticErr::{eb}",
        f"v3AcousticDur::{db}",
        f"v3AcousticRatio::{arb}",
        f"v3Detector::p{persistence}|s{stems}|i{strict}",
        f"v3Rhythm::q{step % 4}|par{step % 2}|{reg}",
        f"v3Cross::{ab}|{mb}|{eb}",
        f"v3Cross::{ab}|{db}|p{persistence}|s{stems}",
        f"v3Cross::{mb}|{eb}|i{strict}|{reg}",
        f"v3Cross::{arb}|{eb}|p{persistence}|s{stems}",
        f"v3Context::ssp{ssp}|pc{sspc}|lex{lex}|ncp{ncp}",
        f"v3Context::r{rms}|pc{rmpc}|slot{slot}|ch{chord}",
        f"v3AcousticContext::{ab}|{eb}|ssp{ssp}|pc{sspc}",
        f"v3AcousticContext::{mb}|{db}|lex{lex}|ncp{ncp}|{reg}",
        f"v3AcousticContext::{arb}|p{persistence}|r{rms}|slot{slot}|ch{chord}",
        f"v3AcousticContext::q{step % 4}|{eb}|ssp{ssp}|r{rms}|{reg}",
        f"v3AcousticContext::par{step % 2}|{ab}|pc{sspc}|ncp{ncp}|{reg}",
        f"v3AcousticContext::s{stems}|i{strict}|{mb}|r{rms}|pc{rmpc}",
        f"v3AcousticContext::{ab}|{mb}|{eb}|{db}|{reg}",
    }


def rank(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows = []
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


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not CONTEXT_PATH.exists() or not CONSENSUS_PATH.exists():
        raise RuntimeError("Missing prerequisite contextual or fold-consensus output")

    ctx = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    if abs(float(consensus.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    counts = tuple(int(x) for x in consensus.get("championMatchedMissingExtra", []))
    if counts != EXPECTED:
        raise RuntimeError(f"Expected champion {EXPECTED}, got {counts}")

    sweeps = consensus.get("consensusSweeps") or []
    sweep3 = next((r for r in sweeps if int(r.get("voteThreshold", -1)) == 3), None)
    if sweep3 is None:
        raise RuntimeError("Missing votes>=3 fold-consensus sweep")
    target_tokens = {str(t) for t in sweep3.get("tokens") or []}
    if len(target_tokens) != TARGET_TRUE + TARGET_FALSE:
        raise RuntimeError(f"Expected 38 votes>=3 target tokens, got {len(target_tokens)}")

    rows = list(ctx.get("candidateRows") or [])
    by_key = {token_key(r): r for r in rows}
    target_rows = [by_key[k] for k in target_tokens if k in by_key]
    if len(target_rows) != len(target_tokens):
        missing = sorted(target_tokens - set(by_key))[:10]
        raise RuntimeError(f"Could not map all votes>=3 tokens into contextual rows; missing={missing}")

    true_count = sum(1 for r in target_rows if str(r.get("label")) == "true")
    false_count = sum(1 for r in target_rows if str(r.get("label")) == "false")
    if (true_count, false_count) != (TARGET_TRUE, TARGET_FALSE):
        raise RuntimeError(f"Expected target pocket 7/31, got {true_count}/{false_count}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    enriched = []
    for row in target_rows:
        label = str(row["label"])
        sigs = sorted(refine_signatures(row))
        for sig in sigs:
            groups[sig][label] += 1
        enriched.append({
            "token": row.get("token"),
            "measure": int(row["measure"]),
            "step": int(row["step"]),
            "pitch": int(row["pitch"]),
            "label": label,
            "maxAmplitude": row.get("maxAmplitude"),
            "meanAmplitude": row.get("meanAmplitude"),
            "minGridError": row.get("minGridError"),
            "maxDuration": row.get("maxDuration"),
            "sweepPersistence": row.get("sweepPersistence"),
            "stemCountAtWide": row.get("stemCountAtWide"),
            "strictestSweepIndex": row.get("strictestSweepIndex"),
            "signatures": sigs,
        })

    ranked = rank(groups)
    zero3 = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 3]
    zero2 = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 2]
    near = [r for r in ranked if int(r["true"]) <= 1 and int(r["false"]) >= 5]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during votes3 acoustic refinement")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-votes3-acoustic-refinement",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "targetTrue": true_count,
        "targetFalse": false_count,
        "zeroPrecisionMin3False": zero3,
        "zeroPrecisionMin2False": zero2,
        "nearZeroMax1TrueMin5False": near,
        "rankedSignatures": ranked,
        "targetRows": enriched,
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
        "championPitchF1": EXPECTED_F1,
        "targetTrue": true_count,
        "targetFalse": false_count,
        "zeroPrecisionMin3Count": len(zero3),
        "zeroPrecisionMin2Count": len(zero2),
        "nearZeroCount": len(near),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 VOTES3 ACOUSTIC REFINEMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Target votes>=3 true/false:", true_count, "/", false_count)
    print("Zero-precision acoustic/context signatures (3+ false, 0 true):", len(zero3))
    for r in zero3[:40]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("Zero-precision signatures (2+ false, 0 true):", len(zero2))
    print("Near-zero signatures (5+ false, <=1 true):", len(near))
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
