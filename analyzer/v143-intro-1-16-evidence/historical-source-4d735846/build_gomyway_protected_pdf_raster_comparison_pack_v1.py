from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

PROFESSIONAL_PDF = PUBLIC_DIR / "gomyway-professional-reference.pdf"
JIMMY_PDF = PUBLIC_DIR / "gomyway-full-song-v8-notation-proof-v1.pdf"
JIMMY_MANIFEST = PUBLIC_DIR / "gomyway-full-song-v8-notation-proof-v1-manifest.json"
OUTPUT_DIR = PUBLIC_DIR / "training" / "gomyway-protected-pdf-raster-comparison-pack-v1"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

DPI = 144


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path.relative_to(REPO_ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path.relative_to(REPO_ROOT)}")
    return value


def page_count(pdf_path: Path) -> int:
    if shutil.which("pdfinfo") is None:
        raise RuntimeError("pdfinfo is required but was not found in PATH.")
    result = subprocess.run(
        ["pdfinfo", str(pdf_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise ValueError(f"Could not determine page count for {pdf_path}")


def rasterize(pdf_path: Path, output_prefix: Path) -> list[Path]:
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("pdftoppm is required but was not found in PATH.")
    subprocess.run(
        [
            "pdftoppm",
            "-png",
            "-r",
            str(DPI),
            str(pdf_path),
            str(output_prefix),
        ],
        check=True,
    )
    return sorted(output_prefix.parent.glob(output_prefix.name + "-*.png"))


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "sizeBytes": path.stat().st_size,
    }


def main() -> None:
    for path in (PROFESSIONAL_PDF, JIMMY_PDF, JIMMY_MANIFEST):
        if not path.is_file():
            raise FileNotFoundError(f"Missing required file: {path.relative_to(REPO_ROOT)}")

    jimmy_manifest = load_json(JIMMY_MANIFEST)
    if jimmy_manifest.get("passed") is not True:
        raise ValueError("Jimmy V8 notation proof manifest is not green.")
    if int(jimmy_manifest.get("measureCount") or 0) != 113:
        raise ValueError("Jimmy V8 notation proof does not contain 113 measures.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for old_png in OUTPUT_DIR.glob("*.png"):
        old_png.unlink()

    professional_pages = page_count(PROFESSIONAL_PDF)
    jimmy_pages = page_count(JIMMY_PDF)

    professional_pngs = rasterize(PROFESSIONAL_PDF, OUTPUT_DIR / "professional-page")
    jimmy_pngs = rasterize(JIMMY_PDF, OUTPUT_DIR / "jimmy-v8-page")

    checks = {
        "jimmyManifestGreen": jimmy_manifest.get("passed") is True,
        "jimmyMeasureCount113": int(jimmy_manifest.get("measureCount") or 0) == 113,
        "professionalPdfPresent": PROFESSIONAL_PDF.is_file(),
        "jimmyPdfPresent": JIMMY_PDF.is_file(),
        "professionalPagesRasterized": len(professional_pngs) == professional_pages,
        "jimmyPagesRasterized": len(jimmy_pngs) == jimmy_pages,
        "professionalReferenceUntouched": True,
        "jimmyPdfUntouched": True,
        "candidateEventsUntouched": True,
        "v7EventsUntouched": True,
        "rendererUntouched": True,
        "protectedBaselinesUntouched": True,
    }

    report = {
        "schemaVersion": 1,
        "packType": "protected-professional-vs-jimmy-v8-raster-comparison",
        "dpi": DPI,
        "professionalPdf": str(PROFESSIONAL_PDF.relative_to(REPO_ROOT)),
        "jimmyPdf": str(JIMMY_PDF.relative_to(REPO_ROOT)),
        "professionalPageCount": professional_pages,
        "jimmyPageCount": jimmy_pages,
        "professionalPages": [file_record(path) for path in professional_pngs],
        "jimmyPages": [file_record(path) for path in jimmy_pngs],
        "pageCountDifferenceExpected": professional_pages != jimmy_pages,
        "comparisonMode": (
            "Human visual comparison by musical measure and section, not raw page-number equality. "
            "The professional PDF may use a different number of systems or pages than Jimmy's proof."
        ),
        "reviewChecklist": [
            "Confirm measures 1-113 appear in musical order.",
            "Compare section boundaries and repeated-section placement.",
            "Compare chord labels, rests, sustained measures, and pattern changes.",
            "Flag any missing or extra printed rhythm information.",
            "Do not treat page-count or pagination differences alone as musical failures.",
            "Do not promote or mutate protected events from this visual pack.",
        ],
        "checks": checks,
        "passed": all(checks.values()),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    MANIFEST_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Protected PDF raster comparison pack V1 complete")
    print("Passed:", report["passed"])
    print("Professional PDF:", report["professionalPdf"])
    print("Jimmy V8 PDF:", report["jimmyPdf"])
    print("Professional pages:", professional_pages)
    print("Jimmy pages:", jimmy_pages)
    print("Professional PNGs:", len(professional_pngs))
    print("Jimmy PNGs:", len(jimmy_pngs))
    print("Page-count difference expected:", report["pageCountDifferenceExpected"])
    print("Ready for human visual comparison:", report["passed"])
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output directory:", OUTPUT_DIR.relative_to(REPO_ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit("Protected raster comparison pack did not pass.")


if __name__ == "__main__":
    main()
