import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V39 = PUBLIC / "gomyway-locked-fret-digit-raw-relocalization-v39.json"
OUTPUT = PUBLIC / "gomyway-raw-digit-line-suppression-calibration-v40.json"
PREVIEW_DIR = PUBLIC / "gomyway-raw-digit-line-suppression-calibration-v40"

CONFIGS = [
    {"name": "no-line-removal", "lineScale": 0.0, "closeWidth": 2},
    {"name": "long-lines-6x", "lineScale": 6.0, "closeWidth": 2},
    {"name": "long-lines-8x", "lineScale": 8.0, "closeWidth": 2},
    {"name": "long-lines-10x", "lineScale": 10.0, "closeWidth": 3},
]


def slots(data):
    output = []
    for row in data.get("rows", []):
        for measure in row.get("measureEventSlots", []):
            for slot in measure.get("eventSlots", []):
                item = dict(slot)
                item["pageNumber"] = int(row["pageNumber"])
                item["rowIndex"] = int(row["rowIndex"])
                item["measure"] = int(item.get("measure", measure.get("measure", 0)))
                output.append(item)
    return output


def six_rows(binary):
    counts = binary[:, round(binary.shape[1] * 0.05):round(binary.shape[1] * 0.98)].sum(axis=1) / 255
    raw = [i for i, value in enumerate(counts) if value >= max(20, binary.shape[1] * 0.35)]
    groups = []
    for value in raw:
        if groups and value - groups[-1][-1] <= 3:
            groups[-1].append(value)
        else:
            groups.append([value])
    rows = [round(median(group)) for group in groups]
    best = []
    best_score = -1e30
    for index in range(max(0, len(rows) - 5)):
        group = rows[index:index + 6]
        if len(group) != 6:
            continue
        gaps = [group[i + 1] - group[i] for i in range(5)]
        spacing = median(gaps)
        if not 5 <= spacing <= 30:
            continue
        irregularity = max(abs(gap - spacing) for gap in gaps)
        if irregularity > max(3, spacing * 0.3):
            continue
        score = sum(counts[y] for y in group) - irregularity * binary.shape[1]
        if score > best_score:
            best_score = score
            best = group
    return best


def candidate_count(cv2, patch, spacing, expected_local_x, local_y, config):
    blur = cv2.GaussianBlur(patch, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 7,
    )

    processed = binary.copy()
    if config["lineScale"] > 0:
        kernel_width = max(9, round(spacing * config["lineScale"]))
        horizontal = cv2.morphologyEx(
            binary,
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1)),
        )
        processed = cv2.subtract(binary, horizontal)

    processed = cv2.morphologyEx(
        processed,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (config["closeWidth"], 2)),
    )

    count, _, stats, centroids = cv2.connectedComponentsWithStats(processed, 8)
    candidates = []
    for label in range(1, count):
        x, y, width, height, area = [int(value) for value in stats[label]]
        if area < 4:
            continue
        if width > spacing * 2.2 or height > spacing * 2.4:
            continue
        cx, cy = centroids[label]
        aspect = width / max(1, height)
        x_distance = abs(cx - expected_local_x)
        y_distance = abs(cy - local_y)
        if not 0.12 <= aspect <= 2.2:
            continue
        if height < max(3, spacing * 0.22):
            continue
        if x_distance > spacing * 2.6 or y_distance > spacing * 1.15:
            continue
        candidates.append({
            "score": round(float(x_distance + y_distance * 0.5), 3),
            "x": x, "y": y, "width": width, "height": height,
            "area": area, "centerX": round(float(cx), 2),
            "centerY": round(float(cy), 2),
        })
    candidates.sort(key=lambda item: item["score"])
    return processed, candidates


