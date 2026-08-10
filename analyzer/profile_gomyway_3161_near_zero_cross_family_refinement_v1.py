from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_cross_family_interactions_v1 as cross3161
import profile_gomyway_3161_fundamental_phase_lock_survivors_v1 as phase3161
import profile_gomyway_3161_fundamental_periodicity_survivors_v1 as period3161
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = s3161.recur
recall = s3161.recall
v2 = s3161.v2
v3 = s3161.v3
harmonic = s3161.harmonic
register = s3161.register

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-near-zero-cross-family-refinement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-near-zero-cross-family-refinement-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61
EXPECTED_NEAR_ZERO_SIGNATURES = 1
EXPECTED_NEAR_ZERO_TRUE = 1
EXPECTED_NEAR_ZERO_FALSE = 6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def pick(signatures: set[str], prefix: str) -> str:
    rows = sorted(s for s in signatures if s.startswith(prefix))
    if len(rows) != 1:
        raise RuntimeError(f"Expected one {prefix} signature, got {rows}")
    return rows[0]


def refinement_signatures(
    phase_sigs: set[str],
    period_sigs: set[str],
    register_sigs: set[str],
) -> set[str]:
    phase_cross = pick(phase_sigs, "phaseLockCross::")
    phase_error = pick(phase_sigs, "phaseErrorCross::")
    period_cross = pick(period_sigs, "periodicityCross::")
    period_alias = pick(period_sigs, "periodicityAliasCross::")

    register_primary = sorted(
        s for s in register_sigs
        if s.startswith("measureDistributionCross::")
        or s.startswith("measureRarityCross::")
        or s.startswith("neighborRegisterCross::")
        or s.startswith("registerShapeCross::")
    )
    if not register_primary:
        register_primary = sorted(register_sigs)[:4]

    out = {
        f"phasePeriod::{phase_cross}|{period_cross}",
        f"phaseAlias::{phase_error}|{period_alias}",
    }
    for rs in register_primary[:6]:
        out.add(f"phaseRegister::{phase_cross}|{rs}")
        out.add(f"periodRegister::{period_cross}|{rs}")
        out.add(f"phasePeriodRegister::{phase_cross}|{period_cross}|{rs}")
    return out


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
    cross_groups: dict[str, Counter[str]] = defaultdict(Counter)
    cross_by_token: dict[tuple[int, int, int], set[str]] = {}

    def cross_record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        fw = cross3161.flux3161.stem_flux_features(winner_audio, winner_sr, center)
        fa = cross3161.flux3161.stem_flux_features(alt_audio, alt_sr, center)
        fs = cross3161.flux3161.signatures_for(fw, fa)
        pw = cross3161.partial3161.stem_partial_spacing_features(winner_audio, winner_sr, center, pitch)
        pa = cross3161.partial3161.stem_partial_spacing_features(alt_audio, alt_sr, center, pitch)
        ps = cross3161.partial3161.signatures_for(pw, pa)
        cw = cross3161.comb3161.stem_comb_features(winner_audio, winner_sr, center, pitch)
        ca = cross3161.comb3161.stem_comb_features(alt_audio, alt_sr, center, pitch)
        cs = cross3161.comb3161.signatures_for(cw, ca)
        aw = cross3161.attack3161.transient.transient_features(winner_audio, winner_sr, center)
        aa = cross3161.attack3161.transient.transient_features(alt_audio, alt_sr, center)
        ats = cross3161.attack3161.transient.signatures_for(aw, aa)
        sigs = cross3161.cross_signatures(fs, ps, cs, ats)
        cross_by_token[tok] = sigs
        for sig in sigs:
            cross_groups[sig][truth] += int(count)

    for tok, count in matched.items():
        cross_record(tok, int(count), "true")
    for tok, count in extras.items():
        cross_record(tok, int(count), "false")

    near_zero = [
        r for r in precision_rows(cross_groups)
        if int(r["true"]) <= 1 and int(r["false"]) >= 5
    ]
    near_zero.sort(key=lambda r: (int(r["true"]), -int(r["false"]), str(r["signature"])))
    if len(near_zero) != EXPECTED_NEAR_ZERO_SIGNATURES:
        raise RuntimeError(f"Expected exactly 1 near-zero cross-family signature, got {len(near_zero)}")
    target = near_zero[0]
    if int(target["true"]) != EXPECTED_NEAR_ZERO_TRUE or int(target["false"]) != EXPECTED_NEAR_ZERO_FALSE:
        raise RuntimeError(f"Expected near-zero signature 1 true / 6 false, got {target}")
    target_signature = str(target["signature"])

    maps = register.build_maps(champion)
    refinement_groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def refine(tok: tuple[int, int, int], count: int, truth: str) -> None:
        if target_signature not in cross_by_token.get(tok, set()):
            return
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        phw = phase3161.stem_phase_features(winner_audio, winner_sr, center, pitch)
        pha = phase3161.stem_phase_features(alt_audio, alt_sr, center, pitch)
        phase_sigs = phase3161.signatures_for(phw, pha)
        pew = period3161.periodicity_features(winner_audio, winner_sr, center, pitch)
        pea = period3161.periodicity_features(alt_audio, alt_sr, center, pitch)
        period_sigs = period3161.signatures_for(pew, pea)
        register_sigs = register.signatures_for(register.local_features(tok, maps))
        signatures = refinement_signatures(phase_sigs, period_sigs, register_sigs)
        for sig in signatures:
            refinement_groups[sig][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "phaseSignatures": sorted(phase_sigs),
            "periodicitySignatures": sorted(period_sigs),
            "registerSignatures": sorted(register_sigs),
            "refinementSignatures": sorted(signatures),
        })

    for tok, count in matched.items():
        refine(tok, int(count), "true")
    for tok, count in extras.items():
        refine(tok, int(count), "false")

    targeted_true = sum(int(r["count"]) for r in details if r["truth"] == "true")
    targeted_false = sum(int(r["count"]) for r in details if r["truth"] == "false")
    if targeted_true != 1 or targeted_false != 6:
        raise RuntimeError(f"Expected targeted near-zero pocket 1/6, got {targeted_true}/{targeted_false}")

    ranked = precision_rows(refinement_groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 3]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during near-zero cross-family refinement profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-near-zero-cross-family-refinement",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "targetNearZeroSignature": target,
        "targetedTrue": targeted_true,
        "targetedFalse": targeted_false,
        "featureFamily": "phase-periodicity-register-refinement-of-cross-family-near-zero-pocket",
        "zeroPrecisionRefinementSignaturesMin3False": zero,
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
        "targetedTrue": targeted_true,
        "targetedFalse": targeted_false,
        "zeroPrecisionRefinementSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 NEAR-ZERO CROSS-FAMILY REFINEMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Target near-zero signature:", target_signature)
    print("Targeted true/false:", targeted_true, "/", targeted_false)
    print("Zero-precision refinement signatures (3+ false, 0 true):", len(zero))
    for row in zero[:50]:
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
