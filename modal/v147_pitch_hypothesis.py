from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

MIN_GUITAR_MIDI = 40
MAX_GUITAR_MIDI = 88
OCTAVE_WEIGHT = 0.25
MIN_ALTERNATE_FUNDAMENTAL_DB = 3.0
MIN_SCORE_MARGIN_DB = 3.0
MIN_FUNDAMENTAL_MARGIN_DB = 2.0
SCORE_ROUND_DIGITS = 6

CANDIDATE_BAND_SEMITONES = 0.30
BASELINE_WINDOW_SEMITONES = 2.0
BASELINE_EXCLUSION_SEMITONES = 0.75
DB_FLOOR = 1e-8


def candidate_midis(original_midi: int) -> tuple[int, ...]:
    """Return the frozen V147 {-1, 0, +1} candidate family in range."""
    if isinstance(original_midi, bool) or not isinstance(original_midi, int):
        return ()
    return tuple(
        midi
        for midi in (original_midi - 1, original_midi, original_midi + 1)
        if MIN_GUITAR_MIDI <= midi <= MAX_GUITAR_MIDI
    )


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def score_candidate_evidence(fundamental_delta_db: Any, octave_delta_db: Any) -> float | None:
    """Apply the frozen V147 score without changing the evidence itself."""
    fundamental = _finite_number(fundamental_delta_db)
    octave = _finite_number(octave_delta_db)
    if fundamental is None or octave is None:
        return None
    return fundamental + OCTAVE_WEIGHT * max(0.0, octave)


