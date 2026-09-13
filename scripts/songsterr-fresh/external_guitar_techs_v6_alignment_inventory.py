#!/usr/bin/env python3
"""Reference-blind Guitar-TECHS V6 inventory/alignment audit.

This tool is intentionally forbidden from importing or invoking Basic Pitch or
V6 corroboration. It implements the frozen metadata/alignment audit in
SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_PREREGISTRATION.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import tempfile
import zipfile
from collections import Counter, defaultdict, deque
from pathlib import Path, PurePosixPath

import mido
import numpy as np
import soundfile as sf

CONTRACT = "songsterr-fresh-guitar-techs-v6-alignment-inventory-v1"
ZENODO_RECORD = "14963133"
ZENODO_VERSION = "v1"
FRAME_SAMPLES = 2048
HOP_SAMPLES = 256
ALIGNMENT_SEARCH_SECONDS = 0.150
MIDI_GAUSSIAN_SIGMA_SECONDS = 0.010

EXPECTED_PACKAGES = {
    "P1_chords.zip": "be9ef8bbdceb1912d565254e607a6d94",
    "P1_scales.zip": "9c0b98e8fb42a522df727ea8bf545e4f",
    "P1_singlenotes.zip": "ca0c4674dde3805574685a313f7c39eb",
    "P1_techniques.zip": "18634a41a6db5a8de10d07eb3122a872",
    "P2_chords.zip": "eb6f74dd19162237189281688ad7ad2e",
    "P2_scales.zip": "96664853872f51e5f8aa4447313b7cf5",
    "P2_singlenotes.zip": "40fbf03d8b04bb2cf42df20f36dc2254",
    "P2_techniques.zip": "f4189251ce50be25f06a173b2c2bba00",
    "P3_music.zip": "071ba80aecf00f4a31fbd167b3f22198",
}

PACKAGING_NAMES = {".DS_Store"}


class AuditError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def md5_file(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.md5()  # nosec - dataset identity is published as MD5
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def is_packaging_entry(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        "__MACOSX" in path.parts
        or path.name in PACKAGING_NAMES
        or path.name.startswith("._")
        or not path.name
    )


def classify_entry(name: str) -> str:
    normalized = name.replace("\\", "/")
    lowered = normalized.lower()
    if is_packaging_entry(normalized):
        return "packaging"
    if "/audio/directinput/" in lowered and lowered.endswith(".wav"):
        return "directinput_wav"
    if "/audio/micamp/" in lowered and lowered.endswith(".wav"):
        return "micamp_wav"
    if "/video/ego/" in lowered and lowered.endswith((".wav", ".mp3", ".flac", ".m4a")):
        return "ego_audio"
    if "/video/exo/" in lowered and lowered.endswith((".wav", ".mp3", ".flac", ".m4a")):
        return "exo_audio"
    if "/midi/" in lowered and lowered.endswith((".mid", ".midi")):
        return "midi"
    return "other"


def semantic_key(name: str, prefix: str) -> str:
    stem = PurePosixPath(name).stem
    if not stem.startswith(prefix):
        raise AuditError(f"EXPECTED_PREFIX_MISSING:{prefix}:{name}")
    key = stem[len(prefix) :]
    if not key:
        raise AuditError(f"EMPTY_SEMANTIC_KEY:{name}")
    return key


def safe_extract_member(archive: zipfile.ZipFile, member: zipfile.ZipInfo, root: Path) -> Path:
    pure = PurePosixPath(member.filename)
    if pure.is_absolute() or ".." in pure.parts:
        raise AuditError(f"UNSAFE_ZIP_PATH:{member.filename}")
    target = root.joinpath(*pure.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    with archive.open(member, "r") as src, target.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)
    return target


def build_tempo_map(midi_file: mido.MidiFile) -> list[tuple[int, int]]:
    events: list[tuple[int, int, int, int]] = []
    for track_index, track in enumerate(midi_file.tracks):
        tick = 0
        for order, message in enumerate(track):
            tick += int(message.time)
            if message.type == "set_tempo":
                events.append((tick, track_index, order, int(message.tempo)))
    events.sort(key=lambda row: (row[0], row[1], row[2]))
    collapsed: list[tuple[int, int]] = [(0, 500000)]
    for tick, _track, _order, tempo in events:
        if tick == collapsed[-1][0]:
            collapsed[-1] = (tick, tempo)
        else:
            collapsed.append((tick, tempo))
    return collapsed


def tick_to_seconds(tick: int, ticks_per_beat: int, tempo_map: list[tuple[int, int]]) -> float:
    if ticks_per_beat <= 0:
        raise AuditError("SMPTE_TIME_DIVISION_NOT_SUPPORTED")
    target = int(tick)
    seconds = 0.0
    last_tick = 0
    tempo = 500000
    for change_tick, change_tempo in tempo_map:
        if change_tick > target:
            break
        if change_tick > last_tick:
            seconds += mido.tick2second(change_tick - last_tick, ticks_per_beat, tempo)
            last_tick = change_tick
        tempo = int(change_tempo)
    if target > last_tick:
        seconds += mido.tick2second(target - last_tick, ticks_per_beat, tempo)
    return float(seconds)


def parse_midi(path: Path) -> dict:
    midi_file = mido.MidiFile(path)
    if midi_file.ticks_per_beat <= 0:
        raise AuditError("SMPTE_TIME_DIVISION_NOT_SUPPORTED")
    tempo_map = build_tempo_map(midi_file)

    track_rows = []
    all_note_edges: list[dict] = []
    tempo_event_count = 0
    channels = set()
    for track_index, track in enumerate(midi_file.tracks):
        tick = 0
        track_note_edges = 0
        track_channels = set()
        for order, message in enumerate(track):
            tick += int(message.time)
            if message.type == "set_tempo":
                tempo_event_count += 1
            if message.type in {"note_on", "note_off"}:
                channel = int(getattr(message, "channel", 0))
                note = int(message.note)
                velocity = int(getattr(message, "velocity", 0))
                edge_type = "on" if message.type == "note_on" and velocity > 0 else "off"
                all_note_edges.append({
                    "tick": tick,
                    "track": track_index,
                    "order": order,
                    "channel": channel,
                    "note": note,
                    "velocity": velocity,
                    "edge": edge_type,
                })
                track_note_edges += 1
                track_channels.add(channel)
                channels.add(channel)
        track_rows.append({
            "trackIndex": track_index,
            "messageCount": len(track),
            "noteEdgeCount": track_note_edges,
            "channels": sorted(track_channels),
        })

    all_note_edges.sort(key=lambda row: (row["tick"], row["track"], row["order"]))
    active: dict[tuple[int, int, int], deque[dict]] = defaultdict(deque)
    paired_events = []
    unmatched_off = []
    same_key_overlap_count = 0
    note_on_ticks = []

    for edge in all_note_edges:
        key = (edge["track"], edge["channel"], edge["note"])
        if edge["edge"] == "on":
            if active[key]:
                same_key_overlap_count += 1
            active[key].append(edge)
            note_on_ticks.append(edge["tick"])
        else:
            if not active[key]:
                unmatched_off.append(edge)
                continue
            onset = active[key].popleft()
            paired_events.append({
                "track": onset["track"],
                "channel": onset["channel"],
                "midi": onset["note"],
                "onsetTick": onset["tick"],
                "offsetTick": edge["tick"],
                "onsetSeconds": tick_to_seconds(onset["tick"], midi_file.ticks_per_beat, tempo_map),
                "offsetSeconds": tick_to_seconds(edge["tick"], midi_file.ticks_per_beat, tempo_map),
            })

    unmatched_on = [row for queue in active.values() for row in queue]
    paired_events.sort(key=lambda row: (row["onsetSeconds"], row["track"], row["channel"], row["midi"]))
    distinct_onsets = sorted({tick_to_seconds(tick, midi_file.ticks_per_beat, tempo_map) for tick in note_on_ticks})
    pitches = [row["midi"] for row in paired_events]

    return {
        "format": int(midi_file.type),
        "trackCount": len(midi_file.tracks),
        "ticksPerBeat": int(midi_file.ticks_per_beat),
        "tempoEventCount": tempo_event_count,
        "tempoMap": [{"tick": tick, "tempoMicrosecondsPerBeat": tempo} for tick, tempo in tempo_map],
        "channels": sorted(channels),
        "tracks": track_rows,
        "noteEdgeCount": len(all_note_edges),
        "pairedEventCount": len(paired_events),
        "unmatchedNoteOffCount": len(unmatched_off),
        "unmatchedNoteOnCount": len(unmatched_on),
        "sameKeyOverlapCount": same_key_overlap_count,
        "pitchMin": min(pitches) if pitches else None,
        "pitchMax": max(pitches) if pitches else None,
        "distinctOnsetCount": len(distinct_onsets),
        "distinctOnsetSeconds": distinct_onsets,
    }


def next_power_of_two(value: int) -> int:
    return 1 << (int(value) - 1).bit_length()


def positive_spectral_flux(audio: np.ndarray, sample_rate: int) -> tuple[np.ndarray, np.ndarray]:
    mono = np.asarray(audio, dtype=np.float64)
    if mono.ndim != 1 or mono.size < FRAME_SAMPLES or not np.all(np.isfinite(mono)):
        raise AuditError("FINITE_AUDIO_WITH_FULL_FRAME_REQUIRED")
    fft_size = next_power_of_two(FRAME_SAMPLES)
    window = np.hanning(FRAME_SAMPLES)
    starts = np.arange(0, mono.size - FRAME_SAMPLES + 1, HOP_SAMPLES, dtype=np.int64)
    novelty = np.zeros(starts.size, dtype=np.float64)
    previous = None
    for index, start in enumerate(starts):
        frame = mono[start : start + FRAME_SAMPLES]
        frame = (frame - float(np.mean(frame))) * window
        magnitude = np.abs(np.fft.rfft(frame, n=fft_size))
        if previous is not None:
            novelty[index] = float(np.sum(np.maximum(0.0, magnitude - previous)))
        previous = magnitude
    norm = float(np.linalg.norm(novelty))
    if math.isfinite(norm) and norm > 0.0:
        novelty /= norm
    # Freeze frame-center timing before observing dataset alignment values.
    centers_seconds = (starts.astype(np.float64) + FRAME_SAMPLES / 2.0) / float(sample_rate)
    return novelty, centers_seconds


def midi_onset_envelope(onsets: list[float], frame_centers: np.ndarray, sample_rate: int) -> np.ndarray:
    envelope = np.zeros(frame_centers.size, dtype=np.float64)
    if not onsets or frame_centers.size == 0:
        return envelope
    first_center = float(frame_centers[0])
    hop_seconds = HOP_SAMPLES / float(sample_rate)
    for onset in sorted(set(float(value) for value in onsets)):
        position = (onset - first_center) / hop_seconds
        index = int(math.floor(position + 0.5))
        if 0 <= index < envelope.size:
            envelope[index] = 1.0
    sigma_hops = MIDI_GAUSSIAN_SIGMA_SECONDS / hop_seconds
    radius = max(1, int(math.ceil(4.0 * sigma_hops)))
    x = np.arange(-radius, radius + 1, dtype=np.float64)
    kernel = np.exp(-0.5 * np.square(x / sigma_hops))
    kernel /= float(np.sum(kernel))
    envelope = np.convolve(envelope, kernel, mode="same")
    norm = float(np.linalg.norm(envelope))
    if math.isfinite(norm) and norm > 0.0:
        envelope /= norm
    return envelope


def cosine_for_lag(audio_env: np.ndarray, midi_env: np.ndarray, lag_hops: int) -> float:
    if lag_hops >= 0:
        if lag_hops >= audio_env.size:
            return float("-inf")
        audio_slice = audio_env[lag_hops:]
        midi_slice = midi_env[: midi_env.size - lag_hops] if lag_hops else midi_env
    else:
        amount = -lag_hops
        if amount >= audio_env.size:
            return float("-inf")
        audio_slice = audio_env[: audio_env.size - amount]
        midi_slice = midi_env[amount:]
    if audio_slice.size == 0 or midi_slice.size != audio_slice.size:
        return float("-inf")
    denominator = float(np.linalg.norm(audio_slice) * np.linalg.norm(midi_slice))
    if not math.isfinite(denominator) or denominator <= 0.0:
        return float("-inf")
    value = float(np.dot(audio_slice, midi_slice) / denominator)
    return value if math.isfinite(value) else float("-inf")


def estimate_constant_lag(audio: np.ndarray, sample_rate: int, onsets: list[float]) -> dict:
    novelty, centers = positive_spectral_flux(audio, sample_rate)
    midi_env = midi_onset_envelope(onsets, centers, sample_rate)
    if float(np.linalg.norm(novelty)) <= 0.0:
        return {"status": "INSUFFICIENT_ZERO_AUDIO_NOVELTY"}
    if float(np.linalg.norm(midi_env)) <= 0.0:
        return {"status": "INSUFFICIENT_ZERO_MIDI_ONSET_ENVELOPE"}

    hop_seconds = HOP_SAMPLES / float(sample_rate)
    maximum_hops = int(math.floor(ALIGNMENT_SEARCH_SECONDS / hop_seconds + 1e-12))
    rows = []
    for lag_hops in range(-maximum_hops, maximum_hops + 1):
        rows.append((lag_hops, cosine_for_lag(novelty, midi_env, lag_hops)))
    finite = [(lag, value) for lag, value in rows if math.isfinite(value)]
    if not finite:
        return {"status": "INSUFFICIENT_NO_FINITE_CORRELATIONS"}
    best_value = max(value for _lag, value in finite)
    winners = [lag for lag, value in finite if value == best_value]
    if len(winners) != 1:
        return {"status": "AMBIGUOUS_EXACT_TIE", "bestCorrelation": best_value, "winnerHops": winners}
    best_lag = winners[0]
    separated = [value for lag, value in finite if abs(lag - best_lag) > 2]
    next_best = max(separated) if separated else None
    return {
        "status": "OK",
        "lagHops": int(best_lag),
        "lagSecondsAddedToMidi": float(best_lag * hop_seconds),
        "bestCorrelation": float(best_value),
        "nextBestCorrelationOutsidePlusMinus2Hops": None if next_best is None else float(next_best),
        "hopSeconds": hop_seconds,
        "searchMaximumHops": maximum_hops,
        "frameTimingAnchor": "center",
    }


def inspect_wav_and_alignment(path: Path, onsets: list[float]) -> tuple[dict, dict]:
    info = sf.info(path)
    audio, sample_rate = sf.read(path, dtype="float64", always_2d=True)
    if audio.ndim != 2 or audio.shape[0] == 0 or not np.all(np.isfinite(audio)):
        raise AuditError("FINITE_NONEMPTY_WAV_REQUIRED")
    mono = np.mean(audio, axis=1, dtype=np.float64)
    wav = {
        "sampleRate": int(sample_rate),
        "channels": int(audio.shape[1]),
        "frames": int(audio.shape[0]),
        "durationSeconds": float(audio.shape[0] / float(sample_rate)),
        "format": str(info.format),
        "subtype": str(info.subtype),
    }
    alignment = estimate_constant_lag(mono, int(sample_rate), onsets)
    return wav, alignment


def pair_entries(entries: list[zipfile.ZipInfo]) -> tuple[dict[str, zipfile.ZipInfo], dict[str, zipfile.ZipInfo], list[str], list[str]]:
    di_by_key: dict[str, list[zipfile.ZipInfo]] = defaultdict(list)
    midi_by_key: dict[str, list[zipfile.ZipInfo]] = defaultdict(list)
    for entry in entries:
        kind = classify_entry(entry.filename)
        if kind == "directinput_wav":
            di_by_key[semantic_key(entry.filename, "directinput_")].append(entry)
        elif kind == "midi":
            midi_by_key[semantic_key(entry.filename, "midi_")].append(entry)
    duplicate_di = sorted(key for key, rows in di_by_key.items() if len(rows) != 1)
    duplicate_midi = sorted(key for key, rows in midi_by_key.items() if len(rows) != 1)
    if duplicate_di or duplicate_midi:
        raise AuditError(f"AMBIGUOUS_DUPLICATE_BASENAMES:DI={duplicate_di}:MIDI={duplicate_midi}")
    return (
        {key: rows[0] for key, rows in di_by_key.items()},
        {key: rows[0] for key, rows in midi_by_key.items()},
        duplicate_di,
        duplicate_midi,
    )


def audit_archive(archive_path: Path, expected_md5: str, package_name: str) -> dict:
    if package_name not in EXPECTED_PACKAGES:
        raise AuditError(f"UNKNOWN_PACKAGE:{package_name}")
    frozen_md5 = EXPECTED_PACKAGES[package_name]
    if expected_md5 != frozen_md5:
        raise AuditError(f"EXPECTED_MD5_ARGUMENT_CHANGED:{expected_md5}!={frozen_md5}")
    actual_md5 = md5_file(archive_path)
    if actual_md5 != frozen_md5:
        raise AuditError(f"ARCHIVE_MD5_MISMATCH:{actual_md5}!={frozen_md5}")

    with zipfile.ZipFile(archive_path, "r") as archive:
        entries = [entry for entry in archive.infolist() if not entry.is_dir()]
        counts = Counter(classify_entry(entry.filename) for entry in entries)
        di_by_key, midi_by_key, _duplicate_di, _duplicate_midi = pair_entries(entries)
        all_keys = sorted(set(di_by_key) | set(midi_by_key))
        unpaired_di = sorted(set(di_by_key) - set(midi_by_key))
        unpaired_midi = sorted(set(midi_by_key) - set(di_by_key))
        paired_keys = sorted(set(di_by_key) & set(midi_by_key))

        pairs = []
        with tempfile.TemporaryDirectory(prefix="guitar-techs-v6-") as tmp:
            root = Path(tmp)
            for index, key in enumerate(paired_keys, start=1):
                di_entry = di_by_key[key]
                midi_entry = midi_by_key[key]
                di_path = safe_extract_member(archive, di_entry, root)
                midi_path = safe_extract_member(archive, midi_entry, root)
                midi = parse_midi(midi_path)
                wav, alignment = inspect_wav_and_alignment(di_path, midi["distinctOnsetSeconds"])
                pairs.append({
                    "semanticKey": key,
                    "diEntry": di_entry.filename,
                    "midiEntry": midi_entry.filename,
                    "diSha256": sha256_file(di_path),
                    "midiSha256": sha256_file(midi_path),
                    "wav": wav,
                    "midi": {key2: value for key2, value in midi.items() if key2 != "distinctOnsetSeconds"},
                    "alignment": alignment,
                })
                di_path.unlink(missing_ok=True)
                midi_path.unlink(missing_ok=True)
                print(f"GUITAR_TECHS_AUDIT_PAIR_COMPLETE {index}/{len(paired_keys)} {package_name} {key}", flush=True)

    identity_rows = [
        {
            "semanticKey": row["semanticKey"],
            "diEntry": row["diEntry"],
            "midiEntry": row["midiEntry"],
            "diSha256": row["diSha256"],
            "midiSha256": row["midiSha256"],
        }
        for row in pairs
    ]
    pairing_manifest_sha = sha256_bytes(canonical_json(identity_rows).encode("utf-8"))
    lag_rows = [
        {
            "semanticKey": row["semanticKey"],
            "status": row["alignment"]["status"],
            "lagHops": row["alignment"].get("lagHops"),
            "lagSecondsAddedToMidi": row["alignment"].get("lagSecondsAddedToMidi"),
        }
        for row in pairs
    ]
    lag_manifest_sha = sha256_bytes(canonical_json(lag_rows).encode("utf-8"))

    midi_anomaly_totals = {
        "unmatchedNoteOffCount": sum(row["midi"]["unmatchedNoteOffCount"] for row in pairs),
        "unmatchedNoteOnCount": sum(row["midi"]["unmatchedNoteOnCount"] for row in pairs),
        "sameKeyOverlapCount": sum(row["midi"]["sameKeyOverlapCount"] for row in pairs),
    }
    paired_event_count = sum(row["midi"]["pairedEventCount"] for row in pairs)
    pitches = [
        pitch
        for row in pairs
        for pitch in (row["midi"]["pitchMin"], row["midi"]["pitchMax"])
        if pitch is not None
    ]

    return {
        "contract": CONTRACT,
        "zenodoRecord": ZENODO_RECORD,
        "zenodoVersion": ZENODO_VERSION,
        "package": package_name,
        "archiveMd5Expected": frozen_md5,
        "archiveMd5Actual": actual_md5,
        "archiveMd5Verified": True,
        "archiveSha256": sha256_file(archive_path),
        "entryCounts": dict(sorted(counts.items())),
        "semanticKeyCount": len(all_keys),
        "pairedDiMidiCount": len(paired_keys),
        "unpairedDiKeys": unpaired_di,
        "unpairedMidiKeys": unpaired_midi,
        "pairingManifestSha256": pairing_manifest_sha,
        "alignmentLagManifestSha256": lag_manifest_sha,
        "pairedReferenceEventCount": paired_event_count,
        "referencePitchMin": min(pitches) if pitches else None,
        "referencePitchMax": max(pitches) if pitches else None,
        "midiAnomalyTotals": midi_anomaly_totals,
        "pairs": pairs,
        "policyBoundary": {
            "basicPitchInvoked": False,
            "v6Invoked": False,
            "correctnessComputed": False,
            "protectedSongUsed": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", required=True)
    parser.add_argument("--package-name", required=True)
    parser.add_argument("--expected-md5", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit_archive(Path(args.archive), args.expected_md5, args.package_name)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(result) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": result["contract"],
        "package": result["package"],
        "pairedDiMidiCount": result["pairedDiMidiCount"],
        "pairedReferenceEventCount": result["pairedReferenceEventCount"],
        "pairingManifestSha256": result["pairingManifestSha256"],
        "alignmentLagManifestSha256": result["alignmentLagManifestSha256"],
        "output": str(output),
        "outputSha256": sha256_file(output),
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
