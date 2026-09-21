#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import random
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from guitartechs_real_training.real_training import (
    MASK,
    NUM_CLASSES,
    NUM_STRINGS,
    aggregate_metrics,
    checkpoint_selection_rows,
    load_manifest,
    qualifies,
    sha256_file,
    state_sha256,
)
from guitartechs_training_v2.sampling import (
    BATCH_SIZE,
    SEED,
    SEQUENCE_FRAMES,
    batch_epoch_plan,
    build_epoch_plan,
    supervised_frame_positions,
)

EPOCHS = 1000
CHECKPOINTS = 50
CHECKPOINT_EVERY_EPOCHS = EPOCHS // CHECKPOINTS
MICROBATCH_SEQUENCES = 1
EXPECTED_TRAINING_GROUPS = {"P1": 41, "P2": 40}
BUDGET_RECEIPT_SHA256 = "8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430"
FAILURE_DIAGNOSIS_SHA256 = "c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848"


def sequence_windows(feat, start, end):
    if feat.ndim != 2 or feat.shape[0] != 192:
        raise ValueError("expected 192 x T CQT feature array")
    if not (0 <= start < end <= feat.shape[1]) or end - start != SEQUENCE_FRAMES:
        raise ValueError("invalid frozen 200-frame segment")
    half = 4
    padded = np.pad(feat, ((0, 0), (half, half)))
    windows = np.lib.stride_tricks.sliding_window_view(padded, 9, axis=1)
    windows = windows[:, start:end, :].transpose(1, 0, 2)
    return np.ascontiguousarray(windows, dtype=np.float32)


def sequence_loss(logits, labels):
    if labels.ndim != 3 or labels.shape[1] != NUM_STRINGS:
        raise ValueError("labels must be B x 6 x T")
    batch, _, frames = labels.shape
    if logits.shape != (batch, frames, NUM_STRINGS * NUM_CLASSES):
        raise ValueError("unexpected TabCNN output shape")

    x = logits.reshape(batch, frames, NUM_STRINGS, NUM_CLASSES)
    target = labels.transpose(1, 2).contiguous()
    target = target.clone()
    target[target == -1] = NUM_CLASSES - 1

    flat = F.cross_entropy(
        x.reshape(-1, NUM_CLASSES),
        target.reshape(-1),
        ignore_index=MASK,
        reduction="none",
    ).reshape(batch, frames, NUM_STRINGS)

    valid = target != MASK
    counts = valid.sum(dim=-1).clamp(min=1)
    frame_loss = (flat * valid).sum(dim=-1) * NUM_STRINGS / counts
    return frame_loss.mean()


def _content_name(category):
    return "PalmMute" if category == "techniques" else category


