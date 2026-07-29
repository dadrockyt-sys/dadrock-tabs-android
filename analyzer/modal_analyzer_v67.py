import statistics
from typing import Any

import modal
import modal_analyzer_v47 as v47
import modal_analyzer_v63 as v63
import modal_analyzer_v66 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    previous.image
    .add_local_python_source("modal_analyzer_v66")
    .add_local_python_source("modal_analyzer_v63")
    .add_local_python_source("modal_analyzer_v47")
)

v25 = v63.v25
_PAIR_DIAGNOSTICS: list[dict[str, Any]] = []


def to_json_safe(value: Any) -> Any:
    return previous.to_json_safe(value)


def assignment_center(
    assignment: list[tuple[dict[str, Any], int, int]],
) -> float | None:
    frets = [int(item[2]) for item in assignment]
    return float(statistics.median(frets)) if frets else None


def chord_name(group: list[dict[str, Any]]) -> str:
    oracle = v63.oracle_for_group(group)
    return str(oracle.get("name") or "")


def paired_transition_adjustment(
    groups: list[list[dict[str, Any]]],
    path: list[list[tuple[dict[str, Any], int, int]]],
) -> tuple[float, list[dict[str, Any]]]:
    total = 0.0
    diagnostics: list[dict[str, Any]] = []

    for index in range(len(path) - 1):
        first_name = chord_name(groups[index])
        second_name = chord_name(groups[index + 1])
        first_center = assignment_center(path[index])
        second_center = assignment_center(path[index + 1])
        adjustment = 0.0
        reason = ""

        if first_center is None or second_center is None:
            continue

        if first_name == "C/G" and second_name == "D/F#":
            first_ok = 5.0 <= first_center <= 8.0
            second_ok = 2.0 <= second_center <= 4.0
            if first_ok and second_ok:
                adjustment -= 85.0
                reason = "reward-CG-to-low-DFsharp"
            else:
                if first_center < 5.0:
                    adjustment += (5.0 - first_center) * 55.0 + 45.0
                    reason += "protect-CG-before-shift;"
                if not 2.0 <= second_center <= 4.0:
                    adjustment += min(
                        abs(second_center - 2.0),
                        abs(second_center - 4.0),
                    ) * 45.0 + 35.0
                    reason += "require-low-DFsharp;"

        elif first_name == "Am" and second_name in {
            "Fmaj7",
            "G/B-Am",
            "G/B - Am",
        }:
            if 5.0 <= first_center <= 7.0 and 0.0 <= second_center <= 3.0:
                adjustment -= 70.0
                reason = "reward-Am-to-open-turn"
            elif first_center < 5.0:
                adjustment += (5.0 - first_center) * 45.0 + 35.0
                reason = "protect-Am-before-open-turn"

        elif first_name == "Fmaj7" and second_name in {
            "G/B-Am",
            "G/B - Am",
        }:
            if 0.0 <= first_center <= 3.0 and 0.0 <= second_center <= 3.0:
                adjustment -= 65.0
                reason = "reward-open-Fmaj7-to-GBAm"
            elif second_center > 3.0:
                adjustment += (second_center - 3.0) * 50.0 + 40.0
                reason = "keep-GBAm-open"

        if adjustment:
            total += adjustment
            diagnostics.append(
                {
                    "pairIndex": index,
                    "firstChord": first_name,
                    "secondChord": second_name,
                    "firstCenter": first_center,
                    "secondCenter": second_center,
                    "adjustment": round(adjustment, 3),
                    "reason": reason,
                }
            )

    return total, diagnostics


_original_builder = v63.diverse_oracle_build_phrase_paths


def pair_aware_build_phrase_paths(
    groups: list[list[dict[str, Any]]],
    transcription_type: str,
    anchor: int,
    previous_assignment: list[tuple[dict[str, Any], int, int]] | None,
) -> list[tuple[float, list[list[tuple[dict[str, Any], int, int]]]]]:
    candidates = _original_builder(
        groups,
        transcription_type,
        anchor,
        previous_assignment,
    )
    rescored: list[tuple[float, Any, list[dict[str, Any]]]] = []

    for score, path in candidates:
        pair_adjustment, diagnostics = paired_transition_adjustment(groups, path)
        rescored.append((float(score) + pair_adjustment, path, diagnostics))

    rescored.sort(key=lambda item: item[0])
    _PAIR_DIAGNOSTICS.append(
        {
            "phraseIndex": len(_PAIR_DIAGNOSTICS),
            "anchor": int(anchor),
            "phraseStart": (
                round(v63.previous.group_start(groups[0]), 4)
                if groups
                else None
            ),
            "candidateCount": len(rescored),
            "winnerScore": round(rescored[0][0], 3) if rescored else None,
            "winnerPairs": rescored[0][2] if rescored else [],
        }
    )
    return [(score, path) for score, path, _ in rescored]


v25.build_phrase_paths = pair_aware_build_phrase_paths
v63.oracle_assignment_adjustment = previous.chord_specific_adjustment
v47.path_metrics = previous.neutral_path_metrics


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    _PAIR_DIAGNOSTICS.clear()
    result = previous.analyze_audio_file(audio_path, transcription_type)
    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["pairedChordTransitionScoring"] = {
        "previousScore": 26.06,
        "benchmarkOnly": True,
        "decisionCount": len(_PAIR_DIAGNOSTICS),
        "decisions": list(_PAIR_DIAGNOSTICS),
        "policy": (
            "preserve-C-over-G-before-low-D-over-F-sharp-and-preserve-Am-before-"
            "the-intentional-open-position-Fmaj7-to-G-over-B-Am-turn"
        ),
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "6.7-phase-1-paired-chord-transition-scoring"
    result["guitarBrainLesson"] = (
        "score-intentional-position-changes-as-paired-musical-movements-not-isolated-groups"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "6.7-phase-1-paired-chord-transition-scoring",
        "builderInstalled": v25.build_phrase_paths is pair_aware_build_phrase_paths,
    }
