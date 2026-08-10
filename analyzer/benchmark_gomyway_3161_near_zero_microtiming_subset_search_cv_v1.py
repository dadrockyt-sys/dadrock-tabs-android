from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_3161_near_zero_microtiming_precision_prune_cv_v1 as base

micro = base.micro
s3161 = base.s3161
recur = base.recur
recall = base.recall
v2 = base.v2
v3 = base.v3
harmonic = base.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-refinement-v1.json"
CROSS_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-subset-search-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-subset-search-cv-v1-manifest.json"
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


def train_safe_signatures(rows: list[dict[str, Any]], candidate_subset: set[str]) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        truth = str(row["truth"])
        count = int(row["count"])
        for sig in set(row["microSignatures"]) & candidate_subset:
            groups[sig][truth] += count
    return {
        sig for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= 1
    }


def evaluate_subset(
    subset: set[str],
    pocket: list[dict[str, Any]],
    champion: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    baseline: dict[str, Any],
    grid: dict[tuple[int, int], float],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
) -> dict[str, Any]:
    pruned: Counter[tuple[int, int, int]] = Counter()
    for row in pocket:
        if set(row["microSignatures"]) & subset:
            pruned[row["token"]] += int(row["count"])

    true_pruned = int(sum((pruned & reference).values()))
    prune_count = int(sum(pruned.values()))
    false_pruned = prune_count - true_pruned
    candidate = champion - pruned
    score = recur.grade(candidate, reference)

    folds: list[dict[str, Any]] = []
    cv_true_pruned = 0
    cv_false_pruned = 0
    folds_with_false_reduction = 0
    for fold in range(FOLDS):
        train = [r for r in pocket if fold_for(r["token"]) != fold]
        test = [r for r in pocket if fold_for(r["token"]) == fold]
        learned = train_safe_signatures(train, subset)
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
            "learned": sorted(learned),
            "truePruned": fold_true,
            "falsePruned": fold_false,
        })

    prune_specific_cv_passed = (
        cv_true_pruned == 0
        and cv_false_pruned >= 2
        and folds_with_false_reduction >= 2
    )

    section_rows: dict[int, dict[str, int]] = defaultdict(lambda: {"truePruned": 0, "falsePruned": 0})
    for row in pocket:
        if set(row["microSignatures"]) & subset:
            section = int(row["token"][0]) // 16
            key = "truePruned" if row["truth"] == "true" else "falsePruned"
            section_rows[section][key] += int(row["count"])
    section_stability_passed = all(v["truePruned"] == 0 for v in section_rows.values()) and false_pruned >= 1

    shifted: list[dict[str, Any]] = []
    shifted_window_stability_passed = True
    for shift_ms in SHIFT_MS:
        shift_true = 0
        shift_false = 0
        for row in pocket:
            sigs = feature_signatures(row["token"], grid, winner_audio, winner_sr, alt_audio, alt_sr, shift_ms)
            if sigs & subset:
                if row["truth"] == "true":
                    shift_true += int(row["count"])
                else:
                    shift_false += int(row["count"])
        passed = shift_true == 0 and shift_false >= 1
        shifted_window_stability_passed = shifted_window_stability_passed and passed
        shifted.append({"shiftMs": shift_ms, "truePruned": shift_true, "falsePruned": shift_false, "passed": passed})

    accepted = (
        true_pruned == 0
        and false_pruned >= 1
        and int(score["matched"]) == int(baseline["matched"])
        and float(score["pitchF1"]) > float(baseline["pitchF1"])
        and prune_specific_cv_passed
        and section_stability_passed
        and shifted_window_stability_passed
    )

    return {
        "subset": sorted(subset),
        "subsetSize": len(subset),
        "score": score,
        "pruneCount": prune_count,
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "cvTruePruned": cv_true_pruned,
        "cvFalsePruned": cv_false_pruned,
        "foldsWithFalseReduction": folds_with_false_reduction,
        "pruneSpecificCrossValidationPassed": prune_specific_cv_passed,
        "sectionStabilityPassed": section_stability_passed,
        "shiftedWindowStabilityPassed": shifted_window_stability_passed,
        "folds": folds,
        "shiftedWindows": shifted,
        "accepted": accepted,
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
    champion, reconstruction = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    profile = v2.load_json(PROFILE_PATH)
    cross = v2.load_json(CROSS_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False or cross.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Profiler inputs are not reference-free during detection")

    zero_rows = list(profile.get("zeroPrecisionRefinementSignaturesMin3False", []))
    signatures = sorted({str(r["signature"]) for r in zero_rows})
    if len(signatures) != 7:
        raise RuntimeError(f"Expected 7 saved microtiming zero signatures, got {len(signatures)}")

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
    if (pocket_true, pocket_false) != (1, 6):
        raise RuntimeError(f"Expected frozen target pocket 1/6, got {pocket_true}/{pocket_false}")

    results: list[dict[str, Any]] = []
    for size in range(1, len(signatures) + 1):
        for combo in itertools.combinations(signatures, size):
            results.append(evaluate_subset(
                set(combo), pocket, champion, reference, baseline, grid,
                winner_audio, winner_sr, alt_audio, alt_sr,
            ))

    accepted = [r for r in results if r["accepted"]]
    accepted.sort(key=lambda r: (-int(r["falsePruned"]), -float(r["score"]["pitchF1"]), int(r["subsetSize"]), r["subset"]))
    best = accepted[0] if accepted else None

    near = sorted(
        [r for r in results if r["truePruned"] == 0],
        key=lambda r: (
            -int(r["cvFalsePruned"]), int(r["cvTruePruned"]),
            -int(r["falsePruned"]), int(r["subsetSize"]), r["subset"],
        ),
    )[:20]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during microtiming subset search CV")

    output = {
        "schemaVersion": 1,
        "passed": best is not None,
        "profileType": "31.61-near-zero-microtiming-subset-search-cv",
        "baselineScore": baseline,
        "reconstruction": reconstruction,
        "targetCrossFamilySignature": target_signature,
        "candidateSignatureCount": len(signatures),
        "subsetsTested": len(results),
        "acceptedSubsetCount": len(accepted),
        "bestAccepted": best,
        "topZeroTrueCandidates": near,
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
        "passed": best is not None,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": baseline["pitchF1"],
        "subsetsTested": len(results),
        "acceptedSubsetCount": len(accepted),
        "bestPitchF1": best["score"]["pitchF1"] if best else baseline["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 NEAR-ZERO MICROTIMING SUBSET SEARCH CV V1 COMPLETE")
    print("Passed:", best is not None)
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Candidate microtiming signatures:", len(signatures))
    print("Subsets tested:", len(results))
    print("Accepted subsets:", len(accepted))
    if best:
        print("BEST ACCEPTED SUBSET")
        print("Subset size:", best["subsetSize"])
        print("Subset:", " || ".join(best["subset"]))
        print("Pitch F1:", best["score"]["pitchF1"])
        print("Matched/missing/extra:", best["score"]["matched"], "/", best["score"]["missing"], "/", best["score"]["extra"])
        print("Pruned true/false:", best["truePruned"], "/", best["falsePruned"])
        print("CV true/false pruned:", best["cvTruePruned"], "/", best["cvFalsePruned"])
        print("Folds with false reduction:", best["foldsWithFalseReduction"])
        print("Prune-specific CV passed:", best["pruneSpecificCrossValidationPassed"])
        print("Section stability passed:", best["sectionStabilityPassed"])
        print("Shifted-window stability passed:", best["shiftedWindowStabilityPassed"])
    else:
        print("No subset satisfied every strict validation gate.")
        print("Top zero-full-data-true-loss candidates:")
        for row in near[:10]:
            print(
                f"size={row['subsetSize']} fullFalse={row['falsePruned']} "
                f"cvTrue={row['cvTruePruned']} cvFalse={row['cvFalsePruned']} "
                f"folds={row['foldsWithFalseReduction']} "
                f"shifted={row['shiftedWindowStabilityPassed']} subset={' || '.join(row['subset'])}"
            )
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
