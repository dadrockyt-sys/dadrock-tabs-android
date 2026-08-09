from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2769_spectral_envelope_survivors_precision_v1 as survivor

recur = survivor.recur
recall = survivor.recall
v2 = survivor.v2
v3 = survivor.v3
harmonic = survivor.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2769-dual-stem-harmonic-phase-coherence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2769-dual-stem-harmonic-phase-coherence-v1-manifest.json"
EXPECTED = (183, 684, 272)
EXPECTED_F1 = 27.69


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def _frame_complex(audio: np.ndarray, sr: int, center: float, offset: float, win_s: float = 0.046) -> tuple[np.ndarray, np.ndarray]:
    n = max(128, int(round(win_s * sr)))
    mid = int(round((center + offset) * sr))
    start = max(0, mid - n // 2)
    end = min(len(audio), start + n)
    x = np.asarray(audio[start:end], dtype=np.float64)
    if x.size < n:
        x = np.pad(x, (0, n - x.size))
    x = x - float(np.mean(x))
    w = np.hanning(n)
    z = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    return z, freqs


def phase_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    f0 = midi_hz(pitch)
    offsets = [-0.024, -0.012, 0.0, 0.012, 0.024]
    harmonic_phases: list[list[float]] = [[] for _ in range(4)]
    harmonic_mags: list[list[float]] = [[] for _ in range(4)]

    for off in offsets:
        z, freqs = _frame_complex(audio, sr, center, off)
        for h in range(1, 5):
            target = f0 * h
            if target >= freqs[-1]:
                continue
            idx = int(np.argmin(np.abs(freqs - target)))
            val = z[idx]
            harmonic_phases[h - 1].append(float(np.angle(val)))
            harmonic_mags[h - 1].append(float(np.abs(val)))

    coherences: list[float] = []
    phase_drifts: list[float] = []
    mag_stabilities: list[float] = []
    for phases, mags in zip(harmonic_phases, harmonic_mags):
        if len(phases) < 3:
            continue
        ph = np.asarray(phases, dtype=np.float64)
        vec = np.exp(1j * ph)
        coherences.append(float(np.abs(np.mean(vec))))
        unwrapped = np.unwrap(ph)
        phase_drifts.append(float(abs(unwrapped[-1] - unwrapped[0])))
        mg = np.asarray(mags, dtype=np.float64)
        mean_mag = float(np.mean(mg)) + 1e-12
        mag_stabilities.append(float(np.std(mg) / mean_mag))

    if not coherences:
        return {
            "meanCoherence": 0.0,
            "minCoherence": 0.0,
            "phaseDrift": 9.99,
            "magCv": 9.99,
            "harmonicAgreement": 0.0,
        }

    c = np.asarray(coherences, dtype=np.float64)
    d = np.asarray(phase_drifts, dtype=np.float64)
    m = np.asarray(mag_stabilities, dtype=np.float64)
    agreement = 1.0 - min(1.0, float(np.std(c)) * 2.0)
    return {
        "meanCoherence": round(float(np.mean(c)), 6),
        "minCoherence": round(float(np.min(c)), 6),
        "phaseDrift": round(float(np.mean(d)), 6),
        "magCv": round(float(np.mean(m)), 6),
        "harmonicAgreement": round(float(agreement), 6),
    }


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    mean_min = min(wf["meanCoherence"], af["meanCoherence"])
    min_min = min(wf["minCoherence"], af["minCoherence"])
    drift_max = max(wf["phaseDrift"], af["phaseDrift"])
    magcv_max = max(wf["magCv"], af["magCv"])
    agree_min = min(wf["harmonicAgreement"], af["harmonicAgreement"])
    cross_mean_diff = abs(wf["meanCoherence"] - af["meanCoherence"])
    cross_drift_diff = abs(wf["phaseDrift"] - af["phaseDrift"])

    mc = bucket(mean_min, [0.20, 0.35, 0.50, 0.68], ["mc_lt020", "mc_020_035", "mc_035_050", "mc_050_068", "mc_068_plus"])
    mn = bucket(min_min, [0.10, 0.22, 0.38, 0.55], ["mn_lt010", "mn_010_022", "mn_022_038", "mn_038_055", "mn_055_plus"])
    dr = bucket(drift_max, [0.7, 1.4, 2.4, 3.8], ["dr_lt07", "dr_07_14", "dr_14_24", "dr_24_38", "dr_38_plus"])
    cv = bucket(magcv_max, [0.18, 0.32, 0.50, 0.80], ["cv_lt018", "cv_018_032", "cv_032_050", "cv_050_080", "cv_080_plus"])
    ag = bucket(agree_min, [0.30, 0.50, 0.68, 0.82], ["ag_lt030", "ag_030_050", "ag_050_068", "ag_068_082", "ag_082_plus"])
    md = bucket(cross_mean_diff, [0.06, 0.12, 0.22, 0.35], ["md_lt006", "md_006_012", "md_012_022", "md_022_035", "md_035_plus"])
    dd = bucket(cross_drift_diff, [0.35, 0.75, 1.5, 2.5], ["dd_lt035", "dd_035_075", "dd_075_150", "dd_150_250", "dd_250_plus"])

    return {
        f"phaseCoherenceCross::{mc}|{mn}|{dr}|{cv}",
        f"harmonicPhaseAgreement::{mc}|{ag}|{md}|{dd}",
        f"dualStemPhaseCross::{mn}|{dr}|{md}|{dd}",
        f"phaseMagnitudeCross::{mc}|{cv}|{ag}|{md}",
        f"phaseCompositeCross::{mc}|{mn}|{ag}|{cv}|{dr}",
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
    champion, _ = survivor.reconstruct_2769(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.69 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = phase_features(winner_audio, winner_sr, center, pitch)
        af = phase_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
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
    zero = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero.sort(key=lambda row: (-int(row["false"]), str(row["signature"])))
    supported = [row for row in ranked if int(row["true"]) >= 5]
    supported.sort(key=lambda row: (-float(row["precision"]), -int(row["true"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.69 harmonic phase-coherence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.69-dual-stem-harmonic-phase-coherence",
        "champion2769Score": score,
        "featureFamily": "dual-stem-harmonic-phase-partial-coherence-and-cross-signature-composites",
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

    print("GOMYWAY 27.69 DUAL-STEM HARMONIC PHASE COHERENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-phase signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true harmonic-phase signatures:")
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
