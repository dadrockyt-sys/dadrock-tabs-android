#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HOLDOUT_DIR) not in sys.path:
    sys.path.insert(0, str(HOLDOUT_DIR))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import materialize_accepted_family  # noqa: E402

EXPECTED_ACCEPTED_EVENT_COUNT = 1144
EXPECTED_ACCEPTED_EVENT_SHA256 = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
EXPECTED_CANDIDATE_EVENT_COUNT = 1144
EXPECTED_CANDIDATE_EVENT_SHA256 = "ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77"
EXPECTED_CANDIDATE_FILE_SHA256 = "c0215690d5bfd9d2d47b8784eee886e942fbd28c499f25c643635c45ff7a9636"
EXPECTED_DECISIONS_FILE_SHA256 = "3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9"
EXPECTED_DECISION_COUNT = 1144
EXPECTED_CHANGED_COUNT = 247
EXPECTED_ARTIFACT_SUPPORT_BLOB = "f4278ffaacaca3f66baf7a3112e2af0f3bc387cf"
EXPECTED_PITCH_HYPOTHESIS_BLOB = "49bce8b968406bb0d61ab61394954ef8a8303eb7"
EXPECTED_CANONICAL_BLOB = "088d44827fb23e20d9aeeb4944a672989af5846c"

OCTAVE_WEIGHT = 0.25
MIN_ALT_FUNDAMENTAL_DB = 3.0
MIN_SCORE_MARGIN_DB = 3.0
MIN_FUNDAMENTAL_MARGIN_DB = 2.0
PROXIMITY_DB = (0.25, 0.5, 1.0, 2.0)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def quantiles(values: Sequence[float]) -> dict[str, float | None]:
    ordered = sorted(float(value) for value in values if math.isfinite(float(value)))
    if not ordered:
        return {key: None for key in ("min", "p10", "p25", "p50", "p75", "p90", "max", "mean")}

    def q(frac: float) -> float:
        if len(ordered) == 1:
            return ordered[0]
        pos = frac * (len(ordered) - 1)
        lo = int(math.floor(pos))
        hi = int(math.ceil(pos))
        if lo == hi:
            return ordered[lo]
        weight = pos - lo
        return ordered[lo] * (1.0 - weight) + ordered[hi] * weight

    return {
        "min": ordered[0],
        "p10": q(0.10),
        "p25": q(0.25),
        "p50": q(0.50),
        "p75": q(0.75),
        "p90": q(0.90),
        "max": ordered[-1],
        "mean": sum(ordered) / len(ordered),
    }


