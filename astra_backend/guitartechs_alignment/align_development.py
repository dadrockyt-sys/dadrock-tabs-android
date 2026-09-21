#!/usr/bin/env python3
"""Frozen Guitar-TECHS P1/P2 alignment verifier.

Development-only. It estimates a constant audio-vs-MIDI lag from a deterministic
energy-onset envelope, applies the pre-frozen acceptance policy, and emits JSON.
It does not train/import a model, compute TabCNN features, or access P3.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np

SAMPLE_RATE = 8000
WINDOW_MS = 20
HOP_MS = 2
LAG_MIN_MS = -100
LAG_MAX_MS = 100
LAG_STEP_MS = 1
MATCH_TOLERANCE_MS = 20
MINIMUM_MIDI_ONSET_GROUPS = 30
MINIMUM_MATCHED_FRACTION = 0.8
MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_MS = 10
BOOTSTRAP_STRATA = 5
MAXIMUM_BOOTSTRAP_LAG_MAD_MS = 5
MAXIMUM_ABSOLUTE_APPLIED_CORRECTION_MS = 100
PEAK_STRENGTH_POSITIVE_QUANTILE = 0.50
CANONICAL_STRING_NAMES = {"e", "B", "G", "D", "A", "E"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_vlq(data: bytes, index: int):
    value = 0
    for _ in range(4):
        if index >= len(data):
            raise ValueError("truncated vlq")
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            return value, index
    return value, index


def parse_track(chunk: bytes):
    i = 0
    running = None
    tick = 0
    name = None
    note_on_ticks = []
    tempos = []
    while i < len(chunk):
        delta, i = read_vlq(chunk, i)
        tick += delta
        if i >= len(chunk):
            break
        status = chunk[i]
        if status < 0x80:
            if running is None:
                raise ValueError("running status without status")
            status = running
        else:
            i += 1
            if status < 0xF0:
                running = status

        if status == 0xFF:
            if i >= len(chunk):
                raise ValueError("truncated meta event")
            meta_type = chunk[i]
            i += 1
            length, i = read_vlq(chunk, i)
            payload = chunk[i:i + length]
            if len(payload) != length:
                raise ValueError("truncated meta payload")
            i += length
            if meta_type == 0x03:
                name = payload.decode("utf-8", "replace")
            elif meta_type == 0x51 and length == 3:
                tempos.append((tick, int.from_bytes(payload, "big")))
            continue

        if status in (0xF0, 0xF7):
            length, i = read_vlq(chunk, i)
            i += length
            continue

        kind = status & 0xF0
        if kind in (0xC0, 0xD0):
            if i >= len(chunk):
                raise ValueError("truncated one-byte midi event")
            i += 1
            continue
        if i + 1 >= len(chunk):
            raise ValueError("truncated two-byte midi event")
        _, velocity = chunk[i], chunk[i + 1]
        i += 2
        if kind == 0x90 and velocity > 0:
            note_on_ticks.append(tick)
    return {"name": name, "noteOnTicks": note_on_ticks, "tempos": tempos}


def tick_to_seconds(tick: int, ppq: int, tempo_events):
    elapsed = 0.0
    last_tick = 0
    tempo = 500000
    for event_tick, new_tempo in tempo_events:
        if event_tick > tick:
            break
        elapsed += (event_tick - last_tick) * tempo / 1_000_000.0 / ppq
        last_tick = event_tick
        tempo = new_tempo
    elapsed += (tick - last_tick) * tempo / 1_000_000.0 / ppq
    return elapsed


def parse_midi_onset_groups(path: Path):
    data = path.read_bytes()
    if len(data) < 14 or data[:4] != b"MThd":
        raise ValueError("missing MThd")
    header_len = struct.unpack(">I", data[4:8])[0]
    fmt, track_count, division = struct.unpack(">HHH", data[8:14])
    if division & 0x8000:
        raise ValueError("SMPTE MIDI division unsupported")
    if fmt not in (0, 1):
        raise ValueError("unsupported MIDI format")
    pos = 8 + header_len
    tracks = []
    for _ in range(track_count):
        if pos + 8 > len(data) or data[pos:pos + 4] != b"MTrk":
            raise ValueError("missing MTrk")
        size = struct.unpack(">I", data[pos + 4:pos + 8])[0]
        chunk = data[pos + 8:pos + 8 + size]
        if len(chunk) != size:
            raise ValueError("truncated MTrk")
        tracks.append(parse_track(chunk))
        pos += 8 + size

    tempos = [(0, 500000)]
    for track in tracks:
        tempos.extend(track["tempos"])
    by_tick = {}
    for event_tick, tempo in sorted(tempos, key=lambda item: item[0]):
        by_tick[event_tick] = tempo
    tempo_events = sorted(by_tick.items())

    string_tracks = [track for track in tracks if track["name"] in CANONICAL_STRING_NAMES]
    if not string_tracks:
        raise ValueError("no explicit string tracks")
    ticks = sorted({tick for track in string_tracks for tick in track["noteOnTicks"]})
    seconds = [tick_to_seconds(tick, division, tempo_events) for tick in ticks]
    return {
        "format": fmt,
        "ppq": division,
        "stringTrackNames": [track["name"] for track in string_tracks],
        "onsetGroupTicks": ticks,
        "onsetGroupSeconds": seconds,
    }


def decode_audio(path: Path):
    cmd = [
        "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
        "-i", str(path), "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
        "-f", "s16le", "-acodec", "pcm_s16le", "pipe:1",
    ]
    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pcm = np.frombuffer(result.stdout, dtype="<i2").astype(np.float64) / 32768.0
    if pcm.size == 0:
        raise ValueError("decoded audio is empty")
    return pcm


def onset_envelope(samples: np.ndarray):
    samples = np.asarray(samples, dtype=np.float64)
    window = int(round(SAMPLE_RATE * WINDOW_MS / 1000.0))
    hop = int(round(SAMPLE_RATE * HOP_MS / 1000.0))
    if samples.size < window + hop:
        raise ValueError("audio too short")
    squared = samples * samples
    csum = np.concatenate(([0.0], np.cumsum(squared)))
    starts = np.arange(0, samples.size - window + 1, hop, dtype=np.int64)
    energy = (csum[starts + window] - csum[starts]) / window
    log_rms = np.log1p(np.sqrt(np.maximum(energy, 0.0)) * 1000.0)
    flux = np.maximum(0.0, np.diff(log_rms, prepend=log_rms[0]))
    if flux.size >= 3:
        flux = np.convolve(flux, np.array([0.25, 0.5, 0.25]), mode="same")
    times = (starts + window) / SAMPLE_RATE
    return times, flux


def sample_envelope(times, flux, query):
    return np.interp(query, times, flux, left=0.0, right=0.0)


def best_lag_ms(midi_times, env_times, flux):
    midi = np.asarray(midi_times, dtype=np.float64)
    if midi.size == 0:
        raise ValueError("empty midi onset list")
    scored = []
    for lag in range(LAG_MIN_MS, LAG_MAX_MS + 1, LAG_STEP_MS):
        values = sample_envelope(env_times, flux, midi + lag / 1000.0)
        ordered = np.sort(values)
        trim = int(math.floor(ordered.size * 0.1))
        core = ordered[trim:ordered.size - trim] if ordered.size - 2 * trim > 0 else ordered
        score = float(np.mean(core))
        scored.append((score, -abs(lag), -lag, lag))
    return max(scored)[3]


def deterministic_strata_lags(midi_times, env_times, flux):
    midi = list(midi_times)
    lags = []
    for stratum in range(BOOTSTRAP_STRATA):
        subset = midi[stratum::BOOTSTRAP_STRATA]
        if len(subset) < 3:
            raise ValueError("insufficient onset groups per deterministic stratum")
        lags.append(best_lag_ms(subset, env_times, flux))
    return lags


def local_peak_matches(midi_times, lag_ms, env_times, flux):
    positive = flux[flux > 0]
    if positive.size == 0:
        return {"matched": 0, "fraction": 0.0, "residualsMs": [], "threshold": None}
    threshold = float(np.quantile(positive, PEAK_STRENGTH_POSITIVE_QUANTILE))
    tolerance = MATCH_TOLERANCE_MS / 1000.0
    residuals = []
    for midi_time in midi_times:
        target = midi_time + lag_ms / 1000.0
        left = int(np.searchsorted(env_times, target - tolerance, side="left"))
        right = int(np.searchsorted(env_times, target + tolerance, side="right"))
        if right <= left:
            continue
        segment = flux[left:right]
        rel = int(np.argmax(segment))
        strength = float(segment[rel])
        if strength < threshold:
            continue
        residuals.append(abs(float(env_times[left + rel]) - target) * 1000.0)
    return {
        "matched": len(residuals),
        "fraction": len(residuals) / len(midi_times) if midi_times else 0.0,
        "residualsMs": residuals,
        "threshold": threshold,
    }


def evaluate_alignment(midi_times, samples):
    midi = list(midi_times)
    blockers = []
    if len(midi) < MINIMUM_MIDI_ONSET_GROUPS:
        return {"status": "abstained", "blockers": ["MINIMUM_MIDI_ONSET_GROUPS_NOT_MET"], "midiOnsetGroups": len(midi)}

    env_times, flux = onset_envelope(samples)
    if not np.any(flux > 0):
        return {"status": "abstained", "blockers": ["AUDIO_ONSET_ENVELOPE_EMPTY"], "midiOnsetGroups": len(midi)}

    lag_ms = int(best_lag_ms(midi, env_times, flux))
    strata_lags = deterministic_strata_lags(midi, env_times, flux)
    median_strata = float(np.median(strata_lags))
    lag_mad_ms = float(np.median(np.abs(np.asarray(strata_lags, dtype=np.float64) - median_strata)))
    matches = local_peak_matches(midi, lag_ms, env_times, flux)
    residuals = matches["residualsMs"]
    median_residual_ms = float(np.median(residuals)) if residuals else None

    if abs(lag_ms) > MAXIMUM_ABSOLUTE_APPLIED_CORRECTION_MS:
        blockers.append("MAXIMUM_ABSOLUTE_APPLIED_CORRECTION_EXCEEDED")
    if matches["fraction"] < MINIMUM_MATCHED_FRACTION:
        blockers.append("MINIMUM_MATCHED_FRACTION_NOT_MET")
    if median_residual_ms is None or median_residual_ms > MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_MS:
        blockers.append("MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_EXCEEDED")
    if lag_mad_ms > MAXIMUM_BOOTSTRAP_LAG_MAD_MS:
        blockers.append("MAXIMUM_BOOTSTRAP_LAG_MAD_EXCEEDED")

    return {
        "status": "complete" if not blockers else "abstained",
        "blockers": sorted(set(blockers)),
        "midiOnsetGroups": len(midi),
        "appliedCorrectionMs": lag_ms,
        "deterministicStrataLagMs": strata_lags,
        "bootstrapLagMedianMs": median_strata,
        "bootstrapLagMadMs": lag_mad_ms,
        "matchedOnsetGroups": matches["matched"],
        "matchedFraction": matches["fraction"],
        "medianAbsoluteResidualMs": median_residual_ms,
        "peakStrengthThreshold": matches["threshold"],
        "audioEnvelope": {
            "sampleRate": SAMPLE_RATE,
            "windowMs": WINDOW_MS,
            "hopMs": HOP_MS,
            "positiveQuantileThreshold": PEAK_STRENGTH_POSITIVE_QUANTILE,
        },
    }


def performance_key(path: Path):
    stem = path.stem
    parent = path.parent.name
    for prefix in [f"{parent}_", "midi_", "directinput_", "micamp_", "ego_", "exo_"]:
        if stem.lower().startswith(prefix.lower()) and len(stem) > len(prefix):
            return stem[len(prefix):]
    return stem


def visible_files(root: Path):
    out = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if "__MACOSX" in rel.parts or path.name == ".DS_Store" or path.name.startswith("._"):
            continue
        out.append(path)
    return sorted(out)


def ffmpeg_version():
    result = subprocess.run(["ffmpeg", "-version"], check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return result.stdout.splitlines()[0].strip()


def align_archive(root: Path, archive: str, performer: str, category: str, script_sha256: str):
    files = visible_files(root)
    midis = {}
    captures = {}
    for path in files:
        key = performance_key(path)
        suffix = path.suffix.lower()
        if suffix in {".mid", ".midi"}:
            midis.setdefault(key, []).append(path)
        elif suffix in {".wav", ".mp3"}:
            view = path.parent.name
            captures.setdefault(key, {}).setdefault(view, []).append(path)

    results = []
    for key in sorted(set(midis) | set(captures)):
        midi_paths = midis.get(key, [])
        if len(midi_paths) != 1:
            results.append({"performanceKey": key, "status": "abstained", "blockers": ["EXPECTED_EXACTLY_ONE_MIDI_FILE"], "midiFileCount": len(midi_paths)})
            continue
        midi_meta = parse_midi_onset_groups(midi_paths[0])
        view_results = []
        for view in sorted(captures.get(key, {})):
            paths = captures[key][view]
            if len(paths) != 1:
                view_results.append({"captureView": view, "status": "abstained", "blockers": ["EXPECTED_EXACTLY_ONE_CAPTURE_FILE"], "fileCount": len(paths)})
                continue
            path = paths[0]
            try:
                outcome = evaluate_alignment(midi_meta["onsetGroupSeconds"], decode_audio(path))
                outcome.update({"captureView": view, "sourceSuffix": path.suffix.lower()})
            except Exception as exc:
                outcome = {"captureView": view, "sourceSuffix": path.suffix.lower(), "status": "abstained", "blockers": ["AUDIO_DECODE_OR_ALIGNMENT_ERROR"], "error": str(exc)[:500]}
            view_results.append(outcome)
        results.append({
            "performanceKey": key,
            "midi": {"format": midi_meta["format"], "ppq": midi_meta["ppq"], "stringTrackNames": midi_meta["stringTrackNames"], "onsetGroupCount": len(midi_meta["onsetGroupSeconds"])},
            "captureAlignments": view_results,
        })

    flat = [view for result in results for view in result.get("captureAlignments", [])]
    return {
        "schema": "astra-guitar-techs-development-alignment-archive-v1",
        "archive": archive,
        "performer": performer,
        "category": category,
        "scriptSha256": script_sha256,
        "runtime": {"python": sys.version.split()[0], "numpy": np.__version__, "ffmpeg": ffmpeg_version()},
        "policy": {
            "sampleRate": SAMPLE_RATE, "windowMs": WINDOW_MS, "hopMs": HOP_MS,
            "lagSearchMs": [LAG_MIN_MS, LAG_MAX_MS], "lagStepMs": LAG_STEP_MS,
            "matchToleranceMs": MATCH_TOLERANCE_MS, "minimumMidiOnsetGroups": MINIMUM_MIDI_ONSET_GROUPS,
            "minimumMatchedFraction": MINIMUM_MATCHED_FRACTION,
            "maximumMedianAbsoluteResidualMs": MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_MS,
            "bootstrapStrata": BOOTSTRAP_STRATA, "maximumBootstrapLagMadMs": MAXIMUM_BOOTSTRAP_LAG_MAD_MS,
            "maximumAbsoluteAppliedCorrectionMs": MAXIMUM_ABSOLUTE_APPLIED_CORRECTION_MS,
            "peakStrengthPositiveQuantile": PEAK_STRENGTH_POSITIVE_QUANTILE,
            "failureAction": "exclude-recording-session-plus-capture-path-and-abstain",
        },
        "performanceResults": results,
        "summary": {
            "performanceCount": len(results),
            "captureAlignmentCount": len(flat),
            "completeCaptureAlignments": sum(view.get("status") == "complete" for view in flat),
            "abstainedCaptureAlignments": sum(view.get("status") != "complete" for view in flat),
        },
        "guards": {"p3Opened": False, "modelImported": False, "tabcnnFeaturesComputed": False, "trainingRun": False, "customerDeliveryEligible": False},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--archive", required=True)
    parser.add_argument("--performer", required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--script-sha256", required=True)
    args = parser.parse_args()
    this_sha = sha256(Path(__file__))
    if this_sha != args.script_sha256:
        raise SystemExit("alignment script SHA256 mismatch")
    report = align_archive(Path(args.root), args.archive, args.performer, args.category, this_sha)
    output = Path(args.output)
    if output.exists():
        raise SystemExit("refusing to overwrite output")
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
