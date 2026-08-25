from __future__ import annotations

import copy

from v143_precision_replay_artifact_validator import (
    ReplayArtifactValidationError,
    _self_test_product,
    validate_product,
)


def _must_reject(product: dict, label: str) -> None:
    try:
        validate_product(product)
    except ReplayArtifactValidationError:
        return
    raise AssertionError(f"validator accepted corrupted replay evidence: {label}")


def check() -> None:
    base = _self_test_product()
    assert validate_product(copy.deepcopy(base))["passed"] is True

    # Force the two-view minimum to change while leaving the stored aggregate
    # evidence untouched. Increasing only one equal view can leave min(A, B)
    # unchanged, so use a decrease that must alter the reconstructed aggregate.
    broken_view = copy.deepcopy(base)
    broken_view["precisionReplayEvidence"]["eligibleAttacks"][0]["candidates"][0]["viewA"]["attack"] -= 0.20
    _must_reject(broken_view, "two-view aggregate mismatch")

    broken_strength = copy.deepcopy(base)
    broken_strength["precisionReplayEvidence"]["eligibleAttacks"][0]["precisionStrength"] += 0.25
    _must_reject(broken_strength, "precision strength mismatch")

    broken_grid = copy.deepcopy(base)
    broken_grid["precisionReplayEvidence"]["eligibleAttacks"][0]["gridTime"] += 0.25
    _must_reject(broken_grid, "grid/onset error mismatch")

    print("PASS v143 precision replay corruption rejection")


if __name__ == "__main__":
    check()
