import numpy as np
from synthetic.source_domain_joint_coverage_manifest_v2 import _map, _rows_for_family, _validate_group, AXES

def test_inverse_cdf_bounds_and_midpoints():
    for axis,(dist,lo,hi) in AXES.items():
        a=_map(axis,.01); b=_map(axis,.5); c=_map(axis,.99)
        assert lo < a < b < c < hi

def test_training_family_exact_strata_and_categories():
    rows=_rows_for_family(np.arange(30),"train","isolated")
    _validate_group(rows,30,15,11)
    for axis in AXES:
        assert sorted(r["strata"][axis] for r in rows)==list(range(30))
    assert sum(r["nonlinearActive"] for r in rows)==15
    assert sum(r["humActive"] for r in rows)==11

def test_challenge_family_exact_strata_and_categories():
    rows=_rows_for_family(np.arange(6),"challenge","scales")
    _validate_group(rows,6,3,2)
    for axis in AXES:
        assert sorted(r["strata"][axis] for r in rows)==list(range(6))
    assert sum(r["nonlinearActive"] for r in rows)==3
    assert sum(r["humActive"] for r in rows)==2

def test_named_permutations_are_deterministic_and_family_specific():
    a=_rows_for_family(np.arange(30),"train","isolated")
    b=_rows_for_family(np.arange(30),"train","isolated")
    c=_rows_for_family(np.arange(30),"train","legato")
    assert a==b
    assert [r["attackBaseRiseSeconds"] for r in a] != [r["attackBaseRiseSeconds"] for r in c]
