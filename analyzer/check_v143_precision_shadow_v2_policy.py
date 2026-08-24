from __future__ import annotations

from v143_contextual_prune_precision_shadow_v2 import secondary_gate_decision


def check() -> None:
    # Non-harmonic observed secondaries: two independent physical views are enough.
    assert secondary_gate_decision(
        score_ratio=0.80,
        attack_ratio=0.80,
        body_ratio=0.80,
        harmonic_above_primary=False,
    )
    assert secondary_gate_decision(
        score_ratio=0.86,
        attack_ratio=0.83,
        body_ratio=0.79,
        harmonic_above_primary=False,
    )
    assert secondary_gate_decision(
        score_ratio=0.86,
        attack_ratio=0.79,
        body_ratio=0.83,
        harmonic_above_primary=False,
    )
    assert secondary_gate_decision(
        score_ratio=0.79,
        attack_ratio=0.83,
        body_ratio=0.83,
        harmonic_above_primary=False,
    )
    assert not secondary_gate_decision(
        score_ratio=0.86,
        attack_ratio=0.79,
        body_ratio=0.79,
        harmonic_above_primary=False,
    )

    # Known upper-harmonic family remains protected by the full legacy 0.92 AND gate.
    assert secondary_gate_decision(
        score_ratio=0.92,
        attack_ratio=0.92,
        body_ratio=0.92,
        harmonic_above_primary=True,
    )
    assert not secondary_gate_decision(
        score_ratio=0.99,
        attack_ratio=0.99,
        body_ratio=0.91,
        harmonic_above_primary=True,
    )
    assert not secondary_gate_decision(
        score_ratio=0.99,
        attack_ratio=0.91,
        body_ratio=0.99,
        harmonic_above_primary=True,
    )

    print("PASS precision shadow v2 envelope-balanced policy")


if __name__ == "__main__":
    check()
