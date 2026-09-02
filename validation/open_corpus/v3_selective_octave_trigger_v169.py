#!/usr/bin/env python3
"""Frozen V3 reference-blind selective octave trigger.

This module does not read references and does not change the frozen V2 score.
It decides whether an already-computed V2 octave proposal is stable enough to
replace the original Basic Pitch pitch.
"""
from __future__ import annotations

import json
from statistics import median
from typing import Any

from analyze_guitar_techs_harmonic_octave_v169 import EPS
from evaluate_harmonic_candidate_ranking_v2_v169 import (
    FRAME_DELTAS,
    best_candidate_window,
    candidate_features,
    fft_power_frame,
    synthetic_audio,
)

TRIGGER_CONFIGS: tuple[dict[str, Any], ...] = (
    {"id": "C075-M005", "consensusThreshold": 0.75, "medianAdvantageThreshold": 0.05},
    {"id": "C075-M010", "consensusThreshold": 0.75, "medianAdvantageThreshold": 0.10},
    {"id": "C075-M015", "consensusThreshold": 0.75, "medianAdvantageThreshold": 0.15},
    {"id": "C075-M020", "consensusThreshold": 0.75, "medianAdvantageThreshold": 0.20},
    {"id": "C100-M005", "consensusThreshold": 1.00, "medianAdvantageThreshold": 0.05},
    {"id": "C100-M010", "consensusThreshold": 1.00, "medianAdvantageThreshold": 0.10},
    {"id": "C100-M015", "consensusThreshold": 1.00, "medianAdvantageThreshold": 0.15},
    {"id": "C100-M020", "consensusThreshold": 1.00, "medianAdvantageThreshold": 0.20},
)

CONFIG_BY_ID = {row["id"]: row for row in TRIGGER_CONFIGS}


def _winner(scores: dict[int, float], candidates: tuple[int, int, int]) -> int:
    return sorted(candidates, key=lambda midi: (-float(scores[midi]), midi))[0]


def observe_trigger(
    audio,
    sample_rate: int,
    onset: float,
    baseline_pitch: int,
) -> dict[str, Any]:
    """Return reference-blind V3 stability evidence for one baseline event."""
    p = int(baseline_pitch)
    candidates = (p - 12, p, p + 12)

    ordinary_features: dict[int, dict[str, Any]] = {}
    for candidate_pitch in candidates:
        row = best_candidate_window(
            audio,
            sample_rate,
            float(onset),
            0.0,
            candidate_pitch,
        )
        if row is None:
            return {
                "baselinePitch": p,
                "ordinaryV2Winner": p,
                "ordinaryV2ProposalDiffers": False,
                "triggerEligible": False,
                "ineligibleReason": "ordinary-v2-window-unavailable",
                "commonFrameCount": 0,
                "consensusFraction": 0.0,
                "medianAdvantage": 0.0,
                "commonFrameWinners": [],
                "advantages": [],
            }
        ordinary_features[candidate_pitch] = row

    ordinary_scores = {
        candidate_pitch: float(ordinary_features[candidate_pitch]["score"])
        for candidate_pitch in candidates
    }
    ordinary_winner = _winner(ordinary_scores, candidates)
    if ordinary_winner == p:
        return {
            "baselinePitch": p,
            "ordinaryV2Winner": p,
            "ordinaryV2ProposalDiffers": False,
            "triggerEligible": False,
            "ineligibleReason": "ordinary-v2-keeps-baseline",
            "commonFrameCount": 0,
            "consensusFraction": 0.0,
            "medianAdvantage": 0.0,
            "commonFrameWinners": [],
            "advantages": [],
        }

    common_winners: list[int] = []
    advantages: list[float] = []
    per_frame: list[dict[str, Any]] = []
    for delta in FRAME_DELTAS:
        frame = fft_power_frame(audio, sample_rate, float(onset) + float(delta))
        if frame is None:
            return {
                "baselinePitch": p,
                "ordinaryV2Winner": int(ordinary_winner),
                "ordinaryV2ProposalDiffers": True,
                "triggerEligible": False,
                "ineligibleReason": "common-frame-unavailable",
                "commonFrameCount": len(common_winners),
                "consensusFraction": 0.0,
                "medianAdvantage": 0.0,
                "commonFrameWinners": common_winners,
                "advantages": advantages,
            }
        freqs, power = frame
        rows = {
            candidate_pitch: candidate_features(freqs, power, candidate_pitch)
            for candidate_pitch in candidates
        }
        scores = {candidate_pitch: float(rows[candidate_pitch]["score"]) for candidate_pitch in candidates}
        frame_winner = _winner(scores, candidates)
        denom = abs(scores[ordinary_winner]) + abs(scores[p]) + EPS
        advantage = (scores[ordinary_winner] - scores[p]) / denom
        common_winners.append(int(frame_winner))
        advantages.append(float(advantage))
        per_frame.append(
            {
                "delta": float(delta),
                "winner": int(frame_winner),
                "winnerScore": float(scores[ordinary_winner]),
                "baselineScore": float(scores[p]),
                "ordinaryWinnerAdvantage": float(advantage),
            }
        )

    consensus = sum(value == ordinary_winner for value in common_winners) / len(FRAME_DELTAS)
    med_adv = float(median(advantages))
    return {
        "baselinePitch": p,
        "ordinaryV2Winner": int(ordinary_winner),
        "ordinaryV2ProposalDiffers": True,
        "triggerEligible": True,
        "ineligibleReason": None,
        "commonFrameCount": len(common_winners),
        "consensusFraction": float(consensus),
        "medianAdvantage": med_adv,
        "commonFrameWinners": common_winners,
        "advantages": advantages,
        "perFrame": per_frame,
    }


