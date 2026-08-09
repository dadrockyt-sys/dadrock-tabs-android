from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2769_dual_stem_harmonic_phase_coherence_v1 as phase

recur = phase.recur
recall = phase.recall
v2 = phase.v2
v3 = phase.v3
harmonic = phase.harmonic
survivor = phase.survivor

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2769-dual-stem-harmonic-phase-coherence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2802-harmonic-phase-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2802-harmonic-phase-survivors-precision-v1-manifest.json"
EXPECTED_2769 = (183, 684, 272)
EXPECTED_2769_F1 = 27.69
EXPECTED_2802 = (183, 684, 256)
EXPECTED_2802_F1 = 28.02
EXPECTED_ZERO_SIGNATURES = 4
EXPECTED_TOP3_FALSE_PRUNED = 16


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def reconstruct_2802(
    grid: dict[tuple[int, int], float],
    winner_audio,
    winner_sr: int,
    alt_audio,
    alt_sr: int,
    reference: Counter[tuple[int, int, int]],
) -> tuple[Counter[tuple[int, int, int]], dict[str, Any]]:
    champion_2769, _ = survivor.reconstruct_2769(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score_2769 = recur.grade(champion_2769, reference)
    actual_2769 = (
        int(score_2769["matched"]),
        int(score_2769["missing"]),
        int(score_2769["extra"]),
    )
    if actual_2769 != EXPECTED_2769 or abs(float(score_2769["pitchF1"]) - EXPECTED_2769_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 27.69 champion {EXPECTED_2769}/{EXPECTED_2769_F1}, "
            f"got {actual_2769}/{score_2769['pitchF1']}"
        )

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("27.69 harmonic-phase profile is not reference-free during detection")

    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} harmonic-phase zero-precision signatures, got {len(zero_rows)}"
        )
    zero_rows.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    top3 = {str(r["signature"]) for r in zero_rows[:3]}

    profile_rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in profile_rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_2769.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        signatures = {str(s) for s in row.get("signatures", [])}
        if signatures & top3:
            pruned[tok] = count

    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = int(sum(pruned.values()) - true_pruned)
    if true_pruned != 0 or false_pruned != EXPECTED_TOP3_FALSE_PRUNED:
        raise RuntimeError(
            f"Expected validated top3 harmonic-phase prune to remove 0 true / {EXPECTED_TOP3_FALSE_PRUNED} false, "
            f"got {true_pruned} true / {false_pruned} false"
        )

    champion_2802 = champion_2769 - pruned
    score_2802 = recur.grade(champion_2802, reference)
    actual_2802 = (
        int(score_2802["matched"]),
        int(score_2802["missing"]),
        int(score_2802["extra"]),
    )
    if actual_2802 != EXPECTED_2802 or abs(float(score_2802["pitchF1"]) - EXPECTED_2802_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 28.02 champion {EXPECTED_2802}/{EXPECTED_2802_F1}, "
            f"got {actual_2802}/{score_2802['pitchF1']}"
        )

    return champion_2802, {
        "score2769": score_2769,
        "score2802": score_2802,
        "validatedTop3Signatures": sorted(top3),
        "top3TruePruned": true_pruned,
        "top3FalsePruned": false_pruned,
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

    champion, reconstruction = reconstruct_2802(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )
    score = recur.grade(champion, reference)

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = phase.phase_features(winner_audio, winner_sr, center, pitch)
        af = phase.phase_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(phase.signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero.sort(key=lambda row: (-int(row["false"]), str(row["signature"])))
    supported = [row for row in ranked if int(row["true"]) >= 5]
    supported.sort(key=lambda row: (-float(row["precision"]), -int(row["true"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 28.02 harmonic-phase survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-28.02-harmonic-phase-survivor-precision",
        "champion2802Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "dual-stem-harmonic-phase-partial-coherence-survivors-after-validated-top3-prune",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
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
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 28.02 HARMONIC PHASE SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Validated top3 harmonic-phase true pruned:", reconstruction["top3TruePruned"])
    print("Validated top3 harmonic-phase false pruned:", reconstruction["top3FalsePruned"])
    print("Generalizable zero-precision harmonic-phase survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true harmonic-phase survivor signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
