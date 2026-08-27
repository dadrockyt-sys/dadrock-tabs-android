#!/usr/bin/env python3
"""Stage-one V154 scorer: combined Guitar recognition + Bass recognition.

Generated data must already be frozen before this scorer is invoked. Professional
reference data is read only here, after generation, and is never used to modify
or select generated notes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

STEP_TOLERANCE = 0.50
GROSS_STEP_TOLERANCE = 2.00
EPSILON = 1e-9


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_ratio(num: int | float, den: int | float, *, empty: float = 1.0) -> float:
    return empty if den == 0 else float(num) / float(den)


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = safe_ratio(matched, generated)
    recall = safe_ratio(matched, reference)
    f1 = 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)
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


def normalize_note(note: Mapping[str, Any], *, label: str) -> dict[str, Any] | None:
    if bool(note.get("excludeFromScoring", False)):
        return None
    measure = int(note["measure"])
    step = float(note["step"])
    midi = int(note["midi"])
    if measure < 1 or not 0.0 <= step <= 15.999999:
        raise ValueError(f"invalid measure/step for {label}: {measure}/{step}")
    if not 0 <= midi <= 127:
        raise ValueError(f"invalid MIDI for {label}: {midi}")
    return {"measure": measure, "step": step, "midi": midi}


def normalize_notes(notes: Sequence[Mapping[str, Any]], *, label: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for note in notes:
        normalized = normalize_note(note, label=label)
        if normalized is not None:
            result.append(normalized)
    return result


def load_generated(payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    song = payload.get("song") or {}
    if str(song.get("artist", "")).strip().lower() != "lenny kravitz" or str(song.get("title", "")).strip().lower() != "are you gonna go my way":
        raise ValueError("generated song identity mismatch")
    safety = payload.get("safety") or {}
    if safety.get("referenceRead") is not False:
        raise ValueError("generated payload must prove referenceRead=false")
    if safety.get("humanCorrection") is not False:
        raise ValueError("generated payload must prove humanCorrection=false")
    streams = payload.get("streams")
    if not isinstance(streams, Mapping):
        raise ValueError("generated payload missing streams")
    guitar = streams.get("combinedGuitar")
    bass = streams.get("bass")
    if not isinstance(guitar, list) or not isinstance(bass, list):
        raise ValueError("generated streams combinedGuitar and bass must be lists")
    return normalize_notes(guitar, label="generated.combinedGuitar"), normalize_notes(bass, label="generated.bass")


def load_reference(payload: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    song = payload.get("song") or {}
    if str(song.get("artist", "")).strip().lower() != "lenny kravitz" or str(song.get("title", "")).strip().lower() != "are you gonna go my way":
        raise ValueError("reference song identity mismatch")
    auth = payload.get("referenceAuthorization") or {}
    if auth.get("userProvidedOrAuthorized") is not True or auth.get("privateScoringOnly") is not True:
        raise ValueError("reference authorization flags are not frozen for private scoring")
    parts = payload.get("parts")
    if not isinstance(parts, Mapping):
        raise ValueError("reference payload missing parts")
    rhythm_raw = parts.get("rhythm", [])
    lead_raw = parts.get("lead", [])
    bass_raw = parts.get("bass", [])
    if not all(isinstance(rows, list) for rows in (rhythm_raw, lead_raw, bass_raw)):
        raise ValueError("reference rhythm/lead/bass must be lists")
    rhythm = normalize_notes(rhythm_raw, label="reference.rhythm")
    lead = normalize_notes(lead_raw, label="reference.lead")
    bass = normalize_notes(bass_raw, label="reference.bass")
    return rhythm + lead, bass, {
        "rhythmIncluded": len(rhythm),
        "leadIncluded": len(lead),
        "bassIncluded": len(bass),
        "rhythmExcluded": len(rhythm_raw) - len(rhythm),
        "leadExcluded": len(lead_raw) - len(lead),
        "bassExcluded": len(bass_raw) - len(bass),
    }


def greedy_match(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]], tolerance: float) -> list[tuple[int, int, float]]:
    candidates: list[tuple[float, int, int]] = []
    for gi, g in enumerate(generated):
        for ri, r in enumerate(reference):
            if int(g["measure"]) != int(r["measure"]):
                continue
            if int(g["midi"]) != int(r["midi"]):
                continue
            delta = abs(float(g["step"]) - float(r["step"]))
            if delta <= tolerance + EPSILON:
                candidates.append((delta, gi, ri))
    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    used_g: set[int] = set()
    used_r: set[int] = set()
    pairs: list[tuple[int, int, float]] = []
    for delta, gi, ri in candidates:
        if gi in used_g or ri in used_r:
            continue
        used_g.add(gi)
        used_r.add(ri)
        pairs.append((gi, ri, delta))
    return pairs


def pitch_content_diagnostic(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    gc = Counter((int(n["measure"]), int(n["midi"])) for n in generated)
    rc = Counter((int(n["measure"]), int(n["midi"])) for n in reference)
    return prf(sum((gc & rc).values()), sum(gc.values()), sum(rc.values()))


def percentile(values: Sequence[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * q))
    return ordered[index]


def score_stream(generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    local_pairs = greedy_match(generated, reference, STEP_TOLERANCE)
    gross_pairs = greedy_match(generated, reference, GROSS_STEP_TOLERANCE)
    deltas = [delta for _, _, delta in local_pairs]
    return {
        "primaryTimingAwarePitch": prf(len(local_pairs), len(generated), len(reference)),
        "grossTimingAwarePitch": prf(len(gross_pairs), len(generated), len(reference)),
        "localTimingErrorSteps": {
            "median": percentile(deltas, 0.50),
            "p90": percentile(deltas, 0.90),
            "maximum": max(deltas) if deltas else None,
        },
        "diagnosticPitchContentByMeasure": pitch_content_diagnostic(generated, reference),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("generated_json", type=Path)
    ap.add_argument("reference_json", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"score output already exists: {args.output}")

    generated_payload = load_json(args.generated_json)
    reference_payload = load_json(args.reference_json)
    if not isinstance(generated_payload, Mapping) or not isinstance(reference_payload, Mapping):
        raise ValueError("generated/reference payloads must be objects")

    generated_guitar, generated_bass = load_generated(generated_payload)
    reference_guitar, reference_bass, reference_counts = load_reference(reference_payload)
    report = {
        "schema": "dadrock.tabs.v154.cpu-front-end-score.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "combinedGuitar": score_stream(generated_guitar, reference_guitar),
        "bass": score_stream(generated_bass, reference_bass),
        "referenceCounts": reference_counts,
        "gates": {
            "combinedGuitarTimingAwarePitchF1Target": 0.80,
            "bassTimingAwarePitchF1Target": 0.80,
            "primaryToleranceGridSteps": STEP_TOLERANCE,
            "grossToleranceGridSteps": GROSS_STEP_TOLERANCE,
        },
        "policy": {
            "combinedGuitarScoredBeforeRoleSplit": True,
            "measurePitchContentDiagnosticOnly": True,
            "scoringWritesNoCorrections": True,
            "postScoreRetuningOfSameGeneratedOutputForbidden": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
