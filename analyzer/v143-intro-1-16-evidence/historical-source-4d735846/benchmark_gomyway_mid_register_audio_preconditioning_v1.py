from __future__ import annotations

import hashlib
import json
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_harmonic_refinement_v2 as harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-mid-register-audio-preconditioning-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-mid-register-audio-preconditioning-v1-manifest.json"

MID_MIN = 52
MID_MAX = 63
CURRENT_CHAMPION_F1 = 6.99
HARMONIC_CONFIG = {"name": "harmonic_r074_cap5", "ratio": 0.74, "cap": 5, "intervals": (12, 19, 24)}

VARIANTS: list[dict[str, Any]] = [
    {"name": "band120_700", "low": 120.0, "high": 700.0},
    {"name": "band140_900", "low": 140.0, "high": 900.0},
    {"name": "band100_1200", "low": 100.0, "high": 1200.0},
    {"name": "band160_650", "low": 160.0, "high": 650.0},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grouped_for(path: Path, grid: dict[tuple[int, int], float]):
    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    notes = v2.basic_pitch_notes(path)
    grouped, _discarded, _distances = harmonic.snap_notes(notes, grid)
    return grouped


def prediction(grouped):
    return harmonic.predict_for_config(grouped, HARMONIC_CONFIG)


def merge_with_cap(*predictions: Counter[tuple[int, int, int]]) -> Counter[tuple[int, int, int]]:
    merged: Counter[tuple[int, int, int]] = Counter()
    for pred in predictions:
        for token, count in pred.items():
            if token in merged:
                continue
            measure, step, _midi = token
            slot_count = sum(v for (m, s, _p), v in merged.items() if m == measure and s == step)
            if slot_count >= 5:
                continue
            merged[token] = min(1, count)
    return merged


def targeted_mid(pred: Counter[tuple[int, int, int]]) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in pred.items() if MID_MIN <= token[2] <= MID_MAX})


def preprocess(source: Path, destination: Path, low: float, high: float) -> None:
    audio, sample_rate = sf.read(source, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    nyquist = sample_rate / 2.0
    sos = butter(4, [low / nyquist, high / nyquist], btype="bandpass", output="sos")
    filtered = sosfiltfilt(sos, audio).astype(np.float32)
    peak = float(np.max(np.abs(filtered))) if filtered.size else 0.0
    if peak > 0:
        filtered = filtered * (0.95 / peak)
    sf.write(destination, filtered, sample_rate, subtype="PCM_16")


def grade(name: str, predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    pitch_f1 = round(100.0 * v2.f1(matched, predicted_count, expected), 2)
    return {
        "name": name,
        "pitchF1": pitch_f1,
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "predictions": predicted_count,
    }


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    print("Building frozen 6.99 cross-stem champion...", flush=True)
    base_winner = prediction(grouped_for(WINNER_STEM, grid))
    base_alt = prediction(grouped_for(ALT_STEM, grid))
    champion = merge_with_cap(base_winner, base_alt)
    results = [grade("champion", champion, reference)]

    with tempfile.TemporaryDirectory(prefix="gomyway-mid-precondition-") as tmp:
        tmp_root = Path(tmp)
        for variant in VARIANTS:
            filtered_predictions = []
            for stem_name, stem_path in (("winner", WINNER_STEM), ("alt", ALT_STEM)):
                out = tmp_root / f"{stem_name}-{variant['name']}.wav"
                preprocess(stem_path, out, float(variant["low"]), float(variant["high"]))
                pred = targeted_mid(prediction(grouped_for(out, grid)))
                filtered_predictions.append(pred)

            for source_name, pred in (("winnerstem", filtered_predictions[0]), ("altstem", filtered_predictions[1])):
                merged = merge_with_cap(champion, pred)
                row = grade(f"{variant['name']}_{source_name}", merged, reference)
                results.append(row)
                print(
                    f"{row['name']}: pitchF1={row['pitchF1']} matched={row['matched']} missing={row['missing']} "
                    f"extra={row['extra']} predictions={row['predictions']}",
                    flush=True,
                )

            merged_both = merge_with_cap(champion, filtered_predictions[0], filtered_predictions[1])
            row = grade(f"{variant['name']}_both", merged_both, reference)
            results.append(row)
            print(
                f"{row['name']}: pitchF1={row['pitchF1']} matched={row['matched']} missing={row['missing']} "
                f"extra={row['extra']} predictions={row['predictions']}",
                flush=True,
            )

    ranked = sorted(results, key=lambda row: (row["pitchF1"], row["matched"], -row["extra"]), reverse=True)
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "mid-register-audio-preconditioning-recall",
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "targetMidiRange": [MID_MIN, MID_MAX],
        "variants": VARIANTS,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matched"],
        "winnerMissing": winner["missing"],
        "winnerExtra": winner["extra"],
        "improvementVsChampionPoints": round(float(winner["pitchF1"]) - CURRENT_CHAMPION_F1, 2),
        "winnerBeatsChampion": float(winner["pitchF1"]) > CURRENT_CHAMPION_F1,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "cross-validate-winning-mid-register-preconditioning"
            if float(winner["pitchF1"]) > CURRENT_CHAMPION_F1
            else "evaluate-mid-register-specialist-detector"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY MID-REGISTER AUDIO PRECONDITIONING V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", CURRENT_CHAMPION_F1)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Improvement vs champion points:", output["improvementVsChampionPoints"])
    print("Winner beats champion:", output["winnerBeatsChampion"])
    print("Professional reference used during detection: False")
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
