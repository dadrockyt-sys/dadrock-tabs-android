from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2328_onset_sustain_survivors_precision_v1 as p2328
import profile_gomyway_1460_dual_stem_attack_envelope_v1 as attack

recur = p2328.recur
recall = p2328.recall
v2 = p2328.v2
v3 = p2328.v3
harmonic = p2328.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ONSET_SURVIVOR_PATH = PUBLIC / "gomyway-2328-onset-sustain-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2328-dual-stem-transient-onset-morphology-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2328-dual-stem-transient-onset-morphology-v1-manifest.json"
EXPECTED = (183, 684, 522)
EXPECTED_F1 = 23.28


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


def spectral_flux(pre: np.ndarray, onset: np.ndarray) -> float:
    if pre.size < 64 or onset.size < 64:
        return 0.0
    n_fft = 2048
    a = np.abs(np.fft.rfft(pre * np.hanning(pre.size), n=n_fft))
    b = np.abs(np.fft.rfft(onset * np.hanning(onset.size), n=n_fft))
    a = a / (float(np.linalg.norm(a)) + 1e-9)
    b = b / (float(np.linalg.norm(b)) + 1e-9)
    return float(np.sqrt(np.mean(np.square(b - a))))


def transient_features(audio: np.ndarray, sample_rate: int, center: float) -> dict[str, float]:
    pre = attack.segment(audio, sample_rate, center, -80.0, -20.0)
    onset = attack.segment(audio, sample_rate, center, -10.0, 50.0)
    early = attack.segment(audio, sample_rate, center, 50.0, 110.0)
    first20 = attack.segment(audio, sample_rate, center, -5.0, 15.0)

    pre_rms = attack.rms(pre)
    onset_rms = attack.rms(onset)
    early_rms = attack.rms(early)
    first20_rms = attack.rms(first20)

    peak_latency_ms = 60.0
    if onset.size:
        peak_index = int(np.argmax(np.abs(onset)))
        peak_latency_ms = 1000.0 * peak_index / max(1, sample_rate)

    return {
        "preRms": pre_rms,
        "onsetRms": onset_rms,
        "earlyRms": early_rms,
        "attackPreRatio": onset_rms / (pre_rms + 1e-9),
        "earlyOnsetRatio": early_rms / (onset_rms + 1e-9),
        "first20Concentration": first20_rms / (onset_rms + 1e-9),
        "peakLatencyMs": peak_latency_ms,
        "crest": attack.crest(onset),
        "spectralFlux": spectral_flux(pre, onset),
    }


def ratio_bucket(value: float, prefix: str) -> str:
    if value < 0.75:
        return f"{prefix}_lt075"
    if value < 1.00:
        return f"{prefix}_075_100"
    if value < 1.35:
        return f"{prefix}_100_135"
    if value < 1.80:
        return f"{prefix}_135_180"
    if value < 2.50:
        return f"{prefix}_180_250"
    return f"{prefix}_250_plus"


def latency_bucket(value: float) -> str:
    if value < 8.0:
        return "lat_lt8"
    if value < 18.0:
        return "lat_8_18"
    if value < 32.0:
        return "lat_18_32"
    if value < 48.0:
        return "lat_32_48"
    return "lat_48_plus"


def flux_bucket(value: float) -> str:
    if value < 0.010:
        return "flux_lt010"
    if value < 0.020:
        return "flux_010_020"
    if value < 0.035:
        return "flux_020_035"
    if value < 0.055:
        return "flux_035_055"
    return "flux_055_plus"


def crest_bucket(value: float) -> str:
    if value < 2.0:
        return "crest_lt2"
    if value < 3.0:
        return "crest_2_3"
    if value < 4.5:
        return "crest_3_4p5"
    return "crest_4p5_plus"


def diff_bucket(value: float) -> str:
    if value < 0.20:
        return "diff_lt020"
    if value < 0.50:
        return "diff_020_050"
    if value < 1.00:
        return "diff_050_100"
    return "diff_100_plus"


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

    survivor_payload = v2.load_json(ONSET_SURVIVOR_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("23.28 onset-sustain survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("23.28 onset-sustain family is not exhausted")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    champion = p2328.reconstruct_2328(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 23.28 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = transient_features(winner_audio, winner_sr, center)
        af = transient_features(alt_audio, alt_sr, center)

        min_attack = min(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
        max_attack = max(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
        min_conc = min(float(wf["first20Concentration"]), float(af["first20Concentration"]))
        max_early = max(float(wf["earlyOnsetRatio"]), float(af["earlyOnsetRatio"]))
        min_flux = min(float(wf["spectralFlux"]), float(af["spectralFlux"]))
        max_latency = max(float(wf["peakLatencyMs"]), float(af["peakLatencyMs"]))
        min_crest = min(float(wf["crest"]), float(af["crest"]))
        attack_diff = abs(math.log2((float(wf["attackPreRatio"]) + 1e-6) / (float(af["attackPreRatio"]) + 1e-6)))

        a = ratio_bucket(min_attack, "attack")
        ax = ratio_bucket(max_attack, "maxattack")
        c = ratio_bucket(min_conc, "conc")
        e = ratio_bucket(max_early, "early")
        f = flux_bucket(min_flux)
        l = latency_bucket(max_latency)
        cr = crest_bucket(min_crest)
        d = diff_bucket(attack_diff)

        signatures = {
            f"minAttack::{a}",
            f"maxAttack::{ax}",
            f"attackConcentration::{c}",
            f"earlyDecay::{e}",
            f"spectralFlux::{f}",
            f"peakLatency::{l}",
            f"onsetCrest::{cr}",
            f"stemAttackDiff::{d}",
            f"attackFluxCross::{a}|{f}|{d}",
            f"attackLatencyCross::{a}|{l}|{d}",
            f"concentrationFluxCross::{c}|{f}|{d}",
            f"transientShapeCross::{a}|{c}|{e}|{l}|{d}",
        }
        for signature in signatures:
            groups[signature][truth] += int(count)

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "minAttackPreRatio": min_attack,
            "maxAttackPreRatio": max_attack,
            "minFirst20Concentration": min_conc,
            "maxEarlyOnsetRatio": max_early,
            "minSpectralFlux": min_flux,
            "maxPeakLatencyMs": max_latency,
            "minOnsetCrest": min_crest,
            "stemAttackDifferenceOctaves": attack_diff,
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
        raise RuntimeError("Protected candidate changed during 23.28 transient onset morphology profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-23.28-dual-stem-transient-onset-morphology",
        "champion2328Score": score,
        "featureFamily": "dual-stem-transient-onset-morphology",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-transient-onset-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 23.28 DUAL-STEM TRANSIENT ONSET MORPHOLOGY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision transient-onset signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true transient-onset signatures (5+ true):")
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
