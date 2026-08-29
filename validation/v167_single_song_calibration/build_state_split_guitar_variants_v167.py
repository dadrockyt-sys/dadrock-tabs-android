#!/usr/bin/env python3
"""Build the preregistered V167 state-split Guitar family before scoring.

The active branch is fixed from the frozen post-I004 diagnosis: Basic-Pitch-active,
max-active-tied candidates (ratio >= 1.00) with harmonic/octave suppression. The
inactive branch is the only experimental dimension. Generation is reference-blind,
and a q1.00/noharm reproduction control must normalize exactly to frozen I004 before
any scorer/reference-facing work is allowed.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import build_upstream_recovery_variants_v167 as base_builder

EXPECTED_I003_SHA256 = "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115"
EXPECTED_I004_SHA256 = "728785c631750cbfcad48cc3243c238d6e7de6f337cce87e125a651ca2793acc"
EXPECTED_POOL_SHA256 = "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673"
EXPECTED_I003_COUNTS = {"combinedGuitar": 1050, "bass": 512}
EXPECTED_I004_COUNTS = {"combinedGuitar": 1113, "bass": 512}
EXPECTED_GUITAR_POOL_ROWS = 13328
EXPECTED_GUITAR_POOL_SITES = 272

TEMPLATE_RANK_MIN = 0.975
ACTIVITY_SUPPORT_MIN = 0.05
ONSET_SUPPORT_MIN = 0.50
ACTIVE_RATIO_MIN = 1.00
ACTIVE_INTERVAL_POLICY = "exclude_harmonic_octave"
HARMONIC_OCTAVE_INTERVALS = frozenset({12, 19, 24})
CHORD_INTERVALS = frozenset({3, 4, 5, 7, 8, 9, 10})
MAX_ADDS_PER_SITE = 1
GUITAR_CAP = 6
EPS = 1e-12

REPRODUCTION_CONTROL_ID = "gss-repro-q100-noharm"
NEW_VARIANT_IDS = (
    "gss-active-only",
    "gss-inactive-q125-noharm",
    "gss-inactive-q100-chord",
    "gss-inactive-q125-chord",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def normalized_scoring_coordinates(events: list[dict[str, Any]]) -> list[tuple[int, float, int]]:
    return sorted(
        (
            int(event["measure"]),
            float(event["step"]),
            int(event["midi"]),
        )
        for event in events
        if not bool(event.get("excludeFromScoring", False))
    )


def normalized_absolute_coordinates(events: list[dict[str, Any]]) -> list[tuple[int, int]]:
    return sorted(
        (int(event["absoluteGridStep"]), int(event["midi"]))
        for event in events
    )


def full_config(
    variant_id: str,
    *,
    inactive_enabled: bool,
    inactive_ratio_min: float | None,
    inactive_interval_policy: str | None,
    reproduction_control: bool = False,
) -> dict[str, Any]:
    return {
        "id": variant_id,
        "stream": "combinedGuitar",
        "baseline": False,
        "reproductionControl": bool(reproduction_control),
        "templateRankMin": TEMPLATE_RANK_MIN,
        "activitySupportMin": ACTIVITY_SUPPORT_MIN,
        "onsetSupportMin": ONSET_SUPPORT_MIN,
        "requireBasicPitchActiveContext": True,
        "fundamentalPresentRequired": True,
        "maxAddsPerSite": MAX_ADDS_PER_SITE,
        "existingIteration003EventsPreferred": True,
        "stepMidiDedupe": True,
        "polyphonyCap": GUITAR_CAP,
        "activeBranch": {
            "candidateState": "basic_pitch_active",
            "candidateToMaxActiveTemplateScoreMin": ACTIVE_RATIO_MIN,
            "intervalContextPolicy": ACTIVE_INTERVAL_POLICY,
            "harmonicOctaveIntervalsRejected": sorted(HARMONIC_OCTAVE_INTERVALS),
        },
        "inactiveBranch": {
            "enabled": bool(inactive_enabled),
            "candidateState": "basic_pitch_inactive",
            "candidateToMaxActiveTemplateScoreMin": inactive_ratio_min,
            "intervalContextPolicy": inactive_interval_policy,
            "harmonicOctaveIntervalsRejected": sorted(HARMONIC_OCTAVE_INTERVALS),
            "chordIntervalsAllowed": sorted(CHORD_INTERVALS),
        },
    }


def preregistered_configs() -> Iterable[dict[str, Any]]:
    # No-score reproduction control: exactly the already-scored I004 whole rule,
    # expressed through the state-split implementation.
    yield full_config(
        REPRODUCTION_CONTROL_ID,
        inactive_enabled=True,
        inactive_ratio_min=1.00,
        inactive_interval_policy="exclude_harmonic_octave",
        reproduction_control=True,
    )
    yield full_config(
        "gss-active-only",
        inactive_enabled=False,
        inactive_ratio_min=None,
        inactive_interval_policy=None,
    )
    yield full_config(
        "gss-inactive-q125-noharm",
        inactive_enabled=True,
        inactive_ratio_min=1.25,
        inactive_interval_policy="exclude_harmonic_octave",
    )
    yield full_config(
        "gss-inactive-q100-chord",
        inactive_enabled=True,
        inactive_ratio_min=1.00,
        inactive_interval_policy="chord_interval",
    )
    yield full_config(
        "gss-inactive-q125-chord",
        inactive_enabled=True,
        inactive_ratio_min=1.25,
        inactive_interval_policy="chord_interval",
    )


def active_context(site_rows: list[dict[str, Any]]) -> tuple[list[int], float | None]:
    active_rows = [
        row for row in site_rows
        if bool(row.get("basicPitchActiveAtSite", False))
    ]
    active_midis = sorted({int(row["midi"]) for row in active_rows})
    if not active_rows:
        return active_midis, None
    max_score = max(float(row.get("templateScore", 0.0)) for row in active_rows)
    return active_midis, max_score if max_score > EPS else None


def nearest_different_active_interval(candidate_midi: int, active_midis: list[int]) -> int | None:
    intervals = [
        abs(int(candidate_midi) - int(active))
        for active in active_midis
        if int(active) != int(candidate_midi)
    ]
    return min(intervals) if intervals else None


def interval_policy_ok(nearest_interval: int | None, policy: str | None) -> bool:
    if policy is None:
        return False
    if policy == "exclude_harmonic_octave":
        return nearest_interval not in HARMONIC_OCTAVE_INTERVALS
    if policy == "chord_interval":
        return (
            nearest_interval in CHORD_INTERVALS
            if nearest_interval is not None
            else False
        )
    raise ValueError(f"unknown interval policy: {policy}")


def branch_eligible(
    row: dict[str, Any],
    ratio: float,
    nearest_interval: int | None,
    config: dict[str, Any],
) -> tuple[bool, str | None]:
    if bool(row.get("basicPitchActiveAtSite", False)):
        active = config["activeBranch"]
        if ratio + EPS < float(active["candidateToMaxActiveTemplateScoreMin"]):
            return False, None
        if not interval_policy_ok(nearest_interval, str(active["intervalContextPolicy"])):
            return False, None
        return True, "active_max"

    inactive = config["inactiveBranch"]
    if not bool(inactive["enabled"]):
        return False, None
    inactive_ratio = inactive.get("candidateToMaxActiveTemplateScoreMin")
    if inactive_ratio is None or ratio + EPS < float(inactive_ratio):
        return False, None
    if not interval_policy_ok(nearest_interval, inactive.get("intervalContextPolicy")):
        return False, None
    return True, "inactive"


def build_guitar(
    base_guitar: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    lattice: list[float],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = copy.deepcopy(base_guitar)
    occupied = {
        (int(note["absoluteGridStep"]), int(note["midi"]))
        for note in out
    }
    new_pairs: set[tuple[int, int]] = set()
    per_step: dict[int, int] = defaultdict(int)
    for note in out:
        per_step[int(note["absoluteGridStep"])] += 1

    by_site: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_site[int(row["siteFrame"])].append(row)

    eligible = 0
    active_eligible = 0
    inactive_eligible = 0
    added = 0
    active_added = 0
    inactive_added = 0
    sites_with_active_context = 0
    sites_with_eligible = 0
    sites_with_adds = 0

    for site in sorted(by_site):
        site_rows = by_site[site]
        active_midis, max_active_score = active_context(site_rows)
        if not active_midis or max_active_score is None:
            continue
        sites_with_active_context += 1

        candidates: list[tuple[dict[str, Any], int, float, int | None, str]] = []
        for row in site_rows:
            if config["fundamentalPresentRequired"] and not bool(row.get("fundamentalPresent", False)):
                continue
            if float(row.get("templateRank", 0.0)) < float(config["templateRankMin"]):
                continue
            if float(row.get("onsetSupport", 0.0)) < float(config["onsetSupportMin"]):
                continue
            if float(row.get("activitySupport", 0.0)) < float(config["activitySupportMin"]):
                continue

            candidate_score = float(row.get("templateScore", 0.0))
            ratio = candidate_score / max_active_score
            midi = int(row["midi"])
            nearest_interval = nearest_different_active_interval(midi, active_midis)
            ok, branch = branch_eligible(row, ratio, nearest_interval, config)
            if not ok or branch is None:
                continue

            absolute = base_builder.corrected_step(float(row["siteSeconds"]), lattice)
            if absolute is None:
                continue
            if (absolute, midi) in occupied or per_step[absolute] >= GUITAR_CAP:
                continue

            eligible += 1
            if branch == "active_max":
                active_eligible += 1
            else:
                inactive_eligible += 1
            candidates.append((row, absolute, ratio, nearest_interval, branch))

        if not candidates:
            continue
        sites_with_eligible += 1

        # Exactly the frozen contextual top-1/site ordering. Reproduction control
        # therefore has a deterministic path to I004 equality.
        candidates.sort(key=lambda item: (
            -float(item[2]),
            -float(item[0].get("templateRank", 0.0)),
            -float(item[0].get("templateScore", 0.0)),
            -float(item[0].get("onsetSupport", 0.0)),
            -float(item[0].get("activitySupport", 0.0)),
            int(item[0]["midi"]),
        ))

        row, absolute, ratio, nearest_interval, branch = candidates[0]
        midi = int(row["midi"])
        pair = (absolute, midi)
        if pair in occupied or per_step[absolute] >= GUITAR_CAP:
            continue

        evidence = {
            "siteFrame": int(row["siteFrame"]),
            "siteSeconds": float(row["siteSeconds"]),
            "candidateMidi": midi,
            "templateRank": float(row["templateRank"]),
            "templateScore": float(row["templateScore"]),
            "fundamentalPresent": bool(row.get("fundamentalPresent", False)),
            "onsetSupport": float(row["onsetSupport"]),
            "activitySupport": float(row["activitySupport"]),
            "basicPitchActiveAtSite": bool(row.get("basicPitchActiveAtSite", False)),
            "activeMidisAtSite": active_midis,
            "maxActiveTemplateScore": float(max_active_score),
            "candidateToMaxActiveTemplateScoreRatio": float(ratio),
            "nearestDifferentActiveSemitoneDistance": nearest_interval,
            "stateSplitBranch": branch,
        }
        out.append(
            base_builder.event_for_recovery(
                absolute,
                midi,
                "combinedGuitar",
                config,
                evidence,
            )
        )
        occupied.add(pair)
        new_pairs.add(pair)
        per_step[absolute] += 1
        added += 1
        if branch == "active_max":
            active_added += 1
        else:
            inactive_added += 1
        sites_with_adds += 1

    out.sort(key=lambda note: (int(note["absoluteGridStep"]), int(note["midi"])))
    if max(per_step.values(), default=0) > GUITAR_CAP:
        raise AssertionError("state-split Guitar variant exceeded polyphony cap")
    if len(new_pairs) != added:
        raise AssertionError("state-split Guitar variant added duplicate coordinates")
    return out, {
        "added": added,
        "activeAdded": active_added,
        "inactiveAdded": inactive_added,
        "eligible": eligible,
        "activeEligible": active_eligible,
        "inactiveEligible": inactive_eligible,
        "sitesWithActiveContext": sites_with_active_context,
        "sitesWithEligible": sites_with_eligible,
        "sitesWithAdds": sites_with_adds,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-i003", type=Path, required=True)
    ap.add_argument("--baseline-i004", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    if args.output_dir.exists() or args.manifest.exists():
        raise RuntimeError("state-split generation outputs must not pre-exist")
    if sha256_file(args.base_i003) != EXPECTED_I003_SHA256:
        raise RuntimeError("frozen I003 SHA256 mismatch")
    if sha256_file(args.baseline_i004) != EXPECTED_I004_SHA256:
        raise RuntimeError("frozen I004 SHA256 mismatch")
    if sha256_file(args.pool) != EXPECTED_POOL_SHA256:
        raise RuntimeError("frozen evidence-pool SHA256 mismatch")

    i003 = json.loads(args.base_i003.read_text(encoding="utf-8"))
    i004 = json.loads(args.baseline_i004.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))

    if i003.get("version") != "V167" or int((i003.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("state-split generator requires frozen V167 I003")
    if i004.get("version") != "V167" or int((i004.get("calibration") or {}).get("iteration", -1)) != 4:
        raise RuntimeError("state-split baseline must be frozen V167 I004")
    for payload, name in ((i003, "I003"), (i004, "I004")):
        safety = payload.get("safety") or {}
        if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
            raise RuntimeError(f"{name} safety boundary invalid")

    policy = pool.get("policy") or {}
    for key in ("referenceRead", "scorerRead", "thresholdTuningPerformed", "candidateGenerationBehaviorModified"):
        if policy.get(key) is not False:
            raise RuntimeError(f"evidence-pool policy boundary invalid: {key}")

    i003_streams = i003.get("streams") or {}
    i004_streams = i004.get("streams") or {}
    for stream, expected in EXPECTED_I003_COUNTS.items():
        if len(i003_streams.get(stream) or []) != expected:
            raise RuntimeError(f"I003 {stream} count drift")
    for stream, expected in EXPECTED_I004_COUNTS.items():
        if len(i004_streams.get(stream) or []) != expected:
            raise RuntimeError(f"I004 {stream} count drift")

    base_guitar = [
        base_builder.compact_base_note(dict(note), "combinedGuitar")
        for note in i003_streams["combinedGuitar"]
    ]
    base_bass = [
        base_builder.compact_base_note(dict(note), "bass")
        for note in i003_streams["bass"]
    ]
    if normalized_scoring_coordinates(base_bass) != normalized_scoring_coordinates(list(i004_streams["bass"])):
        raise RuntimeError("I004 Bass is not exactly the frozen I003 scoring stream")

    i004_guitar_coordinates = normalized_scoring_coordinates(list(i004_streams["combinedGuitar"]))
    i004_bass_coordinates = normalized_scoring_coordinates(list(i004_streams["bass"]))

    lattice = [float(x) for x in timebase.get("subdivisionTimesSeconds") or []]
    if len(lattice) < 5 or any(b <= a for a, b in zip(lattice, lattice[1:])):
        raise RuntimeError("invalid frozen subdivision lattice")

    guitar_pool = (pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}
    guitar_rows = list(guitar_pool.get("candidates") or [])
    if len(guitar_rows) != EXPECTED_GUITAR_POOL_ROWS:
        raise RuntimeError("frozen Guitar evidence-pool row count drift")
    if len({int(row["siteFrame"]) for row in guitar_rows}) != EXPECTED_GUITAR_POOL_SITES:
        raise RuntimeError("frozen Guitar evidence-pool site count drift")

    configs = list(preregistered_configs())
    if len(configs) != 5:
        raise RuntimeError("state-split preregistration must contain one reproduction control + four new rules")
    if [config["id"] for config in configs[1:]] != list(NEW_VARIANT_IDS):
        raise RuntimeError("state-split new-rule identity drift")

    manifest: dict[str, Any] = {
        "schema": "dadrock.tabs.v167.predeclared-state-split-guitar-manifest.v1",
        "version": "V167",
        "status": "FROZEN_BEFORE_REFERENCE_SCORING",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.base_i003),
            "iteration004Sha256": sha256_file(args.baseline_i004),
            "poolSha256": sha256_file(args.pool),
            "timebaseSha256": sha256_file(args.timebase),
            "i003Counts": EXPECTED_I003_COUNTS,
            "i004Counts": EXPECTED_I004_COUNTS,
            "guitarPoolRows": len(guitar_rows),
            "guitarPoolSites": EXPECTED_GUITAR_POOL_SITES,
        },
        "baseline": {
            "id": "i004-baseline",
            "candidatePath": str(args.baseline_i004),
            "candidateSha256": sha256_file(args.baseline_i004),
            "totalAdditionsVsI003": 63,
            "scored": True,
        },
        "policy": {
            "professionalReferenceReadByGenerator": False,
            "scorerReadByGenerator": False,
            "allNewRulesPredeclaredBeforeScoring": True,
            "individualEventSelectionByReference": False,
            "iteration003Immutable": True,
            "iteration004Immutable": True,
            "baselineIsFrozenIteration004": True,
            "bassStreamFixedExactlyToIteration004": True,
            "reproductionControlScored": False,
            "reproductionMustEqualIteration004BeforeScoring": True,
            "newRuleCount": 4,
            "activeBranchFixed": {
                "candidateState": "basic_pitch_active",
                "candidateToMaxActiveTemplateScoreMin": ACTIVE_RATIO_MIN,
                "intervalContextPolicy": ACTIVE_INTERVAL_POLICY,
            },
            "inactiveBranchFamily": [
                "off",
                "ratio_1.25_exclude_harmonic_octave",
                "ratio_1.00_chord_interval",
                "ratio_1.25_chord_interval",
            ],
            "templateRankMin": TEMPLATE_RANK_MIN,
            "activitySupportMin": ACTIVITY_SUPPORT_MIN,
            "onsetSupportMin": ONSET_SUPPORT_MIN,
            "requireBasicPitchActiveContext": True,
            "fundamentalPresentRequired": True,
            "maxAddsPerSite": MAX_ADDS_PER_SITE,
            "existingIteration003EventsPreferred": True,
            "newStepMidiDedupeAgainstImmutableParent": True,
            "polyphonyCap": GUITAR_CAP,
            "globalPhaseCorrectionGridSteps": base_builder.GLOBAL_PHASE_CORRECTION,
            "newRecoveryTimingRule": "nearest-frozen-v166-subdivision-then-frozen-minus-12-global-phase",
            "topOneOrdering": [
                "candidate_to_max_active_template_ratio_desc",
                "template_rank_desc",
                "template_score_desc",
                "onset_support_desc",
                "activity_support_desc",
                "midi_asc",
            ],
            "postScoreRetuning": False,
            "automaticIteration005Promotion": False,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        },
        "reproductionControl": None,
        "newVariants": [],
    }

    for config in configs:
        guitar, summary = build_guitar(base_guitar, guitar_rows, config, lattice)
        variant = {**copy.deepcopy(config), "summary": copy.deepcopy(summary)}
        payload = base_builder.score_minimal_payload(i003, guitar, base_bass, variant)
        path = args.output_dir / "guitar" / f"{config['id']}.json"
        write_json(path, payload)
        if normalized_scoring_coordinates(payload["streams"]["bass"]) != i004_bass_coordinates:
            raise AssertionError(f"Bass drift in state-split candidate {config['id']}")
        row = {
            "id": config["id"],
            "config": copy.deepcopy(config),
            "summary": copy.deepcopy(summary),
            "relativePath": str(path.relative_to(args.output_dir)),
            "sha256": sha256_file(path),
            "counts": {
                "combinedGuitar": len(guitar),
                "bass": len(base_bass),
            },
            "totalAdditionsVsI003": int(summary["added"]),
            "scored": not bool(config.get("reproductionControl", False)),
        }
        if bool(config.get("reproductionControl", False)):
            reproduced = normalized_scoring_coordinates(payload["streams"]["combinedGuitar"])
            if reproduced != i004_guitar_coordinates:
                raise RuntimeError("state-split reproduction control does not normalize exactly to frozen I004")
            row["scored"] = False
            row["normalizedGuitarExactlyIteration004"] = True
            row["normalizedBassExactlyIteration004"] = True
            row["iteration004NormalizedGuitarCoordinateCount"] = len(i004_guitar_coordinates)
            manifest["reproductionControl"] = row
        else:
            manifest["newVariants"].append(row)

    if manifest["reproductionControl"] is None:
        raise RuntimeError("missing state-split reproduction control")
    if len(manifest["newVariants"]) != 4:
        raise RuntimeError("state-split new variant count drift")
    if [row["id"] for row in manifest["newVariants"]] != list(NEW_VARIANT_IDS):
        raise RuntimeError("state-split new variant ordering drift")

    write_json(args.manifest, manifest)
    print(json.dumps({
        "reproductionControl": {
            "id": manifest["reproductionControl"]["id"],
            "sha256": manifest["reproductionControl"]["sha256"],
            "added": manifest["reproductionControl"]["summary"]["added"],
            "normalizedGuitarExactlyIteration004": True,
            "scored": False,
        },
        "newVariantCount": len(manifest["newVariants"]),
        "newVariantSummaries": [
            {
                "id": row["id"],
                "added": row["summary"]["added"],
                "activeAdded": row["summary"]["activeAdded"],
                "inactiveAdded": row["summary"]["inactiveAdded"],
            }
            for row in manifest["newVariants"]
        ],
        "manifestSha256": sha256_file(args.manifest),
        "professionalReferenceReadByGenerator": False,
        "scorerReadByGenerator": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
