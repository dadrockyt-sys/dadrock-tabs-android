from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-baseline.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-voicing-miss-diagnosis.json"
)

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _name(midi_pitch: int) -> str:
    octave = midi_pitch // 12 - 1
    return f"{NOTE_NAMES[midi_pitch % 12]}{octave}"


def _nearest(candidate: list[int], target: int) -> dict[str, Any] | None:
    if not candidate:
        return None
    pitch = min(candidate, key=lambda value: abs(value - target))
    return {
        "pitch": pitch,
        "note": _name(pitch),
        "semitoneDelta": pitch - target,
        "absoluteSemitoneDelta": abs(pitch - target),
    }


def main() -> None:
    baseline = _load(BASELINE_PATH)
    reports: list[dict[str, Any]] = []
    missing_pitch_counts: dict[str, int] = {}
    neighbor_substitution_counts: dict[str, int] = {}

    for miss in baseline["missedAttacks"]:
        expected = [int(value) for value in miss.get("expectedPitches", [])]
        candidate = [int(value) for value in miss.get("candidatePitches", [])]
        expected_set = set(expected)
        candidate_set = set(candidate)

        exact = sorted(expected_set & candidate_set)
        missing = sorted(expected_set - candidate_set)
        extra = sorted(candidate_set - expected_set)

        missing_rows: list[dict[str, Any]] = []
        for pitch in missing:
            nearest = _nearest(candidate, pitch)
            row = {
                "pitch": pitch,
                "note": _name(pitch),
                "nearestCandidate": nearest,
                "samePitchClassPresent": any(
                    value % 12 == pitch % 12 for value in candidate
                ),
                "octaveEquivalentCandidates": [
                    {
                        "pitch": value,
                        "note": _name(value),
                        "octaveDelta": (value - pitch) // 12,
                    }
                    for value in candidate
                    if value % 12 == pitch % 12
                ],
            }
            missing_rows.append(row)
            key = f"{pitch}:{_name(pitch)}"
            missing_pitch_counts[key] = missing_pitch_counts.get(key, 0) + 1

            if nearest and nearest["absoluteSemitoneDelta"] <= 2:
                neighbor_key = (
                    f"{pitch}:{_name(pitch)}->"
                    f"{nearest['pitch']}:{nearest['note']}"
                )
                neighbor_substitution_counts[neighbor_key] = (
                    neighbor_substitution_counts.get(neighbor_key, 0) + 1
                )

        reports.append(
            {
                "measureNumber": miss["measureNumber"],
                "attackNumber": miss["attackNumber"],
                "chordLabels": miss["chordLabels"],
                "targetPhase": miss["targetPhase"],
                "timingDeltaSeconds": miss["timingDeltaSeconds"],
                "voicingRecall": miss["voicingRecall"],
                "expectedPitches": [
                    {"pitch": pitch, "note": _name(pitch)}
                    for pitch in expected
                ],
                "candidatePitches": [
                    {"pitch": pitch, "note": _name(pitch)}
                    for pitch in candidate
                ],
                "exactMatchedPitches": [
                    {"pitch": pitch, "note": _name(pitch)}
                    for pitch in exact
                ],
                "missingPitches": missing_rows,
                "extraCandidatePitches": [
                    {"pitch": pitch, "note": _name(pitch)}
                    for pitch in extra
                ],
                "classification": (
                    "octave-placement-problem"
                    if any(row["samePitchClassPresent"] for row in missing_rows)
                    else "pitch-extraction-or-grouping-problem"
                ),
            }
        )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-rhythm-chord-voicing-miss-diagnosis",
        "sourceBaseline": str(BASELINE_PATH.relative_to(REPO_ROOT)),
        "missedAttackCount": len(reports),
        "missingPitchCounts": dict(
            sorted(
                missing_pitch_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "neighborSubstitutionCounts": dict(
            sorted(
                neighbor_substitution_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ),
        "missReports": reports,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForTargetedChordRecoverySweep": True,
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional chord voicing-miss diagnosis complete")
    print(f"Missed attacks inspected: {len(reports)}")
    print(f"Missing pitch counts: {payload['missingPitchCounts']}")
    print(f"Neighbor substitutions: {payload['neighborSubstitutionCounts']}")

    for row in reports:
        missing_text = ", ".join(
            f"{item['note']} nearest={item['nearestCandidate']}"
            for item in row["missingPitches"]
        )
        exact_text = ", ".join(
            item["note"] for item in row["exactMatchedPitches"]
        ) or "none"
        candidate_text = ", ".join(
            item["note"] for item in row["candidatePitches"]
        ) or "none"
        print(
            f"MISS measure {row['measureNumber']:>2} attack {row['attackNumber']} | "
            f"exact={exact_text} | candidate={candidate_text} | "
            f"missing={missing_text} | classification={row['classification']}"
        )

    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
