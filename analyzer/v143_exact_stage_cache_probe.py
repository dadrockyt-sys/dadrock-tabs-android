"""Synthetic structural gate for the V143 exact-stage cache.

No audio is read, no Demucs/model code is imported, and no reference-facing
scoring is performed.
"""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from v143_exact_stage_cache import ExactStageCache, cache_key, sha256_bytes


def base_fingerprint() -> dict:
    return {
        "schema_version": 1,
        "normalized_source_sha256": "a" * 64,
        "separator_model": "htdemucs",
        "separator_weights_sha256": "b" * 64,
        "demucs_parameters": {
            "segment": None,
            "overlap": 0.25,
            "shifts": 1,
            "split": True,
        },
        "shift_policy": {
            "mode": "private_rng_exact",
            "seed": 0,
            "trace_policy": "frozen",
        },
        "audio_format": {
            "sample_rate_hz": 44100,
            "channels": 2,
        },
        "runtime_controls": {
            "torch_intraop_threads": 1,
            "torch_interop_threads": 1,
            "omp_num_threads": 1,
            "mkl_num_threads": 1,
            "onednn_enabled": False,
        },
        "code_policy_version": "v143-exact-cpu-policy-1",
    }


def main() -> int:
    results = {
        "audioUsed": False,
        "demucsInvoked": False,
        "referenceFacingScoring": False,
    }

    with tempfile.TemporaryDirectory(prefix="v143-exact-cache-") as temp_dir:
        root = Path(temp_dir) / "cache"
        cache = ExactStageCache(root)
        fingerprint = base_fingerprint()
        payloads = {
            "guitar.stage.bin": b"synthetic-guitar-stage-bytes-v143",
            "aggregate.stage.bin": b"synthetic-derived-aggregate-v143",
        }

        results["emptyMissPassed"] = cache.lookup(fingerprint) is None

        key = cache.store(fingerprint, payloads)
        hit = cache.lookup(fingerprint)
        results["cacheKey"] = key
        results["cacheKeyDeterministicPassed"] = key == cache_key(fingerprint)
        results["exactHitPassed"] = hit == payloads
        results["exactHitHashesPassed"] = (
            hit is not None
            and {name: sha256_bytes(data) for name, data in hit.items()}
            == {name: sha256_bytes(data) for name, data in payloads.items()}
        )

        mismatch = copy.deepcopy(fingerprint)
        mismatch["runtime_controls"]["torch_intraop_threads"] = 2
        results["keyMismatchMissPassed"] = cache.lookup(mismatch) is None
        results["keyMismatchChangesKeyPassed"] = cache_key(mismatch) != key

        corrupt_path = cache.entry_path(fingerprint) / "guitar.stage.bin"
        corrupt_path.write_bytes(b"corrupted")
        results["corruptionMissPassed"] = cache.lookup(fingerprint) is None

        cache.remove(fingerprint)
        results["cleanupPassed"] = not cache.entry_path(fingerprint).exists()

    gate_fields = [
        "emptyMissPassed",
        "cacheKeyDeterministicPassed",
        "exactHitPassed",
        "exactHitHashesPassed",
        "keyMismatchMissPassed",
        "keyMismatchChangesKeyPassed",
        "corruptionMissPassed",
        "cleanupPassed",
    ]
    results["allPassed"] = all(results.get(field) is True for field in gate_fields)
    print(json.dumps(results, sort_keys=True))
    return 0 if results["allPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
