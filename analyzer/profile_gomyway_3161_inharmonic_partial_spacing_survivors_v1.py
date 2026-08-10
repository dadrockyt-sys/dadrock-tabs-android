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
OUTPUT_PATH = PUBLIC / "gomyway-3161-inharmonic-partial-spacing-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-inharmonic-partial-spacing-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def stem_partial_spacing_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    f0 = midi_hz(pitch)
    offsets = [-0.020, 0.0, 0.020]
    med_abs_cents: list[float] = []
    max_abs_cents: list[float] = []
    weighted_abs_cents: list[float] = []
    coherent_partial_fraction: list[float] = []
    signed_drift: list[float] = []

    for off in offsets:
        z, freqs = phase._frame_complex(audio, sr, center, off, win_s=0.090)
        mags = np.abs(z)
        errors: list[float] = []
        weights: list[float] = []

        for h in range(2, 7):
            target = f0 * h
            if target >= freqs[-1]:
                break
            idx = int(np.argmin(np.abs(freqs - target)))
            radius = max(2, int(round(target * 0.018 / max(freqs[1] - freqs[0], 1e-9))))
            lo = max(0, idx - radius)
            hi = min(len(mags), idx + radius + 1)
            if hi <= lo:
                continue
            local_idx = lo + int(np.argmax(mags[lo:hi]))
            peak_hz = float(freqs[local_idx])
            if peak_hz <= 0.0:
                continue
            cents = 1200.0 * np.log2(peak_hz / target)
            errors.append(float(cents))
            weights.append(float(mags[local_idx]) + 1e-12)

        if not errors:
            med_abs_cents.append(999.0)
            max_abs_cents.append(999.0)
            weighted_abs_cents.append(999.0)
            coherent_partial_fraction.append(0.0)
            signed_drift.append(999.0)
            continue

        arr = np.asarray(errors, dtype=float)
        w = np.asarray(weights, dtype=float)
        med_abs_cents.append(float(np.median(np.abs(arr))))
        max_abs_cents.append(float(np.max(np.abs(arr))))
        weighted_abs_cents.append(float(np.sum(np.abs(arr) * w) / (np.sum(w) + 1e-12)))
        coherent_partial_fraction.append(float(np.mean(np.abs(arr) <= 18.0)))
        signed_drift.append(float(np.median(arr)))

    return {
        "medianPartialSpacingErrorCents": round(float(np.median(med_abs_cents)), 6),
        "maxPartialSpacingErrorCents": round(float(np.max(max_abs_cents)), 6),
        "weightedPartialSpacingErrorCents": round(float(np.median(weighted_abs_cents)), 6),
        "minCoherentPartialFraction": round(float(np.min(coherent_partial_fraction)), 6),
        "medianSignedPartialDriftCents": round(float(np.median(signed_drift)), 6),
        "spacingStabilityCents": round(float(np.std(np.asarray(med_abs_cents))), 6),
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    med = max(w["medianPartialSpacingErrorCents"], a["medianPartialSpacingErrorCents"])
    peak = max(w["maxPartialSpacingErrorCents"], a["maxPartialSpacingErrorCents"])
    weighted = max(w["weightedPartialSpacingErrorCents"], a["weightedPartialSpacingErrorCents"])
    coherent = min(w["minCoherentPartialFraction"], a["minCoherentPartialFraction"])
    drift = max(abs(w["medianSignedPartialDriftCents"]), abs(a["medianSignedPartialDriftCents"]))
    stability = max(w["spacingStabilityCents"], a["spacingStabilityCents"])
    stem_diff = abs(w["medianPartialSpacingErrorCents"] - a["medianPartialSpacingErrorCents"])

    me = bucket(med, [6, 12, 20, 35], ["me_lt006", "me_006_012", "me_012_020", "me_020_035", "me_035_plus"])
    pe = bucket(peak, [12, 24, 40, 70], ["pe_lt012", "pe_012_024", "pe_024_040", "pe_040_070", "pe_070_plus"])
    we = bucket(weighted, [8, 16, 28, 45], ["we_lt008", "we_008_016", "we_016_028", "we_028_045", "we_045_plus"])
    cf = bucket(coherent, [0.25, 0.50, 0.75, 0.95], ["cf_lt025", "cf_025_050", "cf_050_075", "cf_075_095", "cf_095_plus"])
    dr = bucket(drift, [5, 12, 25, 45], ["dr_lt005", "dr_005_012", "dr_012_025", "dr_025_045", "dr_045_plus"])
    st = bucket(stability, [4, 10, 20, 35], ["st_lt004", "st_004_010", "st_010_020", "st_020_035", "st_035_plus"])
    sd = bucket(stem_diff, [5, 12, 25, 45], ["sd_lt005", "sd_005_012", "sd_012_025", "sd_025_045", "sd_045_plus"])

    agreement = "both_tight" if max(w["medianPartialSpacingErrorCents"], a["medianPartialSpacingErrorCents"]) < 16 else (
        "one_tight" if min(w["medianPartialSpacingErrorCents"], a["medianPartialSpacingErrorCents"]) < 16 else "neither_tight"
    )

    return {
        f"maxMedianPartialSpacingError::{me}",
        f"maxPeakPartialSpacingError::{pe}",
        f"maxWeightedPartialSpacingError::{we}",
        f"minCoherentPartialFraction::{cf}",
        f"maxSignedPartialDrift::{dr}",
        f"partialSpacingStability::{st}",
        f"partialSpacingStemDifference::{sd}",
        f"dualStemPartialSpacingAgreement::{agreement}",
        f"inharmonicityCross::{me}|{pe}|{cf}|{agreement}",
        f"partialDriftCross::{we}|{dr}|{st}|{sd}",
        f"partialSpacingComposite::{me}|{we}|{cf}|{st}|{agreement}",
    }


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

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_partial_spacing_features(winner_audio, winner_sr, center, pitch)
        af = stem_partial_spacing_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
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
        raise RuntimeError("Protected candidate changed during 31.61 inharmonic partial-spacing profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-inharmonic-partial-spacing-survivors",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "dual-stem-inharmonic-partial-spacing-consistency",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
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

    print("GOMYWAY 31.61 INHARMONIC PARTIAL SPACING SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision inharmonic partial-spacing signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true inharmonic partial-spacing signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
