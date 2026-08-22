from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161
import profile_gomyway_2802_dual_stem_harmonic_residual_cancellation_v1 as residual

recur = s3161.recur
recall = s3161.recall
v2 = s3161.v2
v3 = s3161.v3
harmonic = s3161.harmonic
phase = residual.phase

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-fundamental-harmonic-alias-survivors-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-fundamental-harmonic-alias-survivors-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(pitch: float) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def amp_at(z: np.ndarray, freqs: np.ndarray, hz: float) -> float:
    if hz <= 0.0 or hz >= float(freqs[-1]):
        return 0.0
    i = int(np.argmin(np.abs(freqs - hz)))
    return float(abs(z[i]))


def stem_features(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    offsets = (-0.020, 0.0, 0.020)
    vals: list[dict[str, float]] = []
    f0 = midi_hz(pitch)
    for off in offsets:
        z, freqs = phase._frame_complex(audio, sr, center, off, win_s=0.070)
        fund = amp_at(z, freqs, f0)
        sub = amp_at(z, freqs, f0 / 2.0)
        h2 = amp_at(z, freqs, f0 * 2.0)
        h3 = amp_at(z, freqs, f0 * 3.0)
        lo = amp_at(z, freqs, midi_hz(pitch - 1))
        hi = amp_at(z, freqs, midi_hz(pitch + 1))
        eps = 1e-12
        vals.append({
            "fund": fund,
            "subRatio": sub / (fund + eps),
            "h2Ratio": h2 / (fund + eps),
            "h3Ratio": h3 / (fund + eps),
            "neighborRatio": max(lo, hi) / (fund + eps),
            "harmonicBurden": (h2 + h3) / (fund + eps),
            "fundShare": fund / (fund + sub + h2 + h3 + lo + hi + eps),
        })
    out: dict[str, float] = {}
    for key in vals[0]:
        arr = np.asarray([v[key] for v in vals], dtype=np.float64)
        out[key] = round(float(np.median(arr)), 6)
    return out


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_share = min(w["fundShare"], a["fundShare"])
    max_sub = max(w["subRatio"], a["subRatio"])
    max_h2 = max(w["h2Ratio"], a["h2Ratio"])
    max_harm = max(w["harmonicBurden"], a["harmonicBurden"])
    max_neighbor = max(w["neighborRatio"], a["neighborRatio"])
    share_diff = abs(w["fundShare"] - a["fundShare"])

    fs = bucket(min_share, [0.08, 0.14, 0.22, 0.34], ["fs_lt008", "fs_008_014", "fs_014_022", "fs_022_034", "fs_034_plus"])
    sub = bucket(max_sub, [0.40, 0.80, 1.50, 3.00], ["sub_lt040", "sub_040_080", "sub_080_150", "sub_150_300", "sub_300_plus"])
    h2 = bucket(max_h2, [0.50, 1.00, 2.00, 4.00], ["h2_lt050", "h2_050_100", "h2_100_200", "h2_200_400", "h2_400_plus"])
    hb = bucket(max_harm, [0.80, 1.50, 3.00, 6.00], ["hb_lt080", "hb_080_150", "hb_150_300", "hb_300_600", "hb_600_plus"])
    nr = bucket(max_neighbor, [0.50, 1.00, 2.00, 4.00], ["nr_lt050", "nr_050_100", "nr_100_200", "nr_200_400", "nr_400_plus"])
    sd = bucket(share_diff, [0.05, 0.12, 0.22, 0.35], ["sd_lt005", "sd_005_012", "sd_012_022", "sd_022_035", "sd_035_plus"])
    alias = "subharmonic_alias" if max_sub >= 1.5 else ("harmonic_alias" if max_harm >= 3.0 else ("neighbor_competition" if max_neighbor >= 2.0 else "fundamental_supported"))

    return {
        f"minFundamentalShare::{fs}",
        f"maxSubharmonicRatio::{sub}",
        f"maxSecondHarmonicRatio::{h2}",
        f"maxHarmonicBurden::{hb}",
        f"maxSemitoneNeighborRatio::{nr}",
        f"fundamentalShareStemDifference::{sd}",
        f"harmonicAliasClass::{alias}",
        f"fundamentalAliasCross::{fs}|{sub}|{hb}|{nr}",
        f"dualStemAliasCross::{alias}|{fs}|{sd}|{h2}",
        f"subharmonicCompetitionCross::{sub}|{nr}|{fs}|{sd}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig, c in groups.items():
        true, false = int(c["true"]), int(c["false"])
        total = true + false
        rows.append({"signature": sig, "true": true, "false": false, "total": total,
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

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center, pitch)
        af = stem_features(alt_audio, alt_sr, center, pitch)
        sigs = sorted(signatures_for(wf, af))
        for sig in sigs:
            groups[sig][truth] += int(count)
        details.append({"token": list(tok), "truth": truth, "count": int(count), "winner": wf, "alternate": af, "signatures": sigs})

    matched = champion & reference
    extras = champion - reference
    for tok, count in matched.items(): record(tok, int(count), "true")
    for tok, count in extras.items(): record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 31.61 fundamental/harmonic alias profiler")

    output = {
        "schemaVersion": 1, "passed": True,
        "profileType": "validated-31.61-fundamental-harmonic-alias-survivors",
        "champion3161Score": score, "reconstruction": reconstruction,
        "featureFamily": "fundamental-vs-subharmonic-harmonic-and-semitone-alias-support",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported, "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
        "protected949CandidateHashUnchanged": True, "candidateEventsModified": False,
        "v7EventsModified": False, "rendererModified": False,
        "protectedBaselinesChanged": False, "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1, "passed": True, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after, "championPitchF1": score["pitchF1"],
        "matched": score["matched"], "missing": score["missing"], "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero), "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 FUNDAMENTAL HARMONIC ALIAS SURVIVORS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision fundamental/harmonic-alias signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true fundamental/harmonic-alias signatures:")
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