def _result(
    original_midi: Any,
    selected_midi: Any,
    reason: str,
    candidates: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    changed = (
        isinstance(original_midi, int)
        and not isinstance(original_midi, bool)
        and isinstance(selected_midi, int)
        and not isinstance(selected_midi, bool)
        and selected_midi != original_midi
    )
    semitone_delta = selected_midi - original_midi if changed else 0
    return {
        "originalMidi": original_midi,
        "selectedMidi": selected_midi,
        "changed": changed,
        "semitoneDelta": semitone_delta,
        "reason": reason,
        "candidates": [dict(row) for row in candidates],
    }


def choose_pitch_hypothesis(
    original_midi: Any,
    evidence_by_midi: Mapping[int, Mapping[str, Any]] | Any,
) -> dict[str, Any]:
    """Choose a bounded V147 pitch hypothesis, failing closed to original MIDI.

    Expected evidence rows contain ``fundamentalDeltaDb`` and ``octaveDeltaDb``.
    Missing, malformed, non-finite, weak, ambiguous, or tied evidence preserves
    the original MIDI exactly.
    """
    candidates = candidate_midis(original_midi)
    if not candidates:
        return _result(original_midi, original_midi, "invalid-original-midi")
    if not isinstance(evidence_by_midi, Mapping):
        return _result(original_midi, original_midi, "malformed-evidence")

    scored: list[dict[str, Any]] = []
    for midi in candidates:
        row = evidence_by_midi.get(midi)
        if not isinstance(row, Mapping):
            return _result(original_midi, original_midi, "missing-or-malformed-candidate")

        fundamental = _finite_number(row.get("fundamentalDeltaDb"))
        octave = _finite_number(row.get("octaveDeltaDb"))
        score = score_candidate_evidence(fundamental, octave)
        if fundamental is None or octave is None or score is None:
            return _result(original_midi, original_midi, "non-finite-evidence")

        scored.append(
            {
                "midi": midi,
                "fundamentalDeltaDb": round(fundamental, SCORE_ROUND_DIGITS),
                "octaveDeltaDb": round(octave, SCORE_ROUND_DIGITS),
                "scoreDb": round(score, SCORE_ROUND_DIGITS),
                "_rawFundamentalDeltaDb": fundamental,
                "_rawScoreDb": score,
            }
        )

    rounded_best = max(row["scoreDb"] for row in scored)
    best_rows = [row for row in scored if row["scoreDb"] == rounded_best]
    public_rows = [
        {key: value for key, value in row.items() if not key.startswith("_")}
        for row in scored
    ]

    if len(best_rows) != 1:
        return _result(original_midi, original_midi, "tied-best-score", public_rows)

    best = best_rows[0]
    if best["midi"] == original_midi:
        return _result(original_midi, original_midi, "original-best", public_rows)

    original = next(row for row in scored if row["midi"] == original_midi)
    alternate_fundamental = best["_rawFundamentalDeltaDb"]
    original_fundamental = original["_rawFundamentalDeltaDb"]
    alternate_score = best["_rawScoreDb"]
    original_score = original["_rawScoreDb"]

    if alternate_fundamental < MIN_ALTERNATE_FUNDAMENTAL_DB:
        return _result(original_midi, original_midi, "alternate-fundamental-too-weak", public_rows)
    if alternate_score < original_score + MIN_SCORE_MARGIN_DB:
        return _result(original_midi, original_midi, "alternate-score-margin-too-small", public_rows)
    if alternate_fundamental < original_fundamental + MIN_FUNDAMENTAL_MARGIN_DB:
        return _result(original_midi, original_midi, "alternate-fundamental-margin-too-small", public_rows)

    selected_midi = int(best["midi"])
    if not (MIN_GUITAR_MIDI <= selected_midi <= MAX_GUITAR_MIDI):
        return _result(original_midi, original_midi, "alternate-out-of-range", public_rows)

    return _result(original_midi, selected_midi, "alternate-supported", public_rows)


def _band_delta_db(
    cqt_magnitude: Any,
    midi_bins: Any,
    frame_indices: Sequence[int],
    center_midi: float,
) -> float | None:
    """Extract the frozen width-normalized median band-vs-local-baseline delta."""
    try:
        import numpy as np
    except Exception:
        return None

    try:
        cqt = np.asarray(cqt_magnitude, dtype=float)
        bins = np.asarray(midi_bins, dtype=float)
    except Exception:
        return None

    if cqt.ndim != 2 or bins.ndim != 1 or cqt.shape[0] != bins.shape[0]:
        return None
    if cqt.shape[0] == 0 or cqt.shape[1] == 0 or not frame_indices:
        return None
    if not np.all(np.isfinite(cqt)) or not np.all(np.isfinite(bins)):
        return None
    if np.any(cqt < 0.0):
        return None

    frames: list[int] = []
    for frame in frame_indices:
        if isinstance(frame, bool) or not isinstance(frame, int):
            return None
        if frame < 0 or frame >= cqt.shape[1]:
            return None
        frames.append(frame)
    if not frames:
        return None

    distance = np.abs(bins - float(center_midi))
    candidate_mask = distance <= CANDIDATE_BAND_SEMITONES
    baseline_mask = (
        (distance <= BASELINE_WINDOW_SEMITONES)
        & (distance > BASELINE_EXCLUSION_SEMITONES)
    )
    candidate_count = int(np.count_nonzero(candidate_mask))
    if candidate_count == 0 or not np.any(baseline_mask):
        return None

    deltas: list[float] = []
    for frame in frames:
        band_magnitude = float(np.sum(cqt[candidate_mask, frame]))
        baseline_per_bin = float(np.median(cqt[baseline_mask, frame]))
        baseline_magnitude = baseline_per_bin * candidate_count
        band_db = 20.0 * math.log10(max(band_magnitude, DB_FLOOR))
        baseline_db = 20.0 * math.log10(max(baseline_magnitude, DB_FLOOR))
        delta = band_db - baseline_db
        if not math.isfinite(delta):
            return None
        deltas.append(delta)

    return float(np.median(np.asarray(deltas, dtype=float)))


def extract_candidate_evidence_from_cqt(
    cqt_magnitude: Any,
    midi_bins: Any,
    frame_indices: Sequence[int],
    original_midi: Any,
) -> dict[int, dict[str, float]] | None:
    """Extract V147 candidate evidence from an already-computed magnitude CQT."""
    candidates = candidate_midis(original_midi)
    if not candidates:
        return None

    try:
        import numpy as np

        bins = np.asarray(midi_bins, dtype=float)
    except Exception:
        return None
    if bins.ndim != 1 or bins.size == 0 or not np.all(np.isfinite(bins)):
        return None

    evidence: dict[int, dict[str, float]] = {}
    min_bin = float(np.min(bins))
    max_bin = float(np.max(bins))

    for midi in candidates:
        fundamental = _band_delta_db(cqt_magnitude, bins, frame_indices, float(midi))
        if fundamental is None:
            return None

        octave_center = float(midi + 12)
        octave_has_full_window = (
            min_bin <= octave_center - BASELINE_WINDOW_SEMITONES
            and max_bin >= octave_center + BASELINE_WINDOW_SEMITONES
        )
        if octave_has_full_window:
            octave = _band_delta_db(cqt_magnitude, bins, frame_indices, octave_center)
            if octave is None:
                return None
        else:
            octave = 0.0

        evidence[midi] = {
            "fundamentalDeltaDb": round(float(fundamental), SCORE_ROUND_DIGITS),
            "octaveDeltaDb": round(float(octave), SCORE_ROUND_DIGITS),
        }

    return evidence


def choose_pitch_hypothesis_from_cqt(
    original_midi: Any,
    cqt_magnitude: Any,
    midi_bins: Any,
    frame_indices: Sequence[int],
) -> dict[str, Any]:
    """Extract prepared-CQT evidence and apply the frozen fail-closed decision."""
    evidence = extract_candidate_evidence_from_cqt(
        cqt_magnitude,
        midi_bins,
        frame_indices,
        original_midi,
    )
    if evidence is None:
        return _result(original_midi, original_midi, "cqt-evidence-unavailable")
    return choose_pitch_hypothesis(original_midi, evidence)
