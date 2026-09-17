#!/usr/bin/env python3
"""Deterministic EGSet12 note-birth scorer frozen by the EGSet12 PRE.

The scorer uses exact MIDI and one-to-one onset matching within <= 50 ms.
References are parsed only when this program is explicitly invoked after raw
prediction and qualification artifacts have already been materialized.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

TOLERANCE_SECONDS = 0.050
TRACK_IDS = tuple(f"{index:02d}" for index in range(1, 13))
QUALIFIER_CONTRACT = "songsterr-fresh-egset12-positive-core-adapter-v1"
MODEL_CONTRACT = "songsterr-fresh-basic-pitch-isolated-guitar-v1"
CONTRACT = "songsterr-fresh-egset12-note-birth-score-v1"
VERSION = 1


class Egset12ScoringError(RuntimeError):
    pass


def _finite_nonnegative(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Egset12ScoringError(f"{label}_NUMERIC_REQUIRED")
    number = float(value)
    if not math.isfinite(number) or number < 0.0:
        raise Egset12ScoringError(f"{label}_FINITE_NONNEGATIVE_REQUIRED")
    return number


def _midi(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise Egset12ScoringError(f"{label}_MIDI_NUMERIC_REQUIRED")
    number = float(value)
    rounded = int(round(number))
    if not math.isfinite(number) or number != float(rounded) or not 0 <= rounded <= 127:
        raise Egset12ScoringError(f"{label}_INTEGER_MIDI_REQUIRED")
    return rounded


def parse_note_midi_jams(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    annotations = payload.get("annotations")
    if not isinstance(annotations, list):
        raise Egset12ScoringError(f"JAMS_ANNOTATIONS_LIST_REQUIRED:{path.name}")
    rows: list[dict[str, Any]] = []
    matching_annotations = 0
    stable_index = 0
    for annotation_index, annotation in enumerate(annotations):
        if not isinstance(annotation, dict) or annotation.get("namespace") != "note_midi":
            continue
        matching_annotations += 1
        data = annotation.get("data")
        if not isinstance(data, list):
            raise Egset12ScoringError(f"JAMS_NOTE_MIDI_DATA_LIST_REQUIRED:{path.name}:{annotation_index}")
        for data_index, row in enumerate(data):
            if not isinstance(row, dict):
                raise Egset12ScoringError(f"JAMS_NOTE_MIDI_ROW_OBJECT_REQUIRED:{path.name}:{annotation_index}:{data_index}")
            onset = _finite_nonnegative(row.get("time"), "JAMS_TIME")
            midi = _midi(row.get("value"), "JAMS_VALUE")
            rows.append({
                "midi": midi,
                "startSeconds": onset,
                "stableIndex": stable_index,
                "annotationIndex": annotation_index,
                "dataIndex": data_index,
            })
            stable_index += 1
    if matching_annotations == 0:
        raise Egset12ScoringError(f"JAMS_NOTE_MIDI_NAMESPACE_MISSING:{path.name}")
    if not rows:
        raise Egset12ScoringError(f"JAMS_NOTE_MIDI_EMPTY:{path.name}")
    rows.sort(key=lambda row: (row["midi"], row["startSeconds"], row["stableIndex"]))
    return rows


def load_prediction_pair(model_path: Path, qualifier_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
    model = json.loads(model_path.read_text(encoding="utf-8"))
    qualifier = json.loads(qualifier_path.read_text(encoding="utf-8"))
    if model.get("contract") != MODEL_CONTRACT or model.get("version") != 1 or model.get("referenceBlind") is not True:
        raise Egset12ScoringError(f"MODEL_CONTRACT_MISMATCH:{model_path.name}")
    if qualifier.get("contract") != QUALIFIER_CONTRACT or qualifier.get("version") != 1 or qualifier.get("referenceBlind") is not True:
        raise Egset12ScoringError(f"QUALIFIER_CONTRACT_MISMATCH:{qualifier_path.name}")
    notes = model.get("notes")
    proposals = qualifier.get("proposals")
    if not isinstance(notes, list) or not isinstance(proposals, list) or len(notes) != len(proposals):
        raise Egset12ScoringError(f"PREDICTION_IDENTITY_LENGTH_MISMATCH:{model_path.name}")
    proposal_by_id = {}
    for row in proposals:
        if not isinstance(row, dict) or not isinstance(row.get("noteId"), str):
            raise Egset12ScoringError(f"QUALIFIER_NOTE_ID_INVALID:{qualifier_path.name}")
        if row["noteId"] in proposal_by_id:
            raise Egset12ScoringError(f"QUALIFIER_NOTE_ID_DUPLICATE:{row['noteId']}")
        proposal_by_id[row["noteId"]] = row
    raw: list[dict[str, Any]] = []
    positive: list[dict[str, Any]] = []
    counts = {"raw": 0, "corroborated": 0, "rejected": 0, "insufficient": 0}
    for index, note in enumerate(notes):
        if not isinstance(note, dict):
            raise Egset12ScoringError(f"MODEL_NOTE_OBJECT_REQUIRED:{model_path.name}:{index}")
        note_id = note.get("noteId")
        if not isinstance(note_id, str) or note_id not in proposal_by_id:
            raise Egset12ScoringError(f"MODEL_QUALIFIER_NOTE_ID_MISMATCH:{model_path.name}:{index}")
        midi = _midi(note.get("midi"), "MODEL_MIDI")
        onset = _finite_nonnegative(note.get("startSeconds"), "MODEL_START")
        proposal = proposal_by_id[note_id]
        if _midi(proposal.get("midi"), "QUALIFIER_MIDI") != midi or _finite_nonnegative(proposal.get("startSeconds"), "QUALIFIER_START") != onset:
            raise Egset12ScoringError(f"MODEL_QUALIFIER_NOTE_IDENTITY_MISMATCH:{note_id}")
        status = proposal.get("status")
        if status not in ("corroborated", "rejected", "insufficient"):
            raise Egset12ScoringError(f"QUALIFIER_STATUS_INVALID:{note_id}")
        item = {"noteId": note_id, "midi": midi, "startSeconds": onset, "stableIndex": index}
        raw.append(item)
        counts["raw"] += 1
        counts[status] += 1
        if status == "corroborated":
            positive.append(item)
    if set(proposal_by_id) != {row["noteId"] for row in raw}:
        raise Egset12ScoringError(f"QUALIFIER_HAS_EXTRA_NOTE_IDS:{qualifier_path.name}")
    return raw, positive, counts


def _better(left: tuple[int, float, tuple[tuple[int, int], ...]], right: tuple[int, float, tuple[tuple[int, int], ...]]) -> tuple[int, float, tuple[tuple[int, int], ...]]:
    if left[0] != right[0]:
        return left if left[0] > right[0] else right
    if not math.isclose(left[1], right[1], rel_tol=0.0, abs_tol=1e-15):
        return left if left[1] < right[1] else right
    return left if left[2] <= right[2] else right


def _match_one_midi(predictions: list[dict[str, Any]], references: list[dict[str, Any]]) -> tuple[tuple[int, int], ...]:
    preds = sorted(predictions, key=lambda row: (row["startSeconds"], row["stableIndex"]))
    refs = sorted(references, key=lambda row: (row["startSeconds"], row["stableIndex"]))
    # DP state is (maximum cardinality, minimum total absolute onset error,
    # lexicographically stable matched index pairs).
    dp: list[list[tuple[int, float, tuple[tuple[int, int], ...]]]] = [
        [(0, 0.0, tuple()) for _ in range(len(refs) + 1)] for _ in range(len(preds) + 1)
    ]
    for i in range(1, len(preds) + 1):
        for j in range(1, len(refs) + 1):
            best = _better(dp[i - 1][j], dp[i][j - 1])
            error = abs(float(preds[i - 1]["startSeconds"]) - float(refs[j - 1]["startSeconds"]))
            if error <= TOLERANCE_SECONDS:
                previous = dp[i - 1][j - 1]
                candidate = (
                    previous[0] + 1,
                    previous[1] + error,
                    previous[2] + ((int(preds[i - 1]["stableIndex"]), int(refs[j - 1]["stableIndex"])),),
                )
                best = _better(best, candidate)
            dp[i][j] = best
    return dp[-1][-1][2]


def score_inventory(predictions: list[dict[str, Any]], references: list[dict[str, Any]]) -> dict[str, Any]:
    matches: list[tuple[int, int]] = []
    midis = sorted({row["midi"] for row in predictions} | {row["midi"] for row in references})
    for midi in midis:
        matches.extend(_match_one_midi(
            [row for row in predictions if row["midi"] == midi],
            [row for row in references if row["midi"] == midi],
        ))
    tp = len(matches)
    fp = len(predictions) - tp
    fn = len(references) - tp
    precision = float(tp / (tp + fp)) if tp + fp else 0.0
    recall = float(tp / (tp + fn)) if tp + fn else 0.0
    f1 = float(2.0 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matchCount": tp,
    }


def _aggregate(rows: list[dict[str, Any]], inventory: str) -> dict[str, Any]:
    tp = sum(row[inventory]["tp"] for row in rows)
    fp = sum(row[inventory]["fp"] for row in rows)
    fn = sum(row[inventory]["fn"] for row in rows)
    precision = float(tp / (tp + fp)) if tp + fp else 0.0
    recall = float(tp / (tp + fn)) if tp + fn else 0.0
    f1 = float(2.0 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "micro": {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1},
        "macro": {
            "precision": sum(row[inventory]["precision"] for row in rows) / len(rows),
            "recall": sum(row[inventory]["recall"] for row in rows) / len(rows),
            "f1": sum(row[inventory]["f1"] for row in rows) / len(rows),
        },
    }


def score_corpus(predictions_dir: Path, qualifications_dir: Path, references_dir: Path) -> dict[str, Any]:
    tracks: list[dict[str, Any]] = []
    total_counts = {"raw": 0, "corroborated": 0, "rejected": 0, "insufficient": 0}
    for track_id in TRACK_IDS:
        raw, positive, counts = load_prediction_pair(
            predictions_dir / f"{track_id}.json",
            qualifications_dir / f"{track_id}.json",
        )
        refs = parse_note_midi_jams(references_dir / f"{track_id}.jams")
        raw_score = score_inventory(raw, refs)
        positive_score = score_inventory(positive, refs)
        for key in total_counts:
            total_counts[key] += counts[key]
        tracks.append({
            "track": track_id,
            "referenceNoteBirthCount": len(refs),
            "predictionCounts": counts,
            "raw": raw_score,
            "positiveCore": positive_score,
        })
    if len(tracks) != 12:
        raise Egset12ScoringError("ALL_12_TRACKS_REQUIRED")
    retention = float(total_counts["corroborated"] / total_counts["raw"]) if total_counts["raw"] else 0.0
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "matching": {
            "pitch": "exact-midi",
            "onsetToleranceSeconds": TOLERANCE_SECONDS,
            "oneToOne": True,
            "objective": "maximum-cardinality-then-minimum-total-absolute-onset-error-then-stable-order",
        },
        "tracks": tracks,
        "corpus": {
            "raw": _aggregate(tracks, "raw"),
            "positiveCore": _aggregate(tracks, "positiveCore"),
            "predictionCounts": total_counts,
            "positiveCoreRetentionFraction": retention,
        },
        "prospectivePerformancePassThresholdDefined": False,
        "postHocExclusionsApplied": False,
        "octaveForgivenessApplied": False,
        "pitchClassForgivenessApplied": False,
        "toleranceSweepApplied": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions-dir", required=True)
    parser.add_argument("--qualifications-dir", required=True)
    parser.add_argument("--references-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = score_corpus(Path(args.predictions_dir), Path(args.qualifications_dir), Path(args.references_dir))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    # The human-readable stdout reveal occurs only after the complete score file exists.
    print(json.dumps({"contract": result["contract"], "corpus": result["corpus"]}, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
