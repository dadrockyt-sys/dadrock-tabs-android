import json
import re
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
INTRO_PATH = PUBLIC / "gomyway-professional-rhythm-reference-v2.json"
STRUCTURE_PATH = PUBLIC / "gomyway-professional-rhythm-reference.json"
OUTPUT_PATH = PUBLIC / "gomyway-professional-rhythm-reference-full-machine.json"
REPORT_PATH = PUBLIC / "gomyway-professional-rhythm-reference-full-machine-report.json"

EXPECTED_MEASURES = 113
STANDARD_TUNING = [64, 59, 55, 50, 45, 40]  # high E to low E
FRET_RE = re.compile(r"^\(?([0-9]{1,2})\)?$")
RHYTHM_LABEL_RE = re.compile(r"rhythm|gtr\.?\s*1|guitar\s*1|electric guitar", re.I)
EXCLUDED_LABEL_RE = re.compile(r"lead|solo|bass|vocal|melody|gtr\.?\s*2|guitar\s*2", re.I)


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def import_fitz():
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required. Run: pip install pymupdf") from exc
    return fitz


def cluster(values: list[float], tolerance: float) -> list[float]:
    if not values:
        return []
    values = sorted(values)
    groups: list[list[float]] = [[values[0]]]
    for value in values[1:]:
        if abs(value - median(groups[-1])) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [float(median(group)) for group in groups]


def page_words(page: Any) -> list[dict[str, Any]]:
    result = []
    for item in page.get_text("words"):
        x0, y0, x1, y1, text = item[:5]
        result.append({
            "x0": float(x0), "y0": float(y0), "x1": float(x1), "y1": float(y1),
            "cx": float((x0 + x1) / 2), "cy": float((y0 + y1) / 2),
            "text": str(text).strip(),
        })
    return result


def drawing_lines(page: Any) -> tuple[list[tuple[float, float, float]], list[tuple[float, float, float]]]:
    horizontal: list[tuple[float, float, float]] = []
    vertical: list[tuple[float, float, float]] = []
    for drawing in page.get_drawings():
        for item in drawing.get("items", []):
            if not item or item[0] != "l":
                continue
            p1, p2 = item[1], item[2]
            x1, y1 = float(p1.x), float(p1.y)
            x2, y2 = float(p2.x), float(p2.y)
            if abs(y1 - y2) <= 1.2 and abs(x2 - x1) >= 60:
                horizontal.append((min(x1, x2), max(x1, x2), (y1 + y2) / 2))
            if abs(x1 - x2) <= 1.2 and abs(y2 - y1) >= 18:
                vertical.append(((x1 + x2) / 2, min(y1, y2), max(y1, y2)))
    return horizontal, vertical


