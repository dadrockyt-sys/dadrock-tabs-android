from __future__ import annotations

"""Research-only adapter for a guitar-specific HCQT+Mel tablature model.

This module is intentionally outside the V143 producer. It refuses any audio
whose SHA differs from the approved fixture unless an explicit non-candidate
probe flag is supplied. Upstream model code/weights are MIT-licensed and are
loaded from user-supplied local paths; no third-party weights are vendored.
"""

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import numpy as np

APPROVED_AUDIO_SHA256 = "215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f"
UPSTREAM_CODE_REPO = "ErenReyhanlioglu/Guitar-Transcription"
UPSTREAM_WEIGHTS_REPO = "ErenReyhanlioglu/Guitar-Transcription-Weights"
UPSTREAM_MODEL_FAMILY = "cnn_mtl_20251210_113013"
UPSTREAM_CONFIG_BLOB = "8fb170c504a7a43e49d65d14ae47944cee77d52e"
UPSTREAM_MODEL_BLOB = "cfe5a8e91d7315ad43f976bc114fdaba82838fbd"
UPSTREAM_FOLD1_WEIGHT_BLOB = "82094eecad83603b331b1bfbce0f0310f8942df8"
SR, HOP, WINDOW, CHUNK = 22050, 512, 19, 500
HARMONICS = (0.5, 1.0, 2.0, 3.0, 4.0, 5.0)
TUNING_LOW_TO_HIGH = (40, 45, 50, 55, 59, 64)
STRING_NAMES_HIGH_TO_LOW = ("e", "B", "G", "D", "A", "E")
SILENCE_CLASS, NUM_CLASSES, MIN_MIDI, MAX_MIDI = 20, 21, 40, 88


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_features(audio: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    import librosa

    audio = np.asarray(audio, dtype=np.float32)
    fmin = float(librosa.note_to_hz("E2"))
    channels = []
    for harmonic in HARMONICS:
        vqt = librosa.vqt(
            y=audio, sr=SR, hop_length=HOP, fmin=harmonic * fmin,
            n_bins=144, bins_per_octave=36, gamma=0,
        )
        db = librosa.amplitude_to_db(np.abs(vqt), ref=np.max)
        channels.append((db / 80.0 + 1.0).astype(np.float32))
    frames = min(x.shape[-1] for x in channels)
    hcqt = np.stack([x[..., :frames] for x in channels], axis=0)
    mel = librosa.feature.melspectrogram(
        y=audio, sr=SR, n_mels=256, n_fft=2048, hop_length=HOP,
        win_length=None, center=True, htk=False,
    )
    mel = (librosa.power_to_db(mel, ref=np.max) / 80.0 + 1.0).astype(np.float32)[None]
    frames = min(frames, mel.shape[-1])
    hcqt, mel = hcqt[..., :frames], mel[..., :frames]
    times = librosa.frames_to_time(np.arange(frames), sr=SR, hop_length=HOP)
    if hcqt.shape != (6, 144, frames) or mel.shape != (1, 256, frames):
        raise RuntimeError(f"feature shape mismatch hcqt={hcqt.shape} mel={mel.shape}")
    return hcqt, mel, np.asarray(times, dtype=np.float64)


def load_audio(path: Path) -> np.ndarray:
    import librosa

    audio, rate = librosa.load(str(path), sr=SR, mono=True)
    if rate != SR or audio.size == 0:
        raise RuntimeError("audio decode/resample failed")
    return np.asarray(audio, dtype=np.float32)


def load_model(upstream_code: Path, config_path: Path, checkpoint: Path, device: str):
    import torch
    import yaml

    sys.path.insert(0, str(upstream_code.resolve()))
    try:
        get_model = importlib.import_module("src.models").get_model
        config = yaml.safe_load(config_path.read_text())
        model = get_model(config).to(device)
        with torch.no_grad():
            model({
                "hcqt": torch.zeros(1, 6, 144, WINDOW, device=device),
                "mel": torch.zeros(1, 1, 256, WINDOW, device=device),
            })
        state = torch.load(str(checkpoint), map_location=device, weights_only=True)
        model.load_state_dict(state, strict=True)
        model.eval()
        return model
    finally:
        sys.path.pop(0)


def windows(feature: np.ndarray, start: int, valid: int, chunk: int):
    import torch
    import torch.nn.functional as F

    part = feature[..., start : start + valid]
    if valid < chunk:
        part = np.pad(part, [(0, 0)] * (part.ndim - 1) + [(0, chunk - valid)])
    x = torch.from_numpy(part.astype(np.float32, copy=False)).unsqueeze(0)
    x = F.pad(x, (WINDOW // 2, WINDOW // 2), "constant", 0)
    x = x.unfold(3, WINDOW, 1).permute(0, 3, 1, 2, 4)
    b, t, c, f, w = x.shape
    return x.reshape(b * t, c, f, w)


def infer(model, hcqt: np.ndarray, mel: np.ndarray, device: str) -> dict[str, np.ndarray]:
    import torch

    total = hcqt.shape[-1]
    keys = ("tab_logits", "multipitch_logits", "hand_pos_logits", "activity_logits")
    out: dict[str, list[np.ndarray]] = {k: [] for k in keys}
    with torch.no_grad():
        for start in range(0, total, CHUNK):
            valid = min(CHUNK, total - start)
            raw = model({
                "hcqt": windows(hcqt, start, valid, CHUNK).to(device),
                "mel": windows(mel, start, valid, CHUNK).to(device),
            })
            for key in keys:
                value = raw[key]
                if key == "tab_logits":
                    value = value.view(-1, 6, NUM_CLASSES)
                out[key].append(value[:valid].cpu().numpy())
    return {k: np.concatenate(v, axis=0) for k, v in out.items()}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.asarray(x, dtype=np.float32)))


def probabilities(raw: Mapping[str, np.ndarray]):
    logits = np.asarray(raw["tab_logits"], dtype=np.float32)
    exp = np.exp(logits - logits.max(axis=-1, keepdims=True))
    tab_probs = exp / exp.sum(axis=-1, keepdims=True)
    classes = logits.argmax(axis=-1).astype(np.int16)
    confidence = np.take_along_axis(tab_probs, classes[..., None], axis=-1)[..., 0]
    hp_logits = np.asarray(raw["hand_pos_logits"], dtype=np.float32)
    hp_exp = np.exp(hp_logits - hp_logits.max(axis=-1, keepdims=True))
    hp = hp_exp / hp_exp.sum(axis=-1, keepdims=True)
    return classes, confidence, sigmoid(raw["multipitch_logits"]), sigmoid(raw["activity_logits"]), hp


def project_string(ext_low_to_high: int) -> int:
    return 5 - int(ext_low_to_high)


def model_tab_at_frame(classes: np.ndarray, confidence: np.ndarray, activity: np.ndarray, frame: int):
    notes = []
    for ext_string in range(6):
        fret = int(classes[frame, ext_string])
        if fret == SILENCE_CLASS:
            continue
        string_index = project_string(ext_string)
        notes.append({
            "stringIndex": string_index,
            "stringName": STRING_NAMES_HIGH_TO_LOW[string_index],
            "fret": fret,
            "midi": TUNING_LOW_TO_HIGH[ext_string] + fret,
            "classProbability": float(confidence[frame, ext_string]),
            "stringActivityProbability": float(activity[frame, ext_string]),
        })
    return notes


def grid_samples(product: Mapping[str, Any], times: np.ndarray, classes: np.ndarray,
                 confidence: np.ndarray, mp: np.ndarray, activity: np.ndarray, hp: np.ndarray):
    attacks = (product.get("precisionReplayEvidence") or {}).get("eligibleAttacks") or []
    rows = []
    for attack in attacks:
        grid_time = float(attack["gridTime"])
        frame = int(np.clip(np.rint(grid_time * SR / HOP), 0, len(times) - 1))
        tab = model_tab_at_frame(classes, confidence, activity, frame)
        support = []
        for value in attack.get("candidateMidis") or []:
            midi = int(value)
            support.append({
                "midi": midi,
                "multipitchProbability": float(mp[frame, midi - MIN_MIDI]) if MIN_MIDI <= midi <= MAX_MIDI else None,
            })
        rows.append({
            "measure": int(attack["measure"]), "step": int(attack["step"]),
            "gridTime": grid_time, "modelFrame": frame, "modelFrameTime": float(times[frame]),
            "retainedByCurrentPrecision": bool(attack.get("retained")),
            "currentCandidateMidis": sorted(int(x) for x in attack.get("candidateMidis") or []),
            "modelTab": tab, "modelTabMidis": sorted({int(x["midi"]) for x in tab}),
            "candidateMultipitchSupport": support,
            "handPositionProbabilities": [float(x) for x in hp[frame]],
        })
    return rows


def self_test() -> dict[str, Any]:
    t = np.arange(SR, dtype=np.float32) / SR
    audio = (0.1 * np.sin(2 * np.pi * 110.0 * t)).astype(np.float32)
    hcqt, mel, times = extract_features(audio)
    return {
        "schemaVersion": 1,
        "probe": "v143-specialized-guitar-amt-hcqt-mel-cascaded-mtl",
        "featureSelfTestPassed": hcqt.shape[:2] == (6, 144) and mel.shape[:2] == (1, 256) and len(times) == hcqt.shape[-1],
        "hcqtShape": list(hcqt.shape), "melShape": list(mel.shape), "frameCount": len(times),
        "productionModified": False, "professionalReferenceUsed": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Bounded source-only specialized guitar-AMT probe")
    p.add_argument("--audio", type=Path); p.add_argument("--upstream-code", type=Path)
    p.add_argument("--config", type=Path); p.add_argument("--checkpoint", type=Path)
    p.add_argument("--v143-product", type=Path); p.add_argument("--out", type=Path)
    p.add_argument("--device", default="cpu"); p.add_argument("--allow-nonapproved-domain-probe", action="store_true")
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True)); return
    required = (args.audio, args.upstream_code, args.config, args.checkpoint, args.out)
    if any(x is None for x in required):
        raise SystemExit("--audio --upstream-code --config --checkpoint --out are required")

    audio_sha = sha256(args.audio)
    approved = audio_sha == APPROVED_AUDIO_SHA256
    if not approved and not args.allow_nonapproved_domain_probe:
        raise SystemExit(f"refusing audio SHA {audio_sha}; expected approved {APPROVED_AUDIO_SHA256}")

    audio = load_audio(args.audio)
    hcqt, mel, times = extract_features(audio)
    model = load_model(args.upstream_code, args.config, args.checkpoint, args.device)
    raw = infer(model, hcqt, mel, args.device)
    classes, conf, mp, activity, hp = probabilities(raw)
    product = json.loads(args.v143_product.read_text()) if args.v143_product else None
    report = {
        "schemaVersion": 1, "probe": "v143-specialized-guitar-amt-hcqt-mel-cascaded-mtl",
        "researchOnly": True, "productionModified": False, "professionalReferenceUsed": False,
        "sourceAudio": {"name": args.audio.name, "sha256": audio_sha, "approvedFixture": approved,
                        "approvedFixtureSha256": APPROVED_AUDIO_SHA256, "domainProbeOnly": not approved},
        "checkpoint": {"name": args.checkpoint.name, "sha256": sha256(args.checkpoint),
                       "expectedFold1GitBlob": UPSTREAM_FOLD1_WEIGHT_BLOB},
        "upstream": {"codeRepository": UPSTREAM_CODE_REPO, "weightsRepository": UPSTREAM_WEIGHTS_REPO,
                     "license": "MIT", "modelFamily": UPSTREAM_MODEL_FAMILY,
                     "configGitBlob": UPSTREAM_CONFIG_BLOB, "modelSourceGitBlob": UPSTREAM_MODEL_BLOB},
        "featureContract": {"sampleRate": SR, "hopLength": HOP, "windowSize": WINDOW,
                            "hcqtHarmonics": list(HARMONICS), "hcqtShape": list(hcqt.shape),
                            "melShape": list(mel.shape)},
        "predictionSummary": {"activeFrameStringCount": int(np.sum(classes != SILENCE_CLASS)),
                              "meanActiveClassProbability": float(np.mean(conf[classes != SILENCE_CLASS]))
                              if np.any(classes != SILENCE_CLASS) else None},
    }
    if product is not None:
        report["v143GridSamples"] = grid_samples(product, times, classes, conf, mp, activity, hp)
        report["v143GridSampleCount"] = len(report["v143GridSamples"])
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"out": str(args.out), "approvedFixture": approved,
                      "frameCount": len(times), "v143GridSampleCount": report.get("v143GridSampleCount")}, indent=2))


if __name__ == "__main__":
    main()
