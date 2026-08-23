from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Callable, Sequence

from v143_candidate_timing_adapter import (
    HISTORICAL_WIDE_RECALL_SWEEPS,
    ReferenceError if False else TimingSlot,
    build_subdivision_grid,
    candidate_slots_from_event_groups,
    detect_candidate_slots,
    note_events_from_predict,
)
from v143_production_engine import V143ProductionEngine
from v143_reference_free_timing import (
    ReferenceFreeTimingEstimate,
    estimate_reference_free_timing,
)
from v143_rhythm_runtime import analyze_candidates, load_mono_wav


TimingEstimator = Callable[..., ReferenceFreeTimingEstimate]
CandidateDetector = Callable[..., list[dict[str, Any]]]
StemLoader = Callable[[str | Path], tuple[Any, int]]
RhythmAnalyzer = Callable[..., list[dict[str, Any]]]
ContextualSelector = Callable[[Sequence[dict[str, Any]]], list[dict[str, Any]]]

# Keep the historical widest Basic Pitch sweep as the only source of candidate
# locations. A stricter historical sweep is run in parallel only as extra
# reference-free pitch/onset evidence. It is never allowed to invent a slot that
# the high-recall sweep did not already expose.
WIDE_RECALL_SWEEP = HISTORICAL_WIDE_RECALL_SWEEPS[-1]
PRECISION_EVIDENCE_SWEEP = HISTORICAL_WIDE_RECALL_SWEEPS[0]
CONTEXTUAL_MIN_PRECISION_SOURCE_COUNT = 2


def _precision_hypothesis_quality(hypothesis: dict[str, Any]) -> tuple[float, ...]:
    """Prefer pitches that survive the stricter sweep on independent stems."""
    precision_supported = bool(hypothesis.get("precisionSupported"))
    precision_amplitude = float(
        hypothesis.get("precisionMaxAmplitude", hypothesis.get("maxAmplitude", 0.0))
    )
    precision_grid_error = float(
        hypothesis.get("precisionMinGridError", hypothesis.get("minGridError", 999.0))
    )
    precision_duration = float(
        hypothesis.get("precisionMaxDuration", hypothesis.get("maxDuration", 0.0))
    )
    return (
        1.0 if precision_supported else 0.0,
        float(hypothesis.get("precisionSourceCount", 0)),
        float(hypothesis.get("precisionEventCount", 0)),
        float(hypothesis.get("sourceCount", 0)),
        float(hypothesis.get("eventCount", 0)),
        precision_amplitude,
        -precision_grid_error,
        precision_duration,
        -float(hypothesis.get("midi", 0)),
    )


