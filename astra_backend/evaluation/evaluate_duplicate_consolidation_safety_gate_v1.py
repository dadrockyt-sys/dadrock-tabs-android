"""Evaluate Duplicate Consolidation Safety Gate V1 on the frozen 16-case suite.

The gate decision is computed first from separator-output evidence only. Reference
source audio is used only afterward to score the action for this development-set
evaluation.
"""
from __future__ import annotations

import argparse
import csv
import json
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import tensorflow_hub as hub

from duplicate_consolidation_safety_gate_v1 import (
    ConsolidationSafetyConfig,
    decide_consolidation,
    pair_safety_metrics,
)
from evaluate_noncollinear_duplicate_stress_v1 import (
    SOURCES,
    PERTURBATIONS,
    make_split,
    energy,
)
from pair_consistency_classifier_v1 import PairClassifierConfig, classify_pair
from stem_bleed_cleanup_v1 import si_sdr
from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems

TARGET_SR = 16000
GUITAR_LABELS = {
    "Guitar",
    "Electric guitar",
    "Acoustic guitar",
    "Steel guitar, slide guitar",
    "Tapping (guitar technique)",
    "Strum",
}
BASS_LABELS = {"Bass guitar"}


def load(path: Path):
    return sf.read(path, always_2d=True, dtype="float32")


def class_names(model):
    path = model.class_map_path().numpy().decode("utf-8")
    with open(path, newline="", encoding="utf-8") as f:
        return [row["display_name"] for row in csv.DictReader(f)]


