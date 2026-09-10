#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

CONTRACT = "songsterr-fresh-v3-unresolved-duration-inventory-v2"
V3_RELEASE_CONTRACT = "songsterr-fresh-spectral-activation-release-evidence-v3"
REATTACK_REASON = "NO_CLEAR_RELEASE_BEFORE_SAME_PITCH_REATTACK"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Build a descriptive inventory of unresolved v3 duration evidence "
            "without changing events or selecting new thresholds."
        )
    )
    parser.add_argument("--evidence", required=True, help="v3 note evidence JSON")
    parser.add_argument("--output", required=True, help="inventory JSON")
    return parser.parse_args()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values, q):
    if not values:
        return None
    ordered = sorted(float(v) for v in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def stats(values):
    cleaned = [float(v) for v in values if v is not None and math.isfinite(float(v))]
    if not cleaned:
        return {
            "count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": len(cleaned),
        "minimum": min(cleaned),
        "p10": percentile(cleaned, 0.10),
        "median": percentile(cleaned, 0.50),
        "mean": sum(cleaned) / len(cleaned),
        "p90": percentile(cleaned, 0.90),
        "maximum": max(cleaned),
    }


def midi_histogram(rows):
    counts = Counter(int(row["selectedMidi"]) for row in rows)
    return {str(midi): count for midi, count in sorted(counts.items())}


def next_same_pitch_gap(onsets, index, midi):
    source_start = float(onsets[index]["sourceStart"])
    for later in onsets[index + 1:]:
        if later.get("classification") != "unambiguous":
            continue
        if later.get("selectedMidi") is None or int(later["selectedMidi"]) != midi:
            continue
        gap = float(later["sourceStart"]) - source_start
        return gap if gap >= 0.0 else None
    return None


def summarize_group(rows, gaps):
    return {
        "count": len(rows),
        "midiHistogram": midi_histogram(rows),
        "onsetConfidence": stats([row.get("onsetConfidence") for row in rows]),
        "nextSamePitchReattackGapSeconds": stats(gaps),
    }


def fraction(part, whole):
    return float(part) / float(whole) if whole else 0.0


def main():
    args = parse_args()
    evidence_path = Path(args.evidence)
    evidence = load_json(evidence_path)

    release = (evidence.get("diagnostics") or {}).get("releaseEvidence") or {}
    if release.get("contract") != V3_RELEASE_CONTRACT:
        raise RuntimeError(
            f"V3_UNRESOLVED_INVENTORY_REQUIRES_V3_RELEASE:{release.get('contract')}"
        )
    if release.get("samePitchReattackUsedAsDuration") is not False:
        raise RuntimeError("V3_UNRESOLVED_INVENTORY_REATTACK_DURATION_GUARD_CHANGED")
    if release.get("nextOnsetUsedAsDuration") is not False:
        raise RuntimeError("V3_UNRESOLVED_INVENTORY_NEXT_ONSET_DURATION_GUARD_CHANGED")
    if release.get("decodedModelNoteEndUsedAsDuration") is not False:
        raise RuntimeError("V3_UNRESOLVED_INVENTORY_DECODED_END_DURATION_GUARD_CHANGED")

    onsets = evidence.get("onsets")
    if not isinstance(onsets, list):
        raise RuntimeError("V3_UNRESOLVED_INVENTORY_ONSETS_MISSING")

    unresolved = []
    resolved = []
    primary_groups = defaultdict(list)
    primary_gaps = defaultdict(list)
    fallback_groups = defaultdict(list)
    fallback_gaps = defaultdict(list)

    resolved_gaps = []
    unresolved_gaps = []
    by_midi = defaultdict(lambda: {
        "eligibleCount": 0,
        "resolvedCount": 0,
        "unresolvedCount": 0,
        "resolvedOnsetConfidence": [],
        "unresolvedOnsetConfidence": [],
        "resolvedNextSamePitchReattackGapSeconds": [],
        "unresolvedNextSamePitchReattackGapSeconds": [],
        "unresolvedPrimaryReasonCounts": Counter(),
        "unresolvedFallbackReasonCounts": Counter(),
    })

    resolved_count = 0
    eligible_count = 0
    for index, onset in enumerate(onsets):
        if onset.get("classification") != "unambiguous" or onset.get("selectedMidi") is None:
            continue

        eligible_count += 1
        midi = int(onset["selectedMidi"])
        gap = next_same_pitch_gap(onsets, index, midi)
        midi_context = by_midi[midi]
        midi_context["eligibleCount"] += 1

        if onset.get("durationSeconds") is not None:
            if onset.get("sourceEnd") is None:
                raise RuntimeError(
                    f"V3_UNRESOLVED_INVENTORY_RESOLVED_EVENT_MISSING_END:{onset.get('onsetId')}"
                )
            resolved_count += 1
            resolved.append(onset)
            midi_context["resolvedCount"] += 1
            midi_context["resolvedOnsetConfidence"].append(onset.get("onsetConfidence"))
            if gap is not None:
                resolved_gaps.append(gap)
                midi_context["resolvedNextSamePitchReattackGapSeconds"].append(gap)
            continue

        if onset.get("sourceEnd") is not None:
            raise RuntimeError(
                f"V3_UNRESOLVED_INVENTORY_UNRESOLVED_EVENT_HAS_END:{onset.get('onsetId')}"
            )

        duration_evidence = (onset.get("provenance") or {}).get("durationEvidence") or {}
        if duration_evidence.get("resolved") is not False:
            raise RuntimeError(
                f"V3_UNRESOLVED_INVENTORY_UNRESOLVED_PROVENANCE_CHANGED:{onset.get('onsetId')}"
            )
        reason = duration_evidence.get("reason") or "UNDECLARED"

        unresolved.append(onset)
        midi_context["unresolvedCount"] += 1
        midi_context["unresolvedOnsetConfidence"].append(onset.get("onsetConfidence"))
        midi_context["unresolvedPrimaryReasonCounts"][reason] += 1
        primary_groups[reason].append(onset)
        if gap is not None:
            unresolved_gaps.append(gap)
            midi_context["unresolvedNextSamePitchReattackGapSeconds"].append(gap)
            primary_gaps[reason].append(gap)

        fallback = duration_evidence.get("activationFallback")
        if reason == REATTACK_REASON:
            if not isinstance(fallback, dict) or fallback.get("attempted") is not True:
                raise RuntimeError(
                    f"V3_UNRESOLVED_INVENTORY_FALLBACK_PROVENANCE_MISSING:{onset.get('onsetId')}"
                )
            if fallback.get("resolved") is not False:
                raise RuntimeError(
                    f"V3_UNRESOLVED_INVENTORY_FALLBACK_RESOLUTION_MISMATCH:{onset.get('onsetId')}"
                )
            fallback_reason = fallback.get("reason") or "UNDECLARED"
            midi_context["unresolvedFallbackReasonCounts"][fallback_reason] += 1
            fallback_groups[fallback_reason].append(onset)
            if gap is not None:
                fallback_gaps[fallback_reason].append(gap)
        elif fallback is not None:
            raise RuntimeError(
                f"V3_UNRESOLVED_INVENTORY_UNEXPECTED_FALLBACK_PROVENANCE:{onset.get('onsetId')}"
            )

    expected_attempted = release.get("attemptedPromotedOnsetCount")
    expected_resolved = release.get("resolvedPromotedOnsetCount")
    expected_unresolved = release.get("unresolvedPromotedOnsetCount")
    if expected_attempted is not None and int(expected_attempted) != eligible_count:
        raise RuntimeError(
            f"V3_UNRESOLVED_INVENTORY_ATTEMPTED_COUNT_MISMATCH:{eligible_count}:{expected_attempted}"
        )
    if expected_resolved is not None and int(expected_resolved) != resolved_count:
        raise RuntimeError(
            f"V3_UNRESOLVED_INVENTORY_RESOLVED_COUNT_MISMATCH:{resolved_count}:{expected_resolved}"
        )
    if expected_unresolved is not None and int(expected_unresolved) != len(unresolved):
        raise RuntimeError(
            f"V3_UNRESOLVED_INVENTORY_UNRESOLVED_COUNT_MISMATCH:{len(unresolved)}:{expected_unresolved}"
        )

    primary = {
        reason: summarize_group(rows, primary_gaps[reason])
        for reason, rows in sorted(primary_groups.items())
    }
    fallback = {
        reason: summarize_group(rows, fallback_gaps[reason])
        for reason, rows in sorted(fallback_groups.items())
    }

    midi_resolution = {}
    for midi, context in sorted(by_midi.items()):
        midi_resolution[str(midi)] = {
            "eligibleCount": context["eligibleCount"],
            "resolvedCount": context["resolvedCount"],
            "unresolvedCount": context["unresolvedCount"],
            "unresolvedFraction": fraction(
                context["unresolvedCount"], context["eligibleCount"]
            ),
            "resolvedOnsetConfidence": stats(context["resolvedOnsetConfidence"]),
            "unresolvedOnsetConfidence": stats(context["unresolvedOnsetConfidence"]),
            "resolvedNextSamePitchReattackGapSeconds": stats(
                context["resolvedNextSamePitchReattackGapSeconds"]
            ),
            "unresolvedNextSamePitchReattackGapSeconds": stats(
                context["unresolvedNextSamePitchReattackGapSeconds"]
            ),
            "unresolvedPrimaryReasonCounts": dict(sorted(
                context["unresolvedPrimaryReasonCounts"].items()
            )),
            "unresolvedFallbackReasonCounts": dict(sorted(
                context["unresolvedFallbackReasonCounts"].items()
            )),
        }

    output = {
        "contract": CONTRACT,
        "version": 2,
        "descriptiveOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "readsDecodedModelNoteEnd": False,
        "usesDecodedModelNoteEndAsDuration": False,
        "usesNextOnsetAsDuration": False,
        "usesSamePitchReattackAsDuration": False,
        "proposesNewReleaseRule": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "sourceEvidence": {
            "path": str(evidence_path),
            "sha256": sha256_file(evidence_path),
            "releaseContract": release.get("contract"),
            "activationRule": release.get("activationFixedRule"),
        },
        "counts": {
            "durationEligibleEvents": eligible_count,
            "resolvedEvents": resolved_count,
            "unresolvedEvents": len(unresolved),
        },
        "resolutionContext": {
            "resolvedOnsetConfidence": stats([
                row.get("onsetConfidence") for row in resolved
            ]),
            "unresolvedOnsetConfidence": stats([
                row.get("onsetConfidence") for row in unresolved
            ]),
            "resolvedNextSamePitchReattackGapSeconds": stats(resolved_gaps),
            "unresolvedNextSamePitchReattackGapSeconds": stats(unresolved_gaps),
            "byMidi": midi_resolution,
        },
        "unresolvedPrimaryReasons": primary,
        "reattackCensoredFallbackRejections": fallback,
        "hardGuards": {
            "inputEventMutation": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInference": False,
            "decodedModelEndRead": False,
            "newThresholdSelection": False,
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print(json.dumps({
        "contract": CONTRACT,
        "counts": output["counts"],
        "primaryReasons": {k: v["count"] for k, v in primary.items()},
        "fallbackRejections": {k: v["count"] for k, v in fallback.items()},
        "resolvedMedianNextSamePitchGapSeconds": output["resolutionContext"]["resolvedNextSamePitchReattackGapSeconds"]["median"],
        "unresolvedMedianNextSamePitchGapSeconds": output["resolutionContext"]["unresolvedNextSamePitchReattackGapSeconds"]["median"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