def _merge_precision_evidence(
    base_rows: Sequence[dict[str, Any]],
    precision_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    precision_by_location = {
        (int(row["measure"]), int(row["step"])): row
        for row in precision_rows
    }
    out: list[dict[str, Any]] = []

    for raw in base_rows:
        row = deepcopy(raw)
        key = (int(row["measure"]), int(row["step"]))
        precision = precision_by_location.get(key)
        precision_hypotheses = {
            int(item["midi"]): item
            for item in (precision or {}).get("pitchHypotheses", [])
            if item.get("midi") is not None
        }

        row["precisionCandidateSupported"] = precision is not None
        row["precisionSourceCount"] = int((precision or {}).get("sourceCount") or 0)
        row["precisionEventCount"] = int((precision or {}).get("eventCount") or 0)
        row["precisionPitchCount"] = int((precision or {}).get("candidatePitchCount") or 0)
        row["wideRecallSweep"] = str(WIDE_RECALL_SWEEP[0])
        row["precisionEvidenceSweep"] = str(PRECISION_EVIDENCE_SWEEP[0])
        row["pitchEvidenceMode"] = "wide-recall-plus-independent-precision-sweep"

        enriched_hypotheses: list[dict[str, Any]] = []
        for raw_hypothesis in row.get("pitchHypotheses") or []:
            hypothesis = deepcopy(raw_hypothesis)
            midi = int(hypothesis["midi"])
            precise = precision_hypotheses.get(midi)
            hypothesis["precisionSupported"] = precise is not None
            hypothesis["precisionSourceCount"] = int(
                (precise or {}).get("sourceCount") or 0
            )
            hypothesis["precisionEventCount"] = int(
                (precise or {}).get("eventCount") or 0
            )
            if precise is not None:
                hypothesis["precisionMaxAmplitude"] = float(
                    precise.get("maxAmplitude") or 0.0
                )
                hypothesis["precisionMeanAmplitude"] = float(
                    precise.get("meanAmplitude") or 0.0
                )
                hypothesis["precisionMinGridError"] = float(
                    precise.get("minGridError") or 0.0
                )
                hypothesis["precisionMaxDuration"] = float(
                    precise.get("maxDuration") or 0.0
                )
                hypothesis["precisionBestOnsetTime"] = float(
                    precise.get("bestOnsetTime") or 0.0
                )
                hypothesis["precisionBestOffsetTime"] = float(
                    precise.get("bestOffsetTime") or 0.0
                )
            enriched_hypotheses.append(hypothesis)

        if not enriched_hypotheses:
            raise RuntimeError(f"Candidate {key} lost all wide-recall pitch hypotheses")

        old_dominant = int(row["dominantMidi"])
        new_dominant = int(
            max(enriched_hypotheses, key=_precision_hypothesis_quality)["midi"]
        )
        row["dominantMidiWideRecall"] = old_dominant
        row["dominantMidi"] = new_dominant
        row["precisionEvidenceChangedDominant"] = new_dominant != old_dominant
        row["pitchHypotheses"] = enriched_hypotheses
        out.append(row)

    return out


def detect_precision_contextual_candidate_slots(
    stem_paths: Sequence[str | Path],
    beat_times: Sequence[float],
    *,
    predictor: Any = None,
    beats_per_measure: int = 4,
    subdivisions_per_beat: int = 4,
    measure_start: int = 1,
    first_beat_in_measure: int = 0,
    max_grid_error_seconds: float = 0.10,
) -> list[dict[str, Any]]:
    """Build the same high-recall slot universe plus an independent strict view.

    The wide sweep remains authoritative for *where* a candidate can exist. The
    stricter sweep only annotates those already-existing slots and pitches. This
    keeps timing recall stable while giving the note mapper a way to distinguish
    persistent guitar pitches from low-threshold harmonic clutter.
    """
    base_rows = detect_candidate_slots(
        stem_paths=stem_paths,
        beat_times=beat_times,
        predictor=predictor,
        sweeps=(WIDE_RECALL_SWEEP,),
        beats_per_measure=beats_per_measure,
        subdivisions_per_beat=subdivisions_per_beat,
        measure_start=measure_start,
        first_beat_in_measure=first_beat_in_measure,
        max_grid_error_seconds=max_grid_error_seconds,
    )

    grid = build_subdivision_grid(
        beat_times,
        beats_per_measure=beats_per_measure,
        subdivisions_per_beat=subdivisions_per_beat,
        measure_start=measure_start,
        first_beat_in_measure=first_beat_in_measure,
    )
    precision_groups: list[tuple[str, list[Any]]] = []
    for stem_index, stem_path in enumerate(stem_paths):
        stem = Path(stem_path)
        sweep_name, onset_threshold, frame_threshold = PRECISION_EVIDENCE_SWEEP
        precision_groups.append(
            (
                f"stem{stem_index}:{stem.name}:{sweep_name}",
                note_events_from_predict(
                    stem,
                    predictor=predictor,
                    onset_threshold=float(onset_threshold),
                    frame_threshold=float(frame_threshold),
                ),
            )
        )

    try:
        precision_rows = candidate_slots_from_event_groups(
            precision_groups,
            grid,
            max_grid_error_seconds=max_grid_error_seconds,
        )
    except ValueError:
        precision_rows = []

    return _merge_precision_evidence(base_rows, precision_rows)


def _precision_consensus(row: dict[str, Any]) -> bool:
    return bool(row.get("precisionCandidateSupported")) and int(
        row.get("precisionSourceCount") or 0
    ) >= CONTEXTUAL_MIN_PRECISION_SOURCE_COUNT


def apply_reference_free_contextual_selection(
    ranked_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Rescue strong local attacks without touching V143 scores or ranks.

    The frozen V143 model uses one global top-q cutoff. On arbitrary songs that
    can erase quieter measures even when the same two separated guitar views and
    the stricter Basic Pitch pass both show a local attack. We preserve every
    baseline selection and only add a candidate when it has two-stem precision
    consensus, is a local V143 score peak, and is at least the median score for
    its own measure. If a candidate-rich measure would otherwise be completely
    empty, its strongest two-stem precision candidate is retained fail-safe.
    """
    rows = [deepcopy(row) for row in ranked_rows]
    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        row["v143BaseSelected"] = bool(row.get("v143Selected"))
        row["v143ContextualRescued"] = False
        row["v143SelectionReason"] = (
            "frozen-global-q" if row["v143BaseSelected"] else "not-selected"
        )
        by_measure[int(row["measure"])].append(row)

    for measure_rows in by_measure.values():
        ordered = sorted(measure_rows, key=lambda row: int(row["step"]))
        measure_median = float(median(float(row["v143Score"]) for row in ordered))

        for index, row in enumerate(ordered):
            if row["v143BaseSelected"] or not _precision_consensus(row):
                continue
            score = float(row["v143Score"])
            left = float(ordered[index - 1]["v143Score"]) if index > 0 else None
            right = (
                float(ordered[index + 1]["v143Score"])
                if index + 1 < len(ordered)
                else None
            )
            at_least_neighbors = (
                (left is None or score >= left)
                and (right is None or score >= right)
            )
            strictly_above_one_neighbor = (
                (left is not None and score > left)
                or (right is not None and score > right)
                or (left is None and right is None)
            )
            local_peak = at_least_neighbors and strictly_above_one_neighbor
            if local_peak and score >= measure_median:
                row["v143ContextualRescued"] = True
                row["v143SelectionReason"] = "two-stem-precision-local-peak"

        if not any(
            bool(row["v143BaseSelected"]) or bool(row["v143ContextualRescued"])
            for row in ordered
        ):
            precision_rows = [row for row in ordered if _precision_consensus(row)]
            if precision_rows:
                strongest = max(
                    precision_rows,
                    key=lambda row: (float(row["v143Score"]), -int(row["step"])),
                )
                strongest["v143ContextualRescued"] = True
                strongest["v143SelectionReason"] = "quiet-measure-precision-failsafe"

        for row in ordered:
            row["v143Selected"] = bool(
                row["v143BaseSelected"] or row["v143ContextualRescued"]
            )
            row["v143SelectionMode"] = (
                "v143-global-q-plus-reference-free-precision-context"
            )
            row["professionalReferenceUsed"] = False
            row["runtimeLabelsRequired"] = False

    return rows


@dataclass(frozen=True)
class ReferenceFreeRhythmResult:
    """One reference-free Rhythm Guitar pass through timing, candidates, and V143."""

    timing: ReferenceFreeTimingEstimate
    candidates: tuple[dict[str, Any], ...]
    rows: tuple[dict[str, Any], ...]

    @property
    def selected_rows(self) -> tuple[dict[str, Any], ...]:
        return tuple(row for row in self.rows if bool(row.get("v143Selected")))

    @property
    def candidate_count(self) -> int:
        return len(self.candidates)

    @property
    def selected_count(self) -> int:
        return len(self.selected_rows)

    @property
    def base_selected_count(self) -> int:
        return sum(1 for row in self.rows if bool(row.get("v143BaseSelected")))

    @property
    def contextual_rescued_count(self) -> int:
        return sum(1 for row in self.rows if bool(row.get("v143ContextualRescued")))

    @property
    def selection_changed(self) -> bool:
        return self.contextual_rescued_count > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "timing": {
                "tempoBpm": float(self.timing.tempo_bpm),
                "timeSignature": "4/4",
                "firstBeatInMeasure": int(self.timing.first_beat_in_measure),
                "downbeatIndexMod4": int(self.timing.downbeat_index_mod4),
                "beatConfidence": float(self.timing.beat_confidence),
                "barConfidence": float(self.timing.bar_confidence),
                "beatTimes": [float(value) for value in self.timing.beat_times],
            },
            "candidateCount": self.candidate_count,
            "selectedCount": self.selected_count,
            "selection": {
                "version": 2,
                "mode": "v143-global-q-plus-reference-free-precision-context",
                "baseSelectedCount": self.base_selected_count,
                "contextualRescuedCount": self.contextual_rescued_count,
                "selectionChanged": self.selection_changed,
                "wideRecallSweep": str(WIDE_RECALL_SWEEP[0]),
                "precisionEvidenceSweep": str(PRECISION_EVIDENCE_SWEEP[0]),
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            },
            "candidates": [dict(row) for row in self.candidates],
            "rows": [dict(row) for row in self.rows],
        }


def analyze_reference_free_rhythm(
    full_mix_path: str | Path,
    candidate_stem_paths: Sequence[str | Path],
    carrier_stem_a_path: str | Path,
    carrier_stem_b_path: str | Path,
    *,
    predictor: Any = None,
    engine: V143ProductionEngine | None = None,
    timing_estimator: TimingEstimator = estimate_reference_free_timing,
    candidate_detector: CandidateDetector = detect_precision_contextual_candidate_slots,
    stem_loader: StemLoader = load_mono_wav,
    rhythm_analyzer: RhythmAnalyzer = analyze_candidates,
    contextual_selector: ContextualSelector = apply_reference_free_contextual_selection,
) -> ReferenceFreeRhythmResult:
    """
    Assemble the reference-free Rhythm Guitar boundary for arbitrary uploads.

    Timing is estimated from the normalized full mix. Candidate generation uses
    caller-selected separated Rhythm Guitar stem paths. The wide Basic Pitch pass
    owns the candidate universe; a stricter independent pass supplies only extra
    pitch/onset confidence. Frozen V143 scores/ranks are then preserved while a
    conservative local selector can rescue quieter two-stem precision attacks.

    This coordinator deliberately does not perform separation, technique
    classification, PDF rendering, offline grading, or professional-reference
    access.
    """
    candidate_paths = tuple(Path(path) for path in candidate_stem_paths)
    if not candidate_paths:
        raise ValueError("At least one candidate Rhythm Guitar stem is required")

    timing = timing_estimator(full_mix_path)
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError(
            "timing_estimator must return ReferenceFreeTimingEstimate"
        )

    adapter_kwargs = timing.candidate_adapter_kwargs()
    candidates = candidate_detector(
        stem_paths=candidate_paths,
        predictor=predictor,
        **adapter_kwargs,
    )
    if not candidates:
        raise ValueError("Candidate detector returned no Rhythm Guitar candidates")

    stem_a_audio, stem_a_sr = stem_loader(carrier_stem_a_path)
    stem_b_audio, stem_b_sr = stem_loader(carrier_stem_b_path)

    scorer = engine or V143ProductionEngine()
    ranked_rows = rhythm_analyzer(
        candidates,
        stem_a_audio,
        int(stem_a_sr),
        stem_b_audio,
        int(stem_b_sr),
        scorer,
    )

    if len(ranked_rows) != len(candidates):
        raise RuntimeError(
            "V143 runtime changed candidate row count: "
            f"{len(candidates)} -> {len(ranked_rows)}"
        )

    rows = contextual_selector(ranked_rows)
    if len(rows) != len(ranked_rows):
        raise RuntimeError(
            "Contextual selector changed candidate row count: "
            f"{len(ranked_rows)} -> {len(rows)}"
        )

    required_runtime_fields = {"v143Score", "v143Rank", "v143Selected"}
    for index, row in enumerate(rows):
        missing = sorted(required_runtime_fields.difference(row))
        if missing:
            raise RuntimeError(
                f"V143 result row {index} is missing runtime fields: {missing}"
            )
        if row.get("professionalReferenceUsed") not in {None, False}:
            raise RuntimeError("Contextual selector used professional reference data")
        if row.get("runtimeLabelsRequired") not in {None, False}:
            raise RuntimeError("Contextual selector requires runtime labels")

    return ReferenceFreeRhythmResult(
        timing=timing,
        candidates=tuple(dict(row) for row in candidates),
        rows=tuple(dict(row) for row in rows),
    )


__all__ = [
    "WIDE_RECALL_SWEEP",
    "PRECISION_EVIDENCE_SWEEP",
    "CONTEXTUAL_MIN_PRECISION_SOURCE_COUNT",
    "ReferenceFreeRhythmResult",
    "detect_precision_contextual_candidate_slots",
    "apply_reference_free_contextual_selection",
    "analyze_reference_free_rhythm",
]
