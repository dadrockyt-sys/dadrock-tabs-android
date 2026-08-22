from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-protected-pdf-comparison-input-audit-v1.json"

COMPARISON_READY_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-merge-v1.json"

PDF_SUFFIXES = {".pdf"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}

PROFESSIONAL_TOKENS = (
    "professional",
    "benchmark",
    "reference",
    "example",
)
JIMMY_TOKENS = (
    "gomyway",
    "full-song",
    "rhythm",
    "notation",
    "measure-grid",
    "proof",
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def score_name(path: Path, tokens: tuple[str, ...]) -> int:
    name = path.name.lower()
    return sum(1 for token in tokens if token in name)


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(REPO_ROOT)),
        "name": path.name,
        "suffix": path.suffix.lower(),
        "sizeBytes": path.stat().st_size,
        "professionalScore": score_name(path, PROFESSIONAL_TOKENS),
        "jimmyScore": score_name(path, JIMMY_TOKENS),
    }


def choose_best(records: list[dict[str, Any]], score_key: str) -> dict[str, Any] | None:
    if not records:
        return None
    ranked = sorted(
        records,
        key=lambda item: (
            int(item.get(score_key, 0)),
            int(item.get("sizeBytes", 0)),
            item.get("path", ""),
        ),
        reverse=True,
    )
    best = ranked[0]
    if int(best.get(score_key, 0)) <= 0:
        return None
    return best


def main() -> None:
    completion = load_json(COMPARISON_READY_PATH)
    ready = bool(completion.get("readyForProtectedPdfComparison"))

    visual_files = [
        path
        for path in PUBLIC_DIR.rglob("*")
        if path.is_file()
        and path != OUTPUT_PATH
        and path.suffix.lower() in PDF_SUFFIXES | IMAGE_SUFFIXES
    ]

    records = [file_record(path) for path in sorted(visual_files)]
    pdf_records = [item for item in records if item["suffix"] in PDF_SUFFIXES]
    image_records = [item for item in records if item["suffix"] in IMAGE_SUFFIXES]

    professional_candidates = sorted(
        [item for item in records if item["professionalScore"] > 0],
        key=lambda item: (
            item["professionalScore"],
            item["sizeBytes"],
            item["path"],
        ),
        reverse=True,
    )
    jimmy_candidates = sorted(
        [item for item in pdf_records if item["jimmyScore"] > 0],
        key=lambda item: (
            item["jimmyScore"],
            item["sizeBytes"],
            item["path"],
        ),
        reverse=True,
    )

    selected_professional = choose_best(professional_candidates, "professionalScore")
    selected_jimmy = choose_best(jimmy_candidates, "jimmyScore")

    distinct_inputs = bool(
        selected_professional
        and selected_jimmy
        and selected_professional["path"] != selected_jimmy["path"]
    )

    passed = bool(ready and selected_professional and selected_jimmy and distinct_inputs)

    report = {
        "schemaVersion": 1,
        "auditType": "protected-pdf-comparison-input",
        "completionArtifact": str(COMPARISON_READY_PATH.relative_to(REPO_ROOT)),
        "fullSongReadyForComparison": ready,
        "visualFileCount": len(records),
        "pdfFileCount": len(pdf_records),
        "imageFileCount": len(image_records),
        "selectedProfessionalBenchmark": selected_professional,
        "selectedJimmyPdf": selected_jimmy,
        "distinctInputs": distinct_inputs,
        "professionalCandidates": professional_candidates[:30],
        "jimmyPdfCandidates": jimmy_candidates[:30],
        "passed": passed,
        "interpretation": (
            "This read-only gate inventories the repository's PDF and image assets, identifies the "
            "most likely uploaded professional benchmark and the most likely generated Jimmy rhythm "
            "PDF, and verifies that the full-song review-evidence merge has passed. It does not yet "
            "score visual or musical similarity. The selected paths must be confirmed by this audit "
            "before rasterization and protected page-by-page comparison begins."
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Protected PDF comparison input audit V1 complete")
    print("Passed:", report["passed"])
    print("Full-song ready for comparison:", report["fullSongReadyForComparison"])
    print("Visual files:", report["visualFileCount"])
    print("PDF files:", report["pdfFileCount"])
    print("Image files:", report["imageFileCount"])
    print("Selected professional benchmark:", (
        selected_professional["path"] if selected_professional else None
    ))
    print("Selected Jimmy PDF:", selected_jimmy["path"] if selected_jimmy else None)
    print("Distinct inputs:", report["distinctInputs"])
    print()

    print("Top professional candidates:")
    for item in professional_candidates[:10]:
        print(
            " ",
            item["path"],
            f"score={item['professionalScore']}",
            f"size={item['sizeBytes']}",
        )

    print()
    print("Top Jimmy PDF candidates:")
    for item in jimmy_candidates[:10]:
        print(
            " ",
            item["path"],
            f"score={item['jimmyScore']}",
            f"size={item['sizeBytes']}",
        )

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
