"""OFFLINE REVIEW ONLY: synthetic proof of first-add ancestry limitations.

No real project repository, training media, launch receipt or runner is involved.
This is not a deployable single-use guard or an authorization mechanism.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

MARKER = "synthetic-only-claim-marker.txt"  # NEVER the real trigger path


def git(directory: Path, *args: str) -> str:
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    result = subprocess.run(
        ["git", *args], cwd=directory, env=env, check=True,
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def new_repo(directory: Path) -> None:
    git(directory, "init", "-q", "-b", "offline-synthetic-main")
    git(directory, "config", "user.email", "synthetic@example.invalid")
    git(directory, "config", "user.name", "Synthetic Offline Tester")
    (directory / "README.txt").write_text("offline only\n")
    git(directory, "add", "README.txt")
    git(directory, "commit", "-qm", "synthetic base")


def add_first_marker(directory: Path) -> None:
    (directory / MARKER).write_text("synthetic marker\n")
    git(directory, "add", MARKER)
    git(directory, "commit", "-qm", "synthetic first addition")


def workflow_ancestry_guard(directory: Path, run_attempt: str = "1") -> bool:
    """Faithful abstract of current history and first-attempt checks, fake path."""
    if run_attempt != "1":
        return False
    history = git(directory, "rev-list", "--count", "HEAD", "--", MARKER)
    changed = git(directory, "diff-tree", "--no-commit-id", "--name-status", "-r", "--root", "HEAD", "--", MARKER)
    return history == "1" and changed == "A\t" + MARKER


class SyntheticOnlyReview(unittest.TestCase):
    def test_first_addition_passes_but_edit_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            new_repo(d)
            add_first_marker(d)
            self.assertTrue(workflow_ancestry_guard(d))
            self.assertFalse(workflow_ancestry_guard(d, run_attempt="2"))
            (d / MARKER).write_text("edited synthetic marker\n")
            git(d, "add", MARKER)
            git(d, "commit", "-qm", "synthetic edit")
            self.assertFalse(workflow_ancestry_guard(d))

    def test_duplicate_first_attempt_events_both_pass_same_commit(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            new_repo(d)
            add_first_marker(d)
            one_sha = git(d, "rev-parse", "HEAD")
            # Two distinct first-attempt *events* at exactly the same commit.
            # GITHUB_RUN_ATTEMPT == 1 is scoped to an individual run, not all runs.
            accepted_events = [workflow_ancestry_guard(d, "1") for _ in ("event-A", "event-B")]
            self.assertEqual(accepted_events, [True, True])
            self.assertEqual(git(d, "rev-parse", "HEAD"), one_sha)

    def test_rewritten_history_can_pass_first_addition_again(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            new_repo(d)
            add_first_marker(d)
            first_sha = git(d, "rev-parse", "HEAD")
            self.assertTrue(workflow_ancestry_guard(d))
            git(d, "switch", "-q", "--orphan", "synthetic-rewritten-history")
            (d / MARKER).write_text("synthetic marker in separate history\n")
            git(d, "add", MARKER)
            git(d, "commit", "-qm", "independent synthetic root")
            self.assertNotEqual(git(d, "rev-parse", "HEAD"), first_sha)
            self.assertTrue(workflow_ancestry_guard(d))

    def test_atomic_claim_contract_would_reject_second_event(self):
        # Abstract model only: must be implemented by a separate trusted,
        # durable, shared and linearizable backend before any real use.
        state = "UNUSED"
        def compare_and_set(expected: str, replacement: str) -> bool:
            nonlocal state
            if state != expected:
                return False
            state = replacement
            return True
        self.assertTrue(compare_and_set("UNUSED", "CONSUMED"))
        self.assertFalse(compare_and_set("UNUSED", "CONSUMED"))
        self.assertEqual(state, "CONSUMED")

    def test_historical_budget_is_not_a_worst_case_bound(self):
        # Frozen historical timing receipt, NOT measurements in this run.
        historical = Decimal("11023.169")
        ceiling = Decimal("18000")
        illustrative_gap = ceiling - historical
        self.assertEqual(illustrative_gap, Decimal("6976.831"))
        self.assertEqual(illustrative_gap / Decimal("60"), Decimal("116.2805166666666666666666667"))
        self.assertGreater(illustrative_gap, Decimal(0))
        # Positive illustrative gap cannot validate unknown H1 evaluation,
        # setup, resource peaks or failure reserve.


if __name__ == "__main__":
    unittest.main(verbosity=2)
