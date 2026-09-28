import numpy as np

from synthetic.source_domain_joint_coverage_manifest_v2 import AXES, FAMILIES
from synthetic.source_domain_joint_coverage_v3_final_v1 import (
    DESCRIPTORS, _challenge_rows_for_family, _coverage
)


def test_v3_family_manifest_has_12_rows_and_exact_marginal_strata():
    rows=_challenge_rows_for_family([10,11,12,13,14,15],"isolated")
    assert len(rows)==12
    assert sorted((r["sourceRowIndex"],r["replicate"]) for r in rows)==[
        (10,0),(10,1),(11,0),(11,1),(12,0),(12,1),
        (13,0),(13,1),(14,0),(14,1),(15,0),(15,1),
    ]
    for axis in AXES:
        assert sorted(r["strata"][axis] for r in rows)==list(range(12))
    assert sum(r["nonlinearActive"] for r in rows)==6
    hum=[r for r in rows if r["humActive"]]
    assert len(hum)==4
    assert sum(r["humFundamentalHz"]==50 for r in hum)==2
    assert sum(r["humFundamentalHz"]==60 for r in hum)==2


def _records(n,challenge=False):
    out=[]
    for fam in FAMILIES:
        for i in range(n):
            r={"family":fam}
            for j,d in enumerate(DESCRIPTORS):
                if challenge:
                    r[d]=15.0 + 0.1*i + j
                else:
                    r[d]=float(i+j)
            out.append(r)
    return out


def test_v3_coverage_is_35_of_35_when_challenge_medians_inside():
    x=_coverage(_records(30),_records(12,True))
    assert x["total"]==35 and x["required"]==35
    assert x["passed"]==35 and x["admissionPassed"] is True


def test_v3_coverage_fails_single_outside_descriptor():
    tr=_records(30)
    ch=_records(12,True)
    for r in ch:
        if r["family"]=="repeated":
            r["rmsNormalizedFirstDifferenceEnergy"]=999.0
    x=_coverage(tr,ch)
    assert x["passed"]==34
    assert x["admissionPassed"] is False


def test_descriptor_contract_replaces_raw_first_difference_only():
    assert DESCRIPTORS==(
        "waveformRms",
        "spectralCentroid",
        "rmsNormalizedFirstDifferenceEnergy",
        "preparedCqtPositiveFlux",
        "preparedCqtRowDisplacement",
    )
