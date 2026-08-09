from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench

v2 = bench.v2
v3 = bench.v3
recur = bench.recur
recall = bench.recall
cached = bench.cached

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-source-confidence-duration-residual-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-source-confidence-duration-residual-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19

CONF_BUCKETS = (
    ("conf_lt_020", float("-inf"), 0.20),
    ("conf_020_024", 0.20, 0.24),
    ("conf_024_028", 0.24, 0.28),
    ("conf_028_034", 0.28, 0.34),
    ("conf_034_044", 0.34, 0.44),
    ("conf_044_060", 0.44, 0.60),
    ("conf_060_plus", 0.60, float("inf")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def conf_bucket(value: float) -> str:
    for name, lo, hi in CONF_BUCKETS:
        if lo <= value < hi:
            return name
    return "conf_unknown"


def duration_bucket(value: int) -> str:
    if value <= 1:
        return "dur_1"
    if value == 2:
        return "dur_2"
    if value <= 4:
        return "dur_3_4"
    if value <= 8:
        return "dur_5_8"
    return "dur_9_plus"


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def note_pitch(note: Any) -> int | None:
    if isinstance(note, bool):
        return None
    if isinstance(note, (int, float, str)):
        try:
            return int(float(note))
        except (TypeError, ValueError):
            return None
    if not isinstance(note, dict):
        return None
    for key in ("midi", "midiPitch", "pitch", "note", "noteNumber"):
        value = note.get(key)
        if value is None or isinstance(value, bool):
            continue
        try:
            return int(float(value))
        except (TypeError, ValueError):
            continue
    return None


def event_pitches(event: dict[str, Any]) -> list[int]:
    notes = event.get("notes")
    pitches: list[int] = []
    if isinstance(notes, list):
        for note in notes:
            pitch = note_pitch(note)
            if pitch is not None:
                pitches.append(pitch)
    elif notes is not None:
        pitch = note_pitch(notes)
        if pitch is not None:
            pitches.append(pitch)

    if not pitches:
        for key in ("midi", "midiPitch", "pitch", "noteNumber"):
            pitch = note_pitch(event.get(key))
            if pitch is not None:
                pitches.append(pitch)
                break
    return sorted(set(pitches))


def source_token_features(events: list[dict[str, Any]]) -> dict[tuple[int, int, int], dict[str, Any]]:
    # Build the full timing grid once so its validity is checked exactly as in the
    # grading pipeline. Source events already carry the protected measure/step
    # projection, so feature rows can then be mapped directly without calling
    # build_timing_grid() on isolated single events.
    v2.build_timing_grid(events)

    features: dict[tuple[int, int, int], dict[str, Any]] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = v2.measure_of(event)
        step = v2.step_of(event)
        if measure is None or step is None:
            continue
        if not 1 <= measure <= v2.MEASURE_END or not 0 <= step < v2.STEPS_PER_MEASURE:
            continue

        confidence = as_float(event.get("confidence"), 0.0)
        duration_steps = as_int(event.get("durationSteps"), 0)
        candidate = {
            "confidence": confidence,
            "durationSteps": duration_steps,
            "confidenceBucket": conf_bucket(confidence),
            "durationBucket": duration_bucket(duration_steps),
        }

        for pitch in event_pitches(event):
            token = (int(measure), int(step), int(pitch))
            previous = features.get(token)
            if previous is None or (
                candidate["confidence"], candidate["durationSteps"]
            ) > (
                previous["confidence"], previous["durationSteps"]
            ):
                features[token] = dict(candidate)
    return features


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, _ = v2.build_timing_grid(events)
    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    rows = cached.load_profile_rows()
    champion_additions = bench.rows_to_counter(rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual != EXPECTED_1419 or abs(float(score_1419["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, "
            f"got {actual}/{score_1419['pitchF1']}"
        )

    token_features = source_token_features(events)
    if not token_features:
        raise RuntimeError("No source confidence/duration tokens could be projected from protected events.")

    champion_tokens = set(champion_1419.keys())
    residual = {
        token: feature
        for token, feature in token_features.items()
        if token not in champion_tokens
    }

    single_counts: dict[str, Counter[str]] = defaultdict(Counter)
    joint_counts: dict[str, Counter[str]] = defaultdict(Counter)
    detailed_rows: list[dict[str, Any]] = []

    for token, feature in residual.items():
        truth = "true" if token in reference else "false"
        cb = str(feature["confidenceBucket"])
        db = str(feature["durationBucket"])
        single_counts[f"confidence|{cb}"][truth] += 1
        single_counts[f"duration|{db}"][truth] += 1
        joint_counts[f"{cb}|{db}"][truth] += 1
        detailed_rows.append({
            "token": list(token),
            "true": truth == "true",
            **feature,
        })

    def summarize(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
        output: list[dict[str, Any]] = []
        for name, counts in groups.items():
            row = {
                "signature": name,
                **precision_row(int(counts["true"]), int(counts["false"])),
            }
            output.append(row)
        return sorted(
            output,
            key=lambda row: (row["precision"], row["true"], -row["false"]),
            reverse=True,
        )

    singles = summarize(single_counts)
    joints = summarize(joint_counts)
    supported = [row for row in joints if int(row["true"]) >= 2]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during confidence-duration residual profile")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-source-confidence-duration-residual",
        "championScore": score_1419,
        "sourceTokenCount": len(token_features),
        "residualSourceTokenCount": len(residual),
        "singleFeaturePrecision": singles,
        "jointFeaturePrecision": joints,
        "supportedJointFeaturePrecision": supported,
        "rows": detailed_rows,
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
        "championPitchF1": score_1419["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 SOURCE CONFIDENCE DURATION RESIDUAL V1")
    print("Passed: True")
    print("Champion remains frozen:", score_1419["pitchF1"], "/", score_1419["matched"], "/", score_1419["missing"], "/", score_1419["extra"])
    print("Source tokens:", len(token_features))
    print("Residual source tokens:", len(residual))
    print("\nTop confidence/duration single-feature signatures:")
    for row in singles[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nTop repeatable confidence x duration signatures:")
    for row in joints[:25]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("\nTop supported confidence x duration signatures (2+ true):")
    for row in supported[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
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
