#!/usr/bin/env python3
"""One bounded training-only tiny-fit candidate for Astra event-contract V2.

This module is intentionally separate from V1-V5. It cannot run more than four
P1 examples, 200 frames/example or 200 optimizer steps. It uses explicit source
onsets, not state-change-derived onset targets, and its decoder can emit a new
event for a same-string/same-fret reattack.
"""
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
import time
import zipfile

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(HERE / "evaluation") not in sys.path:
    sys.path.insert(0, str(HERE / "evaluation"))

from evaluation.prepared_event_adapter_v1 import (
    MASK,
    prepare_event_crop,
    select_training_crop,
    source_events_from_notes,
)
from evaluation.event_contract_v2 import Event, score_events

SCHEMA = "astra-tiny-fit-pilot-v1"
SEED = 20260921
NUM_STRINGS = 6
NUM_FRETS = 20
NUM_CLASSES = 21
SILENCE_CLASS = 20
FEATURE_DIM = 192
HIDDEN_DIM = 128

MAX_EXAMPLES = 4
MAX_FRAMES_PER_EXAMPLE = 200
MAX_OPTIMIZER_STEPS = 200
MAX_TRAIN_EVAL_SECONDS = 2700
MAX_ENTIRE_JOB_SECONDS = 3600
MAX_CANDIDATE_DESIGNS = 1

STATE_LOSS_WEIGHT = 1.0
ONSET_LOSS_WEIGHT = 4.0
STATE_ACTIVE_WEIGHT = 1.5
ONSET_POS_WEIGHT = 8.0
STATE_ACTIVE_THRESHOLD = 0.50
ONSET_THRESHOLD = 0.50
OPTIMIZER = "Adam"
LEARNING_RATE = 0.01

PRIMARY_CONTENT = ("chords", "scales", "singlenotes", "techniques")
VIEW_PRIORITY = {"directinput": 0, "micamp": 1, "ego": 2, "exo": 3}

FROZEN_CAPTURE_KEYS = (
    "P1|chords|Drop3_7|directinput",
    "P1|scales|Ab|directinput",
    "P1|singlenotes|allsinglenotes|directinput",
    "P1|techniques|PalmMute|directinput",
)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_json(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def _performance_key_from_path(path):
    path = Path(path)
    stem = path.stem
    parent = path.parent.name
    for prefix in (parent + "_", "midi_", "directinput_", "micamp_", "ego_", "exo_"):
        if stem.lower().startswith(prefix.lower()) and len(stem) > len(prefix):
            return stem[len(prefix):]
    return stem


def extract_selected_source(archive_path, *, capture_key, output_dir):
    """Extract exactly one selected MIDI and one selected audio member from a pinned ZIP.

    ZIP member names may be inspected, but unrelated media bytes are never extracted.
    The enclosing workflow must verify the full archive hash before calling this helper.
    """
    if capture_key not in FROZEN_CAPTURE_KEYS:
        raise ValueError("capture key is outside frozen pilot selection")
    performer, category, performance, view = capture_key.split("|")
    if performer != "P1":
        raise ValueError("pilot source extraction is P1 only")
    archive = Path(archive_path)
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    midi = []
    audio = []
    with zipfile.ZipFile(archive) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            member = Path(info.filename)
            if "__MACOSX" in member.parts or member.name == ".DS_Store" or member.name.startswith("._"):
                continue
            if any(part in {"", ".", ".."} for part in member.parts):
                raise RuntimeError("unsafe archive member path")
            suffix = member.suffix.lower()
            if _performance_key_from_path(member) != performance:
                continue
            if suffix in (".mid", ".midi"):
                midi.append(info)
            elif suffix in (".wav", ".mp3") and member.parent.name == view:
                audio.append(info)
        if len(midi) != 1 or len(audio) != 1:
            raise RuntimeError(
                f"selected archive source ambiguity: midi={len(midi)} audio={len(audio)}"
            )
        outputs = []
        for info, parent in ((midi[0], "midi"), (audio[0], view)):
            dest_dir = root / parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / Path(info.filename).name
            if dest.exists():
                raise RuntimeError("selected extraction destination already exists")
            with zf.open(info, "r") as src, dest.open("wb") as dst:
                while True:
                    block = src.read(1024 * 1024)
                    if not block:
                        break
                    dst.write(block)
            outputs.append({
                "member": info.filename,
                "path": str(dest),
                "sha256": _sha256_file(dest),
                "bytes": dest.stat().st_size,
            })
    receipt = {
        "schema": "astra-tiny-fit-selected-source-v1",
        "captureKey": capture_key,
        "archive": archive.name,
        "selectedMembers": outputs,
        "unrelatedMediaExtracted": False,
        "customerDeliveryEligible": False,
    }
    print("TINY_FIT_SELECTED_SOURCE=" + json.dumps(receipt, sort_keys=True))
    return receipt


def set_determinism():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))


