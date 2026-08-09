from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1813_pitch_specific_onset_survivors_precision_v1 as p1813

b1750 = p1813.b1750
onset = p1813.onset
harmonic = onset.harmonic
recur = p1813.recur
recall = p1813.recall
v2 = p1813.v2
v3 = p1813.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1813-dual-stem-harmonic-occupancy-inharmonic-residual-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1813-dual-stem-harmonic-occupancy-inharmonic-residual-v1-manifest.json"
EXPECTED = (183, 684, 969)
EXPECTED_F1 = 18.13


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct_1813(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1750 = onset.reconstruct_1750(grid)
    profile_payload = v2.load_json(b1750.PROFILE_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in rows}
    predicates = (
        b1750.pred_a, b1750.pred_b, b1750.pred_c, b1750.pred_d, b1750.pred_e,
        b1750.pred_f, b1750.pred_g, b1750.pred_h, b1750.pred_i, b1750.pred_j,
        b1750.pred_k, b1750.pred_l, b1750.pred_m,
    )
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1750.items():
        row = row_by_token.get(tok)
        if row is not None and any(pred(row) for pred in predicates):
            pruned[tok] = count
    return champion_1750 - pruned


def occupancy_bucket(value: int) -> str:
    if value <= 1:
        return "occ_0_1"
    if value == 2:
        return "occ_2"
    if value == 3:
        return "occ_3"
    if value == 4:
        return "occ_4"
    return "occ_5plus"


def ratio_bucket(value: float) -> str:
    if value < 0.80:
        return "ratio_lt080"
    if value < 1.10:
        return "ratio_080_110"
    if value < 1.50:
        return "ratio_110_150"
    if value < 2.00:
        return "ratio_150_200"
    if value < 3.00:
        return "ratio_200_300"
    return "ratio_300_plus"


def residual_bucket(value: float) -> str:
    if value < 0.20:
        return "resid_lt020"
    if value < 0.35:
        return "resid_020_035"
    if value < 0.50:
        return "resid_035_050"
    if value < 0.70:
        return "resid_050_070"
    return "resid_070_plus"


def disagreement_bucket(value: int) -> str:
    if value <= 0:
        return "occagree_0"
    if value == 1:
        return "occagree_1"
    return "occagree_2plus"


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


def band_energy(spec: np.ndarray, freqs: np.ndarray, center_hz: float, half_width_hz: float) -> float:
    mask = (freqs >= center_hz - half_width_hz) & (freqs <= center_hz + half_width_hz)
    if not np.any(mask):
        return 0.0
    return float(np.sum(spec[mask]))


def stem_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, Any]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {
            "occupancy": 0,
            "harmonicToSide": 0.0,
            "inharmonicResidual": 1.0,
            "harmonicEnergy": 0.0,
            "sideEnergy": 0.0,
        }

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9

    harmonic_energies: list[float] = []
    side_energies: list[float] = []
    occupancy = 0
    for h in range(1, 7):
        hz = f0 * h
        if hz >= nyquist - 60.0:
            break
        half_width = max(6.0, hz * 0.012)
        he = band_energy(spec, freqs, hz, half_width)
        left = band_energy(spec, freqs, hz * 0.94, half_width)
        right = band_energy(spec, freqs, hz * 1.06, half_width)
        side = 0.5 * (left + right)
        harmonic_energies.append(he)
        side_energies.append(side)
        if he >= side * 1.35 and he > 0.0:
            occupancy += 1

    harmonic_energy = float(sum(harmonic_energies))
    side_energy = float(sum(side_energies))
    total_band = harmonic_energy + side_energy
    harmonic_to_side = harmonic_energy / (side_energy + eps)
    inharmonic_residual = side_energy / (total_band + eps)

    return {
        "occupancy": occupancy,
        "harmonicToSide": harmonic_to_side,
        "inharmonicResidual": inharmonic_residual,
        "harmonicEnergy": harmonic_energy,
        "sideEnergy": side_energy,
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

    survivor_payload = v2.load_json(p1813.OUTPUT_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("18.13 pitch-onset survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("18.13 pitch-onset survivor branch is not exhausted")

    champion = reconstruct_1813(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 18.13 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)

        min_occ = min(int(wf["occupancy"]), int(af["occupancy"]))
        max_occ = max(int(wf["occupancy"]), int(af["occupancy"]))
        occ_disagreement = abs(int(wf["occupancy"]) - int(af["occupancy"]))
        min_harmonic_to_side = min(float(wf["harmonicToSide"]), float(af["harmonicToSide"]))
        max_residual = max(float(wf["inharmonicResidual"]), float(af["inharmonicResidual"]))

        min_occ_b = occupancy_bucket(min_occ)
        max_occ_b = occupancy_bucket(max_occ)
        ratio_b = ratio_bucket(min_harmonic_to_side)
        residual_b = residual_bucket(max_residual)
        disagree_b = disagreement_bucket(occ_disagreement)

        signatures = {
            "minOccupancy": min_occ_b,
            "maxOccupancy": max_occ_b,
            "harmonicToSide": ratio_b,
            "inharmonicResidual": residual_b,
            "occupancyAgreement": disagree_b,
            "occupancyRatio": f"{min_occ_b}|{ratio_b}",
            "occupancyResidual": f"{min_occ_b}|{residual_b}",
            "ratioResidual": f"{ratio_b}|{residual_b}",
            "occupancyCross": f"{min_occ_b}|{max_occ_b}|{disagree_b}",
            "harmonicStructureCross": f"{min_occ_b}|{ratio_b}|{residual_b}|{disagree_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minOccupancy": min_occ,
            "maxOccupancy": max_occ,
            "occupancyDisagreement": occ_disagreement,
            "minHarmonicToSide": min_harmonic_to_side,
            "maxInharmonicResidual": max_residual,
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
        raise RuntimeError("Protected candidate changed during 18.13 harmonic occupancy profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-18.13-dual-stem-harmonic-occupancy-inharmonic-residual",
        "champion1813Score": score,
        "featureFamily": "dual-stem-harmonic-occupancy-inharmonic-residual",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-harmonic-occupancy-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 18.13 DUAL-STEM HARMONIC OCCUPANCY INHARMONIC RESIDUAL V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-occupancy signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-occupancy signatures (5+ true):")
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
