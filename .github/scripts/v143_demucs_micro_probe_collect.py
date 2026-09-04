from __future__ import annotations

import json
import os
import statistics
from pathlib import Path

import modal


AUDIO_URL = os.environ["AUDIO_URL"]
AUDIO_BLOB_SHA = os.environ["AUDIO_BLOB_SHA"]
CLIP_SECONDS = 6.0
PROMOTION_SPEEDUP_THRESHOLD = 1.25


def mean_elapsed(rows: list[dict]) -> float:
    return statistics.fmean(float(row["elapsedSeconds"]) for row in rows)


def main() -> None:
    fn = modal.Function.from_name(
        "dadrock-v143-demucs-perf-probe",
        "run_cpu_policy_once",
        environment_name="main",
    )

    planned = [
        ("frozen-1", "frozen"),
        ("frozen-2", "frozen"),
        ("threads4-1", "threads4"),
        ("threads4-2", "threads4"),
    ]

    calls = [
        (label, policy, fn.spawn(AUDIO_URL, policy, CLIP_SECONDS))
        for label, policy in planned
    ]

    runs: list[dict] = []
    for label, policy, call in calls:
        result = call.get()
        if not isinstance(result, dict):
            raise RuntimeError(f"{label} returned a non-dict aggregate")
        if result.get("policy") != policy:
            raise RuntimeError(f"{label} returned unexpected policy metadata")
        if float(result.get("clipSeconds") or 0) != CLIP_SECONDS:
            raise RuntimeError(f"{label} returned unexpected clip duration")
        if result.get("referenceFacingAccuracyScored") is not False:
            raise RuntimeError(f"{label} violated reference-scoring boundary")
        if result.get("referenceScoreCalls") != 0:
            raise RuntimeError(f"{label} reported reference score calls")
        if result.get("rawAudioRetained") is not False:
            raise RuntimeError(f"{label} retained raw audio")
        if result.get("stemBytesRetained") is not False:
            raise RuntimeError(f"{label} retained stem bytes")
        runs.append(
            {
                "label": label,
                "policy": policy,
                "functionCallId": call.object_id,
                "elapsedSeconds": float(result["elapsedSeconds"]),
                "wallSeconds": float(result["wallSeconds"]),
                "sha256": str(result["sha256"]),
                "bytes": int(result["bytes"]),
            }
        )

    frozen = [row for row in runs if row["policy"] == "frozen"]
    candidate = [row for row in runs if row["policy"] == "threads4"]
    frozen_hashes = {row["sha256"] for row in frozen}
    candidate_hashes = {row["sha256"] for row in candidate}
    frozen_repeatable = len(frozen_hashes) == 1
    candidate_repeatable = len(candidate_hashes) == 1
    exact_baseline_parity = (
        frozen_repeatable
        and candidate_repeatable
        and next(iter(frozen_hashes)) == next(iter(candidate_hashes))
    )
    frozen_mean = mean_elapsed(frozen)
    candidate_mean = mean_elapsed(candidate)
    speedup = frozen_mean / candidate_mean if candidate_mean > 0 else None

    summary = {
        "schemaVersion": 1,
        "gate": "v143-demucs-cpu-policy-micro-probe",
        "diagnosticSourceCommit": os.environ.get("GITHUB_SHA"),
        "audioBlobSha": AUDIO_BLOB_SHA,
        "clipSeconds": CLIP_SECONDS,
        "model": "htdemucs_6s.yaml",
        "singleStem": "Guitar",
        "demucsShifts": 1,
        "demucsOverlap": 0.10,
        "demucsSegmentSize": 6,
        "separatorSeed": 143,
        "device": "cpu",
        "runs": runs,
        "frozenRepeatable": frozen_repeatable,
        "candidateRepeatable": candidate_repeatable,
        "exactBaselineParity": exact_baseline_parity,
        "frozenMeanSeconds": round(frozen_mean, 3),
        "candidateMeanSeconds": round(candidate_mean, 3),
        "speedup": None if speedup is None else round(speedup, 3),
        "promotionSpeedupThreshold": PROMOTION_SPEEDUP_THRESHOLD,
        "promotionEligible": bool(
            exact_baseline_parity
            and speedup is not None
            and speedup >= PROMOTION_SPEEDUP_THRESHOLD
        ),
        "referenceFree": True,
        "referenceFacingAccuracyScored": False,
        "referenceScoreCalls": 0,
        "rawAudioRetained": False,
        "stemBytesRetained": False,
        "productionWorkerChanged": False,
        "productionBridgeChanged": False,
        "vercelChanged": False,
    }

    out = Path("debug/v143-contextual-prune/demucs-cpu-policy-micro-probe")
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))

    if not frozen_repeatable:
        raise SystemExit("Frozen 6-second baseline was not byte-repeatable")
    if not candidate_repeatable:
        raise SystemExit("CPU4 6-second candidate was not byte-repeatable")


if __name__ == "__main__":
    main()
