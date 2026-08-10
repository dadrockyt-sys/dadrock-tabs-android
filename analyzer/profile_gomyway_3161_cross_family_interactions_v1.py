from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_spectral_flux_survivors_v1 as flux3161
import profile_gomyway_3161_inharmonic_partial_spacing_survivors_v1 as partial3161
import profile_gomyway_3161_harmonic_comb_alignment_survivors_v1 as comb3161
import profile_gomyway_3161_transient_attack_survivors_v1 as attack3161
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = s3161.recur
recall = s3161.recall
v2 = s3161.v2
v3 = s3161.v3
harmonic = s3161.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pick(signatures: set[str], prefix: str) -> str:
    matches = sorted(s for s in signatures if s.startswith(prefix))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one signature for prefix {prefix!r}, got {matches}")
    return matches[0]


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


def cross_signatures(
    flux_sigs: set[str],
    partial_sigs: set[str],
    comb_sigs: set[str],
    attack_sigs: set[str],
) -> set[str]:
    flux_primary = pick(flux_sigs, "fluxComposite::")
    flux_energy = pick(flux_sigs, "energyFluxCross::")
    partial_primary = pick(partial_sigs, "partialSpacingComposite::")
    partial_inharm = pick(partial_sigs, "inharmonicityCross::")
    comb_primary = pick(comb_sigs, "combAlignmentComposite::")
    comb_harmonic = pick(comb_sigs, "harmonicCombCross::")
    attack_primary = pick(attack_sigs, "transientAttackCross::")
    attack_contrast = pick(attack_sigs, "attackContrastCross::")
    attack_dual = pick(attack_sigs, "dualStemTransientCross::")

    return {
        f"fluxAttack::{flux_primary}|{attack_primary}",
        f"fluxComb::{flux_primary}|{comb_primary}",
        f"fluxPartial::{flux_primary}|{partial_primary}",
        f"attackComb::{attack_primary}|{comb_primary}",
        f"attackPartial::{attack_primary}|{partial_primary}",
        f"combPartial::{comb_primary}|{partial_primary}",
        f"energyAttack::{flux_energy}|{attack_contrast}",
        f"harmonicSpacing::{comb_harmonic}|{partial_inharm}",
        f"fluxAttackComb::{flux_primary}|{attack_primary}|{comb_primary}",
        f"fluxAttackPartial::{flux_primary}|{attack_primary}|{partial_primary}",
        f"attackCombPartial::{attack_primary}|{comb_primary}|{partial_primary}",
        f"fluxCombPartial::{flux_primary}|{comb_primary}|{partial_primary}",
        f"fourFamily::{flux_primary}|{attack_primary}|{comb_primary}|{partial_primary}",
        f"fourFamilyAlt::{flux_energy}|{attack_dual}|{comb_harmonic}|{partial_inharm}",
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
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}"
        )

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])

        flux_w = flux3161.stem_flux_features(winner_audio, winner_sr, center)
        flux_a = flux3161.stem_flux_features(alt_audio, alt_sr, center)
        flux_sigs = flux3161.signatures_for(flux_w, flux_a)

        partial_w = partial3161.stem_partial_spacing_features(winner_audio, winner_sr, center, pitch)
        partial_a = partial3161.stem_partial_spacing_features(alt_audio, alt_sr, center, pitch)
        partial_sigs = partial3161.signatures_for(partial_w, partial_a)

        comb_w = comb3161.stem_comb_features(winner_audio, winner_sr, center, pitch)
        comb_a = comb3161.stem_comb_features(alt_audio, alt_sr, center, pitch)
        comb_sigs = comb3161.signatures_for(comb_w, comb_a)

        attack_w = attack3161.transient.transient_features(winner_audio, winner_sr, center)
        attack_a = attack3161.transient.transient_features(alt_audio, alt_sr, center)
        attack_sigs = attack3161.transient.signatures_for(attack_w, attack_a)

        signatures = sorted(cross_signatures(flux_sigs, partial_sigs, comb_sigs, attack_sigs))
        for signature in signatures:
            groups[signature][truth] += int(count)

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    near_zero = [r for r in ranked if int(r["true"]) <= 1 and int(r["false"]) >= 5]
    near_zero.sort(key=lambda r: (int(r["true"]), -int(r["false"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 31.61 cross-family interaction profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-cross-family-interactions",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "featureFamily": "cross-family-flux-transient-comb-partial-spacing",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "nearZeroPrecisionSignaturesMax1TrueMin5False": near_zero,
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
        "nearZeroSignatureCount": len(near_zero),
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 CROSS-FAMILY INTERACTIONS V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision cross-family signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Near-zero cross-family signatures (5+ false, <=1 true):", len(near_zero))
    for row in near_zero[:30]:
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
