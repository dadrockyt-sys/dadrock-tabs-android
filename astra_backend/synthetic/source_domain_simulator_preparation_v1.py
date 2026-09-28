#!/usr/bin/env python3
"""Model-free preparation for source-domain simulator diversity V1."""
from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import numpy as np

from synthetic.s0_pilot_v1 import (
    AUDIO_SECONDS, CLIP_SECONDS, build_template, generate_dataset, targets_for_template,
)
from synthetic.s9_pilot_v1 import build_intervention_dataset, intervention_chord_template
from synthetic.s2_pilot_v1 import dataset_array_hashes
from synthetic.s13_pilot_v1 import file_sha256
from synthetic.source_domain_simulator_diversity_v1 import render_source_domain
from tabcnn_runtime.preprocessing import CQT_BINS, extract_cqt_features, rms_normalize

SCHEMA="astra-source-domain-simulator-preparation-v1"
EXPECTED_EXAMPLES=294
MAX_RENDERED_CLIPS=900
MAX_AUDIO_SECONDS=1800.0
MAX_PERSISTED_BYTES=500*1024*1024
MAX_WALL_SECONDS=45*60.0

def _template_and_variant(family,template_id,occurrence,s9_slot=None):
    fam=str(family); tid=str(template_id)
    if s9_slot is not None:
        slot=int(s9_slot)
        if fam!="chords" or not 0<=slot<30:
            raise RuntimeError("invalid S9 chord slot")
        return intervention_chord_template(slot),slot%3
    if ":" not in tid:
        raise RuntimeError("unexpected template id: "+tid)
    base=int(tid.rsplit(":",1)[1])
    if not 0 <= int(occurrence) <= 2:
        raise RuntimeError("variant occurrence out of range")
    return build_template(fam,base),int(occurrence)

def _render_features(template,variant,profile):
    audio=render_source_domain(template,variant,profile=profile)
    feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
    if feat.ndim!=2 or feat.shape[1]!=CQT_BINS or not np.isfinite(feat).all():
        raise RuntimeError("invalid source-domain prepared features")
    return feat

