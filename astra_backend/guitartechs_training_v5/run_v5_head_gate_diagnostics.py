#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from guitartechs_real_training import real_training as base
from guitartechs_training_v2.sampling import build_epoch_plan
from guitartechs_training_v5.model import (
    MAX_MIDI, MIN_MIDI, NUM_CLASSES, NUM_FRETS, NUM_PITCHES, NUM_STRINGS,
    OPEN_MIDI, SILENCE_CLASS, TemporalTabCNNV5,
)
from guitartechs_training_v5.objective_decoder import (
    ACTIVITY_CONTINUE_CONFIDENCE,
    ACTIVITY_START_CONFIDENCE,
    GAP_FRAMES,
    MIN_RUN_FRAMES,
    ONSET_START_CONFIDENCE,
    STATE_CONTINUE_CONFIDENCE,
    STATE_CONTINUE_VS_SILENCE_RATIO,
    STATE_START_CONFIDENCE,
    STATE_START_VS_SILENCE_RATIO,
    _merge_short_gaps,
    _prune_short_active_runs,
    decode_multitask,
)

CANDIDATE_ID = "astra_guitartechs_tabcnn_v5_temporal_multitask"
SOURCE_RUN_ID = 36115823434
EXPECTED_CAPTURE_COUNTS = {"P1": 136, "P2": 120}
CONTENT_NAMES = ("chords", "scales", "singlenotes", "PalmMute")
BINS = 100


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def content_name(category):
    return "PalmMute" if category == "techniques" else category


def new_model(source_root):
    return TemporalTabCNNV5(source_root)


def load_model(path, expected_sha, expected_fold, source_root):
    if sha256_file(path) != expected_sha:
        raise RuntimeError(f"model SHA mismatch for {expected_fold}")
    payload = torch.load(path, map_location="cpu")
    if payload.get("candidateId") != CANDIDATE_ID or payload.get("fold") != expected_fold:
        raise RuntimeError("frozen V5 model identity mismatch")
    model = new_model(source_root)
    model.load_state_dict(payload["stateDict"])
    if base.state_sha256(model) != payload.get("stateSha256"):
        raise RuntimeError("frozen V5 state hash mismatch")
    return model, payload


def infer_heads(model, feat, chunk_frames=512):
    if feat.ndim != 2 or feat.shape[0] != 192:
        raise ValueError("expected 192 x T CQT")
    pad = np.pad(feat, ((0, 0), (base.HALF_CONTEXT, base.HALF_CONTEXT)))
    windows = np.lib.stride_tricks.sliding_window_view(
        pad, base.FRAME_CONTEXT, axis=1
    ).transpose(1, 0, 2)
    frames = feat.shape[1]
    state = np.empty((frames, NUM_STRINGS, NUM_CLASSES), dtype=np.float32)
    onset = np.empty((frames, NUM_STRINGS), dtype=np.float32)
    activity = np.empty((frames, NUM_STRINGS), dtype=np.float32)
    pitch = np.empty((frames, NUM_PITCHES), dtype=np.float32)
    hidden = None
    model.eval()
    with torch.no_grad():
        for lo in range(0, frames, chunk_frames):
            hi = min(frames, lo + chunk_frames)
            w = np.ascontiguousarray(windows[lo:hi])[None, :, None, :, :]
            out = model(torch.from_numpy(w), hidden)
            hidden = out["hidden"].detach()
            state[lo:hi] = torch.softmax(
                out["tablature"].reshape(1, hi - lo, NUM_STRINGS, NUM_CLASSES),
                dim=-1,
            )[0].cpu().numpy()
            onset[lo:hi] = torch.sigmoid(out["onset"])[0].cpu().numpy()
            activity[lo:hi] = torch.sigmoid(out["activity"])[0].cpu().numpy()
            pitch[lo:hi] = torch.sigmoid(out["pitch"])[0].cpu().numpy()
    return state, onset, activity, pitch


