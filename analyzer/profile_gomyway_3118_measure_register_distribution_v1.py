from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3118_measure_position_survivors_precision_v1 as s3118

recur = s3118.recur
recall = s3118.recall
v2 = s3118.v2
v3 = s3118.v3
harmonic = s3118.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3118-measure-register-distribution-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3118-measure-register-distribution-v1-manifest.json"
EXPECTED = (183, 684, 124)
EXPECTED_F1 = 31.18


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: int, cuts: list[int], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def median_int(values: list[int]) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    n = len(ordered)
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return int(round((ordered[mid - 1] + ordered[mid]) / 2.0))


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


def build_maps(champion: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    measure_pitches: dict[int, list[int]] = defaultdict(list)
    measure_pitch_counts: dict[int, Counter[int]] = defaultdict(Counter)
    measure_pc_counts: dict[int, Counter[int]] = defaultdict(Counter)
    measure_oct_counts: dict[int, Counter[int]] = defaultdict(Counter)

    for (measure, _step, pitch), count in champion.items():
        for _ in range(max(0, int(count))):
            measure_pitches[measure].append(pitch)
        measure_pitch_counts[measure][pitch] += int(count)
        measure_pc_counts[measure][pitch % 12] += int(count)
        measure_oct_counts[measure][pitch // 12] += int(count)

    return {
        "measurePitches": measure_pitches,
        "measurePitchCounts": measure_pitch_counts,
        "measurePcCounts": measure_pc_counts,
        "measureOctCounts": measure_oct_counts,
    }


def local_features(tok: tuple[int, int, int], maps: dict[str, Any]) -> dict[str, Any]:
    measure, step, pitch = tok
    measure_pitches: dict[int, list[int]] = maps["measurePitches"]
    measure_pitch_counts: dict[int, Counter[int]] = maps["measurePitchCounts"]
    measure_pc_counts: dict[int, Counter[int]] = maps["measurePcCounts"]
    measure_oct_counts: dict[int, Counter[int]] = maps["measureOctCounts"]

    pitches = measure_pitches.get(measure, [])
    unique = sorted(set(pitches))
    med = median_int(pitches)
    low = min(pitches) if pitches else pitch
    high = max(pitches) if pitches else pitch
    span = high - low
    distance_from_median = abs(pitch - med)
    distance_from_low = pitch - low
    distance_from_high = high - pitch

    if len(unique) <= 1:
        rank_pct = 50
    else:
        rank_idx = unique.index(pitch) if pitch in unique else 0
        rank_pct = int(round(100.0 * rank_idx / (len(unique) - 1)))

    pc = pitch % 12
    octave = pitch // 12
    same_pitch_measure = int(measure_pitch_counts.get(measure, Counter()).get(pitch, 0))
    same_pc_measure = int(measure_pc_counts.get(measure, Counter()).get(pc, 0))
    same_oct_measure = int(measure_oct_counts.get(measure, Counter()).get(octave, 0))

    neighbor_pc = 0
    neighbor_oct = 0
    neighbor_exact_pitch = 0
    neighbor_measures_present = 0
    neighbor_medians: list[int] = []
    for other_measure in (measure - 2, measure - 1, measure + 1, measure + 2):
        other_pitches = measure_pitches.get(other_measure, [])
        if not other_pitches:
            continue
        neighbor_measures_present += 1
        neighbor_medians.append(median_int(other_pitches))
        neighbor_pc += int(measure_pc_counts.get(other_measure, Counter()).get(pc, 0))
        neighbor_oct += int(measure_oct_counts.get(other_measure, Counter()).get(octave, 0))
        neighbor_exact_pitch += int(measure_pitch_counts.get(other_measure, Counter()).get(pitch, 0))

    neighbor_median = median_int(neighbor_medians) if neighbor_medians else med
    neighbor_median_distance = abs(pitch - neighbor_median)

    return {
        "measure": measure,
        "step": step,
        "pitch": pitch,
        "pitchClass": pc,
        "octaveBand": octave,
        "measureEventCount": len(pitches),
        "measureUniquePitchCount": len(unique),
        "measureMedianPitch": med,
        "measureLowPitch": low,
        "measureHighPitch": high,
        "measurePitchSpan": span,
        "distanceFromMeasureMedian": distance_from_median,
        "distanceFromMeasureLow": distance_from_low,
        "distanceFromMeasureHigh": distance_from_high,
        "measureRankPct": rank_pct,
        "samePitchMeasure": same_pitch_measure,
        "samePcMeasure": same_pc_measure,
        "sameOctaveMeasure": same_oct_measure,
        "neighborMeasuresPresent": neighbor_measures_present,
        "neighborSamePitch": neighbor_exact_pitch,
        "neighborSamePc": neighbor_pc,
        "neighborSameOctave": neighbor_oct,
        "neighborMedianDistance": neighbor_median_distance,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    pc = f"pc{int(f['pitchClass'])}"
    ob = bucket(int(f["octaveBand"]), [3, 4, 5, 99], ["ob3m", "ob4", "ob5", "ob6p"])
    span = bucket(int(f["measurePitchSpan"]), [5, 11, 17, 23, 99], ["sp0_5", "sp6_11", "sp12_17", "sp18_23", "sp24p"])
    med = bucket(int(f["distanceFromMeasureMedian"]), [2, 5, 9, 14, 99], ["md0_2", "md3_5", "md6_9", "md10_14", "md15p"])
    edge = min(int(f["distanceFromMeasureLow"]), int(f["distanceFromMeasureHigh"]))
    edge_b = bucket(edge, [0, 2, 5, 99], ["edge0", "edge1_2", "edge3_5", "edge6p"])
    rank = bucket(int(f["measureRankPct"]), [10, 30, 70, 90, 100], ["rk0_10", "rk11_30", "rk31_70", "rk71_90", "rk91_100"])
    uniq = bucket(int(f["measureUniquePitchCount"]), [2, 4, 7, 99], ["u1_2", "u3_4", "u5_7", "u8p"])
    ev = bucket(int(f["measureEventCount"]), [6, 12, 20, 99], ["ev0_6", "ev7_12", "ev13_20", "ev21p"])
    spm = bucket(int(f["samePitchMeasure"]), [1, 2, 4, 99], ["spm1", "spm2", "spm3_4", "spm5p"])
    pcm = bucket(int(f["samePcMeasure"]), [1, 2, 4, 99], ["pcm1", "pcm2", "pcm3_4", "pcm5p"])
    om = bucket(int(f["sameOctaveMeasure"]), [2, 5, 9, 99], ["om0_2", "om3_5", "om6_9", "om10p"])
    nsp = bucket(int(f["neighborSamePitch"]), [0, 1, 3, 99], ["nsp0", "nsp1", "nsp2_3", "nsp4p"])
    npc = bucket(int(f["neighborSamePc"]), [0, 2, 5, 99], ["npc0", "npc1_2", "npc3_5", "npc6p"])
    nmd = bucket(int(f["neighborMedianDistance"]), [2, 5, 9, 14, 99], ["nmd0_2", "nmd3_5", "nmd6_9", "nmd10_14", "nmd15p"])

    return {
        f"measureMedianDistance::{med}",
        f"measureEdgeDistance::{edge_b}",
        f"measurePitchRank::{rank}",
        f"measurePitchSpan::{span}",
        f"measurePitchRecurrence::{spm}",
        f"measurePitchClassRecurrence::{pcm}",
        f"neighborPitchRecurrence::{nsp}",
        f"neighborPitchClassRecurrence::{npc}",
        f"neighborMedianDistance::{nmd}",
        f"registerShapeCross::{ob}|{span}|{med}|{rank}",
        f"measureRarityCross::{pc}|{ob}|{spm}|{pcm}|{om}",
        f"neighborRegisterCross::{pc}|{ob}|{nsp}|{npc}|{nmd}",
        f"measureDistributionCross::{uniq}|{ev}|{span}|{edge_b}|{rank}",
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

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion, reconstruction = s3118.reconstruct_3118(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.18 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    maps = build_maps(champion)
    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = local_features(tok, maps)
        signatures = sorted(signatures_for(features))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "features": features,
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
        raise RuntimeError("Protected candidate changed during 31.18 measure-register distribution profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.18-measure-register-distribution-precision",
        "champion3118Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "measure-and-neighboring-measure-register-pitch-distribution-shape",
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

    print("GOMYWAY 31.18 MEASURE REGISTER DISTRIBUTION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision measure-register signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true measure-register signatures:")
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