def pitch_for_config(observation: dict[str, Any], config_id: str) -> int:
    if config_id not in CONFIG_BY_ID:
        raise KeyError(f"unknown V3 trigger config: {config_id}")
    p = int(observation["baselinePitch"])
    if not bool(observation["triggerEligible"]):
        return p
    config = CONFIG_BY_ID[config_id]
    if (
        float(observation["consensusFraction"]) >= float(config["consensusThreshold"])
        and float(observation["medianAdvantage"]) >= float(config["medianAdvantageThreshold"])
    ):
        return int(observation["ordinaryV2Winner"])
    return p


def pitches_for_all_configs(observation: dict[str, Any]) -> dict[str, int]:
    return {config["id"]: pitch_for_config(observation, config["id"]) for config in TRIGGER_CONFIGS}


def self_test() -> dict[str, Any]:
    sample_rate = 48000
    # Frozen V2 synthetic fixture: true fundamental is MIDI 45 (110 Hz).
    audio = synthetic_audio((1.00, 0.70, 0.50, 0.35, 0.25, 0.18, 0.12, 0.08), sample_rate=sample_rate)

    # When the baseline itself is 45, ordinary V2 should preserve it and V3
    # must leave every candidate unchanged.
    keep = observe_trigger(audio, sample_rate, 0.30, 45)
    if keep["ordinaryV2Winner"] != 45:
        raise RuntimeError(f"unexpected keep-fixture V2 winner: {keep['ordinaryV2Winner']}")
    if any(value != 45 for value in pitches_for_all_configs(keep).values()):
        raise RuntimeError("V3 altered a baseline that ordinary V2 kept")

    # Present the same signal with an octave-high baseline. The candidate
    # neighborhood becomes {45,57,69}; frozen V2 should propose 45 and the
    # common-frame evidence should agree at all four deltas.
    high = observe_trigger(audio, sample_rate, 0.30, 57)
    if high["ordinaryV2Winner"] != 45:
        raise RuntimeError(f"unexpected octave-high fixture V2 winner: {high['ordinaryV2Winner']}")
    if high["commonFrameCount"] != 4 or high["consensusFraction"] != 1.0:
        raise RuntimeError(f"common-frame consensus fixture failed: {high}")
    if high["medianAdvantage"] <= 0.0:
        raise RuntimeError(f"expected positive octave correction advantage: {high['medianAdvantage']}")

    return {
        "status": "V3_SELECTIVE_TRIGGER_SELF_TEST_PASS",
        "triggerConfigCount": len(TRIGGER_CONFIGS),
        "configIds": [row["id"] for row in TRIGGER_CONFIGS],
        "keepFixtureWinner": keep["ordinaryV2Winner"],
        "octaveHighFixtureWinner": high["ordinaryV2Winner"],
        "octaveHighConsensusFraction": high["consensusFraction"],
        "octaveHighMedianAdvantage": high["medianAdvantage"],
        "referenceRead": False,
        "guitarSetJamsNoteEventsRead": 0,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }


if __name__ == "__main__":
    print(json.dumps(self_test(), indent=2, sort_keys=True))
