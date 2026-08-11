from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-3676-onset-slot-local-contrast-nested-cv-v1.json"
OUTPUT = PUBLIC / "gomyway-3676-local-contrast-selection-instability-v1.json"
MANIFEST = PUBLIC / "gomyway-3676-local-contrast-selection-instability-v1-manifest.json"


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    schemes = [
        ("normal", payload.get("normalCv") or []),
        ("section", payload.get("sectionCv") or []),
        ("shiftedWindow", payload.get("shiftedWindowCv") or []),
    ]

    selected = Counter()
    selected_pass = Counter()
    selected_fail = Counter()
    by_scheme: dict[str, Counter[str]] = defaultdict(Counter)
    q_counts = Counter()
    rows: list[dict[str, Any]] = []

    for scheme, folds in schemes:
        for r in folds:
            feature = str(r.get("feature") or (r.get("chosen") or {}).get("feature") or "")
            q = float((r.get("chosen") or {}).get("tailQuantile", 0.0))
            passed = bool(r.get("passed"))
            lift = float(r.get("heldoutPrecisionLift", 0.0))
            selected[feature] += 1
            by_scheme[scheme][feature] += 1
            q_counts[q] += 1
            if passed:
                selected_pass[feature] += 1
            else:
                selected_fail[feature] += 1
            rows.append({
                "scheme": scheme,
                "fold": int(r.get("fold", 0)),
                "feature": feature,
                "tailQuantile": q,
                "direction": int(r.get("direction", 0)),
                "lift": lift,
                "passed": passed,
            })

    feature_summary = []
    for feature, count in selected.most_common():
        p = selected_pass[feature]
        f = selected_fail[feature]
        feature_summary.append({
            "feature": feature,
            "selectedFolds": count,
            "passedWhenSelected": p,
            "failedWhenSelected": f,
            "passRateWhenSelectedPct": round(100.0 * p / count, 2) if count else 0.0,
            "schemes": {k: int(v[feature]) for k, v in by_scheme.items() if v[feature]},
        })

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-local-contrast-selection-instability-diagnostic",
        "outerFoldCount": len(rows),
        "featureSelectionCounts": dict(selected),
        "tailQuantileCounts": {str(k): v for k, v in sorted(q_counts.items())},
        "featureSummary": feature_summary,
        "folds": rows,
        "diagnosticWinner": "localStemAttackContrast",
        "diagnosticWinnerSelectedFolds": int(selected["localStemAttackContrast"]),
        "diagnosticWinnerPassedFolds": int(selected_pass["localStemAttackContrast"]),
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUTPUT.relative_to(ROOT)),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 LOCAL CONTRAST SELECTION INSTABILITY V1 COMPLETE")
    print("Outer folds analyzed:", len(rows))
    print("Diagnostic winner selected folds:", selected["localStemAttackContrast"])
    print("Diagnostic winner passed folds:", selected_pass["localStemAttackContrast"])
    print("Feature selection summary:")
    for item in feature_summary:
        print("FEATURE", item)
    print("Tail quantiles:", dict(sorted(q_counts.items())))
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Manifest:", MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
