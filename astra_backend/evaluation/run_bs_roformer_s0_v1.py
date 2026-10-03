"""Run the user-authorized BS-Roformer ONNX S0 development evaluation.

This script:
1. verifies the exact FP16 model SHA,
2. separates each frozen S0 mixture,
3. scores raw guitar/bass stems against exact synthetic ground truth,
4. records separator-output diagnostics,
5. applies the already-frozen bleed cleanup,
6. scores cleaned stems,
7. records runtime, reconstruction and per-mixture results.

It does not train or tune the separator or cleanup thresholds.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from stem_bleed_cleanup_v1 import CleanupConfig, exact_residual, si_sdr, suppress_cross_stem_bleed
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems


def load(path: Path):
    x, fs = sf.read(path, always_2d=True, dtype="float32")
    return x, fs


def truth_stems(directory: Path):
    out = {}
    for p in sorted(directory.glob("*.wav")):
        if p.name.endswith("_mix.wav"):
            continue
        role = p.stem.split("_", 1)[1]
        x, fs = load(p)
        out[role] = (x, fs)
    return out


def collapse_truth(truth: dict[str, tuple[np.ndarray, int]], target: str, length: int) -> np.ndarray:
    exact = [v[0][:length] for k, v in truth.items() if k == target]
    if exact:
        return np.sum(np.stack(exact), axis=0).astype(np.float32)
    sample = next(iter(truth.values()))[0]
    return np.zeros_like(sample[:length], dtype=np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s0-root", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--output-json", required=True)
    args = ap.parse_args()

    adapter = BsRoformer6StemOnnxAdapter(Path(args.model))
    cfg = CleanupConfig()
    diagnostic_cfg = DiagnosticConfig()
    root = Path(args.s0_root)
    rows = []
    started = time.perf_counter()

    for d in sorted(root.glob("S0M*")):
        mixes = list(d.glob("*_mix.wav"))
        if len(mixes) != 1:
            continue

        mix, fs = load(mixes[0])
        truth = truth_stems(d)

        t0 = time.perf_counter()
        raw = adapter.separate_array(mix, fs)
        sep_seconds = time.perf_counter() - t0

        diagnostics = diagnose_stems(mix, raw, fs, diagnostic_cfg)

        # Cleanup only uses separator outputs; no ground truth leaks into cleanup.
        cleaned, _ = suppress_cross_stem_bleed(raw, fs, cfg)

        length = len(mix)
        row = {
            "id": d.name,
            "separatorSeconds": sep_seconds,
            "diagnostics": diagnostics,
            "stems": {},
        }

        for target in ("guitar", "bass"):
            ref = collapse_truth(truth, target, length)
            ref_energy = float(np.sum(ref.astype(np.float64) ** 2))

            if ref_energy < 1e-12:
                row["stems"][target] = {
                    "targetPresent": False,
                    "rawEnergy": float(np.mean(raw[target] ** 2)),
                    "cleanEnergy": float(np.mean(cleaned[target] ** 2)),
                }
            else:
                raw_score = si_sdr(ref, raw[target])
                clean_score = si_sdr(ref, cleaned[target])
                row["stems"][target] = {
                    "targetPresent": True,
                    "rawSiSdrDb": raw_score,
                    "cleanSiSdrDb": clean_score,
                    "improvementDb": clean_score - raw_score,
                }

        residual = exact_residual(mix, cleaned)
        recon = residual.copy()
        for value in cleaned.values():
            recon += value[: len(recon)]

        row["cleanReconstructionMaxAbsError"] = float(
            np.max(np.abs(recon - mix[: len(recon)]))
        )
        rows.append(row)

    present = []
    for row in rows:
        for data in row["stems"].values():
            if data.get("targetPresent"):
                present.append(data["improvementDb"])

    result = {
        "schemaVersion": 1,
        "kind": "bs-roformer-sw-6stem-s0-evaluation",
        "modelSha256": FP16_SHA256,
        "cleanupConfig": cfg.to_dict(),
        "diagnosticConfig": diagnostic_cfg.to_dict(),
        "mixtureCount": len(rows),
        "totalWallSeconds": time.perf_counter() - started,
        "meanCleanupImprovementDb": float(np.mean(present)) if present else None,
        "minimumCleanupImprovementDb": float(np.min(present)) if present else None,
        "maximumCleanupImprovementDb": float(np.max(present)) if present else None,
        "results": rows,
        "interpretationBoundary": "S0 synthetic mixtures only; not commercial-song evidence.",
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
