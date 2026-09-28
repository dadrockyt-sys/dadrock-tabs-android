import numpy as np
import pytest

from synthetic.s13_preimplementation_review_v1 import (
    BINS, build_review_evidence, validated_soften,
)

def test_isolated_new_pitch_and_context_are_changed():
    e=build_review_evidence()["cases"]["isolated_new_pitch"]
    assert e["before"] == [0.0,1.0,1.0,1.0]
    assert e["after"] == pytest.approx([0.0,0.3,0.51,1.0], abs=1e-6)
    assert e["contextAtOnsetBefore"] != e["contextAtOnsetAfter"]

def test_repeated_same_pitch_is_still_modified():
    e=build_review_evidence()["cases"]["repeated_same_pitch"]
    assert e["after"][1] == pytest.approx(0.86, abs=1e-6)
    assert e["after"][2] == pytest.approx(0.902, abs=1e-6)

def test_attack_over_sustain_changes_unrelated_bin():
    e=build_review_evidence()["cases"]["attack_over_sustain"]
    assert e["sustainBinBefore"][2] == pytest.approx(0.6)
    assert e["sustainBinAfter"][2] == pytest.approx(0.74, abs=1e-6)
    assert e["attackBinAfter"][2] == pytest.approx(0.3, abs=1e-6)

def test_adjacent_onsets_are_order_coupled():
    e=build_review_evidence()["cases"]["adjacent_onsets"]
    assert e["after"] == pytest.approx([0.0,0.5,0.425,0.7125,1.0], abs=1e-6)

def test_frame_zero_ignored_and_final_frame_safe():
    e=build_review_evidence()["cases"]["boundaries"]
    assert e["frameZeroIgnored"] is True
    assert e["after"] == pytest.approx([1.0,0.0,0.0,0.5], abs=1e-6)

def test_input_immutability():
    x=np.zeros((4,BINS),dtype=np.float32); x[1,0]=1
    y=np.zeros((6,4),dtype=np.int64); y[0,1]=1
    before=x.copy()
    validated_soften(x,y,0.5)
    assert np.array_equal(x,before)

@pytest.mark.parametrize("shape",[(4,191),(4,193),(1,4,192)])
def test_feature_shape_rejection(shape):
    x=np.zeros(shape,dtype=np.float32)
    y=np.zeros((6,4),dtype=np.int64)
    with pytest.raises(ValueError):
        validated_soften(x,y,0.5)

def test_mismatched_onset_shape_rejected():
    x=np.zeros((4,BINS),dtype=np.float32)
    for y in (np.zeros((5,4)),np.zeros((6,3)),np.zeros((6,4,1))):
        with pytest.raises(ValueError):
            validated_soften(x,y,0.5)

def test_nonfinite_inputs_rejected():
    x=np.zeros((4,BINS),dtype=np.float32)
    y=np.zeros((6,4),dtype=np.float32)
    x[1,0]=np.nan
    with pytest.raises(ValueError):
        validated_soften(x,y,0.5)
    x[1,0]=0
    y[0,1]=np.inf
    with pytest.raises(ValueError):
        validated_soften(x,y,0.5)
