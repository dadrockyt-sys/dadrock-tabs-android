from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
INTRO_OVERLAY_PATH = PUBLIC / "gomyway-v8-supervised-intro-overlay-v3.json"
TRAINING_GATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-training-gate-v1.json"
NOTATION_LOCK_PATH = PUBLIC / "professional-tablature-notation-standard-lock-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-full-rhythm-technique-evidence-audit-v1.json"

TECHNIQUE_KEYS = (
    "techniques",
    "technique",
    "articulations",
    "articulation",
    "effects",
    "effect",
    "expressions",
    "expression",
    "ornaments",
    "ornament",
)

BEND_WORDS = ("bend", "full-bend", "half-bend", "release", "prebend", "pre-bend")
VIBRATO_WORDS = ("vibrato", "vib")
SUSTAIN_WORDS = ("sustain", "let-ring", "let ring", "ring", "tie", "held", "hold")


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def events_from(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    raise RuntimeError("No recognized event list")


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def duration_steps(event: dict[str, Any]) -> int:
    value = integer(event.get("durationSteps", event.get("duration", 1)))
    return max(1, value or 1)


def notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    if not isinstance(value, list):
        return []
    return [note for note in value if isinstance(note, dict)]


def note_signature(event: dict[str, Any]) -> tuple[tuple[int | None, int | None], ...]:
    result: list[tuple[int | None, int | None]] = []
    for note in notes(event):
        string_value = integer(note.get("string", note.get("stringIndex")))
        fret_value = integer(note.get("fret"))
        result.append((string_value, fret_value))
    return tuple(sorted(result))


def flatten_text(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip().lower()] if value.strip() else []
    if isinstance(value, (int, float, bool)):
        return [str(value).lower()]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            result.extend(flatten_text(item))
        return result
    if isinstance(value, dict):
        result = []
        for key, item in value.items():
            result.append(str(key).strip().lower())
            result.extend(flatten_text(item))
        return result
    return [str(value).strip().lower()]


def explicit_technique_tokens(event: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for key in TECHNIQUE_KEYS:
        if key in event:
            result.extend(flatten_text(event.get(key)))
    for note in notes(event):
        for key in TECHNIQUE_KEYS:
            if key in note:
                result.extend(flatten_text(note.get(key)))
    return sorted(set(token for token in result if token))


def contains_word(tokens: list[str], words: tuple[str, ...]) -> bool:
    joined = " ".join(tokens)
    return any(word in joined for word in words)


def main() -> None:
    source = load(SOURCE_PATH)
    intro = load(INTRO_OVERLAY_PATH)
    training_gate = load(TRAINING_GATE_PATH)
    notation_lock = load(NOTATION_LOCK_PATH)

    source_events = events_from(source)
    intro_events = events_from(intro)

    key_counts: Counter[str] = Counter()
    token_counts: Counter[str] = Counter()
    explicit_bends: list[dict[str, Any]] = []
    explicit_vibrato: list[dict[str, Any]] = []
    explicit_sustain: list[dict[str, Any]] = []
    duration_sustain: list[dict[str, Any]] = []
    long_duration_events: list[dict[str, Any]] = []

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for index, event in enumerate(source_events):
        measure_value = measure(event)
        step_value = step(event)
        if measure_value is not None:
            by_measure[measure_value].append(event)

        for key in TECHNIQUE_KEYS:
            if key in event:
                key_counts[key] += 1
        for note in notes(event):
            for key in TECHNIQUE_KEYS:
                if key in note:
                    key_counts[f"notes.{key}"] += 1

        tokens = explicit_technique_tokens(event)
        token_counts.update(tokens)
        row = {
            "eventIndex": index,
            "measureNumber": measure_value,
            "quantizedStep": step_value,
            "durationSteps": duration_steps(event),
            "notes": notes(event),
            "tokens": tokens,
        }
        if contains_word(tokens, BEND_WORDS):
            explicit_bends.append(row)
        if contains_word(tokens, VIBRATO_WORDS):
            explicit_vibrato.append(row)
        if contains_word(tokens, SUSTAIN_WORDS):
            explicit_sustain.append(row)
        if duration_steps(event) > 1:
            duration_sustain.append(row)
        if duration_steps(event) >= 4:
            long_duration_events.append(row)

    continuation_candidates: list[dict[str, Any]] = []
    for measure_value, measure_events in sorted(by_measure.items()):
        ordered = sorted(
            measure_events,
            key=lambda event: (
                step(event) if step(event) is not None else 10_000,
                duration_steps(event),
            ),
        )
        for current, following in zip(ordered, ordered[1:]):
            current_step = step(current)
            following_step = step(following)
            if current_step is None or following_step is None:
                continue
            current_signature = note_signature(current)
            following_signature = note_signature(following)
            if current_signature and current_signature == following_signature:
                continuation_candidates.append({
                    "measureNumber": measure_value,
                    "fromStep": current_step,
                    "toStep": following_step,
                    "noteSignature": current_signature,
                    "fromDurationSteps": duration_steps(current),
                    "evidence": "same-note-signature-repeated",
                })

    intro_bends = []
    intro_vibrato = []
    for index, event in enumerate(intro_events):
        tokens = explicit_technique_tokens(event)
        row = {
            "eventIndex": index,
            "measureNumber": measure(event),
            "quantizedStep": step(event),
            "tokens": tokens,
            "notes": notes(event),
        }
        if contains_word(tokens, BEND_WORDS):
            intro_bends.append(row)
        if contains_word(tokens, VIBRATO_WORDS):
            intro_vibrato.append(row)

    technique_layer_present = bool(
        explicit_bends
        or explicit_vibrato
        or explicit_sustain
        or duration_sustain
        or continuation_candidates
    )
    explicit_full_song_techniques_present = bool(
        explicit_bends or explicit_vibrato or explicit_sustain
    )

    checks = {
        "rhythmTrainingGatePassed": training_gate.get("passed") is True,
        "notationStandardLockPassed": notation_lock.get("passed") is True,
        "sourceEventCountExact": len(source_events) == 949,
        "introOverlayHasExpectedBends": len(intro_bends) == 6,
        "techniqueEvidenceAudited": True,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "protectedRendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    report = {
        "schemaVersion": 1,
        "auditType": "full-rhythm-technique-and-sustain-evidence",
        "passed": all(checks.values()),
        "source": {
            "path": str(SOURCE_PATH.relative_to(ROOT)),
            "eventCount": len(source_events),
        },
        "introOverlay": {
            "path": str(INTRO_OVERLAY_PATH.relative_to(ROOT)),
            "eventCount": len(intro_events),
            "explicitBendCount": len(intro_bends),
            "explicitVibratoCount": len(intro_vibrato),
        },
        "fullSongEvidence": {
            "recognizedTechniqueKeyCounts": dict(sorted(key_counts.items())),
            "uniqueTechniqueTokenCount": len(token_counts),
            "techniqueTokenCounts": dict(token_counts.most_common(100)),
            "explicitBendCount": len(explicit_bends),
            "explicitVibratoCount": len(explicit_vibrato),
            "explicitSustainCount": len(explicit_sustain),
            "durationSustainCandidateCount": len(duration_sustain),
            "longDurationEventCount": len(long_duration_events),
            "sameNoteContinuationCandidateCount": len(continuation_candidates),
            "techniqueLayerPresent": technique_layer_present,
            "explicitFullSongTechniquesPresent": explicit_full_song_techniques_present,
        },
        "samples": {
            "explicitBends": explicit_bends[:30],
            "explicitVibrato": explicit_vibrato[:30],
            "explicitSustain": explicit_sustain[:30],
            "durationSustainCandidates": duration_sustain[:30],
            "sameNoteContinuationCandidates": continuation_candidates[:30],
        },
        "readiness": {
            "readyForTechniqueRendererBinding": explicit_full_song_techniques_present,
            "readyForDurationSustainLines": bool(duration_sustain),
            "readyForSameNoteContinuationLines": bool(continuation_candidates),
            "requiresTechniqueRecoveryBeforeCompleteProof": not explicit_full_song_techniques_present,
        },
        "checks": checks,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY FULL RHYTHM TECHNIQUE EVIDENCE AUDIT V1 COMPLETE")
    print("Passed:", report["passed"])
    print("Source events:", len(source_events))
    print("Recognized technique keys:", dict(sorted(key_counts.items())))
    print("Explicit bends:", len(explicit_bends))
    print("Explicit vibrato:", len(explicit_vibrato))
    print("Explicit sustain markers:", len(explicit_sustain))
    print("Duration sustain candidates:", len(duration_sustain))
    print("Same-note continuation candidates:", len(continuation_candidates))
    print("Ready for technique renderer binding:", report["readiness"]["readyForTechniqueRendererBinding"])
    print("Ready for duration sustain lines:", report["readiness"]["readyForDurationSustainLines"])
    print("Requires technique recovery before complete proof:", report["readiness"]["requiresTechniqueRecoveryBeforeCompleteProof"])
    print("Source events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Protected renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
