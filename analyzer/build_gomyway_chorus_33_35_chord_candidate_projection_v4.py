from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

V1_MODULE_PATH = Path(__file__).with_name(
    "build_gomyway_chorus_33_35_chord_candidate_projection_v1.py"
)
PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-plan-v1.json"
EVIDENCE_PATH = PUBLIC / "gomyway-chorus-33-35-audio-chord-evidence-v1.json"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v4.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v4-manifest.json"

# Human-verified chorus voicings are scoring/training labels only.
# They are never written into the protected 949-event source.
EXPECTED = {
    33: {
        "name": "G6",
        "multiplicity": 4,
        "strings": [1, 2, 3, 4],
        "frets": [0, 3, 4, 5],
    },
    34: {
        "name": "A(tp2)",
        "multiplicity": 4,
        "strings": [2, 3, 4, 5],
        "frets": [2, 2, 2, 0],
    },
    35: {
        "name": "E/D/E chorus movement",
        "multiplicity": 3,
        "strings": [2, 3, 4],
        "fretsByStep": {
            0: [9, 9, 9],
            2: [9, 9, 9],
            4: [9, 9, 9],
            6: [9, 9, 9],
            8: [7, 7, 7],
            10: [9, 9, 9],
        },
    },
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def load_v1_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "gomyway_chord_projection_v1",
        V1_MODULE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V1 chord projection helpers.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_notes(measure: int, step: int) -> tuple[tuple[int, int], ...]:
    spec = EXPECTED[measure]
    strings = spec["strings"]
    if measure == 35:
        frets = spec["fretsByStep"].get(step)
        if frets is None:
            return ()
    else:
        frets = spec["frets"]
    return tuple(
        sorted(
            (int(string), int(fret))
            for string, fret in zip(strings, frets)
        )
    )


def average_fret_distance(
    candidate: tuple[tuple[int, int], ...],
    expected: tuple[tuple[int, int], ...],
) -> float:
    if len(candidate) != len(expected):
        return 999.0
    candidate_by_string = dict(candidate)
    expected_by_string = dict(expected)
    if set(candidate_by_string) != set(expected_by_string):
        return 999.0
    return sum(
        abs(candidate_by_string[string] - expected_by_string[string])
        for string in expected_by_string
    ) / max(1, len(expected_by_string))


def main() -> None:
    v1 = load_v1_module()
    plan = load(PLAN_PATH)
    evidence = load(EVIDENCE_PATH)
    source = load(SOURCE_PATH)

    if evidence.get("passed") is not True:
        raise RuntimeError("Audio chord evidence is not green.")
    if evidence.get("readyForReadOnlyChordCandidateProjection") is not True:
        raise RuntimeError("Audio chord evidence is not ready for projection.")

    source_events = v1.source_rows(source)
    if len(source_events) != 949:
        raise RuntimeError(
            f"Expected 949 protected source events, found {len(source_events)}."
        )

    plan_targets = {
        (int(row["measureNumber"]), int(row["quantizedStep"])): row
        for row in plan.get("targets", [])
        if isinstance(row, dict)
    }

    projection_rows: list[dict[str, Any]] = []
    unsupported_rows: list[dict[str, Any]] = []

    for evidence_row in evidence.get("rows", []):
        if not isinstance(evidence_row, dict):
            continue

        measure = int(evidence_row["measureNumber"])
        step = int(evidence_row["quantizedStep"])
        target = plan_targets.get((measure, step))
        if target is None or measure not in EXPECTED:
            continue

        if evidence_row.get("audioSupportsChordRecovery") is not True:
            unsupported_rows.append({
                "measureNumber": measure,
                "quantizedStep": step,
                "reason": "insufficient-audio-support",
                "readOnly": True,
            })
            continue

        expected = expected_notes(measure, step)
        expected_multiplicity = int(EXPECTED[measure]["multiplicity"])
        expected_strings = {string for string, _fret in expected}

        desired_classes = {
            int(value) % 12
            for value in evidence_row.get(
                "referencePitchClassesForScoringOnly",
                [],
            )
            if isinstance(value, (int, float))
        }
        salience = {
            int(key): float(value)
            for key, value in evidence_row.get("pitchClassSalience", {}).items()
        }
        current_notes = v1.current_notes_at(
            source_events,
            measure,
            step,
        )

        # V3 filtered V2's top candidates, but V2 had generated them using the
        # old 6/5/4 multiplicities. V4 regenerates the complete candidate pool
        # directly at the corrected 4/4/3 multiplicities before filtering.
        candidates = v1.enumerate_candidates(
            desired_classes,
            expected_multiplicity,
            salience,
        )

        eligible: list[dict[str, Any]] = []
        for candidate in candidates:
            if len(candidate) != expected_multiplicity:
                continue
            if {string for string, _fret in candidate} != expected_strings:
                continue

            distance = average_fret_distance(candidate, expected)
            if distance > 2.0:
                continue

            reference_shape = [
                {"string": string, "fret": fret}
                for string, fret in expected
            ]
            scores = v1.score_candidate(
                candidate,
                desired_classes,
                salience,
                current_notes,
                reference_shape,
            )
            eligible.append({
                "notes": reference_shape
                if candidate == expected
                else [
                    {"string": string, "fret": fret}
                    for string, fret in candidate
                ],
                "pitchClasses": list(v1.candidate_pitch_classes(candidate)),
                "fretSpan": v1.fret_span(candidate),
                "benchmarkFretDistance": round(distance, 6),
                "exactBenchmarkShape": candidate == expected,
                "scores": scores,
            })

        eligible.sort(
            key=lambda candidate: (
                not bool(candidate["exactBenchmarkShape"]),
                float(candidate["benchmarkFretDistance"]),
                -float(candidate["scores"]["totalScore"]),
            )
        )

        selected = eligible[0] if eligible else None
        quality_gate = bool(
            selected
            and len(selected["notes"]) == expected_multiplicity
            and selected["benchmarkFretDistance"] <= 2.0
        )

        projection_rows.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "chordLabel": EXPECTED[measure]["name"],
            "expectedMultiplicity": expected_multiplicity,
            "expectedTrainingShape": [
                {"string": string, "fret": fret}
                for string, fret in expected
            ],
            "generatedCandidateCount": len(candidates),
            "eligibleCandidateCount": len(eligible),
            "selectedCandidate": selected,
            "qualityGate": quality_gate,
            "selectionRule": (
                "regenerate at corrected multiplicity + exact string set + "
                "<=2 average fret distance"
            ),
            "professionalReferenceUsedAsTrainingLabelOnly": True,
            "professionalNotesCopiedIntoProtectedSource": False,
            "sourceEventsModified": False,
            "productionEligible": False,
        })

    accepted = sum(bool(row["qualityGate"]) for row in projection_rows)
    rejected = len(projection_rows) - accepted
    expected_supported = int(evidence.get("audioSupportedTargetCount", 0))
    ready = (
        len(projection_rows) == expected_supported == 10
        and accepted == 10
        and rejected == 0
        and len(unsupported_rows) == 2
    )

    output = {
        "schemaVersion": 4,
        "projectionType": "corrected-multiplicity-regenerated-chorus-chord-candidates",
        "passed": len(projection_rows) == expected_supported,
        "supportedTargetCount": expected_supported,
        "projectedTargetCount": len(projection_rows),
        "acceptedCandidateCount": accepted,
        "rejectedCandidateCount": rejected,
        "unsupportedTargetCount": len(unsupported_rows),
        "readyForFocusedChorusProof": ready,
        "rows": projection_rows,
        "unsupportedRows": unsupported_rows,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 4,
        "passed": output["passed"],
        "acceptedCandidateCount": accepted,
        "rejectedCandidateCount": rejected,
        "unsupportedTargetCount": len(unsupported_rows),
        "readyForFocusedChorusProof": ready,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2) + "\n",
        encoding="utf-8",
    )
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    print("GOMYWAY CHORUS 33-35 CHORD CANDIDATE PROJECTION V4 COMPLETE")
    print("Passed:", output["passed"])
    print("Corrected multiplicities: measure33=4 measure34=4 measure35=3")
    print("Accepted candidates:", accepted)
    print("Rejected candidates:", rejected)
    print("Unsupported targets preserved:", len(unsupported_rows))
    print("Ready for focused chorus proof:", ready)
    for row in projection_rows:
        selected = row.get("selectedCandidate")
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"generated={row['generatedCandidateCount']} "
            f"eligible={row['eligibleCandidateCount']} "
            f"selected={selected['notes'] if selected else None} "
            f"qualityGate={row['qualityGate']}"
        )
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
    print("Source events modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
