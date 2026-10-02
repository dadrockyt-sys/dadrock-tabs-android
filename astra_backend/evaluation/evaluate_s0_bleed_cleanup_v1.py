"""Evaluate bleed cleanup on frozen S0 exact-component mixtures.

Default mode injects deterministic -18 dB cross-stem bleed into ground-truth stems.
It does NOT run a separator or any learned model.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import soundfile as sf
from stem_bleed_cleanup_v1 import CleanupConfig, exact_residual, inject_symmetric_bleed, si_sdr, suppress_cross_stem_bleed


def load_wav(path: Path):
    x,fs=sf.read(path,always_2d=True,dtype="float32")
    return x,fs


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--s0-root", required=True)
    ap.add_argument("--output-json")
    ap.add_argument("--bleed-db", type=float, default=-18.0)
    args=ap.parse_args()
    root=Path(args.s0_root)
    cfg=CleanupConfig()
    rows=[]
    for directory in sorted(root.glob("S0M*")):
        stem_paths=sorted(p for p in directory.glob("*.wav") if not p.name.endswith("_mix.wav"))
        mix_paths=list(directory.glob("*_mix.wav"))
        if not stem_paths or len(mix_paths)!=1:
            continue
        truth={}; fs=None
        for path in stem_paths:
            x,sr=load_wav(path)
            if fs is not None and sr != fs:
                raise SystemExit(f"sample-rate mismatch in {directory.name}")
            fs=sr
            truth[path.stem.split("_",1)[1]]=x
        mix,mix_fs=load_wav(mix_paths[0])
        if mix_fs != fs:
            raise SystemExit(f"mixture sample-rate mismatch in {directory.name}")
        length=min([len(mix), *[len(x) for x in truth.values()]])
        mix=mix[:length]; truth={k:v[:length] for k,v in truth.items()}
        estimated=inject_symmetric_bleed(truth,args.bleed_db)
        cleaned,_=suppress_cross_stem_bleed(estimated,fs,cfg)
        raw_scores={k:si_sdr(truth[k],estimated[k]) for k in truth}
        clean_scores={k:si_sdr(truth[k],cleaned[k]) for k in truth}
        residual=exact_residual(mix,cleaned)
        recon=residual.copy()
        for value in cleaned.values(): recon += value[:length]
        rows.append({
            "id":directory.name,
            "rawMeanSiSdrDb":float(np.mean(list(raw_scores.values()))),
            "cleanMeanSiSdrDb":float(np.mean(list(clean_scores.values()))),
            "meanImprovementDb":float(np.mean(list(clean_scores.values()))-np.mean(list(raw_scores.values()))),
            "reconstructionMaxAbsError":float(np.max(np.abs(recon-mix))),
            "rawByStem":raw_scores,
            "cleanByStem":clean_scores,
        })
    result={
        "schemaVersion":1,
        "mode":"deterministic_symmetric_bleed_injection",
        "bleedDb":args.bleed_db,
        "cleanupConfig":cfg.to_dict(),
        "mixtureCount":len(rows),
        "meanImprovementDb":float(np.mean([r["meanImprovementDb"] for r in rows])),
        "minimumMixtureImprovementDb":float(min(r["meanImprovementDb"] for r in rows)),
        "maximumReconstructionAbsError":float(max(r["reconstructionMaxAbsError"] for r in rows)),
        "allMixturesImproved":all(r["meanImprovementDb"]>0 for r in rows),
        "results":rows,
        "interpretation":"Development-unit-test only; this is known injected bleed, not separator evidence."
    }
    text=json.dumps(result,indent=2)+"\n"
    if args.output_json: Path(args.output_json).write_text(text)
    print(text,end="")

if __name__=="__main__": main()
