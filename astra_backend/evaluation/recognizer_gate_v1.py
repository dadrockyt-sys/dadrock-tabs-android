"""Conservative recognizer-gated cleanup policy V1."""
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class RecognizerGateConfig:
    other_abs_max: float = 0.002
    confident_abs_min: float = 0.05
    confident_margin_min: float = 0.03
    contamination_pressure_min: float = 0.20
    competitor_dominance_min: float = 0.20
    cleanup_floor_gain: float = 0.85
    cleanup_competition: float = 0.35

    def to_dict(self) -> dict:
        return asdict(self)

def decide(claimed_class, guitar_score, bass_score, diagnostics, cfg=RecognizerGateConfig()):
    string_abs=max(guitar_score,bass_score)
    margin=abs(guitar_score-bass_score)
    winner="guitar" if guitar_score >= bass_score else "bass"
    if claimed_class not in {"guitar","bass"}:
        return {"state":"uncertain","applyCleanup":False,"reason":"unsupported_claim"}
    if string_abs <= cfg.other_abs_max:
        return {"state":"other_or_low_confidence","applyCleanup":False,"winner":winner,"stringEvidence":string_abs,"margin":margin,"reason":"absolute_string_evidence_too_low"}
    if string_abs >= cfg.confident_abs_min and margin >= cfg.confident_margin_min:
        if winner == claimed_class:
            return {"state":"agree","applyCleanup":False,"winner":winner,"stringEvidence":string_abs,"margin":margin,"reason":"recognizer_agrees_preserve_raw"}
        pressure=float(diagnostics.get("interferencePressure",0.0))
        dominance=float(diagnostics.get("competitorDominanceFraction",0.0))
        if pressure >= cfg.contamination_pressure_min and dominance >= cfg.competitor_dominance_min:
            return {"state":"disagree_with_contamination","applyCleanup":True,"winner":winner,"stringEvidence":string_abs,"margin":margin,"interferencePressure":pressure,"competitorDominanceFraction":dominance,"reason":"recognizer_disagrees_and_separator_indicates_contamination"}
        return {"state":"disagree_without_contamination","applyCleanup":False,"winner":winner,"stringEvidence":string_abs,"margin":margin,"reason":"disagreement_not_enough_to_modify_audio"}
    return {"state":"uncertain","applyCleanup":False,"winner":winner,"stringEvidence":string_abs,"margin":margin,"reason":"insufficient_margin_or_absolute_evidence"}
