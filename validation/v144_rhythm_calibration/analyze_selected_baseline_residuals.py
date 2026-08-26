from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_measure_set_guard import measure_set_evidence  # noqa: E402
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from analyze_split_baseline import (  # noqa: E402
    fit_measure_hotspots,
    score_subset,
    signature_counts,
    split_name,
    unmatched_rows,
)
from score_selected_conjunction_candidate import score_full_candidate  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
BASELINE_NAME = "prune-triple-67348efe50436fc5"
BASELINE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
EXPECTED_FULL = {
    "pitchContentF1": 0.2909090909090909,
    "pitchTimingTolerantF1": 0.045933014354066985,
    "stringFretTimingTolerantF1": 0.031578947368421054,
    "chordPitchSetTolerantF1": 0.023496890117484452,
    "exactVoicingTolerantF1": 0.023496890117484452,
    "measureCoverageRecall": 1.0,
}
EXPECTED_CRITICAL = 1810


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reconstruct the accepted V144 rhythm baseline and build residual fit/validation/canary diagnostics."
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("selected_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("events_output", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.selected_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("selected baseline manifest classification changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("selected baseline name changed")
    if (manifest.get("transform") or {}).get("signatures") != BASELINE_SIGNATURES:
        raise ValueError("selected baseline transform changed")
    selected_info = manifest.get("selectedCandidate") or {}
    if int(selected_info.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("selected baseline event count changed")
    if selected_info.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("selected baseline event SHA changed")
    if (manifest.get("promotionScope") or {}).get("calibrationBaseline") is not True:
        raise ValueError("selected manifest is not calibration baseline")
    if (manifest.get("promotionScope") or {}).get("productionPromotionAllowed") is not False:
        raise ValueError("selected manifest unexpectedly allows Production promotion")

    stream = load_json(args.v5_render_stream)
    source_events = canonical_events(stream.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT:
        raise ValueError(f"unexpected immutable V5 event count {len(source_events)}")
    if sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event SHA changed")

    selected_events = apply_triple_prune(source_events, BASELINE_SIGNATURES)
    if len(selected_events) != BASELINE_EVENT_COUNT:
        raise ValueError(f"selected baseline reconstruction count changed: {len(selected_events)}")
    selected_sha = sha256_json(selected_events)
    if selected_sha != BASELINE_EVENT_SHA256:
        raise ValueError(f"selected baseline reconstruction SHA changed: {selected_sha}")

    measure_evidence = measure_set_evidence(source_events, selected_events)
    if measure_evidence["baselineGeneratedMeasureSetPreserved"] is not True:
        raise ValueError("accepted baseline no longer preserves source measure set")
    if measure_evidence["candidateGeneratedMeasureCount"] != 113:
        raise ValueError("accepted baseline must retain 113 generated measures")

    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(selected_events)
    config = ContextSplitConfig.from_mapping(load_json(args.config))

    full = score_full_candidate(selected_events, reference)
    if int(full["criticalMismatchCount"]) != EXPECTED_CRITICAL:
        raise ValueError("accepted baseline full critical mismatch identity changed")
    for name, expected in EXPECTED_FULL.items():
        actual = float(full["gatedMetrics"][name])
        if actual != expected:
            raise ValueError(f"accepted baseline full metric changed: {name}={actual!r}")

    split_scores: dict[str, Any] = {}
    split_rows: dict[str, tuple[list[dict[str, Any]], list[dict[str, Any]]]] = {}
    for stage in ("fit", "validation", "canary"):
        generated_subset = [row for row in generated_notes if split_name(row, config) == stage]
        reference_subset = [row for row in reference_notes if split_name(row, config) == stage]
        split_rows[stage] = (generated_subset, reference_subset)
        split_scores[stage] = score_subset(generated_subset, reference_subset)

    fit_generated, fit_reference = split_rows["fit"]
    fit_unmatched_generated, fit_unmatched_reference = unmatched_rows(
        fit_generated, fit_reference
    )

    report = {
        "schemaVersion": 14407,
        "classification": "v144-rhythm-accepted-baseline-residual-diagnostics",
        "evaluationRole": "gold-calibration-residual-analysis-not-unseen-holdout",
        "mayClaimUnseenGeneralization": False,
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "sourceEventCount": SOURCE_EVENT_COUNT,
            "sourceEventSha256": SOURCE_EVENT_SHA256,
            "reconstructedDeterministically": True,
            "generatedMeasureCount": 113,
            "baselineGeneratedMeasureSetPreserved": True,
        },
        "fullCalibration": full,
        "splits": split_scores,
        "fitOnlyResidualSignals": {
            "grossUnmatchedGeneratedNoteCount": len(fit_unmatched_generated),
            "grossUnmatchedReferenceNoteCount": len(fit_unmatched_reference),
            "falsePositiveContextSignatures": signature_counts(fit_unmatched_generated),
            "falseNegativeContextSignatures": signature_counts(fit_unmatched_reference),
            "highestPitchErrorMeasures": fit_measure_hotspots(
                fit_generated, fit_reference, limit=32
            ),
        },
        "nextCandidateConstructionContract": {
            "baselineMustBeThisAcceptedEventSha256": BASELINE_EVENT_SHA256,
            "fitLabelsMayDriveConstructionAndRanking": True,
            "validationLabelsMayDriveConstructionOrRanking": False,
            "canaryLabelsMayDriveConstructionOrRanking": False,
            "fullGoldResultsMayDriveAlternativeSelectionWithinConsumedFamily": False,
            "runtimeReferenceInputAllowed": False,
            "baselineGeneratedMeasureSetMustBePreserved": True,
            "numericThresholdsMayBeChangedFromTheseResiduals": False,
        },
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.events_output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.events_output.write_text(
        json.dumps(
            {
                "schemaVersion": 14407,
                "instrument": "rhythm",
                "candidateName": BASELINE_NAME,
                "runtimeReferenceInputUsed": False,
                "baselineGeneratedMeasureSetPreserved": True,
                "renderEvents": selected_events,
            },
            separators=(",", ":"),
        ) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
