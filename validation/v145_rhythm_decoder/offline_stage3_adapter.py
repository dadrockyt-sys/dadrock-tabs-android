from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
MODAL_DIR = ROOT / "modal"
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
for entry in (MODAL_DIR, HOLDOUT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import v145_rhythm_sequence_decoder as stage2  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402


SCHEMA_VERSION = 14503
CLASSIFICATION = "v145-rhythm-stage3-offline-generated-only-candidate"
EXPECTED_SOURCE_PATH = "debug/v143-contextual-prune/v5-professional-pdf/v5-render-stream.json"
EXPECTED_SOURCE_GIT_BLOB = "fe61f7ad53a4d71348a5113ecc9e3876eaad98d4"
EXPECTED_SOURCE_RAW_SHA256 = "7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2"
EXPECTED_SOURCE_EVENT_COUNT = 1209
EXPECTED_MEASURE_COUNT = 113
EXPECTED_MEASURE_SET = frozenset(range(1, EXPECTED_MEASURE_COUNT + 1))
EXPECTED_TEMPO_BPM = 129.19921875
EXPECTED_TIME_SIGNATURE = "4/4"
STEPS_PER_MEASURE = 16
STEPS_PER_QUARTER = 4
STAGE1_BLOB = "2fd979aebb4685e86c7f24a0162f69de306c06e9"
STAGE2_BLOB = "5f86f57d0fd10774690d50528d51bad6e0392bf3"
MAX_CONVERSION_RESIDUAL_STEPS = 0.01
RENDERER_OPEN_MIDI = (64, 59, 55, 50, 45, 40)
_PROTECTED_VALUE_KEYS = (
    "bendSemitones",
    "bendTargetFret",
    "bendTargetMidi",
    "legatoTargetEventIndex",
    "legatoContinuationFromEventIndex",
    "legatoContinuationType",
)
_LINK_KEYS = ("legatoTargetEventIndex", "legatoContinuationFromEventIndex")


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _source_step_seconds(tempo_bpm: float = EXPECTED_TEMPO_BPM) -> float:
    tempo = float(tempo_bpm)
    if not math.isfinite(tempo) or tempo <= 0:
        raise ValueError("tempo must be finite and positive")
    return 60.0 / tempo / STEPS_PER_QUARTER


def _event_cell(event: Mapping[str, Any]) -> tuple[int, int, int]:
    return int(event["measure"]), int(event["step"]), int(event["stringIndex"])


def _validate_source_events(events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise ValueError(f"Stage3 source event count must be exactly {EXPECTED_SOURCE_EVENT_COUNT}")

    copied = [deepcopy(dict(event)) for event in events]
    measures: set[int] = set()
    seen_indices: set[int] = set()
    for list_index, event in enumerate(copied):
        event_index = event.get("eventIndex")
        measure = event.get("measure")
        step = event.get("step")
        midi = event.get("midi")
        string_index = event.get("stringIndex")
        fret = event.get("fret")
        duration_steps = event.get("durationSteps")

        if not _is_int(event_index) or event_index != list_index:
            raise ValueError("Stage3 source eventIndex must equal source list index 0..1208")
        if event_index in seen_indices:
            raise ValueError("Stage3 source eventIndex values must be unique")
        seen_indices.add(event_index)
        if not _is_int(measure) or not 1 <= measure <= EXPECTED_MEASURE_COUNT:
            raise ValueError("Stage3 source measure outside 1..113")
        if not _is_int(step) or not 0 <= step < STEPS_PER_MEASURE:
            raise ValueError("Stage3 source step outside 0..15")
        if not _is_int(midi):
            raise ValueError("Stage3 source MIDI must be an integer")
        if not _is_int(string_index) or not 0 <= string_index <= 5:
            raise ValueError("Stage3 source stringIndex outside 0..5")
        if not _is_int(fret) or not 0 <= fret <= 36:
            raise ValueError("Stage3 source fret outside renderer range")
        if not _is_int(duration_steps) or duration_steps <= 0:
            raise ValueError("Stage3 source durationSteps must be a positive integer")
        measures.add(measure)

    if measures != set(EXPECTED_MEASURE_SET):
        raise ValueError("Stage3 source must cover exactly measures 1..113")
    return copied


def reconstruct_generated_evidence(
    events: Sequence[Mapping[str, Any]],
    *,
    tempo_bpm: float = EXPECTED_TEMPO_BPM,
) -> list[dict[str, object]]:
    """Convert renderer-grid events to generated-only Stage2 evidence."""

    step_seconds = _source_step_seconds(tempo_bpm)
    evidence: list[dict[str, object]] = []
    for event in events:
        absolute_step = (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(event["step"])
        evidence.append(
            {
                "midi": int(event["midi"]),
                "onset": float(absolute_step * step_seconds),
                "duration": float(int(event["durationSteps"]) * step_seconds),
                "confidence": 1.0,
            }
        )
    return evidence


def protected_source_indices(events: Sequence[Mapping[str, Any]]) -> frozenset[int]:
    """Return source indices whose technique/link semantics must remain byte-identical."""

    protected: set[int] = set()
    references: set[int] = set()
    event_count = len(events)
    for index, event in enumerate(events):
        techniques = event.get("techniques")
        rhythm_techniques = event.get("rhythmTechniques")
        if isinstance(techniques, Sequence) and not isinstance(techniques, (str, bytes)) and len(techniques) > 0:
            protected.add(index)
        if isinstance(rhythm_techniques, Sequence) and not isinstance(rhythm_techniques, (str, bytes)) and len(rhythm_techniques) > 0:
            protected.add(index)
        if any(event.get(key) is not None for key in _PROTECTED_VALUE_KEYS):
            protected.add(index)

        for key in _LINK_KEYS:
            value = event.get(key)
            if value is None:
                continue
            if not _is_int(value) or not 0 <= value < event_count:
                raise ValueError(f"Stage3 source has invalid {key}")
            references.add(int(value))

    return frozenset(protected | references)


def _half_up_absolute_step(onset_seconds: float, step_seconds: float) -> tuple[int, float]:
    ratio = float(onset_seconds) / float(step_seconds)
    absolute_step = int(math.floor(ratio + 0.5))
    residual = abs(ratio - absolute_step)
    return absolute_step, residual


def _decoded_groups(decoded_notes: Sequence[Any]) -> list[tuple[float, tuple[Any, ...]]]:
    grouped: dict[float, list[Any]] = {}
    seen_sources: set[int] = set()
    for note in decoded_notes:
        source_index = int(note.source_index)
        if source_index in seen_sources:
            raise ValueError("Stage3 decoder reused one source event")
        seen_sources.add(source_index)
        grouped.setdefault(float(note.onset), []).append(note)
    return [
        (onset, tuple(sorted(rows, key=lambda row: (int(row.midi), int(row.source_index)))))
        for onset, rows in sorted(grouped.items())
    ]


def apply_decode_result(
    source_events: Sequence[Mapping[str, Any]],
    decode_result: Any,
    *,
    step_seconds: float,
    required_measure_set: frozenset[int],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Apply one frozen Stage2 result with Stage3 atomic fail-closed guards."""

    source = [deepcopy(dict(event)) for event in source_events]
    candidate = deepcopy(source)
    protected = protected_source_indices(source)
    source_cells = Counter(_event_cell(event) for event in source)

    stats = {
        "decodedNoteCount": len(tuple(decode_result.decoded_notes)),
        "undecodedSourceCount": len(tuple(decode_result.undecoded_source_indices)),
        "protectedSourceCount": len(protected),
        "decodedGroupCount": 0,
        "appliedGroupCount": 0,
        "protectedGroupCount": 0,
        "residualOrRangePreservedGroupCount": 0,
        "collisionPreservedGroupCount": 0,
        "appliedEventCount": 0,
    }

    for _selected_onset, group in _decoded_groups(decode_result.decoded_notes):
        stats["decodedGroupCount"] += 1
        group_indices = {int(note.source_index) for note in group}
        if any(index < 0 or index >= len(source) for index in group_indices):
            raise ValueError("Stage3 decoder returned source index outside source stream")
        if group_indices & protected:
            stats["protectedGroupCount"] += 1
            continue

        proposals: dict[int, dict[str, Any]] = {}
        preserve_group = False
        for note in group:
            source_index = int(note.source_index)
            source_event = source[source_index]
            if int(note.midi) != int(source_event["midi"]):
                raise ValueError("Stage3 decoder changed MIDI evidence")

            absolute_step, residual = _half_up_absolute_step(float(note.onset), step_seconds)
            if residual > MAX_CONVERSION_RESIDUAL_STEPS or not 0 <= absolute_step < EXPECTED_MEASURE_COUNT * STEPS_PER_MEASURE:
                preserve_group = True
                break

            string_index = int(note.string) - 1
            fret = int(note.fret)
            midi = int(note.midi)
            if not 0 <= string_index <= 5 or not 0 <= fret <= 24:
                raise ValueError("Stage3 decoded guitar position outside frozen range")
            if RENDERER_OPEN_MIDI[string_index] + fret != midi:
                raise ValueError("Stage3 decoded guitar position does not reproduce source MIDI")

            proposal = deepcopy(source_event)
            proposal["measure"] = absolute_step // STEPS_PER_MEASURE + 1
            proposal["step"] = absolute_step % STEPS_PER_MEASURE
            proposal["stringIndex"] = string_index
            proposal["fret"] = fret
            proposals[source_index] = proposal

        if preserve_group:
            stats["residualOrRangePreservedGroupCount"] += 1
            continue
        if len(proposals) != len(group_indices):
            raise ValueError("Stage3 decoded group source mapping is incomplete")

        target_cells = [_event_cell(proposals[index]) for index in sorted(proposals)]
        if len(target_cells) != len(set(target_cells)):
            raise ValueError("Stage3 decoded group proposed duplicate guitar cells")

        group_source_cells = Counter(_event_cell(source[index]) for index in group_indices)
        collides = False
        for cell in target_cells:
            outside_count = source_cells[cell] - group_source_cells[cell]
            if outside_count > 0:
                collides = True
                break
        if collides:
            stats["collisionPreservedGroupCount"] += 1
            continue

        for source_index, proposal in proposals.items():
            candidate[source_index] = proposal
        stats["appliedGroupCount"] += 1
        stats["appliedEventCount"] += len(proposals)

    if len(candidate) != len(source):
        raise ValueError("Stage3 candidate changed event count")
    for index, (before, after) in enumerate(zip(source, candidate)):
        if int(after.get("eventIndex", -1)) != index:
            raise ValueError("Stage3 candidate changed eventIndex/source ordering")
        if int(after.get("midi", -9999)) != int(before["midi"]):
            raise ValueError("Stage3 candidate changed MIDI")
        changed_keys = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
        if not changed_keys.issubset({"measure", "step", "stringIndex", "fret"}):
            raise ValueError("Stage3 candidate changed a forbidden source field")

    candidate_cells = Counter(_event_cell(event) for event in candidate)
    for cell, count in candidate_cells.items():
        if count > 1 and count > source_cells[cell]:
            raise ValueError("Stage3 candidate increased a renderer-cell multiplicity")

    candidate_measures = frozenset(int(event["measure"]) for event in candidate)
    if candidate_measures != required_measure_set:
        raise ValueError("Stage3 candidate changed generated measure coverage")

    return candidate, stats


def build_stage3_candidate(source_payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(source_payload, Mapping):
        raise ValueError("Stage3 source payload must be a JSON object")
    if float(source_payload.get("tempo", 0.0)) != EXPECTED_TEMPO_BPM:
        raise ValueError("Stage3 source tempo changed")
    if str(source_payload.get("timeSignature", "")) != EXPECTED_TIME_SIGNATURE:
        raise ValueError("Stage3 source time signature changed")

    raw_events = source_payload.get("events")
    if not isinstance(raw_events, Sequence) or isinstance(raw_events, (str, bytes)):
        raise ValueError("Stage3 source events must be a JSON array")
    source_events = _validate_source_events(raw_events)
    step_seconds = _source_step_seconds()
    evidence = reconstruct_generated_evidence(source_events)

    # Frozen Stage 3 contract: exactly one Stage 2 decoder call.
    decode_result = stage2.decode_global_rhythm_sequence(evidence)
    candidate_events, stats = apply_decode_result(
        source_events,
        decode_result,
        step_seconds=step_seconds,
        required_measure_set=EXPECTED_MEASURE_SET,
    )

    canonical = canonical_events(candidate_events)
    if len(canonical) != EXPECTED_SOURCE_EVENT_COUNT:
        raise ValueError("Stage3 canonical candidate event count changed")
    event_sha = sha256_json(canonical)
    grid = decode_result.grid

    return {
        "schemaVersion": SCHEMA_VERSION,
        "classification": CLASSIFICATION,
        "evaluationRole": "generated-only-pre-reference-candidate",
        "instrument": "rhythm",
        "source": {
            "path": EXPECTED_SOURCE_PATH,
            "gitBlob": EXPECTED_SOURCE_GIT_BLOB,
            "rawSha256": EXPECTED_SOURCE_RAW_SHA256,
            "eventCount": EXPECTED_SOURCE_EVENT_COUNT,
            "measureCount": EXPECTED_MEASURE_COUNT,
            "tempoBpm": EXPECTED_TEMPO_BPM,
            "timeSignature": EXPECTED_TIME_SIGNATURE,
        },
        "decoder": {
            "stage1Blob": STAGE1_BLOB,
            "stage2Blob": STAGE2_BLOB,
            "decoderCallCount": 1,
            "grid": None
            if grid is None
            else {
                "quantum": float(grid.quantum),
                "phase": float(grid.phase),
                "support": float(grid.support),
                "medianNormalizedResidual": float(grid.median_normalized_residual),
                "meanNormalizedResidual": float(grid.mean_normalized_residual),
                "evidenceCount": int(grid.evidence_count),
                "candidateCount": int(grid.candidate_count),
            },
            "clusterCount": int(decode_result.cluster_count),
            "decodedClusterCount": int(decode_result.decoded_cluster_count),
        },
        "adapter": {
            **stats,
            "sourceStepSeconds": step_seconds,
            "maximumConversionResidualSteps": MAX_CONVERSION_RESIDUAL_STEPS,
            "eventCountPreserved": True,
            "eventIndexAndSourceOrderPreserved": True,
            "midiEvidencePreserved": True,
            "generatedMeasureSetPreserved": True,
            "allowedChangedFields": ["measure", "step", "stringIndex", "fret"],
        },
        "candidate": {
            "eventCount": len(canonical),
            "eventSha256": event_sha,
            "generatedMeasureCount": len({int(row["measure"]) for row in canonical}),
        },
        "safety": {
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
            "goldInputUsed": False,
            "fitLabelsRead": False,
            "validationLabelsRead": False,
            "canaryLabelsRead": False,
            "newPitchGeneration": False,
            "eventDeletion": False,
            "eventAddition": False,
            "modalDependency": False,
            "modalGpuUsed": False,
            "liveAudioBenchmarkRun": False,
            "acceptedBaselineChanged": False,
        },
        "renderEvents": candidate_events,
    }


def _load_exact_source(path: Path) -> Mapping[str, Any]:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SOURCE_RAW_SHA256:
        raise ValueError(f"Stage3 source raw SHA256 changed: {digest}")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("Stage3 source file must contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the single preregistered V145 Stage3 offline generated-only candidate.")
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = _load_exact_source(args.v5_render_stream)
    candidate = build_stage3_candidate(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: candidate[key] for key in ("schemaVersion", "classification", "candidate", "adapter", "safety")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
