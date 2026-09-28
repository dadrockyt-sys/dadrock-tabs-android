import json
from pathlib import Path
from synthetic.source_domain_v2_corrected_stage_a_adjudication_v1 import adjudicate, RETAIN

def _stage():
    return {
      "schema":"astra-source-domain-v2-stage-a-result-v1",
      "frozenInputs":{
        "controlSha256":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
        "manifestContentSha256":"2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"},
      "scientificGate":{"criteria":{**{k:True for k in RETAIN},"fundamentalWithin15Cents":False}}
    }

def _isolated():
    return {
      "schema":"astra-source-domain-v2-source-isolating-pitch-result-v1",
      "frozenInputs":{
        "controlSha256":"16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894",
        "manifestContentSha256":"2dc6e09c3c617ac55e84e386e6fc6ff26d0e68ed81016169cad5ce72c7d95469"},
      "summary":{
        "admissionPassed":True,
        "criteria":{"allIsolatedMeasurableWithin15Cents":True,"allOriginalMeasurableEventsRetained":True},
        "originalMeasurableEvents":86,"isolatedMeasurableEvents":86,
        "missingOriginalMeasurableEvents":0,"outside15Cents":0,
        "maxAbsoluteIsolatedCents":8.1
      }
    }

def test_corrected_adjudication_passes_without_rewriting_original(tmp_path):
    a=tmp_path/"a.json"; i=tmp_path/"i.json"; o=tmp_path/"o.json"
    a.write_text(json.dumps(_stage())); i.write_text(json.dumps(_isolated()))
    r=adjudicate(a,i,o)
    assert r["correctedStageAPassed"] is True
    assert r["originalStageAFailurePreserved"] is True
    assert r["execution"]["waveformRenders"]==0

def test_retained_original_failure_blocks_pass(tmp_path):
    s=_stage(); s["scientificGate"]["criteria"]["peakUnder0_999"]=False
    a=tmp_path/"a.json"; i=tmp_path/"i.json"; o=tmp_path/"o.json"
    a.write_text(json.dumps(s)); i.write_text(json.dumps(_isolated()))
    try:
        adjudicate(a,i,o)
    except SystemExit:
        pass
    else:
        raise AssertionError("expected fail")
    assert json.loads(o.read_text())["correctedStageAPassed"] is False

def test_isolated_failure_blocks_pass(tmp_path):
    x=_isolated(); x["summary"]["outside15Cents"]=1
    a=tmp_path/"a.json"; i=tmp_path/"i.json"; o=tmp_path/"o.json"
    a.write_text(json.dumps(_stage())); i.write_text(json.dumps(x))
    try:
        adjudicate(a,i,o)
    except SystemExit:
        pass
    else:
        raise AssertionError("expected fail")
