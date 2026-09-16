#!/usr/bin/env python3
"""Synthetic/local successor integration for frozen V3 iteration 3.

This module is a research-only successor to frozen V6. It does not expose any
file, network, model, workflow, dataset, subprocess, or repository-loading
entry point. It accepts only in-memory arrays.

Frozen integration contract:
  docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_INTEGRATION_PRE.md
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6
import physical_template_plausibility_v3_iteration3 as frozen_v3

CONTRACT = "songsterr-fresh-onset-birth-v3-successor-integration-research-v7"
VERSION = 7

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-evidence-significance-synthetic-research-v3"
EXPECTED_V3_VERSION = 3

EXPECTED_SAMPLE_RATE = 44100
EXPECTED_FRAME_SAMPLES = 2048
EXPECTED_HOP_SAMPLES = 256
EXPECTED_FFT_SIZE = 8192
EXPECTED_FRAME_END_OFFSETS = tuple(range(-6 * EXPECTED_HOP_SAMPLES, 7 * EXPECTED_HOP_SAMPLES, EXPECTED_HOP_SAMPLES))
EXPECTED_POST_END_MAX = 4 * EXPECTED_HOP_SAMPLES
EXPECTED_PLAYABLE_MIDI_MIN = 40
EXPECTED_PLAYABLE_MIDI_MAX = 88
EXPECTED_MIN_ANALYSIS_RMS = 1e-5
EXPECTED_MIN_INNOVATION_ENERGY = 1e-6
EXPECTED_V6_TEMPLATE_FUNDAMENTAL_RATIO = 0.20
EXPECTED_NECESSITY_FRACTION_MIN = 0.01
EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN = 0.10


def _dependency_contract_ok() -> bool:
    return bool(
        getattr(frozen_v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(frozen_v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(frozen_v6, "SAMPLE_RATE", None) == EXPECTED_SAMPLE_RATE
        and getattr(frozen_v6, "FRAME_SAMPLES", None) == EXPECTED_FRAME_SAMPLES
        and getattr(frozen_v6, "HOP_SAMPLES", None) == EXPECTED_HOP_SAMPLES
        and getattr(frozen_v6, "FFT_SIZE", None) == EXPECTED_FFT_SIZE
        and tuple(getattr(frozen_v6, "FRAME_END_OFFSETS", ())) == EXPECTED_FRAME_END_OFFSETS
        and getattr(frozen_v6, "POST_END_MAX", None) == EXPECTED_POST_END_MAX
        and getattr(frozen_v6, "PLAYABLE_MIDI_MIN", None) == EXPECTED_PLAYABLE_MIDI_MIN
        and getattr(frozen_v6, "PLAYABLE_MIDI_MAX", None) == EXPECTED_PLAYABLE_MIDI_MAX
        and getattr(frozen_v6, "MIN_ANALYSIS_RMS", None) == EXPECTED_MIN_ANALYSIS_RMS
        and getattr(frozen_v6, "MIN_INNOVATION_ENERGY", None) == EXPECTED_MIN_INNOVATION_ENERGY
        and getattr(frozen_v6, "TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN", None)
        == EXPECTED_V6_TEMPLATE_FUNDAMENTAL_RATIO
        and getattr(frozen_v6, "NECESSITY_FRACTION_MIN", None) == EXPECTED_NECESSITY_FRACTION_MIN
        and getattr(frozen_v3, "CONTRACT", None) == EXPECTED_V3_CONTRACT
        and getattr(frozen_v3, "VERSION", None) == EXPECTED_V3_VERSION
        and getattr(frozen_v3, "MIN_CANDIDATE_EVIDENCE_FRACTION", None)
        == EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN
    )


def _failure(status: str, selected_midi: Any = None, **diagnostics: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "passed": False,
        "status": status,
        "successorContract": CONTRACT,
        "successorVersion": VERSION,
        "promotedFromV3Failure": False,
    }
    if selected_midi is not None:
        row["selectedMidi"] = selected_midi
    row.update(diagnostics)
    return row


def _validated_selected_midi(selected_midi: Any) -> tuple[int | None, dict[str, Any] | None]:
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        return None, _failure("MIDI_INTEGER_REQUIRED", selected_midi)
    value = int(selected_midi)
    if not EXPECTED_PLAYABLE_MIDI_MIN <= value <= EXPECTED_PLAYABLE_MIDI_MAX:
        return None, _failure("MIDI_OUTSIDE_PLAYABLE_RANGE", value)
    return value, None


def _extract_necessity_fraction(v3_result: dict[str, Any]) -> float | None:
    iteration2_result = v3_result.get("iteration2Composite")
    if not isinstance(iteration2_result, dict):
        return None
    base_result = iteration2_result.get("baseComposite")
    if not isinstance(base_result, dict):
        return None
    value = base_result.get("necessityFraction")
    if not isinstance(value, (int, float, np.integer, np.floating)):
        return None
    numeric = float(value)
    return numeric if math.isfinite(numeric) else None


def expected_frequency_grid() -> np.ndarray:
    """Return the frozen V6 FFT frequency grid as a fresh in-memory array."""

    return np.fft.rfftfreq(EXPECTED_FFT_SIZE, d=1.0 / float(EXPECTED_SAMPLE_RATE))


def evaluate_in_memory_innovation(
    selected_midi: int,
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Map frozen V3 iteration-3 evidence into the V7 research successor."""

    if not _dependency_contract_ok():
        return _failure("FROZEN_DEPENDENCY_CONTRACT_MISMATCH", selected_midi)

    midi, error = _validated_selected_midi(selected_midi)
    if error is not None:
        return error
    assert midi is not None

    v3_result = frozen_v3.evaluate_evidence_significance_composite(
        midi,
        innovation,
        frequencies,
    )
    if not isinstance(v3_result, dict):
        return _failure("V3_RESULT_NOT_MAPPING", midi)

    necessity_fraction = _extract_necessity_fraction(v3_result)

    if v3_result.get("passed") is not True:
        row = dict(v3_result)
        row["passed"] = False
        row["successorContract"] = CONTRACT
        row["successorVersion"] = VERSION
        row["promotedFromV3Failure"] = False
        row["v3Composite"] = v3_result
        if necessity_fraction is not None:
            row["necessityFraction"] = necessity_fraction
        return row

    candidate_evidence_fraction = v3_result.get("candidateEvidenceFraction")
    credible_lower_owners = v3_result.get("credibleLowerOwners")
    vetoing_owners = v3_result.get("vetoingOwners")

    if necessity_fraction is None:
        return _failure(
            "V3_PASS_WITHOUT_FINITE_NECESSITY_FRACTION",
            midi,
            v3Composite=v3_result,
        )
    if necessity_fraction < EXPECTED_NECESSITY_FRACTION_MIN:
        return _failure(
            "V3_PASS_BELOW_FROZEN_NECESSITY_THRESHOLD",
            midi,
            necessityFraction=necessity_fraction,
            v3Composite=v3_result,
        )
    if not isinstance(candidate_evidence_fraction, (int, float, np.integer, np.floating)):
        return _failure(
            "V3_PASS_WITHOUT_NUMERIC_CANDIDATE_EVIDENCE_FRACTION",
            midi,
            necessityFraction=necessity_fraction,
            v3Composite=v3_result,
        )
    evidence_fraction = float(candidate_evidence_fraction)
    if not math.isfinite(evidence_fraction):
        return _failure(
            "V3_PASS_WITHOUT_FINITE_CANDIDATE_EVIDENCE_FRACTION",
            midi,
            necessityFraction=necessity_fraction,
            candidateEvidenceFraction=evidence_fraction,
            v3Composite=v3_result,
        )
    if evidence_fraction < EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN:
        return _failure(
            "V3_PASS_BELOW_FROZEN_EVIDENCE_THRESHOLD",
            midi,
            necessityFraction=necessity_fraction,
            candidateEvidenceFraction=evidence_fraction,
            v3Composite=v3_result,
        )
    if not isinstance(credible_lower_owners, list) or not isinstance(vetoing_owners, list):
        return _failure(
            "V3_PASS_WITHOUT_LOWER_OWNER_DIAGNOSTICS",
            midi,
            necessityFraction=necessity_fraction,
            candidateEvidenceFraction=evidence_fraction,
            v3Composite=v3_result,
        )
    if vetoing_owners:
        return _failure(
            "V3_PASS_WITH_VETOING_LOWER_OWNER",
            midi,
            necessityFraction=necessity_fraction,
            candidateEvidenceFraction=evidence_fraction,
            credibleLowerOwners=credible_lower_owners,
            vetoingOwners=vetoing_owners,
            v3Composite=v3_result,
        )

    return {
        "passed": True,
        "status": "PASS",
        "selectedMidi": midi,
        "successorContract": CONTRACT,
        "successorVersion": VERSION,
        "promotedFromV3Failure": False,
        "necessityFraction": necessity_fraction,
        "candidateEvidenceFraction": evidence_fraction,
        "minimumCandidateEvidenceFraction": EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN,
        "credibleLowerOwners": credible_lower_owners,
        "vetoingOwners": vetoing_owners,
        "v3Composite": v3_result,
    }


