from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from modal.v147_pitch_hypothesis import choose_pitch_hypothesis


def _e(fundamental: float, octave: float = 0.0) -> dict[str, float]:
    return {
        "fundamentalDeltaDb": fundamental,
        "octaveDeltaDb": octave,
    }


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _case(
    name: str,
    category: str,
    original_midi: int,
    evidence: Any,
    expected_midi: int,
) -> dict[str, Any]:
    result = choose_pitch_hypothesis(original_midi, evidence)
    passed = result["selectedMidi"] == expected_midi
    return {
        "name": name,
        "category": category,
        "originalMidi": original_midi,
        "expectedMidi": expected_midi,
        "passed": passed,
        "result": result,
    }


def _run_cases() -> list[dict[str, Any]]:
    return [
        _case(
            "correct-control",
            "correct-control",
            60,
            {59: _e(1), 60: _e(7), 61: _e(2)},
            60,
        ),
        _case(
            "down-one-recovery",
            "deliberate-mislabel",
            60,
            {59: _e(8), 60: _e(3), 61: _e(1)},
            59,
        ),
        _case(
            "up-one-recovery",
            "deliberate-mislabel",
            60,
            {59: _e(1), 60: _e(3), 61: _e(8)},
            61,
        ),
        _case(
            "ambiguous-neighbor",
            "ambiguous",
            60,
            {59: _e(1), 60: _e(4), 61: _e(6.5)},
            60,
        ),
        _case(
            "weak-evidence",
            "ambiguous",
            60,
            {59: _e(0), 60: _e(0), 61: _e(2.9)},
            60,
        ),
        _case(
            "tie",
            "ambiguous",
            60,
            {59: _e(7), 60: _e(2), 61: _e(7)},
            60,
        ),
        _case(
            "low-guitar-boundary",
            "boundary",
            40,
            {40: _e(2), 41: _e(7)},
            41,
        ),
        _case(
            "high-guitar-boundary",
            "boundary",
            88,
            {87: _e(7), 88: _e(2)},
            87,
        ),
        _case(
            "missing-candidate-evidence",
            "malformed",
            60,
            {59: _e(8), 60: _e(2)},
            60,
        ),
        _case(
            "non-finite-evidence",
            "malformed",
            60,
            {59: _e(8), 60: _e(2), 61: _e(float("inf"))},
            60,
        ),
        _case(
            "malformed-container",
            "malformed",
            60,
            [59, 60, 61],
            60,
        ),
    ]


def build_proof() -> dict[str, Any]:
    first_cases = _run_cases()
    second_cases = _run_cases()
    deterministic = _canonical_bytes(first_cases) == _canonical_bytes(second_cases)

    correct_controls = [row for row in first_cases if row["category"] == "correct-control"]
    deliberate = [row for row in first_cases if row["category"] == "deliberate-mislabel"]
    ambiguous = [row for row in first_cases if row["category"] == "ambiguous"]
    malformed = [row for row in first_cases if row["category"] == "malformed"]

    range_violations = sum(
        1
        for row in first_cases
        if not 40 <= int(row["result"]["selectedMidi"]) <= 88
    )

    metrics = {
        "casesTotal": len(first_cases),
        "casesPassed": sum(1 for row in first_cases if row["passed"]),
        "correctControls": len(correct_controls),
        "correctControlsFlipped": sum(
            1 for row in correct_controls if row["result"]["changed"]
        ),
        "deliberateMislabels": len(deliberate),
        "deliberateMislabelsRecovered": sum(1 for row in deliberate if row["passed"]),
        "ambiguousCases": len(ambiguous),
        "ambiguousCasesKept": sum(
            1
            for row in ambiguous
            if row["result"]["selectedMidi"] == row["originalMidi"]
        ),
        "rangeViolations": range_violations,
        "malformedFailClosed": sum(
            1
            for row in malformed
            if row["result"]["selectedMidi"] == row["originalMidi"]
        ),
        "malformedCases": len(malformed),
        "deterministic": deterministic,
    }

    go = (
        metrics["casesPassed"] == metrics["casesTotal"]
        and metrics["correctControlsFlipped"] == 0
        and metrics["deliberateMislabelsRecovered"] == metrics["deliberateMislabels"]
        and metrics["ambiguousCasesKept"] == metrics["ambiguousCases"]
        and metrics["rangeViolations"] == 0
        and metrics["malformedFailClosed"] == metrics["malformedCases"]
        and metrics["deterministic"] is True
    )

    payload = {
        "schema": 14701,
        "phase": "V147-Phase-A",
        "evidenceClass": "cpu-generated-reference-free",
        "referenceFree": True,
        "calibrationReferenceRead": False,
        "goldRead": False,
        "modalGpuUsed": False,
        "liveAudioUsed": False,
        "productionIntegrated": False,
        "cases": first_cases,
        "metrics": metrics,
        "gate": "GO" if go else "STOP",
    }
    payload_sha256 = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    payload["proofPayloadSha256"] = payload_sha256
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    proof = build_proof()
    canonical = _canonical_bytes(proof).decode("utf-8")
    print(f"V147_PROOF_JSON={canonical}")

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return 0 if proof["gate"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
