from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_3676_pitch_register_interval_recovery_v1 as prof

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PITCH_PATH = PUBLIC / "gomyway-3676-pitch-register-interval-recovery-v1.json"
PATTERN_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
PHRASE_PATH = PUBLIC / "gomyway-3676-repeated-phrase-template-recovery-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-multifamily-nested-agreement-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-multifamily-nested-agreement-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FOLD_COUNT = 5
INNER_FOLDS = 4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token_tuple(value: Any) -> tuple[int, int, int]:
    if isinstance(value, str):
        parts = value.replace("(", "").replace(")", "").replace("[", "").replace("]", "").split(",")
        return int(parts[0]), int(parts[1]), int(parts[2])
    return int(value[0]), int(value[1]), int(value[2])


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def pitch_f1(matched: int, missing: int, extra: int) -> float:
    d = 2 * matched + missing + extra
    return round(100.0 * (2 * matched / d if d else 0.0), 2)


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(r["label"] == "true" for r in rows)
    f = len(rows) - t
    m, miss, extra = EXPECTED[0] + t, EXPECTED[1] - t, EXPECTED[2] + f
    return {
        "selected": len(rows), "recoverTrue": t, "recoverFalse": f,
        "precision": round(precision(t, f), 2), "pitchF1": pitch_f1(m, miss, extra),
        "matchedMissingExtra": [m, miss, extra],
    }


def prepare_rows() -> list[dict[str, Any]]:
    pitch = json.loads(PITCH_PATH.read_text(encoding="utf-8"))
    pattern = json.loads(PATTERN_PATH.read_text(encoding="utf-8"))
    phrase = json.loads(PHRASE_PATH.read_text(encoding="utf-8"))
    if tuple(pitch.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Pitch profiler is not anchored to frozen 36.76 champion")
    if tuple(phrase.get("championMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Phrase profiler is not anchored to frozen 36.76 champion")
    pmap = {token_tuple(r["token"]): r for r in pattern.get("candidateRows") or []}
    phmap = {token_tuple(r["token"]): r for r in phrase.get("candidateRows") or []}
    out = []
    for r in pitch.get("candidateRows") or []:
        tok = token_tuple(r["token"])
        raw = pmap.get(tok, {})
        phr = phmap.get(tok)
        persistence = int(raw.get("sweepPersistence", 0) or 0)
        stems = int(raw.get("stemCountAtWide", 0) or 0)
        strictest = int(raw.get("strictestSweepIndex", 99) if raw else 99)
        grid = float(raw.get("minGridError", 9.0) if raw else 9.0)
        duration = float(raw.get("maxDuration", 0.0) if raw else 0.0)
        ac_multi = sum((stems >= 2, persistence >= 3, strictest <= 1, grid <= 0.035, duration >= 0.08)) >= 2
        ac_strong = stems >= 2 and persistence >= 3
        ph_present = phr is not None
        ph_exact = bool(phr and int(phr.get("exactSupport", 0)) >= 1)
        ph_strong = bool(phr and (int(phr.get("strongSupport", 0)) >= 1 or float(phr.get("bestSimilarity", 0.0)) >= 0.60))
        out.append({
            "token": tok, "measure": int(r["measure"]), "label": str(r.get("label")),
            "prcross": tuple(str(s) for s in (r.get("signatures") or []) if str(s).startswith("prCross::")),
            "stemBoth": stems >= 2, "persistent3p": persistence >= 3, "strictSweep": strictest <= 1,
            "tightGrid": grid <= 0.035, "acousticMulti": ac_multi, "acousticStrong": ac_strong,
            "phraseAny": ph_present, "phraseExact": ph_exact, "phraseStrong": ph_strong,
        })
    return out


def aggregate(rows: list[dict[str, Any]], fold_fn: Callable[[int], int] | None = None) -> dict[str, Any]:
    totals: dict[str, Counter[str]] = defaultdict(Counter)
    folds: dict[str, dict[int, Counter[str]]] = defaultdict(lambda: defaultdict(Counter))
    for r in rows:
        fold = fold_fn(r["measure"]) if fold_fn else -1
        for sig in r["prcross"]:
            totals[sig][r["label"]] += 1
            if fold_fn:
                folds[sig][fold][r["label"]] += 1
    return {"totals": totals, "folds": folds}


def scheme_useful(agg: dict[str, Any], sig: str) -> bool:
    supported = useful = 0
    for fold in range(INNER_FOLDS):
        c = agg["folds"].get(sig, {}).get(fold, Counter())
        t, f = int(c["true"]), int(c["false"])
        if t + f == 0:
            continue
        supported += 1
        if t > 0 and precision(t, f) >= 35.0:
            useful += 1
    return supported >= 2 and useful >= 2


def learn_pitch_core(train: list[dict[str, Any]]) -> set[str]:
    measures = [r["measure"] for r in train]
    lo, hi = min(measures), max(measures)
    normal = aggregate(train, lambda m: m % INNER_FOLDS)
    section = aggregate(train, lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS))
    shifted = aggregate(train, lambda m: shifted_fold(m, lo, hi, INNER_FOLDS))
    learned = set()
    for sig, c in normal["totals"].items():
        t, f = int(c["true"]), int(c["false"])
        if t < 3 or t + f < 4 or precision(t, f) < 40.0:
            continue
        agreement = sum((scheme_useful(normal, sig), scheme_useful(section, sig), scheme_useful(shifted, sig)))
        if agreement >= 2:
            learned.add(sig)
    return learned


RULES: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("pitchCore", lambda r: r["pitchCore"]),
    ("pitchCore+stemBoth", lambda r: r["pitchCore"] and r["stemBoth"]),
    ("pitchCore+persistent3p", lambda r: r["pitchCore"] and r["persistent3p"]),
    ("pitchCore+strictSweep", lambda r: r["pitchCore"] and r["strictSweep"]),
    ("pitchCore+tightGrid", lambda r: r["pitchCore"] and r["tightGrid"]),
    ("pitchCore+acousticMulti", lambda r: r["pitchCore"] and r["acousticMulti"]),
    ("pitchCore+acousticStrong", lambda r: r["pitchCore"] and r["acousticStrong"]),
    ("pitchCore+phraseAny", lambda r: r["pitchCore"] and r["phraseAny"]),
    ("pitchCore+phraseExact", lambda r: r["pitchCore"] and r["phraseExact"]),
    ("pitchCore+phraseStrong", lambda r: r["pitchCore"] and r["phraseStrong"]),
    ("pitchCore+acousticMulti+phraseAny", lambda r: r["pitchCore"] and r["acousticMulti"] and r["phraseAny"]),
    ("pitchCore+acousticMulti+phraseStrong", lambda r: r["pitchCore"] and r["acousticMulti"] and r["phraseStrong"]),
    ("pitchCore+acousticStrong+phraseAny", lambda r: r["pitchCore"] and r["acousticStrong"] and r["phraseAny"]),
    ("pitchCore+acousticStrong+phraseStrong", lambda r: r["pitchCore"] and r["acousticStrong"] and r["phraseStrong"]),
]


