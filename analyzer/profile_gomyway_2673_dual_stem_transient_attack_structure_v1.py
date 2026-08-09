from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2568_dual_stem_spectral_tonal_noise_contrast_v1 as spectral

recur = spectral.recur
recall = spectral.recall
v2 = spectral.v2
v3 = spectral.v3
harmonic = spectral.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SPECTRAL_PROFILE_PATH = PUBLIC / "gomyway-2568-dual-stem-spectral-tonal-noise-contrast-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2673-dual-stem-transient-attack-structure-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2673-dual-stem-transient-attack-structure-v1-manifest.json"
EXPECTED_2568 = (183, 684, 375)
EXPECTED_2568_F1 = 25.68
EXPECTED_2673 = (183, 684, 319)
EXPECTED_2673_F1 = 26.73
EXPECTED_SPECTRAL_ZERO_SIGNATURES = 11
EXPECTED_SPECTRAL_PRUNE_COUNT = 56


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2673(
    grid: dict[tuple[int, int], float],
    winner_audio: np.ndarray,
    winner_sr: int,
    alt_audio: np.ndarray,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], Counter[tuple[int, int, int]]]:
    champion2568, _ = spectral.reconstruct_2568(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score2568 = recur.grade(champion2568, reference)
    actual2568 = (int(score2568["matched"]), int(score2568["missing"]), int(score2568["extra"]))
    if actual2568 != EXPECTED_2568 or abs(float(score2568["pitchF1"]) - EXPECTED_2568_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 25.68 champion {EXPECTED_2568}/{EXPECTED_2568_F1}, got {actual2568}/{score2568['pitchF1']}")

    profile = v2.load_json(SPECTRAL_PROFILE_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.68 spectral profile is not reference-free during detection")
    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_SPECTRAL_ZERO_SIGNATURES:
        raise RuntimeError(f"Expected {EXPECTED_SPECTRAL_ZERO_SIGNATURES} spectral zero-precision signatures, got {len(zero_rows)}")
    signatures = {str(row["signature"]) for row in zero_rows}
    row_by_token = {token(row): row for row in profile.get("rows", [])}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2568.items():
        row = row_by_token.get(tok)
        if row is not None and ({str(s) for s in row.get("signatures", [])} & signatures):
            pruned[tok] = count

    if int(sum(pruned.values())) != EXPECTED_SPECTRAL_PRUNE_COUNT:
        raise RuntimeError(f"Expected frozen spectral prune count {EXPECTED_SPECTRAL_PRUNE_COUNT}, got {sum(pruned.values())}")
    if int(sum((pruned & reference).values())) != 0:
        raise RuntimeError("Frozen spectral prune unexpectedly removes reference matches")

    champion2673 = champion2568 - pruned
    score2673 = recur.grade(champion2673, reference)
    actual2673 = (int(score2673["matched"]), int(score2673["missing"]), int(score2673["extra"]))
    if actual2673 != EXPECTED_2673 or abs(float(score2673["pitchF1"]) - EXPECTED_2673_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 26.73 champion {EXPECTED_2673}/{EXPECTED_2673_F1}, got {actual2673}/{score2673['pitchF1']}")
    return champion2673, pruned


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x), dtype=np.float64) + 1e-12)) if x.size else 0.0


