#!/usr/bin/env python3
"""Reference-blind structural audit for the Songsterr fresh purpose-built holdout.

This module implements the frozen V1 preregistration.  It consumes exactly four
independent JSON byte streams plus expected SHA-256 identities.  Raw bytes are
hashed before any JSON parsing.  It has intentionally no evaluated-audio,
Basic-Pitch, V6, correctness, score, or model-output input path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping

TIMING_BOUND_SECONDS = 0.025
MIDI_MIN = 40
MIDI_MAX = 88

HARDWARE_CONTRACT = "songsterr-fresh-purpose-built-reference-hardware-v1"
BIRTH_CONTRACT = "songsterr-fresh-purpose-built-birth-stream-v1"
LATCH_CONTRACT = "songsterr-fresh-purpose-built-pitch-latch-stream-v1"
CLOCK_CONTRACT = "songsterr-fresh-purpose-built-clock-sync-v1"
EVENT_SEMANTICS_VERSION = "physical-reference-semantics-v1"

SOURCE_NAMES = ("hardware", "birth", "pitchLatch", "clockSync")

BLOCKER_KEYS = (
    "invalidConfigurationOrCalibrationDeclarationCount",
    "sourceSha256MismatchCount",
    "clockSyncLossOrTimingBoundViolationCount",
    "nonmonotonicBirthTimestampCount",
    "nonmonotonicPitchLatchTimestampCount",
    "duplicateBirthIdCount",
    "duplicatePitchLatchIdCount",
    "unmatchedBirthCount",
    "unmatchedPitchLatchCount",
    "multiplePitchLatchesPerBirthCount",
    "physicalStringMismatchCount",
    "ambiguousPitchStateCount",
    "birthPitchTimestampDeltaViolationCount",
    "invalidFretStringOrDerivedMidiCount",
    "sameStringOverlapCount",
    "sameKeyOverlapCount",
    "forbiddenModelOrAudioDerivedProvenanceCount",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _empty_blockers() -> dict[str, int]:
    return {key: 0 for key in BLOCKER_KEYS}


def _authorization_boundary() -> dict[str, Any]:
    return {
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
    }


def _failure_result(
    *,
    blocker_counts: Mapping[str, int],
    source_sha256: Mapping[str, Mapping[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    return {
        "contract": "songsterr-fresh-purpose-built-reference-blind-structural-audit-v1",
        "contractValid": False,
        "sourceSha256": dict(source_sha256),
        "derivedNoteEventCount": 0,
        "derivedPopulationSha256": None,
        "blockerCounts": dict(blocker_counts),
        "errors": sorted(set(errors)),
        "datasetStructurallySuitable": False,
        "authoritativeStructuralSuitabilityEstablished": False,
        **_authorization_boundary(),
    }


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _strictly_increasing(values: list[float]) -> int:
    return sum(1 for a, b in zip(values, values[1:]) if not b > a)


def _source_hash_report(
    raw_sources: Mapping[str, bytes], expected_sha256: Mapping[str, str]
) -> tuple[dict[str, dict[str, Any]], int, list[str]]:
    report: dict[str, dict[str, Any]] = {}
    mismatches = 0
    errors: list[str] = []
    for name in SOURCE_NAMES:
        expected = expected_sha256.get(name)
        actual = sha256_bytes(raw_sources[name])
        valid_expected = isinstance(expected, str) and len(expected) == 64 and all(
            ch in "0123456789abcdefABCDEF" for ch in expected
        )
        matches = bool(valid_expected and actual == expected.lower())
        if not matches:
            mismatches += 1
            errors.append(f"SOURCE_SHA256_MISMATCH:{name}")
        report[name] = {
            "expected": expected,
            "actual": actual,
            "matches": matches,
        }
    return report, mismatches, errors


def audit_raw_sources(
    *, raw_sources: Mapping[str, bytes], expected_sha256: Mapping[str, str]
) -> dict[str, Any]:
    """Audit four exact byte streams.

    Hash checking is deliberately completed for all sources before *any* JSON
    parsing.  If one or more hashes mismatch, the function returns immediately.
    """
    required_names = set(SOURCE_NAMES)
    raw_names = set(raw_sources)
    expected_names = set(expected_sha256)
    missing_sources = sorted(required_names - raw_names)
    extra_sources = sorted(raw_names - required_names)
    missing_hashes = sorted(required_names - expected_names)
    extra_hashes = sorted(expected_names - required_names)
    invalid_byte_sources = sorted(
        name for name in required_names & raw_names
        if not isinstance(raw_sources[name], bytes)
    )
    if missing_sources or extra_sources or missing_hashes or extra_hashes or invalid_byte_sources:
        errors = (
            [f"MISSING_SOURCE:{name}" for name in missing_sources]
            + [f"EXTRA_SOURCE:{name}" for name in extra_sources]
            + [f"MISSING_EXPECTED_SHA256:{name}" for name in missing_hashes]
            + [f"EXTRA_EXPECTED_SHA256:{name}" for name in extra_hashes]
            + [f"SOURCE_NOT_BYTES:{name}" for name in invalid_byte_sources]
        )
        blockers = _empty_blockers()
        blockers["sourceSha256MismatchCount"] = len(errors)
        return _failure_result(
            blocker_counts=blockers,
            source_sha256={},
            errors=errors,
        )

    source_sha256, mismatch_count, hash_errors = _source_hash_report(raw_sources, expected_sha256)
    if mismatch_count:
        blockers = _empty_blockers()
        blockers["sourceSha256MismatchCount"] = mismatch_count
        return _failure_result(
            blocker_counts=blockers,
            source_sha256=source_sha256,
            errors=hash_errors,
        )

    parsed: dict[str, Any] = {}
    parse_errors: list[str] = []
    for name in SOURCE_NAMES:
        try:
            parsed[name] = json.loads(raw_sources[name].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            parse_errors.append(f"INVALID_JSON:{name}:{type(exc).__name__}")

    if parse_errors:
        blockers = _empty_blockers()
        blockers["invalidConfigurationOrCalibrationDeclarationCount"] = len(parse_errors)
        return _failure_result(
            blocker_counts=blockers,
            source_sha256=source_sha256,
            errors=parse_errors,
        )

    return _audit_parsed_sources(
        hardware=parsed["hardware"],
        birth_stream=parsed["birth"],
        latch_stream=parsed["pitchLatch"],
        clock_sync=parsed["clockSync"],
        source_sha256=source_sha256,
    )


def _audit_parsed_sources(
    *,
    hardware: Any,
    birth_stream: Any,
    latch_stream: Any,
    clock_sync: Any,
    source_sha256: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    blockers = _empty_blockers()
    errors: list[str] = []

    # Hardware/configuration contract.
    hardware_ok = isinstance(hardware, dict)
    if not hardware_ok:
        errors.append("HARDWARE_TOP_LEVEL_OBJECT_REQUIRED")
    else:
        required_checks = [
            hardware.get("contract") == HARDWARE_CONTRACT,
            _nonempty_string(hardware.get("configurationId")),
            _nonempty_string(hardware.get("calibrationId")),
            hardware.get("calibrationUsedHoldoutData") is False,
            hardware.get("calibrationUsedModelOutputs") is False,
            hardware.get("calibrationDerivedFromEvaluatedAudio") is False,
            _is_finite_number(hardware.get("maxAbsoluteReferenceTimingErrorSeconds"))
            and 0 <= float(hardware["maxAbsoluteReferenceTimingErrorSeconds"]) <= TIMING_BOUND_SECONDS,
            isinstance(hardware.get("maxFret"), int)
            and not isinstance(hardware.get("maxFret"), bool)
            and 1 <= hardware["maxFret"] <= 36,
            hardware.get("eventSemanticsVersion") == EVENT_SEMANTICS_VERSION,
        ]
        open_midi = hardware.get("openStringMidi")
        open_midi_ok = (
            isinstance(open_midi, list)
            and len(open_midi) == 6
            and all(isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 127 for v in open_midi)
            and all(b > a for a, b in zip(open_midi, open_midi[1:]))
        )
        required_checks.append(open_midi_ok)
        if not all(required_checks):
            errors.append("INVALID_HARDWARE_OR_CALIBRATION_DECLARATION")
            hardware_ok = False

        provenance_fields = (
            "calibrationUsedModelOutputs",
            "calibrationDerivedFromEvaluatedAudio",
        )
        blockers["forbiddenModelOrAudioDerivedProvenanceCount"] += sum(
            hardware.get(field) is not False for field in provenance_fields
        )

    if not hardware_ok:
        blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1

    max_fret = hardware.get("maxFret") if isinstance(hardware, dict) else None
    open_midi = hardware.get("openStringMidi") if isinstance(hardware, dict) else None

    # Stream wrappers and event arrays.
    births: list[Any] = []
    if not isinstance(birth_stream, dict) or birth_stream.get("contract") != BIRTH_CONTRACT or not isinstance(birth_stream.get("events"), list):
        errors.append("INVALID_BIRTH_STREAM_DECLARATION")
        blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
    else:
        births = birth_stream["events"]

    latches: list[Any] = []
    if not isinstance(latch_stream, dict) or latch_stream.get("contract") != LATCH_CONTRACT or not isinstance(latch_stream.get("events"), list):
        errors.append("INVALID_PITCH_LATCH_STREAM_DECLARATION")
        blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
    else:
        latches = latch_stream["events"]

    # Clock/sync contract.
    clock_ok = isinstance(clock_sync, dict) and clock_sync.get("contract") == CLOCK_CONTRACT
    if not clock_ok:
        errors.append("INVALID_CLOCK_SYNC_DECLARATION")
        blockers["clockSyncLossOrTimingBoundViolationCount"] += 1
    else:
        if not _nonempty_string(clock_sync.get("syncId")) or not _nonempty_string(clock_sync.get("clockDomainId")):
            errors.append("INVALID_CLOCK_SYNC_IDENTITY")
            blockers["clockSyncLossOrTimingBoundViolationCount"] += 1
        if clock_sync.get("syncLost") is not False:
            errors.append("CLOCK_SYNC_LOST")
            blockers["clockSyncLossOrTimingBoundViolationCount"] += 1
        max_err = clock_sync.get("maxAbsoluteErrorSeconds")
        if not (_is_finite_number(max_err) and 0 <= float(max_err) <= TIMING_BOUND_SECONDS):
            errors.append("CLOCK_SYNC_ERROR_BOUND_VIOLATION")
            blockers["clockSyncLossOrTimingBoundViolationCount"] += 1
        for field in ("usedModelOutputs", "derivedFromEvaluatedAudio"):
            if clock_sync.get(field) is not False:
                blockers["forbiddenModelOrAudioDerivedProvenanceCount"] += 1
                errors.append(f"FORBIDDEN_PROVENANCE:clockSync:{field}")

    valid_births: list[dict[str, Any]] = []
    birth_ids: list[str] = []
    birth_onsets_in_order: list[float] = []
    for index, event in enumerate(births):
        if not isinstance(event, dict):
            errors.append(f"INVALID_BIRTH_EVENT:{index}")
            blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
            continue
        event_id = event.get("birthEventId")
        onset = event.get("onsetSeconds")
        release = event.get("releaseSeconds")
        string_number = event.get("stringNumber")
        fields_ok = (
            _nonempty_string(event_id)
            and _is_finite_number(onset)
            and float(onset) >= 0
            and _is_finite_number(release)
            and float(release) > float(onset) if _is_finite_number(onset) and _is_finite_number(release) else False
        )
        string_ok = isinstance(string_number, int) and not isinstance(string_number, bool) and 1 <= string_number <= 6
        if not fields_ok:
            errors.append(f"INVALID_BIRTH_EVENT_FIELDS:{index}")
            blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
        if not string_ok:
            blockers["invalidFretStringOrDerivedMidiCount"] += 1
            errors.append(f"INVALID_BIRTH_STRING:{index}")
        for field in ("usedModelOutputs", "derivedFromEvaluatedAudio"):
            if event.get(field) is not False:
                blockers["forbiddenModelOrAudioDerivedProvenanceCount"] += 1
                errors.append(f"FORBIDDEN_PROVENANCE:birth:{index}:{field}")
        if _nonempty_string(event_id):
            birth_ids.append(event_id.strip())
        if _is_finite_number(onset) and float(onset) >= 0:
            birth_onsets_in_order.append(float(onset))
        if fields_ok and string_ok:
            valid_births.append({
                "birthEventId": event_id.strip(),
                "onsetSeconds": float(onset),
                "releaseSeconds": float(release),
                "stringNumber": string_number,
            })

    blockers["nonmonotonicBirthTimestampCount"] = _strictly_increasing(birth_onsets_in_order)
    if blockers["nonmonotonicBirthTimestampCount"]:
        errors.append("NONMONOTONIC_BIRTH_TIMESTAMPS")
    birth_counts = Counter(birth_ids)
    blockers["duplicateBirthIdCount"] = sum(count - 1 for count in birth_counts.values() if count > 1)
    if blockers["duplicateBirthIdCount"]:
        errors.append("DUPLICATE_BIRTH_IDS")

    valid_latches: list[dict[str, Any]] = []
    latch_ids: list[str] = []
    latch_times_in_order: list[float] = []
    for index, record in enumerate(latches):
        if not isinstance(record, dict):
            errors.append(f"INVALID_PITCH_LATCH_RECORD:{index}")
            blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
            continue
        latch_id = record.get("pitchLatchId")
        birth_id = record.get("birthEventId")
        timestamp = record.get("timestampSeconds")
        string_number = record.get("stringNumber")
        fret = record.get("fret")
        state = record.get("state")
        id_time_ok = (
            _nonempty_string(latch_id)
            and _nonempty_string(birth_id)
            and _is_finite_number(timestamp)
            and float(timestamp) >= 0
        )
        string_fret_ok = (
            isinstance(string_number, int) and not isinstance(string_number, bool) and 1 <= string_number <= 6
            and isinstance(fret, int) and not isinstance(fret, bool)
            and isinstance(max_fret, int) and 0 <= fret <= max_fret
        )
        if not id_time_ok:
            errors.append(f"INVALID_PITCH_LATCH_FIELDS:{index}")
            blockers["invalidConfigurationOrCalibrationDeclarationCount"] += 1
        if not string_fret_ok:
            blockers["invalidFretStringOrDerivedMidiCount"] += 1
            errors.append(f"INVALID_PITCH_LATCH_STRING_OR_FRET:{index}")
        if state != "UNAMBIGUOUS":
            blockers["ambiguousPitchStateCount"] += 1
            errors.append(f"AMBIGUOUS_PITCH_STATE:{index}")
        for field in ("usedModelOutputs", "derivedFromEvaluatedAudio"):
            if record.get(field) is not False:
                blockers["forbiddenModelOrAudioDerivedProvenanceCount"] += 1
                errors.append(f"FORBIDDEN_PROVENANCE:pitchLatch:{index}:{field}")
        if _nonempty_string(latch_id):
            latch_ids.append(latch_id.strip())
        if _is_finite_number(timestamp) and float(timestamp) >= 0:
            latch_times_in_order.append(float(timestamp))
        if id_time_ok and string_fret_ok:
            valid_latches.append({
                "pitchLatchId": latch_id.strip(),
                "birthEventId": birth_id.strip(),
                "timestampSeconds": float(timestamp),
                "stringNumber": string_number,
                "fret": fret,
                "state": state,
            })

    blockers["nonmonotonicPitchLatchTimestampCount"] = _strictly_increasing(latch_times_in_order)
    if blockers["nonmonotonicPitchLatchTimestampCount"]:
        errors.append("NONMONOTONIC_PITCH_LATCH_TIMESTAMPS")
    latch_counts = Counter(latch_ids)
    blockers["duplicatePitchLatchIdCount"] = sum(count - 1 for count in latch_counts.values() if count > 1)
    if blockers["duplicatePitchLatchIdCount"]:
        errors.append("DUPLICATE_PITCH_LATCH_IDS")

    births_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in valid_births:
        births_by_id[event["birthEventId"]].append(event)
    latches_by_birth: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in valid_latches:
        latches_by_birth[record["birthEventId"]].append(record)

    unique_birth_ids = set(births_by_id)
    linked_birth_ids = set(latches_by_birth)
    blockers["unmatchedBirthCount"] = sum(
        1 for birth_id in unique_birth_ids if birth_id not in linked_birth_ids
    )
    blockers["unmatchedPitchLatchCount"] = sum(
        len(records) for birth_id, records in latches_by_birth.items() if birth_id not in unique_birth_ids
    )
    blockers["multiplePitchLatchesPerBirthCount"] = sum(
        len(records) - 1 for birth_id, records in latches_by_birth.items()
        if birth_id in unique_birth_ids and len(records) > 1
    )
    if blockers["unmatchedBirthCount"]:
        errors.append("UNMATCHED_BIRTHS")
    if blockers["unmatchedPitchLatchCount"]:
        errors.append("UNMATCHED_PITCH_LATCHES")
    if blockers["multiplePitchLatchesPerBirthCount"]:
        errors.append("MULTIPLE_PITCH_LATCHES_PER_BIRTH")

    # Same-string overlap is defined entirely by independently sensed birth
    # timing/string identity.  Audit it directly from valid birth evidence so a
    # separate latch anomaly cannot hide an overlap that is already observable.
    births_by_string: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for birth in valid_births:
        births_by_string[birth["stringNumber"]].append(birth)
    for events in births_by_string.values():
        events.sort(key=lambda event: (event["onsetSeconds"], event["birthEventId"]))
        for previous, current in zip(events, events[1:]):
            if current["onsetSeconds"] < previous["releaseSeconds"]:
                blockers["sameStringOverlapCount"] += 1
    if blockers["sameStringOverlapCount"]:
        errors.append("SAME_STRING_OVERLAP")

    derived: list[dict[str, Any]] = []
    if isinstance(open_midi, list) and len(open_midi) == 6:
        # Preserve the frozen birth-stream chronology.  Duplicate birth IDs are
        # blockers and therefore cannot produce derived events.
        for birth in valid_births:
            birth_id = birth["birthEventId"]
            birth_records = births_by_id[birth_id]
            latch_records = latches_by_birth.get(birth_id, [])
            if len(birth_records) != 1 or len(latch_records) != 1:
                continue
            latch = latch_records[0]
            if latch["state"] != "UNAMBIGUOUS":
                continue
            if birth["stringNumber"] != latch["stringNumber"]:
                blockers["physicalStringMismatchCount"] += 1
                errors.append(f"PHYSICAL_STRING_MISMATCH:{birth_id}")
                continue
            delta = abs(birth["onsetSeconds"] - latch["timestampSeconds"])
            if delta > TIMING_BOUND_SECONDS:
                blockers["birthPitchTimestampDeltaViolationCount"] += 1
                errors.append(f"BIRTH_PITCH_TIMESTAMP_DELTA_VIOLATION:{birth_id}")
                continue
            midi = open_midi[birth["stringNumber"] - 1] + latch["fret"]
            if not isinstance(midi, int) or not MIDI_MIN <= midi <= MIDI_MAX:
                blockers["invalidFretStringOrDerivedMidiCount"] += 1
                errors.append(f"DERIVED_MIDI_OUT_OF_RANGE:{birth_id}:{midi}")
                continue
            derived.append({
                "eventId": birth_id,
                "stringNumber": birth["stringNumber"],
                "fret": latch["fret"],
                "midi": midi,
                "onsetSeconds": birth["onsetSeconds"],
                "releaseSeconds": birth["releaseSeconds"],
                "sourceBirthEventId": birth_id,
                "sourcePitchLatchId": latch["pitchLatchId"],
                "sourcePitchLatchTimestampSeconds": latch["timestampSeconds"],
            })

    # Same-key overlap needs deterministic derived pitch identity.  It is
    # therefore applied only to otherwise valid one-to-one derived events.
    by_midi: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in derived:
        by_midi[event["midi"]].append(event)
    for events in by_midi.values():
        events.sort(key=lambda event: (event["onsetSeconds"], event["eventId"]))
        active: list[dict[str, Any]] = []
        for event in events:
            active = [prior for prior in active if prior["releaseSeconds"] > event["onsetSeconds"]]
            blockers["sameKeyOverlapCount"] += len(active)
            active.append(event)
    if blockers["sameKeyOverlapCount"]:
        errors.append("SAME_KEY_OVERLAP")

    contract_valid = not errors and all(value == 0 for value in blockers.values())
    suitable = contract_valid
    population_bytes = canonical_json(derived).encode("utf-8")
    result = {
        "contract": "songsterr-fresh-purpose-built-reference-blind-structural-audit-v1",
        "contractValid": contract_valid,
        "sourceSha256": dict(source_sha256),
        "derivedNoteEventCount": len(derived),
        "derivedPopulationSha256": sha256_bytes(population_bytes) if derived or contract_valid else None,
        "blockerCounts": blockers,
        "errors": sorted(set(errors)),
        "datasetStructurallySuitable": suitable,
        "authoritativeStructuralSuitabilityEstablished": suitable,
        **_authorization_boundary(),
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hardware", required=True, help="Exact hardware/config JSON byte stream")
    parser.add_argument("--hardware-sha256", required=True)
    parser.add_argument("--birth-stream", required=True, help="Exact birth/dynamics JSON byte stream")
    parser.add_argument("--birth-stream-sha256", required=True)
    parser.add_argument("--pitch-latch-stream", required=True, help="Exact pitch-latch JSON byte stream")
    parser.add_argument("--pitch-latch-stream-sha256", required=True)
    parser.add_argument("--clock-sync", required=True, help="Exact clock/sync JSON byte stream")
    parser.add_argument("--clock-sync-sha256", required=True)
    parser.add_argument("--output", help="Optional deterministic result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_sources = {
        "hardware": Path(args.hardware).read_bytes(),
        "birth": Path(args.birth_stream).read_bytes(),
        "pitchLatch": Path(args.pitch_latch_stream).read_bytes(),
        "clockSync": Path(args.clock_sync).read_bytes(),
    }
    expected = {
        "hardware": args.hardware_sha256,
        "birth": args.birth_stream_sha256,
        "pitchLatch": args.pitch_latch_stream_sha256,
        "clockSync": args.clock_sync_sha256,
    }
    result = audit_raw_sources(raw_sources=raw_sources, expected_sha256=expected)
    rendered = canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["datasetStructurallySuitable"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
