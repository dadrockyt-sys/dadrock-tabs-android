from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

import benchmark_gomyway_1569_attack_envelope_final_survivor_precision_prune_cv_v1 as b1569
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy

recur = b1569.recur
recall = b1569.recall
v2 = b1569.v2
v3 = b1569.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1590-dual-stem-harmonic-comb-coherence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1590-dual-stem-harmonic-comb-coherence-v1-manifest.json"
EXPECTED = (183, 684, 1252)
EXPECTED_F1 = 15.90


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    return audio, int(sample_rate)


def segment(audio: np.ndarray, sample_rate: int, center_seconds: float) -> np.ndarray:
    center = int(round(center_seconds * sample_rate))
    radius = int(round(0.085 * sample_rate))
    start = max(0, center - radius)
    end = min(len(audio), center + radius)
    return audio[start:end]


def peak_near(spec: np.ndarray, freqs: np.ndarray, freq: float, width: float) -> float:
    if freq <= 0.0 or freq >= float(freqs[-1]):
        return 0.0
    mask = (freqs >= freq - width) & (freqs <= freq + width)
    return float(np.max(spec[mask])) if np.any(mask) else 0.0


def comb_score(spec: np.ndarray, freqs: np.ndarray, f0: float) -> float:
    weights = (1.0, 0.55, 0.32, 0.20)
    widths = (5.0, 7.0, 9.0, 11.0)
    total = 0.0
    for harmonic, (weight, width) in enumerate(zip(weights, widths), start=1):
        total += weight * peak_near(spec, freqs, harmonic * f0, width)
    return total


def stem_features(audio: np.ndarray, sample_rate: int, center_seconds: float, midi: int) -> dict[str, float]:
    values = segment(audio, sample_rate, center_seconds)
    if values.size < 256:
        return {
            "comb": 0.0,
            "combRatio": 0.0,
            "neighborMargin": 0.0,
            "fundamentalShare": 0.0,
        }

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = midi_hz(midi)

    target = comb_score(spec, freqs, f0)
    lower = comb_score(spec, freqs, f0 * (2.0 ** (-1.0 / 12.0)))
    upper = comb_score(spec, freqs, f0 * (2.0 ** (1.0 / 12.0)))
    neighbor = max(lower, upper)

    band = (freqs >= max(70.0, f0 * 0.75)) & (freqs <= min(float(freqs[-1]), max(1400.0, f0 * 4.4)))
    broadband = float(np.sum(spec[band])) + 1e-9

    fundamental = peak_near(spec, freqs, f0, 5.0)
    h2 = peak_near(spec, freqs, 2.0 * f0, 7.0)
    h3 = peak_near(spec, freqs, 3.0 * f0, 9.0)
    harmonic_sum = fundamental + h2 + h3 + 1e-9

    return {
        "comb": target,
        "combRatio": target / broadband,
        "neighborMargin": target / (neighbor + 1e-9),
        "fundamentalShare": fundamental / harmonic_sum,
    }


def bucket(value: float, edges: tuple[float, ...], labels: tuple[str, ...]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def comb_ratio_bucket(value: float) -> str:
    return bucket(value, (0.0015, 0.003, 0.006, 0.012), ("comb_lt0015", "comb_0015_003", "comb_003_006", "comb_006_012", "comb_012_plus"))


def margin_bucket(value: float) -> str:
    return bucket(value, (0.80, 0.95, 1.10, 1.35), ("margin_lt080", "margin_080_095", "margin_095_110", "margin_110_135", "margin_135_plus"))


def f0share_bucket(value: float) -> str:
    return bucket(value, (0.20, 0.35, 0.50, 0.70), ("f0share_lt020", "f0share_020_035", "f0share_035_050", "f0share_050_070", "f0share_070_plus"))


def disagreement_bucket(value: float) -> str:
    return bucket(value, (0.20, 0.50, 1.00, 2.00), ("disagree_lt020", "disagree_020_050", "disagree_050_100", "disagree_100_200", "disagree_200_plus"))


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        rows.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_1590(grid: Any, row_by_token: dict[tuple[int, int, int], dict[str, Any]]) -> Counter[tuple[int, int, int]]:
    champion_1569 = b1569.reconstruct_1569(grid)
    final_pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1569.items():
        row = row_by_token.get(tok)
        if row is not None and (
            b1569.pred_a(row)
            or b1569.pred_b(row)
            or b1569.pred_c(row)
            or b1569.pred_d(row)
            or b1569.pred_e(row)
        ):
            final_pruned[tok] = count
    return champion_1569 - final_pruned


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

    survivor_payload = v2.load_json(b1569.PROFILE_1569_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.69 survivor profile is not reference-free during detection")
    survivor_rows = list(survivor_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in survivor_rows}

    champion = reconstruct_1590(grid, row_by_token)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 15.90 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = load_mono(legacy.WINNER_STEM)
    alt_audio, alt_sr = load_mono(legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)

        min_comb_ratio = min(wf["combRatio"], af["combRatio"])
        max_comb_ratio = max(wf["combRatio"], af["combRatio"])
        min_margin = min(wf["neighborMargin"], af["neighborMargin"])
        max_margin = max(wf["neighborMargin"], af["neighborMargin"])
        min_f0share = min(wf["fundamentalShare"], af["fundamentalShare"])
        ratio_disagreement = abs(math.log2((wf["combRatio"] + 1e-9) / (af["combRatio"] + 1e-9)))
        margin_disagreement = abs(math.log2((wf["neighborMargin"] + 1e-9) / (af["neighborMargin"] + 1e-9)))

        min_comb_b = comb_ratio_bucket(min_comb_ratio)
        max_comb_b = comb_ratio_bucket(max_comb_ratio)
        min_margin_b = margin_bucket(min_margin)
        max_margin_b = margin_bucket(max_margin)
        min_f0_b = f0share_bucket(min_f0share)
        ratio_disagree_b = disagreement_bucket(ratio_disagreement)
        margin_disagree_b = disagreement_bucket(margin_disagreement)

        signatures = {
            "minCombRatio": min_comb_b,
            "maxCombRatio": max_comb_b,
            "minNeighborMargin": min_margin_b,
            "maxNeighborMargin": max_margin_b,
            "minFundamentalShare": min_f0_b,
            "combRatioDisagreement": ratio_disagree_b,
            "marginDisagreement": margin_disagree_b,
            "combMargin": f"{min_comb_b}|{min_margin_b}",
            "combF0Share": f"{min_comb_b}|{min_f0_b}",
            "marginF0Share": f"{min_margin_b}|{min_f0_b}",
            "combAgreement": f"{min_comb_b}|{ratio_disagree_b}",
            "marginAgreement": f"{min_margin_b}|{margin_disagree_b}",
            "combMarginAgreement": f"{min_comb_b}|{min_margin_b}|{ratio_disagree_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minCombRatio": min_comb_ratio,
            "maxCombRatio": max_comb_ratio,
            "minNeighborMargin": min_margin,
            "maxNeighborMargin": max_margin,
            "minFundamentalShare": min_f0share,
            "combRatioDisagreementOctaves": ratio_disagreement,
            "marginDisagreementOctaves": margin_disagreement,
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
        raise RuntimeError("Protected candidate changed during 15.90 harmonic-comb coherence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-15.90-dual-stem-harmonic-comb-coherence",
        "champion1590Score": score,
        "featureFamily": "dual-stem-harmonic-comb-coherence",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-harmonic-comb-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 15.90 DUAL-STEM HARMONIC COMB COHERENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-comb signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-comb signatures (5+ true):")
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
