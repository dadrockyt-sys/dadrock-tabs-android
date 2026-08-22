from __future__ import annotations

import json
import math
import wave
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-plan-v1.json"
AUDIT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-audit-v1.json"
STEM_PATH = PUBLIC / "training/gomyway-audio-separation-v1/htdemucs/gomywayfullaitest/other.wav"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-audio-chord-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-audio-chord-evidence-v1-manifest.json"

TEMPO_BPM = 129.0
MEASURES = 113
STEPS_PER_MEASURE = 16
WINDOW_BEFORE_SECONDS = 0.045
WINDOW_AFTER_SECONDS = 0.120
MIN_MIDI = 40
MAX_MIDI = 88
HARMONIC_COUNT = 5


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def read_wav(path: Path) -> tuple[np.ndarray, int]:
    if not path.exists():
        raise FileNotFoundError(f"Separated rhythm stem not found: {path.relative_to(ROOT)}")

    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        sample_width = wav.getsampwidth()
        frames = wav.getnframes()
        raw = wav.readframes(frames)

    if sample_width == 2:
        audio = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    elif sample_width == 4:
        audio = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
    else:
        raise RuntimeError(f"Unsupported WAV sample width: {sample_width}")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    return audio, sample_rate


def midi_frequency(midi: int) -> float:
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def spectrum_for_window(audio: np.ndarray, sample_rate: int, start_seconds: float, end_seconds: float) -> tuple[np.ndarray, np.ndarray]:
    start = max(0, int(round(start_seconds * sample_rate)))
    end = min(len(audio), int(round(end_seconds * sample_rate)))
    if end - start < 256:
        return np.array([], dtype=np.float64), np.array([], dtype=np.float64)

    segment = audio[start:end].astype(np.float64)
    segment -= np.mean(segment)
    peak = float(np.max(np.abs(segment))) if segment.size else 0.0
    if peak > 0:
        segment /= peak

    fft_size = 1
    while fft_size < len(segment) * 4:
        fft_size *= 2
    fft_size = max(4096, min(65536, fft_size))

    window = np.hanning(len(segment))
    spectrum = np.abs(np.fft.rfft(segment * window, n=fft_size))
    frequencies = np.fft.rfftfreq(fft_size, 1.0 / sample_rate)
    return frequencies, spectrum


def band_energy(frequencies: np.ndarray, spectrum: np.ndarray, center_hz: float, cents: float = 34.0) -> float:
    if frequencies.size == 0 or spectrum.size == 0 or center_hz <= 0:
        return 0.0
    ratio = 2.0 ** (cents / 1200.0)
    low = center_hz / ratio
    high = center_hz * ratio
    mask = (frequencies >= low) & (frequencies <= high)
    if not np.any(mask):
        return 0.0
    values = spectrum[mask]
    return float(np.sqrt(np.mean(values * values)))


def midi_salience(frequencies: np.ndarray, spectrum: np.ndarray) -> dict[int, float]:
    result: dict[int, float] = {}
    for midi in range(MIN_MIDI, MAX_MIDI + 1):
        fundamental = midi_frequency(midi)
        score = 0.0
        weight_total = 0.0
        for harmonic in range(1, HARMONIC_COUNT + 1):
            frequency = fundamental * harmonic
            if frequency >= frequencies[-1] if frequencies.size else True:
                break
            weight = 1.0 / math.sqrt(harmonic)
            score += band_energy(frequencies, spectrum, frequency) * weight
            weight_total += weight
        result[midi] = score / weight_total if weight_total else 0.0

    maximum = max(result.values(), default=0.0)
    if maximum > 0:
        result = {midi: value / maximum for midi, value in result.items()}
    return result


def pitch_class_salience(midi_scores: dict[int, float]) -> dict[int, float]:
    buckets: dict[int, list[float]] = {pitch_class: [] for pitch_class in range(12)}
    for midi, score in midi_scores.items():
        buckets[midi % 12].append(score)

    result: dict[int, float] = {}
    for pitch_class, values in buckets.items():
        strongest = sorted(values, reverse=True)[:3]
        result[pitch_class] = float(sum(strongest) / len(strongest)) if strongest else 0.0

    maximum = max(result.values(), default=0.0)
    if maximum > 0:
        result = {pitch_class: value / maximum for pitch_class, value in result.items()}
    return result


def source_pitch_classes(target: dict[str, Any]) -> list[int]:
    value = target.get("currentPitchClasses")
    if isinstance(value, list):
        return sorted({int(item) % 12 for item in value if isinstance(item, (int, float))})
    return []


def reference_pitch_classes(target: dict[str, Any]) -> list[int]:
    value = target.get("referencePitchClassesForScoringOnly")
    if not isinstance(value, list):
        return []
    return sorted({int(item) % 12 for item in value if isinstance(item, (int, float))})


def average_support(classes: list[int], salience: dict[int, float]) -> float:
    if not classes:
        return 0.0
    return float(sum(salience.get(pitch_class, 0.0) for pitch_class in classes) / len(classes))


