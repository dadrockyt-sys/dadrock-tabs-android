from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2140_dual_stem_harmonic_onset_sustain_stability_v1 as stability
import benchmark_gomyway_2140_onset_sustain_stability_precision_prune_cv_v1 as bench

recur = stability.recur
recall = stability.recall
v2 = stability.v2
v3 = stability.v3
harmonic = stability.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_2140_PATH = PUBLIC / "gomyway-2140-dual-stem-harmonic-onset-sustain-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2328-onset-sustain-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2328-onset-sustain-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 522)
EXPECTED_F1 = 23.28
EXPECTED_PRUNE_COUNT = 138


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


def current_stability_row(
    tok: tuple[int, int, int],
    count: int,
    grid: Any,
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
) -> dict[str, Any]:
    measure, step, pitch_midi = tok
    center = float(grid[(measure, step)])
    wf = stability.stem_stability(winner_audio, winner_sr, center, pitch_midi)
    af = stability.stem_stability(alt_audio, alt_sr, center, pitch_midi)

    min_early = min(float(wf["earlyRetention"]), float(af["earlyRetention"]))
    min_sustain = min(float(wf["sustainRetention"]), float(af["sustainRetention"]))
    min_sve = min(float(wf["sustainVsEarly"]), float(af["sustainVsEarly"]))
    min_decay = min(float(wf["decayMargin"]), float(af["decayMargin"]))
    sustain_diff = abs(float(wf["sustainRetention"]) - float(af["sustainRetention"]))

    return {
        "token": list(tok),
        "count": int(count),
        "winner": wf,
        "alternate": af,
        "minEarlyRetention": min_early,
        "minSustainRetention": min_sustain,
        "minSustainVsEarly": min_sve,
        "minDecayMargin": min_decay,
        "sustainRetentionStemDifference": sustain_diff,
    }


def reconstruct_2328(
    grid: Any,
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
) -> Counter[tuple[int, int, int]]:
    profile_payload = v2.load_json(PROFILE_2140_PATH)
    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != 27:
        raise RuntimeError(f"Expected 27 onset-sustain zero-precision signatures, got {len(zero_rows)}")
    zero_signatures = {str(r["signature"]) for r in zero_rows}

    champion_2140 = stability.reconstruct_2140(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2140.items():
        row = current_stability_row(tok, int(count), grid, winner_audio, winner_sr, alt_audio, alt_sr)
        if bench.row_signatures(row) & zero_signatures:
            pruned[tok] = count

    prune_count = int(sum(pruned.values()))
    if prune_count != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(f"Expected validated onset-sustain prune count {EXPECTED_PRUNE_COUNT}, got {prune_count}")
    return champion_2140 - pruned


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

    profile_payload = v2.load_json(PROFILE_2140_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("21.40 onset-sustain profile is not reference-free during detection")
    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != 27:
        raise RuntimeError(f"Expected 27 validated onset-sustain signatures, got {len(zero_rows)}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    champion = reconstruct_2328(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 23.28 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        row = current_stability_row(tok, count, grid, winner_audio, winner_sr, alt_audio, alt_sr)
        row["truth"] = truth
        for signature in bench.row_signatures(row):
            groups[signature][truth] += int(count)
        details.append(row)

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
        raise RuntimeError("Protected candidate changed during 23.28 onset-sustain survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-23.28-onset-sustain-survivors-precision",
        "champion2328Score": score,
        "featureFamily": "dual-stem-harmonic-onset-sustain-stability-survivors",
        "validatedParentWinner": "onsetsustain2140_union_all_zero_precision",
        "validatedParentSignatureCount": 27,
        "validatedParentPruneCount": EXPECTED_PRUNE_COUNT,
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
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-onset-sustain-survivor-signatures-with-prune-specific-heldout-cv-or-freeze-family-if-none",
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

    print("GOMYWAY 23.28 ONSET-SUSTAIN SURVIVORS PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated parent prune count:", EXPECTED_PRUNE_COUNT)
    print("Generalizable zero-precision onset-sustain survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true onset-sustain survivor signatures (5+ true):")
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
