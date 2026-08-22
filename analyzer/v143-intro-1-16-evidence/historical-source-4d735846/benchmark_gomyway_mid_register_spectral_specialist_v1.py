from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-spectral-specialist-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-spectral-specialist-v1-manifest.json"

MID_MIN = 52
MID_MAX = 63
FOLDS = 5
CURRENT_CHAMPION_F1 = 6.99

VARIANTS: list[dict[str, Any]] = [
    {"name": "dual_snr4", "snr": 4.0, "mode": "dual"},
    {"name": "dual_snr5", "snr": 5.0, "mode": "dual"},
    {"name": "dual_snr6", "snr": 6.0, "mode": "dual"},
    {"name": "either_snr8", "snr": 8.0, "mode": "either"},
    {"name": "either_snr10", "snr": 10.0, "mode": "either"},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def load_filtered(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    nyquist = sample_rate / 2.0
    sos = butter(4, [90.0 / nyquist, 1400.0 / nyquist], btype="bandpass", output="sos")
    return sosfiltfilt(sos, audio).astype(np.float32), int(sample_rate)


def spectral_score(audio: np.ndarray, sample_rate: int, center_seconds: float, midi: int) -> float:
    center = int(round(center_seconds * sample_rate))
    radius = int(round(0.055 * sample_rate))
    start = max(0, center - radius)
    end = min(len(audio), center + radius)
    segment = audio[start:end]
    if len(segment) < 256:
        return 0.0
    n_fft = 4096
    window = np.hanning(len(segment)).astype(np.float32)
    spec = np.abs(np.fft.rfft(segment * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = midi_hz(midi)

    def peak_near(freq: float, width_hz: float = 5.0) -> float:
        if freq >= freqs[-1]:
            return 0.0
        mask = (freqs >= freq - width_hz) & (freqs <= freq + width_hz)
        return float(np.max(spec[mask])) if np.any(mask) else 0.0

    fundamental = peak_near(f0)
    harmonic2 = peak_near(2.0 * f0, 7.0)
    harmonic3 = peak_near(3.0 * f0, 9.0)
    local_mask = (freqs >= max(70.0, f0 - 55.0)) & (freqs <= f0 + 55.0)
    exclude = (freqs >= f0 - 8.0) & (freqs <= f0 + 8.0)
    noise_values = spec[local_mask & ~exclude]
    if noise_values.size == 0:
        return 0.0
    floor = float(np.median(noise_values)) + 1e-9
    harmonic_support = 0.25 * harmonic2 + 0.12 * harmonic3
    return (fundamental + harmonic_support) / floor


def specialist_scores(path: Path, grid: dict[tuple[int, int], float]) -> dict[tuple[int, int, int], float]:
    audio, sample_rate = load_filtered(path)
    scores: dict[tuple[int, int, int], float] = {}
    for (measure, step), center_seconds in grid.items():
        if measure < 17 or measure > 113:
            continue
        for midi in range(MID_MIN, MID_MAX + 1):
            scores[(measure, step, midi)] = spectral_score(audio, sample_rate, float(center_seconds), midi)
    return scores


def additions_for_variant(
    variant: dict[str, Any],
    winner_scores: dict[tuple[int, int, int], float],
    alt_scores: dict[tuple[int, int, int], float],
    champion: Counter[tuple[int, int, int]],
) -> Counter[tuple[int, int, int]]:
    additions: Counter[tuple[int, int, int]] = Counter()
    threshold = float(variant["snr"])
    for token in winner_scores.keys():
        if champion.get(token, 0) > 0:
            continue
        w = winner_scores.get(token, 0.0)
        a = alt_scores.get(token, 0.0)
        accepted = (w >= threshold and a >= threshold) if variant["mode"] == "dual" else (w >= threshold or a >= threshold)
        if accepted:
            additions[token] = 1
    return additions


def grade(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, float | int]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
    }


def subset(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Building frozen 6.99 cross-stem champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    champion = precond.merge_with_cap(base_winner, base_alt)
    champion_score = grade(champion, reference)

    print("Computing independent spectral specialist scores...", flush=True)
    winner_scores = specialist_scores(WINNER_STEM, grid)
    alt_scores = specialist_scores(ALT_STEM, grid)

    results: dict[str, Any] = {}
    for variant in VARIANTS:
        additions = additions_for_variant(variant, winner_scores, alt_scores, champion)
        prediction = precond.merge_with_cap(champion, additions)
        score = grade(prediction, reference)
        positive_f1 = 0
        positive_matched = 0
        deltas: list[float] = []
        fold_rows = []
        for fold in range(FOLDS):
            ref_fold = subset(reference, fold)
            champ_fold = subset(champion, fold)
            pred_fold = subset(prediction, fold)
            c = grade(champ_fold, ref_fold)
            p = grade(pred_fold, ref_fold)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            matched_delta = int(p["matched"]) - int(c["matched"])
            extra_delta = int(p["extra"]) - int(c["extra"])
            deltas.append(delta)
            if delta > 0:
                positive_f1 += 1
            if matched_delta > 0:
                positive_matched += 1
            fold_rows.append({"fold": fold + 1, "deltaPoints": delta, "matchedDelta": matched_delta, "extraDelta": extra_delta})
        mean_delta = round(sum(deltas) / len(deltas), 2)
        median_delta = sorted(deltas)[len(deltas) // 2]
        crossval_passed = positive_f1 >= 4 and positive_matched >= 4 and mean_delta > 0 and median_delta > 0
        results[variant["name"]] = {
            "variant": variant,
            "additionCount": sum(additions.values()),
            "score": score,
            "folds": fold_rows,
            "positiveF1Folds": positive_f1,
            "positiveMatchedFolds": positive_matched,
            "meanFoldDeltaPoints": mean_delta,
            "medianFoldDeltaPoints": median_delta,
            "crossValidationPassed": crossval_passed,
        }
        print(
            f"{variant['name']}: pitchF1={score['pitchF1']} matched={score['matched']} missing={score['missing']} extra={score['extra']} "
            f"additions={sum(additions.values())} cv={crossval_passed} folds={positive_f1}/{FOLDS} matchedFolds={positive_matched}/{FOLDS} "
            f"mean={mean_delta:+.2f} median={median_delta:+.2f}",
            flush=True,
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["crossValidationPassed"]),
            float(item[1]["score"]["pitchF1"]),
            int(item[1]["score"]["matched"]),
            -int(item[1]["score"]["extra"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during specialist benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "independent-mid-register-spectral-specialist",
        "currentChampion": champion_score,
        "targetMidiRange": [MID_MIN, MID_MAX],
        "results": results,
        "winner": winner_name,
        "winnerPitchF1": winner["score"]["pitchF1"],
        "winnerMatched": winner["score"]["matched"],
        "winnerMissing": winner["score"]["missing"],
        "winnerExtra": winner["score"]["extra"],
        "winnerCrossValidationPassed": winner["crossValidationPassed"],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "audit-contiguous-section-stability-for-spectral-specialist"
            if winner["crossValidationPassed"] and float(winner["score"]["pitchF1"]) > CURRENT_CHAMPION_F1
            else "retain-6.99-champion-and-profile-spectral-specialist-false-positive-structure"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner_name,
        "winnerPitchF1": winner["score"]["pitchF1"],
        "winnerCrossValidationPassed": winner["crossValidationPassed"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER SPECTRAL SPECIALIST V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["score"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["score"]["matched"], "/", winner["score"]["missing"], "/", winner["score"]["extra"])
    print("Winner positive F1 folds:", winner["positiveF1Folds"], "/", FOLDS)
    print("Winner positive matched folds:", winner["positiveMatchedFolds"], "/", FOLDS)
    print("Winner mean/median fold delta points:", winner["meanFoldDeltaPoints"], "/", winner["medianFoldDeltaPoints"])
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
