from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-pattern-library.json"

PRIORITY_ORDER = [
    "em-riff-a",
    "em-riff-b",
    "g-position-riff-a",
    "g-position-riff-b",
    "picked-muted-turnaround",
    "chorus-g6",
    "chorus-atp2",
    "chorus-e-d-e",
    "chorus-g-e",
    "bridge-e-d",
    "bridge-a-e",
    "solo-backing-e-d",
    "solo-backing-a-d6-a",
    "solo-transition-e-d",
    "solo-transition-held-d",
    "solo-transition-pickup-4-5-6",
    "full-measure-rest",
    "outro-g-atp2",
    "outro-held-atp2",
    "outro-final-held-atp2-dead-note-rest",
]

PATTERN_FEATURES = {
    "em-riff-a": ["full-step bend", "bend release", "single-note riff", "sustain"],
    "em-riff-b": ["single-note riff", "two-note chord ending", "sustain"],
    "g-position-riff-a": ["full-step bend", "bend release", "vibrato", "single-note riff"],
    "g-position-riff-b": ["single-note riff", "vibrato"],
    "picked-muted-turnaround": ["dead notes", "alternate picking", "single-note turnaround"],
    "chorus-g6": ["G6 voicing", "repeated chord attacks", "sustain"],
    "chorus-atp2": ["A(tp2) voicing", "repeated chord attacks", "sustain"],
    "chorus-e-d-e": ["E-D-E chord movement", "rests", "sustain"],
    "chorus-g-e": ["G-E chord movement", "rests", "sustain"],
    "bridge-e-d": ["E-D chord movement", "dead-note strums", "rests"],
    "bridge-a-e": ["A-E chord movement", "dead-note strums", "slides", "sustain"],
    "solo-backing-e-d": ["E-D chord movement", "dead-note strums", "short chord attacks"],
    "solo-backing-a-d6-a": ["A-D6-A chord movement", "dead-note strums", "short chord attacks"],
    "solo-transition-e-d": ["E-D chord movement", "dead-note strums"],
    "solo-transition-held-d": ["held D voicing", "tie", "sustain"],
    "solo-transition-pickup-4-5-6": ["dead notes", "ascending pickup", "single notes"],
    "full-measure-rest": ["full-measure rest"],
    "outro-g-atp2": ["G(tp2)-A(tp2) movement", "sustain"],
    "outro-held-atp2": ["held A(tp2) voicing", "tie", "multi-measure sustain"],
    "outro-final-held-atp2-dead-note-rest": ["held A(tp2)", "dead note", "rest", "final barline"],
}


def main() -> None:
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(
            "Missing professional rhythm reference. Run "
            "python analyzer/build_professional_rhythm_reference_measure_map.py first."
        )

    reference = json.loads(REFERENCE_PATH.read_text())
    measures = reference.get("measures") or []

    measures_by_pattern: dict[str, list[int]] = defaultdict(list)
    source_pages_by_pattern: dict[str, set[int]] = defaultdict(set)
    sections_by_pattern: dict[str, set[str]] = defaultdict(set)

    for measure in measures:
        pattern_id = str(measure.get("patternId") or "unclassified")
        measure_number = int(measure.get("measureNumber") or 0)
        measures_by_pattern[pattern_id].append(measure_number)
        source_pages_by_pattern[pattern_id].update(measure.get("sourcePages") or [])
        section = measure.get("sectionLabel")
        if section:
            sections_by_pattern[pattern_id].add(str(section))

    discovered = sorted(
        measures_by_pattern,
        key=lambda item: (
            PRIORITY_ORDER.index(item) if item in PRIORITY_ORDER else len(PRIORITY_ORDER),
            item,
        ),
    )

    patterns = []
    for pattern_id in discovered:
        assigned_measures = sorted(measures_by_pattern[pattern_id])
        patterns.append({
            "patternId": pattern_id,
            "priority": discovered.index(pattern_id) + 1,
            "assignedMeasureCount": len(assigned_measures),
            "assignedMeasures": assigned_measures,
            "sourcePages": sorted(source_pages_by_pattern[pattern_id]),
            "sectionLabels": sorted(sections_by_pattern[pattern_id]),
            "expectedFeatures": PATTERN_FEATURES.get(pattern_id, []),
            "events": [],
            "eventTranscriptionStatus": "pending-manual-verification",
            "verifiedFromProfessionalPages": False,
            "readOnlyBenchmark": True,
            "mayGenerateJimmyNotes": False,
        })

    classified_measure_count = sum(
        item["assignedMeasureCount"]
        for item in patterns
        if item["patternId"] != "unclassified"
    )
    report = {
        "schemaVersion": 1,
        "referenceType": "professional-rhythm-reusable-pattern-library",
        "instrumentPart": "rhythm",
        "sourceMeasureReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "patternCount": len(patterns),
        "measureCount": len(measures),
        "classifiedMeasureCount": classified_measure_count,
        "measurePatternCoveragePercent": round(
            (classified_measure_count / len(measures)) * 100.0, 6
        ) if measures else 0.0,
        "allPatternsEventVerified": all(
            item["verifiedFromProfessionalPages"] is True for item in patterns
        ),
        "readyForExactScoring": False,
        "verificationQueue": [item["patternId"] for item in patterns],
        "patterns": patterns,
        "safeguards": {
            "professionalReferenceMayScoreButNotGenerate": True,
            "directAudioRemainsSourceOfTruth": True,
            "lockedV7EventsProtected": True,
            "lockedIntroTemplateProtected": True,
            "lockedVerse1TemplateProtected": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "noSyntheticNotes": True,
        },
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional rhythm pattern library built:", report["patternCount"])
    print("Measures classified:", f"{classified_measure_count}/{len(measures)}")
    print("Pattern coverage:", f"{report['measurePatternCoveragePercent']}%")
    print("Exact event scoring ready:", report["readyForExactScoring"])
    print("First verification target:", report["verificationQueue"][0])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
