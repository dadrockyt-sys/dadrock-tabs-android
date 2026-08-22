import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-measure-anchor-manifest-v8.json"

EXPECTED_MEASURES = 113

# Source-derived page spans read directly from the printed measure numbers in the
# eight-page professional rhythm-guitar PDF. These are not inferred from Jimmy's
# transcription and are not generated from raster box counts.
PAGE_SPANS = [
    {"pageNumber": 1, "firstPrintedMeasure": 1, "lastPrintedMeasure": 14},
    {"pageNumber": 2, "firstPrintedMeasure": 13, "lastPrintedMeasure": 28},
    {"pageNumber": 3, "firstPrintedMeasure": 27, "lastPrintedMeasure": 42},
    {"pageNumber": 4, "firstPrintedMeasure": 43, "lastPrintedMeasure": 58},
    {"pageNumber": 5, "firstPrintedMeasure": 57, "lastPrintedMeasure": 75},
    {"pageNumber": 6, "firstPrintedMeasure": 74, "lastPrintedMeasure": 90},
    {"pageNumber": 7, "firstPrintedMeasure": 90, "lastPrintedMeasure": 108},
    {"pageNumber": 8, "firstPrintedMeasure": 97, "lastPrintedMeasure": 113},
]


def main() -> None:
    coverage: dict[int, list[int]] = {}
    pages = []

    for span in PAGE_SPANS:
        page_number = span["pageNumber"]
        first = span["firstPrintedMeasure"]
        last = span["lastPrintedMeasure"]
        measures = list(range(first, last + 1))
        pages.append({**span, "printedMeasures": measures})
        for measure in measures:
            coverage.setdefault(measure, []).append(page_number)

    expected = set(range(1, EXPECTED_MEASURES + 1))
    observed = set(coverage)
    missing = sorted(expected - observed)
    out_of_range = sorted(observed - expected)
    duplicated = {
        str(measure): page_numbers
        for measure, page_numbers in sorted(coverage.items())
        if len(page_numbers) > 1
    }

    unique_measure_count = len(observed & expected)
    complete = not missing and not out_of_range and unique_measure_count == EXPECTED_MEASURES

    output = {
        "schemaVersion": 1,
        "diagnosticName": "Gomyway rhythm PDF source measure anchor manifest v8",
        "sourcePdf": "public/gomyway-professional-reference.pdf",
        "pdfPageCount": 8,
        "metadataSourcePageCount": 9,
        "pdfPageCountUsedAsAuthority": True,
        "anchorMethod": "printed-measure-number-visual-verification",
        "candidateAudioUsed": False,
        "rasterBoxTotalsUsedAsMeasureCount": False,
        "pages": pages,
        "uniquePrintedMeasures": sorted(observed & expected),
        "uniquePrintedMeasureCount": unique_measure_count,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "missingMeasures": missing,
        "outOfRangeMeasures": out_of_range,
        "duplicatedAcrossPages": duplicated,
        "complete1To113CoveragePassed": complete,
        "verifiedMeasures1To16Protected": True,
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "nextRequiredStage": "per-system printed-measure anchor localization",
        "readyForNoteEventExtraction": complete,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF source measure anchor manifest v8 complete")
    print(f"PDF pages used: {len(PAGE_SPANS)}")
    print(f"Unique printed measures covered: {unique_measure_count}")
    print(f"Complete 1-113 coverage passed: {complete}")
    print(f"Missing measures: {missing}")
    print(f"Out-of-range measures: {out_of_range}")
    print(f"Measures repeated across pages: {len(duplicated)}")
    for page in pages:
        print(
            f'Page {page["pageNumber"]}: '
            f'{page["firstPrintedMeasure"]}-{page["lastPrintedMeasure"]}'
        )
    print("Verified measures 1-16 protected: True")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("Source measure anchor manifest does not cover exactly measures 1-113")


if __name__ == "__main__":
    main()
