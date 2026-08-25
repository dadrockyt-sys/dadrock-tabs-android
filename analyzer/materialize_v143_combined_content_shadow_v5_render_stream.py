#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import v143_contextual_prune_attack_shadow_v3_replay_validator as attack_v3
import v143_contextual_prune_combined_content_shadow_v5_replay_validator as combined_v5

EXPECTED_V5_SHA256 = "eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee"
EXPECTED_ATTACK_SHA256 = "039a42d06abdc60a111cd85f0db9ac07b81caf1c1d91fd65e260ffb6119b1892"
ALLOWED_TECHNIQUES = {
    "bend", "bend-release", "pre-bend", "sustain-tie", "let-ring", "palm-mute",
    "slide-up", "slide-down", "hammer-on", "pull-off", "vibrato", "dead-note",
    "muted-strum", "natural-harmonic", "pinch-harmonic", "tap", "trill",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["measure"]), int(row["step"])


def _normalize_techniques(event: dict[str, Any]) -> list[str]:
    found: set[str] = set()
    for field in ("rhythmTechniques", "techniques"):
        for value in event.get(field) or []:
            raw = value if isinstance(value, str) else value.get("type") if isinstance(value, dict) else ""
            name = str(raw or "").strip().lower()
            if name in ALLOWED_TECHNIQUES:
                found.add(name)
    return sorted(found)


def _duration_steps(event: dict[str, Any]) -> int:
    sustain = event.get("rhythmSustain") if isinstance(event.get("rhythmSustain"), dict) else {}
    value = sustain.get("durationSteps", event.get("durationSteps", 1))
    try:
        return max(1, int(round(float(value))))
    except (TypeError, ValueError):
        return 1


def _duration_seconds(event: dict[str, Any]) -> float | None:
    sustain = event.get("rhythmSustain") if isinstance(event.get("rhythmSustain"), dict) else {}
    value = sustain.get("durationSeconds", event.get("durationSeconds"))
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if numeric >= 0 else None


def _sustain_tier(event: dict[str, Any]) -> str | None:
    sustain = event.get("rhythmSustain") if isinstance(event.get("rhythmSustain"), dict) else {}
    value = str(sustain.get("tier", event.get("sustainTier", "")) or "").strip().lower()
    return value if value in {"short", "medium", "long"} else None


def _copy_optional_performance_fields(out: dict[str, Any], source: dict[str, Any]) -> None:
    duration_seconds = _duration_seconds(source)
    if duration_seconds is not None:
        out["durationSeconds"] = duration_seconds
    sustain_tier = _sustain_tier(source)
    if sustain_tier:
        out["sustainTier"] = sustain_tier
    for field in ("bendSemitones", "bendTargetFret", "bendTargetMidi"):
        if source.get(field) is not None:
            out[field] = source[field]
    if source.get("bendRelease") is True:
        out["bendRelease"] = True