def evaluate_in_memory_audio_event(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
) -> dict[str, Any]:
    """Apply frozen V6 onset innovation, then frozen V3 iteration 3, in memory."""

    if not _dependency_contract_ok():
        return _failure("FROZEN_DEPENDENCY_CONTRACT_MISMATCH", selected_midi)

    midi, error = _validated_selected_midi(selected_midi)
    if error is not None:
        return error
    assert midi is not None

    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        return _failure("ONSET_SAMPLE_INTEGER_REQUIRED", midi)
    onset = int(onset_sample)
    if onset < 0:
        return _failure("ONSET_BEFORE_AUDIO", midi)

    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        return _failure("AUDIO_COERCION_FAILED", midi, errorType=type(exc).__name__)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        return _failure("FINITE_MONO_AUDIO_REQUIRED", midi)

    try:
        onset_result = frozen_v6._onset_innovation_spectrum(values, onset)
    except frozen_v6.CorroborationError as exc:
        return _failure(str(exc), midi)
    except Exception as exc:
        return _failure("V6_ONSET_INNOVATION_FAILED", midi, errorType=type(exc).__name__)

    if not isinstance(onset_result, dict):
        return _failure("V6_ONSET_RESULT_NOT_MAPPING", midi)
    if onset_result.get("status") != "OK":
        diagnostics = {
            key: value
            for key, value in onset_result.items()
            if key != "innovation"
        }
        return _failure(str(onset_result.get("status", "V6_ONSET_NOT_OK")), midi, onsetDiagnostics=diagnostics)

    innovation = onset_result.get("innovation")
    frequencies = expected_frequency_grid()
    composite = evaluate_in_memory_innovation(midi, innovation, frequencies)
    row = dict(composite)
    row["analysisRms"] = onset_result.get("analysisRms")
    row["innovationEnergy"] = onset_result.get("innovationEnergy")
    row["onsetSourceContract"] = EXPECTED_V6_CONTRACT
    return row
