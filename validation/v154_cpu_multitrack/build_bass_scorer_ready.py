#!/usr/bin/env python3
"""Build the frozen V154 Bass scorer reference without reading generated output.

This script is deliberately reference-only. Its three data inputs are hard-coded,
content-hash pinned, and live under research/v154-professional-references/. It has
no generated-candidate argument and performs no scoring.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REF_ROOT = ROOT / "research" / "v154-professional-references"
SOURCE_PATH = REF_ROOT / "bass-professional-reference-machine-readable.json"
TIMING_PATH = REF_ROOT / "bass-source-local-attack-timing.json"
MAPPING_PATH = REF_ROOT / "source-meter-to-fixed-grid-mapping.json"
OUTPUT_PATH = REF_ROOT / "scorer-ready" / "bass-scorer-ready.json"
RECEIPT_PATH = REF_ROOT / "scorer-ready" / "bass-scorer-ready-receipt.json"

EXPECTED_SHA256 = {
    SOURCE_PATH: "a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3",
    TIMING_PATH: "7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244",
    MAPPING_PATH: "1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648",
}
EXPECTED_SOURCE_EVENTS = 569
EXPECTED_SOURCE_MEASURES = 113
EXPECTED_PITCHED_ROWS = 547
EXPECTED_DEAD_NOTES = 7
EXPECTED_CONTINUATIONS = 8
EXPECTED_MEASURE_88_EVENTS = 7
ALLOWED_DUPLICATE_LOCAL_STEPS = {(35, 4), (36, 4), (43, 0)}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_pinned(path: Path) -> tuple[dict[str, Any], bytes]:
    data = path.read_bytes()
    actual = sha256_bytes(data)
    expected = EXPECTED_SHA256[path]
    if actual != expected:
        raise RuntimeError(f"frozen input identity mismatch: {path}: {actual} != {expected}")
    payload = json.loads(data)
    if not isinstance(payload, dict):
        raise TypeError(f"expected object in {path}")
    return payload, data


def measure_length_16ths(time_signature: str) -> int:
    numerator_text, denominator_text = time_signature.split("/", 1)
    numerator = int(numerator_text)
    denominator = int(denominator_text)
    value = numerator * (16 / denominator)
    if int(value) != value:
        raise ValueError(f"unsupported non-integral 16th measure length: {time_signature}")
    return int(value)


def main() -> int:
    if OUTPUT_PATH.exists() or RECEIPT_PATH.exists():
        raise RuntimeError("Bass scorer-ready output/receipt already exists; frozen outputs are write-once")

    source, _ = load_pinned(SOURCE_PATH)
    timing, _ = load_pinned(TIMING_PATH)
    mapping, _ = load_pinned(MAPPING_PATH)

    if source.get("part") != "bass":
        raise ValueError("source part identity mismatch")
    song = source.get("song") or {}
    if song.get("artist") != "Lenny Kravitz" or song.get("title") != "Are You Gonna Go My Way":
        raise ValueError("source song identity mismatch")
    if timing.get("status") != "FROZEN_REFERENCE_ONLY_SOURCE_LOCAL_TIMING":
        raise ValueError("timing artifact is not frozen")
    timing_policy = timing.get("policy") or {}
    for key in ("candidateRead", "scoringPerformed", "generatedCandidateModified", "candidateHumanCorrection", "thresholdSweep", "gpuUsed", "mainOrProductionModified"):
        if timing_policy.get(key) is not False:
            raise ValueError(f"timing safety flag must be false: {key}")
    transform = mapping.get("transform") or {}
    if transform.get("generatedCandidateConsulted") is not False or transform.get("scoringPerformed") is not False:
        raise ValueError("frozen meter mapping safety flags invalid")
    if transform.get("noPadding") is not True or transform.get("noStretching") is not True:
        raise ValueError("frozen meter mapping must forbid padding/stretching")

    measures = source.get("measures")
    if not isinstance(measures, list) or len(measures) != EXPECTED_SOURCE_MEASURES:
        raise ValueError("unexpected Bass source measure count")
    if [int(m.get("measure", -1)) for m in measures] != list(range(1, EXPECTED_SOURCE_MEASURES + 1)):
        raise ValueError("Bass source measures are not exactly 1..113")

    steps_by_measure = timing.get("stepsByMeasure")
    if not isinstance(steps_by_measure, dict) or set(steps_by_measure) != {str(i) for i in range(1, 114)}:
        raise ValueError("timing artifact must contain exactly source measures 1..113")

    source_event_count = 0
    dead_note_count = 0
    continuation_count = 0
    excluded_measure_88_event_count = 0
    rows: list[dict[str, int]] = []
    provenance_rows: list[dict[str, int]] = []
    cumulative_source_step = 0

    for measure_obj in measures:
        source_measure = int(measure_obj["measure"])
        time_signature = str(measure_obj.get("timeSignature", ""))
        if source_measure == 104:
            if time_signature != "2/4":
                raise ValueError("source measure 104 must be 2/4")
        elif time_signature != "4/4":
            raise ValueError(f"unexpected source meter at measure {source_measure}: {time_signature}")

        events = measure_obj.get("events")
        if not isinstance(events, list):
            raise TypeError(f"measure {source_measure} events must be a list")
        source_event_count += len(events)
        local_steps = steps_by_measure[str(source_measure)]
        if not isinstance(local_steps, list) or len(local_steps) != len(events):
            raise ValueError(f"measure {source_measure}: timing/event length mismatch")

        prior_non_null: int | None = None
        seen_steps: set[int] = set()
        for event_index, (event, local_step) in enumerate(zip(events, local_steps)):
            if int(event.get("visualOrder", event_index)) != event_index:
                raise ValueError(f"measure {source_measure}: visualOrder drift at event {event_index}")
            continuation_only = bool(event.get("continuationOnly", False))
            kind = event.get("kind")
            midi = event.get("midi")
            excluded_measure = source_measure == 88 or bool(measure_obj.get("excludeFromScoring", False))

            if kind == "deadNote":
                dead_note_count += 1
                if midi is not None:
                    raise ValueError(f"measure {source_measure}: dead note unexpectedly has MIDI")
            if continuation_only:
                continuation_count += 1

            if excluded_measure:
                if source_measure != 88:
                    raise ValueError(f"unexpected excluded source measure: {source_measure}")
                excluded_measure_88_event_count += 1
                if local_step is not None:
                    raise ValueError("measure 88 timing must remain unresolved/null")
                continue

            if continuation_only:
                if local_step is not None:
                    raise ValueError(f"measure {source_measure}: continuation-only event must have null timing")
                continue

            if local_step is None:
                raise ValueError(f"measure {source_measure}: attack-like event has null timing")
            local_step = int(local_step)
            measure_len = measure_length_16ths(time_signature)
            if not 0 <= local_step < measure_len:
                raise ValueError(f"measure {source_measure}: local step {local_step} outside {time_signature}")
            if prior_non_null is not None and local_step < prior_non_null:
                raise ValueError(f"measure {source_measure}: local timing is not nondecreasing")
            if local_step in seen_steps and (source_measure, local_step) not in ALLOWED_DUPLICATE_LOCAL_STEPS:
                raise ValueError(f"measure {source_measure}: unapproved collocated source step {local_step}")
            prior_non_null = local_step
            seen_steps.add(local_step)

            if kind == "deadNote":
                continue
            if kind != "note" or not isinstance(midi, int):
                raise ValueError(f"measure {source_measure}: pitched scorer event identity invalid")

            absolute_source_step = cumulative_source_step + local_step
            scorer_measure = absolute_source_step // 16 + 1
            scorer_step = absolute_source_step % 16
            row = {"measure": scorer_measure, "midi": midi, "step": scorer_step}
            rows.append(row)
            provenance_rows.append({
                "sourceMeasure": source_measure,
                "visualOrder": event_index,
                "sourceLocalStep": local_step,
                "scorerMeasure": scorer_measure,
                "scorerStep": scorer_step,
                "midi": midi,
            })

        cumulative_source_step += measure_length_16ths(time_signature)

    if source_event_count != EXPECTED_SOURCE_EVENTS:
        raise ValueError(f"source event count {source_event_count} != {EXPECTED_SOURCE_EVENTS}")
    if dead_note_count != EXPECTED_DEAD_NOTES:
        raise ValueError(f"dead-note count {dead_note_count} != {EXPECTED_DEAD_NOTES}")
    if continuation_count != EXPECTED_CONTINUATIONS:
        raise ValueError(f"continuation count {continuation_count} != {EXPECTED_CONTINUATIONS}")
    if excluded_measure_88_event_count != EXPECTED_MEASURE_88_EVENTS:
        raise ValueError("measure 88 excluded-event count mismatch")
    if len(rows) != EXPECTED_PITCHED_ROWS:
        raise ValueError(f"scorer row count {len(rows)} != {EXPECTED_PITCHED_ROWS}")
    if cumulative_source_step != 1800:
        raise ValueError(f"unexpected total source length in 16ths: {cumulative_source_step}")

    # Mechanical anchor checks around the frozen 2/4 source bar.
    anchors = {(r["sourceMeasure"], r["sourceLocalStep"]): (r["scorerMeasure"], r["scorerStep"]) for r in provenance_rows}
    expected_anchors = {
        (104, 0): (104, 0),
        (104, 6): (104, 6),
        (105, 0): (104, 8),
        (105, 8): (105, 0),
        (106, 8): (106, 0),
        (109, 14): (109, 6),
    }
    for key, expected in expected_anchors.items():
        if anchors.get(key) != expected:
            raise ValueError(f"meter-mapping anchor failed for {key}: {anchors.get(key)} != {expected}")

    payload = {
        "counts": {"events": source_event_count, "measures": EXPECTED_SOURCE_MEASURES, "notes": len(rows)},
        "grid": {"stepsPerBeat": 4, "stepsPerMeasure": 16, "timeSignature": "nominal 4/4 fixed scorer grid"},
        "normalizationPolicy": {
            "candidateGenerationMayReadThis": False,
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "measure88Excluded": True,
            "referenceOnly": True,
            "scoringPerformed": False,
            "sourceMeterPreservedBeforeFixedGridMapping": True,
            "timingDecodedFromCanonicalNotation": True,
            "timingInferredFromGeneratedCandidate": False,
        },
        "notes": rows,
        "part": "bass",
        "schema": "dadrock.tabs.v154.bass-scorer-ready.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
    }
    output_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_sha = sha256_bytes(output_bytes)

    receipt = {
        "audit": {
            "continuationOnlySuppressed": continuation_count,
            "deadNotesSuppressedFromPitchRows": dead_note_count,
            "measure88ExcludedEvents": excluded_measure_88_event_count,
            "pitchedScorerRows": len(rows),
            "sourceEvents": source_event_count,
            "sourceMeasures": EXPECTED_SOURCE_MEASURES,
            "totalSourceLength16ths": cumulative_source_step,
        },
        "frozenInputs": {
            str(SOURCE_PATH.relative_to(ROOT)): EXPECTED_SHA256[SOURCE_PATH],
            str(TIMING_PATH.relative_to(ROOT)): EXPECTED_SHA256[TIMING_PATH],
            str(MAPPING_PATH.relative_to(ROOT)): EXPECTED_SHA256[MAPPING_PATH],
        },
        "outputPath": str(OUTPUT_PATH.relative_to(ROOT)),
        "outputSha256": output_sha,
        "policy": {
            "candidateGenerationMayReadReference": False,
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "humanCandidateCorrection": False,
            "mainOrProductionModified": False,
            "modalL4CudaGpuUsed": False,
            "referenceFacingScoreCalls": 0,
            "referenceOnly": True,
            "scoringPerformed": False,
            "thresholdSweep": False,
        },
        "schema": "dadrock.tabs.v154.bass-scorer-ready-receipt.v1",
        "validation": "PASS",
    }
    receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(output_bytes)
    RECEIPT_PATH.write_bytes(receipt_bytes)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
