"""Freeze raw Basic Pitch activation evidence for Go My Way guitar stem.

Reference-blind:
- immutable source audio
- frozen BS-Roformer guitar stem
- Basic Pitch 0.4.0 model output before note-event thresholding
No professional reference is read.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import soundfile as sf

EXPECTED_BP_SHA256="3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--guitar-wav",required=True)
    ap.add_argument("--output-npz",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()

    import basic_pitch
    from basic_pitch.inference import predict
    model_path=Path(basic_pitch.ICASSP_2022_MODEL_PATH)
    model_sha=sha(model_path)
    if model_sha!=EXPECTED_BP_SHA256:
        raise RuntimeError(f"Basic Pitch model SHA mismatch: {model_sha}")

    model_output,midi_data,note_events=predict(
        a.guitar_wav,
        onset_threshold=0.5,
        frame_threshold=0.3,
        minimum_note_length=127.70,
        melodia_trick=True,
    )

    arrays={}
    meta={}
    if isinstance(model_output,dict):
        for k,v in model_output.items():
            arr=np.asarray(v)
            arrays[str(k)]=arr.astype(np.float32)
            meta[str(k)]={"shape":list(arr.shape),"dtype":str(arr.dtype),
                          "min":float(np.min(arr)) if arr.size else None,
                          "max":float(np.max(arr)) if arr.size else None,
                          "mean":float(np.mean(arr)) if arr.size else None}
    else:
        arr=np.asarray(model_output)
        arrays["model_output"]=arr.astype(np.float32)
        meta["model_output"]={"shape":list(arr.shape),"dtype":str(arr.dtype),
                              "min":float(np.min(arr)) if arr.size else None,
                              "max":float(np.max(arr)) if arr.size else None,
                              "mean":float(np.mean(arr)) if arr.size else None}

    np.savez_compressed(a.output_npz,**arrays)
    audio,sr=sf.read(a.guitar_wav,dtype="float32",always_2d=True)
    out={
      "schemaVersion":1,
      "kind":"gomyway-basic-pitch-raw-guitar-activations-v1",
      "referenceBlind":True,
      "professionalReferenceRead":False,
      "basicPitchVersion":"0.4.0",
      "basicPitchModelSha256":model_sha,
      "guitarStemSha256":sha(a.guitar_wav),
      "sampleRate":int(sr),
      "audioDurationSeconds":len(audio)/float(sr),
      "modelOutput":meta,
      "thresholdedNoteEventCount":len(note_events),
      "npzSha256":sha(a.output_npz),
      "interpretationBoundary":"Raw activation evidence only; no threshold search or professional-reference tuning."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
