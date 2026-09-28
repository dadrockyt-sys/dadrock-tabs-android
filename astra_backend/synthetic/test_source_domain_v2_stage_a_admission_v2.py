import json

from synthetic.source_domain_v2_stage_a_admission_v1 import (
    EXPECTED_MANIFEST_CONTENT_SHA256,
    TRAIN_POSITIONS,
    CHALLENGE_POSITIONS,
    _manifest_payload_sha,
    _override_from_manifest,
    _selected_rows,
)
from synthetic.source_domain_joint_coverage_manifest_v2 import AXES, FAMILIES


def _row(family,kind,row_index,pos,n,*,hum_active=None,hum_hz=None):
    active=bool(pos%3==0) if hum_active is None else bool(hum_active)
    if hum_hz is None and active:
        hum_hz=50
    r={
        "family":family,
        "kind":kind,
        "rowIndex":row_index,
        "nonlinearActive":bool(pos%2),
        "humActive":active,
        "humFundamentalHz":int(hum_hz) if active else None,
        "strata":{a:pos for a in AXES},
    }
    for j,a in enumerate(AXES):
        r[a]=float((j+1)*0.01+pos*1e-5)
    return r


def test_frozen_stage_a_positions():
    assert TRAIN_POSITIONS==(0,29)
    assert CHALLENGE_POSITIONS==(0,5)


def test_selected_rows_are_exactly_four_per_family():
    m={"trainRows":[],"primaryChallengeRows":[]}
    base=0
    for fam in FAMILIES:
        m["trainRows"] += [_row(fam,"train",base+i,i,30) for i in range(30)]
        m["primaryChallengeRows"] += [_row(fam,"challenge",base+100+i,i,6) for i in range(6)]
        base += 200
    s=_selected_rows(m)
    assert len(s)==28
    for fam in FAMILIES:
        f=[x for x in s if x[0]==fam]
        assert [(x[1],x[2]) for x in f]==[
            ("train",0),("train",29),("challenge",0),("challenge",5)
        ]


def test_active_hum_override_includes_manifest_frequency_only():
    r=_row("isolated","train",0,0,30,hum_active=True,hum_hz=50)
    o=_override_from_manifest(r)
    assert set(o)==set(AXES)|{"nonlinearActive","humActive","humFundamentalHz"}
    assert o["humActive"] is True
    assert o["humFundamentalHz"]==50
    assert "humCombinedRmsRelative" not in o

    r60=_row("isolated","train",1,1,30,hum_active=True,hum_hz=60)
    o60=_override_from_manifest(r60)
    assert o60["humFundamentalHz"]==60
    assert "humCombinedRmsRelative" not in o60


def test_inactive_hum_override_excludes_frequency_and_amplitude_override():
    r=_row("isolated","train",2,2,30,hum_active=False)
    o=_override_from_manifest(r)
    assert set(o)==set(AXES)|{"nonlinearActive","humActive"}
    assert o["humActive"] is False
    assert "humFundamentalHz" not in o
    assert "humCombinedRmsRelative" not in o


def test_manifest_payload_hash_excludes_embedded_hash_field():
    m={"schema":"x","a":1}
    raw=json.dumps(m,sort_keys=True,separators=(",",":")).encode()
    import hashlib
    expected=hashlib.sha256(raw).hexdigest()
    m["manifestContentSha256"]=expected
    assert _manifest_payload_sha(m)==expected


def test_expected_frozen_manifest_hash_is_pinned():
    assert EXPECTED_MANIFEST_CONTENT_SHA256=="2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"
