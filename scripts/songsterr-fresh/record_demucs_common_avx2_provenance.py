#!/usr/bin/env python3

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
from pathlib import Path

CONTRACT = "songsterr-fresh-demucs-common-avx2-provenance-v1"
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
HARD_GUARDS = {
    "preferredStemSelection": False,
    "basicPitchInvocation": False,
    "releaseEvidenceInvocation": False,
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
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Record one fixed Demucs stem produced under the common ATen+oneDNN AVX2 caps. "
            "This is reference-blind provenance for reproducibility diagnosis only."
        )
    )
    parser.add_argument("--stem", required=True)
    parser.add_argument("--input-sha256", required=True)
    parser.add_argument("--model-asset", required=True)
    parser.add_argument("--sample-label", required=True)
    parser.add_argument("--native-cpu-model", required=True)
    parser.add_argument("--native-cpu-vendor", required=True)
    parser.add_argument("--native-torch-capability", required=True)
    parser.add_argument("--onednn-isa-line", required=True)
    parser.add_argument("--azure-region", default="")
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def require(condition, code):
    if not condition:
        raise RuntimeError(code)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_model_asset(asset):
    for key, expected in EXPECTED_MODEL_ASSET.items():
        require(asset.get(key) == expected, f"DEMUCS_COMMON_AVX2_MODEL_ASSET_CHANGED:{key}")
    require(
        asset.get("legacyFallback", {}).get("primary") is False,
        "DEMUCS_COMMON_AVX2_LEGACY_FALLBACK_PRIMARY",
    )


def main():
    args = parse_args()
    import numpy as np
    import soundfile as sf
    import torch

    require(args.input_sha256.lower() == EXPECTED_INPUT_SHA256, "DEMUCS_COMMON_AVX2_INPUT_SHA_CHANGED")
    require(os.environ.get("ATEN_CPU_CAPABILITY") == "avx2", "DEMUCS_COMMON_AVX2_ATEN_CONTROL_MISSING")
    require(os.environ.get("ONEDNN_MAX_CPU_ISA") == "AVX2", "DEMUCS_COMMON_AVX2_ONEDNN_CONTROL_MISSING")
    require(torch.backends.cpu.get_cpu_capability() == "AVX2", "DEMUCS_COMMON_AVX2_ATEN_CAP_NOT_EFFECTIVE")
    require("AVX2" in args.onednn_isa_line.upper(), "DEMUCS_COMMON_AVX2_ONEDNN_CAP_NOT_VERIFIED")

    model_asset = json.loads(Path(args.model_asset).read_text(encoding="utf-8"))
    validate_model_asset(model_asset)

    stem = Path(args.stem)
    require(stem.is_file(), "DEMUCS_COMMON_AVX2_STEM_MISSING")
    pcm, sample_rate = sf.read(stem, always_2d=True, dtype="float32")
    require(pcm.size > 0, "DEMUCS_COMMON_AVX2_EMPTY_PCM")
    require(np.all(np.isfinite(pcm)), "DEMUCS_COMMON_AVX2_NONFINITE_PCM")
    pcm = np.ascontiguousarray(pcm)

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "sampleLabel": args.sample_label,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "scope": "independent-host-common-aten-onednn-avx2-demucs-pass",
        "source": {
            "sourceAudioGitBlobSha": "4dd709e3fa177b4daeed71ca97f0199757729d4b",
            "decodedSeparationWavSha256": args.input_sha256.lower(),
            "stemFileSha256": sha256_file(stem),
            "stemPcmSha256": hashlib.sha256(pcm.tobytes()).hexdigest(),
            "sampleRate": int(sample_rate),
            "shape": [int(value) for value in pcm.shape],
            "totalPcmValues": int(pcm.size),
            "stemRms": float(math.sqrt(float(np.mean(pcm.astype(np.float64) ** 2)))),
        },
        "executionContractCandidate": {
            "productionAuthorized": False,
            "selectionBasis": "constrain-both-dispatch-surfaces-proven-causal-by-same-host-diagnostic",
            "atenCpuCapability": "avx2",
            "onednnMaxCpuIsa": "AVX2",
            "demucsModel": "htdemucs_6s",
            "device": "cpu",
            "shifts": 0,
            "overlap": 0.25,
            "segmentSeconds": 7,
            "stem": "guitar",
        },
        "runtime": {
            "nativeCpuModel": args.native_cpu_model,
            "nativeCpuVendor": args.native_cpu_vendor,
            "nativeTorchCpuCapability": args.native_torch_capability,
            "effectiveTorchCpuCapability": torch.backends.cpu.get_cpu_capability(),
            "effectiveOneDnnIsaLine": args.onednn_isa_line,
            "azureRegion": args.azure_region or None,
            "imageOS": os.environ.get("ImageOS"),
            "imageVersion": os.environ.get("ImageVersion"),
            "runnerOS": os.environ.get("RUNNER_OS"),
            "runnerArch": os.environ.get("RUNNER_ARCH"),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torchVersion": torch.__version__,
            "torchNumThreads": torch.get_num_threads(),
            "torchNumInteropThreads": torch.get_num_interop_threads(),
            "cudaAvailable": bool(torch.cuda.is_available()),
            "packages": {name: importlib.metadata.version(name) for name in PACKAGE_NAMES},
            "controls": {
                "ATEN_CPU_CAPABILITY": os.environ.get("ATEN_CPU_CAPABILITY"),
                "ONEDNN_MAX_CPU_ISA": os.environ.get("ONEDNN_MAX_CPU_ISA"),
                "OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS"),
                "MKL_NUM_THREADS": os.environ.get("MKL_NUM_THREADS"),
                "OPENBLAS_NUM_THREADS": os.environ.get("OPENBLAS_NUM_THREADS"),
                "NUMEXPR_NUM_THREADS": os.environ.get("NUMEXPR_NUM_THREADS"),
                "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
            },
        },
        "modelAsset": dict(EXPECTED_MODEL_ASSET),
        "hardGuards": dict(HARD_GUARDS),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": CONTRACT,
        "sampleLabel": args.sample_label,
        "nativeCpuVendor": args.native_cpu_vendor,
        "nativeCpuModel": args.native_cpu_model,
        "nativeTorchCpuCapability": args.native_torch_capability,
        "effectiveTorchCpuCapability": payload["runtime"]["effectiveTorchCpuCapability"],
        "effectiveOneDnnIsaLine": args.onednn_isa_line,
        "stemFileSha256": payload["source"]["stemFileSha256"],
        "stemPcmSha256": payload["source"]["stemPcmSha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
