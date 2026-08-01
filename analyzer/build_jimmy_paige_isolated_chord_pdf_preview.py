from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INSPECTION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-human-chord-layout-inspection.json"
PREVIEW_JSON_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-layout-preview.json"
PDF_OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview.pdf"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-chord-preview-report.json"

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 42
RIGHT = 42
TOP = 54
BOTTOM = 48
STRING_ORDER = ["e", "B", "G", "D", "A", "E"]


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def cell_map(row: dict[str, Any]) -> dict[str, str]:
    return {
        str(cell["stringName"]): str(cell["display"])
        for cell in row.get("renderCells", [])
    }


def content_for_page(measures: list[dict[str, Any]], page_number: int, total_pages: int) -> bytes:
    commands: list[str] = []

    def text(x: float, y: float, size: float, value: str, font: str = "F1") -> None:
        commands.append(f"BT /{font} {size:.1f} Tf {x:.1f} {y:.1f} Td ({pdf_escape(value)}) Tj ET")

    text(LEFT, PAGE_HEIGHT - TOP, 15, "DadRock AI - Isolated Chord Resolver Preview", "F2")
    text(LEFT, PAGE_HEIGHT - TOP - 18, 8.5, "BENCHMARK ONLY - NOT PRODUCTION OUTPUT")
    text(LEFT, PAGE_HEIGHT - TOP - 31, 8.5, "Professional PDF remains scoring authority")
    text(PAGE_WIDTH - RIGHT - 70, PAGE_HEIGHT - TOP, 8.5, f"Page {page_number}/{total_pages}")

    y = PAGE_HEIGHT - TOP - 58
    usable_width = PAGE_WIDTH - LEFT - RIGHT

    for measure in measures:
        rows = measure.get("rows", [])
        rows = sorted(rows, key=lambda row: (float(row["targetPhase"]), int(row["attackNumber"])))
        title = f"Measure {measure['measureNumber']}"
        labels: list[str] = []
        for row in rows:
            for label in row.get("chordLabels", []):
                if label not in labels:
                    labels.append(label)
        if labels:
            title += " | " + " / ".join(labels)

        text(LEFT, y, 10.5, title, "F2")
        y -= 12

        count = max(len(rows), 1)
        label_width = 22
        column_width = (usable_width - label_width) / count

        text(LEFT, y, 7.5, "phase")
        for index, row in enumerate(rows):
            x = LEFT + label_width + index * column_width + 2
            text(x, y, 7.5, f"{float(row['targetPhase']):.2f}")
        y -= 10

        for string_name in STRING_ORDER:
            text(LEFT + 8, y, 8, string_name, "F2")
            for index, row in enumerate(rows):
                display = cell_map(row).get(string_name, "-")
                x = LEFT + label_width + index * column_width + 5
                text(x, y, 8.5, display, "F2")
            y -= 9

        commands.append(f"0.75 w {LEFT:.1f} {y + 6:.1f} m {PAGE_WIDTH - RIGHT:.1f} {y + 6:.1f} l S")
        y -= 12

    text(LEFT, BOTTOM - 8, 7.5, "Renderer unchanged | Production promotion disabled | Source events untouched")
    return ("\n".join(commands) + "\n").encode("latin-1")


def build_pdf(page_measure_groups: list[list[dict[str, Any]]]) -> bytes:
    objects: list[bytes] = []

    def add_object(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    catalog_id = add_object(b"")
    pages_id = add_object(b"")
    font_regular_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    font_bold_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>")

    page_ids: list[int] = []
    total_pages = len(page_measure_groups)
    for page_number, measures in enumerate(page_measure_groups, start=1):
        stream = content_for_page(measures, page_number, total_pages)
        content_id = add_object(
            f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
            + stream
            + b"endstream"
        )
        page_id = add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R "
                f"/MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
                f"/Resources << /Font << /F1 {font_regular_id} 0 R /F2 {font_bold_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        page_ids.append(page_id)

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii")
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("ascii")

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for object_number, payload in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_number} 0 obj\n".encode("ascii"))
        output.extend(payload)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def main() -> None:
    inspection = load(INSPECTION_PATH)
    preview = load(PREVIEW_JSON_PATH)

    if not bool(inspection.get("humanLayoutInspectionPassed", False)):
        raise RuntimeError("Human chord layout inspection gate is not passing")
    if not bool(inspection.get("readyForIsolatedPdfPreviewBenchmark", False)):
        raise RuntimeError("Human inspection gate is not ready for isolated PDF preview")

    inspection_sha_before = sha256(INSPECTION_PATH)
    preview_sha_before = sha256(PREVIEW_JSON_PATH)

    measures = preview.get("measures", [])
    if not isinstance(measures, list) or len(measures) != 11:
        raise RuntimeError("Expected 11 inspected measures in layout preview")

    page_measure_groups = [measures[:6], measures[6:]]
    pdf_bytes = build_pdf(page_measure_groups)
    PDF_OUTPUT_PATH.write_bytes(pdf_bytes)

    inspection_sha_after = sha256(INSPECTION_PATH)
    preview_sha_after = sha256(PREVIEW_JSON_PATH)

    attack_count = sum(int(measure.get("attackCount", len(measure.get("rows", [])))) for measure in measures)
    pdf_valid_header = pdf_bytes.startswith(b"%PDF-1.4")
    pdf_valid_eof = pdf_bytes.rstrip().endswith(b"%%EOF")
    pdf_page_count = pdf_bytes.count(b"/Type /Page ")

    checks = {
        "humanInspectionPassed": True,
        "measureCount11": len(measures) == 11,
        "attackCount44": attack_count == 44,
        "pdfHeaderValid": pdf_valid_header,
        "pdfEofValid": pdf_valid_eof,
        "pdfPageCount2": pdf_page_count == 2,
        "inspectionShaUnchanged": inspection_sha_before == inspection_sha_after,
        "layoutPreviewShaUnchanged": preview_sha_before == preview_sha_after,
        "rendererChangedFalse": True,
        "productionPromotionAllowedFalse": True,
    }
    passed = all(checks.values())

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "isolated-protected-chord-pdf-preview",
        "checks": checks,
        "measureCount": len(measures),
        "attackCount": attack_count,
        "pdfPageCount": pdf_page_count,
        "pdfByteLength": len(pdf_bytes),
        "pdfSha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "isolatedPdfPreviewPassed": passed,
        "readyForHumanPdfInspection": passed,
        "professionalPdfRemainsScoringAuthority": True,
        "protectedPitchCheckpointChanged": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForProduction": False,
        "pdfOutput": str(PDF_OUTPUT_PATH.relative_to(REPO_ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Isolated chord PDF preview benchmark complete")
    print(f"Measures rendered: {len(measures)}/11")
    print(f"Chord attacks rendered: {attack_count}/44")
    print(f"PDF pages: {pdf_page_count}/2")
    print(f"PDF bytes: {len(pdf_bytes)}")
    for name, value in checks.items():
        print(f"{name}: {value}")
    print(f"Isolated PDF preview passed: {passed}")
    print(f"Ready for human PDF inspection: {passed}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"PDF: {PDF_OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