def select_pilot_capture_keys(corrections):
    """Metadata-only selection: one canonical P1 view in each primary content."""
    if not isinstance(corrections, dict):
        raise ValueError("corrections must be a capture-key mapping")
    grouped = defaultdict(list)
    for key in corrections:
        parts = key.split("|")
        if len(parts) != 4:
            raise ValueError("invalid alignment capture key")
        performer, category, performance, view = parts
        if performer != "P1" or category not in PRIMARY_CONTENT:
            continue
        grouped[(category, performance)].append((view, key))

    selected = []
    for category in PRIMARY_CONTENT:
        performances = sorted(perf for (cat, perf) in grouped if cat == category)
        if not performances:
            raise ValueError("missing P1 primary content " + category)
        performance = performances[0]
        views = sorted(
            grouped[(category, performance)],
            key=lambda row: (VIEW_PRIORITY.get(row[0], 99), row[0], row[1]),
        )
        selected.append(views[0][1])
    return tuple(selected)


class TinyEventFitModel(nn.Module):
    """Single frozen tiny candidate: per-frame MLP + state and onset heads."""

    def __init__(self):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(FEATURE_DIM, HIDDEN_DIM),
            nn.ReLU(),
        )
        self.state_head = nn.Linear(HIDDEN_DIM, NUM_STRINGS * NUM_CLASSES)
        self.onset_head = nn.Linear(HIDDEN_DIM, NUM_STRINGS)

    def forward(self, features):
        if features.ndim != 3 or features.shape[-1] != FEATURE_DIM:
            raise ValueError("features must be B x T x 192")
        hidden = self.encoder(features)
        return {
            "state": self.state_head(hidden),
            "onset": self.onset_head(hidden),
        }


def explicit_event_loss(outputs, state_targets, onset_targets):
    """Fixed two-head objective using prepared source onsets verbatim."""
    if state_targets.ndim != 3 or state_targets.shape[1] != NUM_STRINGS:
        raise ValueError("state targets must be B x 6 x T")
    if onset_targets.shape != state_targets.shape:
        raise ValueError("onset targets must match state targets")
    batch, _, frames = state_targets.shape
    state_logits = outputs["state"]
    onset_logits = outputs["onset"]
    if state_logits.shape != (batch, frames, NUM_STRINGS * NUM_CLASSES):
        raise ValueError("unexpected state output shape")
    if onset_logits.shape != (batch, frames, NUM_STRINGS):
        raise ValueError("unexpected onset output shape")

    target_state = state_targets.transpose(1, 2).contiguous().clone()
    target_state[target_state == -1] = SILENCE_CLASS
    invalid = (target_state != MASK) & ((target_state < 0) | (target_state >= NUM_CLASSES))
    if torch.any(invalid):
        raise ValueError("invalid state target")

    state_raw = F.cross_entropy(
        state_logits.reshape(-1, NUM_CLASSES),
        target_state.reshape(-1),
        ignore_index=MASK,
        reduction="none",
    ).reshape(batch, frames, NUM_STRINGS)
    state_valid = target_state != MASK
    state_active = state_valid & (target_state != SILENCE_CLASS)
    state_weight = torch.ones_like(state_raw)
    state_weight[state_active] = STATE_ACTIVE_WEIGHT
    state_weight *= state_valid
    state_loss = (state_raw * state_weight).sum() / state_weight.sum().clamp(min=1.0)

    onset = onset_targets.transpose(1, 2).contiguous()
    onset_valid = onset != MASK
    if torch.any(onset_valid & ((onset < 0) | (onset > 1))):
        raise ValueError("invalid explicit onset target")
    onset_target = torch.where(onset_valid, onset, torch.zeros_like(onset)).to(torch.float32)
    onset_raw = F.binary_cross_entropy_with_logits(
        onset_logits,
        onset_target,
        pos_weight=torch.tensor(ONSET_POS_WEIGHT, dtype=onset_logits.dtype, device=onset_logits.device),
        reduction="none",
    )
    onset_loss = (
        onset_raw[onset_valid].mean()
        if torch.any(onset_valid)
        else onset_logits.new_tensor(0.0)
    )
    total = STATE_LOSS_WEIGHT * state_loss + ONSET_LOSS_WEIGHT * onset_loss
    return total, {"state": state_loss, "onset": onset_loss}


