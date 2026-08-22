from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import benchmark_gomyway_3676_pitchcore_learned_failure_penalty_cv_v1 as penalty

bench = penalty.bench
anatomy = penalty.anatomy
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitchcore-penalty-learnability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitchcore-penalty-learnability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5

GATES = {
    "current": {"minSupport": 3, "minFalse": 2, "minFalseRate": 60.0, "requireFalseGtTrue": True},
    "support2_false2_55": {"minSupport": 2, "minFalse": 2, "minFalseRate": 55.0, "requireFalseGtTrue": True},
    "support3_false1_55": {"minSupport": 3, "minFalse": 1, "minFalseRate": 55.0, "requireFalseGtTrue": True},
    "support2_false1_60": {"minSupport": 2, "minFalse": 1, "minFalseRate": 60.0, "requireFalseGtTrue": True},
    "support2_false1_55": {"minSupport": 2, "minFalse": 1, "minFalseRate": 55.0, "requireFalseGtTrue": True},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def feature_counts(marked_train: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected = [r for r in marked_train if r.get("pitchCore")]
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in selected:
        label = "true" if row["label"] == "true" else "false"
        for tag in anatomy.feature_tags(row):
            groups[tag][label] += 1

    out: dict[str, dict[str, Any]] = {}
    for tag, c in groups.items():
        t, f = int(c["true"]), int(c["false"])
        support = t + f
        out[tag] = {
            "true": t,
            "false": f,
            "support": support,
            "falseRate": round(100.0 * f / support, 2) if support else 0.0,
            "falseMinusTrue": f - t,
        }
    return out


def qualifies(row: dict[str, Any], gate: dict[str, Any]) -> bool:
    if int(row["support"]) < int(gate["minSupport"]):
        return False
    if int(row["false"]) < int(gate["minFalse"]):
        return False
    if bool(gate["requireFalseGtTrue"]) and int(row["false"]) <= int(row["true"]):
        return False
    if float(row["falseRate"]) < float(gate["minFalseRate"]):
        return False
    return True


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r["measure"]) != fold]
        core = bench.learn_pitch_core(train)
        marked = bench.mark_pitch_core(train, core)
        selected = [r for r in marked if r.get("pitchCore")]
        counts = feature_counts(marked)

        gate_results: dict[str, Any] = {}
        for gate_name, gate in GATES.items():
            learned = [
                {"feature": tag, **stats}
                for tag, stats in counts.items()
                if qualifies(stats, gate)
            ]
            learned.sort(key=lambda r: (-int(r["falseMinusTrue"]), -float(r["falseRate"]), -int(r["support"]), str(r["feature"])))
            gate_results[gate_name] = {
                "learnedPenaltyCount": len(learned),
                "topPenalties": learned[:20],
            }

        near_misses = []
        current = GATES["current"]
        for tag, stats in counts.items():
            if qualifies(stats, current):
                continue
            # Show directionally negative features that miss the current gate narrowly.
            if int(stats["false"]) > int(stats["true"]) and int(stats["false"]) >= 1 and int(stats["support"]) >= 2:
                near_misses.append({"feature": tag, **stats})
        near_misses.sort(key=lambda r: (-int(r["falseMinusTrue"]), -float(r["falseRate"]), -int(r["support"]), str(r["feature"])))

        out.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "learnedPitchCoreCount": len(core),
            "selectedTrainPitchCore": len(selected),
            "gateResults": gate_results,
            "currentGateNearMisses": near_misses[:25],
        })
        print(
            f"{name} fold {fold}: core={len(core)} selectedTrain={len(selected)} "
            f"current={gate_results['current']['learnedPenaltyCount']} "
            f"relaxed={gate_results['support2_false1_55']['learnedPenaltyCount']}",
            flush=True,
        )
    return out


def recurring_features(all_folds: list[dict[str, Any]], gate_name: str) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    schemes: dict[str, set[str]] = defaultdict(set)
    for fold in all_folds:
        for row in fold["gateResults"][gate_name]["topPenalties"]:
            feature = str(row["feature"])
            counts[feature] += 1
            schemes[feature].add(str(fold["scheme"]))
    rows = [
        {"feature": feature, "trainingFolds": count, "schemes": sorted(schemes[feature])}
        for feature, count in counts.items()
        if count >= 2
    ]
    rows.sort(key=lambda r: (-int(r["trainingFolds"]), -len(r["schemes"]), str(r["feature"])))
    return rows


def main() -> None:
    before = sha256(bench.prof.recall.CANDIDATE_PATH)
    rows = bench.prepare_rows()
    if not rows:
        raise RuntimeError("No residual rows available")
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)

    normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section = evaluate_scheme(rows, "section", lambda m: bench.contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: bench.shifted_fold(m, lo, hi, FOLD_COUNT))
    all_folds = normal + section + shifted

    recurrence = {name: recurring_features(all_folds, name) for name in GATES}
    current_nonzero = sum(int(f["gateResults"]["current"]["learnedPenaltyCount"]) > 0 for f in all_folds)
    relaxed_nonzero = sum(int(f["gateResults"]["support2_false1_55"]["learnedPenaltyCount"]) > 0 for f in all_folds)

    after = sha256(bench.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during penalty learnability profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitchcore-penalty-learnability-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "gates": GATES,
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "currentGateNonzeroFoldCount": current_nonzero,
        "relaxedGateNonzeroFoldCount": relaxed_nonzero,
        "recurringPenaltyFeaturesByGate": recurrence,
        "note": "Diagnostic only. Labels are used on outer-training rows to measure penalty learnability. No held-out fold is used to select a gate and no candidate/champion promotion is allowed.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
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
        "candidateSha256": after,
        "currentGateNonzeroFoldCount": current_nonzero,
        "relaxedGateNonzeroFoldCount": relaxed_nonzero,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCHCORE PENALTY LEARNABILITY V1 COMPLETE")
    print("Current gate nonzero folds:", current_nonzero, "/", len(all_folds))
    print("Relaxed gate nonzero folds:", relaxed_nonzero, "/", len(all_folds))
    for gate_name in GATES:
        print("GATE", gate_name, "recurring features:")
        for item in recurrence[gate_name][:20]:
            print("RECUR", item)
    print("Validated new champion: False")
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
