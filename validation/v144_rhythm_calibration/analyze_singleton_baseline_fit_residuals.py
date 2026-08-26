from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
SEARCH_DIR = ROOT / "validation" / "v144_rhythm_calibration"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, SEARCH_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from analyze_current_baseline_fit_mechanisms import same_onset_pitch_mechanisms  # noqa: E402
from analyze_current_baseline_fit_onset_topology import analyze_onset_topology  # noqa: E402
from analyze_split_baseline import split_name  # noqa: E402
from search_atomic_singleton_onset_replacements import (  # noqa: E402
    ACCEPTED_EVENT_COUNT as PRIOR_EVENT_COUNT,
    ACCEPTED_EVENT_SHA256 as PRIOR_EVENT_SHA256,
    ACCEPTED_GENERATED_MEASURE_COUNT as PRIOR_MEASURE_COUNT,
    SOURCE_EVENT_COUNT,
    SOURCE_EVENT_SHA256,
    changed_event_count,
    reconstruct_accepted_baseline,
)
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_singleton_onset_replacement_policy import (  # noqa: E402
    apply_singleton_onset_replacement_rule,
)

REPORT_SCHEMA_VERSION = 14422
BASELINE_NAME = "singleton-onset-replace-be9e9aa7a734e3cd"
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "4e6f9f247134f79f30a5448515c52a6ca1012c1f1314c3458b448582999e3881"
BASELINE_MEASURE_COUNT = 113
BASELINE_CHANGED_EVENT_COUNT = 110
CONTEXT_SIGNATURE = "stepParity::0"
SOURCE_STRING_INDEX = 0
SOURCE_PITCH_CLASS = 4
TARGET_STRING_INDEX = 3
SEMITONE_SHIFT = -12


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def reconstruct_selected_baseline(source_events: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Reconstruct the accepted singleton baseline without opening gold labels."""
    prior = reconstruct_accepted_baseline(source_events)
    if len(prior) != PRIOR_EVENT_COUNT or sha256_json(prior) != PRIOR_EVENT_SHA256:
        raise ValueError("prior accepted pitch-position baseline identity changed")
    if len({int(row["measure"]) for row in prior}) != PRIOR_MEASURE_COUNT:
        raise ValueError("prior accepted pitch-position baseline measure count changed")

    selected = canonical_events(
        apply_singleton_onset_replacement_rule(
            prior,
            CONTEXT_SIGNATURE,
            SOURCE_STRING_INDEX,
            SOURCE_PITCH_CLASS,
            TARGET_STRING_INDEX,
            SEMITONE_SHIFT,
            maximum_abs_semitone_shift=12,
        )
    )
    if len(selected) != BASELINE_EVENT_COUNT:
        raise ValueError("selected singleton baseline event count changed")
    if sha256_json(selected) != BASELINE_EVENT_SHA256:
        raise ValueError("selected singleton baseline event SHA changed")
    if len({int(row["measure"]) for row in selected}) != BASELINE_MEASURE_COUNT:
        raise ValueError("selected singleton baseline measure count changed")
    changed = changed_event_count(
        prior,
        selected,
        expected_context_signature=CONTEXT_SIGNATURE,
        expected_source_string_index=SOURCE_STRING_INDEX,
        expected_source_pitch_class=SOURCE_PITCH_CLASS,
        expected_target_string_index=TARGET_STRING_INDEX,
        expected_semitone_shift=SEMITONE_SHIFT,
    )
    if changed != BASELINE_CHANGED_EVENT_COUNT:
        raise ValueError("selected singleton baseline changed-event count changed")
    return selected


def analyze_fit_residuals(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Return descriptive aggregate FIT residuals only; never candidate rules or shifts."""
    generated = [dict(row) for row in generated_notes]
    reference = [dict(row) for row in reference_notes]
    topology = analyze_onset_topology(generated, reference)
    onset = same_onset_pitch_mechanisms(generated, reference)

    pitch_content = scorer.multiset_match(
        ((row["measure"], row["midi"]) for row in generated),
        ((row["measure"], row["midi"]) for row in reference),
    )
    tight_pitch_pairs = scorer.greedy_match(
        generated,
        reference,
        lambda generated_row, reference_row: generated_row["midi"] == reference_row["midi"],
        scorer.STEP_TOLERANCE,
    )
    gross_pitch_pairs = scorer.greedy_match(
        generated,
        reference,
        lambda generated_row, reference_row: generated_row["midi"] == reference_row["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )
    position_pairs = scorer.greedy_match(
        generated,
        reference,
        lambda generated_row, reference_row: (
            generated_row["midi"] == reference_row["midi"]
            and generated_row["stringIndex"] == reference_row["stringIndex"]
            and generated_row["fret"] == reference_row["fret"]
        ),
        scorer.STEP_TOLERANCE,
    )

    generated_count = len(generated)
    reference_count = len(reference)
    pitch_matched = int(pitch_content["matched"])
    tight_matched = len(tight_pitch_pairs)
    gross_matched = len(gross_pitch_pairs)
    position_matched = len(position_pairs)

    mechanisms = {
        **onset,
        "sameMeasurePitchMatchesDisplacedFromExactOnset": max(
            0, pitch_matched - onset["exactOnsetExactPitchNotes"]
        ),
        "samePitchTimingMatchesRecoveredOnlyByGrossTwoStepTolerance": max(
            0, gross_matched - tight_matched
        ),
        "sameMeasurePitchMatchesStillOutsideGrossTwoStepToleranceOrCompeting": max(
            0, pitch_matched - gross_matched
        ),
        "correctPitchTimingButWrongStringFret": max(0, tight_matched - position_matched),
        "grossUnmatchedGeneratedNotes": generated_count - gross_matched,
        "grossUnmatchedReferenceNotes": reference_count - gross_matched,
        "pitchContentFalsePositiveNotes": generated_count - pitch_matched,
        "pitchContentFalseNegativeNotes": reference_count - pitch_matched,
    }

    return {
        "generatedNoteCount": generated_count,
        "referenceNoteCount": reference_count,
        "pitchContentMatchedNotes": pitch_matched,
        "tightPitchTimingMatchedNotes": tight_matched,
        "grossPitchTimingMatchedNotes": gross_matched,
        "exactStringFretTimingMatchedNotes": position_matched,
        "mechanisms": dict(sorted(mechanisms.items())),
        **topology,
    }


def diagnostic_contract() -> dict[str, Any]:
    return {
        "candidateConstructionPerformed": False,
        "candidateRankingPerformed": False,
        "candidateSelectionPerformed": False,
        "candidateRuleOrShiftHistogramEmitted": False,
        "validationLabelsUsedForDiagnostic": False,
        "canaryLabelsUsedForDiagnostic": False,
        "interpretationBoundary": {
            "aggregateFitResidualsOnly": True,
            "mayInformMateriallyDistinctFamilyUnit": True,
            "mayRankSpecificRuleOrShift": False,
            "validationMayInformFamilyShape": False,
            "canaryMayInformFamilyShape": False,
            "consumedFamilyResultsMayInformFamilyShape": False,
            "fixedSelectorThresholdsMayChange": False,
            "runtimeReferenceInputAllowed": False,
        },
    }


def _validate_manifest(manifest: Mapping[str, Any]) -> None:
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("accepted singleton manifest classification changed")
    if manifest.get("status") != "accepted-calibration-baseline-not-production":
        raise ValueError("accepted singleton manifest status changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("accepted singleton baseline name changed")

    transform = manifest.get("transform") or {}
    expected_transform = {
        "contextSignature": CONTEXT_SIGNATURE,
        "sourceStringIndex": SOURCE_STRING_INDEX,
        "sourcePitchClass": SOURCE_PITCH_CLASS,
        "targetStringIndex": TARGET_STRING_INDEX,
        "semitoneShift": SEMITONE_SHIFT,
        "changedEventCount": BASELINE_CHANGED_EVENT_COUNT,
    }
    for key, expected in expected_transform.items():
        if transform.get(key) != expected:
            raise ValueError(f"accepted singleton transform {key} changed")
    if transform.get("professionalReferenceRuntimeInput") is not False:
        raise ValueError("accepted singleton transform unexpectedly permits runtime reference")

    selected = manifest.get("selectedCandidate") or {}
    if int(selected.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("accepted singleton event count changed")
    if selected.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("accepted singleton event SHA changed")
    if selected.get("pdfEventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("accepted singleton PDF event SHA changed")
    if float(selected.get("pdfEventFidelity") or 0.0) != 1.0:
        raise ValueError("accepted singleton PDF fidelity changed")
    if int(selected.get("generatedMeasureCount") or 0) != BASELINE_MEASURE_COUNT:
        raise ValueError("accepted singleton generated measure count changed")

    promotion = manifest.get("promotionScope") or {}
    if promotion.get("calibrationBaseline") is not True:
        raise ValueError("accepted singleton manifest is not a calibration baseline")
    if promotion.get("productionPromotionAllowed") is not False:
        raise ValueError("accepted singleton manifest unexpectedly allows Production promotion")
    if promotion.get("mayClaimUnseenGeneralization") is not False:
        raise ValueError("accepted singleton manifest unexpectedly allows unseen-generalization claim")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnostic-only aggregate FIT residual topology/mechanism analysis for the accepted "
            "V144 Rhythm singleton baseline. It constructs, ranks, selects, validates, canaries, "
            "and promotes no candidate."
        )
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("accepted_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.accepted_manifest)
    _validate_manifest(manifest)

    v5_payload = load_json(args.v5_render_stream)
    source_events = canonical_events(v5_payload.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT:
        raise ValueError("immutable V5 event count changed")
    if sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event SHA changed")

    # Gold labels remain unopened until accepted-baseline identity is reconstructed and proven.
    baseline_events = reconstruct_selected_baseline(source_events)

    config = ContextSplitConfig.from_mapping(load_json(args.config))
    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(baseline_events)
    fit_generated = [row for row in generated_notes if split_name(row, config) == "fit"]
    fit_reference = [row for row in reference_notes if split_name(row, config) == "fit"]

    report = {
        "schemaVersion": REPORT_SCHEMA_VERSION,
        "classification": "v144-rhythm-singleton-baseline-fit-residual-topology-mechanisms",
        "evaluationRole": "gold-calibration-fit-only-accepted-singleton-baseline-aggregate-diagnostic",
        "mayClaimUnseenGeneralization": False,
        **diagnostic_contract(),
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "generatedMeasureCount": BASELINE_MEASURE_COUNT,
            "changedEventCountFromPriorBaseline": BASELINE_CHANGED_EVENT_COUNT,
            "referenceFreeReconstructionBeforeLabels": True,
        },
        "fit": analyze_fit_residuals(fit_generated, fit_reference),
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
