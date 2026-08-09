from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

v2 = bench.v2
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-detector-event-evidence-inventory-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-detector-event-evidence-inventory-v1-manifest.json"

CONFIDENCE_KEYS = (
    "confidence",
    "noteConfidence",
    "probability",
    "amplitude",
    "velocity",
)
START_KEYS = ("start", "start_time", "startTime")
END_KEYS = ("end", "end_time", "endTime")
DURATION_KEYS = ("duration", "durationSeconds", "noteDuration")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_float(value: Any) -> float | None:
    try:
        if value is None or isinstance(value, bool):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def first_number(event: dict[str, Any], keys: tuple[str, ...]) -> tuple[str | None, float | None]:
    for key in keys:
        value = as_float(event.get(key))
        if value is not None:
            return key, value
    return None, None


def summarize(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    ordered = sorted(values)
    n = len(ordered)
    return {
        "count": n,
        "min": round(ordered[0], 6),
        "p10": round(ordered[max(0, int((n - 1) * 0.10))], 6),
        "p25": round(ordered[max(0, int((n - 1) * 0.25))], 6),
        "median": round(float(median(ordered)), 6),
        "p75": round(ordered[max(0, int((n - 1) * 0.75))], 6),
        "p90": round(ordered[max(0, int((n - 1) * 0.90))], 6),
        "max": round(ordered[-1], 6),
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    key_counts: Counter[str] = Counter()
    confidence_key_counts: Counter[str] = Counter()
    duration_key_counts: Counter[str] = Counter()
    confidence_values: list[float] = []
    duration_values: list[float] = []
    derived_duration_values: list[float] = []

    sample_events: list[dict[str, Any]] = []

    for event in events:
        if not isinstance(event, dict):
            continue
        key_counts.update(event.keys())

        conf_key, conf = first_number(event, CONFIDENCE_KEYS)
        if conf_key is not None and conf is not None:
            confidence_key_counts[conf_key] += 1
            confidence_values.append(conf)

        dur_key, dur = first_number(event, DURATION_KEYS)
        if dur_key is not None and dur is not None:
            duration_key_counts[dur_key] += 1
            duration_values.append(dur)

        _, start = first_number(event, START_KEYS)
        _, end = first_number(event, END_KEYS)
        if start is not None and end is not None and end >= start:
            derived_duration_values.append(end - start)

        if len(sample_events) < 5:
            sample_events.append({
                "keys": sorted(event.keys()),
                "confidenceKey": conf_key,
                "confidence": conf,
                "durationKey": dur_key,
                "duration": dur,
                "start": start,
                "end": end,
            })

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during source detector inventory")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "source-detector-event-evidence-inventory",
        "eventCount": len(events),
        "topEventKeys": key_counts.most_common(40),
        "confidenceKeyCounts": dict(confidence_key_counts),
        "durationKeyCounts": dict(duration_key_counts),
        "confidenceSummary": summarize(confidence_values),
        "explicitDurationSummary": summarize(duration_values),
        "derivedDurationSummary": summarize(derived_duration_values),
        "sampleEvents": sample_events,
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "eventCount": len(events),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 SOURCE DETECTOR EVENT EVIDENCE INVENTORY V1")
    print("Passed: True")
    print("Protected event count:", len(events))
    print("Confidence key counts:", dict(confidence_key_counts))
    print("Duration key counts:", dict(duration_key_counts))
    print("Confidence summary:", summarize(confidence_values))
    print("Explicit duration summary:", summarize(duration_values))
    print("Derived duration summary:", summarize(derived_duration_values))
    print("Top event keys:")
    for key, count in key_counts.most_common(30):
        print(f"  {key}: {count}")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
