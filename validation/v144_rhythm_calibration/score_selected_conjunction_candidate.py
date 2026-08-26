from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_rhythm_holdout as scorer  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402
from v144_rhythm_conjunction_prune_policy import apply_conjunction_prune  # noqa: E402

BASELINE_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
SELECTED_EVENT_SHA256 = "db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f"
SELECTED_EVENT_COUNT = 1112
SELECTED_NAME = "prune-conjunction-33ac980932c68313"
SELECTED_SIGNATURES = ["register::high", "section16::1"]
SOURCE_SELECTION_REPORT_BLOB = "b92a3638d5b8fff0e911df43fb381f89f088afd6"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_for_pairs(pairs, generated, reference) -> dict[str, Any]:
    return scorer.metric_for_pairs(pairs, generated, reference)


def metric_summary(metric: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: metric[key]
        for key in (
            "matched",
            "generated",
            "reference",
            "falsePositive",
            "falseNegative",
            "precision",
            "recall",
            "f1",
        )
        if key in metric
    }


def score_full_candidate(
    events: Sequence[Mapping[str, Any]], reference: Mapping[str, Any]
) -> dict[str, Any]:
    generated_notes, generated_rests = scorer.flatten_generated(events)
    reference_notes, reference_rests, reference_measures = scorer.flatten_reference(reference)
    generated_measures = {int(note["measure"]) for note in generated_notes}

    pitch_content = scorer.multiset_match(
        ((note["measure"], note["midi"]) for note in generated_notes),
        ((note["measure"], note["midi"]) for note in reference_notes),
    )
    pitch_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.STEP_TOLERANCE,
    )
    position_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: (
            generated["midi"] == ref["midi"]
            and generated["stringIndex"] == ref["stringIndex"]
            and generated["fret"] == ref["fret"]
        ),
        scorer.STEP_TOLERANCE,
    )
    gross_pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )

    generated_onsets = scorer.onset_groups(generated_notes)
    reference_onsets = scorer.onset_groups(reference_notes)
    pitchset_pairs = scorer.greedy_match(
        generated_onsets,
        reference_onsets,
        lambda generated, ref: generated["pitchSet"] == ref["pitchSet"],
        scorer.STEP_TOLERANCE,
    )
    voicing_pairs = scorer.greedy_match(
        generated_onsets,
        reference_onsets,
        lambda generated, ref: generated["voicing"] == ref["voicing"],
        scorer.STEP_TOLERANCE,
    )

    pitch_timing = metric_for_pairs(pitch_pairs, generated_notes, reference_notes)
    position_timing = metric_for_pairs(position_pairs, generated_notes, reference_notes)
    pitchset = metric_for_pairs(pitchset_pairs, generated_onsets, reference_onsets)
    voicing = metric_for_pairs(voicing_pairs, generated_onsets, reference_onsets)

    generated_labels = scorer.label_events(generated_notes)
    reference_labels = scorer.label_events(reference_notes)
    technique_pairs = scorer.greedy_match(
        generated_labels,
        reference_labels,
        lambda generated, ref: (
            generated["midi"] == ref["midi"]
            and generated["stringIndex"] == ref["stringIndex"]
            and generated["fret"] == ref["fret"]
            and generated["label"] == ref["label"]
        ),
        scorer.STEP_TOLERANCE,
    )
    technique = metric_for_pairs(technique_pairs, generated_labels, reference_labels)

    missing_reference_measures = sorted(reference_measures - generated_measures)
    extra_generated_measures = sorted(generated_measures - reference_measures)
    measure_coverage = {
        "referenceMeasureCount": len(reference_measures),
        "generatedMeasureCount": len(generated_measures),
        "matchedReferenceMeasures": len(reference_measures & generated_measures),
        "recall": scorer.safe_ratio(
            len(reference_measures & generated_measures), len(reference_measures)
        ),
        "missingReferenceMeasures": missing_reference_measures,
        "extraGeneratedMeasures": extra_generated_measures,
    }

    gross_unmatched_reference = len(reference_notes) - len(gross_pairs)
    gross_unmatched_generated = len(generated_notes) - len(gross_pairs)
    critical = (
        len(missing_reference_measures)
        + gross_unmatched_reference
        + gross_unmatched_generated
    )

    gated = {
        "pitchContentF1": float(pitch_content["f1"]),
        "pitchTimingTolerantF1": float(pitch_timing["f1"]),
        "stringFretTimingTolerantF1": float(position_timing["f1"]),
        "chordPitchSetTolerantF1": float(pitchset["f1"]),
        "exactVoicingTolerantF1": float(voicing["f1"]),
        "measureCoverageRecall": float(measure_coverage["recall"]),
    }

    return {
        "generatedEventCount": len(generated_notes),
        "referenceNoteCount": len(reference_notes),
        "gatedMetrics": gated,
        "criticalMismatchCount": int(critical),
        "criticalMismatchBreakdown": {
            "missingReferenceMeasures": len(missing_reference_measures),
            "grossUnmatchedReferenceNotes": gross_unmatched_reference,
            "grossUnmatchedGeneratedNotes": gross_unmatched_generated,
        },
        "diagnostics": {
            "pitchContent": metric_summary(pitch_content),
            "pitchTiming": metric_summary(pitch_timing),
            "stringFretTiming": metric_summary(position_timing),
            "chordPitchSet": metric_summary(pitchset),
            "exactChordVoicing": metric_summary(voicing),
            "technique": metric_summary(technique),
            "measureCoverage": measure_coverage,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize and score the accepted V144 conjunction candidate against the full gold calibration reference."
    )
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("baseline_report", type=Path)
    parser.add_argument("selection_report", type=Path)
    parser.add_argument("candidate_spec", type=Path)
    parser.add_argument("score_report", type=Path)
    parser.add_argument("events_output", type=Path)
    args = parser.parse_args()

    baseline_stream = load_json(args.render_stream)
    baseline_events = canonical_events(baseline_stream.get("events") or [])
    if len(baseline_events) != 1209:
        raise ValueError(f"unexpected baseline event count: {len(baseline_events)}")
    if sha256_json(baseline_events) != BASELINE_EVENT_SHA256:
        raise ValueError("immutable V5 canonical event identity changed")

    selection = load_json(args.selection_report)
    if selection.get("selected") != SELECTED_NAME or selection.get("promotionAllowed") is not True:
        raise ValueError("accepted conjunction selection report changed")
    locked = selection.get("locked") or {}
    if locked.get("signatures") != SELECTED_SIGNATURES:
        raise ValueError("accepted conjunction signatures changed")
    if locked.get("eventSha256") != SELECTED_EVENT_SHA256:
        raise ValueError("accepted conjunction event SHA changed")
    if int(locked.get("eventCount") or 0) != SELECTED_EVENT_COUNT:
        raise ValueError("accepted conjunction event count changed")
    if (selection.get("validation") or {}).get("passed") is not True:
        raise ValueError("accepted conjunction validation gate no longer passes")
    if (selection.get("canary") or {}).get("passed") is not True:
        raise ValueError("accepted conjunction canary gate no longer passes")

    selected_events = apply_conjunction_prune(baseline_events, SELECTED_SIGNATURES)
    selected_sha = sha256_json(selected_events)
    if len(selected_events) != SELECTED_EVENT_COUNT or selected_sha != SELECTED_EVENT_SHA256:
        raise ValueError(
            f"selected candidate reconstruction mismatch count={len(selected_events)} sha={selected_sha}"
        )

    reference = scorer.validate_reference(load_json(args.gold_reference))
    selected_score = score_full_candidate(selected_events, reference)
    baseline = load_json(args.baseline_report)
    baseline_metrics = (baseline.get("baseline") or {}).get("gatedMetrics") or {}
    baseline_critical = int((baseline.get("baseline") or {}).get("criticalMismatchCount") or 0)

    deltas = {
        name: float(selected_score["gatedMetrics"][name]) - float(baseline_metrics[name])
        for name in (
            "pitchContentF1",
            "pitchTimingTolerantF1",
            "stringFretTimingTolerantF1",
            "chordPitchSetTolerantF1",
            "exactVoicingTolerantF1",
            "measureCoverageRecall",
        )
    }
    critical_delta = int(selected_score["criticalMismatchCount"]) - baseline_critical

    spec = {
        "schemaVersion": 14403,
        "classification": "v144-rhythm-selected-calibration-candidate",
        "instrument": "rhythm",
        "name": SELECTED_NAME,
        "sourceSelectionReportGitBlob": SOURCE_SELECTION_REPORT_BLOB,
        "sourceCandidate": {
            "role": "immutable-v5-read-only-baseline",
            "eventCount": 1209,
            "eventSha256": BASELINE_EVENT_SHA256,
        },
        "transform": {
            "type": "two-signature-conjunction-prune",
            "signatures": SELECTED_SIGNATURES,
            "runtimeInputs": "reference-free-event-context-only",
            "professionalReferenceRuntimeInput": False,
        },
        "selectedCandidate": {
            "eventCount": SELECTED_EVENT_COUNT,
            "eventSha256": SELECTED_EVENT_SHA256,
        },
        "selectionEvidence": {
            "fitPassed": True,
            "validationPassed": True,
            "canaryPassed": True,
            "promotionScope": "v144-calibration-only",
            "mayPromoteProduction": False,
            "mayClaimUnseenGeneralization": False,
        },
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
            "pdfEventFidelityMustRemainExactlyOne": True,
        },
    }

    report = {
        "schemaVersion": 14403,
        "classification": "v144-rhythm-selected-candidate-full-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "instrument": "rhythm",
        "candidateName": SELECTED_NAME,
        "candidateEventCount": SELECTED_EVENT_COUNT,
        "candidateEventSha256": SELECTED_EVENT_SHA256,
        "referenceRole": "gold-calibration-reference-not-unseen-holdout",
        "score": selected_score,
        "baselineComparison": {
            "baselineEventSha256": BASELINE_EVENT_SHA256,
            "gatedMetricDeltas": deltas,
            "criticalMismatchDelta": critical_delta,
        },
        "pdfEventFidelity": None,
        "pdfEventSha256": None,
        "near100CalibrationTargetReached": False,
        "mayClaimUnseenGeneralization": False,
        "safety": {
            "v5Modified": False,
            "mainModified": False,
            "productionModified": False,
            "runtimeReferenceInputUsed": False,
            "modalGpuInvoked": False,
            "pdfEventFidelityReproofRequired": True,
        },
    }

    args.candidate_spec.parent.mkdir(parents=True, exist_ok=True)
    args.score_report.parent.mkdir(parents=True, exist_ok=True)
    args.events_output.parent.mkdir(parents=True, exist_ok=True)
    args.candidate_spec.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.score_report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.events_output.write_text(
        json.dumps(
            {
                "schemaVersion": 14403,
                "instrument": "rhythm",
                "candidateName": SELECTED_NAME,
                "runtimeReferenceInputUsed": False,
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
