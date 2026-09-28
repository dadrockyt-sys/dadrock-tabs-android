import numpy as np
import pytest

from synthetic.source_domain_simulator_diversity_v1 import (
    CHALLENGE_PROFILE,
    FINAL_PEAK,
    FIXTURE_FAMILIES,
    _fixture_template,
    build_review_evidence,
    render_source_domain,
    source_parameters,
)
from synthetic.s0_pilot_v1 import targets_for_template
from tabcnn_runtime.preprocessing import extract_cqt_features, rms_normalize

def test_parameter_draw_is_deterministic_and_within_frozen_ranges():
    a=source_parameters("isolated:00",0)
    b=source_parameters("isolated:00",0)
    assert a==b
    assert .0015 <= a["attackBaseRiseSeconds"] <= .050
    assert 0 <= a["transientNoiseGain"] <= .20
    assert .003 <= a["transientDecaySeconds"] <= .020
    assert .60 <= a["dampingMultiplier"] <= 1.80
    assert .55 <= a["brightness"] <= .92
    assert .08 <= a["pickPosition"] <= .48
    assert 2800 <= a["lowpassCutoffHz"] <= 12000
    assert -6 <= a["spectralTiltDb"] <= 6
    assert 20 <= a["highpassCornerHz"] <= 80
    assert 1.0 <= a["nonlinearDrive"] <= 2.5
    assert 0 <= a["nonlinearWet"] <= .30
    assert 1e-5 <= a["broadbandNoiseRmsRelative"] <= 3e-3
    assert a["humFundamentalHz"] in (50,60)
    assert 0 <= a["humCombinedRmsRelative"] <= 1e-3

def test_challenge_profile_is_exactly_frozen():
    assert CHALLENGE_PROFILE["attackBaseRiseSeconds"]==.045
    assert CHALLENGE_PROFILE["transientNoiseGain"]==.03
    assert CHALLENGE_PROFILE["lowpassCutoffHz"]==3500
    assert CHALLENGE_PROFILE["spectralTiltDb"]==-4
    assert CHALLENGE_PROFILE["nonlinearWet"]==.20
    assert CHALLENGE_PROFILE["humActive"] is False

@pytest.mark.parametrize("name",FIXTURE_FAMILIES)
def test_fixture_rerender_is_bit_deterministic_and_finite(name):
    t=_fixture_template(name)
    a=render_source_domain(t,0)
    b=render_source_domain(t,0)
    assert np.array_equal(a,b)
    assert np.isfinite(a).all()
    assert float(np.max(np.abs(a))) < .999
    assert float(np.max(np.abs(a))) <= FINAL_PEAK+1e-4

def test_legato_nonattack_event_never_gets_transient_injection():
    t=_fixture_template("legato")
    _,meta=render_source_domain(t,0,return_metadata=True)
    nonattack=[e for e in meta["events"] if not e["attack"]]
    assert nonattack
    assert all(e["transientApplied"] is False for e in nonattack)

def test_negative_only_fixture_has_no_attacked_note_event():
    t=_fixture_template("negative-only")
    _,meta=render_source_domain(t,0,return_metadata=True)
    assert not any(e["attack"] for e in meta["events"])

def test_labels_and_references_do_not_depend_on_source_domain_render():
    t=_fixture_template("chords")
    a=render_source_domain(t,0)
    b=render_source_domain(t,0,profile="challenge")
    fa=extract_cqt_features(rms_normalize(a)).squeeze(0).T
    fb=extract_cqt_features(rms_normalize(b)).squeeze(0).T
    assert fa.shape==fb.shape
    sa,oa,ra=targets_for_template(t,len(fa))
    sb,ob,rb=targets_for_template(t,len(fb))
    assert np.array_equal(sa,sb)
    assert np.array_equal(oa,ob)
    assert ra==rb

def test_source_domain_changes_survive_frozen_frontend():
    t=_fixture_template("isolated")
    base=render_source_domain(t,0)
    challenge=render_source_domain(t,0,profile="challenge")
    fb=extract_cqt_features(rms_normalize(base))
    fc=extract_cqt_features(rms_normalize(challenge))
    assert fb.shape==fc.shape
    assert not np.array_equal(fb,fc)

def test_invalid_profile_rejected():
    with pytest.raises(ValueError):
        render_source_domain(_fixture_template("isolated"),0,profile="not-a-profile")

def test_full_model_free_admission_review_passes_and_stays_under_render_ceiling():
    e=build_review_evidence()
    assert e["modelRun"] is False
    assert e["optimizerSteps"]==0
    assert e["p1Accessed"] is False and e["p2Accessed"] is False and e["p3Opened"] is False
    assert e["fixtureRenderCount"] <= 60
    assert e["admissionPassed"] is True
    assert all(e["criteria"].values())
    assert e["attackBoundaryMeasuredRiseSeconds"]["ratio"] >= 4.0
    assert e["maxAbsoluteFundamentalErrorCents"] <= 15.0
