#!/usr/bin/env python3
"""Build all predeclared V167 upstream-recovery calibration variants before scoring.

This generator is reference-blind: it reads only the frozen Iteration 002 candidate,
the frozen V167 upstream evidence pool, and the frozen V166 subdivision timebase.
It emits score-minimal candidate payloads plus a SHA256 manifest. No scorer or
professional reference path is accepted as input.
"""
from __future__ import annotations

import argparse
import bisect
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

STEPS_PER_MEASURE = 16
GLOBAL_PHASE_CORRECTION = -12
GUITAR_CAP = 6
BASS_CAP = 1
EXPECTED_BASE_COUNTS = {"combinedGuitar": 1050, "bass": 402}
EXPECTED_POOL_BLOB_SHA256 = "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673"

GUITAR_RANK_THRESHOLDS = (0.80, 0.90, 0.95, 0.975)
GUITAR_ONSET_THRESHOLDS = (0.35, 0.50, 0.65)
GUITAR_MAX_ADDS_PER_SITE = (1, 2)
GUITAR_INACTIVE_ONLY = (True, False)
GUITAR_ACTIVITY_MIN = 0.05

BASS_RANK_THRESHOLDS = (0.80, 0.90, 0.95, 0.975)
BASS_ONSET_THRESHOLDS = (0.20, 0.35, 0.50)
BASS_ACTIVITY_THRESHOLDS = (0.04, 0.10)
BASS_SCOPES = ("all", "no_stable_state", "low_register", "low_register_no_stable_state")
BASS_LOW_REGISTER_MAX_MIDI = 40


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def nearest_lattice_step(seconds: float, lattice: list[float]) -> int:
    x = float(seconds)
    index = bisect.bisect_left(lattice, x)
    if index <= 0:
        return 0
    if index >= len(lattice):
        return len(lattice) - 1
    before, after = index - 1, index
    db, da = abs(x - lattice[before]), abs(lattice[after] - x)
    return before if db <= da else after


def corrected_step(seconds: float, lattice: list[float]) -> int | None:
    raw = nearest_lattice_step(seconds, lattice)
    corrected = raw + GLOBAL_PHASE_CORRECTION
    return corrected if corrected >= 0 else None


def compact_base_note(note: dict[str, Any], stream: str) -> dict[str, Any]:
    absolute = int(note["absoluteGridStep"])
    measure = int(note["measure"])
    step = int(round(float(note["step"])))
    midi = int(note["midi"])
    if (measure - 1) * STEPS_PER_MEASURE + step != absolute:
        raise ValueError(f"{stream} Iteration 002 coordinate invariant failed")
    return {"measure": measure, "step": step, "midi": midi, "absoluteGridStep": absolute}


def event_for_recovery(absolute: int, midi: int, stream: str, rule: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "measure": absolute // STEPS_PER_MEASURE + 1,
        "step": absolute % STEPS_PER_MEASURE,
        "midi": int(midi),
        "absoluteGridStep": int(absolute),
        "v167RecoverySweepEvidence": {
            "stream": stream,
            "rule": copy.deepcopy(rule),
            "evidence": copy.deepcopy(evidence),
            "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
            "referenceReadByGenerator": False,
            "scorerReadByGenerator": False,
        },
    }


def score_minimal_payload(base: dict[str, Any], guitar: list[dict[str, Any]], bass: list[dict[str, Any]], variant: dict[str, Any]) -> dict[str, Any]:
    safety = base.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise ValueError("Iteration 002 safety boundary invalid")
    return {
        "schema": "dadrock.tabs.v167.recovery-sweep-score-candidate.v1",
        "version": "V167",
        "status": "PREDECLARED_RECOVERY_SWEEP_VARIANT_FROZEN_BEFORE_SCORING",
        "song": copy.deepcopy(base.get("song")),
        "safety": {**copy.deepcopy(safety), "referenceRead": False, "humanCorrection": False},
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "v167RecoverySweep": variant,
    }


