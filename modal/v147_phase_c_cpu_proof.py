from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from modal.v147_phase_c_artifact_support import (
    EXPECTED_ACCEPTED_EVENT_COUNT,
    EXPECTED_ACCEPTED_EVENT_SHA256,
    EXPECTED_RAW_AUDIO_SHA256,
    apply_fixed_time_pitch_decisions,
    decide_event_from_prepared_cqt,
    materialize_accepted_family,
    timing_and_metadata_violations,
    verify_raw_audio_identity,
)

ROOT = Path(__file__).resolve().parents[1]
V5_PATH = ROOT / "debug" / "v143-contextual-prune" / "v5-professional-pdf" / "v5-render-stream.json"
EXPECTED_V145_BLOB = "2fd979aebb4685e86c7f24a0162f69de306c06e9"
EXPECTED_V147_BLOB = "49bce8b968406bb0d61ab61394954ef8a8303eb7"
EXPECTED_PREREG_BLOB = "5c19ed572d17cc9a760f1b63ee03c1b2c4543d30"
EXPECTED_CLARIFICATION_BLOB = "6ced1bae4cdaad8306b008827657afbb27a87dbc"


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def _event(midi: int = 60, *, event_index: int = 0, step: int = 0) -> dict[str, Any]:
    position = {
        59: (1, 0),
        60: (1, 1),
        61: (1, 2),
        64: (0, 0),
    }
    string_index, fret = position[midi]
    return {
        "eventIndex": event_index,
        "midi": midi,
        "stringIndex": string_index,
        "fret": fret,
        "measure": 1,
        "step": step,
        "durationSeconds": 0.20,
        "durationSteps": 2,
        "techniques": [],
        "metadataSource": "phase-c-generated-proof",
    }


def _cqt(strong_midi: int, *, flat: bool = False) -> tuple[np.ndarray, np.ndarray, list[float]]:
    bins = np.arange(38.0, 103.01, 0.25, dtype=float)
    times = [0.02, 0.04, 0.06, 0.08, 0.10]
    cqt = np.ones((len(bins), len(times)), dtype=float)
    if not flat:
        original = np.abs(bins - 60.0) <= 0.30
        strong = np.abs(bins - float(strong_midi)) <= 0.30
        cqt[original, :] = 2.0
        cqt[strong, :] = 20.0
    return cqt, bins, times


