"""No-network standard-library fixtures; no model/optimizer/data execution."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from guitartechs_training_v10.h1_pilot_readiness_v1 import (
    ScalarProgress, STEP_CAP, git_blob_sha, require_zero_control, verify_population,
)


class ReadinessGuards(unittest.TestCase):
    def make_population(self, root):
        rows = []
        corrections = {}
        for p, n in (("P1", 136), ("P2", 120)):
            for i in range(n):
                key = f"{p}|chords|piece{i}|directinput"
                corrections[key] = -i
                ident = hashlib.sha256(key.encode()).hexdigest()[:24]
                names = [ident + ".features.npy", ident + ".labels.npy"]
                for name in names:
                    (root / name).write_bytes(name.encode())
                rows.append({
                    "key": key, "performer": p, "category": "chords",
                    "performanceKey": f"piece{i}", "captureView": "directinput",
                    "lagMs": -i, "frames": 200,
                    "featureFile": names[0], "labelFile": names[1],
                    "featureSha256": hashlib.sha256(names[0].encode()).hexdigest(),
                    "labelSha256": hashlib.sha256(names[1].encode()).hexdigest(),
                })
        body = json.dumps({
            "schema": "astra-guitar-techs-primary-alignment-corrections-v1",
            "acceptedPrimaryCount": 256, "correctionsMs": corrections
        }, sort_keys=True).encode()
        alignment = root / "alignment.json"
        alignment.write_bytes(body)
        return rows, alignment, git_blob_sha(body)

    def test_population_and_tamper_guards(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            rows, alignment, blob = self.make_population(root)
            receipt = verify_population(rows, root, alignment, blob)
            self.assertEqual(receipt["captureCount"], 256)
            self.assertEqual(receipt["performerCounts"], {"P1": 136, "P2": 120})
            with self.assertRaisesRegex(RuntimeError, "FROZEN_ALIGNMENT_BLOB_MISMATCH"):
                verify_population(rows, root, alignment, "0" * 40)
            with self.assertRaisesRegex(RuntimeError, "FROZEN_ACCEPTED_KEYS_MISMATCH"):
                verify_population(rows[:-1], root, alignment, blob)
            rows[0]["performanceKey"] = "substituted"
            with self.assertRaisesRegex(RuntimeError, "CAPTURE_IDENTITY_MISMATCH"):
                verify_population(rows, root, alignment, blob)
            rows[0]["performanceKey"] = "piece0"
            rows[0]["featureFile"] = "../other.npy"
            with self.assertRaisesRegex(RuntimeError, "PREPARED_FILE_IDENTITY_MISMATCH"):
                verify_population(rows, root, alignment, blob)
            rows[0]["featureFile"] = hashlib.sha256(rows[0]["key"].encode()).hexdigest()[:24] + ".features.npy"
            (root / rows[0]["featureFile"]).write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "PREPARED_FILE_HASH_MISMATCH"):
                verify_population(rows, root, alignment, blob)

    def test_control_checks(self):
        require_zero_control({"f1": 0.0}, {"predictedEvents": 0, "activeRunsAfterPrune": 0})
        for metrics, totals in (
            ({"f1": 0.1}, {"predictedEvents": 0, "activeRunsAfterPrune": 0}),
            ({"f1": 0}, {"predictedEvents": 0, "activeRunsAfterPrune": 1}),
            ({"f1": 0}, {"predictedEvents": 1, "activeRunsAfterPrune": 0}),
        ):
            with self.assertRaises(RuntimeError):
                require_zero_control(metrics, totals)

    def test_step_cap_atomic_failure_receipt(self):
        with tempfile.TemporaryDirectory() as path:
            journal = ScalarProgress(Path(path) / "progress.json", {"synthetic": True})
            with self.assertRaises(ValueError):
                journal.payload["nan"] = float("nan")
                journal.save()
            journal.payload.pop("nan")
            for i in range(STEP_CAP):
                journal.before_step()
                journal.confirmed_step("fold", "arm", 1, i + 1)
            with self.assertRaisesRegex(RuntimeError, "H1_GLOBAL_STEP_CAP_EXHAUSTED"):
                journal.before_step()
            journal.control_verified("fold_a")
            journal.control_verified("fold_b")
            journal.finish()
            saved = json.loads(journal.path.read_text())
            self.assertEqual(saved["optimizerStepsConfirmed"], STEP_CAP)
            self.assertEqual(saved["status"], "completed")
            self.assertFalse(journal.path.with_suffix(".json.tmp").exists())
            with self.assertRaisesRegex(RuntimeError, "DUPLICATE_CONTROL"):
                journal.control_verified("fold_a")
            journal.fail(RuntimeError("synthetic_failure"))
            self.assertEqual(json.loads(journal.path.read_text())["errorCode"], "synthetic_failure")


if __name__ == "__main__":
    unittest.main()
