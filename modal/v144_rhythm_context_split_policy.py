from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any, Mapping


MUSICAL_METRICS = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "exactVoicingTolerantF1",
)

SPLITS = ("fit", "validation", "canary")


@dataclass(frozen=True)
class ContextSplitConfig:
    minimum_pitch_content_gain: float = 0.005
    minimum_musical_floor_gain: float = 0.0
    maximum_per_metric_regression: float = 0.0
    maximum_canary_regression: float = 0.0
    maximum_critical_mismatch_increase: int = 0
    required_pdf_event_fidelity: float = 1.0
    holdout_must_remain_closed: bool = True
    split_seed: int = 144
    fit_percent: int = 60
    validation_percent: int = 20

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "ContextSplitConfig":
        obj = cls(
            minimum_pitch_content_gain=float(payload.get("minimumPitchContentGain", 0.005)),
            minimum_musical_floor_gain=float(payload.get("minimumMusicalFloorGain", 0.0)),
            maximum_per_metric_regression=float(payload.get("maximumPerMetricRegression", 0.0)),
            maximum_canary_regression=float(payload.get("maximumCanaryRegression", 0.0)),
            maximum_critical_mismatch_increase=int(payload.get("maximumCriticalMismatchIncrease", 0)),
            required_pdf_event_fidelity=float(payload.get("requiredPdfEventFidelity", 1.0)),
            holdout_must_remain_closed=bool(payload.get("holdoutMustRemainClosed", True)),
            split_seed=int(payload.get("splitSeed", 144)),
            fit_percent=int(payload.get("fitPercent", 60)),
            validation_percent=int(payload.get("validationPercent", 20)),
        )
        obj.validate()
        return obj

    def validate(self) -> None:
        if self.minimum_pitch_content_gain < 0.0:
            raise ValueError("minimum_pitch_content_gain must be non-negative")
        if self.minimum_musical_floor_gain < 0.0:
            raise ValueError("minimum_musical_floor_gain must be non-negative")
        if self.maximum_per_metric_regression < 0.0:
            raise ValueError("maximum_per_metric_regression must be non-negative")
        if self.maximum_canary_regression < 0.0:
            raise ValueError("maximum_canary_regression must be non-negative")
        if self.maximum_critical_mismatch_increase < 0:
            raise ValueError("maximum_critical_mismatch_increase must be non-negative")
        if self.required_pdf_event_fidelity != 1.0:
            raise ValueError("V144 requires exact PDF-event fidelity 1.0")
        if not 1 <= self.fit_percent <= 98:
            raise ValueError("fit_percent must be in [1, 98]")
        if not 1 <= self.validation_percent <= 98:
            raise ValueError("validation_percent must be in [1, 98]")
        if self.fit_percent + self.validation_percent >= 100:
            raise ValueError("fit + validation must leave a non-empty canary split")


def split_for_location(
    measure: int,
    step: int,
    *,
    seed: int = 144,
    fit_percent: int = 60,
    validation_percent: int = 20,
) -> str:
    """Return a stable split without Python hash/random-state dependence."""
    m = int(measure)
    s = int(step)
    if m < 1 or not 0 <= s <= 15:
        raise ValueError(f"invalid rhythm location measure={m} step={s}")
    if not 1 <= int(fit_percent) <= 98:
        raise ValueError("fit_percent must be in [1, 98]")
    if not 1 <= int(validation_percent) <= 98:
        raise ValueError("validation_percent must be in [1, 98]")
    if int(fit_percent) + int(validation_percent) >= 100:
        raise ValueError("fit + validation must leave canary capacity")

    token = f"v144|{int(seed)}|{m}|{s}".encode("utf-8")
    bucket = int.from_bytes(hashlib.blake2s(token, digest_size=4).digest(), "big") % 100
    if bucket < int(fit_percent):
        return "fit"
    if bucket < int(fit_percent) + int(validation_percent):
        return "validation"
    return "canary"


