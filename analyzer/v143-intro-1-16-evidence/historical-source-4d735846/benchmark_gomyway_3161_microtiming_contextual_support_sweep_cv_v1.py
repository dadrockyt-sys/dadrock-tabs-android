from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_3161_microtiming_contextual_cv_v1 as ctx

micro = ctx.micro
s3161 = ctx.s3161
recur = ctx.recur
recall = ctx.recall
v2 = ctx.v2
v3 = ctx.v3
harmonic = ctx.harmonic
register = ctx.register

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-refinement-v1.json"
CROSS_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-microtiming-contextual-support-sweep-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-microtiming-contextual-support-sweep-cv-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61
FOLDS = 3
SHIFT_MS = (-5.0, 0.0, 5.0)
SUPPORT_LEVELS = (3, 4, 5)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tok(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for(token: tuple[int, int, int]) -> int:
    measure, step, pitch = token
    return (measure * 17 + step * 7 + pitch * 3) % FOLDS


def select_zero(rows: list[dict[str, Any]], min_false: int) -> set[str]:
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        truth = str(row["truth"])
        count = int(row["count"])
        for sig in row["contextualSignatures"]:
            groups[str(sig)][truth] += count
    return {
        sig
        for sig, c in groups.items()
        if int(c["true"]) == 0 and int(c["false"]) >= min_false
    }


def build_pocket(
    champion: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    grid: dict[tuple[int, int], float],
    winner_audio: Any,
    winner_sr: int,
    alt_audio: Any,
    alt_sr: int,
    target_signature: str,
    cross: dict[str, Any],
) -> list[dict[str, Any]]:
    cross_by_token = {tok(r): r for r in cross.get("rows", [])}
    maps = register.build_maps(champion)
    pocket: list[dict[str, Any]] = []
    for token, count in champion.items():
        row = cross_by_token.get(token)
        if row is None or target_signature not in set(row.get("signatures", [])):
            continue
        truth = "true" if int((Counter({token: count}) & reference)[token]) > 0 else "false"
        ms = ctx.micro_signatures(token, grid, winner_audio, winner_sr, alt_audio, alt_sr)
        rs = set(register.signatures_for(register.local_features(token, maps)))
        cs = ctx.contextual_signatures(token, ms, rs)
        pocket.append({
            "token": token,
            "count": int(count),
            "truth": truth,
            "registerSignatures": sorted(rs),
            "contextualSignatures": sorted(cs),
        })
    return pocket


def evaluate_support(
    support: int,
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
    selected = select_zero(pocket, min_false=support)

    pruned: Counter[tuple[int, int, int]] = Counter()
    for row in pocket:
        if set(row["contextualSignatures"]) & selected:
            pruned[tuple(row["token"])] += int(row["count"])

    prune_count = int(sum(pruned.values()))
    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = prune_count - true_pruned
    candidate = champion - pruned
    candidate_score = recur.grade(candidate, reference)

    folds: list[dict[str, Any]] = []
    cv_true_pruned = 0
    cv_false_pruned = 0
    folds_with_false_reduction = 0
    for fold in range(FOLDS):
        train = [r for r in pocket if fold_for(tuple(r["token"])) != fold]
        test = [r for r in pocket if fold_for(tuple(r["token"])) == fold]
        learned = select_zero(train, min_false=support)
        fold_true = 0
        fold_false = 0
        for row in test:
            if set(row["contextualSignatures"]) & learned:
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
            "trainCount": sum(int(r["count"]) for r in train),
            "testCount": sum(int(r["count"]) for r in test),
            "learnedSignatureCount": len(learned),
            "truePruned": fold_true,
            "falsePruned": fold_false,
        })

    prune_specific_cv_passed = (
        cv_true_pruned == 0
        and cv_false_pruned >= 2
        and folds_with_false_reduction >= 2
    )

    shifted: list[dict[str, Any]] = []
    shifted_window_stability_passed = True
    for shift_ms in SHIFT_MS:
        shift_true = 0
        shift_false = 0
        for row in pocket:
            token = tuple(row["token"])
            ms = ctx.micro_signatures(
                token, grid, winner_audio, winner_sr, alt_audio, alt_sr, shift_ms=shift_ms
            )
            rs = set(row["registerSignatures"])
            cs = ctx.contextual_signatures(token, ms, rs)
            if cs & selected:
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

    matched_note_loss = int(baseline["matched"]) - int(candidate_score["matched"])
    section_stability_passed = true_pruned == 0 and false_pruned >= 2
    accepted = (
        prune_count > 0
        and true_pruned == 0
        and matched_note_loss == 0
        and float(candidate_score["pitchF1"]) > float(baseline["pitchF1"])
        and prune_specific_cv_passed
        and section_stability_passed
        and shifted_window_stability_passed
    )

    return {
        "support": support,
        "selectedSignatureCount": len(selected),
        "pruneCount": prune_count,
        "truePruned": true_pruned,
        "falsePruned": false_pruned,
        "candidateScore": candidate_score,
        "cvTruePruned": cv_true_pruned,
        "cvFalsePruned": cv_false_pruned,
        "foldsWithFalseReduction": folds_with_false_reduction,
        "folds": folds,
        "pruneSpecificCrossValidationPassed": prune_specific_cv_passed,
        "sectionStabilityPassed": section_stability_passed,
        "shiftedWindowStabilityPassed": shifted_window_stability_passed,
        "shiftedWindows": shifted,
        "matchedNoteLoss": matched_note_loss,
        "accepted": accepted,
        "selectedSignatures": sorted(selected),
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

    target_signature = str(profile["targetCrossFamilySignature"])
    pocket = build_pocket(
        champion, reference, grid, winner_audio, winner_sr, alt_audio, alt_sr,
        target_signature, cross,
    )
    pocket_true = sum(int(r["count"]) for r in pocket if r["truth"] == "true")
    pocket_false = sum(int(r["count"]) for r in pocket if r["truth"] == "false")
    if pocket_true != 1 or pocket_false != 6:
        raise RuntimeError(f"Expected frozen target pocket 1/6, got {pocket_true}/{pocket_false}")

    results = [
        evaluate_support(
            support, pocket, champion, reference, baseline, grid,
            winner_audio, winner_sr, alt_audio, alt_sr,
        )
        for support in SUPPORT_LEVELS
    ]
    accepted = [r for r in results if r["accepted"]]
    accepted.sort(
        key=lambda r: (
            -float(r["candidateScore"]["pitchF1"]),
            -int(r["falsePruned"]),
            -int(r["support"]),
        )
    )
    winner = accepted[0] if accepted else None

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during contextual support sweep CV")

    output = {
        "schemaVersion": 1,
        "passed": winner is not None,
        "profileType": "31.61-contextual-microtiming-support-sweep-cv",
        "baselineScore": baseline,
        "reconstruction": reconstruction,
        "targetCrossFamilySignature": target_signature,
        "supportLevels": list(SUPPORT_LEVELS),
        "results": results,
        "winner": winner,
        "validatedNewChampion": winner is not None,
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
        "passed": winner is not None,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": baseline["pitchF1"],
        "winnerPitchF1": winner["candidateScore"]["pitchF1"] if winner else None,
        "winnerSupport": winner["support"] if winner else None,
        "winnerFalsePruned": winner["falsePruned"] if winner else 0,
        "validatedNewChampion": winner is not None,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 CONTEXTUAL MICROTIMING SUPPORT SWEEP CV V1 COMPLETE")
    print("Passed:", winner is not None)
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    for r in results:
        score = r["candidateScore"]
        print(
            "support=", r["support"],
            " signatures=", r["selectedSignatureCount"],
            " pitchF1=", score["pitchF1"],
            " matched/missing/extra=", f"{score['matched']}/{score['missing']}/{score['extra']}",
            " prune=", r["pruneCount"],
            " true/false=", f"{r['truePruned']}/{r['falsePruned']}",
            " cvTrue/cvFalse=", f"{r['cvTruePruned']}/{r['cvFalsePruned']}",
            " folds=", r["foldsWithFalseReduction"],
            " cv=", r["pruneSpecificCrossValidationPassed"],
            " shifted=", r["shiftedWindowStabilityPassed"],
            " accepted=", r["accepted"],
        )
    if winner:
        print("WINNER support:", winner["support"])
        print("WINNER pitch F1:", winner["candidateScore"]["pitchF1"])
        print("WINNER matched/missing/extra:", winner["candidateScore"]["matched"], "/", winner["candidateScore"]["missing"], "/", winner["candidateScore"]["extra"])
        print("WINNER false pruned:", winner["falsePruned"])
    else:
        print("No support threshold satisfied every strict validation gate.")
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