def mono16(x, fs):
    mono = np.mean(x, axis=1)
    if fs != TARGET_SR:
        g = gcd(fs, TARGET_SR)
        mono = resample_poly(mono, TARGET_SR // g, fs // g).astype(np.float32)
    return mono.astype(np.float32)


def evidence(model, names, x, fs):
    scores, _, _ = model(mono16(x, fs))
    arr = scores.numpy()
    idx = {n: i for i, n in enumerate(names)}
    gi = [idx[n] for n in GUITAR_LABELS]
    bi = [idx[n] for n in BASS_LABELS]
    return {
        "guitar": float(np.max(np.mean(arr[:, gi], axis=0))),
        "bass": float(np.max(np.mean(arr[:, bi], axis=0))),
    }


def claim_row(case_id, claimed, stems, diagnostics, ev):
    strongest = max(
        (k for k in stems if k != claimed),
        key=lambda k: diagnostics[claimed]["perCompetitor"][k]["overlapPressure"],
    )
    return {
        "mixture": case_id,
        "claimedStem": claimed,
        "claimedStemEnergy": energy(stems[claimed]),
        "claimedEvidence": ev[claimed],
        "strongestOverlapCompetitor": strongest,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture-dir", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--hub-url", default="https://tfhub.dev/google/yamnet/1")
    args = ap.parse_args()

    yam = hub.load(args.hub_url)
    names = class_names(yam)
    pair_cfg = PairClassifierConfig()
    safety_cfg = ConsolidationSafetyConfig()
    diag_cfg = DiagnosticConfig()
    rows = []

    for source_class, source_id, filename in SOURCES:
        source, fs = load(Path(args.fixture_dir) / filename)

        for mode in PERTURBATIONS:
            case_id = f"{source_id}_{mode}"
            part_a, part_b = make_split(source, fs, mode, source_class)

            if source_class == "bass":
                stems = {"guitar": part_a, "bass": part_b}
                false_claim, companion = "guitar", "bass"
                expected_state = "duplicate_bass_candidate"
            else:
                stems = {"guitar": part_b, "bass": part_a}
                false_claim, companion = "bass", "guitar"
                expected_state = "duplicate_guitar_candidate"

            mixture = stems["guitar"] + stems["bass"]
            diagnostics = diagnose_stems(mixture, stems, fs, diag_cfg)
            ev = {k: evidence(yam, names, v, fs) for k, v in stems.items()}
            g = claim_row(case_id, "guitar", stems, diagnostics, ev)
            b = claim_row(case_id, "bass", stems, diagnostics, ev)
            pair = classify_pair(g, b, pair_cfg)

            # IMPORTANT: gate decision is made before any reference-based scoring.
            metrics = pair_safety_metrics(stems["guitar"], stems["bass"], fs, safety_cfg)
            gate = decide_consolidation(pair["state"], metrics, safety_cfg)

            merged = (stems[companion] + stems[false_claim]).astype(np.float32)
            raw_score = float(si_sdr(source, stems[companion]))
            merged_score = float(si_sdr(source, merged))
            merge_delta = merged_score - raw_score

            if gate["automaticAction"] == "full_merge":
                selected = merged
                selected_score = merged_score
            else:
                selected = stems[companion]
                selected_score = raw_score

            selected_delta = selected_score - raw_score
            recon_error = float(np.max(np.abs(merged - mixture))) if gate["automaticAction"] == "full_merge" else 0.0

            rows.append({
                "id": case_id,
                "sourceClass": source_class,
                "sourceId": source_id,
                "perturbation": mode,
                "expectedPairState": expected_state,
                "observedPairState": pair["state"],
                "pairCorrect": pair["state"] == expected_state,
                "energyGapDb": float(pair["energyGapDb"]),
                "recognizerEvidence": ev,
                "safetyMetrics": metrics,
                "gate": gate,
                "rawCompanionSiSdrDb": raw_score,
                "mergedCompanionSiSdrDb": merged_score,
                "mergeImprovementDb": merge_delta,
                "selectedActionSiSdrDb": selected_score,
                "selectedActionImprovementDb": selected_delta,
                "selectedActionReconstructionMaxAbsError": recon_error,
            })

    time_rows = [r for r in rows if r["perturbation"] == "time_varying_split"]
    negative_merge_rows = [r for r in rows if r["mergeImprovementDb"] < 0.0]
    automatic_rows = [r for r in rows if r["gate"]["automaticAction"] != "none"]

    pair_accuracy = sum(r["pairCorrect"] for r in rows) / len(rows)
    time_all_merge = all(r["gate"]["decision"] == "merge_safe" for r in time_rows)
    all_negative_avoided = all(r["gate"]["automaticAction"] != "full_merge" for r in negative_merge_rows)
    min_auto_delta = min([r["selectedActionImprovementDb"] for r in automatic_rows], default=0.0)
    max_recon = max([r["selectedActionReconstructionMaxAbsError"] for r in rows], default=0.0)

    criteria = {
        "pairClassifierBehaviorPreserved": abs(pair_accuracy - 0.9375) < 1e-12,
        "allFourTimeVaryingSplitsMergeSafe": bool(time_all_merge),
        "allNegativeFullMergeCasesAvoided": bool(all_negative_avoided),
        "noAutomaticActionWorseThanMinus0_5Db": bool(min_auto_delta >= -0.5),
        "mergeReconstructionNumericallyExact": bool(max_recon <= 1e-7),
    }
    passed = all(criteria.values())

    result = {
        "schemaVersion": 1,
        "kind": "duplicate-consolidation-safety-gate-v1-evaluation",
        "pairClassifierConfig": pair_cfg.to_dict(),
        "consolidationSafetyConfig": safety_cfg.to_dict(),
        "caseCount": len(rows),
        "pairAccuracy": pair_accuracy,
        "gateDecisionCounts": {
            k: sum(r["gate"]["decision"] == k for r in rows)
            for k in ("merge_safe", "preserve_separate", "uncertain")
        },
        "automaticMergeCount": len(automatic_rows),
        "minimumAutomaticActionImprovementDb": float(min_auto_delta),
        "maximumAutomaticMergeReconstructionMaxAbsError": float(max_recon),
        "successCriteria": criteria,
        "passed": bool(passed),
        "results": rows,
        "interpretationBoundary": (
            "Frozen 16-case synthetic development suite only. Gate decisions use no reference audio. "
            "Reference source is used only for retrospective scoring. No production or real-audio action authorized."
        ),
    }

    Path(args.output_json).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
