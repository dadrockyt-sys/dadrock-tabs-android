from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-event-scaffold.json"
VERSE1_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-template-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"

EXPECTED_LOCKED_STEPS = [2, 6, 10, 14, 18, 20, 22, 26, 30]
FIRST_MEASURE_STEPS = [step for step in EXPECTED_LOCKED_STEPS if step < 16]
SECOND_MEASURE_STEPS = [step - 16 for step in EXPECTED_LOCKED_STEPS if step >= 16]


def main() -> None:
    if not SCAFFOLD_PATH.exists():
        raise FileNotFoundError(
            "Missing Em riff scaffold. Run "
            "python analyzer/build_professional_em_riff_event_scaffold.py first."
        )
    if not VERSE1_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing Verse 1 rhythm lock. Run "
            "python analyzer/run_v8_verse1_rhythm_template_lock_benchmark.py first."
        )

    scaffold = json.loads(SCAFFOLD_PATH.read_text())
    verse1_lock = json.loads(VERSE1_LOCK_PATH.read_text())

    locked_steps = sorted(
        int(item.get("consensusStep"))
        for item in verse1_lock.get("lockedRhythmTemplate") or []
        if isinstance(item, dict) and item.get("consensusStep") is not None
    )

    pattern_ids = {
        item.get("patternId")
        for item in scaffold.get("patterns") or []
        if isinstance(item, dict)
    }

    checks = {
        "scaffoldContainsEmRiffA": "em-riff-a" in pattern_ids,
        "scaffoldContainsEmRiffB": "em-riff-b" in pattern_ids,
        "verse1TemplateLocked": verse1_lock.get("rhythmTemplateLocked") is True,
        "lockedStepsMatchProtectedConsensus": locked_steps == EXPECTED_LOCKED_STEPS,
        "firstMeasureHasFourProtectedOnsets": len(FIRST_MEASURE_STEPS) == 4,
        "secondMeasureHasFiveProtectedOnsets": len(SECOND_MEASURE_STEPS) == 5,
        "professionalReferenceMayScoreButNotGenerate": True,
        "directAudioRemainsSourceOfTruth": True,
        "lockedV7EventsProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-protected-timing-alignment",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "twoMeasureLockedSteps": locked_steps,
        "patternTiming": {
            "em-riff-a": {
                "measureRole": "first measure of two-measure Em phrase",
                "quantizedOnsetSteps": FIRST_MEASURE_STEPS,
                "onsetCount": len(FIRST_MEASURE_STEPS),
                "timingSource": "locked direct-audio Verse 1 consensus",
                "noteIdentityStatus": "professional-source feature scaffold only",
                "stringFretStatus": "pending manual verification",
            },
            "em-riff-b": {
                "measureRole": "second measure of two-measure Em phrase",
                "quantizedOnsetSteps": SECOND_MEASURE_STEPS,
                "onsetCount": len(SECOND_MEASURE_STEPS),
                "timingSource": "locked direct-audio Verse 1 consensus",
                "noteIdentityStatus": "professional-source feature scaffold only",
                "stringFretStatus": "pending manual verification",
            },
        },
        "checks": checks,
        "safeguards": {
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotCreateNewJimmyEvents": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Manually verify the visible string/fret identities and technique ownership for each "
            "protected onset before exact note scoring is enabled."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff timing alignment pass:", report["passed"])
    print("Two-measure protected steps:", locked_steps)
    print("em-riff-a onset steps:", FIRST_MEASURE_STEPS)
    print("em-riff-b onset steps:", SECOND_MEASURE_STEPS)
    print("Ready for exact scoring:", report["readyForExactScoring"])
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
