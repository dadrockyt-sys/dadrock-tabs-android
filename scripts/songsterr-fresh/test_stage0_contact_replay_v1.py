#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "stage0_contact_replay_v1.py"
spec = importlib.util.spec_from_file_location("stage0", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base_docs():
    cfg = {
        "contract": mod.CONFIG_CONTRACT,
        "configurationId": "cfg-stage0-synth",
        "loggerFirmwareId": "fw-synth-1",
        "topologyId": "topo-isolated-synth",
        "stage": mod.STAGE,
        "stringCount": 6,
        "fretNumbers": [1, 2, 3, 4],
        "phaseOrder": [1, 2, 3, 4, 5, 6],
        "sampleEncoding": mod.ENCODING,
        "usedEvaluatedAudio": False,
        "usedModelOutputs": False,
        "derivedFromEvaluatedAudio": False,
    }
    fixture = {
        "contract": mod.FIXTURE_CONTRACT,
        "fixtureId": "fixture-synth-1",
        "configurationId": cfg["configurationId"],
        "topologyId": cfg["topologyId"],
        "stage": mod.STAGE,
        "usedEvaluatedAudio": False,
        "usedModelOutputs": False,
        "cycles": [
            {
                "cycleSequence": 0,
                "strings": [
                    {"stringNumber": 1, "expectedActiveFrets": []},
                    {"stringNumber": 2, "expectedActiveFrets": [1]},
                    {"stringNumber": 3, "expectedActiveFrets": [2]},
                    {"stringNumber": 4, "expectedActiveFrets": [3]},
                    {"stringNumber": 5, "expectedActiveFrets": [4]},
                    {"stringNumber": 6, "expectedActiveFrets": []},
                ],
            }
        ],
    }
    raws = {
        1: [0, 0, 0, 0],
        2: [1, 0, 0, 0],
        3: [0, 1, 0, 0],
        4: [0, 0, 1, 0],
        5: [0, 0, 0, 1],
        6: [0, 0, 0, 0],
    }
    scan = {
        "contract": mod.SCAN_CONTRACT,
        "loggerId": "logger-synth-1",
        "configurationId": cfg["configurationId"],
        "topologyId": cfg["topologyId"],
        "fixtureId": fixture["fixtureId"],
        "stage": mod.STAGE,
        "clockDomainId": "clock-synth-1",
        "usedEvaluatedAudio": False,
        "usedModelOutputs": False,
        "derivedFromEvaluatedAudio": False,
        "records": [
            {
                "cycleSequence": 0,
                "phaseSequence": phase,
                "tick": 100 + phase,
                "driveStringNumber": string_number,
                "rawSenseValues": raws[string_number],
                "healthStatus": "OK",
            }
            for phase, string_number in enumerate(range(1, 7))
        ],
    }
    return cfg, fixture, scan


def render(value):
    return mod.canonical_json(value).encode("utf-8")


def run_docs(cfg, fixture, scan):
    raw = {"configuration": render(cfg), "fixture": render(fixture), "scanLog": render(scan)}
    expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    return mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)


