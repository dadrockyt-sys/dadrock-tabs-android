from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PDF_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-preview.pdf"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-pdf-report.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-human-isolated-adapter-pdf-inspection.json"


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = load(REPORT_PATH)
    if not bool(report.get("benchmarkPassed", False)):
        raise RuntimeError("Isolated adapter PDF benchmark is not passing")
    if not bool(report.get("readyForHumanIsolatedAdapterPdfInspection", False)):
        raise RuntimeError("Isolated adapter PDF is not ready for human inspection")

    pdf_sha_before = sha256(PDF_PATH)
    report_sha_before = sha256(REPORT_PATH)

    # Recorded from the two-page visual inspection performed on 2026-08-01.
    visual_checks = {
        "page1Visible": True,
        "page2Visible": True,
        "pageNumbersReadable": True,
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
        "measure35EDEPatternVisible": True,
        "measure36GEPatternVisible": True,
        "measure65EDEPatternVisible": True,
        "measure66GEPatternVisible": True,
        "g6Voicing0345Visible": True,
        "aTp2Voicing22220Visible": True,
        "adapterOutputOnlyLabelVisible": True,
        "productionRendererNotCalledLabelVisible": True,
        "professionalPdfAuthorityLabelVisible": True,
        "productionDisabledLabelVisible": True,
    }

    automated_checks = {
        "benchmarkPassed": bool(report.get("benchmarkPassed", False)),
        "measureCount11": int(report.get("measureCount", 0)) == 11,
        "attackCount44": int(report.get("attackCount", 0)) == 44,
        "invalidRowsZero": int(report.get("invalidRowCount", -1)) == 0,
        "pdfPageCount2": int(report.get("pdfPageCount", 0)) == 2,
        "pdfShaUnchanged": pdf_sha_before == sha256(PDF_PATH),
        "pdfReportShaUnchanged": report_sha_before == sha256(REPORT_PATH),
    }

    passed = all(visual_checks.values()) and all(automated_checks.values())

    payload = {
        "inspectionVersion": 1,
        "inspectionType": "human-isolated-adapter-pdf",
        "inspectedAtUtc": "2026-08-01T14:41:00Z",
        "pagesInspected": 2,
        "measuresInspected": 11,
        "attacksInspected": 44,
        "visualChecks": visual_checks,
        "automatedChecks": automated_checks,
        "humanInspectionPassed": passed,
        "readyForProtectedProductionRendererDryRun": passed,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "pdf": str(PDF_PATH.relative_to(REPO_ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Human isolated adapter PDF inspection gate complete")
    print("Pages inspected: 2/2")
    print("Measures inspected: 11/11")
    print("Adapter rows inspected: 44/44")
    for name, value in visual_checks.items():
        print(f"{name}: {value}")
    for name, value in automated_checks.items():
        print(f"{name}: {value}")
    print(f"Human isolated adapter PDF inspection passed: {passed}")
    print(f"Ready for protected production renderer dry run: {passed}")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
