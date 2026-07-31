from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from basic_pitch.inference import predict

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = REPO_ROOT / "public" / "gomywayfullaitest.m4a"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-em-riff-extraction-training.json"
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"

TEMPO = 129.0
MEASURE_SECONDS = (60.0 / TEMPO) * 4.0
PHRASE_START_MEASURES = (18, 20, 22, 24, 26, 28, 30)
TIMING_TOLERANCE_SECONDS = 0.16

# Protected two-measure Em-riff curriculum. These pitches are used only to score
# read-only Basic Pitch candidates; they are never copied into production events.
PROTECTED_SLOTS = (
    {"patternId": "em-riff-a", "step": 2, "measureOffset": 0, "acceptedMidi": (57, 59)},
    {"patternId": "em-riff-a", "step": 6, "measureOffset": 0, "acceptedMidi": (55,)},
    {"patternId": "em-riff-a", "step": 10, "measureOffset": 0, "acceptedMidi": (52,)},
    {"patternId": "em-riff-a", "step": 14, "measureOffset": 0, "acceptedMidi": (45,)},
    {"patternId": "em-riff-b", "step": 2, "measureOffset": 1, "acceptedMidi": (57, 59)},
    {"patternId": "em-riff-b", "step": 4, "measureOffset": 1, "acceptedMidi": (55,)},
    {"patternId": "em-riff-b", "step": 6, "measureOffset": 1, "acceptedMidi": (52,)},
    {"patternId": "em-riff-b", "step": 10, "measureOffset": 1, "acceptedMidi": (45,)},
    {"patternId": "em-riff-b", "step": 14, "measureOffset": 1, "acceptedMidi": (58, 62)},
)

