#!/usr/bin/env python3
"""Offline, conditional disk overlap ledger from existing scalar inventory receipts.

No media, network, GitHub Actions, model code or actual runner measurements.
This tool is a desk-review sensitivity model, NEVER a launch gate or upper bound.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import argparse
import json

ACCEPTED_CAPTURES = 256
ACCEPTED_WAV_HEADERS = 158
ACCEPTED_VIDEO_MP3_NO_DURATIONS = 98
NOMINAL_WAV_FRAMES = 1_227_986
COMPRESSED_SUM = 4_004_045_267
EXTRACTED_VISIBLE_LOGICAL_SUM = 7_288_969_715
FEATURE_AND_LABEL_BYTES_PER_FRAME = 780
SAMPLE_RATE_HZ = 22_050
HOP_SAMPLES = 512
HISTORICAL_LOG_RECEIPT_GIT_BLOB = "5706ac4ed1a9590fa74f7644e6be7e642ffb9db2"
HISTORIC_INVENTORY_RUN_ID = 35_563_511_409
WORKFLOW_GIT_BLOB = "90e8168fc1ca40738ba07291ca1001a36718f4e3"


@dataclass(frozen=True)
class Archive:
    name: str
    job_id: int
    compressed: int
    extracted_visible: int
    wav_accepted: int
    video_accepted: int
    nominal_wav_frames: int

    @property
    def accepted(self) -> int:
        return self.wav_accepted + self.video_accepted


# Previously recorded inventory-only receipt figures, ordered exactly as in the
# dormant workflow. NOT actual H1 preparation/output sizes or disk peaks.
ARCHIVES = (
    Archive("P1_chords.zip", 106220738915, 981741162, 1271640503, 54, 30, 366620),
    Archive("P1_scales.zip", 106220738971, 453349723, 548096546, 24, 23, 165384),
    Archive("P1_singlenotes.zip", 106220738900, 108626613, 157082257, 2, 1, 47546),
    Archive("P1_techniques.zip", 106220738799, 326280863, 651845901, 2, 0, 47546),
    Archive("P2_chords.zip", 106220738819, 1150819056, 2442840341, 48, 24, 342294),
    Archive("P2_scales.zip", 106220738872, 471254783, 996527054, 24, 19, 164882),
    Archive("P2_singlenotes.zip", 106220738938, 116133457, 286690653, 2, 1, 47546),
    Archive("P2_techniques.zip", 106220738845, 395839610, 934246460, 2, 0, 46168),
)


def validate_archives(archives: tuple[Archive, ...] = ARCHIVES) -> None:
    if len(archives) != 8 or len({a.name for a in archives}) != 8:
        raise ValueError("HISTORICAL_ARCHIVE_SET_DRIFT")
    if any(type(v) is not int or v < 0 for a in archives for v in (
        a.job_id, a.compressed, a.extracted_visible, a.wav_accepted,
        a.video_accepted, a.nominal_wav_frames
    )):
        raise ValueError("INVALID_HISTORICAL_INPUT")
    if (sum(a.compressed for a in archives) != COMPRESSED_SUM
            or sum(a.extracted_visible for a in archives) != EXTRACTED_VISIBLE_LOGICAL_SUM
            or sum(a.accepted for a in archives) != ACCEPTED_CAPTURES
            or sum(a.wav_accepted for a in archives) != ACCEPTED_WAV_HEADERS
            or sum(a.video_accepted for a in archives) != ACCEPTED_VIDEO_MP3_NO_DURATIONS
            or sum(a.nominal_wav_frames for a in archives) != NOMINAL_WAV_FRAMES):
        raise ValueError("HISTORICAL_SCALAR_RECONCILIATION_FAILED")


def hypothetical_video_frames(minutes: int) -> int:
    if type(minutes) is not int or minutes <= 0:
        raise ValueError("INVALID_HYPOTHETICAL_VIDEO_MINUTES")
    return (minutes * 60 * SAMPLE_RATE_HZ + HOP_SAMPLES - 1) // HOP_SAMPLES


def gib(n: int) -> str:
    return str((Decimal(n) / Decimal(2 ** 30)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def stage_scenario(video_minutes: int, archives: tuple[Archive, ...] = ARCHIVES) -> dict:
    validate_archives(archives)
    frames_per_video = hypothetical_video_frames(video_minutes)
    retained = 0
    rows = []
    phases = []
    for a in archives:
        # WAV header duration is source metadata, not actual CQT F_i.
        # The 98 video captures' duration is a purely hypothetical per-file value.
        this_prepared = (a.nominal_wav_frames + a.video_accepted * frames_per_video) * FEATURE_AND_LABEL_BYTES_PER_FRAME
        extract = retained + a.compressed + a.extracted_visible
        end_prep = retained + a.extracted_visible + this_prepared
        after_cleanup = retained + this_prepared
        rows.append({
            "archive": a.name,
            "historicalInventoryJobId": a.job_id,
            "previouslyRetainedNominalPreparedBytes": retained,
            "currentNominalPreparedPayloadBytes": this_prepared,
            "atZipAndExtractionLogicalBytes": extract,
            "atEndOfPreparationLogicalBytes": end_prep,
            "afterArchiveCleanupLogicalBytes": after_cleanup,
            "wavHeaderAcceptedCount": a.wav_accepted,
            "hypotheticalMp3VideoCaptureCount": a.video_accepted,
        })
        phases.extend(((extract, a.name, "zipAndExtraction"),
                       (end_prep, a.name, "endOfPreparation"),
                       (after_cleanup, a.name, "afterArchiveCleanup")))
        retained = after_cleanup
    largest = max(phases, key=lambda x: x[0])
    return {
        "hypotheticalVideoMinutesPerAcceptedMp3Capture": video_minutes,
        "nominalWavFrameProxyFromHistoricalHeaders": NOMINAL_WAV_FRAMES,
        "hypotheticalMp3FrameProxy": frames_per_video * ACCEPTED_VIDEO_MP3_NO_DURATIONS,
        "conditionalTotalNominalPreparedPayloadBytes": retained,
        "conditionalTotalNominalPreparedPayloadGiB": gib(retained),
        "maxIdentifiableStageLogicalBytes": largest[0],
        "maxIdentifiableStageLogicalGiB": gib(largest[0]),
        "maxIdentifiableStageArchive": largest[1],
        "maxIdentifiableStageName": largest[2],
        "perArchive": rows,
        "actualPeakFilesystemBytes": None,
        "availableRunnerDiskBytes": None,
        "completePeakBoundEstablished": False,
        "scenarioOnly": True,
    }


def receipt() -> dict:
    validate_archives()
    scenarios = [stage_scenario(v) for v in (1, 2, 5, 10, 15)]
    return {
        "schema": "astra-h1-offline-historical-stage-disk-ledger-v1",
        "historicalInventoryRunId": HISTORIC_INVENTORY_RUN_ID,
        "historicalInventoryRecoveredReceiptGitBlob": HISTORICAL_LOG_RECEIPT_GIT_BLOB,
        "dormantWorkflowGitBlob": WORKFLOW_GIT_BLOB,
        "population": {"acceptedTotal": ACCEPTED_CAPTURES, "wavHeaderDurations": ACCEPTED_WAV_HEADERS,
                       "mp3VideoDurationsAbsent": ACCEPTED_VIDEO_MP3_NO_DURATIONS},
        "historicalLogicalCompressedSumBytes": COMPRESSED_SUM,
        "historicalLogicalExtractedSumBytes": EXTRACTED_VISIBLE_LOGICAL_SUM,
        "assumptions": [
            "All WAV CQT frames are NOMINAL approximations from historic WAV headers; real prepared frames were not logged.",
            "Each of 98 MP3/video source durations is an explicitly hypothetical uniform number of minutes.",
            "Extraction logical bytes are historical per-archive stat().st_size sums from separate 2026-09-21 jobs.",
            "Workflow order is frozen; ZIP removed before preparing current archive; extracted archive removed after preparation.",
            "Only prepared array payload is modeled (780 bytes per nominal frame); no NPY headers, manifests or filesystem overhead.",
            "Other concurrent resources, package/source/cache bytes, OS and disk reserves, runner capacity and failures are excluded.",
            "No hypothetical stage value is a measured physical disk peak or a provable resource upper bound.",
        ],
        "scenarios": scenarios,
        "runtimeMinutesFeasibility": "UNPROVEN",
        "diskFeasibility": "UNPROVEN",
        "ramFeasibility": "UNPROVEN",
        "launchPermission": False,
        "trainingExecuted": False,
        "mediaAcquired": False,
        "readiness": "NO_GO_INSUFFICIENT_EVIDENCE",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video-minutes", type=int, help="Show one conditional scenario (not a measured video duration)")
    args = parser.parse_args()
    if args.video_minutes is not None:
        output = stage_scenario(args.video_minutes)
    else:
        output = receipt()
    print(json.dumps(output, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
