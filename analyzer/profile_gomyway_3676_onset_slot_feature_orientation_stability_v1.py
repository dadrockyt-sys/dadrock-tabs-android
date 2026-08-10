from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3676_onset_slot_stability_v1 as onset

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CV_PATH = PUBLIC / "gomyway-3676-onset-slot-continuous-nested-cv-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-feature-orientation-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-feature-orientation-stability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
FEATURES = [
    "attackMean",
    "fluxMean",
    "sustainMean",
    "midShareMean",
    "highShareMean",
    "onsetAgreement",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before = sha256(onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(CV_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Continuous onset-slot CV is not anchored to frozen 36.76 champion")

    folds: list[dict[str, Any]] = []
    for key in ("normalCv", "sectionCv", "shiftedWindowCv"):
        folds.extend(list(payload.get(key) or []))
    if not folds:
        raise RuntimeError("Continuous onset-slot CV fold results are missing")

    stats: dict[str, dict[str, Any]] = {}
    for feature in FEATURES:
        selected = 0
        positive = 0
        negative = 0
        zero = 0
        passed_selected = 0
        failed_selected = 0
        weights: list[float] = []
        schemes: Counter[str] = Counter()
        for fold in folds:
            model = fold.get("model") or {}
            model_features = set(model.get("features") or [])
            weights_map = model.get("weights") or {}
            if feature not in model_features:
                continue
            selected += 1
            w = float(weights_map.get(feature, 0.0))
            weights.append(w)
            if w > 0:
                positive += 1
            elif w < 0:
                negative += 1
            else:
                zero += 1
            if bool(fold.get("passed")):
                passed_selected += 1
            else:
                failed_selected += 1
            schemes[str(fold.get("scheme"))] += 1

        nonzero = positive + negative
        dominant = max(positive, negative)
        dominant_direction = "positive" if positive > negative else "negative" if negative > positive else "mixed"
        direction_consistency = (100.0 * dominant / nonzero) if nonzero else 0.0
        stats[feature] = {
            "selectedFolds": selected,
            "positiveWeights": positive,
            "negativeWeights": negative,
            "zeroWeights": zero,
            "dominantDirection": dominant_direction,
            "directionConsistencyPct": round(direction_consistency, 2),
            "passedWhenSelected": passed_selected,
            "failedWhenSelected": failed_selected,
            "meanWeight": round(sum(weights) / len(weights), 6) if weights else 0.0,
            "meanAbsWeight": round(sum(abs(w) for w in weights) / len(weights), 6) if weights else 0.0,
            "schemes": dict(schemes),
        }

    ranked = [
        {"feature": feature, **row}
        for feature, row in stats.items()
    ]
    ranked.sort(
        key=lambda r: (
            -int(r["selectedFolds"]),
            -float(r["directionConsistencyPct"]),
            -int(r["passedWhenSelected"]),
            int(r["failedWhenSelected"]),
            str(r["feature"]),
        )
    )

    stable = [
        r for r in ranked
        if int(r["selectedFolds"]) >= 5
        and float(r["directionConsistencyPct"]) >= 80.0
        and str(r["dominantDirection"]) != "mixed"
    ]
    unstable = [
        r for r in ranked
        if int(r["selectedFolds"]) >= 3
        and float(r["directionConsistencyPct"]) < 80.0
    ]

    after = sha256(onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during onset feature-orientation diagnostic")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "36.76-onset-slot-feature-orientation-stability-diagnostic",
        "frozenChampionPitchF1": EXPECTED_F1,
        "frozenChampionMatchedMissingExtra": list(EXPECTED),
        "foldCount": len(folds),
        "features": ranked,
        "stableDirectionFeatures": stable,
        "unstableDirectionFeatures": unstable,
        "validatedNewChampion": False,
        "note": "Diagnostic only. Reads previously completed nested-CV training models to determine whether continuous audio feature orientation is stable across partitions. No held-out labels are used to alter detection and no promotion is allowed.",
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
        "stableDirectionFeatureCount": len(stable),
        "unstableDirectionFeatureCount": len(unstable),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT FEATURE ORIENTATION STABILITY V1 COMPLETE")
    print("Analyzed folds:", len(folds))
    print("Stable-direction features:", len(stable))
    for row in stable:
        print("STABLE", row)
    print("Unstable-direction features:", len(unstable))
    for row in unstable:
        print("UNSTABLE", row)
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
