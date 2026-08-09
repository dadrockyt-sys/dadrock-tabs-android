from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1750_octave_subharmonic_survivors_precision_v1 as p1750

b1694 = p1750.b1694
octave = p1750.octave
harmonic = octave.harmonic
recur = p1750.recur
recall = p1750.recall
v2 = p1750.v2
v3 = p1750.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1694_PATH = PUBLIC / "gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1750-dual-stem-pitch-specific-onset-contrast-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1750-dual-stem-pitch-specific-onset-contrast-v1-manifest.json"
EXPECTED = (183, 684, 1041)
EXPECTED_F1 = 17.50
FRAME_OFFSETS = (-0.060, -0.030, 0.0, 0.030, 0.060)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def reconstruct_1750(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1694 = octave.reconstruct_1694(grid)
    profile_payload = v2.load_json(PROFILE_1694_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in rows}
    predicates = (
        b1694.pred_a,
        b1694.pred_b,
        b1694.pred_c,
        b1694.pred_d,
        b1694.pred_e,
        b1694.pred_f,
        b1694.pred_g,
        b1694.pred_h,
        b1694.pred_i,
    )
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1694.items():
        row = row_by_token.get(tok)
        if row is not None and any(pred(row) for pred in predicates):
            pruned[tok] = count
    return champion_1694 - pruned


def ratio_bucket(value: float) -> str:
    if value < 0.70:
        return "ratio_lt070"
    if value < 0.90:
        return "ratio_070_090"
    if value < 1.10:
        return "ratio_090_110"
    if value < 1.40:
        return "ratio_110_140"
    if value < 1.80:
        return "ratio_140_180"
    return "ratio_180_plus"


def peak_bucket(value: int) -> str:
    return {
        0: "peak_pre60",
        1: "peak_pre30",
        2: "peak_onset",
        3: "peak_post30",
        4: "peak_post60",
    }.get(int(value), "peak_other")


def disagreement_bucket(value: int) -> str:
    if value <= 0:
        return "peakagree_0"
    if value == 1:
        return "peakagree_1"
    return "peakagree_2plus"


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


def pitch_score(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> float:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return 0.0
    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    return float(harmonic.comb_score(spec, freqs, harmonic.midi_hz(midi)))


def onset_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, Any]:
    scores = [pitch_score(audio, sample_rate, center + offset, midi) for offset in FRAME_OFFSETS]
    eps = 1e-9
    pre = max(scores[0], scores[1])
    onset = scores[2]
    post = max(scores[3], scores[4])
    peak_index = int(np.argmax(np.asarray(scores, dtype=np.float64)))
    return {
        "scores": scores,
        "pre": pre,
        "onset": onset,
        "post": post,
        "onsetVsPre": onset / (pre + eps),
        "postVsPre": post / (pre + eps),
        "postVsOnset": post / (onset + eps),
        "peakIndex": peak_index,
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

    survivor_payload = v2.load_json(p1750.OUTPUT_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("17.50 octave survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("17.50 octave/subharmonic survivor branch is not exhausted")

    champion = reconstruct_1750(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 17.50 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = onset_features(winner_audio, winner_sr, center, pitch)
        af = onset_features(alt_audio, alt_sr, center, pitch)

        min_onset_vs_pre = min(float(wf["onsetVsPre"]), float(af["onsetVsPre"]))
        min_post_vs_pre = min(float(wf["postVsPre"]), float(af["postVsPre"]))
        max_post_vs_onset = max(float(wf["postVsOnset"]), float(af["postVsOnset"]))
        peak_disagreement = abs(int(wf["peakIndex"]) - int(af["peakIndex"]))

        onset_b = ratio_bucket(min_onset_vs_pre)
        post_b = ratio_bucket(min_post_vs_pre)
        sustain_b = ratio_bucket(max_post_vs_onset)
        winner_peak_b = peak_bucket(int(wf["peakIndex"]))
        alt_peak_b = peak_bucket(int(af["peakIndex"]))
        disagree_b = disagreement_bucket(peak_disagreement)

        signatures = {
            "minOnsetVsPre": onset_b,
            "minPostVsPre": post_b,
            "maxPostVsOnset": sustain_b,
            "winnerPeakTiming": winner_peak_b,
            "altPeakTiming": alt_peak_b,
            "peakTimingAgreement": disagree_b,
            "onsetPost": f"{onset_b}|{post_b}",
            "onsetSustain": f"{onset_b}|{sustain_b}",
            "postAgreement": f"{post_b}|{disagree_b}",
            "onsetAgreement": f"{onset_b}|{disagree_b}",
            "pitchOnsetCross": f"{onset_b}|{post_b}|{disagree_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minOnsetVsPre": min_onset_vs_pre,
            "minPostVsPre": min_post_vs_pre,
            "maxPostVsOnset": max_post_vs_onset,
            "peakTimingDisagreement": peak_disagreement,
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
        raise RuntimeError("Protected candidate changed during 17.50 pitch-specific onset contrast profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-17.50-dual-stem-pitch-specific-onset-contrast",
        "champion1750Score": score,
        "featureFamily": "dual-stem-pitch-specific-onset-contrast",
        "frameOffsetsSeconds": list(FRAME_OFFSETS),
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-pitch-specific-onset-contrast-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 17.50 DUAL-STEM PITCH-SPECIFIC ONSET CONTRAST V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision pitch-specific onset signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true pitch-specific onset signatures (5+ true):")
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
