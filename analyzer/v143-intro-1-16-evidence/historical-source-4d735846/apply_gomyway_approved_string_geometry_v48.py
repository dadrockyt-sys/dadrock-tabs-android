"""Build a read-only professional note-event extraction scaffold for measures 17-113.

This stage does not recognize fret values and does not alter any locked data. It
combines the human-approved string-line geometry from v47 with the canonical row
localization manifest from v10, producing one extraction record per canonical
row covering measures 17-113. The output is intentionally a scaffold for the
next glyph-recognition stage.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
VALIDATION = PUBLIC / "gomyway-string-line-geometry-human-validation-v47.json"
LOCALIZATION = PUBLIC / "gomyway-rhythm-pdf-canonical-row-localization-v10.json"
OUTPUT = PUBLIC / "gomyway-approved-string-geometry-extraction-scaffold-v48.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def collect_rows(value: Any, inherited_page: int = 0) -> list[dict[str, Any]]:
    """Collect every localized row, preserving its enclosing page number.

    V10 stores rows separately under each entry in ``pages``. The original v48
    helper returned only the first page's rows, which meant measures 17-113 were
    never reached. This collector deliberately flattens all page groups.
    """
    collected: list[dict[str, Any]] = []

    if isinstance(value, dict):
        page_number = inherited_page
        try:
            page_number = int(value.get("pageNumber", inherited_page))
        except (TypeError, ValueError):
            page_number = inherited_page

        rows = value.get("rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict) or "measures" not in row:
                    continue
                normalized = dict(row)
                normalized.setdefault("pageNumber", page_number)
                collected.append(normalized)

        for key, child in value.items():
            if key == "rows":
                continue
            collected.extend(collect_rows(child, page_number))

    elif isinstance(value, list):
        for child in value:
            collected.extend(collect_rows(child, inherited_page))

    return collected


def normalize_measures(row: dict[str, Any]) -> list[int]:
    raw = row.get("measures", [])
    if not isinstance(raw, list):
        return []
    result: list[int] = []
    for value in raw:
        try:
            measure = int(value)
        except (TypeError, ValueError):
            continue
        if 17 <= measure <= 113:
            result.append(measure)
    return sorted(set(result))


def main() -> None:
    validation = load_json(VALIDATION)
    localization = load_json(LOCALIZATION)

    if validation.get("humanVisualValidationComplete") is not True:
        raise RuntimeError("V47 human visual validation is incomplete")
    if validation.get("allRowsHumanApproved") is not True:
        raise RuntimeError("V47 did not approve all locked geometry rows")
    if validation.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("V47 locked-measure safeguard is not intact")
    if localization.get("completeLocalizationScaffoldPassed") is not True:
        raise RuntimeError("V10 canonical localization scaffold did not pass")

    localized_rows = collect_rows(localization)
    if not localized_rows:
        raise RuntimeError("Could not find canonical localized rows in v10")

    scaffold_rows: list[dict[str, Any]] = []
    covered: set[int] = set()

    for row in localized_rows:
        measures = normalize_measures(row)
        if not measures:
            continue

        page_number = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        string_rows = (
            row.get("stringRowsPixels")
            or row.get("stringRowPixels")
            or row.get("rowsPixels")
            or []
        )

        if not isinstance(string_rows, list):
            string_rows = []

        scaffold_rows.append(
            {
                "pageNumber": page_number,
                "rowIndex": row_index,
                "measures": measures,
                "pixelBounds": row.get("pixelBounds", {}),
                "crop": row.get("crop"),
                "stringRowsPixels": string_rows,
                "approvedStringGeometryApplied": True,
                "candidateGlyphRecognitionPerformed": False,
                "semanticEvents": [],
            }
        )
        covered.update(measures)

    expected = set(range(17, 114))
    missing = sorted(expected - covered)
    out_of_range = sorted(covered - expected)
    complete = not missing and not out_of_range

    output = {
        "diagnosticName": "Gomyway approved string geometry extraction scaffold v48",
        "validationSource": str(VALIDATION.relative_to(ROOT)),
        "localizationSource": str(LOCALIZATION.relative_to(ROOT)),
        "canonicalRowsPrepared": len(scaffold_rows),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete,
        "missingMeasures": missing,
        "outOfRangeMeasures": out_of_range,
        "rows": scaffold_rows,
        "approvedStringGeometryApplied": True,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "recognize-professional-fret-glyphs-with-approved-row-specific-"
            "string-geometry-v49"
        ),
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Approved string geometry extraction scaffold v48 complete")
    print(f"Canonical rows prepared: {output['canonicalRowsPrepared']}")
    print(
        "Unique measures 17-113 covered: "
        f"{output['uniqueMeasures17To113Covered']}"
    )
    print(
        "Complete 17-113 coverage passed: "
        f"{output['complete17To113CoveragePassed']}"
    )
    print(f"Missing measures: {output['missingMeasures']}")
    print(f"Out-of-range measures: {output['outOfRangeMeasures']}")
    print("Approved string geometry applied: True")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V48 failed complete measures 17-113 coverage")


if __name__ == "__main__":
    main()
