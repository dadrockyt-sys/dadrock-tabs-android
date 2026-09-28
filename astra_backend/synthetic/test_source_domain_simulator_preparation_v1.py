import pytest

from synthetic.source_domain_simulator_preparation_v1 import _template_and_variant

def test_standard_template_occurrence_maps_to_variant():
    t,v=_template_and_variant("isolated","isolated:03",2)
    assert t["templateId"]=="isolated:03"
    assert t["baseIndex"]==3
    assert v==2

def test_s9_chord_slot_reconstructs_unique_frozen_template_and_control_variant():
    t,v=_template_and_variant("chords","s9-chords:0",0,s9_slot=17)
    assert t["templateId"]=="s9-chords:17"
    assert t["split"]=="train"
    assert v==2
    assert len(t["segments"])==6

def test_invalid_standard_occurrence_rejected():
    with pytest.raises(RuntimeError):
        _template_and_variant("scales","scales:00",3)

def test_unexpected_template_id_rejected():
    with pytest.raises(RuntimeError):
        _template_and_variant("isolated","bad-template-id",0)

def test_invalid_s9_slot_rejected():
    with pytest.raises(RuntimeError):
        _template_and_variant("chords","s9-chords:0",0,s9_slot=30)
