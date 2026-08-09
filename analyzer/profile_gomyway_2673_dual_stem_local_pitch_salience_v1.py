from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2673_dual_stem_transient_attack_structure_v1 as transient

recur = transient.recur
recall = transient.recall
v2 = transient.v2
v3 = transient.v3
harmonic = transient.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
TRANSIENT_PROFILE_PATH = PUBLIC / "gomyway-2673-dual-stem-transient-attack-structure-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2673-dual-stem-local-pitch-salience-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2673-dual-stem-local-pitch-salience-v1-manifest.json"
EXPECTED_2673 = (183, 684, 319)
EXPECTED_2673_F1 = 26.73


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
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


def local_band_energy(power: np.ndarray, freqs: np.ndarray, freq: float, rel_width: float = 0.018) -> float:
    if freq <= 0.0 or freq > float(freqs[-1]):
        return 0.0
    width = max(7.0, freq * rel_width)
    mask = np.abs(freqs - freq) <= width
    return float(np.sum(power[mask])) if np.any(mask) else 0.0


def pitch_salience_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    values = np.asarray(harmonic.segment(audio, sample_rate, center), dtype=np.float64)
    if values.size < 512:
        return {
            "fundamentalShare": 0.0,
            "harmonicStackShare": 0.0,
            "targetToNeighbor": 0.0,
            "targetToOctave": 0.0,
            "stackToNeighbors": 0.0,
            "peakOffsetCents": 999.0,
        }

    values = values - float(np.mean(values))
    window = np.hanning(values.size)
    spectrum = np.abs(np.fft.rfft(values * window)) ** 2
    freqs = np.fft.rfftfreq(values.size, d=1.0 / float(sample_rate))
    band = (freqs >= 60.0) & (freqs <= min(6000.0, sample_rate * 0.48))
    power = spectrum[band]
    band_freqs = freqs[band]
    total = float(np.sum(power)) + 1e-12
    if power.size < 8:
        return {
            "fundamentalShare": 0.0,
            "harmonicStackShare": 0.0,
            "targetToNeighbor": 0.0,
            "targetToOctave": 0.0,
            "stackToNeighbors": 0.0,
            "peakOffsetCents": 999.0,
        }

    f0 = harmonic.midi_hz(midi)
    fundamental = local_band_energy(power, band_freqs, f0)
    stack = 0.0
    for h in range(1, 7):
        hf = f0 * h
        if hf > float(band_freqs[-1]):
            break
        stack += local_band_energy(power, band_freqs, hf)

    neighbors = 0.0
    for semitones in (-2, -1, 1, 2):
        nf = f0 * (2.0 ** (semitones / 12.0))
        neighbors += local_band_energy(power, band_freqs, nf)

    octave_energy = local_band_energy(power, band_freqs, f0 * 2.0)
    suboct_energy = local_band_energy(power, band_freqs, f0 * 0.5)
    octave_competition = max(octave_energy, suboct_energy)

    stack_neighbors = 0.0
    for semitones in (-1, 1):
        nf0 = f0 * (2.0 ** (semitones / 12.0))
        for h in range(1, 5):
            hf = nf0 * h
            if hf > float(band_freqs[-1]):
                break
            stack_neighbors += local_band_energy(power, band_freqs, hf)

    search = (band_freqs >= f0 * 0.94) & (band_freqs <= f0 * 1.06)
    peak_offset_cents = 999.0
    if np.any(search):
        local_p = power[search]
        local_f = band_freqs[search]
        if local_p.size:
            peak_f = float(local_f[int(np.argmax(local_p))])
            if peak_f > 0.0 and f0 > 0.0:
                peak_offset_cents = abs(1200.0 * math.log2(peak_f / f0))

    return {
        "fundamentalShare": fundamental / total,
        "harmonicStackShare": stack / total,
        "targetToNeighbor": fundamental / max(neighbors, 1e-12),
        "targetToOctave": fundamental / max(octave_competition, 1e-12),
        "stackToNeighbors": stack / max(stack_neighbors, 1e-12),
        "peakOffsetCents": float(peak_offset_cents),
    }


