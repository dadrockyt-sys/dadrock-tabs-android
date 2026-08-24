from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

EXPECTED_ORIGINAL_PITCH_COUNT = 7535
EXPECTED_RETAINED_ATTACK_COUNT = 725
EXPECTED_RETAINED_PITCH_COUNT = 987
EXPECTED_PROMOTION_COUNT = 144
EXPECTED_SUPPRESSED_PITCH_COUNT = 6548


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return float(numerator / denominator)


def build_report(product: Mapping[str, Any]) -> dict[str, Any]:
    diagnostics = product.get("precisionDiagnostics") or {}
    original = int(diagnostics.get("originalPitchHypothesisCount") or -1)
    attacks = int(diagnostics.get("retainedAttackCount") or -1)
    retained = int(diagnostics.get("retainedPitchHypothesisCount") or -1)
    promotions = int(diagnostics.get("fundamentalPromotionCount") or -1)
    suppressed = int(diagnostics.get("suppressedPitchCount") or -1)

    expected = {
        "originalPitchHypothesisCount": EXPECTED_ORIGINAL_PITCH_COUNT,
        "retainedAttackCount": EXPECTED_RETAINED_ATTACK_COUNT,
        "retainedPitchHypothesisCount": EXPECTED_RETAINED_PITCH_COUNT,
        "fundamentalPromotionCount": EXPECTED_PROMOTION_COUNT,
        "suppressedPitchCount": EXPECTED_SUPPRESSED_PITCH_COUNT,
    }
    observed = {
        "originalPitchHypothesisCount": original,
        "retainedAttackCount": attacks,
        "retainedPitchHypothesisCount": retained,
        "fundamentalPromotionCount": promotions,
        "suppressedPitchCount": suppressed,
    }
    if observed != expected:
        raise ValueError(f"historical precision identity mismatch: {observed!r}")

    original_non_primary = original - attacks
    mandatory_strongest_raw_secondaries = promotions
    optional_candidates = original_non_primary - mandatory_strongest_raw_secondaries

    retained_secondaries = retained - attacks
    optional_survivors = retained_secondaries - mandatory_strongest_raw_secondaries
    optional_suppressed = optional_candidates - optional_survivors

    if optional_suppressed != suppressed:
        raise ValueError(
            "optional-candidate accounting does not reconcile with historical "
            f"suppressedPitchCount: {optional_suppressed} != {suppressed}"
        )

    return {
        "schemaVersion": 1,
        "classification": "extreme-optional-secondary-pruning",
        "source": {
            "precisionDiagnosticsBound": True,
            "newInferenceUsed": False,
            "professionalReferenceUsed": False,
            "referenceRuntimeInputUsed": False,
        },
        "accounting": {
            "originalPitchHypothesisCount": original,
            "retainedAttackPrimaryCount": attacks,
            "originalNonPrimaryCount": original_non_primary,
            "mandatoryStrongestRawSecondaryCount": mandatory_strongest_raw_secondaries,
            "optionalCandidateCount": optional_candidates,
            "retainedPitchHypothesisCount": retained,
            "retainedSecondaryCount": retained_secondaries,
            "optionalSurvivorCount": optional_survivors,
            "optionalSuppressedCount": optional_suppressed,
            "optionalSurvivalRate": _ratio(optional_survivors, optional_candidates),
            "optionalSuppressionRate": _ratio(optional_suppressed, optional_candidates),
            "wholeUniverseSuppressionRate": _ratio(suppressed, original),
        },
        "interpretation": {
            "statement": (
                "After removing one primary per retained attack and the 144 "
                "strongest-raw secondaries that are forced survivors on promoted-"
                "fundamental attacks, the legacy precision gate retained only "
                "118 of 6,666 optional pitch candidates."
            ),
            "legacyOptionalGateSurvivalPercent": 100.0 * _ratio(optional_survivors, optional_candidates),
            "legacyOptionalGateSuppressionPercent": 100.0 * _ratio(optional_suppressed, optional_candidates),
            "eventMutationJustified": False,
            "suppressedPerEventRowsAvailable": False,
            "exactRelaxedRuleRecoveryCountClaimed": False,
        },
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json",
    )
    parser.add_argument(
        "--output",
        default="debug/v143-contextual-prune/precision-optional-candidate-accounting.json",
    )
    args = parser.parse_args()
    product = json.loads(Path(args.input).read_text())
    report = build_report(product)
    Path(args.output).write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
