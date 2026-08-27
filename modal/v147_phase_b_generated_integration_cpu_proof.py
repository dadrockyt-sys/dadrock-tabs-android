from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from modal.v147_phase_b_generated_integration import (
    decode_generated_pitch_hypotheses,
    integration_result_to_dict,
    position_identity_violations,
)

EXPECTED_V145_BLOB = "2fd979aebb4685e86c7f24a0162f69de306c06e9"
EXPECTED_V147_BLOB = "49bce8b968406bb0d61ab61394954ef8a8303eb7"


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _event(midi: int, onset: float = 0.10) -> dict[str, float | int]:
    return {
        "midi": midi,
        "onset": onset,
        "duration": 0.20,
        "confidence": 0.90,
    }


def _e(fundamental: float, octave: float = 0.0) -> dict[str, float]:
    return {
        "fundamentalDeltaDb": fundamental,
        "octaveDeltaDb": octave,
    }


def _git_blob(path: str) -> str | None:
    try:
        return subprocess.check_output(["git", "hash-object", path], text=True).strip()
    except Exception:
        return None


def _case(
    name: str,
    category: str,
    evidence: Any,
    expected_midi: int,
) -> dict[str, Any]:
    events = [_event(60)]
    before = _canonical_bytes(events)
    result = decode_generated_pitch_hypotheses(events, evidence, 0.25)
    after = _canonical_bytes(events)

    decision = result.decisions[0]
    decoded = result.decode_result.decoded_notes
    cardinality_ok = (
        result.normalized_evidence_count == 1
        and len(result.decisions) == 1
        and result.decode_result.evidence_count == 1
        and result.decode_result.decoded_evidence_count == 1
        and len(decoded) == 1
    )
    selected_ok = int(decision["selectedMidi"]) == expected_midi
    decoded_ok = len(decoded) == 1 and decoded[0].midi == expected_midi
    position_violations = position_identity_violations(result)
    input_mutated = before != after
    passed = (
        cardinality_ok
        and selected_ok
        and decoded_ok
        and position_violations == 0
        and not input_mutated
    )

    return {
        "name": name,
        "category": category,
        "expectedMidi": expected_midi,
        "passed": passed,
        "cardinalityOk": cardinality_ok,
        "positionIdentityViolations": position_violations,
        "inputMutated": input_mutated,
        "integration": integration_result_to_dict(result),
    }


def _run_cases() -> list[dict[str, Any]]:
    return [
        _case(
            "control-passthrough",
            "control",
            {0: {59: _e(1), 60: _e(8), 61: _e(2)}},
            60,
        ),
        _case(
            "down-one-end-to-end",
            "strong-alternate",
            {0: {59: _e(8), 60: _e(3), 61: _e(1)}},
            59,
        ),
        _case(
            "up-one-end-to-end",
            "strong-alternate",
            {0: {59: _e(1), 60: _e(3), 61: _e(8)}},
            61,
        ),
        _case(
            "ambiguous-fail-closed",
            "ambiguous",
            {0: {59: _e(1), 60: _e(4), 61: _e(6.5)}},
            60,
        ),
        _case(
            "missing-evidence-fail-closed",
            "malformed",
            {},
            60,
        ),
    ]


def build_proof() -> dict[str, Any]:
    first_cases = _run_cases()
    second_cases = _run_cases()
    deterministic = _canonical_bytes(first_cases) == _canonical_bytes(second_cases)

    source_blobs = {
        "v145Decoder": _git_blob("modal/v145_rhythm_decoder.py"),
        "v147PitchHypothesis": _git_blob("modal/v147_pitch_hypothesis.py"),
    }
    source_identity_ok = (
        source_blobs["v145Decoder"] == EXPECTED_V145_BLOB
        and source_blobs["v147PitchHypothesis"] == EXPECTED_V147_BLOB
    )

    all_decisions = [
        decision
        for case in first_cases
        for decision in case["integration"]["decisions"]
    ]
    controls = [case for case in first_cases if case["category"] == "control"]
    strong = [case for case in first_cases if case["category"] == "strong-alternate"]
    ambiguous = [case for case in first_cases if case["category"] == "ambiguous"]
    malformed = [case for case in first_cases if case["category"] == "malformed"]

    metrics = {
        "casesTotal": len(first_cases),
        "casesPassed": sum(1 for case in first_cases if case["passed"]),
        "inputEvents": len(first_cases),
        "normalizedEvidence": sum(
            int(case["integration"]["normalizedEvidenceCount"])
            for case in first_cases
        ),
        "decisions": len(all_decisions),
        "pitchChanges": sum(1 for decision in all_decisions if decision["changed"]),
        "controlFlips": sum(
            1
            for case in controls
            if case["integration"]["decisions"][0]["changed"]
        ),
        "strongAlternatesRecovered": sum(1 for case in strong if case["passed"]),
        "strongAlternates": len(strong),
        "ambiguousKept": sum(
            1
            for case in ambiguous
            if case["integration"]["decisions"][0]["selectedMidi"] == 60
        ),
        "ambiguousCases": len(ambiguous),
        "malformedKept": sum(
            1
            for case in malformed
            if case["integration"]["decisions"][0]["selectedMidi"] == 60
        ),
        "malformedCases": len(malformed),
        "sourceCardinalityViolations": sum(
            1 for case in first_cases if not case["cardinalityOk"]
        ),
        "positionIdentityViolations": sum(
            int(case["positionIdentityViolations"])
            for case in first_cases
        ),
        "inputMutationViolations": sum(
            1 for case in first_cases if case["inputMutated"]
        ),
        "deterministic": deterministic,
        "frozenSourceIdentityMatch": source_identity_ok,
    }

    go = (
        metrics["casesPassed"] == metrics["casesTotal"]
        and metrics["controlFlips"] == 0
        and metrics["strongAlternatesRecovered"] == metrics["strongAlternates"]
        and metrics["ambiguousKept"] == metrics["ambiguousCases"]
        and metrics["malformedKept"] == metrics["malformedCases"]
        and metrics["sourceCardinalityViolations"] == 0
        and metrics["positionIdentityViolations"] == 0
        and metrics["inputMutationViolations"] == 0
        and metrics["deterministic"] is True
        and metrics["frozenSourceIdentityMatch"] is True
    )

    payload = {
        "schema": 14711,
        "phase": "V147-Phase-B",
        "evidenceClass": "cpu-generated-reference-free-decoder-integration",
        "referenceFree": True,
        "calibrationReferenceRead": False,
        "goldRead": False,
        "realAudioRead": False,
        "analyzerIntegrated": False,
        "modalGpuUsed": False,
        "productionIntegrated": False,
        "sourceBlobs": source_blobs,
        "cases": first_cases,
        "metrics": metrics,
        "gate": "GO" if go else "STOP",
    }
    payload["proofPayloadSha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    proof = build_proof()
    print("V147_PHASE_B_PROOF_JSON=" + _canonical_bytes(proof).decode("utf-8"))

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(proof, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return 0 if proof["gate"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
