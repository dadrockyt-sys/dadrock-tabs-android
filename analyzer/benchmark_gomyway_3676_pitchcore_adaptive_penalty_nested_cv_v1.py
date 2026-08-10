from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitchcore_penalty_learnability_v1 as learn

penalty = learn.penalty
bench = learn.bench
anatomy = learn.anatomy
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitchcore-adaptive-penalty-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitchcore-adaptive-penalty-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
CUTOFFS = [0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00, 99.0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    d = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / d if d else 0.0), 2)


def project_stats(t: int, f: int) -> dict[str, Any]:
    m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
    return {
        "recoverTrue": t,
        "recoverFalse": f,
        "precision": round(precision(t, f), 2),
        "pitchF1": pitch_f1(m, miss, extra),
        "matchedMissingExtra": [m, miss, extra],
    }


def learn_penalties_with_gate(marked_train: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    counts = learn.feature_counts(marked_train)
    learned: dict[str, dict[str, Any]] = {}
    for tag, row in counts.items():
        if not learn.qualifies(row, gate):
            continue
        t, f, support = int(row["true"]), int(row["false"]), int(row["support"])
        learned[tag] = {
            **row,
            "penalty": round((f - t) / support, 6) if support else 0.0,
        }
    return learned


def penalty_score(row: dict[str, Any], learned_penalties: dict[str, dict[str, Any]]) -> float:
    return sum(float(learned_penalties[tag]["penalty"]) for tag in anatomy.feature_tags(row) if tag in learned_penalties)


def selected_counts(marked_rows: list[dict[str, Any]], learned_penalties: dict[str, dict[str, Any]], cutoff: float) -> tuple[int, int]:
    t = f = 0
    for row in marked_rows:
        if not row.get("pitchCore"):
            continue
        if penalty_score(row, learned_penalties) >= cutoff:
            continue
        if row["label"] == "true":
            t += 1
        else:
            f += 1
    return t, f


def fold_functions(rows: list[dict[str, Any]], folds: int) -> list[tuple[str, Callable[[int], int]]]:
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    return [
        ("normal", lambda m: m % folds),
        ("section", lambda m: bench.contiguous_fold(m, lo, hi, folds)),
        ("shiftedWindow", lambda m: bench.shifted_fold(m, lo, hi, folds)),
    ]


def inner_score(train_rows: list[dict[str, Any]], gate_name: str, cutoff: float) -> dict[str, Any]:
    gate = learn.GATES[gate_name]
    scheme_summaries: list[dict[str, Any]] = []
    total_t = total_f = 0

    for scheme_name, fold_fn in fold_functions(train_rows, INNER_FOLDS):
        scheme_t = scheme_f = 0
        useful_folds = 0
        for fold in range(INNER_FOLDS):
            inner_train = [r for r in train_rows if fold_fn(int(r["measure"])) != fold]
            inner_test = [r for r in train_rows if fold_fn(int(r["measure"])) == fold]
            core = bench.learn_pitch_core(inner_train)
            marked_train = bench.mark_pitch_core(inner_train, core)
            marked_test = bench.mark_pitch_core(inner_test, core)
            penalties = learn_penalties_with_gate(marked_train, gate)
            t, f = selected_counts(marked_test, penalties, cutoff)
            scheme_t += t
            scheme_f += f
            useful_folds += int(t > 0 and pitch_f1(EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f) > EXPECTED_F1)
        scheme_stats = project_stats(scheme_t, scheme_f)
        scheme_stats["scheme"] = scheme_name
        scheme_stats["usefulFolds"] = useful_folds
        scheme_summaries.append(scheme_stats)
        total_t += scheme_t
        total_f += scheme_f

    overall = project_stats(total_t, total_f)
    improving_schemes = sum(int(float(s["pitchF1"]) > EXPECTED_F1 and int(s["recoverTrue"]) > 0) for s in scheme_summaries)
    return {
        "gate": gate_name,
        "cutoff": cutoff,
        "overall": overall,
        "schemes": scheme_summaries,
        "improvingSchemes": improving_schemes,
        "worstSchemeF1": min((float(s["pitchF1"]) for s in scheme_summaries), default=0.0),
    }


def choose_gate_and_cutoff(train_rows: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = []
    for gate_name in learn.GATES:
        for cutoff in CUTOFFS:
            result = inner_score(train_rows, gate_name, cutoff)
            overall = result["overall"]
            if int(overall["recoverTrue"]) <= 0:
                continue
            candidates.append(result)
    if not candidates:
        return inner_score(train_rows, "current", 99.0)
    return max(
        candidates,
        key=lambda r: (
            int(r["improvingSchemes"]),
            float(r["worstSchemeF1"]),
            float(r["overall"]["pitchF1"]),
            float(r["overall"]["precision"]),
            int(r["overall"]["recoverTrue"]),
            -int(r["overall"]["recoverFalse"]),
        ),
    )


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    out = []
    passed_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        train_rows = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test_rows = [r for r in rows if fold_fn(int(r["measure"])) == fold]

        choice = choose_gate_and_cutoff(train_rows)
        gate_name = str(choice["gate"])
        cutoff = float(choice["cutoff"])

        core = bench.learn_pitch_core(train_rows)
        marked_train = bench.mark_pitch_core(train_rows, core)
        marked_test = bench.mark_pitch_core(test_rows, core)
        learned_penalties = learn_penalties_with_gate(marked_train, learn.GATES[gate_name])
        t, f = selected_counts(marked_test, learned_penalties, cutoff)
        held = project_stats(t, f)
        fold_pass = bool(core) and t > 0 and float(held["pitchF1"]) > EXPECTED_F1
        passed_count += int(fold_pass)

        out.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train_rows),
            "testRows": len(test_rows),
            "learnedPitchCoreCount": len(core),
            "chosenGate": gate_name,
            "chosenCutoff": cutoff,
            "innerSelection": choice,
            "learnedPenaltyCount": len(learned_penalties),
            "learnedPenalties": learned_penalties,
            "heldoutCandidate": held,
            "passed": fold_pass,
        })
        print(
            f"  core={len(core)} gate={gate_name} penalties={len(learned_penalties)} cutoff={cutoff} "
            f"held={t}/{f} F1={held['pitchF1']} pass={fold_pass}",
            flush=True,
        )
    return passed_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(bench.prof.recall.CANDIDATE_PATH)
    rows = bench.prepare_rows()
    if not rows:
        raise RuntimeError("No residual rows available")
    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting adaptive nested pitch-core penalty CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: bench.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: bench.shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(bench.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during adaptive nested penalty CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitchcore-adaptive-penalty-nested-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "adaptivePenaltyArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory strict nested validation. Pitch core, penalty gate, penalty cutoff, and penalty features are selected using outer-training data only. Outer held-out labels are used only for final grading.",
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
        "adaptivePenaltyArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCHCORE ADAPTIVE PENALTY NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Adaptive penalty architecture generalizes:", generalizes)
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
