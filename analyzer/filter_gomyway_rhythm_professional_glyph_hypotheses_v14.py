import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-rhythm-professional-symbol-candidates-v13.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-glyph-hypotheses-v14.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-professional-glyph-hypotheses-v14"

LOCKED_MEASURE_END = 16
TARGET_MEASURE_START = 17
TARGET_MEASURE_END = 113


def cluster_x(candidates: list[dict[str, Any]], tolerance: float) -> list[list[dict[str, Any]]]:
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda item: float(item["centerPixels"]["x"]))
    groups: list[list[dict[str, Any]]] = [[ordered[0]]]
    for candidate in ordered[1:]:
        center = median(float(item["centerPixels"]["x"]) for item in groups[-1])
        if abs(float(candidate["centerPixels"]["x"]) - center) <= tolerance:
            groups[-1].append(candidate)
        else:
            groups.append([candidate])
    return groups


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing v13 candidates: {INPUT_PATH.relative_to(ROOT)}")

    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if not source.get("complete17To113MeasureCoveragePassed", False):
        raise RuntimeError("V13 did not pass complete 17-113 coverage")
    if source.get("lockedMeasures1To16Touched", True):
        raise RuntimeError("V13 touched protected measures 1-16")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rows_output = []
    total_input = 0
    total_string_local = 0
    total_compact = 0
    total_columns = 0
    measures_seen: list[int] = []
    geometry_counts: Counter[str] = Counter()

    print("Professional rhythm glyph hypothesis filtering v14 starting", flush=True)

    for row in source["rows"]:
        measures = [int(value) for value in row["measures"]]
        string_rows = [int(value) for value in row["stringRowsPixelsHighEToLowE"]]
        if len(string_rows) != 6:
            raise RuntimeError(
                f"Expected six strings on page {row['pageNumber']} row {row['rowIndex']}"
            )
        spacing = float(median(string_rows[index + 1] - string_rows[index] for index in range(5)))

        candidates = row["symbolCandidates"]
        total_input += len(candidates)
        string_local = [
            candidate
            for candidate in candidates
            if candidate.get("nearestStringIndexHighEToLowE") is not None
            and float(candidate.get("distanceToNearestStringPixels", 9999)) <= spacing * 0.72
        ]
        compact = [
            candidate
            for candidate in string_local
            if candidate.get("geometryClass") == "compact-glyph-candidate"
            and int(candidate["boundsPixels"]["width"]) <= round(spacing * 1.9)
            and int(candidate["boundsPixels"]["height"]) <= round(spacing * 1.9)
            and int(candidate["areaPixels"]) >= max(5, round(spacing * spacing * 0.06))
        ]

        for candidate in string_local:
            geometry_counts[str(candidate.get("geometryClass"))] += 1

        groups = cluster_x(compact, max(4.0, spacing * 0.55))
        columns = []
        for column_index, group in enumerate(groups, start=1):
            string_indices = sorted(
                {
                    int(item["nearestStringIndexHighEToLowE"])
                    for item in group
                    if item.get("nearestStringIndexHighEToLowE") is not None
                }
            )
            center_x = round(median(float(item["centerPixels"]["x"]) for item in group), 2)
            columns.append(
                {
                    "columnIndex": column_index,
                    "centerX": center_x,
                    "candidateCount": len(group),
                    "stringIndicesHighEToLowE": string_indices,
                    "candidateIndices": [int(item["candidateIndex"]) for item in group],
                    "semanticValues": None,
                    "recognitionStatus": "unrecognized",
                    "requiresTemplateRecognition": True,
                    "requiresHumanVerification": True,
                }
            )

        image = cv2.imread(str(ROOT / row["sourceCrop"]), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(f"Unable to read source crop: {row['sourceCrop']}")
        for y in string_rows:
            cv2.line(image, (0, y), (image.shape[1] - 1, y), (255, 0, 0), 1)
        by_index = {int(candidate["candidateIndex"]): candidate for candidate in candidates}
        for column in columns:
            x = round(float(column["centerX"]))
            cv2.line(image, (x, max(0, string_rows[0] - round(spacing))), (x, min(image.shape[0] - 1, string_rows[-1] + round(spacing))), (0, 255, 255), 1)
            for candidate_index in column["candidateIndices"]:
                candidate = by_index[candidate_index]
                bounds = candidate["boundsPixels"]
                x0 = int(bounds["x"])
                y0 = int(bounds["y"])
                width = int(bounds["width"])
                height = int(bounds["height"])
                cv2.rectangle(image, (x0, y0), (x0 + width, y0 + height), (0, 0, 255), 1)

        preview_path = PREVIEW_DIR / (
            f"page-{int(row['pageNumber']):02d}-row-{int(row['rowIndex']):02d}-"
            f"measures-{'-'.join(str(value) for value in measures)}.png"
        )
        cv2.imwrite(str(preview_path), image)

        total_string_local += len(string_local)
        total_compact += len(compact)
        total_columns += len(columns)
        measures_seen.extend(measures)
        rows_output.append(
            {
                "pageNumber": int(row["pageNumber"]),
                "rowIndex": int(row["rowIndex"]),
                "measures": measures,
                "sourceCrop": row["sourceCrop"],
                "stringSpacingPixels": round(spacing, 2),
                "inputCandidateCount": len(candidates),
                "stringLocalCandidateCount": len(string_local),
                "compactGlyphHypothesisCount": len(compact),
                "xAlignedHypothesisColumns": columns,
                "hypothesisColumnCount": len(columns),
                "preview": str(preview_path.relative_to(ROOT)),
                "semanticNoteEventsExtracted": False,
            }
        )
        print(
            f"Page {row['pageNumber']} row {row['rowIndex']}: "
            f"measures {measures[0]}-{measures[-1]}, "
            f"input={len(candidates)}, local={len(string_local)}, "
            f"compact={len(compact)}, columns={len(columns)}",
            flush=True,
        )

    unique_measures = sorted(set(measures_seen))
    expected = list(range(TARGET_MEASURE_START, TARGET_MEASURE_END + 1))
    complete = unique_measures == expected
    locked_touched = any(measure <= LOCKED_MEASURE_END for measure in measures_seen)

    reduction_ratio = round(total_compact / total_input, 6) if total_input else 0.0
    output = {
        "diagnosticName": "Gomyway professional rhythm glyph hypothesis filtering v14",
        "referenceType": "professional-rhythm-tab-unrecognized-glyph-hypotheses",
        "targetMeasureStart": TARGET_MEASURE_START,
        "targetMeasureEnd": TARGET_MEASURE_END,
        "uniqueTargetMeasuresCovered": len(unique_measures),
        "complete17To113MeasureCoveragePassed": complete,
        "lockedMeasures1To16Touched": locked_touched,
        "inputGeometricCandidateCount": total_input,
        "stringLocalCandidateCount": total_string_local,
        "compactGlyphHypothesisCount": total_compact,
        "xAlignedHypothesisColumnCount": total_columns,
        "compactToInputReductionRatio": reduction_ratio,
        "stringLocalGeometryClassCounts": dict(sorted(geometry_counts.items())),
        "rows": rows_output,
        "candidateAudioUsed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "semanticNoteEventsExtracted": False,
        "glyphValuesRecognized": False,
        "manualVerificationRequiredBeforeScoring": True,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "build-locked-glyph-template-library-from-measures-1-16",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm glyph hypothesis filtering v14 complete")
    print(f"Input geometric candidates: {total_input}")
    print(f"String-local candidates: {total_string_local}")
    print(f"Compact glyph hypotheses: {total_compact}")
    print(f"X-aligned hypothesis columns: {total_columns}")
    print(f"Compact/input reduction ratio: {reduction_ratio}")
    print(f"Unique measures 17-113 covered: {len(unique_measures)}")
    print(f"Complete 17-113 coverage passed: {complete}")
    print(f"Locked measures 1-16 touched: {locked_touched}")
    print("Glyph values recognized: False")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V14 did not preserve complete target measure coverage")
    if locked_touched:
        raise RuntimeError("V14 touched protected measures 1-16")
    if total_compact <= 0 or total_columns <= 0:
        raise RuntimeError("V14 produced no usable glyph hypotheses")


if __name__ == "__main__":
    main()
