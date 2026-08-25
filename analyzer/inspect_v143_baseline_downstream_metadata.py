#!/usr/bin/env python3
"""Inspect exact downstream metadata in the immutable V143 baseline product.

Evidence-only: this utility never infers, scores, thresholds, changes notes, or invokes
runtime models. It exposes the nested rhythm sustain/technique structures already present
in the pinned candidate so a later replay can be source-faithful instead of guessed.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_EVENTS = 967
EXPECTED_ONSETS = 725
EXPECTED_MEASURES = 113
INTEREST_TERMS = (
    "sustain", "technique", "hammer", "pull", "slide", "bend", "vibrato",
    "palm", "ring", "ghost", "accent", "harmonic", "duration", "evidence",
    "diagnostic", "source", "attack", "onset",
)


def type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


def stable_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def event_identity(event: dict[str, Any]) -> dict[str, Any]:
    return {
        key: event.get(key)
        for key in ("eventIndex", "measure", "step", "midi", "dominantMidi", "stringIndex", "fret", "onsetTime", "offsetTime", "duration")
        if key in event
    }


def nested_object_summary(values: list[Any]) -> dict[str, Any]:
    objects = [value for value in values if isinstance(value, dict)]
    schema_counts: collections.Counter[str] = collections.Counter()
    type_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    scalar_distributions: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    signatures: collections.Counter[str] = collections.Counter()
    for obj in objects:
        signatures[stable_value(obj)] += 1
        for key, value in obj.items():
            schema_counts[key] += 1
            type_counts[key][type_name(value)] += 1
            if value is None or isinstance(value, (str, int, float, bool)):
                scalar_distributions[key][stable_value(value)] += 1
    return {
        "presentObjectCount": len(objects),
        "missingOrNonObjectCount": len(values) - len(objects),
        "schema": {
            key: {
                "presentCount": schema_counts[key],
                "types": dict(sorted(type_counts[key].items())),
                **(
                    {"scalarDistribution": dict(sorted(scalar_distributions[key].items(), key=lambda item: (-item[1], item[0])))}
                    if key in scalar_distributions else {}
                ),
            }
            for key in sorted(schema_counts)
        },
        "topExactSignatures": [
            {"count": count, "value": json.loads(signature)}
            for signature, count in signatures.most_common(80)
        ],
        "uniqueExactSignatureCount": len(signatures),
    }


def compact_if_small(value: Any, max_chars: int = 12000) -> Any:
    text = stable_value(value)
    if len(text) <= max_chars:
        return value
    if isinstance(value, dict):
        return {"type": "object", "keys": sorted(value), "jsonChars": len(text)}
    if isinstance(value, list):
        return {"type": "array", "length": len(value), "jsonChars": len(text)}
    return {"type": type_name(value), "jsonChars": len(text)}


def walk_interest_paths(value: Any, path: str = "$", depth: int = 0, out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if out is None:
        out = []
    if depth > 8 or len(out) >= 500:
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if any(term in str(key).lower() for term in INTEREST_TERMS):
                item: dict[str, Any] = {"path": child_path, "type": type_name(child)}
                if child is None or isinstance(child, (str, int, float, bool)):
                    item["value"] = child
                elif isinstance(child, list):
                    item["length"] = len(child)
                    if child and len(child) <= 8 and all(x is None or isinstance(x, (str, int, float, bool)) for x in child):
                        item["sample"] = child
                elif isinstance(child, dict):
                    item["keys"] = sorted(str(k) for k in child.keys())[:60]
                out.append(item)
            walk_interest_paths(child, child_path, depth + 1, out)
            if len(out) >= 500:
                break
    elif isinstance(value, list):
        for index, child in enumerate(value[:3]):
            walk_interest_paths(child, f"{path}[{index}]", depth + 1, out)
            if len(out) >= 500:
                break
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidate_path = args.candidate.resolve()
    product = json.loads(candidate_path.read_text(encoding="utf-8"))
    if not isinstance(product, dict):
        raise SystemExit("candidate root must be an object")
    events = product.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise SystemExit("candidate must expose direct object-array events")

    onset_keys = sorted({(int(event["measure"]), int(event["step"])) for event in events})
    measures = sorted({int(event["measure"]) for event in events})
    if len(events) != EXPECTED_EVENTS:
        raise SystemExit(f"event count mismatch: {len(events)}")
    if len(onset_keys) != EXPECTED_ONSETS:
        raise SystemExit(f"onset count mismatch: {len(onset_keys)}")
    if measures != list(range(1, EXPECTED_MEASURES + 1)):
        raise SystemExit("measure coverage mismatch")

    event_schema_counts: collections.Counter[str] = collections.Counter()
    event_type_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for event in events:
        for key, value in event.items():
            event_schema_counts[key] += 1
            event_type_counts[key][type_name(value)] += 1

    sustain_values = [event.get("rhythmSustain") for event in events]
    shadow_values = [event.get("rhythmSustainShadow") for event in events]
    legato_evidence_values = [event.get("legatoEvidence") for event in events]

    technique_length_distribution: collections.Counter[str] = collections.Counter()
    technique_value_distribution: collections.Counter[str] = collections.Counter()
    technique_type_distribution: collections.Counter[str] = collections.Counter()
    technique_samples: list[dict[str, Any]] = []
    sustain_samples: list[dict[str, Any]] = []
    sustain_shadow_samples: list[dict[str, Any]] = []
    legato_samples: list[dict[str, Any]] = []

    for event in events:
        techniques = event.get("rhythmTechniques")
        if not isinstance(techniques, list):
            techniques = []
        technique_length_distribution[str(len(techniques))] += 1
        for technique in techniques:
            technique_value_distribution[stable_value(technique)] += 1
            raw_type = technique if isinstance(technique, str) else technique.get("type") if isinstance(technique, dict) else None
            technique_type_distribution[str(raw_type)] += 1
        if techniques and len(technique_samples) < 120:
            technique_samples.append({"event": event_identity(event), "rhythmTechniques": techniques})

        sustain = event.get("rhythmSustain")
        if isinstance(sustain, dict):
            duration_steps = sustain.get("durationSteps")
            if (duration_steps not in (None, 1, 1.0) or sustain.get("tier") not in (None, "short")) and len(sustain_samples) < 160:
                sustain_samples.append({"event": event_identity(event), "rhythmSustain": sustain})

        shadow = event.get("rhythmSustainShadow")
        if isinstance(shadow, dict) and len(sustain_shadow_samples) < 120:
            sustain_shadow_samples.append({"event": event_identity(event), "rhythmSustain": sustain, "rhythmSustainShadow": shadow})

        if isinstance(event.get("legatoEvidence"), dict) and len(legato_samples) < 120:
            legato_samples.append({
                "event": event_identity(event),
                "legatoContinuationType": event.get("legatoContinuationType"),
                "legatoTargetEventIndex": event.get("legatoTargetEventIndex"),
                "legatoTargetMidi": event.get("legatoTargetMidi"),
                "legatoTargetFret": event.get("legatoTargetFret"),
                "legatoEvidence": event.get("legatoEvidence"),
                "rhythmTechniques": techniques,
            })

    replay = product.get("precisionReplayEvidence") if isinstance(product.get("precisionReplayEvidence"), dict) else {}
    eligible = replay.get("eligibleAttacks") if isinstance(replay.get("eligibleAttacks"), list) else []
    eligible_schema_counts: collections.Counter[str] = collections.Counter()
    eligible_type_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    candidate_schema_counts: collections.Counter[str] = collections.Counter()
    candidate_type_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    candidate_selected = collections.Counter()
    candidate_primary = collections.Counter()
    candidate_count = 0
    for attack in eligible:
        if not isinstance(attack, dict):
            continue
        for key, value in attack.items():
            eligible_schema_counts[key] += 1
            eligible_type_counts[key][type_name(value)] += 1
        for candidate in attack.get("candidates") or []:
            if not isinstance(candidate, dict):
                continue
            candidate_count += 1
            for key, value in candidate.items():
                candidate_schema_counts[key] += 1
                candidate_type_counts[key][type_name(value)] += 1
            candidate_selected[stable_value(candidate.get("selected"))] += 1
            candidate_primary[stable_value(candidate.get("primary"))] += 1

    top_level = {
        key: {"type": type_name(value), **({"length": len(value)} if isinstance(value, (dict, list)) else {})}
        for key, value in sorted(product.items())
    }
    product_without_events = {key: value for key, value in product.items() if key != "events"}

    report = {
        "schemaVersion": "v143-baseline-downstream-metadata-inspection-v2",
        "purpose": "evidence-only nested downstream inspection; no inference or musical mutation",
        "candidate": {
            "path": str(candidate_path),
            "sha256": sha256_file(candidate_path),
            "eventCount": len(events),
            "uniqueOnsets": len(onset_keys),
            "measureCount": len(measures),
            "measureRange": [measures[0], measures[-1]],
        },
        "topLevel": top_level,
        "selectedTopLevelDiagnostics": {
            key: compact_if_small(product.get(key))
            for key in ("sustainDiagnostics", "semanticGuard", "preFreezeTrace", "precisionPolicy", "candidateDiagnostics", "correctionDiagnostics")
            if key in product
        },
        "eventSchema": {
            key: {"presentCount": event_schema_counts[key], "types": dict(sorted(event_type_counts[key].items()))}
            for key in sorted(event_schema_counts)
        },
        "rhythmSustain": nested_object_summary(sustain_values),
        "rhythmSustainShadow": nested_object_summary(shadow_values),
        "rhythmTechniques": {
            "lengthDistribution": dict(sorted(technique_length_distribution.items(), key=lambda item: int(item[0]))),
            "techniqueTypeDistribution": dict(sorted(technique_type_distribution.items())),
            "exactValueDistribution": dict(sorted(technique_value_distribution.items(), key=lambda item: (-item[1], item[0]))),
            "samples": technique_samples,
        },
        "legatoEvidence": {
            **nested_object_summary(legato_evidence_values),
            "samples": legato_samples,
        },
        "sustainSamples": sustain_samples,
        "sustainShadowSamples": sustain_shadow_samples,
        "precisionReplayEvidenceSchema": {
            "eligibleAttackCount": len(eligible),
            "eligibleAttackSchema": {
                key: {"presentCount": eligible_schema_counts[key], "types": dict(sorted(eligible_type_counts[key].items()))}
                for key in sorted(eligible_schema_counts)
            },
            "candidateCount": candidate_count,
            "candidateSchema": {
                key: {"presentCount": candidate_schema_counts[key], "types": dict(sorted(candidate_type_counts[key].items()))}
                for key in sorted(candidate_schema_counts)
            },
            "candidateSelectedDistribution": dict(sorted(candidate_selected.items())),
            "candidatePrimaryDistribution": dict(sorted(candidate_primary.items())),
            "policy": compact_if_small(replay.get("policy")),
            "replayCompleteness": compact_if_small(replay.get("replayCompleteness")),
            "sourceViewEvidenceReady": replay.get("sourceViewEvidenceReady"),
            "attackPolicyReplayReady": replay.get("attackPolicyReplayReady"),
            "precisionStrengthRecomputeReady": replay.get("precisionStrengthRecomputeReady"),
        },
        "candidateInterestPathsExcludingEvents": walk_interest_paths(product_without_events),
        "guards": {
            "expectedEvents": EXPECTED_EVENTS,
            "expectedOnsets": EXPECTED_ONSETS,
            "expectedMeasures": EXPECTED_MEASURES,
            "contentMutation": False,
            "professionalReferenceUsed": False,
            "modalInvoked": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidateSha256": report["candidate"]["sha256"],
        "events": len(events),
        "onsets": len(onset_keys),
        "measures": len(measures),
        "rhythmSustainObjects": report["rhythmSustain"]["presentObjectCount"],
        "rhythmSustainShadowObjects": report["rhythmSustainShadow"]["presentObjectCount"],
        "techniqueAnnotatedEvents": len(technique_samples),
        "legatoEvidenceObjects": report["legatoEvidence"]["presentObjectCount"],
        "eligibleAttacks": len(eligible),
        "output": str(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
