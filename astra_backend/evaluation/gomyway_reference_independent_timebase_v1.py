"""Reference-independent full-song musical grid diagnostic for Go My Way.

Two deliberately separated modes:
1) generate: reads only decoded song audio and freezes a candidate 4/4 beat/step grid.
2) compare: reads the already-frozen candidate plus the professional timing map and
   produces diagnostics only. It never rewrites the candidate.

This is an existing-reference development diagnostic, not a sealed holdout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import median

import numpy as np
import soundfile as sf

from v143_candidate_timing_adapter import build_subdivision_grid
from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
from v143_reference_free_timing import estimate_reference_free_timing_from_samples

EXPECTED_AUDIO_SOURCE = "public/gomywayfullaitest.m4a"
EXPECTED_AUDIO_GIT_BLOB = "5e34fb55fbd011c55b56bc40cc5d062735b3fcd0"
BEATS_PER_MEASURE = 4
SUBDIVISIONS_PER_BEAT = 4


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def finite(values):
    return [float(v) for v in values if math.isfinite(float(v))]


def summarize(values):
    vals = finite(values)
    if not vals:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(vals),
        "mean": float(np.mean(vals)),
        "median": float(np.median(vals)),
        "min": float(np.min(vals)),
        "max": float(np.max(vals)),
    }


def generate(args) -> int:
    wav = Path(args.audio_wav)
    source = Path(args.audio_source)
    samples, sample_rate = sf.read(str(wav), dtype="float32", always_2d=False)

    timing = estimate_reference_free_timing_from_samples(samples, int(sample_rate))
    repair = repair_reference_free_beat_grid_from_samples(samples, int(sample_rate), timing)
    repaired = repair.timing

    slots = build_subdivision_grid(
        repaired.beat_times,
        beats_per_measure=BEATS_PER_MEASURE,
        subdivisions_per_beat=SUBDIVISIONS_PER_BEAT,
        measure_start=1,
        first_beat_in_measure=repaired.first_beat_in_measure,
    )

    measures = {}
    for slot in slots:
        row = measures.setdefault(int(slot.measure), {"measure": int(slot.measure), "steps": {}})
        row["steps"][str(int(slot.step))] = float(slot.time_seconds)

    normalized_measures = []
    for m in sorted(measures):
        steps = measures[m]["steps"]
        normalized_measures.append({
            "measure": m,
            "availableStepCount": len(steps),
            "stepTimesSeconds": steps,
            "startSeconds": steps.get("0"),
        })

    beat_times = [float(x) for x in repaired.beat_times]
    beat_intervals = [b - a for a, b in zip(beat_times[:-1], beat_times[1:])]
    candidate = {
        "schemaVersion": 1,
        "kind": "gomyway-reference-independent-full-song-grid-v1",
        "status": "frozen-before-professional-comparison",
        "referenceBlindGeneration": True,
        "professionalTimingMapReadDuringGeneration": False,
        "professionalScorerRowsReadDuringGeneration": False,
        "audio": {
            "sourcePath": args.audio_source_path_label,
            "expectedRepositoryGitBlob": EXPECTED_AUDIO_GIT_BLOB,
            "sourceSha256": sha256_file(source),
            "decodedWavSha256": sha256_file(wav),
            "sampleRate": int(sample_rate),
            "durationSeconds": float(len(samples) / float(sample_rate)),
        },
        "estimator": {
            "name": "v143-reference-free-timing-plus-beat-grid-repair",
            "tempoBpm": float(repaired.tempo_bpm),
            "beatConfidence": float(repaired.beat_confidence),
            "barConfidence": float(repaired.bar_confidence),
            "firstBeatInMeasure": int(repaired.first_beat_in_measure),
            "downbeatIndexMod4": int(repaired.downbeat_index_mod4),
            "meterAssumption": {"numerator": 4, "denominator": 4},
            "beatsPerMeasure": BEATS_PER_MEASURE,
            "subdivisionsPerBeat": SUBDIVISIONS_PER_BEAT,
            "stepsPerMeasure": BEATS_PER_MEASURE * SUBDIVISIONS_PER_BEAT,
        },
        "grid": {
            "beatCount": len(beat_times),
            "beatTimesSeconds": beat_times,
            "beatIntervalSummarySeconds": summarize(beat_intervals),
            "measureCountWithAnySlots": len(normalized_measures),
            "firstMeasureNumber": min(measures) if measures else None,
            "lastMeasureNumber": max(measures) if measures else None,
            "slotCount": len(slots),
            "measures": normalized_measures,
        },
        "repairDiagnostics": repair.diagnostics(),
        "interpretationBoundary": (
            "Candidate timing/measure/step coordinates were generated from audio only. "
            "The estimator assumes 4/4 and does not know the professional 2/4 exception. "
            "This frozen candidate may be compared diagnostically afterward, but must not "
            "be retuned from that comparison."
        ),
    }
    write_json(Path(args.output_json), candidate)
    print(json.dumps({
        "tempoBpm": candidate["estimator"]["tempoBpm"],
        "beatCount": candidate["grid"]["beatCount"],
        "measureCount": candidate["grid"]["measureCountWithAnySlots"],
        "firstBeatInMeasure": candidate["estimator"]["firstBeatInMeasure"],
        "barConfidence": candidate["estimator"]["barConfidence"],
    }, indent=2))
    return 0


def _candidate_starts(candidate: dict) -> dict[int, float]:
    out = {}
    for row in candidate["grid"]["measures"]:
        if row.get("startSeconds") is not None:
            out[int(row["measure"])] = float(row["startSeconds"])
    return out


def _reference_starts(reference: dict) -> dict[int, float]:
    return {
        int(row["measureNumber"]): float(row["startSeconds"])
        for row in reference["measureBoundaries"]
    }


def _shift_diagnostic(candidate_starts, reference_starts, shift):
    errors = []
    pairs = []
    # candidate measure c is compared to professional measure c+shift.
    for c, ct in candidate_starts.items():
        r = c + int(shift)
        if r not in reference_starts:
            continue
        error = ct - reference_starts[r]
        errors.append(error)
        pairs.append({"candidateMeasure": c, "referenceMeasure": r, "signedErrorSeconds": error})
    if not errors:
        return None
    abs_errors = [abs(e) for e in errors]
    return {
        "measureShift": int(shift),
        "pairCount": len(errors),
        "meanSignedErrorSeconds": float(np.mean(errors)),
        "medianSignedErrorSeconds": float(np.median(errors)),
        "meanAbsoluteErrorSeconds": float(np.mean(abs_errors)),
        "medianAbsoluteErrorSeconds": float(np.median(abs_errors)),
        "maxAbsoluteErrorSeconds": float(np.max(abs_errors)),
        "pairs": pairs,
    }


def compare(args) -> int:
    candidate_path = Path(args.candidate_json)
    frozen_sha = sha256_file(candidate_path)
    candidate = json.loads(candidate_path.read_text())
    if candidate.get("referenceBlindGeneration") is not True:
        raise RuntimeError("candidate is not declared reference-blind")
    if candidate.get("professionalTimingMapReadDuringGeneration") is not False:
        raise RuntimeError("candidate generation provenance is not clean")

    # The professional timing map is intentionally opened only after the candidate
    # bytes and SHA-256 have been frozen above.
    reference_path = Path(args.professional_timing_map)
    reference = json.loads(reference_path.read_text())
    if reference.get("audioSource") != EXPECTED_AUDIO_SOURCE:
        raise RuntimeError("professional timing map audio binding mismatch")

    candidate_starts = _candidate_starts(candidate)
    reference_starts = _reference_starts(reference)
    diagnostics = [
        d for d in (_shift_diagnostic(candidate_starts, reference_starts, s) for s in range(-8, 9))
        if d is not None
    ]
    best = min(
        diagnostics,
        key=lambda d: (d["medianAbsoluteErrorSeconds"], d["meanAbsoluteErrorSeconds"], abs(d["measureShift"])),
    )

    raw_zero = next((d for d in diagnostics if d["measureShift"] == 0), None)
    ref_durations = [float(x["durationSeconds"]) for x in reference["measureBoundaries"]]
    ref_bpms = [
        60.0 * int(x["meter"]["numerator"]) / float(x["durationSeconds"])
        for x in reference["measureBoundaries"]
        if int(x["meter"]["numerator"]) > 0
    ]

    paired = best["pairs"]
    drift = None
    if len(paired) >= 2:
        xs = np.asarray([p["referenceMeasure"] for p in paired], dtype=np.float64)
        ys = np.asarray([p["signedErrorSeconds"] for p in paired], dtype=np.float64)
        slope, intercept = np.polyfit(xs, ys, 1)
        drift = {
            "secondsPerReferenceMeasure": float(slope),
            "interceptSeconds": float(intercept),
            "predictedDriftAcross113MeasuresSeconds": float(slope * 112.0),
        }

    out = {
        "schemaVersion": 1,
        "kind": "gomyway-reference-independent-full-song-grid-v1-professional-comparison",
        "candidateFrozenSha256BeforeReferenceRead": frozen_sha,
        "candidateMutatedAfterComparison": False,
        "comparisonIsDiagnosticOnly": True,
        "professionalTimingMapSha256": sha256_file(reference_path),
        "candidate": {
            "tempoBpm": candidate["estimator"]["tempoBpm"],
            "beatCount": candidate["grid"]["beatCount"],
            "measureCountWithAnySlots": candidate["grid"]["measureCountWithAnySlots"],
            "meterAssumption": candidate["estimator"]["meterAssumption"],
            "barConfidence": candidate["estimator"]["barConfidence"],
        },
        "professional": {
            "declaredBaseTempoBpm": reference.get("baseTempoBpm"),
            "resolvedTempoBpm": reference.get("alignment", {}).get("resolvedTempoBpm"),
            "measureCount": reference.get("measureCount"),
            "meterRegions": reference.get("meterRegions"),
            "measureDurationSummarySeconds": summarize(ref_durations),
            "impliedMeasureBpmSummary": summarize(ref_bpms),
        },
        "sameNumberingDiagnostic": raw_zero,
        "bestIntegerMeasureShiftDiagnostic": best,
        "allIntegerShiftSummaries": [
            {k: d[k] for k in d if k != "pairs"} for d in diagnostics
        ],
        "bestShiftDrift": drift,
        "interpretationBoundary": (
            "The integer shift is a post-freeze diagnostic alignment only. It must not be "
            "fed back into or used to rewrite the frozen candidate. The professional map "
            "contains a 2/4 measure at 104 while the candidate estimator is 4/4-only, so "
            "late-song measure-number divergence is expected unless independently detected."
        ),
    }
    write_json(Path(args.output_json), out)
    print(json.dumps({
        "candidateSha256": frozen_sha,
        "candidateTempoBpm": out["candidate"]["tempoBpm"],
        "bestShift": best["measureShift"],
        "pairCount": best["pairCount"],
        "medianAbsoluteErrorSeconds": best["medianAbsoluteErrorSeconds"],
        "meanAbsoluteErrorSeconds": best["meanAbsoluteErrorSeconds"],
        "drift": drift,
    }, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--audio-source", required=True)
    g.add_argument("--audio-source-path-label", default=EXPECTED_AUDIO_SOURCE)
    g.add_argument("--audio-wav", required=True)
    g.add_argument("--output-json", required=True)
    g.set_defaults(func=generate)

    c = sub.add_parser("compare")
    c.add_argument("--candidate-json", required=True)
    c.add_argument("--professional-timing-map", required=True)
    c.add_argument("--output-json", required=True)
    c.set_defaults(func=compare)

    args = ap.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
