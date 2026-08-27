#!/usr/bin/env python3
"""Copyright-safe CPU scorer for DadRock multitrack guitar/bass transcription.

This module contains scoring logic only. It does not scrape, download, embed, or
redistribute any third-party tablature. Reference JSON must be supplied by the
user from a source they are authorized to use.

Primary evaluation is local/timing-aware note matching. Coarse per-measure pitch
content is retained as a diagnostic only and must not be used for event-level
candidate selection.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

STEP_TOLERANCE = 0.50
GROSS_STEP_TOLERANCE = 2.00
EPSILON = 1e-9
PARTS = ("rhythm", "lead", "bass")
GUITAR_PARTS = ("rhythm", "lead")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_ratio(num: int | float, den: int | float, *, empty: float = 1.0) -> float:
    return empty if den == 0 else float(num) / float(den)


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = safe_ratio(matched, generated)
    recall = safe_ratio(matched, reference)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "matched": matched,
        "generated": generated,
        "reference": reference,
        "falsePositive": generated - matched,
        "falseNegative": reference - matched,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def normalize_note(note: Mapping[str, Any], *, part: str) -> dict[str, Any]:
    measure = int(note["measure"])
    step = float(note["step"])
    midi = int(note["midi"])
    if measure < 1 or not 0.0 <= step <= 15.999999:
        raise ValueError(f"invalid measure/step for {part}: {measure}/{step}")
    if not 0 <= midi <= 127:
        raise ValueError(f"invalid MIDI for {part}: {midi}")
    string_index = note.get("stringIndex")
    fret = note.get("fret")
    if string_index is not None:
        string_index = int(string_index)
    if fret is not None:
        fret = int(fret)
    return {
        "part": part,
        "measure": measure,
        "step": step,
        "midi": midi,
        "stringIndex": string_index,
        "fret": fret,
    }


def load_parts(payload: Mapping[str, Any], *, label: str) -> dict[str, list[dict[str, Any]]]:
    song = payload.get("song")
    if not isinstance(song, Mapping):
        raise ValueError(f"{label} missing song metadata")
    title = str(song.get("title", "")).strip().lower()
    artist = str(song.get("artist", "")).strip().lower()
    if title != "are you gonna go my way" or artist != "lenny kravitz":
        raise ValueError(f"{label} song identity mismatch")
    raw_parts = payload.get("parts")
    if not isinstance(raw_parts, Mapping):
        raise ValueError(f"{label} missing parts object")
    result: dict[str, list[dict[str, Any]]] = {}
    for part in PARTS:
        raw_notes = raw_parts.get(part, [])
        if not isinstance(raw_notes, list):
            raise ValueError(f"{label} part {part} must be a list")
        result[part] = [normalize_note(note, part=part) for note in raw_notes]
    return result


def multiset_pitch_content(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gc = Counter((int(n["measure"]), int(n["midi"])) for n in generated)
    rc = Counter((int(n["measure"]), int(n["midi"])) for n in reference)
    matched = sum((gc & rc).values())
    return prf(matched, sum(gc.values()), sum(rc.values()))


def greedy_match(
    generated: Sequence[Mapping[str, Any]],
    reference: Sequence[Mapping[str, Any]],
    *,
    tolerance: float,
    require_position: bool = False,
) -> list[tuple[int, int]]:
    candidates: list[tuple[float, int, int]] = []
    for gi, g in enumerate(generated):
        for ri, r in enumerate(reference):
            if int(g["measure"]) != int(r["measure"]):
                continue
            if int(g["midi"]) != int(r["midi"]):
                continue
            if require_position:
                if g.get("stringIndex") is None or g.get("fret") is None:
                    continue
                if r.get("stringIndex") is None or r.get("fret") is None:
                    continue
                if int(g["stringIndex"]) != int(r["stringIndex"]) or int(g["fret"]) != int(r["fret"]):
                    continue
            delta = abs(float(g["step"]) - float(r["step"]))
            if delta <= tolerance + EPSILON:
                candidates.append((delta, gi, ri))
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    used_g: set[int] = set()
    used_r: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for _, gi, ri in candidates:
        if gi in used_g or ri in used_r:
            continue
        used_g.add(gi)
        used_r.add(ri)
        pairs.append((gi, ri))
    return pairs


def metric_from_pairs(pairs: Sequence[tuple[int, int]], generated: Sequence[Any], reference: Sequence[Any]) -> dict[str, Any]:
    return prf(len(pairs), len(generated), len(reference))


def score_note_stream(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    local_pairs = greedy_match(generated, reference, tolerance=STEP_TOLERANCE)
    gross_pairs = greedy_match(generated, reference, tolerance=GROSS_STEP_TOLERANCE)
    position_pairs = greedy_match(generated, reference, tolerance=STEP_TOLERANCE, require_position=True)
    has_reference_position = any(n.get("stringIndex") is not None and n.get("fret") is not None for n in reference)
    return {
        "primaryTimingAwarePitch": metric_from_pairs(local_pairs, generated, reference),
        "grossTimingAwarePitch": metric_from_pairs(gross_pairs, generated, reference),
        "positionTiming": metric_from_pairs(position_pairs, generated, reference) if has_reference_position else None,
        "diagnosticPitchContentByMeasure": multiset_pitch_content(generated, reference),
        "policy": {
            "primaryMetric": "timing-aware pitch F1 within ±0.5 grid step",
            "grossToleranceSteps": GROSS_STEP_TOLERANCE,
            "measurePitchContentDiagnosticOnly": True,
        },
    }


def flatten(parts: Mapping[str, Sequence[Mapping[str, Any]]], selected: Iterable[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for part in selected:
        rows.extend(dict(note) for note in parts.get(part, []))
    rows.sort(key=lambda n: (int(n["measure"]), float(n["step"]), int(n["midi"]), str(n["part"])))
    return rows


def score_role_assignment(
    generated_parts: Mapping[str, Sequence[Mapping[str, Any]]],
    reference_parts: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    # Match guitar notes ignoring role first; then ask whether matched notes landed in
    # the same professional role. This isolates recognition quality from role split.
    g_union = flatten(generated_parts, GUITAR_PARTS)
    r_union = flatten(reference_parts, GUITAR_PARTS)
    pairs = greedy_match(g_union, r_union, tolerance=STEP_TOLERANCE)
    correct = sum(1 for gi, ri in pairs if g_union[gi]["part"] == r_union[ri]["part"])
    return {
        "matchedGuitarNotesIgnoringRole": len(pairs),
        "correctRoleAssignmentsAmongMatched": correct,
        "roleAssignmentAccuracy": safe_ratio(correct, len(pairs), empty=0.0),
        "note": "Role accuracy is conditional on a timing-aware pitch match; it does not penalize acoustic recognition twice.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("generated_json", type=Path)
    ap.add_argument("reference_json", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    generated_payload = load_json(args.generated_json)
    reference_payload = load_json(args.reference_json)
    if not isinstance(generated_payload, Mapping) or not isinstance(reference_payload, Mapping):
        raise ValueError("generated/reference payloads must be JSON objects")

    generated = load_parts(generated_payload, label="generated")
    reference = load_parts(reference_payload, label="reference")

    report: dict[str, Any] = {
        "schema": "dadrock.tabs.v154.cpu-multitrack-reference-score.v1",
        "song": {"title": "Are You Gonna Go My Way", "artist": "Lenny Kravitz"},
        "referencePolicy": {
            "containsNoBundledThirdPartyTab": True,
            "referenceMustBeUserProvidedOrOtherwiseAuthorized": True,
            "candidateGenerationMayNotReadReference": True,
            "referenceReadOnlyAtScoringBoundary": True,
        },
        "parts": {},
    }
    for part in PARTS:
        report["parts"][part] = score_note_stream(generated[part], reference[part])

    generated_guitar = flatten(generated, GUITAR_PARTS)
    reference_guitar = flatten(reference, GUITAR_PARTS)
    report["combinedGuitar"] = score_note_stream(generated_guitar, reference_guitar)
    report["guitarRoleAssignment"] = score_role_assignment(generated, reference)
    report["allThreePartsUnion"] = score_note_stream(flatten(generated, PARTS), flatten(reference, PARTS))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
