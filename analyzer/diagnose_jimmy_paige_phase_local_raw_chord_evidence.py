from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-jimmy-paige-phase-local-raw-chord-evidence")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)

WINNING_PARAMETERS = {
    "onset_threshold": 0.28,
    "frame_threshold": 0.12,
    "minimum_note_length": 35.0,
    "minimum_frequency": 82.0,
    "maximum_frequency": 1400.0,
    "multiple_pitch_bends": True,
}

PHASE_WINDOWS = [
    (0.60, 1.00),
    (0.70, 1.00),
    (0.75, 1.05),
    (0.80, 1.10),
]

THRESHOLDS = [0.08, 0.10, 0.12, 0.14, 0.16]


@app.function(image=image, timeout=3600, memory=4096)
def inspect_phase_local_evidence(
    audio_bytes: bytes,
    measure_bounds: dict[str, list[float]],
) -> bytes:
    import numpy as np
    from basic_pitch.constants import AUDIO_SAMPLE_RATE, FFT_HOP
    from basic_pitch.inference import predict

    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        model_output, _, _ = predict(
            audio_path,
            onset_threshold=WINNING_PARAMETERS["onset_threshold"],
            frame_threshold=WINNING_PARAMETERS["frame_threshold"],
            minimum_note_length=WINNING_PARAMETERS["minimum_note_length"],
            minimum_frequency=WINNING_PARAMETERS["minimum_frequency"],
            maximum_frequency=WINNING_PARAMETERS["maximum_frequency"],
            multiple_pitch_bends=WINNING_PARAMETERS["multiple_pitch_bends"],
            melodia_trick=True,
        )

        note_matrix = np.asarray(model_output["note"])
        onset_matrix = np.asarray(model_output["onset"])
        seconds_per_frame = float(FFT_HOP) / float(AUDIO_SAMPLE_RATE)
        midi_base = 21
        col58 = 58 - midi_base
        col62 = 62 - midi_base

        reports: list[dict[str, Any]] = []

        for measure_text, raw_bounds in sorted(
            measure_bounds.items(), key=lambda item: int(item[0])
        ):
            measure = int(measure_text)
            start_seconds = float(raw_bounds[0])
            end_seconds = float(raw_bounds[1])
            duration = end_seconds - start_seconds
            phase_rows: list[dict[str, Any]] = []

            for phase_start, phase_end in PHASE_WINDOWS:
                region_start = start_seconds + duration * phase_start
                region_end = start_seconds + duration * phase_end
                frame_start = max(0, int(region_start / seconds_per_frame))
                frame_end = min(
                    note_matrix.shape[0],
                    max(frame_start + 1, int(region_end / seconds_per_frame)),
                )

                values58 = note_matrix[frame_start:frame_end, col58]
                values62 = note_matrix[frame_start:frame_end, col62]
                onsets58 = onset_matrix[frame_start:frame_end, col58]
                onsets62 = onset_matrix[frame_start:frame_end, col62]

                same_frame_min = np.minimum(values58, values62)
                same_frame_product = values58 * values62

                threshold_rows: dict[str, Any] = {}
                for threshold in THRESHOLDS:
                    threshold_rows[f"{threshold:.2f}"] = {
                        "sameFrameCount": int(
                            np.sum((values58 >= threshold) & (values62 >= threshold))
                        ),
                        "midi58Count": int(np.sum(values58 >= threshold)),
                        "midi62Count": int(np.sum(values62 >= threshold)),
                    }

                best_index = int(np.argmax(same_frame_min))
                phase_rows.append(
                    {
                        "phaseStart": phase_start,
                        "phaseEnd": phase_end,
                        "frameStart": frame_start,
                        "frameEnd": frame_end,
                        "sameFrameMinimumMaximum": round(
                            float(np.max(same_frame_min)), 6
                        ),
                        "sameFrameProductMaximum": round(
                            float(np.max(same_frame_product)), 6
                        ),
                        "bestCoactivationSeconds": round(
                            float((frame_start + best_index) * seconds_per_frame),
                            6,
                        ),
                        "midi58AtBestFrame": round(
                            float(values58[best_index]), 6
                        ),
                        "midi62AtBestFrame": round(
                            float(values62[best_index]), 6
                        ),
                        "midi58Maximum": round(float(np.max(values58)), 6),
                        "midi62Maximum": round(float(np.max(values62)), 6),
                        "midi58OnsetMaximum": round(float(np.max(onsets58)), 6),
                        "midi62OnsetMaximum": round(float(np.max(onsets62)), 6),
                        "thresholdEvidence": threshold_rows,
                    }
                )

            reports.append(
                {
                    "measureNumber": measure,
                    "expectedDoubleStop": measure % 2 == 0,
                    "measureStartSeconds": start_seconds,
                    "measureEndSeconds": end_seconds,
                    "phaseReports": phase_rows,
                }
            )

        return json.dumps(
            {
                "benchmarkVersion": 1,
                "benchmarkType": "phase-local-raw-chord-coactivation-diagnosis",
                "winningParameters": WINNING_PARAMETERS,
                "phaseWindows": PHASE_WINDOWS,
                "thresholds": THRESHOLDS,
                "secondsPerFrame": seconds_per_frame,
                "measureReports": reports,
                "professionalPdfRemainsScoringAuthority": True,
                "productionPromotionAllowed": False,
                "syntheticNotesAllowed": False,
                "protectedPitchCheckpointChanged": False,
            }
        ).encode("utf-8")
    finally:
        audio_path.unlink(missing_ok=True)


