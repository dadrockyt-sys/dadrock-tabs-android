"""Freeze raw Go My Way note evidence under the V4-origin research clock.

No reference-conditioned inference. Saves raw whole/guitar/bass Basic Pitch events so
later diagnostics can reuse byte-identical prediction evidence.
"""
from __future__ import annotations
import argparse, json, tempfile
from pathlib import Path
from evaluate_gomyway_full_song_professional_v2 import EXPECTED_BP_SHA256, BASIC_PITCH_VERSION, sha256_file, load_audio
from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
from evaluate_s0_transcription_failure_attribution_v1 import run_probe
from pretrained_note_front_end_v1 import basic_pitch_model_identity, ONSET_THRESHOLD, FRAME_THRESHOLD, MIN_NOTE_LENGTH_MS

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--audio-source",required=True); ap.add_argument("--audio-wav",required=True)
    ap.add_argument("--timing-map",required=True); ap.add_argument("--model",required=True)
    ap.add_argument("--output-json",required=True)
    a=ap.parse_args()
    bp=basic_pitch_model_identity()
    if bp["packageVersion"]!=BASIC_PITCH_VERSION or bp["modelSha256"]!=EXPECTED_BP_SHA256:
        raise RuntimeError("Basic Pitch frozen identity mismatch")
    timing=json.loads(Path(a.timing_map).read_text())
    audio,fs=load_audio(Path(a.audio_wav))
    stems=BsRoformer6StemOnnxAdapter(Path(a.model)).separate_array(audio,fs)
    with tempfile.TemporaryDirectory(prefix="astra_note_evidence_") as td:
        td=Path(td)
        whole=run_probe(audio,fs,td/"whole.wav","whole")
        guitar=run_probe(stems["guitar"],fs,td/"guitar.wav","guitar")
        bass=run_probe(stems["bass"],fs,td/"bass.wav","bass")
    out={
      "schemaVersion":1,
      "kind":"gomyway-v4-origin-frozen-note-evidence-v1",
      "referenceBlindInference":True,
      "audio":{"sourcePath":a.audio_source,"sourceSha256":sha256_file(Path(a.audio_source)),"durationSeconds":len(audio)/float(fs)},
      "timingMap":{"path":a.timing_map,"sha256":sha256_file(Path(a.timing_map))},
      "separator":{"name":"BS-Roformer-SW 6-stem FP16 ONNX","modelSha256":FP16_SHA256},
      "transcriber":{"name":"Basic Pitch","packageVersion":BASIC_PITCH_VERSION,"modelSha256":bp["modelSha256"],
                     "onsetThreshold":ONSET_THRESHOLD,"frameThreshold":FRAME_THRESHOLD,"minimumNoteLengthMs":MIN_NOTE_LENGTH_MS},
      "predictionCounts":{"whole":len(whole),"guitar":len(guitar),"bass":len(bass)},
      "predictions":{"whole":whole,"guitar":guitar,"bass":bass},
      "interpretationBoundary":"Raw frozen note evidence only. No professional note reference is read or used during generation."
    }
    Path(a.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"predictionCounts":out["predictionCounts"],"timingMapSha256":out["timingMap"]["sha256"]},indent=2))

if __name__=="__main__":main()
