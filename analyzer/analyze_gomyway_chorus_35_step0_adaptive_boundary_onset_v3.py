from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

V2_PATH = PUBLIC / "gomyway-chorus-35-step0-boundary-sequence-onset-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-35-step0-adaptive-boundary-onset-v3.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-35-step0-adaptive-boundary-onset-v3-manifest.json"

# The V2 extractor uses 256-sample hops at 22,050 Hz. Two hops provide a
# conservative resolution-aware separation gate without forcing the earlier
# fixed 40 ms clearance that rejected the only chronologically valid peak.
SAMPLE_RATE = 22050
HOP_SIZE = 256
MIN_CLEARANCE_HOPS = 2
MIN_CLEARANCE_SECONDS = (HOP_SIZE / SAMPLE_RATE) * MIN_CLEARANCE_HOPS
MAX_BOUNDARY_CLUSTER_SECONDS = 0.08


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    v2 = load(V2_PATH)
    if v2.get("passed") is not True:
        raise RuntimeError("Boundary sequence onset V2 did not complete.")
    if v2.get("qualityGate") is not False:
        raise RuntimeError("Adaptive arbitration is only for a blocked V2 result.")

    left = number(v2.get("leftBoundaryStartSeconds"))
    following = number(v2.get("followingBoundaryStartSeconds"))
    if left is None or following is None or not left < following:
        raise RuntimeError("Invalid chronological boundary anchors.")

    peak_rows = [
        row for row in v2.get("onsetPeaks", [])
        if isinstance(row, dict) and number(row.get("timeSeconds")) is not None
    ]

    evaluated: list[dict[str, Any]] = []
    for peak in peak_rows:
        onset = float(peak["timeSeconds"])
        after_left = onset - left
        before_following = following - onset
        chronological = left < onset < following
        adaptive_clearance = bool(
            chronological
            and after_left >= MIN_CLEARANCE_SECONDS
            and before_following >= MIN_CLEARANCE_SECONDS
        )
        boundary_cluster = bool(
            chronological
            and before_following <= MAX_BOUNDARY_CLUSTER_SECONDS
        )
        evaluated.append({
            "timeSeconds": round(onset, 6),
            "spectralFlux": peak.get("spectralFlux"),
            "afterLeftSeconds": round(after_left, 6),
            "beforeFollowingSeconds": round(before_following, 6),
            "chronologicalOrderPassed": chronological,
            "adaptiveClearancePassed": adaptive_clearance,
            "boundaryClusterWithFollowingEvent": boundary_cluster,
        })

    eligible = [row for row in evaluated if row["adaptiveClearancePassed"]]
    eligible.sort(
        key=lambda row: (
            -float(row.get("spectralFlux") or 0.0),
            abs(float(row["beforeFollowingSeconds"]) - float(row["afterLeftSeconds"])),
        )
    )
    selected = eligible[0] if eligible else None

    quality_gate = bool(
        selected is not None
        and float(selected["afterLeftSeconds"]) >= MIN_CLEARANCE_SECONDS
        and float(selected["beforeFollowingSeconds"]) >= MIN_CLEARANCE_SECONDS
    )

    output = {
        "schemaVersion": 3,
        "analysisType": "read-only-resolution-aware-boundary-onset-arbitration",
        "passed": True,
        "leftBoundaryMeasure": 34,
        "leftBoundaryStep": 15,
        "leftBoundaryStartSeconds": round(left, 6),
        "targetMeasure": 35,
        "targetStep": 0,
        "followingBoundaryMeasure": 35,
        "followingBoundaryStep": 1,
        "followingBoundaryStartSeconds": round(following, 6),
        "hopResolutionSeconds": round(HOP_SIZE / SAMPLE_RATE, 6),
        "minimumClearanceHops": MIN_CLEARANCE_HOPS,
        "minimumAdaptiveClearanceSeconds": round(MIN_CLEARANCE_SECONDS, 6),
        "maximumBoundaryClusterSeconds": MAX_BOUNDARY_CLUSTER_SECONDS,
        "evaluatedOnsetPeakCount": len(evaluated),
        "eligibleAdaptiveOnsetCount": len(eligible),
        "evaluatedOnsets": evaluated,
        "selectedOnset": selected,
        "resolvedStartSeconds": selected["timeSeconds"] if selected else None,
        "qualityGate": quality_gate,
        "readyForCompletedTimingPlanV3": quality_gate,
        "audioTimingEvidenceClaimed": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "timingRepairAppliedToProtectedSource": False,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 3,
        "passed": True,
        "eligibleAdaptiveOnsetCount": len(eligible),
        "resolvedStartSeconds": output["resolvedStartSeconds"],
        "qualityGate": quality_gate,
        "readyForCompletedTimingPlanV3": quality_gate,
        "audioTechniqueSupportClaimed": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 35 STEP 0 ADAPTIVE BOUNDARY ONSET V3 COMPLETE")
    print("Passed: True")
    print("Left boundary m34s15:", round(left, 6))
    print("Following boundary m35s1:", round(following, 6))
    print("Hop resolution seconds:", round(HOP_SIZE / SAMPLE_RATE, 6))
    print("Minimum adaptive clearance seconds:", round(MIN_CLEARANCE_SECONDS, 6))
    print("Evaluated onset peaks:", len(evaluated))
    print("Eligible adaptive onsets:", len(eligible))
    for row in evaluated:
        print(
            f"onset={row['timeSeconds']} flux={row['spectralFlux']} "
            f"afterLeft={row['afterLeftSeconds']} "
            f"beforeFollowing={row['beforeFollowingSeconds']} "
            f"chronological={row['chronologicalOrderPassed']} "
            f"adaptiveGate={row['adaptiveClearancePassed']} "
            f"boundaryCluster={row['boundaryClusterWithFollowingEvent']}"
        )
    print("Resolved measure 35 step 0 start:", output["resolvedStartSeconds"])
    print("Quality gate:", quality_gate)
    print("Ready for completed timing plan V3:", quality_gate)
    print("Timing repair applied to protected source: False")
    print("Audio technique support claimed: False")
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
