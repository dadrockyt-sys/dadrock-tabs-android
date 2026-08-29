#!/usr/bin/env python3
"""Build the preregistered V167 same-MIDI temporal-recurrence Guitar family.

Reference-blind generation only. The immutable I005 winner contains 1050 original
I003 Guitar events plus exactly 48 state-split additions. This builder never invents,
retimes, or reference-selects an event: it keeps all 1050 I003 events and filters
only the exact 48 frozen I005 additions by preregistered same-MIDI connected-burst
rules. Bass is copied exactly from I005. No scorer or professional-reference input
exists.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

EXPECTED = {
    "i003Sha256": "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115",
    "i005Sha256": "86329ebc25e589f566d466a7a65cae35a158c25f470b1c034973f3dbc7d38b31",
    "diagnosisSha256": "fd5c12339e594ae1207e2c4edb2eb034a9249de15ab99d3623cf5f6922061b36",
    "i003GuitarCount": 1050,
    "i005GuitarCount": 1098,
    "bassCount": 512,
    "additionCount": 48,
}

STEPS_PER_MEASURE = 16
EXPECTED_VARIANT_ADDITIONS = {
    "recur-repro-i005": 48,
    "recur-gap1-earliest": 43,
    "recur-gap1-strongest": 43,
    "recur-gap2-strongest": 40,
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def coord(note: Mapping[str, Any]) -> tuple[int, float, int]:
    return int(note["measure"]), float(note["step"]), int(note["midi"])


def normalized(events: Iterable[Mapping[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        coord(row)
        for row in events
        if not bool(row.get("excludeFromScoring", False))
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


def recovery_evidence(note: Mapping[str, Any]) -> Mapping[str, Any]:
    wrapper = note.get("v167RecoverySweepEvidence") or {}
    rule = wrapper.get("rule") or {}
    evidence = wrapper.get("evidence") or {}
    if rule.get("id") != "gss-active-only":
        raise RuntimeError("I005 addition is not from frozen gss-active-only rule")
    if evidence.get("stateSplitBranch") != "active_max":
        raise RuntimeError("I005 addition is not active_max branch")
    if not bool(evidence.get("basicPitchActiveAtSite", False)):
        raise RuntimeError("I005 addition lacks frozen active Basic Pitch state")
    return evidence


def configs() -> list[dict[str, Any]]:
    return [
        {
            "id": "recur-repro-i005",
            "reproductionControl": True,
            "maxConnectedGapSteps": None,
            "burstSelector": None,
            "description": "exact normalized I005 reproduction control",
        },
        {
            "id": "recur-gap1-earliest",
            "reproductionControl": False,
            "maxConnectedGapSteps": 1,
            "burstSelector": "earliest",
            "description": "collapse each same-MIDI gap<=1 connected burst to its earliest addition",
        },
        {
            "id": "recur-gap1-strongest",
            "reproductionControl": False,
            "maxConnectedGapSteps": 1,
            "burstSelector": "strongest_evidence",
            "description": "collapse each same-MIDI gap<=1 connected burst by max onset, then activity, then earliest",
        },
        {
            "id": "recur-gap2-strongest",
            "reproductionControl": False,
            "maxConnectedGapSteps": 2,
            "burstSelector": "strongest_evidence",
            "description": "collapse each same-MIDI gap<=2 connected burst by max onset, then activity, then earliest",
        },
    ]


def connected_components(rows: list[Mapping[str, Any]], max_gap: int) -> list[list[Mapping[str, Any]]]:
    by_midi: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        by_midi[int(row["midi"])].append(row)
    components: list[list[Mapping[str, Any]]] = []
    for midi in sorted(by_midi):
        ordered = sorted(by_midi[midi], key=lambda r: int(r["absoluteGridStep"]))
        current: list[Mapping[str, Any]] = []
        previous_step: int | None = None
        for row in ordered:
            step = int(row["absoluteGridStep"])
            if previous_step is None or step - previous_step <= max_gap:
                current.append(row)
            else:
                components.append(current)
                current = [row]
            previous_step = step
        if current:
            components.append(current)
    return components


def choose_burst_member(component: list[Mapping[str, Any]], selector: str) -> Mapping[str, Any]:
    if not component:
        raise RuntimeError("empty recurrence component")
    if selector == "earliest":
        return min(component, key=lambda r: int(r["absoluteGridStep"]))
    if selector == "strongest_evidence":
        def key(row: Mapping[str, Any]) -> tuple[float, float, int]:
            evidence = recovery_evidence(row)
            return (
                float(evidence.get("onsetSupport", 0.0)),
                float(evidence.get("activitySupport", 0.0)),
                -int(row["absoluteGridStep"]),
            )
        return max(component, key=key)
    raise ValueError(f"unknown burst selector: {selector}")


def kept_additions_for_config(
    additions: list[Mapping[str, Any]],
    config: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], dict[str, Any]]:
    if bool(config["reproductionControl"]):
        return list(additions), {
            "connectedComponentCount": len(additions),
            "burstComponentCount": 0,
            "burstEventCount": 0,
            "collapsedEventCount": 0,
        }

    max_gap = int(config["maxConnectedGapSteps"])
    selector = str(config["burstSelector"])
    components = connected_components(additions, max_gap)
    kept: list[Mapping[str, Any]] = []
    burst_components = 0
    burst_events = 0
    for component in components:
        if len(component) == 1:
            kept.extend(component)
            continue
        burst_components += 1
        burst_events += len(component)
        kept.append(choose_burst_member(component, selector))
    kept.sort(key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"])))
    return kept, {
        "connectedComponentCount": len(components),
        "burstComponentCount": burst_components,
        "burstEventCount": burst_events,
        "collapsedEventCount": len(additions) - len(kept),
    }


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
        "schema": "dadrock.tabs.v167.temporal-recurrence-score-candidate.v1",
        "version": "V167",
        "status": "PREDECLARED_TEMPORAL_RECURRENCE_VARIANT_FROZEN_BEFORE_SCORING",
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
        "v167TemporalRecurrencePruning": {
            "config": copy.deepcopy(config),
            "summary": copy.deepcopy(summary),
            "sourceIteration": 5,
            "originalI003GuitarEventsAlwaysKept": True,
            "onlyFrozenI005StateSplitAdditionsFiltered": True,
            "selectorUsesReference": False,
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
        raise RuntimeError("temporal-recurrence generation outputs must not pre-exist")
    for path, expected in (
        (args.i003, EXPECTED["i003Sha256"]),
        (args.i005, EXPECTED["i005Sha256"]),
        (args.diagnosis, EXPECTED["diagnosisSha256"]),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen recurrence input SHA mismatch: {path}: {actual}")

    i003 = json.loads(args.i003.read_text(encoding="utf-8"))
    i005 = json.loads(args.i005.read_text(encoding="utf-8"))
    diagnosis = json.loads(args.diagnosis.read_text(encoding="utf-8"))
    if int((i003.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("recurrence base must be frozen I003")
    if int((i005.get("calibration") or {}).get("iteration", -1)) != 5:
        raise RuntimeError("recurrence source must be frozen I005")
    if diagnosis.get("schema") != "dadrock.tabs.v167.post-topology-temporal-recurrence-analysis.v1":
        raise RuntimeError("temporal recurrence diagnosis schema is not frozen expected v1")
    if diagnosis.get("additionCount") != EXPECTED["additionCount"]:
        raise RuntimeError("temporal recurrence diagnosis addition count drift")
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
        raise RuntimeError(f"I005 recurrence addition count drift: {len(additions_rich)}")
    if len({coord(row) for row in additions_rich}) != len(additions_rich):
        raise RuntimeError("I005 additions contain duplicate normalized coordinates")
    if len({int(row["absoluteGridStep"]) for row in additions_rich}) != len(additions_rich):
        raise RuntimeError("I005 additions no longer occupy 48 unique grid steps")
    for row in additions_rich:
        recovery_evidence(row)

    base_guitar = [compact_note(row, "combinedGuitar") for row in i003_guitar_rich]
    bass = [compact_note(row, "bass") for row in i005_bass_rich]

    manifest: dict[str, Any] = {
        "schema": "dadrock.tabs.v167.predeclared-temporal-recurrence-guitar-manifest.v1",
        "version": "V167",
        "status": "FROZEN_BEFORE_REFERENCE_SCORING",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.i003),
            "iteration005Sha256": sha256_file(args.i005),
            "temporalDiagnosisSha256": sha256_file(args.diagnosis),
            "baseGuitarCount": len(base_guitar),
            "sourceI005AdditionCount": len(additions_rich),
            "bassCount": len(bass),
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
            "noThresholdSweep": True,
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
        kept_rows, component_summary = kept_additions_for_config(additions_rich, config)
        expected_added = EXPECTED_VARIANT_ADDITIONS[str(config["id"])]
        if len(kept_rows) != expected_added:
            raise RuntimeError(
                f"{config['id']} addition count drift: {len(kept_rows)} != {expected_added}"
            )
        guitar = copy.deepcopy(base_guitar) + [
            compact_note(row, "combinedGuitar") for row in kept_rows
        ]
        guitar.sort(key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"])))
        summary = {
            "baseI003GuitarEvents": len(base_guitar),
            "sourceI005Additions": len(additions_rich),
            "keptI005Additions": len(kept_rows),
            "prunedI005Additions": len(additions_rich) - len(kept_rows),
            "guitarEventCount": len(guitar),
            "bassEventCount": len(bass),
            **component_summary,
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
        raise RuntimeError("recurrence reproduction control Guitar differs from I005")
    if normalized(repro_payload["streams"]["bass"]) != normalized(i005_bass_rich):
        raise RuntimeError("recurrence reproduction control Bass differs from I005")

    write_json(args.manifest, manifest)
    print(json.dumps({
        "variantCount": len(manifest["variants"]),
        "variantAdditionCounts": {
            row["id"]: row["summary"]["keptI005Additions"]
            for row in manifest["variants"]
        },
        "manifestSha256": sha256_file(args.manifest),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
