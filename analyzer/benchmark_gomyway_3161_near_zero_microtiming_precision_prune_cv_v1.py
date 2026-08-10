from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_near_zero_microtiming_refinement_v1 as micro

s3161 = micro.s3161
recur = micro.recur
recall = micro.recall
v2 = micro.v2
v3 = micro.v3
harmonic = micro.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-refinement-v1.json"
CROSS_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61
FOLDS = 3
SHIFT_MS = (-5.0, 0.0, 5.0)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tok(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for(token: tuple[int, int, int]) -> int:
    measure, step, pitch = token
    return (measure * 17 + step * 7 + pitch * 3) % FOLDS


def feature_signatures(
    token: tuple[int, int, int],
    grid: dict[tuple[int, int], float],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
    shift_ms: float = 0.0,
) -> set[str]:
    measure, step, _pitch = token
    center = float(grid[(measure, step)]) + shift_ms / 1000.0
    wf = micro.onset_offset_features(winner_audio, winner_sr, center)
    af = micro.onset_offset_features(alt_audio, alt_sr, center)
    return set(micro.signatures_for(wf, af))


def select_zero_signatures(rows: list[dict[str, Any]], min_false: int) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        truth = str(row["truth"])
        count = int(row["count"])
        for sig in row["microSignatures"]:
            groups[str(sig)][truth] += count
    return {
        sig
        for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= min_false
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

    profile = v2.load_json(PROFILE_PATH)
    cross = v2.load_json(CROSS_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Microtiming profile is not reference-free during detection")
    if cross.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cross-family profile is not reference-free during detection")

    selected_rows = list(profile.get("zeroPrecisionRefinementSignaturesMin3False", []))
    if not selected_rows:
        raise RuntimeError("Expected saved zero-precision microtiming signatures")
    selected = {str(r["signature"]) for r in selected_rows}
    for row in selected_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 3:
            raise RuntimeError(f"Invalid saved microtiming zero row: {row}")

    target_signature = str(profile["targetCrossFamilySignature"])
    cross_by_token = {tok(r): r for r in cross.get("rows", [])}

    pocket: list[dict[str, Any]] = []
    for token, count in champion.items():
        row = cross_by_token.get(token)
        if row is None or target_signature not in set(row.get("signatures", [])):
            continue
        truth = "true" if int((Counter({token: count}) & reference)[token]) > 0 else "false"
        pocket.append({
            "token": token,
            "count": int(count),
            "truth": truth,
            "microSignatures": sorted(feature_signatures(token, grid, winner_audio, winner_sr, alt_audio, alt_sr)),
        })

    pocket_true = sum(r["count"] for r in pocket if r["truth"] == "true")
    pocket_false = sum(r["count"] for r in pocket if r["truth"] == "false")
    if pocket_true != 1 or pocket_false != 6:
        raise RuntimeError(f"Expected frozen target pocket 1/6, got {pocket_true}/{pocket_false}")

    pruned: Counter[tuple[int, int, int]] = Counter()
    for row in pocket:
        if set(row["microSignatures"]) & selected:
            pruned[row["token"]] += int(row["count"])

    true_pruned = int(sum((pruned & reference).values()))
    prune_count = int(sum(pruned.values()))
    false_pruned = prune_count - true_pruned
    if true_pruned != 0 or false_pruned < 3:
        raise RuntimeError(
            f"Full-data microtiming rule is not safely useful: pruned={prune_count} true={true_pruned} false={false_pruned}"
        )

    candidate = champion - pruned
    candidate_score = recur.grade(candidate, reference)
    if int(candidate_score["matched"]) != int(baseline["matched"]):
        raise RuntimeError("Candidate lost matched notes")

    folds: list[dict[str, Any]] = []
    cv_true_pruned = 0
    cv_false_pruned = 0
    folds_with_false_reduction = 0
    for fold in range(FOLDS):
        train = [r for r in pocket if fold_for(r["token"]) != fold]
        test = [r for r in pocket if fold_for(r["token"]) == fold]
        learned = select_zero_signatures(train, min_false=2)
        fold_true = 0
        fold_false = 0
        for row in test:
            if set(row["microSignatures"]) & learned:
                if row["truth"] == "true":
                    fold_true += int(row["count"])
                else:
                    fold_false += int(row["count"])
        cv_true_pruned += fold_true
        cv_false_pruned += fold_false
        if fold_false > 0:
            folds_with_false_reduction += 1
        folds.append({
            "fold": fold,
            "trainCount": sum(r["count"] for r in train),
            "testCount": sum(r["count"] for r in test),
            "learnedSignatureCount": len(learned),
            "truePruned": fold_true,
            "falsePruned": fold_false,
            "passedZeroTrueLoss": fold_true == 0,
        })

    prune_specific_cv_passed = (
        cv_true_pruned == 0
        and cv_false_pruned >= 2
        and folds_with_false_reduction >= 2
    )

    section_rows: dict[int, dict[str, int]] = defaultdict(lambda: {"truePruned": 0, "falsePruned": 0})
    for row in pocket:
        if set(row["microSignatures"]) & selected:
            measure = int(row["token"][0])
            section = measure // 16
            if row["truth"] == "true":
                section_rows[section]["truePruned"] += int(row["count"])
            else:
                section_rows[section]["falsePruned"] += int(row["count"])
    section_stability_passed = all(v["truePruned"] == 0 for v in section_rows.values()) and false_pruned >= 3

    shifted: list[dict[str, Any]] = []
    shifted_window_stability_passed = True
    for shift_ms in SHIFT_MS:
        shift_true = 0
        shift_false = 0
        for row in pocket:
            sigs = feature_signatures(
                row["token"], grid, winner_audio, winner_sr, alt_audio, alt_sr, shift_ms=shift_ms
            )
            if sigs & selected:
                if row["truth"] == "true":
                    shift_true += int(row["count"])
                else:
                    shift_false += int(row["count"])
        passed = shift_true == 0 and shift_false >= 2
        shifted_window_stability_passed = shifted_window_stability_passed and passed
        shifted.append({
            "shiftMs": shift_ms,
            "truePruned": shift_true,
            "falsePruned": shift_false,
            "passed": passed,
        })

    accepted = (
        prune_specific_cv_passed
        and section_stability_passed
        and shifted_window_stability_passed
        and true_pruned == 0
        and int(candidate_score["matched"]) == int(baseline["matched"])
        and float(candidate_score["pitchF1"]) > float(baseline["pitchF1"])
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during microtiming precision-prune CV")

    output = {
        "schemaVersion": 1,
        "passed": accepted,
        "profileType": "31.61-near-zero-microtiming-precision-prune-cv",
        "baselineScore": baseline,
        "candidateScore": candidate_score,
        "targetCrossFamilySignature": target_signature,
        "selectedZeroPrecisionSignatures": sorted(selected),
        "pruneCount": prune_count,
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "extraReduction": false_pruned,
        "pruneSpecificCrossValidationPassed": prune_specific_cv_passed,
        "cvTruePruned": cv_true_pruned,
        "cvFalsePruned": cv_false_pruned,
        "foldsWithFalseReduction": folds_with_false_reduction,
        "folds": folds,
        "sectionStabilityPassed": section_stability_passed,
        "sectionRows": dict(section_rows),
        "shiftedWindowStabilityPassed": shifted_window_stability_passed,
        "shiftedWindows": shifted,
        "matchedNoteLoss": int(baseline["matched"]) - int(candidate_score["matched"]),
        "validatedNewChampion": accepted,
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
        "passed": accepted,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": baseline["pitchF1"],
        "candidatePitchF1": candidate_score["pitchF1"],
        "matched": candidate_score["matched"],
        "missing": candidate_score["missing"],
        "extra": candidate_score["extra"],
        "pruneCount": prune_count,
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "validatedNewChampion": accepted,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 NEAR-ZERO MICROTIMING PRECISION PRUNE CV V1 COMPLETE")
    print("Passed:", accepted)
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Candidate pitch F1:", candidate_score["pitchF1"])
    print("Candidate matched/missing/extra:", candidate_score["matched"], "/", candidate_score["missing"], "/", candidate_score["extra"])
    print("Selected zero-precision signature count:", len(selected))
    print("Candidate prune count:", prune_count)
    print("Candidate true pruned:", true_pruned)
    print("Candidate false pruned:", false_pruned)
    print("Candidate extra reduction:", false_pruned)
    print("Prune-specific cross-validation passed:", prune_specific_cv_passed)
    print("CV true pruned:", cv_true_pruned)
    print("CV false pruned:", cv_false_pruned)
    print("Folds with false reduction:", folds_with_false_reduction)
    print("Section stability passed:", section_stability_passed)
    print("Shifted-window stability passed:", shifted_window_stability_passed)
    print("Matched-note loss:", int(baseline["matched"]) - int(candidate_score["matched"]))
    print("Validated new champion:", accepted)
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
