#!/usr/bin/env python3
"""Reference-blind EGSet12 adapter for the frozen Songsterr Fresh positive core.

This adapter is research-only. It reuses the already-frozen V2 model-note
validator/audio loader and the already-frozen fail-closed positive-core
composer. It defines no new threshold, rescue rule, candidate subset, score,
or customer/production decision.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import qualify_basic_pitch_note_births_v2 as frozen_v2
import onset_birth_corroboration_v6 as frozen_v6
import v7_fail_closed_positive_core_v1 as positive_core

CONTRACT = "songsterr-fresh-egset12-positive-core-adapter-v1"
VERSION = 1
EXPECTED_V2_CONTRACT = "songsterr-fresh-model-note-qualification-v2"
EXPECTED_V2_VERSION = 2
EXPECTED_POSITIVE_CORE_CONTRACT = "songsterr-fresh-v7-fail-closed-positive-core-v1"
EXPECTED_POSITIVE_CORE_VERSION = 1

STATE_TO_STATUS = {
    positive_core.POSITIVE_CORE_CANDIDATE: "corroborated",
    positive_core.PROTECTION_REJECTED: "rejected",
    positive_core.UNRESOLVED_SUPPORT_OR_CONTEXT: "insufficient",
}


class Egset12AdapterError(RuntimeError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _dependency_guard() -> None:
    if getattr(frozen_v2, "CONTRACT", None) != EXPECTED_V2_CONTRACT or getattr(frozen_v2, "VERSION", None) != EXPECTED_V2_VERSION:
        raise Egset12AdapterError("FROZEN_V2_DEPENDENCY_MISMATCH")
    if getattr(positive_core, "CONTRACT", None) != EXPECTED_POSITIVE_CORE_CONTRACT or getattr(positive_core, "VERSION", None) != EXPECTED_POSITIVE_CORE_VERSION:
        raise Egset12AdapterError("FROZEN_POSITIVE_CORE_DEPENDENCY_MISMATCH")
    if getattr(frozen_v6, "SAMPLE_RATE", None) != 44100 or getattr(frozen_v6, "FFT_SIZE", None) != 8192:
        raise Egset12AdapterError("FROZEN_DSP_GRID_MISMATCH")


def map_composition_state(state: str) -> str:
    try:
        return STATE_TO_STATUS[state]
    except KeyError as exc:
        raise Egset12AdapterError(f"UNEXPECTED_COMPOSITION_STATE:{state}") from exc


def qualify_reference_blind(audio_path: Path, model_notes_path: Path) -> dict[str, Any]:
    _dependency_guard()
    payload = json.loads(model_notes_path.read_text(encoding="utf-8"))
    notes, identity = frozen_v2.validate_model_notes(payload)
    audio, audio_details = frozen_v2.load_analysis_audio(audio_path)
    frequencies = np.fft.rfftfreq(frozen_v6.FFT_SIZE, d=1.0 / float(frozen_v6.SAMPLE_RATE))

    proposals: list[dict[str, Any]] = []
    counts = {"corroborated": 0, "rejected": 0, "insufficient": 0}
    for note in notes:
        onset_sample = int(round(note["startSeconds"] * frozen_v6.SAMPLE_RATE))
        decision = positive_core.evaluate_fail_closed_positive_core(
            audio,
            onset_sample,
            note["midi"],
            frequencies,
        )
        if decision.get("selectedMidi") != note["midi"]:
            raise Egset12AdapterError(f"SELECTED_MIDI_IDENTITY_MISMATCH:{note['noteId']}")
        state = decision.get("compositionState")
        if not isinstance(state, str):
            raise Egset12AdapterError(f"COMPOSITION_STATE_MISSING:{note['noteId']}")
        status = map_composition_state(state)
        counts[status] += 1
        proposals.append({
            "noteId": note["noteId"],
            "midi": note["midi"],
            "startSeconds": note["startSeconds"],
            "status": status,
            "compositionState": state,
            "protectionRejectionReasons": list(decision.get("protectionRejectionReasons") or []),
            "supportEligible": decision.get("supportEligible"),
            "candidateEvidencePass": decision.get("candidateEvidencePass"),
            "noLowerOwnerVeto": decision.get("noLowerOwnerVeto"),
            "kktStrictRawNecessityCertified": decision.get("kktStrictRawNecessityCertified"),
            "dependencyDiagnostic": decision.get("dependencyDiagnostic"),
        })

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "referenceBlind": True,
        "method": "frozen-v2-input-plumbing-plus-frozen-v7-fail-closed-positive-core-v1",
        "modelNoteIdentitySha256": identity["sha256"],
        "candidateConfidenceUsedForDecision": False,
        "referenceAnnotationUsed": False,
        "historicalRaw001Applied": False,
        "rankTopKDefined": False,
        "weightedScoreDefined": False,
        "reattackFallbackDefined": False,
        "proposals": proposals,
        "diagnostics": {
            "proposalCount": len(proposals),
            "statusCounts": counts,
            "audio": audio_details,
            "analysisSampleRate": frozen_v6.SAMPLE_RATE,
            "fftSize": frozen_v6.FFT_SIZE,
        },
        "provenance": {
            "audioPathName": audio_path.name,
            "audioSha256": frozen_v2.sha256_file(audio_path),
            "modelNotesPathName": model_notes_path.name,
            "modelNoteIdentity": dict(identity),
            "modelInvokedByAdapter": False,
            "networkInvokedByAdapter": False,
            "referenceAnnotationUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--model-notes", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = qualify_reference_blind(Path(args.audio), Path(args.model_notes))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": output["contract"],
        "version": output["version"],
        "modelNoteIdentitySha256": output["modelNoteIdentitySha256"],
        "statusCounts": output["diagnostics"]["statusCounts"],
        "referenceAnnotationUsed": output["referenceAnnotationUsed"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