def guitar_configs() -> Iterable[dict[str, Any]]:
    yield {"id": "g-baseline", "stream": "combinedGuitar", "baseline": True}
    for rank in GUITAR_RANK_THRESHOLDS:
        for onset in GUITAR_ONSET_THRESHOLDS:
            for max_adds in GUITAR_MAX_ADDS_PER_SITE:
                for inactive_only in GUITAR_INACTIVE_ONLY:
                    yield {
                        "id": f"g-r{int(rank*1000):03d}-o{int(onset*100):02d}-n{max_adds}-i{int(inactive_only)}",
                        "stream": "combinedGuitar",
                        "baseline": False,
                        "templateRankMin": rank,
                        "onsetSupportMin": onset,
                        "activitySupportMin": GUITAR_ACTIVITY_MIN,
                        "fundamentalPresentRequired": True,
                        "basicPitchInactiveOnly": inactive_only,
                        "maxAddsPerSite": max_adds,
                        "existingEventsPreferred": True,
                        "stepMidiDedupe": True,
                        "polyphonyCap": GUITAR_CAP,
                    }


def bass_configs() -> Iterable[dict[str, Any]]:
    yield {"id": "b-baseline", "stream": "bass", "baseline": True}
    for rank in BASS_RANK_THRESHOLDS:
        for onset in BASS_ONSET_THRESHOLDS:
            for activity in BASS_ACTIVITY_THRESHOLDS:
                for scope in BASS_SCOPES:
                    yield {
                        "id": f"b-r{int(rank*1000):03d}-o{int(onset*100):02d}-a{int(activity*100):02d}-{scope}",
                        "stream": "bass",
                        "baseline": False,
                        "templateRankMin": rank,
                        "onsetSupportMin": onset,
                        "activitySupportMin": activity,
                        "fundamentalPresentRequired": True,
                        "scope": scope,
                        "lowRegisterMaxMidi": BASS_LOW_REGISTER_MAX_MIDI,
                        "existingEventsPreferred": True,
                        "stepCap": BASS_CAP,
                    }