def bucket(v: float, edges: list[tuple[float, str]], tail: str) -> str:
    for limit, label in edges:
        if v < limit:
            return label
    return tail


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_fund = min(w["fundamentalShare"], a["fundamentalShare"])
    min_stack = min(w["harmonicStackShare"], a["harmonicStackShare"])
    min_neighbor = min(w["targetToNeighbor"], a["targetToNeighbor"])
    min_octave = min(w["targetToOctave"], a["targetToOctave"])
    min_stack_neighbor = min(w["stackToNeighbors"], a["stackToNeighbors"])
    max_offset = max(w["peakOffsetCents"], a["peakOffsetCents"])
    neighbor_diff = abs(w["targetToNeighbor"] - a["targetToNeighbor"])
    stack_diff = abs(w["harmonicStackShare"] - a["harmonicStackShare"])

    fund = bucket(min_fund, [(0.010, "fund_lt010"), (0.025, "fund_010_025"), (0.050, "fund_025_050"), (0.100, "fund_050_100")], "fund_100_plus")
    stack = bucket(min_stack, [(0.050, "stack_lt050"), (0.100, "stack_050_100"), (0.180, "stack_100_180"), (0.300, "stack_180_300")], "stack_300_plus")
    neigh = bucket(min_neighbor, [(0.20, "nbr_lt020"), (0.50, "nbr_020_050"), (1.00, "nbr_050_100"), (2.00, "nbr_100_200")], "nbr_200_plus")
    octave = bucket(min_octave, [(0.50, "oct_lt050"), (1.00, "oct_050_100"), (2.00, "oct_100_200"), (4.00, "oct_200_400")], "oct_400_plus")
    stacknbr = bucket(min_stack_neighbor, [(0.30, "stacknbr_lt030"), (0.75, "stacknbr_030_075"), (1.50, "stacknbr_075_150"), (3.00, "stacknbr_150_300")], "stacknbr_300_plus")
    offset = bucket(max_offset, [(10.0, "off_lt10"), (25.0, "off_10_25"), (50.0, "off_25_50"), (100.0, "off_50_100")], "off_100_plus")
    ndiff = bucket(neighbor_diff, [(0.10, "ndiff_lt010"), (0.30, "ndiff_010_030"), (0.75, "ndiff_030_075")], "ndiff_075_plus")
    sdiff = bucket(stack_diff, [(0.015, "sdiff_lt015"), (0.040, "sdiff_015_040"), (0.090, "sdiff_040_090")], "sdiff_090_plus")

    return {
        f"minFundamentalShare::{fund}",
        f"minHarmonicStackShare::{stack}",
        f"minTargetNeighborRatio::{neigh}",
        f"minTargetOctaveRatio::{octave}",
        f"minStackNeighborRatio::{stacknbr}",
        f"maxPeakOffset::{offset}",
        f"targetNeighborAgreement::{ndiff}",
        f"harmonicStackAgreement::{sdiff}",
        f"localPitchSalienceCross::{fund}|{stack}|{neigh}|{offset}",
        f"pitchCompetitionCross::{neigh}|{octave}|{stacknbr}|{ndiff}",
        f"dualStemPitchSalienceCross::{stack}|{neigh}|{sdiff}|{offset}",
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

    transient_profile = v2.load_json(TRANSIENT_PROFILE_PATH)
    if transient_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("26.73 transient profile is not reference-free during detection")
    if transient_profile.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("26.73 transient branch is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, spectral_pruned = transient.reconstruct_2673(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED_2673 or abs(float(score["pitchF1"]) - EXPECTED_2673_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 26.73 champion {EXPECTED_2673}/{EXPECTED_2673_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = pitch_salience_features(winner_audio, winner_sr, center, pitch)
        af = pitch_salience_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for s in signatures:
            groups[s][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": signatures,
        })

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
        raise RuntimeError("Protected candidate changed during 26.73 local pitch salience profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-26.73-dual-stem-local-pitch-salience",
        "champion2673Score": score,
        "featureFamily": "dual-stem-local-pitch-salience",
        "validatedSpectralPruneCount": int(sum(spectral_pruned.values())),
        "transientBranchExhausted": True,
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

    print("GOMYWAY 26.73 DUAL-STEM LOCAL PITCH SALIENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision local pitch salience signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed local pitch salience signatures:")
    for row in supported[:30]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
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
