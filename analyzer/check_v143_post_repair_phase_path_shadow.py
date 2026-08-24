from __future__ import annotations

import subprocess

from v143_post_repair_phase_path_shadow import (
    PhasePathWindow,
    local_window_specs,
    summarize_phase_path,
)


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _window(index: int, phase: int, *, strong: bool = True) -> PhasePathWindow:
    start = index * 16
    end = start + 64
    return PhasePathWindow(
        name=f"w{index}",
        start_beat_index=start,
        end_beat_index_exclusive=end,
        winner_downbeat_index_mod4=phase,
        confidence=0.4 if strong else 0.1,
        consensus_signal_count=2 if strong else 1,
        stable_across_halves=bool(strong),
        signal_winners={"accent": phase, "bassChange": phase},
        candidate_combined_scores={0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0},
    )


def main() -> int:
    specs = local_window_specs(449)
    assert len(specs) >= 20, specs
    assert all(start % 4 == 0 for _name, start, _end in specs)
    assert all(end > start for _name, start, end in specs)
    assert specs[0][1] == 0
    assert specs[-1][2] == 449

    # Strong windows of one phase form a contiguous run. A weak/ambiguous window
    # breaks that run, and a later strong phase creates a separate run/transition.
    values = (
        _window(0, 1),
        _window(1, 1),
        _window(2, 1, strong=False),
        _window(3, 2),
        _window(4, 2),
    )
    summary = summarize_phase_path(values)
    assert summary["windowCount"] == 5, summary
    assert summary["strongWindowCount"] == 4, summary
    assert summary["strongPhaseWindowCounts"] == {"1": 2, "2": 2}, summary
    assert summary["multipleStrongPhasesObserved"] is True, summary
    assert len(summary["strongRuns"]) == 2, summary
    assert summary["strongRuns"][0]["phase"] == 1, summary
    assert summary["strongRuns"][1]["phase"] == 2, summary
    assert summary["strongTransitionCount"] == 1, summary
    assert summary["strongTransitions"][0]["fromPhase"] == 1, summary
    assert summary["strongTransitions"][0]["toPhase"] == 2, summary
    assert summary["referenceFree"] is True
    assert summary["runtimeLabelsRequired"] is False
    assert summary["productionModified"] is False

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 post-repair local phase path checker: PASS")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
