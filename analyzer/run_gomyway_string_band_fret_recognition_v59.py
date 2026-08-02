"""Recognize fret digits only inside six approved canonical string bands.

V56 searched connected components across the entire row crop, allowing rhythm
stems, bend graphics, lyrics, and technique marks to become fret candidates.
V59 instead processes six narrow, non-overlapping bands centred on the already
human-approved v55 string rows. It uses the original grayscale crop, removes only
the local horizontal string pixels, and rejects any component whose centre falls
outside its assigned string band.

This stage is read-only and diagnostic. Measures 1-16, V7 events, source images,
and production files are never modified.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
TEMPLATE_LIBRARY_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT_PATH = PUBLIC / "gomyway-string-band-fret-recognition-v59.json"
PREVIEW_DIR = PUBLIC / "gomyway-string-band-fret-recognition-v59"

REQUIRED_FRETS = ("0", "2", "3")
NORMALIZED_SIZE = (32, 32)
MIN_COMPONENT_AREA = 5
MAX_COMPONENT_AREA = 180
MIN_COMPONENT_HEIGHT = 5
MAX_COMPONENT_HEIGHT_RATIO = 0.88
MIN_COMPONENT_WIDTH = 2
MAX_COMPONENT_WIDTH_RATIO = 0.78
MIN_ASPECT_RATIO = 0.16
MAX_ASPECT_RATIO = 1.15
MIN_MATCH_SCORE = 0.52
MIN_MARGIN = 0.04
BAND_HALF_HEIGHT_RATIO = 0.43
STRING_ERASE_HALF_HEIGHT = 1


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_crop(job: dict[str, Any]) -> Path:
    for key in ("crop", "sourceCrop", "cropPath", "rowCrop", "imagePath", "previewPath"):
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
    return cv2.resize(patch, NORMALIZED_SIZE, interpolation=cv2.INTER_AREA)


def load_templates(cv2: Any, library: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    loaded: dict[str, list[dict[str, Any]]] = {fret: [] for fret in REQUIRED_FRETS}
    for fret in REQUIRED_FRETS:
        for entry in library.get("templates", {}).get(fret, []):
            image_path = ROOT / str(entry.get("templateImage", ""))
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
            loaded[fret].append({**entry, "image": normalize_patch(cv2, image)})
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
            scores.append((float(result.max()), str(entry.get("templateId", ""))))
        scores.sort(reverse=True)
        top = scores[: min(5, len(scores))]
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
    }


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    source = load_json(INPUT_PATH)
    library = load_json(TEMPLATE_LIBRARY_PATH)
    jobs = source.get("recognitionJobs", [])
    if source.get("allCanonicalRowsPromoted") is not True:
        raise RuntimeError("V55 did not promote all canonical rows")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V55 complete measures 17-113 coverage did not pass")
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

    print("Canonical string-band fret recognition v59 starting", flush=True)

    for job in jobs:
        crop_path = resolve_crop(job)
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unable to read {crop_path.relative_to(ROOT)}")

        rows = [float(value) for value in job.get("canonicalStringRowsPixels", [])]
        if len(rows) != 6:
            raise RuntimeError("V55 canonical row count changed")
        spacing = float(job.get("canonicalMedianSpacingPixels", 18.4))
        band_half_height = max(5, int(round(spacing * BAND_HALF_HEIGHT_RATIO)))
        max_height = max(MIN_COMPONENT_HEIGHT, int(round(spacing * MAX_COMPONENT_HEIGHT_RATIO)))
        max_width = max(MIN_COMPONENT_WIDTH, int(round(spacing * MAX_COMPONENT_WIDTH_RATIO)))

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        candidates: list[dict[str, Any]] = []

        for string_index, row_y_float in enumerate(rows):
            row_y = int(round(row_y_float))
            band_top = max(0, row_y - band_half_height)
            band_bottom = min(gray.shape[0], row_y + band_half_height + 1)
            if band_bottom <= band_top:
                continue

            band_gray = gray[band_top:band_bottom, :]
            binary = cv2.adaptiveThreshold(
                band_gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                21,
                8,
            )

            local_row = row_y - band_top
            erase_top = max(0, local_row - STRING_ERASE_HALF_HEIGHT)
            erase_bottom = min(binary.shape[0], local_row + STRING_ERASE_HALF_HEIGHT + 1)
            binary[erase_top:erase_bottom, :] = 0

            count, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, 8)
            for component_index in range(1, count):
                x, y_local, width, height, area = [int(value) for value in stats[component_index]]
                center_x, center_y_local = [float(value) for value in centroids[component_index]]
                y = y_local + band_top
                center_y = center_y_local + band_top

                if not (MIN_COMPONENT_AREA <= area <= MAX_COMPONENT_AREA):
                    continue
                if not (MIN_COMPONENT_WIDTH <= width <= max_width):
                    continue
                if not (MIN_COMPONENT_HEIGHT <= height <= max_height):
                    continue
                aspect_ratio = width / float(height)
                if not (MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO):
                    continue
                if abs(center_y - row_y_float) > band_half_height:
                    continue

                pad_x = max(3, round(width * 0.45))
                pad_y = max(3, round(height * 0.35))
                x0 = max(0, x - pad_x)
                y0 = max(band_top, y - pad_y)
                x1 = min(gray.shape[1], x + width + pad_x)
                y1 = min(band_bottom, y + height + pad_y)
                patch = gray[y0:y1, x0:x1]
                if patch.size == 0:
                    continue

                match = score_patch(cv2, patch, templates)
                candidate = {
                    "stringHighEToLowE": string_index + 1,
                    "boundingBox": {"x": x, "y": y, "width": width, "height": height},
                    "centroid": [round(center_x, 3), round(center_y, 3)],
                    "distanceToCanonicalStringPixels": round(abs(center_y - row_y_float), 3),
                    "bandTop": band_top,
                    "bandBottom": band_bottom,
                    "componentArea": area,
                    "aspectRatio": round(aspect_ratio, 3),
                    **match,
                }
                candidates.append(candidate)
                total_candidates += 1
                if match["accepted"]:
                    accepted_matches += 1
                    cv2.rectangle(preview, (x, y), (x + width, y + height), (0, 255, 0), 1)
                    cv2.putText(
                        preview,
                        str(match["recognizedFret"]),
                        (x, max(10, y - 2)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )

        for row_y_float in rows:
            row_y = int(round(row_y_float))
            cv2.line(preview, (0, row_y), (preview.shape[1] - 1, row_y), (255, 0, 0), 1)

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)
        preview_name = (
            f"page-{int(job.get('pageNumber', 0)):02d}-"
            f"row-{int(job.get('rowIndex', 0)):02d}.png"
        )
        preview_path = PREVIEW_DIR / preview_name
        cv2.imwrite(str(preview_path), preview)

        accepted = sum(1 for item in candidates if item["accepted"])
        output_jobs.append(
            {
                **job,
                "v59StringBandCandidates": candidates,
                "v59CandidateCount": len(candidates),
                "v59AcceptedFretMatchCount": accepted,
                "v59Preview": str(preview_path.relative_to(ROOT)),
                "wholeRowComponentSearchPerformed": False,
                "canonicalStringBandSearchPerformed": True,
            }
        )
        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, candidates={len(candidates)}, accepted={accepted}",
            flush=True,
        )

    complete_coverage = covered == set(range(17, 114))
    acceptance_ratio = accepted_matches / total_candidates if total_candidates else 0.0
    output = {
        "diagnosticName": "Gomyway canonical string-band fret recognition v59",
        "sourceCanonicalRows": str(INPUT_PATH.relative_to(ROOT)),
        "sourceLockedTemplateLibrary": str(TEMPLATE_LIBRARY_PATH.relative_to(ROOT)),
        "recognitionJobsProcessed": len(output_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "candidateComponentsObserved": total_candidates,
        "acceptedFretMatches": accepted_matches,
        "acceptedMatchRatio": round(acceptance_ratio, 6),
        "requiredFretClasses": [int(value) for value in REQUIRED_FRETS],
        "canonicalStringBandSearchPerformed": True,
        "wholeRowComponentSearchPerformed": False,
        "recognitionJobs": output_jobs,
        "humanVisualValidationRequired": True,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-v59-string-band-fret-previews",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Canonical string-band fret recognition v59 complete")
    print(f"Recognition jobs processed: {len(output_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"Candidate components observed: {total_candidates}")
    print(f"Accepted fret matches: {accepted_matches}")
    print(f"Accepted match ratio: {acceptance_ratio:.6f}")
    print("Canonical string-band search performed: True")
    print("Whole-row component search performed: False")
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
