"""No-reference coherence diagnostics for duplicate-class stem pairs."""
from __future__ import annotations

import numpy as np

def _mono(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return x.astype(np.float64)
    return np.mean(x.astype(np.float64), axis=1)

def normalized_corr(a: np.ndarray, b: np.ndarray) -> float:
    a=_mono(a); b=_mono(b)
    n=min(len(a),len(b))
    if n==0:
        return 0.0
    a=a[:n]-np.mean(a[:n]); b=b[:n]-np.mean(b[:n])
    den=float(np.linalg.norm(a)*np.linalg.norm(b))
    if den <= 1e-20:
        return 0.0
    return float(np.dot(a,b)/den)

def max_short_lag_corr(a: np.ndarray, b: np.ndarray, fs: int, max_lag_ms: float=10.0) -> dict:
    a=_mono(a); b=_mono(b)
    n=min(len(a),len(b))
    a=a[:n]; b=b[:n]
    max_lag=max(1,int(round(fs*max_lag_ms/1000.0)))
    best_corr=-1.0
    best_lag=0
    for lag in range(-max_lag,max_lag+1):
        if lag < 0:
            aa=a[-lag:]; bb=b[:len(aa)]
        elif lag > 0:
            aa=a[:-lag]; bb=b[lag:]
        else:
            aa=a; bb=b
        if len(aa)<8:
            continue
        c=normalized_corr(aa,bb)
        if abs(c)>abs(best_corr):
            best_corr=c; best_lag=lag
    return {"maxAbsCorr":float(abs(best_corr)),"signedCorr":float(best_corr),"lagSamples":int(best_lag)}

def pair_coherence_metrics(a: np.ndarray, b: np.ndarray, fs: int) -> dict:
    zero=normalized_corr(a,b)
    lag=max_short_lag_corr(a,b,fs)
    ea=float(np.mean(np.asarray(a,dtype=np.float64)**2))
    eb=float(np.mean(np.asarray(b,dtype=np.float64)**2))
    gap=abs(10.0*np.log10((ea+1e-20)/(eb+1e-20)))
    return {
        "zeroLagCorr":float(zero),
        "maxShortLagAbsCorr":lag["maxAbsCorr"],
        "maxShortLagSignedCorr":lag["signedCorr"],
        "bestLagSamples":lag["lagSamples"],
        "energyGapDb":float(gap),
    }
