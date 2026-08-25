from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

EXPECTED_POLICY = "envelope-balanced-secondary-v2"
EXPECTED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
EVIDENCE_FIELDS = ("attack", "early", "sustain", "body", "continuity", "score")


class ReplayArtifactValidationError(ValueError):
    pass


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ReplayArtifactValidationError(f"{label} is not numeric") from exc
    if not math.isfinite(number):
        raise ReplayArtifactValidationError(f"{label} is not finite")
    return number


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise ReplayArtifactValidationError(f"{label} is boolean, not integer")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ReplayArtifactValidationError(f"{label} is not integer-like") from exc
    return number


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayArtifactValidationError(message)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_product(product: Mapping[str, Any]) -> dict[str, Any]:
    candidate = product.get("candidate") or {}
    replay = product.get("precisionReplayEvidence") or {}
    precision = product.get("precisionDiagnostics") or {}
    diagnostics = product.get("candidateDiagnostics") or {}
    assembly = product.get("assembly") or {}
    timing = product.get("timing") or {}
    events = product.get("events") or []

    _require(isinstance(candidate, Mapping), "candidate metadata missing")
    _require(isinstance(replay, Mapping), "precisionReplayEvidence missing")
    _require(isinstance(precision, Mapping), "precisionDiagnostics missing")
    _require(isinstance(diagnostics, Mapping), "candidateDiagnostics missing")
    _require(isinstance(assembly, Mapping), "assembly metadata missing")
    _require(isinstance(timing, Mapping), "timing metadata missing")
    _require(isinstance(events, Sequence) and not isinstance(events, (str, bytes, bytearray)), "events must be a sequence")

    _require(candidate.get("approvedFixture") is True, "candidate is not approved fixture")
    _require(candidate.get("sourceSha256") == EXPECTED_AUDIO_SHA256, "approved fixture SHA mismatch")
    _require(candidate.get("professionalReferenceUsed") is False, "candidate indicates professional reference use")
    _require(candidate.get("runtimeLabelsRequired") is False, "candidate requires runtime labels")
    _require(candidate.get("productionModified") is False, "candidate indicates production mutation")

    _require(replay.get("schemaVersion") == 1, "unexpected replay schemaVersion")
    _require(replay.get("policy") == EXPECTED_POLICY, "unexpected replay policy")
    _require(replay.get("referenceFree") is True, "replay is not reference-free")
    _require(replay.get("professionalReferenceUsed") is False, "replay indicates professional reference use")
    _require(replay.get("runtimeLabelsRequired") is False, "replay requires runtime labels")
    _require(replay.get("productionModified") is False, "replay indicates production mutation")
    _require(replay.get("candidateAddsUnobservedAttack") is False, "replay says attack was invented")
    _require(replay.get("candidateAddsUnobservedPitch") is False, "replay says pitch was invented")

    attacks = replay.get("attacks") or []
    _require(isinstance(attacks, Sequence) and not isinstance(attacks, (str, bytes, bytearray)), "replay attacks must be a sequence")
    _require(len(attacks) == _int(replay.get("retainedAttackCount"), "replay.retainedAttackCount"), "replay attack count mismatch")
    _require(len(attacks) > 0, "replay contains no attacks")

    attack_candidates: dict[tuple[int, int], set[int]] = {}
    attack_selected: dict[tuple[int, int], set[int]] = {}
    candidate_total = 0
    selected_total = 0

    for attack_index, attack in enumerate(attacks):
        _require(isinstance(attack, Mapping), f"attack[{attack_index}] is not a mapping")
        measure = _int(attack.get("measure"), f"attack[{attack_index}].measure")
        step = _int(attack.get("step"), f"attack[{attack_index}].step")
        key = (measure, step)
        _require(key not in attack_candidates, f"duplicate replay attack {key}")
        _finite(attack.get("onsetTime"), f"attack[{attack_index}].onsetTime")

        candidate_midis_raw = attack.get("candidateMidis") or []
        candidates = attack.get("candidates") or []
        _require(
            isinstance(candidate_midis_raw, Sequence) and not isinstance(candidate_midis_raw, (str, bytes, bytearray)),
            f"attack {key} candidateMidis is not a sequence",
        )
        _require(
            isinstance(candidates, Sequence) and not isinstance(candidates, (str, bytes, bytearray)),
            f"attack {key} candidates is not a sequence",
        )
        candidate_midis = [_int(value, f"attack {key} candidateMidi") for value in candidate_midis_raw]
        candidate_records: list[int] = []
        selected: set[int] = set()
        primaries: list[int] = []

        for candidate_index, item in enumerate(candidates):
            _require(isinstance(item, Mapping), f"attack {key} candidate[{candidate_index}] is not a mapping")
            midi = _int(item.get("midi"), f"attack {key} candidate[{candidate_index}].midi")
            candidate_records.append(midi)
            values = {field: _finite(item.get(field), f"attack {key} MIDI {midi} {field}") for field in EVIDENCE_FIELDS}
            _require(
                math.isclose(values["body"], max(values["early"], values["sustain"]), rel_tol=0.0, abs_tol=1e-12),
                f"attack {key} MIDI {midi} body is not max(early,sustain)",
            )
            _require(
                math.isclose(values["continuity"], min(values["early"], values["sustain"]), rel_tol=0.0, abs_tol=1e-12),
                f"attack {key} MIDI {midi} continuity is not min(early,sustain)",
            )
            expected_score = values["attack"] + 0.65 * values["body"] + 0.15 * values["continuity"]
            _require(
                math.isclose(values["score"], expected_score, rel_tol=0.0, abs_tol=1e-10),
                f"attack {key} MIDI {midi} score formula mismatch",
            )
            if item.get("selected") is True:
                selected.add(midi)
            if item.get("primary") is True:
                primaries.append(midi)

        _require(candidate_midis == candidate_records, f"attack {key} candidate identity/order mismatch")
        _require(len(candidate_records) == len(set(candidate_records)), f"attack {key} contains duplicate MIDI")
        _require(len(candidate_records) > 0, f"attack {key} has no pitch hypotheses")
        _require(len(primaries) == 1, f"attack {key} must contain exactly one primary")
        _require(primaries[0] in selected, f"attack {key} primary is not selected")
        _require(selected, f"attack {key} has no selected pitch")

        attack_candidates[key] = set(candidate_records)
        attack_selected[key] = selected
        candidate_total += len(candidate_records)
        selected_total += len(selected)

    _require(
        candidate_total == _int(replay.get("originalPitchHypothesisCount"), "replay.originalPitchHypothesisCount"),
        "replay original pitch count mismatch",
    )
    _require(
        _int(precision.get("retainedAttackCount"), "precision.retainedAttackCount") == len(attacks),
        "precision/replay retained attack count mismatch",
    )
    _require(
        _int(precision.get("originalPitchHypothesisCount"), "precision.originalPitchHypothesisCount") == candidate_total,
        "precision/replay original pitch count mismatch",
    )
    _require(
        _int(precision.get("retainedPitchHypothesisCount"), "precision.retainedPitchHypothesisCount") == selected_total,
        "precision/replay selected pitch count mismatch",
    )

    event_keys: set[tuple[int, int]] = set()
    emitted_by_key: dict[tuple[int, int], set[int]] = {}
    for event_index, event in enumerate(events):
        _require(isinstance(event, Mapping), f"event[{event_index}] is not a mapping")
        key = (
            _int(event.get("measure"), f"event[{event_index}].measure"),
            _int(event.get("step"), f"event[{event_index}].step"),
        )
        midi = _int(event.get("midi"), f"event[{event_index}].midi")
        _require(key in attack_candidates, f"render emitted attack absent from replay: {key}")
        _require(midi in attack_candidates[key], f"render emitted unobserved pitch {midi} at {key}")
        _require(midi in attack_selected[key], f"render emitted replay-unselected pitch {midi} at {key}")
        emitted_by_key.setdefault(key, set()).add(midi)
        event_keys.add(key)

    _require(event_keys == set(attack_candidates), "render/replay attack identity mismatch")
    _require(len(events) == _int(product.get("noteCount"), "product.noteCount"), "noteCount does not match events length")
    _require(len(attacks) == _int(product.get("selectedCount"), "product.selectedCount"), "selectedCount does not match replay attacks")
    _require(len(attacks) == _int(assembly.get("selectedAttackCount"), "assembly.selectedAttackCount"), "assembly selected attack count mismatch")
    _require(len(events) == _int(assembly.get("renderNoteCount"), "assembly.renderNoteCount"), "assembly render note count mismatch")

    supported_pitch_count = _int(diagnostics.get("supportedPitchCount"), "candidateDiagnostics.supportedPitchCount")
    rendered_pitch_count = _int(diagnostics.get("renderedPitchCount"), "candidateDiagnostics.renderedPitchCount")
    rendered_note_count = _int(diagnostics.get("renderedNoteCount"), "candidateDiagnostics.renderedNoteCount")
    dropped_pitch_count = _int(diagnostics.get("voicingDroppedPitchCount"), "candidateDiagnostics.voicingDroppedPitchCount")
    _require(diagnostics.get("everyCorrectedAttackRendered") is True, "candidate did not render every retained attack")
    _require(supported_pitch_count == selected_total, "candidate supported pitch count does not match replay selected total")
    _require(rendered_pitch_count == len(events), "candidate rendered pitch count mismatch")
    _require(rendered_note_count == len(events), "candidate rendered note count mismatch")
    _require(dropped_pitch_count == selected_total - len(events), "candidate voicing drop accounting mismatch")
    _require(dropped_pitch_count >= 0, "candidate voicing drop count is negative")

    measure_start = _int(timing.get("measureStart"), "timing.measureStart")
    measure_end = _int(timing.get("measureEnd"), "timing.measureEnd")
    _require(measure_start <= measure_end, "timing measure range is inverted")
    expected_measures = set(range(measure_start, measure_end + 1))
    replay_measures = {measure for measure, _step in attack_candidates}
    _require(replay_measures == expected_measures, "replay does not cover exact audio-derived measure range")
    _require(
        len(expected_measures) == _int(product.get("audioDerivedMeasureCount"), "product.audioDerivedMeasureCount"),
        "audioDerivedMeasureCount mismatch",
    )

    return {
        "schemaVersion": 1,
        "classification": "v143-precision-replay-artifact-exact-binding",
        "passed": True,
        "policy": EXPECTED_POLICY,
        "retainedAttackCount": len(attacks),
        "originalPitchHypothesisCount": candidate_total,
        "storedSelectedPitchCount": selected_total,
        "renderedPitchCount": len(events),
        "voicingDroppedPitchCount": dropped_pitch_count,
        "measureStart": measure_start,
        "measureEnd": measure_end,
        "replayEvidenceSha256": _canonical_sha256(replay),
        "eventsSha256": _canonical_sha256(events),
        "referenceFree": True,
        "newInferenceUsed": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _self_test_product() -> dict[str, Any]:
    attack = {
        "measure": 1,
        "step": 0,
        "onsetTime": 0.25,
        "candidateMidis": [60, 64],
        "candidates": [
            {
                "midi": 60,
                "attack": 1.0,
                "early": 0.8,
                "sustain": 0.6,
                "body": 0.8,
                "continuity": 0.6,
                "score": 1.61,
                "selected": True,
                "primary": True,
            },
            {
                "midi": 64,
                "attack": 0.9,
                "early": 0.7,
                "sustain": 0.5,
                "body": 0.7,
                "continuity": 0.5,
                "score": 1.43,
                "selected": True,
                "primary": False,
            },
        ],
    }
    return {
        "candidate": {
            "approvedFixture": True,
            "sourceSha256": EXPECTED_AUDIO_SHA256,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        },
        "precisionReplayEvidence": {
            "schemaVersion": 1,
            "policy": EXPECTED_POLICY,
            "retainedAttackCount": 1,
            "originalPitchHypothesisCount": 2,
            "attacks": [attack],
            "candidateAddsUnobservedAttack": False,
            "candidateAddsUnobservedPitch": False,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        },
        "precisionDiagnostics": {
            "retainedAttackCount": 1,
            "originalPitchHypothesisCount": 2,
            "retainedPitchHypothesisCount": 2,
        },
        "candidateDiagnostics": {
            "supportedPitchCount": 2,
            "renderedPitchCount": 1,
            "renderedNoteCount": 1,
            "voicingDroppedPitchCount": 1,
            "everyCorrectedAttackRendered": True,
        },
        "assembly": {
            "selectedAttackCount": 1,
            "renderNoteCount": 1,
        },
        "timing": {
            "measureStart": 1,
            "measureEnd": 1,
        },
        "events": [{"measure": 1, "step": 0, "midi": 60}],
        "noteCount": 1,
        "selectedCount": 1,
        "audioDerivedMeasureCount": 1,
    }


def _self_test() -> None:
    product = _self_test_product()
    report = validate_product(product)
    assert report["passed"] is True
    assert report["originalPitchHypothesisCount"] == 2
    assert report["storedSelectedPitchCount"] == 2
    assert report["renderedPitchCount"] == 1
    assert report["voicingDroppedPitchCount"] == 1

    broken = json.loads(json.dumps(product))
    broken["events"][0]["midi"] = 67
    try:
        validate_product(broken)
    except ReplayArtifactValidationError:
        pass
    else:
        raise AssertionError("validator failed to reject an invented rendered pitch")

    print("PASS v143 precision replay artifact exact-binding self-test")


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
    report = validate_product(product)
    Path(args.output).write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
