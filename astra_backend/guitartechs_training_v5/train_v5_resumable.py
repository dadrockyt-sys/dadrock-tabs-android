#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
import tempfile
import time

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import guitartechs_training_v2.train_v2 as base
from guitartechs_real_training import real_training as metrics_base
from guitartechs_training_v5.model import TemporalTabCNNV5
from guitartechs_training_v5.objective_decoder import (
    bounded_content_weights,
    decode_multitask,
    v5_sequence_loss,
)
from guitartechs_training_v2.sampling import (
    BATCH_SIZE,
    SEED,
    SEQUENCE_FRAMES,
    batch_epoch_plan,
    build_epoch_plan,
    supervised_frame_positions,
)

RESUME_SCHEMA = "astra-guitar-techs-v5-resume-state-v1"
CANDIDATE_ID = "astra_guitartechs_tabcnn_v5_temporal_multitask"
TOTAL_EPOCHS = 1000
CHECKPOINT_EVERY_EPOCHS = 20
FROZEN_SEGMENT_ENDS = (400, 800, 1000)
BASE_TRAINER_GIT_BLOB = "4db5add96c58a8e54868ea06dacb1da724675163"
SAMPLER_GIT_BLOB = "9eb62fde56f592646077afa1e0ff3013a5dc6560"
V5_MODEL_GIT_BLOB = "105aae211c3e9d806f3b1feb60052d51169832a4"
V5_OBJECTIVE_DECODER_GIT_BLOB = "908e08f2798669fb99048390d373ccc5cae6f70a"
V5_DESIGN_GIT_BLOB = "4ec63cb6dad38b74e553b83033930289a52daefe"
V5_SYNTHETIC_VERIFICATION_GIT_BLOB = "__V5_SYNTHETIC_VERIFICATION_BLOB__"
V5_AUTHORIZATION_GIT_BLOB = "__V5_AUTHORIZATION_BLOB__"
V4_ERROR_DECOMPOSITION_RESULT_GIT_BLOB = "15a31047147ef02d34b01a02436eee195695b231"
THRESHOLDS_RECEIPT_SHA256 = "fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15"
ALIGNMENT_ACCEPTED_KEYS_SHA256 = "f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc"


def _clone_state_dict(state):
    return {key: value.detach().cpu().clone() for key, value in state.items()}


def _rank(record):
    metrics = record["metrics"]
    return (
        metrics["f1"],
        metrics["completeness"],
        -metrics["abstentionRate"],
        -record["epoch"],
    )


def _rng_state():
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state().clone(),
    }


def _restore_rng_state(state):
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch"])


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _atomic_torch_save(payload, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    torch.save(payload, tmp)
    os.replace(tmp, path)
    return _sha256(path)


def _verified_torch_load(path, expected_sha256):
    actual = _sha256(path)
    if actual != expected_sha256:
        raise RuntimeError(
            f"resume-state SHA-256 mismatch: expected {expected_sha256}, got {actual}"
        )
    return torch.load(path, map_location="cpu")


def _validate_segment_end(end_epoch):
    if end_epoch not in FROZEN_SEGMENT_ENDS:
        raise ValueError(
            f"end epoch must be one of frozen segment boundaries {FROZEN_SEGMENT_ENDS}"
        )


def _setup_determinism():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))


def _new_model_and_optimizer(source_root):
    model = TemporalTabCNNV5(source_root)
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)
    return model, optimizer



def _content_name(category):
    return "PalmMute" if category == "techniques" else category


def _training_content_weights(rows):
    groups = {
        (row["performer"], row["category"], row["performanceKey"])
        for row in rows
    }
    counts = {name: 0 for name in ("chords", "scales", "singlenotes", "PalmMute")}
    for _, category, _ in groups:
        counts[_content_name(category)] += 1
    return bounded_content_weights(counts)


