#!/usr/bin/env python3
"""Stage-A frozen pretrained note-front-end adapter/scorer.

Pure scoring/identity utilities plus a thin Basic Pitch 0.4.0 inference wrapper.
No optimizer, threshold search, string/fret learning, or P3 access.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib, math
from pathlib import Path

OPEN_MIDI=(40,45,50,55,59,64)
P1_KEYS=(
"P1|chords|Drop3_7|directinput","P1|scales|Ab|directinput",
"P1|singlenotes|allsinglenotes|directinput","P1|techniques|PalmMute|directinput")
P2_KEYS=tuple(k.replace("P1|","P2|",1) for k in P1_KEYS)
FRAMES=200
ONSET_TOLERANCE=0.05
OFFSET_TOLERANCE=0.05
BASIC_PITCH_VERSION="0.4.0"
ONSET_THRESHOLD=0.5
FRAME_THRESHOLD=0.3
MIN_NOTE_LENGTH_MS=127.70

@dataclass(frozen=True)
class PitchEvent:
    id:str
    pitch:int
    start:float
    end:float

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def string_fret_to_midi(string,fret):
    if type(string) is not int or not 0<=string<6: raise ValueError("invalid string")
    if type(fret) is not int or not 0<=fret<=19: raise ValueError("invalid fret")
    return OPEN_MIDI[string]+fret

def validate_meta(meta,expected_key):
    if meta.get("captureKey")!=expected_key: raise RuntimeError("capture identity mismatch")
    if meta.get("captureView")!="directinput": raise RuntimeError("capture view mismatch")
    p=meta.get("prepared",{})
    if int(p.get("unresolvedLabelCount",-1))!=0: raise RuntimeError("unresolved selected labels")
    crop=p.get("crop",{})
    if int(crop.get("frames",-1))!=FRAMES: raise RuntimeError("crop frame identity mismatch")
    if meta.get("performer")!=expected_key.split("|",1)[0]: raise RuntimeError("performer mismatch")
    return True

def reference_pitch_events(meta):
    validate_meta(meta,meta["captureKey"])
    out=[]
    duplicate_groups={}
    for row in meta["prepared"]["scorableEvents"]:
        pitch=string_fret_to_midi(int(row["string"]),int(row["fret"]))
        e=PitchEvent(str(row["id"]),pitch,float(row["start"]),float(row["end"]))
        out.append(e)
        key=(round(e.start,9),round(e.end,9),pitch)
        duplicate_groups.setdefault(key,[]).append(e.id)
    ambiguous=[ids for ids in duplicate_groups.values() if len(ids)>1]
    return sorted(out,key=lambda e:(e.pitch,e.start,e.end,e.id)), ambiguous

def basic_pitch_to_crop_events(note_events,crop_start_seconds,crop_end_seconds):
    if not math.isfinite(crop_start_seconds) or not math.isfinite(crop_end_seconds) or crop_end_seconds<=crop_start_seconds:
        raise ValueError("invalid crop interval")
    out=[]
    for i,row in enumerate(note_events):
        if len(row)<3: raise ValueError("invalid Basic Pitch note tuple")
        start,end,pitch=float(row[0]),float(row[1]),int(row[2])
        if not (math.isfinite(start) and math.isfinite(end)) or end<=start: continue
        if start>=crop_end_seconds or end<=crop_start_seconds: continue
        local_start=max(0.0,start-crop_start_seconds)
        local_end=min(crop_end_seconds,end)-crop_start_seconds
        if local_end>local_start:
            out.append(PitchEvent(f"bp:{i}",pitch,local_start,local_end))
    return sorted(out,key=lambda e:(e.pitch,e.start,e.end,e.id))

def _match(preds,refs,require_offset):
    candidates=[]
    for pi,p in enumerate(preds):
        for ri,r in enumerate(refs):
            if p.pitch!=r.pitch: continue
            od=abs(p.start-r.start)
            if od>ONSET_TOLERANCE: continue
            off=abs(p.end-r.end)
            if require_offset and off>OFFSET_TOLERANCE: continue
            candidates.append((od+(off if require_offset else 0),pi,ri))
    usedp=set(); usedr=set(); matched=[]
    for _,pi,ri in sorted(candidates):
        if pi in usedp or ri in usedr: continue
        usedp.add(pi); usedr.add(ri); matched.append((pi,ri))
    tp=len(matched); fp=len(preds)-tp; fn=len(refs)-tp
    precision=tp/len(preds) if preds else (1.0 if not refs else 0.0)
    recall=tp/len(refs) if refs else 1.0
    f1=(2*precision*recall/(precision+recall)) if precision+recall else 0.0
    return {"referenceCount":len(refs),"predictionCount":len(preds),"truePositive":tp,"falsePositive":fp,"falseNegative":fn,
            "precision":precision,"recall":recall,"f1":f1,"matchedPairs":matched}

def score_pitch_events(preds,refs):
    return {"pitchOnset":_match(preds,refs,False),"pitchOnsetOffset":_match(preds,refs,True)}

def run_basic_pitch(audio_path):
    import basic_pitch
    from basic_pitch.inference import predict
    version=getattr(basic_pitch,"__version__",None)
    if version is not None and version!=BASIC_PITCH_VERSION: raise RuntimeError("Basic Pitch version mismatch")
    _,_,notes=predict(
      audio_path,
      onset_threshold=ONSET_THRESHOLD,
      frame_threshold=FRAME_THRESHOLD,
      minimum_note_length=MIN_NOTE_LENGTH_MS,
      melodia_trick=True,
    )
    return notes

def basic_pitch_model_identity():
    import basic_pitch
    p=Path(basic_pitch.ICASSP_2022_MODEL_PATH)
    return {"packageVersion":BASIC_PITCH_VERSION,"modelPath":str(p),"modelSha256":sha256_file(p),"modelBytes":p.stat().st_size}
