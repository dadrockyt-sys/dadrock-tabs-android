from synthetic.s11_pilot_v1 import RUN_SEEDS
from synthetic.source_domain_simulator_training_v1 import evaluate_gate as v1_evaluate_gate
from synthetic.source_domain_v3_synthetic_training_v1 import (
    SEEDS, MAX_MODELS, MAX_STEPS_PER_MODEL, MAX_TOTAL_STEPS,
    MAX_FIT_EVAL_SECONDS, EXPECTED, evaluate_gate,
)


def test_v3_model_budget_and_seeds_are_frozen_s11_values():
    assert tuple(SEEDS)==tuple(RUN_SEEDS)==(20260927,20260928,20260929)
    assert MAX_MODELS==6
    assert MAX_STEPS_PER_MODEL==500
    assert MAX_TOTAL_STEPS==3000
    assert MAX_FIT_EVAL_SECONDS==5400.0


def test_v3_uses_exact_v1_scientific_gate_function():
    assert evaluate_gate is v1_evaluate_gate


def test_v3_dataset_file_hashes_are_frozen():
    assert EXPECTED=={
      "control":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
      "intervention":"a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b",
      "challenge":"368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce",
    }