def build_source_domain_datasets(control_path,intervention_out,challenge_out,receipt_out):
    started=time.monotonic()
    c=np.load(control_path,allow_pickle=False)
    if len(c["features"])!=EXPECTED_EXAMPLES:
        raise RuntimeError("unexpected frozen S9 control size")
    ia={k:np.array(c[k],copy=True) for k in c.files}
    qa={k:np.array(c[k],copy=True) for k in c.files}

    occurrences={}
    chord_train_rows=np.flatnonzero((c["family"]=="chords")&(c["split"]=="train"))
    if len(chord_train_rows)!=30:
        raise RuntimeError("expected 30 frozen S9 training chord rows")
    chord_slot_for_row={int(row):slot for slot,row in enumerate(chord_train_rows.tolist())}
    historical_truncated_chord_refs=0
    rendered=0
    changed_intervention=[]
    changed_challenge=[]
    row_records=[]

    for i in range(len(c["features"])):
        tid=str(c["template_id"][i]); fam=str(c["family"][i]); split=str(c["split"][i])
        occ=occurrences.get(tid,0)
        occurrences[tid]=occ+1
        s9_slot=chord_slot_for_row.get(int(i))
        template,variant=_template_and_variant(fam,tid,occ,s9_slot=s9_slot)

        # Verify reconstructed source template yields the exact frozen state/onset
        # before it is permitted to provide a replacement waveform.
        state,onset,refs=targets_for_template(template,c["features"][i].shape[0])
        refs_json=json.dumps(refs,separators=(",",":"),sort_keys=True)
        if not np.array_equal(state,c["state"][i]):
            raise RuntimeError(f"reconstructed state mismatch row {i}")
        if not np.array_equal(onset,c["onset"][i]):
            raise RuntimeError(f"reconstructed onset mismatch row {i}")
        frozen_refs=str(c["refs_json"][i])
        if s9_slot is None:
            if refs_json!=frozen_refs:
                raise RuntimeError(f"reconstructed references mismatch row {i}")
        else:
            # Historical S9 storage copied the S0 fixed-width Unicode dtypes before
            # assigning longer S9 chord IDs. Training-chord template IDs and refs were
            # therefore truncated. Preserve those bytes as historical control identity;
            # require the stored value to be an exact prefix of the reconstructed refs.
            if not (len(frozen_refs)<len(refs_json) and refs_json.startswith(frozen_refs)):
                raise RuntimeError(f"S9 historical reference truncation mismatch row {i}")
            if not template["templateId"].startswith(tid):
                raise RuntimeError(f"S9 historical template-id truncation mismatch row {i}")
            historical_truncated_chord_refs+=1

        if split=="train":
            feat=_render_features(template,variant,"intervention"); rendered+=1
            if feat.shape!=c["features"][i].shape:
                raise RuntimeError("intervention feature shape mismatch")
            ia["features"][i]=feat
            changed_intervention.append(i)
        if split=="test":
            feat=_render_features(template,variant,"challenge"); rendered+=1
            if feat.shape!=c["features"][i].shape:
                raise RuntimeError("challenge feature shape mismatch")
            qa["features"][i]=feat
            changed_challenge.append(i)

        if split in ("train","test"):
            row_records.append({"rowIndex":int(i),"family":fam,"split":split,
                                "templateId":tid,"variant":int(variant)})

    train_rows=np.flatnonzero(c["split"]=="train")
    test_rows=np.flatnonzero(c["split"]=="test")
    heldout=np.flatnonzero(c["split"]!="train")
    non_test=np.flatnonzero(c["split"]!="test")

    if changed_intervention!=train_rows.tolist():
        raise RuntimeError("intervention changed-row set is not exactly training rows")
    if changed_challenge!=test_rows.tolist():
        raise RuntimeError("challenge changed-row set is not exactly test rows")
    if not np.array_equal(ia["features"][heldout],c["features"][heldout]):
        raise RuntimeError("intervention validation/test features changed")
    if not np.array_equal(qa["features"][non_test],c["features"][non_test]):
        raise RuntimeError("challenge train/validation features changed")

    for k in c.files:
        if k=="features": continue
        if not np.array_equal(ia[k],c[k]) or not np.array_equal(qa[k],c[k]):
            raise RuntimeError("non-feature identity mismatch: "+k)

    if rendered>MAX_RENDERED_CLIPS:
        raise RuntimeError("render ceiling exceeded")
    rendered_audio_seconds=rendered*CLIP_SECONDS
    if rendered_audio_seconds>MAX_AUDIO_SECONDS:
        raise RuntimeError("audio-seconds ceiling exceeded")

    np.savez_compressed(intervention_out,**ia)
    np.savez_compressed(challenge_out,**qa)
    i=np.load(intervention_out,allow_pickle=False)
    q=np.load(challenge_out,allow_pickle=False)

    total_bytes=sum(Path(p).stat().st_size for p in (control_path,intervention_out,challenge_out))
    if total_bytes>MAX_PERSISTED_BYTES:
        raise RuntimeError("persisted-byte ceiling exceeded")

    elapsed=time.monotonic()-started
    if elapsed>MAX_WALL_SECONDS:
        raise RuntimeError("preparation wall-time ceiling exceeded")

    receipt={
      "schema":SCHEMA,
      "status":"model-free-preparation-complete",
      "controlExamples":int(len(c["features"])),
      "interventionChangedTrainingRows":int(len(train_rows)),
      "challengeChangedTestRows":int(len(test_rows)),
      "renderedClips":int(rendered),
      "renderedAudioSeconds":float(rendered_audio_seconds),
      "preparationSeconds":float(elapsed),
      "arrayHashes":{
        "control":dataset_array_hashes(c),
        "intervention":dataset_array_hashes(i),
        "challenge":dataset_array_hashes(q),
      },
      "datasetFileSha256":{
        "control":file_sha256(control_path),
        "intervention":file_sha256(intervention_out),
        "challenge":file_sha256(challenge_out),
      },
      "persistedDatasetBytes":{
        "control":int(Path(control_path).stat().st_size),
        "intervention":int(Path(intervention_out).stat().st_size),
        "challenge":int(Path(challenge_out).stat().st_size),
        "total":int(total_bytes),
      },
      "identity":{
        "interventionValidationTestFeaturesBitIdentical":True,
        "challengeTrainValidationFeaturesBitIdentical":True,
        "allNonFeatureArraysBitIdentical":True,
        "changedInterventionRowsExactlyTrain":True,
        "changedChallengeRowsExactlyTest":True,
        "reconstructedStateOnsetMatchEveryRow":True,
        "heldoutAndNonS9ReferencesMatchExactly":True,
        "historicalS9TrainChordReferencePrefixesVerified":historical_truncated_chord_refs==30,
      },
      "historicalS9StringStorage":{
        "trainingChordRowsWithTruncatedTemplateIdAndRefs":int(historical_truncated_chord_refs),
        "preservedUnchangedInAllArms":True,
        "repairAttempted":False,
        "note":"Frozen S9 training-chord template_id/refs_json fields are fixed-width-truncated; state/onset are intact. New arms preserve these historical fields byte-identically."
      },
      "rowRecords":row_records,
      "ceilings":{
        "renderedClipsMax":MAX_RENDERED_CLIPS,
        "audioSecondsMax":MAX_AUDIO_SECONDS,
        "persistedBytesMax":MAX_PERSISTED_BYTES,
        "wallSecondsMax":MAX_WALL_SECONDS,
      },
      "execution":{
        "modelRun":False,"modelsLoaded":0,"modelInference":False,"optimizerSteps":0,
        "thresholdSearch":False,"thresholdRetuning":False,"automaticRetry":False,
        "p1Accessed":False,"p2Accessed":False,"p3Opened":False,
        "paidComputeDollars":0,"productionMutation":False,
      },
    }
    Path(receipt_out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

def prepare_only(out_dir):
    out=Path(out_dir)
    if out.exists(): raise RuntimeError("refusing existing preparation path")
    out.mkdir(parents=True)
    ds=out/"datasets"; ds.mkdir()
    s0=ds/"s0-control.npz"
    control=ds/"s9-control.npz"
    intervention=ds/"source-domain-intervention.npz"
    challenge=ds/"source-domain-challenge.npz"

    generate_dataset(s0,out/"s0-render-receipt.json")
    build_intervention_dataset(s0,control,out/"s9-diverse-receipt.json")
    receipt=build_source_domain_datasets(
        control,intervention,challenge,out/"source-domain-dataset-receipt.json"
    )
    # Full preparation includes 294 frozen S0 renders, 30 S9 chord replacement
    # renders, plus the source-domain train/test renders counted above.
    full_rendered_clips=294+30+int(receipt["renderedClips"])
    full_audio_seconds=full_rendered_clips*CLIP_SECONDS
    if full_rendered_clips>MAX_RENDERED_CLIPS or full_audio_seconds>MAX_AUDIO_SECONDS:
        raise RuntimeError("full preparation render/audio ceiling exceeded")
    receipt["fullPreparationRenderedClips"]=int(full_rendered_clips)
    receipt["fullPreparationAudioSeconds"]=float(full_audio_seconds)
    Path(out/"source-domain-dataset-receipt.json").write_text(
        json.dumps(receipt,indent=2,sort_keys=True)+"\n"
    )
    # S0 is an intermediate input, not part of the frozen three-arm package.
    s0.unlink()
    summary={
      "schema":"astra-source-domain-simulator-preparation-summary-v1",
      "modelRun":False,"optimizerSteps":0,
      "datasetReceipt":receipt,
      "guards":{"p1Accessed":False,"p2Accessed":False,"p3Opened":False},
    }
    (out/"preparation-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print("SOURCE_DOMAIN_PREPARATION="+json.dumps(summary,sort_keys=True))
    return summary

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out-dir",required=True)
    a=ap.parse_args(); prepare_only(a.out_dir)

if __name__=="__main__": main()
