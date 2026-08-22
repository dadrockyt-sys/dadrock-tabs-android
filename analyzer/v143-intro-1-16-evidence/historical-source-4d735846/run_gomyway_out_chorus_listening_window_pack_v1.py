from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

REVIEW_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-unresolved-review-pack-v1.json"
)
TIMING_MAP_CANDIDATES = (
    REPO_ROOT / "public" / "gomyway-professional-timing-map-v2.json",
    REPO_ROOT / "public" / "gomyway-professional-timing-map-v1.json",
)
FULL_MIX_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OTHER_STEM_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "gomyway-audio-separation-v1"
    / "htdemucs"
    / "gomywayfullaitest"
    / "other.wav"
)
OUTPUT_DIR = (
    REPO_ROOT
    / "public"
    / "training"
    / "gomyway-out-chorus-listening-window-pack-v1"
)
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

TARGETS = (
    (103, 2),
    (103, 3),
    (104, 9),
    (105, 15),
    (109, 15),
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing required file: {path.relative_to(REPO_ROOT)}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def find_timing_map() -> Path:
    for path in TIMING_MAP_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Missing professional timing map V2/V1 in public/."
    )


def measure_number(item: dict[str, Any]) -> int | None:
    value = item.get("measureNumber", item.get("measure"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_measure_bounds(
    payload: dict[str, Any],
) -> dict[int, tuple[float, float]]:
    candidate_lists: list[list[Any]] = []

    for key in (
        "measures",
        "measureBounds",
        "measureBoundaries",
        "measureReports",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            candidate_lists.append(value)

    bounds: dict[int, tuple[float, float]] = {}

    for rows in candidate_lists:
        for row in rows:
            if not isinstance(row, dict):
                continue

            number = measure_number(row)
            if number is None:
                continue

            start = row.get(
                "startSeconds",
                row.get("start", row.get("measureStartSeconds")),
            )
            end = row.get(
                "endSeconds",
                row.get("end", row.get("measureEndSeconds")),
            )

            if start is None and isinstance(row.get("timeRange"), list):
                time_range = row["timeRange"]
                if len(time_range) >= 2:
                    start, end = time_range[:2]

            try:
                start_value = float(start)
                end_value = float(end)
            except (TypeError, ValueError):
                continue

            if end_value > start_value:
                bounds[number] = (start_value, end_value)

    if bounds:
        return bounds

    # Fallback for timing maps that contain a flat event list.
    events = payload.get("notes") or payload.get("events") or []
    grouped: dict[int, list[tuple[float, float]]] = {}

    if isinstance(events, list):
        for event in events:
            if not isinstance(event, dict):
                continue
            number = measure_number(event)
            if number is None:
                continue
            try:
                start = float(event.get("start"))
                end = float(event.get("end", start))
            except (TypeError, ValueError):
                continue
            grouped.setdefault(number, []).append((start, end))

    for number, timings in grouped.items():
        starts = [item[0] for item in timings]
        ends = [item[1] for item in timings]
        bounds[number] = (min(starts), max(ends))

    if not bounds:
        raise ValueError(
            "Could not extract measure boundaries from the timing map."
        )

    return bounds


def target_time(
    measure: int,
    step: int,
    bounds: dict[int, tuple[float, float]],
) -> tuple[float, float, float]:
    if measure not in bounds:
        raise KeyError(f"Timing map has no measure {measure}.")

    start, end = bounds[measure]
    duration = end - start
    center = start + duration * (step / 16.0)
    return start, end, center


def run_ffmpeg(
    source: Path,
    output: Path,
    start: float,
    duration: float,
) -> None:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        f"{max(0.0, start):.6f}",
        "-i",
        str(source),
        "-t",
        f"{duration:.6f}",
        "-vn",
        "-ac",
        "2",
        "-ar",
        "44100",
        "-c:a",
        "pcm_s16le",
        str(output),
    ]
    subprocess.run(command, check=True)


def main() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but was not found in PATH.")

    review = load_json(REVIEW_PATH)
    timing_path = find_timing_map()
    timing = load_json(timing_path)
    bounds = extract_measure_bounds(timing)

    for audio_path in (FULL_MIX_PATH, OTHER_STEM_PATH):
        if not audio_path.exists():
            raise FileNotFoundError(
                f"Missing audio source: {audio_path.relative_to(REPO_ROOT)}"
            )

    unresolved = {
        (
            int(item["measureNumber"]),
            int(item["candidateStep"]),
        ): item
        for item in review.get("reviewItems") or []
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_items: list[dict[str, Any]] = []

    for measure, step in TARGETS:
        if (measure, step) not in unresolved:
            raise ValueError(
                f"Expected unresolved event missing from review pack: "
                f"measure {measure}, step {step}"
            )

        measure_start, measure_end, center = target_time(
            measure,
            step,
            bounds,
        )

        item_dir = OUTPUT_DIR / f"m{measure:03d}-s{step:02d}"
        item_dir.mkdir(parents=True, exist_ok=True)

        windows = {
            "tight": (center - 0.75, 1.50),
            "context": (center - 2.50, 5.00),
            "measure": (
                max(0.0, measure_start - 0.20),
                (measure_end - measure_start) + 0.40,
            ),
        }

        files: dict[str, dict[str, str]] = {}

        for window_name, (window_start, window_duration) in windows.items():
            files[window_name] = {}

            for source_name, source_path in (
                ("full-mix", FULL_MIX_PATH),
                ("other-stem", OTHER_STEM_PATH),
            ):
                output = item_dir / f"{source_name}-{window_name}.wav"
                run_ffmpeg(
                    source_path,
                    output,
                    window_start,
                    window_duration,
                )
                files[window_name][source_name] = str(
                    output.relative_to(REPO_ROOT)
                )

        source_item = unresolved[(measure, step)]
        manifest_items.append({
            "measureNumber": measure,
            "candidateStep": step,
            "measureStartSeconds": round(measure_start, 6),
            "measureEndSeconds": round(measure_end, 6),
            "targetSeconds": round(center, 6),
            "classification": source_item.get("classification"),
            "rankingScore": source_item.get("rankingScore"),
            "confidenceBand": source_item.get("confidenceBand"),
            "strongestComponents": source_item.get("strongestComponents"),
            "files": files,
            "reviewQuestions": [
                "Is the onset audible in both the full mix and the separated other stem?",
                "Does it sound like rhythm guitar rather than percussion or vocal leakage?",
                "Is it a new articulation or the continuation of a previous note/chord?",
                "Does it belong in the professional rhythm part at this sixteenth-note step?",
            ],
            "reviewDecision": None,
            "automaticDecisionAllowed": False,
        })

    manifest = {
        "schemaVersion": 1,
        "packType": "out-chorus-synchronized-listening-windows",
        "timingMap": str(timing_path.relative_to(REPO_ROOT)),
        "fullMix": str(FULL_MIX_PATH.relative_to(REPO_ROOT)),
        "otherStem": str(OTHER_STEM_PATH.relative_to(REPO_ROOT)),
        "reviewOrder": [[m, s] for m, s in TARGETS],
        "itemCount": len(manifest_items),
        "items": manifest_items,
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus listening-window pack V1 complete")
    print("Items:", len(manifest_items))
    print("Timing map:", timing_path.relative_to(REPO_ROOT))
    print("Output directory:", OUTPUT_DIR.relative_to(REPO_ROOT))
    print()

    for item in manifest_items:
        print(
            f"measure {item['measureNumber']} step {item['candidateStep']} "
            f"target={item['targetSeconds']:.6f}s "
            f"band={item['confidenceBand']}"
        )
        print("  ", item["files"]["tight"]["full-mix"])
        print("  ", item["files"]["tight"]["other-stem"])

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Manifest:", MANIFEST_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
