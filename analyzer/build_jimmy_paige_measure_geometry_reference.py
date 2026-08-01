from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PUBLIC_DIR = Path("public")
AUTHORITY_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-professional-pdf-authority-selection.json"
SEED_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-verified-professional-technique-seed.json"
PROFESSIONAL_PDF = PUBLIC_DIR / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-jimmy-paige-measure-geometry-reference.json"

PAGE_MEASURE_RANGES = [
    {"page": 1, "measureStart": 1, "measureEnd": 14},
    {"page": 2, "measureStart": 13, "measureEnd": 26},
    {"page": 3, "measureStart": 27, "measureEnd": 42},
    {"page": 4, "measureStart": 43, "measureEnd": 56},
    {"page": 5, "measureStart": 57, "measureEnd": 75},
    {"page": 6, "measureStart": 74, "measureEnd": 89},
    {"page": 7, "measureStart": 90, "measureEnd": 108},
    {"page": 8, "measureStart": 97, "measureEnd": 113},
]

VERIFIED_GEOMETRY_TARGETS = [
    {
        "technique": "full-bend-release",
        "measures": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
        "primitives": ["upward-curve", "arrow-head", "release-curve", "amount-label"],
    },
    {
        "technique": "vibrato",
        "measures": [25, 26, 27, 55, 56, 57],
        "primitives": ["wavy-line"],
    },
    {
        "technique": "muted-note",
        "measures": [28, 58, 70, 72, 74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94],
        "primitives": ["x-notehead"],
    },
    {
        "technique": "pick-direction",
        "measures": [28, 58],
        "primitives": ["downstroke-symbol", "upstroke-symbol"],
    },
    {
        "technique": "chord-sustain-tie",
        "measures": [33, 34, 35, 36, 38, 63, 64, 65, 66, 93, 94, 106, 110, 111, 112, 113],
        "primitives": ["multi-string-tie"],
    },
    {
        "technique": "chord-slide",
        "measures": [71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91],
        "primitives": ["diagonal-slide-line"],
    },
    {
        "technique": "time-signature",
        "measures": [1, 104, 105],
        "primitives": ["stacked-numerals"],
    },
    {
        "technique": "section-label",
        "measures": [1, 17, 33, 39, 47, 63, 70, 78, 103],
        "primitives": ["italic-text-label"],
    },
    {
        "technique": "final-barline",
        "measures": [113],
        "primitives": ["double-barline"],
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        value = json.load(source)
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object JSON at {path}")
    return value


def main() -> None:
    for required in (AUTHORITY_PATH, SEED_PATH, PROFESSIONAL_PDF):
        if not required.exists():
            raise RuntimeError(f"Required input missing: {required}")

    authority = load_json(AUTHORITY_PATH)
    seed = load_json(SEED_PATH)

    authority_confirmed = bool(
        authority.get("professionalPdfAuthorityConfirmed")
        or authority.get("professional_pdf_authority_confirmed")
    )
    seed_passed = bool(seed.get("seedPassed") or seed.get("seed_passed"))

    if not authority_confirmed:
        raise RuntimeError("Professional PDF authority is not confirmed")
    if not seed_passed:
        raise RuntimeError("Verified technique seed has not passed")

    pdf_sha_before = sha256(PROFESSIONAL_PDF)

    worksheet_rows = []
    for target in VERIFIED_GEOMETRY_TARGETS:
        for measure in target["measures"]:
            page_candidates = [
                page["page"]
                for page in PAGE_MEASURE_RANGES
                if page["measureStart"] <= measure <= page["measureEnd"]
            ]
            worksheet_rows.append(
                {
                    "measure": measure,
                    "pageCandidates": page_candidates,
                    "technique": target["technique"],
                    "drawingPrimitives": target["primitives"],
                    "normalizedGeometry": {
                        "xStart": None,
                        "xEnd": None,
                        "yTop": None,
                        "yBottom": None,
                        "anchorString": None,
                        "anchorFret": None,
                    },
                    "status": "verified-location-awaiting-geometry",
                    "synthetic": False,
                }
            )

    result = {
        "schemaVersion": 1,
        "professionalPdf": str(PROFESSIONAL_PDF),
        "professionalPdfSha256": pdf_sha_before,
        "professionalPdfAuthorityConfirmed": authority_confirmed,
        "verifiedTechniqueSeedPassed": seed_passed,
        "pageMeasureRanges": PAGE_MEASURE_RANGES,
        "geometryTechniqueFamilies": len(VERIFIED_GEOMETRY_TARGETS),
        "geometryWorksheetRows": len(worksheet_rows),
        "rows": worksheet_rows,
        "syntheticAnnotationsCreated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForHumanGeometryAnnotation": True,
        "readyForTechniqueRendererTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    pdf_sha_after = sha256(PROFESSIONAL_PDF)
    pdf_unchanged = pdf_sha_before == pdf_sha_after
    result["professionalPdfShaUnchanged"] = pdf_unchanged
    result["worksheetPassed"] = bool(
        authority_confirmed
        and seed_passed
        and pdf_unchanged
        and len(worksheet_rows) > 0
    )
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Professional measure geometry reference worksheet complete")
    print(f"Professional PDF authority confirmed: {authority_confirmed}")
    print(f"Verified technique seed passed: {seed_passed}")
    print(f"Geometry technique families: {len(VERIFIED_GEOMETRY_TARGETS)}")
    print(f"Geometry worksheet rows: {len(worksheet_rows)}")
    print(f"Professional PDF SHA unchanged: {pdf_unchanged}")
    print(f"Worksheet passed: {result['worksheetPassed']}")
    print("Ready for human geometry annotation: True")
    print("Ready for technique renderer training: False")
    print("Synthetic annotations created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
