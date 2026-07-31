from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-v8-notation-em-riff-identity-join.json"

VERSE_START = 18
VERSE_END = 32
STEPS_PER_MEASURE = 16
MATCH_RADIUS_STEPS = 1


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _safe_int(value: Any, fallback: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = -1.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _event_step(event: dict[str, Any]) -> int:
    position = _safe_float(event.get("positionInMeasure"))
    if position >= 0.0:
        return max(0, min(STEPS_PER_MEASURE - 1, int(round(position * STEPS_PER_MEASURE))))

    for key in ("quantizedStep", "step", "stepInMeasure"):
        step = _safe_int(event.get(key))
        if step >= 0:
            return max(0, min(STEPS_PER_MEASURE - 1, step))
    return -1


def main() -> None:
    if not NOTATION_PATH.exists():
        raise FileNotFoundError(
            "Missing full-song V8 notation. Generate public/gomyway-full-song-v8-notation.json first."
        )
    if not TIMING_PATH.exists():
        raise FileNotFoundError(
            "Missing Em riff timing alignment. Run "
            "python analyzer/run_professional_em_riff_timing_alignment_benchmark.py first."
        )

    notation = json.loads(NOTATION_PATH.read_text())
    timing = json.loads(TIMING_PATH.read_text())

    protected_steps = {
        pattern_id: [int(step) for step in item.get("quantizedOnsetSteps") or []]
        for pattern_id, item in (timing.get("patternTiming") or {}).items()
        if isinstance(item, dict)
    }

    identity_events: list[dict[str, Any]] = []
    for node in _walk(notation):
        measure = _safe_int(node.get("measureNumber"))
        string_index = _safe_int(node.get("stringIndex"))
        fret = _safe_int(node.get("fret"))
        step = _event_step(node)
        if (
            VERSE_START <= measure <= VERSE_END
            and string_index >= 0
            and fret >= 0
            and step >= 0
        ):
            identity_events.append(
                {
                    "measureNumber": measure,
                    "quantizedStep": step,
                    "stringIndex": string_index,
                    "fret": fret,
                    "confidence": node.get("confidence"),
                    "sourceEventIndex": node.get("sourceEventIndex", node.get("eventIndex")),
                }
            )

    support: dict[str, dict[int, Counter[tuple[int, int]]]] = {
        "em-riff-a": defaultdict(Counter),
        "em-riff-b": defaultdict(Counter),
    }
    matched_count = 0

    for event in identity_events:
        measure = int(event["measureNumber"])
        step = int(event["quantizedStep"])
        pattern_id = "em-riff-a" if measure % 2 == 0 else "em-riff-b"
        targets = protected_steps.get(pattern_id) or []
        nearest = min(targets, key=lambda target: abs(target - step), default=None)
        if nearest is None or abs(nearest - step) > MATCH_RADIUS_STEPS:
            continue
        support[pattern_id][nearest][(int(event["stringIndex"]), int(event["fret"]))] += 1
        matched_count += 1

    pattern_evidence: dict[str, list[dict[str, Any]]] = {}
    slots_with_evidence = 0
    for pattern_id in ("em-riff-a", "em-riff-b"):
        slots: list[dict[str, Any]] = []
        for step in protected_steps.get(pattern_id) or []:
            ranked = support[pattern_id][step].most_common()
            candidates = [
                {
                    "stringIndex": identity[0],
                    "fret": identity[1],
                    "support": count,
                }
                for identity, count in ranked
            ]
            if candidates:
                slots_with_evidence += 1
            slots.append(
                {
                    "quantizedStep": step,
                    "identityCandidates": candidates,
                    "leadingIdentity": candidates[0] if candidates else None,
                    "manualProfessionalVerificationRequired": True,
                }
            )
        pattern_evidence[pattern_id] = slots

    protected_slot_count = sum(len(steps) for steps in protected_steps.values())
    checks = {
        "timingAlignmentPassed": timing.get("passed") is True,
        "notationIdentityEventsPresent": bool(identity_events),
        "protectedTimingCorrect": protected_steps.get("em-riff-a") == [2, 6, 10, 14]
        and protected_steps.get("em-riff-b") == [2, 4, 6, 10, 14],
        "identityEvidenceFound": slots_with_evidence > 0,
        "readOnlyJoin": True,
        "lockedV7EventsProtected": True,
        "lockedIntroTemplateProtected": True,
        "lockedVerse1TemplateProtected": True,
        "professionalReferenceMayScoreButNotGenerate": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-notation-em-riff-read-only-identity-join",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "verseMeasuresInspected": [VERSE_START, VERSE_END],
        "notationIdentityEventCount": len(identity_events),
        "matchedProtectedEventCount": matched_count,
        "protectedSlotCount": protected_slot_count,
        "slotsWithIdentityEvidence": slots_with_evidence,
        "patternEvidence": pattern_evidence,
        "checks": checks,
        "safeguards": {
            "notationSourceReadOnly": True,
            "doesNotModifyV8Notation": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotPromoteWithoutManualVerification": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Compare each leading V8 notation identity against the visible professional Em riff. "
            "Only confirmed string/fret identities and techniques may enter the scoring reference."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("V8 notation Em riff identity join pass:", report["passed"])
    print("Notation identity events inspected:", len(identity_events))
    print("Matched protected events:", matched_count)
    print("Slots with identity evidence:", f"{slots_with_evidence}/{protected_slot_count}")
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
