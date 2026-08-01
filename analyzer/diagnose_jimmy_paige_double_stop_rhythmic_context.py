from __future__ import annotations

import json
from collections import Counter
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import REPO_ROOT

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
FEATURES_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-double-stop-pair-feature-diagnosis.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-double-stop-rhythmic-context.json"

CONTEXT_BEFORE_SECONDS = 0.75
CONTEXT_AFTER_SECONDS = 0.35
TARGET_PITCHES = {58, 62}


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _end(event: dict[str, Any]) -> float:
    for key in ("end", "end_time", "endTime"):
        if event.get(key) is not None:
            return float(event[key])
    duration = float(event.get("duration", event.get("duration_seconds", 0.0)) or 0.0)
    return _start(event) + duration


def _duration(event: dict[str, Any]) -> float:
    return max(0.0, _end(event) - _start(event))


def _pair_center(item: dict[str, Any]) -> float:
    pair = item.get("bestPair") or item.get("pair") or item
    if pair.get("pairCenterSeconds") is not None:
        return float(pair["pairCenterSeconds"])
    return (
        float(pair.get("pitch58Start", 0.0))
        + float(pair.get("pitch62Start", 0.0))
    ) / 2.0


def _context_report(
    events: list[dict[str, Any]],
    center: float,
) -> dict[str, Any]:
    before = [
        event
        for event in events
        if center - CONTEXT_BEFORE_SECONDS <= _start(event) < center
    ]
    after = [
        event
        for event in events
        if center < _start(event) <= center + CONTEXT_AFTER_SECONDS
    ]
    before.sort(key=_start)
    after.sort(key=_start)

    before_pitches = [int(event.get("midiPitch", -999)) for event in before]
    after_pitches = [int(event.get("midiPitch", -999)) for event in after]

    last_before = before[-8:]
    first_after = after[:5]

    return {
        "centerSeconds": round(center, 6),
        "beforeEventCount": len(before),
        "afterEventCount": len(after),
        "beforePitchCounts": {
            str(pitch): count
            for pitch, count in sorted(Counter(before_pitches).items())
        },
        "afterPitchCounts": {
            str(pitch): count
            for pitch, count in sorted(Counter(after_pitches).items())
        },
        "precedingPitchSequence": [
            {
                "pitch": int(event.get("midiPitch", -999)),
                "deltaSeconds": round(_start(event) - center, 6),
                "durationSeconds": round(_duration(event), 6),
                "confidence": event.get("confidence"),
            }
            for event in last_before
        ],
        "followingPitchSequence": [
            {
                "pitch": int(event.get("midiPitch", -999)),
                "deltaSeconds": round(_start(event) - center, 6),
                "durationSeconds": round(_duration(event), 6),
                "confidence": event.get("confidence"),
            }
            for event in first_after
        ],
        "precedingTargetToneCount": sum(
            1 for pitch in before_pitches if pitch in TARGET_PITCHES
        ),
        "precedingLowRegisterCount": sum(
            1 for pitch in before_pitches if 40 <= pitch <= 57
        ),
        "precedingUpperRegisterCount": sum(
            1 for pitch in before_pitches if 58 <= pitch <= 76
        ),
        "precedingAttackDensityPerSecond": round(
            len(before) / CONTEXT_BEFORE_SECONDS,
            3,
        ),
        "followingAttackDensityPerSecond": round(
            len(after) / CONTEXT_AFTER_SECONDS,
            3,
        ),
    }


def _extract_feature_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("pairFeatures", "pairs", "reports", "featureRows", "items"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    rows: list[dict[str, Any]] = []
    for key in ("truePositivePairs", "falsePositivePairs"):
        value = payload.get(key)
        if isinstance(value, list):
            label = "true-positive" if key.startswith("true") else "false-positive"
            for item in value:
                rows.append({**item, "classification": label})
    return rows


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")
    if not FEATURES_PATH.is_file():
        raise FileNotFoundError(f"Missing pair feature diagnosis: {FEATURES_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    feature_payload = json.loads(FEATURES_PATH.read_text(encoding="utf-8"))
    rows = _extract_feature_rows(feature_payload)

    if not rows:
        raise RuntimeError("No pair feature rows found in feature diagnosis JSON")

    reports: list[dict[str, Any]] = []
    for item in rows:
        classification = str(
            item.get("classification")
            or item.get("label")
            or item.get("type")
            or "unknown"
        )
        measure = int(item.get("measureNumber", item.get("measure", -1)))
        center = _pair_center(item)
        reports.append(
            {
                "classification": classification,
                "measureNumber": measure,
                "pairCenterPhase": item.get("pairCenterPhase", item.get("phase")),
                "onsetSeparationSeconds": item.get(
                    "onsetSeparationSeconds",
                    item.get("separationSeconds", item.get("sep")),
                ),
                "sustainOverlapSeconds": item.get(
                    "sustainOverlapSeconds",
                    item.get("overlapSeconds", item.get("overlap")),
                ),
                "minimumPairDurationSeconds": item.get(
                    "minimumPairDurationSeconds",
                    item.get("minDurationSeconds", item.get("minDuration")),
                ),
                "nearbySupportCount": item.get(
                    "nearbySupportCount",
                    item.get("supportCount", item.get("support")),
                ),
                **_context_report(events, center),
            }
        )

    true_rows = [
        item for item in reports if "true" in item["classification"].lower()
    ]
    false_rows = [
        item for item in reports if "false" in item["classification"].lower()
    ]

    def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
        values = [float(item[key]) for item in rows if item.get(key) is not None]
        return round(sum(values) / len(values), 6) if values else None

    summary = {
        "truePositiveCount": len(true_rows),
        "falsePositiveCount": len(false_rows),
        "truePositiveMeanPrecedingDensity": _mean(
            true_rows, "precedingAttackDensityPerSecond"
        ),
        "falsePositiveMeanPrecedingDensity": _mean(
            false_rows, "precedingAttackDensityPerSecond"
        ),
        "truePositiveMeanFollowingDensity": _mean(
            true_rows, "followingAttackDensityPerSecond"
        ),
        "falsePositiveMeanFollowingDensity": _mean(
            false_rows, "followingAttackDensityPerSecond"
        ),
        "truePositiveMeanPrecedingLowRegisterCount": _mean(
            true_rows, "precedingLowRegisterCount"
        ),
        "falsePositiveMeanPrecedingLowRegisterCount": _mean(
            false_rows, "precedingLowRegisterCount"
        ),
        "truePositiveMeanPrecedingTargetToneCount": _mean(
            true_rows, "precedingTargetToneCount"
        ),
        "falsePositiveMeanPrecedingTargetToneCount": _mean(
            false_rows, "precedingTargetToneCount"
        ),
    }

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "double-stop-rhythmic-context-diagnosis",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "sourcePairFeatures": str(FEATURES_PATH.relative_to(REPO_ROOT)),
        "contextBeforeSeconds": CONTEXT_BEFORE_SECONDS,
        "contextAfterSeconds": CONTEXT_AFTER_SECONDS,
        "reports": reports,
        "summary": summary,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Double-stop rhythmic-context diagnosis")
    for item in reports:
        print(
            f"{item['classification'].upper()} measure {item['measureNumber']:>2} | "
            f"beforeDensity={item['precedingAttackDensityPerSecond']} | "
            f"afterDensity={item['followingAttackDensityPerSecond']} | "
            f"lowBefore={item['precedingLowRegisterCount']} | "
            f"targetsBefore={item['precedingTargetToneCount']} | "
            f"preceding={[row['pitch'] for row in item['precedingPitchSequence']]}"
        )

    print("Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