def decode_event_list(
    state_logits,
    onset_logits,
    *,
    hop_seconds,
    state_active_threshold=STATE_ACTIVE_THRESHOLD,
    onset_threshold=ONSET_THRESHOLD,
    id_prefix="pred",
):
    """Decode explicit events; an onset can split an active same-fret run."""
    if isinstance(state_logits, torch.Tensor):
        state_logits = state_logits.detach().cpu()
    if isinstance(onset_logits, torch.Tensor):
        onset_logits = onset_logits.detach().cpu()
    if state_logits.ndim != 2 or state_logits.shape[1] != NUM_STRINGS * NUM_CLASSES:
        raise ValueError("state logits must be T x 126")
    if onset_logits.shape != (state_logits.shape[0], NUM_STRINGS):
        raise ValueError("onset logits must be T x 6")
    hop = float(hop_seconds)
    if not math.isfinite(hop) or hop <= 0:
        raise ValueError("hop_seconds must be positive")

    state_prob = torch.softmax(state_logits.reshape(-1, NUM_STRINGS, NUM_CLASSES), dim=-1).numpy()
    onset_prob = torch.sigmoid(onset_logits).numpy()
    frames = state_prob.shape[0]
    events = []
    serial = [0] * NUM_STRINGS

    for string in range(NUM_STRINGS):
        current = None

        def close(frame):
            nonlocal current
            if current is None:
                return
            end = frame * hop
            if end <= current["start"]:
                end = current["start"] + hop
            events.append(Event(
                current["id"], string, current["fret"], current["start"], end
            ))
            current = None

        for frame in range(frames):
            row = state_prob[frame, string]
            fret = int(np.argmax(row[:NUM_FRETS]))
            active_prob = float(row[fret])
            silence_prob = float(row[SILENCE_CLASS])
            active_ok = active_prob >= state_active_threshold and active_prob > silence_prob
            onset_ok = float(onset_prob[frame, string]) >= onset_threshold

            if current is not None:
                # A source-like onset is allowed to reattack the same fret.
                if onset_ok and active_ok:
                    close(frame)
                    serial[string] += 1
                    current = {
                        "id": f"{id_prefix}:s{string}:{serial[string]}",
                        "fret": fret,
                        "start": frame * hop,
                    }
                    continue
                if not active_ok or fret != current["fret"]:
                    close(frame)
                    # Fret changes without an admitted onset do not invent events.
                    continue

            if current is None and onset_ok and active_ok:
                serial[string] += 1
                current = {
                    "id": f"{id_prefix}:s{string}:{serial[string]}",
                    "fret": fret,
                    "start": frame * hop,
                }

        close(frames)

    return sorted(events, key=lambda e: (e.string, e.start, e.fret, e.id))


def onset_admission_recall(state_logits, onset_logits, state_targets, onset_targets):
    if isinstance(state_logits, torch.Tensor):
        state_logits = state_logits.detach().cpu()
    if isinstance(onset_logits, torch.Tensor):
        onset_logits = onset_logits.detach().cpu()
    state_prob = torch.softmax(state_logits.reshape(-1, NUM_STRINGS, NUM_CLASSES), dim=-1).numpy()
    onset_prob = torch.sigmoid(onset_logits).numpy()
    state = np.asarray(state_targets)
    onset = np.asarray(onset_targets)
    if state.shape != (NUM_STRINGS, state_prob.shape[0]) or onset.shape != state.shape:
        raise ValueError("target shape mismatch")
    total = admitted = 0
    for string in range(NUM_STRINGS):
        for frame in range(state.shape[1]):
            if onset[string, frame] != 1:
                continue
            fret = int(state[string, frame])
            if not 0 <= fret < NUM_FRETS:
                continue
            total += 1
            row = state_prob[frame, string]
            best = int(np.argmax(row[:NUM_FRETS]))
            if (
                onset_prob[frame, string] >= ONSET_THRESHOLD
                and best == fret
                and row[best] >= STATE_ACTIVE_THRESHOLD
                and row[best] > row[SILENCE_CLASS]
            ):
                admitted += 1
    return admitted / total if total else None


