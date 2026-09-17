#!/usr/bin/env python3
"""Synthetic-only contract tests for the EGSet12 evaluation support code.

No EGSet12 corpus file, network resource, model inference, or reference result is
accessed by this test.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import egset12_note_birth_scorer_v1 as scorer
import egset12_positive_core_adapter_v1 as adapter
import v7_fail_closed_positive_core_v1 as positive_core


def require(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def test_state_mapping() -> None:
    require(adapter.map_composition_state(positive_core.POSITIVE_CORE_CANDIDATE) == "corroborated", "positive mapping")
    require(adapter.map_composition_state(positive_core.PROTECTION_REJECTED) == "rejected", "rejected mapping")
    require(adapter.map_composition_state(positive_core.UNRESOLVED_SUPPORT_OR_CONTEXT) == "insufficient", "unresolved mapping")


def test_exact_tolerance_and_one_to_one() -> None:
    refs = [
        {"midi": 60, "startSeconds": 1.000, "stableIndex": 0},
        {"midi": 60, "startSeconds": 1.080, "stableIndex": 1},
        {"midi": 64, "startSeconds": 2.000, "stableIndex": 2},
    ]
    preds = [
        {"midi": 60, "startSeconds": 0.950, "stableIndex": 0},  # exact 50 ms -> eligible
        {"midi": 60, "startSeconds": 1.030, "stableIndex": 1},  # can match only one 60 ref
        {"midi": 64, "startSeconds": 2.0500001, "stableIndex": 2},  # > 50 ms -> no match
    ]
    result = scorer.score_inventory(preds, refs)
    require(result["tp"] == 2, "two exact one-to-one matches")
    require(result["fp"] == 1, "one unmatched prediction")
    require(result["fn"] == 1, "one unmatched reference")


def test_maximum_cardinality_before_error() -> None:
    refs = [
        {"midi": 60, "startSeconds": 0.000, "stableIndex": 0},
        {"midi": 60, "startSeconds": 0.090, "stableIndex": 1},
    ]
    preds = [
        {"midi": 60, "startSeconds": 0.040, "stableIndex": 0},
        {"midi": 60, "startSeconds": 0.050, "stableIndex": 1},
    ]
    result = scorer.score_inventory(preds, refs)
    require(result["tp"] == 2, "maximum cardinality must be chosen")


def test_note_midi_parser_is_schema_driven() -> None:
    payload = {
        "annotations": [
            {"namespace": "tempo", "data": [{"time": 0.0, "duration": 0.0, "value": 120.0, "confidence": 1.0}]},
            {"namespace": "note_midi", "data": [
                {"time": 0.25, "duration": 0.1, "value": 64, "confidence": 1.0},
                {"time": 0.10, "duration": 0.1, "value": 60.0, "confidence": 1.0},
            ]},
        ]
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "synthetic.jams"
        path.write_text(json.dumps(payload), encoding="utf-8")
        rows = scorer.parse_note_midi_jams(path)
    require([(row["midi"], row["startSeconds"]) for row in rows] == [(60, 0.10), (64, 0.25)], "deterministic note_midi parse")


def test_composition_truth_table_no_rescue() -> None:
    for support in (False, True):
        for evidence in (False, True):
            for owner in (False, True):
                for kkt in (False, True):
                    row = positive_core.compose_available_flags(support, evidence, owner, kkt)
                    expected = (
                        positive_core.POSITIVE_CORE_CANDIDATE
                        if support and evidence and owner and kkt
                        else positive_core.UNRESOLVED_SUPPORT_OR_CONTEXT
                        if not support
                        else positive_core.PROTECTION_REJECTED
                    )
                    require(row["compositionState"] == expected, f"truth table mismatch {support,evidence,owner,kkt}")


def main() -> int:
    test_state_mapping()
    test_exact_tolerance_and_one_to_one()
    test_maximum_cardinality_before_error()
    test_note_midi_parser_is_schema_driven()
    test_composition_truth_table_no_rescue()
    print(json.dumps({
        "status": "PASS_SYNTHETIC_EGSET12_SUPPORT",
        "egset12CorpusAccessed": False,
        "networkAccessed": False,
        "modelInvoked": False,
        "referenceResultAccessed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
