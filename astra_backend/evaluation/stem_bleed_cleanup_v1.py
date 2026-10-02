"""Target-preserving cross-stem bleed cleanup primitives.

No model loading, downloads, source separation or transcription occurs here.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.signal import stft, istft

@dataclass(frozen=True)
class CleanupConfig:
    n_fft: int = 2048
    hop: int = 512
    power: float = 2.0
    competition: float = 0.50
    floor_gain: float = 0.60

    def to_dict(self) -> dict:
        return asdict(self)


def _stft(x: np.ndarray, fs: int, cfg: CleanupConfig) -> np.ndarray:
    zs=[]
    for ch in range(x.shape[1]):
        _,_,z=stft(x[:,ch], fs=fs, nperseg=cfg.n_fft,
                   noverlap=cfg.n_fft-cfg.hop, boundary="zeros", padded=True)
        zs.append(z)
    return np.stack(zs, axis=0)


def _istft(z: np.ndarray, fs: int, cfg: CleanupConfig, length: int) -> np.ndarray:
    ys=[]
    for ch in range(z.shape[0]):
        _,y=istft(z[ch], fs=fs, nperseg=cfg.n_fft,
                  noverlap=cfg.n_fft-cfg.hop, input_onesided=True, boundary=True)
        ys.append(y[:length])
    y=np.stack(ys, axis=1)
    if y.shape[0] < length:
        y=np.pad(y, ((0,length-y.shape[0]),(0,0)))
    return y.astype(np.float32)


def suppress_cross_stem_bleed(
    stems: dict[str,np.ndarray], fs: int, cfg: CleanupConfig = CleanupConfig()
) -> tuple[dict[str,np.ndarray], dict[str,np.ndarray]]:
    """Apply soft cross-stem competition without hard-zeroing target bins."""
    names=list(stems)
    if not names:
        return {},{}
    length=min(v.shape[0] for v in stems.values())
    z={k:_stft(v[:length],fs,cfg) for k,v in stems.items()}
    mag_pow={k:np.maximum(np.abs(v),1e-12)**cfg.power for k,v in z.items()}
    total=np.sum(np.stack([mag_pow[k] for k in names],axis=0),axis=0)
    cleaned={}; masks={}
    for k in names:
        own=mag_pow[k]
        competing=np.maximum(total-own,0.0)
        confidence=own/(own+cfg.competition*competing+1e-12)
        gain=cfg.floor_gain+(1.0-cfg.floor_gain)*confidence
        masks[k]=gain.astype(np.float32)
        cleaned[k]=_istft(z[k]*gain,fs,cfg,length)
    return cleaned,masks


def exact_residual(mixture: np.ndarray, cleaned: dict[str,np.ndarray]) -> np.ndarray:
    """Residual that makes cleaned stems + residual reconstruct the input mixture."""
    if not cleaned:
        return mixture.astype(np.float32, copy=True)
    length=min([mixture.shape[0], *[v.shape[0] for v in cleaned.values()]])
    total=np.zeros_like(mixture[:length], dtype=np.float32)
    for value in cleaned.values():
        total += value[:length].astype(np.float32)
    return mixture[:length].astype(np.float32)-total


def si_sdr(reference: np.ndarray, estimate: np.ndarray, eps: float=1e-12) -> float:
    r=reference.reshape(-1).astype(np.float64)
    e=estimate.reshape(-1).astype(np.float64)
    n=min(len(r),len(e)); r=r[:n]; e=e[:n]
    r-=np.mean(r); e-=np.mean(e)
    scale=np.dot(e,r)/(np.dot(r,r)+eps)
    target=scale*r
    noise=e-target
    return float(10*np.log10((np.dot(target,target)+eps)/(np.dot(noise,noise)+eps)))


def inject_symmetric_bleed(
    truth: dict[str,np.ndarray], bleed_db: float = -18.0
) -> dict[str,np.ndarray]:
    """Development-only deterministic contamination for validating cleanup math."""
    gain=10.0**(bleed_db/20.0)
    names=list(truth)
    out={}
    for name in names:
        y=truth[name].astype(np.float32,copy=True)
        for other in names:
            if other != name:
                y += gain*truth[other].astype(np.float32)
        out[name]=y
    return out
