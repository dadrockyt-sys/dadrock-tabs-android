import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONSENSUS_PATH = PUBLIC / "gomyway-locked-event-consensus-v20.json"
CANONICAL_SOURCE = PUBLIC / "gomyway-professional-rhythm-reference-full-machine.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-localization-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
PREVIEW_DIR = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21"

LOCKED_START = 1
LOCKED_END = 16

STRING_KEYS = ("stringIndex", "string_index", "string", "stringNumber", "string_number")
FRET_KEYS = ("fret", "fretNumber", "fret_number")
MEASURE_KEYS = ("measure", "measureNumber", "measure_number", "measureIndex")
TIME_KEYS = ("beat", "beatPosition", "beat_position", "offset", "start", "startTime", "start_time", "time")
TECHNIQUE_KEYS = ("technique", "articulation", "bend", "slide", "hammerOn", "pullOff", "palmMute", "muted")


def first_value(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data:
            return data[key]
    return None


def walk(value: Any, measure_context: int | None = None) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    if isinstance(value, dict):
        own_measure = first_value(value, MEASURE_KEYS)
        if isinstance(own_measure, (int, float)):
            measure_context = int(own_measure)
        string_value = first_value(value, STRING_KEYS)
        fret_value = first_value(value, FRET_KEYS)
        if string_value is not None and fret_value is not None and measure_context is not None:
            if LOCKED_START <= measure_context <= LOCKED_END:
                output.append({
                    "measure": measure_context,
                    "string": string_value,
                    "fret": fret_value,
                    "time": first_value(value, TIME_KEYS),
                    "technique": {key: value[key] for key in TECHNIQUE_KEYS if key in value},
                })
        for child in value.values():
            output.extend(walk(child, measure_context))
    elif isinstance(value, list):
        for child in value:
            output.extend(walk(child, measure_context))
    return output


def cluster(values: list[int], tolerance: int) -> list[int]:
    if not values:
        return []
    groups: list[list[int]] = [[values[0]]]
    for value in sorted(values)[1:]:
        if abs(value - round(median(groups[-1]))) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def choose_six_string_rows(binary: Any) -> list[int]:
    height, width = binary.shape
    x0, x1 = round(width * 0.06), round(width * 0.98)
    counts = binary[:, x0:x1].sum(axis=1)
    threshold = max(20, round((x1 - x0) * 0.42))
    rows = cluster([int(i) for i, value in enumerate(counts) if value >= threshold], 3)
    best: list[int] = []
    best_score = float("-inf")
    for index in range(max(0, len(rows) - 5)):
        group = rows[index:index + 6]
        if len(group) != 6:
            continue
        gaps = [group[i + 1] - group[i] for i in range(5)]
        spacing = float(median(gaps))
        if not 5 <= spacing <= 30:
            continue
        irregularity = max(abs(gap - spacing) for gap in gaps)
        if irregularity > max(3.0, spacing * 0.28):
            continue
        score = sum(int(counts[y]) for y in group) - irregularity * width
        if score > best_score:
            best_score = score
            best = group
    return best


def numeric_time(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def normalize_string(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        number = int(value)
        if 0 <= number <= 5:
            return number + 1
        if 1 <= number <= 6:
            return number
    if isinstance(value, str):
        digits = "".join(ch for ch in value if ch.isdigit())
        if digits:
            number = int(digits)
            if 0 <= number <= 5:
                return number + 1
            if 1 <= number <= 6:
                return number
    return None


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    for path in (CONSENSUS_PATH, CANONICAL_SOURCE, LOCALIZATION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    consensus = json.loads(CONSENSUS_PATH.read_text(encoding="utf-8"))
    if not consensus.get("consensusPassed", False):
        raise RuntimeError("V20 locked event consensus has not passed")

    canonical = json.loads(CANONICAL_SOURCE.read_text(encoding="utf-8"))
    events = walk(canonical)
    if len(events) != 144:
        raise RuntimeError(f"Expected 144 locked events, found {len(events)}")

    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    row_lookup: dict[int, dict[str, Any]] = {}
    for page in localization["pages"]:
        for row in page["rows"]:
            for measure in row["measures"]:
                measure_number = int(measure)
                if LOCKED_START <= measure_number <= LOCKED_END:
                    row_lookup[measure_number] = {
                        "pageNumber": int(page["pageNumber"]),
                        "rowIndex": int(row["rowIndex"]),
                        "measures": [int(value) for value in row["measures"]],
                        "crop": row["crop"],
                    }

    if sorted(row_lookup) != list(range(1, 17)):
        raise RuntimeError("V10 does not provide complete locked measure crop coverage")

    events_by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        events_by_measure[int(event["measure"])].append(event)

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rows_output = []
    total_components = 0
    total_event_slots = 0
    rows_with_six_strings = 0
    unique_rows: dict[tuple[int, int], dict[str, Any]] = {}
    for measure, row in row_lookup.items():
        unique_rows[(row["pageNumber"], row["rowIndex"])] = row

    print("Locked professional event PDF glyph localization v21 starting", flush=True)

    for (page_number, row_index), row in sorted(unique_rows.items()):
        crop_path = ROOT / row["crop"]
        image = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

        blur = cv2.GaussianBlur(image, (3, 3), 0)
        binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 9)
        string_rows = choose_six_string_rows(binary)
        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        components: list[dict[str, Any]] = []

        if len(string_rows) == 6:
            rows_with_six_strings += 1
            spacing = float(median([string_rows[i + 1] - string_rows[i] for i in range(5)]))
            line_mask = np.zeros_like(binary)
            thickness = max(1, round(spacing * 0.18))
            for y in string_rows:
                line_mask[max(0, y - thickness):min(binary.shape[0], y + thickness + 1), :] = binary[max(0, y - thickness):min(binary.shape[0], y + thickness + 1), :]
                cv2.line(annotated, (0, y), (image.shape[1] - 1, y), (255, 0, 0), 1)
            symbols = cv2.subtract(binary, line_mask)
            symbols = cv2.morphologyEx(symbols, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
            count, _, stats, centroids = cv2.connectedComponentsWithStats(symbols, 8)
            min_area = max(5, round(spacing * spacing * 0.05))
            max_area = round(image.shape[0] * image.shape[1] * 0.01)
            for label in range(1, count):
                x, y, width, height, area = [int(value) for value in stats[label]]
                if not min_area <= area <= max_area:
                    continue
                cx, cy = [float(value) for value in centroids[label]]
                nearest = min(range(6), key=lambda idx: abs(cy - string_rows[idx]))
                distance = abs(cy - string_rows[nearest])
                if distance > spacing * 0.78:
                    continue
                if width > spacing * 1.8 or height > spacing * 1.9:
                    continue
                components.append({
                    "componentIndex": len(components) + 1,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "area": area,
                    "centerX": round(cx, 2),
                    "centerY": round(cy, 2),
                    "stringHighEToLowE": nearest + 1,
                })
                cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 0, 255), 1)

        measure_slots = []
        row_measures = [m for m in row["measures"] if LOCKED_START <= m <= LOCKED_END]
        width = image.shape[1]
        measure_count = len(row_measures)
        for local_index, measure in enumerate(row_measures):
            x0 = round(width * local_index / measure_count)
            x1 = round(width * (local_index + 1) / measure_count)
            measure_events = events_by_measure[measure]
            time_values = [numeric_time(event.get("time")) for event in measure_events]
            numeric_values = [value for value in time_values if value is not None]
            distinct_times = sorted(set(numeric_values))
            fallback_order = {id(event): index for index, event in enumerate(measure_events)}

            slots = []
            for event in measure_events:
                event_time = numeric_time(event.get("time"))
                if event_time is not None and distinct_times:
                    time_index = distinct_times.index(event_time)
                    fraction = (time_index + 0.5) / max(1, len(distinct_times))
                else:
                    fraction = (fallback_order[id(event)] + 0.5) / max(1, len(measure_events))
                expected_x = x0 + fraction * (x1 - x0)
                string_number = normalize_string(event.get("string"))
                matching = [component for component in components if component["stringHighEToLowE"] == string_number]
                nearest = min(matching, key=lambda component: abs(component["centerX"] - expected_x)) if matching else None
                distance = abs(nearest["centerX"] - expected_x) if nearest else None
                slots.append({
                    "measure": measure,
                    "string": event.get("string"),
                    "normalizedStringHighEToLowE": string_number,
                    "fret": event.get("fret"),
                    "time": event.get("time"),
                    "technique": event.get("technique") or {},
                    "expectedX": round(expected_x, 2),
                    "nearestComponentIndex": nearest["componentIndex"] if nearest else None,
                    "distancePixels": round(distance, 2) if distance is not None else None,
                    "localizedHypothesisOnly": True,
                    "requiresVisualAndTemplateVerification": True,
                })
                total_event_slots += 1
                if nearest and string_number and len(string_rows) == 6:
                    cv2.circle(annotated, (round(nearest["centerX"]), string_rows[string_number - 1]), 4, (0, 255, 0), 1)
            measure_slots.append({"measure": measure, "xRangePixels": [x0, x1], "eventSlots": slots})

        preview_path = PREVIEW_DIR / f"page-{page_number:02d}-row-{row_index:02d}-locked.png"
        cv2.imwrite(str(preview_path), annotated)
        total_components += len(components)
        rows_output.append({
            "pageNumber": page_number,
            "rowIndex": row_index,
            "measures": row_measures,
            "sourceCrop": row["crop"],
            "sixStringRowsDetected": len(string_rows) == 6,
            "stringRowsPixelsHighEToLowE": string_rows,
            "compactStringLocalComponents": components,
            "measureEventSlots": measure_slots,
            "preview": str(preview_path.relative_to(ROOT)),
            "localizationVerified": False,
        })
        print(
            f"Page {page_number} row {row_index}: measures {row_measures[0]}-{row_measures[-1]}, "
            f"sixStrings={len(string_rows) == 6}, components={len(components)}, "
            f"eventSlots={sum(len(item['eventSlots']) for item in measure_slots)}",
            flush=True,
        )

    all_rows_detected = rows_with_six_strings == len(unique_rows)
    all_events_scaffolded = total_event_slots == 144
    output = {
        "diagnosticName": "Gomyway locked event PDF glyph localization v21",
        "referenceType": "locked-professional-event-to-pdf-glyph-localization-hypotheses",
        "canonicalSource": str(CANONICAL_SOURCE.relative_to(ROOT)),
        "lockedEventConsensus": str(CONSENSUS_PATH.relative_to(ROOT)),
        "lockedEventCount": len(events),
        "lockedRowsProcessed": len(unique_rows),
        "rowsWithSixStringsDetected": rows_with_six_strings,
        "allLockedRowsHaveSixStrings": all_rows_detected,
        "compactStringLocalComponents": total_components,
        "eventLocalizationSlots": total_event_slots,
        "all144EventsScaffolded": all_events_scaffolded,
        "rows": rows_output,
        "localizationHypothesesVerified": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "validate-locked-event-glyph-localization-and-build-template-library-v22",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked professional event PDF glyph localization v21 complete")
    print(f"Locked rows processed: {len(unique_rows)}")
    print(f"Rows with six strings detected: {rows_with_six_strings}")
    print(f"Compact string-local components: {total_components}")
    print(f"Event localization slots: {total_event_slots}")
    print(f"All 144 events scaffolded: {all_events_scaffolded}")
    print("Localization hypotheses verified: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")

    if not all_rows_detected:
        raise RuntimeError("V21 did not detect six strings in every locked row")
    if not all_events_scaffolded:
        raise RuntimeError("V21 did not scaffold all 144 locked events")


if __name__ == "__main__":
    main()
