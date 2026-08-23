#!/usr/bin/env python3
"""Verify that the professional Rhythm holdout is a complete scorer-only source.

This validator is intentionally downstream of the freeze/PDF identity gate. It refuses
partial screenshots, non-contiguous measure coverage, duplicate note identities, and
incomplete source provenance. It never writes analyzer/runtime output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_pre_reference_gate(freeze_dir: Path) -> Mapping[str, Any]:
    manifest = load_json(freeze_dir / "rhythm-freeze-manifest.json")
    if not isinstance(manifest, Mapping):
        raise ValueError("freeze manifest must be an object")

    required = {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "v143RuntimeSafetyVerified": True,
        "referenceOpenedDuringFreeze": False,
        "pdfFidelityVerified": True,
    }
    for key, expected in required.items():
        if manifest.get(key) is not expected:
            raise ValueError(f"pre-reference gate failed: {key}={manifest.get(key)!r}")

    event_hash = str(manifest.get("eventSha256") or "")
    pdf_hash = str(manifest.get("pdfEventSha256") or "")
    if len(event_hash) != 64 or pdf_hash != event_hash:
        raise ValueError("frozen/PDF event hashes are not identical")
    if float(manifest.get("pdfEventFidelity", 0.0)) != 1.0:
        raise ValueError("PDF event fidelity must equal 1.0 before reference access")
    return manifest


def validate_reference(reference: Any) -> dict[str, Any]:
    if not isinstance(reference, Mapping):
        raise ValueError("reference must be an object")
    if reference.get("schemaVersion") != 1:
        raise ValueError("unsupported reference schemaVersion")
    if reference.get("instrument") != "rhythm":
        raise ValueError("reference instrument must be rhythm")
    if reference.get("holdout") is not True:
        raise ValueError("reference must be marked holdout=true")
    if reference.get("completeReference") is not True:
        raise ValueError("partial reference cannot authorize final scoring")
    if reference.get("transcribedFromCompleteSource") is not True:
        raise ValueError("reference must be transcribed from the complete source")
    if reference.get("stepsPerMeasure") != 16:
        raise ValueError("reference must use the 16-step V143 measure grid")

    source = reference.get("source")
    if not isinstance(source, Mapping):
        raise ValueError("reference source metadata is required")
    if source.get("kind") != "professional-human-tab":
        raise ValueError("reference source must be a professional human-written tab")
    if source.get("completeSource") is not True:
        raise ValueError("reference source must be explicitly complete")
    if not str(source.get("provenance") or "").strip():
        raise ValueError("reference provenance is required")
    if int(source.get("pageCount") or 0) < 1:
        raise ValueError("reference source pageCount must be positive")
    source_hash = str(source.get("sourceSha256") or "").lower()
    if len(source_hash) != 64 or any(c not in "0123456789abcdef" for c in source_hash):
        raise ValueError("reference sourceSha256 must be lowercase SHA-256 hex")

    measure_range = reference.get("measureRange")
    if not isinstance(measure_range, Mapping):
        raise ValueError("measureRange is required")
    first_measure = int(measure_range.get("firstMeasure") or 0)
    last_measure = int(measure_range.get("lastMeasure") or 0)
    measure_count = int(measure_range.get("measureCount") or 0)
    if first_measure < 1 or last_measure < first_measure:
        raise ValueError("invalid reference measureRange")
    expected_count = last_measure - first_measure + 1
    if measure_count != expected_count:
        raise ValueError(
            f"measureRange measureCount={measure_count} does not equal contiguous range size {expected_count}"
        )

    measures = reference.get("measures")
    if not isinstance(measures, list) or len(measures) != measure_count:
        raise ValueError(
            f"reference must contain exactly {measure_count} declared measures"
        )

    expected_numbers = list(range(first_measure, last_measure + 1))
    actual_numbers: list[int] = []
    playable_note_count = 0
    rest_onset_count = 0
    technique_label_count = 0

    for measure_object in measures:
        if not isinstance(measure_object, Mapping):
            raise ValueError("each reference measure must be an object")
        measure = int(measure_object.get("measure") or 0)
        actual_numbers.append(measure)
        events = measure_object.get("events")
        if not isinstance(events, list):
            raise ValueError(f"reference measure {measure} events must be an array")

        seen_onsets: set[int] = set()
        for onset in events:
            if not isinstance(onset, Mapping):
                raise ValueError(f"reference measure {measure} onset must be an object")
            step = int(onset.get("step"))
            if not 0 <= step <= 15:
                raise ValueError(f"reference measure {measure} has invalid step {step}")
            if step in seen_onsets:
                raise ValueError(
                    f"reference measure {measure} has duplicate onset object at step {step}; combine chord notes into one onset"
                )
            seen_onsets.add(step)

            notes = onset.get("notes")
            if not isinstance(notes, list):
                raise ValueError(f"reference measure {measure} step {step} notes must be an array")
            if bool(onset.get("rest", False)):
                rest_onset_count += 1
            technique_label_count += len(onset.get("techniques") or [])

            note_signatures: set[tuple[int, int, int]] = set()
            for note in notes:
                if not isinstance(note, Mapping):
                    raise ValueError("reference note must be an object")
                string_index = int(note.get("stringIndex"))
                fret = int(note.get("fret"))
                midi = int(note.get("midi"))
                if string_index not in OPEN_MIDI_BY_STRING_INDEX:
                    raise ValueError(
                        f"reference measure {measure} step {step} has invalid stringIndex {string_index}"
                    )
                if not 0 <= fret <= 36:
                    raise ValueError(
                        f"reference measure {measure} step {step} has invalid fret {fret}"
                    )
                expected_midi = OPEN_MIDI_BY_STRING_INDEX[string_index] + fret
                if midi != expected_midi:
                    raise ValueError(
                        f"reference pitch-position mismatch measure={measure} step={step}: "
                        f"stringIndex={string_index} fret={fret} midi={midi} expected={expected_midi}"
                    )
                signature = (string_index, fret, midi)
                if signature in note_signatures:
                    raise ValueError(
                        f"duplicate reference note at measure={measure} step={step}: {signature}"
                    )
                note_signatures.add(signature)
                playable_note_count += 1
                technique_label_count += len(note.get("techniques") or [])

    if actual_numbers != expected_numbers:
        raise ValueError(
            "reference measures must be contiguous, ordered, and exactly match measureRange"
        )
    if playable_note_count < 1:
        raise ValueError("complete professional reference contains no playable notes")

    return {
        "schemaVersion": 2,
        "instrument": "rhythm",
        "referenceComplete": True,
        "sourceComplete": True,
        "sourceSha256": source_hash,
        "sourcePageCount": int(source["pageCount"]),
        "firstMeasure": first_measure,
        "lastMeasure": last_measure,
        "measureCount": measure_count,
        "playableNoteCount": playable_note_count,
        "restOnsetCount": rest_onset_count,
        "techniqueLabelCount": technique_label_count,
        "contiguousMeasureCoverage": True,
        "pitchPositionConsistency": True,
        "duplicateOnsets": 0,
        "duplicateNotes": 0,
        "passed": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument("reference_json", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    freeze_dir = args.freeze_dir.resolve()
    reference_path = args.reference_json.resolve()
    reference_root = (Path(__file__).resolve().parent / "reference").resolve()
    if not (reference_path == reference_root or reference_root in reference_path.parents):
        raise ValueError("professional reference must live under validation/rhythm_holdout/reference")

    # Safety/PDF identity are verified before opening the professional reference.
    manifest = require_pre_reference_gate(freeze_dir)

    reference_bytes = reference_path.read_bytes()
    reference_json_sha256 = hashlib.sha256(reference_bytes).hexdigest()
    reference = json.loads(reference_bytes.decode("utf-8"))
    report = validate_reference(reference)
    report.update(
        {
            "referenceOpenedOnlyAfterFreezeValidation": True,
            "referenceJsonSha256": reference_json_sha256,
            "frozenEventSha256": manifest["eventSha256"],
            "pdfEventSha256": manifest["pdfEventSha256"],
            "pdfEventFidelity": manifest["pdfEventFidelity"],
            "professionalReferenceUsedByAnalyzer": False,
            "referenceRuntimeInputUsed": False,
            "runtimeLabelsRequired": False,
            "v143RuntimeSafetyVerified": True,
        }
    )

    output_path = (
        args.output.resolve()
        if args.output
        else freeze_dir / "rhythm-reference-completeness.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
