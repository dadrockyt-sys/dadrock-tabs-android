from synthetic.source_domain_v2_source_isolating_pitch_v1 import (
    MAX_RENDERS, MAX_AUDIO_SECONDS, _render_isolated
)
from synthetic.source_domain_v2_stage_a_admission_v1 import _override_from_manifest
from synthetic.source_domain_joint_coverage_manifest_v2 import AXES
from synthetic.s0_pilot_v1 import build_template


def _manifest_row(*,hum_active=False,hum_hz=None):
    r={a:0.0 for a in AXES}
    r.update({
        "attackBaseRiseSeconds":0.01,
        "transientNoiseGain":0.05,
        "transientDecaySeconds":0.01,
        "dampingMultiplier":1.0,
        "brightness":0.7,
        "pickPosition":0.2,
        "lowpassCutoffHz":6000.0,
        "spectralTiltDb":0.0,
        "highpassCornerHz":40.0,
        "nonlinearDrive":1.2,
        "nonlinearWet":0.1,
        "broadbandNoiseRmsRelative":1e-4,
        "nonlinearActive":True,
        "humActive":hum_active,
        "humFundamentalHz":hum_hz if hum_active else None,
    })
    return r


def test_probe_ceilings_match_frozen_protocol():
    assert MAX_RENDERS==172
    assert MAX_AUDIO_SECONDS==344.0


def test_isolated_probe_is_deterministic_and_bounded():
    t=build_template("isolated",0)
    o=_override_from_manifest(_manifest_row(hum_active=False))
    a,ma=_render_isolated(t,0,0,o)
    b,mb=_render_isolated(t,0,0,o)
    assert (a==b).all()
    assert ma["eventIndex"]==0
    assert ma["pitch"]==mb["pitch"]
    assert abs(a).max()<.999


def test_chord_probe_preserves_original_event_index():
    t=build_template("chords",12)
    o=_override_from_manifest(_manifest_row(hum_active=True,hum_hz=60))
    a,m=_render_isolated(t,0,4,o)
    assert m["eventIndex"]==4
    assert m["pitch"]==64
    assert abs(a).max()<.999


def test_inactive_hum_remains_inactive_in_probe_params():
    t=build_template("isolated",0)
    o=_override_from_manifest(_manifest_row(hum_active=False))
    _,m=_render_isolated(t,0,0,o)
    assert m["params"]["humActive"] is False


def test_active_hum_uses_manifest_frequency():
    t=build_template("isolated",0)
    o=_override_from_manifest(_manifest_row(hum_active=True,hum_hz=50))
    _,m=_render_isolated(t,0,0,o)
    assert m["params"]["humActive"] is True
    assert m["params"]["humFundamentalHz"]==50
