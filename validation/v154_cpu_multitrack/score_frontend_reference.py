#!/usr/bin/env python3
"""Stage-one V154 scorer: combined Guitar recognition + Bass recognition.

Generated data must already be frozen before this scorer is invoked. Professional
reference data is read only here, after generation, and is never used to modify
or select generated notes.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
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


def optimal_one_to_one_match(
    generated: Sequence[Mapping[str, Any]],
    reference: Sequence[Mapping[str, Any]],
    tolerance: float,
) -> list[tuple[int, int, float]]:
    """Maximize valid same-measure/same-MIDI matches, then minimize timing error.

    A nearest-delta-first greedy matcher can lose cardinality in ambiguous local
    neighborhoods. This dynamic program works independently inside each
    (measure, MIDI) group, sorts events by onset so input order cannot affect the
    result, maximizes one-to-one match count first, and minimizes total absolute
    timing error among maximum-cardinality solutions.
    """
    generated_groups: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
    reference_groups: dict[tuple[int, int], list[tuple[float, int]]] = defaultdict(list)
    for gi, note in enumerate(generated):
        generated_groups[(int(note["measure"]), int(note["midi"]))].append((float(note["step"]), gi))
    for ri, note in enumerate(reference):
        reference_groups[(int(note["measure"]), int(note["midi"]))].append((float(note["step"]), ri))

    pairs: list[tuple[int, int, float]] = []
    action_rank = {"match": 0, "skip_generated": 1, "skip_reference": 2}

    for key in sorted(set(generated_groups) & set(reference_groups)):
        generated_rows = sorted(generated_groups[key], key=lambda row: (row[0], row[1]))
        reference_rows = sorted(reference_groups[key], key=lambda row: (row[0], row[1]))
        n = len(generated_rows)
        m = len(reference_rows)
        match_count = [[0] * (m + 1) for _ in range(n + 1)]
        total_error = [[0.0] * (m + 1) for _ in range(n + 1)]
        action: list[list[str | None]] = [[None] * (m + 1) for _ in range(n + 1)]

        def better(candidate: tuple[int, float, str], best: tuple[int, float, str] | None) -> bool:
            if best is None:
                return True
            if candidate[0] != best[0]:
                return candidate[0] > best[0]
            if abs(candidate[1] - best[1]) > EPSILON:
                return candidate[1] < best[1]
            return action_rank[candidate[2]] < action_rank[best[2]]

        for i in range(n - 1, -1, -1):
            for j in range(m - 1, -1, -1):
                best: tuple[int, float, str] | None = None

                candidate = (match_count[i + 1][j], total_error[i + 1][j], "skip_generated")
                if better(candidate, best):
                    best = candidate

                candidate = (match_count[i][j + 1], total_error[i][j + 1], "skip_reference")
                if better(candidate, best):
                    best = candidate

                delta = abs(generated_rows[i][0] - reference_rows[j][0])
                if delta <= tolerance + EPSILON:
                    candidate = (
                        1 + match_count[i + 1][j + 1],
                        delta + total_error[i + 1][j + 1],
                        "match",
                    )
                    if better(candidate, best):
                        best = candidate

                assert best is not None
                match_count[i][j], total_error[i][j], action[i][j] = best

        i = 0
        j = 0
        while i < n and j < m:
            current = action[i][j]
            if current == "match":
                generated_step, gi = generated_rows[i]
                reference_step, ri = reference_rows[j]
                pairs.append((gi, ri, abs(generated_step - reference_step)))
                i += 1
                j += 1
            elif current == "skip_generated":
                i += 1
            elif current == "skip_reference":
                j += 1
            else:
                raise RuntimeError("matching dynamic program entered an invalid state")

    pairs.sort(
        key=lambda pair: (
            int(generated[pair[0]]["measure"]),
            int(generated[pair[0]]["midi"]),
            float(generated[pair[0]]["step"]),
            float(reference[pair[1]]["step"]),
            pair[0],
            pair[1],
        )
    )
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
    local_pairs = optimal_one_to_one_match(generated, reference, STEP_TOLERANCE)
    gross_pairs = optimal_one_to_one_match(generated, reference, GROSS_STEP_TOLERANCE)
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
            "matchingAlgorithm": "maximum-cardinality-then-minimum-total-absolute-timing-error-within-measure-midi",
            "matchingInputOrderInvariant": True,
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
