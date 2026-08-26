from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
import unittest

MODAL_DIR = Path(__file__).resolve().parents[1]
if str(MODAL_DIR) not in sys.path:
    sys.path.insert(0, str(MODAL_DIR))

from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_staged_selector import (  # noqa: E402
    gate_locked_candidate,
    lock_fit_candidate,
    staged_select_candidate,
)


MUSICAL = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "exactVoicingTolerantF1",
)


def metrics(value: float = 0.2, *, pitch: float | None = None, critical: int = 100):
    gated = {name: value for name in MUSICAL}
    if pitch is not None:
        gated["pitchContentF1"] = pitch
    gated["pdfEventFidelity"] = 1.0
    return {"gatedMetrics": gated, "criticalMismatchCount": critical}


def safety():
    return {
        "v5Modified": False,
        "productionModified": False,
        "mainModified": False,
        "runtimeReferenceInputUsed": False,
        "modalGpuInvoked": False,
        "deterministic": True,
        "baselineGeneratedMeasureSetPreserved": True,
    }


def candidate(
    name: str,
    *,
    fit=None,
    validation=None,
    canary=None,
    policy: str = "test-policy",
):
    item = {
        "name": name,
        "policy": policy,
        "fit": fit if fit is not None else metrics(),
        "safety": safety(),
        "holdout": None,
    }
    if validation is not None:
        item["validation"] = validation
    if canary is not None:
        item["canary"] = canary
    return item


