"""Pair-level guitar/bass consistency classifier V1.

Diagnostic-only. It classifies the relationship between the separator's guitar
and bass stems; it never suppresses, merges, or reassigns audio.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math

@dataclass(frozen=True)
class PairClassifierConfig:
    silent_energy_max: float = 1e-9
    substantial_string_evidence_min: float = 0.05
    same_class_margin_min: float = 0.005
    pair_energy_gap_max_db: float = 6.0
    mutual_overlap_required: bool = True

    def to_dict(self):
        return asdict(self)

def winner(ev):
    if ev["guitar"] > ev["bass"]:
        return "guitar", ev["guitar"]-ev["bass"]
    if ev["bass"] > ev["guitar"]:
        return "bass", ev["bass"]-ev["guitar"]
    return "tie", 0.0

def classify_pair(guitar_row, bass_row, cfg=PairClassifierConfig()):
    ge=guitar_row["claimedEvidence"]
    be=bass_row["claimedEvidence"]
    gw,gm=winner(ge)
    bw,bm=winner(be)

    g_energy=float(guitar_row["claimedStemEnergy"])
    b_energy=float(bass_row["claimedStemEnergy"])
    gap=abs(10.0*math.log10((g_energy+1e-20)/(b_energy+1e-20)))

    if g_energy <= cfg.silent_energy_max or b_energy <= cfg.silent_energy_max:
        return {
            "state":"missing_or_silent_member",
            "guitarWinner":gw,
            "bassWinner":bw,
            "energyGapDb":gap,
            "reason":"one_pair_member_near_silent"
        }

    mutual=(
        guitar_row.get("strongestOverlapCompetitor")=="bass"
        and bass_row.get("strongestOverlapCompetitor")=="guitar"
    )

    if gw=="guitar" and bw=="bass":
        return {
            "state":"complementary_pair",
            "guitarWinner":gw,
            "bassWinner":bw,
            "energyGapDb":gap,
            "mutualOverlap":mutual,
            "reason":"pair_classes_complementary"
        }

    if gw==bw and gw in {"guitar","bass"}:
        g_abs=max(ge["guitar"],ge["bass"])
        b_abs=max(be["guitar"],be["bass"])
        strong=(
            g_abs >= cfg.substantial_string_evidence_min
            and b_abs >= cfg.substantial_string_evidence_min
            and gm >= cfg.same_class_margin_min
            and bm >= cfg.same_class_margin_min
            and gap <= cfg.pair_energy_gap_max_db
            and (mutual if cfg.mutual_overlap_required else True)
        )
        if strong:
            return {
                "state":f"duplicate_{gw}_candidate",
                "guitarWinner":gw,
                "bassWinner":bw,
                "energyGapDb":gap,
                "mutualOverlap":mutual,
                "reason":"both_substantial_pair_members_favor_same_class"
            }

    return {
        "state":"ambiguous_pair",
        "guitarWinner":gw,
        "bassWinner":bw,
        "energyGapDb":gap,
        "mutualOverlap":mutual,
        "reason":"insufficient_pair_consistency_evidence"
    }
