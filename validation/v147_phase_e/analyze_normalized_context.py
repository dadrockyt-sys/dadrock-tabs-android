#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(HOLDOUT_DIR) not in sys.path:
    sys.path.insert(0, str(HOLDOUT_DIR))

from canonical import canonical_events, sha256_json  # noqa: E402
from modal.v147_phase_c_artifact_support import materialize_accepted_family  # noqa: E402

ACCEPTED_SHA = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
CANDIDATE_SHA = "ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77"
CANDIDATE_FILE_SHA = "c0215690d5bfd9d2d47b8784eee886e942fbd28c499f25c643635c45ff7a9636"
DECISIONS_FILE_SHA = "3ec6c42730bf571c29258eca131c4e32da257c1ac6073e5319073818e8ac49b9"
EXPECTED_CHANGED = 247


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_bin(midi: int) -> str:
    if midi <= 51:
        return "40-51"
    if midi <= 63:
        return "52-63"
    if midi <= 75:
        return "64-75"
    return "76-88"


def onset_bin(size: int) -> str:
    return str(size) if size <= 3 else "4+"


def group_rates(total: Counter[str], changed: Counter[str], overall_rate: float) -> list[dict[str, Any]]:
    rows = []
    for key in sorted(total):
        population = int(total[key])
        changes = int(changed[key])
        rate = changes / population if population else 0.0
        rows.append({
            "key": key,
            "population": population,
            "changed": changes,
            "changeRate": rate,
            "rateRatioVsOverall": rate / overall_rate if overall_rate else None,
        })
    return rows


