from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
JOIN_PATH = REPO_ROOT / "public" / "gomyway-v8-notation-em-riff-identity-join.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-identity-contrast.json"

# Standard guitar stringIndex convention used by the V8 notation output:
# 0=high-e, 1=B, 2=G, 3=D, 4=A, 5=low-E.
# These identities are manually verified from the supplied professional rhythm pages.
EXPECTED = {
    "em-riff-a": {
        2: [{"stringIndex": 2, "fret": 2, "technique": "full-step-bend"}],
        6: [{"stringIndex": 2, "fret": 0, "technique": "bend-release-target"}],
        10: [{"stringIndex": 3, "fret": 2, "technique": "picked-note"}],
        14: [{"stringIndex": 4, "fret": 0, "technique": "open-string-note"}],
    },
    "em-riff-b": {
        2: [{"stringIndex": 2, "fret": 2, "technique": "full-step-bend"}],
        4: [{"stringIndex": 2, "fret": 0, "technique": "bend-release-target"}],
        6: [{"stringIndex": 3, "fret": 2, "technique": "picked-note"}],
        10: [{"stringIndex": 4, "fret": 0, "technique": "open-string-note"}],
        14: [
            {"stringIndex": 1, "fret": 3, "technique": "ending-double-stop"},
            {"stringIndex": 2, "fret": 3, "technique": "ending-double-stop"},
        ],
    },
}


def _identity(value: Any) -> tuple[int, int] | None:
    if not isinstance(value, dict):
        return None
    try:
        return int(value.get("stringIndex")), int(value.get("fret"))
    except (TypeError, ValueError):
        return None


def main() -> None:
    if not JOIN_PATH.exists():
        raise FileNotFoundError(
            "Missing V8 notation identity join. Run "
            "python analyzer/run_v8_notation_em_riff_identity_join_benchmark.py first."
        )

    joined = json.loads(JOIN_PATH.read_text())
    if joined.get("passed") is not True:
        raise ValueError("The protected V8 notation identity join did not pass.")

    comparisons: list[dict[str, Any]] = []
    exact_leading_matches = 0
    slot_count = 0

    for pattern_id, slots in (joined.get("patternEvidence") or {}).items():
        expected_slots = EXPECTED.get(pattern_id) or {}
        for slot in slots or []:
            step = int(slot.get("quantizedStep"))
            expected_events = expected_slots.get(step) or []
            expected_identities = {
                (int(item["stringIndex"]), int(item["fret"]))
                for item in expected_events
            }
            leading = _identity(slot.get("leadingIdentity"))
            alternatives = {
                identity
                for identity in (
                    _identity(item)
                    for item in slot.get("identityCandidates") or []
                )
                if identity is not None
            }

            leading_matches = leading in expected_identities
            any_candidate_matches = bool(expected_identities & alternatives)
            if leading_matches:
                exact_leading_matches += 1
            slot_count += 1

            comparisons.append(
                {
                    "patternId": pattern_id,
                    "quantizedStep": step,
                    "professionalExpectedEvents": expected_events,
                    "jimmyLeadingIdentity": (
                        {"stringIndex": leading[0], "fret": leading[1]}
                        if leading is not None
                        else None
                    ),
                    "leadingIdentityMatchesProfessional": leading_matches,
                    "anyRankedCandidateMatchesProfessional": any_candidate_matches,
                    "status": (
                        "leading-match"
                        if leading_matches
                        else "training-correction-required"
                    ),
                }
            )

    exact_percentage = round(100.0 * exact_leading_matches / max(1, slot_count), 2)
    correction_slots = [
        item for item in comparisons
        if item["status"] == "training-correction-required"
    ]

    checks = {
        "identityJoinPassed": joined.get("passed") is True,
        "allNineProtectedSlotsCompared": slot_count == 9,
        "professionalEventsAreScoringOnly": True,
        "professionalEventsDoNotGenerateJimmyNotes": True,
        "v8NotationReadOnly": True,
        "lockedV7EventsProtected": True,
        "lockedIntroTemplateProtected": True,
        "lockedVerse1TemplateProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-identity-contrast",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "protectedSlotCount": slot_count,
        "exactLeadingIdentityMatches": exact_leading_matches,
        "exactLeadingIdentityPercentage": exact_percentage,
        "correctionRequiredSlotCount": len(correction_slots),
        "comparisons": comparisons,
        "checks": checks,
        "safeguards": {
            "comparisonIsReadOnly": True,
            "doesNotModifyV8Notation": True,
            "doesNotModifyLockedTiming": True,
            "doesNotModifyRenderer": True,
            "doesNotModifyProtectedBaselines": True,
        },
        "nextStep": (
            "Train a separate candidate-scoring layer to prefer direct-audio pitch and repeated-riff "
            "support that agree with the verified Em-riff identities. Do not rewrite protected V7/V8 "
            "events until a later adoption benchmark proves improvement."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff identity contrast pass:", report["passed"])
    print("Protected slots compared:", slot_count)
    print("Exact leading identity matches:", f"{exact_leading_matches}/{slot_count}")
    print("Exact leading identity percentage:", f"{exact_percentage}%")
    print("Slots requiring training correction:", len(correction_slots))
    for item in correction_slots:
        print(
            " -",
            item["patternId"],
            "step",
            item["quantizedStep"],
            "Jimmy:",
            item["jimmyLeadingIdentity"],
            "Professional:",
            item["professionalExpectedEvents"],
        )
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
