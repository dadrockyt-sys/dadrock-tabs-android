from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

import profile_gomyway_1460_broad_champion_extras_cross_signatures_v1 as p1460
import benchmark_gomyway_1454_broad_score_agreement_precision_prune_cv_v1 as b1454
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy

recur = b1454.recur
recall = b1454.recall
v2 = b1454.v2
v3 = b1454.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1460-dual-stem-attack-envelope-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1460-dual-stem-attack-envelope-v1-manifest.json"
EXPECTED = (183, 684, 1456)
EXPECTED_F1 = 14.60


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    return audio, int(sample_rate)


def segment(audio: np.ndarray, sample_rate: int, center_seconds: float, start_ms: float, end_ms: float) -> np.ndarray:
    start = int(round((center_seconds + start_ms / 1000.0) * sample_rate))
    end = int(round((center_seconds + end_ms / 1000.0) * sample_rate))
    start = max(0, min(len(audio), start))
    end = max(start, min(len(audio), end))
    return audio[start:end]


def rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values, dtype=np.float64)) + 1e-12))


def crest(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    base = rms(values)
    return float(np.max(np.abs(values)) / (base + 1e-9))


def zcr_per_second(values: np.ndarray, sample_rate: int) -> float:
    if values.size < 2:
        return 0.0
    crossings = int(np.count_nonzero(np.signbit(values[1:]) != np.signbit(values[:-1])))
    return float(crossings * sample_rate / max(1, values.size - 1))


def ratio_bucket(value: float, prefix: str) -> str:
    if value < 0.80:
        return f"{prefix}_lt080"
    if value < 1.00:
        return f"{prefix}_080_100"
    if value < 1.25:
        return f"{prefix}_100_125"
    if value < 1.60:
        return f"{prefix}_125_160"
    if value < 2.20:
        return f"{prefix}_160_220"
    return f"{prefix}_220_plus"


def decay_bucket(value: float) -> str:
    if value < 0.45:
        return "decay_lt045"
    if value < 0.70:
        return "decay_045_070"
    if value < 0.95:
        return "decay_070_095"
    if value < 1.20:
        return "decay_095_120"
    return "decay_120_plus"


def crest_bucket(value: float) -> str:
    if value < 2.0:
        return "crest_lt2"
    if value < 3.0:
        return "crest_2_3"
    if value < 4.5:
        return "crest_3_4p5"
    return "crest_4p5_plus"


def zcr_bucket(value: float) -> str:
    if value < 800.0:
        return "zcr_lt800"
    if value < 1600.0:
        return "zcr_800_1600"
    if value < 3000.0:
        return "zcr_1600_3000"
    return "zcr_3000_plus"


def disagree_bucket(value: float) -> str:
    if value < 0.20:
        return "attack_disagree_lt020"
    if value < 0.50:
        return "attack_disagree_020_050"
    if value < 1.00:
        return "attack_disagree_050_100"
    return "attack_disagree_100_plus"


def stem_features(audio: np.ndarray, sample_rate: int, center_seconds: float) -> dict[str, float]:
    pre = segment(audio, sample_rate, center_seconds, -90.0, -20.0)
    attack = segment(audio, sample_rate, center_seconds, -5.0, 45.0)
    sustain = segment(audio, sample_rate, center_seconds, 45.0, 115.0)
    post = segment(audio, sample_rate, center_seconds, -5.0, 115.0)

    pre_rms = rms(pre)
    attack_rms = rms(attack)
    sustain_rms = rms(sustain)
    attack_ratio = attack_rms / (pre_rms + 1e-9)
    decay_ratio = sustain_rms / (attack_rms + 1e-9)
    return {
        "preRms": pre_rms,
        "attackRms": attack_rms,
        "sustainRms": sustain_rms,
        "attackRatio": attack_ratio,
        "decayRatio": decay_ratio,
        "crest": crest(post),
        "zcr": zcr_per_second(post, sample_rate),
    }


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
    return sorted(rows, key=lambda row: (-int(row["total"]), -float(row["precision"]), str(row["signature"])))


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

    champion_1454 = b1454.reconstruct_1454(grid)
    winner_scores = legacy.spectral.specialist_scores(legacy.WINNER_STEM, grid)
    alt_scores = legacy.spectral.specialist_scores(legacy.ALT_STEM, grid)

    def score_agreement(tok: tuple[int, int, int]) -> tuple[str, str]:
        return (
            legacy.pruning.score_bucket(tok, winner_scores, alt_scores),
            legacy.pruning.agreement_bucket(tok, winner_scores, alt_scores),
        )

    validated_union = {
        ("16_20", "both_ge8"),
        ("20_plus", "both_ge8"),
        ("20_plus", "single_stem_or_weak_second"),
    }
    fifth_pruned = Counter({tok: count for tok, count in champion_1454.items() if score_agreement(tok) in validated_union})
    champion = champion_1454 - fifth_pruned

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.60 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = load_mono(legacy.WINNER_STEM)
    alt_audio, alt_sr = load_mono(legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    rows: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = stem_features(winner_audio, winner_sr, center)
        af = stem_features(alt_audio, alt_sr, center)

        max_attack = max(wf["attackRatio"], af["attackRatio"])
        min_attack = min(wf["attackRatio"], af["attackRatio"])
        max_decay = max(wf["decayRatio"], af["decayRatio"])
        min_decay = min(wf["decayRatio"], af["decayRatio"])
        min_crest = min(wf["crest"], af["crest"])
        max_zcr = max(wf["zcr"], af["zcr"])
        attack_disagree = abs(math.log2((wf["attackRatio"] + 1e-6) / (af["attackRatio"] + 1e-6)))

        signatures = {
            "maxAttack": ratio_bucket(max_attack, "maxattack"),
            "minAttack": ratio_bucket(min_attack, "minattack"),
            "maxDecay": decay_bucket(max_decay),
            "minDecay": "min_" + decay_bucket(min_decay),
            "minCrest": "min_" + crest_bucket(min_crest),
            "maxZcr": "max_" + zcr_bucket(max_zcr),
            "attackDisagreement": disagree_bucket(attack_disagree),
        }
        combos = {
            "attackPair": f"{signatures['maxAttack']}|{signatures['minAttack']}",
            "attackDecay": f"{signatures['minAttack']}|{signatures['maxDecay']}",
            "attackCrest": f"{signatures['minAttack']}|{signatures['minCrest']}",
            "attackZcr": f"{signatures['minAttack']}|{signatures['maxZcr']}",
            "attackAgreement": f"{signatures['minAttack']}|{signatures['attackDisagreement']}",
            "decayCrest": f"{signatures['maxDecay']}|{signatures['minCrest']}",
        }

        score_bucket, agreement_bucket = score_agreement(tok)
        cross = {
            "attackScoreAgreement": f"{signatures['minAttack']}|score{score_bucket}|{agreement_bucket}",
            "decayScoreAgreement": f"{signatures['maxDecay']}|score{score_bucket}|{agreement_bucket}",
        }

        for name, signature in {**signatures, **combos, **cross}.items():
            groups[f"{name}::{signature}"][truth] += count

        rows.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "maxAttackRatio": max_attack,
            "minAttackRatio": min_attack,
            "maxDecayRatio": max_decay,
            "minDecayRatio": min_decay,
            "minCrest": min_crest,
            "maxZcr": max_zcr,
            "attackDisagreementOctaves": attack_disagree,
            "scoreBucket": score_bucket,
            "stemAgreement": agreement_bucket,
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
        raise RuntimeError("Protected candidate changed during 14.60 dual-stem attack-envelope profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.60-dual-stem-attack-envelope",
        "champion1460Score": score,
        "featureFamily": "dual-stem-waveform-attack-envelope",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
        "rows": rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-attack-envelope-signatures-with-prune-specific-heldout-cv",
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

    print("GOMYWAY 14.60 DUAL-STEM ATTACK ENVELOPE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision attack/envelope signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true attack/envelope signatures (5+ true):")
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