def repeated_reference_events(events):
    groups = defaultdict(list)
    for event in sorted(events, key=lambda e: (e.string, e.fret, e.start, e.id)):
        groups[(event.string, event.fret)].append(event)
    return [event for group in groups.values() for event in group[1:]]


def validate_training_arrays(features, state_targets, onset_targets):
    if features.ndim != 3 or features.shape[-1] != FEATURE_DIM:
        raise ValueError("features must be B x T x 192")
    batch, frames, _ = features.shape
    if batch <= 0 or batch > MAX_EXAMPLES:
        raise ValueError("pilot example cap exceeded")
    if frames <= 0 or frames > MAX_FRAMES_PER_EXAMPLE:
        raise ValueError("pilot frame cap exceeded")
    if state_targets.shape != (batch, NUM_STRINGS, frames):
        raise ValueError("state target shape mismatch")
    if onset_targets.shape != state_targets.shape:
        raise ValueError("onset target shape mismatch")


def fit_tiny_model(
    features,
    state_targets,
    onset_targets,
    *,
    requested_steps=MAX_OPTIMIZER_STEPS,
    wall_seconds_limit=MAX_TRAIN_EVAL_SECONDS,
    clock=time.monotonic,
):
    """Fit the one frozen candidate while enforcing non-negotiable caps."""
    if type(requested_steps) is not int or requested_steps <= 0 or requested_steps > MAX_OPTIMIZER_STEPS:
        raise ValueError("requested optimizer steps exceed frozen pilot cap")
    if (
        isinstance(wall_seconds_limit, bool)
        or not isinstance(wall_seconds_limit, (int, float))
        or wall_seconds_limit <= 0
        or wall_seconds_limit > MAX_TRAIN_EVAL_SECONDS
    ):
        raise ValueError("wall_seconds_limit exceeds frozen pilot cap")

    x = torch.as_tensor(features, dtype=torch.float32)
    state = torch.as_tensor(state_targets, dtype=torch.long)
    onset = torch.as_tensor(onset_targets, dtype=torch.long)
    validate_training_arrays(x, state, onset)

    set_determinism()
    model = TinyEventFitModel()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    started = clock()

    model.eval()
    with torch.no_grad():
        initial_total, initial_parts = explicit_event_loss(model(x), state, onset)

    steps = 0
    stop_reason = "requested_steps_reached"
    model.train()
    while steps < requested_steps:
        if clock() - started >= wall_seconds_limit:
            stop_reason = "training_evaluation_wall_limit"
            break
        optimizer.zero_grad(set_to_none=True)
        outputs = model(x)
        total, _parts = explicit_event_loss(outputs, state, onset)
        if not torch.isfinite(total):
            raise RuntimeError("nonfinite pilot loss")
        total.backward()
        grads = [p.grad for p in model.parameters() if p.requires_grad]
        if not grads or any(g is None or not torch.all(torch.isfinite(g)) for g in grads):
            raise RuntimeError("nonfinite or missing pilot gradient")
        optimizer.step()
        steps += 1

    model.eval()
    with torch.no_grad():
        final_outputs = model(x)
        final_total, final_parts = explicit_event_loss(final_outputs, state, onset)
    elapsed = clock() - started
    if steps > MAX_OPTIMIZER_STEPS:
        raise RuntimeError("optimizer cap invariant violated")
    if elapsed > wall_seconds_limit and stop_reason != "training_evaluation_wall_limit":
        stop_reason = "training_evaluation_wall_limit"

    return model, {
        "optimizerSteps": steps,
        "requestedOptimizerSteps": requested_steps,
        "elapsedSeconds": elapsed,
        "stopReason": stop_reason,
        "initialLoss": {
            "total": float(initial_total),
            "state": float(initial_parts["state"]),
            "onset": float(initial_parts["onset"]),
        },
        "finalLoss": {
            "total": float(final_total),
            "state": float(final_parts["state"]),
            "onset": float(final_parts["onset"]),
        },
    }


def _event_from_dict(row):
    return Event(row["id"], int(row["string"]), int(row["fret"]), float(row["start"]), float(row["end"]))


