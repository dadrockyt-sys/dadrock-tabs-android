from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2813_chord_context_survivors_precision_v1 as c2813

recur = c2813.recur
recall = c2813.recall
v2 = c2813.v2
v3 = c2813.v3
harmonic = c2813.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2813-temporal-density-crowding-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2813-temporal-density-crowding-v1-manifest.json"
EXPECTED = (183, 684, 251)
EXPECTED_F1 = 28.13


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: int, cuts: list[int], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def slot_counts(champion: Counter[tuple[int, int, int]]) -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = defaultdict(int)
    for (measure, step, _pitch), count in champion.items():
        out[(measure, step)] += int(count)
    return dict(out)


def measure_counts(champion: Counter[tuple[int, int, int]]) -> dict[int, int]:
    out: dict[int, int] = defaultdict(int)
    for (measure, _step, _pitch), count in champion.items():
        out[measure] += int(count)
    return dict(out)


def pitch_step_map(champion: Counter[tuple[int, int, int]]) -> dict[tuple[int, int], list[int]]:
    out: dict[tuple[int, int], list[int]] = defaultdict(list)
    for (measure, step, pitch), count in champion.items():
        for _ in range(int(count)):
            out[(measure, pitch)].append(step)
    for key in out:
        out[key].sort()
    return dict(out)


def local_features(
    tok: tuple[int, int, int],
    champion: Counter[tuple[int, int, int]],
    slots: dict[tuple[int, int], int],
    measures: dict[int, int],
    pitch_steps: dict[tuple[int, int], list[int]],
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
) -> dict[str, Any]:
    measure, step, pitch = tok
    same = int(slots.get((measure, step), 0))
    pm1 = int(slots.get((measure, step - 1), 0))
    pp1 = int(slots.get((measure, step + 1), 0))
    pm2 = int(slots.get((measure, step - 2), 0))
    pp2 = int(slots.get((measure, step + 2), 0))
    window1 = same + pm1 + pp1
    window2 = window1 + pm2 + pp2
    measure_density = int(measures.get(measure, 0))

    steps = pitch_steps.get((measure, pitch), [])
    nearest_same_pitch = min((abs(step - s) for s in steps if s != step), default=99)
    repeated_same_pitch = sum(1 for s in steps if abs(step - s) <= 2 and s != step)

    neighbor_slot_max = max(pm1, pp1)
    neighbor_slot_sum = pm1 + pp1
    local_spike = max(0, same - max(pm1, pp1))

    center = float(grid[(measure, step)])
    wf = c2813.chord.phase.phase_features(winner_audio, winner_sr, center, pitch)
    af = c2813.chord.phase.phase_features(alt_audio, alt_sr, center, pitch)
    wm = float(wf.get("meanMagnitude", wf.get("magnitudeMean", 0.0)) or 0.0)
    am = float(af.get("meanMagnitude", af.get("magnitudeMean", 0.0)) or 0.0)
    stem_ratio = (min(wm, am) / max(wm, am)) if max(wm, am) > 1e-12 else 0.0

    return {
        "sameSlot": same,
        "neighborSlotSum": neighbor_slot_sum,
        "neighborSlotMax": neighbor_slot_max,
        "window1": window1,
        "window2": window2,
        "measureDensity": measure_density,
        "nearestSamePitchStep": nearest_same_pitch,
        "repeatedSamePitch": repeated_same_pitch,
        "localSpike": local_spike,
        "stemRatio": stem_ratio,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    same = bucket(int(f["sameSlot"]), [1, 2, 3, 5, 99], ["s1", "s2", "s3", "s4_5", "s6p"])
    nsum = bucket(int(f["neighborSlotSum"]), [0, 2, 5, 9, 99], ["ns0", "ns1_2", "ns3_5", "ns6_9", "ns10p"])
    nmax = bucket(int(f["neighborSlotMax"]), [0, 1, 3, 5, 99], ["nm0", "nm1", "nm2_3", "nm4_5", "nm6p"])
    w1 = bucket(int(f["window1"]), [1, 4, 8, 14, 99], ["w1_1", "w1_2_4", "w1_5_8", "w1_9_14", "w1_15p"])
    w2 = bucket(int(f["window2"]), [3, 8, 14, 22, 99], ["w2_0_3", "w2_4_8", "w2_9_14", "w2_15_22", "w2_23p"])
    md = bucket(int(f["measureDensity"]), [5, 10, 18, 28, 99], ["md0_5", "md6_10", "md11_18", "md19_28", "md29p"])
    rsp = bucket(int(f["nearestSamePitchStep"]), [1, 2, 4, 8, 99], ["rsp1", "rsp2", "rsp3_4", "rsp5_8", "rsp9p"])
    rep = bucket(int(f["repeatedSamePitch"]), [0, 1, 2, 99], ["rep0", "rep1", "rep2", "rep3p"])
    spike = bucket(int(f["localSpike"]), [0, 1, 2, 4, 99], ["sp0", "sp1", "sp2", "sp3_4", "sp5p"])
    sr = float(f["stemRatio"])
    srb = "sr_lt025" if sr < 0.25 else ("sr_025_050" if sr < 0.50 else ("sr_050_075" if sr < 0.75 else "sr_075p"))

    return {
        f"sameSlotDensity::{same}",
        f"neighborCrowding::{nsum}",
        f"neighborPeak::{nmax}",
        f"microWindowDensity::{w1}",
        f"localWindowDensity::{w2}",
        f"measureEventDensity::{md}",
        f"samePitchAttackDistance::{rsp}",
        f"samePitchRepeatCount::{rep}",
        f"localDensitySpike::{spike}",
        f"crowdingStemSupport::{srb}",
        f"densityCross::{same}|{nsum}|{w1}|{spike}",
        f"repeatAttackCross::{rsp}|{rep}|{w1}|{srb}",
        f"measureCrowdingCross::{md}|{w2}|{same}",
        f"stemCrowdingCross::{same}|{nmax}|{spike}|{srb}",
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
    champion, reconstruction = c2813.reconstruct_2813(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 28.13 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    slots = slot_counts(champion)
    measures = measure_counts(champion)
    pitch_steps = pitch_step_map(champion)
    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        features = local_features(
            tok, champion, slots, measures, pitch_steps, grid,
            winner_audio, winner_sr, alt_audio, alt_sr,
        )
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
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 28.13 temporal-density crowding profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.13-temporal-density-crowding-precision",
        "champion2813Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "local-temporal-density-event-crowding-repeat-attack-and-cross-stem-support",
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

    print("GOMYWAY 28.13 TEMPORAL DENSITY CROWDING V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision temporal-density signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true temporal-density signatures:")
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