def decode_ablation(state, onset, activity, *, use_onset, use_activity, use_state):
    frames = state.shape[0]
    decoded = np.full((frames, NUM_STRINGS), -1, dtype=np.int16)
    for string in range(NUM_STRINGS):
        current = -1
        for frame in range(frames):
            row = state[frame, string]
            silence = float(row[SILENCE_CLASS])
            best_fret = int(np.argmax(row[:NUM_FRETS]))
            best_active = float(row[best_fret])
            gates = []
            if use_onset:
                gates.append(float(onset[frame, string]) >= ONSET_START_CONFIDENCE)
            if use_activity:
                gates.append(float(activity[frame, string]) >= ACTIVITY_START_CONFIDENCE)
            if use_state:
                gates.append(
                    best_active >= STATE_START_CONFIDENCE
                    and best_active >= silence * STATE_START_VS_SILENCE_RATIO
                )
            can_start = all(gates) if gates else True

            if current >= 0:
                if can_start and best_fret != current:
                    current = best_fret
                    decoded[frame, string] = current
                    continue
                keep = float(row[current])
                if (
                    float(activity[frame, string]) >= ACTIVITY_CONTINUE_CONFIDENCE
                    and keep >= STATE_CONTINUE_CONFIDENCE
                    and keep >= silence * STATE_CONTINUE_VS_SILENCE_RATIO
                ):
                    decoded[frame, string] = current
                    continue
                current = -1
            if can_start:
                current = best_fret
                decoded[frame, string] = current
        decoded[:, string] = _prune_short_active_runs(
            _merge_short_gaps(decoded[:, string], GAP_FRAMES),
            MIN_RUN_FRAMES,
        )
    return decoded


def onset_masks(ref):
    x = ref.T
    valid = x != base.MASK
    active = valid & (x >= 0)
    onset_valid = np.zeros_like(valid, dtype=bool)
    onset = np.zeros_like(valid, dtype=bool)
    if len(x) > 1:
        onset_valid[1:] = valid[1:] & valid[:-1]
        onset[1:] = onset_valid[1:] & active[1:] & (
            (~active[:-1]) | (x[1:] != x[:-1])
        )
    return x, valid, active, onset_valid, onset


def update_hist(acc, scores, positive):
    idx = np.minimum(BINS - 1, np.floor(np.clip(scores, 0, 1) * BINS).astype(np.int64))
    pos = positive.astype(bool)
    if np.any(pos):
        acc["pos"] += np.bincount(idx[pos], minlength=BINS)
    if np.any(~pos):
        acc["neg"] += np.bincount(idx[~pos], minlength=BINS)


def finalize_hist(acc):
    pos = acc["pos"].astype(np.float64)
    neg = acc["neg"].astype(np.float64)
    p_total, n_total = pos.sum(), neg.sum()
    tp = np.cumsum(pos[::-1])
    fp = np.cumsum(neg[::-1])
    tpr = tp / p_total if p_total else np.zeros_like(tp)
    fpr = fp / n_total if n_total else np.zeros_like(fp)
    precision = tp / np.maximum(tp + fp, 1.0)
    recall = tpr
    auroc = float(np.trapz(tpr, fpr)) if p_total and n_total else None
    auprc = float(np.trapz(precision[::-1], recall[::-1])) if p_total else None
    return {
        "positiveCount": int(p_total),
        "negativeCount": int(n_total),
        "approxAUROC100Bins": auroc,
        "approxAUPRC100Bins": auprc,
    }


def empty_gate_counts():
    names = (
        "referenceOnsets", "onsetPass", "activityPass", "statePass",
        "stateIdentityCorrect", "onsetActivityPass", "onsetStatePass",
        "activityStatePass", "fullGatePass", "fullExactIdentityPass",
    )
    return {k: 0 for k in names}


def add_gate_counts(acc, ref_state, onset_mask, state, onset, activity):
    positions = np.argwhere(onset_mask)
    for frame, string in positions:
        fret = int(ref_state[frame, string])
        row = state[frame, string]
        silence = float(row[SILENCE_CLASS])
        best_fret = int(np.argmax(row[:NUM_FRETS]))
        best_active = float(row[best_fret])
        op = float(onset[frame, string]) >= ONSET_START_CONFIDENCE
        ap = float(activity[frame, string]) >= ACTIVITY_START_CONFIDENCE
        sp = (
            best_active >= STATE_START_CONFIDENCE
            and best_active >= silence * STATE_START_VS_SILENCE_RATIO
        )
        ident = best_fret == fret
        acc["referenceOnsets"] += 1
        acc["onsetPass"] += int(op)
        acc["activityPass"] += int(ap)
        acc["statePass"] += int(sp)
        acc["stateIdentityCorrect"] += int(ident)
        acc["onsetActivityPass"] += int(op and ap)
        acc["onsetStatePass"] += int(op and sp)
        acc["activityStatePass"] += int(ap and sp)
        acc["fullGatePass"] += int(op and ap and sp)
        acc["fullExactIdentityPass"] += int(op and ap and sp and ident)