def detect_tab_staves(page: Any, words: list[dict[str, Any]]) -> list[dict[str, Any]]:
    horizontal, _ = drawing_lines(page)
    ys = cluster([line[2] for line in horizontal], 1.5)
    staves = []
    i = 0
    while i <= len(ys) - 6:
        group = ys[i:i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if 4 <= spacing <= 18 and max(abs(gap - spacing) for gap in gaps) <= 2.5:
            matching = [line for line in horizontal if min(abs(line[2] - y) for y in group) <= 1.8]
            x_left = median([line[0] for line in matching])
            x_right = median([line[1] for line in matching])
            label_words = [w["text"] for w in words if w["x1"] <= x_left + 12 and group[0] - 35 <= w["cy"] <= group[-1] + 15]
            label = " ".join(label_words)
            excluded = bool(EXCLUDED_LABEL_RE.search(label))
            explicit_rhythm = bool(RHYTHM_LABEL_RE.search(label))
            staves.append({
                "stringYs": group,
                "top": group[0],
                "bottom": group[-1],
                "spacing": spacing,
                "xLeft": float(x_left),
                "xRight": float(x_right),
                "label": label,
                "explicitRhythm": explicit_rhythm,
                "excluded": excluded,
            })
            i += 6
        else:
            i += 1

    usable = [s for s in staves if not s["excluded"]]
    explicit = [s for s in usable if s["explicitRhythm"]]
    return explicit if explicit else usable[:1]  # only the first non-excluded guitar staff


def measure_boxes(page: Any, stave: dict[str, Any]) -> tuple[list[tuple[float, float]], bool]:
    _, vertical = drawing_lines(page)
    top = stave["top"] - stave["spacing"] * 1.5
    bottom = stave["bottom"] + stave["spacing"] * 1.5
    xs = [x for x, y1, y2 in vertical if y1 <= top + 5 and y2 >= bottom - 5]
    xs.extend([stave["xLeft"], stave["xRight"]])
    xs = [x for x in cluster(xs, 2.0) if stave["xLeft"] - 4 <= x <= stave["xRight"] + 4]
    xs.sort()
    boxes = [(xs[i], xs[i + 1]) for i in range(len(xs) - 1) if xs[i + 1] - xs[i] >= 22]
    detected = len(boxes) >= 2
    if not detected:
        width = stave["xRight"] - stave["xLeft"]
        estimated = max(2, round(width / 125))
        step = width / estimated
        boxes = [(stave["xLeft"] + i * step, stave["xLeft"] + (i + 1) * step) for i in range(estimated)]
    return boxes, detected


def nearest_string(cy: float, ys: list[float], spacing: float) -> tuple[int | None, float]:
    distances = [abs(cy - y) for y in ys]
    index = min(range(6), key=distances.__getitem__)
    if distances[index] > max(4.0, spacing * 0.62):
        return None, distances[index]
    return index, distances[index]


def extract_events(words: list[dict[str, Any]], stave: dict[str, Any], x0: float, x1: float, page_number: int, box_index: int, detected_barlines: bool) -> list[dict[str, Any]]:
    events = []
    width = max(1.0, x1 - x0)
    relevant = [w for w in words if x0 <= w["cx"] < x1 and stave["top"] - 6 <= w["cy"] <= stave["bottom"] + 6]
    for word in relevant:
        match = FRET_RE.match(word["text"])
        muted = word["text"] in {"x", "X"}
        if not match and not muted:
            continue
        string_index, distance = nearest_string(word["cy"], stave["stringYs"], stave["spacing"])
        if string_index is None:
            continue
        fret = int(match.group(1)) if match else 0
        if fret > 24:
            continue
        position = round(round(max(0.0, min(0.999, (word["cx"] - x0) / width)) * 16) / 16, 4)
        confidence = round(
            0.55 * max(0.0, 1.0 - distance / max(1.0, stave["spacing"] * 0.65))
            + 0.25 * (1.0 if detected_barlines else 0.7)
            + 0.20 * (1.0 if 2 <= word["x1"] - word["x0"] <= 18 else 0.7),
            4,
        )
        events.append({
            "stringIndex": string_index,
            "fret": fret,
            "midiPitch": STANDARD_TUNING[string_index] + fret,
            "positionInMeasure": position,
            "durationSteps": 1,
            "technique": "muted-note" if muted else None,
            "machineConfidence": confidence,
            "professionalPdfEvidence": {
                "pageNumber": page_number,
                "staffLabel": stave["label"],
                "measureBoxIndex": box_index,
                "token": word["text"],
                "tokenBox": [word["x0"], word["y0"], word["x1"], word["y1"]],
                "measureBox": [x0, stave["top"], x1, stave["bottom"]],
            },
        })
    events.sort(key=lambda e: (e["positionInMeasure"], e["stringIndex"]))
    for index, event in enumerate(events):
        next_position = events[index + 1]["positionInMeasure"] if index + 1 < len(events) else 1.0
        event["durationSteps"] = max(1, min(16, round(max(1 / 16, next_position - event["positionInMeasure"]) * 16)))
    return events


def main() -> None:
    fitz = import_fitz()
    intro = load_json(INTRO_PATH)
    structure = load_json(STRUCTURE_PATH)
    verified_intro = intro.get("measures", []) if isinstance(intro, dict) else []
    if len(verified_intro) != 16:
        raise RuntimeError("Verified rhythm intro reference must contain exactly 16 measures")

    doc = fitz.open(PDF_PATH)
    machine_measures: list[dict[str, Any]] = []
    diagnostics = []
    measure_number = 1
    for page_index in range(len(doc)):
        page = doc[page_index]
        words = page_words(page)
        staves = detect_tab_staves(page, words)
        page_count = 0
        for stave in staves:
            boxes, detected = measure_boxes(page, stave)
            for box_index, (x0, x1) in enumerate(boxes):
                if measure_number > EXPECTED_MEASURES:
                    break
                events = extract_events(words, stave, x0, x1, page_index + 1, box_index, detected)
                machine_measures.append({
                    "measureNumber": measure_number,
                    "events": events,
                    "instrumentPart": "rhythm-guitar",
                    "machineExtracted": True,
                    "humanConfirmed": False,
                    "professionalPdfPage": page_index + 1,
                    "machineConfidence": round(sum(e["machineConfidence"] for e in events) / len(events), 4) if events else 0.0,
                    "eventCount": len(events),
                })
                measure_number += 1
                page_count += 1
        diagnostics.append({"pageNumber": page_index + 1, "rhythmStaffCount": len(staves), "measureCount": page_count})

    extracted_count = len(machine_measures)
    merged = []
    for number in range(1, EXPECTED_MEASURES + 1):
        if number <= 16:
            row = dict(verified_intro[number - 1])
            row["measureNumber"] = number
            row["instrumentPart"] = "rhythm-guitar"
            row["machineExtracted"] = False
            row["humanConfirmed"] = True
            row["referenceAuthority"] = "verified-professional-reference"
            merged.append(row)
        elif number <= extracted_count:
            row = dict(machine_measures[number - 1])
            row["referenceAuthority"] = "professional-pdf-machine-extraction"
            merged.append(row)
        else:
            merged.append({
                "measureNumber": number,
                "events": [],
                "instrumentPart": "rhythm-guitar",
                "machineExtracted": False,
                "humanConfirmed": False,
                "machineConfidence": 0.0,
                "eventCount": 0,
                "referenceAuthority": "missing",
            })

    nonempty_remaining = sum(1 for row in merged[16:] if row.get("eventCount", len(row.get("events", []))) > 0)
    full_measure_coverage = extracted_count >= EXPECTED_MEASURES
    machine_reference_ready = full_measure_coverage and nonempty_remaining > 0

    output = {
        "song": "Are You Gonna Go My Way",
        "artist": "Lenny Kravitz",
        "instrumentPart": "rhythm-guitar",
        "transcriptionType": "rhythm",
        "measureCount": EXPECTED_MEASURES,
        "verifiedMeasureCount": 16,
        "machineExtractedMeasureCount": max(0, min(EXPECTED_MEASURES, extracted_count) - 16),
        "professionalPdf": str(PDF_PATH.relative_to(ROOT)),
        "professionalPdfRemainsScoringAuthority": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "measures": merged,
        "machineReferenceReady": machine_reference_ready,
        "productionPromotionAllowed": False,
    }
    report = {
        "instrumentPart": "rhythm-guitar-only",
        "pdfPageCount": len(doc),
        "detectedMeasureCount": extracted_count,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "fullMeasureCoveragePassed": full_measure_coverage,
        "remainingMeasuresWithDetectedEvents": nonempty_remaining,
        "verifiedIntroPreserved": True,
        "professionalPdfRemainsScoringAuthority": True,
        "machineReferenceReady": machine_reference_ready,
        "diagnostics": diagnostics,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "productionPromotionAllowed": False,
    }
    write_json(OUTPUT_PATH, output)
    write_json(REPORT_PATH, report)

    print("Rhythm-guitar-only machine professional reference complete")
    print(f"Detected PDF measures: {extracted_count}/113")
    print("Verified rhythm measures preserved: 16/113")
    print(f"Remaining measures with detected events: {nonempty_remaining}/97")
    print(f"Full measure coverage passed: {full_measure_coverage}")
    print(f"Machine reference ready: {machine_reference_ready}")
    print("Lead guitar included: False")
    print("Bass included: False")
    print("Vocals included: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Report: {REPORT_PATH.relative_to(ROOT)}")

    if not machine_reference_ready:
        raise RuntimeError("Rhythm-guitar machine reference did not reach complete usable coverage")


if __name__ == "__main__":
    main()
