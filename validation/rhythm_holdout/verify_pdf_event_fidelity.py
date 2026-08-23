#!/usr/bin/env python3
"""Prove the professional PDF data path uses the exact frozen Rhythm events.

Run after freeze and after the preview/full PDF preparation step has emitted the event
stream it rendered. This script never reads the professional human reference.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from canonical import canonical_events, sha256_json  # noqa: E402

REFERENCE_DIR = (HERE / "reference").resolve()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def find_render_events(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        raise ValueError("PDF event evidence must be a JSON object")
    containers = [payload]
    for key in ("analysis", "pdf", "professionalPdf", "render", "data"):
        nested = payload.get(key)
        if isinstance(nested, Mapping):
            containers.append(nested)
    for container in containers:
        value = container.get("renderEvents")
        if isinstance(value, list) and value:
            return canonical_events(value)
    raise ValueError("PDF evidence must expose the non-empty renderEvents stream it rendered")


def require_manifest_safety(manifest: Mapping[str, Any]) -> None:
    required = {
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "referenceRuntimeInputUsed": False,
        "runtimeLabelsRequired": False,
        "v143RuntimeSafetyVerified": True,
        "referenceOpenedDuringFreeze": False,
    }
    for key, expected in required.items():
        if manifest.get(key) is not expected:
            raise ValueError(
                f"PDF fidelity cannot proceed with unsafe freeze manifest: {key}={manifest.get(key)!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("freeze_dir", type=Path)
    parser.add_argument("pdf_event_json", type=Path)
    args = parser.parse_args()

    freeze_dir = args.freeze_dir.resolve()
    evidence_path = args.pdf_event_json.resolve()
    if REFERENCE_DIR == evidence_path or REFERENCE_DIR in evidence_path.parents:
        raise ValueError("PDF fidelity stage must not read the professional reference directory")

    snapshot_path = freeze_dir / "rhythm-frozen-analysis.json"
    manifest_path = freeze_dir / "rhythm-freeze-manifest.json"
    snapshot = load_json(snapshot_path)
    manifest = load_json(manifest_path)
    if not isinstance(manifest, Mapping):
        raise ValueError("freeze manifest must be a JSON object")
    require_manifest_safety(manifest)

    frozen_events = canonical_events(snapshot.get("renderEvents", []))
    if not frozen_events:
        raise ValueError("frozen snapshot has no renderEvents")
    frozen_hash = sha256_json(frozen_events)
    if manifest.get("eventSha256") != frozen_hash:
        raise ValueError("freeze manifest event hash no longer matches frozen snapshot")

    pdf_evidence = load_json(evidence_path)
    if not isinstance(pdf_evidence, Mapping):
        raise ValueError("PDF event evidence must be a JSON object")
    if pdf_evidence.get("runtimeSafetyVerified") is not True:
        raise ValueError("PDF render evidence does not prove V143 runtime safety")
    if pdf_evidence.get("runtimeLabelsRequired") is not False:
        raise ValueError("PDF render evidence does not prove runtime labels were unnecessary")
    if pdf_evidence.get("referenceOpened") is not False:
        raise ValueError("PDF render evidence indicates reference access")

    pdf_events = find_render_events(pdf_evidence)
    pdf_hash = sha256_json(pdf_events)

    exact = pdf_hash == frozen_hash and pdf_events == frozen_events
    report = {
        "schemaVersion": 2,
        "instrument": "rhythm",
        "referenceOpenedDuringPdfFidelityCheck": False,
        "runtimeSafetyVerified": True,
        "runtimeLabelsRequired": False,
        "frozenEventCount": len(frozen_events),
        "pdfEventCount": len(pdf_events),
        "frozenEventSha256": frozen_hash,
        "pdfEventSha256": pdf_hash,
        "pdfEventFidelity": 1.0 if exact else 0.0,
        "passed": exact,
    }
    (freeze_dir / "rhythm-pdf-event-fidelity.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if not exact:
        print(json.dumps(report, indent=2, sort_keys=True))
        raise SystemExit("professional PDF event stream differs from frozen scored event stream")

    manifest["pdfEventSha256"] = pdf_hash
    manifest["pdfFidelityVerified"] = True
    manifest["pdfEventFidelity"] = 1.0
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
