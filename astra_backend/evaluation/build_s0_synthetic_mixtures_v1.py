"""Build deterministic S0 synthetic mixtures from rights-cleared fixture files.

This script performs mixing only. It does not run source separation or transcription.
Requires ffmpeg/ffprobe.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

MIXES = [{"id":"S0M01","durationSeconds":5.352,"components":[["guitar","G09","freesound_community-clean-electric-guitar-loop-83895(1).mp3",0],["bass","B01","freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3",0]],"mixSha256":"c184fa3f3a52f0216dbb93d528fa547697c05ea886a82f03111cc925afa9d4ea"},{"id":"S0M02","durationSeconds":6.888,"components":[["guitar","G10","freesound_community-electric-guitar-metal-riff-107087(1).mp3",0],["bass","B06","freesound_community-bass-guitar-death-metal-loop-240-bpm-101327.mp3",0]],"mixSha256":"0b288c2d944a278e839b8371d284320c1a1dca9f75c90dfdbb2f7343a1bb61f4"},{"id":"S0M03","durationSeconds":9.552,"components":[["guitar","G13","freesound_community-electric-guitar-strumming-3-97679(1).mp3",0],["bass","B12","freesound_community-picked_bassnote_a-100710.mp3",-6]],"mixSha256":"af84665940e0d41db383dd7e3f3680f47e3ee8d600284dd897405a201945041a"},{"id":"S0M04","durationSeconds":18.155094,"components":[["guitar","G14","freesound_community-electric-guitar-tapping-34546(1).mp3",0],["bass","B08","idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3",0]],"mixSha256":"8b6469957de871a727c31803033f2878f5855f1b67c4902619f2df42a3b22ff7"},{"id":"S0M05","durationSeconds":6.034281,"components":[["guitar","G21","shidenbeatsmusic-jingle-slide-guitar-22108(1).mp3",0],["bass","B20","freesound_community-fretless-bass-open-d-bridge-pickup-100754.mp3",-3]],"mixSha256":"e2159232e929c03ca5b1e862ceb673f09e06e13e2fe06133f8aa02a13af154b9"},{"id":"S0M06","durationSeconds":10.464,"components":[["guitar","G23","sunnyscy-guitar-riff-in-e-minor-95-bpm-dry-475013(1).mp3",0],["bass","B26","freesound_community-bass60bpm-78680.mp3",0]],"mixSha256":"6877e998de996690d3213b0bdc353c070c7f40f09dbbdb39561dcf398f3a44c5"},{"id":"S0M07","durationSeconds":5.352,"components":[["guitar","G09","freesound_community-clean-electric-guitar-loop-83895(1).mp3",0],["other_drums","N01","dragon-studio-atmospheric-drums-443147(1).mp3",-3]],"mixSha256":"70025eeedbc427b14e752c8c3c7a65af8760bc5a0f6b52577d248b098c38da93"},{"id":"S0M08","durationSeconds":5.592,"components":[["bass","B01","freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3",0],["other_drums","N01","dragon-studio-atmospheric-drums-443147(1).mp3",-3]],"mixSha256":"3ff02d21ef02abea882d9252a4efae2085aeed4b75e48cc07db83e49e350f6b2"},{"id":"S0M09","durationSeconds":6.888,"components":[["guitar","G10","freesound_community-electric-guitar-metal-riff-107087(1).mp3",0],["other_speech","N04","freesound_community-speech-dramatic-female-38105(1).mp3",-6]],"mixSha256":"a2e59454a220e4a4900563cc14323006fd04da0b9b4d02610b2d9e50954ba822"},{"id":"S0M10","durationSeconds":7.366531,"components":[["bass","B08","idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3",0],["other_speech","N04","freesound_community-speech-dramatic-female-38105(1).mp3",-6]],"mixSha256":"28b96a6c5a464df2642cba831a06d328df669a96b6a21dce18e9466e42da0c89"},{"id":"S0M11","durationSeconds":5.592,"components":[["guitar","G23","sunnyscy-guitar-riff-in-e-minor-95-bpm-dry-475013(1).mp3",0],["bass","B01","freesound_community-electric-bass-guitar-loop-2-bpm-110-43631.mp3",-3],["other_drums","N01","dragon-studio-atmospheric-drums-443147(1).mp3",-6]],"mixSha256":"95284f8148408814dd2c460aad1d16321b274c7ad8cf4683163525fa477ec107"},{"id":"S0M12","durationSeconds":7.366531,"components":[["guitar","G14","freesound_community-electric-guitar-tapping-34546(1).mp3",0],["bass","B08","idoberg-funk-rock-slap-bass-riff-em-106bpm-490940.mp3",-3],["other_speech","N04","freesound_community-speech-dramatic-female-38105(1).mp3",-9]],"mixSha256":"290b1c51c3b485efc3384b4aae5b50ee1e6bcf86e7c4f938f5b7d0a149bd5b68"}]

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def probe_duration(path: Path) -> float:
    out=subprocess.check_output([
        "ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1",str(path)
    ], text=True)
    return float(out.strip())

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True)
    ap.add_argument("--output-dir", required=True)
    args=ap.parse_args()
    src=Path(args.source_dir)
    out=Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    built=[]
    for spec in MIXES:
        d=out/spec["id"]; d.mkdir(exist_ok=True)
        component_files=[]
        durations=[]
        for _,_,name,_ in spec["components"]:
            durations.append(probe_duration(src/name))
        duration=min(durations)
        rows=[]
        for i,(role,source_id,name,relative_db) in enumerate(spec["components"],1):
            rendered_db=relative_db-6
            target=d/f"{i:02d}_{role}.wav"
            subprocess.run([
                "ffmpeg","-y","-v","error","-i",str(src/name),
                "-t",f"{duration:.6f}",
                "-af",f"aresample=44100,volume={rendered_db}dB",
                "-ac","2","-c:a","pcm_f32le",str(target)
            ], check=True)
            component_files.append(target)
            rows.append({
                "role":role,"sourceId":source_id,"sourceFilename":name,
                "relativeGainDb":relative_db,"renderedGainDb":rendered_db,
                "stemFilename":target.name,"stemSha256":sha256(target)
            })
        mix=d/f'{spec["id"]}_mix.wav'
        cmd=["ffmpeg","-y","-v","error"]
        for p in component_files: cmd += ["-i",str(p)]
        ins="".join(f"[{i}:a]" for i in range(len(component_files)))
        cmd += ["-filter_complex",f"{ins}amix=inputs={len(component_files)}:normalize=0:duration=shortest[a]",
                "-map","[a]","-c:a","pcm_f32le",str(mix)]
        subprocess.run(cmd, check=True)
        built.append({
            "id":spec["id"],"durationSeconds":duration,
            "components":rows,"mixFilename":mix.name,"mixSha256":sha256(mix)
        })
    (out/"S0_MANIFEST.generated.json").write_text(
        json.dumps({"schemaVersion":1,"mixtures":built}, indent=2)+"\n"
    )

if __name__=="__main__":
    main()