def finalize_gate_counts(acc):
    n = acc["referenceOnsets"]
    out = dict(acc)
    for k, v in acc.items():
        if k != "referenceOnsets":
            out[k + "Rate"] = (v / n) if n else 0.0
    return out


def aggregate_performance(captures):
    perfs = defaultdict(list)
    for c in captures:
        perfs[c["performance"]].append(c)
    perf = []
    fields = ("precision","recall","f1","completeness","frameAccuracy","abstentionRate")
    for key, views in sorted(perfs.items()):
        rec = {"performance": key, "category": views[0]["category"]}
        for f in fields:
            rec[f] = float(np.mean([v[f] for v in views]))
        perf.append(rec)
    fold = {f: float(np.mean([p[f] for p in perf])) for f in fields}
    fold["contentF1"] = {}
    for category in ("chords","scales","singlenotes","techniques"):
        vals = [p["f1"] for p in perf if p["category"] == category]
        fold["contentF1"][content_name(category)] = float(np.mean(vals)) if vals else 0.0
    fold["performanceCount"] = len(perf)
    fold["captureCount"] = len(captures)
    return fold


def assert_metrics(actual, expected, tol=1e-12):
    for f in ("precision","recall","f1","completeness","frameAccuracy","abstentionRate"):
        if abs(float(actual[f]) - float(expected[f])) > tol:
            raise RuntimeError(f"frozen V5 metric mismatch at {f}: {actual[f]} vs {expected[f]}")
    for c in CONTENT_NAMES:
        if abs(float(actual["contentF1"][c]) - float(expected["contentF1"][c])) > tol:
            raise RuntimeError(f"frozen V5 content metric mismatch at {c}")


def pitch_targets(ref_state, valid):
    frames = ref_state.shape[0]
    target = np.zeros((frames, NUM_PITCHES), dtype=bool)
    frame_valid = valid.all(axis=1)
    for s in range(NUM_STRINGS):
        fret = ref_state[:, s]
        active = frame_valid & (fret >= 0) & (fret < NUM_FRETS)
        where = np.flatnonzero(active)
        if len(where):
            pitch_idx = OPEN_MIDI[s] + fret[where] - MIN_MIDI
            target[where, pitch_idx.astype(np.int64)] = True
    return target, frame_valid


def sequence_boundary_diagnostic(rows, performer):
    train = [r for r in rows if r["performer"] == performer]
    by_key = {r["key"]: r for r in train}
    label_cache = {}
    total_onsets = 0
    boundary_onsets = 0
    sequence_count = 0
    for epoch in range(1000):
        for item in build_epoch_plan(train, epoch=epoch):
            sequence_count += 1
            key = item["captureKey"]
            if key not in label_cache:
                label_cache[key] = np.load(by_key[key]["_labels"], mmap_mode="r")
            ref = label_cache[key]
            start, end = item["startFrame"], item["endFrame"]
            for s in range(NUM_STRINGS):
                r = ref[s]
                for frame in range(start, end):
                    if frame <= 0 or r[frame] < 0 or r[frame] == base.MASK:
                        continue
                    prev = r[frame - 1]
                    if prev == base.MASK:
                        continue
                    is_onset = prev < 0 or prev != r[frame]
                    if is_onset:
                        total_onsets += 1
                        if frame == start:
                            boundary_onsets += 1
    return {
        "trainingPerformer": performer,
        "sequenceCount": sequence_count,
        "referenceOnsetsInsideSampledSequences": total_onsets,
        "referenceOnsetsAtSequenceFirstFrameUnsup": boundary_onsets,
        "boundaryLossFraction": boundary_onsets / total_onsets if total_onsets else 0.0,
    }


