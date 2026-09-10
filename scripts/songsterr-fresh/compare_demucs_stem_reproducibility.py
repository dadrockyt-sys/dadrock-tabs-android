#!/usr/bin/env python3

import argparse
import hashlib
import json
import math
from pathlib import Path

CONTRACT = "songsterr-fresh-demucs-stem-reproducibility-comparison-v1"


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Compare two already-produced Demucs guitar stems from the same verified input "
            "without selecting a preferred stem or changing downstream evidence."
        )
    )
    parser.add_argument("--a", help="first guitar stem WAV")
    parser.add_argument("--b", help="second guitar stem WAV")
    parser.add_argument("--input-sha256", help="verified separation-input SHA-256")
    parser.add_argument("--model-asset", help="pinned Demucs model-asset JSON")
    parser.add_argument("--runtime-metadata", help="runtime metadata JSON")
    parser.add_argument("--output", help="comparison JSON")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if not args.self_test and not all((
        args.a, args.b, args.input_sha256, args.model_asset,
        args.runtime_metadata, args.output
    )):
        parser.error(
            "--a, --b, --input-sha256, --model-asset, --runtime-metadata, and --output "
            "are required unless --self-test is used"
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


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_model_asset(asset):
    required = {
        "contract": "songsterr-fresh-demucs-model-asset-v2",
        "primaryLoader": "huggingface",
        "hfRepoId": "adefossez/HTDemucs-6s",
        "hfPinnedRevision": "3c5ee475be622df764938de97e4281a7b07ffa58",
        "hfAssetUploadRevision": "053e1404489b3dc58bf718224fac4b7316de8c93",
        "assetFilename": "5c90dfd2.safetensors",
        "assetSha256": "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411",
    }
    for key, expected in required.items():
        require(asset.get(key) == expected, f"DEMUCS_REPRO_MODEL_ASSET_CHANGED:{key}")
    return required


def compare_stems(a_path, b_path, input_sha256, model_asset, runtime_metadata):
    import numpy as np
    import soundfile as sf

    a_path = Path(a_path)
    b_path = Path(b_path)
    require(a_path.is_file() and b_path.is_file(), "DEMUCS_REPRO_STEM_MISSING")
    require(
        isinstance(input_sha256, str) and len(input_sha256) == 64
        and all(ch in "0123456789abcdef" for ch in input_sha256.lower()),
        "DEMUCS_REPRO_INPUT_SHA_INVALID",
    )
    fixed_asset = validate_model_asset(model_asset)
    require(isinstance(runtime_metadata, dict) and runtime_metadata,
            "DEMUCS_REPRO_RUNTIME_METADATA_MISSING")

    a, sr_a = sf.read(a_path, always_2d=True, dtype="float32")
    b, sr_b = sf.read(b_path, always_2d=True, dtype="float32")
    require(sr_a == sr_b and sr_a > 0, "DEMUCS_REPRO_SAMPLE_RATE_MISMATCH")
    require(a.shape == b.shape and a.size > 0, "DEMUCS_REPRO_SHAPE_MISMATCH")
    require(np.all(np.isfinite(a)) and np.all(np.isfinite(b)), "DEMUCS_REPRO_NONFINITE_PCM")

    diff = a.astype(np.float64) - b.astype(np.float64)
    abs_diff = np.abs(diff)
    file_sha_a = sha256_file(a_path)
    file_sha_b = sha256_file(b_path)
    pcm_sha_a = sha256_bytes(np.ascontiguousarray(a).tobytes())
    pcm_sha_b = sha256_bytes(np.ascontiguousarray(b).tobytes())
    exact_samples = bool(np.array_equal(a, b))
    differing_samples = int(np.count_nonzero(a != b))
    total_samples = int(a.size)
    mae = float(np.mean(abs_diff))
    rmse = float(math.sqrt(float(np.mean(diff * diff))))
    max_abs = float(np.max(abs_diff))
    reference_rms = float(math.sqrt(float(np.mean(a.astype(np.float64) ** 2))))
    if rmse == 0.0:
        snr_db = None
    elif reference_rms == 0.0:
        snr_db = None
    else:
        snr_db = float(20.0 * math.log10(reference_rms / rmse))

    return {
        "contract": CONTRACT,
        "version": 1,
        "diagnosticOnly": True,
        "referenceBlind": True,
        "changesDuration": False,
        "changesPitchIdentity": False,
        "invokesModel": False,
        "selectsPreferredStem": False,
        "proposesDemucsSettingChange": False,
        "thresholdSelection": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
        "source": {
            "verifiedSeparationInputSha256": input_sha256.lower(),
            "stemAPath": str(a_path),
            "stemBPath": str(b_path),
            "stemAFileSha256": file_sha_a,
            "stemBFileSha256": file_sha_b,
            "stemAPcmSha256": pcm_sha_a,
            "stemBPcmSha256": pcm_sha_b,
            "modelAsset": fixed_asset,
            "runtimeMetadata": runtime_metadata,
        },
        "comparison": {
            "sampleRate": int(sr_a),
            "shape": [int(v) for v in a.shape],
            "totalPcmValues": total_samples,
            "fileBytesIdentical": file_sha_a == file_sha_b,
            "pcmBytesIdentical": pcm_sha_a == pcm_sha_b,
            "exactSampleEquality": exact_samples,
            "differingPcmValueCount": differing_samples,
            "differingPcmValueFraction": float(differing_samples / total_samples),
            "meanAbsoluteDifference": mae,
            "rootMeanSquareDifference": rmse,
            "maximumAbsoluteDifference": max_abs,
            "referenceStemRms": reference_rms,
            "snrDbRelativeToStemA": snr_db,
        },
        "hardGuards": {
            "preferredStemSelection": False,
            "durationWrite": False,
            "sourceEndWrite": False,
            "pitchIdentityWrite": False,
            "modelInferenceByComparator": False,
            "thresholdSelection": False,
            "thresholdSweep": False,
            "acceptanceDecision": False,
        },
    }


def self_test():
    import tempfile
    import numpy as np
    import soundfile as sf

    asset = {
        "contract": "songsterr-fresh-demucs-model-asset-v2",
        "primaryLoader": "huggingface",
        "hfRepoId": "adefossez/HTDemucs-6s",
        "hfPinnedRevision": "3c5ee475be622df764938de97e4281a7b07ffa58",
        "hfAssetUploadRevision": "053e1404489b3dc58bf718224fac4b7316de8c93",
        "assetFilename": "5c90dfd2.safetensors",
        "assetSha256": "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411",
    }
    runtime = {"python": "self-test", "platform": "self-test"}
    input_sha = "a" * 64

    with tempfile.TemporaryDirectory() as tmp:
        a_path = Path(tmp) / "a.wav"
        b_path = Path(tmp) / "b.wav"
        c_path = Path(tmp) / "c.wav"
        samples = np.linspace(-0.5, 0.5, 2048, dtype=np.float32).reshape(-1, 1)
        sf.write(a_path, samples, 22050, subtype="FLOAT")
        sf.write(b_path, samples.copy(), 22050, subtype="FLOAT")
        changed = samples.copy()
        changed[100, 0] += np.float32(0.001)
        sf.write(c_path, changed, 22050, subtype="FLOAT")

        equal = compare_stems(a_path, b_path, input_sha, asset, runtime)
        require(equal["comparison"]["exactSampleEquality"] is True,
                "DEMUCS_REPRO_SELF_TEST_EQUAL_NOT_EQUAL")
        require(equal["comparison"]["rootMeanSquareDifference"] == 0.0,
                "DEMUCS_REPRO_SELF_TEST_EQUAL_RMSE")

        different = compare_stems(a_path, c_path, input_sha, asset, runtime)
        require(different["comparison"]["exactSampleEquality"] is False,
                "DEMUCS_REPRO_SELF_TEST_DIFFERENT_NOT_DETECTED")
        require(different["comparison"]["differingPcmValueCount"] == 1,
                "DEMUCS_REPRO_SELF_TEST_DIFFERING_COUNT")
        require(different["selectsPreferredStem"] is False,
                "DEMUCS_REPRO_SELF_TEST_PREFERENCE_GUARD")

        broken = dict(asset)
        broken["assetSha256"] = "b" * 64
        try:
            compare_stems(a_path, b_path, input_sha, broken, runtime)
        except RuntimeError as exc:
            require("MODEL_ASSET_CHANGED" in str(exc),
                    "DEMUCS_REPRO_SELF_TEST_WRONG_ASSET_FAILURE")
        else:
            raise RuntimeError("DEMUCS_REPRO_SELF_TEST_ASSET_FAIL_OPEN")

    print(json.dumps({
        "selfTest": "PASS",
        "contract": CONTRACT,
        "diagnosticOnly": True,
        "selectsPreferredStem": False,
        "thresholdSweep": False,
        "ownsAcceptanceDecision": False,
    }, sort_keys=True))


def main():
    args = parse_args()
    if args.self_test:
        self_test()
        return
    payload = compare_stems(
        args.a,
        args.b,
        args.input_sha256,
        load_json(args.model_asset),
        load_json(args.runtime_metadata),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
