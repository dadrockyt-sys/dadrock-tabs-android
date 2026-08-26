from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
MODAL_DIR = ROOT / "modal"
for entry in (HOLDOUT_DIR, MODAL_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_rhythm_holdout as scorer  # noqa: E402
from canonical import canonical_events  # noqa: E402
from v144_rhythm_context_split_policy import (  # noqa: E402
    ContextSplitConfig,
    context_signature,
    split_for_location,
)

EXPECTED_GLOBAL = {
    "pitchContentF1": 0.2830626450116009,
    "pitchTimingTolerantF1": 0.044547563805104405,
    "stringFretTimingTolerantF1": 0.03062645011600928,
    "chordPitchSetTolerantF1": 0.022757697456492636,
    "exactVoicingTolerantF1": 0.022757697456492636,
}
EXPECTED_CRITICAL = 1875


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def split_name(row: Mapping[str, Any], config: ContextSplitConfig) -> str:
    return split_for_location(
        int(row["measure"]),
        int(row["step"]),
        seed=config.split_seed,
        fit_percent=config.fit_percent,
        validation_percent=config.validation_percent,
    )


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


def score_subset(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    pitch_content = scorer.multiset_match(
        ((n["measure"], n["midi"]) for n in generated_notes),
        ((n["measure"], n["midi"]) for n in reference_notes),
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

    pitch_timing = scorer.metric_for_pairs(pitch_pairs, generated_notes, reference_notes)
    string_fret_timing = scorer.metric_for_pairs(position_pairs, generated_notes, reference_notes)
    pitchset = scorer.metric_for_pairs(pitchset_pairs, generated_onsets, reference_onsets)
    voicing = scorer.metric_for_pairs(voicing_pairs, generated_onsets, reference_onsets)

    return {
        "noteCounts": {
            "generated": len(generated_notes),
            "reference": len(reference_notes),
        },
        "pitchContent": metric_summary(pitch_content),
        "pitchTiming": metric_summary(pitch_timing),
        "stringFretTiming": metric_summary(string_fret_timing),
        "chordPitchSet": metric_summary(pitchset),
        "exactChordVoicing": metric_summary(voicing),
        "criticalMismatchCount": (
            len(generated_notes) - len(gross_pairs)
            + len(reference_notes) - len(gross_pairs)
        ),
        "grossMatchedPitchTimingNotes": len(gross_pairs),
    }


def unmatched_rows(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    pairs = scorer.greedy_match(
        generated_notes,
        reference_notes,
        lambda generated, ref: generated["midi"] == ref["midi"],
        scorer.GROSS_STEP_TOLERANCE,
    )
    matched_generated = {g for g, _ in pairs}
    matched_reference = {r for _, r in pairs}
    return (
        [row for i, row in enumerate(generated_notes) if i not in matched_generated],
        [row for i, row in enumerate(reference_notes) if i not in matched_reference],
    )


def signature_counts(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for row in rows:
        counts.update(context_signature(row))
    return [
        {"signature": signature, "count": count}
        for signature, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def fit_measure_hotspots(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    limit: int = 24,
) -> list[dict[str, Any]]:
    generated_by_measure: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    reference_by_measure: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in generated_notes:
        generated_by_measure[int(row["measure"])].append(row)
    for row in reference_notes:
        reference_by_measure[int(row["measure"])].append(row)

    rows: list[dict[str, Any]] = []
    for measure in sorted(set(generated_by_measure) | set(reference_by_measure)):
        metric = scorer.multiset_match(
            (int(row["midi"]) for row in generated_by_measure[measure]),
            (int(row["midi"]) for row in reference_by_measure[measure]),
        )
        rows.append(
            {
                "measure": measure,
                "generated": metric["generated"],
                "reference": metric["reference"],
                "matched": metric["matched"],
                "falsePositive": metric["falsePositive"],
                "falseNegative": metric["falseNegative"],
                "totalPitchErrors": metric["falsePositive"] + metric["falseNegative"],
                "pitchContentF1": metric["f1"],
            }
        )
    rows.sort(key=lambda row: (-row["totalPitchErrors"], row["pitchContentF1"], row["measure"]))
    return rows[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build split-isolated V144 baseline diagnostics.")
    parser.add_argument("render_stream", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("baseline_report", type=Path)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    stream = load_json(args.render_stream)
    reference = scorer.validate_reference(load_json(args.gold_reference))
    baseline = load_json(args.baseline_report)
    config = ContextSplitConfig.from_mapping(load_json(args.config))

    events = canonical_events(stream.get("events") or [])
    generated_notes, _ = scorer.flatten_generated(events)
    reference_notes, _, _ = scorer.flatten_reference(reference)

    global_score = score_subset(generated_notes, reference_notes)
    global_metrics = {
        "pitchContentF1": global_score["pitchContent"]["f1"],
        "pitchTimingTolerantF1": global_score["pitchTiming"]["f1"],
        "stringFretTimingTolerantF1": global_score["stringFretTiming"]["f1"],
        "chordPitchSetTolerantF1": global_score["chordPitchSet"]["f1"],
        "exactVoicingTolerantF1": global_score["exactChordVoicing"]["f1"],
    }
    for name, expected in EXPECTED_GLOBAL.items():
        if float(global_metrics[name]) != expected:
            raise ValueError(f"global baseline metric changed: {name}={global_metrics[name]!r}")
    if int(global_score["criticalMismatchCount"]) != EXPECTED_CRITICAL:
        raise ValueError("global critical mismatch count changed")
    if (baseline.get("evaluationRole") != "calibration-baseline-not-unseen-holdout"):
        raise ValueError("baseline report has incorrect evaluation semantics")

    split_scores: dict[str, Any] = {}
    split_rows: dict[str, tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]] = {}
    for name in ("fit", "validation", "canary"):
        generated_subset = [row for row in generated_notes if split_name(row, config) == name]
        reference_subset = [row for row in reference_notes if split_name(row, config) == name]
        split_rows[name] = (generated_subset, reference_subset)
        split_scores[name] = score_subset(generated_subset, reference_subset)

    fit_generated, fit_reference = split_rows["fit"]
    fit_false_positive_rows, fit_false_negative_rows = unmatched_rows(fit_generated, fit_reference)

    report = {
        "schemaVersion": 14401,
        "classification": "v144-rhythm-split-isolated-baseline-diagnostics",
        "evaluationRole": "gold-calibration-fit-validation-canary-diagnostics",
        "mayClaimUnseenGeneralization": False,
        "splitPolicy": {
            "seed": config.split_seed,
            "fitPercent": config.fit_percent,
            "validationPercent": config.validation_percent,
            "canaryPercent": 100 - config.fit_percent - config.validation_percent,
            "locationKey": "measure+step",
            "crossSplitMatchingAllowed": False,
        },
        "globalReproduction": {
            "gatedMetrics": global_metrics,
            "criticalMismatchCount": global_score["criticalMismatchCount"],
            "matchesPersistedFrozenV5BaselineExactly": True,
            "pdfEventFidelity": baseline["baseline"]["gatedMetrics"]["pdfEventFidelity"],
        },
        "splits": split_scores,
        "fitOnlyCalibrationSignals": {
            "grossUnmatchedGeneratedNoteCount": len(fit_false_positive_rows),
            "grossUnmatchedReferenceNoteCount": len(fit_false_negative_rows),
            "falsePositiveContextSignatures": signature_counts(fit_false_positive_rows),
            "falseNegativeContextSignatures": signature_counts(fit_false_negative_rows),
            "highestPitchErrorMeasures": fit_measure_hotspots(fit_generated, fit_reference),
        },
        "safety": {
            "fitLabelsMayDriveCalibration": True,
            "validationLabelsMayDriveCalibration": False,
            "canaryLabelsMayDriveCalibration": False,
            "v5Modified": False,
            "productionModified": False,
            "mainModified": False,
            "modalGpuInvoked": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
