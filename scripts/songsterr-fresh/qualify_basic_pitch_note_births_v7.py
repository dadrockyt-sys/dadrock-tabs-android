#!/usr/bin/env python3
"""Boundary-aware research qualifier using frozen V7/V3 evidence.

This successor leaves frozen V2/V6/V3/V7 files unchanged. It reuses frozen V2
WAV/model validation and clip-start routing semantics. Ordinary in-clip events
use frozen V7 onset innovation; clip-start events use the prospectively frozen
V7 one-sided post-spectrum adapter.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6
import onset_birth_corroboration_v7 as frozen_v7
import qualify_basic_pitch_note_births_v2 as frozen_v2
from clip_start_pitch_presence_v7 import (
    METHOD as CLIP_START_METHOD,
    WINDOW_SAMPLES as CLIP_START_WINDOW_SAMPLES,
    classify_clip_start_pitch_presence_v7,
)

CONTRACT = "songsterr-fresh-model-note-qualification-v7-boundary-research"
VERSION = 7
METHOD = "v7-onset-birth-plus-clip-start-post-spectrum-wrapper-v1"
NORMAL_METHOD = "v7-v3-evidence-significance-on-frozen-v6-onset-innovation"

_NORMAL_UNAVAILABLE_STATUSES = {
    "FROZEN_DEPENDENCY_CONTRACT_MISMATCH",
    "MIDI_INTEGER_REQUIRED",
    "MIDI_OUTSIDE_PLAYABLE_RANGE",
    "ONSET_SAMPLE_INTEGER_REQUIRED",
    "ONSET_BEFORE_AUDIO",
    "AUDIO_COERCION_FAILED",
    "FINITE_MONO_AUDIO_REQUIRED",
    "REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO",
    "FINITE_EXACT_FRAME_REQUIRED",
    "PRE_POST_NOVELTY_FRAMES_REQUIRED",
    "INSUFFICIENT_LOW_AUDIO_SUPPORT",
    "INSUFFICIENT_NO_FEATURE_BINS",
    "INSUFFICIENT_LOW_FEATURE_ENERGY",
    "V6_ONSET_INNOVATION_FAILED",
    "V6_ONSET_RESULT_NOT_MAPPING",
    "V3_RESULT_NOT_MAPPING",
}


class QualificationV7Error(RuntimeError):
    pass


def _normal_v7_classification(
    audio: np.ndarray,
    onset_sample: int,
    selected_midi: int,
) -> dict[str, Any]:
    result = frozen_v7.evaluate_in_memory_audio_event(
        audio,
        onset_sample,
        selected_midi,
    )
    if not isinstance(result, dict):
        return {
            "classification": frozen_v6.CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "reason": "V7_RESULT_NOT_MAPPING",
            "fit": {},
        }

    status = str(result.get("status", "V7_STATUS_MISSING"))
    if result.get("passed") is True:
        classification = frozen_v6.CLASS_CORROBORATED
    elif status == frozen_v2.NO_BIRTH_REASON:
        # Preserve frozen V2 semantics for a fully contextualized proposed birth.
        classification = frozen_v6.CLASS_NOT_CORROBORATED
    elif status in _NORMAL_UNAVAILABLE_STATUSES:
        classification = frozen_v6.CLASS_INSUFFICIENT
    else:
        classification = frozen_v6.CLASS_NOT_CORROBORATED

    return {
        "classification": classification,
        "selectedMidi": selected_midi,
        "reason": status,
        "fit": result,
    }


def _map_classification(result: dict[str, Any], normal_mode: bool) -> str:
    classification = result.get("classification")
    reason = result.get("reason")
    if classification == frozen_v6.CLASS_CORROBORATED:
        return "corroborated"
    if classification == frozen_v6.CLASS_NOT_CORROBORATED:
        return "rejected"
    if (
        normal_mode
        and classification == frozen_v6.CLASS_INSUFFICIENT
        and reason == frozen_v2.NO_BIRTH_REASON
    ):
        return "rejected"
    if classification == frozen_v6.CLASS_INSUFFICIENT:
        return "insufficient"
    raise QualificationV7Error(f"UNEXPECTED_CLASSIFICATION:{classification}")


def classify_proposal(audio: np.ndarray, note: dict[str, Any]) -> dict[str, Any]:
    original_onset_sample = int(round(float(note["startSeconds"]) * frozen_v6.SAMPLE_RATE))
    if original_onset_sample < 0:
        raise QualificationV7Error("NEGATIVE_ONSET_SAMPLE")

    clip_start_mode = original_onset_sample < frozen_v2.REQUIRED_LEFT_CONTEXT_SAMPLES
    if clip_start_mode:
        try:
            result = classify_clip_start_pitch_presence_v7(
                audio,
                original_onset_sample,
                int(note["midi"]),
            )
        except Exception as exc:
            return {
                "noteId": note["noteId"],
                "midi": int(note["midi"]),
                "startSeconds": float(note["startSeconds"]),
                "status": "insufficient",
                "independentOnsetConfidence": 0.0,
                "provenance": {
                    "wrapperMethod": METHOD,
                    "method": CLIP_START_METHOD,
                    "qualificationMode": "clip-start-one-sided-pitch-presence-v7",
                    "classification": frozen_v6.CLASS_INSUFFICIENT,
                    "reason": f"CLIP_START_V7_EXCEPTION:{type(exc).__name__}",
                    "leftBoundaryZeroPaddingSamples": 0,
                    "syntheticPreContextUsed": False,
                    "originalOnsetSample": original_onset_sample,
                    "requiredLeftContextSamples": frozen_v2.REQUIRED_LEFT_CONTEXT_SAMPLES,
                    "requiredRightContextSamples": frozen_v2.REQUIRED_RIGHT_CONTEXT_SAMPLES,
                    "clipStartWindowSamples": CLIP_START_WINDOW_SAMPLES,
                    "candidateConfidenceReadForDecision": False,
                },
            }
        mode = "clip-start-one-sided-pitch-presence-v7"
        row_method = CLIP_START_METHOD
    else:
        result = _normal_v7_classification(
            audio,
            original_onset_sample,
            int(note["midi"]),
        )
        mode = "normal-in-clip-onset-birth-v7"
        row_method = NORMAL_METHOD

    status = _map_classification(result, normal_mode=not clip_start_mode)
    fit = result.get("fit") if isinstance(result.get("fit"), dict) else {}
    independent_onset_confidence = 1.0 if status == "corroborated" else 0.0

    return {
        "noteId": note["noteId"],
        "midi": int(note["midi"]),
        "startSeconds": float(note["startSeconds"]),
        "status": status,
        "independentOnsetConfidence": independent_onset_confidence,
        "provenance": {
            "wrapperMethod": METHOD,
            "method": row_method,
            "qualificationMode": mode,
            "classification": result.get("classification"),
            "reason": result.get("reason"),
            "leftBoundaryZeroPaddingSamples": 0,
            "syntheticPreContextUsed": False,
            "originalOnsetSample": original_onset_sample,
            "requiredLeftContextSamples": frozen_v2.REQUIRED_LEFT_CONTEXT_SAMPLES,
            "requiredRightContextSamples": frozen_v2.REQUIRED_RIGHT_CONTEXT_SAMPLES,
            "clipStartWindowSamples": CLIP_START_WINDOW_SAMPLES if clip_start_mode else None,
            "analysisRms": fit.get("analysisRms"),
            "innovationEnergy": fit.get("innovationEnergy"),
            "necessityFraction": fit.get("necessityFraction"),
            "candidateEvidenceFraction": fit.get("candidateEvidenceFraction"),
            "credibleLowerOwners": fit.get("credibleLowerOwners", []),
            "vetoingOwners": fit.get("vetoingOwners", []),
            "evidenceKind": fit.get("evidenceKind", "ordinary-in-clip-onset-innovation"),
            "v7Status": fit.get("v7Status", fit.get("status")),
            "v3Composite": fit.get("v3Composite"),
            "candidateConfidenceReadForDecision": False,
        },
    }


def qualify(audio_path: Path, model_notes_path: Path) -> dict[str, Any]:
    model_payload = json.loads(model_notes_path.read_text(encoding="utf-8"))
    notes, identity = frozen_v2.validate_model_notes(model_payload)
    audio, audio_details = frozen_v2.load_analysis_audio(audio_path)

    proposals = [classify_proposal(audio, note) for note in notes]
    counts = {"corroborated": 0, "rejected": 0, "insufficient": 0}
    mode_counts = {
        "clip-start-one-sided-pitch-presence-v7": 0,
        "normal-in-clip-onset-birth-v7": 0,
    }
    for row in proposals:
        counts[row["status"]] += 1
        mode_counts[row["provenance"]["qualificationMode"]] += 1

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "referenceBlind": True,
        "modelNoteIdentitySha256": identity["sha256"],
        "method": METHOD,
        "candidateConfidenceUsedForDecision": False,
        "independentOfBasicPitchCandidateConfidence": True,
        "referenceTabUsed": False,
        "proposals": proposals,
        "diagnostics": {
            "proposalCount": len(proposals),
            "statusCounts": counts,
            "modeCounts": mode_counts,
            "confidenceSemantics": "binary-corroboration-indicator-not-calibrated-probability",
            "v7DependencyContractIntegrity": bool(frozen_v7._dependency_contract_ok()),
            "clipStartUsesSyntheticPreContext": False,
            "clipStartWindowSamples": CLIP_START_WINDOW_SAMPLES,
            "clipStartEvidenceKind": "clip-start-post-spectrum-evidence",
            "normalEvidenceKind": "ordinary-in-clip-onset-innovation",
            "minimumAnalysisRms": frozen_v6.MIN_ANALYSIS_RMS,
            "minimumInnovationEnergy": frozen_v6.MIN_INNOVATION_ENERGY,
            "necessityFractionMin": frozen_v7.EXPECTED_NECESSITY_FRACTION_MIN,
            "candidateEvidenceFractionMin": frozen_v7.EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN,
            "requiredLeftContextSamples": frozen_v2.REQUIRED_LEFT_CONTEXT_SAMPLES,
            "requiredRightContextSamples": frozen_v2.REQUIRED_RIGHT_CONTEXT_SAMPLES,
            "audio": audio_details,
        },
        "provenance": {
            "audioPathName": audio_path.name,
            "audioSha256": frozen_v2.sha256_file(audio_path),
            "modelNotesPathName": model_notes_path.name,
            "modelNoteIdentity": dict(identity),
            "modelInvokedByQualifier": False,
            "gpuInvoked": False,
            "networkInvoked": False,
            "candidateConfidenceReadForDecision": False,
            "referenceTabUsed": False,
            "legacyV143ScorerImported": False,
            "syntheticPreContextUsed": False,
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
    output = qualify(Path(args.audio), Path(args.model_notes))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(output, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        frozen_v2.canonical_json(
            {
                "contract": output["contract"],
                "version": output["version"],
                "method": output["method"],
                "modelNoteIdentitySha256": output["modelNoteIdentitySha256"],
                "diagnostics": output["diagnostics"],
                "provenance": output["provenance"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