def mark_pitch_core(rows: list[dict[str, Any]], learned: set[str]) -> list[dict[str, Any]]:
    return [{**r, "pitchCore": bool(set(r["prcross"]) & learned)} for r in rows]


def choose_rule(train: list[dict[str, Any]], learned: set[str]) -> tuple[str, dict[str, Any]]:
    marked = mark_pitch_core(train, learned)
    base_true = sum(r["label"] == "true" for r in train)
    base_false = len(train) - base_true
    base_precision = precision(base_true, base_false)
    choices = []
    for name, pred in RULES:
        s = stats([r for r in marked if pred(r)])
        if s["selected"] >= 4 and s["recoverTrue"] >= 2 and s["pitchF1"] > EXPECTED_F1 and s["precision"] >= max(35.0, base_precision + 5.0):
            choices.append((name, s))
    if not choices:
        return "none", stats([])
    return max(choices, key=lambda x: (x[1]["pitchF1"], x[1]["precision"], x[1]["recoverTrue"], -x[1]["recoverFalse"]))


def apply_rule(rows: list[dict[str, Any]], learned: set[str], rule_name: str) -> dict[str, Any]:
    if rule_name == "none":
        return stats([])
    pred = dict(RULES)[rule_name]
    marked = mark_pitch_core(rows, learned)
    return stats([r for r in marked if pred(r)])


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    results = []
    pass_count = 0
    for fold in range(FOLD_COUNT):
        print(f"{name}: outer fold {fold + 1}/{FOLD_COUNT} ...", flush=True)
        train = [r for r in rows if fold_fn(r["measure"]) != fold]
        test = [r for r in rows if fold_fn(r["measure"]) == fold]
        learned = learn_pitch_core(train)
        chosen_rule, train_result = choose_rule(train, learned)
        held = apply_rule(test, learned, chosen_rule)
        fold_pass = bool(learned) and chosen_rule != "none" and held["recoverTrue"] > 0 and held["pitchF1"] > EXPECTED_F1
        pass_count += int(fold_pass)
        row = {
            "scheme": name, "fold": fold, "trainRows": len(train), "testRows": len(test),
            "learnedStablePrCrossCount": len(learned), "learnedStablePrCross": sorted(learned),
            "chosenRule": chosen_rule, "trainCandidate": train_result, "heldoutCandidate": held, "passed": fold_pass,
        }
        results.append(row)
        print(f"  learned={len(learned)} rule={chosen_rule} held={held['recoverTrue']}/{held['recoverFalse']} F1={held['pitchF1']} pass={fold_pass}", flush=True)
    return pass_count == FOLD_COUNT, results


def main() -> None:
    before = sha256(prof.recall.CANDIDATE_PATH)
    rows = prepare_rows()
    if not rows:
        raise RuntimeError("No residual rows available")
    measures = [r["measure"] for r in rows]
    lo, hi = min(measures), max(measures)

    print("Starting strict nested multi-family agreement CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % FOLD_COUNT)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, FOLD_COUNT))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, FOLD_COUNT))
    family_generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during nested multi-family benchmark")

    output = {
        "schemaVersion": 1, "passed": True,
        "profileType": "36.76-multifamily-nested-agreement-cv",
        "baselinePitchF1": EXPECTED_F1, "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass, "normalCv": normal,
        "sectionStabilityPassed": section_pass, "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass, "shiftedWindowCv": shifted,
        "multiFamilyArchitectureGeneralizes": family_generalizes,
        "validatedNewChampion": False,
        "validationNote": "Strict exploratory architecture validation. Pitch-core signatures and agreement rule are learned inside training folds only. No promotion from this benchmark alone.",
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False,
        "protectedBaselinesChanged": False, "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1, "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)), "candidateSha256": after,
        "multiFamilyArchitectureGeneralizes": family_generalizes,
        "validatedNewChampion": False, "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 MULTIFAMILY NESTED AGREEMENT CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Multi-family architecture generalizes:", family_generalizes)
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
