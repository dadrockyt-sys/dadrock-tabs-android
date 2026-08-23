from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from v143_candidate_timing_adapter import detect_candidate_slots
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
    candidate_detector: CandidateDetector = detect_candidate_slots,
    stem_loader: StemLoader = load_mono_wav,
    rhythm_analyzer: RhythmAnalyzer = analyze_candidates,
) -> ReferenceFreeRhythmResult:
    """
    Assemble the reference-free Rhythm Guitar boundary for arbitrary uploads.

    Timing is estimated from the normalized full mix. Candidate generation uses
    caller-selected separated Rhythm Guitar stem paths. The frozen V143 carrier
    keeps its explicit paired-stem contract through carrier_stem_a_path and
    carrier_stem_b_path.

    This coordinator deliberately does not perform separation, note naming,
    technique classification, PDF rendering, or offline grading.
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
    rows = rhythm_analyzer(
        candidates,
        stem_a_audio,
        int(stem_a_sr),
        stem_b_audio,
        int(stem_b_sr),
        scorer,
    )

    if len(rows) != len(candidates):
        raise RuntimeError(
            "V143 runtime changed candidate row count: "
            f"{len(candidates)} -> {len(rows)}"
        )

    required_runtime_fields = {"v143Score", "v143Rank", "v143Selected"}
    for index, row in enumerate(rows):
        missing = sorted(required_runtime_fields.difference(row))
        if missing:
            raise RuntimeError(
                f"V143 result row {index} is missing runtime fields: {missing}"
            )

    return ReferenceFreeRhythmResult(
        timing=timing,
        candidates=tuple(dict(row) for row in candidates),
        rows=tuple(dict(row) for row in rows),
    )


__all__ = [
    "ReferenceFreeRhythmResult",
    "analyze_reference_free_rhythm",
]
