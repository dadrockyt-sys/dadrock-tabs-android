import json
from collections import Counter
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
AUDIT = PUBLIC / "gomyway-locked-template-source-box-audit-v38.json"
OUTPUT = PUBLIC / "gomyway-locked-fret-digit-raw-relocalization-v39.json"


def slots(data):
    out = []
    for row in data.get("rows", []):
        for measure in row.get("measureEventSlots", []):
            for slot in measure.get("eventSlots", []):
                item = dict(slot)
                item["pageNumber"] = int(row["pageNumber"])
                item["rowIndex"] = int(row["rowIndex"])
                item["measure"] = int(item.get("measure", measure.get("measure", 0)))
                out.append(item)
    return out


def fret(slot):
    return str(int(slot["fret"]))


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


def main():
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (ASSIGNMENT, LOCALIZATION, AUDIT):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT.read_text())
    localization = json.loads(LOCALIZATION.read_text())
    audit = json.loads(AUDIT.read_text())
    if audit.get("humanVisualValidationComplete", False):
        raise RuntimeError("V38 unexpectedly claims visual approval")
    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 contains component collisions")

    row_lookup = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }
    locked = [slot for slot in slots(assignment) if 1 <= slot["measure"] <= 16 and fret(slot) in {"0", "2", "3"}]
    if len(locked) != 144:
        raise RuntimeError(f"Expected 144 locked slots, found {len(locked)}")

    image_cache = {}
    rows_cache = {}
    found = Counter()
    missing = Counter()
    details = []

    print("Locked fret digit raw-pixel relocalization v39 starting", flush=True)

    for slot in locked:
        key = (slot["pageNumber"], slot["rowIndex"])
        row = row_lookup[key]
        if key not in image_cache:
            gray = cv2.imread(str(ROOT / row["sourceCrop"]), cv2.IMREAD_GRAYSCALE)
            if gray is None:
                raise RuntimeError(f"Unable to read {row['sourceCrop']}")
            image_cache[key] = gray
            binary = cv2.adaptiveThreshold(cv2.GaussianBlur(gray, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 8)
            rows_cache[key] = six_rows(binary)

        gray = image_cache[key]
        string_rows = rows_cache[key]
        string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
        expected_x = float(slot.get("expectedX") or 0)
        fret_value = fret(slot)
        selected = None

        if len(string_rows) == 6 and 1 <= string_number <= 6:
            spacing = float(median([string_rows[i + 1] - string_rows[i] for i in range(5)]))
            y_center = string_rows[string_number - 1]
            x0 = max(0, round(expected_x - spacing * 2.5))
            x1 = min(gray.shape[1], round(expected_x + spacing * 2.5))
            y0 = max(0, round(y_center - spacing * 1.1))
            y1 = min(gray.shape[0], round(y_center + spacing * 1.1))
            patch = gray[y0:y1, x0:x1]
            binary = cv2.adaptiveThreshold(cv2.GaussianBlur(patch, (3, 3), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 7)
            local_y = y_center - y0
            band = max(1, round(spacing * 0.12))
            binary[max(0, local_y - band):min(binary.shape[0], local_y + band + 1), :] = 0
            count, _, stats, centroids = cv2.connectedComponentsWithStats(binary, 8)
            candidates = []
            for label in range(1, count):
                x, y, width, height, area = [int(value) for value in stats[label]]
                if area < 4 or width > spacing * 1.6 or height > spacing * 1.8:
                    continue
                cx, cy = centroids[label]
                aspect = width / max(1, height)
                x_distance = abs((x0 + cx) - expected_x)
                y_distance = abs((y0 + cy) - y_center)
                if 0.18 <= aspect <= 1.4 and height >= max(3, spacing * 0.28) and y_distance <= spacing * 0.9:
                    candidates.append((x_distance + y_distance * 0.6, x0 + cx, y0 + cy, width, height, area))
            if candidates:
                selected = min(candidates)

        if selected is None:
            missing[fret_value] += 1
        else:
            found[fret_value] += 1

        details.append({
            "measure": slot["measure"],
            "stringHighEToLowE": string_number,
            "fret": int(fret_value),
            "expectedX": round(expected_x, 2),
            "candidateFound": selected is not None,
            "selectedCandidate": None if selected is None else {
                "score": round(selected[0], 3),
                "centerX": round(float(selected[1]), 2),
                "centerY": round(float(selected[2]), 2),
                "width": int(selected[3]),
                "height": int(selected[4]),
                "area": int(selected[5]),
            },
        })

    total_found = sum(found.values())
    ratio = total_found / len(locked)
    passed = ratio >= 0.70
    output = {
        "diagnosticName": "Gomyway locked fret digit raw-pixel relocalization v39",
        "lockedEventSlotsObserved": len(locked),
        "plausibleDigitCandidatesByFret": dict(found),
        "missingCandidatesByFret": dict(missing),
        "plausibleDigitCandidateTotal": total_found,
        "plausibleDigitCandidateRatio": round(ratio, 6),
        "rawRelocalizationScaffoldPassed": passed,
        "details": details,
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "build-v39-raw-digit-review-sample-v40" if passed else "calibrate-raw-digit-window-and-line-suppression-v40",
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n")

    print("Locked fret digit raw-pixel relocalization v39 complete")
    print(f"Locked event slots observed: {len(locked)}")
    print(f"Plausible digit candidates by fret: {dict(found)}")
    print(f"Missing candidates by fret: {dict(missing)}")
    print(f"Plausible digit candidate total: {total_found}")
    print(f"Plausible digit candidate ratio: {ratio:.6f}")
    print(f"Raw relocalization scaffold passed: {passed}")
    print("Human visual validation complete: False")
    print("Glyph templates human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
