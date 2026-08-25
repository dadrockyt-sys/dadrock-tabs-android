from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Mapping

from v143_rhythm_guitar_note_mapper import resolve_joint_chord_voicing

MAX_GUITAR_STRINGS = 6


class ReplayVoicingValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayVoicingValidationError(message)


def _expected_voicing(attack: Mapping[str, Any]) -> tuple[list[int], dict[int, dict[str, Any]]]:
    candidates = {
        int(item["midi"]): item
        for item in (attack.get("candidates") or [])
    }
    selected = {
        midi
        for midi, item in candidates.items()
        if item.get("selected") is True
    }
    primaries = [midi for midi, item in candidates.items() if item.get("primary") is True]
    _require(len(primaries) == 1, "retained replay attack must have one primary")
    primary = int(primaries[0])
    _require(primary in selected, "primary is not selected")

    others = sorted(
        (midi for midi in selected if midi != primary),
        key=lambda midi: (
            -float(candidates[midi]["score"]),
            -float(candidates[midi]["attack"]),
            -float(candidates[midi]["body"]),
            int(midi),
        ),
    )

    kept = [primary]
    voicing = resolve_joint_chord_voicing(kept)
    _require(voicing is not None, f"primary MIDI {primary} has no legal guitar position")

    for midi in others:
        if len(kept) >= MAX_GUITAR_STRINGS:
            break
        trial = kept + [int(midi)]
        trial_voicing = resolve_joint_chord_voicing(trial)
        if trial_voicing is None:
            continue
        kept = trial
        voicing = trial_voicing

    _require(voicing is not None, "expected voicing unexpectedly missing")
    return kept, voicing


def validate_product_voicing(product: Mapping[str, Any]) -> dict[str, Any]:
    replay = product.get("precisionReplayEvidence") or {}
    events = product.get("events") or []
    diagnostics = product.get("candidateDiagnostics") or {}

    _require(replay.get("schemaVersion") == 2, "voicing validation requires replay schema 2")
    _require(replay.get("referenceFree") is True, "replay is not reference-free")
    _require(replay.get("professionalReferenceUsed") is False, "replay indicates professional reference use")

    attacks = replay.get("attacks") or []
    attack_by_key: dict[tuple[int, int], Mapping[str, Any]] = {}
    selected_total = 0
    for attack in attacks:
        key = (int(attack["measure"]), int(attack["step"]))
        _require(key not in attack_by_key, f"duplicate replay attack {key}")
        _require(attack.get("retained") is True, f"replay attack {key} is not retained")
        attack_by_key[key] = attack
        selected_total += sum(
            1
            for item in (attack.get("candidates") or [])
            if item.get("selected") is True
        )

    events_by_key: dict[tuple[int, int], list[Mapping[str, Any]]] = {}
    for event in events:
        key = (int(event["measure"]), int(event["step"]))
        events_by_key.setdefault(key, []).append(event)

    _require(set(events_by_key) == set(attack_by_key), "render/replay attack identities differ")

    expected_rendered_total = 0
    voicing_dropped_total = 0
    for key in sorted(attack_by_key):
        attack = attack_by_key[key]
        candidates = {
            int(item["midi"]): item
            for item in (attack.get("candidates") or [])
        }
        primary = next(
            int(midi)
            for midi, item in candidates.items()
            if item.get("primary") is True
        )
        supported = {
            int(midi)
            for midi, item in candidates.items()
            if item.get("selected") is True
        }
        expected_midis, expected_voicing = _expected_voicing(attack)
        expected_set = set(expected_midis)
        actual = events_by_key[key]
        actual_midis = [int(event["midi"]) for event in actual]

        _require(len(actual_midis) == len(set(actual_midis)), f"duplicate rendered MIDI at {key}")
        _require(set(actual_midis) == expected_set, f"rendered pitch set does not match deterministic voicing at {key}")
        _require(expected_set.issubset(supported), f"deterministic voicing escaped supported pitch set at {key}")

        for event in actual:
            midi = int(event["midi"])
            position = expected_voicing[midi]
            _require(int(event.get("stringIndex")) == int(position["stringIndex"]), f"string index mismatch at {key} MIDI {midi}")
            _require(str(event.get("stringName")) == str(position["stringName"]), f"string name mismatch at {key} MIDI {midi}")
            _require(int(event.get("fret")) == int(position["fret"]), f"fret mismatch at {key} MIDI {midi}")
            _require(int(event.get("dominantMidi")) == primary, f"dominant/primary mismatch at {key} MIDI {midi}")
            mapping = event.get("noteMapping") or {}
            _require(mapping.get("precisionPrimaryPreserved") is True, f"primary-preservation marker missing at {key}")
            _require(int(mapping.get("sourceAttackMidi")) == primary, f"sourceAttackMidi mismatch at {key}")
            _require(bool(mapping.get("primaryTechniqueNote")) == (midi == primary), f"primaryTechniqueNote mismatch at {key} MIDI {midi}")

        expected_rendered_total += len(expected_set)
        voicing_dropped_total += len(supported - expected_set)

    _require(len(events) == expected_rendered_total, "rendered event total does not match deterministic voicing")
    if diagnostics:
        _require(int(diagnostics.get("renderedPitchCount")) == expected_rendered_total, "candidate renderedPitchCount mismatch")
        _require(int(diagnostics.get("renderedNoteCount")) == expected_rendered_total, "candidate renderedNoteCount mismatch")
        _require(int(diagnostics.get("voicingDroppedPitchCount")) == voicing_dropped_total, "candidate voicingDroppedPitchCount mismatch")
        _require(int(diagnostics.get("supportedPitchCount")) == selected_total, "candidate supportedPitchCount mismatch")

    return {
        "schemaVersion": 1,
        "classification": "v143-precision-deterministic-voicing-replay",
        "passed": True,
        "attackCount": len(attack_by_key),
        "selectedPitchCount": selected_total,
        "renderedPitchCount": expected_rendered_total,
        "voicingDroppedPitchCount": voicing_dropped_total,
        "stringFretReplayMatches": True,
        "primaryPreservationMatches": True,
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "productionModified": False,
    }