def build_proof() -> dict[str, Any]:
    source = json.loads(V5_PATH.read_text(encoding="utf-8"))
    accepted = materialize_accepted_family(source)

    cases: list[dict[str, Any]] = []
    for name, strong_midi, expected_midi in (
        ("strong-down-one", 59, 59),
        ("strong-up-one", 61, 61),
        ("strong-original-control", 60, 60),
    ):
        event = _event(60)
        cqt, bins, times = _cqt(strong_midi)
        decision = decide_event_from_prepared_cqt(event, cqt, bins, times)
        passed = int(decision["selectedMidi"]) == expected_midi
        cases.append(
            {
                "name": name,
                "expectedMidi": expected_midi,
                "selectedMidi": int(decision["selectedMidi"]),
                "reason": decision["reason"],
                "passed": passed,
            }
        )

    event = _event(60)
    cqt, bins, _ = _cqt(61)
    insufficient = decide_event_from_prepared_cqt(event, cqt[:, :2], bins, [0.02, 0.04])
    cases.append(
        {
            "name": "insufficient-frames-fail-closed",
            "expectedMidi": 60,
            "selectedMidi": int(insufficient["selectedMidi"]),
            "reason": insufficient["reason"],
            "passed": int(insufficient["selectedMidi"]) == 60 and insufficient["reason"] == "insufficient-frames",
        }
    )

    before = [_event(60, event_index=0, step=4)]
    fixed = apply_fixed_time_pitch_decisions(before, {0: 61})
    after = fixed["events"]
    fixed_ok = (
        fixed["changedEventCount"] == 1
        and fixed["onsetGroupFailClosedCount"] == 0
        and int(after[0]["midi"]) == 61
        and not timing_and_metadata_violations(before, after)
    )
    cases.append(
        {
            "name": "fixed-timing-fingering",
            "expectedMidi": 61,
            "selectedMidi": int(after[0]["midi"]),
            "passed": fixed_ok,
        }
    )

    invalid_before = [_event(60, event_index=0), _event(64, event_index=1)]
    invalid = apply_fixed_time_pitch_decisions(invalid_before, {0: 62, 1: 65})
    fail_closed_ok = (
        invalid["events"] == invalid_before
        and invalid["changedEventCount"] == 0
        and invalid["onsetGroupFailClosedCount"] == 1
    )
    cases.append(
        {
            "name": "invalid-delta-group-fail-closed",
            "passed": fail_closed_ok,
        }
    )

    raw_guard_rejected_wrong_bytes = False
    try:
        verify_raw_audio_identity(b"phase-c-proof-does-not-contain-real-audio")
    except ValueError:
        raw_guard_rejected_wrong_bytes = True

    deterministic_event = _event(60)
    deterministic_cqt, deterministic_bins, deterministic_times = _cqt(59)
    first = decide_event_from_prepared_cqt(
        deterministic_event,
        deterministic_cqt,
        deterministic_bins,
        deterministic_times,
    )
    second = decide_event_from_prepared_cqt(
        deterministic_event,
        deterministic_cqt,
        deterministic_bins,
        deterministic_times,
    )
    deterministic = _canonical_bytes(first) == _canonical_bytes(second)

    source_blobs = {
        "v145Decoder": _git_blob("modal/v145_rhythm_decoder.py"),
        "v147PitchHypothesis": _git_blob("modal/v147_pitch_hypothesis.py"),
        "phaseCPreregistration": _git_blob("docs/v147-phase-c-real-audio-artifact-preregistration.md"),
        "phaseCClarification": _git_blob("docs/v147-phase-c-preregistration-clarification.md"),
    }
    frozen_source_identity_match = (
        source_blobs["v145Decoder"] == EXPECTED_V145_BLOB
        and source_blobs["v147PitchHypothesis"] == EXPECTED_V147_BLOB
        and source_blobs["phaseCPreregistration"] == EXPECTED_PREREG_BLOB
        and source_blobs["phaseCClarification"] == EXPECTED_CLARIFICATION_BLOB
    )

    metrics = {
        "casesTotal": len(cases),
        "casesPassed": sum(1 for row in cases if row["passed"]),
        "acceptedEventCount": len(accepted),
        "acceptedEventIdentityVerified": len(accepted) == EXPECTED_ACCEPTED_EVENT_COUNT,
        "strongAlternates": 2,
        "strongAlternatesRecovered": sum(
            1 for row in cases if row["name"] in {"strong-down-one", "strong-up-one"} and row["passed"]
        ),
        "controlFlips": 0 if next(row for row in cases if row["name"] == "strong-original-control")["passed"] else 1,
        "insufficientFramesKept": 1 if next(row for row in cases if row["name"] == "insufficient-frames-fail-closed")["passed"] else 0,
        "fixedTimingCasesPassed": 1 if fixed_ok else 0,
        "invalidGroupFailClosed": 1 if fail_closed_ok else 0,
        "rawAudioGuardRejectedWrongBytes": raw_guard_rejected_wrong_bytes,
        "deterministic": deterministic,
        "frozenSourceIdentityMatch": frozen_source_identity_match,
    }

    gate = (
        metrics["casesPassed"] == metrics["casesTotal"]
        and metrics["acceptedEventIdentityVerified"]
        and metrics["strongAlternatesRecovered"] == 2
        and metrics["controlFlips"] == 0
        and metrics["insufficientFramesKept"] == 1
        and metrics["fixedTimingCasesPassed"] == 1
        and metrics["invalidGroupFailClosed"] == 1
        and raw_guard_rejected_wrong_bytes
        and deterministic
        and frozen_source_identity_match
    )

    proof = {
        "schema": 14721,
        "phase": "V147-Phase-C-pre-audio",
        "evidenceClass": "cpu-generated-reference-free-pre-audio-contract",
        "gate": "GO" if gate else "STOP",
        "acceptedSource": {
            "eventCount": len(accepted),
            "eventSha256": EXPECTED_ACCEPTED_EVENT_SHA256,
        },
        "expectedRawAudioSha256": EXPECTED_RAW_AUDIO_SHA256,
        "cases": cases,
        "metrics": metrics,
        "sourceBlobs": source_blobs,
        "referenceFree": True,
        "realAudioRead": False,
        "audioDecoded": False,
        "calibrationReferenceRead": False,
        "goldRead": False,
        "calibrationScoreRun": False,
        "candidateConstructed": False,
        "modalGpuUsed": False,
        "productionIntegrated": False,
    }
    payload = dict(proof)
    proof["proofPayloadSha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    return proof


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    proof = build_proof()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("V147_PHASE_C_PRE_AUDIO_PROOF_JSON=" + json.dumps(proof, sort_keys=True, separators=(",", ":")))
    return 0 if proof["gate"] == "GO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