def evaluate_fitted_model(model, features, state_targets, onset_targets, metas, *, hop_seconds):
    x = torch.as_tensor(features, dtype=torch.float32)
    model.eval()
    with torch.no_grad():
        outputs = model(x)

    examples = []
    total_tp = total_offset_ok = 0
    repeated_ref_count = repeated_tp = 0
    all_predicted = 0
    for index, meta in enumerate(metas):
        pred = decode_event_list(
            outputs["state"][index],
            outputs["onset"][index],
            hop_seconds=hop_seconds,
            id_prefix=f"pred:{index}",
        )
        ref = [_event_from_dict(row) for row in meta["prepared"]["scorableEvents"]]
        score = score_events(pred, ref, onset_tolerance=0.05, offset_tolerance=0.05)
        repeated = repeated_reference_events(ref)
        repeated_score = score_events(pred, repeated, onset_tolerance=0.05, offset_tolerance=0.05)
        admission = onset_admission_recall(
            outputs["state"][index],
            outputs["onset"][index],
            state_targets[index],
            onset_targets[index],
        )
        total_tp += score["truePositive"]
        total_offset_ok += score["matchedOffsetWithinTolerance"]
        repeated_ref_count += len(repeated)
        repeated_tp += repeated_score["truePositive"]
        all_predicted += len(pred)
        examples.append({
            "captureKey": meta["captureKey"],
            "referenceAttackCount": score["referenceCount"],
            "predictedAttackCount": score["predictionCount"],
            "event": score,
            "repeatedReferenceAttackCount": len(repeated),
            "repeatedAttackRecall": repeated_score["recall"] if repeated else None,
            "onsetAdmissionRecall": admission,
            "sourceEventSha256": meta["prepared"]["sourceEventSha256"],
            "targetSha256": meta["prepared"]["targetSha256"],
            "featureSha256": meta["featureSha256"],
            "unresolvedLabelCount": meta["prepared"]["unresolvedLabelCount"],
        })

    with torch.no_grad():
        silence_features = torch.zeros((1, MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM), dtype=torch.float32)
        silence_out = model(silence_features)
        silence_pred = decode_event_list(
            silence_out["state"][0],
            silence_out["onset"][0],
            hop_seconds=hop_seconds,
            id_prefix="silence",
        )

    repeated_recall = repeated_tp / repeated_ref_count if repeated_ref_count else None
    offset_fraction = total_offset_ok / total_tp if total_tp else None
    return {
        "examples": examples,
        "trainingExampleEventF1Min": min((row["event"]["f1"] for row in examples), default=0.0),
        "matchedOffsetWithin50msFraction": offset_fraction,
        "repeatedReferenceAttackCount": repeated_ref_count,
        "repeatedAttackRecall": repeated_recall,
        "repeatedAttackCoverageSatisfied": repeated_ref_count > 0,
        "noEventSyntheticFalsePositiveCount": len(silence_pred),
        "predictedAttackCountTotal": all_predicted,
    }


def _metrics_finite(value):
    if value is None:
        return True
    if isinstance(value, bool):
        return True
    if isinstance(value, (int, float)):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_metrics_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_metrics_finite(v) for v in value)
    return True


