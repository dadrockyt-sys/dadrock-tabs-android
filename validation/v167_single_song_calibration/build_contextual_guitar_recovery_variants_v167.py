#!/usr/bin/env python3
"""Build the preregistered sparse contextual Guitar recovery family for V167.

Reference-blind generator. It reads only frozen Iteration 003, the frozen V167
upstream evidence pool, and the frozen V166 subdivision timebase. The 36
nonbaseline rules use relative template evidence versus Basic Pitch-active pitches
at the same site plus a preregistered interval-context policy. All complete
candidates are written and hashed before any scorer/reference-facing step.
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

EXPECTED_BASE_SHA256 = "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115"
EXPECTED_POOL_SHA256 = "1c983784c2d12a22437a80387525789bcf55a2f4e4a5c7a96608c575bf709673"
EXPECTED_BASE_COUNTS = {"combinedGuitar": 1050, "bass": 512}
EXPECTED_GUITAR_POOL_ROWS = 13328
EXPECTED_GUITAR_POOL_SITES = 272

TEMPLATE_RANK_MIN = 0.975
ACTIVITY_SUPPORT_MIN = 0.05
ONSET_SUPPORT_MINS = (0.50, 0.65)
CANDIDATE_TO_MAX_ACTIVE_RATIOS = (0.75, 1.00, 1.25)
ACTIVE_STATE_MODES = ("allow_active", "inactive_only")
INTERVAL_POLICIES = ("none", "exclude_harmonic_octave", "chord_interval")
HARMONIC_OCTAVE_INTERVALS = frozenset({12, 19, 24})
CHORD_INTERVALS = frozenset({3, 4, 5, 7, 8, 9, 10})
MAX_ADDS_PER_SITE = 1
GUITAR_CAP = 6
EPS = 1e-12


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def contextual_configs() -> Iterable[dict[str, Any]]:
    yield {"id": "gctx-baseline", "stream": "combinedGuitar", "baseline": True}
    for onset in ONSET_SUPPORT_MINS:
        for ratio in CANDIDATE_TO_MAX_ACTIVE_RATIOS:
            for active_mode in ACTIVE_STATE_MODES:
                for interval_policy in INTERVAL_POLICIES:
                    yield {
                        "id": (
                            f"gctx-o{int(round(onset * 100)):02d}"
                            f"-q{int(round(ratio * 100)):03d}"
                            f"-{'allow' if active_mode == 'allow_active' else 'inactive'}"
                            f"-{'none' if interval_policy == 'none' else ('noharm' if interval_policy == 'exclude_harmonic_octave' else 'chord')}"
                        ),
                        "stream": "combinedGuitar",
                        "baseline": False,
                        "templateRankMin": TEMPLATE_RANK_MIN,
                        "activitySupportMin": ACTIVITY_SUPPORT_MIN,
                        "onsetSupportMin": onset,
                        "candidateToMaxActiveTemplateScoreMin": ratio,
                        "activeStateMode": active_mode,
                        "intervalContextPolicy": interval_policy,
                        "requireBasicPitchActiveContext": True,
                        "fundamentalPresentRequired": True,
                        "maxAddsPerSite": MAX_ADDS_PER_SITE,
                        "existingIteration003EventsPreferred": True,
                        "stepMidiDedupe": True,
                        "polyphonyCap": GUITAR_CAP,
                        "harmonicOctaveIntervalsRejected": sorted(HARMONIC_OCTAVE_INTERVALS),
                        "chordIntervalsAllowed": sorted(CHORD_INTERVALS),
                    }


def active_context(site_rows: list[dict[str, Any]]) -> tuple[list[int], float | None]:
    active_rows = [row for row in site_rows if bool(row.get("basicPitchActiveAtSite", False))]
    active_midis = sorted({int(row["midi"]) for row in active_rows})
    if not active_rows:
        return active_midis, None
    max_score = max(float(row.get("templateScore", 0.0)) for row in active_rows)
    return active_midis, max_score if max_score > EPS else None


def nearest_different_active_interval(candidate_midi: int, active_midis: list[int]) -> int | None:
    intervals = [abs(int(candidate_midi) - int(active)) for active in active_midis if int(active) != int(candidate_midi)]
    return min(intervals) if intervals else None


def interval_policy_ok(nearest_interval: int | None, policy: str) -> bool:
    if policy == "none":
        return True
    if policy == "exclude_harmonic_octave":
        return nearest_interval not in HARMONIC_OCTAVE_INTERVALS
    if policy == "chord_interval":
        return nearest_interval in CHORD_INTERVALS if nearest_interval is not None else False
    raise ValueError(f"unknown interval policy: {policy}")


def build_guitar(
    base_guitar: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    lattice: list[float],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    out = copy.deepcopy(base_guitar)
    if bool(config.get("baseline", False)):
        return out, {
            "added": 0,
            "eligible": 0,
            "sitesWithActiveContext": 0,
            "sitesWithEligible": 0,
            "sitesWithAdds": 0,
        }

    occupied = {(int(note["absoluteGridStep"]), int(note["midi"])) for note in out}
    per_step: dict[int, int] = defaultdict(int)
    for note in out:
        per_step[int(note["absoluteGridStep"])] += 1

    by_site: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_site[int(row["siteFrame"])].append(row)

    eligible = 0
    added = 0
    sites_with_active_context = 0
    sites_with_eligible = 0
    sites_with_adds = 0

    for site in sorted(by_site):
        site_rows = by_site[site]
        active_midis, max_active_score = active_context(site_rows)
        if not active_midis or max_active_score is None:
            continue
        sites_with_active_context += 1

        candidates: list[tuple[dict[str, Any], int, float, int | None]] = []
        for row in site_rows:
            if config["fundamentalPresentRequired"] and not bool(row.get("fundamentalPresent", False)):
                continue
            if float(row.get("templateRank", 0.0)) < float(config["templateRankMin"]):
                continue
            if float(row.get("onsetSupport", 0.0)) < float(config["onsetSupportMin"]):
                continue
            if float(row.get("activitySupport", 0.0)) < float(config["activitySupportMin"]):
                continue
            if config["activeStateMode"] == "inactive_only" and bool(row.get("basicPitchActiveAtSite", False)):
                continue

            candidate_score = float(row.get("templateScore", 0.0))
            ratio = candidate_score / max_active_score
            if ratio + EPS < float(config["candidateToMaxActiveTemplateScoreMin"]):
                continue

            midi = int(row["midi"])
            nearest_interval = nearest_different_active_interval(midi, active_midis)
            if not interval_policy_ok(nearest_interval, str(config["intervalContextPolicy"])):
                continue

            absolute = base_builder.corrected_step(float(row["siteSeconds"]), lattice)
            if absolute is None:
                continue
            if (absolute, midi) in occupied or per_step[absolute] >= GUITAR_CAP:
                continue

            eligible += 1
            candidates.append((row, absolute, ratio, nearest_interval))

        if not candidates:
            continue
        sites_with_eligible += 1

        # Predeclared reference-blind top-1/site ordering. Relative evidence is
        # primary; remaining keys only make ties deterministic.
        candidates.sort(key=lambda item: (
            -float(item[2]),
            -float(item[0].get("templateRank", 0.0)),
            -float(item[0].get("templateScore", 0.0)),
            -float(item[0].get("onsetSupport", 0.0)),
            -float(item[0].get("activitySupport", 0.0)),
            int(item[0]["midi"]),
        ))

        site_added = 0
        for row, absolute, ratio, nearest_interval in candidates:
            midi = int(row["midi"])
            if (absolute, midi) in occupied or per_step[absolute] >= GUITAR_CAP:
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
            }
            out.append(base_builder.event_for_recovery(absolute, midi, "combinedGuitar", config, evidence))
            occupied.add((absolute, midi))
            per_step[absolute] += 1
            added += 1
            site_added += 1
            if site_added >= MAX_ADDS_PER_SITE:
                break
        if site_added:
            sites_with_adds += 1

    out.sort(key=lambda note: (int(note["absoluteGridStep"]), int(note["midi"])))
    if max(per_step.values(), default=0) > GUITAR_CAP:
        raise AssertionError("contextual Guitar variant exceeded polyphony cap")
    if len({(int(n["absoluteGridStep"]), int(n["midi"])) for n in out}) != len(out):
        raise AssertionError("contextual Guitar variant violated (step,midi) dedupe")
    return out, {
        "added": added,
        "eligible": eligible,
        "sitesWithActiveContext": sites_with_active_context,
        "sitesWithEligible": sites_with_eligible,
        "sitesWithAdds": sites_with_adds,
    }


def normalized_coordinates(events: list[dict[str, Any]]) -> list[tuple[int, int]]:
    return sorted((int(event["absoluteGridStep"]), int(event["midi"])) for event in events)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--pool", type=Path, required=True)
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    if args.output_dir.exists() or args.manifest.exists():
        raise RuntimeError("contextual sweep generation outputs must not pre-exist")
    if sha256_file(args.base) != EXPECTED_BASE_SHA256:
        raise RuntimeError("frozen Iteration 003 SHA256 mismatch")
    if sha256_file(args.pool) != EXPECTED_POOL_SHA256:
        raise RuntimeError("frozen V167 evidence-pool SHA256 mismatch")

    base = json.loads(args.base.read_text(encoding="utf-8"))
    pool = json.loads(args.pool.read_text(encoding="utf-8"))
    timebase = json.loads(args.timebase.read_text(encoding="utf-8"))

    if base.get("version") != "V167" or int((base.get("calibration") or {}).get("iteration", -1)) != 3:
        raise RuntimeError("contextual sweep base must be frozen V167 Iteration 003")
    safety = base.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise RuntimeError("Iteration 003 safety boundary invalid")
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
    if len(streams.get("combinedGuitar") or []) != EXPECTED_BASE_COUNTS["combinedGuitar"]:
        raise RuntimeError("Iteration 003 Guitar count drift")
    if len(streams.get("bass") or []) != EXPECTED_BASE_COUNTS["bass"]:
        raise RuntimeError("Iteration 003 Bass count drift")
    base_guitar = [base_builder.compact_base_note(dict(note), "combinedGuitar") for note in streams["combinedGuitar"]]
    base_bass = [base_builder.compact_base_note(dict(note), "bass") for note in streams["bass"]]
    bass_coordinates = normalized_coordinates(base_bass)

    guitar_pool = (pool.get("upstreamPitchPools") or {}).get("guitarStandaloneHarmonic") or {}
    guitar_rows = list(guitar_pool.get("candidates") or [])
    if len(guitar_rows) != EXPECTED_GUITAR_POOL_ROWS:
        raise RuntimeError("frozen Guitar upstream pool count drift")
    if len({int(row["siteFrame"]) for row in guitar_rows}) != EXPECTED_GUITAR_POOL_SITES:
        raise RuntimeError("frozen Guitar upstream site count drift")

    configs = list(contextual_configs())
    if len(configs) != 37 or sum(bool(c.get("baseline", False)) for c in configs) != 1:
        raise RuntimeError("contextual preregistration must be baseline + 36 rules")

    manifest: dict[str, Any] = {
        "schema": "dadrock.tabs.v167.predeclared-contextual-guitar-recovery-manifest.v1",
        "version": "V167",
        "status": "FROZEN_BEFORE_REFERENCE_SCORING",
        "classification": "SINGLE_SONG_TRAINING_CALIBRATION_ONLY",
        "inputs": {
            "iteration003Sha256": sha256_file(args.base),
            "poolSha256": sha256_file(args.pool),
            "timebaseSha256": sha256_file(args.timebase),
            "baseCounts": EXPECTED_BASE_COUNTS,
            "guitarPoolRows": len(guitar_rows),
            "guitarPoolSites": EXPECTED_GUITAR_POOL_SITES,
        },
        "policy": {
            "referenceRead": False,
            "scorerRead": False,
            "allVariantRulesPredeclaredBeforeScoring": True,
            "individualEventSelectionByReference": False,
            "iteration003Immutable": True,
            "bassNormalizedStreamFixedToIteration003": True,
            "existingIteration003GuitarEventsPreferred": True,
            "globalPhaseCorrectionGridSteps": base_builder.GLOBAL_PHASE_CORRECTION,
            "newRecoveryTimingRule": "nearest-frozen-v166-subdivision-then-frozen-minus-12-global-phase",
            "siteSelectionOrder": [
                "candidate_to_max_active_template_score_ratio_desc",
                "template_rank_desc",
                "template_score_desc",
                "onset_support_desc",
                "activity_support_desc",
                "midi_asc",
            ],
            "fundamentalPresentFilterInheritedFromFrozenStructuralEvidence": True,
            "gpuCudaModalUsed": False,
            "mainOrProductionModified": False,
        },
        "variants": [],
    }

    for config in configs:
        guitar, summary = build_guitar(base_guitar, guitar_rows, config, lattice)
        if normalized_coordinates(base_bass) != bass_coordinates:
            raise AssertionError("Bass baseline coordinates changed during contextual generation")
        variant = {**copy.deepcopy(config), "summary": copy.deepcopy(summary)}
        payload = base_builder.score_minimal_payload(base, guitar, base_bass, variant)
        path = args.output_dir / "guitar" / f"{config['id']}.json"
        write_json(path, payload)
        manifest["variants"].append({
            "id": str(config["id"]),
            "stream": "combinedGuitar",
            "config": copy.deepcopy(config),
            "summary": copy.deepcopy(summary),
            "relativePath": str(path.relative_to(args.output_dir)),
            "sha256": sha256_file(path),
            "counts": {"combinedGuitar": len(guitar), "bass": len(base_bass)},
        })

    write_json(args.manifest, manifest)
    print(json.dumps({
        "variantCount": len(manifest["variants"]),
        "nonBaselineCount": len(manifest["variants"]) - 1,
        "manifestSha256": sha256_file(args.manifest),
        "minAdded": min(int(row["summary"]["added"]) for row in manifest["variants"]),
        "maxAdded": max(int(row["summary"]["added"]) for row in manifest["variants"]),
        "bassCountEveryVariant": EXPECTED_BASE_COUNTS["bass"],
        "referenceRead": False,
        "scorerRead": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
