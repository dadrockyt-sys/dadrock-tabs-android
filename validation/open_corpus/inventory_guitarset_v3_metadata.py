#!/usr/bin/env python3
"""Metadata/path-only GuitarSet v1.1.0 inventory for V3.

This tool intentionally does not extract/decode audio and does not read JAMS member
contents. It hashes the opaque ZIP archives and inspects ZIP central-directory metadata
(path names/sizes/CRC) only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

AUDIO_OFFICIAL_MD5 = "275966d6610ac34999b58426beb119c3"
ANNOTATION_OFFICIAL_MD5 = "b39b78e63d3446f2e54ddb7a54df9b10"
PLAYERS = ("00", "01", "02", "03", "04", "05")
DEV_PLAYERS = ("02", "04", "05")
EVAL_PLAYERS = ("00", "01", "03")
KNOWN_ANOMALIES = (
    "04_BN3-154-E_comp",
    "04_Jazz1-200-B_comp",
    "02_Funk2-119-G_comp",
)


def file_digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def central_directory_entries(path: Path, suffix: str) -> list[zipfile.ZipInfo]:
    with zipfile.ZipFile(path, "r") as archive:
        return sorted(
            [entry for entry in archive.infolist() if not entry.is_dir() and entry.filename.lower().endswith(suffix)],
            key=lambda entry: entry.filename,
        )


def audio_track_stem(filename: str) -> str:
    name = Path(filename).name
    if not name.lower().endswith(".wav"):
        raise ValueError(f"not a WAV path: {filename}")
    stem = name[:-4]
    if stem.endswith("_mic"):
        stem = stem[:-4]
    return stem


def annotation_track_stem(filename: str) -> str:
    name = Path(filename).name
    if not name.lower().endswith(".jams"):
        raise ValueError(f"not a JAMS path: {filename}")
    return name[:-5]


def player_from_stem(stem: str) -> str:
    if len(stem) < 3 or stem[2] != "_":
        raise ValueError(f"unexpected GuitarSet stem: {stem}")
    return stem[:2]


def metadata_record(entry: zipfile.ZipInfo) -> dict[str, object]:
    return {
        "path": entry.filename,
        "compressedSize": entry.compress_size,
        "uncompressedSize": entry.file_size,
        "crc32": f"{entry.CRC:08x}",
    }


def inventory(audio_zip: Path, annotation_zip: Path, *, verify_official_md5: bool = True) -> dict[str, object]:
    audio_md5 = file_digest(audio_zip, "md5")
    annotation_md5 = file_digest(annotation_zip, "md5")
    if verify_official_md5:
        if audio_md5 != AUDIO_OFFICIAL_MD5:
            raise SystemExit(f"audio MD5 mismatch: {audio_md5}")
        if annotation_md5 != ANNOTATION_OFFICIAL_MD5:
            raise SystemExit(f"annotation MD5 mismatch: {annotation_md5}")

    audio_entries = central_directory_entries(audio_zip, ".wav")
    annotation_entries = central_directory_entries(annotation_zip, ".jams")

    audio_stems = [audio_track_stem(entry.filename) for entry in audio_entries]
    annotation_stems = [annotation_track_stem(entry.filename) for entry in annotation_entries]

    if len(audio_stems) != len(set(audio_stems)):
        raise SystemExit("duplicate normalized audio track stems")
    if len(annotation_stems) != len(set(annotation_stems)):
        raise SystemExit("duplicate annotation track stems")
    if len(audio_stems) != 360:
        raise SystemExit(f"expected 360 microphone WAV tracks, found {len(audio_stems)}")
    if len(annotation_stems) != 360:
        raise SystemExit(f"expected 360 JAMS tracks, found {len(annotation_stems)}")
    if set(audio_stems) != set(annotation_stems):
        missing_audio = sorted(set(annotation_stems) - set(audio_stems))
        missing_annotation = sorted(set(audio_stems) - set(annotation_stems))
        raise SystemExit(
            "mic/JAMS stem mismatch: "
            f"missingAudio={missing_audio[:10]} missingAnnotation={missing_annotation[:10]}"
        )

    counts = Counter(player_from_stem(stem) for stem in annotation_stems)
    if set(counts) != set(PLAYERS):
        raise SystemExit(f"unexpected player IDs: {sorted(counts)}")
    for player in PLAYERS:
        if counts[player] != 60:
            raise SystemExit(f"player {player} expected 60 tracks, found {counts[player]}")

    anomaly_missing = sorted(set(KNOWN_ANOMALIES) - set(annotation_stems))
    if anomaly_missing:
        raise SystemExit(f"predeclared anomaly stems missing: {anomaly_missing}")
    if any(player_from_stem(stem) not in DEV_PLAYERS for stem in KNOWN_ANOMALIES):
        raise SystemExit("predeclared anomaly escaped development split")

    dev_tracks = sorted(stem for stem in annotation_stems if player_from_stem(stem) in DEV_PLAYERS)
    eval_tracks = sorted(stem for stem in annotation_stems if player_from_stem(stem) in EVAL_PLAYERS)
    if len(dev_tracks) != 180 or len(eval_tracks) != 180:
        raise SystemExit(f"split count mismatch: dev={len(dev_tracks)} eval={len(eval_tracks)}")

    return {
        "schema": "dadrock.tabs.open-corpus.guitarset-v3-metadata-inventory.v1",
        "status": "GUITARSET_V3_METADATA_INVENTORY_PASS",
        "source": {
            "dataset": "GuitarSet",
            "version": "1.1.0",
            "zenodoRecord": "3371780",
            "doi": "10.5281/zenodo.3371780",
        },
        "archives": {
            "audioMonoMic": {
                "filename": audio_zip.name,
                "sizeBytes": audio_zip.stat().st_size,
                "officialMd5": AUDIO_OFFICIAL_MD5,
                "observedMd5": audio_md5,
                "sha256": file_digest(audio_zip, "sha256"),
                "wavEntryCount": len(audio_entries),
            },
            "annotation": {
                "filename": annotation_zip.name,
                "sizeBytes": annotation_zip.stat().st_size,
                "officialMd5": ANNOTATION_OFFICIAL_MD5,
                "observedMd5": annotation_md5,
                "sha256": file_digest(annotation_zip, "sha256"),
                "jamsEntryCount": len(annotation_entries),
            },
        },
        "pairing": {
            "uniqueTrackCount": len(annotation_stems),
            "exactNormalizedStemPairing": True,
            "players": {player: counts[player] for player in PLAYERS},
            "developmentPlayers": list(DEV_PLAYERS),
            "evaluationPlayers": list(EVAL_PLAYERS),
            "developmentTrackCount": len(dev_tracks),
            "evaluationTrackCount": len(eval_tracks),
            "knownAnomalyTracks": list(KNOWN_ANOMALIES),
        },
        "paths": {
            "audioWavEntries": [metadata_record(entry) for entry in audio_entries],
            "annotationJamsEntries": [metadata_record(entry) for entry in annotation_entries],
        },
        "safety": {
            "zipCentralDirectoryOnly": True,
            "audioDecoded": False,
            "jamsMemberContentsRead": False,
            "jamsNoteEventsRead": 0,
            "basicPitchInferenceCalls": 0,
            "guitarSetProspectiveEvaluationScoreCalls": 0,
            "v168ReferenceFacingScoreCalls": 0,
            "goatRestrictedBytesRead": False,
            "gpuCudaModalUsed": False,
        },
    }


def make_self_test_zip(path: Path, names: list[str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in names:
            archive.writestr(name, b"")


def self_test() -> None:
    stems: list[str] = []
    for player in PLAYERS:
        for i in range(60):
            mode = "comp" if i < 30 else "solo"
            stems.append(f"{player}_Synthetic{i:02d}-120-C_{mode}")
    replacements = {
        "02_Synthetic00-120-C_comp": "02_Funk2-119-G_comp",
        "04_Synthetic00-120-C_comp": "04_BN3-154-E_comp",
        "04_Synthetic01-120-C_comp": "04_Jazz1-200-B_comp",
    }
    stems = [replacements.get(stem, stem) for stem in stems]

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        audio = root / "audio_mono-mic.zip"
        annotation = root / "annotation.zip"
        make_self_test_zip(audio, [f"audio_mono-mic/{stem}_mic.wav" for stem in stems])
        make_self_test_zip(annotation, [f"annotation/{stem}.jams" for stem in stems])
        report = inventory(audio, annotation, verify_official_md5=False)
        assert report["status"] == "GUITARSET_V3_METADATA_INVENTORY_PASS"
        assert report["pairing"]["evaluationTrackCount"] == 180
        assert report["safety"]["jamsNoteEventsRead"] == 0
        print(json.dumps({
            "status": "GUITARSET_V3_METADATA_INVENTORY_SELF_TEST_PASS",
            "trackCount": report["pairing"]["uniqueTrackCount"],
            "jamsNoteEventsRead": 0,
            "basicPitchInferenceCalls": 0,
            "v168ReferenceFacingScoreCalls": 0,
        }, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-zip", type=Path)
    parser.add_argument("--annotation-zip", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.audio_zip or not args.annotation_zip or not args.output:
        parser.error("--audio-zip, --annotation-zip and --output are required unless --self-test")

    report = inventory(args.audio_zip, args.annotation_zip)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "audioSha256": report["archives"]["audioMonoMic"]["sha256"],
        "annotationSha256": report["archives"]["annotation"]["sha256"],
        "trackCount": report["pairing"]["uniqueTrackCount"],
        "developmentTrackCount": report["pairing"]["developmentTrackCount"],
        "evaluationTrackCount": report["pairing"]["evaluationTrackCount"],
        "jamsNoteEventsRead": 0,
        "basicPitchInferenceCalls": 0,
        "guitarSetProspectiveEvaluationScoreCalls": 0,
        "v168ReferenceFacingScoreCalls": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