def _infer_v5(model, feat, chunk_frames=512):
    if feat.ndim != 2 or feat.shape[0] != 192:
        raise ValueError("expected 192 x T CQT feature array")
    pad = np.pad(
        feat,
        ((0, 0), (metrics_base.HALF_CONTEXT, metrics_base.HALF_CONTEXT)),
    )
    windows = np.lib.stride_tricks.sliding_window_view(
        pad, metrics_base.FRAME_CONTEXT, axis=1
    ).transpose(1, 0, 2)

    state_probabilities = np.empty(
        (feat.shape[1], base.NUM_STRINGS, base.NUM_CLASSES),
        dtype=np.float32,
    )
    onset_probabilities = np.empty(
        (feat.shape[1], base.NUM_STRINGS),
        dtype=np.float32,
    )
    activity_probabilities = np.empty(
        (feat.shape[1], base.NUM_STRINGS),
        dtype=np.float32,
    )

    hidden = None
    model.eval()
    with torch.no_grad():
        for lo in range(0, len(windows), chunk_frames):
            hi = min(len(windows), lo + chunk_frames)
            w = np.ascontiguousarray(windows[lo:hi])[None, :, None, :, :]
            output = model(torch.from_numpy(w), hidden)
            hidden = output["hidden"].detach()
            state = torch.softmax(
                output["tablature"].reshape(1, hi - lo, base.NUM_STRINGS, base.NUM_CLASSES),
                dim=-1,
            )[0].cpu().numpy().astype(np.float32)
            onset = torch.sigmoid(output["onset"])[0].cpu().numpy().astype(np.float32)
            activity = torch.sigmoid(output["activity"])[0].cpu().numpy().astype(np.float32)
            state_probabilities[lo:hi] = state
            onset_probabilities[lo:hi] = onset
            activity_probabilities[lo:hi] = activity

    return decode_multitask(
        state_probabilities,
        onset_probabilities,
        activity_probabilities,
    )


def _aggregate_metrics_v5(rows, model, data_dir):
    captures = []
    for row in rows:
        feat = np.load(row["_features"], mmap_mode="r")
        ref = np.load(row["_labels"], mmap_mode="r")
        pred = _infer_v5(model, feat)
        metrics = metrics_base.capture_metrics(pred, ref)
        metrics.update({
            "key": row["key"],
            "performance": (
                row["performer"] + "|" + row["category"] + "|" + row["performanceKey"]
            ),
            "category": row["category"],
        })
        captures.append(metrics)

    perfs = defaultdict(list)
    for capture in captures:
        perfs[capture["performance"]].append(capture)

    perf_metrics = []
    for key, views in sorted(perfs.items()):
        category = views[0]["category"]
        rec = {"performance": key, "category": category}
        for field in (
            "precision", "recall", "f1", "completeness",
            "frameAccuracy", "abstentionRate",
        ):
            rec[field] = float(np.mean([view[field] for view in views]))
        perf_metrics.append(rec)

    fold = {}
    for field in (
        "precision", "recall", "f1", "completeness",
        "frameAccuracy", "abstentionRate",
    ):
        fold[field] = float(np.mean([p[field] for p in perf_metrics]))
    fold["contentF1"] = {}
    for category in ("chords", "scales", "singlenotes", "techniques"):
        values = [p["f1"] for p in perf_metrics if p["category"] == category]
        name = _content_name(category)
        fold["contentF1"][name] = float(np.mean(values)) if values else 0.0
    fold["performanceCount"] = len(perf_metrics)
    fold["captureCount"] = len(captures)
    return fold


def _identity(args, group_count, validation_capture_count):
    return {
        "schema": RESUME_SCHEMA,
        "candidateId": CANDIDATE_ID,
        "fold": args.fold,
        "trainPerformer": args.train_performer,
        "validationPerformer": args.val_performer,
        "seed": SEED,
        "totalEpochs": TOTAL_EPOCHS,
        "sequenceFrames": SEQUENCE_FRAMES,
        "batchSequences": BATCH_SIZE,
        "microbatchSequences": base.MICROBATCH_SEQUENCES,
        "checkpointEveryEpochs": CHECKPOINT_EVERY_EPOCHS,
        "validationCheckpoints": base.CHECKPOINTS,
        "trainingPerformanceCount": group_count,
        "validationCaptureCount": validation_capture_count,
        "source": {
            "v2BaseTrainerGitBlob": BASE_TRAINER_GIT_BLOB,
            "v2SamplerGitBlob": SAMPLER_GIT_BLOB,
            "v5ModelGitBlob": V5_MODEL_GIT_BLOB,
            "v5ObjectiveDecoderGitBlob": V5_OBJECTIVE_DECODER_GIT_BLOB,
            "v5DesignGitBlob": V5_DESIGN_GIT_BLOB,
            "v5SyntheticVerificationGitBlob": V5_SYNTHETIC_VERIFICATION_GIT_BLOB,
            "v5AuthorizationGitBlob": V5_AUTHORIZATION_GIT_BLOB,
            "v4ErrorDecompositionResultGitBlob": V4_ERROR_DECOMPOSITION_RESULT_GIT_BLOB,
            "thresholdsReceiptSha256": THRESHOLDS_RECEIPT_SHA256,
            "alignmentAcceptedCaptureKeysSha256": ALIGNMENT_ACCEPTED_KEYS_SHA256,
            "budgetReceiptSha256": base.BUDGET_RECEIPT_SHA256,
            "v2FailureDiagnosisReceiptSha256": base.FAILURE_DIAGNOSIS_SHA256,
        },
        "guards": {
            "p3Opened": False,
            "publishedCheckpointLoaded": False,
            "paidComputeUsed": False,
            "customerDeliveryEligible": False,
        },
    }


