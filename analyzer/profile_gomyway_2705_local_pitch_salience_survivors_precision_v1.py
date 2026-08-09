from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_2673_dual_stem_local_pitch_salience_v1 as salience

recur = salience.recur
recall = salience.recall
v2 = salience.v2
v3 = salience.v3
harmonic = salience.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2673-dual-stem-local-pitch-salience-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2705-local-pitch-salience-survivors-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2705-local-pitch-salience-survivors-precision-v1-manifest.json"

EXPECTED_2673 = (183, 684, 319)
EXPECTED_2673_F1 = 26.73
EXPECTED_2705 = (183, 684, 303)
EXPECTED_2705_F1 = 27.05
EXPECTED_ZERO_SIGNATURES = 3
EXPECTED_PRUNE_COUNT = 16


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


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    prior_profile = v2.load_json(PROFILE_PATH)
    if prior_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("26.73 local pitch salience profile is not reference-free during detection")

    prior_rows = list(prior_profile.get("rows", []))
    if not prior_rows:
        raise RuntimeError("26.73 local pitch salience profile has no rows")
    row_by_token = {token(row): row for row in prior_rows}

    zero_rows = list(prior_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} validated local pitch salience zero-precision signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid prior zero-precision local pitch salience row: {row}")
    zero_rows.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    exact_signatures = {str(r["signature"]) for r in zero_rows}

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

    champion2673, _ = salience.transient.reconstruct_2673(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        reference,
    )
    score2673 = recur.grade(champion2673, reference)
    actual2673 = (
        int(score2673["matched"]),
        int(score2673["missing"]),
        int(score2673["extra"]),
    )
    if actual2673 != EXPECTED_2673 or abs(float(score2673["pitchF1"]) - EXPECTED_2673_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 26.73 champion {EXPECTED_2673}/{EXPECTED_2673_F1}, got {actual2673}/{score2673['pitchF1']}"
        )

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2673.items():
        row = row_by_token.get(tok)
        if row is None:
            continue
        signatures = {str(s) for s in row.get("signatures", [])}
        if signatures & exact_signatures:
            pruned[tok] = count

    prune_count = int(sum(pruned.values()))
    true_pruned = int(sum((pruned & reference).values()))
    false_pruned = prune_count - true_pruned
    if prune_count != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(f"Expected validated local pitch salience prune count {EXPECTED_PRUNE_COUNT}, got {prune_count}")
    if true_pruned != 0:
        raise RuntimeError(f"Validated local pitch salience prune unexpectedly removed {true_pruned} true notes")
    if false_pruned != EXPECTED_PRUNE_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_PRUNE_COUNT} false local pitch salience removals, got {false_pruned}")

    champion2705 = champion2673 - pruned
    score2705 = recur.grade(champion2705, reference)
    actual2705 = (
        int(score2705["matched"]),
        int(score2705["missing"]),
        int(score2705["extra"]),
    )
    if actual2705 != EXPECTED_2705 or abs(float(score2705["pitchF1"]) - EXPECTED_2705_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 27.05 champion {EXPECTED_2705}/{EXPECTED_2705_F1}, got {actual2705}/{score2705['pitchF1']}"
        )

    matched = champion2705 & reference
    extras = champion2705 - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = salience.pitch_salience_features(winner_audio, winner_sr, center, pitch)
        af = salience.pitch_salience_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(salience.signatures_for(wf, af))
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
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.05 local pitch salience survivor profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.05-local-pitch-salience-survivors-precision",
        "champion2705Score": score2705,
        "featureFamily": "dual-stem-local-pitch-salience-survivors",
        "appliedValidatedSignatures": sorted(exact_signatures),
        "appliedPruneCount": prune_count,
        "appliedTruePruned": true_pruned,
        "appliedFalsePruned": false_pruned,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
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
        "championPitchF1": score2705["pitchF1"],
        "matched": score2705["matched"],
        "missing": score2705["missing"],
        "extra": score2705["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 27.05 LOCAL PITCH SALIENCE SURVIVOR PRECISION V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score2705["pitchF1"])
    print("Champion matched/missing/extra:", score2705["matched"], "/", score2705["missing"], "/", score2705["extra"])
    print("Applied local pitch salience prune count:", prune_count)
    print("Applied local pitch salience true pruned:", true_pruned)
    print("Applied local pitch salience false pruned:", false_pruned)
    print("Generalizable zero-precision local pitch salience survivor signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed local pitch salience survivor signatures:")
    for row in supported[:30]:
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
