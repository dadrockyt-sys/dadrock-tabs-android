from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from canonical import canonical_events, sha256_json  # noqa: E402
import score_rhythm_holdout as scorer  # noqa: E402
from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_triple_conjunction_policy import apply_triple_prune  # noqa: E402
from analyze_split_baseline import score_subset, split_name  # noqa: E402

SOURCE_EVENT_COUNT = 1209
SOURCE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
BASELINE_NAME = "prune-triple-67348efe50436fc5"
BASELINE_SIGNATURES = ["register::high", "section16::1", "stepParity::0"]
BASELINE_EVENT_COUNT = 1144
BASELINE_EVENT_SHA256 = "68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3"
NEAR_100 = 0.99
EXPECTED_FIT = {
    "generated": 643,
    "reference": 594,
    "pitchContentMatched": 138,
    "pitchTimingMatched": 28,
    "stringFretTimingMatched": 20,
    "criticalMismatchCount": 1105,
    "pitchContentF1": 0.2231204527081649,
    "pitchTimingF1": 0.04527081649151172,
    "stringFretTimingF1": 0.03233629749393695,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def deletion_only_ceiling(matched: int, reference: int) -> dict[str, Any]:
    """Best possible PRF if an oracle may only delete generated false positives.

    The oracle keeps every currently matched generated item and deletes every other
    generated item. It cannot insert a missing reference item, repitch a note, move
    an onset, or change string/fret. Therefore recall is permanently bounded by the
    current matched/reference ratio.
    """
    if matched < 0 or reference < 0 or matched > reference:
        raise ValueError("invalid matched/reference counts")
    metric = scorer.prf(matched, matched, reference)
    return {
        **metric,
        "oracleDeletesAllGeneratedFalsePositives": True,
        "oraclePreservesAllCurrentlyMatchedGeneratedItems": True,
        "mayInsertMissingReferenceItems": False,
        "mayRepitchGeneratedItems": False,
        "mayMoveGeneratedOnsets": False,
        "mayChangeStringOrFret": False,
    }


def assert_fit_identity(score: Mapping[str, Any]) -> None:
    counts = score["noteCounts"]
    if int(counts["generated"]) != EXPECTED_FIT["generated"]:
        raise ValueError("accepted baseline fit generated-note count changed")
    if int(counts["reference"]) != EXPECTED_FIT["reference"]:
        raise ValueError("accepted baseline fit reference-note count changed")
    if int(score["pitchContent"]["matched"]) != EXPECTED_FIT["pitchContentMatched"]:
        raise ValueError("accepted baseline fit pitch-content matched count changed")
    if int(score["pitchTiming"]["matched"]) != EXPECTED_FIT["pitchTimingMatched"]:
        raise ValueError("accepted baseline fit pitch-timing matched count changed")
    if int(score["stringFretTiming"]["matched"]) != EXPECTED_FIT["stringFretTimingMatched"]:
        raise ValueError("accepted baseline fit string/fret matched count changed")
    if int(score["criticalMismatchCount"]) != EXPECTED_FIT["criticalMismatchCount"]:
        raise ValueError("accepted baseline fit critical mismatch count changed")
    for key, metric_name in (
        ("pitchContentF1", "pitchContent"),
        ("pitchTimingF1", "pitchTiming"),
        ("stringFretTimingF1", "stringFretTiming"),
    ):
        if float(score[metric_name]["f1"]) != EXPECTED_FIT[key]:
            raise ValueError(f"accepted baseline fit metric changed: {metric_name}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute fit-only oracle ceilings for deletion/pruning-only V144 rhythm corrections."
    )
    parser.add_argument("v5_render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("selected_manifest", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    manifest = load_json(args.selected_manifest)
    if manifest.get("classification") != "v144-rhythm-selected-calibration-baseline":
        raise ValueError("selected baseline manifest classification changed")
    if manifest.get("name") != BASELINE_NAME:
        raise ValueError("selected baseline name changed")
    if (manifest.get("transform") or {}).get("signatures") != BASELINE_SIGNATURES:
        raise ValueError("selected baseline transform changed")
    selected = manifest.get("selectedCandidate") or {}
    if int(selected.get("eventCount") or 0) != BASELINE_EVENT_COUNT:
        raise ValueError("selected baseline event count changed")
    if selected.get("eventSha256") != BASELINE_EVENT_SHA256:
        raise ValueError("selected baseline event SHA changed")

    stream = load_json(args.v5_render_stream)
    source_events = canonical_events(stream.get("events") or [])
    if len(source_events) != SOURCE_EVENT_COUNT:
        raise ValueError("immutable V5 event count changed")
    if sha256_json(source_events) != SOURCE_EVENT_SHA256:
        raise ValueError("immutable V5 event SHA changed")

    baseline_events = apply_triple_prune(source_events, BASELINE_SIGNATURES)
    if len(baseline_events) != BASELINE_EVENT_COUNT:
        raise ValueError("accepted baseline reconstruction event count changed")
    if sha256_json(baseline_events) != BASELINE_EVENT_SHA256:
        raise ValueError("accepted baseline reconstruction SHA changed")

    reference = scorer.validate_reference(load_json(args.gold_reference))
    reference_notes, _, _ = scorer.flatten_reference(reference)
    generated_notes, _ = scorer.flatten_generated(baseline_events)
    config = ContextSplitConfig.from_mapping(load_json(args.config))

    # Deliberately construct only the fit rows. Validation/canary rows are never
    # materialized, scored, summarized, or used to choose a mechanism here.
    fit_generated = [row for row in generated_notes if split_name(row, config) == "fit"]
    fit_reference = [row for row in reference_notes if split_name(row, config) == "fit"]
    fit_score = score_subset(fit_generated, fit_reference)
    assert_fit_identity(fit_score)

    reference_count = int(fit_score["noteCounts"]["reference"])
    pitch_content_ceiling = deletion_only_ceiling(
        int(fit_score["pitchContent"]["matched"]), reference_count
    )
    pitch_timing_ceiling = deletion_only_ceiling(
        int(fit_score["pitchTiming"]["matched"]), reference_count
    )
    string_fret_ceiling = deletion_only_ceiling(
        int(fit_score["stringFretTiming"]["matched"]), reference_count
    )

    report = {
        "schemaVersion": 14409,
        "classification": "v144-rhythm-fit-only-deletion-pruning-ceiling",
        "evaluationRole": "accepted-baseline-fit-only-mechanism-diagnostic-not-unseen-holdout",
        "mayClaimUnseenGeneralization": False,
        "baseline": {
            "name": BASELINE_NAME,
            "eventCount": BASELINE_EVENT_COUNT,
            "eventSha256": BASELINE_EVENT_SHA256,
            "reconstructedDeterministically": True,
        },
        "fitOnly": {
            "noteCounts": fit_score["noteCounts"],
            "criticalMismatchCount": fit_score["criticalMismatchCount"],
            "current": {
                "pitchContent": fit_score["pitchContent"],
                "pitchTiming": fit_score["pitchTiming"],
                "stringFretTiming": fit_score["stringFretTiming"],
            },
            "oracleDeletionOnlyCeilings": {
                "pitchContent": pitch_content_ceiling,
                "pitchTiming": pitch_timing_ceiling,
                "stringFretTiming": string_fret_ceiling,
            },
        },
        "mechanismConclusion": {
            "near100Threshold": NEAR_100,
            "pitchContentNear100ReachableByDeletionOnlyOnFit": float(pitch_content_ceiling["f1"]) >= NEAR_100,
            "pitchTimingNear100ReachableByDeletionOnlyOnFit": float(pitch_timing_ceiling["f1"]) >= NEAR_100,
            "stringFretTimingNear100ReachableByDeletionOnlyOnFit": float(string_fret_ceiling["f1"]) >= NEAR_100,
            "pureDeletionCanRecoverMissingReferenceNotes": False,
            "pureDeletionCanCorrectWrongPitch": False,
            "pureDeletionCanCorrectWrongOnset": False,
            "pureDeletionCanCorrectWrongStringOrFret": False,
            "materiallyDifferentCorrectionMechanismRequiredForNear100OnFit": True,
        },
        "isolation": {
            "fitLabelsOpened": True,
            "validationLabelsOpened": False,
            "canaryLabelsOpened": False,
            "fullGoldUsedToChooseMechanism": False,
            "candidateRankingPerformed": False,
            "candidateSelectionPerformed": False,
            "numericThresholdsChanged": False,
            "runtimeReferenceInputAllowed": False,
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
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
