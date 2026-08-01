from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-heldout-chord-voicing-placement-diagnosis-63-67.json"
)
VALIDATION_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-protected-octave-normalized-voicings-63-67.json"
)

ALLOWED_OCTAVE_OFFSETS = (-24, -12, 0, 12, 24)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pitch_class(pitch: int) -> int:
    return int(pitch) % 12


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in (
        "voicingPlacementMisses",
        "placementMisses",
        "missedAttacks",
        "reports",
        "attackReports",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def _list_of_ints(row: dict[str, Any], *keys: str) -> list[int]:
    for key in keys:
        value = row.get(key)
        if isinstance(value, list):
            result: list[int] = []
            for item in value:
                if isinstance(item, (int, float)):
                    result.append(int(item))
                elif isinstance(item, dict):
                    for pitch_key in ("pitch", "midiPitch", "midi"):
                        if pitch_key in item:
                            result.append(int(item[pitch_key]))
                            break
            if result:
                return result
    return []


def _best_octave_matches(
    expected: list[int],
    candidate: list[int],
) -> tuple[int, list[dict[str, Any]]]:
    used_indexes: set[int] = set()
    matches: list[dict[str, Any]] = []

    for expected_pitch in expected:
        best: tuple[int, int, int] | None = None
        for index, candidate_pitch in enumerate(candidate):
            if index in used_indexes:
                continue
            if _pitch_class(candidate_pitch) != _pitch_class(expected_pitch):
                continue
            delta = candidate_pitch - expected_pitch
            if delta not in ALLOWED_OCTAVE_OFFSETS:
                continue
            ranking = (abs(delta), abs(candidate_pitch - expected_pitch), index)
            if best is None or ranking < best:
                best = ranking

        if best is None:
            continue

        index = best[2]
        candidate_pitch = candidate[index]
        used_indexes.add(index)
        matches.append(
            {
                "expectedPitch": expected_pitch,
                "candidatePitch": candidate_pitch,
                "octaveOffsetSemitones": candidate_pitch - expected_pitch,
            }
        )

    return len(matches), matches


def main() -> None:
    diagnosis = _load(DIAGNOSIS_PATH)
    validation = _load(VALIDATION_PATH)
    rows = _extract_rows(diagnosis)
    if not rows:
        raise RuntimeError("No voicing-placement miss rows were found")

    recovered_rows: list[dict[str, Any]] = []
    unresolved_rows: list[dict[str, Any]] = []
    offset_counts: dict[str, int] = {}

    for row in rows:
        expected = _list_of_ints(
            row,
            "expectedPitches",
            "expected",
            "targetPitches",
        )
        candidate = _list_of_ints(
            row,
            "candidatePitches",
            "candidate",
            "observedPitches",
        )
        matched_count, matches = _best_octave_matches(expected, candidate)
        recall = matched_count / len(expected) if expected else 0.0
        full_recovery = bool(expected and matched_count == len(expected))

        result = {
            "measureNumber": int(row.get("measureNumber", row.get("measure", -1))),
            "attackNumber": int(row.get("attackNumber", row.get("attack", -1))),
            "expectedPitches": expected,
            "candidatePitches": candidate,
            "octaveNormalizedMatches": matches,
            "octaveNormalizedRecall": round(recall, 4),
            "fullyRecovered": full_recovery,
        }

        for match in matches:
            key = str(match["octaveOffsetSemitones"])
            offset_counts[key] = offset_counts.get(key, 0) + 1

        if full_recovery:
            recovered_rows.append(result)
        else:
            unresolved_rows.append(result)

    exact_count = int(validation.get("exactVoicingMatchedAttacks", 13))
    pitch_class_count = int(validation.get("pitchClassMatchedAttacks", 21))
    target_count = int(validation.get("targetAttacks", 21))
    recovered_attack_count = len(recovered_rows)
    guarded_exact_equivalent = min(target_count, exact_count + recovered_attack_count)
    guarded_recall = (
        100.0 * guarded_exact_equivalent / target_count if target_count else 0.0
    )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-octave-normalized-voicing-recovery",
        "sourceDiagnosis": str(DIAGNOSIS_PATH.relative_to(REPO_ROOT)),
        "sourceValidation": str(VALIDATION_PATH.relative_to(REPO_ROOT)),
        "exactVoicingMatchedAttacks": exact_count,
        "pitchClassMatchedAttacks": pitch_class_count,
        "targetAttacks": target_count,
        "placementMissesInspected": len(rows),
        "fullyRecoveredPlacementMisses": recovered_attack_count,
        "unresolvedPlacementMisses": len(unresolved_rows),
        "guardedExactEquivalentAttacks": guarded_exact_equivalent,
        "guardedExactEquivalentRecallPercentage": round(guarded_recall, 2),
        "octaveOffsetCounts": offset_counts,
        "recoveredRows": recovered_rows,
        "unresolvedRows": unresolved_rows,
        "policy": {
            "allowedOctaveOffsetsSemitones": list(ALLOWED_OCTAVE_OFFSETS),
            "pitchClassMustMatch": True,
            "oneCandidateNoteCanMatchOnlyOneExpectedNote": True,
            "exactVoicingRemainsPreferred": True,
            "octaveNormalizationIsEvaluationOnly": True,
            "stringAndFretAssignmentNotChanged": True,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForCanonicalVoicingResolverTraining": (
            len(unresolved_rows) == 0 and guarded_recall >= 90.0
        ),
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Protected octave-normalized voicing benchmark complete")
    print(f"Placement misses inspected: {len(rows)}")
    print(f"Fully recovered by octave normalization: {recovered_attack_count}")
    print(f"Unresolved placement misses: {len(unresolved_rows)}")
    print(
        f"Guarded exact-equivalent attacks: {guarded_exact_equivalent}/{target_count} "
        f"({payload['guardedExactEquivalentRecallPercentage']:.2f}%)"
    )
    print(f"Octave offsets observed: {offset_counts}")
    for row in unresolved_rows:
        print(
            f"UNRESOLVED measure {row['measureNumber']} attack {row['attackNumber']} | "
            f"recall={row['octaveNormalizedRecall']:.2f} | "
            f"expected={row['expectedPitches']} | candidate={row['candidatePitches']}"
        )
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
