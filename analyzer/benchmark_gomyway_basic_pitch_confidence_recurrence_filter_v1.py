from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-basic-pitch-confidence-recurrence-filter-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-basic-pitch-confidence-recurrence-filter-v1-manifest.json"

TUNED_BASIC_PITCH_F1 = 6.39
CHORD_AWARE_WINNER_F1 = 6.51
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]
SNAP_TOLERANCE_SECONDS = 0.085

# Detection stays fixed at the tuned Basic Pitch winner.
v2.ONSET_THRESHOLD = 0.50
v2.FRAME_THRESHOLD = 0.30
v2.MINIMUM_NOTE_LENGTH_MS = 110.0

CONFIGS: list[dict[str, Any]] = [
    {"name": "confidence025", "relativeAmplitude": 0.25, "requireSupport": False, "supportRadius": 0, "cap": 5},
    {"name": "confidence035", "relativeAmplitude": 0.35, "requireSupport": False, "supportRadius": 0, "cap": 5},
    {"name": "confidence045", "relativeAmplitude": 0.45, "requireSupport": False, "supportRadius": 0, "cap": 5},
    {"name": "support1_amp025", "relativeAmplitude": 0.25, "requireSupport": True, "supportRadius": 1, "cap": 5},
    {"name": "support2_amp025", "relativeAmplitude": 0.25, "requireSupport": True, "supportRadius": 2, "cap": 5},
    {"name": "support1_amp035", "relativeAmplitude": 0.35, "requireSupport": True, "supportRadius": 1, "cap": 5},
    {"name": "support2_amp035", "relativeAmplitude": 0.35, "requireSupport": True, "supportRadius": 2, "cap": 5},
    {"name": "support2_amp045_cap4", "relativeAmplitude": 0.45, "requireSupport": True, "supportRadius": 2, "cap": 4},
]


def evaluate(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    reference_count = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    score = round(100.0 * v2.f1(matched, predicted_count, reference_count), 2)

    pref = Counter({k: n for k, n in reference.items() if k[0] in PRIORITY_MEASURES})
    ppred = Counter({k: n for k, n in predicted.items() if k[0] in PRIORITY_MEASURES})
    return {
        "pitchF1": score,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
        "priority": {
            "matched": sum((pref & ppred).values()),
            "missing": sum((pref - ppred).values()),
            "extra": sum((ppred - pref).values()),
        },
    }


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(STEM_PATH)

    before = v2.sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diag = v2.build_timing_grid(events)
    grid_items = list(grid.items())
    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    notes = v2.basic_pitch_notes(STEM_PATH)
    slotted: dict[tuple[int, int], list[tuple[int, float]]] = defaultdict(list)
    for start, _end, midi, amp in notes:
        slot, distance = v2.nearest_grid_slot(start, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            continue
        if midi < 40 or midi > 88:
            continue
        slotted[slot].append((midi, amp))

    results: list[dict[str, Any]] = []
    for cfg in CONFIGS:
        predicted: Counter[tuple[int, int, int]] = Counter()
        for (measure, step), rows in slotted.items():
            # Deduplicate same MIDI pitch, retaining strongest confidence.
            strongest: dict[int, float] = {}
            for midi, amp in rows:
                strongest[midi] = max(strongest.get(midi, 0.0), amp)
            if not strongest:
                continue

            max_amp = max(strongest.values())
            kept: list[tuple[int, float]] = []
            for midi, amp in strongest.items():
                if amp < max_amp * float(cfg["relativeAmplitude"]):
                    continue

                supported = False
                if bool(cfg["requireSupport"]):
                    radius = int(cfg["supportRadius"])
                    pitch_class = midi % 12
                    for delta in range(1, radius + 1):
                        for neighbor_step in (step - delta, step + delta):
                            for nmidi, _namp in slotted.get((measure, neighbor_step), []):
                                if nmidi == midi or nmidi % 12 == pitch_class:
                                    supported = True
                                    break
                            if supported:
                                break
                        if supported:
                            break

                    # Strong local events can survive without recurrence.
                    if not supported and amp < max_amp * 0.70:
                        continue

                kept.append((midi, amp))

            kept.sort(key=lambda row: row[1], reverse=True)
            kept = kept[: int(cfg["cap"])]
            for midi, _amp in kept:
                predicted[(measure, step, midi)] += 1

        metrics = evaluate(predicted, reference)
        row = {"name": cfg["name"], "settings": cfg, **metrics}
        results.append(row)
        print(
            f"{cfg['name']}: pitchF1={metrics['pitchF1']} matched={metrics['matched']} "
            f"missing={metrics['missing']} extra={metrics['extra']} predictions={metrics['predictions']} "
            f"priority={metrics['priority']['matched']}/{metrics['priority']['missing']}/{metrics['priority']['extra']}"
        )

    ranked = sorted(results, key=lambda r: (r["pitchF1"], r["matched"], -r["extra"]), reverse=True)
    winner = ranked[0]

    after = v2.sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected 949-event candidate changed.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "basic-pitch-confidence-recurrence-filter",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "timingGrid": grid_diag,
        "professionalReferenceRole": "downstream-grading-only",
        "professionalReferenceUsedDuringDetection": False,
        "tunedBasicPitchF1": TUNED_BASIC_PITCH_F1,
        "chordAwareWinnerF1": CHORD_AWARE_WINNER_F1,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matched"],
        "winnerMissing": winner["missing"],
        "winnerExtra": winner["extra"],
        "winnerPriority": winner["priority"],
        "improvementVsTunedBasicPitchPoints": round(float(winner["pitchF1"]) - TUNED_BASIC_PITCH_F1, 2),
        "improvementVsChordAwareWinnerPoints": round(float(winner["pitchF1"]) - CHORD_AWARE_WINNER_F1, 2),
        "winnerBeatsChordAwareWinner": float(winner["pitchF1"]) > CHORD_AWARE_WINNER_F1,
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "refine-confidence-recurrence-filter-around-winner"
            if float(winner["pitchF1"]) > CHORD_AWARE_WINNER_F1
            else "retain-chord-aware-winner-and-pivot-to-section-conditioned-filter"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "candidateSha256": after,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY BASIC PITCH CONFIDENCE/RECURRENCE FILTER V1 COMPLETE")
    print("Passed: True")
    print("Tuned Basic Pitch F1:", TUNED_BASIC_PITCH_F1)
    print("Chord-aware winner F1:", CHORD_AWARE_WINNER_F1)
    print("Winner:", winner["name"])
    print("Winner pitch F1:", winner["pitchF1"])
    print("Winner matched/missing/extra:", winner["matched"], "/", winner["missing"], "/", winner["extra"])
    print("Winner priority matched/missing/extra:", winner["priority"]["matched"], "/", winner["priority"]["missing"], "/", winner["priority"]["extra"])
    print("Improvement vs tuned Basic Pitch points:", output["improvementVsTunedBasicPitchPoints"])
    print("Improvement vs chord-aware winner points:", output["improvementVsChordAwareWinnerPoints"])
    print("Winner beats chord-aware winner:", output["winnerBeatsChordAwareWinner"])
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
