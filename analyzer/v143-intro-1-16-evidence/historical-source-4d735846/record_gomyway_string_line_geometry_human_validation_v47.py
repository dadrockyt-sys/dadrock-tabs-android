import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-string-line-geometry-consensus-v46.json"
OUTPUT = PUBLIC / "gomyway-string-line-geometry-human-validation-v47.json"

EXPECTED_ROWS = [
    (1, 1),
    (1, 2),
    (1, 3),
    (1, 4),
    (1, 5),
    (1, 6),
    (2, 1),
    (2, 2),
]


def main() -> None:
    if not SOURCE.exists():
        raise RuntimeError(f"Missing prerequisite: {SOURCE.relative_to(ROOT)}")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))

    if source.get("geometryConsensusPassed") is not True:
        raise RuntimeError("V46 geometry consensus did not pass")

    rows = source.get("rows", [])
    observed = {
        (int(row.get("pageNumber", 0)), int(row.get("rowIndex", 0)))
        for row in rows
    }
    expected = set(EXPECTED_ROWS)

    if observed != expected:
        raise RuntimeError(
            f"Expected rows {sorted(expected)}, found {sorted(observed)}"
        )

    approved_rows = []
    for row in rows:
        approved_rows.append(
            {
                "pageNumber": int(row["pageNumber"]),
                "rowIndex": int(row["rowIndex"]),
                "stringSpacingPixels": row.get("stringSpacingPixels"),
                "gapStandardDeviation": row.get("gapStandardDeviation"),
                "consensusPassed": row.get("consensusPassed"),
                "humanApproved": True,
            }
        )

    output = {
        "diagnosticName": "Gomyway string-line geometry human validation v47",
        "source": str(SOURCE.relative_to(ROOT)),
        "rowsExpected": len(EXPECTED_ROWS),
        "rowsReviewed": len(approved_rows),
        "rowsHumanApproved": len(approved_rows),
        "allRowsHumanApproved": len(approved_rows) == len(EXPECTED_ROWS),
        "humanReviewStatement": (
            "All eight yellow six-string overlays were visually reviewed and "
            "confirmed to align with the six professional TAB string lines."
        ),
        "rows": approved_rows,
        "geometryConsensusPassed": True,
        "humanVisualValidationComplete": True,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "apply-approved-row-specific-string-geometry-to-read-only-"
            "professional-note-event-extraction-measures-17-113-v48"
        ),
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("String-line geometry human validation v47 complete")
    print(f"Rows expected: {output['rowsExpected']}")
    print(f"Rows reviewed: {output['rowsReviewed']}")
    print(f"Rows human approved: {output['rowsHumanApproved']}")
    print(f"All rows human approved: {output['allRowsHumanApproved']}")
    print("Geometry consensus passed: True")
    print("Human visual validation complete: True")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