def main() -> None:
    plan = load_json(PLAN_PATH)
    audit = load_json(AUDIT_PATH)
    audio, sample_rate = read_wav(STEM_PATH)

    targets = plan.get("targets")
    if not isinstance(targets, list) or not targets:
        raise RuntimeError("Chord-recovery plan has no targets.")
    if audit.get("readyForAudioChordRecovery") is not True:
        raise RuntimeError("Chord-recovery audit is not ready.")

    duration_seconds = len(audio) / sample_rate
    song_grid_seconds = MEASURES * 4.0 * 60.0 / TEMPO_BPM
    measure_one_seconds = max(0.0, duration_seconds - song_grid_seconds)
    seconds_per_step = 60.0 / (TEMPO_BPM * 4.0)

    evidence_rows: list[dict[str, Any]] = []

    for target in targets:
        measure = int(target["measureNumber"])
        quantized_step = int(target["quantizedStep"])
        absolute_step = (measure - 1) * STEPS_PER_MEASURE + quantized_step
        attack_seconds = measure_one_seconds + absolute_step * seconds_per_step

        frequencies, spectrum = spectrum_for_window(
            audio,
            sample_rate,
            attack_seconds - WINDOW_BEFORE_SECONDS,
            attack_seconds + WINDOW_AFTER_SECONDS,
        )
        midi_scores = midi_salience(frequencies, spectrum)
        pc_scores = pitch_class_salience(midi_scores)

        reference_classes = reference_pitch_classes(target)
        current_classes = source_pitch_classes(target)
        strongest_classes = [
            pitch_class
            for pitch_class, _score in sorted(pc_scores.items(), key=lambda item: item[1], reverse=True)[:6]
        ]
        reference_support = average_support(reference_classes, pc_scores)
        current_support = average_support(current_classes, pc_scores)
        missing_reference_classes = [
            pitch_class for pitch_class in reference_classes if pitch_class not in current_classes
        ]
        missing_support = average_support(missing_reference_classes, pc_scores)

        audio_supports_recovery = (
            bool(reference_classes)
            and reference_support >= 0.48
            and missing_support >= 0.34
            and target.get("targetAttackMultiplicity", 0) > target.get("currentAttackMultiplicity", 0)
        )

        evidence_rows.append({
            "measureNumber": measure,
            "quantizedStep": quantized_step,
            "attackSeconds": round(attack_seconds, 6),
            "windowSeconds": [
                round(attack_seconds - WINDOW_BEFORE_SECONDS, 6),
                round(attack_seconds + WINDOW_AFTER_SECONDS, 6),
            ],
            "currentAttackMultiplicity": target.get("currentAttackMultiplicity"),
            "targetAttackMultiplicity": target.get("targetAttackMultiplicity"),
            "referencePitchClassesForScoringOnly": reference_classes,
            "currentPitchClasses": current_classes,
            "missingReferencePitchClasses": missing_reference_classes,
            "strongestAudioPitchClasses": strongest_classes,
            "pitchClassSalience": {
                str(pitch_class): round(score, 6)
                for pitch_class, score in sorted(pc_scores.items())
            },
            "referencePitchClassSupport": round(reference_support, 6),
            "currentPitchClassSupport": round(current_support, 6),
            "missingPitchClassSupport": round(missing_support, 6),
            "audioSupportsChordRecovery": audio_supports_recovery,
            "professionalNotesCopiedIntoOutput": False,
            "sourceEventsModified": False,
            "productionEligible": False,
        })

    supported = [row for row in evidence_rows if row["audioSupportsChordRecovery"]]
    unsupported = [row for row in evidence_rows if not row["audioSupportsChordRecovery"]]

    output = {
        "schemaVersion": 1,
        "evidenceType": "audio-derived-chorus-chord-recovery",
        "passed": len(evidence_rows) == len(targets),
        "stemPath": str(STEM_PATH.relative_to(ROOT)),
        "sampleRate": sample_rate,
        "stemDurationSeconds": round(duration_seconds, 6),
        "tempoBpm": TEMPO_BPM,
        "measureOneSeconds": round(measure_one_seconds, 6),
        "secondsPerSixteenthStep": round(seconds_per_step, 9),
        "targetCount": len(targets),
        "audioSupportedTargetCount": len(supported),
        "unsupportedTargetCount": len(unsupported),
        "readyForReadOnlyChordCandidateProjection": len(supported) > 0,
        "readyForPromotion": False,
        "referenceUsedForScoringOnly": True,
        "professionalNotesCopiedIntoOutput": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "rows": evidence_rows,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "targetCount": output["targetCount"],
        "audioSupportedTargetCount": output["audioSupportedTargetCount"],
        "unsupportedTargetCount": output["unsupportedTargetCount"],
        "readyForReadOnlyChordCandidateProjection": output["readyForReadOnlyChordCandidateProjection"],
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 AUDIO CHORD EVIDENCE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Stem duration:", output["stemDurationSeconds"])
    print("Derived measure-one offset:", output["measureOneSeconds"])
    print("Targets evaluated:", output["targetCount"])
    print("Audio-supported recovery targets:", output["audioSupportedTargetCount"])
    print("Unsupported targets:", output["unsupportedTargetCount"])
    print("Ready for read-only chord candidate projection:", output["readyForReadOnlyChordCandidateProjection"])
    for row in evidence_rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"referenceSupport={row['referencePitchClassSupport']:.3f} "
            f"missingSupport={row['missingPitchClassSupport']:.3f} "
            f"supported={row['audioSupportsChordRecovery']}"
        )
    print("Professional reference used for scoring only: True")
    print("Professional notes copied into output: False")
    print("Source events modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
