#!/usr/bin/env python3

import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import math
import os
import platform
import subprocess
import tempfile
from pathlib import Path

CONTRACT = "songsterr-fresh-demucs-cross-run-provenance-v1"
EXPECTED_INPUT_SHA256 = "e03e1885185f4983b3eeaa66f36510b7709d607c14010f964e0aad427ecc474a"
EXPECTED_MODEL_ASSET = {
    "contract": "songsterr-fresh-demucs-model-asset-v2",
    "primaryLoader": "huggingface",
    "hfRepoId": "adefossez/HTDemucs-6s",
    "hfPinnedRevision": "3c5ee475be622df764938de97e4281a7b07ffa58",
    "hfAssetUploadRevision": "053e1404489b3dc58bf718224fac4b7316de8c93",
    "assetFilename": "5c90dfd2.safetensors",
    "assetSha256": "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411",
}
PACKAGE_NAMES = (
    "numpy",
    "torch",
    "huggingface-hub",
    "safetensors",
    "sphn",
    "demucs",
    "soundfile",
)
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "PYTHONHASHSEED",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Record one already-produced fixed Demucs guitar stem plus hosted-runner provenance "
            "for cross-run reproducibility diagnosis. This tool is reference-blind and does not "
            "select a preferred stem or alter downstream evidence."
        )
    )
    parser.add_argument("--stem", help="already-produced Demucs guitar stem WAV")
    parser.add_argument("--input-sha256", help="verified decoded separation-input SHA-256")
    parser.add_argument("--model-asset", help="verified Demucs model-asset JSON")
    parser.add_argument("--sample-label", help="stable label for this independent hosted job")
    parser.add_argument("--output", help="output provenance JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all(
        (args.stem, args.input_sha256, args.model_asset, args.sample_label, args.output)
    ):
        parser.error(
            "--stem, --input-sha256, --model-asset, --sample-label, and --output are required "
            "unless --self-test is used"
        )
    return args


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def command_text(argv):
    try:
        return subprocess.check_output(argv, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as exc:
        return f"UNAVAILABLE:{type(exc).__name__}:{exc}"


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_model_asset(asset):
    for key, expected in EXPECTED_MODEL_ASSET.items():
        require(asset.get(key) == expected, f"DEMUCS_CROSS_RUN_MODEL_ASSET_CHANGED:{key}")
    require(
        asset.get("legacyFallback", {}).get("primary") is False,
        "DEMUCS_CROSS_RUN_LEGACY_FALLBACK_PRIMARY",
    )


def first_cpu_model():
    cpuinfo = Path("/proc/cpuinfo")
    if not cpuinfo.is_file():
        return None
    for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lower().startswith("model name") and ":" in line:
            return line.split(":", 1)[1].strip()
    return None


def numpy_config_text(np):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        np.show_config()
    return stream.getvalue().strip()


def torch_cpu_capability(torch):
    try:
        return torch.backends.cpu.get_cpu_capability()
    except Exception as exc:
        return f"UNAVAILABLE:{type(exc).__name__}:{exc}"


def build_payload(stem_path, input_sha256, model_asset, sample_label):
    import numpy as np
    import soundfile as sf
    import torch

    stem_path = Path(stem_path)
    require(stem_path.is_file(), "DEMUCS_CROSS_RUN_STEM_MISSING")
    require(
        input_sha256.lower() == EXPECTED_INPUT_SHA256,
        "DEMUCS_CROSS_RUN_INPUT_SHA_CHANGED",
    )
    validate_model_asset(model_asset)
    require(sample_label.strip(), "DEMUCS_CROSS_RUN_SAMPLE_LABEL_EMPTY")

    pcm, sample_rate = sf.read(stem_path, always_2d=True, dtype="float32")
    require(pcm.size > 0, "DEMUCS_CROSS_RUN_EMPTY_PCM")
    require(np.all(np.isfinite(pcm)), "DEMUCS_CROSS_RUN_NONFINITE_PCM")
    contiguous_pcm = np.ascontiguousarray(pcm)
    pcm_sha256 = hashlib.sha256(contiguous_pcm.tobytes()).hexdigest()
    stem_rms = float(math.sqrt(float(np.mean(contiguous_pcm.astype(np.float64) ** 2))))

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "sampleLabel": sample_label,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "scope": "independent-hosted-run-single-fixed-demucs-pass",
        "source": {
            "sourceAudioGitBlobSha": "4dd709e3fa177b4daeed71ca97f0199757729d4b",
            "decodedSeparationWavSha256": input_sha256.lower(),
            "stemFileSha256": sha256_file(stem_path),
            "stemPcmSha256": pcm_sha256,
            "sampleRate": int(sample_rate),
            "shape": [int(v) for v in contiguous_pcm.shape],
            "totalPcmValues": int(contiguous_pcm.size),
            "stemRms": stem_rms,
        },
        "demucs": {
            "package": "demucs",
            "packageVersion": importlib.metadata.version("demucs"),
            "model": "htdemucs_6s",
            "device": "cpu",
            "shifts": 0,
            "overlap": 0.25,
            "segmentSeconds": 7,
            "stem": "guitar",
            "modelAsset": dict(EXPECTED_MODEL_ASSET),
        },
        "runtime": {
            "python": platform.python_version(),
            "pythonBuild": list(platform.python_build()),
            "platform": platform.platform(),
            "uname": list(platform.uname()),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "libc": list(platform.libc_ver()),
            "cpuModel": first_cpu_model(),
            "lscpu": command_text(["lscpu"]),
            "runnerOS": os.environ.get("RUNNER_OS"),
            "runnerArch": os.environ.get("RUNNER_ARCH"),
            "runnerName": os.environ.get("RUNNER_NAME"),
            "imageOS": os.environ.get("ImageOS"),
            "imageVersion": os.environ.get("ImageVersion"),
            "githubRunId": os.environ.get("GITHUB_RUN_ID"),
            "githubRunAttempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "githubJob": os.environ.get("GITHUB_JOB"),
            "githubSha": os.environ.get("GITHUB_SHA"),
            "ffmpegVersion": command_text(["ffmpeg", "-version"]).splitlines()[0],
            "packages": {
                name: importlib.metadata.version(name)
                for name in PACKAGE_NAMES
            },
            "numpyConfig": numpy_config_text(np),
            "torch": {
                "version": torch.__version__,
                "numThreads": torch.get_num_threads(),
                "numInteropThreads": torch.get_num_interop_threads(),
                "cpuCapability": torch_cpu_capability(torch),
                "mkldnnEnabled": bool(torch.backends.mkldnn.enabled),
                "mklAvailable": bool(torch.backends.mkl.is_available()),
                "openmpAvailable": bool(torch.backends.openmp.is_available()),
                "cudaAvailable": bool(torch.cuda.is_available()),
                "config": torch.__config__.show(),
            },
            "threadingEnvironment": {
                key: os.environ.get(key)
                for key in THREAD_ENV_KEYS
            },
        },
        "hardGuards": {
            "basicPitchInvoked": False,
            "releaseEvidenceInvoked": False,
            "preferredStemSelection": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "thresholdSelection": False,
            "thresholdSweep": False,
            "downstreamAgreementObjective": False,
            "acceptanceDecision": False,
            "customerDeliveryInvoked": False,
            "legacyV143ScorerImported": False,
            "professionalScorerUsed": False,
            "referenceTabUsed": False,
        },
    }
    return payload


