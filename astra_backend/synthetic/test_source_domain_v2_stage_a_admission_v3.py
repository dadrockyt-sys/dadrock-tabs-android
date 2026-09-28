from synthetic.source_domain_v2_stage_a_admission_v2 import (
    _simultaneous_attacked_indices,
    SIMULTANEOUS_EPS_SECONDS,
)
from synthetic.source_domain_v2_stage_a_admission_v1 import (
    TRAIN_POSITIONS, CHALLENGE_POSITIONS, EXPECTED_MANIFEST_CONTENT_SHA256
)


def _event(start,attack=True):
    return {
        "string":0,"fret":0,"start":float(start),"end":float(start)+.2,
        "attack":bool(attack),"palm":False,"soft":False,
    }


def test_stage_a_selection_and_manifest_identity_unchanged():
    assert TRAIN_POSITIONS==(0,29)
    assert CHALLENGE_POSITIONS==(0,5)
    assert EXPECTED_MANIFEST_CONTENT_SHA256=="2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"


def test_simultaneous_group_detects_same_onset_attacks():
    t={"segments":[_event(.32),_event(.32),_event(.32),_event(1.08)]}
    assert _simultaneous_attacked_indices(t)=={0,1,2}


def test_nonattack_same_time_does_not_make_attack_simultaneous():
    t={"segments":[_event(.32),_event(.32,attack=False),_event(.8)]}
    assert _simultaneous_attacked_indices(t)==set()


def test_microsecond_boundary_is_frozen():
    t={"segments":[_event(.32),_event(.32+SIMULTANEOUS_EPS_SECONDS)]}
    assert _simultaneous_attacked_indices(t)=={0,1}

    t2={"segments":[_event(.32),_event(.32+SIMULTANEOUS_EPS_SECONDS*2)]}
    assert _simultaneous_attacked_indices(t2)==set()
