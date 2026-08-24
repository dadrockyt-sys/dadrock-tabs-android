from __future__ import annotations

import hashlib
import json
import math
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from v143_rhythm_guitar_note_mapper import resolve_joint_chord_voicing

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
RETIRED_EVENT_SHA256 = "a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb"
HARMONIC_INTERVALS = {12, 19, 24, 28, 31, 36}
POSITIVE_ATTACK_FLOOR = 0.0
POSITIVE_BODY_FLOOR = -0.25
LEGATO_TYPES = {"hammer-on", "pull-off", "slide-up", "slide-down"}


def canonical_sha(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _tier(steps: int) -> str:
    if steps == 1:
        return "short"
    if steps <= 2:
        return "medium"
    return "long"


def _duration_steps(duration: float, tempo: float) -> int:
    step = 60.0 / float(tempo) / 4.0
    return max(1, int(math.floor(float(duration) / step + 0.5)))


def _strongest(hypotheses: list[list[Any]]) -> int | None:
    positive = [item for item in hypotheses if float(item[1]) > POSITIVE_ATTACK_FLOOR and float(item[2]) > POSITIVE_BODY_FLOOR]
    if not positive:
        return None
    return int(max(positive, key=lambda item: (float(item[4]), float(item[1]), -int(item[0])))[0])


def reconstruct(evidence: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    provenance = evidence.get("provenance") or {}
    if provenance.get("sourceAudioSha256") != APPROVED_AUDIO_SHA256:
        raise RuntimeError("frozen evidence source audio changed")
    if provenance.get("retiredFrozenEventSha256") != RETIRED_EVENT_SHA256:
        raise RuntimeError("frozen evidence retired identity changed")
    if provenance.get("referenceFree") is not True or provenance.get("professionalReferenceUsed") is not False:
        raise RuntimeError("frozen evidence safety provenance changed")
    if provenance.get("referenceRuntimeInputUsed") is not False or provenance.get("preScorer") is not True:
        raise RuntimeError("frozen evidence is not a sealed pre-scorer source")

    attacks = list(evidence.get("attacks") or [])
    old_render = list(evidence.get("oldRenderEvents") or [])
    old_links = list(evidence.get("oldLegatoLinks") or [])
    tempo = float(evidence.get("tempoBpm") or 0.0)
    if len(attacks) != 725 or len(old_render) != 985 or len(old_links) != 28 or tempo <= 0.0:
        raise RuntimeError("frozen evidence cardinality changed")

    old_by_index = {int(event["eventIndex"]): deepcopy(event) for event in old_render}
    if set(old_by_index) != set(range(985)):
        raise RuntimeError("old render event indices are incomplete")

    survivors: list[dict[str, Any]] = []
    suppressed: list[dict[str, int]] = []
    remapped_survivor_count = 0
    attack_keys: set[tuple[int, int]] = set()

    for attack in attacks:
        measure, step, time_seconds, primary, hypotheses, notes = attack
        key = (int(measure), int(step))
        if key in attack_keys:
            raise RuntimeError(f"duplicate attack key: {key}")
        attack_keys.add(key)
        primary = int(primary)
        supported = {int(item[0]) for item in hypotheses}
        note_midis = {int(item[1]) for item in notes}
        strongest = _strongest(hypotheses)
        suppress: int | None = None
        if strongest is not None and strongest != primary and strongest - primary in HARMONIC_INTERVALS and strongest in note_midis:
            suppress = strongest
            supported.remove(strongest)
            suppressed.append({"measure": key[0], "step": key[1], "primaryMidi": primary, "suppressedMidi": strongest, "interval": strongest - primary})
        if primary not in supported:
            raise RuntimeError(f"guard removed primary at {key}")

        evidence_by_midi = {int(item[0]): item for item in hypotheses if int(item[0]) in supported}
        others = sorted(
            (midi for midi in supported if midi != primary),
            key=lambda midi: (-float(evidence_by_midi[midi][4]), -float(evidence_by_midi[midi][1]), -float(evidence_by_midi[midi][2]), int(midi)),
        )
        selected = [primary]
        voicing = resolve_joint_chord_voicing(selected)
        if voicing is None:
            raise RuntimeError(f"primary is not playable at {key}")
        for midi in others:
            if len(selected) >= 6:
                break
            trial = selected + [int(midi)]
            trial_voicing = resolve_joint_chord_voicing(trial)
            if trial_voicing is not None:
                selected = trial
                voicing = trial_voicing

        expected = note_midis - ({suppress} if suppress is not None else set())
        if set(selected) != expected:
            raise RuntimeError(f"guard unexpectedly changed selected pitch identity at {key}")

        note_by_midi = {int(item[1]): item for item in notes}
        ordered_midis = sorted(selected, key=lambda midi: (int(voicing[int(midi)]["stringIndex"]), int(midi)))
        for midi in ordered_midis:
            old_note = note_by_midi[int(midi)]
            old_index = int(old_note[0])
            event = deepcopy(old_by_index[old_index])
            event["_oldEventIndex"] = old_index
            event["_timeSeconds"] = float(time_seconds)
            old_mapping = (int(event["stringIndex"]), int(event["fret"]))
            event["stringIndex"] = int(voicing[int(midi)]["stringIndex"])
            event["fret"] = int(voicing[int(midi)]["fret"])
            if old_mapping != (int(event["stringIndex"]), int(event["fret"])):
                remapped_survivor_count += 1
            survivors.append(event)

    if len(attack_keys) != 725 or len(suppressed) != 96 or len(survivors) != 889:
        raise RuntimeError("harmonic guard reconstruction cardinality failed")
    interval_counts: dict[str, int] = {}
    for item in suppressed:
        key = str(item["interval"])
        interval_counts[key] = interval_counts.get(key, 0) + 1
    if interval_counts != {"12": 78, "19": 11, "24": 6, "28": 1}:
        raise RuntimeError("harmonic guard interval distribution changed")
    if remapped_survivor_count != 48:
        raise RuntimeError("joint voicing remap count changed")

    # Candidate assembly emits attacks in key order and notes in high-to-low string order.
    survivors.sort(key=lambda event: (int(event["measure"]), int(event["step"]), int(event["stringIndex"]), int(event["midi"])))
    old_to_new: dict[int, int] = {}
    for index, event in enumerate(survivors):
        old_to_new[int(event["_oldEventIndex"])] = index
        event["eventIndex"] = index

    # New immediate-next topology on each mapped string. This is the dependency
    # used by both legato and sustain. Never invent a new legato link from cached evidence.
    ordered = sorted(range(len(survivors)), key=lambda index: (float(survivors[index]["_timeSeconds"]), int(survivors[index]["stringIndex"]), int(survivors[index]["fret"])))
    next_same_string: dict[int, int | None] = {}
    next_index_by_string: dict[int, int] = {}
    for index in reversed(ordered):
        string_index = int(survivors[index]["stringIndex"])
        next_same_string[index] = next_index_by_string.get(string_index)
        next_index_by_string[string_index] = index

    # Strip all historical legato metadata first, then re-bind only evidence-backed
    # old primary-primary links that remain immediate same-string neighbors.
    for event in survivors:
        for field in ("legatoTargetEventIndex", "legatoTargetFret", "legatoTargetMidi", "legatoContinuationFromEventIndex", "legatoContinuationType"):
            event.pop(field, None)
        techniques = [str(value) for value in event.get("techniques") or []]
        event["techniques"] = [value for value in techniques if value not in LEGATO_TYPES]

    kept_links = 0
    stripped_links = 0
    for old_source, old_target, technique in old_links:
        old_source = int(old_source)
        old_target = int(old_target)
        if old_source not in old_to_new or old_target not in old_to_new:
            stripped_links += 1
            continue
        source_index = old_to_new[old_source]
        target_index = old_to_new[old_target]
        source = survivors[source_index]
        target = survivors[target_index]
        valid = (
            int(source["stringIndex"]) == int(target["stringIndex"])
            and next_same_string.get(source_index) == target_index
        )
        if not valid:
            stripped_links += 1
            continue
        source["legatoTargetEventIndex"] = target_index
        source["legatoTargetFret"] = int(target["fret"])
        source["legatoTargetMidi"] = int(target["midi"])
        source["techniques"] = list(source.get("techniques") or []) + [str(technique)]
        target["legatoContinuationFromEventIndex"] = source_index
        target["legatoContinuationType"] = str(technique)
        kept_links += 1
    if kept_links != 27 or stripped_links != 1:
        raise RuntimeError("conservative cached legato rebind count changed")

    # Sustain evidence may only be shortened when new same-string topology creates
    # an earlier hard end. It is never lengthened from cached evidence.
    timeline = sorted(range(len(survivors)), key=lambda index: (float(survivors[index]["_timeSeconds"]), index))
    next_time_by_string: dict[int, float] = {}
    hard_end: dict[int, float] = {}
    for index in reversed(timeline):
        event = survivors[index]
        onset = float(event["_timeSeconds"])
        string_index = int(event["stringIndex"])
        limit = onset + 3.0
        if string_index in next_time_by_string:
            limit = min(limit, max(onset, next_time_by_string[string_index] - 0.01))
        hard_end[index] = limit
        next_time_by_string[string_index] = onset

    old_note_meta: dict[int, bool] = {}
    for attack in attacks:
        for note in attack[5]:
            old_note_meta[int(note[0])] = bool(note[4])

    clamped_sustain_count = 0
    for index, event in enumerate(survivors):
        old_index = int(event["_oldEventIndex"])
        if old_note_meta.get(old_index) is True:
            onset = float(event["_timeSeconds"])
            old_duration = float(event.get("durationSeconds") or 0.0)
            maximum = max(0.0, float(hard_end[index]) - onset)
            if old_duration > maximum + 1.0e-9:
                new_duration = maximum
                steps = _duration_steps(new_duration, tempo)
                event["durationSeconds"] = float(new_duration)
                event["durationSteps"] = int(steps)
                event["sustainTier"] = _tier(steps)
                clamped_sustain_count += 1
        event.pop("_oldEventIndex", None)
        event.pop("_timeSeconds", None)

    if clamped_sustain_count != 13:
        raise RuntimeError("conservative sustain-clamp count changed")

    # Final fail-closed invariants.
    if len({(int(event["measure"]), int(event["step"])) for event in survivors}) != 725:
        raise RuntimeError("reconstruction changed attack identity")
    if any(int(event["midi"]) not in {int(item[0]) for attack in attacks if (int(attack[0]), int(attack[1])) == (int(event["measure"]), int(event["step"])) for item in attack[4]} for event in survivors):
        raise RuntimeError("reconstruction invented a pitch")

    corrected = {
        "schemaVersion": 1,
        "mode": "v143-promoted-harmonic-guard-frozen-upstream-reuse",
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "freshSeparatorInference": False,
        "historicalFrozenUpstreamReused": True,
        "tempoBpm": tempo,
        "timeSignature": "4/4",
        "tuning": "E Standard",
        "renderEvents": survivors,
    }
    proof = {
        "schemaVersion": 1,
        "passed": True,
        "mode": corrected["mode"],
        "sourceAudioSha256": APPROVED_AUDIO_SHA256,
        "retiredEventSha256": RETIRED_EVENT_SHA256,
        "oldRenderEventCount": 985,
        "attackCount": 725,
        "suppressedHarmonicCount": 96,
        "intervalCounts": interval_counts,
        "correctedRenderEventCount": len(survivors),
        "remappedSurvivorCount": remapped_survivor_count,
        "historicalLegatoLinkCount": 28,
        "retainedEvidenceBackedLegatoLinkCount": kept_links,
        "strippedInvalidatedLegatoLinkCount": stripped_links,
        "conservativelyClampedSustainCount": clamped_sustain_count,
        "correctedRenderEventsCanonicalSha256": canonical_sha(survivors),
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "modalUsed": False,
        "freshSeparatorInference": False,
        "productionModified": False,
    }
    return corrected, proof


def main(evidence_path: str, corrected_path: str, proof_path: str) -> None:
    evidence = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
    corrected, proof = reconstruct(evidence)
    corrected_destination = Path(corrected_path)
    proof_destination = Path(proof_path)
    corrected_destination.parent.mkdir(parents=True, exist_ok=True)
    proof_destination.parent.mkdir(parents=True, exist_ok=True)
    corrected_destination.write_text(json.dumps(corrected, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    proof_destination.write_text(json.dumps(proof, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: v143_reconstruct_harmonic_guard_from_frozen_evidence.py EVIDENCE CORRECTED PROOF")
    main(sys.argv[1], sys.argv[2], sys.argv[3])
