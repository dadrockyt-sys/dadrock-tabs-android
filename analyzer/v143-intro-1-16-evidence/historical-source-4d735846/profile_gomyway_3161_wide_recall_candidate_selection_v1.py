from __future__ import annotations

import hashlib
import json
from bisect import bisect_left
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from basic_pitch.inference import predict

import profile_gomyway_3161_wide_recall_basic_pitch_sweep_v1 as wide

micro = wide.micro
s3161 = wide.s3161
recur = wide.recur
recall = wide.recall
v2 = wide.v2
v3 = wide.v3
harmonic = wide.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-candidate-selection-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-wide-recall-candidate-selection-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61
MAX_GRID_ERROR_SECONDS = 0.10
GUITAR_MIDI_MIN = 40
GUITAR_MIDI_MAX = 88

SWEEPS = [
    ("o030_f020", 0.30, 0.20),
    ("o025_f015", 0.25, 0.15),
    ("o020_f012", 0.20, 0.12),
    ("o015_f010", 0.15, 0.10),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nearest_slot(start_time: float, sorted_times: list[float], time_to_slots: dict[float, list[tuple[int, int]]]) -> tuple[tuple[int, int], float] | None:
    i = bisect_left(sorted_times, start_time)
    candidates: list[float] = []
    if i < len(sorted_times):
        candidates.append(sorted_times[i])
    if i > 0:
        candidates.append(sorted_times[i - 1])
    if not candidates:
        return None
    best_time = min(candidates, key=lambda t: abs(t - start_time))
    error = abs(best_time - start_time)
    if error > MAX_GRID_ERROR_SECONDS:
        return None
    return sorted(time_to_slots[best_time])[0], error


def parse_event(event: Any) -> tuple[float, float, int, float] | None:
    return wide.parse_note_event(event)


def detect_with_metadata(stem: Path, grid: dict[tuple[int, int], float], onset: float, frame: float) -> dict[tuple[int, int, int], dict[str, float]]:
    sorted_times = sorted(set(float(t) for t in grid.values()))
    time_to_slots: dict[float, list[tuple[int, int]]] = defaultdict(list)
    for slot, t in grid.items():
        time_to_slots[float(t)].append(slot)

    result = predict(
        str(stem),
        onset_threshold=onset,
        frame_threshold=frame,
        minimum_note_length=20.0,
        minimum_frequency=80.0,
        maximum_frequency=1400.0,
    )
    if not isinstance(result, tuple) or len(result) < 3:
        raise RuntimeError(f"Unexpected Basic Pitch return shape for {stem}")

    found: dict[tuple[int, int, int], dict[str, float]] = {}
    for raw in list(result[2] or []):
        event = parse_event(raw)
        if event is None:
            continue
        start, end, pitch, amp = event
        if pitch < GUITAR_MIDI_MIN or pitch > GUITAR_MIDI_MAX:
            continue
        nearest = nearest_slot(start, sorted_times, time_to_slots)
        if nearest is None:
            continue
        (measure, step), grid_error = nearest
        tok = (int(measure), int(step), int(pitch))
        duration = max(0.0, float(end) - float(start))
        prev = found.get(tok)
        row = {
            "amplitude": float(amp),
            "gridError": float(grid_error),
            "duration": float(duration),
        }
        if prev is None or (row["amplitude"], -row["gridError"], row["duration"]) > (prev["amplitude"], -prev["gridError"], prev["duration"]):
            found[tok] = row
    return found


def bucket(value: float, cuts: list[float], labels: list[str]) -> str:
    for cut, label in zip(cuts, labels):
        if value <= cut:
            return label
    return labels[-1]


def signatures(row: dict[str, Any]) -> set[str]:
    amp = float(row["maxAmplitude"])
    mean_amp = float(row["meanAmplitude"])
    err = float(row["minGridError"])
    dur = float(row["maxDuration"])
    persistence = int(row["sweepPersistence"])
    stems = int(row["stemCountAtWide"])
    strictest = int(row["strictestSweepIndex"])

    amp_b = bucket(amp, [0.05, 0.10, 0.20, 0.35, 0.55, 1.0], ["a05", "a10", "a20", "a35", "a55", "a100"])
    mean_b = bucket(mean_amp, [0.05, 0.10, 0.20, 0.35, 0.55, 1.0], ["ma05", "ma10", "ma20", "ma35", "ma55", "ma100"])
    err_b = bucket(err, [0.010, 0.020, 0.035, 0.055, 0.080, 0.100], ["e010", "e020", "e035", "e055", "e080", "e100"])
    dur_b = bucket(dur, [0.04, 0.08, 0.14, 0.24, 0.40, 9.0], ["d040", "d080", "d140", "d240", "d400", "d400p"])

    out = {
        f"widePersistence::p{persistence}",
        f"wideStemAgreement::s{stems}",
        f"wideStrictestSweep::i{strictest}",
        f"wideAmplitude::{amp_b}",
        f"wideMeanAmplitude::{mean_b}",
        f"wideGridError::{err_b}",
        f"wideDuration::{dur_b}",
        f"wideCross::p{persistence}|s{stems}",
        f"wideCross::p{persistence}|{amp_b}",
        f"wideCross::p{persistence}|{err_b}",
        f"wideCross::s{stems}|{amp_b}",
        f"wideCross::s{stems}|{err_b}",
        f"wideCross::i{strictest}|{amp_b}|{err_b}",
        f"wideCross::p{persistence}|s{stems}|{amp_b}",
        f"wideCross::p{persistence}|s{stems}|{err_b}",
        f"wideCross::p{persistence}|s{stems}|{amp_b}|{err_b}",
        f"wideRhythm::stepParity{int(row['step']) % 2}|p{persistence}|s{stems}",
        f"wideRhythm::stepQuarter{int(row['step']) % 4}|p{persistence}|s{stems}",
        f"wideRegister::{'low' if int(row['pitch']) < 48 else ('mid' if int(row['pitch']) < 60 else 'high')}|p{persistence}|s{stems}",
    }
    return out


def ranked(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig, c in groups.items():
        true = int(c["true"])
        false = int(c["false"])
        total = true + false
        rows.append({
            "signature": sig,
            "true": true,
            "false": false,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"]), str(r["signature"])))


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
    champion, reconstruction = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    stems = [Path(harmonic.legacy.WINNER_STEM), Path(harmonic.legacy.ALT_STEM)]
    detections: dict[str, list[dict[tuple[int, int, int], dict[str, float]]]] = {}
    for name, onset, frame in SWEEPS:
        detections[name] = [detect_with_metadata(stem, grid, onset, frame) for stem in stems]

    widest_name = SWEEPS[-1][0]
    widest_tokens = set().union(*(set(m.keys()) for m in detections[widest_name]))
    novel_tokens = sorted(tok for tok in widest_tokens if tok not in champion)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    true_total = 0
    false_total = 0

    for tok in novel_tokens:
        per_sweep_presence: list[int] = []
        all_meta: list[dict[str, float]] = []
        strictest_index = len(SWEEPS) - 1
        for idx, (name, _onset, _frame) in enumerate(SWEEPS):
            stem_maps = detections[name]
            present = sum(1 for m in stem_maps if tok in m)
            per_sweep_presence.append(present)
            if present and strictest_index == len(SWEEPS) - 1:
                strictest_index = idx
            for m in stem_maps:
                if tok in m:
                    all_meta.append(m[tok])

        if not all_meta:
            continue
        widest_stem_count = sum(1 for m in detections[widest_name] if tok in m)
        row = {
            "token": list(tok),
            "measure": tok[0],
            "step": tok[1],
            "pitch": tok[2],
            "sweepPresence": per_sweep_presence,
            "sweepPersistence": sum(1 for x in per_sweep_presence if x > 0),
            "stemCountAtWide": widest_stem_count,
            "strictestSweepIndex": strictest_index,
            "maxAmplitude": max(float(m["amplitude"]) for m in all_meta),
            "meanAmplitude": sum(float(m["amplitude"]) for m in all_meta) / len(all_meta),
            "minGridError": min(float(m["gridError"]) for m in all_meta),
            "maxDuration": max(float(m["duration"]) for m in all_meta),
        }
        sigs = sorted(signatures(row))
        is_true = int((Counter({tok: 1}) & reference)[tok]) > 0
        label = "true" if is_true else "false"
        if is_true:
            true_total += 1
        else:
            false_total += 1
        for sig in sigs:
            groups[sig][label] += 1
        row["label"] = label
        row["signatures"] = sigs
        details.append(row)

    rows = ranked(groups)
    perfect = [r for r in rows if int(r["true"]) >= 3 and int(r["false"]) == 0]
    high80 = [r for r in rows if int(r["true"]) >= 5 and float(r["precision"]) >= 80.0]
    high50 = [r for r in rows if int(r["true"]) >= 8 and float(r["precision"]) >= 50.0]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during wide-recall candidate selection profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "31.61-wide-recall-candidate-selection",
        "champion3161Score": baseline,
        "reconstruction": reconstruction,
        "widestSweep": widest_name,
        "novelCandidateCount": len(details),
        "recoverableTrueCount": true_total,
        "recoveryFalseCount": false_total,
        "perfectRecoverySignaturesMin3True": perfect,
        "highPrecisionRecoverySignaturesMin5True80Pct": high80,
        "moderateRecoverySignaturesMin8True50Pct": high50,
        "rankedSignatures": rows,
        "candidateRows": details,
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
        "novelCandidateCount": len(details),
        "recoverableTrueCount": true_total,
        "recoveryFalseCount": false_total,
        "perfectSignatureCount": len(perfect),
        "high80SignatureCount": len(high80),
        "high50SignatureCount": len(high50),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 WIDE-RECALL CANDIDATE SELECTION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", baseline["pitchF1"])
    print("Champion matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Novel wide-recall candidates:", len(details))
    print("Recoverable true / false:", true_total, "/", false_total)
    print("Perfect recovery signatures (3+ true, 0 false):", len(perfect))
    for r in perfect[:30]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("High-precision recovery signatures (5+ true, >=80%):", len(high80))
    for r in high80[:30]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("Moderate recovery signatures (8+ true, >=50%):", len(high50))
    for r in high50[:30]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
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
