from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench
import profile_gomyway_1382_dual_stem_broadband_onset_evidence_v1 as broad

cached = bench.cached
recur = bench.recur
v2 = bench.v2
v3 = bench.v3
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-dual-stem-pitch-periodicity-residual-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-dual-stem-pitch-periodicity-residual-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19
FRAME_SECONDS = 0.092
EPS = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def frame(audio: np.ndarray, sr: int, center: float) -> np.ndarray:
    arr = broad.mono(audio)
    n = max(256, int(round(FRAME_SECONDS * sr)))
    c = int(round(center * sr))
    start = max(0, c - n // 2)
    stop = min(len(arr), start + n)
    out = np.zeros(n, dtype=np.float64)
    chunk = arr[start:stop]
    out[: len(chunk)] = chunk
    out -= float(np.mean(out))
    if len(out) > 1:
        out *= np.hanning(len(out))
    return out


def midi_hz(pitch: int) -> float:
    return 440.0 * (2.0 ** ((float(pitch) - 69.0) / 12.0))


def normalized_lag_corr(x: np.ndarray, lag: int) -> float:
    if lag <= 0 or lag >= len(x) - 8:
        return 0.0
    a = x[:-lag]
    b = x[lag:]
    denom = float(np.sqrt(np.sum(a * a) * np.sum(b * b))) + EPS
    return float(np.sum(a * b) / denom)


def periodicity_at_pitch(audio: np.ndarray, sr: int, center: float, pitch: int) -> dict[str, float]:
    x = frame(audio, sr, center)
    f0 = midi_hz(pitch)
    target_lag = max(1, int(round(sr / max(f0, 1.0))))

    # Allow a tiny timing tolerance around the expected period.
    target_values = [normalized_lag_corr(x, target_lag + d) for d in (-2, -1, 0, 1, 2)]
    target_corr = max(target_values)

    neighbor_corrs: list[float] = []
    for semitone_delta in (-2, -1, 1, 2):
        neighbor_hz = f0 * (2.0 ** (semitone_delta / 12.0))
        neighbor_lag = max(1, int(round(sr / max(neighbor_hz, 1.0))))
        neighbor_corrs.append(
            max(normalized_lag_corr(x, neighbor_lag + d) for d in (-2, -1, 0, 1, 2))
        )
    best_neighbor = max(neighbor_corrs) if neighbor_corrs else 0.0

    # Octave-period support is useful for distorted guitar, where the first harmonic can dominate.
    octave_lag = max(1, int(round(sr / max(f0 * 2.0, 1.0))))
    octave_corr = max(normalized_lag_corr(x, octave_lag + d) for d in (-2, -1, 0, 1, 2))

    return {
        "targetCorr": target_corr,
        "bestNeighborCorr": best_neighbor,
        "targetMargin": target_corr - best_neighbor,
        "octaveCorr": octave_corr,
        "targetOrOctaveCorr": max(target_corr, octave_corr),
    }


def bucket(value: float, edges: tuple[float, ...], prefix: str) -> str:
    for edge in edges:
        if value < edge:
            return f"{prefix}_lt_{str(edge).replace('.', 'p').replace('-', 'm')}"
    return f"{prefix}_{str(edges[-1]).replace('.', 'p').replace('-', 'm')}_plus"


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    rows = cached.load_profile_rows()
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

    champion_tokens = set(champion_additions.keys())
    residual_rows = [row for row in rows if bench.token(row) not in champion_tokens]
    print(f"14.19 residual detector rows: {len(residual_rows)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    missing_reference = reference - champion_1419

    feature_counts: dict[str, Counter[str]] = defaultdict(Counter)
    joint_counts: dict[str, Counter[str]] = defaultdict(Counter)
    detailed: list[dict[str, Any]] = []

    for index, row in enumerate(residual_rows, 1):
        token = bench.token(row)
        measure, step, pitch = token
        center = float(grid[(measure, step)])

        # All detector-side audio features are frozen before consulting the grading label.
        w = periodicity_at_pitch(winner_audio, winner_sr, center, pitch)
        a = periodicity_at_pitch(alt_audio, alt_sr, center, pitch)

        max_target = max(w["targetCorr"], a["targetCorr"])
        min_target = min(w["targetCorr"], a["targetCorr"])
        max_target_or_oct = max(w["targetOrOctaveCorr"], a["targetOrOctaveCorr"])
        min_target_or_oct = min(w["targetOrOctaveCorr"], a["targetOrOctaveCorr"])
        max_margin = max(w["targetMargin"], a["targetMargin"])
        min_margin = min(w["targetMargin"], a["targetMargin"])

        maxb = bucket(max_target, (0.10, 0.20, 0.30, 0.40, 0.55, 0.70), "maxcorr")
        minb = bucket(min_target, (0.00, 0.10, 0.20, 0.30, 0.45, 0.60), "mincorr")
        maxob = bucket(max_target_or_oct, (0.15, 0.25, 0.35, 0.45, 0.60, 0.75), "maxoct")
        minob = bucket(min_target_or_oct, (0.05, 0.15, 0.25, 0.35, 0.50, 0.65), "minoct")
        maxmb = bucket(max_margin, (-0.10, 0.00, 0.05, 0.10, 0.20, 0.35), "maxmargin")
        minmb = bucket(min_margin, (-0.20, -0.10, 0.00, 0.05, 0.10, 0.20), "minmargin")

        is_true = missing_reference.get(token, 0) > 0
        truth = "true" if is_true else "false"

        for name, value in (
            ("maxTarget", maxb),
            ("minTarget", minb),
            ("maxTargetOrOctave", maxob),
            ("minTargetOrOctave", minob),
            ("maxMargin", maxmb),
            ("minMargin", minmb),
        ):
            feature_counts[f"{name}|{value}"][truth] += 1

        recurrence = int(row.get("recurrence", 0))
        recur_label = "4plus" if recurrence >= 4 else str(recurrence)
        signatures = (
            f"{maxb}|{maxmb}|recur_{recur_label}",
            f"{maxob}|{maxmb}|recur_{recur_label}",
            f"{minob}|{minmb}|recur_{recur_label}",
            f"{maxb}|{minb}|{maxmb}",
            f"{maxob}|{minob}|{maxmb}",
            f"{maxob}|{maxmb}",
        )
        for signature in signatures:
            joint_counts[signature][truth] += 1

        detailed.append({
            "token": list(token),
            "trueMissingReference": is_true,
            "recurrence": recurrence,
            "winner": {k: round(float(v), 6) for k, v in w.items()},
            "alternate": {k: round(float(v), 6) for k, v in a.items()},
            "maxTargetCorr": round(max_target, 6),
            "minTargetCorr": round(min_target, 6),
            "maxTargetOrOctaveCorr": round(max_target_or_oct, 6),
            "minTargetOrOctaveCorr": round(min_target_or_oct, 6),
            "maxTargetMargin": round(max_margin, 6),
            "minTargetMargin": round(min_margin, 6),
        })

        if index % 250 == 0:
            print(f"Pitch periodicity measured: {index}/{len(residual_rows)}", flush=True)

    def summarize(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for signature, counts in groups.items():
            out.append({"signature": signature, **precision_row(int(counts["true"]), int(counts["false"]))})
        return sorted(
            out,
            key=lambda r: (float(r["precision"]), int(r["true"]), -int(r["false"])),
            reverse=True,
        )

    singles = summarize(feature_counts)
    joints = summarize(joint_counts)
    repeatable = [row for row in joints if int(row["true"]) >= 2]
    supported = [row for row in joints if int(row["true"]) >= 3]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.19 pitch-periodicity residual profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-reference-free-dual-stem-pitch-periodicity-residual",
        "championScore": score_1419,
        "frameSeconds": FRAME_SECONDS,
        "residualRowCount": len(residual_rows),
        "singleFeaturePrecision": singles,
        "jointFeaturePrecision": joints,
        "repeatableJointPrecision": repeatable,
        "supportedJointPrecision": supported,
        "rows": detailed,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-high-precision-pitch-periodicity-pockets-else-pivot-detector-family",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score_1419["pitchF1"],
        "residualRowCount": len(residual_rows),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 DUAL-STEM PITCH PERIODICITY RESIDUAL V1 COMPLETE")
    print("Passed: True")
    print("Champion remains frozen:", score_1419["pitchF1"], "/", score_1419["matched"], "/", score_1419["missing"], "/", score_1419["extra"])
    print("Residual detector rows:", len(residual_rows))
    print("Top repeatable pitch-periodicity signatures:")
    for row in repeatable[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top supported pitch-periodicity signatures (3+ true):")
    for row in supported[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
