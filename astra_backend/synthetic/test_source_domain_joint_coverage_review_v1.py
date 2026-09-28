import numpy as np
from synthetic.source_domain_joint_coverage_review_v1 import empirical_percentile, conjunction_flags, summarize

def test_empirical_percentile_exact():
    assert empirical_percentile([1,2,3,4],2)==0.5
    assert empirical_percentile([1,2,3,4],0)==0.0
    assert empirical_percentile([1,2,3,4],4)==1.0

def test_summarize_exact():
    s=summarize([1,2,4])
    assert s=={"count":3,"min":1.0,"median":2.0,"max":4.0}

def test_full_challenge_side_conjunction_boundaries():
    r={
      "attackBaseRiseSeconds":.045,"transientNoiseGain":.03,"dampingMultiplier":1.45,
      "brightness":.60,"pickPosition":.42,"lowpassCutoffHz":3500,
      "spectralTiltDb":-4.0,"broadbandNoiseRmsRelative":.001,
      "nonlinearActive":True,"nonlinearWet":.20
    }
    assert all(conjunction_flags(r))

def test_one_boundary_violation_breaks_final_conjunction():
    r={
      "attackBaseRiseSeconds":.0449,"transientNoiseGain":.03,"dampingMultiplier":1.45,
      "brightness":.60,"pickPosition":.42,"lowpassCutoffHz":3500,
      "spectralTiltDb":-4.0,"broadbandNoiseRmsRelative":.001,
      "nonlinearActive":True,"nonlinearWet":.20
    }
    f=conjunction_flags(r)
    assert f[0] is False and not all(f)
