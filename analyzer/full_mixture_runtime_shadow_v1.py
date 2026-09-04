from __future__ import annotations

from pathlib import Path
from typing import Any


def _is_trusted_full_mixture_observation_v1(observation: Any) -> bool:
    if not isinstance(observation, dict):
        return False

    provenance = observation.get("provenance")
    diagnostics = observation.get("diagnostics")
    if not isinstance(provenance, dict) or not isinstance(diagnostics, dict):
        return False

    wav_adapter = diagnostics.get("wavAdapter")
    if not isinstance(wav_adapter, dict):
        return False

    return all(
        (
            provenance.get("sourceKind") == "full-mixture",
            provenance.get("sourceIdentity") == "request-audio",
            provenance.get("referenceBlind") is True,
            provenance.get("referenceRuntimeInputUsed") is False,
            diagnostics.get("referenceBlind") is True,
            diagnostics.get("carrierInputUsed") is False,
            diagnostics.get("transcribedEventInputUsed") is False,
            wav_adapter.get("fullMixtureOnly") is True,
            wav_adapter.get("separatedCarrierUsed") is False,
            wav_adapter.get("transcribedEventInputUsed") is False,
        )
    )


def estimate_full_mixture_runtime_shadow_v1(
    normalized_wav_path: str | Path | None,
) -> dict[str, Any] | None:
    """Return admitted research-only mixture structure or fail open to None."""
    if normalized_wav_path is None:
        return None

    try:
        wav_path = Path(normalized_wav_path)
        if not wav_path.is_file():
            return None

        from full_mixture_wav_adapter_v1 import (
            estimate_full_mixture_structure_from_wav_v1,
        )

        observation = estimate_full_mixture_structure_from_wav_v1(wav_path)
    except Exception:
        return None

    if not _is_trusted_full_mixture_observation_v1(observation):
        return None

    return observation
