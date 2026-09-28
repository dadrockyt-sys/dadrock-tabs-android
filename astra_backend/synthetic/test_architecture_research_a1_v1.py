import torch

from synthetic.architecture_research_a1_v1 import (
    A1Model, SEEDS, MAX_MODELS, MAX_STEPS_PER_MODEL, MAX_TOTAL_STEPS,
    initialize_a1, parameter_count,
)
from synthetic.s11_pilot_v1 import RUN_SEEDS


def test_a1_shapes_match_s11_contract():
    m=A1Model(960)
    x=torch.zeros((7,960),dtype=torch.float32)
    state,onset=m(x)
    assert state.shape==(7,126)
    assert onset.shape==(7,6)


def test_state_and_onset_encoder_parameter_sets_are_disjoint():
    m=A1Model(960)
    s={id(p) for p in m.state_encoder.parameters()}
    o={id(p) for p in m.onset_encoder.parameters()}
    assert s
    assert o
    assert s.isdisjoint(o)


def test_state_path_backward_does_not_touch_onset_encoder():
    m=A1Model(960)
    x=torch.randn((4,960),dtype=torch.float32)
    state,_=m(x)
    state.sum().backward()
    assert any(p.grad is not None for p in m.state_encoder.parameters())
    assert all(p.grad is None for p in m.onset_encoder.parameters())


def test_onset_path_backward_does_not_touch_state_encoder():
    m=A1Model(960)
    x=torch.randn((4,960),dtype=torch.float32)
    _,onset=m(x)
    onset.sum().backward()
    assert any(p.grad is not None for p in m.onset_encoder.parameters())
    assert all(p.grad is None for p in m.state_encoder.parameters())


def test_a1_seed_and_optimizer_budget_are_frozen():
    assert tuple(SEEDS)==tuple(RUN_SEEDS)==(20260927,20260928,20260929)
    assert MAX_MODELS==3
    assert MAX_STEPS_PER_MODEL==500
    assert MAX_TOTAL_STEPS==1500


def test_a1_initialization_is_deterministic_and_seed_distinct():
    a=initialize_a1(SEEDS[0],960)
    b=initialize_a1(SEEDS[0],960)
    c=initialize_a1(SEEDS[1],960)
    assert all(torch.equal(x,y) for x,y in zip(a.state_dict().values(),b.state_dict().values()))
    assert any(not torch.equal(x,y) for x,y in zip(a.state_dict().values(),c.state_dict().values()))
    assert parameter_count(a)>0
