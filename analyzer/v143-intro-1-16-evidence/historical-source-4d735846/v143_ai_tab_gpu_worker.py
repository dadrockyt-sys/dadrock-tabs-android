from __future__ import annotations

import json
import subprocess
import sys

import modal


app = modal.App("dadrock-v143-ai-tab-gpu-worker")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "audio-separator[gpu]==0.44.5",
    )
)


@app.function(
    image=image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def gpu_smoke() -> dict:
    import torch
    import onnxruntime as ort

    env = subprocess.run(
        ["audio-separator", "--env_info"],
        capture_output=True,
        text=True,
        check=False,
    )

    cuda_available = bool(torch.cuda.is_available())
    providers = list(ort.get_available_providers())

    result = {
        "cudaAvailable": cuda_available,
        "torchVersion": str(torch.__version__),
        "torchCudaVersion": None if torch.version.cuda is None else str(torch.version.cuda),
        "deviceCount": torch.cuda.device_count(),
        "deviceName": (
            torch.cuda.get_device_name(0)
            if cuda_available
            else None
        ),
        "onnxProviders": providers,
        "audioSeparatorExitCode": env.returncode,
        "audioSeparatorEnvInfo": env.stdout + env.stderr,
    }

    if not cuda_available:
        raise RuntimeError(
            "Modal GPU exists but PyTorch CUDA is unavailable:\n"
            + json.dumps(result, indent=2)
        )

    if "CUDAExecutionProvider" not in providers:
        raise RuntimeError(
            "ONNX Runtime CUDA provider unavailable:\n"
            + json.dumps(result, indent=2)
        )

    return result

@app.function(
    image=image,
    gpu="L4",
    timeout=1200,
    memory=8192,
)
def direct_replay(
    source_audio: bytes,
    historical_guitar: bytes,
) -> dict:
    import hashlib
    import subprocess
    import tempfile
    import time
    from pathlib import Path

    import numpy as np
    import soundfile as sf
    import torch

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable in Modal worker")

    started = time.monotonic()

    with tempfile.TemporaryDirectory(
        prefix="v143-direct-replay-"
    ) as tmp:
        root = Path(tmp)

        source = root / "input.m4a"
        normalized = root / "input-normalized.wav"
        historical = root / "historical-direct.wav"
        output_dir = root / "output"

        output_dir.mkdir(parents=True)

        source.write_bytes(source_audio)
        historical.write_bytes(historical_guitar)

        # Exact production compatibility decode established
        # during the Codespace separator investigation.
        ffmpeg = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-vn",
                "-c:a",
                "pcm_s16le",
                str(normalized),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if ffmpeg.returncode != 0:
            raise RuntimeError(
                "FFmpeg normalization failed:\n"
                + ffmpeg.stderr[-4000:]
            )

        separation_started = time.monotonic()

        command = [
            sys.executable,
            "-c",
            "import os,random; random.seed(int(os.environ.get('JIMMY_SEPARATOR_SEED','143'))); from audio_separator.utils.cli import main; raise SystemExit(main())",
            str(source),
            "--model_filename",
            "htdemucs_6s.yaml",
            "--output_dir",
            str(output_dir),
            "--output_format",
            "WAV",
            "--single_stem",
            "Guitar",
            "--demucs_shifts",
            "1",
            "--demucs_overlap",
            "0.10",
            "--demucs_segment_size",
            "6",
            "--use_soundfile",
        ]

        run = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        separation_seconds = (
            time.monotonic() - separation_started
        )

        log = (run.stdout or "") + (run.stderr or "")

        if run.returncode != 0:
            raise RuntimeError(
                "Modal Demucs separation failed "
                f"with code {run.returncode}:\n"
                + "\n".join(log.splitlines()[-60:])
            )

        candidates = sorted(
            output_dir.glob("*.wav")
        )

        guitar_candidates = [
            path
            for path in candidates
            if "guitar" in path.name.lower()
        ]

        if not guitar_candidates:
            raise RuntimeError(
                "No Guitar WAV produced. Files: "
                + repr([p.name for p in candidates])
            )

        generated = guitar_candidates[0]

        a, sr_a = sf.read(
            generated,
            always_2d=True,
            dtype="float64",
        )

        b, sr_b = sf.read(
            historical,
            always_2d=True,
            dtype="float64",
        )

        if int(sr_a) != int(sr_b):
            raise RuntimeError(
                f"Sample-rate mismatch: {sr_a} != {sr_b}"
            )

        # Historical V143 replay comparison is mono,
        # matching our existing local replay harness.
        a = np.mean(a, axis=1)
        b = np.mean(b, axis=1)

        generated_samples = len(a)
        historical_samples = len(b)

        n = min(
            generated_samples,
            historical_samples,
        )

        if n == 0:
            raise RuntimeError("Empty separator output")

        aa = a[:n]
        bb = b[:n]

        diff = aa - bb

        rmse = float(
            np.sqrt(
                np.mean(diff * diff)
            )
        )

        peak_error = float(
            np.max(np.abs(diff))
        )

        denom = float(
            np.linalg.norm(aa)
            * np.linalg.norm(bb)
        )

        correlation = (
            float(np.dot(aa, bb) / denom)
            if denom > 0.0
            else 0.0
        )

        exact_samples = bool(
            generated_samples == historical_samples
            and np.array_equal(aa, bb)
        )

        replay_passed = bool(
            exact_samples
            or (
                correlation >= 0.99999
                and rmse <= 1e-5
            )
        )

        return {
            "cudaAvailable": True,
            "deviceName": str(
                torch.cuda.get_device_name(0)
            ),
            "sourceBytes": int(len(source_audio)),
            "normalizedBytes": int(
                normalized.stat().st_size
            ),
            "generatedBytes": int(
                generated.stat().st_size
            ),
            "sampleRate": int(sr_a),
            "generatedSamples": int(
                generated_samples
            ),
            "historicalSamples": int(
                historical_samples
            ),
            "exactDecodedSamples": exact_samples,
            "rmse": rmse,
            "peakAbsoluteError": peak_error,
            "correlation": correlation,
            "directReplayPassed": replay_passed,
            "separationSeconds": round(
                separation_seconds,
                3,
            ),
            "totalRemoteSeconds": round(
                time.monotonic() - started,
                3,
            ),
            "generatedSha256": hashlib.sha256(
                generated.read_bytes()
            ).hexdigest(),
            "generatedWavBytes": generated.read_bytes(),
            "historicalSha256": hashlib.sha256(
                historical_guitar
            ).hexdigest(),
            "separatorLogTail": "\n".join(
                log.splitlines()[-20:]
            ),
        }

@app.local_entrypoint()
def main(mode: str = "smoke"):
    import json
    from pathlib import Path

    if mode == "smoke":
        result = gpu_smoke.remote()

        print()
        print("=== V143 MODAL GPU SMOKE PASSED ===")
        print(json.dumps(result, indent=2))
        return

    if mode == "direct":
        source = Path(
            "public/gomywayfullaitest.m4a"
        )

        historical = Path(
            "public/separator-benchmark-v2/"
            "gomyway-demucs6s-direct-guitar.wav"
        )

        if not source.exists():
            raise RuntimeError(
                f"Source missing: {source}"
            )

        if not historical.exists():
            raise RuntimeError(
                f"Historical stem missing: {historical}"
            )

        source_bytes = source.read_bytes()
        historical_bytes = historical.read_bytes()

        total_mib = (
            len(source_bytes)
            + len(historical_bytes)
        ) / (1024 * 1024)

        print(
            "Replay upload payload MiB:",
            round(total_mib, 2),
        )

        if total_mib >= 95:
            raise RuntimeError(
                "Replay payload is too close to "
                "Modal's 100 MB payload limit."
            )

        print(
            "Starting full-song V143 direct "
            "Demucs6s replay on Modal L4..."
        )

        result = direct_replay.remote(
            source_bytes,
            historical_bytes,
        )

        generated_wav = result.pop("generatedWavBytes")
        export_path = Path(
            "public/v143-modal-replay/gomyway-modal-l4-direct-guitar.wav"
        )
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_bytes(generated_wav)

        print(
            "Saved Modal direct WAV:",
            export_path,
            f"({len(generated_wav):,} bytes)",
        )

        print()
        print(
            "=== V143 MODAL DIRECT REPLAY COMPLETE ==="
        )
        print(json.dumps(result, indent=2))
        return

    raise RuntimeError(
        f"Unknown mode: {mode!r}. "
        "Use smoke or direct."
    )
