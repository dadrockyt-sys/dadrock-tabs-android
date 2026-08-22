import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ANCHOR_PATH = PUBLIC / "gomyway-rhythm-pdf-measure-anchor-manifest-v8.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-manifest-v9.json"
EXPECTED_MEASURES = 113

# Visually verified against the 8-page professional rhythm-guitar PDF.
# Bottom-of-page repeated material is intentionally assigned to the next page,
# where the printed measures are unobstructed and complete.
CANONICAL_PAGES = [
    {
        "pageNumber": 1,
        "canonicalMeasureStart": 1,
        "canonicalMeasureEnd": 12,
        "rows": [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]],
    },
    {
        "pageNumber": 2,
        "canonicalMeasureStart": 13,
        "canonicalMeasureEnd": 26,
        "rows": [[13, 14], [15, 16], [17, 18], [19, 20], [21, 22], [23, 24], [25, 26]],
    },
    {
        "pageNumber": 3,
        "canonicalMeasureStart": 27,
        "canonicalMeasureEnd": 40,
        "rows": [[27, 28], [29, 30], [31, 32], [33, 34, 35], [36, 37, 38], [39, 40]],
    },
    {
        "pageNumber": 4,
        "canonicalMeasureStart": 41,
        "canonicalMeasureEnd": 56,
        "rows": [[41, 42], [43, 44], [45, 46], [47, 48], [49, 50], [51, 52], [53, 54], [55, 56]],
    },
    {
        "pageNumber": 5,
        "canonicalMeasureStart": 57,
        "canonicalMeasureEnd": 73,
        "rows": [[57, 58], [59, 60], [61, 62], [63, 64, 65], [66, 67, 68, 69], [70, 71], [72, 73]],
    },
    {
        "pageNumber": 6,
        "canonicalMeasureStart": 74,
        "canonicalMeasureEnd": 89,
        "rows": [[74, 75], [76, 77], [78, 79], [80, 81], [82, 83], [84, 85], [86, 87], [88, 89]],
    },
    {
        "pageNumber": 7,
        "canonicalMeasureStart": 90,
        "canonicalMeasureEnd": 96,
        "rows": [[90, 91], [92, 93, 94], [95, 96]],
    },
    {
        "pageNumber": 8,
        "canonicalMeasureStart": 97,
        "canonicalMeasureEnd": 113,
        "rows": [[97, 98], [99, 100], [101, 102, 103], [104, 105, 106], [107, 108], [109, 110], [111, 112], [113]],
    },
]


def flatten_rows() -> list[int]:
    return [
        measure
        for page in CANONICAL_PAGES
        for row in page["rows"]
        for measure in row
    ]


def main() -> None:
    if not ANCHOR_PATH.exists():
        raise RuntimeError(f"Missing v8 anchor manifest: {ANCHOR_PATH.relative_to(ROOT)}")

    anchors = json.loads(ANCHOR_PATH.read_text(encoding="utf-8"))
    if not anchors.get("complete1To113CoveragePassed", False):
        raise RuntimeError("V8 anchor manifest has not passed complete 1-113 coverage")

    flattened = flatten_rows()
    unique = sorted(set(flattened))
    duplicates = sorted({m for m in flattened if flattened.count(m) > 1})
    missing = sorted(set(range(1, EXPECTED_MEASURES + 1)) - set(unique))
    out_of_range = sorted(m for m in unique if not 1 <= m <= EXPECTED_MEASURES)
    ordered = flattened == list(range(1, EXPECTED_MEASURES + 1))

    page_results = []
    for page in CANONICAL_PAGES:
        row_flat = [m for row in page["rows"] for m in row]
        expected = list(range(page["canonicalMeasureStart"], page["canonicalMeasureEnd"] + 1))
        page_results.append(
            {
                **page,
                "rowCount": len(page["rows"]),
                "measureCount": len(row_flat),
                "continuousWithinPage": row_flat == expected,
                "localizationMethod": "visual-source-row-verification",
                "candidateAudioUsed": False,
            }
        )

    complete = (
        len(unique) == EXPECTED_MEASURES
        and not duplicates
        and not missing
        and not out_of_range
        and ordered
        and all(page["continuousWithinPage"] for page in page_results)
    )

    output = {
        "diagnosticName": "Gomyway rhythm PDF canonical source row manifest v9",
        "referenceType": "professional-rhythm-tab-source-localization",
        "pdfPageCountUsedAsAuthority": 8,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "canonicalMeasureCount": len(unique),
        "canonicalRows": sum(page["rowCount"] for page in page_results),
        "completeOrdered1To113CoveragePassed": complete,
        "missingMeasures": missing,
        "duplicateCanonicalMeasures": duplicates,
        "outOfRangeMeasures": out_of_range,
        "pages": page_results,
        "verifiedMeasures1To16Protected": True,
        "candidateAudioUsed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "noteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "canonical-row-pixel-localization",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF canonical source row manifest v9 complete")
    print(f"Canonical rows: {output['canonicalRows']}")
    print(f"Canonical measures: {output['canonicalMeasureCount']}")
    print(f"Complete ordered 1-113 coverage passed: {complete}")
    print(f"Missing measures: {missing}")
    print(f"Duplicate canonical measures: {duplicates}")
    print(f"Out-of-range measures: {out_of_range}")
    for page in page_results:
        print(
            f"Page {page['pageNumber']}: "
            f"measures {page['canonicalMeasureStart']}-{page['canonicalMeasureEnd']}, "
            f"{page['rowCount']} rows, continuous={page['continuousWithinPage']}"
        )
    print("Verified measures 1-16 protected: True")
    print("Candidate audio used: False")
    print("Note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("Canonical v9 row manifest failed ordered 1-113 validation")


if __name__ == "__main__":
    main()
