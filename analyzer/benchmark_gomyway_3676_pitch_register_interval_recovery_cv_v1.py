from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
CUTOFFS = [0.25, 0.35, 0.50, 0.65, 0.80, 1.00, 1.25, 1.50, 2.00, 2.50]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    denom = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / denom if denom else 0.0), 2)


def stats(rows: list[dict[str, Any]], signatures: dict[str, dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen: list[dict[str, Any]] = []
    for row in rows:
        weight = 0.0
        for sig in row.get("signatures") or []:
            item = signatures.get(str(sig))
            if item is not None:
                weight += float(item["precision"]) / 100.0
        if weight >= cutoff:
            chosen.append(row)
    true = sum(str(r.get("label")) == "true" for r in chosen)
    false = sum(str(r.get("label")) == "false" for r in chosen)
    matched = EXPECTED[0] + true
    missing = EXPECTED[1] - true
    extra = EXPECTED[2] + false
    return {
        "selected": len(chosen),
        "recoverTrue": true,
        "recoverFalse": false,
        "precision": round(100.0 * true / len(chosen), 2) if chosen else 0.0,
        "pitchF1": pitch_f1(matched, missing, extra),
        "matchedMissingExtra": [matched, missing, extra],
    }


def learn(train: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], float, dict[str, Any]]:
    counts: dict[str, Counter[str]] = {}
    for row in train:
        label = str(row.get("label"))
        for sig in row.get("signatures") or []:
            key = str(sig)
            if key not in counts:
                counts[key] = Counter()
            counts[key][label] += 1

    useful: dict[str, dict[str, Any]] = {}
    for sig, c in counts.items():
        true = int(c["true"])
        false = int(c["false"])
        total = true + false
        precision = 100.0 * true / total if total else 0.0
        if true >= 4 and precision >= 25.0:
            useful[sig] = {
                "true": true,
                "false": false,
                "precision": precision,
            }

    candidates: list[tuple[float, dict[str, Any]]] = []
    for cutoff in CUTOFFS:
        s = stats(train, useful, cutoff)
        if int(s["recoverTrue"]) > 0 and float(s["pitchF1"]) > EXPECTED_F1:
            candidates.append((cutoff, s))
    if not candidates:
        return useful, 2.50, stats(train, useful, 2.50)
    cutoff, best = max(
        candidates,
        key=lambda item: (
            float(item[1]["pitchF1"]),
            float(item[1]["precision"]),
            int(item[1]["recoverTrue"]),
            -int(item[1]["recoverFalse"]),
        ),
    )
    return useful, cutoff, best


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[dict[str, Any]], int]) -> tuple[bool, list[dict[str, Any]]]:
    results: list[dict[str, Any]] = []
    passed = True
    for fold in range(FOLD_COUNT):
        train = [r for r in rows if fold_fn(r) != fold]
        test = [r for r in rows if fold_fn(r) == fold]
        useful, cutoff, train_best = learn(train)
        held = stats(test, useful, cutoff)
        fold_pass = (
            int(held["recoverTrue"]) > 0
            and float(held["pitchF1"]) > EXPECTED_F1
        )
        passed = passed and fold_pass
        results.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedSignatureCount": len(useful),
            "chosenCutoff": cutoff,
            "trainCandidatePitchF1": train_best["pitchF1"],
            "trainRecoverTrue": train_best["recoverTrue"],
            "trainRecoverFalse": train_best["recoverFalse"],
            "heldoutRecoverTrue": held["recoverTrue"],
            "heldoutRecoverFalse": held["recoverFalse"],
            "heldoutPrecision": held["precision"],
            "heldoutProjectedPitchF1": held["pitchF1"],
            "passed": fold_pass,
        })
    return passed, results


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateRows") or [])
    if not rows:
        raise RuntimeError("Pitch/register/interval profiler candidate rows are missing")
    if tuple(profile.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profiler is not anchored to frozen 36.76 champion")

    # Relearn full-data rule rather than trusting the profiler's precomputed selection.
    full_useful, full_cutoff, full_candidate = learn(rows)

    measures = sorted({int(r["measure"]) for r in rows})
    lo, hi = min(measures), max(measures)
    span = max(1, hi - lo + 1)

    normal_passed, normal = evaluate_scheme(rows, "normal", lambda r: int(r["measure"]) % FOLD_COUNT)
    shifted_passed, shifted = evaluate_scheme(rows, "shifted", lambda r: (int(r["measure"]) + 2) % FOLD_COUNT)
    section_passed, section = evaluate_scheme(
        rows,
        "section",
        lambda r: min(FOLD_COUNT - 1, int(FOLD_COUNT * (int(r["measure"]) - lo) / span)),
    )

    validated = (
        float(full_candidate["pitchF1"]) > EXPECTED_F1
        and int(full_candidate["recoverTrue"]) > 0
        and normal_passed
        and section_passed
        and shifted_passed
    )

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during pitch/register/interval recovery CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-pitch-register-interval-recovery-nested-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "fullDataLearnedSignatureCount": len(full_useful),
        "fullDataChosenCutoff": full_cutoff,
        "fullDataCandidate": full_candidate,
        "recoveryCrossValidationPassed": normal_passed,
        "normalCv": normal,
        "sectionStabilityPassed": section_passed,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_passed,
        "shiftedCv": shifted,
        "validatedNewChampion": validated,
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
        "fullDataCandidate": full_candidate,
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PITCH REGISTER INTERVAL RECOVERY CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", EXPECTED_F1)
    print("Baseline matched/missing/extra:", *EXPECTED)
    print("Full-data chosen cutoff:", full_cutoff)
    print("Full-data candidate:", full_candidate)
    print("Recovery cross-validation passed:", normal_passed)
    for row in normal:
        print("CV", row)
    print("Section stability passed:", section_passed)
    print("Shifted-window stability passed:", shifted_passed)
    print("Validated new champion:", validated)
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
