from __future__ import annotations

import hashlib
import json
from bisect import bisect_left
from collections import Counter
from pathlib import Path
from typing import Any

from basic_pitch.inference import predict

import profile_gomyway_3161_near_zero_microtiming_refinement_v1 as micro

s3161 = micro.s3161
recur = micro.recur
recall = micro.recall
v2 = micro.v2
v3 = micro.v3
harmonic = micro.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-basic-pitch-sweep-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-wide-recall-basic-pitch-sweep-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61

# Deliberately wider-recall than the current source generation. Read-only profiling only.
SWEEPS = [
    {"name": "o030_f020", "onset_threshold": 0.30, "frame_threshold": 0.20},
    {"name": "o025_f015", "onset_threshold": 0.25, "frame_threshold": 0.15},
    {"name": "o020_f012", "onset_threshold": 0.20, "frame_threshold": 0.12},
    {"name": "o015_f010", "onset_threshold": 0.15, "frame_threshold": 0.10},
]
MAX_GRID_ERROR_SECONDS = 0.10
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def note_events_from_predict(path: Path, onset_threshold: float, frame_threshold: float) -> list[Any]:
    result = predict(
        str(path),
        onset_threshold=onset_threshold,
        frame_threshold=frame_threshold,
        minimum_note_length=20.0,
        minimum_frequency=80.0,
        maximum_frequency=1400.0,
    )
    if not isinstance(result, tuple) or len(result) < 3:
        raise RuntimeError(f"Unexpected Basic Pitch return shape for {path}")
    note_events = result[2]
    return list(note_events or [])


def parse_note_event(event: Any) -> tuple[float, float, int, float] | None:
    if isinstance(event, dict):
        start = event.get("start_time", event.get("start", event.get("startTime")))
        end = event.get("end_time", event.get("end", event.get("endTime", start)))
        pitch = event.get("pitch_midi", event.get("midi", event.get("pitch")))
        amp = event.get("amplitude", event.get("confidence", event.get("velocity", 0.0)))
    elif isinstance(event, (list, tuple)) and len(event) >= 3:
        start, end, pitch = event[0], event[1], event[2]
        amp = event[3] if len(event) >= 4 else 0.0
    else:
        return None
    try:
        return float(start), float(end), int(round(float(pitch))), float(amp or 0.0)
    except (TypeError, ValueError):
        return None


def nearest_grid_token(
    start_time: float,
    pitch: int,
    sorted_times: list[float],
    time_to_slots: dict[float, list[tuple[int, int]]],
) -> tuple[int, int, int] | None:
    if not sorted_times:
        return None
    i = bisect_left(sorted_times, start_time)
    candidates: list[float] = []
    if i < len(sorted_times):
        candidates.append(sorted_times[i])
    if i > 0:
        candidates.append(sorted_times[i - 1])
    if not candidates:
        return None
    best_time = min(candidates, key=lambda t: abs(t - start_time))
    if abs(best_time - start_time) > MAX_GRID_ERROR_SECONDS:
        return None
    slots = time_to_slots[best_time]
    # Timing grid can theoretically contain duplicate timestamps. Use deterministic first slot.
    measure, step = sorted(slots)[0]
    return (int(measure), int(step), int(pitch))


def detect_tokens(
    stem: Path,
    grid: dict[tuple[int, int], float],
    onset_threshold: float,
    frame_threshold: float,
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    sorted_times = sorted(set(float(t) for t in grid.values()))
    time_to_slots: dict[float, list[tuple[int, int]]] = {}
    for slot, t in grid.items():
        time_to_slots.setdefault(float(t), []).append(slot)

    raw = note_events_from_predict(stem, onset_threshold, frame_threshold)
    tokens: Counter[tuple[int, int, int]] = Counter()
    parsed = 0
    accepted = 0
    rejected_pitch = 0
    rejected_grid = 0
    for event in raw:
        parsed_event = parse_note_event(event)
        if parsed_event is None:
            continue
        parsed += 1
        start, _end, pitch, _amp = parsed_event
        if pitch < GUITAR_MIDI_MIN or pitch > GUITAR_MIDI_MAX:
            rejected_pitch += 1
            continue
        tok = nearest_grid_token(start, pitch, sorted_times, time_to_slots)
        if tok is None:
            rejected_grid += 1
            continue
        tokens[tok] += 1
        accepted += 1
    return tokens, {
        "rawNoteEvents": len(raw),
        "parsedNoteEvents": parsed,
        "acceptedGridEvents": accepted,
        "rejectedPitch": rejected_pitch,
        "rejectedGridDistance": rejected_grid,
        "uniqueTokens": len(tokens),
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
    champion, reconstruction = s3161.reconstruct_3161(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    stems = [Path(harmonic.legacy.WINNER_STEM), Path(harmonic.legacy.ALT_STEM)]
    rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for sweep in SWEEPS:
        union: Counter[tuple[int, int, int]] = Counter()
        stem_stats: list[dict[str, Any]] = []
        for stem in stems:
            detected, stats = detect_tokens(
                stem,
                grid,
                float(sweep["onset_threshold"]),
                float(sweep["frame_threshold"]),
            )
            # Presence union: repeated detector duplicates must not inflate note multiplicity.
            for tok in detected:
                union[tok] = 1
            stem_stats.append({"stem": str(stem), **stats})

        novel = Counter({tok: 1 for tok in union if tok not in champion})
        recover_true = int(sum((novel & reference).values()))
        recover_false = int(sum((novel - reference).values()))
        combined = champion | novel
        score = recur.grade(combined, reference)
        row = {
            **sweep,
            "stemStats": stem_stats,
            "unionDetectedUniqueTokens": len(union),
            "novelUniqueTokens": len(novel),
            "recoverTrue": recover_true,
            "recoverFalse": recover_false,
            "recoveryPrecision": round(100.0 * recover_true / (recover_true + recover_false), 2)
            if (recover_true + recover_false) else 0.0,
            "scoreIfAllNovelAdded": score,
        }
        rows.append(row)
        if best is None or (recover_true, -recover_false) > (int(best["recoverTrue"]), -int(best["recoverFalse"])):
            best = row

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during wide-recall Basic Pitch sweep")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "31.61-wide-recall-basic-pitch-threshold-sweep",
        "champion3161Score": baseline,
        "reconstruction": reconstruction,
        "sweeps": rows,
        "bestRecallSweep": best,
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
        "championPitchF1": baseline["pitchF1"],
        "bestSweep": best["name"] if best else None,
        "bestRecoverTrue": best["recoverTrue"] if best else 0,
        "bestRecoverFalse": best["recoverFalse"] if best else 0,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 WIDE-RECALL BASIC-PITCH SWEEP V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", baseline["pitchF1"])
    print("Champion matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    for row in rows:
        score = row["scoreIfAllNovelAdded"]
        print(
            row["name"],
            "novel=", row["novelUniqueTokens"],
            "recoverTrue=", row["recoverTrue"],
            "recoverFalse=", row["recoverFalse"],
            "precision=", row["recoveryPrecision"],
            "allAddedF1=", score["pitchF1"],
            "matched/missing/extra=", f"{score['matched']}/{score['missing']}/{score['extra']}",
        )
    if best:
        print("Best recall sweep:", best["name"], "true=", best["recoverTrue"], "false=", best["recoverFalse"])
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