def duplicate_midis(events: Sequence[Mapping[str, Any]]) -> set[int]:
    counts = Counter(int(row["midi"]) for row in events)
    return {midi for midi, count in counts.items() if count > 1}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v5", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--decisions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    if file_sha(args.candidate) != CANDIDATE_FILE_SHA or file_sha(args.decisions) != DECISIONS_FILE_SHA:
        raise ValueError("preserved input file identity mismatch")

    accepted = canonical_events(materialize_accepted_family(load(args.v5)))
    candidate = canonical_events(load(args.candidate).get("renderEvents") or [])
    decisions = load(args.decisions)
    if len(accepted) != 1144 or sha256_json(accepted) != ACCEPTED_SHA:
        raise ValueError("accepted baseline identity mismatch")
    if len(candidate) != 1144 or sha256_json(candidate) != CANDIDATE_SHA:
        raise ValueError("candidate identity mismatch")
    if not isinstance(decisions, list) or len(decisions) != 1144:
        raise ValueError("decision identity mismatch")

    before_by_index = {int(row["eventIndex"]): row for row in accepted}
    after_by_index = {int(row["eventIndex"]): row for row in candidate}
    decisions_by_index = {int(row["eventIndex"]): row for row in decisions}
    if set(before_by_index) != set(after_by_index) or set(before_by_index) != set(decisions_by_index):
        raise ValueError("event index sets differ")

    before_onsets: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    after_onsets: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in accepted:
        before_onsets[(int(row["measure"]), int(row["step"]))].append(row)
    for row in candidate:
        after_onsets[(int(row["measure"]), int(row["step"]))].append(row)

    total_register: Counter[str] = Counter()
    changed_register: Counter[str] = Counter()
    total_pitch_class: Counter[str] = Counter()
    changed_pitch_class: Counter[str] = Counter()
    total_string: Counter[str] = Counter()
    changed_string: Counter[str] = Counter()
    total_event_onset_size: Counter[str] = Counter()
    changed_event_onset_size: Counter[str] = Counter()
    changed_onsets: set[tuple[int, int]] = set()
    changed_count = 0

    for event_index, before in before_by_index.items():
        after = after_by_index[event_index]
        decision = decisions_by_index[event_index]
        onset = (int(before["measure"]), int(before["step"]))
        size_key = onset_bin(len(before_onsets[onset]))
        reg = register_bin(int(before["midi"]))
        pc = str(int(before["midi"]) % 12)
        string = str(int(before["stringIndex"]))
        total_register[reg] += 1
        total_pitch_class[pc] += 1
        total_string[string] += 1
        total_event_onset_size[size_key] += 1
        changed = int(after["midi"]) != int(before["midi"])
        if bool(decision.get("changed")) != changed:
            raise ValueError(f"decision mismatch event {event_index}")
        if changed:
            changed_count += 1
            changed_onsets.add(onset)
            changed_register[reg] += 1
            changed_pitch_class[pc] += 1
            changed_string[string] += 1
            changed_event_onset_size[size_key] += 1

    if changed_count != EXPECTED_CHANGED:
        raise ValueError(f"changed count mismatch {changed_count}")

    overall_event_rate = changed_count / len(accepted)
    total_onset_size: Counter[str] = Counter()
    changed_onset_size: Counter[str] = Counter()
    for onset, events in before_onsets.items():
        key = onset_bin(len(events))
        total_onset_size[key] += 1
        if onset in changed_onsets:
            changed_onset_size[key] += 1
    overall_onset_rate = len(changed_onsets) / len(before_onsets)

    collisions: list[dict[str, Any]] = []
    collision_cause: Counter[str] = Counter()
    collision_transition: Counter[str] = Counter()
    collision_direction: Counter[str] = Counter()
    for onset in sorted(changed_onsets):
        before_events = before_onsets[onset]
        after_events = after_onsets[onset]
        before_dupes = duplicate_midis(before_events)
        after_dupes = duplicate_midis(after_events)
        introduced = sorted(after_dupes - before_dupes)
        if not introduced:
            continue
        before_onset_by_index = {int(row["eventIndex"]): row for row in before_events}
        after_onset_by_index = {int(row["eventIndex"]): row for row in after_events}
        changed_rows = []
        changed_selected_midis: Counter[int] = Counter()
        unchanged_original_midis = {
            int(before_onset_by_index[index]["midi"])
            for index in before_onset_by_index
            if int(before_onset_by_index[index]["midi"]) == int(after_onset_by_index[index]["midi"])
        }
        for index in sorted(before_onset_by_index):
            before = before_onset_by_index[index]
            after = after_onset_by_index[index]
            if int(before["midi"]) == int(after["midi"]):
                continue
            original = int(before["midi"])
            selected = int(after["midi"])
            changed_selected_midis[selected] += 1
            direction = "up-one" if selected > original else "down-one"
            transition = f"{original % 12}->{selected % 12}"
            collision_direction[direction] += 1
            collision_transition[transition] += 1
            changed_rows.append({
                "eventIndex": index,
                "originalMidi": original,
                "selectedMidi": selected,
                "direction": direction,
                "pitchClassTransition": transition,
                "selectedEqualsUnchangedOnsetPitch": selected in unchanged_original_midis,
            })
        if any(row["selectedEqualsUnchangedOnsetPitch"] for row in changed_rows):
            cause = "changed-into-unchanged-existing-pitch"
        elif any(count > 1 for count in changed_selected_midis.values()):
            cause = "changed-events-converged"
        else:
            cause = "other-collision-mechanism"
        collision_cause[cause] += 1
        collisions.append({
            "measure": onset[0],
            "step": onset[1],
            "onsetSize": len(before_events),
            "introducedDuplicateMidis": introduced,
            "cause": cause,
            "changedEvents": changed_rows,
        })

    result = {
        "schema": "dadrock.tabs.v147.phase-e-normalized-context.result.v1",
        "classification": "reference-free-normalized-context-diagnostic-no-candidate-construction",
        "identities": {
            "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "acceptedEventSha256": ACCEPTED_SHA,
            "candidateEventSha256": CANDIDATE_SHA,
            "candidateFileSha256": CANDIDATE_FILE_SHA,
            "decisionsFileSha256": DECISIONS_FILE_SHA,
        },
        "overall": {
            "acceptedEventCount": len(accepted),
            "changedEventCount": changed_count,
            "eventChangeRate": overall_event_rate,
            "acceptedOnsetCount": len(before_onsets),
            "changedOnsetCount": len(changed_onsets),
            "onsetChangeRate": overall_onset_rate,
        },
        "eventRates": {
            "byOriginalRegister": group_rates(total_register, changed_register, overall_event_rate),
            "byOriginalPitchClass": group_rates(total_pitch_class, changed_pitch_class, overall_event_rate),
            "byOriginalStringIndex": group_rates(total_string, changed_string, overall_event_rate),
            "byAcceptedOnsetSize": group_rates(total_event_onset_size, changed_event_onset_size, overall_event_rate),
        },
        "onsetRates": {
            "byAcceptedOnsetSize": group_rates(total_onset_size, changed_onset_size, overall_onset_rate),
        },
        "collisionAnalysis": {
            "introducedPitchCollisionOnsetCount": len(collisions),
            "fractionOfChangedOnsets": len(collisions) / len(changed_onsets),
            "fractionOfPolyphonicChangedOnsets": len(collisions) / sum(1 for onset in changed_onsets if len(before_onsets[onset]) > 1),
            "causeCounts": dict(sorted(collision_cause.items())),
            "directionCounts": dict(sorted(collision_direction.items())),
            "pitchClassTransitions": [
                {"key": key, "count": count} for key, count in collision_transition.most_common()
            ],
            "onsets": collisions,
        },
        "interpretationBoundary": "Normalized descriptive rates only; no reference labels, threshold selection, candidate construction, or score-guided optimization.",
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
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def fmt_rows(rows: list[dict[str, Any]]) -> str:
        return ", ".join(
            f"{row['key']}: {row['changed']}/{row['population']} ({row['changeRate']*100:.1f}%, {row['rateRatioVsOverall']:.2f}x)"
            for row in rows
        )

    md = [
        "# V147 Phase E — Normalized Context Addendum",
        "",
        "Reference-free denominator analysis only; no Gold/reference or candidate construction.",
        "",
        f"- Overall changed-event rate: **{changed_count}/{len(accepted)} = {overall_event_rate*100:.2f}%**",
        f"- Overall changed-onset rate: **{len(changed_onsets)}/{len(before_onsets)} = {overall_onset_rate*100:.2f}%**",
        f"- By original register: {fmt_rows(result['eventRates']['byOriginalRegister'])}",
        f"- By original pitch class: {fmt_rows(result['eventRates']['byOriginalPitchClass'])}",
        f"- By original string: {fmt_rows(result['eventRates']['byOriginalStringIndex'])}",
        f"- By accepted onset size (events): {fmt_rows(result['eventRates']['byAcceptedOnsetSize'])}",
        f"- By accepted onset size (onsets): {fmt_rows(result['onsetRates']['byAcceptedOnsetSize'])}",
        "",
        "## Introduced pitch collisions",
        f"- Collision onsets: **{len(collisions)} / {len(changed_onsets)} changed onsets ({len(collisions)/len(changed_onsets)*100:.2f}%)**",
        f"- Collision fraction among polyphonic changed onsets: **{len(collisions)/sum(1 for onset in changed_onsets if len(before_onsets[onset]) > 1)*100:.2f}%**",
        f"- Causes: `{dict(sorted(collision_cause.items()))}`",
        f"- Directions: `{dict(sorted(collision_direction.items()))}`",
        f"- Collision pitch-class transitions: `{collision_transition.most_common()}`",
        "",
        "## Safety",
        "- Gold/reference/professional image: **NOT READ**",
        "- Audio/HPSS/CQT/Modal/GPU: **NOT USED**",
        "- Candidate construction/search/retuning: **NOT PERFORMED**",
    ]
    args.markdown.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({
        "overallEventChangeRate": overall_event_rate,
        "overallOnsetChangeRate": overall_onset_rate,
        "collisionOnsets": len(collisions),
        "collisionCauseCounts": dict(sorted(collision_cause.items())),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
