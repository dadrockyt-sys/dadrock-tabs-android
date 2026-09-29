#!/usr/bin/env python3
"""Frozen V4 renderer transforms used by the V4A/V4B experiment.

These transforms operate on 22.05 kHz synthetic waveforms before the existing
frozen RMS normalization/CQT frontend. They do not alter labels, timing, pitch,
model architecture, thresholds, or decoder semantics.
"""
from __future__ import annotations
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
from synthetic.s0_pilot_v1 import ROOT_SEED, _seed

SAMPLE_RATE=22050

def _bp(x,lo,hi):
    return sosfilt(butter(2,[lo/(SAMPLE_RATE/2),hi/(SAMPLE_RATE/2)],btype="bandpass",output="sos"),x)

def _hp(x,hz=70.0):
    return sosfilt(butter(2,hz/(SAMPLE_RATE/2),btype="highpass",output="sos"),x)

def _lp(x,hz=6500.0):
    return sosfilt(butter(2,hz/(SAMPLE_RATE/2),btype="lowpass",output="sos"),x)

def apply_renderer_arm(audio,arm,key):
    x=np.asarray(audio,dtype=np.float64).copy()
    if arm=="R0":
        return x.astype(np.float32)

    # R1: fixed amplifier/cabinet coloration + soft saturation.
    x=_hp(x,70.0)
    x=_lp(x,6500.0)
    x=x+0.35*_bp(x,700.0,2200.0)
    x=np.tanh(1.30*x)/np.tanh(1.30)
    if arm=="R1":
        return x.astype(np.float32)

    # R2: deterministic short-room/capture variation and recording noise.
    rng=np.random.RandomState(_seed(ROOT_SEED,"v4-capture",key))
    ir=np.zeros(int(.040*SAMPLE_RATE)+1,dtype=np.float64)
    ir[0]=1.0
    for sec,gain in ((.008,.12),(.017,.08),(.031,.04)):
        ir[min(len(ir)-1,int(round(sec*SAMPLE_RATE)))]+=gain
    x=np.convolve(x,ir,mode="full")[:len(x)]
    tilt=(-.08,0.0,.08)[int(key)%3]
    smooth=lfilter([0.12],[1,-0.88],x)
    x=(1.0-abs(tilt))*x+tilt*smooth
    x+=rng.normal(0,0.0015,len(x))
    if arm=="R2":
        return x.astype(np.float32)

    if arm!="R3":
        raise ValueError("arm must be R0/R1/R2/R3")

    # R3: mild compression, deterministic transient variation, bounded hum,
    # and bounded output-level variation before frozen RMS normalization.
    x=np.sign(x)*(1-np.exp(-1.15*np.abs(x)))/1.15
    env=np.ones(len(x),dtype=np.float64)
    for center in np.linspace(.20,1.70,5):
        c=int(center*SAMPLE_RATE)
        w=int(.018*SAMPLE_RATE)
        lo=max(0,c-w)
        hi=min(len(x),c+w)
        if hi>lo:
            env[lo:hi]*=float(rng.uniform(.82,1.18))
    x*=env
    if int(key)%3==0:
        t=np.arange(len(x))/SAMPLE_RATE
        phase=float(rng.uniform(0,2*np.pi))
        x+=.0025*np.sin(2*np.pi*60*t+phase)
        x+=.0012*np.sin(2*np.pi*120*t+phase/2)
    x*=float(rng.uniform(.82,1.18))
    return x.astype(np.float32)