def _validate_resume(payload, expected_identity, expected_start_epoch):
    for key, value in expected_identity.items():
        if payload.get(key) != value:
            raise RuntimeError(f"resume-state identity mismatch at {key}")
    if payload.get("nextEpoch") != expected_start_epoch:
        raise RuntimeError("resume-state nextEpoch does not match requested segment start")
    if expected_start_epoch <= 0 or expected_start_epoch >= TOTAL_EPOCHS:
        raise RuntimeError("resume-state start epoch is outside frozen bounds")
    if expected_start_epoch % CHECKPOINT_EVERY_EPOCHS:
        raise RuntimeError("resume-state boundary is not a frozen checkpoint boundary")


def _expected_steps(group_count, epochs):
    return math.ceil(group_count / BATCH_SIZE) * epochs


def _expected_supervised(group_count, epochs):
    return group_count * SEQUENCE_FRAMES * epochs


def _write_resume_receipt(path, payload, state_sha256):
    receipt = {
        "schema": "astra-guitar-techs-v5-resume-receipt-v1",
        "candidateId": payload["candidateId"],
        "fold": payload["fold"],
        "trainPerformer": payload["trainPerformer"],
        "validationPerformer": payload["validationPerformer"],
        "seed": payload["seed"],
        "nextEpoch": payload["nextEpoch"],
        "optimizerSteps": payload["optimizerSteps"],
        "supervisedFramePositions": payload["supervisedFramePositions"],
        "completedValidationCheckpoints": len(payload["checkpointSummaries"]),
        "resumeStateSha256": state_sha256,
        "source": payload["source"],
        "guards": payload["guards"],
    }
    Path(path).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return receipt


