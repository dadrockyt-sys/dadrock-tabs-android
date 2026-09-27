"""Astra event decoder V2: suppress same-fret onset plateaus without retuning.

Historical V3 decoding admitted a new same-string/same-fret attack on every frame
whose onset probability remained above threshold. V2 keeps the exact thresholds
but requires a fresh below->above threshold crossing for a same-fret reattack
while an event is already active. Different-fret onsets retain V1 behavior.

This module is diagnostic/experimental. It does not replace the frozen V3 decoder.
"""
from __future__ import annotations

import math

import numpy as np
import torch

from evaluation.event_contract_v2 import Event

NUM_STRINGS = 6
NUM_FRETS = 20
NUM_CLASSES = 21
SILENCE_CLASS = 20

STATE_ACTIVE_THRESHOLD = 0.50
ONSET_THRESHOLD = 0.50


def decode_event_list_v2(
    state_logits,
    onset_logits,
    *,
    hop_seconds,
    state_active_threshold=STATE_ACTIVE_THRESHOLD,
    onset_threshold=ONSET_THRESHOLD,
    id_prefix="pred",
):
    """Decode explicit attacks with rising-edge gating for same-fret reattacks.

    Rules:
    - a silent->active event may start whenever onset/state admission is satisfied;
    - a different-fret admitted onset may replace the current event immediately;
    - a same-fret reattack requires onset admission on a frame whose immediately
      preceding onset frame was below threshold;
    - state changes without an admitted onset never invent an attack.
    """
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
    if not 0 <= float(state_active_threshold) <= 1:
        raise ValueError("state_active_threshold out of range")
    if not 0 <= float(onset_threshold) <= 1:
        raise ValueError("onset_threshold out of range")

    state_prob = torch.softmax(
        state_logits.reshape(-1, NUM_STRINGS, NUM_CLASSES), dim=-1
    ).numpy()
    onset_prob = torch.sigmoid(onset_logits).numpy()
    frames = state_prob.shape[0]

    events = []
    serial = [0] * NUM_STRINGS

    for string in range(NUM_STRINGS):
        current = None
        previous_onset_ok = False

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

        def start(frame, fret):
            nonlocal current
            serial[string] += 1
            current = {
                "id": f"{id_prefix}:s{string}:{serial[string]}",
                "fret": fret,
                "start": frame * hop,
            }

        for frame in range(frames):
            row = state_prob[frame, string]
            fret = int(np.argmax(row[:NUM_FRETS]))
            active_prob = float(row[fret])
            silence_prob = float(row[SILENCE_CLASS])
            active_ok = (
                active_prob >= state_active_threshold
                and active_prob > silence_prob
            )
            onset_ok = float(onset_prob[frame, string]) >= onset_threshold

            if current is not None:
                if onset_ok and active_ok:
                    same_fret = fret == current["fret"]
                    same_fret_plateau = same_fret and previous_onset_ok
                    if not same_fret_plateau:
                        close(frame)
                        start(frame, fret)
                elif not active_ok or fret != current["fret"]:
                    close(frame)

            if current is None and onset_ok and active_ok:
                start(frame, fret)

            previous_onset_ok = onset_ok

        close(frames)

    return sorted(events, key=lambda e: (e.string, e.start, e.fret, e.id))
