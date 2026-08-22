from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_onset_slot_stability_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-onset-slot-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
INNER_FOLDS = 4
CUTOFFS = [0.35, 0.50, 0.65, 0.80, 1.00, 1.25, 1.50, 2.00]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def base_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(str(r.get("label")) == "true" for r in rows)
    f = len(rows) - t
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def selected_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(str(r.get("label")) == "true" for r in rows)
    f = len(rows) - t
    return {"selected": len(rows), "true": t, "false": f, "precision": round(precision(t, f), 2)}


def aggregate(rows: list[dict[str, Any]], fold_fn: Callable[[int], int] | None = None) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    folds: dict[str, dict[int, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for row in rows:
        label = "true" if str(row.get("label")) == "true" else "false"
        fold = fold_fn(int(row["measure"])) if fold_fn is not None else -1
        for sig in row.get("signatures") or []:
            sig = str(sig)
            totals[sig][label] += 1
            if fold_fn is not None:
                folds[sig][fold][label] += 1
    return {"totals": totals, "folds": folds}


def scheme_useful(agg: dict[str, Any], sig: str, base_precision: float) -> bool:
    supported = useful = 0
    for fold in range(INNER_FOLDS):
        c = agg["folds"].get(sig, {}).get(fold, Counter())
        t, f = int(c["true"]), int(c["false"])
        if t + f == 0:
            continue
        supported += 1
        if t > 0 and precision(t, f) >= base_precision + 5.0:
            useful += 1
    return supported >= 2 and useful >= 2


def learn_signatures(train: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    measures = [int(r["measure"]) for r in train]
    lo, hi = min(measures), max(measures)
    base_p = base_stats(train)["precision"]
    normal = aggregate(train, lambda m: m % INNER_FOLDS)
    section = aggregate(train, lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS))
    shifted = aggregate(train, lambda m: shifted_fold(m, lo, hi, INNER_FOLDS))
    learned: dict[str, dict[str, Any]] = {}
    for sig, c in normal["totals"].items():
        t, f = int(c["true"]), int(c["false"])
        support = t + f
        p = precision(t, f)
        if t < 3 or support < 5 or p < max(25.0, float(base_p) + 5.0):
            continue
        agreement = sum((
            scheme_useful(normal, sig, float(base_p)),
            scheme_useful(section, sig, float(base_p)),
            scheme_useful(shifted, sig, float(base_p)),
        ))
        if agreement < 2:
            continue
        learned[sig] = {"true": t, "false": f, "precision": p, "agreementSchemes": agreement}
    return learned


def score(row: dict[str, Any], learned: dict[str, dict[str, Any]]) -> float:
    return sum(float(learned[s]["precision"]) / 100.0 for s in row.get("signatures") or [] if s in learned)


def apply(rows: list[dict[str, Any]], learned: dict[str, dict[str, Any]], cutoff: float) -> dict[str, Any]:
    chosen = [r for r in rows if score(r, learned) >= cutoff]
    return selected_stats(chosen)


def choose_cutoff(train: list[dict[str, Any]], learned: dict[str, dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    base_p = float(base_stats(train)["precision"])
    choices: list[tuple[float, dict[str, Any]]] = []
    for cutoff in CUTOFFS:
        result = apply(train, learned, cutoff)
        if result["true"] > 0 and result["precision"] >= base_p + 5.0:
            choices.append((cutoff, result))
    if not choices:
        return max(CUTOFFS), apply(train, learned, max(CUTOFFS))
    return max(choices, key=lambda item: (item[1]["true"] - item[1]["false"], item[1]["precision"], item[1]["true"], -item[1]["false"], -item[0]))


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    out: list[dict[str, Any]] = []
    passed_count = 0
    for fold in range(FOLD_COUNT):
        print(f"{name}: outer fold {fold + 1}/{FOLD_COUNT} ...", flush=True)
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        learned = learn_signatures(train)
        cutoff, train_result = choose_cutoff(train, learned)
        held = apply(test, learned, cutoff)
        held_base = base_stats(test)
        fold_pass = bool(learned) and held["true"] > 0 and held["precision"] >= float(held_base["precision"]) + 5.0
        passed_count += int(fold_pass)
        out.append({
            "scheme": name,
            "fold": fold,
            "trainRows": len(train),
            "testRows": len(test),
            "learnedSignatureCount": len(learned),
            "learnedSignatures": learned,
            "chosenCutoff": cutoff,
            "trainCandidate": train_result,
            "heldoutBase": held_base,
            "heldoutCandidate": held,
            "passed": fold_pass,
        })
        print(
            f"  learned={len(learned)} cutoff={cutoff} held={held['true']}/{held['false']} "
            f"precision={held['precision']} base={held_base['precision']} pass={fold_pass}",
            flush=True,
        )
    return passed_count == FOLD_COUNT, out


def main() -> None:
    before = sha256(prof.prof.recall.CANDIDATE_PATH)
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Onset-slot profile candidate slots are missing; run profile_gomyway_3676_onset_slot_stability_v1.py first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Onset-slot profile is not anchored to frozen 36.76 champion")

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting strict nested onset-slot CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, FOLD_COUNT))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(prof.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during onset-slot nested CV")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "onsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory slot-detection validation only. Onset signatures and cutoff are learned from outer-training data only. No pitch recovery or champion promotion is allowed from this benchmark.",
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
        "onsetSlotArchitectureGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Onset-slot architecture generalizes:", generalizes)
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
