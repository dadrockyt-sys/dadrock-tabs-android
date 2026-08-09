from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2409_dual_stem_harmonic_band_concentration_v1 as band
import profile_gomyway_2409_transient_onset_survivors_precision_v1 as p2409

recur = band.recur
recall = band.recall
v2 = band.v2
v3 = band.v3
harmonic = band.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_2409_PATH = PUBLIC / "gomyway-2409-dual-stem-harmonic-band-concentration-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2476-harmonic-band-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2476-harmonic-band-survivors-precision-v1-manifest.json"
EXPECTED = (183, 684, 428)
EXPECTED_F1 = 24.76
EXPECTED_PRUNED = 41
EXPECTED_ZERO_SIGNATURES = 7


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


def feature_row(
    tok: tuple[int, int, int],
    count: int,
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr,
    alt_audio,
    alt_sr,
    truth: str,
) -> dict[str, Any]:
    measure, step, pitch = tok
    center = float(grid[(measure, step)])
    wf = band.stem_features(winner_audio, winner_sr, center, pitch)
    af = band.stem_features(alt_audio, alt_sr, center, pitch)
    signatures = sorted(band.signatures_for(wf, af))
    return {
        "token": list(tok),
        "truth": truth,
        "count": int(count),
        "winner": wf,
        "alternate": af,
        "minHarmonicConcentration": min(wf["harmonicConcentration"], af["harmonicConcentration"]),
        "maxShoulderToCore": max(wf["shoulderToCore"], af["shoulderToCore"]),
        "maxInterharmonicToCore": max(wf["interharmonicToCore"], af["interharmonicToCore"]),
        "maxMeanRelativeBandwidth": max(wf["meanRelativeBandwidth"], af["meanRelativeBandwidth"]),
        "signatures": signatures,
    }


def reconstruct_2476(grid, winner_audio, winner_sr, alt_audio, alt_sr):
    profile = v2.load_json(PROFILE_2409_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("24.09 harmonic-band profile is not reference-free during detection")

    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} validated harmonic-band signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid validated harmonic-band signature row: {row}")
    validated = {str(r["signature"]) for r in zero_rows}

    champion = p2409.reconstruct_2409(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion.items():
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = band.stem_features(winner_audio, winner_sr, center, pitch)
        af = band.stem_features(alt_audio, alt_sr, center, pitch)
        if band.signatures_for(wf, af) & validated:
            pruned[tok] = count

    if int(sum(pruned.values())) != EXPECTED_PRUNED:
        raise RuntimeError(
            f"Expected exact validated harmonic-band prune count {EXPECTED_PRUNED}, got {int(sum(pruned.values()))}"
        )
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

    champion = reconstruct_2476(grid, winner_audio, winner_sr, alt_audio, alt_sr)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 24.76 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

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
        raise RuntimeError("Protected candidate changed during 24.76 harmonic-band survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-24.76-harmonic-band-survivor-precision",
        "champion2476Score": score,
        "featureFamily": "dual-stem-harmonic-band-concentration-survivors",
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

    print("GOMYWAY 24.76 HARMONIC-BAND SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision harmonic-band survivor signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true harmonic-band survivor signatures (5+ true):")
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
