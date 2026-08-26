from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

MODAL_ROOT = Path(__file__).resolve().parents[1]
if str(MODAL_ROOT) not in sys.path:
    sys.path.insert(0, str(MODAL_ROOT))

from v144_rhythm_context_split_policy import ContextSplitConfig  # noqa: E402
from v144_rhythm_context_split_selector import select_candidate  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "v144_rhythm_context_split_reference.json"


class ContextSplitSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.config = ContextSplitConfig()

    def test_fixture_selects_context_preserve(self) -> None:
        result = select_candidate(self.payload["candidates"], config=self.config)
        self.assertEqual(result["selected"], self.payload["expectedSelected"])
        self.assertTrue(result["promotionAllowed"])
        self.assertFalse(result["holdoutOpened"])
        self.assertFalse(result["v5Modified"])

    def test_canary_regression_rejects_context_prune(self) -> None:
        result = select_candidate(self.payload["candidates"], config=self.config)
        prune = next(item for item in result["evaluations"] if item["name"] == "context-prune")
        self.assertFalse(prune["passed"])
        self.assertTrue(any(reason.startswith("canary:") for reason in prune["reasons"]))

    def test_falls_back_to_no_prune_when_gain_disappears(self) -> None:
        payload = copy.deepcopy(self.payload)
        baseline = payload["candidates"][0]
        for candidate in payload["candidates"][1:]:
            candidate["calibration"] = copy.deepcopy(baseline["calibration"])
            candidate["canary"] = copy.deepcopy(baseline["canary"])
        result = select_candidate(payload["candidates"], config=self.config)
        self.assertEqual(result["selected"], "no-prune")
        self.assertFalse(result["promotionAllowed"])
        self.assertEqual(result["selectedReason"], "deterministic-no-prune-fallback")

    def test_candidate_with_open_holdout_is_rejected(self) -> None:
        payload = copy.deepcopy(self.payload)
        candidate = payload["candidates"][1]
        candidate["holdout"] = {"score": 1.0}
        result = select_candidate(payload["candidates"], config=self.config)
        selected_eval = next(item for item in result["evaluations"] if item["name"] == "context-preserve")
        self.assertFalse(selected_eval["passed"])
        self.assertIn("holdout-opened-before-promotion-gate", selected_eval["reasons"])


if __name__ == "__main__":
    unittest.main()
