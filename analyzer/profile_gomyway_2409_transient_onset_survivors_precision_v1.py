from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2328_dual_stem_transient_onset_morphology_v1 as transient
import profile_gomyway_2328_onset_sustain_survivors_precision_v1 as p2328

recur = transient.recur
recall = transient.recall
v2 = transient.v2
v3 = transient.v3
harmonic = transient.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_2328_PATH = PUBLIC / "gomyway-2328-dual-stem-transient-onset-morphology-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2409-transient-onset-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2409-transient-onset-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 469)
EXPECTED_F1 = 24.09
EXPECTED_PRUNED = 53


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


def signature_set_for_features(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    min_attack = min(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
    max_attack = max(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
    min_conc = min(float(wf["first20Concentration"]), float(af["first20Concentration"]))
    max_early = max(float(wf["earlyOnsetRatio"]), float(af["earlyOnsetRatio"]))
    min_flux = min(float(wf["spectralFlux"]), float(af["spectralFlux"]))
    max_latency = max(float(wf["peakLatencyMs"]), float(af["peakLatencyMs"]))
    min_crest = min(float(wf["crest"]), float(af["crest"]))
    attack_diff = abs(math.log2((float(wf["attackPreRatio"]) + 1e-6) / (float(af["attackPreRatio"]) + 1e-6)))

    a = transient.ratio_bucket(min_attack, "attack")
    ax = transient.ratio_bucket(max_attack, "maxattack")
    c = transient.ratio_bucket(min_conc, "conc")
    e = transient.ratio_bucket(max_early, "early")
    f = transient.flux_bucket(min_flux)
    l = transient.latency_bucket(max_latency)
    cr = transient.crest_bucket(min_crest)
    d = transient.diff_bucket(attack_diff)

    return {
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


def feature_row(tok: tuple[int, int, int], count: int, grid: dict[tuple[int, int], float], winner_audio, winner_sr, alt_audio, alt_sr, truth: str) -> dict[str, Any]:
    measure, step, pitch = tok
    center = float(grid[(measure, step)])
    wf = transient.transient_features(winner_audio, winner_sr, center)
    af = transient.transient_features(alt_audio, alt_sr, center)

    min_attack = min(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
    max_attack = max(float(wf["attackPreRatio"]), float(af["attackPreRatio"]))
    min_conc = min(float(wf["first20Concentration"]), float(af["first20Concentration"]))
    max_early = max(float(wf["earlyOnsetRatio"]), float(af["earlyOnsetRatio"]))
    min_flux = min(float(wf["spectralFlux"]), float(af["spectralFlux"]))
    max_latency = max(float(wf["peakLatencyMs"]), float(af["peakLatencyMs"]))
    min_crest = min(float(wf["crest"]), float(af["crest"]))
    attack_diff = abs(math.log2((float(wf["attackPreRatio"]) + 1e-6) / (float(af["attackPreRatio"]) + 1e-6)))

    return {
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
        "signatures": sorted(signature_set_for_features(wf, af)),
    }


def reconstruct_2409(grid, winner_audio, winner_sr, alt_audio, alt_sr):
    profile = v2.load_json(PROFILE_2328_PATH)
    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != 5:
        raise RuntimeError(f"Expected exactly 5 validated transient signatures, got {len(zero_rows)}")
    validated = {str(r["signature"]) for r in zero_rows}

    champion = p2328.reconstruct_2328(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion.items():
        measure, step, _pitch = tok
        center = float(grid[(measure, step)])
        wf = transient.transient_features(winner_audio, winner_sr, center)
        af = transient.transient_features(alt_audio, alt_sr, center)
        if signature_set_for_features(wf, af) & validated:
            pruned[tok] = count

    if int(sum(pruned.values())) != EXPECTED_PRUNED:
        raise RuntimeError(f"Expected exact validated transient prune count {EXPECTED_PRUNED}, got {int(sum(pruned.values()))}")
    return champion - pruned


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

    champion = reconstruct_2409(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 24.09 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok, count, truth):
        row = feature_row(tok, int(count), grid, winner_audio, winner_sr, alt_audio, alt_sr, truth)
        for signature in row["signatures"]:
            groups[signature][truth] += int(count)
        details.append(row)

    for tok, count in matched.items():
        record(tok, count, "true")
    for tok, count in extras.items():
        record(tok, count, "false")

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 24.09 transient-onset survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-24.09-transient-onset-survivor-precision",
        "champion2409Score": score,
        "featureFamily": "dual-stem-transient-onset-morphology-survivors",
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

    print("GOMYWAY 24.09 TRANSIENT-ONSET SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision transient-onset survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true transient-onset survivor signatures (5+ true):")
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
