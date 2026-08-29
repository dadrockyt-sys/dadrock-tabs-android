#!/usr/bin/env python3
"""Mandatory song-blind construction test for the V165 transcriber adapter repair."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import event_logic_v165 as v165
import transcribe_v165 as transcriber

V162_TRANSCRIBER_BLOB = "fa163cafe2131aa73cdbb50df10d4e4912cff53b"
V164_TRANSCRIBER_BLOB = "df1302216df404bc3368ff820f005d6b63ae100d"
V165_CONTRACT_BLOB = "727782651e14699a0205ea97abc6e82b387299dc"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    v162_path = repo / "validation/v162_cpu_autonomous/transcribe_v162.py"
    v164_path = repo / "validation/v164_cpu_autonomous/transcribe_v164.py"
    contract_path = repo / "debug/v165-cpu-autonomous/implementation-contract.json"

    assert git_blob_sha(v162_path) == V162_TRANSCRIBER_BLOB
    assert git_blob_sha(v164_path) == V164_TRANSCRIBER_BLOB
    assert git_blob_sha(contract_path) == V165_CONTRACT_BLOB

    frozen_source = v162_path.read_text()
    assert frozen_source.count("event_logic_v162.py") == 3

    repaired_adapter_source = transcriber._adapt_v164_adapter_source()
    repaired_call = "'event_logic_v162.py', 'event_logic_v165.py', 3, \"event-logic provenance path\""
    stale_call = "'event_logic_v162.py', 'event_logic_v165.py', 2, \"event-logic provenance path\""
    assert repaired_adapter_source.count(repaired_call) == 1
    assert stale_call not in repaired_adapter_source

    runtime_paths = [
        repo / "debug/v165-cpu-autonomous/timebase.json",
        repo / "debug/v165-cpu-autonomous/timebase-qc.json",
        repo / "debug/v165-cpu-autonomous/generated.json",
        repo / "debug/v165-cpu-autonomous/generation-receipt.json",
        repo / "debug/v165-cpu-autonomous/structural-qc.json",
        repo / "debug/v165-cpu-autonomous/terminal-freeze.json",
        repo / ".github/workflows/v165-generate.yml",
    ]
    assert all(not path.exists() for path in runtime_paths)

    # This is the V164-missing boundary: construction must succeed song-blind.
    adapted = transcriber.build_adapted_module()
    assert adapted.CANDIDATE_SCHEMA == "dadrock.tabs.v165.local-evidence-generated.v1"
    assert adapted.RECEIPT_SCHEMA == "dadrock.tabs.v165.cpu-generation-receipt.v1"
    assert adapted.TIMEBASE_SCHEMA == "dadrock.tabs.v165.local-evidence-timebase.v1"
    assert adapted.TIMEBASE_QC_SCHEMA == "dadrock.tabs.v165.local-evidence-timebase-qc.v1"
    assert adapted.PRE_RUN_SCHEMA == "dadrock.tabs.v165.pre-run-identity-receipt.v1"
    assert adapted.ENV_SCHEMA == "dadrock.tabs.v165.cpu-environment-receipt.v1"
    assert adapted.select_event_step is v165.select_event_step
    assert adapted.segment_guitar_rows is v165.segment_guitar_rows
    assert adapted.bass_state_proposals is v165.bass_state_proposals
    assert hasattr(adapted, "_v165_local_support_at_frame")
    assert callable(adapted.main)  # deliberately not called

    assert all(not path.exists() for path in runtime_paths)
    print(json.dumps({
        "schema": "dadrock.tabs.v165.transcriber-adapter-static-test.v1",
        "validation": "PASS",
        "frozenV162ProvenanceOccurrences": 3,
        "requiredV165Occurrences": 3,
        "adapterConstructionSucceeded": True,
        "adaptedMainCalled": False,
        "songAudioRead": False,
        "normalizationExecuted": False,
        "demucsInvoked": False,
        "pitchInferenceInvoked": False,
        "professionalReferenceRead": False,
        "frozenScorerRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
        "V164RuntimeArtifactRead": False,
        "gpuUsed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
