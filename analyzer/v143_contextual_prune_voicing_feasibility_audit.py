#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

EXPECTED_V5_SHA256 = "eb2cd7172ec2edd49e37709b1a4b638c0eb61607524827b3192993ab4b0d52ee"
EXPECTED_POLICY = "attack-v3-plus-harmonic-primary-v4-combined-content-shadow-v5"
OPEN_MIDI_HIGH_TO_LOW = (64, 59, 55, 50, 45, 40)
MAX_FRET = 24
RESOLVER_MAX_MIDI_SPAN = 28


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _legal_positions(midi: int) -> list[tuple[int, int]]:
    return [
        (string_index, int(midi) - open_midi)
        for string_index, open_midi in enumerate(OPEN_MIDI_HIGH_TO_LOW)
        if 0 <= int(midi) - open_midi <= MAX_FRET
    ]


def _physical_assignments(midis: list[int]) -> list[dict[int, tuple[int, int]]]:
    ordered = sorted(set(int(x) for x in midis))
    sets = [_legal_positions(midi) for midi in ordered]
    if any(not positions for positions in sets):
        return []
    out: list[dict[int, tuple[int, int]]] = []
    for positions in itertools.product(*sets):
        strings = [position[0] for position in positions]
        if len(set(strings)) != len(strings):
            continue
        out.append({midi: position for midi, position in zip(ordered, positions)})
    return out


def _resolver_assignments(midis: list[int]) -> list[dict[int, tuple[int, int]]]:
    ordered = sorted(set(int(x) for x in midis))
    if not ordered or len(ordered) > 6 or ordered[-1] - ordered[0] > RESOLVER_MAX_MIDI_SPAN:
        return []
    sets = [_legal_positions(midi) for midi in ordered]
    if any(not positions for positions in sets):
        return []
    out: list[dict[int, tuple[int, int]]] = []
    for positions in itertools.product(*sets):
        strings = tuple(position[0] for position in positions)
        if len(set(strings)) != len(strings):
            continue
        if any(strings[i] <= strings[i + 1] for i in range(len(strings) - 1)):
            continue
        out.append({midi: position for midi, position in zip(ordered, positions)})
    return out


def _format_assignment(assignment: dict[int, tuple[int, int]]) -> list[dict[str, int]]:
    return [
        {"midi": midi, "stringIndexHighToLow": position[0], "fret": position[1]}
        for midi, position in sorted(assignment.items())
    ]


def audit(v5: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    if source_sha256 != EXPECTED_V5_SHA256:
        raise ValueError("unexpected V5 validation bytes")
    if v5.get("validationPassed") is not True or v5.get("policy") != EXPECTED_POLICY:
        raise ValueError("unexpected V5 validation")
    drops = v5.get("combinedVoicingDropAttacks") or []
    if len(drops) != 5:
        raise ValueError(f"expected exactly five V5 voicing-drop attacks, got {len(drops)}")

    rows: list[dict[str, Any]] = []
    counts = {
        "individuallyUnplayable": 0,
        "unavoidableStringCollision": 0,
        "resolverMidiSpanLimit": 0,
        "resolverStringOrdering": 0,
        "other": 0,
    }
    for row in drops:
        selected = sorted(set(int(x) for x in row.get("selected") or []))
        individually_unplayable = [midi for midi in selected if not _legal_positions(midi)]
        physical = _physical_assignments(selected)
        resolver = _resolver_assignments(selected)
        span = selected[-1] - selected[0] if selected else 0

        if individually_unplayable:
            category = "individuallyUnplayable"
            reason = "at least one selected MIDI has no legal 24-fret standard-tuning position"
        elif not physical:
            category = "unavoidableStringCollision"
            reason = "all selected MIDIs are individually playable, but no injective string assignment exists"
        elif span > RESOLVER_MAX_MIDI_SPAN:
            category = "resolverMidiSpanLimit"
            reason = "a physical injective assignment exists, but the deterministic resolver rejects MIDI spans above 28 semitones"
        elif not resolver:
            category = "resolverStringOrdering"
            reason = "a physical injective assignment exists, but none satisfies the deterministic resolver string-order rule"
        else:
            category = "other"
            reason = "resolver can voice the full selected set; drop must arise outside the audited resolver contract"
        counts[category] += 1

        rows.append({
            "measure": int(row["measure"]),
            "step": int(row["step"]),
            "primary": int(row["primary"]),
            "selected": selected,
            "rendered": [int(x) for x in row.get("rendered") or []],
            "midiSpan": span,
            "legalPositions": {
                str(midi): [
                    {"stringIndexHighToLow": string_index, "fret": fret}
                    for string_index, fret in _legal_positions(midi)
                ]
                for midi in selected
            },
            "physicalInjectiveAssignmentCount": len(physical),
            "resolverAssignmentCount": len(resolver),
            "examplePhysicalAssignment": _format_assignment(physical[0]) if physical else None,
            "classification": category,
            "reason": reason,
        })

    checks = {
        "exactFiveDrops": len(rows) == 5,
        "allDropsExplained": counts["other"] == 0,
        "noIndividuallyUnplayablePitch": counts["individuallyUnplayable"] == 0,
        "expectedStringCollisionCount": counts["unavoidableStringCollision"] == 2,
        "expectedResolverSpanCount": counts["resolverMidiSpanLimit"] == 3,
        "noOtherResolverOrderingFailure": counts["resolverStringOrdering"] == 0,
    }
    return {
        "schemaVersion": 1,
        "classification": "v143-combined-v5-voicing-feasibility-audit",
        "sourceV5ValidationSha256": source_sha256,
        "tuningOpenMidiHighToLow": list(OPEN_MIDI_HIGH_TO_LOW),
        "maxFret": MAX_FRET,
        "resolverMaxMidiSpan": RESOLVER_MAX_MIDI_SPAN,
        "dropCount": len(rows),
        "classificationCounts": counts,
        "drops": rows,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "modalInvoked": False,
        "productionModified": False,
        "newNumericThresholdIntroduced": False,
        "pitchIdentityChanged": False,
        "validationChecks": checks,
        "validationPassed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("v5_validation", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source_sha = _sha256(args.v5_validation)
    report = audit(json.loads(args.v5_validation.read_text()), source_sha)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if report["validationPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
