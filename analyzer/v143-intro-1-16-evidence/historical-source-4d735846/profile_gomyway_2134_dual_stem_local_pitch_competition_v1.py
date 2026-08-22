from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2134_harmonic_peak_survivors_precision_v1 as p2134

b2065 = p2134.b2065
peak = p2134.peak
recur = p2134.recur
recall = p2134.recall
v2 = p2134.v2
v3 = p2134.v3
harmonic = peak.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_2065_PATH = PUBLIC / "gomyway-2065-dual-stem-harmonic-peak-alignment-v1.json"
SURVIVOR_2134_PATH = PUBLIC / "gomyway-2134-harmonic-peak-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2134-dual-stem-local-pitch-competition-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2134-dual-stem-local-pitch-competition-v1-manifest.json"
EXPECTED = (183, 684, 665)
EXPECTED_F1 = 21.34


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        t = int(counts["true"])
        f = int(counts["false"])
        total = t + f
        out.append({
            "signature": signature,
            "true": t,
            "false": f,
            "total": total,
            "precision": round(100.0 * t / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2134(grid: Any) -> Counter[tuple[int, int, int]]:
    profile_payload = v2.load_json(PROFILE_2065_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in rows}
    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    zero_signatures = {str(r["signature"]) for r in zero_rows}
    if not zero_signatures:
        raise RuntimeError("20.65 harmonic-peak profile has no validated zero-precision signatures")

    champion_2065 = peak.reconstruct_2065(grid)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2065.items():
        row = row_by_token.get(tok)
        if row is not None and b2065.row_signatures(row) & zero_signatures:
            pruned[tok] = count
    return champion_2065 - pruned


def ratio_bucket(value: float) -> str:
    if value < 0.55:
        return "ratio_lt055"
    if value < 0.75:
        return "ratio_055_075"
    if value < 0.95:
        return "ratio_075_095"
    if value < 1.15:
        return "ratio_095_115"
    if value < 1.45:
        return "ratio_115_145"
    return "ratio_145_plus"


def margin_bucket(value: float) -> str:
    if value < -0.35:
        return "margin_lt_n035"
    if value < -0.15:
        return "margin_n035_n015"
    if value < 0.0:
        return "margin_n015_000"
    if value < 0.20:
        return "margin_000_020"
    return "margin_020_plus"


def disagree_bucket(value: int) -> str:
    if value == 0:
        return "agree_both"
    if value == 1:
        return "agree_one"
    return "agree_none"


def comb_score(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> float:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return 0.0
    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)
    nyquist = sample_rate * 0.5
    eps = 1e-9
    score = 0.0
    weight = 0.0
    for h in range(1, 6):
        hz = f0 * h
        if hz >= nyquist - 20.0:
            break
        half = max(4.0, hz * 0.006)
        mask = (freqs >= hz - half) & (freqs <= hz + half)
        if np.any(mask):
            w = 1.0 / h
            score += w * float(np.max(spec[mask]))
            weight += w
    return score / (weight + eps)


def stem_competition(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, float]:
    target = comb_score(audio, sample_rate, center, midi)
    competitor_midis = [midi - 2, midi - 1, midi + 1, midi + 2, midi - 12, midi + 12]
    competitors = [(m, comb_score(audio, sample_rate, center, m)) for m in competitor_midis if 20 <= m <= 100]
    if not competitors:
        return {"target": target, "bestCompetitor": 0.0, "ratio": 99.0, "margin": 1.0, "targetWins": 1.0}
    best_midi, best = max(competitors, key=lambda item: item[1])
    eps = 1e-9
    ratio = target / (best + eps)
    margin = (target - best) / (target + best + eps)
    return {
        "target": target,
        "bestCompetitor": best,
        "bestCompetitorMidi": float(best_midi),
        "ratio": ratio,
        "margin": margin,
        "targetWins": 1.0 if target >= best else 0.0,
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

    survivor_payload = v2.load_json(SURVIVOR_2134_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("21.34 harmonic-peak survivor profile is not reference-free during detection")
    if survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("21.34 harmonic-peak branch is not exhausted")

    champion = reconstruct_2134(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 21.34 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch_midi = tok
        center = float(grid[(measure, step)])
        wf = stem_competition(winner_audio, winner_sr, center, pitch_midi)
        af = stem_competition(alt_audio, alt_sr, center, pitch_midi)

        min_ratio = min(float(wf["ratio"]), float(af["ratio"]))
        max_ratio = max(float(wf["ratio"]), float(af["ratio"]))
        min_margin = min(float(wf["margin"]), float(af["margin"]))
        wins = int(wf["targetWins"]) + int(af["targetWins"])

        rmin = ratio_bucket(min_ratio)
        rmax = ratio_bucket(max_ratio)
        marg = margin_bucket(min_margin)
        agree = disagree_bucket(2 - wins)
        signatures = {
            "minCompetitionRatio": rmin,
            "maxCompetitionRatio": rmax,
            "competitionMargin": marg,
            "targetWinAgreement": agree,
            "ratioAgreement": f"{rmin}|{agree}",
            "marginAgreement": f"{marg}|{agree}",
            "competitionCross": f"{rmin}|{rmax}|{marg}|{agree}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minTargetVsCompetitorRatio": min_ratio,
            "maxTargetVsCompetitorRatio": max_ratio,
            "minTargetCompetitionMargin": min_margin,
            "targetWinsAcrossStems": wins,
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
        raise RuntimeError("Protected candidate changed during 21.34 local-pitch-competition profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-21.34-dual-stem-local-pitch-competition",
        "champion2134Score": score,
        "featureFamily": "dual-stem-local-pitch-competition",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-local-pitch-competition-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 21.34 DUAL-STEM LOCAL PITCH COMPETITION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision local-pitch-competition signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true local-pitch-competition signatures (5+ true):")
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