def main():
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    for path in (ASSIGNMENT, LOCALIZATION, V39):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT.read_text())
    localization = json.loads(LOCALIZATION.read_text())
    v39 = json.loads(V39.read_text())
    if int(v39.get("plausibleDigitCandidateTotal", -1)) != 0:
        raise RuntimeError("V39 no longer reports zero candidates")
    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 contains component collisions")

    row_lookup = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }
    locked = [
        slot for slot in slots(assignment)
        if 1 <= slot["measure"] <= 16 and str(int(slot["fret"])) in {"0", "2", "3"}
    ]
    if len(locked) != 144:
        raise RuntimeError(f"Expected 144 locked slots, found {len(locked)}")

    image_cache = {}
    row_cache = {}
    results = {config["name"]: Counter() for config in CONFIGS}
    examples = defaultdict(list)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    print("Raw fret digit line suppression calibration v40 starting", flush=True)

    for slot_index, slot in enumerate(locked):
        key = (int(slot["pageNumber"]), int(slot["rowIndex"]))
        row = row_lookup[key]
        if key not in image_cache:
            gray = cv2.imread(str(ROOT / row["sourceCrop"]), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise RuntimeError(f"Unable to read {row['sourceCrop']}")
            image_cache[key] = gray
            page_binary = cv2.adaptiveThreshold(
                cv2.GaussianBlur(gray, (3, 3), 0), 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 31, 8,
            )
            row_cache[key] = six_rows(page_binary)

        gray = image_cache[key]
        string_rows = row_cache[key]
        string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
        expected_x = float(slot.get("expectedX") or 0)
        fret_value = str(int(slot["fret"]))
        if len(string_rows) != 6 or not 1 <= string_number <= 6:
            continue

        spacing = float(median([string_rows[i + 1] - string_rows[i] for i in range(5)]))
        y_center = string_rows[string_number - 1]
        x0 = max(0, round(expected_x - spacing * 3.0))
        x1 = min(gray.shape[1], round(expected_x + spacing * 3.0))
        y0 = max(0, round(y_center - spacing * 1.35))
        y1 = min(gray.shape[0], round(y_center + spacing * 1.35))
        patch = gray[y0:y1, x0:x1]
        expected_local_x = expected_x - x0
        local_y = y_center - y0

        panels = []
        for config in CONFIGS:
            processed, candidates = candidate_count(
                cv2, patch, spacing, expected_local_x, local_y, config
            )
            if candidates:
                results[config["name"]][fret_value] += 1
                if len(examples[config["name"]]) < 12:
                    examples[config["name"]].append({
                        "measure": int(slot["measure"]),
                        "stringHighEToLowE": string_number,
                        "fret": int(fret_value),
                        "candidate": candidates[0],
                    })
            if slot_index < 12:
                panel = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
                cv2.line(panel, (round(expected_local_x), 0), (round(expected_local_x), panel.shape[0] - 1), (0, 0, 255), 1)
                cv2.line(panel, (0, round(local_y)), (panel.shape[1] - 1, round(local_y)), (255, 0, 0), 1)
                for candidate in candidates[:3]:
                    cv2.rectangle(
                        panel,
                        (candidate["x"], candidate["y"]),
                        (candidate["x"] + candidate["width"], candidate["y"] + candidate["height"]),
                        (0, 255, 0), 1,
                    )
                panels.append(panel)
        if slot_index < 12 and panels:
            joined = np.hstack(panels)
            cv2.imwrite(str(PREVIEW_DIR / f"slot-{slot_index + 1:03d}-m{int(slot['measure']):03d}-f{fret_value}.png"), joined)

    summaries = {}
    best_name = None
    best_total = -1
    for config in CONFIGS:
        name = config["name"]
        by_fret = {fret: int(results[name][fret]) for fret in ("0", "2", "3")}
        total = sum(by_fret.values())
        ratio = total / len(locked)
        summaries[name] = {
            "candidatesByFret": by_fret,
            "candidateTotal": total,
            "candidateRatio": round(ratio, 6),
            "examples": examples[name],
        }
        if total > best_total:
            best_total = total
            best_name = name
        print(f"{name}: total={total}, ratio={ratio:.6f}, byFret={by_fret}")

    best_ratio = best_total / len(locked)
    calibration_passed = best_ratio >= 0.55 and all(
        summaries[best_name]["candidatesByFret"][fret] >= 8
        for fret in ("0", "2", "3")
    )

    output = {
        "diagnosticName": "Gomyway raw fret digit line suppression calibration v40",
        "lockedEventSlotsObserved": len(locked),
        "configurations": summaries,
        "bestConfiguration": best_name,
        "bestCandidateTotal": best_total,
        "bestCandidateRatio": round(best_ratio, 6),
        "calibrationPassed": calibration_passed,
        "previewCount": min(12, len(locked)),
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-v40-calibration-previews"
            if calibration_passed
            else "inspect-raw-row-coordinate-model-v41"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")

    print("Raw fret digit line suppression calibration v40 complete")
    print(f"Locked event slots observed: {len(locked)}")
    print(f"Best configuration: {best_name}")
    print(f"Best candidate total: {best_total}")
    print(f"Best candidate ratio: {best_ratio:.6f}")
    print(f"Calibration passed: {calibration_passed}")
    print("Human visual validation complete: False")
    print("Glyph templates human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
