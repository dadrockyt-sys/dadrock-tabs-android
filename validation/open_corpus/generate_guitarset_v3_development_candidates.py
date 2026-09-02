#!/usr/bin/env python3
"""Audio-only GuitarSet V3 development candidate generation.

Processes only preregistered development players 02/04/05, excluding the three
predeclared anomalous tracks. No JAMS/reference input is accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from analyze_guitar_techs_harmonic_octave_v169 import load_mono_audio
from v3_selective_octave_trigger_v169 import TRIGGER_CONFIGS, observe_trigger, pitches_for_all_configs

EXPECTED_MODEL_SHA256 = "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_V2_BLOB = "95e1e7d20a4bb5b15962cb803fa2da4d065743ae"
EXPECTED_V2_HELPER_BLOB = "c39305df4f875bf6aec0d5e9d5b6448a5f7404df"
EXPECTED_V3_TRIGGER_BLOB = "14ddd15fc29bfe947a4e3ce12050b10f43d2435f"

DEV_PLAYERS = ("02", "04", "05")
EVAL_PLAYERS = ("00", "01", "03")
KNOWN_ANOMALIES = {
    "04_BN3-154-E_comp",
    "04_Jazz1-200-B_comp",
    "02_Funk2-119-G_comp",
}
EXPECTED_TRACK_COUNT = 177

BASIC_PITCH_CONFIG = {
    "version": "0.4.0",
    "onsetThreshold": 0.5,
    "frameThreshold": 0.3,
    "minimumNoteLengthMs": 127.70,
    "minimumFrequency": None,
    "maximumFrequency": None,
    "multiplePitchBends": False,
    "melodiaTrick": True,
    "midiTempo": 120.0,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def normalized_basic_pitch_events(note_events: list[tuple[Any, ...]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in note_events:
        start, end, pitch, amplitude = raw[:4]
        rows.append({
            "start": float(start),
            "end": float(end),
            "pitch": int(pitch),
            "amplitude": float(amplitude),
        })
    rows.sort(key=lambda row: (row["start"], row["end"], row["pitch"], row["amplitude"]))
    for event_id, row in enumerate(rows):
        row["eventId"] = event_id
    return rows


def track_stem_from_audio(path: Path) -> str:
    name = path.name
    if not name.endswith("_mic.wav"):
        raise RuntimeError(f"unexpected GuitarSet microphone filename: {name}")
    return name[:-8]


def player_from_stem(stem: str) -> str:
    if len(stem) < 3 or stem[2] != "_":
        raise RuntimeError(f"unexpected GuitarSet track stem: {stem}")
    return stem[:2]


def discover_audio(audio_root: Path) -> list[tuple[str, str, Path]]:
    rows: list[tuple[str, str, Path]] = []
    for path in sorted(audio_root.glob("*.wav")):
        stem = track_stem_from_audio(path)
        player = player_from_stem(stem)
        if player in EVAL_PLAYERS:
            raise RuntimeError(f"sealed evaluation audio present in development workspace: {path.name}")
        if player not in DEV_PLAYERS:
            raise RuntimeError(f"unexpected player in development workspace: {path.name}")
        if stem in KNOWN_ANOMALIES:
            raise RuntimeError(f"predeclared excluded anomaly present in candidate workspace: {path.name}")
        rows.append((player, stem, path))
    if len(rows) != EXPECTED_TRACK_COUNT:
        raise RuntimeError(f"expected {EXPECTED_TRACK_COUNT} admissible development WAVs, found {len(rows)}")
    if len({stem for _, stem, _ in rows}) != EXPECTED_TRACK_COUNT:
        raise RuntimeError("duplicate GuitarSet development track stems")
    counts = {player: sum(row[0] == player for row in rows) for player in DEV_PLAYERS}
    if counts != {"02": 59, "04": 58, "05": 60}:
        raise RuntimeError(f"unexpected development player counts after exclusions: {counts}")
    return rows


def event_with_pitch(event: dict[str, Any], pitch: int) -> dict[str, Any]:
    return {
        "eventId": int(event["eventId"]),
        "start": float(event["start"]),
        "end": float(event["end"]),
        "pitch": int(pitch),
        "amplitude": float(event["amplitude"]),
    }


def build_variants(audio, sample_rate: int, baseline: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, int], list[dict[str, Any]]]:
    variants = {config["id"]: [] for config in TRIGGER_CONFIGS}
    changed = {config["id"]: 0 for config in TRIGGER_CONFIGS}
    observations: list[dict[str, Any]] = []

    for event in baseline:
        observation = observe_trigger(
            audio,
            sample_rate,
            float(event["start"]),
            int(event["pitch"]),
        )
        observation = {"eventId": int(event["eventId"]), **observation}
        observations.append(observation)
        selected = pitches_for_all_configs(observation)
        for config_id, pitch in selected.items():
            variants[config_id].append(event_with_pitch(event, pitch))
            if int(pitch) != int(event["pitch"]):
                changed[config_id] += 1

    for config_id, events in variants.items():
        if len(events) != len(baseline):
            raise RuntimeError(f"event-count identity failed for {config_id}")
    return variants, changed, observations


def self_test() -> dict[str, Any]:
    fake = [
        (0.20, 0.50, 57, 0.75, None),
        (0.10, 0.30, 45, 0.50, None),
    ]
    normalized = normalized_basic_pitch_events(fake)
    if [row["pitch"] for row in normalized] != [45, 57]:
        raise RuntimeError("Basic Pitch normalization/sort self-test failed")
    if [row["eventId"] for row in normalized] != [0, 1]:
        raise RuntimeError("event ID self-test failed")
    if len(TRIGGER_CONFIGS) != 8 or len({row["id"] for row in TRIGGER_CONFIGS}) != 8:
        raise RuntimeError("frozen trigger family self-test failed")
    return {
        "status": "GUITARSET_V3_DEVELOPMENT_CANDIDATE_SELF_TEST_PASS",
        "expectedDevelopmentTrackCount": EXPECTED_TRACK_COUNT,
        "triggerConfigCount": len(TRIGGER_CONFIGS),
        "audioOnlyCli": True,
        "referenceRead": False,
        "guitarSetJamsNoteEventsRead": 0,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-root", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if args.audio_root is None or args.output_dir is None:
        raise SystemExit("--audio-root and --output-dir are required")

    # Candidate-only imports are kept inside the real path so the scorer/static
    # surfaces never need Basic Pitch.
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model, predict

    model_path = Path(ICASSP_2022_MODEL_PATH)
    model_sha = sha256_file(model_path)
    if model_sha != EXPECTED_MODEL_SHA256:
        raise RuntimeError(f"Basic Pitch model SHA256 mismatch: {model_sha}")

    audio_rows = discover_audio(args.audio_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    model = Model(model_path)

    receipts: list[dict[str, Any]] = []
    total_baseline = 0
    total_changed = {config["id"]: 0 for config in TRIGGER_CONFIGS}
    total_trigger_eligible = 0
    total_v2_proposals = 0

    for player, stem, audio_path in audio_rows:
        _, _, note_events = predict(
            audio_path,
            model_or_model_path=model,
            onset_threshold=0.5,
            frame_threshold=0.3,
            minimum_note_length=127.70,
            minimum_frequency=None,
            maximum_frequency=None,
            multiple_pitch_bends=False,
            melodia_trick=True,
            midi_tempo=120.0,
        )
        baseline = normalized_basic_pitch_events(note_events)
        audio, sample_rate = load_mono_audio(audio_path)
        variants, changed, observations = build_variants(audio, sample_rate, baseline)
        trigger_eligible = sum(bool(row["triggerEligible"]) for row in observations)
        v2_proposals = sum(bool(row["ordinaryV2ProposalDiffers"]) for row in observations)

        payload = {
            "schema": "dadrock.tabs.open-corpus.guitarset-v3-development-candidate.v1",
            "dataset": "GuitarSet",
            "datasetVersion": "1.1.0",
            "player": player,
            "trackStem": stem,
            "sourceAudioFile": audio_path.name,
            "sourceAudioSha256": sha256_file(audio_path),
            "basicPitch": {**BASIC_PITCH_CONFIG, "modelSha256": model_sha},
            "frozenV2": {
                "evaluatorGitBlob": EXPECTED_V2_BLOB,
                "helperGitBlob": EXPECTED_V2_HELPER_BLOB,
                "candidateOffsetsSemitones": [-12, 0, 12],
                "alignmentSeconds": 0.0,
            },
            "v3Trigger": {
                "triggerGitBlob": EXPECTED_V3_TRIGGER_BLOB,
                "configs": list(TRIGGER_CONFIGS),
                "commonFrameDeltasSeconds": [0.08, 0.13, 0.18, 0.24],
                "allCommonFramesRequired": True,
            },
            "baselineEventCount": len(baseline),
            "triggerEligibleEventCount": trigger_eligible,
            "ordinaryV2ProposalEventCount": v2_proposals,
            "baselineEvents": baseline,
            "triggerObservations": observations,
            "variants": {
                config_id: {
                    "eventCount": len(events),
                    "changedPitchCount": changed[config_id],
                    "events": events,
                }
                for config_id, events in variants.items()
            },
            "referenceRead": False,
            "guitarSetJamsNoteEventsRead": 0,
            "guitarSetProspectiveEvaluationProcessed": False,
            "guitarSetProspectiveEvaluationScoreCalls": 0,
            "v168ReferenceFacingScoreCalls": 0,
            "v168PoliciesModified": False,
            "goatHoldoutSelectionModified": False,
        }
        output_path = args.output_dir / f"{stem}.json"
        output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt = {
            "file": output_path.name,
            "sha256": sha256_file(output_path),
            "player": player,
            "trackStem": stem,
            "baselineEventCount": len(baseline),
            "triggerEligibleEventCount": trigger_eligible,
            "ordinaryV2ProposalEventCount": v2_proposals,
            "changedPitchCounts": changed,
        }
        receipts.append(receipt)
        total_baseline += len(baseline)
        total_trigger_eligible += trigger_eligible
        total_v2_proposals += v2_proposals
        for config_id in total_changed:
            total_changed[config_id] += changed[config_id]
        print(json.dumps({"candidateFrozen": receipt}, sort_keys=True), flush=True)

    manifest = {
        "schema": "dadrock.tabs.open-corpus.guitarset-v3-development-freeze-manifest.v1",
        "dataset": "GuitarSet",
        "datasetVersion": "1.1.0",
        "players": list(DEV_PLAYERS),
        "sealedEvaluationPlayers": list(EVAL_PLAYERS),
        "excludedKnownAnomalies": sorted(KNOWN_ANOMALIES),
        "candidateFileCount": len(receipts),
        "files": sorted(receipts, key=lambda row: (row["player"], row["trackStem"])),
        "totalBaselineEventCount": total_baseline,
        "totalTriggerEligibleEventCount": total_trigger_eligible,
        "totalOrdinaryV2ProposalEventCount": total_v2_proposals,
        "totalChangedPitchCounts": total_changed,
        "basicPitch": {**BASIC_PITCH_CONFIG, "modelSha256": model_sha},
        "frozenV2": {
            "evaluatorGitBlob": EXPECTED_V2_BLOB,
            "helperGitBlob": EXPECTED_V2_HELPER_BLOB,
            "candidateOffsetsSemitones": [-12, 0, 12],
            "alignmentSeconds": 0.0,
        },
        "v3Trigger": {
            "triggerGitBlob": EXPECTED_V3_TRIGGER_BLOB,
            "configs": list(TRIGGER_CONFIGS),
        },
        "referenceRead": False,
        "guitarSetJamsNoteEventsRead": 0,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    manifest_path = args.output_dir / "candidate-freeze-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "GUITARSET_V3_DEVELOPMENT_CANDIDATES_FROZEN",
        "candidateFileCount": len(receipts),
        "totalBaselineEventCount": total_baseline,
        "totalOrdinaryV2ProposalEventCount": total_v2_proposals,
        "totalTriggerEligibleEventCount": total_trigger_eligible,
        "totalChangedPitchCounts": total_changed,
        "freezeManifestSha256": sha256_file(manifest_path),
        "referenceRead": False,
        "guitarSetJamsNoteEventsRead": 0,
        "guitarSetProspectiveEvaluationProcessed": False,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
