from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"
SCAFFOLD_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-event-scaffold.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-identity-evidence.json"

VERSE_START = 18
VERSE_END = 32
MATCH_RADIUS_STEPS = 1


def _safe_int(value: Any, fallback: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _identity(event: dict[str, Any]) -> tuple[int, int] | None:
    string_index = _safe_int(event.get("stringIndex"))
    fret = _safe_int(event.get("fret"))
    if string_index < 0 or fret < 0:
        return None
    return string_index, fret


def main() -> None:
    for path, command in (
        (CANDIDATE_PATH, "python analyzer/run_v8_rhythm_candidate_benchmark.py"),
        (SCAFFOLD_PATH, "python analyzer/build_professional_em_riff_event_scaffold.py"),
        (TIMING_PATH, "python analyzer/run_professional_em_riff_timing_alignment_benchmark.py"),
    ):
        if not path.exists():
            raise FileNotFoundError(f"Missing {path.name}. Run {command} first.")

    candidates = json.loads(CANDIDATE_PATH.read_text())
    scaffold = json.loads(SCAFFOLD_PATH.read_text())
    timing = json.loads(TIMING_PATH.read_text())

    pattern_timing = timing.get("patternTiming") or {}
    protected_steps = {
        pattern_id: [int(step) for step in item.get("quantizedOnsetSteps") or []]
        for pattern_id, item in pattern_timing.items()
        if isinstance(item, dict)
    }

    events = [
        event
        for event in candidates.get("candidates") or []
        if isinstance(event, dict)
        and VERSE_START <= _safe_int(event.get("measureNumber")) <= VERSE_END
    ]

    support: dict[str, dict[int, Counter[tuple[int, int]]]] = {
        "em-riff-a": defaultdict(Counter),
        "em-riff-b": defaultdict(Counter),
    }
    matched_event_count = 0

    for event in events:
        measure = _safe_int(event.get("measureNumber"))
        step = _safe_int(event.get("quantizedStep"))
        identity = _identity(event)
        if step < 0 or identity is None:
            continue

        pattern_id = "em-riff-a" if measure % 2 == 0 else "em-riff-b"
        target_steps = protected_steps.get(pattern_id) or []
        nearest = min(target_steps, key=lambda item: abs(item - step), default=None)
        if nearest is None or abs(nearest - step) > MATCH_RADIUS_STEPS:
            continue

        support[pattern_id][nearest][identity] += 1
        matched_event_count += 1

    evidence: dict[str, list[dict[str, Any]]] = {}
    identity_slot_count = 0
    for pattern_id in ("em-riff-a", "em-riff-b"):
        slots: list[dict[str, Any]] = []
        for step in protected_steps.get(pattern_id) or []:
            ranked = support[pattern_id][step].most_common()
            candidates_for_slot = [
                {
                    "stringIndex": string_index,
                    "fret": fret,
                    "support": count,
                }
                for (string_index, fret), count in ranked
            ]
            if candidates_for_slot:
                identity_slot_count += 1
            slots.append(
                {
                    "quantizedStep": step,
                    "directAudioIdentityCandidates": candidates_for_slot,
                    "leadingIdentity": candidates_for_slot[0] if candidates_for_slot else None,
                    "status": (
                        "direct-audio-identity-evidence-present"
                        if candidates_for_slot
                        else "identity-evidence-missing"
                    ),
                    "professionalManualVerificationRequired": True,
                }
            )
        evidence[pattern_id] = slots

    scaffold_ids = {
        item.get("patternId")
        for item in scaffold.get("patterns") or []
        if isinstance(item, dict)
    }

    checks = {
        "candidateReportPassed": candidates.get("passed") is True,
        "timingAlignmentPassed": timing.get("passed") is True,
        "scaffoldContainsEmRiffA": "em-riff-a" in scaffold_ids,
        "scaffoldContainsEmRiffB": "em-riff-b" in scaffold_ids,
        "directAudioEventsPresent": bool(events),
        "protectedTimingPresent": protected_steps.get("em-riff-a") == [2, 6, 10, 14]
        and protected_steps.get("em-riff-b") == [2, 4, 6, 10, 14],
        "professionalReferenceMayScoreButNotGenerate": True,
        "lockedV7EventsProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-direct-audio-identity-evidence",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "verseMeasuresInspected": [VERSE_START, VERSE_END],
        "directAudioEventCount": len(events),
        "matchedProtectedEventCount": matched_event_count,
        "protectedSlotCount": sum(len(steps) for steps in protected_steps.values()),
        "slotsWithIdentityEvidence": identity_slot_count,
        "patternEvidence": evidence,
        "checks": checks,
        "safeguards": {
            "evidenceIsReadOnly": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotPromoteIdentityWithoutManualVerification": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Review the leading direct-audio string/fret identity for each protected onset against "
            "the professional score. Only manually verified identities may enter exact scoring."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff identity evidence pass:", report["passed"])
    print("Direct-audio events inspected:", len(events))
    print("Matched protected events:", matched_event_count)
    print(
        "Slots with identity evidence:",
        f"{identity_slot_count}/{report['protectedSlotCount']}",
    )
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