@app.local_entrypoint()
def main() -> None:
    from run_jimmy_paige_full_song_deployed_winner_test import _build_audio_only_wav
    from run_jimmy_paige_low_register_recovery_training_loop import (
        CALIBRATION_PATH,
        REPO_ROOT,
        _load_json,
        _measure_bounds,
    )

    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    total_timeout = max(60, int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "3600")))
    output_path = (
        REPO_ROOT
        / "public"
        / "gomyway-jimmy-paige-phase-local-raw-chord-evidence.json"
    )

    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)
    serialized_bounds = {
        str(measure): [float(start), float(end)]
        for measure, (start, end) in bounds.items()
        if 1 <= int(measure) <= 16
    }
    audio_bytes = _build_audio_only_wav()

    call = inspect_phase_local_evidence.spawn(audio_bytes, serialized_bounds)
    submitted = time.time()
    print(f"Phase-local raw chord diagnosis submitted | callId={call.object_id}")

    while True:
        elapsed = time.time() - submitted
        if elapsed >= total_timeout:
            try:
                call.cancel(terminate_containers=False)
            except Exception:
                pass
            raise TimeoutError("Phase-local raw chord diagnosis exceeded timeout")

        try:
            report = json.loads(call.get(timeout=0).decode("utf-8"))
            break
        except TimeoutError:
            print(
                f"[phase-local heartbeat] elapsed={elapsed:.1f}s | "
                f"callId={call.object_id}",
                flush=True,
            )
            time.sleep(heartbeat)

    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Phase-local raw chord evidence complete")
    for row in report["measureReports"]:
        selected = next(
            item
            for item in row["phaseReports"]
            if item["phaseStart"] == 0.70 and item["phaseEnd"] == 1.00
        )
        evidence = selected["thresholdEvidence"]["0.12"]
        print(
            f"Measure {row['measureNumber']:>2} | expected={row['expectedDoubleStop']} | "
            f"coactivationMax={selected['sameFrameMinimumMaximum']:.4f} | "
            f"sameFrames>=.12={evidence['sameFrameCount']} | "
            f"onset58={selected['midi58OnsetMaximum']:.4f} | "
            f"onset62={selected['midi62OnsetMaximum']:.4f}"
        )

    print(f"Output: {output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