def build_guitar(base_guitar: list[dict[str, Any]], rows: list[dict[str, Any]], config: dict[str, Any], lattice: list[float]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = copy.deepcopy(base_guitar)
    if config.get("baseline"):
        return out, {"added": 0, "eligible": 0, "sitesWithAdds": 0}
    occupied = {(int(n["absoluteGridStep"]), int(n["midi"])) for n in out}
    per_step = defaultdict(int)
    for note in out:
        per_step[int(note["absoluteGridStep"])] += 1
    by_site: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_site[int(row["siteFrame"])].append(row)
    eligible = 0
    added = 0
    sites_with_adds = 0
    for site in sorted(by_site):
        candidates = []
        for row in by_site[site]:
            if config["fundamentalPresentRequired"] and not bool(row.get("fundamentalPresent", False)):
                continue
            if float(row.get("templateRank", 0.0)) < float(config["templateRankMin"]):
                continue
            if float(row.get("onsetSupport", 0.0)) < float(config["onsetSupportMin"]):
                continue
            if float(row.get("activitySupport", 0.0)) < float(config["activitySupportMin"]):
                continue
            if config["basicPitchInactiveOnly"] and bool(row.get("basicPitchActiveAtSite", False)):
                continue
            absolute = corrected_step(float(row["siteSeconds"]), lattice)
            if absolute is None:
                continue
            midi = int(row["midi"])
            if (absolute, midi) in occupied or per_step[absolute] >= GUITAR_CAP:
                continue
            eligible += 1
            candidates.append((row, absolute))
        candidates.sort(key=lambda item: (
            -float(item[0].get("templateRank", 0.0)),
            -float(item[0].get("templateScore", 0.0)),
            -float(item[0].get("onsetSupport", 0.0)),
            -float(item[0].get("activitySupport", 0.0)),
            int(item[0]["midi"]),
        ))
        site_added = 0
        for row, absolute in candidates:
            midi = int(row["midi"])
            if (absolute, midi) in occupied or per_step[absolute] >= GUITAR_CAP:
                continue
            evidence = {
                "siteFrame": int(row["siteFrame"]),
                "siteSeconds": float(row["siteSeconds"]),
                "templateRank": float(row["templateRank"]),
                "templateScore": float(row["templateScore"]),
                "fundamentalPresent": bool(row["fundamentalPresent"]),
                "onsetSupport": float(row["onsetSupport"]),
                "activitySupport": float(row["activitySupport"]),
                "basicPitchActiveAtSite": bool(row["basicPitchActiveAtSite"]),
            }
            out.append(event_for_recovery(absolute, midi, "combinedGuitar", config, evidence))
            occupied.add((absolute, midi))
            per_step[absolute] += 1
            added += 1
            site_added += 1
            if site_added >= int(config["maxAddsPerSite"]):
                break
        if site_added:
            sites_with_adds += 1
    out.sort(key=lambda n: (int(n["absoluteGridStep"]), int(n["midi"])))
    if max(per_step.values(), default=0) > GUITAR_CAP:
        raise AssertionError("Guitar recovery variant exceeded cap")
    return out, {"added": added, "eligible": eligible, "sitesWithAdds": sites_with_adds}


def bass_scope_ok(row: dict[str, Any], scope: str) -> bool:
    low = int(row["midi"]) <= BASS_LOW_REGISTER_MAX_MIDI
    no_state = not bool(row.get("hadNearbyStableState", False))
    if scope == "all":
        return True
    if scope == "no_stable_state":
        return no_state
    if scope == "low_register":
        return low
    if scope == "low_register_no_stable_state":
        return low and no_state
    raise ValueError(f"unknown Bass scope: {scope}")


def build_bass(base_bass: list[dict[str, Any]], rows: list[dict[str, Any]], config: dict[str, Any], lattice: list[float]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = copy.deepcopy(base_bass)
    if config.get("baseline"):
        return out, {"added": 0, "eligible": 0, "sitesWithAdds": 0}
    occupied_steps = {int(n["absoluteGridStep"]) for n in out}
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
            if not bass_scope_ok(row, str(config["scope"])):
                continue
            if float(row.get("templateRank", 0.0)) < float(config["templateRankMin"]):
                continue
            if float(row.get("onsetSupport", 0.0)) < float(config["onsetSupportMin"]):
                continue
            if float(row.get("activitySupport", 0.0)) < float(config["activitySupportMin"]):
                continue
            absolute = corrected_step(float(row["seconds"]), lattice)
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
            out.append(event_for_recovery(absolute, midi, "bass", config, evidence))
            occupied_steps.add(absolute)
            added += 1
            sites_with_adds += 1
            break
    out.sort(key=lambda n: (int(n["absoluteGridStep"]), int(n["midi"])))
    if len({int(n["absoluteGridStep"]) for n in out}) != len(out):
        raise AssertionError("Bass recovery variant violated monophonic cap")
    return out, {"added": added, "eligible": eligible, "sitesWithAdds": sites_with_adds}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()
    if args.output_dir.exists() or args.manifest.exists():
        raise RuntimeError("recovery sweep generation outputs must not pre-exist")
    if sha256_file(args.pool) != EXPECTED_POOL_BLOB_SHA256:
        raise RuntimeError("frozen V167 evidence-pool SHA256 mismatch")

    base = json.loads(args.base.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))
    if base.get("version") != "V167" or int((base.get("calibration") or {}).get("iteration", -1)) != 2:
        raise RuntimeError("recovery sweep base must be frozen V167 Iteration 002")
    if not bool((pool.get("reproduction") or {}).get("exactFrozenV166MusicalStreams", False)):
        raise RuntimeError("evidence pool lacks exact V166 reproduction proof")
    policy = pool.get("policy") or {}
    for key in ("referenceRead", "scorerRead", "thresholdTuningPerformed", "candidateGenerationBehaviorModified"):
        if policy.get(key) is not False:
            raise RuntimeError(f"evidence-pool policy boundary invalid: {key}")

    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds") or []]
    if len(lattice) < 5 or any(b <= a for a, b in zip(lattice, lattice[1:])):
        raise RuntimeError("invalid frozen subdivision lattice")
    streams = base.get("streams") or {}
    if len(streams.get("combinedGuitar") or []) != EXPECTED_BASE_COUNTS["combinedGuitar"] or len(streams.get("bass") or []) != EXPECTED_BASE_COUNTS["bass"]:
        raise RuntimeError("Iteration 002 base stream counts drift")
    base_guitar = [compact_base_note(dict(n), "combinedGuitar") for n in streams["combinedGuitar"]]
    base_bass = [compact_base_note(dict(n), "bass") for n in streams["bass"]]
    upstream = pool.get("upstreamPitchPools") or {}
    guitar_rows = list((upstream.get("guitarStandaloneHarmonic") or {}).get("candidates") or [])
    bass_rows = list((upstream.get("bassPreAdmission") or {}).get("candidates") or [])
    if len(guitar_rows) != 13328 or len(bass_rows) != 36520:
        raise RuntimeError("frozen upstream candidate counts drift")

    manifest: dict[str, Any] = {
        "schema": "dadrock.tabs.v167.predeclared-upstream-recovery-variant-manifest.v1",
        "version": "V167",
        "status": "FROZEN_BEFORE_REFERENCE_SCORING",
        "inputs": {
            "baseSha256": sha256_file(args.base),
            "poolSha256": sha256_file(args.pool),
            "timebaseSha256": sha256_file(args.timebase),
            "baseCounts": EXPECTED_BASE_COUNTS,
            "poolCounts": {"guitar": len(guitar_rows), "bass": len(bass_rows)},
        },
        "policy": {
            "referenceRead": False,
            "scorerRead": False,
            "allVariantRulesPredeclaredBeforeScoring": True,
            "individualEventSelectionByReference": False,
            "existingIteration002EventsPreferred": True,
            "globalPhaseCorrectionGridSteps": GLOBAL_PHASE_CORRECTION,
            "newRecoveryTimingRule": "nearest-frozen-v166-subdivision-then-frozen-minus-12-global-phase",
            "iteration002ExistingEventTimingPreserved": True,
        },
        "variants": [],
    }

    for config in guitar_configs():
        guitar, summary = build_guitar(base_guitar, guitar_rows, config, lattice)
        variant = {**copy.deepcopy(config), "summary": summary}
        payload = score_minimal_payload(base, guitar, base_bass, variant)
        path = args.output_dir / "guitar" / f"{config['id']}.json"
        write_json(path, payload)
        manifest["variants"].append({"id": config["id"], "stream": "combinedGuitar", "config": config, "summary": summary, "relativePath": str(path.relative_to(args.output_dir)), "sha256": sha256_file(path), "counts": {"combinedGuitar": len(guitar), "bass": len(base_bass)}})

    for config in bass_configs():
        bass, summary = build_bass(base_bass, bass_rows, config, lattice)
        variant = {**copy.deepcopy(config), "summary": summary}
        payload = score_minimal_payload(base, base_guitar, bass, variant)
        path = args.output_dir / "bass" / f"{config['id']}.json"
        write_json(path, payload)
        manifest["variants"].append({"id": config["id"], "stream": "bass", "config": config, "summary": summary, "relativePath": str(path.relative_to(args.output_dir)), "sha256": sha256_file(path), "counts": {"combinedGuitar": len(base_guitar), "bass": len(bass)}})

    write_json(args.manifest, manifest)
    print(json.dumps({
        "guitarVariants": sum(v["stream"] == "combinedGuitar" for v in manifest["variants"]),
        "bassVariants": sum(v["stream"] == "bass" for v in manifest["variants"]),
        "totalVariants": len(manifest["variants"]),
        "manifestSha256": sha256_file(args.manifest),
        "referenceRead": False,
        "scorerRead": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
