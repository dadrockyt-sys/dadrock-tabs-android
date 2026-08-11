from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3676-onset-slot-richer-audio-stability-v1.json"
EXPERIMENT_PATHS = [
    PUBLIC / "gomyway-3676-onset-slot-richer-audio-feature-consensus-nested-cv-v2.json",
    PUBLIC / "gomyway-3676-onset-slot-richer-audio-nested-cv-v1.json",
    PUBLIC / "gomyway-3676-onset-slot-invariant-orientation-nested-cv-v1.json",
    PUBLIC / "gomyway-3676-onset-slot-continuous-nested-cv-v1.json",
]
OUTPUT_PATH = PUBLIC / "gomyway-3676-cross-experiment-hard-slot-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-cross-experiment-hard-slot-anatomy-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def slot_key(row: dict[str, Any]) -> str:
    return f"{int(row['measure'])}:{int(row.get('step', row.get('gridStep', 0)))}"


def feature_value(row: dict[str, Any], name: str) -> float:
    return float((row.get("features") or {}).get(name, 0.0))


def score_row(row: dict[str, Any], model: dict[str, Any]) -> float:
    total = 0.0
    norm = 0.0
    for name in model.get("features") or []:
        w = float((model.get("weights") or {}).get(name, 0.0))
        center = float((model.get("center") or {}).get(name, 0.0))
        scale = float((model.get("scale") or {}).get(name, 1.0))
        if abs(scale) < 1e-12:
            scale = 1.0
        total += w * ((feature_value(row, name) - center) / scale)
        norm += abs(w)
    return total / norm if norm > 1e-12 else -1e9


def standardized_difference(a: list[dict[str, Any]], b: list[dict[str, Any]], name: str) -> float:
    if not a or not b:
        return 0.0
    vals = np.asarray([feature_value(r, name) for r in a + b], dtype=np.float64)
    sd = float(np.std(vals))
    if not math.isfinite(sd) or sd < 1e-9:
        return 0.0
    return (float(np.mean([feature_value(r, name) for r in a])) - float(np.mean([feature_value(r, name) for r in b]))) / sd


def load_experiments() -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    for path in EXPERIMENT_PATHS:
        if path.exists():
            out.append((path.stem, json.loads(path.read_text(encoding="utf-8"))))
    return out


def scheme_rows(payload: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    candidates = [
        ("normal", payload.get("normalCv") or []),
        ("section", payload.get("sectionCv") or []),
        ("shiftedWindow", payload.get("shiftedWindowCv") or []),
    ]
    return [(name, rows) for name, rows in candidates if rows]


def main() -> None:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    rows = list(profile.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Richer-audio candidateSlots missing")
    if tuple(profile.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Profile not anchored to frozen 36.76 champion")

    experiments = load_experiments()
    if not experiments:
        raise RuntimeError("No completed onset-slot nested-CV outputs found")

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    row_by_key = {slot_key(r): r for r in rows}
    opportunities: Counter[str] = Counter()
    selections: Counter[str] = Counter()
    experiment_hits: dict[str, Counter[str]] = defaultdict(Counter)

    print(f"Cross-experiment anatomy: {len(experiments)} completed experiments", flush=True)
    for exp_name, payload in experiments:
        print(f"  reconstructing {exp_name} ...", flush=True)
        for scheme, fold_rows in scheme_rows(payload):
            for fold_result in fold_rows:
                fold = int(fold_result.get("fold", 0))
                model = fold_result.get("model") or {}
                threshold = float(fold_result.get("threshold", float("inf")))
                if scheme == "normal":
                    fold_fn: Callable[[int], int] = lambda m: m % OUTER_FOLDS
                elif scheme == "section":
                    fold_fn = lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS)
                else:
                    fold_fn = lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS)
                test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
                for r in test:
                    key = slot_key(r)
                    opportunities[key] += 1
                    if model.get("features") and score_row(r, model) >= threshold:
                        selections[key] += 1
                        experiment_hits[exp_name][key] += 1

    true_rows = [r for r in rows if str(r.get("label")) == "true"]
    false_rows = [r for r in rows if str(r.get("label")) != "true"]

    def rate(r: dict[str, Any]) -> float:
        key = slot_key(r)
        return selections[key] / opportunities[key] if opportunities[key] else 0.0

    hard_true = [r for r in true_rows if opportunities[slot_key(r)] >= 2 and rate(r) <= 0.10]
    recoverable_true = [r for r in true_rows if opportunities[slot_key(r)] >= 2 and rate(r) >= 0.50]
    persistent_false = [r for r in false_rows if opportunities[slot_key(r)] >= 2 and rate(r) >= 0.50]

    feature_names = sorted({k for r in rows for k in (r.get("features") or {}).keys()})
    comparisons: list[dict[str, Any]] = []
    for name in feature_names:
        hard_vs_recoverable = standardized_difference(hard_true, recoverable_true, name)
        hard_vs_false = standardized_difference(hard_true, persistent_false, name)
        comparisons.append({
            "feature": name,
            "hardTrueVsRecoverableTrueEffect": round(hard_vs_recoverable, 4),
            "hardTrueVsPersistentFalseEffect": round(hard_vs_false, 4),
            "combinedMagnitude": round(abs(hard_vs_recoverable) + abs(hard_vs_false), 4),
        })
    comparisons.sort(key=lambda x: (-float(x["combinedMagnitude"]), x["feature"]))

    rhythm = {
        "hardTrueStepMod4": dict(Counter(int(r.get("step", r.get("gridStep", 0))) % 4 for r in hard_true)),
        "hardTrueStepMod8": dict(Counter(int(r.get("step", r.get("gridStep", 0))) % 8 for r in hard_true)),
        "recoverableTrueStepMod4": dict(Counter(int(r.get("step", r.get("gridStep", 0))) % 4 for r in recoverable_true)),
        "persistentFalseStepMod4": dict(Counter(int(r.get("step", r.get("gridStep", 0))) % 4 for r in persistent_false)),
    }

    hardest = sorted(
        [
            {
                "key": slot_key(r),
                "measure": int(r["measure"]),
                "step": int(r.get("step", r.get("gridStep", 0))),
                "opportunities": opportunities[slot_key(r)],
                "selections": selections[slot_key(r)],
                "selectionRate": round(rate(r), 3),
            }
            for r in hard_true
        ],
        key=lambda x: (x["selectionRate"], -x["opportunities"], x["measure"], x["step"]),
    )[:40]

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-cross-experiment-hard-slot-anatomy-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "experimentsAnalyzed": [name for name, _ in experiments],
        "candidateSlots": len(rows),
        "trueSlots": len(true_rows),
        "falseSlots": len(false_rows),
        "hardTrueSlots": len(hard_true),
        "recoverableTrueSlots": len(recoverable_true),
        "persistentFalseSlots": len(persistent_false),
        "topFeatureContrasts": comparisons[:20],
        "rhythmAnatomy": rhythm,
        "hardestTrueSlots": hardest,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "profileType": output["profileType"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 CROSS-EXPERIMENT HARD-SLOT ANATOMY V1 COMPLETE")
    print("Experiments analyzed:", len(experiments))
    print("True slots:", len(true_rows))
    print("Hard true slots:", len(hard_true))
    print("Recoverable true slots:", len(recoverable_true))
    print("Persistent false slots:", len(persistent_false))
    print("Top feature contrasts:")
    for row in comparisons[:12]:
        print("CONTRAST", row)
    print("Rhythm anatomy:", rhythm)
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
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
