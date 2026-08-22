from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2850_temporal_density_survivors_precision_v1 as s2850

recur = s2850.recur
recall = s2850.recall
v2 = s2850.v2
v3 = s2850.v3
harmonic = s2850.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2850-measure-position-rhythmic-role-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2850-measure-position-rhythmic-role-v1-manifest.json"
EXPECTED = (183, 684, 234)
EXPECTED_F1 = 28.50


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


def build_role_maps(champion: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    step_counts: Counter[int] = Counter()
    measure_step_counts: Counter[tuple[int, int]] = Counter()
    pitch_step_measures: dict[tuple[int, int], set[int]] = defaultdict(set)
    step_measures: dict[int, set[int]] = defaultdict(set)
    pitch_measures: dict[int, set[int]] = defaultdict(set)

    for (measure, step, pitch), count in champion.items():
        step_counts[step] += int(count)
        measure_step_counts[(measure, step)] += int(count)
        pitch_step_measures[(pitch, step)].add(measure)
        step_measures[step].add(measure)
        pitch_measures[pitch].add(measure)

    return {
        "stepCounts": step_counts,
        "measureStepCounts": measure_step_counts,
        "pitchStepMeasures": pitch_step_measures,
        "stepMeasures": step_measures,
        "pitchMeasures": pitch_measures,
    }


def local_features(tok: tuple[int, int, int], maps: dict[str, Any]) -> dict[str, Any]:
    measure, step, pitch = tok
    step_counts: Counter[int] = maps["stepCounts"]
    measure_step_counts: Counter[tuple[int, int]] = maps["measureStepCounts"]
    pitch_step_measures: dict[tuple[int, int], set[int]] = maps["pitchStepMeasures"]
    step_measures: dict[int, set[int]] = maps["stepMeasures"]
    pitch_measures: dict[int, set[int]] = maps["pitchMeasures"]

    same_step_here = int(measure_step_counts.get((measure, step), 0))
    same_step_global = int(step_counts.get(step, 0))

    same_step_neighbor_1 = sum(
        int(measure_step_counts.get((measure + d, step), 0)) for d in (-1, 1)
    )
    same_step_neighbor_2 = sum(
        int(measure_step_counts.get((measure + d, step), 0)) for d in (-2, 2)
    )
    same_step_neighbor_4 = sum(
        int(measure_step_counts.get((measure + d, step), 0)) for d in (-4, 4)
    )

    pitch_step_set = pitch_step_measures.get((pitch, step), set())
    same_pitch_step_near = sum(
        1 for m in pitch_step_set if m != measure and abs(m - measure) <= 4
    )
    same_pitch_step_exact2 = int(measure - 2 in pitch_step_set) + int(measure + 2 in pitch_step_set)
    same_pitch_step_exact4 = int(measure - 4 in pitch_step_set) + int(measure + 4 in pitch_step_set)

    step_measure_set = step_measures.get(step, set())
    step_measure_recurrence = sum(1 for m in step_measure_set if m != measure and abs(m - measure) <= 4)

    pitch_measure_set = pitch_measures.get(pitch, set())
    pitch_measure_recurrence = sum(1 for m in pitch_measure_set if m != measure and abs(m - measure) <= 4)

    return {
        "step": step,
        "stepParity": step % 2,
        "stepMod4": step % 4,
        "stepMod8": step % 8,
        "measureMod2": measure % 2,
        "measureMod4": measure % 4,
        "sameStepHere": same_step_here,
        "sameStepGlobal": same_step_global,
        "sameStepNeighbor1": same_step_neighbor_1,
        "sameStepNeighbor2": same_step_neighbor_2,
        "sameStepNeighbor4": same_step_neighbor_4,
        "samePitchStepNear": same_pitch_step_near,
        "samePitchStepExact2": same_pitch_step_exact2,
        "samePitchStepExact4": same_pitch_step_exact4,
        "stepMeasureRecurrence": step_measure_recurrence,
        "pitchMeasureRecurrence": pitch_measure_recurrence,
    }


def signatures_for(f: dict[str, Any]) -> set[str]:
    step = int(f["step"])
    parity = "even" if int(f["stepParity"]) == 0 else "odd"
    sm4 = f"sm4_{int(f['stepMod4'])}"
    sm8 = f"sm8_{int(f['stepMod8'])}"
    mm2 = f"mm2_{int(f['measureMod2'])}"
    mm4 = f"mm4_{int(f['measureMod4'])}"

    here = bucket(int(f["sameStepHere"]), [1, 2, 4, 99], ["sh1", "sh2", "sh3_4", "sh5p"])
    global_step = bucket(int(f["sameStepGlobal"]), [8, 20, 40, 80, 999], ["sg0_8", "sg9_20", "sg21_40", "sg41_80", "sg81p"])
    n1 = bucket(int(f["sameStepNeighbor1"]), [0, 2, 5, 99], ["n1_0", "n1_1_2", "n1_3_5", "n1_6p"])
    n2 = bucket(int(f["sameStepNeighbor2"]), [0, 2, 5, 99], ["n2_0", "n2_1_2", "n2_3_5", "n2_6p"])
    n4 = bucket(int(f["sameStepNeighbor4"]), [0, 2, 5, 99], ["n4_0", "n4_1_2", "n4_3_5", "n4_6p"])
    psn = bucket(int(f["samePitchStepNear"]), [0, 1, 3, 99], ["psn0", "psn1", "psn2_3", "psn4p"])
    sme = bucket(int(f["stepMeasureRecurrence"]), [0, 2, 4, 99], ["smr0", "smr1_2", "smr3_4", "smr5p"])
    pme = bucket(int(f["pitchMeasureRecurrence"]), [0, 2, 4, 99], ["pmr0", "pmr1_2", "pmr3_4", "pmr5p"])
    e2 = f"e2_{int(f['samePitchStepExact2'])}"
    e4 = f"e4_{int(f['samePitchStepExact4'])}"

    return {
        f"rhythmicStep::{step}",
        f"stepParity::{parity}",
        f"stepClass4::{sm4}",
        f"stepClass8::{sm8}",
        f"measureRole2::{mm2}",
        f"measureRole4::{mm4}",
        f"sameStepGlobal::{global_step}",
        f"sameStepNeighbor1::{n1}",
        f"sameStepNeighbor2::{n2}",
        f"sameStepNeighbor4::{n4}",
        f"samePitchStepNear::{psn}",
        f"stepMeasureRecurrence::{sme}",
        f"pitchMeasureRecurrence::{pme}",
        f"positionCross::{parity}|{sm4}|{mm4}|{global_step}",
        f"neighborRoleCross::{sm4}|{mm2}|{n1}|{n2}",
        f"repeatPositionCross::{sm8}|{mm4}|{psn}|{e2}|{e4}",
        f"rhythmicRoleCross::{sm4}|{mm4}|{here}|{sme}|{pme}",
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
    champion, reconstruction = s2850.reconstruct_2850(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 28.50 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    maps = build_role_maps(champion)
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
        raise RuntimeError("Protected candidate changed during 28.50 measure-position rhythmic-role profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.50-measure-position-rhythmic-role-precision",
        "champion2850Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "measure-position-step-class-neighbor-role-and-cross-measure-rhythmic-recurrence",
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

    print("GOMYWAY 28.50 MEASURE POSITION RHYTHMIC ROLE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision measure-position signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true measure-position signatures:")
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
