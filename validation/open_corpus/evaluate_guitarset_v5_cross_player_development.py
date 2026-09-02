#!/usr/bin/env python3
"""Exact cross-player GuitarSet V5 development evaluator.

All admissible 02/04/05 tracks are development. Prospective players 00/01/03
remain forbidden. This script reads no audio and never imports/runs Basic Pitch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from score_guitarset_v3_development_candidates import (
    DEV_PLAYERS,
    EVAL_PLAYERS,
    EXPECTED_TRACK_COUNT,
    KNOWN_ANOMALIES,
    load_reference_events,
    metric,
    score,
    sha256_file,
    verify_candidates,
    verify_reference_root,
)

TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}
PITCH_FLOORS = (72, 76, 79)
MAX_DURATIONS = (0.20, 0.25, 0.30, 0.35)
ADVANTAGE_THRESHOLDS = (0.05, 0.10, 0.15, 0.20)
CONSENSUS_THRESHOLD = 1.00
MIN_CHANGED_PER_PLAYER = 5


def config_id(pitch_floor: int, max_duration: float, advantage: float) -> str:
    return f"P{pitch_floor}-D{int(round(max_duration * 100)):03d}-M{int(round(advantage * 100)):03d}"


CONFIGS: tuple[dict[str, Any], ...] = tuple(
    {
        "id": config_id(pitch_floor, max_duration, advantage),
        "minBaselinePitch": pitch_floor,
        "maxDurationSeconds": max_duration,
        "consensusThreshold": CONSENSUS_THRESHOLD,
        "medianAdvantageThreshold": advantage,
    }
    for pitch_floor in PITCH_FLOORS
    for max_duration in MAX_DURATIONS
    for advantage in ADVANTAGE_THRESHOLDS
)


def _selected(event: dict[str, Any], observation: dict[str, Any], config: dict[str, Any]) -> bool:
    baseline_pitch = int(event["pitch"])
    ordinary_winner = int(observation["ordinaryV2Winner"])
    duration = float(event["end"]) - float(event["start"])
    return (
        bool(observation["triggerEligible"])
        and bool(observation["ordinaryV2ProposalDiffers"])
        and ordinary_winner == baseline_pitch - 12
        and baseline_pitch >= int(config["minBaselinePitch"])
        and duration <= float(config["maxDurationSeconds"])
        and float(observation["consensusFraction"]) >= float(config["consensusThreshold"])
        and float(observation["medianAdvantage"]) >= float(config["medianAdvantageThreshold"])
    )


def _event_with_pitch(event: dict[str, Any], pitch: int) -> dict[str, Any]:
    return {
        "eventId": int(event["eventId"]),
        "start": float(event["start"]),
        "end": float(event["end"]),
        "pitch": int(pitch),
        "amplitude": float(event["amplitude"]),
    }


def build_variant(payload: dict[str, Any], config: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    baseline = payload["baselineEvents"]
    observations = payload["triggerObservations"]
    by_id = {int(row["eventId"]): row for row in observations}
    if len(by_id) != len(observations):
        raise RuntimeError(f"duplicate trigger observation eventId: {payload['trackStem']}")
    variant: list[dict[str, Any]] = []
    changed = 0
    for event in baseline:
        event_id = int(event["eventId"])
        if event_id not in by_id:
            raise RuntimeError(f"missing trigger observation: {payload['trackStem']} event {event_id}")
        observation = by_id[event_id]
        if _selected(event, observation, config):
            pitch = int(observation["ordinaryV2Winner"])
            changed += 1
        else:
            pitch = int(event["pitch"])
        variant.append(_event_with_pitch(event, pitch))
    if len(variant) != len(baseline):
        raise RuntimeError(f"event-count identity failed: {payload['trackStem']} {config['id']}")
    return variant, changed


def _micro(rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    return metric(
        sum(int(row[section][stream]["tp"]) for row in rows),
        sum(int(row[section][stream]["pred"]) for row in rows),
        sum(int(row[section][stream]["ref"]) for row in rows),
    )


def _macro(rows: list[dict[str, Any]], section: str, stream: str) -> float:
    if not rows:
        raise RuntimeError("cannot macro-average empty row set")
    return mean(float(row[section][stream]["f1Pct"]) for row in rows)


def _aggregate(rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    return {
        "macroF1Pct": _macro(rows, section, stream),
        "micro": _micro(rows, section, stream),
        "player": {
            player: {
                "macroF1Pct": _macro([row for row in rows if row["player"] == player], section, stream),
                "micro": _micro([row for row in rows if row["player"] == player], section, stream),
            }
            for player in DEV_PLAYERS
        },
    }


def _qualification(
    baseline: dict[str, Any],
    config_agg: dict[str, Any],
    track_rows: list[dict[str, Any]],
    config_id_value: str,
    changed_by_player: dict[str, int],
    event_identity: bool,
) -> dict[str, Any]:
    combined_primary_macro_gain = config_agg["primary100ms"]["macroF1Pct"] - baseline["primary100ms"]["macroF1Pct"]
    combined_primary_micro_gain = config_agg["primary100ms"]["micro"]["f1Pct"] - baseline["primary100ms"]["micro"]["f1Pct"]
    combined_strict_micro_gain = config_agg["strict50ms"]["micro"]["f1Pct"] - baseline["strict50ms"]["micro"]["f1Pct"]

    player_primary_micro_delta = {
        player: config_agg["primary100ms"]["player"][player]["micro"]["f1Pct"]
        - baseline["primary100ms"]["player"][player]["micro"]["f1Pct"]
        for player in DEV_PLAYERS
    }
    player_primary_macro_delta = {
        player: config_agg["primary100ms"]["player"][player]["macroF1Pct"]
        - baseline["primary100ms"]["player"][player]["macroF1Pct"]
        for player in DEV_PLAYERS
    }
    player_strict_micro_delta = {
        player: config_agg["strict50ms"]["player"][player]["micro"]["f1Pct"]
        - baseline["strict50ms"]["player"][player]["micro"]["f1Pct"]
        for player in DEV_PLAYERS
    }

    track_delta_by_player: dict[str, dict[str, int]] = {player: {} for player in DEV_PLAYERS}
    direction_counts: dict[str, dict[str, int]] = {}
    for player in DEV_PLAYERS:
        subset = [row for row in track_rows if row["player"] == player]
        deltas = {
            row["trackStem"]: int(row["primary100ms"][config_id_value]["tp"] - row["primary100ms"]["baseline"]["tp"])
            for row in subset
        }
        track_delta_by_player[player] = deltas
        direction_counts[player] = {
            "positive": sum(delta > 0 for delta in deltas.values()),
            "neutral": sum(delta == 0 for delta in deltas.values()),
            "negative": sum(delta < 0 for delta in deltas.values()),
        }

    conditions = {
        "eventCountIdentity": bool(event_identity),
        "atLeast5ChangesEachPlayer": all(int(changed_by_player[player]) >= MIN_CHANGED_PER_PLAYER for player in DEV_PLAYERS),
        "combinedPrimaryMacroGainStrictlyPositive": combined_primary_macro_gain > 0.0,
        "combinedPrimaryMicroGainStrictlyPositive": combined_primary_micro_gain > 0.0,
        "combinedStrict50MicroNotLower": combined_strict_micro_gain >= 0.0,
        "eachPlayerPrimaryMicroGainStrictlyPositive": all(value > 0.0 for value in player_primary_micro_delta.values()),
        "eachPlayerPrimaryMacroNotLower": all(value >= 0.0 for value in player_primary_macro_delta.values()),
        "eachPlayerStrict50MicroNotLower": all(value >= 0.0 for value in player_strict_micro_delta.values()),
        "eachPlayerNegativeTrackCountNoGreaterThanPositive": all(
            direction_counts[player]["negative"] <= direction_counts[player]["positive"] for player in DEV_PLAYERS
        ),
    }

    return {
        "qualified": all(conditions.values()),
        "conditions": conditions,
        "combinedPrimaryMacroGainPP": combined_primary_macro_gain,
        "combinedPrimaryMicroGainPP": combined_primary_micro_gain,
        "combinedStrict50MicroGainPP": combined_strict_micro_gain,
        "playerPrimaryMicroDeltaPP": player_primary_micro_delta,
        "playerPrimaryMacroDeltaPP": player_primary_macro_delta,
        "playerStrict50MicroDeltaPP": player_strict_micro_delta,
        "worstPlayerPrimaryMicroGainPP": min(player_primary_micro_delta.values()),
        "worstPlayerStrict50MicroGainPP": min(player_strict_micro_delta.values()),
        "changedPitchCountByPlayer": changed_by_player,
        "primaryTPTrackDirectionCountsByPlayer": direction_counts,
        "primaryTPDeltaByPlayerTrack": track_delta_by_player,
    }


def evaluate(candidate_dir: Path, reference_dir: Path) -> dict[str, Any]:
    manifest, payloads = verify_candidates(candidate_dir)
    if len(payloads) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} development candidate payloads, found {len(payloads)}")
    if any(str(row["player"]) in EVAL_PLAYERS for row in payloads):
        raise RuntimeError("prospective candidate entered V5 development")

    expected_stems = {str(row["trackStem"]) for row in payloads}
    refs = verify_reference_root(reference_dir, expected_stems)
    if len(refs) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} development references, found {len(refs)}")
    if any(path.stem[:2] in EVAL_PLAYERS for path in refs.values()):
        raise RuntimeError("prospective reference entered V5 development")

    track_rows: list[dict[str, Any]] = []
    total_changed = {config["id"]: 0 for config in CONFIGS}
    changed_by_player = {config["id"]: {player: 0 for player in DEV_PLAYERS} for config in CONFIGS}
    total_reference_events = 0

    for payload in payloads:
        stem = str(payload["trackStem"])
        player = str(payload["player"])
        ref = load_reference_events(refs[stem])
        total_reference_events += len(ref)
        variants: dict[str, list[dict[str, Any]]] = {}
        for config in CONFIGS:
            events, changed = build_variant(payload, config)
            variants[config["id"]] = events
            total_changed[config["id"]] += changed
            changed_by_player[config["id"]][player] += changed

        row: dict[str, Any] = {
            "trackStem": stem,
            "player": player,
            "baselineEventCount": len(payload["baselineEvents"]),
            "variantEventCounts": {config_id_value: len(events) for config_id_value, events in variants.items()},
        }
        for section, tol in TOLS.items():
            section_row: dict[str, Any] = {"baseline": score(payload["baselineEvents"], ref, tol)}
            for config_id_value, events in variants.items():
                section_row[config_id_value] = score(events, ref, tol)
            row[section] = section_row
        track_rows.append(row)

    event_identity = all(
        int(row["baselineEventCount"]) == int(count)
        for row in track_rows
        for count in row["variantEventCounts"].values()
    )

    baseline = {section: _aggregate(track_rows, section, "baseline") for section in TOLS}
    config_aggs = {
        config["id"]: {section: _aggregate(track_rows, section, config["id"]) for section in TOLS}
        for config in CONFIGS
    }
    qualifications = {
        config["id"]: _qualification(
            baseline,
            config_aggs[config["id"]],
            track_rows,
            config["id"],
            changed_by_player[config["id"]],
            event_identity,
        )
        for config in CONFIGS
    }
    qualified = [config["id"] for config in CONFIGS if qualifications[config["id"]]["qualified"]]

    selected: str | None = None
    if qualified:
        selected = min(
            qualified,
            key=lambda cid: (
                -float(qualifications[cid]["worstPlayerPrimaryMicroGainPP"]),
                -float(qualifications[cid]["combinedPrimaryMicroGainPP"]),
                -float(qualifications[cid]["combinedPrimaryMacroGainPP"]),
                -float(qualifications[cid]["worstPlayerStrict50MicroGainPP"]),
                int(total_changed[cid]),
                cid,
            ),
        )

    return {
        "schema": "dadrock.tabs.open-corpus.guitarset-v5-cross-player-development.v1",
        "status": "V5_CROSS_PLAYER_DEVELOPMENT_SELECTED" if selected else "NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL",
        "candidateFreezeManifestSha256": sha256_file(candidate_dir / "candidate-freeze-manifest.json"),
        "developmentPlayers": list(DEV_PLAYERS),
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "developmentTrackCount": len(track_rows),
        "totalReferenceEventCount": total_reference_events,
        "configCount": len(CONFIGS),
        "configs": list(CONFIGS),
        "eventCountIdentity": event_identity,
        "baseline": baseline,
        "configAggregates": config_aggs,
        "totalChangedPitchCounts": total_changed,
        "changedPitchCountByPlayer": changed_by_player,
        "qualifications": qualifications,
        "qualifiedConfigIds": qualified,
        "selectedConfigId": selected,
        "selectedConfig": next((config for config in CONFIGS if config["id"] == selected), None),
        "v5DevelopmentScoreCalls": 1,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "audioRead": False,
        "basicPitchInferenceCalls": 0,
        "candidateRegenerated": False,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }


def self_test() -> dict[str, Any]:
    if len(CONFIGS) != 48 or len({config["id"] for config in CONFIGS}) != 48:
        raise RuntimeError("V5 config-family cardinality self-test failed")
    if CONFIGS[0]["id"] != "P72-D020-M005" or CONFIGS[-1]["id"] != "P79-D035-M020":
        raise RuntimeError("V5 config ID boundary self-test failed")
    event = {"eventId": 0, "start": 1.0, "end": 1.19, "pitch": 76, "amplitude": 0.5}
    observation = {
        "eventId": 0,
        "triggerEligible": True,
        "ordinaryV2ProposalDiffers": True,
        "ordinaryV2Winner": 64,
        "consensusFraction": 1.0,
        "medianAdvantage": 0.16,
    }
    probe = next(config for config in CONFIGS if config["id"] == "P76-D020-M015")
    if not _selected(event, observation, probe):
        raise RuntimeError("V5 selected-event self-test failed")
    weak = {**observation, "medianAdvantage": 0.14}
    if _selected(event, weak, probe):
        raise RuntimeError("V5 median-advantage boundary self-test failed")
    return {
        "status": "V5_CROSS_PLAYER_DEVELOPMENT_SELF_TEST_PASS",
        "configCount": len(CONFIGS),
        "developmentPlayers": list(DEV_PLAYERS),
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "v5DevelopmentScoreCalls": 0,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "audioRead": False,
        "basicPitchInferenceCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path)
    parser.add_argument("--reference-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.candidate_dir is None or args.reference_dir is None or args.output is None:
        raise SystemExit("--candidate-dir --reference-dir --output are required")

    result = evaluate(args.candidate_dir, args.reference_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "developmentTrackCount": result["developmentTrackCount"],
        "configCount": result["configCount"],
        "qualifiedConfigIds": result["qualifiedConfigIds"],
        "selectedConfigId": result["selectedConfigId"],
        "v5DevelopmentScoreCalls": result["v5DevelopmentScoreCalls"],
        "guitarSetProspectiveEvaluationScoreCalls": result["guitarSetProspectiveEvaluationScoreCalls"],
        "v168ReferenceFacingScoreCalls": result["v168ReferenceFacingScoreCalls"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