def histogram(values: Iterable[Any]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    return dict(sorted(counts.items(), key=lambda item: item[0]))


def numeric_bin(value: int) -> str:
    if value <= 51:
        return "40-51"
    if value <= 63:
        return "52-63"
    if value <= 75:
        return "64-75"
    return "76-88"


def onset_size_bin(size: int) -> str:
    return str(size) if size <= 3 else "4+"


def pitch_set(events: Sequence[Mapping[str, Any]]) -> list[int]:
    return sorted({int(event["midi"]) for event in events})


def duplicates(events: Sequence[Mapping[str, Any]], key: str) -> int:
    values = [int(event[key]) for event in events]
    return len(values) - len(set(values))


def sorted_counter(counter: Counter[str], limit: int | None = None) -> list[dict[str, Any]]:
    rows = [{"key": key, "count": count} for key, count in counter.most_common()]
    return rows if limit is None else rows[:limit]


def candidate_row(decision: Mapping[str, Any], midi: int) -> Mapping[str, Any]:
    rows = [row for row in decision.get("candidates", []) if int(row.get("midi")) == midi]
    if len(rows) != 1:
        raise ValueError(f"decision {decision.get('eventIndex')} lacks unique evidence row for MIDI {midi}")
    return rows[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v5", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    code_blobs = {
        "artifactSupport": git_blob("modal/v147_phase_c_artifact_support.py"),
        "pitchHypothesis": git_blob("modal/v147_pitch_hypothesis.py"),
        "canonicalAdapter": git_blob("validation/rhythm_holdout/canonical.py"),
    }
    expected_code = {
        "artifactSupport": EXPECTED_ARTIFACT_SUPPORT_BLOB,
        "pitchHypothesis": EXPECTED_PITCH_HYPOTHESIS_BLOB,
        "canonicalAdapter": EXPECTED_CANONICAL_BLOB,
    }
    if code_blobs != expected_code:
        raise ValueError(f"frozen code identity mismatch: {code_blobs}")

    candidate_bytes = args.candidate.read_bytes()
    decisions_bytes = args.decisions.read_bytes()
    candidate_file_sha = sha256_bytes(candidate_bytes)
    decisions_file_sha = sha256_bytes(decisions_bytes)
    if candidate_file_sha != EXPECTED_CANDIDATE_FILE_SHA256:
        raise ValueError(f"candidate file SHA mismatch: {candidate_file_sha}")
    if decisions_file_sha != EXPECTED_DECISIONS_FILE_SHA256:
        raise ValueError(f"decisions file SHA mismatch: {decisions_file_sha}")

    v5_payload = load_json(args.v5)
    accepted = canonical_events(materialize_accepted_family(v5_payload))
    accepted_sha = sha256_json(accepted)
    if len(accepted) != EXPECTED_ACCEPTED_EVENT_COUNT or accepted_sha != EXPECTED_ACCEPTED_EVENT_SHA256:
        raise ValueError("accepted family identity mismatch")

    candidate_payload = json.loads(candidate_bytes)
    candidate = canonical_events(candidate_payload.get("renderEvents") or [])
    candidate_sha = sha256_json(candidate)
    if len(candidate) != EXPECTED_CANDIDATE_EVENT_COUNT or candidate_sha != EXPECTED_CANDIDATE_EVENT_SHA256:
        raise ValueError("V147 candidate identity mismatch")

    decisions = json.loads(decisions_bytes)
    if not isinstance(decisions, list) or len(decisions) != EXPECTED_DECISION_COUNT:
        raise ValueError("decision cardinality mismatch")

    accepted_by_index = {int(row["eventIndex"]): row for row in accepted}
    candidate_by_index = {int(row["eventIndex"]): row for row in candidate}
    decision_by_index = {int(row["eventIndex"]): row for row in decisions}
    if len(accepted_by_index) != len(accepted) or len(candidate_by_index) != len(candidate) or len(decision_by_index) != len(decisions):
        raise ValueError("duplicate eventIndex detected")
    if set(accepted_by_index) != set(candidate_by_index) or set(accepted_by_index) != set(decision_by_index):
        raise ValueError("eventIndex sets differ")

    accepted_onsets: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    candidate_onsets: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    changed_by_onset: Counter[tuple[int, int]] = Counter()
    for row in accepted:
        accepted_onsets[(int(row["measure"]), int(row["step"]))].append(row)
    for row in candidate:
        candidate_onsets[(int(row["measure"]), int(row["step"]))].append(row)

    changed_rows: list[dict[str, Any]] = []
    direction_counter: Counter[str] = Counter()
    transition_counter: Counter[str] = Counter()
    string_transition_counter: Counter[str] = Counter()
    original_register_counter: Counter[str] = Counter()
    selected_register_counter: Counter[str] = Counter()
    onset_size_event_counter: Counter[str] = Counter()
    score_margin_excesses: list[float] = []
    fundamental_margin_excesses: list[float] = []
    alt_fundamental_excesses: list[float] = []
    nearest_gate_excesses: list[float] = []
    frame_counts: list[float] = []
    fret_moves: list[float] = []
    abs_fret_moves: list[float] = []
    string_moves: list[float] = []
    octave_bonus_values: list[float] = []
    octave_margin_contributions: list[float] = []
    octave_dependent_winner_count = 0
    same_string_count = 0
    changed_string_count = 0

    changed_count = 0
    for event_index in sorted(accepted_by_index):
        before = accepted_by_index[event_index]
        after = candidate_by_index[event_index]
        decision = decision_by_index[event_index]
        for key in ("measure", "step"):
            if int(decision[key]) != int(before[key]) or int(after[key]) != int(before[key]):
                raise ValueError(f"timing mismatch eventIndex={event_index}")
        if int(decision["originalMidi"]) != int(before["midi"]):
            raise ValueError(f"decision original MIDI mismatch eventIndex={event_index}")
        if int(decision["selectedMidi"]) != int(after["midi"]):
            raise ValueError(f"decision selected MIDI mismatch eventIndex={event_index}")

        delta = int(after["midi"]) - int(before["midi"])
        changed = delta != 0
        if bool(decision.get("changed")) != changed or int(decision.get("semitoneDelta") or 0) != delta:
            raise ValueError(f"decision changed/delta mismatch eventIndex={event_index}")
        if not changed:
            continue
        if delta not in (-1, 1) or str(decision.get("reason")) != "alternate-supported":
            raise ValueError(f"unexpected changed-event decision eventIndex={event_index}")

        changed_count += 1
        onset = (int(before["measure"]), int(before["step"]))
        changed_by_onset[onset] += 1
        onset_size = len(accepted_onsets[onset])
        onset_size_event_counter[onset_size_bin(onset_size)] += 1

        original_midi = int(before["midi"])
        selected_midi = int(after["midi"])
        original_evidence = candidate_row(decision, original_midi)
        selected_evidence = candidate_row(decision, selected_midi)
        score_margin = float(selected_evidence["scoreDb"]) - float(original_evidence["scoreDb"])
        fundamental_margin = float(selected_evidence["fundamentalDeltaDb"]) - float(original_evidence["fundamentalDeltaDb"])
        alt_fund_excess = float(selected_evidence["fundamentalDeltaDb"]) - MIN_ALT_FUNDAMENTAL_DB
        score_margin_excess = score_margin - MIN_SCORE_MARGIN_DB
        fundamental_margin_excess = fundamental_margin - MIN_FUNDAMENTAL_MARGIN_DB
        nearest_gate_excess = min(alt_fund_excess, score_margin_excess, fundamental_margin_excess)
        selected_octave_bonus = OCTAVE_WEIGHT * max(0.0, float(selected_evidence["octaveDeltaDb"]))
        original_octave_bonus = OCTAVE_WEIGHT * max(0.0, float(original_evidence["octaveDeltaDb"]))
        octave_margin_contribution = selected_octave_bonus - original_octave_bonus

        all_candidates = list(decision.get("candidates", []))
        max_fundamental = max(float(row["fundamentalDeltaDb"]) for row in all_candidates)
        winner_depends_on_octave = float(selected_evidence["fundamentalDeltaDb"]) < max_fundamental - 1e-9
        if winner_depends_on_octave:
            octave_dependent_winner_count += 1

        before_string = int(before["stringIndex"])
        after_string = int(after["stringIndex"])
        before_fret = int(before["fret"])
        after_fret = int(after["fret"])
        string_delta = after_string - before_string
        fret_delta = after_fret - before_fret
        if string_delta == 0:
            same_string_count += 1
        else:
            changed_string_count += 1

        direction = "up-one" if delta == 1 else "down-one"
        direction_counter[direction] += 1
        transition_counter[f"{original_midi % 12}->{selected_midi % 12}"] += 1
        string_transition_counter[f"{before_string}->{after_string}"] += 1
        original_register_counter[numeric_bin(original_midi)] += 1
        selected_register_counter[numeric_bin(selected_midi)] += 1
        score_margin_excesses.append(score_margin_excess)
        fundamental_margin_excesses.append(fundamental_margin_excess)
        alt_fundamental_excesses.append(alt_fund_excess)
        nearest_gate_excesses.append(nearest_gate_excess)
        frame_counts.append(float(len(decision.get("frameIndices", []))))
        fret_moves.append(float(fret_delta))
        abs_fret_moves.append(float(abs(fret_delta)))
        string_moves.append(float(string_delta))
        octave_bonus_values.append(selected_octave_bonus)
        octave_margin_contributions.append(octave_margin_contribution)

        changed_rows.append(
            {
                "eventIndex": event_index,
                "measure": int(before["measure"]),
                "step": int(before["step"]),
                "onsetSize": onset_size,
                "direction": direction,
                "originalMidi": original_midi,
                "selectedMidi": selected_midi,
                "originalPitchClass": original_midi % 12,
                "selectedPitchClass": selected_midi % 12,
                "originalStringIndex": before_string,
                "selectedStringIndex": after_string,
                "stringDelta": string_delta,
                "originalFret": before_fret,
                "selectedFret": after_fret,
                "fretDelta": fret_delta,
                "frameCount": len(decision.get("frameIndices", [])),
                "selectedFundamentalDeltaDb": float(selected_evidence["fundamentalDeltaDb"]),
                "originalFundamentalDeltaDb": float(original_evidence["fundamentalDeltaDb"]),
                "selectedOctaveDeltaDb": float(selected_evidence["octaveDeltaDb"]),
                "originalOctaveDeltaDb": float(original_evidence["octaveDeltaDb"]),
                "selectedScoreDb": float(selected_evidence["scoreDb"]),
                "originalScoreDb": float(original_evidence["scoreDb"]),
                "scoreMarginDb": score_margin,
                "fundamentalMarginDb": fundamental_margin,
                "alternateFundamentalGateExcessDb": alt_fund_excess,
                "scoreMarginGateExcessDb": score_margin_excess,
                "fundamentalMarginGateExcessDb": fundamental_margin_excess,
                "nearestGateExcessDb": nearest_gate_excess,
                "selectedOctaveBonusDb": selected_octave_bonus,
                "octaveMarginContributionDb": octave_margin_contribution,
                "winnerDependsOnOctaveBonus": winner_depends_on_octave,
            }
        )

    if changed_count != EXPECTED_CHANGED_COUNT:
        raise ValueError(f"changed count mismatch: {changed_count}")

    changed_onset_count = len(changed_by_onset)
    changed_onset_size_counter: Counter[str] = Counter()
    changed_notes_per_onset_counter: Counter[str] = Counter()
    pitch_cardinality_delta_counter: Counter[str] = Counter()
    pitch_collision_delta_counter: Counter[str] = Counter()
    string_collision_delta_counter: Counter[str] = Counter()
    introduced_pitch_collision_onsets = 0
    introduced_string_collision_onsets = 0
    polyphonic_changed_onsets = 0
    singleton_changed_onsets = 0

    onset_rows: list[dict[str, Any]] = []
    for onset, num_changed in sorted(changed_by_onset.items()):
        before_events = accepted_onsets[onset]
        after_events = candidate_onsets[onset]
        onset_size = len(before_events)
        changed_onset_size_counter[onset_size_bin(onset_size)] += 1
        changed_notes_per_onset_counter[str(num_changed) if num_changed <= 3 else "4+"] += 1
        if onset_size == 1:
            singleton_changed_onsets += 1
        else:
            polyphonic_changed_onsets += 1

        before_pitch_set = pitch_set(before_events)
        after_pitch_set = pitch_set(after_events)
        cardinality_delta = len(after_pitch_set) - len(before_pitch_set)
        before_pitch_duplicates = duplicates(before_events, "midi")
        after_pitch_duplicates = duplicates(after_events, "midi")
        pitch_collision_delta = after_pitch_duplicates - before_pitch_duplicates
        before_string_duplicates = duplicates(before_events, "stringIndex")
        after_string_duplicates = duplicates(after_events, "stringIndex")
        string_collision_delta = after_string_duplicates - before_string_duplicates
        pitch_cardinality_delta_counter[str(cardinality_delta)] += 1
        pitch_collision_delta_counter[str(pitch_collision_delta)] += 1
        string_collision_delta_counter[str(string_collision_delta)] += 1
        if pitch_collision_delta > 0:
            introduced_pitch_collision_onsets += 1
        if string_collision_delta > 0:
            introduced_string_collision_onsets += 1

        onset_rows.append(
            {
                "measure": onset[0],
                "step": onset[1],
                "onsetSize": onset_size,
                "changedNotes": num_changed,
                "beforePitchSet": before_pitch_set,
                "afterPitchSet": after_pitch_set,
                "pitchSetCardinalityDelta": cardinality_delta,
                "pitchCollisionDelta": pitch_collision_delta,
                "stringCollisionDelta": string_collision_delta,
            }
        )

    proximity_counts = {
        f"within{value:g}DbOfAnyGate": sum(1 for margin in nearest_gate_excesses if margin <= value + 1e-12)
        for value in PROXIMITY_DB
    }

    direction_stats: dict[str, Any] = {}
    for direction in ("down-one", "up-one"):
        subset = [row for row in changed_rows if row["direction"] == direction]
        direction_stats[direction] = {
            "count": len(subset),
            "nearestGateExcessDb": quantiles([float(row["nearestGateExcessDb"]) for row in subset]),
            "onsetSize": histogram(onset_size_bin(int(row["onsetSize"])) for row in subset),
            "originalRegister": histogram(numeric_bin(int(row["originalMidi"])) for row in subset),
            "octaveDependentWinnerCount": sum(1 for row in subset if row["winnerDependsOnOctaveBonus"]),
        }

    result = {
        "schema": "dadrock.tabs.v147.phase-e-reference-free-failure-analysis.result.v1",
        "classification": "reference-free-descriptive-diagnostic-no-candidate-construction",
        "identities": {
            "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "acceptedEventCount": len(accepted),
            "acceptedCanonicalEventSha256": accepted_sha,
            "candidateEventCount": len(candidate),
            "candidateCanonicalEventSha256": candidate_sha,
            "candidateFileSha256": candidate_file_sha,
            "decisionCount": len(decisions),
            "decisionsFileSha256": decisions_file_sha,
            "codeGitBlobs": code_blobs,
        },
        "changeSummary": {
            "changedEventCount": changed_count,
            "direction": dict(sorted(direction_counter.items())),
            "changedOnsetCount": changed_onset_count,
            "singletonChangedOnsets": singleton_changed_onsets,
            "polyphonicChangedOnsets": polyphonic_changed_onsets,
            "changedEventsByAcceptedOnsetSize": dict(sorted(onset_size_event_counter.items())),
            "changedOnsetsByAcceptedOnsetSize": dict(sorted(changed_onset_size_counter.items())),
            "changedNotesPerChangedOnset": dict(sorted(changed_notes_per_onset_counter.items())),
        },
        "pitchContext": {
            "originalRegister": dict(sorted(original_register_counter.items())),
            "selectedRegister": dict(sorted(selected_register_counter.items())),
            "pitchClassTransitions": sorted_counter(transition_counter),
            "topPitchClassTransitions": sorted_counter(transition_counter, 12),
            "pitchSetCardinalityDeltaByChangedOnset": dict(sorted(pitch_cardinality_delta_counter.items())),
            "pitchCollisionDeltaByChangedOnset": dict(sorted(pitch_collision_delta_counter.items())),
            "introducedPitchCollisionOnsets": introduced_pitch_collision_onsets,
        },
        "fingeringContext": {
            "sameStringChangedEvents": same_string_count,
            "differentStringChangedEvents": changed_string_count,
            "stringTransitions": sorted_counter(string_transition_counter),
            "fretDelta": quantiles(fret_moves),
            "absoluteFretDelta": quantiles(abs_fret_moves),
            "stringDelta": quantiles(string_moves),
            "stringCollisionDeltaByChangedOnset": dict(sorted(string_collision_delta_counter.items())),
            "introducedStringCollisionOnsets": introduced_string_collision_onsets,
        },
        "evidenceContext": {
            "frozenConstants": {
                "octaveWeight": OCTAVE_WEIGHT,
                "minimumAlternateFundamentalDb": MIN_ALT_FUNDAMENTAL_DB,
                "minimumScoreMarginDb": MIN_SCORE_MARGIN_DB,
                "minimumFundamentalMarginDb": MIN_FUNDAMENTAL_MARGIN_DB,
            },
            "alternateFundamentalGateExcessDb": quantiles(alt_fundamental_excesses),
            "scoreMarginGateExcessDb": quantiles(score_margin_excesses),
            "fundamentalMarginGateExcessDb": quantiles(fundamental_margin_excesses),
            "nearestGateExcessDb": quantiles(nearest_gate_excesses),
            "fixedGateProximityCounts": proximity_counts,
            "frameCount": quantiles(frame_counts),
            "selectedOctaveBonusDb": quantiles(octave_bonus_values),
            "octaveMarginContributionDb": quantiles(octave_margin_contributions),
            "octaveBonusDependentWinnerCount": octave_dependent_winner_count,
            "octaveBonusDependentWinnerFraction": octave_dependent_winner_count / changed_count,
            "byDirection": direction_stats,
        },
        "changedEvents": changed_rows,
        "changedOnsets": onset_rows,
        "interpretationBoundary": "Descriptive reference-free mechanism evidence only. No per-event correctness labels, threshold tuning, alternate candidate construction, or Gold-derived optimization is present.",
        "safety": {
            "professionalImageRead": False,
            "goldReferenceRead": False,
            "referenceScorerInvoked": False,
            "audioReadOrDecoded": False,
            "hpssCqtRecomputed": False,
            "modalGpuUsed": False,
            "candidateConstructed": False,
            "candidateSearchRun": False,
            "thresholdRetuned": False,
            "mainModified": False,
            "productionModified": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    q = result["evidenceContext"]["nearestGateExcessDb"]
    md = [
        "# V147 Phase E — Reference-Free Failure Analysis",
        "",
        "This is descriptive mechanism analysis only. It does not open Gold/reference content and does not construct a new candidate.",
        "",
        "## Immutable identities",
        f"- Accepted family #10: {len(accepted)} events / `{accepted_sha}`",
        f"- V147 candidate: {len(candidate)} events / `{candidate_sha}`",
        f"- Preserved decisions: {len(decisions)} rows / file SHA256 `{decisions_file_sha}`",
        "",
        "## Change topology",
        f"- Changed events: **{changed_count}** ({direction_counter['down-one']} down-one / {direction_counter['up-one']} up-one)",
        f"- Changed onsets: **{changed_onset_count}**",
        f"- Singleton changed onsets: **{singleton_changed_onsets}**",
        f"- Polyphonic changed onsets: **{polyphonic_changed_onsets}**",
        f"- Changed events by accepted onset size: `{dict(sorted(onset_size_event_counter.items()))}`",
        f"- Changed notes per changed onset: `{dict(sorted(changed_notes_per_onset_counter.items()))}`",
        "",
        "## Structural effects",
        f"- Pitch-collision onsets introduced: **{introduced_pitch_collision_onsets}**",
        f"- String-collision onsets introduced: **{introduced_string_collision_onsets}**",
        f"- Same-string changed events: **{same_string_count}**; different-string changed events: **{changed_string_count}**",
        "",
        "## Frozen evidence margins",
        f"- Nearest decision-gate excess median: **{q['p50']:.3f} dB**",
        f"- Nearest decision-gate excess p10/p90: **{q['p10']:.3f} / {q['p90']:.3f} dB**",
        f"- Within 0.5 dB of at least one frozen gate: **{proximity_counts['within0.5DbOfAnyGate']} / {changed_count}**",
        f"- Within 1.0 dB of at least one frozen gate: **{proximity_counts['within1DbOfAnyGate']} / {changed_count}**",
        f"- Composite winners that were not fundamental-only winners: **{octave_dependent_winner_count} / {changed_count}**",
        "",
        "## Safety",
        "- Gold/reference read: **NO**",
        "- Audio read/decode or HPSS/CQT recompute: **NO**",
        "- Modal/L4/GPU: **NO**",
        "- Candidate construction/search/retuning: **NO**",
        "- main/Production modification: **NO**",
    ]
    args.markdown.write_text("\n".join(md) + "\n", encoding="utf-8")

    print(json.dumps({
        "changedEventCount": changed_count,
        "changedOnsetCount": changed_onset_count,
        "polyphonicChangedOnsets": polyphonic_changed_onsets,
        "singletonChangedOnsets": singleton_changed_onsets,
        "nearGateWithin0_5Db": proximity_counts["within0.5DbOfAnyGate"],
        "nearGateWithin1Db": proximity_counts["within1DbOfAnyGate"],
        "octaveBonusDependentWinnerCount": octave_dependent_winner_count,
        "sameStringChangedEvents": same_string_count,
        "differentStringChangedEvents": changed_string_count,
        "introducedPitchCollisionOnsets": introduced_pitch_collision_onsets,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
