#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-demucs-same-host-cpu-dispatch-comparison-v1"
VARIANTS = (
    "native",
    "aten-avx2",
    "onednn-avx2",
    "combined-avx2",
)
CONTROLS = {
    "native": {},
    "aten-avx2": {"ATEN_CPU_CAPABILITY": "avx2"},
    "onednn-avx2": {"ONEDNN_MAX_CPU_ISA": "AVX2"},
    "combined-avx2": {
        "ATEN_CPU_CAPABILITY": "avx2",
        "ONEDNN_MAX_CPU_ISA": "AVX2",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare four fixed Demucs stems produced on one hosted runner under native, "
            "ATen AVX2-capped, oneDNN AVX2-capped, and combined AVX2-capped dispatch. "
            "This is a reference-blind numerical reproducibility diagnostic only."
        )
    )
    for variant in VARIANTS:
        parser.add_argument(f"--{variant}", required=True)
    parser.add_argument("--native-cpu-model", required=True)
    parser.add_argument("--native-torch-capability", required=True)
    parser.add_argument("--runtime-metadata", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_pcm(path):
    pcm, sample_rate = sf.read(path, always_2d=True, dtype="float32")
    if pcm.size == 0 or not np.all(np.isfinite(pcm)):
        raise RuntimeError(f"DEMUCS_CPU_DISPATCH_INVALID_PCM:{path}")
    return np.ascontiguousarray(pcm), int(sample_rate)


def pcm_sha256(pcm):
    return hashlib.sha256(pcm.tobytes()).hexdigest()


def metrics(a, b):
    if a.shape != b.shape:
        raise RuntimeError(f"DEMUCS_CPU_DISPATCH_SHAPE_MISMATCH:{a.shape}:{b.shape}")
    delta = a.astype(np.float64) - b.astype(np.float64)
    abs_delta = np.abs(delta)
    return {
        "exactSampleEquality": bool(np.array_equal(a, b)),
        "differingPcmValues": int(np.count_nonzero(delta)),
        "totalPcmValues": int(delta.size),
        "mae": float(np.mean(abs_delta)),
        "rmse": float(math.sqrt(float(np.mean(delta ** 2)))),
        "maxAbsoluteDifference": float(np.max(abs_delta)),
    }


def main():
    args = parse_args()
    paths = {variant: Path(getattr(args, variant.replace("-", "_"))) for variant in VARIANTS}
    for variant, path in paths.items():
        if not path.is_file():
            raise RuntimeError(f"DEMUCS_CPU_DISPATCH_STEM_MISSING:{variant}:{path}")

    runtime_metadata = json.loads(Path(args.runtime_metadata).read_text(encoding="utf-8"))
    observations = {}
    pcm_by_variant = {}
    sample_rate = None
    shape = None
    for variant in VARIANTS:
        pcm, rate = load_pcm(paths[variant])
        if sample_rate is None:
            sample_rate = rate
            shape = list(pcm.shape)
        if rate != sample_rate or list(pcm.shape) != shape:
            raise RuntimeError(f"DEMUCS_CPU_DISPATCH_GEOMETRY_CHANGED:{variant}")
        pcm_by_variant[variant] = pcm
        observations[variant] = {
            "controls": CONTROLS[variant],
            "stemFileSha256": sha256_file(paths[variant]),
            "stemPcmSha256": pcm_sha256(pcm),
            "stemRms": float(math.sqrt(float(np.mean(pcm.astype(np.float64) ** 2)))),
        }

    comparisons = {}
    native = pcm_by_variant["native"]
    for variant in VARIANTS[1:]:
        comparisons[f"native-vs-{variant}"] = metrics(native, pcm_by_variant[variant])
    comparisons["aten-avx2-vs-combined-avx2"] = metrics(
        pcm_by_variant["aten-avx2"], pcm_by_variant["combined-avx2"]
    )
    comparisons["onednn-avx2-vs-combined-avx2"] = metrics(
        pcm_by_variant["onednn-avx2"], pcm_by_variant["combined-avx2"]
    )

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "diagnosticOnly": True,
        "scope": "same-host-fixed-demucs-cpu-dispatch-isolation",
        "nativeCpuModel": args.native_cpu_model,
        "nativeTorchCpuCapability": args.native_torch_capability,
        "sampleRate": sample_rate,
        "shape": shape,
        "runtimeMetadata": runtime_metadata,
        "variants": observations,
        "comparisons": comparisons,
        "hardGuards": {
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
        },
    }
    if any(value is not False for value in payload["hardGuards"].values()):
        raise RuntimeError("DEMUCS_CPU_DISPATCH_GUARD_CHANGED")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": CONTRACT,
        "nativeCpuModel": args.native_cpu_model,
        "nativeTorchCpuCapability": args.native_torch_capability,
        "fileHashes": {k: v["stemFileSha256"] for k, v in observations.items()},
        "pcmHashes": {k: v["stemPcmSha256"] for k, v in observations.items()},
        "nativeComparisons": {
            k: {
                "exactSampleEquality": v["exactSampleEquality"],
                "differingPcmValues": v["differingPcmValues"],
                "rmse": v["rmse"],
                "maxAbsoluteDifference": v["maxAbsoluteDifference"],
            }
            for k, v in comparisons.items()
            if k.startswith("native-vs-")
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
