from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1382_dual_stem_broadband_onset_evidence_v1 as onset

attack = onset.attack
recur = onset.recur
v2 = onset.v2
v3 = onset.v3
recall = onset.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-dual-stem-fundamental-overtone-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-dual-stem-fundamental-overtone-evidence-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82
EPS = 1e-9

RATIO_BUCKETS = [
    ("ratio_lt_050", float("-inf"), 0.50),
    ("ratio_050_100", 0.50, 1.00),
    ("ratio_100_200", 1.00, 2.00),
    ("ratio_200_400", 2.00, 4.00),
    ("ratio_400_plus", 4.00, float("inf")),
]

TEMPLATE_BUCKETS = [
    ("template_lt_075", float("-inf"), 0.75),
    ("template_075_100", 0.75, 1.00),
    ("template_100_150", 1.00, 1.50),
    ("template_150_250", 1.50, 2.50),
    ("template_250_plus", 2.50, float("inf")),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midi_hz(midi: int) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def spectral_amp(audio: np.ndarray, sr: int, center: float, midi: int) -> float:
    fr = onset.frame(audio, sr, center)
    spec = np.abs(np.fft.rfft(fr))
    freqs = np.fft.rfftfreq(len(fr), d=1.0 / float(sr))
    hz = midi_hz(midi)
    if hz <= 0.0 or hz >= freqs[-1]:
        return 0.0
    idx = int(np.argmin(np.abs(freqs - hz)))
    lo = max(0, idx - 1)
    hi = min(len(spec), idx + 2)
    return float(np.max(spec[lo:hi])) if hi > lo else 0.0


def harmonic_template(audio: np.ndarray, sr: int, center: float, midi: int) -> float:
    base = spectral_amp(audio, sr, center, midi)
    h2 = spectral_amp(audio, sr, center, midi + 12) if midi + 12 <= 96 else 0.0
    h3 = spectral_amp(audio, sr, center, midi + 19) if midi + 19 <= 96 else 0.0
    return float(base + 0.60 * h2 + 0.35 * h3)


def stem_features(audio: np.ndarray, sr: int, center: float, midi: int) -> dict[str, float]:
    target = spectral_amp(audio, sr, center, midi)
    subs = []
    for delta in (12, 19, 24):
        lower = midi - delta
        if lower >= 20:
            subs.append((lower, spectral_amp(audio, sr, center, lower)))
    max_sub = max((amp for _, amp in subs), default=0.0)
    target_ratio = target / max(max_sub, EPS)

    target_template = harmonic_template(audio, sr, center, midi)
    lower_templates = [harmonic_template(audio, sr, center, lower) for lower, _ in subs]
    max_lower_template = max(lower_templates, default=0.0)
    template_ratio = target_template / max(max_lower_template, EPS)

    return {
        "targetAmp": target,
        "maxSubharmonicAmp": max_sub,
        "targetVsSubharmonicRatio": target_ratio,
        "targetTemplate": target_template,
        "maxLowerTemplate": max_lower_template,
        "templateRatio": template_ratio,
    }


def bucket(value: float, bins) -> str:
    for name, lo, hi in bins:
        if lo <= value < hi:
            return name
    return bins[-1][0]


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
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
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen validated 13.82 champion and detector-side pool...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}"
        )

    pool, recurrence_counts = attack.candidate_pool(grid, winner_scores, alt_scores, champion)
    print(f"Fundamental/overtone candidate pool: {len(pool)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    # Detector pool and audio features are frozen before reference labels are consulted.
    feature_rows: list[dict[str, Any]] = []
    for index, token in enumerate(pool, 1):
        measure, step, pitch = token
        center = float(grid[(measure, step)])
        w = stem_features(winner_audio, winner_sr, center, pitch)
        a = stem_features(alt_audio, alt_sr, center, pitch)
        feature_rows.append({
            "token": [measure, step, pitch],
            "recurrence": int(recurrence_counts[(step, pitch)]),
            "winner": {k: round(float(v), 6) for k, v in w.items()},
            "alternate": {k: round(float(v), 6) for k, v in a.items()},
            "minTargetVsSubharmonicRatio": round(min(w["targetVsSubharmonicRatio"], a["targetVsSubharmonicRatio"]), 6),
            "minTemplateRatio": round(min(w["templateRatio"], a["templateRatio"]), 6),
        })
        if index % 250 == 0:
            print(f"Fundamental/overtone evidence measured: {index}/{len(pool)}", flush=True)

    missing_reference = reference - champion
    ratio_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    template_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    joint_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for row in feature_rows:
        token = tuple(int(v) for v in row["token"])
        is_true = missing_reference.get(token, 0) > 0
        rr = bucket(float(row["minTargetVsSubharmonicRatio"]), RATIO_BUCKETS)
        tr = bucket(float(row["minTemplateRatio"]), TEMPLATE_BUCKETS)
        recurrence = int(row["recurrence"])
        recur_label = "4plus" if recurrence >= 4 else str(recurrence)
        ratio_counts[rr][0 if is_true else 1] += 1
        template_counts[tr][0 if is_true else 1] += 1
        joint_counts[f"{rr}|{tr}|recur_{recur_label}"][0 if is_true else 1] += 1
        row["trueMissingReference"] = is_true
        row["ratioBucket"] = rr
        row["templateBucket"] = tr

    ratio_summary = {k: precision_row(v[0], v[1]) for k, v in ratio_counts.items()}
    template_summary = {k: precision_row(v[0], v[1]) for k, v in template_counts.items()}
    joint_summary = {k: precision_row(v[0], v[1]) for k, v in joint_counts.items()}
    best_joint = sorted(
        joint_summary.items(),
        key=lambda item: (float(item[1]["precision"]), int(item[1]["true"]), -int(item[1]["false"])),
        reverse=True,
    )[:30]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during fundamental/overtone evidence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-13.82-reference-free-dual-stem-fundamental-overtone-evidence",
        "championScore": champion_score,
        "detectorPool": {
            "bothFloor": attack.POOL_FLOOR,
            "localProminenceMargin": attack.POOL_MARGIN,
            "recurrence": attack.POOL_RECURRENCE,
            "count": len(pool),
        },
        "ratioSummary": ratio_summary,
        "templateSummary": template_summary,
        "bestJointBuckets": [{"signature": key, **value} for key, value in best_joint],
        "rows": feature_rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-fundamentalness-pockets-if-repeatable-else-pivot-detector-family",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "poolCount": len(pool),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 DUAL-STEM FUNDAMENTAL/OVERTONE EVIDENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Fundamental/overtone candidate pool:", len(pool))
    print("Target/subharmonic-ratio precision buckets:")
    for name, _, _ in RATIO_BUCKETS:
        row = ratio_summary.get(name, precision_row(0, 0))
        print(f"  {name}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Harmonic-template-ratio precision buckets:")
    for name, _, _ in TEMPLATE_BUCKETS:
        row = template_summary.get(name, precision_row(0, 0))
        print(f"  {name}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top joint fundamental/overtone/recurrence buckets:")
    for key, row in best_joint[:20]:
        print(f"  {key}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
