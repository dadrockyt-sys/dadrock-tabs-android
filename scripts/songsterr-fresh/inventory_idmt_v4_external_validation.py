#!/usr/bin/env python3
"""Inventory-only IDMT-SMT-Guitar V4 external-validation stage.

This tool is intentionally incapable of model inference or correctness scoring.
It inventories a ZIP archive, hashes members, reads WAV container headers, and
summarizes XML structure without consuming audio samples for signal analysis.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import io
import json
import os
import tempfile
import wave
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

CONTRACT = "songsterr-fresh-idmt-v4-inventory-v1"
EXPECTED_ARCHIVE_NAME = "IDMT-SMT-GUITAR_V2.zip"
EXPECTED_ARCHIVE_MD5 = "06796e08731bccffaed6ae59361486e4"


class InventoryError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def file_hash(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def member_sha256(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> str:
    h = hashlib.sha256()
    with zf.open(info, "r") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def xml_structure(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> dict:
    with zf.open(info, "r") as f:
        try:
            tree = ET.parse(f)
        except ET.ParseError as exc:
            raise InventoryError(f"XML_PARSE_FAILED:{info.filename}:{exc}") from exc
    root = tree.getroot()
    rows: list[tuple[str, tuple[str, ...], bool, int]] = []

    def walk(node: ET.Element, path: tuple[str, ...]) -> None:
        tag = local_tag(str(node.tag))
        current = path + (tag,)
        attrs = tuple(sorted(local_tag(str(k)) for k in node.attrib.keys()))
        has_text = bool((node.text or "").strip())
        children = list(node)
        rows.append(("/".join(current), attrs, has_text, len(children)))
        for child in children:
            walk(child, current)

    walk(root, ())
    structural_rows = [
        {"path": p, "attributes": list(a), "hasText": t, "childCount": c}
        for p, a, t, c in rows
    ]
    signature = hashlib.sha256(canonical_json(structural_rows).encode("utf-8")).hexdigest()
    return {
        "rootTag": local_tag(str(root.tag)),
        "structureSha256": signature,
        "elementCount": len(structural_rows),
        "elements": structural_rows,
    }


def wav_header(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> dict:
    with zf.open(info, "r") as raw:
        data = raw.read()
    try:
        with wave.open(io.BytesIO(data), "rb") as handle:
            return {
                "channels": int(handle.getnchannels()),
                "sampleRate": int(handle.getframerate()),
                "sampleWidthBytes": int(handle.getsampwidth()),
                "frameCount": int(handle.getnframes()),
                "compressionType": str(handle.getcomptype()),
            }
    except wave.Error as exc:
        raise InventoryError(f"WAV_HEADER_READ_FAILED:{info.filename}:{exc}") from exc


def extension_of(name: str) -> str:
    suffix = PurePosixPath(name).suffix.lower()
    return suffix if suffix else "<none>"


def leaf_stem(name: str) -> str:
    return PurePosixPath(name).stem


def top_components(name: str) -> tuple[str | None, str | None]:
    parts = [p for p in PurePosixPath(name).parts if p not in ("", "/")]
    return (parts[0] if parts else None, parts[1] if len(parts) > 1 else None)


def inventory_archive(archive_path: Path) -> dict:
    if archive_path.name != EXPECTED_ARCHIVE_NAME:
        raise InventoryError("ARCHIVE_FILENAME_CHANGED")
    archive_md5 = file_hash(archive_path, "md5")
    if archive_md5 != EXPECTED_ARCHIVE_MD5:
        raise InventoryError(f"ARCHIVE_MD5_MISMATCH:{archive_md5}")
    archive_sha256 = file_hash(archive_path, "sha256")

    manifest: list[dict] = []
    ext_counts: collections.Counter[str] = collections.Counter()
    first_counts: collections.Counter[str] = collections.Counter()
    second_counts: collections.Counter[str] = collections.Counter()
    xml_signatures: collections.Counter[str] = collections.Counter()
    xml_signature_examples: dict[str, str] = {}
    xml_signature_details: dict[str, dict] = {}
    wav_header_counts: collections.Counter[str] = collections.Counter()
    wav_header_examples: dict[str, str] = {}
    wav_header_details: dict[str, dict] = {}
    stem_groups: dict[str, dict[str, list[str]]] = collections.defaultdict(
        lambda: {"wav": [], "xml": []}
    )

    with zipfile.ZipFile(archive_path, "r") as zf:
        infos = sorted(zf.infolist(), key=lambda x: x.filename)
        for info in infos:
            if info.is_dir():
                manifest.append(
                    {
                        "path": info.filename,
                        "kind": "directory",
                        "uncompressedSize": int(info.file_size),
                        "compressedSize": int(info.compress_size),
                        "crc32": f"{info.CRC:08x}",
                        "sha256": None,
                        "extension": "<dir>",
                    }
                )
                continue

            ext = extension_of(info.filename)
            ext_counts[ext] += 1
            first, second = top_components(info.filename)
            if first is not None:
                first_counts[first] += 1
            if second is not None:
                second_counts[f"{first}/{second}"] += 1

            sha256 = member_sha256(zf, info)
            row = {
                "path": info.filename,
                "kind": "file",
                "uncompressedSize": int(info.file_size),
                "compressedSize": int(info.compress_size),
                "crc32": f"{info.CRC:08x}",
                "sha256": sha256,
                "extension": ext,
            }

            if ext == ".xml":
                schema = xml_structure(zf, info)
                sig = schema["structureSha256"]
                xml_signatures[sig] += 1
                xml_signature_examples.setdefault(sig, info.filename)
                xml_signature_details.setdefault(sig, schema)
                stem_groups[leaf_stem(info.filename)]["xml"].append(info.filename)
                row["xmlStructureSha256"] = sig
            elif ext == ".wav":
                header = wav_header(zf, info)
                key = canonical_json(header)
                sig = hashlib.sha256(key.encode("utf-8")).hexdigest()
                wav_header_counts[sig] += 1
                wav_header_examples.setdefault(sig, info.filename)
                wav_header_details.setdefault(sig, header)
                stem_groups[leaf_stem(info.filename)]["wav"].append(info.filename)
                row["wavHeaderSha256"] = sig

            manifest.append(row)

    pair_rows = []
    unpaired_wav = []
    unpaired_xml = []
    ambiguous = []
    for stem in sorted(stem_groups):
        wavs = sorted(stem_groups[stem]["wav"])
        xmls = sorted(stem_groups[stem]["xml"])
        if len(wavs) == 1 and len(xmls) == 1:
            pair_rows.append({"stem": stem, "wav": wavs[0], "xml": xmls[0]})
        elif wavs and not xmls:
            unpaired_wav.extend(wavs)
        elif xmls and not wavs:
            unpaired_xml.extend(xmls)
        else:
            ambiguous.append({"stem": stem, "wav": wavs, "xml": xmls})

    return {
        "contract": CONTRACT,
        "version": 1,
        "stage": "inventory-only",
        "dataset": {
            "name": "IDMT-SMT-Guitar Dataset",
            "version": "1.0.0",
            "doi": "10.5281/zenodo.7544110",
            "archiveFilename": archive_path.name,
            "archiveMd5": archive_md5,
            "archiveSha256": archive_sha256,
        },
        "summary": {
            "zipMemberCount": len(manifest),
            "fileExtensionCounts": dict(sorted(ext_counts.items())),
            "firstPathComponentCounts": dict(sorted(first_counts.items())),
            "secondPathComponentCounts": dict(sorted(second_counts.items())),
            "uniqueLeafStemCount": len(stem_groups),
            "exactOneToOneLeafStemPairCount": len(pair_rows),
            "unpairedWavCount": len(unpaired_wav),
            "unpairedXmlCount": len(unpaired_xml),
            "ambiguousStemGroupCount": len(ambiguous),
            "wavHeaderSignatureCount": len(wav_header_counts),
            "xmlStructureSignatureCount": len(xml_signatures),
        },
        "wavHeaderSignatures": [
            {
                "signatureSha256": sig,
                "count": wav_header_counts[sig],
                "example": wav_header_examples[sig],
                "header": wav_header_details[sig],
            }
            for sig in sorted(wav_header_counts)
        ],
        "xmlStructureSignatures": [
            {
                "signatureSha256": sig,
                "count": xml_signatures[sig],
                "example": xml_signature_examples[sig],
                "structure": xml_signature_details[sig],
            }
            for sig in sorted(xml_signatures)
        ],
        "pairs": pair_rows,
        "unpairedWav": sorted(unpaired_wav),
        "unpairedXml": sorted(unpaired_xml),
        "ambiguousStemGroups": ambiguous,
        "manifest": manifest,
        "policyBoundary": {
            "basicPitchInvoked": False,
            "v4ClassifierInvoked": False,
            "demucsInvoked": False,
            "audioSamplesUsedForSignalAnalysis": False,
            "estimateReferenceMatchingPerformed": False,
            "correctnessMetricComputed": False,
            "guitarSetUsed": False,
            "protectedSongUsed": False,
            "durationAuthorityChanged": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        },
    }


def _make_test_wav() -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as h:
        h.setnchannels(1)
        h.setsampwidth(2)
        h.setframerate(44100)
        h.writeframes(b"\x00\x00" * 32)
    return buffer.getvalue()


def run_self_test() -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        archive = root / EXPECTED_ARCHIVE_NAME
        wav_bytes = _make_test_wav()
        xml_a = b"<root><event pitch='60'><onset>0.1</onset></event></root>"
        xml_b = b"<root><event pitch='62'><onset>0.2</onset></event></root>"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("IDMT-SMT-GUITAR_V2/dataset1/audio/a.wav", wav_bytes)
            zf.writestr("IDMT-SMT-GUITAR_V2/dataset1/annotation/a.xml", xml_a)
            zf.writestr("IDMT-SMT-GUITAR_V2/dataset2/audio/b.wav", wav_bytes)
            zf.writestr("IDMT-SMT-GUITAR_V2/dataset2/annotation/b.xml", xml_b)
            zf.writestr("IDMT-SMT-GUITAR_V2/readme.txt", b"inventory test")

        # Self-test uses a synthetic archive whose MD5 intentionally differs.
        global EXPECTED_ARCHIVE_MD5
        original = EXPECTED_ARCHIVE_MD5
        try:
            EXPECTED_ARCHIVE_MD5 = file_hash(archive, "md5")
            report = inventory_archive(archive)
        finally:
            EXPECTED_ARCHIVE_MD5 = original

        assert report["summary"]["exactOneToOneLeafStemPairCount"] == 2
        assert report["summary"]["unpairedWavCount"] == 0
        assert report["summary"]["unpairedXmlCount"] == 0
        assert report["summary"]["wavHeaderSignatureCount"] == 1
        assert report["summary"]["xmlStructureSignatureCount"] == 1
        assert report["policyBoundary"]["correctnessMetricComputed"] is False
        assert report["policyBoundary"]["modelValidationComplete"] is False
        return {
            "contract": CONTRACT,
            "selfTest": "PASS",
            "summary": report["summary"],
            "policyBoundary": report["policyBoundary"],
        }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--archive")
    p.add_argument("--output")
    p.add_argument("--self-test", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        print(canonical_json(run_self_test()))
        return 0
    if not args.archive or not args.output:
        raise InventoryError("USAGE_REQUIRES_ARCHIVE_AND_OUTPUT")
    archive = Path(args.archive)
    output = Path(args.output)
    if not archive.is_file():
        raise InventoryError("ARCHIVE_FILE_REQUIRED")
    if output.exists():
        raise InventoryError("OUTPUT_MUST_NOT_ALREADY_EXIST")
    result = inventory_archive(archive)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(canonical_json({"contract": CONTRACT, "output": str(output), "summary": result["summary"], "policyBoundary": result["policyBoundary"]}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InventoryError as exc:
        print(f"IDMT_V4_INVENTORY_ERROR:{exc}", file=os.sys.stderr)
        raise SystemExit(2)
