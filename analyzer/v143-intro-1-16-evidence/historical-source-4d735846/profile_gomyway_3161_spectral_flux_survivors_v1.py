from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_3161_harmonic_comb_alignment_survivors_v1 as comb3161
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = comb3161.recur
recall = comb3161.recall
v2 = comb3161.v2
v3 = comb3161.v3
harmonic = comb3161.harmonic
phase = comb3161.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-spectral-flux-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-spectral-flux-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def stem_flux_features(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    offsets = [-0.060, -0.030, 0.0, 0.030, 0.060]
    spectra: list[np.ndarray] = []
    energies: list[float] = []
    for off in offsets:
        z, _ = phase._frame_complex(audio, sr, center, off, win_s=0.060)
        mag = np.abs(z).astype(float)
        mag /= float(np.sum(mag) + 1e-12)
        spectra.append(mag)
        energies.append(float(np.sum(np.abs(z) ** 2)) + 1e-12)

    flux: list[float] = []
    positive_flux: list[float] = []
    for a, b in zip(spectra[:-1], spectra[1:]):
        n = min(len(a), len(b))
        d = b[:n] - a[:n]
        flux.append(float(np.sqrt(np.sum(d * d))))
        positive_flux.append(float(np.sum(np.maximum(d, 0.0))))

    loge = np.log(np.asarray(energies, dtype=float))
    energy_delta = np.diff(loge)
    onset_jump = float(loge[2] - loge[1])
    release_drop = float(loge[2] - loge[3])
    pre_flux = float(flux[1])
    post_flux = float(flux[2])

    return {
        "medianFlux": round(float(np.median(flux)), 6),
        "maxFlux": round(float(np.max(flux)), 6),
        "onsetFlux": round(pre_flux, 6),
        "releaseFlux": round(post_flux, 6),
        "medianPositiveFlux": round(float(np.median(positive_flux)), 6),
        "onsetEnergyJump": round(onset_jump, 6),
        "releaseEnergyDrop": round(release_drop, 6),
        "energyDeltaSpread": round(float(np.std(energy_delta)), 6),
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    med = max(w["medianFlux"], a["medianFlux"])
    peak = max(w["maxFlux"], a["maxFlux"])
    onset = max(w["onsetFlux"], a["onsetFlux"])
    release = max(w["releaseFlux"], a["releaseFlux"])
    pos = max(w["medianPositiveFlux"], a["medianPositiveFlux"])
    jump = max(w["onsetEnergyJump"], a["onsetEnergyJump"])
    drop = max(w["releaseEnergyDrop"], a["releaseEnergyDrop"])
    spread = max(w["energyDeltaSpread"], a["energyDeltaSpread"])
    stem_diff = abs(w["onsetFlux"] - a["onsetFlux"])

    mf = bucket(med, [0.08, 0.14, 0.22, 0.34], ["mf_lt080", "mf_080_140", "mf_140_220", "mf_220_340", "mf_340_plus"])
    pf = bucket(peak, [0.10, 0.18, 0.28, 0.42], ["pf_lt100", "pf_100_180", "pf_180_280", "pf_280_420", "pf_420_plus"])
    of = bucket(onset, [0.08, 0.14, 0.22, 0.34], ["of_lt080", "of_080_140", "of_140_220", "of_220_340", "of_340_plus"])
    rf = bucket(release, [0.08, 0.14, 0.22, 0.34], ["rf_lt080", "rf_080_140", "rf_140_220", "rf_220_340", "rf_340_plus"])
    xp = bucket(pos, [0.12, 0.20, 0.30, 0.45], ["xp_lt120", "xp_120_200", "xp_200_300", "xp_300_450", "xp_450_plus"])
    ej = bucket(jump, [-0.25, 0.0, 0.25, 0.60], ["ej_lt_n250", "ej_n250_000", "ej_000_250", "ej_250_600", "ej_600_plus"])
    rd = bucket(drop, [-0.25, 0.0, 0.25, 0.60], ["rd_lt_n250", "rd_n250_000", "rd_000_250", "rd_250_600", "rd_600_plus"])
    es = bucket(spread, [0.10, 0.20, 0.35, 0.60], ["es_lt100", "es_100_200", "es_200_350", "es_350_600", "es_600_plus"])
    sd = bucket(stem_diff, [0.03, 0.06, 0.12, 0.20], ["sd_lt030", "sd_030_060", "sd_060_120", "sd_120_200", "sd_200_plus"])

    agreement = "both_low" if max(w["onsetFlux"], a["onsetFlux"]) < 0.14 else (
        "one_low" if min(w["onsetFlux"], a["onsetFlux"]) < 0.14 else "neither_low"
    )
    return {
        f"medianSpectralFlux::{mf}", f"maxSpectralFlux::{pf}", f"onsetSpectralFlux::{of}",
        f"releaseSpectralFlux::{rf}", f"medianPositiveFlux::{xp}", f"onsetEnergyJump::{ej}",
        f"releaseEnergyDrop::{rd}", f"energyDeltaSpread::{es}", f"onsetFluxStemDifference::{sd}",
        f"dualStemFluxAgreement::{agreement}",
        f"spectralFluxCross::{mf}|{of}|{rf}|{agreement}",
        f"energyFluxCross::{ej}|{rd}|{es}|{of}",
        f"fluxComposite::{mf}|{pf}|{xp}|{sd}|{agreement}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows = []
    for signature, counts in groups.items():
        true, false = int(counts["true"]), int(counts["false"])
        total = true + false
        rows.append({"signature": signature, "true": true, "false": false, "total": total,
                     "precision": round(100.0 * true / total, 2) if total else 0.0})
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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
    champion, reconstruction = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched, extras = champion & reference, champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, _ = tok
        center = float(grid[(measure, step)])
        wf = stem_flux_features(winner_audio, winner_sr, center)
        af = stem_flux_features(alt_audio, alt_sr, center)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "winner": wf, "alternate": af, "signatures": signatures})

    for tok, count in matched.items(): record(tok, int(count), "true")
    for tok, count in extras.items(): record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 31.61 spectral-flux profiler")

    output = {"schemaVersion": 1, "passed": True, "profileType": "validated-31.61-spectral-flux-survivors",
              "champion3161Score": score, "reconstruction": reconstruction,
              "featureFamily": "dual-stem-spectral-flux-energy-change",
              "zeroPrecisionGeneralizableSignaturesMin5False": zero,
              "supportedTrueSignaturesMin5True": supported, "rows": details,
              "professionalReferenceUsedDuringDetection": False,
              "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
              "protected949CandidateHashUnchanged": True, "candidateEventsModified": False,
              "v7EventsModified": False, "rendererModified": False, "protectedBaselinesChanged": False,
              "productionSeparatorChanged": False, "productionPromotionAllowed": False}
    manifest = {"schemaVersion": 1, "passed": True, "output": str(OUTPUT_PATH.relative_to(ROOT)),
                "candidateSha256": after, "championPitchF1": score["pitchF1"], "matched": score["matched"],
                "missing": score["missing"], "extra": score["extra"], "zeroPrecisionSignatureCount": len(zero),
                "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 SPECTRAL FLUX SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision spectral-flux signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]: print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true spectral-flux signatures:")
    for row in supported[:30]: print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