def context_signature(row: Mapping[str, Any]) -> tuple[str, ...]:
    """Build only reference-free structural context from a candidate/runtime row."""
    measure = int(row["measure"])
    step = int(row["step"])
    if measure < 1 or not 0 <= step <= 15:
        raise ValueError(f"invalid rhythm row location measure={measure} step={step}")

    signatures = {
        f"measurePhase::{measure % 4}",
        f"section16::{(measure - 1) // 16}",
        f"stepParity::{step % 2}",
        f"stepQuarter::{step % 4}",
        f"measurePhaseStep::{measure % 4}:{step % 4}",
    }

    midi = row.get("midi")
    if midi is not None:
        midi_value = int(midi)
        register = "low" if midi_value < 48 else ("mid" if midi_value < 60 else "high")
        signatures.add(f"register::{register}")
        signatures.add(f"pitchClass::{midi_value % 12}")
        signatures.add(f"registerStep::{register}:{step % 4}")

    return tuple(sorted(signatures))


def _metric_value(metrics: Mapping[str, Any], name: str) -> float:
    gated = metrics.get("gatedMetrics") if isinstance(metrics.get("gatedMetrics"), Mapping) else metrics
    if name not in gated:
        raise ValueError(f"missing required metric {name}")
    value = float(gated[name])
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"metric {name} outside [0,1]: {value}")
    return value


def metric_vector(metrics: Mapping[str, Any]) -> dict[str, float]:
    return {name: _metric_value(metrics, name) for name in MUSICAL_METRICS}


def musical_floor(metrics: Mapping[str, Any]) -> float:
    values = metric_vector(metrics).values()
    return min(values)


def musical_mean(metrics: Mapping[str, Any]) -> float:
    values = tuple(metric_vector(metrics).values())
    return sum(values) / float(len(values))


def critical_mismatch_count(metrics: Mapping[str, Any]) -> int:
    if "criticalMismatchCount" not in metrics:
        raise ValueError("missing criticalMismatchCount")
    value = int(metrics["criticalMismatchCount"])
    if value < 0:
        raise ValueError("criticalMismatchCount must be non-negative")
    return value


def pdf_event_fidelity(metrics: Mapping[str, Any]) -> float:
    gated = metrics.get("gatedMetrics") if isinstance(metrics.get("gatedMetrics"), Mapping) else metrics
    if "pdfEventFidelity" not in gated:
        raise ValueError("missing pdfEventFidelity")
    return float(gated["pdfEventFidelity"])


def compare_metric_sets(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    maximum_regression: float,
) -> dict[str, Any]:
    baseline_vector = metric_vector(baseline)
    candidate_vector = metric_vector(candidate)
    deltas = {
        name: candidate_vector[name] - baseline_vector[name]
        for name in MUSICAL_METRICS
    }
    regressions = {
        name: delta
        for name, delta in deltas.items()
        if delta < -float(maximum_regression)
    }
    return {
        "deltas": deltas,
        "regressions": regressions,
        "pitchContentGain": deltas["pitchContentF1"],
        "musicalFloorGain": musical_floor(candidate) - musical_floor(baseline),
        "musicalMeanGain": musical_mean(candidate) - musical_mean(baseline),
    }


def evaluate_candidate_pair(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    *,
    config: ContextSplitConfig,
    canary: bool = False,
) -> dict[str, Any]:
    regression_limit = (
        config.maximum_canary_regression
        if canary
        else config.maximum_per_metric_regression
    )
    comparison = compare_metric_sets(
        baseline,
        candidate,
        maximum_regression=regression_limit,
    )
    mismatch_delta = critical_mismatch_count(candidate) - critical_mismatch_count(baseline)
    fidelity = pdf_event_fidelity(candidate)

    reasons: list[str] = []
    if fidelity != config.required_pdf_event_fidelity:
        reasons.append("pdf-event-fidelity-not-exact")
    if comparison["regressions"]:
        reasons.append("musical-metric-regression")
    if mismatch_delta > config.maximum_critical_mismatch_increase:
        reasons.append("critical-mismatch-regression")
    if not canary:
        if comparison["pitchContentGain"] < config.minimum_pitch_content_gain:
            reasons.append("insufficient-pitch-content-gain")
        if comparison["musicalFloorGain"] < config.minimum_musical_floor_gain:
            reasons.append("insufficient-musical-floor-gain")

    return {
        **comparison,
        "criticalMismatchDelta": mismatch_delta,
        "pdfEventFidelity": fidelity,
        "passed": not reasons,
        "reasons": reasons,
    }


__all__ = [
    "ContextSplitConfig",
    "MUSICAL_METRICS",
    "SPLITS",
    "compare_metric_sets",
    "context_signature",
    "critical_mismatch_count",
    "evaluate_candidate_pair",
    "metric_vector",
    "musical_floor",
    "musical_mean",
    "pdf_event_fidelity",
    "split_for_location",
]
