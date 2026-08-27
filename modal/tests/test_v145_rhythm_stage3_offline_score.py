from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
HARNESS_DIR = ROOT / "validation" / "v145_rhythm_decoder"
if str(HARNESS_DIR) not in sys.path:
    sys.path.insert(0, str(HARNESS_DIR))

import score_offline_stage3_candidate as harness  # noqa: E402


class Stage3OfflineScoreHarnessTests(unittest.TestCase):
    def _events(self):
        events = []
        event_index = 0
        for measure in range(1, 114):
            count = 11 if measure <= 79 else 10
            for step in range(count):
                events.append(
                    {
                        "eventIndex": event_index,
                        "measure": measure,
                        "step": step,
                        "stringIndex": 5,
                        "fret": 0,
                        "midi": 40,
                        "durationSteps": 1,
                        "techniques": [],
                    }
                )
                event_index += 1
        self.assertEqual(len(events), 1209)
        return events

    def _candidate(self):
        events = self._events()
        canonical = harness.canonical_events(events)
        event_sha = harness.sha256_json(canonical)
        return {
            "schemaVersion": 14503,
            "classification": "v145-rhythm-stage3-offline-generated-only-candidate",
            "evaluationRole": "generated-only-pre-reference-candidate",
            "instrument": "rhythm",
            "candidate": {
                "eventCount": 1209,
                "eventSha256": event_sha,
                "generatedMeasureCount": 113,
            },
            "safety": {
                "referenceFree": True,
                "professionalReferenceUsed": False,
                "referenceRuntimeInputUsed": False,
                "goldInputUsed": False,
                "acceptedBaselineChanged": False,
            },
            "renderEvents": events,
        }

    def _accepted_manifest(self):
        metrics = {
            name: value
            for name, value in harness.ACCEPTED_METRICS.items()
            if name != "pdfEventFidelity"
        }
        return {
            "classification": harness.ACCEPTED_MANIFEST_CLASSIFICATION,
            "status": harness.ACCEPTED_MANIFEST_STATUS,
            "name": harness.ACCEPTED_NAME,
            "selectedCandidate": {
                "eventCount": harness.ACCEPTED_EVENT_COUNT,
                "eventSha256": harness.ACCEPTED_EVENT_SHA256,
                "pdfEventSha256": harness.ACCEPTED_EVENT_SHA256,
                "pdfEventFidelity": 1.0,
                "generatedMeasureCount": harness.ACCEPTED_MEASURE_COUNT,
            },
            "fullGoldCalibration": {
                "criticalMismatchCount": harness.ACCEPTED_CRITICAL_MISMATCH_COUNT,
                "gatedMetrics": metrics,
            },
        }

    def _freeze_result(self, candidate):
        events = harness.canonical_events(candidate["renderEvents"])
        event_sha = candidate["candidate"]["eventSha256"]
        return (
            {
                "eventSha256": event_sha,
                "pdfEventSha256": event_sha,
                "pdfEventFidelity": 1.0,
            },
            deepcopy(events),
            {"safety": {"referenceFree": True}},
        )

    def _valid_score(self):
        return {
            "generatedEventCount": 1209,
            "referenceNoteCount": 1000,
            "gatedMetrics": {
                "pitchContentF1": 0.40,
                "pitchTimingTolerantF1": 0.10,
                "stringFretTimingTolerantF1": 0.08,
                "chordPitchSetTolerantF1": 0.09,
                "exactVoicingTolerantF1": 0.07,
                "measureCoverageRecall": 1.0,
            },
            "criticalMismatchCount": 1600,
            "diagnostics": {},
        }

    def test_valid_path_orders_reads_scores_once_and_does_not_mutate_candidate(self):
        candidate = self._candidate()
        candidate_before = deepcopy(candidate)
        accepted = self._accepted_manifest()
        reference_raw = json.dumps({"synthetic": True}, sort_keys=True).encode("utf-8")
        expected_sha = hashlib.sha256(reference_raw).hexdigest()
        log = []
        score_calls = []

        candidate_path = Path("candidate.json")
        accepted_path = Path("accepted.json")
        reference_path = Path("synthetic-reference.json")
        freeze_dir = Path("freeze")

        def read_json(path):
            log.append(f"read_json:{path}")
            if path == candidate_path:
                return candidate
            if path == accepted_path:
                return accepted
            raise AssertionError(path)

        def pre_reference(path):
            log.append(f"pre_reference:{path}")
            self.assertEqual(path, freeze_dir)
            return self._freeze_result(candidate)

        def read_bytes(path):
            log.append(f"read_bytes:{path}")
            self.assertEqual(path, reference_path)
            return reference_raw

        def validate_reference(value):
            log.append("validate_reference")
            self.assertEqual(value, {"synthetic": True})
            return value

        def score(events, reference):
            log.append("score")
            score_calls.append((deepcopy(events), deepcopy(reference)))
            return self._valid_score()

        report = harness.evaluate_stage3_candidate(
            freeze_dir,
            candidate_path,
            reference_path,
            accepted_path,
            read_json=read_json,
            read_bytes=read_bytes,
            pre_reference_fn=pre_reference,
            validate_reference_fn=validate_reference,
            score_fn=score,
            expected_gold_sha256=expected_sha,
        )

        self.assertEqual(candidate, candidate_before)
        self.assertEqual(len(score_calls), 1)
        self.assertLess(log.index("pre_reference:freeze"), log.index("read_json:accepted.json"))
        self.assertLess(log.index("pre_reference:freeze"), log.index("read_bytes:synthetic-reference.json"))
        self.assertLess(log.index("read_json:accepted.json"), log.index("read_bytes:synthetic-reference.json"))
        self.assertLess(log.index("read_bytes:synthetic-reference.json"), log.index("score"))
        self.assertEqual(report["schemaVersion"], 14504)
        self.assertEqual(report["classification"], "v145-rhythm-stage3-offline-calibration-score")
        self.assertEqual(report["evaluationRole"], "calibration-benchmark-not-unseen-holdout")
        self.assertFalse(report["mayClaimUnseenGeneralization"])
        self.assertEqual(report["candidate"]["eventCount"], 1209)
        self.assertEqual(report["candidate"]["pdfEventFidelity"], 1.0)
        self.assertFalse(report["safety"]["candidateMutatedDuringEvaluation"])
        self.assertFalse(report["safety"]["acceptedBaselineChanged"])
        self.assertFalse(report["safety"]["promotionAllowed"])
        self.assertTrue(report["safety"]["referenceOpenedOnlyAfterPreReferenceGate"])
        self.assertFalse(report["safety"]["modalGpuUsed"])
        self.assertFalse(report["safety"]["liveAudioBenchmarkRun"])

    def test_failed_pre_reference_gate_prevents_all_calibration_reads(self):
        candidate = self._candidate()
        calls = []

        def read_json(path):
            calls.append(f"json:{path}")
            if path == Path("candidate.json"):
                return candidate
            raise AssertionError("accepted manifest must not be read")

        def fail_pre(_path):
            calls.append("pre")
            raise ValueError("synthetic pre-reference failure")

        def forbidden_bytes(_path):
            raise AssertionError("gold must not be read")

        with self.assertRaisesRegex(ValueError, "synthetic pre-reference failure"):
            harness.evaluate_stage3_candidate(
                Path("freeze"),
                Path("candidate.json"),
                Path("gold.json"),
                Path("accepted.json"),
                read_json=read_json,
                read_bytes=forbidden_bytes,
                pre_reference_fn=fail_pre,
            )
        self.assertEqual(calls, ["json:candidate.json", "pre"])

    def test_candidate_freeze_identity_mismatch_prevents_calibration_reads(self):
        candidate = self._candidate()

        def read_json(path):
            if path == Path("candidate.json"):
                return candidate
            raise AssertionError("accepted manifest must not be read")

        freeze_manifest, frozen_events, snapshot = self._freeze_result(candidate)
        frozen_events = deepcopy(frozen_events)
        frozen_events[0]["fret"] = 1
        frozen_events[0]["midi"] = 41

        def pre_reference(_path):
            return freeze_manifest, frozen_events, snapshot

        with self.assertRaisesRegex(ValueError, "frozen/candidate"):
            harness.evaluate_stage3_candidate(
                Path("freeze"),
                Path("candidate.json"),
                Path("gold.json"),
                Path("accepted.json"),
                read_json=read_json,
                read_bytes=lambda _path: (_ for _ in ()).throw(AssertionError("gold must not be read")),
                pre_reference_fn=pre_reference,
            )

    def test_wrong_accepted_manifest_fails_before_gold_read(self):
        candidate = self._candidate()
        accepted = self._accepted_manifest()
        accepted["name"] = "wrong-baseline"

        def read_json(path):
            if path == Path("candidate.json"):
                return candidate
            if path == Path("accepted.json"):
                return accepted
            raise AssertionError(path)

        with self.assertRaisesRegex(ValueError, "name changed"):
            harness.evaluate_stage3_candidate(
                Path("freeze"),
                Path("candidate.json"),
                Path("gold.json"),
                Path("accepted.json"),
                read_json=read_json,
                read_bytes=lambda _path: (_ for _ in ()).throw(AssertionError("gold must not be read")),
                pre_reference_fn=lambda _path: self._freeze_result(candidate),
            )

    def test_wrong_gold_sha_fails_before_parse_validation_or_score(self):
        candidate = self._candidate()
        accepted = self._accepted_manifest()
        validated = []
        scored = []

        def read_json(path):
            if path == Path("candidate.json"):
                return candidate
            if path == Path("accepted.json"):
                return accepted
            raise AssertionError(path)

        with self.assertRaisesRegex(ValueError, "gold SHA256 changed"):
            harness.evaluate_stage3_candidate(
                Path("freeze"),
                Path("candidate.json"),
                Path("gold.json"),
                Path("accepted.json"),
                read_json=read_json,
                read_bytes=lambda _path: b"wrong synthetic gold bytes",
                pre_reference_fn=lambda _path: self._freeze_result(candidate),
                validate_reference_fn=lambda value: validated.append(value) or value,
                score_fn=lambda events, reference: scored.append((events, reference)) or self._valid_score(),
                expected_gold_sha256=hashlib.sha256(b"different bytes").hexdigest(),
            )
        self.assertEqual(validated, [])
        self.assertEqual(scored, [])

    def test_candidate_only_failure_prevents_pre_reference_and_calibration_reads(self):
        candidate = self._candidate()
        candidate["safety"]["goldInputUsed"] = True
        pre_calls = []

        with self.assertRaisesRegex(ValueError, "goldInputUsed"):
            harness.evaluate_stage3_candidate(
                Path("freeze"),
                Path("candidate.json"),
                Path("gold.json"),
                Path("accepted.json"),
                read_json=lambda path: candidate if path == Path("candidate.json") else (_ for _ in ()).throw(AssertionError("accepted must not be read")),
                read_bytes=lambda _path: (_ for _ in ()).throw(AssertionError("gold must not be read")),
                pre_reference_fn=lambda _path: pre_calls.append(True) or self._freeze_result(candidate),
            )
        self.assertEqual(pre_calls, [])


if __name__ == "__main__":
    unittest.main()
