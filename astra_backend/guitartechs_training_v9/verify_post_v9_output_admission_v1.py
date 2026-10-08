#!/usr/bin/env python3
"""No-media fixtures for the exact post-V9 admission/metrics path."""
import numpy as np
from post_v9_output_admission_audit_v1 import (
    admission_trace, masked_event_counts, summarize_capture, Q,
    MODELS, FOLDS,
)
from guitartechs_training_v4.objective_decoder import (
    decode_with_hysteresis, count_active_runs,
)
from guitartechs_real_training import real_training as base


def template(t=9):
    s = np.zeros((t, 6, 21), dtype=np.float32)
    s[:, :, 20] = 1.
    return s


def main():
    x = template()
    raw, states = admission_trace(x)
    assert raw["activeRunsAfterPrune"] == 0
    assert count_active_runs(states) == 0
    assert np.array_equal(states, decode_with_hysteresis(x))
    labels = np.full((6, len(x)), -1, dtype=np.int16)
    events = np.zeros((len(x), 6), dtype=np.float32)
    final, summary = summarize_capture(x, events, labels)
    assert summary["predictedEvents"] == 0
    assert summary["truePositiveEvents"] == 0
    assert summary["stateArgmaxActiveFraction"] == 0.
    assert summary["finiteNormalized"]
    assert summary["silenceProbabilityQuantiles"] == [1.]*len(Q)

    # Unchanged V4 start and active run; event rank cannot rescue a nonexistent run.
    active = template()
    active[2:6, 0, 20] = .05
    active[2:6, 0, 3] = .95
    trace, admitted = admission_trace(active)
    assert trace["activeRunsAfterPrune"] == 1
    assert trace["acceptedStrongStarts"] == 1
    assert trace["activeRunsBeforeGapMerge"] == 1
    assert count_active_runs(admitted) == 1
    final, summary = summarize_capture(active, events, labels)
    assert summary["predictedEvents"] == 1
    assert summary["referenceEvents"] == 0
    assert summary["truePositiveEvents"] == 0
    assert base.capture_metrics(final, labels)["f1"] == 0.

    # Zero F1 can coexist with a real emitted prediction and a real wrong reference.
    ref = np.full((6, len(x)), -1, dtype=np.int16)
    ref[0, 2:6] = 5
    final, summary = summarize_capture(active, events, ref)
    assert summary["predictedEvents"] == 1
    assert summary["referenceEvents"] == 1
    assert summary["truePositiveEvents"] == 0
    assert base.capture_metrics(final, ref)["f1"] == 0.
    ref[0, 2:6] = 3
    matched = masked_event_counts(final, ref)
    assert matched["predictedEvents"] == matched["referenceEvents"] == matched["truePositiveEvents"] == 1

    # Masking must remove predicted and reference events without mutating inputs.
    ref[0, 2:6] = base.MASK
    assert masked_event_counts(final, ref)["predictedEvents"] == 0
    assert (final[2:6, 0] == 3).all()

    # Strong/confirmed thresholds must be frozen, and invalid distributions fail.
    assert len(FOLDS) == 2 and len(MODELS) == 2
    bad = template()
    bad[0, 0, 20] = .8
    try:
        summarize_capture(bad, events, labels)
    except RuntimeError:
        pass
    else:
        raise AssertionError("normalization guard did not fail")
    print("POST_V9_MODEL_FREE_ADMISSION_FIXTURES_PASS")


if __name__ == "__main__":
    main()
