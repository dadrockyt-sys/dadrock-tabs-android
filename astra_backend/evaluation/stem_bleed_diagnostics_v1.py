"""Separator-output diagnostics for deciding whether bleed cleanup should activate.

These metrics inspect separator stems only. They do not use reference ground truth
and do not alter audio.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np
from scipy.signal import stft

@dataclass(frozen=True)
class DiagnosticConfig:
    n_fft: int = 2048
    hop: int = 512
    active_floor_db: float = -60.0
    dominance_margin_db: float = 3.0

    def to_dict(self) -> dict:
        return asdict(self)

def _power(x: np.ndarray, fs: int, cfg: DiagnosticConfig) -> np.ndarray:
    parts=[]
    for ch in range(x.shape[1]):
        _,_,z=stft(
            x[:,ch],fs=fs,nperseg=cfg.n_fft,
            noverlap=cfg.n_fft-cfg.hop,boundary="zeros",padded=True
        )
        parts.append(np.abs(z).astype(np.float64)**2)
    return np.mean(np.stack(parts,axis=0),axis=0)

def _db_ratio(num: float, den: float, eps: float=1e-20) -> float:
    return float(10.0*np.log10((num+eps)/(den+eps)))

def diagnose_stems(
    mixture: np.ndarray,
    stems: dict[str,np.ndarray],
    fs: int,
    cfg: DiagnosticConfig=DiagnosticConfig(),
) -> dict[str,dict]:
    if not stems:
        return {}
    length=min([len(mixture), *[len(x) for x in stems.values()]])
    mix=mixture[:length]
    powers={k:_power(v[:length],fs,cfg) for k,v in stems.items()}
    waveform_energy={k:float(np.mean(v[:length].astype(np.float64)**2)) for k,v in stems.items()}
    mix_energy=float(np.mean(mix.astype(np.float64)**2))
    out={}
    margin=10.0**(cfg.dominance_margin_db/10.0)

    for target,tp in powers.items():
        peak=float(np.max(tp)) if tp.size else 0.0
        active=tp >= max(peak*10.0**(cfg.active_floor_db/10.0),1e-20)
        others={k:p for k,p in powers.items() if k!=target}
        comp_total=np.sum(np.stack(list(others.values()),axis=0),axis=0) if others else np.zeros_like(tp)
        denom=float(np.sum(tp[active])) if np.any(active) else 0.0
        shared=float(np.sum(np.minimum(tp[active],comp_total[active]))) if np.any(active) else 0.0
        dominance=float(np.mean(comp_total[active] > tp[active]*margin)) if np.any(active) else 0.0
        target_dominance=float(np.mean(tp[active] > comp_total[active]*margin)) if np.any(active) else 0.0
        ambiguity=max(0.0,1.0-dominance-target_dominance)

        per_comp={}
        for name,cp in others.items():
            overlap=float(np.sum(np.minimum(tp[active],cp[active]))) if np.any(active) else 0.0
            per_comp[name]={
                "overlapPressure": float(overlap/(denom+1e-20)),
                "energyRatioToTargetDb": _db_ratio(waveform_energy[name],waveform_energy[target]),
            }
        strongest=max(per_comp, key=lambda k: per_comp[k]["overlapPressure"]) if per_comp else None

        out[target]={
            "stemEnergy": waveform_energy[target],
            "stemToMixtureEnergyDb": _db_ratio(waveform_energy[target],mix_energy),
            "interferencePressure": float(shared/(denom+1e-20)),
            "competitorDominanceFraction": dominance,
            "targetDominanceFraction": target_dominance,
            "ambiguousFraction": ambiguity,
            "strongestOverlapCompetitor": strongest,
            "perCompetitor": per_comp,
        }
    return out
