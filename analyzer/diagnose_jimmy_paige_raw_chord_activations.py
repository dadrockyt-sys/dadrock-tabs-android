from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_full_song_deployed_winner_test import _build_audio_only_wav
from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

app = modal.App("dadrock-jimmy-paige-raw-chord-activation-diagnosis")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-raw-chord-activation-diagnosis.json"
)
LOG_PATH = REPO_ROOT / "jimmy-paige-raw-chord-activation-heartbeat.log"

WINNING_PARAMETERS = {
    "onset_threshold": 0.28,
    "frame_threshold": 0.12,
    "minimum_note_length": 35.0,
    "minimum_frequency": 82.0,
    "maximum_frequency": 1400.0,
    "multiple_pitch_bends": True,
}

TARGET_MIDI = list(range(55, 65))
TARGET_DOUBLE_STOP = [58, 62]


def _log(message: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S %Z')} | {message}"
    print(line, flush=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


@app.function(image=image, timeout=1200, memory=4096)
def inspect_raw_activations(
    audio_bytes: bytes,
    measure_bounds: dict[str, list[float]],
) -> bytes:
    import numpy as np
    from basic_pitch.constants import AUDIO_SAMPLE_RATE, FFT_HOP
    from basic_pitch.inference import predict

    started = time.time()
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as handle:
        audio_path = Path(handle.name)
        handle.write(audio_bytes)

    try:
        model_output, _, note_events = predict(
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

        reports: list[dict[str, Any]] = []
        for measure_text, bounds in sorted(
            measure_bounds.items(),
            key=lambda item: int(item[0]),
        ):
            measure = int(measure_text)
            start_seconds = float(bounds[0])
            end_seconds = float(bounds[1])
            frame_start = max(0, int(start_seconds / seconds_per_frame))
            frame_end = min(
                int(note_matrix.shape[0]),
                max(frame_start + 1, int(end_seconds / seconds_per_frame)),
            )

            pitch_rows: dict[str, Any] = {}
            for midi_pitch in TARGET_MIDI:
                column = midi_pitch - midi_base
                if column < 0 or column >= note_matrix.shape[1]:
                    continue
                note_values = note_matrix[frame_start:frame_end, column]
                onset_values = onset_matrix[frame_start:frame_end, column]
                if note_values.size == 0:
                    continue

                strongest_local = np.argsort(note_values)[-5:][::-1]
                pitch_rows[str(midi_pitch)] = {
                    "noteMaximum": round(float(np.max(note_values)), 6),
                    "noteMean": round(float(np.mean(note_values)), 6),
                    "noteFramesAbove012": int(np.sum(note_values >= 0.12)),
                    "noteFramesAbove008": int(np.sum(note_values >= 0.08)),
                    "onsetMaximum": round(float(np.max(onset_values)), 6),
                    "onsetFramesAbove028": int(np.sum(onset_values >= 0.28)),
                    "onsetFramesAbove020": int(np.sum(onset_values >= 0.20)),
                    "strongestFrameSeconds": [
                        round(
                            float((frame_start + int(index)) * seconds_per_frame),
                            6,
                        )
                        for index in strongest_local
                    ],
                }

            pitch58 = pitch_rows.get("58", {})
            pitch62 = pitch_rows.get("62", {})
            reports.append(
                {
                    "measureNumber": measure,
                    "expectedDoubleStop": measure % 2 == 0,
                    "startSeconds": start_seconds,
                    "endSeconds": end_seconds,
                    "frameStart": frame_start,
                    "frameEnd": frame_end,
                    "pitchActivations": pitch_rows,
                    "targetSummary": {
                        "midi58Maximum": pitch58.get("noteMaximum", 0.0),
                        "midi62Maximum": pitch62.get("noteMaximum", 0.0),
                        "midi58FramesAbove008": pitch58.get(
                            "noteFramesAbove008",
                            0,
                        ),
                        "midi62FramesAbove008": pitch62.get(
                            "noteFramesAbove008",
                            0,
                        ),
                        "bothTargetsHaveSubthresholdEvidence": bool(
                            pitch58.get("noteMaximum", 0.0) >= 0.04
                            and pitch62.get("noteMaximum", 0.0) >= 0.04
                        ),
                    },
                }
            )

        return json.dumps(
            {
                "benchmarkVersion": 1,
                "benchmarkType": "raw-frame-chord-activation-diagnosis",
                "winningParameters": WINNING_PARAMETERS,
                "noteMatrixShape": list(note_matrix.shape),
                "onsetMatrixShape": list(onset_matrix.shape),
                "secondsPerFrame": seconds_per_frame,
                "targetMidiPitches": TARGET_DOUBLE_STOP,
                "neighborMidiRange": TARGET_MIDI,
                "noteEventCount": len(note_events),
                "measureReports": reports,
                "remoteElapsedSeconds": round(time.time() - started, 3),
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
    heartbeat = max(5, int(os.getenv("JIMMY_HEARTBEAT_SECONDS", "15")))
    total_timeout = max(60, int(os.getenv("JIMMY_TOTAL_TIMEOUT_SECONDS", "1200")))

    LOG_PATH.write_text("", encoding="utf-8")
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)
    serialized_bounds = {
        str(measure): [float(start), float(end)]
        for measure, (start, end) in bounds.items()
        if 1 <= int(measure) <= 16
    }
    audio_bytes = _build_audio_only_wav()

    call = inspect_raw_activations.spawn(audio_bytes, serialized_bounds)
    submitted = time.time()
    _log(f"Raw activation diagnosis submitted | callId={call.object_id}")

    while True:
        elapsed = time.time() - submitted
        if elapsed >= total_timeout:
            try:
                call.cancel(terminate_containers=False)
            except Exception:
                pass
            raise TimeoutError("Raw activation diagnosis exceeded total timeout")

        try:
            report = json.loads(call.get(timeout=0).decode("utf-8"))
            break
        except TimeoutError:
            _log(
                f"[raw-activation heartbeat] elapsed={elapsed:.1f}s | "
                f"callId={call.object_id}"
            )
            time.sleep(heartbeat)

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Raw chord activation diagnosis complete")
    for row in report["measureReports"]:
        if row["measureNumber"] in {2, 4, 6, 8, 10, 12, 14, 16}:
            summary = row["targetSummary"]
            print(
                f"Measure {row['measureNumber']:>2} | "
                f"MIDI58 max={summary['midi58Maximum']:.4f} "
                f"frames>=.08={summary['midi58FramesAbove008']} | "
                f"MIDI62 max={summary['midi62Maximum']:.4f} "
                f"frames>=.08={summary['midi62FramesAbove008']} | "
                f"subthresholdPair={summary['bothTargetsHaveSubthresholdEvidence']}"
            )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