class Stage0ReplayTests(unittest.TestCase):
    def assert_fail(self, result, blocker=None):
        self.assertFalse(result["stage0ReplayContractValid"])
        self.assertFalse(result["stage0ContactTopologyReplayPass"])
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])
        if blocker:
            self.assertGreater(result["blockerCounts"][blocker], 0)

    def test_nominal_pass(self):
        result = run_docs(*base_docs())
        self.assertTrue(result["stage0ReplayContractValid"])
        self.assertTrue(result["stage0ContactTopologyReplayPass"])
        self.assertEqual(result["decodedCycleCount"], 1)
        self.assertEqual(result["decodedStringStateCount"], 6)
        self.assertTrue(result["decodedStateSha256"])
        self.assertTrue(all(v == 0 for v in result["blockerCounts"].values()))
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])

    def test_hash_mismatch_short_circuits_before_parse(self):
        cfg, fixture, scan = base_docs()
        raw = {"configuration": b"not json", "fixture": render(fixture), "scanLog": render(scan)}
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        expected["configuration"] = "0" * 64
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "sourceSha256MismatchCount")
        self.assertEqual(result["errors"], ["SOURCE_SHA256_MISMATCH:configuration"])

    def test_missing_and_extra_source_fail(self):
        cfg, fixture, scan = base_docs()
        raw = {"configuration": render(cfg), "fixture": render(fixture), "scanLog": render(scan), "extra": b"{}"}
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "sourceSha256MismatchCount")
        self.assertIn("EXTRA_SOURCE:extra", result["errors"])
        self.assertIn("EXTRA_EXPECTED_SHA256:extra", result["errors"])

    def test_malformed_json_matching_hash_fails_closed(self):
        cfg, fixture, scan = base_docs()
        raw = {"configuration": b"{oops", "fixture": render(fixture), "scanLog": render(scan)}
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "invalidConfigurationDeclarationCount")
        self.assertTrue(any(e.startswith("INVALID_JSON:configuration:") for e in result["errors"]))

    def test_forbidden_provenance_fails(self):
        docs = list(base_docs())
        docs[0]["usedEvaluatedAudio"] = True
        self.assert_fail(run_docs(*docs), "forbiddenAudioOrModelProvenanceCount")
        docs = list(base_docs())
        docs[2]["usedModelOutputs"] = True
        self.assert_fail(run_docs(*docs), "forbiddenAudioOrModelProvenanceCount")

    def test_invalid_fixture_sequence_fails(self):
        docs = list(base_docs())
        docs[1]["cycles"][0]["cycleSequence"] = 1
        self.assert_fail(run_docs(*docs), "sequenceViolationCount")

    def test_scan_phase_sequence_order_fails(self):
        docs = list(base_docs())
        docs[2]["records"][0], docs[2]["records"][1] = docs[2]["records"][1], docs[2]["records"][0]
        self.assert_fail(run_docs(*docs), "sequenceViolationCount")

    def test_equal_tick_fails(self):
        docs = list(base_docs())
        docs[2]["records"][1]["tick"] = docs[2]["records"][0]["tick"]
        self.assert_fail(run_docs(*docs), "nonmonotonicTickCount")

    def test_drive_string_mismatch_fails(self):
        docs = list(base_docs())
        docs[2]["records"][0]["driveStringNumber"] = 2
        self.assert_fail(run_docs(*docs), "driveStringMismatchCount")

    def test_missing_expected_contact_fails(self):
        docs = list(base_docs())
        docs[2]["records"][1]["rawSenseValues"] = [0, 0, 0, 0]
        self.assert_fail(run_docs(*docs), "missingExpectedContactCount")

    def test_unexpected_crosstalk_contact_fails(self):
        docs = list(base_docs())
        docs[2]["records"][1]["rawSenseValues"] = [1, 1, 0, 0]
        self.assert_fail(run_docs(*docs), "unexpectedContactCount")

    def test_expected_multi_contact_passes(self):
        docs = list(base_docs())
        docs[1]["cycles"][0]["strings"][1]["expectedActiveFrets"] = [1, 2]
        docs[2]["records"][1]["rawSenseValues"] = [1, 1, 0, 0]
        result = run_docs(*docs)
        self.assertTrue(result["stage0ContactTopologyReplayPass"])

    def test_health_status_failure(self):
        docs = list(base_docs())
        docs[2]["records"][3]["healthStatus"] = "STUCK"
        self.assert_fail(run_docs(*docs), "healthStatusViolationCount")

    def test_invalid_configuration(self):
        docs = list(base_docs())
        docs[0]["phaseOrder"] = [1, 2, 3, 4, 6, 5]
        self.assert_fail(run_docs(*docs), "invalidConfigurationDeclarationCount")

    def test_invalid_raw_boolean_values(self):
        docs = list(base_docs())
        docs[2]["records"][0]["rawSenseValues"] = [False, 0, 0, 0]
        self.assert_fail(run_docs(*docs), "invalidScanLogDeclarationCount")

    def test_identical_inputs_produce_identical_canonical_result(self):
        docs = base_docs()
        first = mod.canonical_json(run_docs(*copy.deepcopy(docs))).encode("utf-8")
        second = mod.canonical_json(run_docs(*copy.deepcopy(docs))).encode("utf-8")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main(verbosity=2)