def self_test():
    import numpy as np
    import soundfile as sf

    asset = dict(EXPECTED_MODEL_ASSET)
    asset["legacyFallback"] = {"primary": False}
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "stem.wav"
        samples = np.linspace(-0.25, 0.25, 4096, dtype=np.float32).reshape(-1, 1)
        sf.write(stem, samples, 22050, subtype="FLOAT")
        payload = build_payload(stem, EXPECTED_INPUT_SHA256, asset, "self-test")
        require(payload["referenceBlind"] is True, "DEMUCS_CROSS_RUN_SELF_TEST_REFERENCE_BLIND")
        require(payload["diagnosticOnly"] is True, "DEMUCS_CROSS_RUN_SELF_TEST_DIAGNOSTIC")
        require(payload["source"]["totalPcmValues"] == 4096, "DEMUCS_CROSS_RUN_SELF_TEST_PCM")
        require(
            all(value is False for value in payload["hardGuards"].values()),
            "DEMUCS_CROSS_RUN_SELF_TEST_GUARDS",
        )
        broken = dict(asset)
        broken["assetSha256"] = "0" * 64
        try:
            build_payload(stem, EXPECTED_INPUT_SHA256, broken, "broken")
        except RuntimeError as exc:
            require("MODEL_ASSET_CHANGED" in str(exc), "DEMUCS_CROSS_RUN_SELF_TEST_ASSET_ERROR")
        else:
            raise RuntimeError("DEMUCS_CROSS_RUN_SELF_TEST_ASSET_FAIL_OPEN")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "referenceBlind": True,
        "diagnosticOnly": True,
        "preferredStemSelection": False,
        "thresholdSweep": False,
        "acceptanceDecision": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    payload = build_payload(
        args.stem,
        args.input_sha256,
        load_json(args.model_asset),
        args.sample_label,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": payload["contract"],
        "sampleLabel": payload["sampleLabel"],
        "stemFileSha256": payload["source"]["stemFileSha256"],
        "stemPcmSha256": payload["source"]["stemPcmSha256"],
        "cpuModel": payload["runtime"]["cpuModel"],
        "imageVersion": payload["runtime"]["imageVersion"],
        "torchCpuCapability": payload["runtime"]["torch"]["cpuCapability"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
