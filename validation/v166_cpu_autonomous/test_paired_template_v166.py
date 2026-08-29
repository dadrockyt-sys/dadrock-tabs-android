#!/usr/bin/env python3
"""Song-blind static fixture for the exact V166 paired-window template contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import transcribe_v166 as v166

PREREG_BLOB = "ca45241b4ab4689c8ceb3a7107e158367814cc1d"
CONTRACT_BLOB = "9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7"
EXPECTED_OFFSETS = (-1, 0, 1, 2, 3, 4)
TOL = 1e-12


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    prereg = repo / "debug/v166-cpu-autonomous/preregistration.json"
    contract = repo / "debug/v166-cpu-autonomous/implementation-contract.json"
    assert git_blob_sha(prereg) == PREREG_BLOB
    assert git_blob_sha(contract) == CONTRACT_BLOB

    assert tuple(v166.V166_TEMPLATE_FRAME_OFFSETS) == EXPECTED_OFFSETS
    assert v166.V166_TEMPLATE_FRAME_COUNT == 6
    assert v166.paired_window_frames(5, 10) == [4, 5, 6, 7, 8, 9]
    assert v166.paired_window_frames(0, 10) == [0, 0, 1, 2, 3, 4]
    assert v166.paired_window_frames(9, 10) == [8, 9, 9, 9, 9, 9]
    try:
        v166.paired_window_frames(0, 0)
        raise AssertionError("zero-frame input was accepted")
    except RuntimeError:
        pass

    calls: list[list[int]] = []

    def stub_template_scores(cqt, freqs, frames, midi_min, midi_max):
        del freqs, midi_min, midi_max
        selected = [int(x) for x in frames]
        calls.append(selected)
        x = np.asarray(cqt, dtype=float)
        mean = np.mean(x[:, selected], axis=1)
        return mean, 0.5 * mean

    constant = np.repeat(np.arange(1.0, 5.0)[:, None], 10, axis=1)
    freqs = np.arange(4, dtype=float)
    paired_scores, paired_fund = v166.paired_window_template_with(
        stub_template_scores, constant, freqs, 5, 40, 43
    )
    assert calls[-1] == [4, 5, 6, 7, 8, 9]
    predecessor_scores, predecessor_fund = stub_template_scores(
        constant, freqs, [4, 5, 6], 40, 43
    )
    assert np.allclose(paired_scores, predecessor_scores, rtol=TOL, atol=TOL)
    assert np.allclose(paired_fund, predecessor_fund, rtol=TOL, atol=TOL)

    transient = np.ones((1, 10), dtype=float)
    transient[0, 5] = 13.0
    six_scores, _ = v166.paired_window_template_with(
        stub_template_scores, transient, np.ones(1), 5, 40, 40
    )
    three_scores, _ = stub_template_scores(transient, np.ones(1), [4, 5, 6], 40, 40)
    assert 1.0 < float(six_scores[0]) < float(three_scores[0])

    module = v166.build_adapted_module()
    assert module.CANDIDATE_SCHEMA == "dadrock.tabs.v166.local-evidence-generated.v1"
    assert module.RECEIPT_SCHEMA == "dadrock.tabs.v166.cpu-generation-receipt.v1"
    assert module.TIMEBASE_SCHEMA == "dadrock.tabs.v166.local-evidence-timebase.v1"
    assert module.TIMEBASE_QC_SCHEMA == "dadrock.tabs.v166.local-evidence-timebase-qc.v1"
    assert module.PRE_RUN_SCHEMA == "dadrock.tabs.v166.pre-run-identity-receipt.v1"
    assert module.ENV_SCHEMA == "dadrock.tabs.v166.cpu-environment-receipt.v1"
    assert tuple(module.V166_TEMPLATE_FRAME_OFFSETS) == EXPECTED_OFFSETS
    assert module.V166_TEMPLATE_FRAME_COUNT == 6
    assert module.V166_TEMPLATE_EVIDENCE_MODE == "paired-adjacent-six-frame"
    assert module.three_frame_template.__name__ == "_paired_window_template"

    result = {
        "schema": "dadrock.tabs.v166.paired-window-static-test.v1",
        "validation": "PASS",
        "checks": {
            "preregistrationPinned": True,
            "contractPinned": True,
            "offsetsExact": list(EXPECTED_OFFSETS),
            "constantTimeEquivalence": True,
            "boundaryClipping": True,
            "singleTransientDilution": True,
            "adaptedSchemasV166": True,
            "runtimeTemplatePatched": True,
        },
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "scorerRead": False,
            "V165CandidateRead": False,
            "V165ScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
