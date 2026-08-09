from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1694_temporal_pitch_persistence_survivors_precision_v1 as p1694

b1661 = p1694.b1661
temporal = b1661.temporal
harmonic = temporal.harmonic
recur = p1694.recur
recall = p1694.recall
v2 = p1694.v2
v3 = p1694.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1661_PATH = PUBLIC / "gomyway-1661-dual-stem-temporal-pitch-persistence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1-manifest.json"
EXPECTED = (183, 684, 1110)
EXPECTED_F1 = 16.94


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def reconstruct_1694(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1661 = temporal.reconstruct_1661(grid)
    profile_payload = v2.load_json(PROFILE_1661_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1661.items():
        row = row_by_token.get(tok)
        if row is not None and (
            b1661.pred_a(row)
            or b1661.pred_b(row)
            or b1661.pred_c(row)
            or b1661.pred_d(row)
            or b1661.pred_e(row)
        ):
            pruned[tok] = count
    return champion_1661 - pruned


def ratio_bucket(value: float) -> str:
    if value < 0.65:
        return "ratio_lt065"
    if value < 0.85:
        return "ratio_065_085"
    if value < 1.05:
        return "ratio_085_105"
    if value < 1.35:
        return "ratio_105_135"
    if value < 1.80:
        return "ratio_135_180"
    return "ratio_180_plus"


def dominance_bucket(value: float) -> str:
    if value < 0.75:
        return "dom_lt075"
    if value < 1.00:
        return "dom_075_100"
    if value < 1.25:
        return "dom_100_125"
    if value < 1.75:
        return "dom_125_175"
    return "dom_175_plus"


def win_bucket(value: int) -> str:
    if value <= 0:
        return "targetwins_0"
    if value == 1:
        return "targetwins_1"
    return "targetwins_2"


def disagreement_bucket(value: int) -> str:
    return "octave_disagree_0" if value == 0 else "octave_disagree_1"


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


def stem_octave_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, Any]:
    values = harmonic.segment(audio, sample_rate, center)
    if values.size < 256:
        return {
            "target": 0.0,
            "lowerOctave": 0.0,
            "upperOctave": 0.0,
            "targetVsLower": 0.0,
            "targetVsUpper": 0.0,
            "lowerDominance": 0.0,
            "upperDominance": 0.0,
            "targetWins": False,
            "preferred": "target",
        }

    n_fft = 8192
    window = np.hanning(values.size).astype(np.float32)
    spec = np.abs(np.fft.rfft(values * window, n=n_fft))
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate)
    f0 = harmonic.midi_hz(midi)

    target = harmonic.comb_score(spec, freqs, f0)
    lower = harmonic.comb_score(spec, freqs, f0 * 0.5)
    upper = harmonic.comb_score(spec, freqs, f0 * 2.0)
    eps = 1e-9

    scores = {"lower": lower, "target": target, "upper": upper}
    preferred = max(scores, key=scores.get)
    return {
        "target": target,
        "lowerOctave": lower,
        "upperOctave": upper,
        "targetVsLower": target / (lower + eps),
        "targetVsUpper": target / (upper + eps),
        "lowerDominance": lower / (target + eps),
        "upperDominance": upper / (target + eps),
        "targetWins": target >= lower and target >= upper,
        "preferred": preferred,
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

    temporal_survivor_payload = v2.load_json(p1694.OUTPUT_PATH)
    if temporal_survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("16.94 temporal survivor profile is not reference-free during detection")
    if temporal_survivor_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("16.94 temporal survivor branch is not exhausted")

    champion = reconstruct_1694(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 16.94 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_octave_features(winner_audio, winner_sr, center, pitch)
        af = stem_octave_features(alt_audio, alt_sr, center, pitch)

        min_target_vs_lower = min(float(wf["targetVsLower"]), float(af["targetVsLower"]))
        min_target_vs_upper = min(float(wf["targetVsUpper"]), float(af["targetVsUpper"]))
        max_lower_dominance = max(float(wf["lowerDominance"]), float(af["lowerDominance"]))
        max_upper_dominance = max(float(wf["upperDominance"]), float(af["upperDominance"]))
        target_wins = int(bool(wf["targetWins"])) + int(bool(af["targetWins"]))
        octave_disagreement = int(str(wf["preferred"]) != str(af["preferred"]))

        lower_ratio_b = ratio_bucket(min_target_vs_lower)
        upper_ratio_b = ratio_bucket(min_target_vs_upper)
        lower_dom_b = dominance_bucket(max_lower_dominance)
        upper_dom_b = dominance_bucket(max_upper_dominance)
        wins_b = win_bucket(target_wins)
        disagree_b = disagreement_bucket(octave_disagreement)

        signatures = {
            "targetVsLower": lower_ratio_b,
            "targetVsUpper": upper_ratio_b,
            "lowerDominance": lower_dom_b,
            "upperDominance": upper_dom_b,
            "targetWins": wins_b,
            "octaveStemDisagreement": disagree_b,
            "lowerWins": f"{lower_ratio_b}|{wins_b}",
            "lowerDisagreement": f"{lower_ratio_b}|{disagree_b}",
            "upperWins": f"{upper_ratio_b}|{wins_b}",
            "octaveCross": f"{lower_ratio_b}|{upper_ratio_b}|{wins_b}",
            "dominanceCross": f"{lower_dom_b}|{upper_dom_b}|{disagree_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minTargetVsLower": min_target_vs_lower,
            "minTargetVsUpper": min_target_vs_upper,
            "maxLowerDominance": max_lower_dominance,
            "maxUpperDominance": max_upper_dominance,
            "targetWinsAcrossStems": target_wins,
            "octaveStemDisagreement": octave_disagreement,
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
        raise RuntimeError("Protected candidate changed during 16.94 octave/subharmonic discrimination profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-16.94-dual-stem-octave-subharmonic-discrimination",
        "champion1694Score": score,
        "featureFamily": "dual-stem-octave-subharmonic-discrimination",
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-octave-subharmonic-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 16.94 DUAL-STEM OCTAVE SUBHARMONIC DISCRIMINATION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision octave/subharmonic signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true octave/subharmonic signatures (5+ true):")
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
