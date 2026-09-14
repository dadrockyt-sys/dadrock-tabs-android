#!/usr/bin/env python3
"""Additional fail-closed semantic guards for the purpose-built manifest contract.

This module deliberately wraps, rather than rewrites, the already-tested
reference-blind v1 contract validator. A future manifest must pass both the base
validator and these guards before it may advance to any raw-byte structural
audit. No audio/MIDI bytes, model outputs, or correctness observations are read.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "purpose_built_capture_manifest_contract_v1.py"
spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_contract_v1", BASE_PATH)
assert spec and spec.loader
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def semantic_errors(manifest: Any) -> list[str]:
    if not isinstance(manifest, dict):
        return []

    errors: list[str] = []
    corpus = manifest.get("corpus")
    hardware = corpus.get("hardware") if isinstance(corpus, dict) else None
    if isinstance(hardware, dict):
        audio_path_id = hardware.get("evaluatedAudioPathId")
        reference_path_id = hardware.get("independentReferencePathId")
        if (
            _nonempty_string(audio_path_id)
            and _nonempty_string(reference_path_id)
            and audio_path_id.strip() == reference_path_id.strip()
        ):
            errors.append("HARDWARE_AUDIO_REFERENCE_PATH_IDS_MUST_DIFFER")

    attempts = manifest.get("attempts")
    if isinstance(attempts, list):
        by_slot: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            slot_id = attempt.get("slotId")
            if _nonempty_string(slot_id):
                by_slot[slot_id].append(attempt)

        for slot_id, rows in sorted(by_slot.items()):
            if len(rows) < 2:
                continue
            first = rows[0]
            for field in ("playerId", "exerciseId", "category"):
                frozen_value = first.get(field)
                if any(row.get(field) != frozen_value for row in rows[1:]):
                    errors.append(f"SLOT_IDENTITY_CHANGED:{slot_id}:{field}")

    return sorted(set(errors))


def validate_manifest(manifest: Any) -> dict[str, Any]:
    result = base.validate_manifest(manifest)
    extra = semantic_errors(manifest)
    merged_errors = sorted(set(result.get("errors", [])) | set(extra))
    result["errors"] = merged_errors
    result["contractValid"] = not merged_errors
    if extra:
        result["mayAdvanceToReferenceBlindStructuralAudit"] = False
    result["semanticGuardErrors"] = extra
    result["semanticGuardPassed"] = not extra

    # Preserve the base validator's fail-closed authority boundary explicitly.
    result["authoritativeStructuralSuitabilityEstablished"] = False
    result["basicPitchAuthorized"] = False
    result["v6Authorized"] = False
    result["correctnessAuthorized"] = False
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to capture manifest JSON")
    parser.add_argument("--output", help="Optional deterministic validation-result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    result = validate_manifest(manifest)
    rendered = base.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["contractValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