def prepare_capture(args):
    # Import the frozen parser/preprocessing only for real-data preparation.
    from guitartechs_real_training.real_training import (
        decode_audio,
        midi_string_events,
        performance_key,
        visible_files,
    )
    from tabcnn_runtime.preprocessing import (
        HOP_LENGTH_SAMPLES,
        SAMPLE_RATE_HZ,
        extract_cqt_features,
        rms_normalize,
    )

    corrections_doc = json.loads(Path(args.corrections).read_text())
    corrections = corrections_doc["correctionsMs"]
    selected = select_pilot_capture_keys(corrections)
    if selected != FROZEN_CAPTURE_KEYS:
        raise RuntimeError("metadata selection no longer matches frozen pilot capture keys")
    if args.capture_key not in FROZEN_CAPTURE_KEYS:
        raise RuntimeError("capture key is outside frozen pilot selection")
    lag_ms = corrections[args.capture_key]
    performer, category, pkey, view = args.capture_key.split("|")
    if performer != "P1":
        raise RuntimeError("pilot is P1 training-only")

    root = Path(args.root)
    files = visible_files(root)
    midis = {}
    audio = defaultdict(dict)
    for path in files:
        key = performance_key(path)
        suffix = path.suffix.lower()
        if suffix in (".mid", ".midi"):
            midis[key] = path
        elif suffix in (".wav", ".mp3"):
            audio[key][path.parent.name] = path
    if pkey not in midis or view not in audio.get(pkey, {}):
        raise RuntimeError("missing frozen pilot source " + args.capture_key)

    midi_path = midis[pkey]
    audio_path = audio[pkey][view]
    notes = midi_string_events(midi_path)
    source_events, source_issues, _ = source_events_from_notes(
        notes, capture_id=args.capture_key, lag_ms=lag_ms
    )

    audio_samples = decode_audio(audio_path)
    features = extract_cqt_features(rms_normalize(audio_samples)).squeeze(0).astype(np.float32, copy=False)
    if features.ndim != 2 or features.shape[0] != FEATURE_DIM:
        raise RuntimeError("unexpected frozen CQT feature shape")
    if features.shape[1] < MAX_FRAMES_PER_EXAMPLE:
        raise RuntimeError("selected source shorter than 200 frames")

    hop_seconds = HOP_LENGTH_SAMPLES / SAMPLE_RATE_HZ
    crop_selection = select_training_crop(
        source_events,
        total_frames=int(features.shape[1]),
        frames=MAX_FRAMES_PER_EXAMPLE,
        hop_seconds=hop_seconds,
    )
    prepared = prepare_event_crop(
        notes,
        capture_id=args.capture_key,
        lag_ms=lag_ms,
        allowlist_lag_ms=corrections[args.capture_key],
        crop_start_frame=crop_selection["startFrame"],
        frames=MAX_FRAMES_PER_EXAMPLE,
        hop_seconds=hop_seconds,
    )

    start = prepared["crop"]["startFrame"]
    cropped_features = np.ascontiguousarray(
        features[:, start:start + MAX_FRAMES_PER_EXAMPLE].T,
        dtype=np.float32,
    )
    if cropped_features.shape != (MAX_FRAMES_PER_EXAMPLE, FEATURE_DIM):
        raise RuntimeError("prepared feature crop shape mismatch")

    out_dir = Path(args.output_dir) / hashlib.sha256(args.capture_key.encode()).hexdigest()[:16]
    out_dir.mkdir(parents=True, exist_ok=True)
    feature_path = out_dir / "features.npy"
    state_path = out_dir / "state.npy"
    onset_path = out_dir / "onset.npy"
    meta_path = out_dir / "meta.json"
    np.save(feature_path, cropped_features, allow_pickle=False)
    np.save(state_path, np.asarray(prepared["state"], dtype=np.int16), allow_pickle=False)
    np.save(onset_path, np.asarray(prepared["onset"], dtype=np.int16), allow_pickle=False)

    meta = {
        "schema": "astra-tiny-fit-prepared-example-v1",
        "captureKey": args.capture_key,
        "performer": performer,
        "category": category,
        "performanceKey": pkey,
        "captureView": view,
        "lagMs": lag_ms,
        "cropSelection": crop_selection,
        "hopSeconds": hop_seconds,
        "featureFile": feature_path.name,
        "stateFile": state_path.name,
        "onsetFile": onset_path.name,
        "featureSha256": _sha256_file(feature_path),
        "stateFileSha256": _sha256_file(state_path),
        "onsetFileSha256": _sha256_file(onset_path),
        "midiSourceSha256": _sha256_file(midi_path),
        "audioSourceSha256": _sha256_file(audio_path),
        "alignmentCorrectionsSha256": _sha256_file(args.corrections),
        "prepared": prepared,
        "sourceIssueCountBeforeCrop": len(source_issues),
        "guards": {
            "p3Opened": False,
            "customerDeliveryEligible": False,
        },
    }
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    if not prepared["launchReady"]:
        raise RuntimeError("prepared pilot example has unresolved labels")
    print("TINY_FIT_PREPARED=" + json.dumps({
        "captureKey": args.capture_key,
        "cropSelection": crop_selection,
        "referenceEvents": len(prepared["scorableEvents"]),
        "carryIn": len(prepared["carryInEventIds"]),
        "carryOut": len(prepared["carryOutEventIds"]),
        "featureSha256": meta["featureSha256"],
        "targetSha256": prepared["targetSha256"],
    }, sort_keys=True))


