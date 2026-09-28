import numpy as np
import pytest
from synthetic.s13_transform_design_review_v1 import (
    BINS, build_review_evidence, compress_positive_onset_increments
)

def test_isolated_new_pitch_retains_positive_identity():
    e=build_review_evidence()["cases"]["isolated_new_pitch"]
    assert e["after"] == pytest.approx([0.0,0.5,1.0,1.0,1.0])

def test_repeated_same_pitch_keeps_existing_energy_and_half_increment():
    e=build_review_evidence()["cases"]["repeated_same_pitch"]
    assert e["after"] == pytest.approx([0.8,0.9,1.0,0.9,0.8])

def test_attack_over_sustain_preserves_nonrising_sustain_exactly():
    e=build_review_evidence()["cases"]["attack_over_sustain"]
    assert e["sustainAfter"] == pytest.approx(e["sustainBefore"])
    assert e["attackAfter"] == pytest.approx([0.0,0.0,0.5,1.0,1.0])

def test_adjacent_onsets_do_not_recursively_couple():
    e=build_review_evidence()["cases"]["adjacent_onsets"]
    assert e["after"] == pytest.approx([0.0,0.5,0.2,1.0,1.0])

def test_boundaries_are_safe_and_frame_zero_is_unchanged():
    e=build_review_evidence()["cases"]["boundaries"]
    assert e["after"] == pytest.approx([1.0,0.0,0.0,0.5])

def test_unattributed_rising_bins_are_a_known_limitation_not_hidden():
    e=build_review_evidence()["cases"]["simultaneous_unattributed_rise"]
    assert e["afterBin0"][1] == pytest.approx(0.4)
    assert e["afterBin1"][1] == pytest.approx(0.35)

def test_input_immutability():
    x=np.zeros((4,BINS),dtype=np.float32); x[1,0]=1
    y=np.zeros((6,4),dtype=np.int64); y[0,1]=1
    before=x.copy()
    compress_positive_onset_increments(x,y,0.5)
    assert np.array_equal(x,before)

def test_nonrising_bins_bit_preserved():
    x=np.zeros((4,BINS),dtype=np.float32)
    x[0,:]=0.8; x[1,:]=0.7
    y=np.zeros((6,4),dtype=np.int64); y[0,1]=1
    z=compress_positive_onset_increments(x,y,0.25)
    assert np.array_equal(z[1],x[1])

@pytest.mark.parametrize("r",[0.25,0.5,0.75,1.0])
def test_positive_increment_retains_exact_fraction(r):
    x=np.zeros((3,BINS),dtype=np.float32); x[0,0]=0.2; x[1,0]=1.0
    y=np.zeros((6,3),dtype=np.int64); y[0,1]=1
    z=compress_positive_onset_increments(x,y,r)
    assert z[1,0] == pytest.approx(0.2+r*0.8,abs=1e-6)

@pytest.mark.parametrize("r",[0.0,-0.1,1.1,float("nan")])
def test_invalid_retain_fraction_rejected(r):
    x=np.zeros((3,BINS),dtype=np.float32)
    y=np.zeros((6,3),dtype=np.int64)
    with pytest.raises(ValueError):
        compress_positive_onset_increments(x,y,r)

def test_shape_nonfinite_and_range_guards():
    y=np.zeros((6,3),dtype=np.int64)
    with pytest.raises(ValueError):
        compress_positive_onset_increments(np.zeros((3,191),dtype=np.float32),y,0.5)
    x=np.zeros((3,BINS),dtype=np.float32)
    with pytest.raises(ValueError):
        compress_positive_onset_increments(x,np.zeros((5,3)),0.5)
    x[1,0]=np.nan
    with pytest.raises(ValueError):
        compress_positive_onset_increments(x,y,0.5)
    x[1,0]=1.01
    with pytest.raises(ValueError):
        compress_positive_onset_increments(x,y,0.5)
