#!/usr/bin/env python3

import argparse
import hashlib
import json
from importlib.metadata import version as package_version
from pathlib import Path

import yaml
from huggingface_hub.constants import HF_HUB_CACHE

import demucs.hf as demucs_hf
import demucs.pretrained as pretrained

CONTRACT = "songsterr-fresh-demucs-model-asset-v2"
EXPECTED_PACKAGE = "demucs"
EXPECTED_PACKAGE_VERSION = "4.1.0"
EXPECTED_MODEL_NAME = "htdemucs_6s"
EXPECTED_SIGNATURE = "5c90dfd2"
EXPECTED_HF_NAMESPACE = "adefossez"
EXPECTED_HF_REPO_NAME = "HTDemucs-6s"
EXPECTED_HF_REPO_ID = f"{EXPECTED_HF_NAMESPACE}/{EXPECTED_HF_REPO_NAME}"
EXPECTED_HF_REVISION = "053e1404489b3dc58bf718224fac4b7316de8c93"
EXPECTED_BAG_FILENAME = "htdemucs_6s.yaml"
EXPECTED_ASSET_FILENAME = "5c90dfd2.safetensors"
EXPECTED_ASSET_SHA256 = "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411"
EXPECTED_XET_HASH = "4a08ca8231da4bd9433191a95ee700cc8ba8693e980ac5b444f63eff38c807e1"

LEGACY_FALLBACK_FILENAME = "5c90dfd2-34c22ccb.th"
LEGACY_FALLBACK_CHECKSUM_PREFIX = "34c22ccb"
LEGACY_FALLBACK_REMOTE_SUFFIX = f"hybrid_transformer/{LEGACY_FALLBACK_FILENAME}"


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


def parse_legacy_remote_manifest(path):
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


def hf_repo_cache_path():
    escaped = EXPECTED_HF_REPO_ID.replace("/", "--")
    return Path(HF_HUB_CACHE).expanduser() / f"models--{escaped}"


def verify_primary_hf_asset():
    package = package_version(EXPECTED_PACKAGE)
    if package != EXPECTED_PACKAGE_VERSION:
        raise RuntimeError(f"DEMUCS_PACKAGE_VERSION_CHANGED:{package}")

    namespace = getattr(demucs_hf, "DEFAULT_NAMESPACE", None)
    if namespace != EXPECTED_HF_NAMESPACE:
        raise RuntimeError(f"DEMUCS_HF_NAMESPACE_CHANGED:{namespace}")
    repo_name = demucs_hf.hf_repo_name(EXPECTED_MODEL_NAME)
    if repo_name != EXPECTED_HF_REPO_NAME:
        raise RuntimeError(f"DEMUCS_HF_REPO_MAPPING_CHANGED:{repo_name}")

    repo_cache = hf_repo_cache_path()
    snapshot = repo_cache / "snapshots" / EXPECTED_HF_REVISION
    bag_path = snapshot / EXPECTED_BAG_FILENAME
    asset_path = snapshot / EXPECTED_ASSET_FILENAME
    sidecar_path = snapshot / f"{EXPECTED_SIGNATURE}.json"

    missing = [
        str(path)
        for path in (bag_path, asset_path, sidecar_path)
        if not path.is_file()
    ]
    if missing:
        discovered_snapshots = []
        snapshots_root = repo_cache / "snapshots"
        if snapshots_root.is_dir():
            discovered_snapshots = sorted(
                child.name for child in snapshots_root.iterdir() if child.is_dir()
            )
        raise RuntimeError(
            "DEMUCS_HF_PINNED_SNAPSHOT_MISSING:"
            + json.dumps(
                {
                    "expectedRevision": EXPECTED_HF_REVISION,
                    "repoCache": str(repo_cache),
                    "missing": missing,
                    "discoveredSnapshots": discovered_snapshots,
                },
                sort_keys=True,
            )
        )

    bag = yaml.safe_load(bag_path.read_text(encoding="utf-8"))
    signatures = bag.get("models") if isinstance(bag, dict) else None
    if signatures != [EXPECTED_SIGNATURE]:
        raise RuntimeError(f"DEMUCS_HF_BAG_SIGNATURE_CHANGED:{signatures}")

    asset_sha = sha256_file(asset_path)
    if asset_sha != EXPECTED_ASSET_SHA256:
        raise RuntimeError(f"DEMUCS_HF_ASSET_SHA_CHANGED:{asset_sha}")

    refs_main = repo_cache / "refs" / "main"
    cached_main_revision = None
    if refs_main.is_file():
        cached_main_revision = refs_main.read_text(encoding="utf-8").strip()
        if cached_main_revision != EXPECTED_HF_REVISION:
            raise RuntimeError(
                f"DEMUCS_HF_MAIN_REVISION_CHANGED:{cached_main_revision}"
            )

    legacy_models = parse_legacy_remote_manifest(pretrained.REMOTE_ROOT / "files.txt")
    legacy_url = legacy_models.get(EXPECTED_SIGNATURE)
    if not legacy_url or not legacy_url.endswith(LEGACY_FALLBACK_REMOTE_SUFFIX):
        raise RuntimeError(f"DEMUCS_LEGACY_FALLBACK_IDENTITY_CHANGED:{legacy_url}")

    return {
        "contract": CONTRACT,
        "version": 2,
        "package": EXPECTED_PACKAGE,
        "packageVersion": package,
        "modelName": EXPECTED_MODEL_NAME,
        "modelSignature": EXPECTED_SIGNATURE,
        "primaryLoader": "huggingface",
        "hfNamespace": EXPECTED_HF_NAMESPACE,
        "hfRepoName": EXPECTED_HF_REPO_NAME,
        "hfRepoId": EXPECTED_HF_REPO_ID,
        "hfPinnedRevision": EXPECTED_HF_REVISION,
        "hfCachedMainRevision": cached_main_revision,
        "bagFilename": EXPECTED_BAG_FILENAME,
        "bagModels": signatures,
        "assetFilename": EXPECTED_ASSET_FILENAME,
        "assetSha256": asset_sha,
        "expectedAssetSha256": EXPECTED_ASSET_SHA256,
        "assetXetHash": EXPECTED_XET_HASH,
        "assetSnapshotPathIdentity": f"snapshots/{EXPECTED_HF_REVISION}/{EXPECTED_ASSET_FILENAME}",
        "sidecarFilename": sidecar_path.name,
        "legacyFallback": {
            "primary": False,
            "filename": LEGACY_FALLBACK_FILENAME,
            "checksumPrefix": LEGACY_FALLBACK_CHECKSUM_PREFIX,
            "remoteUrl": legacy_url,
        },
        "referenceBlind": True,
        "modelInvokedByThisVerifier": False,
        "gpuInvokedByThisVerifier": False,
        "legacyV143ScorerImported": False,
        "professionalScorerUsed": False,
        "referenceTabUsed": False,
    }


def main():
    args = parse_args()
    payload = verify_primary_hf_asset()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
