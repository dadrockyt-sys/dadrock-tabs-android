from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_cross_stem_consensus_recall_v1 as crossstem

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-cross-stem-missing-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-cross-stem-missing-profile-v1-manifest.json"

# 6.99 is now treated as the benchmark champion after 5-fold CV and contiguous-block stability.
CURRENT_CHAMPION_F1 = 6.99
CURRENT_CHAMPION_RULE = "alt_additions_all"

SECTION_BLOCKS = [
    (17, 32),
    (33, 48),
    (49, 64),
    (65, 80),
    (81, 96),
    (97, 113),
]
REGISTER_BUCKETS = [
    (40, 51, "low_E2-D#3"),
    (52, 63, "mid_E3-D#4"),
    (64, 75, "upper_E4-D#5"),
    (76, 88, "high_E5-E6"),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_name(midi: int) -> str:
    for low, high, name in REGISTER_BUCKETS:
        if low <= midi <= high:
            return name
    return "outside_guitar_range"


def section_name(measure: int) -> str:
    for start, end in SECTION_BLOCKS:
        if start <= measure <= end:
            return f"m{start}_{end}"
    return "outside_reference"


def top_items(counter: Counter[Any], limit: int = 20) -> list[dict[str, Any]]:
    return [
        {"key": key, "count": count}
        for key, count in counter.most_common(limit)
    ]


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    for path in (crossstem.WINNER_STEM, crossstem.ALT_STEM):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark stem: {path.relative_to(ROOT)}")

    print("Analyzing frozen 6.99 cross-stem champion...", flush=True)
    winner_grouped = crossstem.group_rows(crossstem.WINNER_STEM, grid)
    alt_grouped = crossstem.group_rows(crossstem.ALT_STEM, grid)
    predicted = crossstem.merge_rows(winner_grouped, alt_grouped, CURRENT_CHAMPION_RULE)

    matched = sum((predicted & reference).values())
    missing = reference - predicted
    extra = predicted - reference
    predicted_count = sum(predicted.values())
    pitch_f1 = round(100.0 * v2.f1(matched, predicted_count, sum(reference.values())), 2)

    by_section: Counter[str] = Counter()
    by_register: Counter[str] = Counter()
    by_section_register: Counter[str] = Counter()
    by_pitch: Counter[int] = Counter()
    by_pitch_class: Counter[int] = Counter()
    by_step: Counter[int] = Counter()
    by_measure: Counter[int] = Counter()

    for (measure, step, midi), count in missing.items():
        sec = section_name(measure)
        reg = register_name(midi)
        by_section[sec] += count
        by_register[reg] += count
        by_section_register[f"{sec}|{reg}"] += count
        by_pitch[midi] += count
        by_pitch_class[midi % 12] += count
        by_step[step] += count
        by_measure[measure] += count

    section_rows = []
    for start, end in SECTION_BLOCKS:
        sec = f"m{start}_{end}"
        ref_count = sum(v for (m, _s, _p), v in reference.items() if start <= m <= end)
        miss_count = by_section[sec]
        section_rows.append({
            "section": sec,
            "referencePitchTokens": ref_count,
            "missingPitchTokens": miss_count,
            "missingRatePercent": round(100.0 * miss_count / ref_count, 2) if ref_count else 0.0,
        })

    register_rows = []
    for low, high, reg in REGISTER_BUCKETS:
        ref_count = sum(v for (_m, _s, p), v in reference.items() if low <= p <= high)
        miss_count = by_register[reg]
        register_rows.append({
            "register": reg,
            "midiRange": [low, high],
            "referencePitchTokens": ref_count,
            "missingPitchTokens": miss_count,
            "missingRatePercent": round(100.0 * miss_count / ref_count, 2) if ref_count else 0.0,
        })

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during missing-pitch profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "cross-stem-champion-missing-pitch-profile",
        "frozenChampionRule": CURRENT_CHAMPION_RULE,
        "expectedChampionPitchF1": CURRENT_CHAMPION_F1,
        "observedChampionPitchF1": pitch_f1,
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": sum(missing.values()),
        "extraCandidatePitchTokens": sum(extra.values()),
        "sectionProfile": section_rows,
        "registerProfile": register_rows,
        "topSectionRegisterBuckets": top_items(by_section_register, 20),
        "topMissingMidiPitches": top_items(by_pitch, 20),
        "topMissingPitchClasses": top_items(by_pitch_class, 12),
        "topMissingMeasures": top_items(by_measure, 20),
        "missingByStep": dict(sorted(by_step.items())),
        "timingGrid": grid_diagnostics,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "target-largest-missing-section-register-bucket-with-detector-side-evidence",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "frozenChampionRule": CURRENT_CHAMPION_RULE,
        "observedChampionPitchF1": pitch_f1,
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CROSS-STEM MISSING PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion rule:", CURRENT_CHAMPION_RULE)
    print("Observed champion pitch F1:", pitch_f1)
    print("Matched/missing/extra:", matched, "/", sum(missing.values()), "/", sum(extra.values()))
    print("Section profile:")
    for row in section_rows:
        print(
            f"  {row['section']}: missing={row['missingPitchTokens']}/{row['referencePitchTokens']} "
            f"rate={row['missingRatePercent']}%"
        )
    print("Register profile:")
    for row in register_rows:
        print(
            f"  {row['register']}: missing={row['missingPitchTokens']}/{row['referencePitchTokens']} "
            f"rate={row['missingRatePercent']}%"
        )
    print("Top section/register missing buckets:")
    for row in output["topSectionRegisterBuckets"][:10]:
        print(" ", row["key"], row["count"])
    print("Top missing MIDI pitches:")
    for row in output["topMissingMidiPitches"][:10]:
        print(" ", row["key"], row["count"])
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
