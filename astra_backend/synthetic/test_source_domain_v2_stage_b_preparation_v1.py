from synthetic.source_domain_v2_stage_b_preparation_v1 import _coverage, DESCRIPTORS
from synthetic.source_domain_joint_coverage_manifest_v2 import FAMILIES


def _records(challenge=False,offset=0.0):
    out=[]
    n=6 if challenge else 30
    for fam in FAMILIES:
        for i in range(n):
            r={"family":fam}
            # broad training support 0..29; challenge centered inside support.
            for j,d in enumerate(DESCRIPTORS):
                r[d]=(10.0+i if not challenge else 20.0+i*0.1)+j+offset
            out.append(r)
    return out


def test_descriptor_set_is_frozen_five():
    assert DESCRIPTORS==(
        "waveformRms","spectralCentroid","firstDifferenceEnergy",
        "preparedCqtPositiveFlux","preparedCqtRowDisplacement"
    )


def test_coverage_requires_exactly_35_checks_and_passes_inside_support():
    x=_coverage(_records(False),_records(True))
    assert x["total"]==35
    assert x["required"]==35
    assert x["passed"]==35
    assert x["admissionPassed"] is True


def test_coverage_fails_when_one_family_descriptor_median_is_outside():
    train=_records(False)
    challenge=_records(True)
    for r in challenge:
        if r["family"]=="isolated":
            r["waveformRms"]=1000.0
    x=_coverage(train,challenge)
    assert x["total"]==35
    assert x["passed"]==34
    assert x["admissionPassed"] is False


def test_all_seven_families_have_five_checks():
    x=_coverage(_records(False),_records(True))
    assert set(x["byFamily"])==set(FAMILIES)
    assert all(len(v)==5 for v in x["byFamily"].values())