def _load_prepared_examples(examples_dir):
    root = Path(examples_dir)
    metas = []
    arrays = []
    for meta_path in sorted(root.glob("*/meta.json")):
        meta = json.loads(meta_path.read_text())
        d = meta_path.parent
        for filename, field in (
            ("features.npy", "featureSha256"),
            ("state.npy", "stateFileSha256"),
            ("onset.npy", "onsetFileSha256"),
        ):
            if _sha256_file(d / filename) != meta[field]:
                raise RuntimeError("prepared file hash mismatch " + str(d / filename))
        arrays.append((
            np.load(d / "features.npy", allow_pickle=False),
            np.load(d / "state.npy", allow_pickle=False),
            np.load(d / "onset.npy", allow_pickle=False),
        ))
        metas.append(meta)

    if len(metas) != MAX_EXAMPLES:
        raise RuntimeError("real pilot requires exactly four frozen examples")
    keys = tuple(meta["captureKey"] for meta in metas)
    if set(keys) != set(FROZEN_CAPTURE_KEYS):
        raise RuntimeError("prepared capture identity mismatch")
    if any(meta["performer"] != "P1" for meta in metas):
        raise RuntimeError("pilot may only use P1")
    perf_ids = {
        "|".join(meta["captureKey"].split("|")[:3])
        for meta in metas
    }
    if len(perf_ids) != MAX_EXAMPLES:
        raise RuntimeError("pilot requires four distinct underlying performances")
    if any(not meta["prepared"]["launchReady"] for meta in metas):
        raise RuntimeError("unresolved prepared labels block optimizer work")
    if sum(meta["prepared"]["unresolvedLabelCount"] for meta in metas):
        raise RuntimeError("unresolved labels block optimizer work")

    features = np.stack([a[0] for a in arrays])
    state = np.stack([a[1] for a in arrays])
    onset = np.stack([a[2] for a in arrays])
    validate_training_arrays(features, state, onset)
    return metas, features, state, onset


