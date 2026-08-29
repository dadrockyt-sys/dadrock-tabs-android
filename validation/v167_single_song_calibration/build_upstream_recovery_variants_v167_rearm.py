#!/usr/bin/env python3
"""Guard-only re-arm adapter for the V167 upstream-recovery variant builder.

The first arm failed before any scorer/reference read because the validator treated
Iteration 002 Bass as globally monophonic after its already-frozen timing transform.
That transform can legitimately move multiple pre-existing events onto one step.

This adapter pins the exact preregistered builder and changes only that invariant:
pre-existing Iteration 002 Bass step collisions are preserved exactly, while a
recovery rule may still add at most one event to a step that was empty in the
Iteration 002 base. Recovery ranking, thresholds, timing, scopes, and all 146
predeclared variants are otherwise unchanged. No scorer/reference input exists.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

FROZEN_BASE_BUILDER_BLOB = "24413d321f64bbfcce48812ceb85b4593dcfa80c"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_base_builder():
    path = Path(__file__).with_name("build_upstream_recovery_variants_v167.py")
    if not path.is_file() or git_blob_sha(path) != FROZEN_BASE_BUILDER_BLOB:
        raise RuntimeError("V167 re-arm base-builder identity mismatch")
    spec = importlib.util.spec_from_file_location("_v167_preregistered_recovery_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load preregistered V167 recovery builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base_builder()


def bass_configs() -> Iterable[dict[str, Any]]:
    """Keep the exact parameter grid while clarifying the post-timing cap scope."""
    for raw in BASE.bass_configs():
        config = dict(raw)
        if not bool(config.get("baseline", False)):
            if int(config.pop("stepCap")) != 1:
                raise RuntimeError("unexpected preregistered Bass recovery cap")
            config["newRecoveryCapPerPreviouslyEmptyStep"] = 1
            config["preExistingIteration002StepCollisionsPreserved"] = True
        yield config


def build_bass(
    base_bass: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    lattice: list[float],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = copy.deepcopy(base_bass)
    base_step_counts = Counter(int(n["absoluteGridStep"]) for n in base_bass)
    if config.get("baseline"):
        return out, {
            "added": 0,
            "eligible": 0,
            "sitesWithAdds": 0,
            "preExistingCollisionSteps": sum(count > 1 for count in base_step_counts.values()),
        }

    occupied_steps = set(base_step_counts)
    by_site: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_site[int(row["originalFrame"])].append(row)

    eligible = 0
    added = 0
    sites_with_adds = 0
    for site in sorted(by_site):
        ranked = []
        for row in by_site[site]:
            if config["fundamentalPresentRequired"] and not bool(row.get("fundamentalPresent", False)):
                continue
            if not BASE.bass_scope_ok(row, str(config["scope"])):
                continue
            if float(row.get("templateRank", 0.0)) < float(config["templateRankMin"]):
                continue
            if float(row.get("onsetSupport", 0.0)) < float(config["onsetSupportMin"]):
                continue
            if float(row.get("activitySupport", 0.0)) < float(config["activitySupportMin"]):
                continue
            absolute = BASE.corrected_step(float(row["seconds"]), lattice)
            if absolute is None or absolute in occupied_steps:
                continue
            eligible += 1
            ranked.append((row, absolute))

        ranked.sort(key=lambda item: (
            -float(item[0].get("templateRank", 0.0)),
            -float(item[0].get("combinedPitchScore", 0.0)),
            -float(item[0].get("pyinProximity", 0.0)),
            -float(item[0].get("onsetSupport", 0.0)),
            -float(item[0].get("activitySupport", 0.0)),
            int(item[0]["midi"]),
        ))

        for row, absolute in ranked:
            if absolute in occupied_steps:
                continue
            midi = int(row["midi"])
            evidence = {
                "originalFrame": int(row["originalFrame"]),
                "refinedFrame": int(row["refinedFrame"]),
                "seconds": float(row["seconds"]),
                "templateRank": float(row["templateRank"]),
                "combinedPitchScore": float(row["combinedPitchScore"]),
                "harmonicZScore": float(row["harmonicZScore"]),
                "fundamentalPresent": bool(row["fundamentalPresent"]),
                "medianPyinMidi": row.get("medianPyinMidi"),
                "medianPyinVoicedProbability": float(row.get("medianPyinVoicedProbability", 0.0)),
                "pyinProximity": float(row.get("pyinProximity", 0.0)),
                "onsetSupport": float(row["onsetSupport"]),
                "activitySupport": float(row["activitySupport"]),
                "hadNearbyStableState": bool(row.get("hadNearbyStableState", False)),
                "retainedOnset": bool(row.get("retainedOnset", False)),
            }
            out.append(BASE.event_for_recovery(absolute, midi, "bass", config, evidence))
            occupied_steps.add(absolute)
            added += 1
            sites_with_adds += 1
            break

    out.sort(key=lambda n: (int(n["absoluteGridStep"]), int(n["midi"])))
    final_step_counts = Counter(int(n["absoluteGridStep"]) for n in out)
    for step, count in final_step_counts.items():
        if step in base_step_counts:
            if count != base_step_counts[step]:
                raise AssertionError("Bass recovery changed a pre-existing Iteration 002 step occupancy")
        elif count != 1:
            raise AssertionError("Bass recovery added more than one event to a previously empty step")
    if len(out) - len(base_bass) != added:
        raise AssertionError("Bass recovery addition count drift")

    return out, {
        "added": added,
        "eligible": eligible,
        "sitesWithAdds": sites_with_adds,
        "preExistingCollisionSteps": sum(count > 1 for count in base_step_counts.values()),
        "preExistingCollisionsPreserved": True,
        "newRecoveryEventsAddedOnlyToPreviouslyEmptySteps": True,
    }


def main() -> int:
    BASE.bass_configs = bass_configs
    BASE.build_bass = build_bass
    return int(BASE.main())


if __name__ == "__main__":
    raise SystemExit(main())