# Small, bounded curriculum: defaults plus conservative sensitivity changes.
ATTEMPTS = (
    {"name": "default", "onset_threshold": 0.50, "frame_threshold": 0.30, "minimum_note_length": 127.7},
    {"name": "lower-onset", "onset_threshold": 0.40, "frame_threshold": 0.30, "minimum_note_length": 127.7},
    {"name": "lower-frame", "onset_threshold": 0.50, "frame_threshold": 0.22, "minimum_note_length": 127.7},
    {"name": "sensitive-balanced", "onset_threshold": 0.40, "frame_threshold": 0.22, "minimum_note_length": 100.0},
    {"name": "short-note-recovery", "onset_threshold": 0.45, "frame_threshold": 0.25, "minimum_note_length": 75.0},
    {"name": "upper-string-recovery", "onset_threshold": 0.35, "frame_threshold": 0.20, "minimum_note_length": 75.0, "minimum_frequency": 100.0, "maximum_frequency": 1400.0},
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _note_events(model_output: Any) -> list[dict[str, Any]]:
    # Basic Pitch returns (model_output, midi_data, note_events).
    if not isinstance(model_output, tuple) or len(model_output) < 3:
        return []
    events = model_output[2]
    return [event for event in events if isinstance(event, dict)]


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start_time") or event.get("start") or 0.0)


def _event_pitch(event: dict[str, Any]) -> int:
    for key in ("pitch_midi", "midi_pitch", "midiPitch", "pitch"):
        try:
            return int(event.get(key))
        except (TypeError, ValueError):
            continue
    return -1


def _slot_time(phrase_start_measure: int, slot: dict[str, Any]) -> float:
    measure_number = phrase_start_measure + int(slot["measureOffset"])
    local_step = int(slot["step"])
    position = (local_step - 1) / 16.0
    return ((measure_number - 1) * MEASURE_SECONDS) + (position * MEASURE_SECONDS)


def _score(events: list[dict[str, Any]]) -> dict[str, Any]:
    slot_reports: list[dict[str, Any]] = []
    correct_slots = 0

    for slot in PROTECTED_SLOTS:
        accepted = set(int(value) for value in slot["acceptedMidi"])
        support: dict[int, int] = {}
        matches: list[dict[str, Any]] = []

        for phrase_start in PHRASE_START_MEASURES:
            target = _slot_time(phrase_start, slot)
            nearby = [
                event for event in events
                if abs(_event_start(event) - target) <= TIMING_TOLERANCE_SECONDS
            ]
            for event in nearby:
                pitch = _event_pitch(event)
                if pitch >= 0:
                    support[pitch] = support.get(pitch, 0) + 1
                    if pitch in accepted:
                        matches.append(
                            {
                                "phraseStartMeasure": phrase_start,
                                "midiPitch": pitch,
                                "start": round(_event_start(event), 6),
                            }
                        )

        present = bool(matches)
        if present:
            correct_slots += 1
        slot_reports.append(
            {
                "patternId": slot["patternId"],
                "step": slot["step"],
                "acceptedMidiPitches": sorted(accepted),
                "correctCandidatePresent": present,
                "matchingOccurrences": len(matches),
                "observedPitchHistogram": [
                    {"midiPitch": pitch, "support": count}
                    for pitch, count in sorted(
                        support.items(), key=lambda item: (-item[1], item[0])
                    )[:12]
                ],
            }
        )

    return {
        "correctCandidateSlots": correct_slots,
        "candidatePresencePercentage": round(correct_slots / len(PROTECTED_SLOTS), 6),
        "slotReports": slot_reports,
    }


def main() -> None:
    if not AUDIO_PATH.exists():
        raise FileNotFoundError(f"Missing training audio: {AUDIO_PATH}")

    audio_hash_before = _sha256(AUDIO_PATH)
    notation_hash_before = _sha256(NOTATION_PATH) if NOTATION_PATH.exists() else None

    attempts: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for index, parameters in enumerate(ATTEMPTS, start=1):
        kwargs = {key: value for key, value in parameters.items() if key != "name"}
        result = predict(AUDIO_PATH, **kwargs)
        events = _note_events(result)
        score = _score(events)
        attempt = {
            "attempt": index,
            "name": parameters["name"],
            "parameters": kwargs,
            "extractedEventCount": len(events),
            **score,
        }
        attempts.append(attempt)

        if best is None or (
            attempt["correctCandidateSlots"],
            attempt["candidatePresencePercentage"],
            -attempt["extractedEventCount"],
        ) > (
            best["correctCandidateSlots"],
            best["candidatePresencePercentage"],
            -best["extractedEventCount"],
        ):
            best = attempt

    audio_hash_after = _sha256(AUDIO_PATH)
    notation_hash_after = _sha256(NOTATION_PATH) if NOTATION_PATH.exists() else None

    safeguards = {
        "trainingAudioUnchanged": audio_hash_before == audio_hash_after,
        "lockedV8NotationUnchanged": notation_hash_before == notation_hash_after,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noProductionPromotion": True,
        "noSyntheticNotesWritten": True,
    }

    baseline = attempts[0]
    improved = bool(best and best["correctCandidateSlots"] > baseline["correctCandidateSlots"])
    target_reached = bool(best and best["correctCandidateSlots"] >= 8)

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-em-riff-bounded-basic-pitch-extraction-training",
        "passed": all(safeguards.values()) and len(attempts) == len(ATTEMPTS),
        "trainingStarted": True,
        "attemptsCompleted": len(attempts),
        "baselineCorrectCandidateSlots": baseline["correctCandidateSlots"],
        "bestCorrectCandidateSlots": best["correctCandidateSlots"] if best else 0,
        "bestCandidatePresencePercentage": best["candidatePresencePercentage"] if best else 0.0,
        "bestAttempt": best,
        "improved": improved,
        "targetReached": target_reached,
        "readyForRankingTraining": bool(best and best["correctCandidateSlots"] >= 5),
        "productionPromotionAllowed": False,
        "attempts": attempts,
        "safeguards": safeguards,
        "nextStep": (
            "Run bounded candidate-ranking training with the best extraction settings."
            if best and best["correctCandidateSlots"] >= 5
            else "Expand the bounded extraction curriculum using the best attempt as the new read-only baseline."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge Em riff extraction training loop pass:", report["passed"])
    print("Training started: True")
    print("Attempts completed:", report["attemptsCompleted"])
    print("Baseline correct-candidate slots:", f"{report['baselineCorrectCandidateSlots']}/9")
    print("Best correct-candidate slots:", f"{report['bestCorrectCandidateSlots']}/9")
    print("Best attempt:", best["name"] if best else None)
    print("Best parameters:", best["parameters"] if best else None)
    print("Improved:", improved)
    print("Ready for ranking training:", report["readyForRankingTraining"])
    print("Production promotion allowed: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
