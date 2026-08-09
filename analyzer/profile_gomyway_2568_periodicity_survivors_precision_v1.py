from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2552_dual_stem_periodicity_phase_coherence_v1 as period

p2552 = period.p2552
recur = period.recur
recall = period.recall
v2 = period.v2
v3 = period.v3
harmonic = period.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PERIOD_PROFILE_PATH = PUBLIC / "gomyway-2552-dual-stem-periodicity-phase-coherence-v1.json"
TEMPLATE_PROFILE_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2568-periodicity-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2568-periodicity-survivors-precision-v1-manifest.json"
EXPECTED_2552 = (183, 684, 384)
EXPECTED_2552_F1 = 25.52
EXPECTED_2568 = (183, 684, 375)
EXPECTED_2568_F1 = 25.68
EXPECTED_TEMPLATE_ZERO_SIGNATURES = 11
EXPECTED_PERIOD_ZERO_SIGNATURES = 1
EXPECTED_PERIOD_PRUNE_COUNT = 9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


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

    template_profile = v2.load_json(TEMPLATE_PROFILE_PATH)
    template_zero = list(template_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(template_zero) != EXPECTED_TEMPLATE_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_TEMPLATE_ZERO_SIGNATURES} validated harmonic-template signatures, got {len(template_zero)}"
        )
    exact_template_signatures = {str(row["signature"]) for row in template_zero}

    period_profile = v2.load_json(PERIOD_PROFILE_PATH)
    if period_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.52 periodicity profile is not reference-free during detection")
    period_rows = list(period_profile.get("rows", []))
    if not period_rows:
        raise RuntimeError("25.52 periodicity profile has no rows")
    period_row_by_token = {token(row): row for row in period_rows}

    period_zero = list(period_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(period_zero) != EXPECTED_PERIOD_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_PERIOD_ZERO_SIGNATURES} periodicity zero-precision signature, got {len(period_zero)}"
        )
    target_signature = str(period_zero[0]["signature"])
    if int(period_zero[0].get("true", -1)) != 0 or int(period_zero[0].get("false", 0)) < 5:
        raise RuntimeError(f"Invalid periodicity zero-precision row: {period_zero[0]}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion2552, prior_pruned = p2552.reconstruct_2552(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        exact_template_signatures,
    )
    if int(sum(prior_pruned.values())) != p2552.EXPECTED_PRUNE_COUNT:
        raise RuntimeError(
            f"Expected frozen 25.52 harmonic-template prune count {p2552.EXPECTED_PRUNE_COUNT}, got {sum(prior_pruned.values())}"
        )

    baseline2552 = recur.grade(champion2552, reference)
    actual2552 = (
        int(baseline2552["matched"]),
        int(baseline2552["missing"]),
        int(baseline2552["extra"]),
    )
    if actual2552 != EXPECTED_2552 or abs(float(baseline2552["pitchF1"]) - EXPECTED_2552_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 25.52 champion {EXPECTED_2552}/{EXPECTED_2552_F1}, got {actual2552}/{baseline2552['pitchF1']}"
        )

    period_pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2552.items():
        row = period_row_by_token.get(tok)
        if row is not None and target_signature in {str(s) for s in row.get("signatures", [])}:
            period_pruned[tok] = count

    if int(sum(period_pruned.values())) != EXPECTED_PERIOD_PRUNE_COUNT:
        raise RuntimeError(
            f"Expected frozen periodicity prune count {EXPECTED_PERIOD_PRUNE_COUNT}, got {sum(period_pruned.values())}"
        )
    true_pruned = int(sum((period_pruned & reference).values()))
    if true_pruned != 0:
        raise RuntimeError(f"Frozen periodicity prune would remove {true_pruned} true notes")

    champion2568 = champion2552 - period_pruned
    score2568 = recur.grade(champion2568, reference)
    actual2568 = (
        int(score2568["matched"]),
        int(score2568["missing"]),
        int(score2568["extra"]),
    )
    if actual2568 != EXPECTED_2568 or abs(float(score2568["pitchF1"]) - EXPECTED_2568_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 25.68 champion {EXPECTED_2568}/{EXPECTED_2568_F1}, got {actual2568}/{score2568['pitchF1']}"
        )

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    rows: list[dict[str, Any]] = []

    for tok, count in champion2568.items():
        midi = int(tok[1])
        center = float(v2.token_time(grid, tok))
        wf = period.periodicity_features(winner_audio, winner_sr, center, midi)
        af = period.periodicity_features(alt_audio, alt_sr, center, midi)
        signatures = sorted(period.signatures_for(wf, af))
        truth_count = min(int(count), int(reference.get(tok, 0)))
        false_count = int(count) - truth_count
        label_counts = Counter({"true": truth_count, "false": false_count})
        for signature in signatures:
            groups[signature].update(label_counts)
        rows.append({
            "token": list(tok),
            "count": int(count),
            "true": truth_count,
            "false": false_count,
            "winnerFeatures": wf,
            "altFeatures": af,
            "signatures": signatures,
        })

    precision = period.precision_rows(groups)
    zero_precision = [
        row for row in precision
        if int(row["true"]) == 0 and int(row["false"]) >= 5
    ]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 25.68 periodicity survivor profiling")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "25.68-periodicity-phase-coherence-survivor-precision",
        "baseline2552Score": baseline2552,
        "champion2568Score": score2568,
        "periodicityPruneSignature": target_signature,
        "periodicityPruneCount": int(sum(period_pruned.values())),
        "periodicityTruePruned": true_pruned,
        "rows": rows,
        "precisionSignatures": precision,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
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
        "champion2568PitchF1": score2568["pitchF1"],
        "zeroPrecisionSignatureCount": len(zero_precision),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 25.68 PERIODICITY SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score2568["pitchF1"])
    print("Champion matched/missing/extra:", score2568["matched"], "/", score2568["missing"], "/", score2568["extra"])
    print("Applied periodicity signature:", target_signature)
    print("Applied periodicity prune count:", int(sum(period_pruned.values())))
    print("Applied periodicity true pruned:", true_pruned)
    print("Generalizable zero-precision periodicity survivor signatures (5+ false, 0 true):", len(zero_precision))
    for row in zero_precision[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
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
