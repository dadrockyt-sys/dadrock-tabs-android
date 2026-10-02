"""Fail-closed entry point for Independent Bass Feasibility V1.

Preparation only. This module intentionally performs no audio I/O, model loading,
checkpoint download, separation, transcription, or decoding while the frozen
packet status is execution-disabled.
"""
from __future__ import annotations

import json
from pathlib import Path

SPEC = Path(__file__).resolve().parents[2] / "docs" / "astra" / "INDEPENDENT_BASS_FEASIBILITY_EXECUTION_PACKET_V1.json"


def main() -> int:
    packet = json.loads(SPEC.read_text(encoding="utf-8"))
    blockers = packet.get("currentBlockers", [])
    if packet.get("status") != "authorized_for_one_bounded_execution":
        raise SystemExit(
            "Independent Bass Feasibility V1 is disabled. "
            f"status={packet.get('status')!r}; blockers={blockers!r}. "
            "No audio or model has been opened."
        )
    raise SystemExit(
        "Execution implementation is intentionally absent from the preparation packet. "
        "A later explicitly authorized revision must add the admitted execution path."
    )


if __name__ == "__main__":
    main()
