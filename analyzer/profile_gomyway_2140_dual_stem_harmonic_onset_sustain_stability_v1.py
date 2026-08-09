from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2144_local_pitch_competition_survivors_precision_v1 as p2144

b2134 = p2144.b2134
comp = p2144.comp
recur = p2144.recur
recall = p2144.recall
v2 = p2144.v2
v3 = p2144.v3
harmonic = p2144.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LOCAL_SURVIVOR_PATH = PUBLIC / "gomyway-2144-local-pitch-competition-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2140-dual-stem-harmonic-onset-sustain-stability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2140-dual-stem-harmonic-onset-sustain-stability-v1-manifest.json"
EXPECTED = (183, 684, 660)
EXPECTED_F1 = 21.40
TARGET_SIGNATURE = b2134.TARGET_SIGNATURE


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        out.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def audio_slice(audio: np.ndarray, sample_rate: int, start_time: float, end_time: float) -> np.ndarray:
    start = max(0, int(round(start_time * sample_rate)))
    end = min(int(audio.shape[0]), int(round(end_time * sample_rate)))
    if end <= start:
        return np.zeros(0, dtype=np.float32)
    return np.asarray(audio[start:end], dtype=np.float32)


def comb_score_window(
    audio: np.ndarray,
    sample_rate: int,
    center: float,
    midi: int,
    offset_start: float,
    offset_end: float,
) -> float:
    values = audio_slice(audio, sample_rate, center + offset_start, center + offset_end)
    if values.size < 128:
        return 0.0
    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9
    score = 0.0
    weight = 0.0
    for h in range(1, 6):
        hz = f0 * h
        if hz >= nyquist - 20.0:
            break
        half = max(4.0, hz * 0.006)
        mask = (freqs >= hz - half) & (freqs <= hz + half)
        if np.any(mask):
            w = 1.0 / h
            score += w * float(np.max(spec[mask]))
            weight += w
    return score / (weight + eps)


def stem_stability(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    attack = comb_score_window(audio, sample_rate, center, midi, -0.020, 0.080)
    early = comb_score_window(audio, sample_rate, center, midi, 0.080, 0.180)
    sustain = comb_score_window(audio, sample_rate, center, midi, 0.180, 0.340)
    eps = 1e-9
    early_retention = early / (attack + eps)
    sustain_retention = sustain / (attack + eps)
    sustain_vs_early = sustain / (early + eps)
    decay_margin = (sustain - attack) / (sustain + attack + eps)
    return {
        "attackComb": attack,
        "earlyComb": early,
        "sustainComb": sustain,
        "earlyRetention": early_retention,
        "sustainRetention": sustain_retention,
        "sustainVsEarly": sustain_vs_early,
        "decayMargin": decay_margin,
    }


def retention_bucket(value: float) -> str:
    if value < 0.15:
        return "ret_lt015"
    if value < 0.35:
        return "ret_015_035"
    if value < 0.60:
        return "ret_035_060"
    if value < 0.90:
        return "ret_060_090"
    if value < 1.25:
        return "ret_090_125"
    return "ret_125_plus"


def decay_bucket(value: float) -> str:
    if value < -0.70:
        return "decay_lt_n070"
    if value < -0.40:
        return "decay_n070_n040"
    if value < -0.15:
        return "decay_n040_n015"
    if value < 0.15:
        return "decay_n015_015"
    return "decay_015_plus"


def diff_bucket(value: float) -> str:
    if value < 0.15:
        return "diff_lt015"
    if value < 0.35:
        return "diff_015_035"
    if value < 0.70:
        return "diff_035_070"
    return "diff_070_plus"


def reconstruct_2140(
    grid: Any,
    winner_audio: np.ndarray,
    winner_sr: int,
    alt_audio: np.ndarray,
    alt_sr: int,
) -> Counter[tuple[int, int, int]]:
    champion_2134 = comp.reconstruct_2134(grid)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2134.items():
        row = p2144.current_competition_row(
            tok,
            int(count),
            grid,
            winner_audio,
            winner_sr,
            alt_audio,
            alt_sr,
        )
        if TARGET_SIGNATURE in b2134.row_signatures(row):
            pruned[tok] = count
    if int(sum(pruned.values())) != 5:
        raise RuntimeError(f"Expected validated local-pitch prune count 5, got {sum(pruned.values())}")
    return champion_2134 - pruned


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

    local_survivor = v2.load_json(LOCAL_SURVIVOR_PATH)
    if local_survivor.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Local-pitch survivor profile is not reference-free during detection")
    if local_survivor.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("21.40 local-pitch-competition branch is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    champion = reconstruct_2140(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 21.40 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch_midi = tok
        center = float(grid[(measure, step)])
        wf = stem_stability(winner_audio, winner_sr, center, pitch_midi)
        af = stem_stability(alt_audio, alt_sr, center, pitch_midi)

        min_early = min(float(wf["earlyRetention"]), float(af["earlyRetention"]))
        min_sustain = min(float(wf["sustainRetention"]), float(af["sustainRetention"]))
        min_sve = min(float(wf["sustainVsEarly"]), float(af["sustainVsEarly"]))
        min_decay = min(float(wf["decayMargin"]), float(af["decayMargin"]))
        sustain_diff = abs(float(wf["sustainRetention"]) - float(af["sustainRetention"]))

        early_b = retention_bucket(min_early)
        sustain_b = retention_bucket(min_sustain)
        sve_b = retention_bucket(min_sve)
        decay_b = decay_bucket(min_decay)
        diff_b = diff_bucket(sustain_diff)

        signatures = {
            "earlyRetention": early_b,
            "sustainRetention": sustain_b,
            "sustainVsEarly": sve_b,
            "decayMargin": decay_b,
            "stemRetentionDiff": diff_b,
            "retentionCross": f"{early_b}|{sustain_b}|{diff_b}",
            "decayCross": f"{sustain_b}|{decay_b}|{diff_b}",
            "fullStabilityCross": f"{early_b}|{sustain_b}|{sve_b}|{decay_b}|{diff_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minEarlyRetention": min_early,
            "minSustainRetention": min_sustain,
            "minSustainVsEarly": min_sve,
            "minDecayMargin": min_decay,
            "sustainRetentionStemDifference": sustain_diff,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 21.40 harmonic onset-sustain stability profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-21.40-dual-stem-harmonic-onset-sustain-stability",
        "champion2140Score": score,
        "featureFamily": "dual-stem-harmonic-onset-sustain-stability",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-onset-sustain-stability-signatures-with-prune-specific-heldout-cv",
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
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 21.40 DUAL-STEM HARMONIC ONSET-SUSTAIN STABILITY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision onset-sustain stability signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true onset-sustain stability signatures (5+ true):")
    for row in supported_true[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
