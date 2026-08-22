from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-ablate-lowmiddecay60-nested-cv-v3.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-ablate-lowmiddecay60-nested-cv-v3-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
ABLATE_FEATURE = "mean::lowMidDecay60"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v2.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    all_features = sorted((rows[0].get("features") or {}).keys())
    if ABLATE_FEATURE not in all_features:
        raise RuntimeError(f"Expected ablation feature missing: {ABLATE_FEATURE}")
    feature_names = [f for f in all_features if f != ABLATE_FEATURE]

    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting targeted V3 stratified pairwise ablation nested CV", flush=True)
    print("Ablated feature:", ABLATE_FEATURE, flush=True)
    print("Remaining patch features:", len(feature_names), flush=True)
    print("All pairwise sampler/model/search settings are inherited unchanged from V2", flush=True)

    normal_pass, normal = v2.evaluate_scheme(
        x, y, measures, feature_names, "normal", lambda m: m % v2.OUTER_FOLDS
    )
    section_pass, section = v2.evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "section",
        lambda m: v2.v1.contiguous_fold(m, lo, hi, v2.OUTER_FOLDS),
    )
    shifted_pass, shifted = v2.evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "shiftedWindow",
        lambda m: v2.v1.shifted_fold(m, lo, hi, v2.OUTER_FOLDS),
    )

    generalizes = normal_pass and section_pass and shifted_pass
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during targeted V3 ablation CV")

    pass_count = sum(bool(r.get("passed")) for r in normal + section + shifted)
    output = {
        "schemaVersion": 3,
        "profileType": "36.76-patch-pairwise-rank-stratified-targeted-lowmiddecay60-ablation-nested-cv",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "ablationHypothesis": "failure-family split implicated mean::lowMidDecay60",
        "ablatedFeature": ABLATE_FEATURE,
        "remainingFeatureCount": len(feature_names),
        "pairSampler": "deterministic-measure-stratified",
        "maxPairs": v2.MAX_PAIRS,
        "strata": v2.STRATA,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchGeneralizes": generalizes,
        "outerFoldPassCount": pass_count,
        "outerFoldCount": 15,
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 3,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "ablatedFeature": ABLATE_FEATURE,
        "outerFoldPassCount": pass_count,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH STRATIFIED PAIRWISE RANK TARGETED ABLATION V3 COMPLETE")
    print("Ablated feature:", ABLATE_FEATURE)
    print("Outer folds passed:", pass_count, "/15")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise-rank patch V3 generalizes:", generalizes)
    print("Validated new champion: False")
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
