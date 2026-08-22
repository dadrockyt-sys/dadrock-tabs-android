from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

DETAIL_AUDIT_PATH = PUBLIC_DIR / "gomyway-final-ending-event-detail-audit-v1.json"
TIMING_MAP_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-timing-map-v2.json",
    PUBLIC_DIR / "gomyway-professional-timing-map-v1.json",
)
FULL_MIX_PATH = PUBLIC_DIR / "gomywayfullaitest.m4a"
OTHER_STEM_PATH = (
    PUBLIC_DIR
    / "training"
    / "gomyway-audio-separation-v1"
    / "htdemucs"
    / "gomywayfullaitest"
    / "other.wav"
)
OUTPUT_DIR = (
    PUBLIC_DIR
    / "training"
    / "gomyway-final-ending-listening-window-pack-v1"
)
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"

TARGET_MEASURES = (111, 112)


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
    raise FileNotFoundError("Missing professional timing map V2/V1 in public/.")


def measure_number(item: dict[str, Any]) -> int | None:
    value = item.get("measureNumber", item.get("measure"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_measure_bounds(payload: dict[str, Any]) -> dict[int, tuple[float, float]]:
    candidate_lists: list[list[Any]] = []
    for key in ("measures", "measureBounds", "measureBoundaries", "measureReports"):
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
            start = row.get("startSeconds", row.get("start", row.get("measureStartSeconds")))
            end = row.get("endSeconds", row.get("end", row.get("measureEndSeconds")))
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

    if not bounds:
        raise ValueError("Could not extract measure boundaries from the timing map.")
    return bounds


def run_ffmpeg(source: Path, output: Path, start: float, duration: float) -> None:
    subprocess.run(
        [
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
        ],
        check=True,
    )


def main() -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required but was not found in PATH.")

    detail = load_json(DETAIL_AUDIT_PATH)
    timing_path = find_timing_map()
    timing = load_json(timing_path)
    bounds = extract_measure_bounds(timing)

    for audio_path in (FULL_MIX_PATH, OTHER_STEM_PATH):
        if not audio_path.exists():
            raise FileNotFoundError(
                f"Missing audio source: {audio_path.relative_to(REPO_ROOT)}"
            )

    reports = {
        int(item["measureNumber"]): item
        for item in detail.get("measureReports") or []
        if isinstance(item, dict) and item.get("measureNumber") is not None
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_items: list[dict[str, Any]] = []

    for measure in TARGET_MEASURES:
        report = reports.get(measure)
        if report is None:
            raise ValueError(f"Measure {measure} is missing from the event-detail audit.")
        if not report.get("requiresListeningReview"):
            raise ValueError(f"Measure {measure} is not marked for listening review.")
        if measure not in bounds:
            raise KeyError(f"Timing map has no measure {measure}.")

        measure_start, measure_end = bounds[measure]
        measure_duration = measure_end - measure_start
        previous_start = bounds.get(measure - 1, (measure_start - measure_duration, measure_start))[0]
        next_end = bounds.get(measure + 1, (measure_end, measure_end + measure_duration))[1]

        item_dir = OUTPUT_DIR / f"m{measure:03d}"
        item_dir.mkdir(parents=True, exist_ok=True)

        windows = {
            "attack": (measure_start - 0.75, 2.50),
            "measure": (measure_start - 0.20, measure_duration + 0.40),
            "transition": (previous_start - 0.20, (next_end - previous_start) + 0.40),
        }

        files: dict[str, dict[str, str]] = {}
        for window_name, (window_start, window_duration) in windows.items():
            files[window_name] = {}
            for source_name, source_path in (
                ("full-mix", FULL_MIX_PATH),
                ("other-stem", OTHER_STEM_PATH),
            ):
                output = item_dir / f"{source_name}-{window_name}.wav"
                run_ffmpeg(source_path, output, window_start, window_duration)
                files[window_name][source_name] = str(output.relative_to(REPO_ROOT))

        manifest_items.append({
            "measureNumber": measure,
            "measureStartSeconds": round(measure_start, 6),
            "measureEndSeconds": round(measure_end, 6),
            "measureDurationSeconds": round(measure_duration, 6),
            "humanReviewStatus": (report.get("humanReview") or {}).get("status"),
            "measureFlags": report.get("measureFlags") or {},
            "explicitEvents": report.get("explicitEvents") or [],
            "files": files,
            "reviewQuestions": [
                "Is there a fresh rhythm-guitar attack at the beginning of this measure?",
                "Does the guitar sustain for the full measure, or does it decay or stop early?",
                "Is the tie-forward from the previous measure audible and musically correct?",
                "Does the sustained harmony remain rhythm guitar rather than bleed from another source?",
                "Should this measure remain a full-measure sustain in the professional rhythm reference?",
            ],
            "reviewDecision": None,
            "automaticDecisionAllowed": False,
        })

    manifest = {
        "schemaVersion": 1,
        "packType": "final-ending-pending-measure-listening-windows",
        "timingMap": str(timing_path.relative_to(REPO_ROOT)),
        "detailAudit": str(DETAIL_AUDIT_PATH.relative_to(REPO_ROOT)),
        "fullMix": str(FULL_MIX_PATH.relative_to(REPO_ROOT)),
        "otherStem": str(OTHER_STEM_PATH.relative_to(REPO_ROOT)),
        "reviewMeasures": list(TARGET_MEASURES),
        "protectedApprovedMeasure": 113,
        "itemCount": len(manifest_items),
        "items": manifest_items,
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Final-ending listening-window pack V1 complete")
    print("Review measures:", manifest["reviewMeasures"])
    print("Protected approved measure:", manifest["protectedApprovedMeasure"])
    print("Timing map:", timing_path.relative_to(REPO_ROOT))
    print("Output directory:", OUTPUT_DIR.relative_to(REPO_ROOT))
    print()

    for item in manifest_items:
        print(
            f"measure {item['measureNumber']} "
            f"start={item['measureStartSeconds']:.6f}s "
            f"end={item['measureEndSeconds']:.6f}s "
            f"duration={item['measureDurationSeconds']:.6f}s"
        )
        print("  ", item["files"]["attack"]["full-mix"])
        print("  ", item["files"]["attack"]["other-stem"])
        print("  ", item["files"]["measure"]["full-mix"])
        print("  ", item["files"]["measure"]["other-stem"])

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Manifest:", MANIFEST_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
