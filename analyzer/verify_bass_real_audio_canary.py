from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


MIN_DURATION_SECONDS = 10.0
MIN_SAMPLE_RATE = 16000
MIN_RMS = 0.0001
MIN_PEAK = 0.001
MIN_BASS_BAND_PERCENT = 5.0
MIN_ACTIVE_PITCH_FRAMES = 10
PLAYABLE_BASS_MIN_HZ = 41.203445
PLAYABLE_BASS_MAX_HZ = 391.995436


def _view_checks(view: dict[str, Any]) -> dict[str, bool]:
    median = view.get("medianFundamentalHz")
    return {
        "nonEmptyFile": int(view.get("bytes") or 0) > 0,
        "sampleRate": int(view.get("sampleRate") or 0) >= MIN_SAMPLE_RATE,
        "channels": int(view.get("channels") or 0) in {1, 2},
        "duration": float(view.get("durationSeconds") or 0.0) >= MIN_DURATION_SECONDS,
        "rms": float(view.get("rms") or 0.0) >= MIN_RMS,
        "peak": float(view.get("peak") or 0.0) >= MIN_PEAK,
        "bassBandEnergy": float(view.get("bassBand30To1000HzPercent") or 0.0)
        >= MIN_BASS_BAND_PERCENT,
        "activePitchFrames": int(view.get("activePitchFrameCount") or 0)
        >= MIN_ACTIVE_PITCH_FRAMES,
        "medianFundamentalPlayable": median is not None
        and PLAYABLE_BASS_MIN_HZ <= float(median) <= PLAYABLE_BASS_MAX_HZ,
        "playablePitchRange": float(view.get("playableRangeFramePercent") or 0.0)
        >= 99.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    raw_path = Path(args.input)
    output_path = Path(args.output)
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    views = dict(raw.get("views") or {})
    direct = dict(views.get("direct") or {})
    cascade = dict(views.get("cascade") or {})
    direct_checks = _view_checks(direct)
    cascade_checks = _view_checks(cascade)

    separator = dict(raw.get("separator") or {})
    settings = dict(separator.get("settings") or {})
    safety_checks = {
        "approvedFixture": raw.get("approvedFixture")
        == "public/gomywayfullaitest.m4a",
        "referenceFree": raw.get("referenceFree") is True,
        "diagnosticOnly": raw.get("diagnosticOnly") is True,
        "demucsBassStem": settings.get("demucsSingleStem") == "Bass",
        "deterministicSeed": settings.get("deterministicSeed") == 143,
        "trainingDisabled": raw.get("trainingRunAuthorized") is False,
        "routingDisabled": raw.get("analyzerRoutingEnabled") is False,
        "structuredIdentityDisabled": raw.get("professionalStructuredIdentityEnabled")
        is False,
        "pdfDisabled": raw.get("pdfRendererEnabled") is False,
        "noteTimingTechniqueNotClaimed": raw.get("noteTimingTechniqueQualityProven")
        is False,
        "liveEndpointUnchanged": raw.get("liveEndpointDeployedOrModified") is False,
        "vercelNotAttempted": raw.get("vercelDeploymentAttempted") is False,
        "productionUnchanged": raw.get("productionModified") is False,
        "promotionDisabled": raw.get("productionPromotionAuthorized") is False,
        "purchaseNotAttempted": raw.get("paidPurchaseAttempted") is False,
        "tokenNotRedeemed": raw.get("customerTokenRedeemed") is False,
        "emailNotSent": raw.get("customerEmailSent") is False,
    }

    real_audio_separation_passed = all(
        direct_checks[key] and cascade_checks[key]
        for key in (
            "nonEmptyFile",
            "sampleRate",
            "channels",
            "duration",
            "rms",
            "peak",
            "bassBandEnergy",
        )
    )
    pitch_evidence_passed = all(
        direct_checks[key] and cascade_checks[key]
        for key in (
            "activePitchFrames",
            "medianFundamentalPlayable",
            "playablePitchRange",
        )
    )
    passed = (
        real_audio_separation_passed
        and pitch_evidence_passed
        and all(safety_checks.values())
    )

    evidence = {
        "schemaVersion": 1,
        "gate": "bass-real-audio-separation-pitch-canary",
        "approvedFixture": raw.get("approvedFixture"),
        "sourceSha256": raw.get("sourceSha256"),
        "sourceBytes": raw.get("sourceBytes"),
        "separator": separator,
        "thresholds": {
            "minimumDurationSeconds": MIN_DURATION_SECONDS,
            "minimumSampleRate": MIN_SAMPLE_RATE,
            "minimumRms": MIN_RMS,
            "minimumPeak": MIN_PEAK,
            "minimumBassBand30To1000HzPercent": MIN_BASS_BAND_PERCENT,
            "minimumActivePitchFrames": MIN_ACTIVE_PITCH_FRAMES,
            "playableBassMinimumHz": PLAYABLE_BASS_MIN_HZ,
            "playableBassMaximumHz": PLAYABLE_BASS_MAX_HZ,
        },
        "views": {
            "direct": {"metrics": direct, "checks": direct_checks},
            "cascade": {"metrics": cascade, "checks": cascade_checks},
        },
        "stemsDistinct": bool(
            direct.get("sha256")
            and cascade.get("sha256")
            and direct.get("sha256") != cascade.get("sha256")
        ),
        "safetyChecks": safety_checks,
        "realAudioBassSeparationPassed": real_audio_separation_passed,
        "realAudioBassPitchEvidencePassed": pitch_evidence_passed,
        "realAudioBassCanaryPassed": passed,
        "noteTimingTechniqueQualityProven": False,
        "professionalQualityGateSatisfied": False,
        "trainingRunAuthorized": False,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
        "pdfRendererEnabled": False,
        "liveEndpointDeployedOrModified": False,
        "vercelDeploymentAttempted": False,
        "productionModified": False,
        "productionPromotionAuthorized": False,
        "paidPurchaseAttempted": False,
        "customerTokenRedeemed": False,
        "customerEmailSent": False,
        "passed": passed,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
