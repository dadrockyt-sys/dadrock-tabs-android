#!/usr/bin/env python3
"""Frozen post-V9 output-admission audit. CPU inference only; no optimizer or tuning."""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from guitartechs_real_training import real_training as base
from guitartechs_training_v7.model import TemporalTabCNNV7
from guitartechs_training_v9.model import TemporalTabCNNV9
from guitartechs_training_v4 import objective_decoder as v4
from guitartechs_training_v8.decoder import decode_v8_hybrid

Q = (0., .01, .1, .5, .9, .99, 1.)
FOLDS = (
    ("p1-train-p2-validate", "P2", 120, 40),
    ("p2-train-p1-validate", "P1", 136, 41),
)
MODELS = {
    "p1-train-p2-validate": {
        "v9": ("a62cb31bcfaa238965e0f79934a00c430c0b8723a4d51168104ddea5e4a0f90c",
               "933c5faedafa4b3ddfb37e0ad87cef639294a99ff29acd6d581f622ed64a966e", 20),
        "v8": ("072fb49ac8112d65df2d11a0110535d675cafc4b9c04631fd2d0a9eeafcd0763", None, 1000),
    },
    "p2-train-p1-validate": {
        "v9": ("6bb66bebb074f5b26ccaefd2ed2322eefed9381998f7cce81246f4ab5af40452",
               "56b275d79426f5dd14641c0f3ffd802491734dd4f2ec9110a75616b861588a01", 20),
        "v8": ("566a4f2d7e4d97e0b93ffe1662b921d8e0e75066540a8a5f1e683f5a6498d596", None, 940),
    },
}
METRICS = ("precision", "recall", "f1", "completeness", "frameAccuracy", "abstentionRate")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def model_load(path, fold, version, source_root):
    expected_hash, expected_state, epoch = MODELS[fold][version]
    if sha256_file(path) != expected_hash:
        raise RuntimeError("frozen model file SHA-256 mismatch")
    # Only exact, previously verified development checkpoints are deserialized.
    try:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError as ex:
        raise RuntimeError("weights_only torch.load required; refusing unsafe fallback") from ex
    candidate = {
        "v8": "astra_guitartechs_tabcnn_v7_ranked_event_transition",
        "v9": "astra_guitartechs_v9_paired_view_consistency",
    }[version]
    if (checkpoint.get("candidateId") != candidate or
        checkpoint.get("fold") != fold or int(checkpoint.get("epoch", -1)) != epoch):
        raise RuntimeError("frozen model identity/epoch mismatch")
    cls = TemporalTabCNNV9 if version == "v9" else TemporalTabCNNV7
    model = cls(source_root)
    model.load_state_dict(checkpoint["stateDict"], strict=True)
    if expected_state and base.state_sha256(model) != expected_state:
        raise RuntimeError("selected model internal state SHA-256 mismatch")
    model.eval()
    return model


def infer_raw(model, feature, chunk=512):
    if feature.ndim != 2 or feature.shape[0] != 192 or feature.shape[1] < 1:
        raise RuntimeError("unexpected frozen feature shape")
    pad = np.pad(feature, ((0, 0), (base.HALF_CONTEXT, base.HALF_CONTEXT)))
    windows = np.lib.stride_tricks.sliding_window_view(
        pad, base.FRAME_CONTEXT, axis=1).transpose(1, 0, 2)
    total = feature.shape[1]
    state = np.empty((total, base.NUM_STRINGS, base.NUM_CLASSES), dtype=np.float32)
    event = np.empty((total, base.NUM_STRINGS), dtype=np.float32)
    hidden = None
    with torch.inference_mode():
        for lo in range(0, total, chunk):
            hi = min(total, lo + chunk)
            x = np.ascontiguousarray(windows[lo:hi])[None, :, None, :, :]
            output = model(torch.from_numpy(x), hidden)
            hidden = output["hidden"].detach()
            state[lo:hi] = torch.softmax(output["tablature"].reshape(
                1, hi-lo, base.NUM_STRINGS, base.NUM_CLASSES), -1)[0].cpu().numpy()
            event[lo:hi] = output["event"][0].cpu().numpy()
    return state, event


def percentile(values):
    if len(values) == 0:
        return None
    return [float(x) for x in np.quantile(values, Q)]


