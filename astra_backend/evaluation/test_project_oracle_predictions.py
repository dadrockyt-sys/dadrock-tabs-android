import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from project_oracle_predictions import (
    EXPECTED_MODEL_SHA256,
    EXPECTED_RUNNER_GIT_BLOB,
    EXPECTED_SETTINGS,
    project_predictions,
)


def h(ch):
    return ch * 64


class OracleProjectionTests(unittest.TestCase):
    def spec(self):
        return {
            "kind": "gomyway-oracle-basic-pitch-preregistration",
            "version": 1,
            "frozenBeforeOracleInference": True,
            "predictionsRead": False,
            "customerDeliveryEligible": False,
            "oracleInput": {"first30WavSha256": h("a"), "sourceM4aSha256": h("b")},
            "canonicalSource": {"audioSha256": h("c")},
            "timeTransform": {
                "equation": "isolatedSeconds = offsetSeconds + scale * sourceSeconds",
                "offsetSeconds": 0.5,
                "scale": 1.01,
            },
            "runtime": {
                "pythonVersion": "3.10.21",
                "basicPitchVersion": "0.4.0",
                "modelSha256": EXPECTED_MODEL_SHA256,
                "runnerGitBlob": EXPECTED_RUNNER_GIT_BLOB,
                "requirementsLockSha256": h("d"),
                "settings": dict(EXPECTED_SETTINGS),
            },
            "scoring": {
                "scope": "whole-mix-to-rhythm",
                "windowSeconds": [0.1, 28.3],
                "onsetToleranceSeconds": 0.05,
                "labelsSha256": h("e"),
                "alignmentSha256": h("f"),
            },
        }

    def prediction(self):
        return {
            "kind": "whole-mix-basic-pitch-development-only",
            "audioSha256": h("a"),
            "roleAssignment": None,
            "customerDeliveryEligible": False,
            "accuracyScore": None,
            "events": [
                {"start": 0.601, "end": 0.702, "midi": 57, "amplitude": 0.8},
                {"start": 1.51, "end": 1.712, "midi": 50, "amplitude": 0.6},
            ],
        }

    def project(self, prediction=None, spec=None):
        return project_predictions(
            prediction or self.prediction(),
            spec or self.spec(),
            prediction_sha256=h("1"),
            prereg_sha256=h("2"),
        )

    def test_exact_inverse_clock_projection_preserves_midi(self):
        result = self.project()
        self.assertAlmostEqual(result["events"][0]["start"], 0.1)
        self.assertAlmostEqual(result["events"][1]["start"], 1.0)
        self.assertEqual([e["midi"] for e in result["events"]], [57, 50])
        self.assertEqual(result["audioSha256"], h("c"))
        self.assertEqual(result["originAudioSha256"], h("a"))
        self.assertFalse(result["customerDeliveryEligible"])

    def test_pre_source_zero_event_is_dropped_not_clipped(self):
        pred = self.prediction()
        pred["events"].insert(0, {"start": 0.2, "end": 0.3, "midi": 40})
        result = self.project(prediction=pred)
        self.assertEqual(result["droppedBeforeSourceZero"], 1)
        self.assertEqual(result["projectedEventCount"], 2)
        self.assertTrue(all(e["start"] >= 0 for e in result["events"]))

    def test_audio_identity_and_role_claim_fail_closed(self):
        for field, bad in [("audioSha256", h("9")), ("roleAssignment", "rhythm"),
                           ("customerDeliveryEligible", True), ("accuracyScore", 1)]:
            pred = self.prediction()
            pred[field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.project(prediction=pred)

    def test_runtime_model_settings_and_transform_are_frozen(self):
        variants = []
        s = self.spec(); s["runtime"]["basicPitchVersion"] = "0.4.1"; variants.append(s)
        s = self.spec(); s["runtime"]["modelSha256"] = h("0"); variants.append(s)
        s = self.spec(); s["runtime"]["settings"]["onset_threshold"] = 0.49; variants.append(s)
        s = self.spec(); s["timeTransform"]["scale"] = 0; variants.append(s)
        s = self.spec(); s["scoring"]["onsetToleranceSeconds"] = 0.1; variants.append(s)
        for spec in variants:
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                self.project(spec=spec)

    def test_invalid_events_fail_closed_and_unordered_events_are_allowed(self):
        bad_rows = [
            [{"start": 1, "end": 1, "midi": 60}],
            [{"start": 1, "end": 2, "midi": True}],
            [{"start": 1, "end": 2, "midi": 128}],
        ]
        for rows in bad_rows:
            pred = self.prediction(); pred["events"] = rows
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                self.project(prediction=pred)
        pred = self.prediction(); pred["events"] = list(reversed(pred["events"]))
        result = self.project(prediction=pred)
        self.assertEqual([e["midi"] for e in result["events"]], [50, 57])

    def test_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pred = root / "prediction.json"
            spec = root / "spec.json"
            out = root / "output.json"
            pred.write_text(json.dumps(self.prediction()))
            spec.write_text(json.dumps(self.spec()))
            out.write_text("existing")
            proc = subprocess.run([
                sys.executable,
                str(Path(__file__).with_name("project_oracle_predictions.py")),
                "--prediction", str(pred),
                "--preregistration", str(spec),
                "--output", str(out),
            ], capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(out.read_text(), "existing")


if __name__ == "__main__":
    unittest.main()
