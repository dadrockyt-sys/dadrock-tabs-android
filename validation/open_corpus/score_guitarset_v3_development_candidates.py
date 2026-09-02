#!/usr/bin/env python3
"""Reference-only scorer for frozen GuitarSet V3 development candidates.

This process never reads audio and never imports/runs Basic Pitch. It consumes
already-frozen JSON candidates and preregistered development JAMS references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

DEV_PLAYERS = ("02", "04", "05")
EVAL_PLAYERS = ("00", "01", "03")
KNOWN_ANOMALIES = {
    "04_BN3-154-E_comp",
    "04_Jazz1-200-B_comp",
    "02_Funk2-119-G_comp",
}
EXPECTED_TRACK_COUNT = 177
TOLS = {"primary100ms": 0.100, "strict50ms": 0.050}
EXPECTED_CONFIGS = {
    "C075-M005": (0.75, 0.05),
    "C075-M010": (0.75, 0.10),
    "C075-M015": (0.75, 0.15),
    "C075-M020": (0.75, 0.20),
    "C100-M005": (1.00, 0.05),
    "C100-M010": (1.00, 0.10),
    "C100-M015": (1.00, 0.15),
    "C100-M020": (1.00, 0.20),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def player_from_stem(stem: str) -> str:
    if len(stem) < 3 or stem[2] != "_":
        raise RuntimeError(f"unexpected GuitarSet track stem: {stem}")
    return stem[:2]


def load_reference_events(path: Path) -> list[dict[str, Any]]:
    # Lazy import keeps the scorer self-test independent from JAMS installation.
    import jams

    jam = jams.load(str(path))
    annotations = list(jam.search(namespace="note_midi"))
    if len(annotations) == 0:
        annotations = list(jam.search(namespace="pitch_midi"))
    if len(annotations) != 6:
        raise RuntimeError(f"expected exactly six GuitarSet string note annotations in {path.name}, found {len(annotations)}")

    rows: list[dict[str, Any]] = []
    for string_index, annotation in enumerate(annotations):
        for event_index, note in enumerate(annotation):
            rows.append({
                "pitch": int(round(float(note.value))),
                "start": float(note.time),
                "stringIndex": int(string_index),
                "eventIndex": int(event_index),
            })
    rows.sort(key=lambda row: (row["pitch"], row["start"], row["stringIndex"], row["eventIndex"]))
    return rows


def matches(pred: list[dict[str, Any]], ref: list[dict[str, Any]], tol: float) -> int:
    # Intentionally identical to the frozen P3 exact-pitch greedy onset matcher.
    p: dict[int, list[float]] = defaultdict(list)
    r: dict[int, list[float]] = defaultdict(list)
    for row in pred:
        p[int(row["pitch"])].append(float(row["start"]))
    for row in ref:
        r[int(row["pitch"])].append(float(row["start"]))
    total = 0
    for pitch in sorted(set(p) | set(r)):
        a = sorted(p[pitch])
        b = sorted(r[pitch])
        i = j = 0
        while i < len(a) and j < len(b):
            d = a[i] - b[j]
            if abs(d) <= tol:
                total += 1
                i += 1
                j += 1
            elif d < -tol:
                i += 1
            else:
                j += 1
    return total


def metric(tp: int, pred: int, ref: int) -> dict[str, Any]:
    precision = tp / pred if pred else (1.0 if ref == 0 else 0.0)
    recall = tp / ref if ref else (1.0 if pred == 0 else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "tp": int(tp),
        "pred": int(pred),
        "ref": int(ref),
        "precisionPct": 100.0 * precision,
        "recallPct": 100.0 * recall,
        "f1Pct": 100.0 * f1,
    }


def score(events: list[dict[str, Any]], ref: list[dict[str, Any]], tol: float) -> dict[str, Any]:
    return metric(matches(events, ref, tol), len(events), len(ref))


def verify_candidates(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = root / "candidate-freeze-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("candidateFileCount") != EXPECTED_TRACK_COUNT:
        raise RuntimeError("development candidateFileCount mismatch")
    if tuple(manifest.get("players", [])) != DEV_PLAYERS:
        raise RuntimeError("development player identity mismatch")
    if tuple(manifest.get("sealedEvaluationPlayers", [])) != EVAL_PLAYERS:
        raise RuntimeError("sealed evaluation player identity mismatch")
    if set(manifest.get("excludedKnownAnomalies", [])) != KNOWN_ANOMALIES:
        raise RuntimeError("known anomaly exclusion mismatch")
    if manifest.get("referenceRead") is not False or manifest.get("guitarSetJamsNoteEventsRead") != 0:
        raise RuntimeError("candidate reference-isolation guard failed")
    configs = {
        row["id"]: (float(row["consensusThreshold"]), float(row["medianAdvantageThreshold"]))
        for row in manifest["v3Trigger"]["configs"]
    }
    if configs != EXPECTED_CONFIGS:
        raise RuntimeError(f"trigger config set mismatch: {configs}")

    payloads: list[dict[str, Any]] = []
    stems: set[str] = set()
    for receipt in manifest["files"]:
        path = root / receipt["file"]
        if sha256_file(path) != receipt["sha256"]:
            raise RuntimeError(f"candidate hash mismatch: {path.name}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        stem = str(payload["trackStem"])
        player = player_from_stem(stem)
        if player not in DEV_PLAYERS or player in EVAL_PLAYERS:
            raise RuntimeError(f"non-development candidate encountered: {stem}")
        if stem in KNOWN_ANOMALIES:
            raise RuntimeError(f"excluded anomaly candidate encountered: {stem}")
        if stem in stems:
            raise RuntimeError(f"duplicate candidate stem: {stem}")
        stems.add(stem)
        if payload.get("referenceRead") is not False or payload.get("guitarSetJamsNoteEventsRead") != 0:
            raise RuntimeError(f"candidate reference guard failed: {stem}")
        baseline_count = len(payload["baselineEvents"])
        if baseline_count != int(payload["baselineEventCount"]):
            raise RuntimeError(f"baseline event count mismatch: {stem}")
        if set(payload["variants"]) != set(EXPECTED_CONFIGS):
            raise RuntimeError(f"variant set mismatch: {stem}")
        for config_id, variant in payload["variants"].items():
            if len(variant["events"]) != baseline_count or int(variant["eventCount"]) != baseline_count:
                raise RuntimeError(f"event-count identity failed: {stem} {config_id}")
        payloads.append(payload)

    if len(stems) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} unique candidate stems, found {len(stems)}")
    counts = {player: sum(player_from_stem(stem) == player for stem in stems) for player in DEV_PLAYERS}
    if counts != {"02": 59, "04": 58, "05": 60}:
        raise RuntimeError(f"candidate player counts mismatch: {counts}")
    return manifest, sorted(payloads, key=lambda row: (row["player"], row["trackStem"]))


def verify_reference_root(root: Path, expected_stems: set[str]) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for path in sorted(root.glob("*.jams")):
        stem = path.stem
        player = player_from_stem(stem)
        if player in EVAL_PLAYERS:
            raise RuntimeError(f"sealed evaluation JAMS present in development scorer workspace: {path.name}")
        if player not in DEV_PLAYERS:
            raise RuntimeError(f"unexpected JAMS player: {path.name}")
        if stem in KNOWN_ANOMALIES:
            raise RuntimeError(f"excluded anomaly JAMS present in development scorer workspace: {path.name}")
        if stem in mapping:
            raise RuntimeError(f"duplicate JAMS stem: {stem}")
        mapping[stem] = path
    if set(mapping) != expected_stems:
        missing = sorted(expected_stems - set(mapping))
        extra = sorted(set(mapping) - expected_stems)
        raise RuntimeError(f"development JAMS/candidate mismatch: missing={missing[:10]} extra={extra[:10]}")
    return mapping


def micro(track_rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    return metric(
        sum(row[section][stream]["tp"] for row in track_rows),
        sum(row[section][stream]["pred"] for row in track_rows),
        sum(row[section][stream]["ref"] for row in track_rows),
    )


def aggregate_stream(track_rows: list[dict[str, Any]], section: str, stream: str) -> dict[str, Any]:
    combined_micro = micro(track_rows, section, stream)
    player_micro = {
        player: micro([row for row in track_rows if row["player"] == player], section, stream)
        for player in DEV_PLAYERS
    }
    return {
        "macroF1Pct": mean(row[section][stream]["f1Pct"] for row in track_rows),
        "micro": combined_micro,
        "playerMicro": player_micro,
    }


def qualify_candidates(
    baseline_agg: dict[str, Any],
    config_aggs: dict[str, dict[str, Any]],
    total_changed: dict[str, int],
    event_count_identity: bool,
) -> tuple[dict[str, dict[str, Any]], list[str], str | None]:
    qualifications: dict[str, dict[str, Any]] = {}
    qualified: list[str] = []

    for config_id, aggregate in sorted(config_aggs.items()):
        primary = aggregate["primary100ms"]
        strict = aggregate["strict50ms"]
        base_primary = baseline_agg["primary100ms"]
        base_strict = baseline_agg["strict50ms"]
        macro_gain = primary["macroF1Pct"] - base_primary["macroF1Pct"]
        micro_gain = primary["micro"]["f1Pct"] - base_primary["micro"]["f1Pct"]
        strict_micro_gain = strict["micro"]["f1Pct"] - base_strict["micro"]["f1Pct"]
        player_deltas = {
            player: primary["playerMicro"][player]["f1Pct"] - base_primary["playerMicro"][player]["f1Pct"]
            for player in DEV_PLAYERS
        }
        conditions = {
            "eventCountIdentity": bool(event_count_identity),
            "primaryMacroGainAtLeast0_25PP": macro_gain >= 0.25,
            "primaryCombinedMicroNotLower": micro_gain >= 0.0,
            "primaryEachPlayerMicroLossNoWorseThan0_10PP": all(value >= -0.10 for value in player_deltas.values()),
            "strict50CombinedMicroNotLower": strict_micro_gain >= 0.0,
        }
        row = {
            "qualified": all(conditions.values()),
            "conditions": conditions,
            "primaryMacroGainPP": macro_gain,
            "primaryCombinedMicroGainPP": micro_gain,
            "strict50CombinedMicroGainPP": strict_micro_gain,
            "primaryPlayerMicroDeltaPP": player_deltas,
            "totalChangedPitchCount": int(total_changed[config_id]),
        }
        qualifications[config_id] = row
        if row["qualified"]:
            qualified.append(config_id)

    selected: str | None = None
    if qualified:
        selected = min(
            qualified,
            key=lambda config_id: (
                int(total_changed[config_id]),
                -float(qualifications[config_id]["primaryMacroGainPP"]),
                -float(EXPECTED_CONFIGS[config_id][0]),
                -float(EXPECTED_CONFIGS[config_id][1]),
                config_id,
            ),
        )
    return qualifications, qualified, selected


def evaluate(candidate_root: Path, reference_root: Path) -> dict[str, Any]:
    manifest, payloads = verify_candidates(candidate_root)
    expected_stems = {str(payload["trackStem"]) for payload in payloads}
    reference_paths = verify_reference_root(reference_root, expected_stems)

    track_rows: list[dict[str, Any]] = []
    total_reference_events = 0
    for payload in payloads:
        stem = str(payload["trackStem"])
        player = str(payload["player"])
        ref = load_reference_events(reference_paths[stem])
        total_reference_events += len(ref)
        row: dict[str, Any] = {
            "trackStem": stem,
            "player": player,
            "referenceEventCount": len(ref),
            "baselineEventCount": len(payload["baselineEvents"]),
            "variantEventCounts": {config_id: len(payload["variants"][config_id]["events"]) for config_id in EXPECTED_CONFIGS},
        }
        for section, tol in TOLS.items():
            section_row: dict[str, Any] = {
                "baseline": score(payload["baselineEvents"], ref, tol),
            }
            for config_id in EXPECTED_CONFIGS:
                section_row[config_id] = score(payload["variants"][config_id]["events"], ref, tol)
            row[section] = section_row
        track_rows.append(row)

    event_identity = all(
        row["baselineEventCount"] == count
        for row in track_rows
        for count in row["variantEventCounts"].values()
    )
    baseline_agg = {
        section: aggregate_stream(track_rows, section, "baseline")
        for section in TOLS
    }
    config_aggs = {
        config_id: {
            section: aggregate_stream(track_rows, section, config_id)
            for section in TOLS
        }
        for config_id in EXPECTED_CONFIGS
    }
    total_changed = {config_id: int(manifest["totalChangedPitchCounts"][config_id]) for config_id in EXPECTED_CONFIGS}
    qualifications, qualified, selected = qualify_candidates(
        baseline_agg,
        config_aggs,
        total_changed,
        event_identity,
    )
    status = "V3_DEVELOPMENT_TRIGGER_SELECTED" if selected is not None else "NO_DEVELOPMENT_SIGNAL"

    return {
        "schema": "dadrock.tabs.open-corpus.guitarset-v3-development-score.v1",
        "status": status,
        "candidateFreezeManifestSha256": sha256_file(candidate_root / "candidate-freeze-manifest.json"),
        "developmentPlayers": list(DEV_PLAYERS),
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "developmentTrackCount": len(track_rows),
        "totalReferenceEventCount": total_reference_events,
        "eventCountIdentity": event_identity,
        "baseline": baseline_agg,
        "configs": config_aggs,
        "qualifications": qualifications,
        "qualifiedConfigIds": qualified,
        "selectedConfigId": selected,
        "selectedConfig": (
            {
                "id": selected,
                "consensusThreshold": EXPECTED_CONFIGS[selected][0],
                "medianAdvantageThreshold": EXPECTED_CONFIGS[selected][1],
                "totalChangedPitchCount": total_changed[selected],
            }
            if selected is not None
            else None
        ),
        "totalChangedPitchCounts": total_changed,
        "candidateRegeneratedByScorer": False,
        "audioReadByScorer": False,
        "referenceReadByScorer": True,
        "guitarSetDevelopmentScoreCalls": 1,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationJamsNoteEventsRead": 0,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }


def self_test() -> dict[str, Any]:
    pred = [
        {"pitch": 60, "start": 0.04},
        {"pitch": 60, "start": 1.08},
        {"pitch": 61, "start": 2.0},
    ]
    ref = [
        {"pitch": 60, "start": 0.0},
        {"pitch": 60, "start": 1.0},
        {"pitch": 61, "start": 2.2},
    ]
    if matches(pred, ref, 0.10) != 2 or matches(pred, ref, 0.05) != 1:
        raise RuntimeError("P3-compatible onset matcher self-test failed")

    # Synthetic aggregates exercise the frozen conservative selection order.
    baseline = {
        "primary100ms": {
            "macroF1Pct": 50.0,
            "micro": {"f1Pct": 50.0},
            "playerMicro": {player: {"f1Pct": 50.0} for player in DEV_PLAYERS},
        },
        "strict50ms": {
            "macroF1Pct": 45.0,
            "micro": {"f1Pct": 45.0},
            "playerMicro": {player: {"f1Pct": 45.0} for player in DEV_PLAYERS},
        },
    }
    config_aggs: dict[str, dict[str, Any]] = {}
    changed = {config_id: 20 for config_id in EXPECTED_CONFIGS}
    for config_id in EXPECTED_CONFIGS:
        config_aggs[config_id] = {
            "primary100ms": {
                "macroF1Pct": 50.30,
                "micro": {"f1Pct": 50.05},
                "playerMicro": {player: {"f1Pct": 50.0} for player in DEV_PLAYERS},
            },
            "strict50ms": {
                "macroF1Pct": 45.2,
                "micro": {"f1Pct": 45.01},
                "playerMicro": {player: {"f1Pct": 45.0} for player in DEV_PLAYERS},
            },
        }
    changed["C100-M020"] = 5
    qualifications, qualified, selected = qualify_candidates(baseline, config_aggs, changed, True)
    if len(qualified) != 8 or selected != "C100-M020":
        raise RuntimeError(f"conservative selection self-test failed: selected={selected}")
    if not qualifications[selected]["qualified"]:
        raise RuntimeError("selected fixture unexpectedly unqualified")

    return {
        "status": "GUITARSET_V3_DEVELOPMENT_SCORER_SELF_TEST_PASS",
        "matcherPrimaryFixtureTP": 2,
        "matcherStrictFixtureTP": 1,
        "syntheticSelectedConfig": selected,
        "audioRead": False,
        "candidateRegenerated": False,
        "realJamsRead": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
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
        raise SystemExit("--candidate-dir, --reference-dir and --output are required")

    report = evaluate(args.candidate_dir, args.reference_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "developmentTrackCount": report["developmentTrackCount"],
        "totalReferenceEventCount": report["totalReferenceEventCount"],
        "eventCountIdentity": report["eventCountIdentity"],
        "baselinePrimaryMacroF1Pct": report["baseline"]["primary100ms"]["macroF1Pct"],
        "baselinePrimaryMicroF1Pct": report["baseline"]["primary100ms"]["micro"]["f1Pct"],
        "qualifiedConfigIds": report["qualifiedConfigIds"],
        "selectedConfig": report["selectedConfig"],
        "guitarSetDevelopmentScoreCalls": report["guitarSetDevelopmentScoreCalls"],
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