def admission_trace(state):
    """Mirror the immutable V4 conditions, then use V4's own gap/prune primitives."""
    t, strings, classes = state.shape
    assert strings == 6 and classes == 21
    before = np.full((t, strings), -1, dtype=np.int16)
    after_merge = before.copy()
    after_prune = before.copy()
    counts = {
        "strongStartCandidates": 0,
        "confirmedStartCandidates": 0,
        "acceptedStrongStarts": 0,
        "acceptedConfirmedStarts": 0,
        "continuedFrames": 0,
        "startRejectedFrames": 0,
    }
    for s in range(strings):
        current = -1
        for i in range(t):
            row = state[i, s]
            silence = float(row[v4.SILENCE_CLASS])
            fret = int(np.argmax(row[:v4.NUM_FRETS]))
            active = float(row[fret])
            strong = active >= v4.DECODER_START_CONFIDENCE and active > silence
            confirm = False
            if not strong and i + 1 < t:
                next_row = state[i+1, s]
                same = float(next_row[fret])
                next_silence = float(next_row[v4.SILENCE_CLASS])
                confirm = (
                    active >= v4.DECODER_CONFIRMED_START_CONFIDENCE
                    and active >= silence * v4.DECODER_CONFIRMED_START_VS_SILENCE_RATIO
                    and same >= v4.DECODER_CONFIRM_CONFIDENCE
                    and same >= next_silence * v4.DECODER_CONFIRM_VS_SILENCE_RATIO
                )
            counts["strongStartCandidates"] += int(strong)
            counts["confirmedStartCandidates"] += int(confirm)
            if current >= 0 and float(row[current]) >= v4.DECODER_CONTINUE_CONFIDENCE and float(row[current]) >= silence * .80:
                before[i, s] = current
                counts["continuedFrames"] += 1
                continue
            if strong or confirm:
                current = fret
                before[i, s] = fret
                counts["acceptedStrongStarts" if strong else "acceptedConfirmedStarts"] += 1
            else:
                current = -1
                counts["startRejectedFrames"] += 1
        after_merge[:, s] = v4._merge_short_gaps(before[:, s], v4.DECODER_GAP_FRAMES)
        after_prune[:, s] = v4._prune_short_active_runs(after_merge[:, s], v4.DECODER_MIN_RUN_FRAMES)
    frozen = v4.decode_with_hysteresis(state)
    if not np.array_equal(after_prune, frozen):
        raise RuntimeError("V4 admission trace diverges from frozen decoder")
    counts.update({
        "activeRunsBeforeGapMerge": v4.count_active_runs(before),
        "activeRunsAfterGapMerge": v4.count_active_runs(after_merge),
        "activeRunsAfterPrune": v4.count_active_runs(after_prune),
    })
    return counts, frozen


def masked_event_counts(pred, ref):
    if ref.shape != (6, pred.shape[0]):
        raise RuntimeError("labels shape mismatch")
    mask = ref == base.MASK
    safe = pred.copy()
    safe[mask.T] = -1
    pe, re = [], []
    for s in range(6):
        pe.extend(base.runs(safe, mask.T, s))
        re.extend(base.runs(ref.T, mask.T, s))
    grouped = defaultdict(lambda: [[], []])
    for item in pe:
        grouped[(item["string"], item["fret"])][0].append(item)
    for item in re:
        grouped[(item["string"], item["fret"])][1].append(item)
    matched = 0
    for ps, rs in grouped.values():
        pairs = base.match_group(
            sorted(ps, key=lambda e: e["start"]),
            sorted(rs, key=lambda e: e["start"]))
        matched += len(pairs)
    return {
        "predictedEvents": len(pe),
        "referenceEvents": len(re),
        "truePositiveEvents": matched,
        "unmatchedPredictedEvents": len(pe)-matched,
        "unmatchedReferenceEvents": len(re)-matched,
    }


def summarize_capture(state, event, ref):
    if not np.isfinite(state).all() or not np.isfinite(event).all():
        raise RuntimeError("nonfinite model outputs; stop")
    if (state < 0).any() or not np.allclose(state.sum(-1), 1, atol=1e-5):
        raise RuntimeError("invalid probability normalization; stop")
    ma = np.max(state[..., :v4.NUM_FRETS], -1)
    silence = state[..., v4.SILENCE_CLASS]
    argmax_active = np.argmax(state, axis=-1) != v4.SILENCE_CLASS
    clipped = np.clip(state.astype(np.float64), 1e-38, 1)
    entropy = -np.sum(clipped*np.log(clipped), -1)
    counts, v4_states = admission_trace(state)
    final = decode_v8_hybrid(state, event)
    return final, {
        "frames": int(state.shape[0]),
        "validPositions": int(np.sum(ref != base.MASK)),
        "maskedPositions": int(np.sum(ref == base.MASK)),
        "finiteNormalized": True,
        "maxActiveProbabilityQuantiles": percentile(ma.ravel()),
        "silenceProbabilityQuantiles": percentile(silence.ravel()),
        "entropyQuantiles": percentile(entropy.ravel()),
        "stateArgmaxActivePositions": int(argmax_active.sum()),
        "stateArgmaxActiveFraction": float(argmax_active.mean()),
        **counts,
        "v8FinalActiveRuns": int(v4.count_active_runs(final)),
        "v8ChangedStatePositions": int(np.count_nonzero(final != v4_states)),
        **masked_event_counts(final, ref),
    }


def aggregate(captures):
    by_perf = defaultdict(list)
    for c in captures:
        by_perf[c["_performance"]].append(c)
    performances = []
    for key, views in sorted(by_perf.items()):
        performances.append({"category": views[0]["_category"], **{
            k: float(np.mean([v["metrics"][k] for v in views])) for k in METRICS
        }})
    summary = {k: float(np.mean([p[k] for p in performances])) for k in METRICS}
    summary["captureCount"] = len(captures)
    summary["performanceCount"] = len(performances)
    summary["contentF1"] = {}
    for cat in ("chords", "scales", "singlenotes", "techniques"):
        arr = [p["f1"] for p in performances if p["category"] == cat]
        summary["contentF1"]["PalmMute" if cat == "techniques" else cat] = float(np.mean(arr)) if arr else 0.
    return summary


