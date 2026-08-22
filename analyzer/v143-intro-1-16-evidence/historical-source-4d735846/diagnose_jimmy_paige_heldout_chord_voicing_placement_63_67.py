from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-heldout-chord-voicing-placement-diagnosis-63-67.json"
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_attack_rows(payload: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(payload, dict):
        for key in ("measureReports", "measures", "reports"):
            value = payload.get(key)
            if isinstance(value, list):
                for measure in value:
                    if not isinstance(measure, dict):
                        continue
                    attacks = measure.get("attacks")
                    if isinstance(attacks, list):
                        for attack in attacks:
                            if isinstance(attack, dict):
                                row = dict(attack)
                                row.setdefault(
                                    "measureNumber",
                                    measure.get("measureNumber", measure.get("measure")),
                                )
                                rows.append(row)
                if rows:
                    return rows
        attacks = payload.get("attacks")
        if isinstance(attacks, list):
            rows.extend(item for item in attacks if isinstance(item, dict))
    return rows


def _value(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return default


def _as_pitch_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []
    result: list[int] = []
    for item in value:
        if isinstance(item, (int, float)):
            result.append(int(item))
        elif isinstance(item, dict):
            for key in ("pitch", "midiPitch", "midi"):
                if key in item:
                    result.append(int(item[key]))
                    break
    return result


def _pitch_class(pitch: int) -> int:
    return pitch % 12


def main() -> None:
    payload = _load(INPUT_PATH)
    rows = _iter_attack_rows(payload)
    if not rows:
        raise RuntimeError("Held-out validation JSON contains no attack-level rows")

    diagnosis_rows: list[dict[str, Any]] = []
    exact_pass_count = 0
    pitch_class_pass_count = 0

    for index, row in enumerate(rows, start=1):
        measure = int(_value(row, "measureNumber", "measure", default=-1))
        attack_number = int(_value(row, "attackNumber", "attack", default=index))
        expected = _as_pitch_list(
            _value(row, "expectedPitches", "targetPitches", default=[])
        )
        candidate = _as_pitch_list(
            _value(
                row,
                "candidatePitches",
                "observedPitches",
                "matchedPitches",
                default=[],
            )
        )

        exact_pass = bool(
            _value(row, "exactPass", "exactVoicingPassed", "exact", default=False)
        )
        pitch_class_pass = bool(
            _value(row, "pitchClassPass", "pitchClassPassed", default=False)
        )
        if not pitch_class_pass:
            expected_classes = {_pitch_class(pitch) for pitch in expected}
            candidate_classes = {_pitch_class(pitch) for pitch in candidate}
            pitch_class_pass = bool(
                expected_classes
                and expected_classes.issubset(candidate_classes)
            )

        if exact_pass:
            exact_pass_count += 1
        if pitch_class_pass:
            pitch_class_pass_count += 1

        if exact_pass or not pitch_class_pass:
            continue

        expected_by_class: dict[int, list[int]] = {}
        candidate_by_class: dict[int, list[int]] = {}
        for pitch in expected:
            expected_by_class.setdefault(_pitch_class(pitch), []).append(pitch)
        for pitch in candidate:
            candidate_by_class.setdefault(_pitch_class(pitch), []).append(pitch)

        octave_offsets: list[int] = []
        class_rows: list[dict[str, Any]] = []
        for pitch_class, expected_pitches in sorted(expected_by_class.items()):
            observed = candidate_by_class.get(pitch_class, [])
            pair_offsets: list[int] = []
            for expected_pitch in expected_pitches:
                if observed:
                    nearest = min(observed, key=lambda item: abs(item - expected_pitch))
                    pair_offsets.append(nearest - expected_pitch)
                    octave_offsets.append(nearest - expected_pitch)
            class_rows.append(
                {
                    "pitchClass": pitch_class,
                    "expectedPitches": sorted(expected_pitches),
                    "candidatePitches": sorted(observed),
                    "nearestOffsetsSemitones": pair_offsets,
                }
            )

        diagnosis_rows.append(
            {
                "measureNumber": measure,
                "attackNumber": attack_number,
                "expectedPitches": expected,
                "candidatePitches": candidate,
                "pitchClassRows": class_rows,
                "octaveOffsetsSemitones": octave_offsets,
                "allOffsetsAreOctaves": bool(
                    octave_offsets
                    and all(offset % 12 == 0 for offset in octave_offsets)
                ),
                "classification": "octave-or-string-placement-error",
            }
        )

    affected_measures = sorted(
        {row["measureNumber"] for row in diagnosis_rows if row["measureNumber"] > 0}
    )

    output = {
        "benchmarkVersion": 1,
        "benchmarkType": "held-out-exact-chord-voicing-placement-diagnosis",
        "sourceValidation": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "attackRowsInspected": len(rows),
        "exactPassCount": exact_pass_count,
        "pitchClassPassCount": pitch_class_pass_count,
        "voicingPlacementMissCount": len(diagnosis_rows),
        "affectedMeasures": affected_measures,
        "diagnosisRows": diagnosis_rows,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForProtectedVoicingPlacementSweep": len(diagnosis_rows) > 0,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Held-out chord voicing placement diagnosis complete")
    print(f"Attack rows inspected: {len(rows)}")
    print(f"Exact pass count: {exact_pass_count}")
    print(f"Pitch-class pass count: {pitch_class_pass_count}")
    print(f"Voicing placement misses: {len(diagnosis_rows)}")
    print(f"Affected measures: {affected_measures}")
    for row in diagnosis_rows:
        print(
            f"MISS measure {row['measureNumber']} attack {row['attackNumber']} | "
            f"expected={row['expectedPitches']} | "
            f"candidate={row['candidatePitches']} | "
            f"offsets={row['octaveOffsetsSemitones']} | "
            f"allOctaves={row['allOffsetsAreOctaves']}"
        )
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
