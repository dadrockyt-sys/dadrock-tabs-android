"""Run read-only locked fret-template matching over the proven v55 canonical rows.

This stage trusts v51/v55 stringRowsPixels and never rediscovers TAB geometry.
It extracts small glyph candidates around each approved string row, suppresses the
horizontal staff line locally, and compares candidates against the human-reviewed
locked fret 0/2/3 template library from measures 1-16.

The output is diagnostic only. Measures 1-16, V7 events, source images, and
production files are never modified.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
TEMPLATE_LIBRARY_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-fret-template-matching-v56.json"
PREVIEW_DIR = PUBLIC / "gomyway-locked-fret-template-matching-v56"

REQUIRED_FRETS = ("0", "2", "3")
NORMALIZED_SIZE = (32, 32)
MIN_COMPONENT_AREA = 5
MAX_COMPONENT_AREA = 220
MIN_COMPONENT_HEIGHT = 5
MAX_COMPONENT_HEIGHT = 30
MIN_COMPONENT_WIDTH = 2
MAX_COMPONENT_WIDTH = 28
MIN_MATCH_SCORE = 0.50
MIN_MARGIN = 0.035


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_crop(job: dict[str, Any]) -> Path:
    for key in ("sourceCrop", "cropPath", "rowCrop", "imagePath", "previewPath"):
        value = job.get(key)
        if isinstance(value, str) and value:
            path = ROOT / value
            if path.exists():
                return path
    raise RuntimeError(
        f"No readable crop for page {job.get('pageNumber')} row {job.get('rowIndex')}"
    )


def normalize_patch(cv2: Any, patch: Any) -> Any:
    if patch.size == 0:
        raise ValueError("Empty patch")
    canvas = cv2.resize(patch, NORMALIZED_SIZE, interpolation=cv2.INTER_AREA)
    return canvas


def load_templates(cv2: Any, library: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    loaded: dict[str, list[dict[str, Any]]] = {fret: [] for fret in REQUIRED_FRETS}
    for fret in REQUIRED_FRETS:
        entries = library.get("templates", {}).get(fret, [])
        for entry in entries:
            image_path = ROOT / str(entry.get("templateImage", ""))
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
            image = normalize_patch(cv2, image)
            loaded[fret].append({**entry, "image": image})
        if not loaded[fret]:
            raise RuntimeError(f"No readable locked templates for fret {fret}")
    return loaded


def score_patch(cv2: Any, patch: Any, templates: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    normalized = normalize_patch(cv2, patch)
    per_fret: dict[str, float] = {}
    best_template_by_fret: dict[str, str] = {}

    for fret, entries in templates.items():
        scores: list[tuple[float, str]] = []
        for entry in entries:
            result = cv2.matchTemplate(normalized, entry["image"], cv2.TM_CCOEFF_NORMED)
            score = float(result.max())
            scores.append((score, str(entry.get("templateId", ""))))
        scores.sort(reverse=True)
        top = scores[: min(5, len(scores))]
        # Median-like robust average of the strongest locked examples.
        per_fret[fret] = sum(score for score, _ in top) / len(top)
        best_template_by_fret[fret] = top[0][1]

    ranked = sorted(per_fret.items(), key=lambda item: item[1], reverse=True)
    best_fret, best_score = ranked[0]
    second_score = ranked[1][1]
    margin = best_score - second_score
    accepted = best_score >= MIN_MATCH_SCORE and margin >= MIN_MARGIN
    return {
        "recognizedFret": int(best_fret) if accepted else None,
        "bestFretHypothesis": int(best_fret),
        "bestScore": round(best_score, 6),
        "secondBestScore": round(second_score, 6),
        "scoreMargin": round(margin, 6),
        "accepted": accepted,
        "scoresByFret": {key: round(value, 6) for key, value in per_fret.items()},
        "bestTemplateByFret": best_template_by_fret,
        "normalizedSize": list(NORMALIZED_SIZE),
    }


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless numpy") from exc

    source = load_json(INPUT_PATH)
    library = load_json(TEMPLATE_LIBRARY_PATH)

    if source.get("allCanonicalRowsPromoted") is not True:
        raise RuntimeError("V55 did not promote all canonical rows")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V55 complete measures 17-113 coverage did not pass")
    jobs = source.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 v55 jobs, found {len(jobs or [])}")
    if library.get("templateLibraryBuilt") is not True:
        raise RuntimeError("Locked glyph template library v33 was not built")

    templates = load_templates(cv2, library)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    output_jobs: list[dict[str, Any]] = []
    total_candidates = 0
    accepted_matches = 0
    covered: set[int] = set()

    print("Locked fret template matching v56 starting", flush=True)

    for job in jobs:
        crop_path = resolve_crop(job)
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unable to read {crop_path.relative_to(ROOT)}")

        rows = [float(value) for value in job.get("canonicalStringRowsPixels", [])]
        if len(rows) != 6:
            raise RuntimeError("V55 canonical row count changed")

        # Dark glyph foreground on white background.
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            8,
        )

        # Remove only a narrow horizontal band centered on each trusted string row.
        cleaned = binary.copy()
        for row_y in rows:
            y = max(0, min(cleaned.shape[0] - 1, int(round(row_y))))
            cleaned[max(0, y - 1): min(cleaned.shape[0], y + 2), :] = 0

        count, labels, stats, centroids = cv2.connectedComponentsWithStats(cleaned, 8)
        candidates: list[dict[str, Any]] = []
        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        for component_index in range(1, count):
            x, y, width, height, area = [int(value) for value in stats[component_index]]
            center_x, center_y = [float(value) for value in centroids[component_index]]
            if not (MIN_COMPONENT_AREA <= area <= MAX_COMPONENT_AREA):
                continue
            if not (MIN_COMPONENT_WIDTH <= width <= MAX_COMPONENT_WIDTH):
                continue
            if not (MIN_COMPONENT_HEIGHT <= height <= MAX_COMPONENT_HEIGHT):
                continue

            distances = [abs(center_y - row_y) for row_y in rows]
            string_index = int(min(range(6), key=lambda index: distances[index]))
            local_spacing = float(job.get("canonicalMedianSpacingPixels", 18.4))
            if distances[string_index] > max(8.0, local_spacing * 0.48):
                continue

            pad_x = max(3, round(width * 0.45))
            pad_y = max(3, round(height * 0.35))
            x0 = max(0, x - pad_x)
            y0 = max(0, y - pad_y)
            x1 = min(gray.shape[1], x + width + pad_x)
            y1 = min(gray.shape[0], y + height + pad_y)
            patch = gray[y0:y1, x0:x1]
            if patch.size == 0:
                continue

            match = score_patch(cv2, patch, templates)
            candidate = {
                "componentIndex": component_index,
                "boundingBox": {"x": x, "y": y, "width": width, "height": height},
                "centroid": [round(center_x, 3), round(center_y, 3)],
                "stringHighEToLowE": string_index + 1,
                "distanceToCanonicalStringPixels": round(distances[string_index], 3),
                **match,
            }
            candidates.append(candidate)
            total_candidates += 1
            if match["accepted"]:
                accepted_matches += 1
                cv2.rectangle(preview, (x, y), (x + width, y + height), (255, 255, 255), 1)
                cv2.putText(
                    preview,
                    str(match["recognizedFret"]),
                    (x, max(10, y - 2)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)
        preview_name = f"page-{int(job.get('pageNumber', 0)):02d}-row-{int(job.get('rowIndex', 0)):02d}.png"
        preview_path = PREVIEW_DIR / preview_name
        cv2.imwrite(str(preview_path), preview)

        accepted = sum(1 for item in candidates if item["accepted"])
        output_jobs.append(
            {
                **job,
                "candidateComponents": candidates,
                "candidateComponentCount": len(candidates),
                "acceptedFretMatchCount": accepted,
                "recognitionPerformed": True,
                "recognitionPreview": str(preview_path.relative_to(ROOT)),
                "geometryRediscoveryPerformed": False,
            }
        )
        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, candidates={len(candidates)}, accepted={accepted}",
            flush=True,
        )

    complete_coverage = covered == set(range(17, 114))
    recognition_performed = len(output_jobs) == 45 and complete_coverage
    acceptance_ratio = accepted_matches / total_candidates if total_candidates else 0.0

    output = {
        "diagnosticName": "Gomyway locked fret template matching v56",
        "sourceCanonicalRows": str(INPUT_PATH.relative_to(ROOT)),
        "sourceLockedTemplateLibrary": str(TEMPLATE_LIBRARY_PATH.relative_to(ROOT)),
        "recognitionJobsProcessed": len(output_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "candidateComponentsObserved": total_candidates,
        "acceptedFretMatches": accepted_matches,
        "acceptedMatchRatio": round(acceptance_ratio, 6),
        "requiredFretClasses": [int(value) for value in REQUIRED_FRETS],
        "minimumMatchScore": MIN_MATCH_SCORE,
        "minimumScoreMargin": MIN_MARGIN,
        "professionalFretGlyphRecognitionPerformed": recognition_performed,
        "geometryRediscoveryPerformed": False,
        "recognitionJobs": output_jobs,
        "humanVisualValidationRequired": True,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-v56-locked-fret-recognition-previews-v57",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked fret template matching v56 complete")
    print(f"Recognition jobs processed: {len(output_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"Candidate components observed: {total_candidates}")
    print(f"Accepted fret matches: {accepted_matches}")
    print(f"Accepted match ratio: {acceptance_ratio:.6f}")
    print(f"Professional fret glyph recognition performed: {recognition_performed}")
    print("Geometry rediscovery performed: False")
    print("Human visual validation required: True")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