def main():
    cli = argparse.ArgumentParser()
    for name in ("manifest", "data-dir", "source-root", "v9-p1", "v9-p2",
                 "v8-p1", "v8-p2", "alignment", "v8-receipt",
                 "v9-receipt", "out"):
        cli.add_argument("--"+name, required=True)
    args = cli.parse_args()
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)
    rows = base.load_manifest(args.manifest, args.data_dir)
    aligned = json.loads(Path(args.alignment).read_text())["correctionsMs"]
    keys = [row["key"] for row in rows]
    if len(keys) != 256 or len(set(keys)) != 256 or set(keys) != set(aligned):
        raise RuntimeError("frozen manifest/alignment key set mismatch")
    if {k: sum(row["performer"] == k for row in rows) for k in ("P1", "P2")} != {"P1": 136, "P2": 120}:
        raise RuntimeError("frozen performer population mismatch")
    manifest_hash = sha256_file(args.manifest)
    v8_receipt = json.loads(Path(args.v8_receipt).read_text())
    v9_receipt = json.loads(Path(args.v9_receipt).read_text())
    result = {
        "schema": "astra-guitar-techs-post-v9-fixed-output-admission-audit-v1",
        "authorization": "2026-10-08 user explicit approval of frozen bounded CPU P1/P2 forward-pass diagnostic",
        "manifestSha256": manifest_hash,
        "quantiles": list(Q),
        "folds": {},
        "guards": {
            "optimizerStepsExecuted": 0, "thresholdSweep": False,
            "p3Opened": False, "protectedSongUsed": False,
            "stageBHoldoutUsed": False, "paidCompute": False,
            "productionOrMainChanged": False,
        },
    }
    for fold, performer, expected_count, performance_count in FOLDS:
        subset = [row for row in rows if row["performer"] == performer]
        if len(subset) != expected_count:
            raise RuntimeError("invalid fold count")
        result["folds"][fold] = {}
        for version in ("v9", "v8"):
            location = getattr(args, version+"-"+("p1" if fold.startswith("p1-") else "p2"))
            model = model_load(location, fold, version, args.source_root)
            captures = []
            for row in subset:
                if sha256_file(row["_features"]) != row["featureSha256"] or sha256_file(row["_labels"]) != row["labelSha256"]:
                    raise RuntimeError("prepared feature or label hash mismatch")
                features = np.load(row["_features"], mmap_mode="r", allow_pickle=False)
                ref = np.load(row["_labels"], mmap_mode="r", allow_pickle=False)
                state, event = infer_raw(model, features)
                decoded, info = summarize_capture(state, event, ref)
                metrics = base.capture_metrics(decoded, ref)
                counts = masked_event_counts(decoded, ref)
                if counts["truePositiveEvents"] > min(counts["predictedEvents"], counts["referenceEvents"]):
                    raise RuntimeError("matching count impossible")
                captures.append({
                    "captureKeySha256": hashlib.sha256(row["key"].encode()).hexdigest(),
                    "_performance": row["performer"]+"|"+row["category"]+"|"+row["performanceKey"],
                    "_category": row["category"],
                    "metrics": metrics,
                    "audit": info,
                })
            agg = aggregate(captures)
            if agg["captureCount"] != expected_count or agg["performanceCount"] != performance_count:
                raise RuntimeError("frozen fold population mismatch")
            expected = (v9_receipt["folds"][fold]["fullValidationMetrics"] if version == "v9" else v8_receipt["folds"][fold])
            for field in ("precision", "recall", "f1", "completeness", "frameAccuracy"):
                if not np.isclose(agg[field], expected[field], rtol=0, atol=1e-8):
                    raise RuntimeError(f"frozen {version} metric non-reproduction: {fold}, {field}, {agg[field]} != {expected[field]}")
            for c in captures:
                del c["_performance"]
                del c["_category"]
            counts = ["predictedEvents", "referenceEvents", "truePositiveEvents",
                      "activeRunsBeforeGapMerge", "activeRunsAfterGapMerge",
                      "activeRunsAfterPrune", "v8FinalActiveRuns"]
            result["folds"][fold][version] = {
                "metrics": agg,
                "countTotals": {k: sum(c["audit"][k] for c in captures) for k in counts},
                "captures": captures,
            }
            print(f"AUDIT_FOLD={fold} MODEL={version} CAPTURES={len(captures)} F1={agg['f1']:.12f}", flush=True)
            del model
    result["decision"] = (
        "If V9 activeRunsAfterPrune totals are zero: frozen V4 admission bottleneck; "
        "if V9 predictedEvents positive and truePositiveEvents zero: "
        "investigate class/string/time/mask/matching contract before representation claims; "
        "otherwise describe measured distributions and stop. No tuning or retraining."
    )
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print("POST_V9_FIXED_OUTPUT_ADMISSION_AUDIT_PASS", flush=True)


if __name__ == "__main__":
    main()
