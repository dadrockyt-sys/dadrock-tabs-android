from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parent
HELPER_PATH = ROOT / "v143_precision_polyphony_boundary.py"
ADAPTER_PATH = ROOT / "v143_contextual_prune_precision_candidate_events.py"


class _Decision:
    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


def _extract_functions(path: Path, names: set[str], namespace: dict[str, Any]) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    selected = [
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    missing = names.difference(node.name for node in selected)
    if missing:
        raise AssertionError(f"Missing expected functions in {path.name}: {sorted(missing)}")
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(module, str(path), "exec"), namespace)
    return {name: namespace[name] for name in names}


def _playable_voicing(midis: Sequence[int]) -> dict[int, dict[str, Any]] | None:
    if len(set(int(midi) for midi in midis)) > 6:
        return None
    return {
        int(midi): {
            "stringIndex": index,
            "stringName": f"S{index + 1}",
            "fret": max(0, int(midi) - 40 - index * 5),
        }
        for index, midi in enumerate(midis)
    }


def _test_helper_never_readmits_pruned_pitch() -> None:
    namespace = {
        "Any": Any,
        "Mapping": Mapping,
        "Sequence": Sequence,
        "MAX_CHORD_NOTES": 6,
        "resolve_joint_chord_voicing": _playable_voicing,
        "PrecisionPolyphonyDecision": _Decision,
    }
    functions = _extract_functions(
        HELPER_PATH,
        {"_ranked_midis", "resolve_precision_polyphony"},
        namespace,
    )
    resolve = functions["resolve_precision_polyphony"]

    evidence = {
        60: {"score": 3.0, "attack": 2.0, "body": 1.0},
        64: {"score": 2.5, "attack": 1.8, "body": 0.9},
        # Deliberately strong, positive, playable, but precision-v2-pruned.
        67: {"score": 9.0, "attack": 8.0, "body": 7.0},
    }
    decision = resolve(
        primary_midi=60,
        precision_midis=(60, 64),
        observed_midis=(60, 64, 67),
        evidence=evidence,
        positive_attack_floor=0.0,
        positive_body_floor=-0.25,
        harmonic_intervals=(12, 19, 24, 28, 31, 36),
    )
    assert set(decision.candidate_midis) == {60, 64}
    assert set(decision.selected_midis).issubset({60, 64})
    assert 67 not in set(decision.selected_midis)
    assert not decision.recovered_midis


def _test_adapter_rejects_hostile_recovery_decisions() -> None:
    namespace = {"Any": Any, "Sequence": Sequence}
    check = _extract_functions(
        ADAPTER_PATH,
        {"_assert_preservation_only_decision"},
        namespace,
    )["_assert_preservation_only_decision"]

    good = SimpleNamespace(
        candidate_midis=(60, 64),
        recovered_midis=frozenset(),
        dropped_midis=frozenset({64}),
    )
    check(precision_midis=(60, 64), selected_midis=(60,), decision=good)

    hostile_cases = (
        SimpleNamespace(
            candidate_midis=(60, 64, 67),
            recovered_midis=frozenset({67}),
            dropped_midis=frozenset(),
        ),
        SimpleNamespace(
            candidate_midis=(60, 64),
            recovered_midis=frozenset(),
            dropped_midis=frozenset(),
        ),
        SimpleNamespace(
            candidate_midis=(60, 64),
            recovered_midis=frozenset({67}),
            dropped_midis=frozenset(),
        ),
    )
    hostile_selected = ((60, 67), (60, 67), (60, 64))
    for decision, selected in zip(hostile_cases, hostile_selected, strict=True):
        try:
            check(
                precision_midis=(60, 64),
                selected_midis=selected,
                decision=decision,
            )
        except RuntimeError:
            continue
        raise AssertionError(
            f"Hostile recovery decision was accepted: {decision.__dict__}"
        )


def _test_legacy_recovery_fields_are_hard_false() -> None:
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    required_false_literals = (
        '"feasibilityRecoveryEligible": False',
        '"feasibilityRecovered": False',
        '"feasibilityRecoveredSecondary": False',
        '"recoveredPitchCount": 0',
        '"recoveryPermitted": False',
    )
    for literal in required_false_literals:
        if literal not in source:
            raise AssertionError(f"Missing preservation literal: {literal}")
    if "midi not in precision_set and not recovered" in source:
        raise AssertionError("Legacy recovery escape hatch is still present")


def main() -> None:
    _test_helper_never_readmits_pruned_pitch()
    _test_adapter_rejects_hostile_recovery_decisions()
    _test_legacy_recovery_fields_are_hard_false()
    print("V143 precision polyphony preservation validation: PASS")


if __name__ == "__main__":
    main()
