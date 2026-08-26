from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_STRUCTURED_SHA256 = "18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8"
EXPECTED_IMAGE_SHA256 = "aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9"
EXPECTED_REFERENCE_SHA256 = "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac"
EXPECTED_TRACK_NAME = "Craig Ross | 1953 Gibson Les Paul Goldtop | Rhythm Guitar"
EXPECTED_TUNING = [64, 59, 55, 50, 45, 40]
EXPECTED_COUNTS = (113, 603, 946, 104)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def normalized_structured_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")


def validate_structured_source(part: dict[str, Any]) -> None:
    digest = sha256_bytes(normalized_structured_bytes(part))
    if digest != EXPECTED_STRUCTURED_SHA256:
        raise ValueError(f"structured source SHA mismatch: {digest}")
    if part.get("songId") != 243:
        raise ValueError("unexpected songId")
    if int(part.get("revisionId") or 0) != 7868948:
        raise ValueError("unexpected revisionId")
    if len(part.get("measures") or []) != 113:
        raise ValueError("unexpected measure count")
    if part.get("name") != EXPECTED_TRACK_NAME:
        raise ValueError("unexpected track name")
    if part.get("tuning") != EXPECTED_TUNING:
        raise ValueError(f"unexpected tuning {part.get('tuning')!r}")


def build_reference(part: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    validate_structured_source(part)
    tuning = part["tuning"]
    measures: list[dict[str, Any]] = []
    onset_count = 0
    note_count = 0
    populated_count = 0

    for measure_number, measure in enumerate(part["measures"], 1):
        by_step: dict[int, set[tuple[int, int, int]]] = {}
        marker = measure.get("marker")
        section = marker.get("text") if isinstance(marker, dict) else None

        for voice in measure.get("voices") or []:
            position = Fraction(0, 1)
            for beat in voice.get("beats") or []:
                step = max(0, min(15, int(round(float(position * 16)))))
                for note in beat.get("notes") or []:
                    if not isinstance(note, dict):
                        continue
                    if note.get("rest") or note.get("dead") or note.get("tie"):
                        continue
                    string_index = note.get("string")
                    fret = note.get("fret")
                    if (
                        isinstance(string_index, int)
                        and isinstance(fret, int)
                        and 0 <= string_index <= 5
                        and 0 <= fret <= 36
                    ):
                        midi = int(tuning[string_index]) + fret
                        by_step.setdefault(step, set()).add((string_index, fret, midi))
                duration = beat.get("duration") or [1, 4]
                position += Fraction(int(duration[0]), int(duration[1]))

        events: list[dict[str, Any]] = []
        for step in sorted(by_step):
            notes = [
                {"stringIndex": string_index, "fret": fret, "midi": midi}
                for string_index, fret, midi in sorted(by_step[step])
            ]
            if notes:
                events.append({"step": step, "notes": notes})
                onset_count += 1
                note_count += len(notes)

        if events:
            populated_count += 1
        row: dict[str, Any] = {"measure": measure_number, "events": events}
        if section:
            row["section"] = section
        measures.append(row)

    counts = {
        "measureCount": len(measures),
        "playableOnsetCount": onset_count,
        "playableNoteCount": note_count,
        "populatedMeasureCount": populated_count,
    }
    if tuple(counts.values()) != EXPECTED_COUNTS:
        raise ValueError(f"reference counts changed: {counts}")

    reference = {
        "schemaVersion": 1,
        "instrument": "rhythm",
        "holdout": True,
        "completeReference": True,
        "transcribedFromCompleteSource": True,
        "source": {
            "kind": "professional-human-tab",
            "title": "Are You Gonna Go My Way",
            "artist": "Lenny Kravitz",
            "provenance": "Exact scorer-only structured extraction of immutable human-written revision 7868948 corresponding to Professionalexample.jpg",
            "pageCount": 8,
            "sourceSha256": EXPECTED_IMAGE_SHA256,
            "completeSource": True,
            "sourceRevisionId": 7868948,
            "structuredSourceSha256": EXPECTED_STRUCTURED_SHA256,
        },
        "measureRange": {"firstMeasure": 1, "lastMeasure": 113, "measureCount": 113},
        "tempoBpm": 129,
        "timeSignature": {"beats": 4, "noteValue": 4},
        "stepsPerMeasure": 16,
        "tuning": ["E4", "B3", "G3", "D3", "A2", "E2"],
        "measures": measures,
    }
    return reference, counts


def serialize_reference(reference: dict[str, Any]) -> bytes:
    return (json.dumps(reference, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the exact V144 gold calibration reference from the verified structured source."
    )
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    source = json.loads(args.structured_source.read_text(encoding="utf-8"))
    reference, counts = build_reference(source)
    output_bytes = serialize_reference(reference)
    digest = sha256_bytes(output_bytes)
    if digest != EXPECTED_REFERENCE_SHA256:
        raise ValueError(f"constructed reference SHA mismatch: {digest}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output_bytes)

    report = {
        "schemaVersion": 14401,
        "classification": "v144-rhythm-gold-calibration-reference-build",
        "referenceRole": "gold-calibration-reference-not-unseen-holdout",
        "legacyReferenceFieldNote": "The exact historical reference bytes retain holdout=true for hash identity; V144 protocol usage is calibration-only.",
        "structuredSourceSha256": EXPECTED_STRUCTURED_SHA256,
        "professionalImageSha256": EXPECTED_IMAGE_SHA256,
        "referenceSha256": digest,
        **counts,
        "exactHistoricalReferenceIdentity": True,
        "v5Modified": False,
        "productionModified": False,
        "modalGpuInvoked": False,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
