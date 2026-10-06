#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, tempfile
from pathlib import Path

EXPECTED_TRACKS=30
EXPECTED_BP_MODEL_SHA="3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"
EXPECTED_GUITAR_FL_SHA="50d93dba89bdd3401849bc735614478e83d9f46d21fa3f71d8aca5acc0a52028"

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def midi_events(path:Path):
    import mido
    mid=mido.MidiFile(path)
    tempo=500000
    sec=0.0
    merged=mido.merge_tracks(mid.tracks)
    active={}
    out=[]
    for msg in merged:
        sec += mido.tick2second(msg.time,mid.ticks_per_beat,tempo)
        if msg.type=="set_tempo":
            tempo=msg.tempo
        elif msg.type=="note_on" and msg.velocity>0:
            active.setdefault(int(msg.note),[]).append((sec,int(msg.velocity)))
        elif msg.type in ("note_off","note_on") and (msg.type=="note_off" or msg.velocity==0):
            q=active.get(int(msg.note),[])
            if q:
                st,vel=q.pop(0); out.append({"start":float(st),"end":float(sec),"pitch":int(msg.note),"velocity":vel})
    out.sort(key=lambda x:(x["start"],x["pitch"],x["end"]))
    for i,e in enumerate(out): e["eventId"]=i
    return out

def normalize_bp(rows):
    out=[]
    for r in rows:
        st,en,pitch,amp=r[:4]
        out.append({"start":float(st),"end":float(en),"pitch":int(pitch),"amplitude":float(amp)})
    out.sort(key=lambda x:(x["start"],x["pitch"],x["end"]))
    for i,e in enumerate(out): e["eventId"]=i
    return out

def write_payload(out:Path,stem:str,source_sha:str,kind:str,events,identity:dict):
    payload={"schema":"astra-fresh-front-end-candidate-v1","trackStem":stem,"sourceAudioSha256":source_sha,"frontEnd":kind,"identity":identity,"events":events,"eventCount":len(events),"referenceRead":False,"predictionMutation":False,"thresholdSearch":False,"optimizerSteps":0}
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    return {"file":out.name,"stem":stem,"sha256":sha256_file(out),"eventCount":len(events),"sourceAudioSha256":source_sha}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio-dir",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--guitar-fl-checkpoint",type=Path,required=True)
    a=ap.parse_args()
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import Model,predict
    if sha256_file(Path(ICASSP_2022_MODEL_PATH))!=EXPECTED_BP_MODEL_SHA: raise RuntimeError("Basic Pitch model SHA mismatch")
    if sha256_file(a.guitar_fl_checkpoint)!=EXPECTED_GUITAR_FL_SHA: raise RuntimeError("guitar-fl checkpoint SHA mismatch")
    from hf_midi_transcription.model import MidiTranscriptionModel
    bp_model=Model(Path(ICASSP_2022_MODEL_PATH))
    alt=MidiTranscriptionModel(device="cpu",instrument="guitar",checkpoint_path=str(a.guitar_fl_checkpoint),batch_size=8)
    audios=sorted(a.audio_dir.glob("*.wav"))
    if len(audios)!=EXPECTED_TRACKS: raise RuntimeError(f"expected {EXPECTED_TRACKS} audio files, got {len(audios)}")
    bp_dir=a.output_dir/"basic_pitch"; alt_dir=a.output_dir/"guitar_fl"
    bp_dir.mkdir(parents=True,exist_ok=True); alt_dir.mkdir(parents=True,exist_ok=True)
    bp_recs=[]; alt_recs=[]
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        for i,p in enumerate(audios,1):
            source_sha=sha256_file(p)
            _,_,bp_rows=predict(p,model_or_model_path=bp_model,onset_threshold=0.5,frame_threshold=0.3,minimum_note_length=127.70,minimum_frequency=None,maximum_frequency=None,multiple_pitch_bends=False,melodia_trick=True,midi_tempo=120.0)
            bp_events=normalize_bp(bp_rows)
            midi=td/f"{p.stem}.mid"
            alt.transcribe(p,midi)
            alt_events=midi_events(midi)
            bp_recs.append(write_payload(bp_dir/f"{p.stem}.json",p.stem,source_sha,"basic_pitch_0.4.0",bp_events,{"modelSha256":EXPECTED_BP_MODEL_SHA,"onsetThreshold":0.5,"frameThreshold":0.3,"minimumNoteLengthMs":127.70,"melodiaTrick":True}))
            alt_recs.append(write_payload(alt_dir/f"{p.stem}.json",p.stem,source_sha,"xavriley_guitar_fl",alt_events,{"checkpointSha256":EXPECTED_GUITAR_FL_SHA,"effectiveOnsetThreshold":0.3,"effectiveOffsetThreshold":0.3,"effectiveFrameThreshold":0.1,"sampleRateHz":16000,"framesPerSecond":100}))
            print(json.dumps({"track":p.stem,"index":i,"basicPitchEvents":len(bp_events),"guitarFlEvents":len(alt_events)}),flush=True)
    for name,recs in (("basic_pitch",bp_recs),("guitar_fl",alt_recs)):
        mp=a.output_dir/f"{name}-candidate-freeze-manifest.json"
        mp.write_text(json.dumps({"schema":"astra-fresh-front-end-candidate-freeze-manifest-v1","frontEnd":name,"trackCount":len(recs),"totalEventCount":sum(r["eventCount"] for r in recs),"files":recs,"referenceRead":False,"predictionMutation":False,"thresholdSearch":False,"optimizerSteps":0},indent=2,sort_keys=True)+"\n")
        print(json.dumps({"frozen":name,"manifestSha256":sha256_file(mp),"totalEventCount":sum(r["eventCount"] for r in recs)},sort_keys=True))
if __name__=="__main__": main()