class StagedSelectorTests(unittest.TestCase):
    def setUp(self):
        self.config = ContextSplitConfig(
            minimum_pitch_content_gain=0.005,
            minimum_musical_floor_gain=0.0,
            maximum_per_metric_regression=0.0,
            maximum_canary_regression=0.0,
            maximum_critical_mismatch_increase=0,
            required_pdf_event_fidelity=1.0,
            holdout_must_remain_closed=True,
        )

    def baseline(self):
        return candidate(
            "no-prune",
            fit=metrics(0.2, critical=100),
            validation=metrics(0.2, critical=100),
            canary=metrics(0.2, critical=100),
            policy="baseline",
        )

    def test_fit_lock_never_reads_validation_or_canary(self):
        baseline = self.baseline()
        better_fit = candidate("better-fit", fit=metrics(0.21, pitch=0.24, critical=85))
        weaker_fit = candidate("weaker-fit", fit=metrics(0.205, pitch=0.22, critical=90))

        better_fit["validation"] = "INVALID-ON-PURPOSE"
        better_fit["canary"] = None
        weaker_fit["validation"] = {"also": "irrelevant"}
        weaker_fit["canary"] = "irrelevant"

        locked = lock_fit_candidate(
            [baseline, weaker_fit, better_fit], config=self.config
        )
        self.assertEqual(locked["locked"], "better-fit")
        self.assertTrue(locked["fitOnlyRanking"])
        self.assertFalse(locked["validationReadDuringLock"])
        self.assertFalse(locked["canaryReadDuringLock"])
        self.assertTrue(locked["baselineGeneratedMeasureSetPreservationRequired"])

    def test_validation_failure_falls_back_without_trying_second_candidate(self):
        baseline = self.baseline()
        first = candidate(
            "first",
            fit=metrics(0.21, pitch=0.24, critical=85),
            validation=metrics(0.19, pitch=0.21, critical=90),
        )
        second = candidate(
            "second",
            fit=metrics(0.205, pitch=0.22, critical=90),
            validation=metrics(0.21, pitch=0.22, critical=90),
            canary=metrics(0.21, pitch=0.22, critical=90),
        )

        result = staged_select_candidate([baseline, second, first], config=self.config)
        self.assertEqual(result["fitLock"]["locked"], "first")
        self.assertEqual(result["selected"], "no-prune")
        self.assertEqual(result["stoppedAt"], "validation")
        self.assertIsNone(result["canary"])
        self.assertFalse(result["alternateAfterGateFailureAllowed"])

    def test_canary_failure_falls_back_without_alternate_selection(self):
        baseline = self.baseline()
        first = candidate(
            "first",
            fit=metrics(0.21, pitch=0.24, critical=85),
            validation=metrics(0.21, pitch=0.22, critical=90),
            canary=metrics(0.19, pitch=0.21, critical=90),
        )
        second = candidate(
            "second",
            fit=metrics(0.205, pitch=0.22, critical=90),
            validation=metrics(0.22, pitch=0.23, critical=80),
            canary=metrics(0.22, pitch=0.23, critical=80),
        )

        result = staged_select_candidate([baseline, second, first], config=self.config)
        self.assertEqual(result["fitLock"]["locked"], "first")
        self.assertEqual(result["selected"], "no-prune")
        self.assertEqual(result["stoppedAt"], "canary")
        self.assertFalse(result["promotionAllowed"])
        self.assertFalse(result["alternateAfterGateFailureAllowed"])

    def test_locked_candidate_can_pass_both_gates(self):
        baseline = self.baseline()
        good = candidate(
            "good",
            fit=metrics(0.21, pitch=0.24, critical=85),
            validation=metrics(0.21, pitch=0.22, critical=90),
            canary=metrics(0.205, pitch=0.21, critical=95),
        )
        result = staged_select_candidate([baseline, good], config=self.config)
        self.assertEqual(result["selected"], "good")
        self.assertEqual(result["stoppedAt"], "complete")
        self.assertTrue(result["promotionAllowed"])
        self.assertTrue(result["validation"]["passed"])
        self.assertTrue(result["canary"]["passed"])

    def test_no_fit_winner_does_not_read_later_stages(self):
        baseline = self.baseline()
        weak = candidate("weak", fit=metrics(0.2, pitch=0.203, critical=100))
        weak["validation"] = "INVALID-ON-PURPOSE"
        weak["canary"] = "INVALID-ON-PURPOSE"
        result = staged_select_candidate([baseline, weak], config=self.config)
        self.assertEqual(result["selected"], "no-prune")
        self.assertEqual(result["stoppedAt"], "fit")
        self.assertIsNone(result["validation"])
        self.assertIsNone(result["canary"])

    def test_validation_gate_does_not_require_minimum_pitch_gain(self):
        baseline = self.baseline()
        locked = candidate(
            "locked",
            fit=metrics(0.21, pitch=0.24, critical=85),
            validation=metrics(0.2, pitch=0.2, critical=100),
            canary=metrics(0.2, pitch=0.2, critical=100),
        )
        gate = gate_locked_candidate(
            baseline, locked, stage="validation", config=self.config
        )
        self.assertTrue(gate["passed"])
        self.assertEqual(gate["pitchContentGain"], 0.0)

    def test_safety_failure_cannot_fit_lock(self):
        baseline = self.baseline()
        unsafe = candidate("unsafe", fit=metrics(0.21, pitch=0.24, critical=80))
        unsafe = deepcopy(unsafe)
        unsafe["safety"]["runtimeReferenceInputUsed"] = True
        result = lock_fit_candidate([baseline, unsafe], config=self.config)
        self.assertEqual(result["locked"], "no-prune")
        evaluation = result["evaluations"][0]
        self.assertFalse(evaluation["passed"])
        self.assertIn("reference-used-as-runtime-input", evaluation["reasons"])

    def test_measure_set_loss_cannot_fit_lock_even_with_large_musical_gain(self):
        baseline = self.baseline()
        drops_measure = candidate(
            "drops-measure",
            fit=metrics(0.24, pitch=0.30, critical=50),
            validation=metrics(0.24, pitch=0.30, critical=50),
            canary=metrics(0.24, pitch=0.30, critical=50),
        )
        drops_measure["safety"]["baselineGeneratedMeasureSetPreserved"] = False

        result = lock_fit_candidate([baseline, drops_measure], config=self.config)
        self.assertEqual(result["locked"], "no-prune")
        evaluation = result["evaluations"][0]
        self.assertFalse(evaluation["passed"])
        self.assertGreater(evaluation["pitchContentGain"], 0.005)
        self.assertIn(
            "baseline-generated-measure-set-not-preserved",
            evaluation["reasons"],
        )

    def test_missing_measure_preservation_proof_cannot_fit_lock(self):
        baseline = self.baseline()
        unproven = candidate("unproven", fit=metrics(0.24, pitch=0.30, critical=50))
        del unproven["safety"]["baselineGeneratedMeasureSetPreserved"]

        result = lock_fit_candidate([baseline, unproven], config=self.config)
        self.assertEqual(result["locked"], "no-prune")
        self.assertIn(
            "baseline-generated-measure-set-not-preserved",
            result["evaluations"][0]["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