def label_balance(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[f"{row['performer']}|{row['category']}|{row['performanceKey']}"].append(row)

    view_priority = {"directinput": 0, "micamp": 1, "ego": 2, "exo": 3}
    canonical = []
    for group_key in sorted(grouped):
        choices = sorted(
            grouped[group_key],
            key=lambda r: (view_priority.get(r["captureView"], 99), r["key"]),
        )
        canonical.append(choices[0])

    total = mask = silence = active = 0
    per_string = [
        {"total": 0, "mask": 0, "silence": 0, "active": 0, "fretHistogram": [0] * 20}
        for _ in range(NUM_STRINGS)
    ]
    per_content = defaultdict(lambda: {"total": 0, "mask": 0, "silence": 0, "active": 0})

    for row in canonical:
        labels = np.load(row["_labels"], mmap_mode="r")
        if labels.ndim != 2 or labels.shape[0] != NUM_STRINGS:
            raise RuntimeError("invalid prepared label shape")
        content = _content_name(row["category"])
        total += int(labels.size)
        m = labels == MASK
        s = labels == -1
        a = labels >= 0
        mask += int(np.sum(m))
        silence += int(np.sum(s))
        active += int(np.sum(a))
        per_content[content]["total"] += int(labels.size)
        per_content[content]["mask"] += int(np.sum(m))
        per_content[content]["silence"] += int(np.sum(s))
        per_content[content]["active"] += int(np.sum(a))

        for string in range(NUM_STRINGS):
            arr = labels[string]
            rec = per_string[string]
            rec["total"] += int(arr.size)
            rec["mask"] += int(np.sum(arr == MASK))
            rec["silence"] += int(np.sum(arr == -1))
            rec["active"] += int(np.sum(arr >= 0))
            for fret in range(20):
                rec["fretHistogram"][fret] += int(np.sum(arr == fret))

    valid = total - mask
    if valid <= 0 or active <= 0:
        raise RuntimeError("label-balance sanity failure: no valid active labels")
    if any(rec["active"] <= 0 for rec in per_string):
        raise RuntimeError("label-balance sanity failure: inactive string")
    required_content = {"chords", "scales", "singlenotes", "PalmMute"}
    if set(per_content) != required_content or any(per_content[c]["active"] <= 0 for c in required_content):
        raise RuntimeError("label-balance sanity failure: missing active primary content")

    for rec in per_string:
        rec["maskFraction"] = rec["mask"] / rec["total"]
        valid_string = rec["total"] - rec["mask"]
        rec["silenceFractionOfValid"] = rec["silence"] / valid_string
        rec["activeFractionOfValid"] = rec["active"] / valid_string

    return {
        "canonicalPerformanceCount": len(canonical),
        "canonicalCaptureKeys": [row["key"] for row in canonical],
        "totalStringFrames": total,
        "maskFraction": mask / total,
        "silenceFractionOfValid": silence / valid,
        "activeFractionOfValid": active / valid,
        "perString": per_string,
        "perContent": dict(sorted(per_content.items())),
    }


def _sequence_tensors(row_by_key, item):
    row = row_by_key[item["captureKey"]]
    feat = np.load(row["_features"], mmap_mode="r")
    labels = np.load(row["_labels"], mmap_mode="r")
    start, end = item["startFrame"], item["endFrame"]
    x = sequence_windows(feat, start, end)
    y = np.asarray(labels[:, start:end], dtype=np.int64)
    return (
        torch.from_numpy(x[None, :, None, :, :]),
        torch.from_numpy(y[None, :, :]),
    )


def train_fold(args):
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    sys.path.insert(0, args.source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile
    from amt_tools.tools.constants import KEY_TABLATURE

    rows = load_manifest(args.manifest, args.data_dir)
    if len(rows) != 256:
        raise RuntimeError("prepared capture count must be 256")
    counts = {p: sum(r["performer"] == p for r in rows) for p in ("P1", "P2")}
    if counts != {"P1": 136, "P2": 120}:
        raise RuntimeError("prepared performer count mismatch")

    train = [r for r in rows if r["performer"] == args.train_performer]
    val = [r for r in rows if r["performer"] == args.val_performer]
    row_by_key = {r["key"]: r for r in train}
    group_count = len({f"{r['performer']}|{r['category']}|{r['performanceKey']}" for r in train})
    if group_count != EXPECTED_TRAINING_GROUPS[args.train_performer]:
        raise RuntimeError("training performance-group count mismatch")

    balance = label_balance(train)
    thresholds = json.loads(Path(args.thresholds).read_text())
    selection_rows = checkpoint_selection_rows(val)

    model = TabCNN(
        dim_in=192,
        profile=GuitarProfile(tuning=["E2", "A2", "D3", "G3", "B3", "E4"], num_frets=19),
        device="cpu",
    )
    optimizer = torch.optim.Adadelta(model.parameters(), lr=1.0)

    checkpoints = []
    best_qualified = None
    best_any = None
    optimizer_steps = 0
    supervised_frames = 0
    start_time = time.time()

    for epoch in range(EPOCHS):
        plan = build_epoch_plan(train, epoch=epoch)
        if len(plan) != group_count:
            raise RuntimeError("epoch plan does not contain every training performance exactly once")
        batches = batch_epoch_plan(plan, batch_size=BATCH_SIZE)
        epoch_losses = []

        model.train()
        for batch in batches:
            optimizer.zero_grad(set_to_none=True)
            for item in batch:
                x, y = _sequence_tensors(row_by_key, item)
                logits = model(x)[KEY_TABLATURE]
                loss = sequence_loss(logits, y)
                if not torch.isfinite(loss):
                    raise RuntimeError("nonfinite V2 sequence loss")
                (loss / len(batch)).backward()
                epoch_losses.append(float(loss.detach()))
            optimizer.step()
            optimizer_steps += 1
            supervised_frames += supervised_frame_positions(batch)

        if (epoch + 1) % CHECKPOINT_EVERY_EPOCHS == 0:
            metrics = aggregate_metrics(selection_rows, model, args.data_dir)
            qualified = qualifies(metrics, thresholds)
            record = {
                "epoch": epoch + 1,
                "optimizerSteps": optimizer_steps,
                "meanSequenceLoss": float(np.mean(epoch_losses)),
                "qualified": qualified,
                "metrics": metrics,
                "stateSha256": state_sha256(model),
            }
            checkpoints.append(record)
            rank = (metrics["f1"], metrics["completeness"], -metrics["abstentionRate"], -(epoch + 1))
            state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            if best_any is None or rank > best_any[0]:
                best_any = (rank, record, state)
            if qualified and (best_qualified is None or rank > best_qualified[0]):
                best_qualified = (rank, record, state)
            print("V2_CHECKPOINT=" + json.dumps(record, sort_keys=True), flush=True)

    if len(checkpoints) != CHECKPOINTS:
        raise RuntimeError("V2 checkpoint count mismatch")
    expected_supervised = group_count * SEQUENCE_FRAMES * EPOCHS
    if supervised_frames != expected_supervised:
        raise RuntimeError("V2 supervised-frame exposure mismatch")

    selected = best_qualified or best_any
    if selected is None:
        raise RuntimeError("no V2 checkpoint evaluated")
    _, selected_record, selected_state = selected
    model.load_state_dict(selected_state)

    full_metrics = aggregate_metrics(val, model, args.data_dir)
    full_qualified = qualifies(full_metrics, thresholds)

    out_model = Path(args.model_out)
    torch.save({
        "candidateId": "astra_guitartechs_tabcnn_v2",
        "fold": args.fold,
        "epoch": selected_record["epoch"],
        "optimizerSteps": selected_record["optimizerSteps"],
        "stateDict": selected_state,
        "stateSha256": selected_record["stateSha256"],
        "sourceRevision": "f50309ad06dc734ddae5e3a0eda756fca221e2e7",
        "budgetReceiptSha256": BUDGET_RECEIPT_SHA256,
    }, out_model)

    receipt = {
        "schema": "astra-guitar-techs-real-training-fold-v2",
        "candidateId": "astra_guitartechs_tabcnn_v2",
        "fold": args.fold,
        "trainPerformer": args.train_performer,
        "validationPerformer": args.val_performer,
        "seed": SEED,
        "epochs": EPOCHS,
        "optimizerSteps": optimizer_steps,
        "sequenceFrames": SEQUENCE_FRAMES,
        "batchSequences": BATCH_SIZE,
        "microbatchSequences": MICROBATCH_SEQUENCES,
        "validationCheckpoints": len(checkpoints),
        "selectionSubsetQualified": best_qualified is not None,
        "selected": selected_record,
        "fullValidationMetrics": full_metrics,
        "fullValidationQualified": full_qualified,
        "checkpointSelectionCaptureKeys": [r["key"] for r in selection_rows],
        "checkpointSummaries": checkpoints,
        "preparedCaptureCounts": counts,
        "trainingPerformanceCount": group_count,
        "validationCaptureCount": len(val),
        "supervisedFramePositions": supervised_frames,
        "pretrainingLabelBalance": balance,
        "modelFileSha256": sha256_file(out_model),
        "wallSeconds": time.time() - start_time,
        "budgetReceiptSha256": BUDGET_RECEIPT_SHA256,
        "failureDiagnosisReceiptSha256": FAILURE_DIAGNOSIS_SHA256,
        "guards": {
            "p3Opened": False,
            "publishedCheckpointLoaded": False,
            "paidComputeUsed": False,
            "customerDeliveryEligible": False,
        },
    }
    Path(args.result_out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("V2_TRAINING_RESULT=" + json.dumps({
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


def self_test(args):
    sys.path.insert(0, args.source_root)
    from amt_tools.models.tabcnn import TabCNN
    from amt_tools.tools.instrument import GuitarProfile
    from amt_tools.tools.constants import KEY_TABLATURE

    torch.manual_seed(SEED)
    model = TabCNN(
        dim_in=192,
        profile=GuitarProfile(tuning=["E2", "A2", "D3", "G3", "B3", "E4"], num_frets=19),
        device="cpu",
    )
    feat = np.random.RandomState(SEED).normal(0, 1, size=(192, 260)).astype(np.float32)
    windows = sequence_windows(feat, 20, 220)
    labels = np.random.RandomState(SEED + 1).randint(
        0, NUM_CLASSES, size=(1, NUM_STRINGS, SEQUENCE_FRAMES), dtype=np.int64
    )
    x = torch.from_numpy(windows[None, :, None, :, :])
    y = torch.from_numpy(labels)
    logits = model(x)[KEY_TABLATURE]
    assert logits.shape == (1, SEQUENCE_FRAMES, NUM_STRINGS * NUM_CLASSES)
    loss = sequence_loss(logits, y)
    assert torch.isfinite(loss)
    loss.backward()
    print("V2_SELF_TEST_PASS")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    test = sub.add_parser("self-test")
    test.add_argument("--source-root", required=True)

    train = sub.add_parser("train-fold")
    for name in (
        "source-root", "manifest", "data-dir", "thresholds", "fold",
        "train-performer", "val-performer", "result-out", "model-out",
    ):
        train.add_argument("--" + name, required=True)

    args = parser.parse_args()
    if args.cmd == "self-test":
        self_test(args)
    else:
        train_fold(args)


if __name__ == "__main__":
    main()
