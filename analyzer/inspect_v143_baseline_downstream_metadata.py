#!/usr/bin/env python3
"""Inspect pinned V143 baseline downstream metadata without changing musical content.

This is an evidence-only utility. It reads the immutable materialized candidate JSON and
summarizes the existing event metadata and any candidate fields that may carry source-side
technique/sustain evidence. It does not infer, score, threshold, or modify notes.
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
PERFORMANCE_KEYS = (
    "sustainSteps",
    "palmMute",
    "letRing",
    "ghost",
    "accent",
    "harmonic",
    "technique",
    "techniqueTargetString",
    "techniqueTargetFret",
)
INTEREST_TERMS = (
    "sustain",
    "technique",
    "hammer",
    "pull",
    "slide",
    "bend",
    "vibrato",
    "palm",
    "ring",
    "ghost",
    "accent",
    "harmonic",
    "duration",
    "evidence",
    "diagnostic",
    "source",
    "attack",
    "onset",
)


def stable_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        return str(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


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


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "measure",
        "step",
        "midi",
        "string",
        "fret",
        *PERFORMANCE_KEYS,
    )
    return {key: event.get(key) for key in keys if key in event}


def is_non_neutral(event: dict[str, Any]) -> bool:
    sustain = event.get("sustainSteps")
    if isinstance(sustain, (int, float)) and sustain > 1:
        return True
    if any(bool(event.get(key)) for key in ("palmMute", "letRing", "ghost", "accent", "harmonic")):
        return True
    if event.get("technique") not in (None, "", "none", "None"):
        return True
    if event.get("techniqueTargetString") is not None or event.get("techniqueTargetFret") is not None:
        return True
    return False


def walk_interest_paths(value: Any, path: str = "$", depth: int = 0, out: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if out is None:
        out = []
    if depth > 8 or len(out) >= 500:
        return out
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            key_lower = str(key).lower()
            if any(term in key_lower for term in INTEREST_TERMS):
                item: dict[str, Any] = {
                    "path": child_path,
                    "type": type_name(child),
                }
                if isinstance(child, (str, int, float, bool)) or child is None:
                    item["value"] = child
                elif isinstance(child, list):
                    item["length"] = len(child)
                    if child and len(child) <= 8 and all(isinstance(x, (str, int, float, bool)) or x is None for x in child):
                        item["sample"] = child
                elif isinstance(child, dict):
                    item["keys"] = sorted(str(k) for k in child.keys())[:40]
                out.append(item)
            walk_interest_paths(child, child_path, depth + 1, out)
            if len(out) >= 500:
                break
    elif isinstance(value, list):
        # Inspect representative array objects only; event-level metadata is summarized separately.
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
        raise SystemExit("candidate root must be a JSON object")

    events = product.get("events")
    if not isinstance(events, list) or not all(isinstance(event, dict) for event in events):
        raise SystemExit("candidate must expose a direct object-array events field")

    onset_keys = sorted({(int(event.get("measure", 0)), int(event.get("step", 0))) for event in events})
    measures = sorted({int(event.get("measure", 0)) for event in events})
    if len(events) != EXPECTED_EVENTS:
        raise SystemExit(f"event count mismatch: expected {EXPECTED_EVENTS}, got {len(events)}")
    if len(onset_keys) != EXPECTED_ONSETS:
        raise SystemExit(f"onset count mismatch: expected {EXPECTED_ONSETS}, got {len(onset_keys)}")
    if len(measures) != EXPECTED_MEASURES or measures != list(range(1, EXPECTED_MEASURES + 1)):
        raise SystemExit("measure coverage mismatch")

    schema_counts: dict[str, int] = collections.Counter()
    type_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    distributions: dict[str, collections.Counter[str]] = {key: collections.Counter() for key in PERFORMANCE_KEYS}
    signature_counts: collections.Counter[str] = collections.Counter()

    ordered_events = sorted(
        enumerate(events),
        key=lambda pair: (
            int(pair[1].get("measure", 0)),
            int(pair[1].get("step", 0)),
            int(pair[1].get("string", 99)) if pair[1].get("string") is not None else 99,
            int(pair[1].get("midi", -1)) if pair[1].get("midi") is not None else -1,
            pair[0],
        ),
    )
    sorted_events = [event for _, event in ordered_events]

    for event in events:
        for key, value in event.items():
            schema_counts[key] += 1
            type_counts[key][type_name(value)] += 1
        signature = {}
        for key in PERFORMANCE_KEYS:
            value = event.get(key)
            distributions[key][stable_value(value)] += 1
            signature[key] = value
        signature_counts[json.dumps(signature, sort_keys=True, separators=(",", ":"), default=str)] += 1

    non_neutral_indices = [index for index, event in enumerate(sorted_events) if is_non_neutral(event)]
    contexts: list[dict[str, Any]] = []
    for index in non_neutral_indices:
        current = sorted_events[index]
        start = max(0, index - 2)
        end = min(len(sorted_events), index + 3)
        contexts.append(
            {
                "eventIndex": index,
                "event": compact_event(current),
                "neighbors": [compact_event(sorted_events[j]) for j in range(start, end) if j != index],
            }
        )

    top_level = {
        key: {
            "type": type_name(value),
            **({"length": len(value)} if isinstance(value, (list, dict)) else {}),
        }
        for key, value in sorted(product.items())
    }

    # Avoid reporting the 967-event array itself as a source-evidence path; its performance
    # metadata is already fully summarized above.
    product_without_events = {key: value for key, value in product.items() if key != "events"}
    interest_paths = walk_interest_paths(product_without_events)

    report = {
        "schemaVersion": "v143-baseline-downstream-metadata-inspection-v1",
        "purpose": "evidence-only inspection; no inference or musical mutation",
        "candidate": {
            "path": str(candidate_path),
            "sha256": sha256_file(candidate_path),
            "eventCount": len(events),
            "uniqueOnsets": len(onset_keys),
            "measureCount": len(measures),
            "measureRange": [measures[0], measures[-1]],
        },
        "topLevel": top_level,
        "eventSchema": {
            key: {
                "presentCount": schema_counts[key],
                "types": dict(sorted(type_counts[key].items())),
            }
            for key in sorted(schema_counts)
        },
        "performanceMetadataDistributions": {
            key: dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))
            for key, counter in distributions.items()
        },
        "performanceSignatureCounts": [
            {"count": count, "signature": json.loads(signature)}
            for signature, count in signature_counts.most_common()
        ],
        "nonNeutralPerformanceEventCount": len(non_neutral_indices),
        "nonNeutralPerformanceContexts": contexts,
        "candidateInterestPathsExcludingEvents": interest_paths,
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
        "nonNeutralPerformanceEvents": len(non_neutral_indices),
        "interestPaths": len(interest_paths),
        "output": str(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
