#!/usr/bin/env python3

import argparse
import hashlib
import json
from importlib.metadata import version as package_version
from pathlib import Path

import torch
import yaml
import demucs.pretrained as pretrained

CONTRACT = "songsterr-fresh-demucs-model-asset-v1"
EXPECTED_PACKAGE = "demucs"
EXPECTED_MODEL_NAME = "htdemucs_6s"
EXPECTED_SIGNATURE = "5c90dfd2"
EXPECTED_FILENAME = "5c90dfd2-34c22ccb.th"
EXPECTED_CHECKSUM_PREFIX = "34c22ccb"
EXPECTED_REMOTE_SUFFIX = f"hybrid_transformer/{EXPECTED_FILENAME}"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def parse_remote_manifest(path):
    root = ""
    models = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("root:"):
            root = line.split(":", 1)[1].strip()
            continue
        signature = line.split("-", 1)[0]
        models[signature] = f"{pretrained.ROOT_URL}{root}{line}"
    return models


def main():
    args = parse_args()
    remote_root = Path(pretrained.REMOTE_ROOT)
    bag_path = remote_root / f"{EXPECTED_MODEL_NAME}.yaml"
    files_path = remote_root / "files.txt"
    if not bag_path.is_file() or not files_path.is_file():
        raise RuntimeError("DEMUCS_MODEL_MANIFEST_FILES_MISSING")

    bag = yaml.safe_load(bag_path.read_text(encoding="utf-8"))
    signatures = bag.get("models") if isinstance(bag, dict) else None
    if signatures != [EXPECTED_SIGNATURE]:
        raise RuntimeError(f"DEMUCS_MODEL_SIGNATURE_CHANGED:{signatures}")

    remote_models = parse_remote_manifest(files_path)
    remote_url = remote_models.get(EXPECTED_SIGNATURE)
    if not remote_url or not remote_url.endswith(EXPECTED_REMOTE_SUFFIX):
        raise RuntimeError(f"DEMUCS_MODEL_REMOTE_ASSET_CHANGED:{remote_url}")

    checkpoint = Path(torch.hub.get_dir()) / "checkpoints" / EXPECTED_FILENAME
    if not checkpoint.is_file():
        raise RuntimeError(f"DEMUCS_MODEL_CHECKPOINT_NOT_FOUND:{checkpoint}")
    full_sha256 = sha256_file(checkpoint)
    if not full_sha256.startswith(EXPECTED_CHECKSUM_PREFIX):
        raise RuntimeError(
            f"DEMUCS_MODEL_CHECKSUM_PREFIX_MISMATCH:{full_sha256}:{EXPECTED_CHECKSUM_PREFIX}"
        )

    payload = {
        "contract": CONTRACT,
        "version": 1,
        "package": EXPECTED_PACKAGE,
        "packageVersion": package_version(EXPECTED_PACKAGE),
        "modelName": EXPECTED_MODEL_NAME,
        "modelSignature": EXPECTED_SIGNATURE,
        "assetFilename": EXPECTED_FILENAME,
        "assetRemoteUrl": remote_url,
        "assetSha256": full_sha256,
        "assetChecksumPrefix": EXPECTED_CHECKSUM_PREFIX,
        "assetChecksumPrefixVerified": True,
        "bagManifestSha256": sha256_file(bag_path),
        "remoteFilesManifestSha256": sha256_file(files_path),
        "referenceBlind": True,
        "modelInvokedByThisVerifier": False,
        "gpuInvokedByThisVerifier": False,
        "legacyV143ScorerImported": False,
        "professionalScorerUsed": False,
        "referenceTabUsed": False,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