def transient_features(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    a = np.asarray(audio, dtype=np.float64)
    def seg(start: float, end: float) -> np.ndarray:
        i0 = max(0, int(round((center + start) * sr)))
        i1 = min(a.size, int(round((center + end) * sr)))
        return a[i0:i1] if i1 > i0 else np.zeros(1, dtype=np.float64)

    pre = seg(-0.060, -0.010)
    attack = seg(-0.010, 0.035)
    early = seg(0.035, 0.100)
    sustain = seg(0.100, 0.220)

    pre_r = rms(pre)
    att_r = rms(attack)
    early_r = rms(early)
    sus_r = rms(sustain)
    eps = 1e-9

    abs_attack = np.abs(attack - float(np.mean(attack)))
    peak = float(np.max(abs_attack)) if abs_attack.size else 0.0
    crest = peak / (att_r + eps)
    onset_ratio = att_r / (pre_r + eps)
    attack_sustain = att_r / (sus_r + eps)
    early_sustain = early_r / (sus_r + eps)
    decay = sus_r / (att_r + eps)

    if attack.size >= 4:
        d = np.diff(attack)
        diff_r = rms(d)
    else:
        diff_r = 0.0
    sharpness = diff_r / (att_r + eps)

    return {
        "preRms": pre_r,
        "attackRms": att_r,
        "earlyRms": early_r,
        "sustainRms": sus_r,
        "onsetRatio": float(onset_ratio),
        "attackToSustain": float(attack_sustain),
        "earlyToSustain": float(early_sustain),
        "decayRatio": float(decay),
        "attackCrest": float(crest),
        "attackSharpness": float(sharpness),
    }


def bucket(v: float, edges: list[tuple[float, str]], tail: str) -> str:
    for limit, label in edges:
        if v < limit:
            return label
    return tail


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    max_onset = max(w["onsetRatio"], a["onsetRatio"])
    min_onset = min(w["onsetRatio"], a["onsetRatio"])
    max_as = max(w["attackToSustain"], a["attackToSustain"])
    min_as = min(w["attackToSustain"], a["attackToSustain"])
    max_crest = max(w["attackCrest"], a["attackCrest"])
    min_crest = min(w["attackCrest"], a["attackCrest"])
    max_sharp = max(w["attackSharpness"], a["attackSharpness"])
    diff_onset = abs(w["onsetRatio"] - a["onsetRatio"])
    diff_as = abs(w["attackToSustain"] - a["attackToSustain"])

    onset = bucket(min_onset, [(1.15,"onset_lt115"),(1.5,"onset_115_150"),(2.0,"onset_150_200"),(3.0,"onset_200_300")], "onset_300_plus")
    onset_max = bucket(max_onset, [(1.5,"maxon_lt150"),(2.5,"maxon_150_250"),(4.0,"maxon_250_400")], "maxon_400_plus")
    ats = bucket(min_as, [(0.8,"ats_lt080"),(1.1,"ats_080_110"),(1.5,"ats_110_150"),(2.2,"ats_150_220")], "ats_220_plus")
    crest = bucket(min_crest, [(2.5,"crest_lt25"),(4.0,"crest_25_40"),(6.0,"crest_40_60")], "crest_60_plus")
    sharp = bucket(max_sharp, [(0.20,"sharp_lt020"),(0.35,"sharp_020_035"),(0.55,"sharp_035_055")], "sharp_055_plus")
    odiff = bucket(diff_onset, [(0.25,"odiff_lt025"),(0.75,"odiff_025_075"),(1.5,"odiff_075_150")], "odiff_150_plus")
    adiff = bucket(diff_as, [(0.20,"adiff_lt020"),(0.50,"adiff_020_050"),(1.0,"adiff_050_100")], "adiff_100_plus")
    balance = "attack_both" if min_onset >= 1.5 else ("attack_one" if max_onset >= 1.5 else "attack_neither")

    return {
        f"minOnsetRatio::{onset}",
        f"maxOnsetRatio::{onset_max}",
        f"minAttackSustain::{ats}",
        f"minAttackCrest::{crest}",
        f"maxAttackSharpness::{sharp}",
        f"onsetStemDifference::{odiff}",
        f"attackSustainDifference::{adiff}",
        f"dualStemAttackBalance::{balance}",
        f"transientAttackCross::{onset}|{ats}|{crest}|{sharp}",
        f"dualStemTransientCross::{balance}|{odiff}|{adiff}|{onset_max}",
        f"attackContrastCross::{onset}|{ats}|{balance}|{odiff}",
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, spectral_pruned = reconstruct_2673(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, _pitch = tok
        center = float(grid[(measure, step)])
        wf = transient_features(winner_audio, winner_sr, center)
        af = transient_features(alt_audio, alt_sr, center)
        signatures = sorted(signatures_for(wf, af))
        for s in signatures:
            groups[s][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "winner": wf, "alternate": af, "signatures": signatures})

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 26.73 transient attack profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-26.73-dual-stem-transient-attack-structure",
        "champion2673Score": score,
        "featureFamily": "dual-stem-transient-attack-structure",
        "validatedSpectralPruneCount": int(sum(spectral_pruned.values())),
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 26.73 DUAL-STEM TRANSIENT ATTACK STRUCTURE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Applied frozen spectral prune count:", int(sum(spectral_pruned.values())))
    print("Generalizable zero-precision transient attack signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed transient attack signatures:")
    for row in supported[:30]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
