#!/usr/bin/env python3
"""Freeze the exact reference-free Rhythm render stream before holdout access.

This script intentionally has no reference-path argument and never opens anything under
validation/rhythm_holdout/reference. It is safe to run before the scorer is allowed to
access professional ground truth.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from canonical import canonical_events, canonical_json, sha256_json  # noqa: E402

REFERENCE_DIR = (HERE / "reference").resolve()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def analysis_object(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("analysis JSON must be an object")
    nested = payload.get("analysis")
    if isinstance(nested, Mapping):
        return nested
    return payload


def safety_value(payload: Mapping[str, Any], analysis: Mapping[str, Any], key: str) -> Any:
    candidates = [
        analysis.get(key),
        payload.get(key),
        analysis.get("safety", {}).get(key)
        if isinstance(analysis.get("safety"), Mapping)
        else None,
        payload.get("safety", {}).get(key)
        if isinstance(payload.get("safety"), Mapping)
        else None,
    ]
    for value in candidates:
        if value is not None:
            return value
    return None


def require_safety(payload: Mapping[str, Any], analysis: Mapping[str, Any]) -> dict[str, bool]:
    expected = {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "v143RuntimeSafetyVerified": True,
    }
    resolved: dict[str, bool] = {}
    for key, wanted in expected.items():
        value = safety_value(payload, analysis, key)
        if value is None:
            raise ValueError(f"missing required anti-leakage flag: {key}")
        if value is not wanted:
            raise ValueError(f"unsafe analysis flag: {key}={value!r}, expected {wanted!r}")
        resolved[key] = wanted
    return resolved


def exact_render_events(
    payload: Mapping[str, Any], analysis: Mapping[str, Any]
) -> list[dict[str, Any]]:
    # Score the exact stream that drives the structured PDF. Never silently fall
    # back to candidates/raw events because that would break PDF identity.
    candidates = [analysis.get("renderEvents"), payload.get("renderEvents")]
    for value in candidates:
        if isinstance(value, list) and value:
            return canonical_events(value)
    raise ValueError(
        "non-empty renderEvents are required; raw analyzer candidates are not a scoring substitute"
    )


def optional_source_provenance(payload: Mapping[str, Any]) -> tuple[str | None, int | None]:
    source_sha = str(payload.get("sourceAudioSha256") or "").strip().lower()
    source_bytes_raw = payload.get("sourceAudioBytes")

    if source_sha:
        if len(source_sha) != 64 or any(char not in "0123456789abcdef" for char in source_sha):
            raise ValueError("sourceAudioSha256 must be a 64-character lowercase hex SHA-256")
    else:
        source_sha = None

    source_bytes: int | None = None
    if source_bytes_raw is not None:
        if isinstance(source_bytes_raw, bool):
            raise ValueError("sourceAudioBytes must be a positive integer")
        source_bytes = int(source_bytes_raw)
        if source_bytes <= 0:
            raise ValueError("sourceAudioBytes must be a positive integer")

    return source_sha, source_bytes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "analysis_json",
        type=Path,
        help="reference-free structured Rhythm analysis/payload JSON",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="directory for frozen snapshot and manifest",
    )
    parser.add_argument(
        "--source-commit",
        default=os.environ.get("GITHUB_SHA"),
        help="source commit for provenance",
    )
    args = parser.parse_args()

    input_path = args.analysis_json.resolve()
    if REFERENCE_DIR == input_path or REFERENCE_DIR in input_path.parents:
        raise ValueError("freeze stage must not read the professional reference directory")

    payload = load_json(input_path)
    if not isinstance(payload, Mapping):
        raise ValueError("analysis JSON must be an object")
    analysis = analysis_object(payload)
    safety = require_safety(payload, analysis)
    events = exact_render_events(payload, analysis)
    source_audio_sha256, source_audio_bytes = optional_source_provenance(payload)

    metadata = {
        "instrument": "rhythm",
        "tempoBpm": analysis.get("tempoBpm", payload.get("tempoBpm")),
        "timeSignature": analysis.get("timeSignature", payload.get("timeSignature")),
        "tuning": analysis.get("tuning", payload.get("tuning")),
        "structuredMode": analysis.get("structuredMode", payload.get("structuredMode")),
        "sourceAudioSha256": source_audio_sha256,
        "sourceAudioBytes": source_audio_bytes,
    }
    frozen = {
        "schemaVersion": 2,
        "instrument": "rhythm",
        "safety": safety,
        "metadata": metadata,
        "renderEvents": events,
    }

    output_dir = args.output_dir.resolve()
    if REFERENCE_DIR == output_dir or REFERENCE_DIR in output_dir.parents:
        raise ValueError("frozen output must not be written into the professional reference directory")
    output_dir.mkdir(parents=True, exist_ok=True)

    snapshot_path = output_dir / "rhythm-frozen-analysis.json"
    snapshot_path.write_text(canonical_json(frozen) + "\n", encoding="utf-8")

    manifest = {
        "schemaVersion": 2,
        "instrument": "rhythm",
        "frozenAtUtc": datetime.now(timezone.utc).isoformat(),
        "sourceCommit": args.source_commit,
        "sourceAudioSha256": source_audio_sha256,
        "sourceAudioBytes": source_audio_bytes,
        "referenceOpenedDuringFreeze": False,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "v143RuntimeSafetyVerified": True,
        "eventCount": len(events),
        "uniqueMeasureCount": len({event["measure"] for event in events}),
        "eventSha256": sha256_json(events),
        "snapshotSha256": sha256_json(frozen),
        "snapshotFile": snapshot_path.name,
        "pdfEventSha256": None,
        "pdfFidelityVerified": False,
    }
    manifest_path = output_dir / "rhythm-freeze-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