def _event_for(midi: int, position: Mapping[str, Any], *, primary: int) -> dict[str, Any]:
    return {
        "measure": 1,
        "step": 0,
        "midi": int(midi),
        "dominantMidi": int(primary),
        "stringIndex": int(position["stringIndex"]),
        "stringName": str(position["stringName"]),
        "fret": int(position["fret"]),
        "noteMapping": {
            "precisionPrimaryPreserved": True,
            "sourceAttackMidi": int(primary),
            "primaryTechniqueNote": int(midi) == int(primary),
        },
    }


def _self_test() -> None:
    attack = {
        "measure": 1,
        "step": 0,
        "retained": True,
        "candidateMidis": [60, 64, 67],
        "candidates": [
            {"midi": 60, "score": 1.0, "attack": 1.0, "body": 0.9, "selected": True, "primary": True},
            {"midi": 64, "score": 0.9, "attack": 0.8, "body": 0.8, "selected": True, "primary": False},
            {"midi": 67, "score": 0.85, "attack": 0.82, "body": 0.75, "selected": True, "primary": False},
        ],
    }
    expected_midis, voicing = _expected_voicing(attack)
    product = {
        "precisionReplayEvidence": {
            "schemaVersion": 2,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "attacks": [attack],
        },
        "events": [_event_for(midi, voicing[midi], primary=60) for midi in expected_midis],
        "candidateDiagnostics": {
            "supportedPitchCount": 3,
            "renderedPitchCount": len(expected_midis),
            "renderedNoteCount": len(expected_midis),
            "voicingDroppedPitchCount": 3 - len(expected_midis),
        },
    }
    report = validate_product_voicing(product)
    assert report["passed"] is True
    assert report["stringFretReplayMatches"] is True

    broken = copy.deepcopy(product)
    broken["events"][0]["fret"] = int(broken["events"][0]["fret"]) + 1
    try:
        validate_product_voicing(broken)
    except ReplayVoicingValidationError:
        pass
    else:
        raise AssertionError("voicing validator failed to reject corrupted fret")

    print("PASS v143 precision deterministic voicing replay self-test")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return
    if not args.input or not args.output:
        raise SystemExit("--input and --output are required unless --self-test is used")
    product = json.loads(Path(args.input).read_text(encoding="utf-8"))
    report = validate_product_voicing(product)
    Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
