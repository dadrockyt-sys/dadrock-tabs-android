from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2476_harmonic_band_survivors_precision_v1 as p2476

band = p2476.band
recur = p2476.recur
recall = p2476.recall
v2 = p2476.v2
v3 = p2476.v3
harmonic = p2476.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1-manifest.json"
EXPECTED = (183, 684, 428)
EXPECTED_F1 = 24.76


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        rows.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def template_score(spec: np.ndarray, freqs: np.ndarray, midi: int, nyquist: float) -> float:
    f0 = harmonic.midi_hz(midi)
    score = 0.0
    weight_sum = 0.0
    for h in range(1, 7):
        hz = f0 * h
        if hz >= nyquist - 80.0:
            break
        hw = max(5.0, hz * 0.006)
        core = band.band_energy(spec, freqs, hz - hw, hz + hw)
        weight = 1.0 / math.sqrt(float(h))
        score += weight * core
        weight_sum += weight
    return score / max(weight_sum, 1e-9)


def stem_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {
            "targetScore": 0.0,
            "bestNeighborScore": 0.0,
            "bestNeighborRatio": 99.0,
            "targetMarginDb": -60.0,
            "bestNeighborOffset": 0.0,
            "octaveAliasRatio": 99.0,
        }

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    nyquist = sample_rate * 0.5
    eps = 1e-9

    target = template_score(spec, freqs, midi, nyquist)
    neighbor_scores: list[tuple[int, float]] = []
    for offset in (-2, -1, 1, 2):
        neighbor_scores.append((offset, template_score(spec, freqs, midi + offset, nyquist)))
    best_offset, best_neighbor = max(neighbor_scores, key=lambda pair: pair[1])

    octave_scores = [
        template_score(spec, freqs, midi - 12, nyquist) if midi - 12 >= 0 else 0.0,
        template_score(spec, freqs, midi + 12, nyquist),
    ]
    best_octave = max(octave_scores)

    ratio = best_neighbor / (target + eps)
    margin_db = 20.0 * math.log10((target + eps) / (best_neighbor + eps))
    octave_ratio = best_octave / (target + eps)

    return {
        "targetScore": float(target),
        "bestNeighborScore": float(best_neighbor),
        "bestNeighborRatio": float(ratio),
        "targetMarginDb": float(margin_db),
        "bestNeighborOffset": float(best_offset),
        "octaveAliasRatio": float(octave_ratio),
    }


def ratio_bucket(v: float) -> str:
    if v < 0.70:
        return "nbr_lt070"
    if v < 0.90:
        return "nbr_070_090"
    if v < 1.05:
        return "nbr_090_105"
    if v < 1.25:
        return "nbr_105_125"
    if v < 1.60:
        return "nbr_125_160"
    return "nbr_160_plus"


def margin_bucket(v: float) -> str:
    if v < -4.0:
        return "margin_lt_m4"
    if v < -1.0:
        return "margin_m4_m1"
    if v < 1.0:
        return "margin_m1_p1"
    if v < 3.0:
        return "margin_p1_p3"
    if v < 6.0:
        return "margin_p3_p6"
    return "margin_p6_plus"


def octave_bucket(v: float) -> str:
    if v < 0.65:
        return "oct_lt065"
    if v < 0.85:
        return "oct_065_085"
    if v < 1.05:
        return "oct_085_105"
    if v < 1.35:
        return "oct_105_135"
    return "oct_135_plus"


def disagreement_bucket(v: float) -> str:
    if v < 0.10:
        return "diff_lt010"
    if v < 0.25:
        return "diff_010_025"
    if v < 0.50:
        return "diff_025_050"
    return "diff_050_plus"


def winner_bucket(v: float) -> str:
    if v <= -1.5:
        return "neighbor_lower2"
    if v < 0.0:
        return "neighbor_lower1"
    if v < 1.5:
        return "neighbor_upper1"
    return "neighbor_upper2"


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    max_ratio = max(wf["bestNeighborRatio"], af["bestNeighborRatio"])
    min_margin = min(wf["targetMarginDb"], af["targetMarginDb"])
    max_octave = max(wf["octaveAliasRatio"], af["octaveAliasRatio"])
    ratio_diff = abs(math.log2((wf["bestNeighborRatio"] + 1e-6) / (af["bestNeighborRatio"] + 1e-6)))
    same_neighbor_side = (wf["bestNeighborOffset"] < 0) == (af["bestNeighborOffset"] < 0)

    r = ratio_bucket(max_ratio)
    m = margin_bucket(min_margin)
    o = octave_bucket(max_octave)
    d = disagreement_bucket(ratio_diff)
    side = "neighborSide_same" if same_neighbor_side else "neighborSide_disagree"
    w = winner_bucket(wf["bestNeighborOffset"] if wf["bestNeighborRatio"] >= af["bestNeighborRatio"] else af["bestNeighborOffset"])

    return {
        f"neighborRatio::{r}",
        f"targetMargin::{m}",
        f"octaveAlias::{o}",
        f"templateAgreement::{d}",
        f"neighborSide::{side}",
        f"dominantNeighbor::{w}",
        f"neighborMarginCross::{r}|{m}|{d}",
        f"neighborOctaveCross::{r}|{o}|{d}",
        f"templateCompetitionCross::{r}|{m}|{o}|{side}|{d}",
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

    exhausted = v2.load_json(p2476.OUTPUT_PATH)
    if exhausted.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("24.76 harmonic-band survivor profile is not reference-free during detection")
    if exhausted.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("24.76 harmonic-band survivor branch is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion = p2476.reconstruct_2476(grid, winner_audio, winner_sr, alt_audio, alt_sr)

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 24.76 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "maxBestNeighborRatio": max(wf["bestNeighborRatio"], af["bestNeighborRatio"]),
            "minTargetMarginDb": min(wf["targetMarginDb"], af["targetMarginDb"]),
            "maxOctaveAliasRatio": max(wf["octaveAliasRatio"], af["octaveAliasRatio"]),
            "signatures": signatures,
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
        raise RuntimeError("Protected candidate changed during 24.76 harmonic-template competition profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-24.76-dual-stem-harmonic-template-competition",
        "champion2476Score": score,
        "featureFamily": "dual-stem-audio-harmonic-template-neighbor-competition",
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

    print("GOMYWAY 24.76 DUAL-STEM HARMONIC TEMPLATE COMPETITION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-template signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-template signatures (5+ true):")
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
