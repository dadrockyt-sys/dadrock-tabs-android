#!/usr/bin/env python3
"""Build the preregistered V167 active-topology Guitar pruning family.

Reference-blind generation only. The immutable I005 winner contains 1050 original
I003 Guitar events plus exactly 48 state-split additions. This builder never invents
or retimes an event: it keeps all 1050 I003 coordinates and deterministically filters
only those 48 additions by their already-frozen active-pitch topology evidence.
Bass is copied exactly from I005. No scorer or professional-reference input exists.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

EXPECTED = {
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "diagnosisSha256": "fe7e826724a11e115a25f932d4b58ed88e3aedae67fb54142cc532cc40ab8450",
    "i003GuitarCount": 1050,
    "i005GuitarCount": 1098,
    "bassCount": 512,
    "additionCount": 48,
}

STEPS_PER_MEASURE = 16
CHORD_INTERVALS = frozenset({3, 4, 5, 7, 8, 9, 10})
EXPECTED_TOPOLOGY_COUNTS = {
    "single": 23,
    "chord": 18,
    "near_unison": 5,
    "remote": 2,
}
EXPECTED_VARIANT_ADDITIONS = {
    "topo-repro-i005": 48,
    "topo-single-or-chord": 41,
    "topo-single-only": 23,
    "topo-chord-only": 18,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def compact_note(note: Mapping[str, Any], stream: str) -> dict[str, Any]:
    absolute = int(note["absoluteGridStep"])
    measure = int(note["measure"])
    step = int(round(float(note["step"])))
    midi = int(note["midi"])
    if (measure - 1) * STEPS_PER_MEASURE + step != absolute:
        raise RuntimeError(f"{stream} coordinate invariant failed")
    return {
        "measure": measure,
        "step": step,
        "midi": midi,
        "absoluteGridStep": absolute,
    }


def coord(note: Mapping[str, Any]) -> tuple[int, float, int]:
    return int(note["measure"]), float(note["step"]), int(note["midi"])


def normalized(events: Iterable[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        coord(row)
        for row in events
        if not bool(row.get("excludeFromScoring", False))
    )


def topology_for_addition(note: Mapping[str, Any]) -> str:
    wrapper = note.get("v167RecoverySweepEvidence") or {}
    rule = wrapper.get("rule") or {}
    evidence = wrapper.get("evidence") or {}
    if rule.get("id") != "gss-active-only":
        raise RuntimeError("I005 addition is not from frozen gss-active-only rule")
    if evidence.get("stateSplitBranch") != "active_max":
        raise RuntimeError("I005 addition is not active_max branch")
    if not bool(evidence.get("basicPitchActiveAtSite", False)):
        raise RuntimeError("I005 active_max addition lacks active Basic Pitch state")
    active_midis = sorted({int(x) for x in evidence.get("activeMidisAtSite") or []})
    if not active_midis:
        raise RuntimeError("I005 addition lacks frozen active MIDI context")
    nearest = evidence.get("nearestDifferentActiveSemitoneDistance")
    if nearest is None:
        if len(active_midis) != 1:
            raise RuntimeError("no-different-active evidence inconsistent with active MIDI count")
        return "single"
    nearest = int(nearest)
    if len(active_midis) < 2:
        raise RuntimeError("different-active interval present with singleton active context")
    if nearest in CHORD_INTERVALS:
        return "chord"
    if nearest in {1, 2}:
        return "near_unison"
    return "remote"


def configs() -> list[dict[str, Any]]:
    return [
        {
            "id": "topo-repro-i005",
            "reproductionControl": True,
            "keepTopologies": ["single", "chord", "near_unison", "remote"],
            "description": "exact normalized I005 reproduction control",
        },
        {
            "id": "topo-single-or-chord",
            "reproductionControl": False,
            "keepTopologies": ["single", "chord"],
            "description": "keep isolated-active reattacks or chord-interval active context",
        },
        {
            "id": "topo-single-only",
            "reproductionControl": False,
            "keepTopologies": ["single"],
            "description": "keep only additions with no different active pitch at site",
        },
        {
            "id": "topo-chord-only",
            "reproductionControl": False,
            "keepTopologies": ["chord"],
            "description": "keep only additions whose nearest different active pitch is a preregistered chord interval",
        },
    ]


def score_payload(
    i005: Mapping[str, Any],
    guitar: list[dict[str, Any]],
    bass: list[dict[str, Any]],
    config: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    safety = i005.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise RuntimeError("I005 safety boundary invalid")
    return {
        "schema": "dadrock.tabs.v167.active-topology-score-candidate.v1",
        "version": "V167",
        "status": "PREDECLARED_ACTIVE_TOPOLOGY_VARIANT_FROZEN_BEFORE_SCORING",
        "song": copy.deepcopy(i005.get("song")),
        "safety": {
            **copy.deepcopy(safety),
            "referenceRead": False,
            "scorerRead": False,
            "humanCorrection": False,
            "individualEventSelectionByReference": False,
            "newReferenceFacingScoreCallsByGenerator": 0,
        },
        "streams": {
            "combinedGuitar": guitar,
            "bass": bass,
        },
        "v167ActiveTopologyPruning": {
            "config": copy.deepcopy(config),
            "summary": copy.deepcopy(summary),
            "sourceIteration": 5,
            "originalI003GuitarEventsAlwaysKept": True,
            "onlyFrozenI005StateSplitAdditionsFiltered": True,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--i003", type=Path, required=True)
    ap.add_argument("--i005", type=Path, required=True)
    ap.add_argument("--diagnosis", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    if args.output_dir.exists() or args.manifest.exists():
        raise RuntimeError("active-topology generation outputs must not pre-exist")
    for path, expected in (
        (args.i003, EXPECTED["i003Sha256"]),
        (args.i005, EXPECTED["i005Sha256"]),
        (args.diagnosis, EXPECTED["diagnosisSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen topology input SHA mismatch: {path}: {actual}")

    i003 = json.loads(args.i003.read_text(encoding="utf-8"))
    i005 = json.loads(args.i005.read_text(encoding="utf-8"))
    diagnosis = json.loads(args.diagnosis.read_text(encoding="utf-8"))
    if int((i003.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("topology base must be frozen I003")
    if int((i005.get("calibration") or {}).get("iteration", -1)) != 5:
        raise RuntimeError("topology source must be frozen I005")
    if diagnosis.get("status") != "POST_I005_AGGREGATE_REFERENCE_BLIND_ANALYSIS_FROZEN":
        raise RuntimeError("topology diagnosis is not frozen")
    dpolicy = diagnosis.get("policy") or {}
    if dpolicy.get("professionalReferenceReadByAnalysis") is not False:
        raise RuntimeError("diagnosis reference boundary invalid")
    if dpolicy.get("scorerReadByAnalysis") is not False:
        raise RuntimeError("diagnosis scorer boundary invalid")
    if dpolicy.get("newRuleSelectedByThisAnalysis") is not False:
        raise RuntimeError("diagnosis unexpectedly selected a rule")

    i003_streams = i003.get("streams") or {}
    i005_streams = i005.get("streams") or {}
    i003_guitar_rich = list(i003_streams.get("combinedGuitar") or [])
    i005_guitar_rich = list(i005_streams.get("combinedGuitar") or [])
    i005_bass_rich = list(i005_streams.get("bass") or [])
    if len(i003_guitar_rich) != EXPECTED["i003GuitarCount"]:
        raise RuntimeError("I003 Guitar count drift")
    if len(i005_guitar_rich) != EXPECTED["i005GuitarCount"]:
        raise RuntimeError("I005 Guitar count drift")
    if len(i005_bass_rich) != EXPECTED["bassCount"]:
        raise RuntimeError("I005 Bass count drift")

    base_coords = set(normalized(i003_guitar_rich))
    additions_rich = [row for row in i005_guitar_rich if coord(row) not in base_coords]
    if len(additions_rich) != EXPECTED["additionCount"]:
        raise RuntimeError(f"I005 topology addition count drift: {len(additions_rich)}")
    if len({coord(row) for row in additions_rich}) != len(additions_rich):
        raise RuntimeError("I005 additions contain duplicate normalized coordinates")

    topology_by_coord: dict[tuple[int, float, int], str] = {}
    topology_counts: Counter[str] = Counter()
    for row in additions_rich:
        topology = topology_for_addition(row)
        topology_by_coord[coord(row)] = topology
        topology_counts[topology] += 1
    if dict(topology_counts) != EXPECTED_TOPOLOGY_COUNTS:
        raise RuntimeError(
            f"frozen topology distribution drift: {dict(topology_counts)} != {EXPECTED_TOPOLOGY_COUNTS}"
        )

    base_guitar = [compact_note(row, "combinedGuitar") for row in i003_guitar_rich]
    compact_additions = {
        coord(row): compact_note(row, "combinedGuitar") for row in additions_rich
    }
    bass = [compact_note(row, "bass") for row in i005_bass_rich]

    manifest: dict[str, Any] = {
        "schema": "dadrock.tabs.v167.predeclared-active-topology-guitar-manifest.v1",
        "version": "V167",
        "status": "FROZEN_BEFORE_REFERENCE_SCORING",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.i003),
            "iteration005Sha256": sha256_file(args.i005),
            "postI005DiagnosisSha256": sha256_file(args.diagnosis),
            "baseGuitarCount": len(base_guitar),
            "sourceI005AdditionCount": len(additions_rich),
            "bassCount": len(bass),
            "sourceTopologyCounts": dict(topology_counts),
        },
        "policy": {
            "professionalReferenceReadByGenerator": False,
            "scorerReadByGenerator": False,
            "newReferenceFacingScoreCallsByGenerator": 0,
            "allVariantRulesPredeclaredBeforeScoring": True,
            "individualEventSelectionByReference": False,
            "onlyFrozenI005AdditionsFiltered": True,
            "allI003GuitarEventsAlwaysKept": True,
            "bassFixedExactlyToI005": True,
            "reproductionControlScored": False,
            "newGuitarVariantScoreCallsPlanned": 3,
            "bassScoreCallsPlanned": 0,
            "automaticIteration006Promotion": False,
            "promotionEligibility": {
                "minimumF1GainPercentagePointsVsI005": 0.10,
                "precisionMustBeAtLeastI005": True,
            },
            "tieBreak": [
                "max_primary_f1",
                "max_primary_precision",
                "fewer_kept_i005_additions",
                "lexicographic_rule_id",
            ],
        },
        "variants": [],
    }

    for config in configs():
        keep = set(str(x) for x in config["keepTopologies"])
        kept_coords = sorted(
            c for c, topology in topology_by_coord.items() if topology in keep
        )
        expected_added = EXPECTED_VARIANT_ADDITIONS[str(config["id"])]
        if len(kept_coords) != expected_added:
            raise RuntimeError(
                f"{config['id']} addition count drift: {len(kept_coords)} != {expected_added}"
            )
        guitar = copy.deepcopy(base_guitar) + [
            copy.deepcopy(compact_additions[c]) for c in kept_coords
        ]
        guitar.sort(key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"])))
        summary = {
            "baseI003GuitarEvents": len(base_guitar),
            "sourceI005Additions": len(additions_rich),
            "keptI005Additions": len(kept_coords),
            "prunedI005Additions": len(additions_rich) - len(kept_coords),
            "guitarEventCount": len(guitar),
            "bassEventCount": len(bass),
            "keptTopologyCounts": dict(
                Counter(topology_by_coord[c] for c in kept_coords)
            ),
        }
        payload = score_payload(i005, guitar, bass, config, summary)
        path = args.output_dir / f"{config['id']}.json"
        write_json(path, payload)
        manifest["variants"].append(
            {
                "id": config["id"],
                "reproductionControl": bool(config["reproductionControl"]),
                "config": copy.deepcopy(config),
                "summary": summary,
                "relativePath": path.name,
                "sha256": sha256_file(path),
                "counts": {
                    "combinedGuitar": len(guitar),
                    "bass": len(bass),
                },
            }
        )

    repro = next(row for row in manifest["variants"] if row["reproductionControl"])
    repro_payload = json.loads(
        (args.output_dir / str(repro["relativePath"])).read_text(encoding="utf-8")
    )
    if normalized(repro_payload["streams"]["combinedGuitar"]) != normalized(i005_guitar_rich):
        raise RuntimeError("topology reproduction control Guitar differs from I005")
    if normalized(repro_payload["streams"]["bass"]) != normalized(i005_bass_rich):
        raise RuntimeError("topology reproduction control Bass differs from I005")

    write_json(args.manifest, manifest)
    print(
        json.dumps(
            {
                "variantCount": len(manifest["variants"]),
                "newVariantCount": sum(
                    not row["reproductionControl"] for row in manifest["variants"]
                ),
                "sourceTopologyCounts": dict(topology_counts),
                "variantAdditions": {
                    row["id"]: row["summary"]["keptI005Additions"]
                    for row in manifest["variants"]
                },
                "manifestSha256": sha256_file(args.manifest),
                "referenceRead": False,
                "scorerRead": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
