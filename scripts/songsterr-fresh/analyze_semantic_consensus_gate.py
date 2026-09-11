#!/usr/bin/env python3

"""Distribution-free analysis of a repeated semantic-consensus gate.

This module does not admit model evidence. It formalizes why finite repeated
execution + unanimity cannot, by itself, prove cross-environment semantic
portability when more than one floating-point execution outcome is possible.

The analysis is reference-blind and model-output-agnostic. It uses no reference
tab, CPU/vendor selector, historical output preference, duration signal, or
observed threshold envelope as a correctness criterion.
"""

import argparse
import json
import math

CONTRACT = "songsterr-fresh-semantic-consensus-gate-analysis-v1"


class ConsensusAnalysisError(RuntimeError):
    pass


def require_run_count(value):
    try:
        count = int(value)
    except (TypeError, ValueError) as exc:
        raise ConsensusAnalysisError("RUN_COUNT_INTEGER_REQUIRED") from exc
    if count < 2:
        raise ConsensusAnalysisError("RUN_COUNT_AT_LEAST_TWO_REQUIRED")
    return count


def iid_unanimity_probability(probabilities, run_count):
    """Probability that all N iid draws land on one semantic outcome."""
    n = require_run_count(run_count)
    if not isinstance(probabilities, (list, tuple)) or len(probabilities) < 2:
        raise ConsensusAnalysisError("AT_LEAST_TWO_OUTCOME_PROBABILITIES_REQUIRED")
    values = []
    for raw in probabilities:
        try:
            value = float(raw)
        except (TypeError, ValueError) as exc:
            raise ConsensusAnalysisError("FINITE_PROBABILITY_REQUIRED") from exc
        if not math.isfinite(value) or value <= 0.0 or value >= 1.0:
            raise ConsensusAnalysisError("PROBABILITY_MUST_BE_STRICTLY_BETWEEN_ZERO_AND_ONE")
        values.append(value)
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ConsensusAnalysisError("PROBABILITIES_MUST_SUM_TO_ONE")
    return float(sum(value ** n for value in values))


def two_mode_false_pass_example(run_count, minority_probability):
    """Construct a non-degenerate two-mode process where unanimity can pass."""
    n = require_run_count(run_count)
    epsilon = float(minority_probability)
    if not math.isfinite(epsilon) or epsilon <= 0.0 or epsilon >= 0.5:
        raise ConsensusAnalysisError("MINORITY_PROBABILITY_MUST_BE_IN_OPEN_INTERVAL_ZERO_TO_HALF")
    majority = 1.0 - epsilon
    unanimity = iid_unanimity_probability([majority, epsilon], n)
    disagreement = 1.0 - unanimity
    return {
        "runCount": n,
        "minorityModeProbability": epsilon,
        "majorityModeProbability": majority,
        "iidUnanimityPassProbability": unanimity,
        "iidDisagreementRejectProbability": disagreement,
        "semanticPortabilityIsUniversal": False,
    }


def build_analysis(run_counts=(2, 3, 5, 10), witness_epsilon=1e-9):
    counts = [require_run_count(value) for value in run_counts]
    examples = [two_mode_false_pass_example(count, witness_epsilon) for count in counts]
    return {
        "contract": CONTRACT,
        "version": 1,
        "referenceBlind": True,
        "measurementOnly": True,
        "analysisScope": "finite-unanimity-semantic-consensus-without-execution-distribution-guarantee",
        "result": {
            "finiteUnanimityImpliesUniversalSemanticPortability": False,
            "distributionFreeFalsePassUpperBoundBelowOneExists": False,
            "reason": (
                "For any finite N and any delta > 0, a non-degenerate two-mode iid execution "
                "distribution can place probability 1-epsilon on one semantic mode and epsilon on "
                "another, with epsilon small enough that unanimity probability "
                "(1-epsilon)^N + epsilon^N exceeds 1-delta. Therefore finite unanimity has no "
                "distribution-free false-pass bound below 1. Correlated executions provide no "
                "stronger guarantee because a shared hidden environment can make repeated runs "
                "agree while another supported environment produces a different semantic result."
            ),
            "iidWitnesses": examples,
            "iidFalseRejectForKnownDistribution": (
                "If p_i are justified semantic-mode probabilities, disagreement rejection probability "
                "is 1 - sum(p_i^N). Current policy forbids deriving admission correctness from observed "
                "historical frequencies, so sample frequencies cannot supply those p_i."
            ),
            "correlationRisk": (
                "Repeated hosted executions are not proven independent draws from all supported compute "
                "surfaces. Agreement can therefore reflect shared environment correlation rather than "
                "universal semantic stability."
            ),
        },
        "policyBoundary": {
            "status": "SEMANTIC_CONSENSUS_NOT_JUSTIFIED_AS_POLICY_B_ADMISSION_GATE",
            "admissionRuleImplemented": False,
            "thresholdsAppliedForAdmission": False,
            "historicalFrequencyUsedForAdmission": False,
            "cpuOrVendorUsedForAdmission": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def run_self_test():
    analysis = build_analysis()
    assert analysis["result"]["finiteUnanimityImpliesUniversalSemanticPortability"] is False
    assert analysis["result"]["distributionFreeFalsePassUpperBoundBelowOneExists"] is False
    witnesses = analysis["result"]["iidWitnesses"]
    assert [item["runCount"] for item in witnesses] == [2, 3, 5, 10]
    assert all(item["iidUnanimityPassProbability"] > 0.99999998 for item in witnesses)
    assert analysis["policyBoundary"]["modelValidationComplete"] is False
    assert analysis["policyBoundary"]["admissionRuleImplemented"] is False

    balanced_two = iid_unanimity_probability([0.5, 0.5], 2)
    balanced_three = iid_unanimity_probability([0.5, 0.5], 3)
    assert math.isclose(balanced_two, 0.5, rel_tol=0.0, abs_tol=1e-15)
    assert math.isclose(balanced_three, 0.25, rel_tol=0.0, abs_tol=1e-15)

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "referenceBlind": True,
        "measurementOnly": True,
        "finiteUnanimityIsNotUniversalPortabilityProof": True,
        "modelValidationComplete": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--run-count", type=int, action="append")
    parser.add_argument("--witness-epsilon", type=float, default=1e-9)
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    counts = tuple(args.run_count) if args.run_count else (2, 3, 5, 10)
    print(json.dumps(build_analysis(counts, args.witness_epsilon), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ConsensusAnalysisError as exc:
        print(f"CONSENSUS_ANALYSIS_ERROR:{exc}")
        raise SystemExit(2)
