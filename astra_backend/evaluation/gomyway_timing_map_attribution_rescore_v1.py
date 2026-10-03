"""Dual-map timing attribution benchmark for Go My Way.

Runs frozen separation + Basic Pitch once, then scores the identical predictions
against the historical V2 timing map and the revalidated V3 timing map.
"""
from __future__ import annotations
import argparse, json, tempfile, time
from pathlib import Path

from evaluate_gomyway_full_song_professional_v2 import (
    EXPECTED_BP_SHA256, BASIC_PITCH_VERSION, ONSET_THRESHOLD, FRAME_THRESHOLD,
    MIN_NOTE_LENGTH_MS, sha256_file, load_audio, validate_reference,
    scorer_targets, score_role, compact_score, excluded_measures
)
from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from evaluate_s0_transcription_failure_attribution_v1 import run_probe
from pretrained_note_front_end_v1 import basic_pitch_model_identity

def score_all(pred, timing, refs):
    targets={}; excluded={}
    for role in ("rhythm","lead","bass"):
        targets[role],excluded[role]=scorer_targets(role,refs[role],timing)
    combined=sorted(targets["rhythm"]+targets["lead"],key=lambda x:(x["start"],x["midi"],x["id"]))
    comb_ex=excluded["rhythm"]|excluded["lead"]
    whole,guitar,bass=pred["whole"],pred["guitar"],pred["bass"]
    scores={
      "separator":{
        "rhythmFromGuitarStem":score_role(guitar,targets["rhythm"],timing,excluded["rhythm"]),
        "leadFromGuitarStem":score_role(guitar,targets["lead"],timing,excluded["lead"]),
        "combinedGuitarFromGuitarStem":score_role(guitar,combined,timing,comb_ex),
        "bassFromBassStem":score_role(bass,targets["bass"],timing,excluded["bass"]),
      },
      "wholeMixControls":{
        "rhythm":score_role(whole,targets["rhythm"],timing,excluded["rhythm"]),
        "lead":score_role(whole,targets["lead"],timing,excluded["lead"]),
        "combinedGuitar":score_role(whole,combined,timing,comb_ex),
        "bass":score_role(whole,targets["bass"],timing,excluded["bass"]),
      }
    }
    return {
      "targetCounts":{r:len(targets[r]) for r in ("rhythm","lead","bass")},
      "combinedGuitarTargetCount":len(combined),
      "excludedMeasures":{r:sorted(excluded[r]) for r in ("rhythm","lead","bass")},
      "scores":{g:{n:compact_score(s) for n,s in vals.items()} for g,vals in scores.items()}
    }

def delta(old,new):
    out={}
    for group in ("separator","wholeMixControls"):
        out[group]={}
        for name in old["scores"][group]:
            a=old["scores"][group][name]; b=new["scores"][group][name]
            out[group][name]={
              "tpDelta":b["tp"]-a["tp"],
              "precisionDelta":(b["precision"] or 0)-(a["precision"] or 0),
              "recallDelta":(b["recall"] or 0)-(a["recall"] or 0),
              "f1Delta":(b["f1"] or 0)-(a["f1"] or 0),
              "maeDeltaSeconds":None if a["meanAbsoluteOnsetErrorSeconds"] is None or b["meanAbsoluteOnsetErrorSeconds"] is None else b["meanAbsoluteOnsetErrorSeconds"]-a["meanAbsoluteOnsetErrorSeconds"]
            }
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio-source",required=True); ap.add_argument("--audio-wav",required=True)
    ap.add_argument("--old-timing-map",required=True); ap.add_argument("--new-timing-map",required=True)
    ap.add_argument("--rhythm-reference",required=True); ap.add_argument("--lead-reference",required=True); ap.add_argument("--bass-reference",required=True)
    ap.add_argument("--model",required=True); ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    bp=basic_pitch_model_identity()
    if bp["packageVersion"]!=BASIC_PITCH_VERSION or bp["modelSha256"]!=EXPECTED_BP_SHA256:
        raise RuntimeError("Basic Pitch frozen identity mismatch")

    refs={
      "rhythm":validate_reference("rhythm",Path(a.rhythm_reference)),
      "lead":validate_reference("lead",Path(a.lead_reference)),
      "bass":validate_reference("bass",Path(a.bass_reference))
    }
    old=json.loads(Path(a.old_timing_map).read_text())
    new=json.loads(Path(a.new_timing_map).read_text())
    for name,t in (("old",old),("new",new)):
        if t.get("audioSource")!="public/gomywayfullaitest.m4a" or int(t.get("measureCount",-1))!=113:
            raise RuntimeError(f"{name} timing map binding mismatch")

    audio,fs=load_audio(Path(a.audio_wav))
    started=time.perf_counter()
    adapter=BsRoformer6StemOnnxAdapter(Path(a.model))
    stems=adapter.separate_array(audio,fs)
    with tempfile.TemporaryDirectory(prefix="astra_gomyway_dualmap_") as td:
        td=Path(td)
        whole=run_probe(audio,fs,td/"whole.wav","whole")
        guitar=run_probe(stems["guitar"],fs,td/"guitar.wav","guitar")
        bass=run_probe(stems["bass"],fs,td/"bass.wav","bass")
    pred={"whole":whole,"guitar":guitar,"bass":bass}

    old_score=score_all(pred,old,refs)
    new_score=score_all(pred,new,refs)
    result={
      "schemaVersion":1,
      "kind":"gomyway-timing-map-attribution-rescore-v1",
      "benchmarkClass":"existing-reference-development-not-holdout",
      "identicalPredictionsUsedForBothTimingMaps":True,
      "referenceBlindInference":True,
      "thresholdSearch":False,
      "separatorOutputMutation":False,
      "audio":{"sourcePath":a.audio_source,"sourceSha256":sha256_file(Path(a.audio_source)),"durationSeconds":len(audio)/float(fs)},
      "separator":{"name":"BS-Roformer-SW 6-stem FP16 ONNX","modelSha256":FP16_SHA256},
      "transcriber":{"name":"Basic Pitch","packageVersion":BASIC_PITCH_VERSION,"modelSha256":bp["modelSha256"],
                     "onsetThreshold":ONSET_THRESHOLD,"frameThreshold":FRAME_THRESHOLD,"minimumNoteLengthMs":MIN_NOTE_LENGTH_MS},
      "predictionCounts":{"whole":len(whole),"guitar":len(guitar),"bass":len(bass)},
      "timingMaps":{
        "historicalV2":{"path":a.old_timing_map,"sha256":sha256_file(Path(a.old_timing_map))},
        "revalidatedV3":{"path":a.new_timing_map,"sha256":sha256_file(Path(a.new_timing_map))}
      },
      "historicalV2":old_score,
      "revalidatedV3":new_score,
      "deltaRevalidatedMinusHistorical":delta(old_score,new_score),
      "runtimeSeconds":time.perf_counter()-started,
      "interpretationBoundary":"The same frozen-model predictions are scored against both timing maps. Any score delta is attributable to timing-map coordinates/filtering, not changed audio inference."
    }
    Path(a.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({
      "predictionCounts":result["predictionCounts"],
      "old":old_score["scores"]["separator"],
      "new":new_score["scores"]["separator"],
      "delta":result["deltaRevalidatedMinusHistorical"]["separator"]
    },indent=2))

if __name__=="__main__":main()
