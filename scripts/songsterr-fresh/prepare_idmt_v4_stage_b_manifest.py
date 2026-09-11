#!/usr/bin/env python3
"""Prepare the non-scoring IDMT V4 Stage B evaluation manifest.

This tool is intentionally model-free. It verifies the frozen Stage A archive/report,
derives the exact mechanically eligible WAV/XML population, and records annotation
value statistics without comparing annotations to any estimate.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import math
import os
import tempfile
import wave
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

CONTRACT = "songsterr-fresh-idmt-v4-stage-b-manifest-v1"
EXPECTED_ARCHIVE_NAME = "IDMT-SMT-GUITAR_V2.zip"
EXPECTED_ARCHIVE_MD5 = "06796e08731bccffaed6ae59361486e4"
EXPECTED_ARCHIVE_SHA256 = "02816258252538603c051054219cb4bba1c0ae8c9d0a3ca5418dfc951eae997a"
EXPECTED_STAGE_A_REPORT_SHA256 = "fd9086891a9a699619810f4bccd6f0f2533c194afc6cc1b09cf80484626d704f"
ELIGIBLE_DATASETS = {"dataset1", "dataset2", "dataset3"}
REQUIRED_FIELDS = {"onsetSec", "offsetSec", "pitch"}


class ManifestError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def hash_bytes(data: bytes, algorithm: str = "sha256") -> str:
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def file_hash(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def member_hash(zf: zipfile.ZipFile, name: str) -> str:
    h = hashlib.sha256()
    with zf.open(name, "r") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def path_dataset(name: str) -> str | None:
    parts = [p for p in PurePosixPath(name).parts if p not in ("", "/")]
    return parts[1] if len(parts) > 1 else None


def wav_header_from_bytes(data: bytes) -> dict:
    try:
        with wave.open(io.BytesIO(data), "rb") as h:
            return {
                "channels": int(h.getnchannels()),
                "sampleRate": int(h.getframerate()),
                "sampleWidthBytes": int(h.getsampwidth()),
                "frameCount": int(h.getnframes()),
                "compressionType": str(h.getcomptype()),
            }
    except wave.Error as exc:
        raise ManifestError(f"WAV_HEADER_READ_FAILED:{exc}") from exc


def child_text_by_local_name(node: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    for child in list(node):
        tag = local_tag(str(child.tag))
        if tag not in out:
            out[tag] = (child.text or "").strip()
    return out


def parse_annotation(xml_bytes: bytes) -> dict:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ManifestError(f"XML_PARSE_FAILED:{exc}") from exc

    result = {
        "rootTag": local_tag(str(root.tag)),
        "events": [],
        "errorReasons": [],
    }
    if result["rootTag"] != "instrumentRecording":
        result["errorReasons"].append("XML_ROOT_NOT_INSTRUMENT_RECORDING")
        return result

    event_nodes = [node for node in root.iter() if local_tag(str(node.tag)) == "event"]
    if not event_nodes:
        result["errorReasons"].append("XML_NO_TRANSCRIPTION_EVENTS")
        return result

    parsed_events = []
    saw_missing = False
    saw_nonfinite = False
    saw_negative = False
    saw_bad_order = False

    for node in event_nodes:
        fields = child_text_by_local_name(node)
        if not REQUIRED_FIELDS.issubset(fields) or any(fields[k] == "" for k in REQUIRED_FIELDS):
            saw_missing = True
            continue
        try:
            onset = float(fields["onsetSec"])
            offset = float(fields["offsetSec"])
            pitch = float(fields["pitch"])
        except ValueError:
            saw_nonfinite = True
            continue
        if not all(math.isfinite(x) for x in (onset, offset, pitch)):
            saw_nonfinite = True
            continue
        if onset < 0:
            saw_negative = True
            continue
        if offset < onset:
            saw_bad_order = True
            continue
        parsed_events.append({"onsetSec": onset, "offsetSec": offset, "pitch": pitch})

    if saw_missing:
        result["errorReasons"].append("XML_EVENT_REQUIRED_FIELD_MISSING")
    if saw_nonfinite:
        result["errorReasons"].append("XML_EVENT_REQUIRED_FIELD_NONFINITE")
    if saw_negative:
        result["errorReasons"].append("XML_EVENT_NEGATIVE_ONSET")
    if saw_bad_order:
        result["errorReasons"].append("XML_EVENT_OFFSET_BEFORE_ONSET")
    if len(parsed_events) != len(event_nodes):
        # Any invalid event makes the entire pair ineligible under the preregistration.
        result["events"] = parsed_events
        return result
    if not parsed_events:
        result["errorReasons"].append("XML_NO_VALID_EVENTS")
        return result

    result["events"] = parsed_events
    return result


def build_manifest(
    archive_path: Path,
    stage_a_report_path: Path,
    *,
    expected_archive_md5: str = EXPECTED_ARCHIVE_MD5,
    expected_archive_sha256: str = EXPECTED_ARCHIVE_SHA256,
    expected_stage_a_report_sha256: str = EXPECTED_STAGE_A_REPORT_SHA256,
) -> dict:
    if archive_path.name != EXPECTED_ARCHIVE_NAME:
        raise ManifestError("ARCHIVE_FILENAME_CHANGED")

    archive_md5 = file_hash(archive_path, "md5")
    archive_sha = file_hash(archive_path, "sha256")
    report_sha = file_hash(stage_a_report_path, "sha256")
    if archive_md5 != expected_archive_md5:
        raise ManifestError(f"ARCHIVE_MD5_MISMATCH:{archive_md5}")
    if archive_sha != expected_archive_sha256:
        raise ManifestError(f"ARCHIVE_SHA256_MISMATCH:{archive_sha}")
    if report_sha != expected_stage_a_report_sha256:
        raise ManifestError(f"STAGE_A_REPORT_SHA256_MISMATCH:{report_sha}")

    report = json.loads(stage_a_report_path.read_text(encoding="utf-8"))
    dataset = report.get("dataset", {})
    if dataset.get("archiveMd5") != archive_md5 or dataset.get("archiveSha256") != archive_sha:
        raise ManifestError("STAGE_A_DATASET_IDENTITY_MISMATCH")

    report_rows = {
        row["path"]: row
        for row in report.get("manifest", [])
        if row.get("kind") == "file"
    }
    header_by_sig = {
        row["signatureSha256"]: row["header"]
        for row in report.get("wavHeaderSignatures", [])
    }

    included = []
    excluded = []
    all_onsets: list[float] = []
    all_offsets: list[float] = []
    all_pitches: list[float] = []
    by_dataset: collections.Counter[str] = collections.Counter()
    sample_width_counts: collections.Counter[str] = collections.Counter()

    with zipfile.ZipFile(archive_path, "r") as zf:
        names = set(zf.namelist())
        for pair in sorted(report.get("pairs", []), key=lambda x: (x["wav"], x["xml"])):
            wav_name = pair["wav"]
            xml_name = pair["xml"]
            dataset_name = path_dataset(wav_name)
            reasons: list[str] = []

            if dataset_name not in ELIGIBLE_DATASETS:
                reasons.append("DATASET_NOT_IN_1_2_3")

            wav_row = report_rows.get(wav_name)
            xml_row = report_rows.get(xml_name)
            if wav_name not in names or not wav_row or member_hash(zf, wav_name) != wav_row.get("sha256"):
                reasons.append("WAV_MEMBER_IDENTITY_MISMATCH")
            if xml_name not in names or not xml_row or member_hash(zf, xml_name) != xml_row.get("sha256"):
                reasons.append("XML_MEMBER_IDENTITY_MISMATCH")

            header = None
            if wav_row is not None:
                sig = wav_row.get("wavHeaderSha256")
                header = header_by_sig.get(sig)
            if header is None:
                # Identity mismatch already blocks inclusion; preserve deterministic reason surface.
                if "WAV_MEMBER_IDENTITY_MISMATCH" not in reasons:
                    reasons.append("WAV_MEMBER_IDENTITY_MISMATCH")
            else:
                if header.get("channels") != 1:
                    reasons.append("WAV_NOT_MONO")
                if header.get("sampleRate") != 44100:
                    reasons.append("WAV_SAMPLE_RATE_NOT_44100")
                if header.get("compressionType") != "NONE":
                    reasons.append("WAV_COMPRESSION_NOT_NONE")
                if header.get("sampleWidthBytes") not in (2, 3):
                    reasons.append("WAV_SAMPLE_WIDTH_NOT_16_OR_24_BIT")

            annotation = None
            if xml_name in names and xml_row is not None:
                annotation = parse_annotation(zf.read(xml_name))
                reasons.extend(annotation["errorReasons"])
                if annotation["events"] and len(annotation["events"]) == 0:
                    reasons.append("XML_NO_VALID_EVENTS")

            reasons = sorted(set(reasons))
            base = {
                "stem": pair["stem"],
                "dataset": dataset_name,
                "wav": wav_name,
                "xml": xml_name,
                "wavSha256": wav_row.get("sha256") if wav_row else None,
                "xmlSha256": xml_row.get("sha256") if xml_row else None,
            }
            if reasons:
                excluded.append({**base, "reasons": reasons})
                continue

            assert header is not None and annotation is not None
            events = annotation["events"]
            onsets = [e["onsetSec"] for e in events]
            offsets = [e["offsetSec"] for e in events]
            pitches = [e["pitch"] for e in events]
            all_onsets.extend(onsets)
            all_offsets.extend(offsets)
            all_pitches.extend(pitches)
            by_dataset[str(dataset_name)] += 1
            sample_width_counts[str(header["sampleWidthBytes"])] += 1
            included.append({
                **base,
                "wavHeader": header,
                "referenceEventCount": len(events),
                "annotationStats": {
                    "onsetMin": min(onsets),
                    "onsetMax": max(onsets),
                    "offsetMin": min(offsets),
                    "offsetMax": max(offsets),
                    "pitchMin": min(pitches),
                    "pitchMax": max(pitches),
                    "integerLikePitchCount": sum(abs(p - round(p)) <= 1e-9 for p in pitches),
                    "nonIntegerPitchCount": sum(abs(p - round(p)) > 1e-9 for p in pitches),
                },
            })

    included_manifest_sha = hash_bytes(canonical_json(included).encode("utf-8"))
    annotation_stats = {
        "totalReferenceEventCount": len(all_pitches),
        "onsetMin": min(all_onsets) if all_onsets else None,
        "onsetMax": max(all_onsets) if all_onsets else None,
        "offsetMin": min(all_offsets) if all_offsets else None,
        "offsetMax": max(all_offsets) if all_offsets else None,
        "pitchMin": min(all_pitches) if all_pitches else None,
        "pitchMax": max(all_pitches) if all_pitches else None,
        "integerLikePitchCount": sum(abs(p - round(p)) <= 1e-9 for p in all_pitches),
        "nonIntegerPitchCount": sum(abs(p - round(p)) > 1e-9 for p in all_pitches),
    }

    return {
        "contract": CONTRACT,
        "version": 1,
        "stage": "stage-b-manifest-preparation-only",
        "inputs": {
            "archiveFilename": archive_path.name,
            "archiveMd5": archive_md5,
            "archiveSha256": archive_sha,
            "stageAReportSha256": report_sha,
        },
        "includedManifestSha256": included_manifest_sha,
        "summary": {
            "stageAExactPairCount": len(report.get("pairs", [])),
            "includedPairCount": len(included),
            "excludedPairCount": len(excluded),
            "includedPairCountByDataset": dict(sorted(by_dataset.items())),
            "includedWavCountBySampleWidthBytes": dict(sorted(sample_width_counts.items())),
            **annotation_stats,
        },
        "included": included,
        "excluded": excluded,
        "policyBoundary": {
            "basicPitchInvoked": False,
            "v4ClassifierInvoked": False,
            "demucsInvoked": False,
            "estimateReferenceMatchingPerformed": False,
            "correctnessMetricComputed": False,
            "protectedSongUsed": False,
            "durationAuthorityChanged": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        },
    }


def _make_wav(channels: int = 1, sampwidth: int = 2) -> bytes:
    b = io.BytesIO()
    with wave.open(b, "wb") as h:
        h.setnchannels(channels)
        h.setsampwidth(sampwidth)
        h.setframerate(44100)
        h.writeframes(b"\x00" * (channels * sampwidth * 64))
    return b.getvalue()


def _xml(onset: float, offset: float, pitch: float) -> bytes:
    return (
        f"<instrumentRecording><transcription><event>"
        f"<onsetSec>{onset}</onsetSec><offsetSec>{offset}</offsetSec><pitch>{pitch}</pitch>"
        f"</event></transcription></instrumentRecording>"
    ).encode()


def run_self_test() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        archive = root / EXPECTED_ARCHIVE_NAME
        files = {
            "IDMT-SMT-GUITAR_V2/dataset1/audio/a.wav": _make_wav(),
            "IDMT-SMT-GUITAR_V2/dataset1/annotation/a.xml": _xml(0.1, 0.5, 60),
            "IDMT-SMT-GUITAR_V2/dataset2/audio/b.wav": _make_wav(channels=2),
            "IDMT-SMT-GUITAR_V2/dataset2/annotation/b.xml": _xml(0.2, 0.6, 64),
            "IDMT-SMT-GUITAR_V2/dataset3/audio/c.wav": _make_wav(sampwidth=3),
            "IDMT-SMT-GUITAR_V2/dataset3/annotation/c.xml": _xml(0.3, 0.8, 67),
        }
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name, data in files.items():
                zf.writestr(name, data)

        manifest = []
        header_sigs = {}
        pairs = []
        with zipfile.ZipFile(archive, "r") as zf:
            for name in sorted(files):
                data = zf.read(name)
                row = {"path": name, "kind": "file", "sha256": hash_bytes(data)}
                if name.endswith(".wav"):
                    header = wav_header_from_bytes(data)
                    sig = hash_bytes(canonical_json(header).encode())
                    row["wavHeaderSha256"] = sig
                    header_sigs[sig] = header
                manifest.append(row)
            for stem in ("a", "b", "c"):
                ds = {"a": "dataset1", "b": "dataset2", "c": "dataset3"}[stem]
                pairs.append({
                    "stem": stem,
                    "wav": f"IDMT-SMT-GUITAR_V2/{ds}/audio/{stem}.wav",
                    "xml": f"IDMT-SMT-GUITAR_V2/{ds}/annotation/{stem}.xml",
                })

        report = {
            "dataset": {
                "archiveMd5": file_hash(archive, "md5"),
                "archiveSha256": file_hash(archive, "sha256"),
            },
            "manifest": manifest,
            "wavHeaderSignatures": [
                {"signatureSha256": sig, "header": header}
                for sig, header in sorted(header_sigs.items())
            ],
            "pairs": pairs,
        }
        report_path = root / "stage-a.json"
        report_path.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        result = build_manifest(
            archive,
            report_path,
            expected_archive_md5=file_hash(archive, "md5"),
            expected_archive_sha256=file_hash(archive, "sha256"),
            expected_stage_a_report_sha256=file_hash(report_path, "sha256"),
        )
        assert result["summary"]["includedPairCount"] == 2
        assert result["summary"]["excludedPairCount"] == 1
        assert result["excluded"][0]["reasons"] == ["WAV_NOT_MONO"]
        assert result["summary"]["totalReferenceEventCount"] == 2
        assert result["summary"]["nonIntegerPitchCount"] == 0
        assert result["policyBoundary"]["correctnessMetricComputed"] is False
        return {
            "contract": CONTRACT,
            "selfTest": "PASS",
            "summary": result["summary"],
            "policyBoundary": result["policyBoundary"],
        }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--archive")
    p.add_argument("--stage-a-report")
    p.add_argument("--output")
    p.add_argument("--self-test", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(canonical_json(run_self_test()))
        return 0
    if not args.archive or not args.stage_a_report or not args.output:
        raise ManifestError("USAGE_REQUIRES_ARCHIVE_STAGE_A_REPORT_AND_OUTPUT")
    archive = Path(args.archive)
    report = Path(args.stage_a_report)
    output = Path(args.output)
    if not archive.is_file() or not report.is_file():
        raise ManifestError("INPUT_FILE_REQUIRED")
    if output.exists():
        raise ManifestError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = build_manifest(archive, report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({
        "contract": CONTRACT,
        "output": str(output),
        "includedManifestSha256": result["includedManifestSha256"],
        "summary": result["summary"],
        "policyBoundary": result["policyBoundary"],
    }))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ManifestError as exc:
        print(f"IDMT_V4_STAGE_B_MANIFEST_ERROR:{exc}", file=os.sys.stderr)
        raise SystemExit(2)
