#!/usr/bin/env python3
"""Merge frozen per-package Guitar-TECHS V6 alignment/inventory reports.

No model or correctness code is imported. The merger applies only the frozen
structural/alignment A/B/C decision from the preregistration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from collections import Counter
from pathlib import Path

CONTRACT = "songsterr-fresh-guitar-techs-v6-alignment-inventory-merged-v1"
PACKAGE_CONTRACT = "songsterr-fresh-guitar-techs-v6-alignment-inventory-v1"
EXPECTED_PACKAGES = {
    "P1_chords.zip",
    "P1_scales.zip",
    "P1_singlenotes.zip",
    "P1_techniques.zip",
    "P2_chords.zip",
    "P2_scales.zip",
    "P2_singlenotes.zip",
    "P2_techniques.zip",
    "P3_music.zip",
}


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package_player_category(package: str) -> tuple[str, str]:
    stem = package[:-4] if package.endswith(".zip") else package
    player, category = stem.split("_", 1)
    return player, category


def merge_reports(paths: list[Path]) -> dict:
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    for report in reports:
        if report.get("contract") != PACKAGE_CONTRACT:
            raise RuntimeError(f"PACKAGE_CONTRACT_CHANGED:{report.get('contract')}")
        policy = report.get("policyBoundary", {})
        assert policy.get("basicPitchInvoked") is False
        assert policy.get("v6Invoked") is False
        assert policy.get("correctnessComputed") is False

    by_package = {report["package"]: report for report in reports}
    if set(by_package) != EXPECTED_PACKAGES:
        raise RuntimeError(f"PACKAGE_SET_CHANGED:{sorted(by_package)}")

    all_pairs = []
    package_summaries = []
    sample_rates = Counter()
    channels = Counter()
    subtypes = Counter()
    midi_formats = Counter()
    ticks_per_beat = Counter()
    lag_hops = []
    lag_seconds = []
    alignment_statuses = Counter()
    total_reference_events = 0
    pitch_values = []
    total_unpaired_di = 0
    total_unpaired_midi = 0
    anomaly_totals = Counter()

    for package in sorted(by_package):
        report = by_package[package]
        player, category = package_player_category(package)
        total_unpaired_di += len(report["unpairedDiKeys"])
        total_unpaired_midi += len(report["unpairedMidiKeys"])
        anomaly_totals.update(report["midiAnomalyTotals"])
        total_reference_events += int(report["pairedReferenceEventCount"])
        if report["referencePitchMin"] is not None:
            pitch_values.extend([int(report["referencePitchMin"]), int(report["referencePitchMax"])])

        for pair in report["pairs"]:
            wav = pair["wav"]
            midi = pair["midi"]
            alignment = pair["alignment"]
            sample_rates[str(wav["sampleRate"])] += 1
            channels[str(wav["channels"])] += 1
            subtypes[str(wav["subtype"])] += 1
            midi_formats[str(midi["format"])] += 1
            ticks_per_beat[str(midi["ticksPerBeat"])] += 1
            status = alignment["status"]
            alignment_statuses[status] += 1
            if status == "OK":
                lag_hops.append(int(alignment["lagHops"]))
                lag_seconds.append(float(alignment["lagSecondsAddedToMidi"]))
            all_pairs.append({
                "package": package,
                "player": player,
                "category": category,
                "semanticKey": pair["semanticKey"],
                "diEntry": pair["diEntry"],
                "midiEntry": pair["midiEntry"],
                "diSha256": pair["diSha256"],
                "midiSha256": pair["midiSha256"],
                "sampleRate": int(wav["sampleRate"]),
                "channels": int(wav["channels"]),
                "subtype": str(wav["subtype"]),
                "referenceEventCount": int(midi["pairedEventCount"]),
                "pitchMin": midi["pitchMin"],
                "pitchMax": midi["pitchMax"],
                "alignmentStatus": status,
                "lagHops": alignment.get("lagHops"),
                "lagSecondsAddedToMidi": alignment.get("lagSecondsAddedToMidi"),
                "bestCorrelation": alignment.get("bestCorrelation"),
                "nextBestCorrelationOutsidePlusMinus2Hops": alignment.get("nextBestCorrelationOutsidePlusMinus2Hops"),
                "hopSeconds": alignment.get("hopSeconds"),
            })

        package_summaries.append({
            "package": package,
            "archiveMd5": report["archiveMd5Actual"],
            "archiveSha256": report["archiveSha256"],
            "entryCounts": report["entryCounts"],
            "pairedDiMidiCount": report["pairedDiMidiCount"],
            "pairedReferenceEventCount": report["pairedReferenceEventCount"],
            "pairingManifestSha256": report["pairingManifestSha256"],
            "alignmentLagManifestSha256": report["alignmentLagManifestSha256"],
            "unpairedDiCount": len(report["unpairedDiKeys"]),
            "unpairedMidiCount": len(report["unpairedMidiKeys"]),
            "midiAnomalyTotals": report["midiAnomalyTotals"],
        })

    identity_manifest = [
        {
            "package": row["package"],
            "semanticKey": row["semanticKey"],
            "diEntry": row["diEntry"],
            "midiEntry": row["midiEntry"],
            "diSha256": row["diSha256"],
            "midiSha256": row["midiSha256"],
        }
        for row in all_pairs
    ]
    lag_manifest = [
        {
            "package": row["package"],
            "semanticKey": row["semanticKey"],
            "alignmentStatus": row["alignmentStatus"],
            "lagHops": row["lagHops"],
            "lagSecondsAddedToMidi": row["lagSecondsAddedToMidi"],
        }
        for row in all_pairs
    ]
    identity_manifest_sha = sha256_bytes(canonical_json(identity_manifest).encode("utf-8"))
    lag_manifest_sha = sha256_bytes(canonical_json(lag_manifest).encode("utf-8"))

    structural_ok = (
        all(report["archiveMd5Verified"] is True for report in reports)
        and total_unpaired_di == 0
        and total_unpaired_midi == 0
        and sum(anomaly_totals.values()) == 0
        and len(all_pairs) > 0
    )
    alignment_ok = alignment_statuses == Counter({"OK": len(all_pairs)})

    all_within_one_hop = False
    if structural_ok and alignment_ok:
        all_within_one_hop = all(
            abs(int(row["lagHops"])) <= 1
            for row in all_pairs
        )
        outcome = "A_RAW_TIMESTAMPS_AUTHORITATIVE" if all_within_one_hop else "B_PER_FILE_CONSTANT_OFFSET_CORRECTION_AUTHORITATIVE"
        suitable = True
    else:
        outcome = "C_DATASET_UNSUITABLE_FOR_V6_ADMISSION"
        suitable = False

    lag_summary = {
        "count": len(lag_seconds),
        "minimumSeconds": min(lag_seconds) if lag_seconds else None,
        "maximumSeconds": max(lag_seconds) if lag_seconds else None,
        "medianSeconds": statistics.median(lag_seconds) if lag_seconds else None,
        "minimumHops": min(lag_hops) if lag_hops else None,
        "maximumHops": max(lag_hops) if lag_hops else None,
        "medianHops": statistics.median(lag_hops) if lag_hops else None,
        "allAbsoluteLagsWithinOneHop": all_within_one_hop,
    }

    population_rows = [
        {
            "package": row["package"],
            "player": row["player"],
            "category": row["category"],
            "semanticKey": row["semanticKey"],
            "diSha256": row["diSha256"],
            "midiSha256": row["midiSha256"],
            "lagSecondsAddedToMidi": row["lagSecondsAddedToMidi"] if suitable else None,
        }
        for row in all_pairs
    ]
    population_sha = sha256_bytes(canonical_json(population_rows).encode("utf-8"))

    return {
        "contract": CONTRACT,
        "zenodoRecord": "14963133",
        "zenodoVersion": "v1",
        "packageCount": len(reports),
        "pairedDiMidiCount": len(all_pairs),
        "pairedReferenceEventCount": total_reference_events,
        "referencePitchMin": min(pitch_values) if pitch_values else None,
        "referencePitchMax": max(pitch_values) if pitch_values else None,
        "totalUnpairedDiCount": total_unpaired_di,
        "totalUnpairedMidiCount": total_unpaired_midi,
        "midiAnomalyTotals": dict(sorted(anomaly_totals.items())),
        "sampleRateCounts": dict(sorted(sample_rates.items())),
        "channelCountCounts": dict(sorted(channels.items())),
        "wavSubtypeCounts": dict(sorted(subtypes.items())),
        "midiFormatCounts": dict(sorted(midi_formats.items())),
        "ticksPerBeatCounts": dict(sorted(ticks_per_beat.items())),
        "alignmentStatusCounts": dict(sorted(alignment_statuses.items())),
        "alignmentLagSummary": lag_summary,
        "pairingIdentityManifestSha256": identity_manifest_sha,
        "alignmentLagManifestSha256": lag_manifest_sha,
        "proposedScoringPopulationSha256": population_sha,
        "alignmentDecision": outcome,
        "datasetStructurallySuitable": suitable,
        "packageSummaries": package_summaries,
        "pairs": all_pairs,
        "policyBoundary": {
            "basicPitchInvoked": False,
            "v6Invoked": False,
            "correctnessComputed": False,
            "protectedSongUsed": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    paths = sorted(input_dir.glob("*.json"))
    result = merge_reports(paths)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": result["contract"],
        "packageCount": result["packageCount"],
        "pairedDiMidiCount": result["pairedDiMidiCount"],
        "pairedReferenceEventCount": result["pairedReferenceEventCount"],
        "alignmentDecision": result["alignmentDecision"],
        "datasetStructurallySuitable": result["datasetStructurallySuitable"],
        "pairingIdentityManifestSha256": result["pairingIdentityManifestSha256"],
        "alignmentLagManifestSha256": result["alignmentLagManifestSha256"],
        "proposedScoringPopulationSha256": result["proposedScoringPopulationSha256"],
        "output": str(output),
        "outputSha256": sha256_file(output),
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
