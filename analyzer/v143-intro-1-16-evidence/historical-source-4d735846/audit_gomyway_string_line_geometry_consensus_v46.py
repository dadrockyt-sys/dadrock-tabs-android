import json
from pathlib import Path
from statistics import median, pstdev

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT = PUBLIC / "gomyway-string-line-geometry-calibration-v45.json"
OUTPUT = PUBLIC / "gomyway-string-line-geometry-consensus-v46.json"


def main() -> None:
    if not INPUT.exists():
        raise RuntimeError(f"Missing prerequisite: {INPUT.relative_to(ROOT)}")

    data = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    if len(rows) != 8:
        raise RuntimeError(f"Expected 8 rows, found {len(rows)}")

    usable = []
    for row in rows:
        spacing = row.get("selectedSpacingPixels")
        gap_std = row.get("gapStandardDeviation")
        selected = row.get("selectedStringRowsPixels") or []
        if spacing is None or gap_std is None or len(selected) != 6:
            continue
        usable.append(row)

    if len(usable) != 8:
        raise RuntimeError(f"Expected 8 usable six-line rows, found {len(usable)}")

    spacings = [float(row["selectedSpacingPixels"]) for row in usable]
    gap_stds = [float(row["gapStandardDeviation"]) for row in usable]
    med_spacing = float(median(spacings))
    spacing_std = float(pstdev(spacings)) if len(spacings) > 1 else 0.0

    reports = []
    consensus_rows = 0
    for row in usable:
        spacing = float(row["selectedSpacingPixels"])
        gap_std = float(row["gapStandardDeviation"])
        deviation = abs(spacing - med_spacing)
        passed = deviation <= 1.0 and gap_std <= 1.0
        if passed:
            consensus_rows += 1
        reports.append({
            "pageNumber": int(row.get("pageNumber", 0)),
            "rowIndex": int(row.get("rowIndex", 0)),
            "selectedSpacingPixels": spacing,
            "spacingDeviationFromMedian": round(deviation, 6),
            "gapStandardDeviation": gap_std,
            "consensusPassed": passed,
            "preview": row.get("preview"),
        })
        print(
            f"Page {row.get('pageNumber')} row {row.get('rowIndex')}: "
            f"spacing={spacing:.3f}, deviation={deviation:.3f}, "
            f"gapStd={gap_std:.6f}, consensusPassed={passed}"
        )

    spacing_consensus = consensus_rows >= 7
    gap_quality_passed = max(gap_stds) <= 1.0
    geometry_consensus_passed = spacing_consensus and gap_quality_passed

    output = {
        "diagnosticName": "Gomyway string-line geometry consensus audit v46",
        "rowsExpected": 8,
        "rowsInspected": len(rows),
        "usableSixLineRows": len(usable),
        "medianStringSpacingPixels": round(med_spacing, 6),
        "stringSpacingPopulationStdDev": round(spacing_std, 6),
        "consensusRows": consensus_rows,
        "spacingConsensus": spacing_consensus,
        "maximumGapStandardDeviation": round(max(gap_stds), 6),
        "gapQualityPassed": gap_quality_passed,
        "geometryConsensusPassed": geometry_consensus_passed,
        "rows": reports,
        "humanVisualValidationComplete": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-eight-v45-string-line-geometry-previews"
            if geometry_consensus_passed
            else "inspect-v46-geometry-consensus-outliers-v47"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("String-line geometry consensus audit v46 complete")
    print(f"Rows expected: 8")
    print(f"Rows inspected: {len(rows)}")
    print(f"Usable six-line rows: {len(usable)}")
    print(f"Median string spacing pixels: {med_spacing:.6f}")
    print(f"String spacing population std dev: {spacing_std:.6f}")
    print(f"Consensus rows: {consensus_rows}")
    print(f"Spacing consensus: {spacing_consensus}")
    print(f"Maximum gap standard deviation: {max(gap_stds):.6f}")
    print(f"Gap quality passed: {gap_quality_passed}")
    print(f"Geometry consensus passed: {geometry_consensus_passed}")
    print("Human visual validation complete: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
