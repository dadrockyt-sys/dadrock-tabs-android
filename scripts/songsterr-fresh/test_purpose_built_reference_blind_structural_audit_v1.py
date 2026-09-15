#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "purpose_built_reference_blind_structural_audit_v1.py"
spec = importlib.util.spec_from_file_location("audit_v1", MODULE_PATH)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def base_documents():
    hardware = {
        "contract": mod.HARDWARE_CONTRACT,
        "configurationId": "cfg-synthetic-1",
        "calibrationId": "cal-synthetic-1",
        "calibrationUsedHoldoutData": False,
        "calibrationUsedModelOutputs": False,
        "calibrationDerivedFromEvaluatedAudio": False,
        "maxAbsoluteReferenceTimingErrorSeconds": 0.010,
        "openStringMidi": [40, 45, 50, 55, 59, 64],
        "maxFret": 30,
        "eventSemanticsVersion": mod.EVENT_SEMANTICS_VERSION,
    }
    births = {
        "contract": mod.BIRTH_CONTRACT,
        "events": [
            {
                "birthEventId": "b1",
                "onsetSeconds": 0.100,
                "releaseSeconds": 0.300,
                "stringNumber": 1,
                "usedModelOutputs": False,
                "derivedFromEvaluatedAudio": False,
            },
            {
                "birthEventId": "b2",
                "onsetSeconds": 0.500,
                "releaseSeconds": 0.800,
                "stringNumber": 2,
                "usedModelOutputs": False,
                "derivedFromEvaluatedAudio": False,
            },
        ],
    }
    latches = {
        "contract": mod.LATCH_CONTRACT,
        "events": [
            {
                "pitchLatchId": "l1",
                "birthEventId": "b1",
                "timestampSeconds": 0.105,
                "stringNumber": 1,
                "fret": 5,
                "state": "UNAMBIGUOUS",
                "usedModelOutputs": False,
                "derivedFromEvaluatedAudio": False,
            },
            {
                "pitchLatchId": "l2",
                "birthEventId": "b2",
                "timestampSeconds": 0.505,
                "stringNumber": 2,
                "fret": 5,
                "state": "UNAMBIGUOUS",
                "usedModelOutputs": False,
                "derivedFromEvaluatedAudio": False,
            },
        ],
    }
    clock = {
        "contract": mod.CLOCK_CONTRACT,
        "syncId": "sync-synthetic-1",
        "clockDomainId": "clock-synthetic-1",
        "syncLost": False,
        "usedModelOutputs": False,
        "derivedFromEvaluatedAudio": False,
        "maxAbsoluteErrorSeconds": 0.010,
    }
    return hardware, births, latches, clock


def render(value):
    return mod.canonical_json(value).encode("utf-8")


def run_docs(hardware, births, latches, clock):
    raw = {
        "hardware": render(hardware),
        "birth": render(births),
        "pitchLatch": render(latches),
        "clockSync": render(clock),
    }
    expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    return mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)


