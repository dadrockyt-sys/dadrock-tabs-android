#!/usr/bin/env python3
"""Astra H1: no-media, non-authorizing capacity formulas from frozen source shapes.

No training, inference, network access, media, manifests, or workflow dispatch.
Optional scalar aggregate-frame input must come from separately reviewed evidence;
never treat scenario frame counts as measurements.
"""
from __future__ import annotations
import argparse
from decimal import Decimal
import json

CAPTURES = 256
MIN_FRAMES_PER_CAPTURE = 200
FEATURE_BINS = 192
FEATURE_ITEM_BYTES = 4
STRINGS = 6
LABEL_ITEM_BYTES = 2
SAMPLE_RATE_HZ = 22050
HOP_SAMPLES = 512
ARCHIVE_COUNT = 8
COMPRESSED_ARCHIVE_BYTES = 4004045267
LARGEST_COMPRESSED_ARCHIVE_BYTES = 1150819056
HISTORIC_INVENTORY_EXTRACTED_SUM_BYTES = 7288969715
EVALUATION_CLASS_COUNT = 21
EVALUATION_EVENT_ITEM_BYTES = 4
EVALUATION_STATE_ITEM_BYTES = 4


def prepared_bytes(total_frames: int) -> int:
    if type(total_frames) is not int or total_frames < CAPTURES * MIN_FRAMES_PER_CAPTURE:
        raise ValueError("MISSING_OR_INVALID_AUTHORIZED_FRAME_AGGREGATE")
    return total_frames * (FEATURE_BINS * FEATURE_ITEM_BYTES + STRINGS * LABEL_ITEM_BYTES)


def hypothetical_frame_count(minutes_per_capture: int) -> int:
    """Round up nominal hop-based frames; NOT a measured file or VQT frame count."""
    if type(minutes_per_capture) is not int or minutes_per_capture <= 0:
        raise ValueError("INVALID_HYPOTHETICAL_MINUTES")
    numerator = minutes_per_capture * 60 * SAMPLE_RATE_HZ
    per_capture = (numerator + HOP_SAMPLES - 1) // HOP_SAMPLES
    return CAPTURES * per_capture


def evaluation_array_bytes(frames_one_capture: int) -> dict:
    """Only sizes of identifiable arrays, not Python/Torch peak-RAM bounds."""
    if type(frames_one_capture) is not int or frames_one_capture <= 0:
        raise ValueError("INVALID_CAPTURE_FRAME_COUNT")
    return {
        "paddedCQTFloat32Bytes": FEATURE_BINS * FEATURE_ITEM_BYTES * (frames_one_capture + 8),
        "storedStateFloat32Bytes": frames_one_capture * STRINGS * EVALUATION_CLASS_COUNT * EVALUATION_STATE_ITEM_BYTES,
        "storedEventFloat32Bytes": frames_one_capture * STRINGS * EVALUATION_EVENT_ITEM_BYTES,
        "stateToFloat64CopyBytes": frames_one_capture * STRINGS * EVALUATION_CLASS_COUNT * 8,
        "notAPeakMemoryBound": True,
    }


def build_receipt(total_frames: int | None = None) -> dict:
    per_frame = FEATURE_BINS * FEATURE_ITEM_BYTES + STRINGS * LABEL_ITEM_BYTES
    # Scenario uses average *nominal* capture duration (minutes), not a measurement.
    scenarios = []
    for minutes in (1, 2, 5, 10, 15):
        frames = hypothetical_frame_count(minutes)
        n = prepared_bytes(frames)
        scenarios.append({
            "hypotheticalMinutesPerCapture": minutes,
            "nominalAggregateFrames": frames,
            "nominalPreparedPayloadBytes": n,
            "nominalPreparedPayloadGiB": str((Decimal(n) / Decimal(2**30)).quantize(Decimal("0.001"))),
            "notAnObservedH1FrameCount": True,
        })
    actual = None if total_frames is None else {
        "externallySuppliedAggregateFrameCount": total_frames,
        "preparedPayloadBytesExcludingNpyHeaders": prepared_bytes(total_frames),
        "independentFrameProvenanceVerified": False,
    }
    return {
        "schema": "astra-h1-static-capacity-review-v1",
        "sourceDerivedConstants": {
            "acceptedCaptures": CAPTURES, "minimumFramesPerCapture": MIN_FRAMES_PER_CAPTURE,
            "featureBins": FEATURE_BINS, "featureItemBytes": FEATURE_ITEM_BYTES,
            "labelStrings": STRINGS, "labelItemBytes": LABEL_ITEM_BYTES,
            "sampleRateHz": SAMPLE_RATE_HZ, "hopSamples": HOP_SAMPLES,
            "preparedPayloadBytesPerFrame": per_frame,
            "preparedFeatureBytesPerFrame": FEATURE_BINS * FEATURE_ITEM_BYTES,
            "preparedLabelBytesPerFrame": STRINGS * LABEL_ITEM_BYTES,
            "npyFilesAcrossCaptures": CAPTURES * 2,
            "minimumPreparedPayloadBytesIfAllCapturesHaveExactly200Frames": prepared_bytes(CAPTURES * MIN_FRAMES_PER_CAPTURE),
            "one200FrameMicrobatchWindowFloat32Bytes": 200 * FEATURE_BINS * 9 * 4,
        },
        "historicMetadata": {
            "developmentArchives": ARCHIVE_COUNT,
            "compressedArchiveSumBytes": COMPRESSED_ARCHIVE_BYTES,
            "largestCompressedArchiveBytes": LARGEST_COMPRESSED_ARCHIVE_BYTES,
            "priorInventoryExtractedAggregateBytesAcrossSeparateRuns": HISTORIC_INVENTORY_EXTRACTED_SUM_BYTES,
            "observedSameRunnerPeakExtractionBytes": None,
        },
        "nominalDurationSensitivity": scenarios,
        "exampleEvaluatorArraysFor100000Frames": evaluation_array_bytes(100000),
        "optionalUnverifiedFrameAggregate": actual,
        "unknownForHardDiskBound": [
            "measuredTotalAcceptedFrames", "peakExtractedBytesPerArchive", "effectiveRunnerFreeDiskBytes",
            "dependencyAndPackageCacheBytes", "repositoryAndPinnedSourceBytes",
            "simultaneousDecodedAudioAndVQTIntermediates", "manifestAndArtifactBytes", "failureAndDiskReserveBytes",
        ],
        "unknownForHardRamBound": [
            "largestAcceptedCaptureFrames", "torchModelParameterAndAdadeltaStateBytes",
            "activationAndAutogradPeaks", "librosaVQTTransientArrayPeak", "pythonAndSystemReserve",
        ],
        "verifiedDiskOrMemoryHeadroom": False,
        "readiness": "NO_GO_INSUFFICIENT_EVIDENCE",
        "launchPermission": False,
        "realMediaRead": False,
        "trainingExecuted": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--aggregate-frames", type=int,
                   help="Optional authorized scalar total across 256 captures; never used as approval")
    args = p.parse_args()
    print(json.dumps(build_receipt(args.aggregate_frames), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