def materialize(
    product: dict[str, Any],
    electric: dict[str, Any],
    attack_report: dict[str, Any],
    primary_report: dict[str, Any],
    durable_v5_report: dict[str, Any],
    attack_report_sha: str,
    durable_v5_sha: str,
) -> dict[str, Any]:
    if attack_report_sha != EXPECTED_ATTACK_SHA256:
        raise ValueError("unexpected attack-v3 validation bytes")
    if durable_v5_sha != EXPECTED_V5_SHA256:
        raise ValueError("unexpected combined-v5 validation bytes")
    if durable_v5_report.get("validationPassed") is not True:
        raise ValueError("durable V5 validation is not passing")

    fresh_v5 = combined_v5.validate(product, electric, attack_report, primary_report, attack_report_sha)
    if fresh_v5.get("validationPassed") is not True:
        raise ValueError("fresh V5 replay failed")
    for field in (
        "combinedRetainedAttackCount", "combinedSelectedPitchCount", "combinedRenderedPitchCount",
        "combinedVoicingDropCount", "primaryV4CorrectionCount", "measureCoverageCount",
    ):
        if fresh_v5.get(field) != durable_v5_report.get(field):
            raise ValueError(f"fresh/durable V5 mismatch: {field}")

    replay = product.get("precisionReplayEvidence") or {}
    eligible_rows = replay.get("eligibleAttacks") or []
    eligible = {_key(row): row for row in eligible_rows}
    baseline = {key for key, row in eligible.items() if row.get("retained") is True}

    pitch_sets: dict[tuple[int, int], set[int]] = {}
    primaries: dict[tuple[int, int], int] = {}
    for key in sorted(baseline):
        row = eligible[key]
        selected = {int(c["midi"]) for c in row.get("candidates") or [] if c.get("selected") is True}
        primary = [int(c["midi"]) for c in row.get("candidates") or [] if c.get("primary") is True]
        if len(primary) != 1 or primary[0] not in selected:
            raise ValueError(f"invalid baseline identity at {key}")
        pitch_sets[key] = selected
        primaries[key] = primary[0]

    rescue_keys: set[tuple[int, int]] = set()
    for row in attack_report.get("rescuedAttackKeys") or []:
        key = _key(row)
        selected = {int(value) for value in row.get("selectedMidis") or []}
        primary = int(row["primaryMidi"])
        if key in baseline or key not in eligible or not selected or primary not in selected:
            raise ValueError(f"invalid rescued identity at {key}")
        rescue_keys.add(key)
        pitch_sets[key] = selected
        primaries[key] = primary

    correction_keys: set[tuple[int, int]] = set()
    for correction in primary_report.get("acceptedCorrectionKeys") or []:
        key = _key(correction)
        old = int(correction["oldPrimary"])
        new = int(correction["newPrimary"])
        if key not in baseline or primaries.get(key) != old:
            raise ValueError(f"invalid V4 correction identity at {key}")
        selected = set(pitch_sets[key])
        selected.add(new)
        selected.discard(old)
        selected.add(new)
        pitch_sets[key] = selected
        primaries[key] = new
        correction_keys.add(key)

    shadow = baseline | rescue_keys
    if len(shadow) != 891 or len(rescue_keys) != 166 or len(correction_keys) != 34:
        raise ValueError("unexpected V5 attack/correction counts")

    baseline_events = product.get("events") or []
    baseline_by_identity: dict[tuple[int, int, int], list[dict[str, Any]]] = {}
    old_event_index_to_identity: dict[int, tuple[int, int, int]] = {}
    for ordinal, event in enumerate(baseline_events):
        try:
            identity = (int(event["measure"]), int(event["step"]), int(event.get("midi", event.get("dominantMidi"))))
        except (KeyError, TypeError, ValueError):
            continue
        baseline_by_identity.setdefault(identity, []).append(event)
        old_index = event.get("eventIndex", ordinal)
        try:
            old_event_index_to_identity[int(old_index)] = identity
        except (TypeError, ValueError):
            pass

    output_events: list[dict[str, Any]] = []
    source_event_for_new_index: dict[int, dict[str, Any]] = {}
    identity_to_new_indices: dict[tuple[int, int, int], list[int]] = {}
    reused_metadata = 0
    generic_baseline_notes = 0
    rescued_notes = 0

    for key in sorted(shadow):
        attack = eligible[key]
        rendered_midis = attack_v3._render_subset(attack, pitch_sets[key], primaries[key])
        positions = attack_v3._resolve(rendered_midis)
        if positions is None or len(positions) != len(rendered_midis):
            raise ValueError(f"could not resolve rendered V5 voicing at {key}")
        is_rescue = key in rescue_keys

        for midi in sorted(rendered_midis, key=lambda value: positions[int(value)][0]):
            string_index, fret = positions[int(midi)]
            identity = (key[0], key[1], int(midi))
            candidates = baseline_by_identity.get(identity) or []
            source = candidates[0] if candidates and not is_rescue else None
            event_index = len(output_events)
            event: dict[str, Any] = {
                "eventIndex": event_index,
                "measure": key[0],
                "step": key[1],
                "stringIndex": int(string_index),
                "fret": int(fret),
                "midi": int(midi),
                "durationSteps": _duration_steps(source) if source else 1,
                "techniques": _normalize_techniques(source) if source else [],
                "v5AttackClass": "rescued" if is_rescue else "baseline",
                "v5Primary": int(midi) == int(primaries[key]),
                "v5PrimaryCorrected": key in correction_keys,
                "metadataSource": "preserved-baseline-note" if source else "v5-shadow-neutral",
            }
            if source:
                reused_metadata += 1
                _copy_optional_performance_fields(event, source)
                source_event_for_new_index[event_index] = source
            elif is_rescue:
                rescued_notes += 1
            else:
                generic_baseline_notes += 1
            output_events.append(event)
            identity_to_new_indices.setdefault(identity, []).append(event_index)

    # Remap preserved legato targets only where both source and target identities survive V5.
    remapped_legato_links = 0
    dropped_legato_links = 0
    for new_index, source in source_event_for_new_index.items():
        raw_target = source.get("legatoTargetEventIndex")
        if raw_target is None:
            continue
        try:
            old_target = old_event_index_to_identity.get(int(raw_target))
        except (TypeError, ValueError):
            old_target = None
        target_indices = identity_to_new_indices.get(old_target, []) if old_target else []
        if target_indices:
            target_index = target_indices[0]
            output_events[new_index]["legatoTargetEventIndex"] = target_index
            output_events[new_index]["legatoTargetFret"] = output_events[target_index]["fret"]
            output_events[new_index]["legatoTargetMidi"] = output_events[target_index]["midi"]
            remapped_legato_links += 1
        else:
            dropped_legato_links += 1

    onsets = {(event["measure"], event["step"]) for event in output_events}
    measures = {event["measure"] for event in output_events}
    rescued_output = [event for event in output_events if event["v5AttackClass"] == "rescued"]
    baseline_output = [event for event in output_events if event["v5AttackClass"] == "baseline"]
    technique_events = [event for event in output_events if event.get("techniques")]

    checks = {
        "eventCount1209": len(output_events) == 1209,
        "onsetCount891": len(onsets) == 891,
        "measureCoverage113": measures == set(range(1, 114)),
        "baselineRendered967": len(baseline_output) == 967,
        "rescuedRendered242": len(rescued_output) == 242,
        "rescuedTechniqueNeutral": all(not event.get("techniques") and int(event.get("durationSteps", 1)) == 1 for event in rescued_output),
        "allEventIndicesSequential": all(event["eventIndex"] == index for index, event in enumerate(output_events)),
        "allFretsLegal": all(0 <= int(event["fret"]) <= attack_v3.MAX_FRET for event in output_events),
        "allStringsLegal": all(0 <= int(event["stringIndex"]) <= 5 for event in output_events),
        "freshV5Passes": fresh_v5.get("validationPassed") is True,
    }
    if not all(checks.values()):
        raise ValueError(f"V5 render materialization invariant failed: {checks}")

    return {
        "schemaVersion": 1,
        "classification": "v143-reference-free-combined-content-shadow-v5-render-stream",
        "policy": combined_v5.POLICY,
        "sourceV5ValidationSha256": durable_v5_sha,
        "sourceAttackV3ValidationSha256": attack_report_sha,
        "tempo": product.get("tempo"),
        "tuning": product.get("tuning", "E Standard"),
        "timeSignature": product.get("timeSignature", "4/4"),
        "keySignature": product.get("keySignature", ""),
        "events": output_events,
        "summary": {
            "renderedEventCount": len(output_events),
            "retainedOnsetCount": len(onsets),
            "measureCoverageCount": len(measures),
            "baselineRenderedEventCount": len(baseline_output),
            "rescuedRenderedEventCount": len(rescued_output),
            "preservedBaselineMetadataEventCount": reused_metadata,
            "neutralBaselineEventCount": generic_baseline_notes,
            "neutralRescuedEventCount": rescued_notes,
            "techniqueEventCount": len(technique_events),
            "remappedLegatoLinkCount": remapped_legato_links,
            "droppedLegatoLinkCount": dropped_legato_links,
            "primaryV4CorrectionAttackCount": len(correction_keys),
        },
        "downstreamTechniqueSustainRecomputed": False,
        "rescuedEventsTechniqueNeutralByDesign": True,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "freezeReady": False,
        "validationChecks": checks,
        "validationPassed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", type=Path)
    parser.add_argument("electric_evidence", type=Path)
    parser.add_argument("attack_v3_validation", type=Path)
    parser.add_argument("primary_v4_validation", type=Path)
    parser.add_argument("combined_v5_validation", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    attack_sha = _sha256(args.attack_v3_validation)
    v5_sha = _sha256(args.combined_v5_validation)
    result = materialize(
        json.loads(args.product.read_text()),
        json.loads(args.electric_evidence.read_text()),
        json.loads(args.attack_v3_validation.read_text()),
        json.loads(args.primary_v4_validation.read_text()),
        json.loads(args.combined_v5_validation.read_text()),
        attack_sha,
        v5_sha,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    args.output.write_text(text)
    print(json.dumps({
        "output": str(args.output),
        **result["summary"],
        "validationPassed": result["validationPassed"],
        "freezeReady": result["freezeReady"],
        "modalInvoked": result["modalInvoked"],
        "professionalReferenceUsed": result["professionalReferenceUsed"],
    }, indent=2, sort_keys=True))
    return 0 if result["validationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
