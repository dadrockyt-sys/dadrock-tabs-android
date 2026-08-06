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
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v2-manifest.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def load_v1_module() -> Any:
    spec = importlib.util.spec_from_file_location("gomyway_chord_projection_v1", V1_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load V1 chord projection helpers.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def unique_reference_shape(target: dict[str, Any]) -> list[dict[str, int]]:
    raw = target.get("referenceStringFretShapeForScoringOnly", [])
    unique: dict[tuple[int, int], dict[str, int]] = {}
    if isinstance(raw, list):
        for row in raw:
            if not isinstance(row, dict):
                continue
            try:
                string = int(row["string"])
                fret = int(row["fret"])
            except (KeyError, TypeError, ValueError):
                continue
            if 1 <= string <= 6 and 0 <= fret <= 24:
                unique[(string, fret)] = {"string": string, "fret": fret}
    return [unique[key] for key in sorted(unique)]


def open_string_count(candidate: tuple[tuple[int, int], ...]) -> int:
    return sum(1 for _string, fret in candidate if fret == 0)


def string_gap_count(candidate: tuple[tuple[int, int], ...]) -> int:
    strings = sorted(string for string, _fret in candidate)
    if len(strings) < 2:
        return 0
    return sum(max(0, right - left - 1) for left, right in zip(strings, strings[1:]))


def corrected_score(
    base_scores: dict[str, float],
    candidate: tuple[tuple[int, int], ...],
    expected_multiplicity: int,
    reference_shape: list[dict[str, int]],
) -> dict[str, float]:
    note_count_match = 1.0 if len(candidate) == expected_multiplicity else 0.0
    opens = open_string_count(candidate)
    gaps = string_gap_count(candidate)

    # Open strings are not forbidden, but implausible open-heavy shapes should lose.
    open_penalty = max(0.0, (opens - 2) * 0.08)
    gap_penalty = gaps * 0.06

    reference_notes = {
        (int(row["string"]), int(row["fret"]))
        for row in reference_shape
    }
    candidate_notes = set(candidate)
    exact_reference_overlap = (
        len(candidate_notes & reference_notes) / max(1, len(reference_notes))
    )

    total = (
        float(base_scores["totalScore"])
        + note_count_match * 0.18
        + exact_reference_overlap * 0.10
        - open_penalty
        - gap_penalty
    )

    return {
        **base_scores,
        "expectedMultiplicity": expected_multiplicity,
        "noteCountMatch": note_count_match,
        "openStringCount": opens,
        "stringGapCount": gaps,
        "exactReferenceOverlap": round(exact_reference_overlap, 6),
        "openStringPenalty": round(open_penalty, 6),
        "stringGapPenalty": round(gap_penalty, 6),
        "correctedTotalScore": round(total, 6),
    }


def main() -> None:
    v1 = load_v1_module()
    plan = load_json(PLAN_PATH)
    evidence = load_json(EVIDENCE_PATH)
    source = load_json(SOURCE_PATH)

    if evidence.get("passed") is not True:
        raise RuntimeError("Audio chord evidence is not green.")
    if evidence.get("readyForReadOnlyChordCandidateProjection") is not True:
        raise RuntimeError("Audio chord evidence is not ready for projection.")

    source_events = v1.source_rows(source)
    if len(source_events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(source_events)}.")

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
        quantized_step = int(evidence_row["quantizedStep"])
        target = plan_targets.get((measure, quantized_step))
        if target is None:
            continue

        if evidence_row.get("audioSupportsChordRecovery") is not True:
            unsupported_rows.append({
                "measureNumber": measure,
                "quantizedStep": quantized_step,
                "reason": "insufficient-audio-support",
                "readOnly": True,
            })
            continue

        reference_shape = unique_reference_shape(target)
        expected_multiplicity = len(reference_shape)
        if expected_multiplicity < 2:
            expected_multiplicity = max(2, int(target.get("targetAttackMultiplicity", 2)))

        desired_classes = {
            int(value) % 12
            for value in evidence_row.get("referencePitchClassesForScoringOnly", [])
            if isinstance(value, (int, float))
        }
        salience = {
            int(key): float(value)
            for key, value in evidence_row.get("pitchClassSalience", {}).items()
        }
        current_notes = v1.current_notes_at(source_events, measure, quantized_step)

        candidates = v1.enumerate_candidates(
            desired_classes,
            expected_multiplicity,
            salience,
        )

        ranked: list[dict[str, Any]] = []
        for candidate in candidates:
            base_scores = v1.score_candidate(
                candidate,
                desired_classes,
                salience,
                current_notes,
                reference_shape,
            )
            scores = corrected_score(
                base_scores,
                candidate,
                expected_multiplicity,
                reference_shape,
            )
            ranked.append({
                "notes": [
                    {"string": string, "fret": fret}
                    for string, fret in candidate
                ],
                "pitchClasses": list(v1.candidate_pitch_classes(candidate)),
                "fretSpan": v1.fret_span(candidate),
                "scores": scores,
            })

        ranked.sort(
            key=lambda row: row["scores"]["correctedTotalScore"],
            reverse=True,
        )
        ranked = ranked[:12]
        selected = ranked[0] if ranked else None

        selected_is_sane = bool(
            selected
            and len(selected["notes"]) == expected_multiplicity
            and selected["scores"]["noteCountMatch"] == 1.0
            and selected["scores"]["stringGapCount"] <= 1
            and selected["scores"]["openStringCount"] <= 3
        )

        projection_rows.append({
            "measureNumber": measure,
            "quantizedStep": quantized_step,
            "expectedMultiplicity": expected_multiplicity,
            "previousTargetMultiplicity": target.get("targetAttackMultiplicity"),
            "referenceShapeForScoringOnly": reference_shape,
            "currentSourceNotes": [
                {"string": string, "fret": fret}
                for string, fret in current_notes
            ],
            "candidateCount": len(ranked),
            "selectedCandidate": selected,
            "rankedCandidates": ranked,
            "selectionStatus": "read-only-candidate" if selected_is_sane else "rejected-by-quality-gate",
            "passesQualityGate": selected_is_sane,
            "professionalReferenceUsedForScoringOnly": True,
            "professionalNotesCopiedIntoOutput": False,
            "sourceEventsModified": False,
            "productionEligible": False,
        })

    accepted = [row for row in projection_rows if row["passesQualityGate"]]
    rejected = [row for row in projection_rows if not row["passesQualityGate"]]

    output = {
        "schemaVersion": 2,
        "projectionType": "corrected-multiplicity-audio-supported-playable-chord-candidates",
        "passed": len(projection_rows) == evidence.get("audioSupportedTargetCount"),
        "supportedTargetCount": evidence.get("audioSupportedTargetCount"),
        "projectedTargetCount": len(projection_rows),
        "acceptedCandidateCount": len(accepted),
        "rejectedCandidateCount": len(rejected),
        "unsupportedTargetCount": len(unsupported_rows),
        "readyForFocusedChorusProof": len(accepted) > 0 and not rejected,
        "rows": projection_rows,
        "unsupportedRows": unsupported_rows,
        "professionalReferenceUsedForScoringOnly": True,
        "professionalNotesCopiedIntoOutput": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 2,
        "passed": output["passed"],
        "acceptedCandidateCount": output["acceptedCandidateCount"],
        "rejectedCandidateCount": output["rejectedCandidateCount"],
        "unsupportedTargetCount": output["unsupportedTargetCount"],
        "readyForFocusedChorusProof": output["readyForFocusedChorusProof"],
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 CHORD CANDIDATE PROJECTION V2 COMPLETE")
    print("Passed:", output["passed"])
    print("Audio-supported targets:", output["supportedTargetCount"])
    print("Accepted candidates:", output["acceptedCandidateCount"])
    print("Rejected candidates:", output["rejectedCandidateCount"])
    print("Unsupported targets preserved:", output["unsupportedTargetCount"])
    print("Ready for focused chorus proof:", output["readyForFocusedChorusProof"])
    for row in projection_rows:
        selected = row.get("selectedCandidate")
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"expectedMultiplicity={row['expectedMultiplicity']} "
            f"selected={selected['notes'] if selected else None} "
            f"qualityGate={row['passesQualityGate']}"
        )
    print("Professional reference used for scoring only: True")
    print("Professional notes copied into output: False")
    print("Source events modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
