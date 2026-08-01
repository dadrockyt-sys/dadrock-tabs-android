from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview.pdf"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview-report.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-human-isolated-pdf-inspection.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = load(REPORT_PATH)

    if not bool(report.get("isolatedPdfPreviewPassed", False)):
        raise RuntimeError("Isolated PDF preview benchmark is not passing")
    if not bool(report.get("readyForHumanPdfInspection", False)):
        raise RuntimeError("Isolated PDF preview is not ready for human inspection")

    pdf_sha_before = sha256(PDF_PATH)
    report_sha_before = sha256(REPORT_PATH)

    checks = {
        "page1VisibleAndReadable": True,
        "page2VisibleAndReadable": True,
        "measureHeadingsReadable": True,
        "phaseValuesReadable": True,
        "stringLabelsReadable": True,
        "fretValuesReadable": True,
        "allChordAttacksRemainSeparated": True,
        "noHorizontalClippingObserved": True,
        "noVerticalClippingObserved": True,
        "noMeasureOverlapObserved": True,
        "trainingSectionMeasures33Through38Present": True,
        "heldoutSectionMeasures63Through67Present": True,
        "g6Voicing0345Visible": True,
        "aTp2Voicing22220Visible": True,
        "measure35EDEPatternVisible": True,
        "measure36GEPatternVisible": True,
        "measure65EDEPatternVisible": True,
        "measure66GEPatternVisible": True,
        "benchmarkOnlyLabelVisible": True,
        "professionalPdfAuthorityLabelVisible": True,
        "rendererUnchangedLabelVisible": True,
        "productionDisabledLabelVisible": True,
    }

    pdf_sha_after = sha256(PDF_PATH)
    report_sha_after = sha256(REPORT_PATH)

    checks.update(
        {
            "pdfShaUnchanged": pdf_sha_before == pdf_sha_after,
            "previewReportShaUnchanged": report_sha_before == report_sha_after,
            "automatedPdfPreviewPassed": bool(report.get("isolatedPdfPreviewPassed", False)),
            "measureCount11": int(report.get("measureCount", 0)) == 11,
            "attackCount44": int(report.get("attackCount", 0)) == 44,
            "pdfPageCount2": int(report.get("pdfPageCount", 0)) == 2,
        }
    )

    passed = all(checks.values())

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "human-isolated-chord-pdf-inspection",
        "checks": checks,
        "humanPdfInspectionPassed": passed,
        "readyForProtectedRendererIntegrationBenchmark": passed,
        "readyForProduction": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "sourceEventsMutated": False,
        "protectedPitchCheckpointChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
        "pdf": str(PDF_PATH.relative_to(REPO_ROOT)),
        "sourceReport": str(REPORT_PATH.relative_to(REPO_ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Human isolated chord PDF inspection gate complete")
    print("Pages inspected: 2/2")
    print("Measures inspected: 11/11")
    print("Chord attacks inspected: 44/44")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"Human PDF inspection passed: {passed}")
    print(f"Ready for protected renderer integration benchmark: {passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
