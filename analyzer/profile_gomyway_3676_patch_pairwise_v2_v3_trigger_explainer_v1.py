from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-failure-anatomy-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v3-trigger-explainer-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-v3-trigger-explainer-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76


def main() -> None:
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(payload.get("baselineMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Failure-anatomy output not anchored to frozen 36.76 champion")

    passing = payload.get("passingSummary") or {}
    failing = payload.get("failingSummary") or {}
    recurrent = payload.get("recurrentTopWeights") or []
    failing_count = int(payload.get("failingFoldCount") or 0)

    radius_counts = {int(k): int(v) for k, v in (failing.get("pairRadiusCounts") or {}).items()}
    max_fail_radius_count = max(radius_counts.values()) if radius_counts else 0
    clustered_radius = bool(radius_counts) and max_fail_radius_count >= max(3, failing_count - 1)
    dominant_radius = None
    if radius_counts:
        dominant_radius = max(radius_counts, key=lambda k: radius_counts[k])

    pass_selected = float(passing.get("meanSelectedPct", 0.0))
    fail_selected = float(failing.get("meanSelectedPct", 0.0))
    selected_gap_value = abs(fail_selected - pass_selected)
    selected_gap = selected_gap_value >= 2.0

    family_rows = []
    for row in recurrent:
        p = int(row.get("passTop8", 0))
        f = int(row.get("failTop8", 0))
        pass_specific = p >= 4 and f == 0
        fail_specific = f >= 3 and p <= 1
        if pass_specific or fail_specific:
            family_rows.append({
                "feature": row.get("feature"),
                "family": row.get("family"),
                "passTop8": p,
                "failTop8": f,
                "signalType": "passSpecific" if pass_specific else "failSpecific",
            })
    family_signal = bool(family_rows)

    ready = clustered_radius or selected_gap or family_signal
    triggers = []
    if clustered_radius:
        triggers.append("clusteredPairRadius")
    if selected_gap:
        triggers.append("selectedRateGap")
    if family_signal:
        triggers.append("featureFamilySplit")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-v3-trigger-explainer",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "failingFoldCount": failing_count,
        "clusteredPairRadius": clustered_radius,
        "failingPairRadiusCounts": radius_counts,
        "dominantFailRadius": dominant_radius,
        "dominantFailRadiusCount": max_fail_radius_count,
        "selectedRateGap": selected_gap,
        "passingMeanSelectedPct": pass_selected,
        "failingMeanSelectedPct": fail_selected,
        "selectedRateGapPctPoints": round(selected_gap_value, 3),
        "featureFamilySplit": family_signal,
        "familySignals": family_rows,
        "activeTriggers": triggers,
        "v3HypothesisReady": ready,
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
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "activeTriggers": triggers,
        "v3HypothesisReady": ready,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 V3 TRIGGER EXPLAINER V1 COMPLETE")
    print("Active V3 triggers:", triggers)
    print("Clustered pair radius:", clustered_radius, "counts:", radius_counts, "dominant:", dominant_radius, "count:", max_fail_radius_count)
    print("Selected-rate gap:", selected_gap, "passMeanPct:", pass_selected, "failMeanPct:", fail_selected, "gapPctPoints:", round(selected_gap_value, 3))
    print("Feature-family split:", family_signal)
    for row in family_rows:
        print("FAMILY SIGNAL", row)
    print("V3 hypothesis ready:", ready)
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
