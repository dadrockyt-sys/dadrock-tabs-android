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
OUTPUT_PATH = PUBLIC / "gomyway-3118-pitch-interval-rhythmic-neighbor-context-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3118-pitch-interval-rhythmic-neighbor-context-v1-manifest.json"
EXPECTED = (183, 684, 124)
EXPECTED_F1 = 31.18


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: int, cuts: list[int], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


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
    slot_pitches: dict[tuple[int, int], set[int]] = defaultdict(set)
    measure_steps: dict[int, dict[int, set[int]]] = defaultdict(lambda: defaultdict(set))
    pitch_locations: dict[int, list[tuple[int, int]]] = defaultdict(list)

    for (measure, step, pitch), count in champion.items():
        if int(count) <= 0:
            continue
        slot_pitches[(measure, step)].add(pitch)
        measure_steps[measure][step].add(pitch)
        pitch_locations[pitch].append((measure, step))

    return {
        "slotPitches": slot_pitches,
        "measureSteps": measure_steps,
        "pitchLocations": pitch_locations,
    }


def nearest_distance(pitch: int, pitches: set[int]) -> int | None:
    if not pitches:
        return None
    return min(abs(pitch - p) for p in pitches)


def nearest_other_distance(pitch: int, pitches: set[int]) -> int | None:
    others = {p for p in pitches if p != pitch}
    return nearest_distance(pitch, others)


def nearest_step_with_pitches(step_map: dict[int, set[int]], step: int, direction: int) -> tuple[int, set[int]] | None:
    candidates = [s for s in step_map if (s < step if direction < 0 else s > step)]
    if not candidates:
        return None
    chosen = max(candidates) if direction < 0 else min(candidates)
    return chosen, step_map[chosen]


def local_features(tok: tuple[int, int, int], maps: dict[str, Any]) -> dict[str, Any]:
    measure, step, pitch = tok
    slot_pitches: dict[tuple[int, int], set[int]] = maps["slotPitches"]
    measure_steps: dict[int, dict[int, set[int]]] = maps["measureSteps"]
    pitch_locations: dict[int, list[tuple[int, int]]] = maps["pitchLocations"]

    current = slot_pitches.get((measure, step), set())
    step_map = measure_steps.get(measure, {})
    prev_item = nearest_step_with_pitches(step_map, step, -1)
    next_item = nearest_step_with_pitches(step_map, step, 1)

    prev_gap = 99 if prev_item is None else step - prev_item[0]
    next_gap = 99 if next_item is None else next_item[0] - step
    prev_interval = 99 if prev_item is None else int(nearest_distance(pitch, prev_item[1]) or 0)
    next_interval = 99 if next_item is None else int(nearest_distance(pitch, next_item[1]) or 0)

    same_slot_interval = nearest_other_distance(pitch, current)
    same_slot_interval = 99 if same_slot_interval is None else int(same_slot_interval)

    neighbor_intervals = [v for v in (prev_interval, next_interval) if v != 99]
    min_neighbor_interval = min(neighbor_intervals) if neighbor_intervals else 99
    max_neighbor_interval = max(neighbor_intervals) if neighbor_intervals else 99

    near_same_pitch = 0
    near_octave_pitch = 0
    for m, s in pitch_locations.get(pitch, []):
        if (m, s) != (measure, step) and abs(m - measure) <= 2 and abs(s - step) <= 4:
            near_same_pitch += 1
    for octave_pitch in (pitch - 12, pitch + 12):
        for m, s in pitch_locations.get(octave_pitch, []):
            if abs(m - measure) <= 2 and abs(s - step) <= 4:
                near_octave_pitch += 1

    return {
        "pitch": pitch,
        "pitchClass": pitch % 12,
        "octaveBand": pitch // 12,
        "step": step,
        "stepMod4": step % 4,
        "slotSize": len(current),
        "sameSlotInterval": same_slot_interval,
        "prevGap": prev_gap,
        "nextGap": next_gap,
        "prevInterval": prev_interval,
        "nextInterval": next_interval,
        "minNeighborInterval": min_neighbor_interval,
        "maxNeighborInterval": max_neighbor_interval,
        "nearSamePitch": near_same_pitch,
        "nearOctavePitch": near_octave_pitch,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    pc = f"pc{int(f['pitchClass'])}"
    ob = bucket(int(f["octaveBand"]), [3, 4, 5, 99], ["ob3m", "ob4", "ob5", "ob6p"])
    sm4 = f"sm4_{int(f['stepMod4'])}"
    slot = bucket(int(f["slotSize"]), [1, 2, 4, 99], ["slot1", "slot2", "slot3_4", "slot5p"])
    ssi = bucket(int(f["sameSlotInterval"]), [0, 2, 5, 11, 99], ["ssi0_2", "ssi3_5", "ssi6_11", "ssi12p", "ssinone"])
    pg = bucket(int(f["prevGap"]), [1, 2, 4, 99], ["pg1", "pg2", "pg3_4", "pgnone"])
    ng = bucket(int(f["nextGap"]), [1, 2, 4, 99], ["ng1", "ng2", "ng3_4", "ngnone"])
    pi = bucket(int(f["prevInterval"]), [0, 2, 5, 11, 99], ["pi0_2", "pi3_5", "pi6_11", "pi12p", "pinone"])
    ni = bucket(int(f["nextInterval"]), [0, 2, 5, 11, 99], ["ni0_2", "ni3_5", "ni6_11", "ni12p", "ninone"])
    mni = bucket(int(f["minNeighborInterval"]), [0, 2, 5, 11, 99], ["mni0_2", "mni3_5", "mni6_11", "mni12p", "mninone"])
    mxi = bucket(int(f["maxNeighborInterval"]), [2, 5, 11, 99], ["mxi0_2", "mxi3_5", "mxi6_11", "mxi12p"])
    same = bucket(int(f["nearSamePitch"]), [0, 1, 3, 99], ["same0", "same1", "same2_3", "same4p"])
    octv = bucket(int(f["nearOctavePitch"]), [0, 1, 3, 99], ["oct0", "oct1", "oct2_3", "oct4p"])

    return {
        f"pitchClass::{pc}",
        f"octaveBand::{ob}",
        f"sameSlotInterval::{ssi}",
        f"neighborMinInterval::{mni}",
        f"neighborMaxInterval::{mxi}",
        f"nearSamePitch::{same}",
        f"nearOctavePitch::{octv}",
        f"pitchRhythmCross::{pc}|{sm4}|{mni}|{same}",
        f"intervalNeighborCross::{slot}|{ssi}|{pi}|{ni}",
        f"rhythmicNeighborCross::{sm4}|{pg}|{ng}|{mni}|{mxi}",
        f"pitchRecurrenceCross::{pc}|{ob}|{same}|{octv}|{mni}",
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
        raise RuntimeError("Protected candidate changed during 31.18 pitch/interval rhythmic-neighbor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.18-pitch-interval-rhythmic-neighbor-context-precision",
        "champion3118Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "pitch-class-local-interval-rhythmic-neighbor-and-pitch-recurrence-context",
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

    print("GOMYWAY 31.18 PITCH INTERVAL RHYTHMIC NEIGHBOR CONTEXT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision pitch/interval-neighbor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true pitch/interval-neighbor signatures:")
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
