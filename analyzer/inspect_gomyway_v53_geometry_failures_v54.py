"""Build a compact visual audit for the v53 full-song geometry failures.

This diagnostic does not rerun detection or modify any locked result. It reads
v53 reports, copies the failed annotated previews into page-sized contact
sheets, and groups the failures by whether no six-line sequence was found or a
sequence was found but failed validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-full-song-string-line-geometry-v53.json"
OUTPUT = PUBLIC / "gomyway-v53-geometry-failure-audit-v54.json"
PREVIEW_DIR = PUBLIC / "gomyway-v53-geometry-failure-audit-v54"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless numpy") from exc

    source = load_json(SOURCE)
    if source.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("Locked-measure safeguard is not intact")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V53 complete measures 17-113 coverage did not pass")

    failed = [
        row for row in source.get("rows", [])
        if row.get("geometryCalibrationPassed") is not True
    ]
    if not failed:
        raise RuntimeError("V53 has no failed rows to inspect")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    cards: list[Any] = []
    reports: list[dict[str, Any]] = []
    no_sequence = 0
    rejected_sequence = 0

    for row in failed:
        preview_path = ROOT / str(row.get("preview"))
        image = cv2.imread(str(preview_path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Unreadable preview: {preview_path.relative_to(ROOT)}")

        selected = row.get("selectedStringRowsPixels", [])
        failure_type = "no-six-line-sequence" if not selected else "sequence-rejected"
        if failure_type == "no-six-line-sequence":
            no_sequence += 1
        else:
            rejected_sequence += 1

        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        measures = row.get("measures", [])
        label = (
            f"p{page} r{row_index} m{','.join(str(v) for v in measures)} | "
            f"{failure_type} | seg={row.get('houghHorizontalSegments')} "
            f"clusters={row.get('clusterCount')} spacing={row.get('selectedSpacingPixels')} "
            f"gapStd={row.get('gapStandardDeviation')}"
        )

        target_width = 1100
        scale = target_width / max(1, image.shape[1])
        resized = cv2.resize(
            image,
            (target_width, max(1, round(image.shape[0] * scale))),
            interpolation=cv2.INTER_AREA,
        )
        header = np.full((54, target_width, 3), 245, dtype=np.uint8)
        cv2.putText(
            header,
            label[:150],
            (12, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )
        card = np.vstack([header, resized])
        cards.append(card)

        reports.append(
            {
                "pageNumber": page,
                "rowIndex": row_index,
                "measures": measures,
                "failureType": failure_type,
                "segments": row.get("houghHorizontalSegments"),
                "clusters": row.get("clusterCount"),
                "selectedSpacingPixels": row.get("selectedSpacingPixels"),
                "gapStandardDeviation": row.get("gapStandardDeviation"),
                "sourcePreview": str(preview_path.relative_to(ROOT)),
            }
        )

    sheets: list[str] = []
    per_sheet = 4
    for start in range(0, len(cards), per_sheet):
        batch = cards[start : start + per_sheet]
        width = max(card.shape[1] for card in batch)
        padded: list[Any] = []
        for card in batch:
            if card.shape[1] < width:
                pad = np.full(
                    (card.shape[0], width - card.shape[1], 3),
                    245,
                    dtype=np.uint8,
                )
                card = np.hstack([card, pad])
            padded.append(card)
        sheet = np.vstack(padded)
        path = PREVIEW_DIR / f"failure-contact-sheet-{start // per_sheet + 1:02d}.png"
        cv2.imwrite(str(path), sheet)
        sheets.append(str(path.relative_to(ROOT)))

    output = {
        "diagnosticName": "Gomyway v53 geometry failure audit v54",
        "source": str(SOURCE.relative_to(ROOT)),
        "failedRows": len(failed),
        "noSixLineSequenceRows": no_sequence,
        "sequenceRejectedRows": rejected_sequence,
        "contactSheets": sheets,
        "rows": reports,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-v54-failure-contact-sheets",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("V53 geometry failure audit v54 complete")
    print(f"Failed rows inspected: {len(failed)}")
    print(f"No six-line sequence found: {no_sequence}")
    print(f"Sequence found but rejected: {rejected_sequence}")
    print(f"Contact sheets built: {len(sheets)}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Professional fret glyph recognition performed: False")
    print("Next required stage: human-review-v54-failure-contact-sheets")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Contact sheets: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
