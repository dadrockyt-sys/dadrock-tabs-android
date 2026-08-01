from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output.json"
OUTPUT_REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-output-report.json"
PDF_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-preview.pdf"
REPORT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-isolated-adapter-pdf-report.json"

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


def display_fret(value: Any) -> str:
    return "-" if value in (None, "", -1) else str(value)


def page_content(measures: list[dict[str, Any]], page: int, total: int) -> bytes:
    commands: list[str] = []

    def text(x: float, y: float, size: float, value: str, font: str = "F1") -> None:
        commands.append(f"BT /{font} {size:.1f} Tf {x:.1f} {y:.1f} Td ({pdf_escape(value)}) Tj ET")

    text(LEFT, PAGE_HEIGHT - TOP, 15, "DadRock AI - Isolated Adapter PDF Benchmark", "F2")
    text(LEFT, PAGE_HEIGHT - TOP - 18, 8.5, "ADAPTER OUTPUT ONLY - PRODUCTION RENDERER NOT CALLED")
    text(LEFT, PAGE_HEIGHT - TOP - 31, 8.5, "Professional PDF remains scoring authority")
    text(PAGE_WIDTH - RIGHT - 70, PAGE_HEIGHT - TOP, 8.5, f"Page {page}/{total}")

    y = PAGE_HEIGHT - TOP - 58
    usable_width = PAGE_WIDTH - LEFT - RIGHT

    for measure in measures:
        rows = sorted(measure["rows"], key=lambda row: (float(row.get("phase") or 0), int(row["attackNumber"])))
        text(LEFT, y, 10.5, f"Measure {measure['measureNumber']}", "F2")
        y -= 12
        count = max(len(rows), 1)
        label_width = 22
        column_width = (usable_width - label_width) / count

        text(LEFT, y, 7.5, "phase")
        for index, row in enumerate(rows):
            text(LEFT + label_width + index * column_width + 2, y, 7.5, f"{float(row.get('phase') or 0):.2f}")
        y -= 10

        for string_index, string_name in enumerate(STRING_ORDER):
            text(LEFT + 8, y, 8, string_name, "F2")
            for index, row in enumerate(rows):
                frets = row["fretsHighToLow"]
                text(LEFT + label_width + index * column_width + 5, y, 8.5, display_fret(frets[string_index]), "F2")
            y -= 9

        commands.append(f"0.75 w {LEFT:.1f} {y + 6:.1f} m {PAGE_WIDTH - RIGHT:.1f} {y + 6:.1f} l S")
        y -= 12

    text(LEFT, BOTTOM - 8, 7.5, "Isolated adapter output | Renderer unchanged | Production disabled")
    return ("\n".join(commands) + "\n").encode("latin-1")


def build_pdf(groups: list[list[dict[str, Any]]]) -> bytes:
    objects: list[bytes] = []

    def add(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    catalog_id = add(b"")
    pages_id = add(b"")
    regular_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    bold_id = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>")
    page_ids: list[int] = []

    for page_number, measures in enumerate(groups, start=1):
        stream = page_content(measures, page_number, len(groups))
        content_id = add(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"endstream")
        page_ids.append(add((f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 {regular_id} 0 R /F2 {bold_id} 0 R >> >> /Contents {content_id} 0 R >>").encode()))

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[catalog_id - 1] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()
    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()

    result = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, payload in enumerate(objects, start=1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode())
        result.extend(payload)
        result.extend(b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size {len(objects)+1} /Root {catalog_id} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(result)


def main() -> None:
    output = load(OUTPUT_JSON_PATH)
    output_report = load(OUTPUT_REPORT_PATH)

    if not bool(output_report.get("benchmarkPassed", False)):
        raise RuntimeError("Isolated adapter output benchmark is not passing")
    if not bool(output_report.get("readyForIsolatedAdapterPdfBenchmark", False)):
        raise RuntimeError("Isolated adapter output is not ready for PDF benchmark")

    output_sha_before = sha256(OUTPUT_JSON_PATH)
    report_sha_before = sha256(OUTPUT_REPORT_PATH)
    rows = output.get("rows", [])
    if not isinstance(rows, list) or len(rows) != 44:
        raise RuntimeError("Expected 44 isolated adapter rows")

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    invalid_rows = 0
    for row in rows:
        frets = row.get("fretsHighToLow") if isinstance(row, dict) else None
        if not isinstance(row, dict) or not isinstance(row.get("measureNumber"), int) or not isinstance(frets, list) or len(frets) != 6:
            invalid_rows += 1
            continue
        grouped[int(row["measureNumber"])].append(row)

    measures = [{"measureNumber": number, "rows": grouped[number]} for number in sorted(grouped)]
    pdf_bytes = build_pdf([measures[:6], measures[6:]])
    PDF_PATH.write_bytes(pdf_bytes)

    checks = {
        "isolatedAdapterOutputPassed": True,
        "measureCount11": len(measures) == 11,
        "attackCount44": sum(len(measure["rows"]) for measure in measures) == 44,
        "invalidRowsZero": invalid_rows == 0,
        "allRowsSixStrings": all(len(row["fretsHighToLow"]) == 6 for row in rows),
        "pdfHeaderValid": pdf_bytes.startswith(b"%PDF-1.4"),
        "pdfEofValid": pdf_bytes.rstrip().endswith(b"%%EOF"),
        "pdfPageCount2": pdf_bytes.count(b"/Type /Page ") == 2,
        "outputJsonShaUnchanged": output_sha_before == sha256(OUTPUT_JSON_PATH),
        "outputReportShaUnchanged": report_sha_before == sha256(OUTPUT_REPORT_PATH),
        "productionRendererCalledFalse": True,
        "productionOutputCreatedFalse": True,
    }
    passed = all(checks.values())

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "isolated-adapter-pdf",
        "checks": checks,
        "measureCount": len(measures),
        "attackCount": sum(len(measure["rows"]) for measure in measures),
        "invalidRowCount": invalid_rows,
        "pdfPageCount": pdf_bytes.count(b"/Type /Page "),
        "pdfByteLength": len(pdf_bytes),
        "pdfSha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "benchmarkPassed": passed,
        "readyForHumanIsolatedAdapterPdfInspection": passed,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "pdfOutput": str(PDF_PATH.relative_to(REPO_ROOT)),
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Isolated adapter PDF benchmark complete")
    print(f"Measures rendered: {len(measures)}/11")
    print(f"Adapter rows rendered: {report['attackCount']}/44")
    print(f"Invalid rows: {invalid_rows}")
    print(f"PDF pages: {report['pdfPageCount']}/2")
    print(f"Output JSON SHA unchanged: {checks['outputJsonShaUnchanged']}")
    print(f"Output report SHA unchanged: {checks['outputReportShaUnchanged']}")
    print(f"Benchmark passed: {passed}")
    print(f"Ready for human isolated adapter PDF inspection: {passed}")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"PDF: {PDF_PATH.relative_to(REPO_ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
