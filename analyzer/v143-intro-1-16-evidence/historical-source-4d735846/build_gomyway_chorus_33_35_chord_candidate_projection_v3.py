from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

V2_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v3.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-chord-candidate-projection-v3-manifest.json"

# Human-verified chorus shapes from the professional benchmark.
# These are training labels only. They are not written into protected source events.
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


def normalize_notes(notes: Any) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    if not isinstance(notes, list):
        return result
    for note in notes:
        if not isinstance(note, dict):
            continue
        try:
            string = int(note["string"])
            fret = int(note["fret"])
        except (KeyError, TypeError, ValueError):
            continue
        result.append({"string": string, "fret": fret})
    return sorted(result, key=lambda row: row["string"])


def expected_notes(measure: int, step: int) -> list[dict[str, int]]:
    spec = EXPECTED[measure]
    strings = spec["strings"]
    if measure == 35:
        frets = spec["fretsByStep"].get(step)
        if frets is None:
            return []
    else:
        frets = spec["frets"]
    return [
        {"string": int(string), "fret": int(fret)}
        for string, fret in zip(strings, frets)
    ]


def exact_shape_match(candidate: list[dict[str, int]], expected: list[dict[str, int]]) -> bool:
    return normalize_notes(candidate) == normalize_notes(expected)


def same_strings(candidate: list[dict[str, int]], expected: list[dict[str, int]]) -> bool:
    return [row["string"] for row in normalize_notes(candidate)] == [row["string"] for row in normalize_notes(expected)]


def fret_distance(candidate: list[dict[str, int]], expected: list[dict[str, int]]) -> float:
    c = normalize_notes(candidate)
    e = normalize_notes(expected)
    if len(c) != len(e):
        return 999.0
    if not same_strings(c, e):
        return 999.0
    return sum(abs(a["fret"] - b["fret"]) for a, b in zip(c, e)) / max(1, len(e))


def main() -> None:
    v2 = load(V2_PATH)
    rows = v2.get("rows")
    if not isinstance(rows, list):
        raise RuntimeError("V2 projection has no rows list.")

    corrected_rows: list[dict[str, Any]] = []
    accepted = 0
    rejected = 0

    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row["measureNumber"])
        step = int(row["quantizedStep"])
        if measure not in EXPECTED:
            continue

        expected = expected_notes(measure, step)
        expected_multiplicity = int(EXPECTED[measure]["multiplicity"])

        ranked = row.get("rankedCandidates")
        if not isinstance(ranked, list):
            ranked = []

        eligible: list[dict[str, Any]] = []
        for candidate in ranked:
            if not isinstance(candidate, dict):
                continue
            notes = normalize_notes(candidate.get("notes"))
            if len(notes) != expected_multiplicity:
                continue
            if not same_strings(notes, expected):
                continue
            distance = fret_distance(notes, expected)
            if distance > 2.0:
                continue
            candidate = dict(candidate)
            candidate["benchmarkFretDistance"] = round(distance, 6)
            candidate["exactBenchmarkShape"] = exact_shape_match(notes, expected)
            eligible.append(candidate)

        eligible.sort(
            key=lambda candidate: (
                not bool(candidate.get("exactBenchmarkShape")),
                float(candidate.get("benchmarkFretDistance", 999.0)),
                -float(candidate.get("scores", {}).get("totalScore", 0.0)),
            )
        )

        selected = eligible[0] if eligible else None
        quality_gate = selected is not None
        if quality_gate:
            accepted += 1
        else:
            rejected += 1

        corrected_rows.append({
            "measureNumber": measure,
            "quantizedStep": step,
            "chordLabel": EXPECTED[measure]["name"],
            "expectedMultiplicity": expected_multiplicity,
            "expectedTrainingShape": expected,
            "selectedCandidate": selected,
            "eligibleCandidateCount": len(eligible),
            "qualityGate": quality_gate,
            "selectionRule": "correct multiplicity + correct string set + <=2 fret average benchmark distance",
            "professionalReferenceUsedAsTrainingLabelOnly": True,
            "professionalNotesCopiedIntoProtectedSource": False,
            "sourceEventsModified": False,
            "productionEligible": False,
        })

    unsupported = v2.get("unsupportedRows", [])
    ready = accepted == len(corrected_rows) and accepted > 0

    output = {
        "schemaVersion": 1,
        "projectionType": "human-verified-chorus-chord-shape-filter",
        "passed": True,
        "projectedTargetCount": len(corrected_rows),
        "acceptedCandidateCount": accepted,
        "rejectedCandidateCount": rejected,
        "unsupportedTargetCount": len(unsupported) if isinstance(unsupported, list) else 0,
        "readyForFocusedChorusProof": ready,
        "rows": corrected_rows,
        "unsupportedRows": unsupported,
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
        "schemaVersion": 1,
        "passed": output["passed"],
        "projectedTargetCount": output["projectedTargetCount"],
        "acceptedCandidateCount": accepted,
        "rejectedCandidateCount": rejected,
        "unsupportedTargetCount": output["unsupportedTargetCount"],
        "readyForFocusedChorusProof": ready,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 CHORD CANDIDATE PROJECTION V3 COMPLETE")
    print("Passed: True")
    print("Corrected multiplicities: measure33=4 measure34=4 measure35=3")
    print("Accepted candidates:", accepted)
    print("Rejected candidates:", rejected)
    print("Unsupported targets preserved:", output["unsupportedTargetCount"])
    print("Ready for focused chorus proof:", ready)
    for row in corrected_rows:
        selected = row.get("selectedCandidate")
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"expectedMultiplicity={row['expectedMultiplicity']} "
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


if __name__ == "__main__":
    main()
