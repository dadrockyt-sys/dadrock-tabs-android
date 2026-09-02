#!/usr/bin/env python3
"""Exact multi-event evaluator for the preregistered GuitarSet V4 discovery family.

Discovery players 02/04 only. Player 05 references and prospective players are
forbidden. This script reads no audio and never imports/runs Basic Pitch.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any

from score_guitarset_v3_development_candidates import (
    KNOWN_ANOMALIES,
    metric,
    score,
    verify_candidates,
    verify_reference_root,
    load_reference_events,
)

DISCOVERY_PLAYERS = ("02", "04")
CONFIRMATION_PLAYER = "05"
EVAL_PLAYERS = ("00", "01", "03")
TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}
CONFIGS: tuple[dict[str, Any], ...] = (
    {"id": "H72-D025", "minBaselinePitch": 72, "maxDurationSeconds": 0.25},
    {"id": "H72-D030", "minBaselinePitch": 72, "maxDurationSeconds": 0.30},
    {"id": "H72-D035", "minBaselinePitch": 72, "maxDurationSeconds": 0.35},
)
EXPECTED_CHANGED = {"H72-D025": 107, "H72-D030": 137, "H72-D035": 157}


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


def _aggregate(rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    if not rows:
        raise RuntimeError("cannot aggregate empty discovery row set")
    return {
        "macroF1Pct": mean(float(row[section][stream]["f1Pct"]) for row in rows),
        "micro": _micro(rows, section, stream),
        "playerMicro": {
            player: _micro([row for row in rows if row["player"] == player], section, stream)
            for player in DISCOVERY_PLAYERS
        },
    }


def _qualification(
    baseline: dict[str, Any],
    config: dict[str, Any],
    track_rows: list[dict[str, Any]],
    config_id: str,
    event_identity: bool,
) -> dict[str, Any]:
    primary_gain_macro = config["primary100ms"]["macroF1Pct"] - baseline["primary100ms"]["macroF1Pct"]
    primary_gain_micro = config["primary100ms"]["micro"]["f1Pct"] - baseline["primary100ms"]["micro"]["f1Pct"]
    strict_gain_micro = config["strict50ms"]["micro"]["f1Pct"] - baseline["strict50ms"]["micro"]["f1Pct"]
    player_deltas = {
        player: config["primary100ms"]["playerMicro"][player]["f1Pct"]
        - baseline["primary100ms"]["playerMicro"][player]["f1Pct"]
        for player in DISCOVERY_PLAYERS
    }
    track_tp_deltas = {
        row["trackStem"]: int(row["primary100ms"][config_id]["tp"] - row["primary100ms"]["baseline"]["tp"])
        for row in track_rows
    }
    conditions = {
        "eventCountIdentity": bool(event_identity),
        "primaryMacroGainStrictlyPositive": primary_gain_macro > 0.0,
        "primaryCombinedMicroGainStrictlyPositive": primary_gain_micro > 0.0,
        "primaryPlayer02MicroNotLower": player_deltas["02"] >= 0.0,
        "primaryPlayer04MicroNotLower": player_deltas["04"] >= 0.0,
        "strict50CombinedMicroNotLower": strict_gain_micro >= 0.0,
        "noDiscoveryTrackPrimaryTPLoss": all(delta >= 0 for delta in track_tp_deltas.values()),
    }
    return {
        "qualified": all(conditions.values()),
        "conditions": conditions,
        "primaryMacroGainPP": primary_gain_macro,
        "primaryCombinedMicroGainPP": primary_gain_micro,
        "strict50CombinedMicroGainPP": strict_gain_micro,
        "primaryPlayerMicroDeltaPP": player_deltas,
        "negativePrimaryTPTrackCount": sum(delta < 0 for delta in track_tp_deltas.values()),
        "positivePrimaryTPTrackCount": sum(delta > 0 for delta in track_tp_deltas.values()),
        "primaryTPDeltaByTrack": track_tp_deltas,
    }


def evaluate(candidate_dir: Path, reference_dir: Path) -> dict[str, Any]:
    manifest, payloads_all = verify_candidates(candidate_dir)
    payloads = [row for row in payloads_all if str(row["player"]) in DISCOVERY_PLAYERS]
    if len(payloads) != 117:
        raise RuntimeError(f"expected 117 discovery candidate payloads, found {len(payloads)}")
    if any(str(row["player"]) == CONFIRMATION_PLAYER for row in payloads):
        raise RuntimeError("player 05 candidate entered V4 discovery-family scoring set")
    if any(str(row["player"]) in EVAL_PLAYERS for row in payloads):
        raise RuntimeError("prospective candidate entered V4 discovery-family scoring set")

    expected_stems = {str(row["trackStem"]) for row in payloads}
    refs = verify_reference_root(reference_dir, expected_stems)
    if any(path.stem.startswith(CONFIRMATION_PLAYER + "_") for path in refs.values()):
        raise RuntimeError("player 05 reference entered V4 discovery-family scoring")
    if any(path.stem[:2] in EVAL_PLAYERS for path in refs.values()):
        raise RuntimeError("prospective reference entered V4 discovery-family scoring")

    track_rows: list[dict[str, Any]] = []
    total_changed = {config["id"]: 0 for config in CONFIGS}
    for payload in payloads:
        stem = str(payload["trackStem"])
        player = str(payload["player"])
        ref = load_reference_events(refs[stem])
        variants: dict[str, list[dict[str, Any]]] = {}
        for config in CONFIGS:
            events, changed = build_variant(payload, config)
            variants[config["id"]] = events
            total_changed[config["id"]] += changed

        row: dict[str, Any] = {
            "trackStem": stem,
            "player": player,
            "baselineEventCount": len(payload["baselineEvents"]),
            "variantEventCounts": {config_id: len(events) for config_id, events in variants.items()},
        }
        for section, tol in TOLS.items():
            section_row: dict[str, Any] = {"baseline": score(payload["baselineEvents"], ref, tol)}
            for config_id, events in variants.items():
                section_row[config_id] = score(events, ref, tol)
            row[section] = section_row
        track_rows.append(row)

    if total_changed != EXPECTED_CHANGED:
        raise RuntimeError(f"V4 discovery-family changed-count mismatch: {total_changed}")

    event_identity = all(
        int(row["baselineEventCount"]) == int(count)
        for row in track_rows
        for count in row["variantEventCounts"].values()
    )
    baseline_agg = {section: _aggregate(track_rows, section, "baseline") for section in TOLS}
    config_aggs = {
        config["id"]: {section: _aggregate(track_rows, section, config["id"]) for section in TOLS}
        for config in CONFIGS
    }
    qualifications = {
        config["id"]: _qualification(
            baseline_agg,
            config_aggs[config["id"]],
            track_rows,
            config["id"],
            event_identity,
        )
        for config in CONFIGS
    }
    qualified = [config["id"] for config in CONFIGS if qualifications[config["id"]]["qualified"]]

    selected: str | None = None
    if qualified:
        selected = min(
            qualified,
            key=lambda config_id: (
                -float(qualifications[config_id]["primaryCombinedMicroGainPP"]),
                -float(qualifications[config_id]["primaryMacroGainPP"]),
                -float(qualifications[config_id]["strict50CombinedMicroGainPP"]),
                int(total_changed[config_id]),
                config_id,
            ),
        )

    return {
        "schema": "dadrock.tabs.open-corpus.guitarset-v4-discovery-family-score.v1",
        "status": "V4_DISCOVERY_FAMILY_SELECTED" if selected else "NO_V4_DISCOVERY_FAMILY_SIGNAL",
        "candidateFreezeManifestSha256": manifest.get("candidateFreezeManifestSha256", None),
        "discoveryPlayers": list(DISCOVERY_PLAYERS),
        "confirmationPlayer": CONFIRMATION_PLAYER,
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "discoveryTrackCount": len(track_rows),
        "configs": list(CONFIGS),
        "totalChangedPitchCounts": total_changed,
        "eventCountIdentity": event_identity,
        "baseline": baseline_agg,
        "configAggregates": config_aggs,
        "qualifications": qualifications,
        "qualifiedConfigIds": qualified,
        "selectedConfigId": selected,
        "exactV4DiscoveryFamilyScoreCalls": 1,
        "player05ReferenceRead": False,
        "player05PerEventLabelsComputed": False,
        "player05ConfirmationScoreCalls": 0,
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
    event = {"eventId": 0, "start": 1.0, "end": 1.24, "pitch": 72, "amplitude": 0.4}
    obs = {
        "eventId": 0,
        "triggerEligible": True,
        "ordinaryV2ProposalDiffers": True,
        "ordinaryV2Winner": 60,
    }
    checks = {config["id"]: _selected(event, obs, config) for config in CONFIGS}
    if checks != {"H72-D025": True, "H72-D030": True, "H72-D035": True}:
        raise RuntimeError(f"family threshold self-test failed: {checks}")
    too_long = {**event, "end": 1.31}
    checks_long = {config["id"]: _selected(too_long, obs, config) for config in CONFIGS}
    if checks_long != {"H72-D025": False, "H72-D030": False, "H72-D035": True}:
        raise RuntimeError(f"duration boundary self-test failed: {checks_long}")
    wrong_direction = {**obs, "ordinaryV2Winner": 84}
    if any(_selected(event, wrong_direction, config) for config in CONFIGS):
        raise RuntimeError("octave-up proposal passed V4 family self-test")
    return {
        "status": "V4_DISCOVERY_FAMILY_SELF_TEST_PASS",
        "configIds": [config["id"] for config in CONFIGS],
        "expectedChangedPitchCounts": EXPECTED_CHANGED,
        "player05ReferenceRead": False,
        "player05ConfirmationScoreCalls": 0,
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
        "qualifiedConfigIds": result["qualifiedConfigIds"],
        "selectedConfigId": result["selectedConfigId"],
        "totalChangedPitchCounts": result["totalChangedPitchCounts"],
        "exactV4DiscoveryFamilyScoreCalls": result["exactV4DiscoveryFamilyScoreCalls"],
        "player05ReferenceRead": result["player05ReferenceRead"],
        "player05ConfirmationScoreCalls": result["player05ConfirmationScoreCalls"],
        "guitarSetProspectiveEvaluationScoreCalls": result["guitarSetProspectiveEvaluationScoreCalls"],
        "v168ReferenceFacingScoreCalls": result["v168ReferenceFacingScoreCalls"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
