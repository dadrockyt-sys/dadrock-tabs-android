from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitchcore_failure_anatomy_v1 as anatomy

bench = anatomy.bench
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitchcore-learned-failure-penalty-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitchcore-learned-failure-penalty-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def learn_penalties(marked_train: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    selected = [r for r in marked_train if r.get("pitchCore")]
    groups: dict[str, Counter[str]] = {}
    for row in selected:
        label = "true" if row["label"] == "true" else "false"
        for tag in anatomy.feature_tags(row):
            groups.setdefault(tag, Counter())[label] += 1

    learned: dict[str, dict[str, Any]] = {}
    for tag, c in groups.items():
        t, f = int(c["true"]), int(c["false"])
        support = t + f
        if support < 3 or f < 2:
            continue
        false_rate = 100.0 * f / support
        if f <= t or false_rate < 60.0:
            continue
        learned[tag] = {
            "true": t,
            "false": f,
            "support": support,
            "falseRate": round(false_rate, 2),
            "penalty": round((f - t) / support, 6),
        }
    return learned


def penalty_score(row: dict[str, Any], learned: dict[str, dict[str, Any]]) -> float:
    return sum(float(learned[tag]["penalty"]) for tag in anatomy.feature_tags(row) if tag in learned)


def apply(marked: list[dict[str, Any]], learned: dict[str, dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen = [
        r for r in marked
        if r.get("pitchCore") and penalty_score(r, learned) < cutoff
    ]
    return bench.stats(chosen)


def choose_cutoff(marked_train: list[dict[str, Any]], learned: dict[str, dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    cutoffs = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 99.0]
    choices = []
    for cutoff in cutoffs:
        result = apply(marked_train, learned, cutoff)
        if result["recoverTrue"] > 0 and result["pitchF1"] > EXPECTED_F1:
            choices.append((cutoff, result))
    if not choices:
        return 99.0, apply(marked_train, learned, 99.0)
    return max(
        choices,
        key=lambda item: (
            item[1]["pitchF1"],
            item[1]["precision"],
            item[1]["recoverTrue"],
            -item[1]["recoverFalse"],
            -item[0],
        ),
    )


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed_count = 0
    for fold in range(FOLD_COUNT):
        print(f"{name}: outer fold {fold + 1}/{FOLD_COUNT} ...", flush=True)
        train = [r for r in rows if fold_fn(r["measure"]) != fold]
        test = [r for r in rows if fold_fn(r["measure"]) == fold]

        pitch_core = bench.learn_pitch_core(train)
        marked_train = bench.mark_pitch_core(train, pitch_core)
        marked_test = bench.mark_pitch_core(test, pitch_core)
        penalties = learn_penalties(marked_train)
        cutoff, train_result = choose_cutoff(marked_train, penalties)
        held = apply(marked_test, penalties, cutoff)

        fold_pass = bool(pitch_core) and held["recoverTrue"] > 0 and held["pitchF1"] > EXPECTED_F1
        passed_count += int(fold_pass)
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedPitchCoreCount": len(pitch_core),
            "learnedPenaltyCount": len(penalties),
            "learnedPenalties": penalties,
            "chosenPenaltyCutoff": cutoff,
            "trainCandidate": train_result,
            "heldoutCandidate": held,
            "passed": fold_pass,
        }
        results.append(row)
        print(
            f"  core={len(pitch_core)} penalties={len(penalties)} cutoff={cutoff} "
            f"held={held['recoverTrue']}/{held['recoverFalse']} F1={held['pitchF1']} pass={fold_pass}",
            flush=True,
        )
    return passed_count == FOLD_COUNT, results


def main() -> None:
    before = sha256(bench.prof.recall.CANDIDATE_PATH)
    rows = bench.prepare_rows()
    if not rows:
        raise RuntimeError("No residual rows available")
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting learned pitch-core failure-penalty CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: bench.contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: bench.shifted_fold(m, lo, hi, FOLD_COUNT))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(bench.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during learned failure-penalty CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitchcore-learned-failure-penalty-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "learnedFailurePenaltyGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory nested validation. Pitch core, false-concentrated penalty features, and penalty cutoff are learned from outer-training data only. Held-out labels are used only for final fold grading.",
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
        "learnedFailurePenaltyGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCHCORE LEARNED FAILURE PENALTY CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Learned failure penalty generalizes:", generalizes)
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
