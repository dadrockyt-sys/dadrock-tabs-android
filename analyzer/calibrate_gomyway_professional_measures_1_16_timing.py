from __future__ import annotations

import bisect
import json
import math
import os
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
EXTRACTION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json"

HEARTBEAT_SECONDS = float(os.environ.get("JIMMY_HEARTBEAT_SECONDS", "15"))
WINDOW_SECONDS = float(os.environ.get("JIMMY_SCORE_WINDOW_SECONDS", "0.22"))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def find_event_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            keys = set().union(*(item.keys() for item in value[:20]))
            if keys.intersection({"midiPitch", "pitch_midi", "start", "start_time"}):
                return value
        for item in value:
            found = find_event_list(item)
            if found:
                return found
    elif isinstance(value, dict):
        for key in ("events", "noteEvents", "notes", "result", "output", "prediction"):
            if key in value:
                found = find_event_list(value[key])
                if found:
                    return found
        for item in value.values():
            found = find_event_list(item)
            if found:
                return found
    return []


def event_start(event: dict[str, Any]) -> float | None:
    for key in ("start", "start_time", "startTime", "time"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def event_pitch(event: dict[str, Any]) -> int | None:
    for key in ("midiPitch", "pitch_midi", "pitchMidi", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def accepted_pitches(event: dict[str, Any]) -> set[int]:
    pitches = {int(event["midiPitch"])}
    sounding = event.get("soundingMidiPitch")
    if isinstance(sounding, (int, float)):
        pitches.add(int(round(sounding)))
    return pitches


def professional_targets(reference: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for measure in reference.get("measures", []):
        number = int(measure["measureNumber"])
        if not 1 <= number <= 16:
            continue
        for index, event in enumerate(measure.get("events", [])):
            targets.append(
                {
                    "measureNumber": number,
                    "eventIndex": index,
                    "positionInMeasure": float(event["positionInMeasure"]),
                    "acceptedPitches": sorted(accepted_pitches(event)),
                    "event": event,
                }
            )
    return targets


def score_candidate(
    targets: list[dict[str, Any]],
    starts: list[float],
    extracted: list[dict[str, Any]],
    tempo: float,
    offset: float,
) -> dict[str, Any]:
    measure_seconds = 4.0 * 60.0 / tempo
    used: set[int] = set()
    matched = 0
    total_abs_delta = 0.0

    for target in targets:
        expected = (
            offset
            + (target["measureNumber"] - 1) * measure_seconds
            + target["positionInMeasure"] * measure_seconds
        )
        left = bisect.bisect_left(starts, expected - WINDOW_SECONDS)
        right = bisect.bisect_right(starts, expected + WINDOW_SECONDS)
        best_index: int | None = None
        best_delta = math.inf
        accepted = set(target["acceptedPitches"])
        for index in range(left, right):
            if index in used:
                continue
            if extracted[index]["midiPitch"] not in accepted:
                continue
            delta = abs(starts[index] - expected)
            if delta < best_delta:
                best_delta = delta
                best_index = index
        if best_index is not None:
            used.add(best_index)
            matched += 1
            total_abs_delta += best_delta

    total = len(targets)
    return {
        "tempoBpm": round(tempo, 4),
        "firstMeasureOffsetSeconds": round(offset, 4),
        "matched": matched,
        "total": total,
        "score": matched / total if total else 0.0,
        "meanAbsoluteTimingErrorSeconds": (
            total_abs_delta / matched if matched else None
        ),
    }


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    extraction = load_json(EXTRACTION_PATH)
    raw_events = find_event_list(extraction)
    extracted: list[dict[str, Any]] = []
    for raw in raw_events:
        start = event_start(raw)
        pitch = event_pitch(raw)
        if start is None or pitch is None:
            continue
        extracted.append({"start": start, "midiPitch": pitch, "raw": raw})
    extracted.sort(key=lambda item: item["start"])
    starts = [item["start"] for item in extracted]
    targets = professional_targets(reference)

    if not extracted:
        raise RuntimeError("No extracted events found in the full-song winner test.")
    if not targets:
        raise RuntimeError("No professional targets found for measures 1-16.")

    print("Jimmy PAIge measures 1-16 timing calibration")
    print(f"Professional targets: {len(targets)}")
    print(f"Extracted events: {len(extracted)}")
    print(f"Timing window: +/-{WINDOW_SECONDS:.3f}s")

    started = time.monotonic()
    last_heartbeat = started
    best: dict[str, Any] | None = None
    candidates_tested = 0

    # Coarse search centered on the documented 129 BPM, but wide enough to
    # expose whether the earlier 133.8 BPM nine-slot alignment was misleading.
    tempo = 126.0
    while tempo <= 136.0001:
        offset = 0.0
        while offset <= 10.0001:
            candidate = score_candidate(targets, starts, extracted, tempo, offset)
            candidates_tested += 1
            if best is None or (
                candidate["matched"],
                -(candidate["meanAbsoluteTimingErrorSeconds"] or 999.0),
            ) > (
                best["matched"],
                -(best["meanAbsoluteTimingErrorSeconds"] or 999.0),
            ):
                best = candidate
            now = time.monotonic()
            if now - last_heartbeat >= HEARTBEAT_SECONDS:
                assert best is not None
                print(
                    "[calibration heartbeat] "
                    f"elapsed={now-started:.1f}s | candidates={candidates_tested} | "
                    f"best={best['matched']}/{best['total']} "
                    f"({best['score']*100:.2f}%) | "
                    f"tempo={best['tempoBpm']:.3f} | "
                    f"offset={best['firstMeasureOffsetSeconds']:.3f}"
                )
                last_heartbeat = now
            offset += 0.05
        tempo += 0.05

    assert best is not None

    # Fine search around the best coarse candidate.
    coarse_best = dict(best)
    tempo_start = best["tempoBpm"] - 0.15
    tempo_end = best["tempoBpm"] + 0.15
    offset_start = best["firstMeasureOffsetSeconds"] - 0.15
    offset_end = best["firstMeasureOffsetSeconds"] + 0.15
    tempo = tempo_start
    while tempo <= tempo_end + 1e-9:
        offset = offset_start
        while offset <= offset_end + 1e-9:
            candidate = score_candidate(targets, starts, extracted, tempo, offset)
            candidates_tested += 1
            if (
                candidate["matched"],
                -(candidate["meanAbsoluteTimingErrorSeconds"] or 999.0),
            ) > (
                best["matched"],
                -(best["meanAbsoluteTimingErrorSeconds"] or 999.0),
            ):
                best = candidate
            offset += 0.005
        tempo += 0.005

    report = {
        "schemaVersion": 1,
        "benchmark": "professional-measures-1-16-timing-calibration",
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "extractionSource": str(EXTRACTION_PATH.relative_to(REPO_ROOT)),
        "timingWindowSeconds": WINDOW_SECONDS,
        "professionalTargetCount": len(targets),
        "extractedEventCount": len(extracted),
        "candidatesTested": candidates_tested,
        "coarseBest": coarse_best,
        "best": best,
        "documentedTempoBpm": 129.0,
        "priorNineSlotTempoBpm": 133.8,
        "readyToReplaceTimingMap": best["score"] >= 0.50,
        "readyForAutomatedTraining": False,
        "notes": (
            "This calibration separates timing-map quality from extraction quality. "
            "A low score after calibration indicates that the professional event encoding "
            "or extracted pitch candidates require inspection before parameter training."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    elapsed = time.monotonic() - started
    print("Timing calibration complete")
    print(
        f"Best: {best['matched']}/{best['total']} "
        f"({best['score']*100:.2f}%)"
    )
    print(f"Best tempo: {best['tempoBpm']:.3f} BPM")
    print(
        "Best first-measure offset: "
        f"{best['firstMeasureOffsetSeconds']:.3f} seconds"
    )
    print(f"Elapsed: {elapsed:.2f} seconds")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print("Ready for automated training: False")


if __name__ == "__main__":
    main()
