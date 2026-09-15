#!/usr/bin/env python3
"""Synthetic-only owner-aware guard for V3 physical-template research iteration 2.

Iteration 1 is imported read-only and remains the sole source of candidate
eligibility and NNLS necessity. This wrapper can only reject an iteration-1
PASS; it can never promote an iteration-1 failure.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import physical_template_plausibility_v3 as base

CONTRACT = "songsterr-fresh-v3-physical-template-owner-aware-synthetic-research-v2"
VERSION = 2
OVERLAP_BIN_RADIUS = 1
MIN_OWNER_EXCLUSIVE_SUPPORTED = 2
MIN_SELECTED_EXCLUSIVE_SUPPORTED = 2

EXPECTED_BASE_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_BASE_VERSION = 1


def _base_contract_ok() -> bool:
    return bool(
        getattr(base, "CONTRACT", None) == EXPECTED_BASE_CONTRACT
        and getattr(base, "VERSION", None) == EXPECTED_BASE_VERSION
    )


def _bins_overlap(bin_a: int, bin_b: int) -> bool:
    return abs(int(bin_a) - int(bin_b)) <= OVERLAP_BIN_RADIUS


def _supported_bins(template: dict[str, Any]) -> list[int]:
    bins = list(template.get("bins", []))
    supported = list(template.get("supported", []))
    if len(bins) != len(supported):
        return []
    return [int(bin_index) for bin_index, flag in zip(bins, supported) if flag is True]


def _exclusive_supported_bins(
    source_template: dict[str, Any],
    other_template: dict[str, Any],
) -> list[int]:
    source_supported = _supported_bins(source_template)
    other_bins = [int(value) for value in other_template.get("bins", [])]
    return [
        source_bin
        for source_bin in source_supported
        if not any(_bins_overlap(source_bin, other_bin) for other_bin in other_bins)
    ]


def evaluate_owner_aware_composite(
    selected_midi: int,
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Apply frozen iteration-1 composite, then the prospective lower-owner guard."""

    if not _base_contract_ok():
        return {
            "passed": False,
            "status": "BASE_CONTRACT_MISMATCH",
            "selectedMidi": int(selected_midi) if isinstance(selected_midi, (int, np.integer)) else selected_midi,
            "promotedFromBaseFailure": False,
        }

    base_result = base.evaluate_composite_necessity(selected_midi, innovation, frequencies)
    if base_result.get("passed") is not True:
        return {
            "passed": False,
            "status": str(base_result.get("status", "BASE_COMPOSITE_FAILED")),
            "selectedMidi": base_result.get("selectedMidi", selected_midi),
            "promotedFromBaseFailure": False,
            "baseComposite": base_result,
            "credibleLowerOwners": [],
            "vetoingOwners": [],
        }

    selected_midi = int(selected_midi)
    selected_template = base_result.get("selectedTemplate")
    if not isinstance(selected_template, dict) or selected_template.get("valid") is not True:
        return {
            "passed": False,
            "status": "BASE_PASS_WITHOUT_VALID_SELECTED_TEMPLATE",
            "selectedMidi": selected_midi,
            "promotedFromBaseFailure": False,
            "baseComposite": base_result,
            "credibleLowerOwners": [],
            "vetoingOwners": [],
        }

    owner_rows: list[dict[str, Any]] = []
    credible_rows: list[dict[str, Any]] = []
    veto_rows: list[dict[str, Any]] = []

    for owner_midi in range(base.PLAYABLE_MIDI_MIN, selected_midi):
        owner_template = base.evaluate_candidate_template(owner_midi, innovation, frequencies)
        if owner_template.get("valid") is not True:
            continue

        owner_exclusive_bins = _exclusive_supported_bins(owner_template, selected_template)
        selected_exclusive_bins = _exclusive_supported_bins(selected_template, owner_template)
        credible = len(owner_exclusive_bins) >= MIN_OWNER_EXCLUSIVE_SUPPORTED
        veto = bool(
            credible
            and len(selected_exclusive_bins) < MIN_SELECTED_EXCLUSIVE_SUPPORTED
        )
        row = {
            "ownerMidi": int(owner_midi),
            "ownerCents": float(owner_template.get("cents", 0.0)),
            "ownerExclusiveSupportedBins": owner_exclusive_bins,
            "ownerExclusiveSupportedCount": len(owner_exclusive_bins),
            "selectedExclusiveSupportedBins": selected_exclusive_bins,
            "selectedExclusiveSupportedCount": len(selected_exclusive_bins),
            "credible": credible,
            "veto": veto,
        }
        owner_rows.append(row)
        if credible:
            credible_rows.append(row)
        if veto:
            veto_rows.append(row)

    if veto_rows:
        return {
            "passed": False,
            "status": "LOWER_OWNER_EXPLAINS_SELECTED",
            "selectedMidi": selected_midi,
            "promotedFromBaseFailure": False,
            "baseComposite": base_result,
            "credibleLowerOwners": credible_rows,
            "vetoingOwners": veto_rows,
            "eligibleLowerOwnerCount": len(owner_rows),
        }

    return {
        "passed": True,
        "status": "PASS",
        "selectedMidi": selected_midi,
        "promotedFromBaseFailure": False,
        "baseComposite": base_result,
        "credibleLowerOwners": credible_rows,
        "vetoingOwners": [],
        "eligibleLowerOwnerCount": len(owner_rows),
    }
