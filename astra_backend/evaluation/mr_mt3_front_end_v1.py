#!/usr/bin/env python3
"""Offline MR-MT3 Stage-A MIDI projection utilities.

This module does not run MR-MT3, open corpus audio, optimize weights, search
thresholds, or access P3. It projects already-produced multitrack MIDI onto the
frozen guitar-domain contract for pitch/onset feasibility scoring.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import math

import mido

from evaluation.pretrained_note_front_end_v1 import PitchEvent, score_pitch_events

MT3_INFER_VERSION="0.2.0"
MT3_INFER_PUBLISH_COMMIT="2d20ee5bb6ca727968bd23c6100fd2a35154166b"
MR_MT3_UPSTREAM_COMMIT="826ea84a933f93cd707d11e91af711f1d19c8d79"
MR_MT3_CHECKPOINT_COMMIT="539c08b0fe551076db6108a5f5b2a57d774881ed"
MR_MT3_CHECKPOINT_URL=(
    "https://huggingface.co/gudgud1014/MR-MT3/resolve/"
    + MR_MT3_CHECKPOINT_COMMIT + "/mt3.pth?download=true"
)
MR_MT3_CHECKPOINT_BYTES=183672643
MR_MT3_CHECKPOINT_SHA256="b8a3807ed265059abd25ad7f68142c06c35e8f6144dcaa45bd55946a3745398f"
MT3_INFER_WHEEL_SHA256="95209657fafab7eda0e5187f5fb9ae3438a18e2a4e30acd4786f3cda25389ff4"

GUITAR_PROGRAM_MIN=24
GUITAR_PROGRAM_MAX=31
GUITAR_PITCH_MIN=40
GUITAR_PITCH_MAX=83
PERCUSSION_CHANNEL=9
OPTIMIZER_STEPS=0
THRESHOLD_SEARCH=False

def _finite(x,name):
    x=float(x)
    if not math.isfinite(x):
        raise ValueError(name+" must be finite")
    return x

def project_midi_to_guitar_events(midi_path,crop_start_seconds,crop_end_seconds):
    """Project MR-MT3-style multitrack MIDI to frozen guitar pitch events.

    Program numbers use the zero-based MIDI convention used by mido.
    Crop clipping is deterministic and never shifts an onset to seek a match.
    """
    crop_start=_finite(crop_start_seconds,"crop start")
    crop_end=_finite(crop_end_seconds,"crop end")
    if crop_end<=crop_start:
        raise ValueError("invalid crop interval")

    mid=mido.MidiFile(str(midi_path))
    tempo=500000
    programs=defaultdict(int)
    active=defaultdict(list)
    seconds=0.0
    out=[]
    stats={
      "accepted":0,
      "rejectedPercussion":0,
      "rejectedProgram":0,
      "rejectedPitchRange":0,
      "unmatchedNoteOff":0,
    }

    for msg in mido.merge_tracks(mid.tracks):
        seconds += mido.tick2second(msg.time,mid.ticks_per_beat,tempo)
        if msg.type=="set_tempo":
            tempo=msg.tempo
            continue
        if not hasattr(msg,"channel"):
            continue
        ch=int(msg.channel)
        if msg.type=="program_change":
            programs[ch]=int(msg.program)
            continue
        if msg.type=="note_on" and int(msg.velocity)>0:
            active[(ch,int(msg.note))].append((seconds,int(programs[ch])))
            continue
        if msg.type not in ("note_off","note_on"):
            continue
        if msg.type=="note_on" and int(msg.velocity)>0:
            continue
        key=(ch,int(msg.note))
        if not active[key]:
            stats["unmatchedNoteOff"]+=1
            continue
        start,program=active[key].pop(0)
        end=seconds
        if end<=start:
            continue
        pitch=int(msg.note)
        if ch==PERCUSSION_CHANNEL:
            stats["rejectedPercussion"]+=1
            continue
        if not GUITAR_PROGRAM_MIN<=program<=GUITAR_PROGRAM_MAX:
            stats["rejectedProgram"]+=1
            continue
        if not GUITAR_PITCH_MIN<=pitch<=GUITAR_PITCH_MAX:
            stats["rejectedPitchRange"]+=1
            continue
        if start>=crop_end or end<=crop_start:
            continue
        local_start=max(0.0,start-crop_start)
        local_end=min(crop_end,end)-crop_start
        if local_end<=local_start:
            continue
        idx=len(out)
        out.append(PitchEvent(f"mrmt3:{idx}",pitch,local_start,local_end))
        stats["accepted"]+=1

    return sorted(out,key=lambda e:(e.pitch,e.start,e.end,e.id)),stats

def score_projected_midi(midi_path,refs,crop_start_seconds,crop_end_seconds):
    preds,stats=project_midi_to_guitar_events(midi_path,crop_start_seconds,crop_end_seconds)
    return {"projectionStats":stats,"predictions":preds,"scores":score_pitch_events(preds,refs)}

def frozen_identity():
    return {
      "mt3InferVersion":MT3_INFER_VERSION,
      "mt3InferPublishCommit":MT3_INFER_PUBLISH_COMMIT,
      "mrMt3UpstreamCommit":MR_MT3_UPSTREAM_COMMIT,
      "checkpointCommit":MR_MT3_CHECKPOINT_COMMIT,
      "checkpointUrl":MR_MT3_CHECKPOINT_URL,
      "checkpointBytes":MR_MT3_CHECKPOINT_BYTES,
      "checkpointSha256":MR_MT3_CHECKPOINT_SHA256,
      "mt3InferWheelSha256":MT3_INFER_WHEEL_SHA256,
      "optimizerSteps":OPTIMIZER_STEPS,
      "thresholdSearch":THRESHOLD_SEARCH,
      "acceptedPrograms":[GUITAR_PROGRAM_MIN,GUITAR_PROGRAM_MAX],
      "acceptedPitchRange":[GUITAR_PITCH_MIN,GUITAR_PITCH_MAX],
    }