class StructuralAuditV1Tests(unittest.TestCase):
    def assert_fail(self, result, blocker=None):
        self.assertFalse(result["contractValid"])
        self.assertFalse(result["datasetStructurallySuitable"])
        self.assertFalse(result["authoritativeStructuralSuitabilityEstablished"])
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])
        if blocker:
            self.assertGreater(result["blockerCounts"][blocker], 0)

    def test_nominal_pass_and_authorization_boundary(self):
        result = run_docs(*base_documents())
        self.assertTrue(result["contractValid"])
        self.assertTrue(result["datasetStructurallySuitable"])
        self.assertTrue(result["authoritativeStructuralSuitabilityEstablished"])
        self.assertEqual(result["derivedNoteEventCount"], 2)
        self.assertTrue(result["derivedPopulationSha256"])
        self.assertTrue(all(value == 0 for value in result["blockerCounts"].values()))
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])

    def test_hash_mismatch_short_circuits_before_json_parse(self):
        hardware, births, latches, clock = base_documents()
        raw = {
            "hardware": b"this is deliberately not JSON",
            "birth": render(births),
            "pitchLatch": render(latches),
            "clockSync": render(clock),
        }
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        expected["hardware"] = "0" * 64
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "sourceSha256MismatchCount")
        self.assertEqual(result["errors"], ["SOURCE_SHA256_MISMATCH:hardware"])

    def test_sync_loss_and_excessive_error_fail(self):
        for mutate in (
            lambda clock: clock.update(syncLost=True),
            lambda clock: clock.update(maxAbsoluteErrorSeconds=0.026),
        ):
            docs = list(base_documents())
            mutate(docs[3])
            self.assert_fail(run_docs(*docs), "clockSyncLossOrTimingBoundViolationCount")

    def test_ambiguous_pitch_fails(self):
        docs = list(base_documents())
        docs[2]["events"][0]["state"] = "AMBIGUOUS"
        self.assert_fail(run_docs(*docs), "ambiguousPitchStateCount")

    def test_unmatched_birth_fails(self):
        docs = list(base_documents())
        docs[1]["events"].append({
            "birthEventId": "b3", "onsetSeconds": 1.0, "releaseSeconds": 1.2,
            "stringNumber": 3, "usedModelOutputs": False, "derivedFromEvaluatedAudio": False,
        })
        self.assert_fail(run_docs(*docs), "unmatchedBirthCount")

    def test_unmatched_latch_fails(self):
        docs = list(base_documents())
        docs[2]["events"].append({
            "pitchLatchId": "l3", "birthEventId": "ghost", "timestampSeconds": 1.0,
            "stringNumber": 3, "fret": 3, "state": "UNAMBIGUOUS",
            "usedModelOutputs": False, "derivedFromEvaluatedAudio": False,
        })
        self.assert_fail(run_docs(*docs), "unmatchedPitchLatchCount")

    def test_multiple_latches_for_one_birth_fail(self):
        docs = list(base_documents())
        docs[2]["events"].insert(1, {
            "pitchLatchId": "l1b", "birthEventId": "b1", "timestampSeconds": 0.110,
            "stringNumber": 1, "fret": 5, "state": "UNAMBIGUOUS",
            "usedModelOutputs": False, "derivedFromEvaluatedAudio": False,
        })
        self.assert_fail(run_docs(*docs), "multiplePitchLatchesPerBirthCount")

    def test_string_mismatch_fails(self):
        docs = list(base_documents())
        docs[2]["events"][0]["stringNumber"] = 2
        self.assert_fail(run_docs(*docs), "physicalStringMismatchCount")

    def test_timestamp_delta_bound_fails(self):
        docs = list(base_documents())
        docs[2]["events"][0]["timestampSeconds"] = 0.126
        self.assert_fail(run_docs(*docs), "birthPitchTimestampDeltaViolationCount")

    def test_nonmonotonic_birth_and_latch_streams_fail(self):
        docs = list(base_documents())
        docs[1]["events"].reverse()
        self.assert_fail(run_docs(*docs), "nonmonotonicBirthTimestampCount")
        docs = list(base_documents())
        docs[2]["events"].reverse()
        self.assert_fail(run_docs(*docs), "nonmonotonicPitchLatchTimestampCount")

    def test_same_string_overlap_fails(self):
        docs = list(base_documents())
        docs[1]["events"][1].update(onsetSeconds=0.200, releaseSeconds=0.400, stringNumber=1)
        docs[2]["events"][1].update(timestampSeconds=0.205, stringNumber=1, fret=7)
        self.assert_fail(run_docs(*docs), "sameStringOverlapCount")

    def test_same_key_overlap_fails_across_strings(self):
        docs = list(base_documents())
        # string 1 fret 5 = MIDI 45; string 2 fret 0 = MIDI 45.
        docs[1]["events"][1].update(onsetSeconds=0.200, releaseSeconds=0.400, stringNumber=2)
        docs[2]["events"][1].update(timestampSeconds=0.205, stringNumber=2, fret=0)
        result = run_docs(*docs)
        self.assert_fail(result, "sameKeyOverlapCount")
        self.assertEqual(result["blockerCounts"]["sameStringOverlapCount"], 0)

    def test_out_of_range_midi_fails(self):
        docs = list(base_documents())
        docs[2]["events"][1]["fret"] = 30  # string 2 open 45 -> MIDI 75 is in range
        docs[1]["events"][1]["stringNumber"] = 6
        docs[2]["events"][1]["stringNumber"] = 6
        docs[2]["events"][1]["fret"] = 30  # string 6 open 64 -> MIDI 94
        self.assert_fail(run_docs(*docs), "invalidFretStringOrDerivedMidiCount")

    def test_audio_or_model_provenance_fails(self):
        for where in ("hardware-model", "hardware-audio", "birth", "latch", "clock"):
            docs = list(base_documents())
            if where == "hardware-model":
                docs[0]["calibrationUsedModelOutputs"] = True
            elif where == "hardware-audio":
                docs[0]["calibrationDerivedFromEvaluatedAudio"] = True
            elif where == "birth":
                docs[1]["events"][0]["usedModelOutputs"] = True
            elif where == "latch":
                docs[2]["events"][0]["derivedFromEvaluatedAudio"] = True
            else:
                docs[3]["usedModelOutputs"] = True
            self.assert_fail(run_docs(*docs), "forbiddenModelOrAudioDerivedProvenanceCount")

    def test_duplicate_ids_fail(self):
        docs = list(base_documents())
        docs[1]["events"][1]["birthEventId"] = "b1"
        self.assert_fail(run_docs(*docs), "duplicateBirthIdCount")
        docs = list(base_documents())
        docs[2]["events"][1]["pitchLatchId"] = "l1"
        self.assert_fail(run_docs(*docs), "duplicatePitchLatchIdCount")


    def test_exactly_four_sources_and_hashes_are_required(self):
        hardware, births, latches, clock = base_documents()
        raw = {
            "hardware": render(hardware),
            "birth": render(births),
            "pitchLatch": render(latches),
            "clockSync": render(clock),
        }
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        raw["unexpected"] = b"{}"
        expected["unexpected"] = hashlib.sha256(b"{}").hexdigest()
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "sourceSha256MismatchCount")
        self.assertIn("EXTRA_SOURCE:unexpected", result["errors"])
        self.assertIn("EXTRA_EXPECTED_SHA256:unexpected", result["errors"])

    def test_ambiguous_latch_is_linked_but_not_derived(self):
        docs = list(base_documents())
        docs[2]["events"][0]["state"] = "AMBIGUOUS"
        result = run_docs(*docs)
        self.assert_fail(result, "ambiguousPitchStateCount")
        self.assertEqual(result["blockerCounts"]["unmatchedBirthCount"], 0)
        self.assertEqual(result["derivedNoteEventCount"], 1)

    def test_malformed_json_with_matching_hash_fails_closed(self):
        hardware, births, latches, clock = base_documents()
        raw = {
            "hardware": b"{not-valid-json",
            "birth": render(births),
            "pitchLatch": render(latches),
            "clockSync": render(clock),
        }
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        result = mod.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        self.assert_fail(result, "invalidConfigurationOrCalibrationDeclarationCount")
        self.assertTrue(any(error.startswith("INVALID_JSON:hardware:") for error in result["errors"]))

    def test_hardware_calibration_holdout_use_and_timing_bound_fail(self):
        docs = list(base_documents())
        docs[0]["calibrationUsedHoldoutData"] = True
        self.assert_fail(run_docs(*docs), "invalidConfigurationOrCalibrationDeclarationCount")

        docs = list(base_documents())
        docs[0]["maxAbsoluteReferenceTimingErrorSeconds"] = 0.026
        self.assert_fail(run_docs(*docs), "invalidConfigurationOrCalibrationDeclarationCount")

    def test_frozen_timing_bound_is_inclusive(self):
        docs = list(base_documents())
        docs[0]["maxAbsoluteReferenceTimingErrorSeconds"] = mod.TIMING_BOUND_SECONDS
        docs[3]["maxAbsoluteErrorSeconds"] = mod.TIMING_BOUND_SECONDS
        docs[2]["events"][0]["timestampSeconds"] = docs[1]["events"][0]["onsetSeconds"] + mod.TIMING_BOUND_SECONDS
        result = run_docs(*docs)
        self.assertTrue(result["datasetStructurallySuitable"])

    def test_equal_birth_or_latch_timestamps_are_nonmonotonic(self):
        docs = list(base_documents())
        docs[1]["events"][1]["onsetSeconds"] = docs[1]["events"][0]["onsetSeconds"]
        docs[1]["events"][1]["releaseSeconds"] = 0.400
        self.assert_fail(run_docs(*docs), "nonmonotonicBirthTimestampCount")

        docs = list(base_documents())
        docs[2]["events"][1]["timestampSeconds"] = docs[2]["events"][0]["timestampSeconds"]
        self.assert_fail(run_docs(*docs), "nonmonotonicPitchLatchTimestampCount")

    def test_same_string_overlap_is_not_hidden_by_latch_anomaly(self):
        docs = list(base_documents())
        docs[1]["events"][1].update(onsetSeconds=0.200, releaseSeconds=0.400, stringNumber=1)
        docs[2]["events"][1].update(timestampSeconds=0.205, stringNumber=2, fret=0)
        result = run_docs(*docs)
        self.assert_fail(result, "sameStringOverlapCount")
        self.assertGreater(result["blockerCounts"]["physicalStringMismatchCount"], 0)

    def test_identical_inputs_produce_byte_identical_canonical_result(self):
        docs_a = base_documents()
        docs_b = copy.deepcopy(docs_a)
        first = mod.canonical_json(run_docs(*docs_a)).encode("utf-8")
        second = mod.canonical_json(run_docs(*docs_b)).encode("utf-8")
        self.assertEqual(first, second)


    def test_invalid_hardware_declaration_fails(self):
        docs = list(base_documents())
        docs[0]["openStringMidi"] = [40, 45, 45, 55, 59, 64]
        self.assert_fail(run_docs(*docs), "invalidConfigurationOrCalibrationDeclarationCount")


if __name__ == "__main__":
    unittest.main(verbosity=2)
