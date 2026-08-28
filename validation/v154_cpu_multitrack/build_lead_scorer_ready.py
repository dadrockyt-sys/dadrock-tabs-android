#!/usr/bin/env python3
"""Build the frozen V154 Lead scorer reference without reading generated output.

Reference-only, write-once, hash-pinned. Performs no scoring.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REF_ROOT = ROOT / "research" / "v154-professional-references"
SOURCE_PATH = REF_ROOT / "lead-professional-reference-machine-readable.json"
TIMING_PATH = REF_ROOT / "lead-source-local-attack-timing.json"
MAPPING_PATH = REF_ROOT / "source-meter-to-fixed-grid-mapping.json"
OUTPUT_PATH = REF_ROOT / "scorer-ready" / "lead-scorer-ready.json"
RECEIPT_PATH = REF_ROOT / "scorer-ready" / "lead-scorer-ready-receipt.json"

EXPECTED_SHA256 = {
    SOURCE_PATH: "122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716",
    TIMING_PATH: "a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3",
    MAPPING_PATH: "1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648",
}
EXPECTED_SOURCE_EVENTS = 487
EXPECTED_SOURCE_MEASURES = 113
EXPECTED_PITCHED_ROWS = 447
EXPECTED_DEAD_NOTES = 11
EXPECTED_CONTINUATIONS = 23
EXPECTED_EXCLUDED = {28: 10, 39: 1}
EXCLUDED_MEASURES = {28, 39}


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
        raise TypeError(path)
    return payload, data


def measure_length_16ths(time_signature: str) -> int:
    if time_signature == "4/4":
        return 16
    if time_signature == "2/4":
        return 8
    raise ValueError(f"unsupported source meter: {time_signature}")


def main() -> int:
    if OUTPUT_PATH.exists() or RECEIPT_PATH.exists():
        raise RuntimeError("Lead scorer-ready output/receipt already exists; frozen outputs are write-once")

    source, _ = load_pinned(SOURCE_PATH)
    timing, _ = load_pinned(TIMING_PATH)
    mapping, _ = load_pinned(MAPPING_PATH)

    if source.get("part") != "lead":
        raise ValueError("source part identity mismatch")
    song = source.get("song") or {}
    if song.get("artist") != "Lenny Kravitz" or song.get("title") != "Are You Gonna Go My Way":
        raise ValueError("source song identity mismatch")
    if timing.get("status") != "FROZEN_REFERENCE_ONLY_SOURCE_LOCAL_TIMING":
        raise ValueError("Lead timing is not frozen")
    timing_policy = timing.get("policy") or {}
    for key in ("candidateRead", "scoringPerformed", "generatedCandidateModified", "candidateHumanCorrection", "thresholdSweep", "gpuUsed", "mainOrProductionModified"):
        if timing_policy.get(key) is not False:
            raise ValueError(f"timing safety flag must be false: {key}")
    excluded_policy = timing_policy.get("excludedMeasures") or {}
    if {int(k) for k in excluded_policy} != EXCLUDED_MEASURES:
        raise ValueError(f"unexpected excluded source measures: {excluded_policy}")

    transform = mapping.get("transform") or {}
    if transform.get("generatedCandidateConsulted") is not False or transform.get("scoringPerformed") is not False:
        raise ValueError("frozen meter mapping safety flags invalid")
    if transform.get("noPadding") is not True or transform.get("noStretching") is not True:
        raise ValueError("frozen meter mapping must forbid padding/stretching")

    measures = source.get("measures")
    if not isinstance(measures, list) or len(measures) != EXPECTED_SOURCE_MEASURES:
        raise ValueError("unexpected Lead source measure count")
    if [int(m.get("measure", -1)) for m in measures] != list(range(1, 114)):
        raise ValueError("Lead source measures are not exactly 1..113")
    steps_by_measure = timing.get("stepsByMeasure")
    if not isinstance(steps_by_measure, dict) or set(steps_by_measure) != {str(i) for i in range(1, 114)}:
        raise ValueError("timing artifact must contain exactly source measures 1..113")

    source_event_count = 0
    dead_note_count = 0
    continuation_count = 0
    excluded_counts = {28: 0, 39: 0}
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
        measure_len = measure_length_16ths(time_signature)

        events = measure_obj.get("events")
        local_steps = steps_by_measure[str(source_measure)]
        if not isinstance(events, list) or not isinstance(local_steps, list) or len(events) != len(local_steps):
            raise ValueError(f"measure {source_measure}: timing/event length mismatch")
        source_event_count += len(events)
        prior_non_null: int | None = None

        for event_index, (event, local_step) in enumerate(zip(events, local_steps)):
            if int(event.get("visualOrder", event_index)) != event_index:
                raise ValueError(f"measure {source_measure}: visualOrder drift at event {event_index}")
            continuation_only = bool(event.get("continuationOnly", False))
            kind = event.get("kind")
            midi = event.get("midi")

            if kind == "deadNote":
                dead_note_count += 1
                if midi is not None:
                    raise ValueError(f"measure {source_measure}: dead note unexpectedly has MIDI")
            elif kind != "note":
                raise ValueError(f"measure {source_measure}: unexpected event kind {kind}")
            if continuation_only:
                continuation_count += 1
                if local_step is not None:
                    raise ValueError(f"measure {source_measure}: continuation-only event must have null timing")
                continue

            if source_measure == 28:
                excluded_counts[28] += 1
                if local_step is not None:
                    raise ValueError("source measure 28 must remain unresolved/null")
                continue

            if local_step is None:
                raise ValueError(f"measure {source_measure}: attack-like event has null timing")
            local_step = int(local_step)
            if not 0 <= local_step < measure_len:
                raise ValueError(f"measure {source_measure}: local step {local_step} outside {time_signature}")
            if prior_non_null is not None and local_step < prior_non_null:
                raise ValueError(f"measure {source_measure}: local timing is not nondecreasing")
            prior_non_null = local_step

            if source_measure == 39:
                excluded_counts[39] += 1
                continue
            if kind == "deadNote":
                continue
            if not isinstance(midi, int):
                raise ValueError(f"measure {source_measure}: pitched event missing MIDI")

            absolute_source_step = cumulative_source_step + local_step
            scorer_measure = absolute_source_step // 16 + 1
            scorer_step = absolute_source_step % 16
            rows.append({"measure": scorer_measure, "midi": midi, "step": scorer_step})
            provenance_rows.append({
                "sourceMeasure": source_measure,
                "visualOrder": event_index,
                "sourceLocalStep": local_step,
                "scorerMeasure": scorer_measure,
                "scorerStep": scorer_step,
                "midi": midi,
            })

        cumulative_source_step += measure_len

    if source_event_count != EXPECTED_SOURCE_EVENTS:
        raise ValueError(f"source event count {source_event_count} != {EXPECTED_SOURCE_EVENTS}")
    if dead_note_count != EXPECTED_DEAD_NOTES:
        raise ValueError(f"dead-note count {dead_note_count} != {EXPECTED_DEAD_NOTES}")
    if continuation_count != EXPECTED_CONTINUATIONS:
        raise ValueError(f"continuation count {continuation_count} != {EXPECTED_CONTINUATIONS}")
    if excluded_counts != EXPECTED_EXCLUDED:
        raise ValueError(f"excluded event counts {excluded_counts} != {EXPECTED_EXCLUDED}")
    if len(rows) != EXPECTED_PITCHED_ROWS:
        raise ValueError(f"scorer row count {len(rows)} != {EXPECTED_PITCHED_ROWS}")
    if cumulative_source_step != 1800:
        raise ValueError(f"unexpected total source length in 16ths: {cumulative_source_step}")

    # Mechanical anchors prove the 2/4 source bar creates the intended 8-step shift.
    anchors = {(r["sourceMeasure"], r["sourceLocalStep"]): (r["scorerMeasure"], r["scorerStep"]) for r in provenance_rows}
    expected_anchors = {
        (107, 0): (106, 8),
        (107, 6): (106, 14),
        (108, 0): (107, 8),
        (108, 6): (107, 14),
    }
    for key, expected in expected_anchors.items():
        if anchors.get(key) != expected:
            raise ValueError(f"meter-mapping anchor failed for {key}: {anchors.get(key)} != {expected}")

    payload = {
        "counts": {"events": source_event_count, "measures": EXPECTED_SOURCE_MEASURES, "notes": len(rows)},
        "grid": {"stepsPerBeat": 4, "stepsPerMeasure": 16, "timeSignature": "nominal 4/4 fixed scorer grid"},
        "normalizationPolicy": {
            "candidateGenerationMayReadThis": False,
            "excludedSourceMeasures": [28, 39],
            "excludedSourceMeasureReasons": {
                "28": "authenticated rendered crop omits rhythm-stem line; exact timing not guessed from spacing",
                "39": "source explicitly labels measures 39-40 as probably a mistake; preserve source uncertainty without candidate penalty",
            },
            "generatedCandidateRead": False,
            "generatedCandidateModified": False,
            "referenceOnly": True,
            "scoringPerformed": False,
            "sourceMeterPreservedBeforeFixedGridMapping": True,
            "timingDecodedFromAuthenticatedNotation": True,
            "timingInferredFromGeneratedCandidate": False,
            "tripletQuantizationPreservedInTimingProvenance": True,
        },
        "notes": rows,
        "part": "lead",
        "schema": "dadrock.tabs.v154.lead-scorer-ready.v1",
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
    }
    output_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_sha = sha256_bytes(output_bytes)

    receipt = {
        "audit": {
            "continuationOnlySuppressed": continuation_count,
            "deadNotesSuppressedFromPitchRows": dead_note_count,
            "excludedSourceMeasureEvents": excluded_counts,
            "pitchedScorerRows": len(rows),
            "sourceEvents": source_event_count,
            "sourceMeasures": EXPECTED_SOURCE_MEASURES,
            "totalSourceLength16ths": cumulative_source_step,
            "meterMappingAnchors": {f"m{k[0]}s{k[1]}": {"measure": v[0], "step": v[1]} for k, v in expected_anchors.items()},
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
        "schema": "dadrock.tabs.v154.lead-scorer-ready-receipt.v1",
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
