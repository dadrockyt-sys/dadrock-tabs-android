#!/usr/bin/env python3
"""Score a frozen Jimmy PAIge Rhythm transcription against the professional holdout.

CRITICAL ORDER: this program validates the freeze manifest, frozen snapshot hash, safety
flags and 100% PDF-event fidelity *before* opening the human-reference JSON. It is a
post-hoc scorer only and never writes corrections back into analyzer output.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REFERENCE_DIR = (HERE / "reference").resolve()
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from canonical import OPEN_MIDI, canonical_events, sha256_json  # noqa: E402

NEAR_100 = 0.99
STEP_TOLERANCE = 0.50
GROSS_STEP_TOLERANCE = 2.00
DURATION_TOLERANCE = 0.25
EPSILON = 1e-9


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def safe_ratio(num: int | float, den: int | float, *, empty: float = 1.0) -> float:
    return empty if den == 0 else float(num) / float(den)


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = safe_ratio(matched, generated)
    recall = safe_ratio(matched, reference)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "matched": matched,
        "generated": generated,
        "reference": reference,
        "falsePositive": generated - matched,
        "falseNegative": reference - matched,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def multiset_match(generated: Iterable[tuple[Any, ...]], reference: Iterable[tuple[Any, ...]]) -> dict[str, Any]:
    g = Counter(generated)
    r = Counter(reference)
    matched = sum((g & r).values())
    return prf(matched, sum(g.values()), sum(r.values()))


def greedy_match(
    generated: Sequence[Mapping[str, Any]],
    reference: Sequence[Mapping[str, Any]],
    compatible: Callable[[Mapping[str, Any], Mapping[str, Any]], bool],
    max_step_delta: float,
) -> list[tuple[int, int]]:
    candidates: list[tuple[float, int, int]] = []
    for gi, gen in enumerate(generated):
        for ri, ref in enumerate(reference):
            if gen["measure"] != ref["measure"] or not compatible(gen, ref):
                continue
            delta = abs(float(gen["step"]) - float(ref["step"]))
            if delta <= max_step_delta + EPSILON:
                candidates.append((delta, gi, ri))
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    used_g: set[int] = set()
    used_r: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for _, gi, ri in candidates:
        if gi in used_g or ri in used_r:
            continue
        used_g.add(gi)
        used_r.add(ri)
        pairs.append((gi, ri))
    return pairs


def metric_for_pairs(pairs: Sequence[tuple[int, int]], generated: Sequence[Any], reference: Sequence[Any]) -> dict[str, Any]:
    return prf(len(pairs), len(generated), len(reference))


def normalize_labels(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(set(str(label).strip() for label in value if str(label).strip()))


def flatten_reference(reference: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[int]]:
    notes: list[dict[str, Any]] = []
    rests: list[dict[str, Any]] = []
    declared_measures: set[int] = set()
    seen_measure_numbers: set[int] = set()

    measures = reference.get("measures")
    if not isinstance(measures, list) or not measures:
        raise ValueError("complete professional reference requires a non-empty measures array")

    for measure_obj in measures:
        if not isinstance(measure_obj, Mapping):
            raise ValueError("reference measure must be an object")
        measure = int(measure_obj.get("measure"))
        if measure < 1 or measure in seen_measure_numbers:
            raise ValueError(f"invalid or duplicate reference measure {measure}")
        seen_measure_numbers.add(measure)
        declared_measures.add(measure)
        events = measure_obj.get("events")
        if not isinstance(events, list):
            raise ValueError(f"reference measure {measure} events must be an array")

        for onset in events:
            if not isinstance(onset, Mapping):
                raise ValueError(f"reference measure {measure} onset must be an object")
            step = float(onset.get("step"))
            if not 0 <= step < 16:
                raise ValueError(f"reference measure {measure} has invalid step {step}")
            onset_techniques = normalize_labels(onset.get("techniques"))
            onset_duration = onset.get("durationSteps")
            onset_tie_in = bool(onset.get("tieIn", False))
            onset_tie_out = bool(onset.get("tieOut", False))
            note_items = onset.get("notes")
            if not isinstance(note_items, list):
                raise ValueError(f"reference measure {measure} onset notes must be an array")

            if bool(onset.get("rest", False)):
                rests.append({"measure": measure, "step": step})
            if not note_items:
                continue

            for note in note_items:
                if not isinstance(note, Mapping):
                    raise ValueError("reference note must be an object")
                string = int(note.get("string"))
                fret = int(note.get("fret"))
                midi = int(note.get("midi"))
                if string not in OPEN_MIDI or not 0 <= fret <= 24:
                    raise ValueError(f"invalid reference string/fret: {string}/{fret}")
                expected = OPEN_MIDI[string] + fret
                if midi != expected:
                    raise ValueError(
                        f"reference pitch-position mismatch measure={measure} step={step}: "
                        f"string={string} fret={fret} midi={midi} expected={expected}"
                    )
                note_duration = note.get("durationSteps", onset_duration)
                duration = None if note_duration is None else float(note_duration)
                techniques = sorted(set(onset_techniques + normalize_labels(note.get("techniques"))))
                notes.append(
                    {
                        "measure": measure,
                        "step": step,
                        "string": string,
                        "fret": fret,
                        "midi": midi,
                        "durationSteps": duration,
                        "tieIn": bool(note.get("tieIn", onset_tie_in)),
                        "tieOut": bool(note.get("tieOut", onset_tie_out)),
                        "techniques": techniques,
                    }
                )

    return notes, rests, declared_measures


def flatten_generated(events: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    notes: list[dict[str, Any]] = []
    rests_seen: set[tuple[int, float]] = set()
    for event in canonical_events(events):
        duration = event.get("durationSteps")
        if duration is None:
            duration = event.get("sustainSteps")
        notes.append(
            {
                "measure": event["measure"],
                "step": event["step"],
                "string": event["string"],
                "fret": event["fret"],
                "midi": event["midi"],
                "durationSteps": duration,
                "tieIn": event.get("tieIn", False),
                "tieOut": event.get("tieOut", False),
                "techniques": event.get("techniques", []),
            }
        )
        if event.get("rest", False):
            rests_seen.add((event["measure"], event["step"]))
    rests = [{"measure": m, "step": s} for m, s in sorted(rests_seen)]
    return notes, rests


def onset_groups(notes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, float], list[Mapping[str, Any]]] = {}
    for note in notes:
        grouped.setdefault((int(note["measure"]), float(note["step"])), []).append(note)
    result: list[dict[str, Any]] = []
    for (measure, step), items in sorted(grouped.items()):
        result.append(
            {
                "measure": measure,
                "step": step,
                "pitchSet": tuple(sorted(int(item["midi"]) for item in items)),
                "voicing": tuple(sorted((int(item["string"]), int(item["fret"]), int(item["midi"])) for item in items)),
            }
        )
    return result


def label_events(notes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for note in notes:
        for label in normalize_labels(note.get("techniques")):
            result.append({**note, "label": label})
    return result


def duration_metrics(
    generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]], pairs: Sequence[tuple[int, int]]
) -> dict[str, Any]:
    comparable = []
    for gi, ri in pairs:
        gd = generated[gi].get("durationSteps")
        rd = reference[ri].get("durationSteps")
        if gd is None or rd is None:
            continue
        comparable.append((float(gd), float(rd)))
    exact = sum(1 for gd, rd in comparable if abs(gd - rd) <= EPSILON)
    tolerant = sum(1 for gd, rd in comparable if abs(gd - rd) <= DURATION_TOLERANCE + EPSILON)
    return {
        "comparable": len(comparable),
        "exactAgreement": safe_ratio(exact, len(comparable)),
        "withinToleranceAgreement": safe_ratio(tolerant, len(comparable)),
        "toleranceSteps": DURATION_TOLERANCE,
    }


def tie_metrics(
    generated: Sequence[Mapping[str, Any]], reference: Sequence[Mapping[str, Any]], pairs: Sequence[tuple[int, int]]
) -> dict[str, Any]:
    ref_relevant = [(gi, ri) for gi, ri in pairs if reference[ri].get("tieIn") or reference[ri].get("tieOut")]
    matched = sum(
        1
        for gi, ri in ref_relevant
        if bool(generated[gi].get("tieIn")) == bool(reference[ri].get("tieIn"))
        and bool(generated[gi].get("tieOut")) == bool(reference[ri].get("tieOut"))
    )
    return {
        "referenceTieNotes": len(ref_relevant),
        "exactAgreement": safe_ratio(matched, len(ref_relevant)),
    }


def validate_pre_reference(freeze_dir: Path) -> tuple[Mapping[str, Any], list[dict[str, Any]], Mapping[str, Any]]:
    # The human reference is intentionally not touched anywhere in this function.
    manifest_path = freeze_dir / "rhythm-freeze-manifest.json"
    snapshot_path = freeze_dir / "rhythm-frozen-analysis.json"
    manifest = load_json(manifest_path)
    snapshot = load_json(snapshot_path)
    if not isinstance(manifest, Mapping) or not isinstance(snapshot, Mapping):
        raise ValueError("freeze manifest/snapshot must be JSON objects")

    for key, expected in {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "referenceOpenedDuringFreeze": False,
        "pdfFidelityVerified": True,
    }.items():
        if manifest.get(key) is not expected:
            raise ValueError(f"freeze manifest fails anti-leakage/PDF gate: {key}={manifest.get(key)!r}")

    safety = snapshot.get("safety")
    if not isinstance(safety, Mapping):
        raise ValueError("frozen snapshot missing safety object")
    if safety.get("referenceFree") is not True:
        raise ValueError("frozen snapshot is not reference-free")
    if safety.get("professionalReferenceUsed") is not False or safety.get("referenceRuntimeInputUsed") is not False:
        raise ValueError("frozen snapshot indicates professional reference/runtime input use")

    generated_events = canonical_events(snapshot.get("renderEvents", []))
    frozen_hash = sha256_json(generated_events)
    if not generated_events or manifest.get("eventSha256") != frozen_hash:
        raise ValueError("frozen event hash mismatch")
    if manifest.get("pdfEventSha256") != frozen_hash or float(manifest.get("pdfEventFidelity", 0.0)) != 1.0:
        raise ValueError("professional PDF event stream is not exactly identical to frozen scored events")
    return manifest, generated_events, snapshot


def validate_reference(reference: Any) -> Mapping[str, Any]:
    if not isinstance(reference, Mapping):
        raise ValueError("professional reference must be a JSON object")
    if reference.get("schemaVersion") != 1:
        raise ValueError("unsupported professional reference schemaVersion")
    if reference.get("instrument") != "rhythm" or reference.get("holdout") is not True:
        raise ValueError("reference is not marked as a Rhythm holdout")
    if reference.get("completeReference") is not True:
        raise ValueError("partial screenshots/extractions cannot authorize final scoring")
    source = reference.get("source")
    if not isinstance(source, Mapping) or source.get("kind") != "professional-human-tab":
        raise ValueError("reference source must be a professional human-written tab")
    if not str(source.get("provenance", "")).strip():
        raise ValueError("professional reference provenance is required")
    if reference.get("stepsPerMeasure", 16) != 16:
        raise ValueError("final scorer currently requires the same 16-step measure grid as the V143 render contract")
    return reference


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument("reference_json", type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--minimum", type=float, default=NEAR_100)
    args = parser.parse_args()

    if not 0.0 < args.minimum <= 1.0:
        raise ValueError("minimum must be in (0, 1]")

    freeze_dir = args.freeze_dir.resolve()

    # 1) Validate safety, freeze hash and PDF identity BEFORE reference access.
    manifest, generated_events, snapshot = validate_pre_reference(freeze_dir)

    # 2) Only now resolve/open the professional human reference.
    reference_path = args.reference_json.resolve()
    if not (reference_path == REFERENCE_DIR or REFERENCE_DIR in reference_path.parents):
        raise ValueError("final professional reference must live under validation/rhythm_holdout/reference")
    reference = validate_reference(load_json(reference_path))

    generated_notes, generated_rests = flatten_generated(generated_events)
    reference_notes, reference_rests, reference_measures = flatten_reference(reference)
    if not reference_notes:
        raise ValueError("complete professional reference has no playable notes")

    generated_measures = {int(note["measure"]) for note in generated_notes}

    pitch_content = multiset_match(
        ((n["measure"], n["midi"]) for n in generated_notes),
        ((n["measure"], n["midi"]) for n in reference_notes),
    )
    exact_pitch_timing = multiset_match(
        ((n["measure"], round(float(n["step"]), 6), n["midi"]) for n in generated_notes),
        ((n["measure"], round(float(n["step"]), 6), n["midi"]) for n in reference_notes),
    )
    exact_position_timing = multiset_match(
        ((n["measure"], round(float(n["step"]), 6), n["midi"], n["string"], n["fret"]) for n in generated_notes),
        ((n["measure"], round(float(n["step"]), 6), n["midi"], n["string"], n["fret"]) for n in reference_notes),
    )

    pitch_pairs = greedy_match(
        generated_notes,
        reference_notes,
        lambda g, r: g["midi"] == r["midi"],
        STEP_TOLERANCE,
    )
    position_pairs = greedy_match(
        generated_notes,
        reference_notes,
        lambda g, r: g["midi"] == r["midi"] and g["string"] == r["string"] and g["fret"] == r["fret"],
        STEP_TOLERANCE,
    )
    gross_pitch_pairs = greedy_match(
        generated_notes,
        reference_notes,
        lambda g, r: g["midi"] == r["midi"],
        GROSS_STEP_TOLERANCE,
    )

    tolerant_pitch_timing = metric_for_pairs(pitch_pairs, generated_notes, reference_notes)
    tolerant_position_timing = metric_for_pairs(position_pairs, generated_notes, reference_notes)

    gen_onsets = onset_groups(generated_notes)
    ref_onsets = onset_groups(reference_notes)
    voicing_pairs = greedy_match(
        gen_onsets,
        ref_onsets,
        lambda g, r: g["voicing"] == r["voicing"],
        STEP_TOLERANCE,
    )
    pitchset_pairs = greedy_match(
        gen_onsets,
        ref_onsets,
        lambda g, r: g["pitchSet"] == r["pitchSet"],
        STEP_TOLERANCE,
    )
    voicing_metric = metric_for_pairs(voicing_pairs, gen_onsets, ref_onsets)
    pitchset_metric = metric_for_pairs(pitchset_pairs, gen_onsets, ref_onsets)

    gen_labels = label_events(generated_notes)
    ref_labels = label_events(reference_notes)
    technique_pairs = greedy_match(
        gen_labels,
        ref_labels,
        lambda g, r: (
            g["midi"] == r["midi"]
            and g["string"] == r["string"]
            and g["fret"] == r["fret"]
            and g["label"] == r["label"]
        ),
        STEP_TOLERANCE,
    )
    technique_metric = metric_for_pairs(technique_pairs, gen_labels, ref_labels)

    rest_pairs = greedy_match(generated_rests, reference_rests, lambda _g, _r: True, STEP_TOLERANCE)
    rest_metric = metric_for_pairs(rest_pairs, generated_rests, reference_rests)

    duration = duration_metrics(generated_notes, reference_notes, position_pairs)
    ties = tie_metrics(generated_notes, reference_notes, position_pairs)

    missing_reference_measures = sorted(reference_measures - generated_measures)
    extra_generated_measures = sorted(generated_measures - reference_measures)
    measure_coverage = {
        "referenceMeasureCount": len(reference_measures),
        "generatedMeasureCount": len(generated_measures),
        "matchedReferenceMeasures": len(reference_measures & generated_measures),
        "recall": safe_ratio(len(reference_measures & generated_measures), len(reference_measures)),
        "missingReferenceMeasures": missing_reference_measures,
        "extraGeneratedMeasures": extra_generated_measures,
    }

    gross_unmatched_reference = len(reference_notes) - len(gross_pitch_pairs)
    gross_unmatched_generated = len(generated_notes) - len(gross_pitch_pairs)
    critical_mismatch_count = len(missing_reference_measures) + gross_unmatched_reference + gross_unmatched_generated

    gated_metrics = {
        "pitchContentF1": pitch_content["f1"],
        "pitchTimingTolerantF1": tolerant_pitch_timing["f1"],
        "stringFretTimingTolerantF1": tolerant_position_timing["f1"],
        "chordPitchSetTolerantF1": pitchset_metric["f1"],
        "exactVoicingTolerantF1": voicing_metric["f1"],
        "measureCoverageRecall": measure_coverage["recall"],
        "pdfEventFidelity": float(manifest.get("pdfEventFidelity", 0.0)),
    }
    if duration["comparable"]:
        gated_metrics["durationAgreement"] = duration["withinToleranceAgreement"]
    if ref_labels:
        gated_metrics["techniqueF1"] = technique_metric["f1"]
    if ties["referenceTieNotes"]:
        gated_metrics["tieAgreement"] = ties["exactAgreement"]
    if reference_rests:
        gated_metrics["restF1"] = rest_metric["f1"]

    threshold_failures = {name: value for name, value in gated_metrics.items() if value + EPSILON < args.minimum}
    # PDF fidelity is exact, not merely near-100.
    if gated_metrics["pdfEventFidelity"] != 1.0:
        threshold_failures["pdfEventFidelity"] = gated_metrics["pdfEventFidelity"]

    passed = not threshold_failures and critical_mismatch_count == 0
    report = {
        "schemaVersion": 1,
        "instrument": "rhythm",
        "scoringMode": "isolated-professional-human-holdout-post-freeze",
        "referenceOpenedOnlyAfterFreezeValidation": True,
        "referenceFree": True,
        "professionalReferenceUsedByAnalyzer": False,
        "referenceRuntimeInputUsed": False,
        "minimumProfessionalScore": args.minimum,
        "timingToleranceSteps": STEP_TOLERANCE,
        "grossTimingToleranceSteps": GROSS_STEP_TOLERANCE,
        "frozenEventSha256": manifest["eventSha256"],
        "pdfEventSha256": manifest["pdfEventSha256"],
        "pdfEventFidelity": manifest["pdfEventFidelity"],
        "generatedEventCount": len(generated_notes),
        "referenceNoteCount": len(reference_notes),
        "metrics": {
            "pitchContentByMeasure": pitch_content,
            "exactPitchTiming": exact_pitch_timing,
            "tolerantPitchTiming": tolerant_pitch_timing,
            "exactStringFretTiming": exact_position_timing,
            "tolerantStringFretTiming": tolerant_position_timing,
            "chordPitchSet": pitchset_metric,
            "chordVoicing": voicing_metric,
            "duration": duration,
            "techniques": technique_metric,
            "ties": ties,
            "rests": rest_metric,
            "measureCoverage": measure_coverage,
        },
        "gatedMetrics": gated_metrics,
        "thresholdFailures": threshold_failures,
        "criticalMismatchCount": critical_mismatch_count,
        "criticalMismatchBreakdown": {
            "missingReferenceMeasures": len(missing_reference_measures),
            "grossUnmatchedReferenceNotes": gross_unmatched_reference,
            "grossUnmatchedGeneratedNotes": gross_unmatched_generated,
        },
        "near100ProfessionalGatePassed": passed,
        "rhythmComplete": passed,
    }

    output_path = args.output.resolve() if args.output else freeze_dir / "rhythm-professional-holdout-score.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