def diagnose_fold(rows, model, validation_performer, expected_metrics):
    selected = [r for r in rows if r["performer"] == validation_performer]
    frozen_caps = []
    ablation_caps = {
        "onsetOnly": [], "activityOnly": [], "stateOnly": [],
        "onsetActivity": [], "onsetState": [], "activityState": [], "full": [],
    }
    head_hist = {
        "onset": {"pos": np.zeros(BINS, dtype=np.int64), "neg": np.zeros(BINS, dtype=np.int64)},
        "activity": {"pos": np.zeros(BINS, dtype=np.int64), "neg": np.zeros(BINS, dtype=np.int64)},
    }
    pitch_tp = pitch_fp = pitch_fn = 0
    gate = empty_gate_counts()
    per_content_gate = {name: empty_gate_counts() for name in CONTENT_NAMES}

    for row in selected:
        feat = np.load(row["_features"], mmap_mode="r")
        ref = np.load(row["_labels"], mmap_mode="r")
        state, onset, activity, pitch = infer_heads(model, feat)
        full = decode_multitask(state, onset, activity)

        meta = {
            "key": row["key"],
            "performance": row["performer"] + "|" + row["category"] + "|" + row["performanceKey"],
            "category": row["category"],
        }
        m = base.capture_metrics(full, ref); m.update(meta); frozen_caps.append(m)

        specs = {
            "onsetOnly": (True, False, False),
            "activityOnly": (False, True, False),
            "stateOnly": (False, False, True),
            "onsetActivity": (True, True, False),
            "onsetState": (True, False, True),
            "activityState": (False, True, True),
            "full": (True, True, True),
        }
        for name, flags in specs.items():
            pred = full if name == "full" else decode_ablation(
                state, onset, activity,
                use_onset=flags[0], use_activity=flags[1], use_state=flags[2],
            )
            mm = base.capture_metrics(pred, ref); mm.update(meta); ablation_caps[name].append(mm)

        ref_state, valid, active, onset_valid, ref_onset = onset_masks(ref)
        update_hist(head_hist["onset"], onset[onset_valid], ref_onset[onset_valid])
        update_hist(head_hist["activity"], activity[valid], active[valid])
        add_gate_counts(gate, ref_state, ref_onset, state, onset, activity)
        add_gate_counts(per_content_gate[content_name(row["category"])], ref_state, ref_onset, state, onset, activity)

        pt, pv = pitch_targets(ref_state, valid)
        pred_pitch = pitch >= 0.50
        pitch_tp += int(np.sum(pred_pitch[pv] & pt[pv]))
        pitch_fp += int(np.sum(pred_pitch[pv] & ~pt[pv]))
        pitch_fn += int(np.sum(~pred_pitch[pv] & pt[pv]))

    reproduced = aggregate_performance(frozen_caps)
    assert_metrics(reproduced, expected_metrics)
    pitch_precision = pitch_tp / (pitch_tp + pitch_fp) if pitch_tp + pitch_fp else 0.0
    pitch_recall = pitch_tp / (pitch_tp + pitch_fn) if pitch_tp + pitch_fn else 0.0
    pitch_f1 = 2*pitch_precision*pitch_recall/(pitch_precision+pitch_recall) if pitch_precision+pitch_recall else 0.0
    return {
        "validationPerformer": validation_performer,
        "frozenMetricReproduction": {"passed": True, "metrics": reproduced},
        "headDiscrimination": {
            "onset": finalize_hist(head_hist["onset"]),
            "activity": finalize_hist(head_hist["activity"]),
            "pitchThreshold050Micro": {
                "truePositive": pitch_tp, "falsePositive": pitch_fp, "falseNegative": pitch_fn,
                "precision": pitch_precision, "recall": pitch_recall, "f1": pitch_f1,
            },
        },
        "trueOnsetGateAttribution": finalize_gate_counts(gate),
        "perContentTrueOnsetGateAttribution": {
            k: finalize_gate_counts(v) for k, v in per_content_gate.items()
        },
        "diagnosticStartGateAblationsPerformanceMacro": {
            k: aggregate_performance(v) for k, v in ablation_caps.items()
        },
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("source-root","manifest","data-dir","development-result","p1-model","p1-result","p2-model","p2-result","out"):
        p.add_argument("--" + name, required=True)
    args = p.parse_args()

    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(4)
    development = json.loads(Path(args.development_result).read_text())
    if development["sourceRun"]["runId"] != SOURCE_RUN_ID or development["decision"]["status"] != "FAIL":
        raise RuntimeError("unexpected frozen V5 result identity")

    rows = base.load_manifest(args.manifest, args.data_dir)
    if len(rows) != 256:
        raise RuntimeError("diagnostic manifest must contain exact 256 paths")
    counts = {p: sum(r["performer"] == p for r in rows) for p in ("P1","P2")}
    if counts != EXPECTED_CAPTURE_COUNTS:
        raise RuntimeError(f"performer counts changed: {counts}")

    specs = [
        ("p1-train-p2-validate","P2",args.p1_model,args.p1_result,development["folds"]["p1-train-p2-validate"]),
        ("p2-train-p1-validate","P1",args.p2_model,args.p2_result,development["folds"]["p2-train-p1-validate"]),
    ]
    folds = {}
    selected_task_log_vars = {}
    for fold, performer, model_path, result_path, frozen in specs:
        if sha256_file(result_path) != frozen["resultJsonSha256"]:
            raise RuntimeError(f"result SHA mismatch for {fold}")
        tr = json.loads(Path(result_path).read_text())
        if tr.get("fold") != fold or tr.get("guards",{}).get("p3Opened") is not False:
            raise RuntimeError("training receipt identity/guard mismatch")
        model, payload = load_model(model_path, frozen["modelSha256"], fold, args.source_root)
        if int(payload.get("epoch",-1)) != int(frozen["selectedCheckpointEpoch"]):
            raise RuntimeError("selected epoch mismatch")
        folds[fold] = diagnose_fold(rows, model, performer, frozen["fullValidationMetrics"])
        task = payload["stateDict"].get("task_log_vars")
        selected_task_log_vars[fold] = [float(x) for x in task.cpu().tolist()] if task is not None else None

    result = {
        "schema":"astra-guitar-techs-v5-head-gate-decomposition-v1",
        "date":"2026-09-26",
        "sourceRunId":SOURCE_RUN_ID,
        "candidateId":CANDIDATE_ID,
        "evidenceBoundary":"P1/P2 frozen V5 evidence only; zero optimizer steps; P3 sealed.",
        "sourceIdentities":{
            "developmentResultSha256":sha256_file(args.development_result),
            "manifestCaptureCounts":counts,
            "modelGitBlob":"105aae211c3e9d806f3b1feb60052d51169832a4",
            "objectiveDecoderGitBlob":"fc9fbd9704a0d6b30f9ee1023af3ec5ae979de16",
            "trainerGitBlob":"685c43d3887a76d01b839f601db1a8eb624d4dee",
        },
        "frozenGate":{
            "onsetStartConfidence":ONSET_START_CONFIDENCE,
            "activityStartConfidence":ACTIVITY_START_CONFIDENCE,
            "stateStartConfidence":STATE_START_CONFIDENCE,
            "stateStartVsSilenceRatio":STATE_START_VS_SILENCE_RATIO,
        },
        "folds":folds,
        "trainingSequenceBoundaryOnsetSupervision":{
            "p1Train":sequence_boundary_diagnostic(rows,"P1"),
            "p2Train":sequence_boundary_diagnostic(rows,"P2"),
        },
        "selectedTaskLogVars":selected_task_log_vars,
        "guards":{
            "optimizerStepsExecuted":0,
            "modelWeightsModified":False,
            "thresholdsRetuned":False,
            "alignmentAllowlistChanged":False,
            "p3Opened":False,
            "paidComputeUsed":False,
            "customerDeliveryEligible":False,
            "mainOrProductionModified":False,
        },
    }
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("V5_HEAD_GATE_DECOMPOSITION_PASS")
    print(json.dumps({
        "folds": {k: {
            "headDiscrimination": v["headDiscrimination"],
            "trueOnsetGateAttribution": v["trueOnsetGateAttribution"],
            "ablations": v["diagnosticStartGateAblationsPerformanceMacro"],
        } for k,v in folds.items()},
        "sequenceBoundary": result["trainingSequenceBoundaryOnsetSupervision"],
        "guards": result["guards"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
