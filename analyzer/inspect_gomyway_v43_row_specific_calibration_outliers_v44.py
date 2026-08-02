import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V43 = PUBLIC / "gomyway-row-specific-string-line-calibration-v43.json"
OUTPUT = PUBLIC / "gomyway-v43-row-specific-calibration-outliers-v44.json"


def main() -> None:
    if not V43.exists():
        raise RuntimeError(f"Missing prerequisite: {V43.relative_to(ROOT)}")

    data = json.loads(V43.read_text(encoding="utf-8"))
    rows = list(data.get("rows", []))
    if len(rows) != 8:
        raise RuntimeError(f"Expected 8 calibrated rows, found {len(rows)}")

    direct = [row for row in rows if row.get("preferredDirection") == "high-E-to-low-E"]
    reversed_rows = [row for row in rows if row.get("preferredDirection") == "low-E-to-high-E"]
    top_values = [float(row.get("topStringY", 0)) for row in rows]
    spacing_values = [float(row.get("stringSpacingPixels", 0)) for row in rows]
    darkness_values = [float(row.get("targetDarknessMean", 0)) for row in rows]
    separation_values = [float(row.get("targetVsRivalSeparation", 0)) for row in rows]

    median_top = float(median(top_values))
    median_spacing = float(median(spacing_values))
    median_darkness = float(median(darkness_values))
    median_separation = float(median(separation_values))

    reports = []
    geometry_outliers = 0
    zero_separation_rows = 0
    saturated_rows = 0
    direction_outliers = 0

    print("V43 row-specific calibration outlier inspection v44 starting", flush=True)

    dominant_direction = (
        "high-E-to-low-E" if len(direct) > len(reversed_rows)
        else "low-E-to-high-E" if len(reversed_rows) > len(direct)
        else "ambiguous"
    )

    for row in rows:
        top = float(row.get("topStringY", 0))
        spacing = float(row.get("stringSpacingPixels", 0))
        darkness = float(row.get("targetDarknessMean", 0))
        separation = float(row.get("targetVsRivalSeparation", 0))
        direction = str(row.get("preferredDirection"))

        spacing_delta = abs(spacing - median_spacing)
        top_delta = abs(top - median_top)
        zero_separation = abs(separation) < 0.25
        saturated = darkness >= 220.0
        direction_outlier = dominant_direction != "ambiguous" and direction != dominant_direction
        geometry_outlier = spacing_delta > max(2.0, median_spacing * 0.4)

        if zero_separation:
            zero_separation_rows += 1
        if saturated:
            saturated_rows += 1
        if direction_outlier:
            direction_outliers += 1
        if geometry_outlier:
            geometry_outliers += 1

        reasons = []
        if zero_separation:
            reasons.append("target-rival-separation-near-zero")
        if saturated:
            reasons.append("darkness-saturated")
        if direction_outlier:
            reasons.append("direction-opposes-dominant")
        if geometry_outlier:
            reasons.append("spacing-geometry-outlier")

        report = {
            "pageNumber": int(row.get("pageNumber", 0)),
            "rowIndex": int(row.get("rowIndex", 0)),
            "topStringY": top,
            "stringSpacingPixels": spacing,
            "preferredDirection": direction,
            "targetDarknessMean": darkness,
            "targetVsRivalSeparation": separation,
            "topDeltaFromMedian": round(top_delta, 6),
            "spacingDeltaFromMedian": round(spacing_delta, 6),
            "isOutlier": bool(reasons),
            "outlierReasons": reasons,
            "preview": row.get("preview"),
        }
        reports.append(report)
        print(
            f"Page {report['pageNumber']} row {report['rowIndex']}: "
            f"direction={direction}, top={top:.1f}, spacing={spacing:.1f}, "
            f"darkness={darkness:.2f}, separation={separation:.2f}, reasons={reasons}"
        )

    trustworthy_rows = sum(1 for report in reports if not report["isOutlier"])
    calibration_trustworthy = (
        trustworthy_rows == 8
        and zero_separation_rows == 0
        and saturated_rows == 0
        and direction_outliers == 0
    )

    output = {
        "diagnosticName": "Gomyway V43 row-specific calibration outlier inspection v44",
        "rowsInspected": len(rows),
        "dominantDirection": dominant_direction,
        "medianTopStringY": round(median_top, 6),
        "medianStringSpacingPixels": round(median_spacing, 6),
        "medianTargetDarknessMean": round(median_darkness, 6),
        "medianTargetVsRivalSeparation": round(median_separation, 6),
        "zeroSeparationRows": zero_separation_rows,
        "saturatedDarknessRows": saturated_rows,
        "directionOutlierRows": direction_outliers,
        "geometryOutlierRows": geometry_outliers,
        "trustworthyRows": trustworthy_rows,
        "calibrationTrustworthy": calibration_trustworthy,
        "rows": reports,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-v43-calibrated-previews"
            if calibration_trustworthy
            else "replace-darkness-objective-with-line-geometry-objective-v45"
        ),
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("V43 row-specific calibration outlier inspection v44 complete")
    print(f"Rows inspected: {len(rows)}")
    print(f"Dominant direction: {dominant_direction}")
    print(f"Zero-separation rows: {zero_separation_rows}")
    print(f"Saturated-darkness rows: {saturated_rows}")
    print(f"Direction-outlier rows: {direction_outliers}")
    print(f"Geometry-outlier rows: {geometry_outliers}")
    print(f"Trustworthy rows: {trustworthy_rows}")
    print(f"Calibration trustworthy: {calibration_trustworthy}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