def train_segment(args):
    _validate_segment_end(args.end_epoch)
    _setup_determinism()

    rows = base.load_manifest(args.manifest, args.data_dir)
    if len(rows) != 256:
        raise RuntimeError("prepared capture count must be 256")
    counts = {p: sum(r["performer"] == p for r in rows) for p in ("P1", "P2")}
    if counts != {"P1": 136, "P2": 120}:
        raise RuntimeError("prepared performer count mismatch")

    train = [r for r in rows if r["performer"] == args.train_performer]
    val = [r for r in rows if r["performer"] == args.val_performer]
    row_by_key = {r["key"]: r for r in train}
    group_count = len({
        f"{r['performer']}|{r['category']}|{r['performanceKey']}" for r in train
    })
    if group_count != base.EXPECTED_TRAINING_GROUPS[args.train_performer]:
        raise RuntimeError("training performance-group count mismatch")

    balance = base.label_balance(train)
    content_weights = _training_content_weights(train)
    thresholds = json.loads(Path(args.thresholds).read_text())
    selection_rows = base.checkpoint_selection_rows(val)
    identity = _identity(args, group_count, len(val))

    model, optimizer = _new_model_and_optimizer(args.source_root)
    start_epoch = 0
    optimizer_steps = 0
    supervised_frames = 0
    checkpoint_summaries = []
    best_any = None
    best_qualified = None
    cumulative_wall_seconds = 0.0
    resume_chain = []

    if args.resume_in:
        if not args.resume_sha256:
            raise RuntimeError("--resume-sha256 is required with --resume-in")
        payload = _verified_torch_load(args.resume_in, args.resume_sha256)
        start_epoch = payload["nextEpoch"]
        _validate_resume(payload, identity, start_epoch)
        model.load_state_dict(payload["modelState"])
        optimizer.load_state_dict(payload["optimizerState"])
        optimizer_steps = payload["optimizerSteps"]
        supervised_frames = payload["supervisedFramePositions"]
        checkpoint_summaries = payload["checkpointSummaries"]
        best_any = payload["bestAny"]
        best_qualified = payload["bestQualified"]
        cumulative_wall_seconds = payload["cumulativeTrainingWallSeconds"]
        resume_chain = list(payload.get("resumeChain", [])) + [{
            "stateSha256": args.resume_sha256,
            "nextEpoch": start_epoch,
        }]
        _restore_rng_state(payload["rngState"])

    if args.end_epoch <= start_epoch:
        raise RuntimeError("segment end must be greater than resume start")

    if optimizer_steps != _expected_steps(group_count, start_epoch):
        raise RuntimeError("resume optimizer-step counter mismatch")
    if supervised_frames != _expected_supervised(group_count, start_epoch):
        raise RuntimeError("resume supervised-frame counter mismatch")
    if len(checkpoint_summaries) != start_epoch // CHECKPOINT_EVERY_EPOCHS:
        raise RuntimeError("resume checkpoint-history length mismatch")

    segment_started = time.time()
    for epoch in range(start_epoch, args.end_epoch):
        plan = build_epoch_plan(train, epoch=epoch)
        if len(plan) != group_count:
            raise RuntimeError("epoch plan does not contain every training performance exactly once")
        batches = batch_epoch_plan(plan, batch_size=BATCH_SIZE)
        epoch_losses = []

        model.train()
        for batch in batches:
            optimizer.zero_grad(set_to_none=True)
            for item in batch:
                x, y = base._sequence_tensors(row_by_key, item)
                from amt_tools.tools.constants import KEY_TABLATURE
                outputs = model(x)
                row = row_by_key[item["captureKey"]]
                content_weight = content_weights[_content_name(row["category"])]
                loss, _loss_parts = v5_sequence_loss(
                    outputs,
                    y,
                    content_weight=content_weight,
                )
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite V5 sequence loss")
                (loss / len(batch)).backward()
                epoch_losses.append(float(loss.detach()))
            optimizer.step()
            optimizer_steps += 1
            supervised_frames += supervised_frame_positions(batch)

        if (epoch + 1) % CHECKPOINT_EVERY_EPOCHS == 0:
            metrics = _aggregate_metrics_v5(selection_rows, model, args.data_dir)
            qualified = base.qualifies(metrics, thresholds)
            record = {
                "epoch": epoch + 1,
                "optimizerSteps": optimizer_steps,
                "meanSequenceLoss": float(np.mean(epoch_losses)),
                "qualified": qualified,
                "metrics": metrics,
                "stateSha256": base.state_sha256(model),
            }
            checkpoint_summaries.append(record)
            ranked = (_rank(record), record, _clone_state_dict(model.state_dict()))
            if best_any is None or ranked[0] > best_any[0]:
                best_any = ranked
            if qualified and (best_qualified is None or ranked[0] > best_qualified[0]):
                best_qualified = ranked
            print("V5_CHECKPOINT=" + json.dumps(record, sort_keys=True), flush=True)

    cumulative_wall_seconds += time.time() - segment_started

    if optimizer_steps != _expected_steps(group_count, args.end_epoch):
        raise RuntimeError("V5 optimizer-step exposure mismatch")
    if supervised_frames != _expected_supervised(group_count, args.end_epoch):
        raise RuntimeError("V5 supervised-frame exposure mismatch")
    if len(checkpoint_summaries) != args.end_epoch // CHECKPOINT_EVERY_EPOCHS:
        raise RuntimeError("V5 checkpoint count mismatch at segment boundary")

    if args.end_epoch < TOTAL_EPOCHS:
        if not args.resume_out or not args.resume_receipt_out:
            raise RuntimeError("intermediate segment requires resume outputs")
        payload = {
            **identity,
            "nextEpoch": args.end_epoch,
            "optimizerSteps": optimizer_steps,
            "supervisedFramePositions": supervised_frames,
            "checkpointSummaries": checkpoint_summaries,
            "bestAny": best_any,
            "bestQualified": best_qualified,
            "currentStateSha256": base.state_sha256(model),
            "modelState": _clone_state_dict(model.state_dict()),
            "optimizerState": optimizer.state_dict(),
            "rngState": _rng_state(),
            "cumulativeTrainingWallSeconds": cumulative_wall_seconds,
            "resumeChain": resume_chain,
        }
        state_sha = _atomic_torch_save(payload, args.resume_out)
        receipt = _write_resume_receipt(args.resume_receipt_out, payload, state_sha)
        print("V5_RESUME_STATE=" + json.dumps(receipt, sort_keys=True))
        return

    if len(checkpoint_summaries) != base.CHECKPOINTS:
        raise RuntimeError("final V5 checkpoint count mismatch")
    if not args.result_out or not args.model_out:
        raise RuntimeError("final segment requires result and model outputs")

    selected = best_qualified or best_any
    if selected is None:
        raise RuntimeError("no V5 checkpoint evaluated")
    _, selected_record, selected_state = selected
    model.load_state_dict(selected_state)

    full_metrics = _aggregate_metrics_v5(val, model, args.data_dir)
    full_qualified = base.qualifies(full_metrics, thresholds)

    out_model = Path(args.model_out)
    torch.save({
        "candidateId": CANDIDATE_ID,
        "fold": args.fold,
        "epoch": selected_record["epoch"],
        "optimizerSteps": selected_record["optimizerSteps"],
        "stateDict": selected_state,
        "stateSha256": selected_record["stateSha256"],
        "sourceRevision": "f50309ad06dc734ddae5e3a0eda756fca221e2e7",
        "budgetReceiptSha256": base.BUDGET_RECEIPT_SHA256,
        "resumableExecution": True,
        "resumeChain": resume_chain,
    }, out_model)

    receipt = {
        "schema": "astra-guitar-techs-real-training-fold-v5",
        "candidateId": CANDIDATE_ID,
        "fold": args.fold,
        "trainPerformer": args.train_performer,
        "validationPerformer": args.val_performer,
        "seed": SEED,
        "epochs": TOTAL_EPOCHS,
        "optimizerSteps": optimizer_steps,
        "sequenceFrames": SEQUENCE_FRAMES,
        "batchSequences": BATCH_SIZE,
        "microbatchSequences": base.MICROBATCH_SEQUENCES,
        "validationCheckpoints": len(checkpoint_summaries),
        "selectionSubsetQualified": best_qualified is not None,
        "selected": selected_record,
        "fullValidationMetrics": full_metrics,
        "fullValidationQualified": full_qualified,
        "checkpointSelectionCaptureKeys": [r["key"] for r in selection_rows],
        "checkpointSummaries": checkpoint_summaries,
        "preparedCaptureCounts": counts,
        "trainingPerformanceCount": group_count,
        "validationCaptureCount": len(val),
        "supervisedFramePositions": supervised_frames,
        "pretrainingLabelBalance": balance,
        "trainingContentWeights": content_weights,
        "v5ModelGitBlob": V5_MODEL_GIT_BLOB,
        "v5DesignGitBlob": V5_DESIGN_GIT_BLOB,
        "v5ObjectiveDecoderGitBlob": V5_OBJECTIVE_DECODER_GIT_BLOB,
        "v5AuthorizationGitBlob": V5_AUTHORIZATION_GIT_BLOB,
        "v4ErrorDecompositionResultGitBlob": V4_ERROR_DECOMPOSITION_RESULT_GIT_BLOB,
        "modelFileSha256": base.sha256_file(out_model),
        "wallSeconds": cumulative_wall_seconds,
        "budgetReceiptSha256": base.BUDGET_RECEIPT_SHA256,
        "failureDiagnosisReceiptSha256": base.FAILURE_DIAGNOSIS_SHA256,
        "resumableExecution": {
            "schema": RESUME_SCHEMA,
            "segmentEnds": list(FROZEN_SEGMENT_ENDS),
            "resumeChain": resume_chain,
        },
        "guards": {
            "p3Opened": False,
            "publishedCheckpointLoaded": False,
            "paidComputeUsed": False,
            "customerDeliveryEligible": False,
        },
    }
    Path(args.result_out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("V5_TRAINING_RESULT=" + json.dumps({
        "fold": args.fold,
        "selectionSubsetQualified": receipt["selectionSubsetQualified"],
        "fullValidationQualified": full_qualified,
        "epoch": selected_record["epoch"],
        "optimizerSteps": optimizer_steps,
        "supervisedFramePositions": supervised_frames,
        "selectionMetrics": selected_record["metrics"],
        "fullValidationMetrics": full_metrics,
        "modelFileSha256": receipt["modelFileSha256"],
    }, sort_keys=True))


def _nested_equal(a, b):
    if torch.is_tensor(a) and torch.is_tensor(b):
        return torch.equal(a, b)
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        return np.array_equal(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_nested_equal(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)) and isinstance(b, type(a)):
        return len(a) == len(b) and all(_nested_equal(x, y) for x, y in zip(a, b))
    return a == b


def resume_self_test(args):
    _setup_determinism()
    sys.path.insert(0, args.source_root)
    from amt_tools.tools.constants import KEY_TABLATURE

    feat = np.random.RandomState(SEED).normal(0, 1, size=(192, 260)).astype(np.float32)
    windows = base.sequence_windows(feat, 20, 220)
    labels = np.random.RandomState(SEED + 1).randint(
        0, base.NUM_CLASSES,
        size=(1, base.NUM_STRINGS, SEQUENCE_FRAMES),
        dtype=np.int64,
    )
    x = torch.from_numpy(windows[None, :, None, :, :])
    y = torch.from_numpy(labels)

    def step(model, optimizer):
        py_scale = random.random()
        np_scale = float(np.random.random())
        jitter = torch.rand_like(x) * 1e-5
        xx = x * (1.0 + (py_scale + np_scale) * 1e-6) + jitter
        optimizer.zero_grad(set_to_none=True)
        outputs = model(xx)
        loss, _ = v5_sequence_loss(outputs, y, content_weight=1.0)
        loss.backward()
        optimizer.step()

    _setup_determinism()
    continuous, continuous_opt = _new_model_and_optimizer(args.source_root)
    for _ in range(4):
        step(continuous, continuous_opt)
    continuous_model = _clone_state_dict(continuous.state_dict())
    continuous_optimizer = continuous_opt.state_dict()
    continuous_rng = _rng_state()

    _setup_determinism()
    split, split_opt = _new_model_and_optimizer(args.source_root)
    for _ in range(2):
        step(split, split_opt)

    with tempfile.TemporaryDirectory() as td:
        state_path = Path(td) / "resume.pt"
        payload = {
            "modelState": _clone_state_dict(split.state_dict()),
            "optimizerState": split_opt.state_dict(),
            "rngState": _rng_state(),
        }
        digest = _atomic_torch_save(payload, state_path)

        _setup_determinism()
        resumed, resumed_opt = _new_model_and_optimizer(args.source_root)
        restored = _verified_torch_load(state_path, digest)
        resumed.load_state_dict(restored["modelState"])
        resumed_opt.load_state_dict(restored["optimizerState"])
        _restore_rng_state(restored["rngState"])
        for _ in range(2):
            step(resumed, resumed_opt)

    if not _nested_equal(continuous_model, resumed.state_dict()):
        raise RuntimeError("resume self-test model state diverged")
    if not _nested_equal(continuous_optimizer, resumed_opt.state_dict()):
        raise RuntimeError("resume self-test optimizer state diverged")
    if not _nested_equal(continuous_rng, _rng_state()):
        raise RuntimeError("resume self-test RNG state diverged")

    print("V5_RESUME_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    smoke = sub.add_parser("resume-self-test")
    smoke.add_argument("--source-root", required=True)

    seg = sub.add_parser("train-segment")
    for name in (
        "source-root", "manifest", "data-dir", "thresholds", "fold",
        "train-performer", "val-performer",
    ):
        seg.add_argument("--" + name, required=True)
    seg.add_argument("--end-epoch", type=int, required=True)
    seg.add_argument("--resume-in")
    seg.add_argument("--resume-sha256")
    seg.add_argument("--resume-out")
    seg.add_argument("--resume-receipt-out")
    seg.add_argument("--result-out")
    seg.add_argument("--model-out")

    args = parser.parse_args()
    if args.cmd == "resume-self-test":
        resume_self_test(args)
    else:
        train_segment(args)


if __name__ == "__main__":
    main()
