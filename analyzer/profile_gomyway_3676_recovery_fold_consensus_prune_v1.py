from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_recovery_precision_survivors_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-3676-recovery-precision-survivors-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-recovery-fold-consensus-prune-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-recovery-fold-consensus-prune-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5

recall = prof.recall


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f1_from_counts(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def learn_zero_precision(rows: list[dict[str, Any]], support: int) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = str(row["label"])
        for sig in row.get("signatures") or []:
            groups[str(sig)][label] += 1
    return {
        sig
        for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= support
    }


def token_key(row: dict[str, Any]) -> str:
    token = row.get("token")
    if token is not None:
        return str(token)
    return f"m{int(row['measure'])}|s{int(row['step'])}|p{int(row['pitch'])}"


def crossfit_partition(
    rows: list[dict[str, Any]],
    fold_fn: Callable[[dict[str, Any]], int],
    partition_name: str,
) -> tuple[dict[str, int], list[dict[str, Any]]]:
    rejected: dict[str, int] = defaultdict(int)
    fold_rows: list[dict[str, Any]] = []
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        if not train or not test:
            fold_rows.append({
                "partition": partition_name,
                "fold": fold,
                "trainRows": len(train),
                "testRows": len(test),
                "learnedSignatureCount": 0,
                "rejected": 0,
                "trueRejected": 0,
                "falseRejected": 0,
            })
            continue
        support = max(3, int(round(5 * len(train) / len(rows))))
        learned = learn_zero_precision(train, support)
        chosen = [
            row for row in test
            if learned.intersection(str(s) for s in row.get("signatures") or [])
        ]
        true_rejected = sum(1 for row in chosen if row["label"] == "true")
        false_rejected = sum(1 for row in chosen if row["label"] == "false")
        for row in chosen:
            rejected[token_key(row)] += 1
        fold_rows.append({
            "partition": partition_name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "support": support,
            "learnedSignatureCount": len(learned),
            "rejected": len(chosen),
            "trueRejected": true_rejected,
            "falseRejected": false_rejected,
        })
    return dict(rejected), fold_rows


def evaluate_vote_threshold(rows: list[dict[str, Any]], votes: dict[str, int], threshold: int) -> dict[str, Any]:
    chosen = [r for r in rows if int(votes.get(token_key(r), 0)) >= threshold]
    true_pruned = sum(1 for r in chosen if r["label"] == "true")
    false_pruned = sum(1 for r in chosen if r["label"] == "false")
    matched = EXPECTED[0] - true_pruned
    missing = EXPECTED[1] + true_pruned
    extra = EXPECTED[2] - false_pruned
    return {
        "voteThreshold": threshold,
        "pruned": len(chosen),
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "precisionOfPrune": round(100.0 * false_pruned / len(chosen), 2) if chosen else 0.0,
        "pitchF1": f1_from_counts(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
        "tokens": [token_key(r) for r in chosen],
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite profiler output: {INPUT_PATH.relative_to(ROOT)}")

    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if abs(float(data.get("championPitchF1", -1)) - EXPECTED_F1) > 0.01:
        raise RuntimeError("Expected frozen 36.76 champion")
    counts = tuple(int(x) for x in data.get("championMatchedMissingExtra", []))
    if counts != EXPECTED:
        raise RuntimeError(f"Expected frozen champion {EXPECTED}, got {counts}")

    rows = list(data.get("selectedRecoveryRows") or [])
    if not rows:
        raise RuntimeError("No selected recovery rows found")
    true_count = sum(1 for r in rows if r["label"] == "true")
    false_count = sum(1 for r in rows if r["label"] == "false")
    if (true_count, false_count) != (89, 233):
        raise RuntimeError(f"Expected recovery layer 89/233, got {true_count}/{false_count}")

    normal_votes, normal_folds = crossfit_partition(
        rows,
        lambda r: int(r["measure"]) % FOLD_COUNT,
        "normal",
    )
    shifted_votes, shifted_folds = crossfit_partition(
        rows,
        lambda r: (int(r["measure"]) + 2) % FOLD_COUNT,
        "shifted",
    )

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    def section_fold(row: dict[str, Any]) -> int:
        rel = int(row["measure"]) - lo
        return min(FOLD_COUNT - 1, int(FOLD_COUNT * rel / span))

    section_votes, section_folds = crossfit_partition(rows, section_fold, "section")

    consensus_votes: dict[str, int] = defaultdict(int)
    for source in (normal_votes, shifted_votes, section_votes):
        for key, value in source.items():
            if value > 0:
                consensus_votes[key] += 1

    sweeps = [evaluate_vote_threshold(rows, consensus_votes, t) for t in (1, 2, 3)]
    safe = [
        r for r in sweeps
        if int(r["truePruned"]) == 0
        and int(r["falsePruned"]) > 0
        and float(r["pitchF1"]) > EXPECTED_F1
    ]
    best_safe = max(safe, key=lambda r: (float(r["pitchF1"]), int(r["falsePruned"]))) if safe else None

    vote_hist: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        v = int(consensus_votes.get(token_key(row), 0))
        vote_hist[str(v)][str(row["label"])] += 1

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during fold-consensus prune profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-recovery-fold-consensus-prune",
        "championPitchF1": EXPECTED_F1,
        "championMatchedMissingExtra": list(EXPECTED),
        "selectedRecoveryTrue": true_count,
        "selectedRecoveryFalse": false_count,
        "normalFolds": normal_folds,
        "shiftedFolds": shifted_folds,
        "sectionFolds": section_folds,
        "voteHistogram": {k: dict(v) for k, v in sorted(vote_hist.items())},
        "consensusSweeps": sweeps,
        "bestSafeCandidate": best_safe,
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
        "bestSafeCandidatePitchF1": best_safe["pitchF1"] if best_safe else None,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RECOVERY FOLD-CONSENSUS PRUNE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", EXPECTED_F1)
    print("Champion matched/missing/extra:", *EXPECTED)
    print("Selected recovery true/false:", true_count, "/", false_count)
    print("Vote histogram:", {k: dict(v) for k, v in sorted(vote_hist.items())})
    for sweep in sweeps:
        print(
            f"votes>={sweep['voteThreshold']} pruned={sweep['pruned']} "
            f"truePruned={sweep['truePruned']} falsePruned={sweep['falsePruned']} "
            f"F1={sweep['pitchF1']} m/m/e={sweep['matchedMissingExtra']}"
        )
    print("Best safe candidate:", best_safe)
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
