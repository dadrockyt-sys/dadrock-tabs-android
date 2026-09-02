#!/usr/bin/env python3
"""V4 development-only GuitarSet discovery analyzer.

Consumes the immutable V3 reference-blind candidate artifact and JAMS references
for discovery players 02/04 only. It does not read audio, run Basic Pitch,
select a V4 trigger, use player 05 references, or touch prospective players.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

from score_guitarset_v3_development_candidates import load_reference_events, matches

EXPECTED_MANIFEST_SHA256 = "4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83"
DISCOVERY_PLAYERS = ("02", "04")
CONFIRMATION_PLAYER = "05"
EVAL_PLAYERS = ("00", "01", "03")
KNOWN_ANOMALIES = {
    "04_BN3-154-E_comp",
    "04_Jazz1-200-B_comp",
    "02_Funk2-119-G_comp",
}
EXPECTED_DISCOVERY_COUNTS = {"02": 59, "04": 58}
TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}
QUANTILES = (0.50, 0.75, 0.90, 0.95, 0.975, 0.99)
SWEEP_FEATURES = (
    "amplitude",
    "durationSeconds",
    "consensusFraction",
    "medianAdvantage",
    "minAdvantage",
    "meanAdvantage",
    "advantageRange",
    "advantageStd",
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def player_from_stem(stem: str) -> str:
    if len(stem) < 3 or stem[2] != "_":
        raise RuntimeError(f"unexpected GuitarSet stem: {stem}")
    return stem[:2]


def quantile(values: list[float], q: float) -> float:
    if not values:
        raise RuntimeError("quantile requested on empty list")
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def class_for_delta(delta_tp: int) -> str:
    if delta_tp > 0:
        return "beneficial"
    if delta_tp < 0:
        return "harmful"
    return "neutral"


def class_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {key: sum(row["primaryClass"] == key for row in rows) for key in ("beneficial", "neutral", "harmful")}
    total = len(rows)
    return {
        "count": total,
        **{f"{key}Count": value for key, value in counts.items()},
        **{f"{key}Pct": (100.0 * value / total if total else None) for key, value in counts.items()},
    }


def numeric_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "minimum": min(values),
        "q10": quantile(values, 0.10),
        "q25": quantile(values, 0.25),
        "median": median(values),
        "q75": quantile(values, 0.75),
        "q90": quantile(values, 0.90),
        "maximum": max(values),
        "mean": mean(values),
    }


def feature_summaries(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for feature in SWEEP_FEATURES:
        out[feature] = {
            label: numeric_summary([float(row[feature]) for row in rows if row["primaryClass"] == label])
            for label in ("beneficial", "neutral", "harmful")
        }
    return out


def sweep(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for feature in SWEEP_FEATURES:
        values = [float(row[feature]) for row in rows]
        thresholds = sorted({float(quantile(values, q)) for q in QUANTILES})
        for threshold in thresholds:
            for op in (">=", "<="):
                selected = [
                    row for row in rows
                    if (float(row[feature]) >= threshold if op == ">=" else float(row[feature]) <= threshold)
                ]
                outputs.append({
                    "feature": feature,
                    "operator": op,
                    "threshold": threshold,
                    "all": class_counts(selected),
                    "byPlayer": {
                        player: class_counts([row for row in selected if row["player"] == player])
                        for player in DISCOVERY_PLAYERS
                    },
                    "byDirection": {
                        direction: class_counts([row for row in selected if row["direction"] == direction])
                        for direction in ("low", "high")
                    },
                })
    return outputs


def verify_candidate_artifact(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = root / "candidate-freeze-manifest.json"
    if sha256_file(manifest_path) != EXPECTED_MANIFEST_SHA256:
        raise RuntimeError("candidate manifest SHA256 mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidateFileCount") != 177:
        raise RuntimeError("candidateFileCount mismatch")
    if manifest.get("players") != ["02", "04", "05"]:
        raise RuntimeError("candidate player list mismatch")
    if manifest.get("sealedEvaluationPlayers") != ["00", "01", "03"]:
        raise RuntimeError("sealed evaluation player list mismatch")
    if set(manifest.get("excludedKnownAnomalies", [])) != KNOWN_ANOMALIES:
        raise RuntimeError("known anomaly list mismatch")
    if manifest.get("referenceRead") is not False or manifest.get("guitarSetJamsNoteEventsRead") != 0:
        raise RuntimeError("candidate reference-isolation guard failed")

    payloads: list[dict[str, Any]] = []
    counts = {player: 0 for player in DISCOVERY_PLAYERS}
    for receipt in manifest["files"]:
        stem = str(receipt["trackStem"])
        player = str(receipt["player"])
        path = root / receipt["file"]
        if not path.is_file() or sha256_file(path) != receipt["sha256"]:
            raise RuntimeError(f"candidate receipt/hash mismatch: {stem}")
        if player == CONFIRMATION_PLAYER:
            # Confirmation payloads are hash-verified but deliberately not parsed.
            continue
        if player not in DISCOVERY_PLAYERS:
            raise RuntimeError(f"unexpected candidate player: {player}")
        if stem in KNOWN_ANOMALIES:
            raise RuntimeError(f"excluded anomaly candidate encountered: {stem}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("player") != player or payload.get("trackStem") != stem:
            raise RuntimeError(f"candidate identity mismatch: {stem}")
        if payload.get("referenceRead") is not False or payload.get("guitarSetJamsNoteEventsRead") != 0:
            raise RuntimeError(f"candidate reference guard failed: {stem}")
        payloads.append(payload)
        counts[player] += 1
    if counts != EXPECTED_DISCOVERY_COUNTS or len(payloads) != 117:
        raise RuntimeError(f"discovery candidate counts mismatch: {counts}, total={len(payloads)}")
    return manifest, sorted(payloads, key=lambda row: (row["player"], row["trackStem"]))


def verify_reference_root(root: Path, expected_stems: set[str]) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in sorted(root.glob("*.jams")):
        stem = path.stem
        player = player_from_stem(stem)
        if player == CONFIRMATION_PLAYER:
            raise RuntimeError(f"player-05 confirmation JAMS forbidden in V4 discovery: {path.name}")
        if player in EVAL_PLAYERS:
            raise RuntimeError(f"prospective evaluation JAMS forbidden in V4 discovery: {path.name}")
        if player not in DISCOVERY_PLAYERS:
            raise RuntimeError(f"unexpected JAMS player: {path.name}")
        if stem in KNOWN_ANOMALIES:
            raise RuntimeError(f"excluded anomaly JAMS forbidden: {path.name}")
        if stem in mapping:
            raise RuntimeError(f"duplicate JAMS stem: {stem}")
        mapping[stem] = path
    if set(mapping) != expected_stems:
        missing = sorted(expected_stems - set(mapping))
        extra = sorted(set(mapping) - expected_stems)
        raise RuntimeError(f"discovery JAMS mismatch: missing={missing[:10]} extra={extra[:10]}")
    return mapping


def one_event_swap_delta_tp(
    baseline: list[dict[str, Any]],
    event_index: int,
    new_pitch: int,
    ref: list[dict[str, Any]],
    tol: float,
    baseline_tp: int,
) -> int:
    swapped = list(baseline)
    original = baseline[event_index]
    swapped[event_index] = {
        **original,
        "pitch": int(new_pitch),
    }
    return int(matches(swapped, ref, tol) - baseline_tp)


def analyze(candidate_root: Path, reference_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest, payloads = verify_candidate_artifact(candidate_root)
    expected_stems = {str(payload["trackStem"]) for payload in payloads}
    refs = verify_reference_root(reference_root, expected_stems)

    rows: list[dict[str, Any]] = []
    total_reference_events = 0
    track_baseline_tp: dict[str, dict[str, int]] = {}

    for payload in payloads:
        stem = str(payload["trackStem"])
        player = str(payload["player"])
        baseline = payload["baselineEvents"]
        observations = payload["triggerObservations"]
        if len(baseline) != len(observations):
            raise RuntimeError(f"baseline/observation count mismatch: {stem}")
        ref = load_reference_events(refs[stem])
        total_reference_events += len(ref)
        baseline_tp = {name: int(matches(baseline, ref, tol)) for name, tol in TOLS.items()}
        track_baseline_tp[stem] = baseline_tp

        by_id = {int(event["eventId"]): (index, event) for index, event in enumerate(baseline)}
        if len(by_id) != len(baseline):
            raise RuntimeError(f"duplicate baseline eventId: {stem}")

        for observation in observations:
            if not bool(observation.get("triggerEligible")):
                continue
            if not bool(observation.get("ordinaryV2ProposalDiffers")):
                continue
            event_id = int(observation["eventId"])
            if event_id not in by_id:
                raise RuntimeError(f"observation eventId absent from baseline: {stem} {event_id}")
            event_index, event = by_id[event_id]
            baseline_pitch = int(event["pitch"])
            winner = int(observation["ordinaryV2Winner"])
            if abs(winner - baseline_pitch) != 12:
                raise RuntimeError(f"non-octave V2 proposal in discovery population: {stem} {event_id}")
            advantages = [float(v) for v in observation["advantages"]]
            winners = [int(v) for v in observation["commonFrameWinners"]]
            if len(advantages) != 4 or len(winners) != 4:
                raise RuntimeError(f"expected four common-frame observations: {stem} {event_id}")

            primary_delta = one_event_swap_delta_tp(
                baseline, event_index, winner, ref, TOLS["primary100ms"], baseline_tp["primary100ms"]
            )
            strict_delta = one_event_swap_delta_tp(
                baseline, event_index, winner, ref, TOLS["strict50ms"], baseline_tp["strict50ms"]
            )
            duration = float(event["end"]) - float(event["start"])
            if duration < 0.0:
                raise RuntimeError(f"negative duration: {stem} {event_id}")
            row = {
                "player": player,
                "trackStem": stem,
                "eventId": event_id,
                "baselinePitch": baseline_pitch,
                "ordinaryV2Winner": winner,
                "direction": "low" if winner < baseline_pitch else "high",
                "pitchClass": baseline_pitch % 12,
                "octave": baseline_pitch // 12 - 1,
                "amplitude": float(event["amplitude"]),
                "durationSeconds": duration,
                "consensusFraction": float(observation["consensusFraction"]),
                "medianAdvantage": float(observation["medianAdvantage"]),
                "advantages": advantages,
                "minAdvantage": min(advantages),
                "maxAdvantage": max(advantages),
                "meanAdvantage": mean(advantages),
                "advantageRange": max(advantages) - min(advantages),
                "advantageStd": pstdev(advantages),
                "positiveAdvantageCount": sum(value > 0.0 for value in advantages),
                "commonFrameWinners": winners,
                "ordinaryWinnerFrameCount": sum(value == winner for value in winners),
                "primaryDeltaTP": primary_delta,
                "strict50DeltaTP": strict_delta,
                "primaryClass": class_for_delta(primary_delta),
                "strict50Class": class_for_delta(strict_delta),
            }
            rows.append(row)

    by_player = {
        player: class_counts([row for row in rows if row["player"] == player])
        for player in DISCOVERY_PLAYERS
    }
    by_direction = {
        direction: class_counts([row for row in rows if row["direction"] == direction])
        for direction in ("low", "high")
    }
    strict_counts = {
        label: sum(row["strict50Class"] == label for row in rows)
        for label in ("beneficial", "neutral", "harmful")
    }
    report = {
        "schema": "dadrock.tabs.open-corpus.guitarset-v4-discovery.v1",
        "status": "V4_DISCOVERY_REPORT_FROZEN",
        "candidateFreezeManifestSha256": sha256_file(candidate_root / "candidate-freeze-manifest.json"),
        "discoveryPlayers": list(DISCOVERY_PLAYERS),
        "confirmationPlayer": CONFIRMATION_PLAYER,
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "discoveryTrackCount": len(payloads),
        "totalReferenceEventCount": total_reference_events,
        "discoveryEventCount": len(rows),
        "primaryClassCounts": class_counts(rows),
        "primaryClassCountsByPlayer": by_player,
        "primaryClassCountsByDirection": by_direction,
        "strict50ClassCounts": {"count": len(rows), **{f"{k}Count": v for k, v in strict_counts.items()}},
        "featureSummariesByPrimaryClass": feature_summaries(rows),
        "univariateThresholdSweeps": sweep(rows),
        "trackBaselineTP": track_baseline_tp,
        "player05ReferenceRead": False,
        "player05PerEventLabelsComputed": False,
        "v4TriggerSelected": False,
        "candidateRegenerated": False,
        "audioRead": False,
        "basicPitchInferenceCalls": 0,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    return report, rows


def self_test() -> dict[str, Any]:
    pred = [
        {"pitch": 60, "start": 0.04, "end": 0.20, "amplitude": 0.5, "eventId": 0},
        {"pitch": 72, "start": 1.02, "end": 1.20, "amplitude": 0.6, "eventId": 1},
    ]
    ref = [{"pitch": 60, "start": 0.00}, {"pitch": 60, "start": 1.00}]
    base_tp = matches(pred, ref, 0.10)
    gain = one_event_swap_delta_tp(pred, 1, 60, ref, 0.10, base_tp)
    if base_tp != 1 or gain != 1 or class_for_delta(gain) != "beneficial":
        raise RuntimeError("counterfactual matcher self-test failed")
    return {
        "status": "V4_DISCOVERY_SELF_TEST_PASS",
        "baselineTP": base_tp,
        "oneEventSwapDeltaTP": gain,
        "player05ReferenceRead": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path)
    parser.add_argument("--reference-dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rows-output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if not all((args.candidate_dir, args.reference_dir, args.output, args.rows_output)):
        raise SystemExit("--candidate-dir --reference-dir --output --rows-output are required")

    report, rows = analyze(args.candidate_dir, args.reference_dir)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with args.rows_output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({
        "status": report["status"],
        "discoveryTrackCount": report["discoveryTrackCount"],
        "discoveryEventCount": report["discoveryEventCount"],
        "primaryClassCounts": report["primaryClassCounts"],
        "primaryClassCountsByPlayer": report["primaryClassCountsByPlayer"],
        "primaryClassCountsByDirection": report["primaryClassCountsByDirection"],
        "player05ReferenceRead": report["player05ReferenceRead"],
        "v4TriggerSelected": report["v4TriggerSelected"],
        "guitarSetProspectiveEvaluationScoreCalls": report["guitarSetProspectiveEvaluationScoreCalls"],
        "v168ReferenceFacingScoreCalls": report["v168ReferenceFacingScoreCalls"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