def train_pilot(args):
    job_started = time.monotonic()
    metas, features, state, onset = _load_prepared_examples(args.examples_dir)
    hop_values = {round(float(meta["hopSeconds"]), 12) for meta in metas}
    if len(hop_values) != 1:
        raise RuntimeError("inconsistent prepared hop")
    hop = float(metas[0]["hopSeconds"])

    # Establish repeated-attack coverage before spending optimizer steps.
    repeated_count = sum(
        len(repeated_reference_events([_event_from_dict(e) for e in meta["prepared"]["scorableEvents"]]))
        for meta in metas
    )
    if repeated_count <= 0:
        receipt = {
            "schema": SCHEMA,
            "status": "stopped_before_optimizer",
            "stopReason": "missing_repeated_same_fret_attack_coverage",
            "optimizerSteps": 0,
            "captureKeys": [m["captureKey"] for m in metas],
            "guards": {"p3Opened": False, "customerDeliveryEligible": False},
        }
        Path(args.result_out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        raise RuntimeError("pilot stopped: selected crops contain no scorable repeated attack")

    model, fit = fit_tiny_model(
        features,
        state,
        onset,
        requested_steps=MAX_OPTIMIZER_STEPS,
        wall_seconds_limit=MAX_TRAIN_EVAL_SECONDS,
    )
    evaluation = evaluate_fitted_model(model, features, state, onset, metas, hop_seconds=hop)
    elapsed_job = time.monotonic() - job_started
    unresolved = sum(meta["prepared"]["unresolvedLabelCount"] for meta in metas)
    all_finite = _metrics_finite(fit) and _metrics_finite(evaluation)
    offset = evaluation["matchedOffsetWithin50msFraction"]
    repeated = evaluation["repeatedAttackRecall"]
    advancement = (
        fit["optimizerSteps"] <= MAX_OPTIMIZER_STEPS
        and fit["elapsedSeconds"] <= MAX_TRAIN_EVAL_SECONDS
        and evaluation["trainingExampleEventF1Min"] >= 0.95
        and offset is not None and offset >= 0.90
        and evaluation["repeatedAttackCoverageSatisfied"]
        and repeated is not None and repeated >= 0.90
        and all_finite
        and unresolved == 0
    )
    receipt = {
        "schema": SCHEMA,
        "status": "completed_training_only_engineering_screen",
        "candidateId": "astra_tiny_event_fit_v1",
        "seed": SEED,
        "limits": {
            "maxUnderlyingPerformances": MAX_EXAMPLES,
            "maxViewsPerPerformance": 1,
            "maxFramesPerExample": MAX_FRAMES_PER_EXAMPLE,
            "maxOptimizerStepsTotal": MAX_OPTIMIZER_STEPS,
            "maxTrainingAndEvaluationWallSeconds": MAX_TRAIN_EVAL_SECONDS,
            "maxEntireJobSeconds": MAX_ENTIRE_JOB_SECONDS,
            "maxCandidateDesignsThisPilot": MAX_CANDIDATE_DESIGNS,
            "automaticRetries": 0,
        },
        "design": {
            "model": "per-frame 192->128 ReLU shared encoder; 6x21 state head; 6 onset-logit head",
            "lossWeights": {"state": STATE_LOSS_WEIGHT, "onset": ONSET_LOSS_WEIGHT},
            "stateActiveWeight": STATE_ACTIVE_WEIGHT,
            "onsetPositiveWeight": ONSET_POS_WEIGHT,
            "decoderThresholds": {
                "stateActive": STATE_ACTIVE_THRESHOLD,
                "onset": ONSET_THRESHOLD,
            },
            "optimizer": OPTIMIZER,
            "learningRate": LEARNING_RATE,
            "initialization": "random",
        },
        "fit": fit,
        "evaluation": evaluation,
        "prepared": [
            {
                "captureKey": m["captureKey"],
                "featureSha256": m["featureSha256"],
                "sourceEventSha256": m["prepared"]["sourceEventSha256"],
                "targetSha256": m["prepared"]["targetSha256"],
                "midiSourceSha256": m["midiSourceSha256"],
                "audioSourceSha256": m["audioSourceSha256"],
                "cropSelection": m["cropSelection"],
                "unresolvedLabelCount": m["prepared"]["unresolvedLabelCount"],
            }
            for m in metas
        ],
        "allMetricsFinite": all_finite,
        "unresolvedLabelCount": unresolved,
        "engineeringAdvancementThresholdsMet": advancement,
        "meaning": "training-only learnability screen; no generalization or customer claim",
        "entireJobElapsedSecondsAtReceipt": elapsed_job,
        "guards": {
            "p2Opened": False,
            "p3Opened": False,
            "publishedCheckpointLoaded": False,
            "paidComputeUsed": False,
            "automaticRetry": False,
            "automaticFullTraining": False,
            "customerDeliveryEligible": False,
        },
    }
    Path(args.result_out).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    torch.save({
        "schema": SCHEMA,
        "candidateId": receipt["candidateId"],
        "seed": SEED,
        "stateDict": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        "optimizerSteps": fit["optimizerSteps"],
        "preparedTargetSetSha256": _sha256_json(receipt["prepared"]),
        "customerDeliveryEligible": False,
    }, args.model_out)
    print("TINY_FIT_RESULT=" + json.dumps({
        "optimizerSteps": fit["optimizerSteps"],
        "stopReason": fit["stopReason"],
        "trainingExampleEventF1Min": evaluation["trainingExampleEventF1Min"],
        "matchedOffsetWithin50msFraction": evaluation["matchedOffsetWithin50msFraction"],
        "repeatedReferenceAttackCount": evaluation["repeatedReferenceAttackCount"],
        "repeatedAttackRecall": evaluation["repeatedAttackRecall"],
        "engineeringAdvancementThresholdsMet": advancement,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    extract = sub.add_parser("extract-selected-source")
    extract.add_argument("--archive", required=True)
    extract.add_argument("--capture-key", required=True)
    extract.add_argument("--output-dir", required=True)

    prep = sub.add_parser("prepare-capture")
    prep.add_argument("--root", required=True)
    prep.add_argument("--capture-key", required=True)
    prep.add_argument("--corrections", required=True)
    prep.add_argument("--output-dir", required=True)

    train = sub.add_parser("train-pilot")
    train.add_argument("--examples-dir", required=True)
    train.add_argument("--result-out", required=True)
    train.add_argument("--model-out", required=True)

    args = parser.parse_args()
    if args.cmd == "extract-selected-source":
        extract_selected_source(args.archive, capture_key=args.capture_key, output_dir=args.output_dir)
    elif args.cmd == "prepare-capture":
        prepare_capture(args)
    else:
        train_pilot(args)


if __name__ == "__main__":
    main()
