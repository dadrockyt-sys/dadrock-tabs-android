#!/usr/bin/env python3
"""Statically inspect the official TabCNN torch-save archive without unpickling it.

This script never imports the checkpoint, constructs the model, or executes inference.
It only verifies bytes and parses pickle opcodes using Python's standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pickletools
import zipfile
from pathlib import Path

EXPECTED_BYTES = 3345122
EXPECTED_MD5 = "ce168b2cd426f81a2a78499214e40605"
EXPECTED_SHA256 = "1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c"


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_global(arg: str) -> dict[str, str]:
    parts = arg.split(" ", 1)
    if len(parts) != 2:
        return {"raw": arg}
    return {"module": parts[0], "name": parts[1]}


def inspect_pickle(payload: bytes) -> dict:
    globals_seen: list[dict[str, str]] = []
    unicode_strings: list[str] = []
    protocol = None
    opcode_counts: dict[str, int] = {}

    for opcode, arg, _position in pickletools.genops(payload):
        opcode_counts[opcode.name] = opcode_counts.get(opcode.name, 0) + 1
        if opcode.name == "PROTO":
            protocol = int(arg)
        elif opcode.name == "GLOBAL":
            globals_seen.append(split_global(str(arg)))
        elif opcode.name in {"BINUNICODE", "SHORT_BINUNICODE", "UNICODE"}:
            value = str(arg)
            if "amt_tools" in value or value.startswith("torch"):
                unicode_strings.append(value)

    unique_globals = sorted(
        {json.dumps(item, sort_keys=True) for item in globals_seen}
    )
    return {
        "protocol": protocol,
        "globals": [json.loads(item) for item in unique_globals],
        "amtToolsGlobals": [
            json.loads(item)
            for item in unique_globals
            if json.loads(item).get("module", "").startswith("amt_tools")
        ],
        "interestingUnicodeStrings": sorted(set(unicode_strings)),
        "opcodeCounts": dict(sorted(opcode_counts.items())),
        "pickleSha256": hashlib.sha256(payload).hexdigest(),
        "pickleBytes": len(payload),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--receipt-out", required=True)
    args = parser.parse_args()

    checkpoint = Path(args.checkpoint)
    size = checkpoint.stat().st_size
    md5 = digest(checkpoint, "md5")
    sha256 = digest(checkpoint, "sha256")

    if size != EXPECTED_BYTES:
        raise SystemExit(f"checkpoint byte mismatch: {size}")
    if md5 != EXPECTED_MD5:
        raise SystemExit(f"checkpoint MD5 mismatch: {md5}")
    if sha256 != EXPECTED_SHA256:
        raise SystemExit(f"checkpoint SHA256 mismatch: {sha256}")
    if not zipfile.is_zipfile(checkpoint):
        raise SystemExit("checkpoint is not a torch zip archive")

    with zipfile.ZipFile(checkpoint) as archive:
        members = sorted(archive.namelist())
        pickle_members = [name for name in members if name.endswith("/data.pkl") or name == "data.pkl"]
        if len(pickle_members) != 1:
            raise SystemExit(f"expected exactly one data.pkl, found {pickle_members}")
        pickle_member = pickle_members[0]
        payload = archive.read(pickle_member)
        archive_members = [
            {
                "name": info.filename,
                "bytes": info.file_size,
                "compressedBytes": info.compress_size,
                "compression": info.compress_type,
            }
            for info in sorted(archive.infolist(), key=lambda item: item.filename)
        ]

    pickle_info = inspect_pickle(payload)
    receipt = {
        "schema": "astra-tabcnn-static-checkpoint-inspection-v1",
        "modelInvoked": False,
        "checkpointUnpickled": False,
        "checkpointImported": False,
        "checkpoint": {
            "bytes": size,
            "md5": md5,
            "sha256": sha256,
            "zipArchive": True,
            "pickleMember": pickle_member,
        },
        "archiveMembers": archive_members,
        "pickle": pickle_info,
    }

    out = Path(args.receipt_out)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("TABCNN_STATIC_INSPECTION=" + json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
