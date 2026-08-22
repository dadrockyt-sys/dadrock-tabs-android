"""Build a read-only visual audit for failed V60 row-local string lattices.

V60 attempted a tightly bounded six-string lattice registration for all 45
canonical rows covering measures 17-113. This stage does not rerun detection,
recognize frets, extract semantic note events, modify locked measures 1-16 or V7
events, use candidate audio, or promote anything to production. It only groups
failed V60 jobs and builds compact contact sheets from their existing previews.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-row-local-string-lattices-v60.json"
OUTPUT = PUBLIC / "gomyway-v60-row-local-string-lattice-failure-audit-v61.json"
PREVIEW_DIR = PUBLIC / "gomyway-v60-row-local-string-lattice-failure-audit-v61"

EXPECTED_JOB_COUNT = 45
EXPECTED_MEASURES = set(range(17, 114))


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
    if source.get("v7EventsModified") is not False:
        raise RuntimeError("Protected V7-event safeguard is not intact")
    if source.get("candidateAudioUsed") is not False:
        raise RuntimeError("V60 unexpectedly used candidate audio")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V60 complete measures 17-113 coverage did not pass")

    jobs = source.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != EXPECTED_JOB_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_JOB_COUNT} V60 jobs, found {len(jobs or [])}")

    covered = {
        int(measure)
        for job in jobs
        for measure in job.get("measures", [])
    }
    if covered != EXPECTED_MEASURES:
        missing = sorted(EXPECTED_MEASURES - covered)
        extra = sorted(covered - EXPECTED_MEASURES)
        raise RuntimeError(f"V60 measure coverage mismatch; missing={missing}, extra={extra}")

    failed = [
        job for job in jobs
        if job.get("v60RowLocalRegistrationPassed") is not True
    ]
    if not failed:
        raise RuntimeError("V60 has no failed jobs to inspect")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    cards: list[Any] = []
    reports: list[dict[str, Any]] = []
    reason_counts: dict[str, int] = {}
    no_valid_lattice = 0
    weak_continuity = 0
    other_failures = 0

    for job in failed:
        preview_value = job.get("v60RegistrationPreview")
        if not isinstance(preview_value, str) or not preview_value:
            raise RuntimeError(
                f"Missing V60 preview for page {job.get('pageNumber')} row {job.get('rowIndex')}"
            )

        preview_path = ROOT / preview_value
        image = cv2.imread(str(preview_path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Unreadable preview: {preview_path.relative_to(ROOT)}")

        registration = job.get("v60Registration", {})
        reason = str(registration.get("reason") or "unknown")
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

        if reason == "no-valid-six-line-lattice":
            no_valid_lattice += 1
        elif reason == "weak-horizontal-continuity":
            weak_continuity += 1
        else:
            other_failures += 1

        page = int(job.get("pageNumber", 0))
        row_index = int(job.get("rowIndex", 0))
        measures = [int(value) for value in job.get("measures", [])]
        expected_rows = job.get("v60ExpectedCanonicalStringRowsPixels", [])
        registered_rows = job.get("v60RegisteredStringRowsPixels", [])

        label = (
            f"p{page} r{row_index} m{','.join(str(v) for v in measures)} | {reason} | "
            f"rows={len(registered_rows)} shift={registration.get('anchorShiftPixels')} "
            f"gap={registration.get('medianGapPixels')} "
            f"gapDev={registration.get('medianGapDeviationPixels')} "
            f"maxGapDev={registration.get('maxGapDeviationPixels')} "
            f"continuity={registration.get('minimumContinuity')}"
        )

        target_width = 1200
        scale = target_width / max(1, image.shape[1])
        resized = cv2.resize(
            image,
            (target_width, max(1, round(image.shape[0] * scale))),
            interpolation=cv2.INTER_AREA,
        )

        header = np.full((62, target_width, 3), 245, dtype=np.uint8)
        cv2.putText(
            header,
            label[:185],
            (12, 39),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )
        cards.append(np.vstack([header, resized]))

        reports.append(
            {
                "pageNumber": page,
                "rowIndex": row_index,
                "measures": measures,
                "failureReason": reason,
                "expectedCanonicalStringRowsPixels": expected_rows,
                "registeredStringRowsPixels": registered_rows,
                "anchorShiftPixels": registration.get("anchorShiftPixels"),
                "medianGapPixels": registration.get("medianGapPixels"),
                "medianGapDeviationPixels": registration.get("medianGapDeviationPixels"),
                "maxGapDeviationPixels": registration.get("maxGapDeviationPixels"),
                "minimumContinuity": registration.get("minimumContinuity"),
                "objective": registration.get("objective"),
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
        "diagnosticName": "Gomyway V60 row-local string-lattice failure audit V61",
        "source": str(SOURCE.relative_to(ROOT)),
        "recognitionJobsInspected": len(jobs),
        "failedJobs": len(failed),
        "passedJobs": len(jobs) - len(failed),
        "noValidSixLineLatticeFailures": no_valid_lattice,
        "weakHorizontalContinuityFailures": weak_continuity,
        "otherFailureCount": other_failures,
        "failureReasonCounts": reason_counts,
        "contactSheets": sheets,
        "jobs": reports,
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": covered == EXPECTED_MEASURES,
        "approvedV55GeometryUsedAsAnchor": source.get("approvedV55GeometryUsedAsAnchor") is True,
        "geometryRediscoveryPerformed": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": "human-review-v61-v60-lattice-failure-contact-sheets",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("V60 row-local string-lattice failure audit V61 complete")
    print(f"Recognition jobs inspected: {len(jobs)}")
    print(f"Failed jobs inspected: {len(failed)}")
    print(f"No valid six-line lattice: {no_valid_lattice}")
    print(f"Weak horizontal continuity: {weak_continuity}")
    print(f"Other failures: {other_failures}")
    print(f"Contact sheets built: {len(sheets)}")
    print(f"Complete 17-113 coverage passed: {covered == EXPECTED_MEASURES}")
    print("Geometry rediscovery performed: False")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print("Next required stage: human-review-v61-v60-lattice-failure-contact-sheets")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Contact sheets: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
